from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
    score: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None


class ReviewCreate(ReviewBase):
    """리뷰 생성 (Firebase UID 사용)"""

    item_id: str  # ULID


class ReviewUpdate(BaseModel):
    score: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None


class Review(ReviewBase):
    id: str  # ULID
    firebase_uid: str
    item_id: str  # ULID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: str  # ULID
    firebase_uid: str
    item_id: str  # ULID
    score: int
    review_text: Optional[str]
    created_at: str
    updated_at: str


class ReviewWithItem(ReviewResponse):
    item_name: str
    item_category: Optional[str]
