from typing import Optional

from pydantic import BaseModel, Field


class KakaoReviewerBase(BaseModel):
    reviewer_id: int = Field(..., description="카카오 리뷰어 고유 ID")
    reviewer_user_name: Optional[str] = Field(
        None, max_length=100, description="리뷰어 사용자명"
    )
    reviewer_review_cnt: int = Field(..., ge=0, description="리뷰 개수")
    reviewer_avg: float = Field(..., ge=0, le=5, description="평균 평점")
    badge_grade: str = Field(..., description="배지 등급")
    badge_level: int = Field(..., ge=0, description="배지 레벨")


class KakaoReviewerCreate(KakaoReviewerBase):
    pass


class KakaoReviewerUpdate(BaseModel):
    reviewer_user_name: Optional[str] = Field(None, max_length=100)
    reviewer_review_cnt: Optional[int] = Field(None, ge=0)
    reviewer_avg: Optional[float] = Field(None, ge=0, le=5)
    badge_grade: Optional[str] = None
    badge_level: Optional[int] = Field(None, ge=0)


class KakaoReviewer(KakaoReviewerBase):
    id: str  # ULID
    crawled_at: str
    updated_at: str

    class Config:
        from_attributes = True


class KakaoReviewerResponse(BaseModel):
    id: str  # ULID
    reviewer_id: int
    reviewer_user_name: Optional[str]
    reviewer_review_cnt: int
    reviewer_avg: float
    badge_grade: str
    badge_level: int
    crawled_at: str
    updated_at: str
