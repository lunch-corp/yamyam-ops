"""
카카오 리뷰 서비스
"""

from typing import List, Optional

from app.core.db import db
from app.database.kakao_queries import (
    CHECK_KAKAO_DINER_EXISTS_BY_PLACE_ID,
    CHECK_KAKAO_REVIEW_DUPLICATE,
    CHECK_KAKAO_REVIEW_EXISTS,
    CHECK_KAKAO_REVIEWER_EXISTS,
    DELETE_KAKAO_REVIEW_BY_REVIEW_ID,
    GET_ALL_KAKAO_REVIEWS,
    GET_KAKAO_REVIEW_BY_REVIEW_ID,
    GET_KAKAO_REVIEWS_BASE_QUERY,
    INSERT_KAKAO_REVIEW,
    UPDATE_KAKAO_REVIEW_BY_REVIEW_ID,
)
from app.schemas.kakao_review import (
    KakaoReviewCreate,
    KakaoReviewResponse,
    KakaoReviewUpdate,
    KakaoReviewWithDetails,
)
from app.services.base_service import BaseService
from fastapi import HTTPException, status


class KakaoReviewService(
    BaseService[KakaoReviewCreate, KakaoReviewUpdate, KakaoReviewResponse]
):
    """카카오 리뷰 서비스"""

    def __init__(self):
        super().__init__("kakao_review", "kakao_review_id")

    def create(self, data: KakaoReviewCreate) -> KakaoReviewResponse:
        """카카오 리뷰 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                # 음식점 존재 확인
                if not self._check_exists(
                    CHECK_KAKAO_DINER_EXISTS_BY_PLACE_ID,
                    (data.kakao_place_id,),
                ):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Kakao diner not found",
                    )

                # 리뷰어 존재 확인
                if not self._check_exists(
                    CHECK_KAKAO_REVIEWER_EXISTS, (data.kakao_user_id,)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="Kakao reviewer not found",
                    )

                # 중복 리뷰 확인
                if self._check_exists(
                    CHECK_KAKAO_REVIEW_DUPLICATE, (data.kakao_review_id,)
                ):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Kakao review already exists",
                    )

                # ULID 생성 (Python ulid_utils.py 사용)
                review_id = self._generate_ulid()

                # 리뷰 생성
                cursor.execute(
                    INSERT_KAKAO_REVIEW,
                    (
                        review_id,
                        data.kakao_review_id,
                        data.kakao_place_id,
                        data.kakao_user_id,
                        data.rating,
                        data.review_text,
                        data.review_images,
                        data.visit_date,
                        data.visit_type,
                        data.helpful_count,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao review", e)

    def get_by_id(self, kakao_review_id: str) -> KakaoReviewWithDetails:
        """카카오 리뷰 상세 조회 (상세 정보 포함)"""
        result = self._execute_query(GET_KAKAO_REVIEW_BY_REVIEW_ID, (kakao_review_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao review not found",
            )

        return self._convert_to_details_response(result)

    def get_list(
        self,
        skip: int = 0,
        limit: int = 100,
        kakao_place_id: Optional[str] = None,
        kakao_user_id: Optional[str] = None,
        min_rating: Optional[int] = None,
    ) -> List[KakaoReviewWithDetails]:
        """카카오 리뷰 목록 조회 (상세 정보 포함)"""
        # 필터링이 필요한 경우 동적 쿼리 사용, 그렇지 않으면 정적 쿼리 사용
        if kakao_place_id or kakao_user_id or min_rating is not None:
            query = GET_KAKAO_REVIEWS_BASE_QUERY

            conditions = []
            params = []

            if kakao_place_id:
                conditions.append("kr.kakao_place_id = %s")
                params.append(kakao_place_id)

            if kakao_user_id:
                conditions.append("kr.kakao_user_id = %s")
                params.append(kakao_user_id)

            if min_rating is not None:
                conditions.append("kr.rating >= %s")
                params.append(min_rating)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += (
                " ORDER BY kr.helpful_count DESC, kr.crawled_at DESC LIMIT %s OFFSET %s"
            )
            params.extend([limit, skip])

            results = self._execute_query_all(query, tuple(params))
        else:
            # 필터링이 없는 경우 정적 쿼리 사용
            results = self._execute_query_all(GET_ALL_KAKAO_REVIEWS, (limit, skip))

        return [self._convert_to_details_response(row) for row in results]

    def update(
        self, kakao_review_id: str, data: KakaoReviewUpdate
    ) -> KakaoReviewResponse:
        """카카오 리뷰 정보 업데이트"""
        # 리뷰 존재 확인
        if not self._check_exists(CHECK_KAKAO_REVIEW_EXISTS, (kakao_review_id,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao review not found",
            )

        # 업데이트할 필드와 값 구성
        update_values = []
        field_mapping = {
            "rating": data.rating,
            "review_text": data.review_text,
            "review_images": data.review_images,
            "visit_date": data.visit_date,
            "visit_type": data.visit_type,
            "helpful_count": data.helpful_count,
        }

        for field, value in field_mapping.items():
            if value is not None:
                update_values.append(value)

        # kakao_review_id를 마지막에 추가
        update_values.append(kakao_review_id)

        result = self._execute_query(
            UPDATE_KAKAO_REVIEW_BY_REVIEW_ID, tuple(update_values)
        )
        return self._convert_to_response(result)

    def delete(self, kakao_review_id: str) -> dict:
        """카카오 리뷰 삭제"""
        result = self._execute_query(
            DELETE_KAKAO_REVIEW_BY_REVIEW_ID, (kakao_review_id,)
        )
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
            kakao_place_id=row["kakao_place_id"],
            kakao_user_id=row["kakao_user_id"],
            rating=row["rating"],
            review_text=row["review_text"],
            review_images=row["review_images"],
            visit_date=row["visit_date"],
            visit_type=row["visit_type"],
            helpful_count=row["helpful_count"],
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )

    def _convert_to_details_response(self, row: dict) -> KakaoReviewWithDetails:
        """데이터베이스 행을 상세 응답 모델로 변환"""
        return KakaoReviewWithDetails(
            id=row["id"],
            kakao_review_id=row["kakao_review_id"],
            kakao_place_id=row["kakao_place_id"],
            kakao_user_id=row["kakao_user_id"],
            rating=row["rating"],
            review_text=row["review_text"],
            review_images=row["review_images"],
            visit_date=row["visit_date"],
            visit_type=row["visit_type"],
            helpful_count=row["helpful_count"],
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
            diner_name=row["diner_name"],
            diner_category=row["diner_category"],
            reviewer_nickname=row["reviewer_nickname"],
        )
