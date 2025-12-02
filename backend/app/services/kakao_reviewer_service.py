"""
카카오 리뷰어 서비스
"""

import pandas as pd
from fastapi import HTTPException, status

from app.core.db import db
from app.database.kakao_queries import (
    CHECK_KAKAO_REVIEWER_EXISTS,
    DELETE_KAKAO_REVIEWER_BY_ID,
    GET_ALL_KAKAO_REVIEWERS,
    GET_KAKAO_REVIEWER_BY_ID,
    INSERT_KAKAO_REVIEWER,
    UPDATE_KAKAO_REVIEWER_BY_ID,
)
from app.schemas.kakao_reviewer import (
    KakaoReviewerCreate,
    KakaoReviewerResponse,
    KakaoReviewerUpdate,
)
from app.services.base_service import BaseService


class KakaoReviewerService(
    BaseService[KakaoReviewerCreate, KakaoReviewerUpdate, KakaoReviewerResponse]
):
    """카카오 리뷰어 서비스"""

    def __init__(self):
        super().__init__("kakao_reviewer", "reviewer_id")

    def create(self, data: KakaoReviewerCreate) -> KakaoReviewerResponse:
        """카카오 리뷰어 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    INSERT_KAKAO_REVIEWER,
                    (
                        data.reviewer_id,
                        data.reviewer_user_name,
                        data.reviewer_review_cnt,
                        data.reviewer_avg,
                        data.badge_grade,
                        data.badge_level,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao reviewer", e)

    def get_by_id(self, reviewer_id: int) -> KakaoReviewerResponse:
        """카카오 리뷰어 상세 조회"""
        result = self._execute_query(GET_KAKAO_REVIEWER_BY_ID, (reviewer_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao reviewer not found",
            )

        return self._convert_to_response(result)

    def get_list(
        self,
        skip: int | None = None,
        limit: int | None = None,
        min_review_count: int | None = None,
        is_verified: bool | None = None,
        use_dataframe: bool = False,
    ) -> list[KakaoReviewerResponse]:
        """카카오 리뷰어 목록 조회"""
        # 필터링이나 페이지네이션이 필요한 경우 동적 쿼리 사용
        if min_review_count is not None or is_verified is not None:
            fields = [
                "id",
                "reviewer_id",
                "reviewer_user_name",
                "reviewer_review_cnt",
                "reviewer_avg",
                "badge_grade",
                "badge_level",
                "crawled_at",
                "updated_at",
            ]

            conditions = []
            params = []

            if min_review_count is not None:
                conditions.append("reviewer_review_cnt >= %s")
                params.append(min_review_count)

            if is_verified is not None:
                conditions.append("badge_grade = %s")
                params.append(is_verified)

            query, query_params = self._build_select_query(
                fields,
                conditions,
                order_by="reviewer_review_cnt DESC, reviewer_avg DESC",
                limit=limit,
                offset=skip,
            )

            params.extend(query_params)
            results = self._execute_query_all(query, tuple(params))
        else:
            # 필터링이 없고 skip/limit이 기본값(0, 100)인 경우 전체 쿼리 사용
            if skip is None and limit is None:
                results = self._execute_query_all(GET_ALL_KAKAO_REVIEWERS, ())
            else:
                # 페이지네이션이 필요한 경우
                from app.database.kakao_queries import GET_ALL_KAKAO_REVIEWERS_PAGINATED

                results = self._execute_query_all(
                    GET_ALL_KAKAO_REVIEWERS_PAGINATED, (limit, skip)
                )

        return (
            [self._convert_to_response(row) for row in results]
            if not use_dataframe
            else pd.DataFrame(results)
        )

    def update(
        self, reviewer_id: int, data: KakaoReviewerUpdate
    ) -> KakaoReviewerResponse:
        """카카오 리뷰어 정보 업데이트"""
        # 리뷰어 존재 확인
        if not self._check_exists(CHECK_KAKAO_REVIEWER_EXISTS, (reviewer_id,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao reviewer not found",
            )

        # 업데이트할 필드와 값 구성
        update_values = []
        field_mapping = {
            "reviewer_user_name": data.reviewer_user_name,
            "reviewer_review_cnt": data.reviewer_review_cnt,
            "reviewer_avg": data.reviewer_avg,
            "badge_grade": data.badge_grade,
            "badge_level": data.badge_level,
        }

        for field, value in field_mapping.items():
            if value is not None:
                update_values.append(value)

        # reviewer_id를 마지막에 추가
        update_values.append(reviewer_id)

        result = self._execute_query(UPDATE_KAKAO_REVIEWER_BY_ID, tuple(update_values))
        return self._convert_to_response(result)

    def delete(self, reviewer_id: int) -> dict:
        """카카오 리뷰어 삭제"""
        result = self._execute_query(DELETE_KAKAO_REVIEWER_BY_ID, (reviewer_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao reviewer not found",
            )

        return {"message": "Kakao reviewer deleted successfully"}

    def _convert_to_response(self, row: dict) -> KakaoReviewerResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return KakaoReviewerResponse(
            id=row["id"],
            reviewer_id=row["reviewer_id"],
            reviewer_user_name=row.get("reviewer_user_name"),
            reviewer_review_cnt=row["reviewer_review_cnt"],
            reviewer_avg=row["reviewer_avg"],
            badge_grade=row["badge_grade"],
            badge_level=row["badge_level"],
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )
