"""
Kakao 음식점 메뉴 모델
"""

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class KakaoDinerMenu(Base, ULIDMixin):
    """카카오 음식점 메뉴 테이블"""

    __tablename__ = "kakao_diner_menus"

    diner_idx = Column(
        Integer,
        ForeignKey("kakao_diner.diner_idx", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name = Column(String(255), nullable=False)
    product_id = Column(String(255), nullable=False, index=True)
    price = Column(Float, nullable=True)
    is_ai_mate = Column(Boolean, nullable=True, index=True)
    photo_url = Column(Text, nullable=True)
    is_recommend = Column(Boolean, nullable=True, index=True)
    desc = Column(Text, nullable=True)
    mod_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    diner = relationship("KakaoDiner", back_populates="menus")

    def __repr__(self):
        return (
            f"<KakaoDinerMenu("
            f"diner_idx={self.diner_idx}, "
            f"name={self.name}, "
            f"product_id={self.product_id})>"
        )
