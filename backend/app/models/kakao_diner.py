from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class KakaoDiner(Base, ULIDMixin):
    __tablename__ = "kakao_diner"

    diner_idx = Column(Integer, unique=True, nullable=False, index=True)
    diner_name = Column(String(255), nullable=False)
    diner_tag = Column(Text)
    diner_menu_name = Column(Text)
    diner_menu_price = Column(Text)
    diner_review_cnt = Column(String(50))
    diner_review_avg = Column(Float)
    diner_blog_review_cnt = Column(Float)
    diner_review_tags = Column(Text)
    diner_road_address = Column(Text)
    diner_num_address = Column(Text)
    diner_phone = Column(String(50))
    diner_lat = Column(Float, nullable=False)
    diner_lon = Column(Float, nullable=False)
    diner_open_time = Column(Text)
    diner_category_large = Column(String(100))
    diner_category_middle = Column(String(100))
    diner_category_small = Column(String(100))
    diner_category_detail = Column(String(100))
    diner_grade = Column(Integer)
    hidden_score = Column(Float)
    bayesian_score = Column(Float)
    crawled_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    reviews = relationship("KakaoReview", back_populates="diner")
    mappings = relationship("ItemKakaoMapping", back_populates="diner")
