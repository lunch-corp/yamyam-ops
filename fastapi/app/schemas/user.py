from typing import Optional

from pydantic import BaseModel, Field


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)


class UserCreate(UserBase):
    """Firebase에서 사용자 생성 시 사용"""

    firebase_uid: str = Field(..., min_length=1, max_length=128)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[str] = Field(None, max_length=255)
    display_name: Optional[str] = Field(None, max_length=100)
    photo_url: Optional[str] = Field(None, max_length=500)


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
    email: Optional[str]
    display_name: Optional[str]
    photo_url: Optional[str]
    created_at: str
    updated_at: str


class FirebaseUserInfo(BaseModel):
    """Firebase에서 가져온 사용자 정보"""

    uid: str
    email: Optional[str]
    display_name: Optional[str]
    photo_url: Optional[str]
    email_verified: bool
    disabled: bool
