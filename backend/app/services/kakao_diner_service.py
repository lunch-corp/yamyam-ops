"""
카카오 음식점 서비스
"""

from typing import List, Optional

from app.core.db import db
from app.database.kakao_queries import (
    CHECK_KAKAO_DINER_EXISTS_BY_IDX,
    DELETE_KAKAO_DINER_BY_IDX,
    GET_ALL_KAKAO_DINERS,
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
from fastapi import HTTPException, status


class KakaoDinerService(
    BaseService[KakaoDinerCreate, KakaoDinerUpdate, KakaoDinerResponse]
):
    """카카오 음식점 서비스"""

    def __init__(self):
        super().__init__("kakao_diner", "diner_idx")

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
        skip: int = 0,
        limit: int = 100,
        diner_tag: Optional[str] = None,
        min_rating: Optional[float] = None,
    ) -> List[KakaoDinerResponse]:
        """카카오 음식점 목록 조회"""
        # 필터링이 필요한 경우 동적 쿼리 사용, 그렇지 않으면 정적 쿼리 사용
        if diner_tag or min_rating is not None:
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
                "crawled_at",
                "updated_at",
            ]

            conditions = []
            params = []

            if diner_tag:
                conditions.append("diner_tag LIKE %s")
                params.append(f"%{diner_tag}%")

            if min_rating is not None:
                conditions.append("diner_review_avg >= %s")
                params.append(min_rating)

            query, query_params = self._build_select_query(
                fields,
                conditions,
                order_by="diner_review_avg DESC NULLS LAST, diner_blog_review_cnt DESC",
                limit=limit,
                offset=skip,
            )

            params.extend(query_params)
            results = self._execute_query_all(query, tuple(params))
        else:
            # 필터링이 없는 경우 정적 쿼리 사용
            results = self._execute_query_all(GET_ALL_KAKAO_DINERS, (limit, skip))

        return [self._convert_to_response(row) for row in results]

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
            crawled_at=row["crawled_at"].isoformat(),
            updated_at=row["updated_at"].isoformat(),
        )
