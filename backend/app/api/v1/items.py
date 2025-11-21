import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.core.db import db
from app.database import base_queries
from app.schemas.item import ItemCreate, ItemResponse, ItemUpdate

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ItemResponse, tags=["items"], summary="아이템 생성")
def create_item(item: ItemCreate):
    """새 아이템 생성"""
    try:
        with db.get_cursor() as (cursor, conn):
            cursor.execute(
                """
                INSERT INTO items (name, category, description, location)
                VALUES (%s, %s, %s, %s)
                RETURNING id, name, category, description, location, created_at, updated_at
                """,
                (item.name, item.category, item.description, item.location),
            )

            result = cursor.fetchone()
            conn.commit()

            return ItemResponse(
                id=result["id"],
                name=result["name"],
                category=result["category"],
                description=result["description"],
                location=result["location"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

    except Exception as e:
        logger.error(f"Error creating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/", response_model=list[ItemResponse], tags=["items"], summary="아이템 목록 조회"
)
def list_items(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: str | None = None,
):
    """아이템 목록 조회"""
    try:
        with db.get_cursor() as (cursor, conn):
            query = """
                SELECT id, name, category, description, location, created_at, updated_at
                FROM items
            """
            params = []

            if category:
                query += " WHERE category = %s"
                params.append(category)

            query += " ORDER BY created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [
                ItemResponse(
                    id=row["id"],
                    name=row["name"],
                    category=row["category"],
                    description=row["description"],
                    location=row["location"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                )
                for row in results
            ]

    except Exception as e:
        logger.error(f"Error getting items: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    tags=["items"],
    summary="아이템 상세 조회",
)
def get_item(item_id: int):
    """특정 아이템 상세 조회"""
    try:
        with db.get_cursor() as (cursor, conn):
            cursor.execute(
                """
                SELECT id, name, category, description, location, created_at, updated_at
                FROM items WHERE id = %s
                """,
                (item_id,),
            )

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
                )

            return ItemResponse(
                id=result["id"],
                name=result["name"],
                category=result["category"],
                description=result["description"],
                location=result["location"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/{item_id}", response_model=ItemResponse, tags=["items"], summary="아이템 수정"
)
def update_item(item_id: int, item_update: ItemUpdate):
    """아이템 정보 업데이트"""
    try:
        with db.get_cursor() as (cursor, conn):
            # 아이템 존재 확인
            cursor.execute(base_queries.CHECK_ITEM_EXISTS, (item_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
                )

            # 업데이트할 필드 구성
            update_fields = []
            update_values = []

            if item_update.name is not None:
                update_fields.append("name = %s")
                update_values.append(item_update.name)

            if item_update.category is not None:
                update_fields.append("category = %s")
                update_values.append(item_update.category)

            if item_update.description is not None:
                update_fields.append("description = %s")
                update_values.append(item_update.description)

            if item_update.location is not None:
                update_fields.append("location = %s")
                update_values.append(item_update.location)

            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update",
                )

            # 업데이트 실행
            update_values.append(item_id)
            cursor.execute(
                f"""
                UPDATE items 
                SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, name, category, description, location, created_at, updated_at
                """,
                update_values,
            )

            result = cursor.fetchone()
            conn.commit()

            return ItemResponse(
                id=result["id"],
                name=result["name"],
                category=result["category"],
                description=result["description"],
                location=result["location"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{item_id}", tags=["items"], summary="아이템 삭제")
def delete_item(item_id: int):
    """아이템 삭제"""
    try:
        with db.get_cursor() as (cursor, conn):
            cursor.execute("DELETE FROM items WHERE id = %s RETURNING id", (item_id,))

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
                )

            conn.commit()
            return {"message": "Item deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
