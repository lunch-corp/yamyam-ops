import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.db import db
from app.core.dependencies import get_firebase_uid
from app.database import base_queries
from app.schemas.review import (
    ReviewCreate,
    ReviewResponse,
    ReviewUpdate,
    ReviewWithItem,
)

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ReviewResponse, tags=["reviews"], summary="리뷰 작성")
def create_review(review: ReviewCreate, firebase_uid: str = Depends(get_firebase_uid)):
    """새 리뷰 작성"""
    try:
        with db.get_cursor() as (cursor, conn):
            # 사용자 존재 확인
            cursor.execute(
                "SELECT 1 FROM users WHERE firebase_uid = %s", (firebase_uid,)
            )
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )

            # 아이템 존재 확인
            cursor.execute(base_queries.CHECK_ITEM_EXISTS, (review.item_id,))
            if not cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Item not found"
                )

            # 중복 리뷰 확인
            cursor.execute(
                "SELECT 1 FROM reviews WHERE firebase_uid = %s AND item_id = %s",
                (firebase_uid, review.item_id),
            )
            if cursor.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Review already exists for this user and item",
                )

            # 리뷰 생성
            cursor.execute(
                """
                INSERT INTO reviews (firebase_uid, item_id, score, review_text)
                VALUES (%s, %s, %s, %s)
                RETURNING id, firebase_uid, item_id, score, review_text, created_at, updated_at
                """,
                (
                    firebase_uid,
                    review.item_id,
                    review.score,
                    review.review_text,
                ),
            )

            result = cursor.fetchone()
            conn.commit()

            return ReviewResponse(
                id=result["id"],
                firebase_uid=result["firebase_uid"],
                item_id=result["item_id"],
                score=result["score"],
                review_text=result["review_text"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/", response_model=list[ReviewWithItem], tags=["reviews"], summary="리뷰 목록 조회"
)
def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    firebase_uid: str | None = None,
    item_id: int | None = None,
):
    """리뷰 목록 조회"""
    try:
        with db.get_cursor() as (cursor, conn):
            query = """
                SELECT r.id, r.firebase_uid, r.item_id, r.score, r.review_text, 
                       r.created_at, r.updated_at, i.name as item_name, i.category as item_category
                FROM reviews r
                JOIN items i ON r.item_id = i.id
            """
            params = []
            conditions = []

            if firebase_uid:
                conditions.append("r.firebase_uid = %s")
                params.append(firebase_uid)

            if item_id:
                conditions.append("r.item_id = %s")
                params.append(item_id)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += " ORDER BY r.created_at DESC LIMIT %s OFFSET %s"
            params.extend([limit, skip])

            cursor.execute(query, params)
            results = cursor.fetchall()

            return [
                ReviewWithItem(
                    id=row["id"],
                    firebase_uid=row["firebase_uid"],
                    item_id=row["item_id"],
                    score=row["score"],
                    review_text=row["review_text"],
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    item_name=row["item_name"],
                    item_category=row["item_category"],
                )
                for row in results
            ]

    except Exception as e:
        logger.error(f"Error getting reviews: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.get(
    "/{review_id}",
    response_model=ReviewWithItem,
    tags=["reviews"],
    summary="리뷰 상세 조회",
)
def get_review(review_id: int):
    """특정 리뷰 상세 조회"""
    try:
        with db.get_cursor() as (cursor, conn):
            cursor.execute(
                """
                SELECT r.id, r.firebase_uid, r.item_id, r.score, r.review_text, 
                       r.created_at, r.updated_at, i.name as item_name, i.category as item_category
                FROM reviews r
                JOIN items i ON r.item_id = i.id
                WHERE r.id = %s
                """,
                (review_id,),
            )

            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
                )

            return ReviewWithItem(
                id=result["id"],
                firebase_uid=result["firebase_uid"],
                item_id=result["item_id"],
                score=result["score"],
                review_text=result["review_text"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
                item_name=result["item_name"],
                item_category=result["item_category"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.put(
    "/{review_id}", response_model=ReviewResponse, tags=["reviews"], summary="리뷰 수정"
)
def update_review(
    review_id: int,
    review_update: ReviewUpdate,
    firebase_uid: str = Depends(get_firebase_uid),
):
    """리뷰 수정"""
    try:
        with db.get_cursor() as (cursor, conn):
            # 리뷰 존재 확인 및 소유자 확인
            cursor.execute(
                "SELECT firebase_uid FROM reviews WHERE id = %s", (review_id,)
            )
            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
                )

            if result["firebase_uid"] != firebase_uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only update your own reviews",
                )

            # 업데이트할 필드 구성
            update_fields = []
            update_values = []

            if review_update.score is not None:
                update_fields.append("score = %s")
                update_values.append(review_update.score)

            if review_update.review_text is not None:
                update_fields.append("review_text = %s")
                update_values.append(review_update.review_text)

            if not update_fields:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No fields to update",
                )

            # 업데이트 실행
            update_values.append(review_id)
            cursor.execute(
                f"""
                UPDATE reviews 
                SET {", ".join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
                RETURNING id, firebase_uid, item_id, score, review_text, created_at, updated_at
                """,
                update_values,
            )

            result = cursor.fetchone()
            conn.commit()

            return ReviewResponse(
                id=result["id"],
                firebase_uid=result["firebase_uid"],
                item_id=result["item_id"],
                score=result["score"],
                review_text=result["review_text"],
                created_at=result["created_at"],
                updated_at=result["updated_at"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )


@router.delete("/{review_id}", tags=["reviews"], summary="리뷰 삭제")
def delete_review(review_id: int, firebase_uid: str = Depends(get_firebase_uid)):
    """리뷰 삭제"""
    try:
        with db.get_cursor() as (cursor, conn):
            # 리뷰 존재 확인 및 소유자 확인
            cursor.execute(
                "SELECT firebase_uid FROM reviews WHERE id = %s", (review_id,)
            )
            result = cursor.fetchone()
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
                )

            if result["firebase_uid"] != firebase_uid:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only delete your own reviews",
                )

            cursor.execute(
                "DELETE FROM reviews WHERE id = %s RETURNING id", (review_id,)
            )

            result = cursor.fetchone()
            conn.commit()
            return {"message": "Review deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting review: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )
