"""
Firebase 인증 의존성
"""

from typing import Optional

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from ..core.firebase_auth import get_current_user, get_user_uid

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

