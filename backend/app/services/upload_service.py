"""
파일 업로드 서비스
"""

import logging
import traceback

from fastapi import HTTPException, UploadFile, status

from app.core.db import db
from app.database import kakao_queries
from app.processors.file_processor import FileProcessor
from app.processors.kakao_data_processor import KakaoDataProcessor

logger = logging.getLogger(__name__)


class UploadService:
    """파일 업로드 서비스"""

    def __init__(self):
        # 파일 타입별 쿼리 매핑 (PROCESSING_CONFIG와 연동)
        self.query_mapping = {
            "diner_basic": kakao_queries.INSERT_KAKAO_DINER_BASIC,
            "diner_categories": kakao_queries.UPDATE_KAKAO_DINER_CATEGORY,
            "diner_menus": kakao_queries.UPDATE_KAKAO_DINER_MENU,
            "diner_reviews": kakao_queries.UPDATE_KAKAO_DINER_REVIEW,
            "diner_tags": kakao_queries.UPDATE_KAKAO_DINER_TAGS,
            "reviewers": kakao_queries.INSERT_KAKAO_REVIEWER,
            "reviews": kakao_queries.INSERT_KAKAO_REVIEW,
            "diner_grade_bayesian": kakao_queries.UPDATE_KAKAO_DINER_GRADE_BAYESIAN,
            "diner_hidden_score": kakao_queries.UPDATE_KAKAO_DINER_HIDDEN_SCORE,
        }

        # 설정 일관성 검증
        self._validate_all_configs()

    def _validate_all_configs(self):
        """모든 설정의 일관성 검증"""
        for file_type in self.query_mapping.keys():
            validation_result = KakaoDataProcessor.validate_config_consistency(
                file_type
            )
            if not validation_result["valid"]:
                logger.warning(
                    f"설정 일관성 문제 ({file_type}): {validation_result['error']}"
                )
            else:
                logger.info(
                    f"설정 일관성 확인됨 ({file_type}): {validation_result['message']}"
                )

    def get_query_for_file_type(self, file_type: str) -> str:
        """파일 타입에 해당하는 쿼리 반환"""
        if file_type not in self.query_mapping:
            raise ValueError(f"지원하지 않는 파일 타입: {file_type}")
        return self.query_mapping[file_type]

    async def _upload_csv_file(
        self, file: UploadFile, file_type: str, dry_run: bool = False
    ) -> dict:
        """공통 CSV 파일 업로드 메서드"""
        try:
            # 파일 확장자 검증
            if not file.filename.endswith(".csv"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="CSV 파일만 업로드 가능합니다.",
                )

            # 파일 읽기
            content = await file.read()
            df = FileProcessor.read_csv(content)

            # TODO: 크롤러 클리너가 마련되면 빼기
            is_valid, error_msg = FileProcessor.validate_columns(
                df, KakaoDataProcessor.get_required_columns(file_type)
            )
            if not is_valid:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=error_msg
                )

            df = FileProcessor.clean_data(df)

            # Dry run 모드인 경우 실제 DB 작업 없이 검증만 수행
            if dry_run:
                logger.info(f"[DRY RUN] {file_type} 파일 검증 시작: {len(df)} 행")

                # 데이터 처리 검증
                validation_errors = []
                for batch in FileProcessor.batch_data(df, batch_size=1000):
                    try:
                        batch_data = KakaoDataProcessor.process_file(file_type, batch)
                        logger.info(f"[DRY RUN] 배치 처리 성공: {len(batch_data)}개")
                    except Exception as e:
                        validation_errors.append(f"배치 처리 실패: {str(e)}")
                        logger.error(f"[DRY RUN] 배치 처리 실패: {str(e)}")

                return {
                    "message": f"[DRY RUN] {file_type} 파일 검증 완료",
                    "total_rows": len(df),
                    "validation_errors": validation_errors,
                    "dry_run": True,
                    "status": "success"
                    if not validation_errors
                    else "validation_failed",
                }

            # 실제 DB 저장
            success_count = 0
            error_count = 0
            error_details = []

            with db.get_cursor() as (cursor, conn):
                batch_num = 0
                for batch in FileProcessor.batch_data(df, batch_size=1000):
                    batch_num += 1
                    batch_data = KakaoDataProcessor.process_file(file_type, batch)

                    # 배치 전체 저장 시도
                    try:
                        cursor.executemany(self.query_mapping[file_type], batch_data)
                        conn.commit()
                        success_count += len(batch_data)
                        logger.info(f"배치 {batch_num} 저장 성공: {len(batch_data)}개")
                    except Exception as e:
                        # 배치 전체 실패 시 개별 행 처리
                        conn.rollback()
                        error_msg = str(e)
                        error_traceback = traceback.format_exc()
                        logger.warning(
                            f"배치 {batch_num} 전체 저장 실패, 개별 행 처리 시작: {error_msg}"
                        )
                        logger.debug(f"배치 {batch_num} 오류 상세:\n{error_traceback}")

                        # 각 행을 개별적으로 처리 (오류가 발생한 행은 건너뛰고 계속 진행)
                        batch_success = 0
                        batch_errors = 0

                        for idx, row_data in enumerate(batch_data):
                            try:
                                # 각 행을 개별 트랜잭션으로 처리
                                cursor.execute(self.query_mapping[file_type], row_data)
                                conn.commit()
                                batch_success += 1
                                success_count += 1
                            except Exception as row_error:
                                conn.rollback()
                                batch_errors += 1
                                error_count += 1

                                # 원본 DataFrame에서 해당 행 찾기
                                original_idx = (batch_num - 1) * 1000 + idx
                                row_error_msg = str(row_error)

                                # 오류 상세 정보 저장 (최대 10개만)
                                if len(error_details) < 10:
                                    error_details.append(
                                        {
                                            "row_index": original_idx,
                                            "data": row_data,
                                            "error": row_error_msg,
                                        }
                                    )

                                # 처음 5개만 상세 로깅
                                if batch_errors <= 5:
                                    logger.error(
                                        f"  행 {original_idx}: {row_error_msg}"
                                    )
                                    logger.error(f"    데이터: {row_data}")

                                    # INTEGER 범위 오류인 경우 특별히 강조
                                    if "integer out of range" in row_error_msg.lower():
                                        logger.error(
                                            "    ⚠️ INTEGER 범위 초과 오류 감지!"
                                        )
                                        # 데이터에서 큰 정수 값 찾기
                                        for i, val in enumerate(row_data):
                                            if (
                                                isinstance(val, (int, float))
                                                and abs(val) > 2147483647
                                            ):
                                                logger.error(
                                                    f"      값[{i}] = {val} (INTEGER 최대값: 2147483647 초과)"
                                                )

                        logger.info(
                            f"배치 {batch_num} 개별 처리 완료: 성공 {batch_success}개, 실패 {batch_errors}개"
                        )

            result = {
                "message": f"{file_type} 파일 업로드 완료",
                "total_rows": len(df),
                "success_count": success_count,
                "error_count": error_count,
                "dry_run": False,
            }

            if error_details:
                result["error_details"] = error_details[:10]  # 최대 10개만 반환
                result["error_summary"] = (
                    f"{len(error_details)}개 행에서 오류 발생 (상세 정보는 error_details 참조)"
                )

            return result

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"파일 업로드 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"파일 처리 중 오류가 발생했습니다: {str(e)}",
            )

    async def upload_diner_basic(self, file: UploadFile, dry_run: bool = False) -> dict:
        """diner_basic.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_basic", dry_run)

    async def upload_diner_categories(
        self, file: UploadFile, dry_run: bool = False
    ) -> dict:
        """diner_categories.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_categories", dry_run)

    async def upload_diner_menus(self, file: UploadFile, dry_run: bool = False) -> dict:
        """diner_menus.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_menus", dry_run)

    async def upload_diner_reviews(
        self, file: UploadFile, dry_run: bool = False
    ) -> dict:
        """diner_reviews.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_reviews", dry_run)

    async def upload_diner_tags(self, file: UploadFile, dry_run: bool = False) -> dict:
        """diner_tags.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_tags", dry_run)

    async def upload_reviewers(self, file: UploadFile, dry_run: bool = False) -> dict:
        """reviewers.csv 파일 업로드"""
        return await self._upload_csv_file(file, "reviewers", dry_run)

    async def upload_reviews(self, file: UploadFile, dry_run: bool = False) -> dict:
        """reviews.csv 파일 업로드"""
        return await self._upload_csv_file(file, "reviews", dry_run)

    async def upload_diner_grade_bayesian(
        self, file: UploadFile, dry_run: bool = False
    ) -> dict:
        """diner_grade_bayesian.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_grade_bayesian", dry_run)

    async def upload_diner_hidden_score(
        self, file: UploadFile, dry_run: bool = False
    ) -> dict:
        """diner_hidden_score.csv 파일 업로드"""
        return await self._upload_csv_file(file, "diner_hidden_score", dry_run)

    def add_new_file_type(
        self,
        file_type: str,
        required_columns: list[str],
        field_mappings: list[tuple[str, str]],
        sql_fields: list[str],
        query: str,
    ) -> None:
        """
        새로운 파일 타입 추가 (완전한 설정)

        Args:
            file_type: 파일 타입명
            required_columns: 필수 컬럼 리스트
            field_mappings: 필드명과 데이터 타입 매핑 리스트
            sql_fields: SQL에 사용할 필드 리스트
            query: 해당 파일 타입에 사용할 SQL 쿼리
        """
        # PROCESSING_CONFIG에 추가
        KakaoDataProcessor.add_new_file_type(
            file_type, required_columns, field_mappings
        )

        # PROCESSING_CONFIG에 sql_fields와 query_name 추가
        KakaoDataProcessor.PROCESSING_CONFIG[file_type]["sql_fields"] = sql_fields
        KakaoDataProcessor.PROCESSING_CONFIG[file_type]["query_name"] = (
            f"{file_type.upper()}_QUERY"
        )

        # 쿼리 매핑에 추가
        self.query_mapping[file_type] = query

        # 설정 일관성 검증
        validation_result = KakaoDataProcessor.validate_config_consistency(file_type)
        if validation_result["valid"]:
            logger.info(f"새로운 파일 타입 '{file_type}' 추가 완료")
        else:
            logger.warning(
                f"새로운 파일 타입 '{file_type}' 설정 문제: {validation_result['error']}"
            )

    def add_new_file_type_simple(
        self,
        file_type: str,
        required_columns: list[str],
        field_mappings: list[tuple[str, str]],
        query: str,
    ) -> None:
        """
        새로운 파일 타입 추가 (간단한 버전)

        Args:
            file_type: 파일 타입명
            required_columns: 필수 컬럼 리스트
            field_mappings: 필드명과 데이터 타입 매핑 리스트
            query: 해당 파일 타입에 사용할 SQL 쿼리
        """
        # field_mappings에서 필드명만 추출하여 sql_fields로 사용
        sql_fields = [field for field, _ in field_mappings]

        self.add_new_file_type(
            file_type, required_columns, field_mappings, sql_fields, query
        )

    async def upload_custom_file(
        self, file: UploadFile, file_type: str, dry_run: bool = False
    ) -> dict:
        """
        커스텀 파일 타입 업로드

        Args:
            file: 업로드할 파일
            file_type: 파일 타입명 (query_mapping에 등록되어 있어야 함)
        """
        if file_type not in self.query_mapping:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"지원하지 않는 파일 타입: {file_type}",
            )
        return await self._upload_csv_file(file, file_type, dry_run)

    async def bulk_upload_all_files(
        self,
        diner_basic: UploadFile,
        diner_categories: UploadFile = None,
        diner_menus: UploadFile = None,
        diner_reviews: UploadFile = None,
        diner_tags: UploadFile = None,
        dry_run: bool = False,
    ) -> dict:
        """모든 Kakao 데이터 파일 일괄 업로드"""
        results = {}

        try:
            # 1. 기본 정보 업로드 (필수)
            basic_result = await self.upload_diner_basic(diner_basic, dry_run)
            results["diner_basic"] = basic_result

            # 2. 카테고리 정보 업로드 (선택)
            if diner_categories:
                categories_result = await self.upload_diner_categories(
                    diner_categories, dry_run
                )
                results["diner_categories"] = categories_result

            # 3. 메뉴 정보 업로드 (선택)
            if diner_menus:
                menus_result = await self.upload_diner_menus(diner_menus, dry_run)
                results["diner_menus"] = menus_result

            # 4. 리뷰 정보 업로드 (선택)
            if diner_reviews:
                reviews_result = await self.upload_diner_reviews(diner_reviews, dry_run)
                results["diner_reviews"] = reviews_result

            # 5. 태그 정보 업로드 (선택)
            if diner_tags:
                tags_result = await self.upload_diner_tags(diner_tags, dry_run)
                results["diner_tags"] = tags_result

            return {
                "message": f"{'[DRY RUN] ' if dry_run else ''}일괄 업로드 완료",
                "results": results,
                "dry_run": dry_run,
            }

        except Exception as e:
            logger.error(f"일괄 업로드 중 오류: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"일괄 업로드 중 오류가 발생했습니다: {str(e)}",
            )
