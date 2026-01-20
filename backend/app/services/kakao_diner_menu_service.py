"""
카카오 음식점 메뉴 서비스
"""

import logging

from fastapi import HTTPException, status

from app.core.db import db
from app.database.kakao_queries import (
    COUNT_KAKAO_DINER_MENUS,
    COUNT_KAKAO_DINER_MENUS_BY_DINER_IDX,
    DELETE_KAKAO_DINER_MENU_BY_ID,
    GET_KAKAO_DINER_MENU_BY_ID,
    GET_KAKAO_DINER_MENUS_BASE,
    GET_KAKAO_DINER_MENUS_BY_DINER_IDX,
    INSERT_KAKAO_DINER_MENU,
    UPDATE_KAKAO_DINER_MENU_BY_ID,
)
from app.schemas.kakao_diner_menu import (
    KakaoDinerMenuCreate,
    KakaoDinerMenuResponse,
    KakaoDinerMenuUpdate,
)
from app.services.base_service import BaseService
from app.utils.ulid_utils import generate_ulid

logger = logging.getLogger(__name__)


class KakaoDinerMenuService(
    BaseService[KakaoDinerMenuCreate, KakaoDinerMenuUpdate, KakaoDinerMenuResponse]
):
    """카카오 음식점 메뉴 서비스"""

    def __init__(self):
        super().__init__("kakao_diner_menus", "id")

    def create(
        self, data: KakaoDinerMenuCreate, dry_run: bool = False
    ) -> KakaoDinerMenuResponse:
        """메뉴 생성"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Creating menu: {data.name}")
                return KakaoDinerMenuResponse(
                    id="dry_run_id",
                    diner_idx=data.diner_idx,
                    name=data.name,
                    product_id=data.product_id,
                    price=data.price,
                    is_ai_mate=data.is_ai_mate,
                    photo_url=data.photo_url,
                    is_recommend=data.is_recommend,
                    desc=data.desc,
                    mod_at=data.mod_at,
                    created_at="2024-01-01T00:00:00",
                    updated_at="2024-01-01T00:00:00",
                )

            with db.get_cursor() as (cursor, conn):
                ulid = generate_ulid()
                cursor.execute(
                    INSERT_KAKAO_DINER_MENU,
                    (
                        ulid,
                        data.diner_idx,
                        data.name,
                        data.product_id,
                        data.price,
                        data.is_ai_mate,
                        data.photo_url,
                        data.is_recommend,
                        data.desc,
                        data.mod_at,
                    ),
                )

                # 생성된 데이터 조회
                cursor.execute(GET_KAKAO_DINER_MENU_BY_ID, (ulid,))
                result = cursor.fetchone()
                conn.commit()

                return self._convert_to_response(result)

        except Exception as e:
            self._handle_exception("creating kakao diner menu", e)

    def get_by_id(self, menu_id: str, dry_run: bool = False) -> KakaoDinerMenuResponse:
        """메뉴 ID로 조회"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Getting menu by id: {menu_id}")
                return None

            with db.get_cursor() as (cursor, conn):
                cursor.execute(GET_KAKAO_DINER_MENU_BY_ID, (menu_id,))
                result = cursor.fetchone()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Menu with id {menu_id} not found",
                    )

                return self._convert_to_response(result)

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("getting kakao diner menu by id", e)

    def get_list(
        self,
        diner_idx: int | None = None,
        is_recommend: bool | None = None,
        is_ai_mate: bool | None = None,
        limit: int | None = None,
        offset: int | None = None,
        dry_run: bool = False,
        **filters,
    ) -> list[KakaoDinerMenuResponse]:
        """메뉴 목록 조회 (필터링 지원)"""
        try:
            if dry_run:
                logger.info(
                    f"[DRY RUN] Getting menu list with filters: diner_idx={diner_idx}, "
                    f"is_recommend={is_recommend}, is_ai_mate={is_ai_mate}"
                )
                return []

            # diner_idx가 지정된 경우 최적화된 쿼리 사용
            if diner_idx is not None and is_recommend is None and is_ai_mate is None:
                with db.get_cursor() as (cursor, conn):
                    cursor.execute(GET_KAKAO_DINER_MENUS_BY_DINER_IDX, (diner_idx,))
                    results = cursor.fetchall()
                    return [self._convert_to_response(row) for row in results]

            # 동적 필터링 쿼리 구성
            query = GET_KAKAO_DINER_MENUS_BASE
            conditions = []
            params = []

            if diner_idx is not None:
                conditions.append("diner_idx = %s")
                params.append(diner_idx)

            if is_recommend is not None:
                conditions.append("is_recommend = %s")
                params.append(is_recommend)

            if is_ai_mate is not None:
                conditions.append("is_ai_mate = %s")
                params.append(is_ai_mate)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            # 정렬
            query += " ORDER BY is_recommend DESC NULLS LAST, name"

            # 페이지네이션
            if limit is not None:
                query += " LIMIT %s"
                params.append(limit)

            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)

            with db.get_cursor() as (cursor, conn):
                cursor.execute(query, tuple(params))
                results = cursor.fetchall()
                return [self._convert_to_response(row) for row in results]

        except Exception as e:
            self._handle_exception("getting kakao diner menu list", e)

    def update(
        self, menu_id: str, data: KakaoDinerMenuUpdate, dry_run: bool = False
    ) -> KakaoDinerMenuResponse:
        """메뉴 업데이트"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Updating menu: {menu_id}")
                return None

            # 기존 메뉴 조회
            existing_menu = self.get_by_id(menu_id)

            # 업데이트할 필드 결정 (None이 아닌 값만)
            update_data = {
                "diner_idx": data.diner_idx
                if data.diner_idx is not None
                else existing_menu.diner_idx,
                "name": data.name if data.name is not None else existing_menu.name,
                "product_id": data.product_id
                if data.product_id is not None
                else existing_menu.product_id,
                "price": data.price if data.price is not None else existing_menu.price,
                "is_ai_mate": data.is_ai_mate
                if data.is_ai_mate is not None
                else existing_menu.is_ai_mate,
                "photo_url": data.photo_url
                if data.photo_url is not None
                else existing_menu.photo_url,
                "is_recommend": data.is_recommend
                if data.is_recommend is not None
                else existing_menu.is_recommend,
                "desc": data.desc if data.desc is not None else existing_menu.desc,
                "mod_at": data.mod_at
                if data.mod_at is not None
                else existing_menu.mod_at,
            }

            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    UPDATE_KAKAO_DINER_MENU_BY_ID,
                    (
                        update_data["diner_idx"],
                        update_data["name"],
                        update_data["product_id"],
                        update_data["price"],
                        update_data["is_ai_mate"],
                        update_data["photo_url"],
                        update_data["is_recommend"],
                        update_data["desc"],
                        update_data["mod_at"],
                        menu_id,
                    ),
                )
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Menu with id {menu_id} not found",
                    )

                return self._convert_to_response(result)

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("updating kakao diner menu", e)

    def delete(self, menu_id: str, dry_run: bool = False) -> dict[str, str]:
        """메뉴 삭제"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Deleting menu: {menu_id}")
                return {"message": f"[DRY RUN] Menu {menu_id} would be deleted"}

            with db.get_cursor() as (cursor, conn):
                cursor.execute(DELETE_KAKAO_DINER_MENU_BY_ID, (menu_id,))
                result = cursor.fetchone()
                conn.commit()

                if not result:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Menu with id {menu_id} not found",
                    )

                return {"message": f"Menu {menu_id} deleted successfully"}

        except HTTPException:
            raise
        except Exception as e:
            self._handle_exception("deleting kakao diner menu", e)

    def get_count(self, diner_idx: int | None = None) -> int:
        """메뉴 개수 조회"""
        try:
            with db.get_cursor() as (cursor, conn):
                if diner_idx is not None:
                    cursor.execute(COUNT_KAKAO_DINER_MENUS_BY_DINER_IDX, (diner_idx,))
                else:
                    cursor.execute(COUNT_KAKAO_DINER_MENUS)
                result = cursor.fetchone()
                return result["count"] if result else 0

        except Exception as e:
            self._handle_exception("counting kakao diner menus", e)

    def _convert_to_response(self, row: dict) -> KakaoDinerMenuResponse:
        """데이터베이스 행을 응답 모델로 변환"""
        return KakaoDinerMenuResponse(
            id=row["id"],
            diner_idx=row["diner_idx"],
            name=row["name"],
            product_id=row["product_id"],
            price=row["price"],
            is_ai_mate=row["is_ai_mate"],
            photo_url=row["photo_url"],
            is_recommend=row["is_recommend"],
            desc=row["desc"],
            mod_at=row["mod_at"],
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )
