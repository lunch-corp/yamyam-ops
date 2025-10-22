"""
공통 CRUD 기능을 제공하는 베이스 서비스 클래스
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypeVar

from fastapi import HTTPException, status

from app.core.db import db
from app.utils.ulid_utils import generate_ulid, is_valid_ulid

T = TypeVar("T")
CreateSchema = TypeVar("CreateSchema")
UpdateSchema = TypeVar("UpdateSchema")
ResponseSchema = TypeVar("ResponseSchema")

logger = logging.getLogger(__name__)


class BaseService(ABC, Generic[CreateSchema, UpdateSchema, ResponseSchema]):
    """공통 CRUD 기능을 제공하는 베이스 서비스"""

    def __init__(self, table_name: str, primary_key_field: str = "id"):
        self.table_name = table_name
        self.primary_key_field = primary_key_field

    def _generate_ulid(self) -> str:
        """새로운 ULID 생성"""
        return generate_ulid()

    def _validate_ulid(self, ulid_string: str) -> bool:
        """ULID 유효성 검증"""
        return is_valid_ulid(ulid_string)

    def _handle_exception(self, operation: str, e: Exception) -> None:
        """공통 예외 처리"""
        if isinstance(e, HTTPException):
            raise e

        logger.error(f"Error {operation}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    def _execute_query(
        self, query: str, params: tuple = None, dry_run: bool = False
    ) -> Any:
        """쿼리 실행 및 결과 반환"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Query: {query}")
                logger.info(f"[DRY RUN] Params: {params}")
                return {"dry_run": True, "query": query, "params": params}

            with db.get_cursor() as (cursor, conn):
                cursor.execute(query, params or ())
                result = cursor.fetchone()
                conn.commit()
                return result
        except Exception as e:
            self._handle_exception("executing query", e)

    def _execute_query_all(
        self, query: str, params: tuple = None, dry_run: bool = False
    ) -> List[Dict]:
        """쿼리 실행 및 모든 결과 반환"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Query: {query}")
                logger.info(f"[DRY RUN] Params: {params}")
                return [{"dry_run": True, "query": query, "params": params}]

            with db.get_cursor() as (cursor, conn):
                cursor.execute(query, params or ())
                results = cursor.fetchall()
                conn.commit()
                return results
        except Exception as e:
            self._handle_exception("executing query", e)

    def _check_exists(
        self, check_query: str, params: tuple, dry_run: bool = False
    ) -> bool:
        """레코드 존재 여부 확인"""
        try:
            if dry_run:
                logger.info(f"[DRY RUN] Check exists query: {check_query}")
                logger.info(f"[DRY RUN] Params: {params}")
                return True  # Dry run에서는 항상 존재한다고 가정

            with db.get_cursor() as (cursor, conn):
                cursor.execute(check_query, params)
                return cursor.fetchone() is not None
        except Exception as e:
            self._handle_exception("checking existence", e)

    def _build_update_query(
        self,
        update_fields: List[str],
        update_values: List[Any],
        where_field: str,
        where_value: Any,
    ) -> tuple:
        """업데이트 쿼리 구성"""
        if not update_fields:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update",
            )

        query = f"""
            UPDATE {self.table_name} 
            SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
            WHERE {where_field} = %s
            RETURNING *
        """

        update_values.append(where_value)
        return query, tuple(update_values)

    def _build_select_query(
        self,
        fields: List[str],
        conditions: List[str] = None,
        order_by: str = None,
        limit: int = None,
        offset: int = None,
    ) -> tuple:
        """SELECT 쿼리 구성"""
        query = f"SELECT {', '.join(fields)} FROM {self.table_name}"
        params = []

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if order_by:
            query += f" ORDER BY {order_by}"

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

        if offset is not None:
            query += " OFFSET %s"
            params.append(offset)

        return query, tuple(params)

    @abstractmethod
    def create(self, data: CreateSchema, dry_run: bool = False) -> ResponseSchema:
        """레코드 생성"""
        pass

    @abstractmethod
    def get_by_id(self, id_value: Any, dry_run: bool = False) -> ResponseSchema:
        """ID로 레코드 조회"""
        pass

    @abstractmethod
    def get_list(
        self, skip: int = 0, limit: int = 100, dry_run: bool = False, **filters
    ) -> List[ResponseSchema]:
        """레코드 목록 조회"""
        pass

    @abstractmethod
    def update(
        self, id_value: Any, data: UpdateSchema, dry_run: bool = False
    ) -> ResponseSchema:
        """레코드 업데이트"""
        pass

    @abstractmethod
    def delete(self, id_value: Any, dry_run: bool = False) -> Dict[str, str]:
        """레코드 삭제"""
        pass

    @abstractmethod
    def _convert_to_response(self, row: Dict) -> ResponseSchema:
        """데이터베이스 행을 응답 모델로 변환"""
        pass
