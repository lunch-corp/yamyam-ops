from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class Item(Base, ULIDMixin):
    __tablename__ = "items"

    name = Column(String(255), nullable=False)
    category = Column(String(100))
    description = Column(Text)
    location = Column(String(255))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    reviews = relationship("Review", back_populates="item")
