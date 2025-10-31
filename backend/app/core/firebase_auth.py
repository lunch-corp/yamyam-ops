"""
Firebase 설정 및 인증 관리
"""

import json
import logging
from typing import Optional

import firebase_admin
from fastapi import HTTPException, status
from firebase_admin import auth, credentials

logger = logging.getLogger(__name__)


class FirebaseAuth:
    """Firebase Authentication 관리 클래스"""

    def __init__(self):
        self._app = None
        self._initialize_firebase()

    def _initialize_firebase(self):
        """Firebase 초기화"""
        try:
            import os

            # GOOGLE_APPLICATION_CREDENTIALS 환경변수 확인
            credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            logger.info(f"Firebase 초기화 시작 - credentials_path: {credentials_path}")

            if credentials_path and os.path.exists(credentials_path):
                logger.info(f"Firebase 키 파일 발견: {credentials_path}")
                # 파일 경로로 직접 초기화
                cred = credentials.Certificate(credentials_path)
                self._app = firebase_admin.initialize_app(cred)
                logger.info(
                    "✅ Firebase가 성공적으로 초기화되었습니다! (파일 경로 방식)"
                )
                return

            # 기존 방식 (환경변수에서 JSON 문자열)
            logger.info("Firebase 키 파일이 없음. 환경변수에서 키 확인 중...")
            firebase_key = self._get_firebase_key()
            if not firebase_key:
                logger.warning(
                    "Firebase 키가 설정되지 않았습니다. Firebase 기능이 비활성화됩니다."
                )
                return

            # Firebase 키를 파싱
            firebase_credentials = json.loads(firebase_key)

            # Firebase 앱 초기화
            cred = credentials.Certificate(firebase_credentials)
            self._app = firebase_admin.initialize_app(cred)

            logger.info("✅ Firebase가 성공적으로 초기화되었습니다! (환경변수 방식)")

        except Exception as e:
            logger.error(f"❌ Firebase 초기화 실패: {e}")
            import traceback

            logger.error(f"상세 오류: {traceback.format_exc()}")
            self._app = None

    def _get_firebase_key(self) -> Optional[str]:
        """환경변수에서 Firebase 키 가져오기"""
        import os

        # GOOGLE_APPLICATION_CREDENTIALS 환경변수 확인
        credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        if credentials_path and os.path.exists(credentials_path):
            try:
                with open(credentials_path, "r") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Firebase 키 파일 읽기 실패: {e}")
                return None

        # 기존 FIREBASE_KEY 환경변수 확인
        return os.getenv("FIREBASE_KEY")

    def verify_token(self, token: str) -> Optional[dict]:
        """Firebase ID 토큰 검증"""
        if not self._app:
            logger.warning("Firebase가 초기화되지 않았습니다.")
            return None

        try:
            # 토큰 검증
            decoded_token = auth.verify_id_token(token)
            return decoded_token
        except auth.InvalidIdTokenError:
            logger.warning("유효하지 않은 Firebase 토큰")
            return None
        except Exception as e:
            logger.error(f"토큰 검증 중 오류: {e}")
            return None

    def get_user_by_uid(self, uid: str) -> Optional[dict]:
        """UID로 사용자 정보 조회"""
        if not self._app:
            return None

        try:
            user = auth.get_user(uid)
            return {
                "uid": user.uid,
                "email": user.email,
                "display_name": user.display_name,
                "photo_url": user.photo_url,
                "email_verified": user.email_verified,
                "disabled": user.disabled,
            }
        except auth.UserNotFoundError:
            logger.warning(f"사용자를 찾을 수 없습니다: {uid}")
            return None
        except Exception as e:
            logger.error(f"사용자 조회 중 오류: {e}")
            return None

    def create_custom_token(
        self, uid: str, additional_claims: Optional[dict] = None
    ) -> Optional[str]:
        """커스텀 토큰 생성"""
        if not self._app:
            return None

        try:
            return auth.create_custom_token(uid, additional_claims).decode("utf-8")
        except Exception as e:
            logger.error(f"커스텀 토큰 생성 중 오류: {e}")
            return None


# 전역 Firebase 인스턴스
firebase_auth = FirebaseAuth()


def get_current_user(token: str) -> dict:
    """현재 사용자 정보 반환"""
    decoded_token = firebase_auth.verify_token(token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return decoded_token


def get_user_uid(token: str) -> str:
    """토큰에서 사용자 UID 추출"""
    decoded_token = get_current_user(token)
    return decoded_token.get("uid")
