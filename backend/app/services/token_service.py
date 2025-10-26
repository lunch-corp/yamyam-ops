"""
Token 관리 서비스
"""

import logging
from typing import Optional

from app.core.config import settings
from app.core.firebase_auth import firebase_auth
from app.schemas.token import TokenPayload, TokenResponse
from app.services.user_service import UserService
from app.utils.jwt_utils import create_access_token, create_refresh_token, verify_token
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)


class TokenService:
    """토큰 관리 서비스"""

    def __init__(self):
        self.user_service = UserService()

    def create_tokens(
        self, user_id: str, firebase_uid: str, email: Optional[str] = None
    ) -> TokenResponse:
        """
        Access Token과 Refresh Token 생성

        Args:
            user_id: 사용자 ID (ULID)
            firebase_uid: Firebase UID
            email: 이메일 (선택)

        Returns:
            TokenResponse: Access Token과 Refresh Token
        """
        # 토큰에 포함할 데이터
        token_data = {
            "user_id": user_id,
            "firebase_uid": firebase_uid,
        }

        if email:
            token_data["email"] = email

        # Access Token 생성
        access_token = create_access_token(token_data)

        # Refresh Token 생성
        refresh_token = create_refresh_token(token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
            expires_in=settings.access_token_expire_minutes * 60,  # 초 단위로 변환
        )

    def verify_access_token(self, token: str) -> TokenPayload:
        """
        Access Token 검증

        Args:
            token: JWT Access Token

        Returns:
            TokenPayload: 토큰 페이로드

        Raises:
            HTTPException: 토큰이 유효하지 않은 경우
        """
        payload = verify_token(token, token_type="access")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않거나 만료된 Access Token입니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenPayload(**payload)

    def verify_refresh_token(self, token: str) -> TokenPayload:
        """
        Refresh Token 검증

        Args:
            token: JWT Refresh Token

        Returns:
            TokenPayload: 토큰 페이로드

        Raises:
            HTTPException: 토큰이 유효하지 않은 경우
        """
        payload = verify_token(token, token_type="refresh")

        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않거나 만료된 Refresh Token입니다.",
            )

        return TokenPayload(**payload)

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Refresh Token을 사용하여 새로운 Access Token 발급

        Args:
            refresh_token: JWT Refresh Token

        Returns:
            dict: 새로운 Access Token 정보

        Raises:
            HTTPException: Refresh Token이 유효하지 않은 경우
        """
        # Refresh Token 검증
        payload = self.verify_refresh_token(refresh_token)

        # 새로운 Access Token 생성
        token_data = {
            "user_id": payload.user_id,
            "firebase_uid": payload.firebase_uid,
        }

        if payload.email:
            token_data["email"] = payload.email

        new_access_token = create_access_token(token_data)

        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    def login_with_firebase(self, firebase_token: str) -> TokenResponse:
        """
        Firebase Token으로 로그인하여 JWT 토큰 발급

        Args:
            firebase_token: Firebase ID Token

        Returns:
            TokenResponse: Access Token과 Refresh Token

        Raises:
            HTTPException: Firebase 토큰이 유효하지 않거나 사용자가 없는 경우
        """
        # Firebase 토큰 검증
        decoded_token = firebase_auth.verify_token(firebase_token)

        if not decoded_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="유효하지 않은 Firebase 토큰입니다.",
            )

        firebase_uid = decoded_token.get("uid")
        email = decoded_token.get("email")

        # 사용자 조회
        try:
            user = self.user_service.get_by_firebase_uid(firebase_uid)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                # 사용자가 없으면 자동 생성
                from app.schemas.user import UserCreate

                user_data = UserCreate(
                    firebase_uid=firebase_uid,
                    name=decoded_token.get("name") or email.split("@")[0]
                    if email
                    else firebase_uid,
                    email=email,
                    display_name=decoded_token.get("name"),
                    photo_url=decoded_token.get("picture"),
                )

                user = self.user_service.create(user_data)
                logger.info(f"새 사용자 자동 생성: {user.id}")
            else:
                raise

        # JWT 토큰 생성
        return self.create_tokens(
            user_id=user.id,
            firebase_uid=user.firebase_uid,
            email=user.email,
        )


# 전역 토큰 서비스 인스턴스
token_service = TokenService()
