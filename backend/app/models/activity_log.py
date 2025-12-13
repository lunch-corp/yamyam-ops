from sqlalchemy import ARRAY, TIMESTAMP, Column, Float, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from .base import Base, ULIDMixin


class UserActivityLog(Base, ULIDMixin):
    """사용자 활동 로그 모델 - ML 추천 모델 학습용"""

    __tablename__ = "user_activity_logs"

    # User identification
    user_id = Column(String(26), nullable=False, index=True)
    firebase_uid = Column(String(128), nullable=False, index=True)

    # Session tracking
    session_id = Column(String(50), nullable=False, index=True)

    # Event information
    event_type = Column(String(50), nullable=False, index=True)
    event_timestamp = Column(
        TIMESTAMP(timezone=True), server_default=func.now(), index=True
    )
    page = Column(String(50))

    # Location related
    location_query = Column(String(255))
    location_address = Column(String(255))
    location_lat = Column(Float)
    location_lon = Column(Float)
    location_method = Column(String(50))

    # Search filter related
    search_radius_km = Column(Float)
    selected_large_categories = Column(ARRAY(Text))
    selected_middle_categories = Column(ARRAY(Text))
    sort_by = Column(String(50))
    period = Column(String(20))

    # Ranking page related
    selected_city = Column(String(100))
    selected_region = Column(String(100))
    selected_grades = Column(ARRAY(Text))

    # Click/Interaction related
    clicked_diner_idx = Column(String(50), index=True)
    clicked_diner_name = Column(String(255))
    display_position = Column(Integer)

    # Additional metadata
    additional_data = Column(JSONB)
    user_agent = Column(Text)
    ip_address = Column(String(45))
