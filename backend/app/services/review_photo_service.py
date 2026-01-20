"""
리뷰 사진 서비스
"""

import logging
from typing import Optional

from app.services.base_service import BaseService

logger = logging.getLogger(__name__)

# SQL 쿼리
GET_TOP_REVIEWER_PHOTO_BY_DINER = """
    SELECT rp.id, rp.review_id, rp.photo_url, rp.original_photo_id,
           rp.media_type, rp.status, rp.display_order, rp.view_count, rp.created_at
    FROM review_photos rp
    JOIN kakao_review kr ON rp.review_id = kr.review_id
    JOIN kakao_reviewer krev ON kr.reviewer_id = krev.reviewer_id
    WHERE kr.diner_idx = %s
    ORDER BY rp.view_count DESC, krev.reviewer_review_cnt DESC, rp.display_order ASC
    LIMIT 1
"""

GET_PHOTOS_BY_DINER_IDX = """
    SELECT rp.id, rp.review_id, rp.photo_url, rp.original_photo_id,
           rp.media_type, rp.status, rp.display_order, rp.view_count, rp.created_at
    FROM review_photos rp
    JOIN kakao_review kr ON rp.review_id = kr.review_id
    WHERE kr.diner_idx = %s
    ORDER BY rp.display_order ASC
"""


class ReviewPhotoService(BaseService):
    """리뷰 사진 서비스"""

    def __init__(self):
        # BaseService는 제네릭이지만, ReviewPhoto는 간단한 서비스이므로
        # 기본 메서드만 구현
        super().__init__("review_photos", "id")

    def get_top_reviewer_photo(self, diner_idx: int) -> Optional[dict]:
        """
        diner_idx별로 view_count가 높은 이미지를 우선 선택
        view_count가 같으면 reviewer_review_cnt가 높은 reviewer의 이미지를 선택

        Args:
            diner_idx: 맛집 인덱스

        Returns:
            dict: 이미지 정보 (photo_url, review_id 등) 또는 None
        """
        try:
            logger.debug(f"이미지 조회 쿼리 실행: diner_idx={diner_idx}")
            result = self._execute_query(GET_TOP_REVIEWER_PHOTO_BY_DINER, (diner_idx,))
            if result:
                logger.info(
                    f"이미지 선택 완료: diner_idx={diner_idx}, photo_url={result.get('photo_url', '')[:50]}..., view_count={result.get('view_count', 0)}"
                )
                return result
            else:
                logger.info(f"이미지 없음: diner_idx={diner_idx} (쿼리 결과 없음)")
                return None
        except Exception as e:
            logger.warning(
                f"이미지 조회 실패 (diner_idx={diner_idx}): {e}", exc_info=True
            )
            return None

    def get_photos_by_diner_idx(self, diner_idx: int) -> list[dict]:
        """
        diner_idx별로 모든 이미지 조회

        Args:
            diner_idx: 맛집 인덱스

        Returns:
            list[dict]: 이미지 정보 리스트
        """
        try:
            results = self._execute_query_all(GET_PHOTOS_BY_DINER_IDX, (diner_idx,))
            return results if results else []
        except Exception as e:
            logger.warning(f"이미지 목록 조회 실패 (diner_idx={diner_idx}): {e}")
            return []

    def get_top_photos_by_diner_idx(self, diner_idx: int, limit: int = 3) -> list[dict]:
        """
        diner_idx별로 view_count가 높은 상위 N개 이미지 조회

        Args:
            diner_idx: 맛집 인덱스
            limit: 조회할 이미지 개수 (기본값: 3)

        Returns:
            list[dict]: 이미지 정보 리스트 (photo_url, view_count 등)
        """
        try:
            # 기존 쿼리를 재사용하되 LIMIT을 파라미터화
            query = """
                SELECT rp.id, rp.review_id, rp.photo_url, rp.original_photo_id,
                       rp.media_type, rp.status, rp.display_order, rp.view_count, rp.created_at
                FROM review_photos rp
                JOIN kakao_review kr ON rp.review_id = kr.review_id
                JOIN kakao_reviewer krev ON kr.reviewer_id = krev.reviewer_id
                WHERE kr.diner_idx = %s
                ORDER BY rp.view_count DESC, krev.reviewer_review_cnt DESC, rp.display_order ASC
                LIMIT %s
            """
            logger.debug(f"상위 {limit}개 이미지 조회: diner_idx={diner_idx}")
            results = self._execute_query_all(query, (diner_idx, limit))

            if results:
                logger.info(f"이미지 {len(results)}개 선택 완료: diner_idx={diner_idx}")
                return results
            else:
                logger.info(f"이미지 없음: diner_idx={diner_idx}")
                return []
        except Exception as e:
            logger.warning(f"상위 이미지 조회 실패 (diner_idx={diner_idx}): {e}")
            return []

    # BaseService 추상 메서드 구현 (필수이지만 실제로는 사용하지 않을 수 있음)
    def create(self, data, dry_run: bool = False):
        """레코드 생성 (미구현)"""
        raise NotImplementedError("ReviewPhotoService.create is not implemented")

    def get_by_id(self, id_value, dry_run: bool = False):
        """ID로 레코드 조회 (미구현)"""
        raise NotImplementedError("ReviewPhotoService.get_by_id is not implemented")

    def get_list(
        self, skip: int = 0, limit: int = 100, dry_run: bool = False, **filters
    ):
        """레코드 목록 조회 (미구현)"""
        raise NotImplementedError("ReviewPhotoService.get_list is not implemented")

    def update(self, id_value, data, dry_run: bool = False):
        """레코드 업데이트 (미구현)"""
        raise NotImplementedError("ReviewPhotoService.update is not implemented")

    def delete(self, id_value, dry_run: bool = False):
        """레코드 삭제 (미구현)"""
        raise NotImplementedError("ReviewPhotoService.delete is not implemented")

    def _convert_to_response(self, row: dict):
        """데이터베이스 행을 응답 모델로 변환 (미구현)"""
        raise NotImplementedError(
            "ReviewPhotoService._convert_to_response is not implemented"
        )
