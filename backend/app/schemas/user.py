from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field


class UserIdType(StrEnum):
    ID = "id"
    FIREBASE_UID = "firebase_uid"


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    display_name: str | None = Field(None, max_length=100)
    photo_url: str | None = Field(None, max_length=500)


class UserCreate(UserBase):
    """Firebase에서 사용자 생성 시 사용"""

    firebase_uid: str = Field(..., min_length=1, max_length=128)


class OnboardingDataCreate(BaseModel):
    """온보딩 데이터 입력 스키마"""

    # Location information
    location: str | None = Field(None, max_length=255)
    location_method: str | None = Field(None, max_length=50)
    user_lat: float | None = None
    user_lon: float | None = None

    # Basic information
    birth_year: int | None = None
    gender: str | None = Field(None, max_length=20)
    dining_companions: list[str] | None = None

    # Budget information
    regular_budget: str | None = Field(None, max_length=50)
    special_budget: str | None = Field(None, max_length=50)

    # Taste preferences
    spice_level: int | None = None
    allergies: str | None = None
    dislikes: str | None = None

    # Food preferences
    food_preferences_large: list[str] | None = None
    food_preferences_middle: dict[str, Any] | None = None

    # Restaurant ratings
    restaurant_ratings: dict[str, Any] | None = None


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    display_name: str | None = Field(None, max_length=100)
    photo_url: str | None = Field(None, max_length=500)
    kakao_reviewer_id: str | None = Field(None, max_length=20)

    # Onboarding fields
    is_personalization_enabled: bool | None = None
    has_completed_onboarding: bool | None = None
    location: str | None = Field(None, max_length=255)
    location_method: str | None = Field(None, max_length=50)
    user_lat: float | None = None
    user_lon: float | None = None
    birth_year: int | None = None
    gender: str | None = Field(None, max_length=20)
    dining_companions: list[str] | None = None
    regular_budget: str | None = Field(None, max_length=50)
    special_budget: str | None = Field(None, max_length=50)
    spice_level: int | None = None
    allergies: str | None = None
    dislikes: str | None = None
    food_preferences_large: list[str] | None = None
    food_preferences_middle: dict[str, Any] | None = None
    restaurant_ratings: dict[str, Any] | None = None


class User(UserBase):
    id: str  # ULID
    firebase_uid: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: str  # ULID
    firebase_uid: str
    name: str
    kakao_reviewer_id: str | None
    email: str | None
    display_name: str | None
    photo_url: str | None
    created_at: str
    updated_at: str

    # Onboarding fields
    is_personalization_enabled: bool | None = None
    has_completed_onboarding: bool | None = None
    onboarding_completed_at: str | None = None
    location: str | None = None
    location_method: str | None = None
    user_lat: float | None = None
    user_lon: float | None = None
    birth_year: int | None = None
    gender: str | None = None
    dining_companions: list[str] | None = None
    regular_budget: str | None = None
    special_budget: str | None = None
    spice_level: int | None = None
    allergies: str | None = None
    dislikes: str | None = None
    food_preferences_large: list[str] | None = None
    food_preferences_middle: dict[str, Any] | None = None
    restaurant_ratings: dict[str, Any] | None = None


class FirebaseUserInfo(BaseModel):
    """Firebase에서 가져온 사용자 정보"""

    uid: str
    email: str | None
    display_name: str | None
    photo_url: str | None
    email_verified: bool
    disabled: bool
