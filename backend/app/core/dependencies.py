"""
인증 의존성 (Firebase + JWT)
"""

from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.firebase_auth import get_current_user, get_user_uid
from app.schemas.token import TokenPayload
from app.services.token_service import token_service

# HTTP Bearer 토큰 스키마
security = HTTPBearer()


def get_firebase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """Firebase 인증된 사용자 정보 반환"""
    return get_current_user(credentials.credentials)


def get_firebase_uid(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> str:
    """Firebase 인증된 사용자 UID 반환"""
    return get_user_uid(credentials.credentials)


def get_optional_firebase_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[dict]:
    """선택적 Firebase 인증 (토큰이 없어도 허용)"""
    if not credentials:
        return None

    try:
        return get_current_user(credentials.credentials)
    except HTTPException:
        return None


def get_optional_firebase_uid(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[str]:
    """선택적 Firebase UID (토큰이 없어도 허용)"""
    user = get_optional_firebase_user(credentials)
    return user.get("uid") if user else None


# ============================================
# JWT Token 기반 인증 (새로운 방식)
# ============================================


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """
    JWT Access Token으로 현재 사용자 정보 반환

    Returns:
        TokenPayload: 토큰 페이로드 (user_id, firebase_uid 등)

    Raises:
        HTTPException: 토큰이 유효하지 않은 경우
    """
    token = credentials.credentials
    return token_service.verify_access_token(token)


def get_user_id_from_token(
    token_payload: TokenPayload = Depends(get_current_user_from_token),
) -> str:
    """
    JWT Token에서 사용자 ID 추출

    Returns:
        str: 사용자 ID (ULID)
    """
    return token_payload.user_id


def get_firebase_uid_from_token(
    token_payload: TokenPayload = Depends(get_current_user_from_token),
) -> str:
    """
    JWT Token에서 Firebase UID 추출

    Returns:
        str: Firebase UID
    """
    return token_payload.firebase_uid


def get_optional_user_from_token(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(
        HTTPBearer(auto_error=False)
    ),
) -> Optional[TokenPayload]:
    """
    선택적 JWT 인증 (토큰이 없어도 허용)

    Returns:
        Optional[TokenPayload]: 토큰 페이로드 또는 None
    """
    if not credentials:
        return None

    try:
        return token_service.verify_access_token(credentials.credentials)
    except HTTPException:
        return None
