"""
카카오 음식점 AI 데이터 서비스
"""

import json
import logging

from fastapi import HTTPException, status

from app.core.db import db
from app.database.kakao_queries import (
    COUNT_KAKAO_DINER_AI_DATA,
    DELETE_KAKAO_DINER_AI_DATA_BY_DINER_IDX,
    DELETE_KAKAO_DINER_AI_DATA_BY_ID,
    GET_KAKAO_DINER_AI_DATA_BY_DINER_IDX,
    GET_KAKAO_DINER_AI_DATA_BY_ID,
    INSERT_KAKAO_DINER_AI_DATA,
    UPDATE_KAKAO_DINER_AI_DATA_BY_ID,
)
from app.schemas.kakao_diner_ai_data import (
    KakaoDinerAIDataCreate,
    KakaoDinerAIDataResponse,
    KakaoDinerAIDataUpdate,
)
from app.services.base_service import BaseService
from app.utils.ulid_utils import generate_ulid

logger = logging.getLogger(__name__)


class KakaoDinerAIDataService(
    BaseService[
        KakaoDinerAIDataCreate, KakaoDinerAIDataUpdate, KakaoDinerAIDataResponse
    ]
):
    """카카오 음식점 AI 데이터 서비스"""

    def __init__(self):
        super().__init__("kakao_diner_ai_data", "id")

    def _extract_all_keywords(
        self,
        ai_bottom_sheet_sheets: dict | list | None,
        blog_summaries: dict | list | None,
    ) -> str | None:
        """
        JSONB 필드에서 모든 keywords를 추출하여 공백으로 구분된 텍스트로 변환

        Args:
            ai_bottom_sheet_sheets: AI 생성 시트 데이터 (JSONB)
            blog_summaries: 블로그 요약 데이터 (JSONB)

        Returns:
            공백으로 구분된 keywords 문자열
        """
        all_keywords = []

        # ai_bottom_sheet_sheets에서 keywords 추출
        if ai_bottom_sheet_sheets:
            if isinstance(ai_bottom_sheet_sheets, list):
                for sheet in ai_bottom_sheet_sheets:
                    if isinstance(sheet, dict):
                        # keywords 필드에서 추출
                        if "keywords" in sheet and isinstance(sheet["keywords"], list):
                            all_keywords.extend(sheet["keywords"])

                        # list 필드 내부의 keywords 추출 (중첩 구조)
                        if "list" in sheet and isinstance(sheet["list"], list):
                            for item in sheet["list"]:
                                if isinstance(item, dict) and "keywords" in item:
                                    if isinstance(item["keywords"], list):
                                        all_keywords.extend(item["keywords"])

        # blog_summaries에서 keywords 추출
        if blog_summaries:
            if isinstance(blog_summaries, list):
                for summary in blog_summaries:
                    if isinstance(summary, dict) and "keywords" in summary:
                        if isinstance(summary["keywords"], list):
                            all_keywords.extend(summary["keywords"])

        # 중복 제거 및 공백으로 구분된 문자열로 변환
        if all_keywords:
            unique_keywords = list(
                dict.fromkeys(all_keywords)
            )  # 순서 유지하며 중복 제거
            return " ".join(str(kw) for kw in unique_keywords if kw)

        return None

    def create(
        self, data: KakaoDinerAIDataCreate, dry_run: bool = False
    ) -> KakaoDinerAIDataResponse:
        """AI 데이터 생성"""
        try:
            if dry_run:
                logger.info(
                    f"[DRY RUN] Creating AI data for diner_idx: {data.diner_idx}"
                )
                return KakaoDinerAIDataResponse(
                    id="dry_run_id",
                    diner_idx=data.diner_idx,
                    ai_bottom_sheet_title=data.ai_bottom_sheet_title,
                    ai_bottom_sheet_summary=data.ai_bottom_sheet_summary,
                    ai_bottom_sheet_sheets=data.ai_bottom_sheet_sheets,
                    ai_bottom_sheet_landing_url=data.ai_bottom_sheet_landing_url,
                    blog_summaries=data.blog_summaries,
                    all_keywords=self._extract_all_keywords(
                        data.ai_bottom_sheet_sheets, data.blog_summaries
                    ),
                    created_at="2024-01-01T00:00:00",
                    updated_at="2024-01-01T00:00:00",
                )

            # all_keywords 자동 생성
            all_keywords = self._extract_all_keywords(
                data.ai_bottom_sheet_sheets, data.blog_summaries
            )

            with db.get_cursor() as (cursor, conn):
                ulid = generate_ulid()

                # JSONB 데이터를 JSON 문자열로 변환
                ai_bottom_sheet_sheets_json = (
                    json.dumps(data.ai_bottom_sheet_sheets, ensure_ascii=False)
                    if data.ai_bottom_sheet_sheets
                    else None
                )
                blog_summaries_json = (
                    json.dumps(data.blog_summaries, ensure_ascii=False)
                    if data.blog_summaries
                    else None
                )

                cursor.execute(
                    INSERT_KAKAO_DINER_AI_DATA,
                    (
                        ulid,
                        data.diner_idx,
                        data.ai_bottom_sheet_title,
                        data.ai_bottom_sheet_summary,
                        ai_bottom_sheet_sheets_json,
                        data.ai_bottom_sheet_landing_url,
                        blog_summaries_json,
                        all_keywords,
                    ),
                )

                # 생성된 데이터 조회
                cursor.execute(GET_KAKAO_DINER_AI_DATA_BY_ID, (ulid,))
                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao diner AI data", e)

    def get_by_id(
        self, ai_data_id: str, dry_run: bool = False
    ) -> KakaoDinerAIDataResponse:
        """AI 데이터 ID로 조회"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Getting AI data by id: {ai_data_id}")
                return None

            with db.get_cursor() as (cursor, conn):
                cursor.execute(GET_KAKAO_DINER_AI_DATA_BY_ID, (ai_data_id,))
                result = cursor.fetchone()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"AI data with id {ai_data_id} not found",
                    )

                return self._convert_to_response(result)

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("getting kakao diner AI data by id", e)

    def get_by_diner_idx(
        self, diner_idx: int, dry_run: bool = False
    ) -> KakaoDinerAIDataResponse | None:
        """diner_idx로 AI 데이터 조회"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Getting AI data by diner_idx: {diner_idx}")
                return None

            with db.get_cursor() as (cursor, conn):
                cursor.execute(GET_KAKAO_DINER_AI_DATA_BY_DINER_IDX, (diner_idx,))
                result = cursor.fetchone()

                if not result:
                    return None

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("getting kakao diner AI data by diner_idx", e)

    def get_list(
        self, skip: int = 0, limit: int = 100, dry_run: bool = False, **filters
    ) -> list[KakaoDinerAIDataResponse]:
        """AI 데이터 목록 조회"""
        try:
            if dry_run:
                logger.info("[DRY RUN] Getting AI data list")
                return []

            # 간단한 구현: 전체 조회 (필요시 필터링 추가)
            with db.get_cursor() as (cursor, conn):
                query = """
                    SELECT id, diner_idx, ai_bottom_sheet_title, ai_bottom_sheet_summary,
                           ai_bottom_sheet_sheets, ai_bottom_sheet_landing_url, blog_summaries, all_keywords,
                           created_at, updated_at
                    FROM kakao_diner_ai_data
                    ORDER BY created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, (limit, skip))
                results = cursor.fetchall()
                return [self._convert_to_response(row) for row in results]

        except Exception as e:
            self._handle_exception("getting kakao diner AI data list", e)

    def update(
        self, ai_data_id: str, data: KakaoDinerAIDataUpdate, dry_run: bool = False
    ) -> KakaoDinerAIDataResponse:
        """AI 데이터 업데이트"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Updating AI data: {ai_data_id}")
                return None

            # 기존 데이터 조회
            existing_data = self.get_by_id(ai_data_id)

            # 업데이트할 필드 결정 (None이 아닌 값만)
            update_data = {
                "diner_idx": data.diner_idx
                if data.diner_idx is not None
                else existing_data.diner_idx,
                "ai_bottom_sheet_title": data.ai_bottom_sheet_title
                if data.ai_bottom_sheet_title is not None
                else existing_data.ai_bottom_sheet_title,
                "ai_bottom_sheet_summary": data.ai_bottom_sheet_summary
                if data.ai_bottom_sheet_summary is not None
                else existing_data.ai_bottom_sheet_summary,
                "ai_bottom_sheet_sheets": data.ai_bottom_sheet_sheets
                if data.ai_bottom_sheet_sheets is not None
                else existing_data.ai_bottom_sheet_sheets,
                "ai_bottom_sheet_landing_url": data.ai_bottom_sheet_landing_url
                if data.ai_bottom_sheet_landing_url is not None
                else existing_data.ai_bottom_sheet_landing_url,
                "blog_summaries": data.blog_summaries
                if data.blog_summaries is not None
                else existing_data.blog_summaries,
            }

            # all_keywords 재생성
            all_keywords = self._extract_all_keywords(
                update_data["ai_bottom_sheet_sheets"], update_data["blog_summaries"]
            )

            with db.get_cursor() as (cursor, conn):
                # JSONB 데이터를 JSON 문자열로 변환
                ai_bottom_sheet_sheets_json = (
                    json.dumps(
                        update_data["ai_bottom_sheet_sheets"], ensure_ascii=False
                    )
                    if update_data["ai_bottom_sheet_sheets"]
                    else None
                )
                blog_summaries_json = (
                    json.dumps(update_data["blog_summaries"], ensure_ascii=False)
                    if update_data["blog_summaries"]
                    else None
                )

                cursor.execute(
                    UPDATE_KAKAO_DINER_AI_DATA_BY_ID,
                    (
                        update_data["diner_idx"],
                        update_data["ai_bottom_sheet_title"],
                        update_data["ai_bottom_sheet_summary"],
                        ai_bottom_sheet_sheets_json,
                        update_data["ai_bottom_sheet_landing_url"],
                        blog_summaries_json,
                        all_keywords,
                        ai_data_id,
                    ),
                )
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"AI data with id {ai_data_id} not found",
                    )

                return self._convert_to_response(result)

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("updating kakao diner AI data", e)

    def delete(self, ai_data_id: str, dry_run: bool = False) -> dict[str, str]:
        """AI 데이터 삭제"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Deleting AI data: {ai_data_id}")
                return {"message": f"[DRY RUN] AI data {ai_data_id} would be deleted"}

            with db.get_cursor() as (cursor, conn):
                cursor.execute(DELETE_KAKAO_DINER_AI_DATA_BY_ID, (ai_data_id,))
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"AI data with id {ai_data_id} not found",
                    )

                return {"message": f"AI data {ai_data_id} deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("deleting kakao diner AI data", e)

    def delete_by_diner_idx(
        self, diner_idx: int, dry_run: bool = False
    ) -> dict[str, str]:
        """diner_idx로 AI 데이터 삭제"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Deleting AI data for diner_idx: {diner_idx}")
                return {
                    "message": f"[DRY RUN] AI data for diner_idx {diner_idx} would be deleted"
                }

            with db.get_cursor() as (cursor, conn):
                cursor.execute(DELETE_KAKAO_DINER_AI_DATA_BY_DINER_IDX, (diner_idx,))
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"AI data for diner_idx {diner_idx} not found",
                    )

                return {
                    "message": f"AI data for diner_idx {diner_idx} deleted successfully"
                }

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("deleting kakao diner AI data by diner_idx", e)

    def get_count(self) -> int:
        """AI 데이터 개수 조회"""
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(COUNT_KAKAO_DINER_AI_DATA)
                result = cursor.fetchone()
                return result["count"] if result else 0

        except Exception as e:
            self._handle_exception("counting kakao diner AI data", e)

    def _convert_to_response(self, row: dict) -> KakaoDinerAIDataResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return KakaoDinerAIDataResponse(
            id=row["id"],
            diner_idx=row["diner_idx"],
            ai_bottom_sheet_title=row["ai_bottom_sheet_title"],
            ai_bottom_sheet_summary=row["ai_bottom_sheet_summary"],
            ai_bottom_sheet_sheets=row["ai_bottom_sheet_sheets"],
            ai_bottom_sheet_landing_url=row["ai_bottom_sheet_landing_url"],
            blog_summaries=row["blog_summaries"],
            all_keywords=row["all_keywords"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
