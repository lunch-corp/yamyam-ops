from sqlalchemy import ARRAY, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
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

    # Onboarding flags
    is_personalization_enabled = Column(Boolean, default=False, server_default="false")
    has_completed_onboarding = Column(Boolean, default=False, server_default="false")
    onboarding_completed_at = Column(DateTime(timezone=True))

    # Location information
    location = Column(String(255))
    location_method = Column(String(50))
    user_lat = Column(Float)
    user_lon = Column(Float)

    # Basic information
    birth_year = Column(Integer)
    gender = Column(String(20))
    dining_companions = Column(ARRAY(String))

    # Budget information
    regular_budget = Column(String(50))
    special_budget = Column(String(50))

    # Taste preferences
    spice_level = Column(Integer)
    allergies = Column(String)
    dislikes = Column(String)

    # Food preferences
    food_preferences_large = Column(ARRAY(String))
    food_preferences_middle = Column(JSONB)

    # Restaurant ratings
    restaurant_ratings = Column(JSONB)

    # Relationships
    reviews = relationship("Review", back_populates="user")
