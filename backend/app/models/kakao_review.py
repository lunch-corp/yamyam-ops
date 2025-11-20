from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class KakaoReview(Base, ULIDMixin):
    __tablename__ = "kakao_review"

    diner_idx = Column(
        Integer, ForeignKey("kakao_diner.diner_idx"), nullable=False, index=True
    )
    reviewer_id = Column(
        Integer, ForeignKey("kakao_reviewer.reviewer_id"), nullable=False, index=True
    )
    review_id = Column(Integer, unique=True, nullable=False, index=True)
    reviewer_review = Column(Text)
    reviewer_review_date = Column(String(50))
    reviewer_review_score = Column(Float, nullable=False)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    diner = relationship("KakaoDiner", back_populates="reviews")
    reviewer = relationship("KakaoReviewer", back_populates="reviews")
