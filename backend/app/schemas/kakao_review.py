from pydantic import BaseModel, Field


class KakaoReviewBase(BaseModel):
    diner_idx: int = Field(..., description="음식점 인덱스")
    reviewer_id: int = Field(..., description="리뷰어 ID")
    review_id: int = Field(..., description="리뷰 고유 ID")
    reviewer_review: str | None = Field(None, description="리뷰 내용")
    reviewer_review_date: str | None = Field(None, description="리뷰 작성일")
    reviewer_review_score: float = Field(..., ge=1, le=5, description="리뷰 평점")


class KakaoReviewCreate(KakaoReviewBase):
    pass


class KakaoReviewUpdate(BaseModel):
    reviewer_review: str | None = None
    reviewer_review_date: str | None = None
    reviewer_review_score: float | None = Field(None, ge=1, le=5)


class KakaoReview(KakaoReviewBase):
    id: str  # ULID
    crawled_at: str
    updated_at: str

    class Config:
        from_attributes = True


class KakaoReviewResponse(BaseModel):
    id: str  # ULID
    diner_idx: int
    reviewer_id: int
    review_id: int
    reviewer_review: str | None
    reviewer_review_date: str | None
    reviewer_review_score: float
    crawled_at: str
    updated_at: str


class KakaoReviewWithDetails(KakaoReviewResponse):
    diner_name: str | None
    diner_tag: str | None
    reviewer_user_name: str | None
