from enum import StrEnum

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


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    email: str | None = Field(None, max_length=255)
    display_name: str | None = Field(None, max_length=100)
    photo_url: str | None = Field(None, max_length=500)
    kakao_reviewer_id: str | None = Field(None, max_length=20)


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


class FirebaseUserInfo(BaseModel):
    """Firebase에서 가져온 사용자 정보"""

    uid: str
    email: str | None
    display_name: str | None
    photo_url: str | None
    email_verified: bool
    disabled: bool
