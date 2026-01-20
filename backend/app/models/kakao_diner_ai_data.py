"""
카카오 음식점 AI 데이터 모델
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base, ULIDMixin


class KakaoDinerAIData(Base, ULIDMixin):
    """카카오 음식점 AI 데이터 모델"""

    __tablename__ = "kakao_diner_ai_data"

    # ForeignKey to kakao_diner.diner_idx (UNIQUE constraint)
    diner_idx = Column(
        Integer,
        ForeignKey("kakao_diner.diner_idx", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True,
    )

    # AI 생성 데이터
    ai_bottom_sheet_title = Column(String(500), nullable=True)
    ai_bottom_sheet_summary = Column(Text, nullable=True)
    ai_bottom_sheet_sheets = Column(JSONB, nullable=True)
    ai_bottom_sheet_landing_url = Column(Text, nullable=True)
    blog_summaries = Column(JSONB, nullable=True)

    # 검색 최적화를 위한 키워드 필드
    all_keywords = Column(Text, nullable=True)

    # Relationship
    diner = relationship("KakaoDiner", back_populates="ai_data")
