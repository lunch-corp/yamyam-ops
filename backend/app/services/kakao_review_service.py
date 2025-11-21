"""
카카오 리뷰 서비스
"""

from fastapi import HTTPException, status

from app.core.db import db
from app.database.kakao_queries import (
    CHECK_KAKAO_DINER_EXISTS_BY_IDX,
    CHECK_KAKAO_REVIEW_EXISTS,
    CHECK_KAKAO_REVIEWER_EXISTS,
    DELETE_KAKAO_REVIEW_BY_ID,
    GET_ALL_KAKAO_REVIEWS,
    GET_KAKAO_REVIEW_BY_ID,
    GET_KAKAO_REVIEWS_BASE_QUERY,
    INSERT_KAKAO_REVIEW,
    UPDATE_KAKAO_REVIEW_BY_ID,
)
from app.schemas.kakao_review import (
    KakaoReviewCreate,
    KakaoReviewResponse,
    KakaoReviewUpdate,
    KakaoReviewWithDetails,
)
from app.services.base_service import BaseService


class KakaoReviewService(
    BaseService[KakaoReviewCreate, KakaoReviewUpdate, KakaoReviewResponse]
):
    """카카오 리뷰 서비스"""

    def __init__(self):
        super().__init__("kakao_review", "review_id")

    def create(self, data: KakaoReviewCreate) -> KakaoReviewResponse:
        """카카오 리뷰 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                # 음식점 존재 확인
                if not self._check_exists(
                    CHECK_KAKAO_DINER_EXISTS_BY_IDX,
                    (data.diner_idx,),
                ):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Kakao diner not found",
                    )

                # 리뷰어 존재 확인
                if not self._check_exists(
                    CHECK_KAKAO_REVIEWER_EXISTS, (data.reviewer_id,)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Kakao reviewer not found",
                    )

                # 리뷰 생성 (UPSERT로 변경되어 중복 확인 불필요)
                cursor.execute(
                    INSERT_KAKAO_REVIEW,
                    (
                        data.diner_idx,
                        data.reviewer_id,
                        data.review_id,
                        data.reviewer_review,
                        data.reviewer_review_date,
                        data.reviewer_review_score,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao review", e)

    def get_by_id(self, review_id: int) -> KakaoReviewWithDetails:
        """카카오 리뷰 상세 조회 (상세 정보 포함)"""
        result = self._execute_query(GET_KAKAO_REVIEW_BY_ID, (review_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao review not found",
            )

        return self._convert_to_details_response(result)

    def get_list(
        self,
        skip: int | None = 0,
        limit: int | None = 100,
        diner_idx: int | None = None,
        reviewer_id: int | None = None,
        min_rating: float | None = None,
    ) -> list[KakaoReviewWithDetails]:
        """카카오 리뷰 목록 조회 (상세 정보 포함)"""
        # 필터링이나 페이지네이션이 필요한 경우 동적 쿼리 사용
        if diner_idx or reviewer_id or min_rating is not None:
            query = GET_KAKAO_REVIEWS_BASE_QUERY

            conditions = []
            params = []

            if diner_idx:
                conditions.append("kr.diner_idx = %s")
                params.append(diner_idx)

            if reviewer_id:
                conditions.append("kr.reviewer_id = %s")
                params.append(reviewer_id)

            if min_rating is not None:
                conditions.append("kr.reviewer_review_score >= %s")
                params.append(min_rating)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY kr.reviewer_review_score DESC, kr.crawled_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            results = self._execute_query_all(query, tuple(params))
        else:
            if skip is None and limit is None:
                results = self._execute_query_all(GET_ALL_KAKAO_REVIEWS, ())
            else:
                # 페이지네이션이 필요한 경우
                from app.database.kakao_queries import GET_ALL_KAKAO_REVIEWS_PAGINATED

                results = self._execute_query_all(
                    GET_ALL_KAKAO_REVIEWS_PAGINATED, (limit, skip)
                )

        return [self._convert_to_details_response(row) for row in results]

    def update(self, review_id: int, data: KakaoReviewUpdate) -> KakaoReviewResponse:
        """카카오 리뷰 정보 업데이트"""
        # 리뷰 존재 확인
        if not self._check_exists(CHECK_KAKAO_REVIEW_EXISTS, (review_id,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao review not found",
            )

        # 업데이트할 필드와 값 구성
        update_values = []
        field_mapping = {
            "reviewer_review": data.reviewer_review,
            "reviewer_review_date": data.reviewer_review_date,
            "reviewer_review_score": data.reviewer_review_score,
        }

        for field, value in field_mapping.items():
            if value is not None:
                update_values.append(value)

        # review_id를 마지막에 추가
        update_values.append(review_id)

        result = self._execute_query(UPDATE_KAKAO_REVIEW_BY_ID, tuple(update_values))
        return self._convert_to_response(result)

    def delete(self, review_id: int) -> dict:
        """카카오 리뷰 삭제"""
        result = self._execute_query(DELETE_KAKAO_REVIEW_BY_ID, (review_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao review not found",
            )

        return {"message": "Kakao review deleted successfully"}

    def _convert_to_response(self, row: dict) -> KakaoReviewResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return KakaoReviewResponse(
            id=row["id"],
            kakao_review_id=row["kakao_review_id"],
            diner_idx=row["diner_idx"],
            reviewer_id=row["reviewer_id"],
            review_id=row["review_id"],
            reviewer_review=row.get("reviewer_review"),
            reviewer_review_date=row.get("reviewer_review_date"),
            reviewer_review_score=row["reviewer_review_score"],
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )

    def _convert_to_details_response(self, row: dict) -> KakaoReviewWithDetails:
        """데이터베이스 행을 상세 응답 모델로 변환"""
        return KakaoReviewWithDetails(
            id=row["id"],
            kakao_review_id=row["kakao_review_id"],
            diner_idx=row["diner_idx"],
            reviewer_id=row["reviewer_id"],
            review_id=row["review_id"],
            reviewer_review=row.get("reviewer_review"),
            reviewer_review_date=row.get("reviewer_review_date"),
            reviewer_review_score=row["reviewer_review_score"],
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
            diner_name=row.get("diner_name"),
            diner_tag=row.get("diner_tag"),
            reviewer_user_name=row.get("reviewer_user_name"),
        )
