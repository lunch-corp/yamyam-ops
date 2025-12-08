"""
카카오 음식점 서비스
"""

import logging
import random

from fastapi import HTTPException, status

from app.core.db import db
from app.database.kakao_queries import (
    CHECK_KAKAO_DINER_EXISTS_BY_IDX,
    DELETE_KAKAO_DINER_BY_IDX,
    GET_KAKAO_DINER_BY_IDX,
    INSERT_KAKAO_DINER_BASIC,
    UPDATE_KAKAO_DINER_BY_IDX,
)
from app.schemas.kakao_diner import (
    KakaoDinerCreate,
    KakaoDinerResponse,
    KakaoDinerUpdate,
)
from app.services.base_service import BaseService

logger = logging.getLogger(__name__)


class KakaoDinerService(
    BaseService[KakaoDinerCreate, KakaoDinerUpdate, KakaoDinerResponse]
):
    """카카오 음식점 서비스"""

    def __init__(self):
        super().__init__("kakao_diner", "diner_idx")

    def get_category_statistics(
        self, category_type: str, parent_category: str = None
    ) -> list[dict]:
        """
        카테고리별 음식점 수 통계 조회

        Args:
            category_type: "large" 또는 "middle"
            parent_category: 중분류 조회 시 대분류 카테고리명

        Returns:
            카테고리별 음식점 수 리스트
        """
        if category_type == "large":
            query = """
                SELECT diner_category_large as name, COUNT(*) as diner_count
                FROM kakao_diner
                WHERE diner_category_large IS NOT NULL
                GROUP BY diner_category_large
                ORDER BY diner_count DESC
            """
            results = self._execute_query_all(query, ())
        elif category_type == "middle":
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="parent_category is required for middle category statistics",
                )
            query = """
                SELECT diner_category_middle as name, COUNT(*) as diner_count
                FROM kakao_diner
                WHERE diner_category_large = %s
                  AND diner_category_middle IS NOT NULL
                GROUP BY diner_category_middle
                ORDER BY diner_count DESC
            """
            results = self._execute_query_all(query, (parent_category,))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="category_type must be 'large' or 'middle'",
            )

        return [
            {"name": row["name"], "count": int(row["diner_count"])} for row in results
        ]

    def create(self, data: KakaoDinerCreate) -> KakaoDinerResponse:
        """카카오 음식점 생성"""
        try:
            with db.get_cursor() as (cursor, conn):
                # INSERT_KAKAO_DINER_BASIC은 ON CONFLICT로 UPSERT 처리
                # ULID는 DB에서 자동 생성되거나 기존 레코드 업데이트
                cursor.execute(
                    INSERT_KAKAO_DINER_BASIC,
                    (
                        data.diner_idx,
                        data.diner_name,
                        data.diner_tag,
                        data.diner_menu_name,
                        data.diner_menu_price,
                        data.diner_review_cnt,
                        data.diner_review_avg,
                        data.diner_blog_review_cnt,
                        data.diner_review_tags,
                        data.diner_road_address,
                        data.diner_num_address,
                        data.diner_phone,
                        data.diner_lat,
                        data.diner_lon,
                        None,  # diner_open_time (optional)
                        data.diner_grade,  # diner_grade (optional)
                        data.hidden_score,  # hidden_score (optional)
                        data.bayesian_score,  # bayesian_score (optional)
                    ),
                )

                # 생성된 데이터 조회
                cursor.execute(GET_KAKAO_DINER_BY_IDX, (data.diner_idx,))
                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao diner", e)

    def get_by_id(self, diner_idx: int) -> KakaoDinerResponse:
        """카카오 음식점 상세 조회 (diner_idx 기준)"""
        result = self._execute_query(GET_KAKAO_DINER_BY_IDX, (diner_idx,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao diner not found",
            )

        return self._convert_to_response(result)

    def get_list_filtered(
        self,
        limit: int | None = None,
        offset: int | None = None,
        diner_category_large: str | None = None,
        diner_category_middle: str | None = None,
        diner_category_small: str | None = None,
        diner_category_detail: str | None = None,
        min_rating: float | None = None,
        user_lat: float | None = None,
        user_lon: float | None = None,
        radius_km: float | None = None,
        n: int | None = None,
    ) -> list[KakaoDinerResponse]:
        """
        카카오 음식점 목록 조회 (필터링 및 정렬)

        Args:
            limit: 반환할 최대 레코드 수 (top-k, n이 None일 때만 적용)
            offset: 페이지네이션 오프셋 (None이면 0으로 처리)
            diner_category_large: 대분류 카테고리 필터
            diner_category_middle: 중분류 카테고리 필터
            diner_category_small: 소분류 카테고리 필터
            diner_category_detail: 세부 카테고리 필터
            min_rating: 최소 평점 필터
            user_lat: 사용자 위도 (거리 필터용)
            user_lon: 사용자 경도 (거리 필터용)
            radius_km: 반경 (km) - 기본 필터
            n: 랜덤 샘플링 개수 (지정 시 필터링된 결과에서 n개 랜덤 샘플링, None이면 샘플링 안 함)

        Returns:
            음식점 목록
        """
        # 1. SQL 쿼리로 기본 필터링 수행
        fields = [
            "id",
            "diner_idx",
            "diner_name",
            "diner_tag",
            "diner_menu_name",
            "diner_menu_price",
            "diner_review_cnt",
            "diner_review_avg",
            "diner_blog_review_cnt",
            "diner_review_tags",
            "diner_road_address",
            "diner_num_address",
            "diner_phone",
            "diner_lat",
            "diner_lon",
            "diner_open_time",
            "diner_category_large",
            "diner_category_middle",
            "diner_category_small",
            "diner_category_detail",
            "diner_grade",
            "hidden_score",
            "bayesian_score",
            "crawled_at",
            "updated_at",
        ]

        conditions = []
        params = []

        # 카테고리 필터 (정확한 매칭으로 인덱스 활용)
        if diner_category_large:
            conditions.append("diner_category_large = %s")
            params.append(diner_category_large)
        if diner_category_middle:
            conditions.append("diner_category_middle = %s")
            params.append(diner_category_middle)
        if diner_category_small:
            conditions.append("diner_category_small = %s")
            params.append(diner_category_small)
        if diner_category_detail:
            conditions.append("diner_category_detail = %s")
            params.append(diner_category_detail)

        # 평점 필터
        if min_rating is not None:
            conditions.append("diner_review_avg >= %s")
            params.append(min_rating)

        # 지역 필터 (ST_DWithin with geography - 정확한 미터 단위)
        if user_lat is not None and user_lon is not None and radius_km is not None:
            conditions.append(
                f"ST_DWithin(ST_SetSRID(ST_MakePoint(diner_lon, diner_lat), 4326)::geography, "
                f"ST_SetSRID(ST_MakePoint({user_lon}, {user_lat}), 4326)::geography, {radius_km * 1000})"
            )

        # 2. 쿼리 빌드
        # n이 지정되면, 필터링된 모든 결과를 가져온 후 Python에서 샘플링
        # n이 None이면 기본 정렬(bayesian_score DESC) 적용
        query_limit = None if n else limit
        order_by = "bayesian_score DESC" if not n else None
        query, query_params = self._build_select_query(
            fields,
            conditions,
            order_by=order_by,
            limit=query_limit,
            offset=offset if offset is not None else 0,
        )

        params.extend(query_params)
        results = self._execute_query_all(query, tuple(params))

        if not results:
            return []

        # 3. 랜덤 샘플링 처리
        if n and len(results) > n:
            results = random.sample(results, n)
        elif n and len(results) <= n:
            # 결과가 n개 이하면 그대로 반환
            pass

        # 4. Response 모델로 변환
        logger.debug(f"results: {len(results)}")
        return [self._convert_to_response(row) for row in results]

    def get_list_sorted(
        self,
        diner_ids: list[str],
        user_id: str | None = None,
        sort_by: str = "rating",
        min_rating: float | None = None,
        user_lat: float | None = None,
        user_lon: float | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[KakaoDinerResponse]:
        """
        음식점 ID 리스트를 받아서 정렬 및 필터링 수행

        Args:
            diner_ids: 음식점 ID 리스트 (ULID)
            user_id: 사용자 ID (개인화 정렬용)
            sort_by: 정렬 기준 (personalization, popularity, hidden_gem, rating, distance, review_count)
            min_rating: 최소 평점 필터
            user_lat: 사용자 위도 (거리 정렬용)
            user_lon: 사용자 경도 (거리 정렬용)
            limit: 반환할 최대 레코드 수
            offset: 페이지네이션 오프셋

        Returns:
            정렬된 음식점 목록
        """
        if not diner_ids:
            return []

        # 1. SQL 쿼리로 ID 리스트 기반 조회
        fields = [
            "id",
            "diner_idx",
            "diner_name",
            "diner_tag",
            "diner_menu_name",
            "diner_menu_price",
            "diner_review_cnt",
            "diner_review_avg",
            "diner_blog_review_cnt",
            "diner_review_tags",
            "diner_road_address",
            "diner_num_address",
            "diner_phone",
            "diner_lat",
            "diner_lon",
            "diner_open_time",
            "diner_category_large",
            "diner_category_middle",
            "diner_category_small",
            "diner_category_detail",
            "diner_grade",
            "hidden_score",
            "bayesian_score",
            "crawled_at",
            "updated_at",
        ]

        # 거리 계산이 필요한 경우 (distance 정렬)
        if user_lat is not None and user_lon is not None:
            fields.insert(
                0,
                f"ST_Distance(ST_SetSRID(ST_MakePoint(diner_lon, diner_lat), 4326)::geography, "
                f"ST_SetSRID(ST_MakePoint({user_lon}, {user_lat}), 4326)::geography) / 1000 AS distance_km",
            )

        conditions = []
        params = []

        # ID 리스트 필터 (IN 절 사용)
        placeholders = ", ".join(["%s"] * len(diner_ids))
        conditions.append(f"id IN ({placeholders})")
        params.extend(diner_ids)

        # 평점 필터
        if min_rating is not None:
            conditions.append("diner_review_avg >= %s")
            params.append(min_rating)

        # 2. ORDER BY 구성 (SQL에서 정렬)
        order_by_clause = None

        if sort_by == "personalization":
            # 개인화는 아직 미구현이므로 bayesian_score로 대체
            order_by_clause = "bayesian_score DESC"

        elif sort_by == "popularity":
            # 인기도 = bayesian_score
            order_by_clause = "bayesian_score DESC"

        elif sort_by == "hidden_gem":
            # 숨찐맛 = hidden_score
            order_by_clause = "hidden_score DESC"

        elif sort_by == "rating":
            # 평점순
            order_by_clause = "diner_review_avg DESC"

        elif sort_by == "review_count":
            # 리뷰수순 (문자열이므로 숫자로 변환하여 정렬)
            order_by_clause = "CAST(diner_review_cnt AS INTEGER) DESC"

        elif sort_by == "distance":
            # 거리순 (거리 계산이 있는 경우만)
            if user_lat is not None and user_lon is not None:
                order_by_clause = "distance_km ASC"
            else:
                order_by_clause = "diner_review_avg DESC"  # 대체

        else:
            # 기본값: 평점순
            order_by_clause = "diner_review_avg DESC"

        # 3. 쿼리 빌드 (SQL에서 정렬 및 limit/offset 적용)
        query, query_params = self._build_select_query(
            fields,
            conditions,
            order_by=order_by_clause,
            limit=limit,
            offset=offset if offset is not None else 0,
        )

        params.extend(query_params)
        results = self._execute_query_all(query, tuple(params))

        if not results:
            return []

        # 4. Response 모델로 변환
        logger.debug(f"results: {len(results)}")
        return [self._convert_to_response(row) for row in results]

    def get_list(
        self,
        limit: int | None = None,
        offset: int | None = None,
        diner_category_large: str | None = None,
        diner_category_middle: str | None = None,
        diner_category_small: str | None = None,
        diner_category_detail: str | None = None,
        min_rating: float | None = None,
        user_lat: float | None = None,
        user_lon: float | None = None,
        radius_km: float | None = None,
        user_id: str | None = None,
        sort_by: str = "popularity",  # personalization, popularity, hidden_gem, rating, distance, review_count
        use_dataframe: bool = False,
    ) -> list[KakaoDinerResponse]:
        """
        카카오 음식점 목록 조회 (필터링 및 정렬)

        Args:
            limit: 반환할 최대 레코드 수 (top-k)
            offset: 페이지네이션 오프셋 (None이면 0으로 처리)
            diner_category_large: 대분류 카테고리 필터 (기본 필터)
            diner_category_middle: 중분류 카테고리 필터 (기본 필터)
            diner_category_small: 소분류 카테고리 필터 (기본 필터)
            diner_category_detail: 세부 카테고리 필터 (기본 필터)
            min_rating: 최소 평점 필터
            user_lat: 사용자 위도 (거리 필터 및 정렬용)
            user_lon: 사용자 경도 (거리 필터 및 정렬용)
            radius_km: 반경 (km) - 기본 필터
            user_id: 사용자 ID (개인화 정렬용)
            sort_by: 정렬 기준 (personalization, popularity, hidden_gem, rating, distance, review_count 중 하나)
            use_dataframe: pandas dataframe 사용 여부

        Returns:
            음식점 목록
        """
        # 1. SQL 쿼리로 기본 필터링 수행
        fields = [
            "id",
            "diner_idx",
            "diner_name",
            "diner_tag",
            "diner_menu_name",
            "diner_menu_price",
            "diner_review_cnt",
            "diner_review_avg",
            "diner_blog_review_cnt",
            "diner_review_tags",
            "diner_road_address",
            "diner_num_address",
            "diner_phone",
            "diner_lat",
            "diner_lon",
            "diner_open_time",
            "diner_category_large",
            "diner_category_middle",
            "diner_category_small",
            "diner_category_detail",
            "diner_grade",
            "hidden_score",
            "bayesian_score",
            "crawled_at",
            "updated_at",
        ]

        # 거리 계산이 필요한 경우 (distance 정렬 또는 거리 필터)
        if user_lat is not None and user_lon is not None:
            fields.insert(
                0,
                f"ST_Distance(ST_SetSRID(ST_MakePoint(diner_lon, diner_lat), 4326)::geography, "
                f"ST_SetSRID(ST_MakePoint({user_lon}, {user_lat}), 4326)::geography) / 1000 AS distance_km",
            )

        conditions = []
        params = []

        # 카테고리 필터 (정확한 매칭으로 인덱스 활용)
        if diner_category_large:
            conditions.append("diner_category_large = %s")
            params.append(diner_category_large)
        if diner_category_middle:
            conditions.append("diner_category_middle = %s")
            params.append(diner_category_middle)
        if diner_category_small:
            conditions.append("diner_category_small = %s")
            params.append(diner_category_small)
        if diner_category_detail:
            conditions.append("diner_category_detail = %s")
            params.append(diner_category_detail)

        # 평점 필터
        if min_rating is not None:
            conditions.append("diner_review_avg >= %s")
            params.append(min_rating)

        # 지역 필터 (ST_DWithin with geography - 정확한 미터 단위)
        if user_lat is not None and user_lon is not None and radius_km is not None:
            conditions.append(
                f"ST_DWithin(ST_SetSRID(ST_MakePoint(diner_lon, diner_lat), 4326)::geography, "
                f"ST_SetSRID(ST_MakePoint({user_lon}, {user_lat}), 4326)::geography, {radius_km * 1000})"
            )

        # 2. ORDER BY 구성 (SQL에서 정렬)
        order_by_clause = None

        if sort_by == "personalization":
            # 개인화는 아직 미구현이므로 bayesian_score로 대체
            order_by_clause = "bayesian_score DESC"

        elif sort_by == "popularity":
            # 인기도 = bayesian_score
            order_by_clause = "bayesian_score DESC"

        elif sort_by == "hidden_gem":
            # 숨찐맛 = hidden_score
            order_by_clause = "hidden_score DESC"

        elif sort_by == "rating":
            # 평점순
            order_by_clause = "diner_review_avg DESC"

        elif sort_by == "review_count":
            # 리뷰수순 (문자열이므로 숫자로 변환하여 정렬)
            order_by_clause = "CAST(diner_review_cnt AS INTEGER) DESC"

        elif sort_by == "distance":
            # 거리순 (거리 계산이 있는 경우만)
            if user_lat is not None and user_lon is not None:
                order_by_clause = "distance_km ASC"
            else:
                order_by_clause = "diner_review_avg DESC"  # 대체

        else:
            # 기본값: 평점순
            order_by_clause = "diner_review_avg DESC"

        # 3. 쿼리 빌드 (SQL에서 정렬 및 limit/offset 적용)
        query, query_params = self._build_select_query(
            fields,
            conditions,
            order_by=order_by_clause,  # SQL에서 정렬
            limit=limit,
            offset=offset if offset is not None else 0,
        )

        params.extend(query_params)
        results = self._execute_query_all(query, tuple(params))

        if not results:
            return []

        # 5. Response 모델로 변환
        logger.debug(f"results: {len(results)}")

        return (
            [self._convert_to_response(row) for row in results]
            if not use_dataframe
            else results
        )

    def update(self, diner_idx: int, data: KakaoDinerUpdate) -> KakaoDinerResponse:
        """카카오 음식점 정보 업데이트"""
        # 음식점 존재 확인
        if not self._check_exists(CHECK_KAKAO_DINER_EXISTS_BY_IDX, (diner_idx,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao diner not found",
            )

        # 업데이트할 필드와 값 구성 (쿼리 순서대로)
        update_values = [
            data.diner_name,
            data.diner_tag,
            data.diner_menu_name,
            data.diner_menu_price,
            data.diner_review_cnt,
            data.diner_review_avg,
            data.diner_blog_review_cnt,
            data.diner_review_tags,
            data.diner_road_address,
            data.diner_num_address,
            data.diner_phone,
            data.diner_lat,
            data.diner_lon,
            data.diner_grade,
            data.hidden_score,
            data.bayesian_score,
            diner_idx,  # WHERE 조건
        ]

        result = self._execute_query(UPDATE_KAKAO_DINER_BY_IDX, tuple(update_values))
        return self._convert_to_response(result)

    def delete(self, diner_idx: int) -> dict:
        """카카오 음식점 삭제"""
        result = self._execute_query(DELETE_KAKAO_DINER_BY_IDX, (diner_idx,))
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao diner not found",
            )

        return {"message": "Kakao diner deleted successfully"}

    def _convert_to_response(self, row: dict) -> KakaoDinerResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return KakaoDinerResponse(
            id=row["id"],
            diner_idx=row["diner_idx"],
            diner_name=row["diner_name"],
            diner_tag=row.get("diner_tag"),
            diner_menu_name=row.get("diner_menu_name"),
            diner_menu_price=row.get("diner_menu_price"),
            diner_review_cnt=row["diner_review_cnt"],
            diner_review_avg=row["diner_review_avg"],
            diner_blog_review_cnt=row["diner_blog_review_cnt"],
            diner_review_tags=row.get("diner_review_tags"),
            diner_road_address=row.get("diner_road_address"),
            diner_num_address=row.get("diner_num_address"),
            diner_phone=row.get("diner_phone"),
            diner_lat=row["diner_lat"],
            diner_lon=row["diner_lon"],
            diner_category_large=row.get("diner_category_large"),
            diner_category_middle=row.get("diner_category_middle"),
            diner_category_small=row.get("diner_category_small"),
            diner_category_detail=row.get("diner_category_detail"),
            diner_grade=row.get("diner_grade"),
            hidden_score=row.get("hidden_score"),
            bayesian_score=row.get("bayesian_score"),
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )
