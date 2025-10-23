from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class Review(Base, ULIDMixin):
    __tablename__ = "reviews"

    firebase_uid = Column(
        String(128), ForeignKey("users.firebase_uid"), nullable=False, index=True
    )
    item_id = Column(String(26), ForeignKey("items.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False)
    review_text = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user = relationship("User", back_populates="reviews")
    item = relationship("Item", back_populates="reviews")
