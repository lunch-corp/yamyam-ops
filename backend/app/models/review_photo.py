from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class ReviewPhoto(Base, ULIDMixin):
    __tablename__ = "review_photos"

    review_id = Column(
        String, ForeignKey("kakao_review.review_id"), nullable=False, index=True
    )
    photo_url = Column(Text, nullable=False)
    original_photo_id = Column(Integer, nullable=True)
    media_type = Column(String(20), default="PHOTO", nullable=False)
    status = Column(String(10), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    view_count = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    review = relationship("KakaoReview", back_populates="photos")
