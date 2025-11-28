from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class User(Base, ULIDMixin):
    __tablename__ = "users"

    firebase_uid = Column(String(128), unique=True, nullable=False, index=True)
    kakao_reviewer_id = Column(String(100), nullable=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255))
    display_name = Column(String(100))
    photo_url = Column(String(500))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    reviews = relationship("Review", back_populates="user")
