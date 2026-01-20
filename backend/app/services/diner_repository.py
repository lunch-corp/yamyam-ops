"""
Diner Repository

DEPRECATED: 이 파일은 더 이상 사용되지 않습니다.
대신 KakaoDinerService를 직접 사용하세요.

DB 조회만 수행하는 간단한 Repository Pattern 구현
"""

import logging
import warnings
from typing import Any

from app.services.kakao_diner_service import KakaoDinerService

logger = logging.getLogger(__name__)

# Deprecation warning
warnings.warn(
    "DinerRepository is deprecated. Use KakaoDinerService directly instead.",
    DeprecationWarning,
    stacklevel=2,
)


class DinerRepository:
    """
    맛집 데이터 조회 Repository (DEPRECATED)

    PostgreSQL DB 조회만 수행 (KakaoDinerService)
    """

    def __init__(self):
        """
        Args:
            None (GCS fallback 제거됨)
        """
        self.db_service = KakaoDinerService()

    def get_recommendations(
        self, filters: dict[str, Any], use_fallback: bool = True
    ) -> list[dict[str, Any]]:
        """
        맛집 추천 조회 (DB만)

        Args:
            filters: 필터 조건
                - limit: 반환 개수
                - diner_category_large: 대분류 카테고리 리스트
                - diner_category_middle: 중분류 카테고리 리스트
                - min_review_count: 최소 리뷰 개수
                - user_lat, user_lon, radius_km: 위치 기반 필터
                - n: 랜덤 샘플링 개수
            use_fallback: (사용하지 않음, 호환성 유지)

        Returns:
            list[dict]: 맛집 리스트

        Example:
            >>> repo = DinerRepository()
            >>> filters = {
            ...     "limit": 5,
            ...     "diner_category_large": ["한식", "일식"],
            ...     "min_review_count": 50
            ... }
            >>> diners = repo.get_recommendations(filters)
        """
        try:
            logger.debug(f"DB 조회 시도: {filters}")
            results = self.db_service.get_list_filtered(**filters)

            if results:
                logger.info(f"DB 조회 성공: {len(results)}개")
                return self._convert_filtered_to_full(results)

            logger.warning("DB 조회 결과가 없음")

        except Exception as e:
            logger.error(f"DB 조회 실패: {e}")

        return []

    def get_by_diner_idx(
        self, diner_idx: int, use_fallback: bool = True
    ) -> dict[str, Any] | None:
        """
        diner_idx로 특정 맛집 조회

        Args:
            diner_idx: 맛집 인덱스
            use_fallback: (사용하지 않음, 호환성 유지)

        Returns:
            dict | None: 맛집 정보 또는 None
        """
        try:
            logger.debug(f"DB 조회 시도: diner_idx={diner_idx}")
            result = self.db_service.get_by_id(diner_idx)

            if result:
                logger.info(f"DB 조회 성공: {diner_idx}")
                return result.model_dump() if hasattr(result, "model_dump") else result

        except Exception as e:
            logger.error(f"DB 조회 실패: diner_idx={diner_idx} - {e}")

        logger.warning(f"맛집을 찾을 수 없음: diner_idx={diner_idx}")
        return None

    def search_diners(
        self, query: str, limit: int = 10, use_fallback: bool = False
    ) -> list[dict[str, Any]]:
        """
        맛집 이름으로 검색

        Args:
            query: 검색어
            limit: 반환 개수
            use_fallback: (사용하지 않음, 호환성 유지)

        Returns:
            list[dict]: 검색 결과
        """
        try:
            logger.debug(f"맛집 검색: query={query}, limit={limit}")
            results = self.db_service.search_diners(query=query, limit=limit)

            if results:
                logger.info(f"검색 성공: {len(results)}개")
                return [
                    r.model_dump() if hasattr(r, "model_dump") else r for r in results
                ]

        except Exception as e:
            logger.error(f"검색 실패: {e}")

        return []

    def get_category_statistics(
        self, category_type: str = "large", parent_category: str | None = None
    ) -> list[dict[str, Any]]:
        """
        카테고리별 통계 조회

        Args:
            category_type: "large" 또는 "middle"
            parent_category: 중분류 조회 시 대분류 카테고리명

        Returns:
            list[dict]: 카테고리별 통계
        """
        try:
            logger.debug(f"카테고리 통계 조회: {category_type}")
            results = self.db_service.get_category_statistics(
                category_type, parent_category
            )

            if results:
                logger.info(f"통계 조회 성공: {len(results)}개")
                return results

        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")

        return []

    def _convert_filtered_to_full(self, filtered_results: list) -> list[dict[str, Any]]:
        """
        FilteredDinerResponse를 전체 정보로 변환

        Args:
            filtered_results: get_list_filtered() 결과 (id, diner_idx, distance만 포함)

        Returns:
            list[dict]: 전체 맛집 정보 리스트
        """
        full_results = []

        for item in filtered_results:
            try:
                # FilteredDinerResponse는 id, diner_idx, distance만 포함
                # 전체 정보를 조회하려면 get_by_id() 호출 필요
                diner_idx = (
                    item.diner_idx
                    if hasattr(item, "diner_idx")
                    else item.get("diner_idx")
                )

                if diner_idx:
                    full_info = self.db_service.get_by_id(diner_idx)
                    if full_info:
                        full_dict = (
                            full_info.model_dump()
                            if hasattr(full_info, "model_dump")
                            else full_info
                        )
                        full_results.append(full_dict)

            except Exception as e:
                logger.warning(f"전체 정보 조회 실패: {e}")
                # 실패해도 계속 진행
                continue

        return full_results

    def health_check(self) -> dict[str, Any]:
        """
        Repository 상태 확인

        Returns:
            dict: 상태 정보
        """
        status = {
            "db": "unknown",
            "fallback_enabled": False,
        }

        # DB 상태 확인
        try:
            self.db_service.get_category_statistics("large")
            status["db"] = "healthy"
        except Exception as e:
            status["db"] = f"unhealthy: {str(e)[:100]}"

        return status
