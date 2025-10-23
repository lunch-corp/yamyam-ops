"""
인증 API 엔드포인트
"""

import logging

from app.core.dependencies import get_current_user_from_token
from app.schemas.token import (
    FirebaseLoginRequest,
    TokenRefreshRequest,
    TokenRefreshResponse,
    TokenResponse,
    TokenVerifyRequest,
    TokenVerifyResponse,
)
from app.services.token_service import token_service
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=TokenResponse, summary="Firebase 로그인")
def login_with_firebase(request: FirebaseLoginRequest):
    """
    Firebase ID Token으로 로그인하여 JWT 토큰 발급

    **Flow:**
    1. 클라이언트가 Firebase Authentication으로 로그인
    2. Firebase ID Token을 받아서 이 엔드포인트로 전송
    3. 서버가 Firebase Token 검증 후 JWT Access/Refresh Token 발급
    4. 클라이언트는 이후 API 요청 시 JWT Access Token 사용

    **Response:**
    - access_token: API 요청에 사용할 JWT Access Token (15분 유효)
    - refresh_token: Access Token 갱신에 사용할 Refresh Token (7일 유효)
    - token_type: "bearer"
    - expires_in: Access Token 만료 시간 (초)
    """
    try:
        return token_service.login_with_firebase(request.firebase_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"로그인 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="로그인 처리 중 오류가 발생했습니다.",
        )


@router.post("/refresh", response_model=TokenRefreshResponse, summary="토큰 갱신")
def refresh_token(request: TokenRefreshRequest):
    """
    Refresh Token을 사용하여 새로운 Access Token 발급

    **사용 시기:**
    - Access Token이 만료되었을 때 (401 Unauthorized)
    - Access Token 만료 전 미리 갱신하고 싶을 때

    **Flow:**
    1. 클라이언트가 저장된 Refresh Token을 전송
    2. 서버가 Refresh Token 검증
    3. 유효하면 새로운 Access Token 발급
    4. Refresh Token은 그대로 사용 (만료 전까지)

    **Response:**
    - access_token: 새로운 JWT Access Token
    - token_type: "bearer"
    - expires_in: Access Token 만료 시간 (초)
    """
    try:
        return token_service.refresh_access_token(request.refresh_token)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"토큰 갱신 중 오류 발생: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="토큰 갱신 중 오류가 발생했습니다.",
        )


@router.post("/verify", response_model=TokenVerifyResponse, summary="토큰 검증")
def verify_token(request: TokenVerifyRequest):
    """
    JWT Access Token 검증

    **사용 목적:**
    - 토큰이 유효한지 확인
    - 토큰 페이로드 정보 조회
    - 디버깅 및 테스트

    **Response:**
    - valid: 토큰 유효성 (true/false)
    - payload: 토큰 페이로드 (user_id, firebase_uid 등)
    - message: 상태 메시지
    """
    try:
        payload = token_service.verify_access_token(request.token)
        return TokenVerifyResponse(
            valid=True,
            payload=payload,
            message="토큰이 유효합니다.",
        )
    except HTTPException as e:
        return TokenVerifyResponse(
            valid=False,
            payload=None,
            message=e.detail,
        )
    except Exception as e:
        logger.error(f"토큰 검증 중 오류 발생: {e}")
        return TokenVerifyResponse(
            valid=False,
            payload=None,
            message="토큰 검증 중 오류가 발생했습니다.",
        )


@router.get("/me", summary="현재 사용자 정보 조회")
def get_current_user_info(current_user=Depends(get_current_user_from_token)):
    """
    JWT Access Token으로 현재 사용자 정보 조회

    **사용 목적:**
    - 로그인한 사용자 정보 확인
    - 토큰이 정상 작동하는지 테스트

    **헤더 필요:**
    - Authorization: Bearer {access_token}

    **Response:**
    - user_id: 사용자 ID (ULID)
    - firebase_uid: Firebase UID
    - email: 이메일 (있는 경우)
    - exp: 토큰 만료 시간
    - iat: 토큰 발급 시간
    """
    return {
        "user_id": current_user.user_id,
        "firebase_uid": current_user.firebase_uid,
        "email": current_user.email,
        "token_type": current_user.type,
        "expires_at": current_user.exp,
        "issued_at": current_user.iat,
    }


@router.post("/logout", summary="로그아웃")
def logout():
    """
    로그아웃

    **참고:**
    JWT는 stateless이므로 서버에서 토큰을 무효화할 수 없습니다.
    클라이언트에서 저장된 Access Token과 Refresh Token을 삭제하면 됩니다.

    **클라이언트 처리:**
    1. 로컬 스토리지/쿠키에서 토큰 삭제
    2. 메모리에 저장된 토큰 정보 초기화
    3. 로그인 페이지로 리다이렉트

    **보안 강화 (선택):**
    - Redis 등을 사용하여 블랙리스트 관리
    - 토큰 만료 시간을 짧게 설정
    """
    return {
        "message": "로그아웃되었습니다. 클라이언트에서 토큰을 삭제해주세요.",
        "instructions": [
            "로컬 스토리지에서 access_token 삭제",
            "로컬 스토리지에서 refresh_token 삭제",
            "메모리에 저장된 사용자 정보 초기화",
        ],
    }
