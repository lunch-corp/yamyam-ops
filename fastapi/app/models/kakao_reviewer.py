from sqlalchemy import Column, DateTime, Float, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class KakaoReviewer(Base, ULIDMixin):
    __tablename__ = "kakao_reviewer"

    kakao_user_id = Column(String(50), unique=True, nullable=False, index=True)
    reviewer_id = Column(Integer, unique=True, nullable=False, index=True)
    reviewer_user_name = Column(String(100))
    reviewer_review_cnt = Column(Integer, nullable=False)
    reviewer_avg = Column(Float, nullable=False)
    badge_grade = Column(String(50), nullable=False)
    badge_level = Column(Integer, nullable=False)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    reviews = relationship("KakaoReview", back_populates="reviewer")
