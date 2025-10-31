"""
카카오 리뷰어 서비스
"""

from typing import List, Optional

from app.core.db import db
from app.database.kakao_queries import (
    CHECK_KAKAO_REVIEWER_EXISTS,
    DELETE_KAKAO_REVIEWER_BY_USER_ID,
    GET_ALL_KAKAO_REVIEWERS,
    GET_KAKAO_REVIEWER_BY_USER_ID,
    INSERT_KAKAO_REVIEWER,
    UPDATE_KAKAO_REVIEWER_BY_USER_ID,
)
from app.schemas.kakao_reviewer import (
    KakaoReviewerCreate,
    KakaoReviewerResponse,
    KakaoReviewerUpdate,
)
from app.services.base_service import BaseService
from fastapi import HTTPException, status


class KakaoReviewerService(
    BaseService[KakaoReviewerCreate, KakaoReviewerUpdate, KakaoReviewerResponse]
):
    """카카오 리뷰어 서비스"""

    def __init__(self):
        super().__init__("kakao_reviewer", "kakao_user_id")

    def create(self, data: KakaoReviewerCreate) -> KakaoReviewerResponse:
        """카카오 리뷰어 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                # ULID 생성 (Python ulid_utils.py 사용)
                reviewer_id = self._generate_ulid()

                cursor.execute(
                    INSERT_KAKAO_REVIEWER,
                    (
                        reviewer_id,
                        data.kakao_user_id,
                        data.nickname,
                        data.profile_image_url,
                        data.review_count,
                        data.follower_count,
                        data.following_count,
                        data.is_verified,
                    ),
                )

                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao reviewer", e)

    def get_by_id(self, kakao_user_id: str) -> KakaoReviewerResponse:
        """카카오 리뷰어 상세 조회"""
        result = self._execute_query(GET_KAKAO_REVIEWER_BY_USER_ID, (kakao_user_id,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao reviewer not found",
            )

        return self._convert_to_response(result)

    def get_list(
        self,
        skip: int = 0,
        limit: int = 100,
        min_review_count: Optional[int] = None,
        is_verified: Optional[bool] = None,
    ) -> List[KakaoReviewerResponse]:
        """카카오 리뷰어 목록 조회"""
        # 필터링이 필요한 경우 동적 쿼리 사용, 그렇지 않으면 정적 쿼리 사용
        if min_review_count is not None or is_verified is not None:
            fields = [
                "id",
                "kakao_user_id",
                "nickname",
                "profile_image_url",
                "review_count",
                "follower_count",
                "following_count",
                "is_verified",
                "crawled_at",
                "updated_at",
            ]

            conditions = []
            params = []

            if min_review_count is not None:
                conditions.append("review_count >= %s")
                params.append(min_review_count)

            if is_verified is not None:
                conditions.append("is_verified = %s")
                params.append(is_verified)

            query, query_params = self._build_select_query(
                fields,
                conditions,
                order_by="review_count DESC, follower_count DESC",
                limit=limit,
                offset=skip,
            )

            params.extend(query_params)
            results = self._execute_query_all(query, tuple(params))
        else:
            # 필터링이 없는 경우 정적 쿼리 사용
            results = self._execute_query_all(GET_ALL_KAKAO_REVIEWERS, (limit, skip))

        return [self._convert_to_response(row) for row in results]

    def update(
        self, kakao_user_id: str, data: KakaoReviewerUpdate
    ) -> KakaoReviewerResponse:
        """카카오 리뷰어 정보 업데이트"""
        # 리뷰어 존재 확인
        if not self._check_exists(CHECK_KAKAO_REVIEWER_EXISTS, (kakao_user_id,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao reviewer not found",
            )

        # 업데이트할 필드와 값 구성
        update_values = []
        field_mapping = {
            "nickname": data.nickname,
            "profile_image_url": data.profile_image_url,
            "review_count": data.review_count,
            "follower_count": data.follower_count,
            "following_count": data.following_count,
            "is_verified": data.is_verified,
        }

        for field, value in field_mapping.items():
            if value is not None:
                update_values.append(value)

        # kakao_user_id를 마지막에 추가
        update_values.append(kakao_user_id)

        result = self._execute_query(
            UPDATE_KAKAO_REVIEWER_BY_USER_ID, tuple(update_values)
        )
        return self._convert_to_response(result)

    def delete(self, kakao_user_id: str) -> dict:
        """카카오 리뷰어 삭제"""
        result = self._execute_query(DELETE_KAKAO_REVIEWER_BY_USER_ID, (kakao_user_id,))
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
            kakao_user_id=row["kakao_user_id"],
            nickname=row["nickname"],
            profile_image_url=row["profile_image_url"],
            review_count=row["review_count"],
            follower_count=row["follower_count"],
            following_count=row["following_count"],
            is_verified=row["is_verified"],
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )
