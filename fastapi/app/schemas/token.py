"""
Token 관련 스키마
"""

from typing import Optional

from pydantic import BaseModel, Field


class TokenResponse(BaseModel):
    """토큰 응답 스키마"""

    access_token: str = Field(..., description="Access Token (JWT)")
    refresh_token: str = Field(..., description="Refresh Token (JWT)")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="Access Token 만료 시간 (초)")


class TokenRefreshRequest(BaseModel):
    """토큰 갱신 요청 스키마"""

    refresh_token: str = Field(..., description="Refresh Token")


class TokenRefreshResponse(BaseModel):
    """토큰 갱신 응답 스키마"""

    access_token: str = Field(..., description="새로운 Access Token")
    token_type: str = Field(default="bearer", description="토큰 타입")
    expires_in: int = Field(..., description="Access Token 만료 시간 (초)")


class FirebaseLoginRequest(BaseModel):
    """Firebase 로그인 요청 스키마"""

    firebase_token: str = Field(..., description="Firebase ID Token")


class TokenPayload(BaseModel):
    """토큰 페이로드 스키마"""

    user_id: str = Field(..., description="사용자 ID (ULID)")
    firebase_uid: str = Field(..., description="Firebase UID")
    email: Optional[str] = Field(None, description="이메일")
    exp: Optional[int] = Field(None, description="만료 시간 (Unix timestamp)")
    iat: Optional[int] = Field(None, description="발급 시간 (Unix timestamp)")
    type: Optional[str] = Field(None, description="토큰 타입 (access/refresh)")


class TokenVerifyRequest(BaseModel):
    """토큰 검증 요청 스키마"""

    token: str = Field(..., description="검증할 JWT 토큰")


class TokenVerifyResponse(BaseModel):
    """토큰 검증 응답 스키마"""

    valid: bool = Field(..., description="토큰 유효성")
    payload: Optional[TokenPayload] = Field(None, description="토큰 페이로드")
    message: Optional[str] = Field(None, description="메시지")
