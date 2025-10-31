"""
JWT 토큰 생성 및 검증 유틸리티
"""

from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings
from jose import JWTError, jwt


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Access Token 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id, firebase_uid 등)
        expires_delta: 만료 시간 (기본값: 15분)

    Returns:
        JWT Access Token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Refresh Token 생성

    Args:
        data: 토큰에 포함할 데이터 (user_id, firebase_uid 등)
        expires_delta: 만료 시간 (기본값: 7일)

    Returns:
        JWT Refresh Token
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )

    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """
    JWT 토큰 검증

    Args:
        token: 검증할 JWT 토큰
        token_type: 토큰 타입 ("access" 또는 "refresh")

    Returns:
        토큰 페이로드 또는 None
    """
    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm]
        )

        # 토큰 타입 확인
        if payload.get("type") != token_type:
            return None

        return payload

    except JWTError:
        return None


def decode_token(token: str) -> Optional[dict]:
    """
    JWT 토큰 디코딩 (검증 없이)

    Args:
        token: 디코딩할 JWT 토큰

    Returns:
        토큰 페이로드 또는 None
    """
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
            options={"verify_exp": False},
        )
        return payload

    except JWTError:
        return None


def get_token_expiry(token: str) -> Optional[datetime]:
    """
    토큰 만료 시간 조회

    Args:
        token: JWT 토큰

    Returns:
        만료 시간 또는 None
    """
    payload = decode_token(token)
    if payload and "exp" in payload:
        return datetime.fromtimestamp(payload["exp"])
    return None
