"""
카카오 음식점 서비스
"""

import pandas as pd
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


class KakaoDinerService(
    BaseService[KakaoDinerCreate, KakaoDinerUpdate, KakaoDinerResponse]
):
    """카카오 음식점 서비스"""

    def __init__(self):
        super().__init__("kakao_diner", "diner_idx")

    def _calculate_personalization_score(
        self, diner_idx_list: list[int], user_id: str | None = None
    ) -> pd.DataFrame:
        """
        개인화 점수 계산 (미구현)

        Args:
            diner_idx_list: 음식점 인덱스 리스트
            user_id: 사용자 ID (Optional)

        Returns:
            DataFrame with columns: diner_idx, score(personalization_score)
        """
        # TODO: 개인화 로직 구현
        pass
        return pd.DataFrame(columns=["diner_idx", "score"])

    def _calculate_popularity_score(self, diner_df: pd.DataFrame) -> pd.DataFrame:
        """
        인기도 점수 계산 (미구현)

        Args:
            diner_df: 음식점 DataFrame

        Returns:
            DataFrame with columns: diner_idx, score(popularity_score)
        """
        # TODO: 인기도 로직 구현 (리뷰수, 평점 등 종합)
        pass
        return pd.DataFrame(columns=["diner_idx", "score"])

    def _calculate_hidden_gem_score(self, diner_idx_list: list[int]) -> pd.DataFrame:
        """
        숨찐맛 점수 계산 (미구현)

        Args:
            diner_idx_list: 음식점 인덱스 리스트

        Returns:
            DataFrame with columns: diner_idx, score(hidden_gem_score)
        """
        # TODO: 숨찐맛 로직 구현
        pass
        return pd.DataFrame(columns=["diner_idx", "score"])

    def _calculate_bayesian_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        베이지안 평균 점수 계산

        Args:
            df: 음식점 DataFrame (diner_review_avg, diner_review_cnt 포함)

        Returns:
            DataFrame with bayesian_score column added
        """
        # 전체 평균 평점과 평균 리뷰수 계산
        C = df["diner_review_avg"].mean()  # 전체 평균 평점
        m = df["diner_review_cnt"].astype(float).mean()  # 평균 리뷰수

        # 베이지안 평균 계산: (v/(v+m)) * R + (m/(v+m)) * C
        # v: 해당 음식점의 리뷰수, R: 해당 음식점의 평점, m: 평균 리뷰수, C: 전체 평균 평점
        df["bayesian_score"] = (
            df["diner_review_cnt"].astype(float)
            / (df["diner_review_cnt"].astype(float) + m)
        ) * df["diner_review_avg"] + (
            m / (df["diner_review_cnt"].astype(float) + m)
        ) * C

        return df

    def _sort_by_score_or_bayesian(
        self, df: pd.DataFrame, score_df: pd.DataFrame, score_column: str = "score"
    ) -> pd.DataFrame:
        """
        점수 DataFrame이 있으면 해당 점수로 정렬, 없으면 bayesian_score로 정렬

        Args:
            df: 원본 DataFrame
            score_df: 점수 DataFrame (diner_idx, score 컬럼 포함)
            score_column: 정렬에 사용할 점수 컬럼명

        Returns:
            정렬된 DataFrame
        """
        if not score_df.empty:
            df = df.merge(score_df, on="diner_idx", how="left")
            df[score_column] = df[score_column].fillna(0)
            df = df.sort_values(by=[score_column], ascending=False)
        else:
            # 점수가 없으면 bayesian_score로 정렬
            df = self._calculate_bayesian_score(df)
            df = df.sort_values(by=["bayesian_score"], ascending=False)

        return df

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

    def get_list(
        self,
        limit: int | None = None,
        diner_category_large: str | None = None,
        diner_category_middle: str | None = None,
        diner_category_small: str | None = None,
        diner_category_detail: str | None = None,
        min_rating: float | None = None,
        user_lat: float | None = None,
        user_lon: float | None = None,
        radius_km: float | None = None,
        user_id: str | None = None,
        sort_by: str = "rating",  # personalization, popularity, hidden_gem, rating, distance, review_count
    ) -> list[KakaoDinerResponse]:
        """
        카카오 음식점 목록 조회 (필터링 및 정렬)

        Args:
            limit: 반환할 최대 레코드 수 (top-k)
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
            "crawled_at",
            "updated_at",
        ]

        # 거리 계산 추가 (지역 필터가 있는 경우)
        if user_lat is not None and user_lon is not None:
            fields.insert(
                0,
                f"ST_Distance(ST_MakePoint(diner_lon, diner_lat)::geography, ST_MakePoint({user_lon}, {user_lat})::geography) / 1000 AS distance_km",
            )

        conditions = []
        params = []

        # 카테고리 필터
        if diner_category_large:
            conditions.append("diner_category_large LIKE %s")
            params.append(f"%{diner_category_large}%")
        if diner_category_middle:
            conditions.append("diner_category_middle LIKE %s")
            params.append(f"%{diner_category_middle}%")
        if diner_category_small:
            conditions.append("diner_category_small LIKE %s")
            params.append(f"%{diner_category_small}%")
        if diner_category_detail:
            conditions.append("diner_category_detail LIKE %s")
            params.append(f"%{diner_category_detail}%")

        # 평점 필터
        if min_rating is not None:
            conditions.append("diner_review_avg >= %s")
            params.append(min_rating)

        # 지역 필터 (ST_DWithin)
        if user_lat is not None and user_lon is not None and radius_km is not None:
            conditions.append(
                f"ST_DWithin(ST_MakePoint(diner_lon, diner_lat)::geography, "
                f"ST_MakePoint({user_lon}, {user_lat})::geography, {radius_km * 1000})"
            )

        # 쿼리 빌드 (정렬 없이, limit도 나중에 적용)
        query, query_params = self._build_select_query(
            fields,
            conditions,
            order_by=None,  # Python에서 정렬
            limit=None,
            offset=None,
        )

        params.extend(query_params)
        results = self._execute_query_all(query, tuple(params))

        if not results:
            # TODO: 필터 후 없을 경우 대책
            return []

        # 2. 결과를 DataFrame으로 변환
        df = pd.DataFrame(results)

        # 3. 정렬 기준에 따라 필요한 점수만 계산
        diner_idx_list = df["diner_idx"].tolist()

        if sort_by == "personalization":
            # 개인화 점수 계산 및 정렬
            personalization_df = self._calculate_personalization_score(
                diner_idx_list, user_id
            )
            df = self._sort_by_score_or_bayesian(df, personalization_df)

        elif sort_by == "popularity":
            # 인기도 점수 계산 및 정렬
            popularity_df = self._calculate_popularity_score(df)
            df = self._sort_by_score_or_bayesian(df, popularity_df)

        elif sort_by == "hidden_gem":
            # 숨찐맛 점수 계산 및 정렬
            hidden_gem_df = self._calculate_hidden_gem_score(diner_idx_list)
            df = self._sort_by_score_or_bayesian(df, hidden_gem_df)

        elif sort_by == "rating":
            # 평점순 정렬
            df = df.sort_values(by=["diner_review_avg"], ascending=False)

        elif sort_by == "review_count":
            # 리뷰수순 정렬
            df = df.sort_values(by=["diner_review_cnt"], ascending=False)

        elif sort_by == "distance":
            # 거리순 정렬 (거리 정보가 있는 경우만)
            if "distance_km" in df.columns:
                df = df.sort_values(by=["distance_km"], ascending=True)
            else:
                # 거리 정보가 없으면 평점순으로 대체
                df = df.sort_values(by=["diner_review_avg"], ascending=False)

        else:
            # 기본값: 평점순
            df = df.sort_values(by=["diner_review_avg"], ascending=False)

        # 4. top-k 적용 (limit이 None이면 전체 반환)
        if limit is not None:
            df = df.head(limit)

        # 5. Response 모델로 변환
        return [self._convert_to_response(row.to_dict()) for _, row in df.iterrows()]

    def update(self, diner_idx: int, data: KakaoDinerUpdate) -> KakaoDinerResponse:
        """카카오 음식점 정보 업데이트"""
        # 음식점 존재 확인
        if not self._check_exists(CHECK_KAKAO_DINER_EXISTS_BY_IDX, (diner_idx,)):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Kakao diner not found",
            )

        # 업데이트할 필드와 값 구성
        update_values = []
        field_mapping = {
            "diner_name": data.diner_name,
            "diner_tag": data.diner_tag,
            "diner_menu_name": data.diner_menu_name,
            "diner_menu_price": data.diner_menu_price,
            "diner_review_cnt": data.diner_review_cnt,
            "diner_review_avg": data.diner_review_avg,
            "diner_blog_review_cnt": data.diner_blog_review_cnt,
            "diner_review_tags": data.diner_review_tags,
            "diner_road_address": data.diner_road_address,
            "diner_num_address": data.diner_num_address,
            "diner_phone": data.diner_phone,
            "diner_lat": data.diner_lat,
            "diner_lon": data.diner_lon,
        }

        for field, value in field_mapping.items():
            if value is not None:
                update_values.append(value)

        # diner_idx를 마지막에 추가
        update_values.append(diner_idx)

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
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )
