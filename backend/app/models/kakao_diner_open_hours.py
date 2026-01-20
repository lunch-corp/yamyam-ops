"""
Kakao 음식점 영업시간 모델
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class KakaoDinerOpenHours(Base, ULIDMixin):
    """카카오 음식점 영업시간 테이블"""

    __tablename__ = "kakao_diner_open_hours"

    diner_idx = Column(
        Integer,
        ForeignKey("kakao_diner.diner_idx", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    day_of_week = Column(
        Integer, nullable=False, index=True
    )  # 0=월요일, 1=화요일, ..., 6=일요일
    is_open = Column(Boolean, nullable=False, default=True, index=True)
    start_time = Column(Time, nullable=True)  # NULL 가능 (휴무일인 경우)
    end_time = Column(Time, nullable=True)  # NULL 가능 (휴무일인 경우)
    description = Column(Text, nullable=True)  # '휴무일', '24시간 영업' 등 추가 설명
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    diner = relationship("KakaoDiner", back_populates="open_hours")

    # Unique constraint: 음식점당 요일별로 하나의 레코드만
    __table_args__ = (
        {"schema": None},  # 기본 스키마 사용
    )

    def __repr__(self):
        return (
            f"<KakaoDinerOpenHours("
            f"diner_idx={self.diner_idx}, "
            f"day_of_week={self.day_of_week}, "
            f"is_open={self.is_open}, "
            f"start_time={self.start_time}, "
            f"end_time={self.end_time})>"
        )
