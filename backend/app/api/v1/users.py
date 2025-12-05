import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import get_firebase_uid
from app.schemas.user import (
    OnboardingDataCreate,
    UserCreate,
    UserIdType,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
user_service = UserService()


@router.post("/", response_model=UserResponse, summary="사용자 생성")
def create_user(user_data: UserCreate):
    """사용자 생성 (PostgreSQL DB에 직접 생성)"""
    return user_service.create(user_data)


@router.get("/me", response_model=UserResponse, summary="현재 사용자 정보 조회")
def get_current_user(firebase_uid: str = Depends(get_firebase_uid)):
    """현재 사용자 정보 조회 (Firebase UID 기준)"""
    return user_service.get_by_firebase_uid(firebase_uid)


@router.get("/{user_id}", response_model=UserResponse, summary="사용자 ID로 조회")
def get_user_by_id(
    user_id: str,
    user_id_type: UserIdType = Query(
        ..., description="ID 타입 (ULID 또는 Firebase UID)"
    ),
):
    """사용자 ID로 조회 (ULID 또는 Firebase ID 기준)"""
    return user_service.get_by_id(user_id, user_id_type)


@router.get("/", response_model=list[UserResponse], summary="사용자 목록 조회")
def list_users(skip: int = 0, limit: int = 100):
    """사용자 목록 조회"""
    return user_service.get_list(skip=skip, limit=limit)


@router.put("/{user_id}", response_model=UserResponse, summary="사용자 정보 수정")
def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_id_type: UserIdType = Query(
        ..., description="ID 타입 (ULID 또는 Firebase UID)"
    ),
):
    """사용자 정보 업데이트 (PostgreSQL DB에서 직접 업데이트)"""
    return user_service.update(user_id, user_update, user_id_type)


@router.put("/me", response_model=UserResponse, summary="내 프로필 수정")
def update_current_user(
    user_update: UserUpdate, firebase_uid: str = Depends(get_firebase_uid)
):
    """현재 사용자 정보 업데이트"""
    # Firebase UID로 사용자 조회 후 업데이트
    user = user_service.get_by_firebase_uid(firebase_uid)
    return user_service.update(user.id, user_update)


@router.delete("/{user_id}", summary="사용자 삭제")
def delete_user(user_id: str):
    """사용자 삭제 (PostgreSQL DB에서 직접 삭제)"""
    return user_service.delete(user_id)


@router.delete("/me", summary="firebase 계정 삭제")
def delete_current_user(firebase_uid: str = Depends(get_firebase_uid)):
    """현재 사용자 계정 삭제"""
    user = user_service.get_by_firebase_uid(firebase_uid)
    return user_service.delete(user.id)


# Firebase 동기화 관련 엔드포인트
@router.post("/me/sync", response_model=UserResponse, summary="특정 사용자 정보 동기화")
def sync_user_with_firebase(firebase_uid: str = Depends(get_firebase_uid)):
    """Firebase Auth 정보로 현재 사용자 정보 동기화 (부분 업데이트)"""
    return user_service.sync_with_firebase(firebase_uid)


@router.post(
    "/sync-from-firebase",
    response_model=UserResponse,
    summary="Firebase 회원가입 직후 사용자 생성",
)
def sync_user_from_firebase(firebase_uid: str = Depends(get_firebase_uid)):
    """
    Firebase 회원가입 직후 PostgreSQL에 사용자 생성

    - What2Eat에서 회원가입 성공 후 호출
    - Firebase ID Token으로 인증
    - 이미 존재하는 경우 기존 사용자 반환
    """
    from app.core.firebase_auth import firebase_auth

    # Firebase에서 사용자 정보 가져오기
    firebase_user = firebase_auth.get_user_by_uid(firebase_uid)
    if not firebase_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Firebase 사용자를 찾을 수 없습니다.",
        )

    email = firebase_user.get("email")
    name = firebase_user.get("display_name") or (
        email.split("@")[0] if email else firebase_uid
    )

    return user_service.create_from_firebase(firebase_uid, email, name)


@router.patch(
    "/me/onboarding",
    response_model=UserResponse,
    summary="온보딩 데이터 저장",
)
def save_onboarding_data(
    onboarding_data: OnboardingDataCreate,
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    온보딩 완료 시 사용자 프로필 데이터 저장

    - What2Eat에서 온보딩 완료 후 호출
    - Firebase ID Token으로 인증
    - 온보딩 데이터 및 평가 데이터 저장
    - has_completed_onboarding, is_personalization_enabled 플래그 업데이트
    """
    return user_service.update_onboarding(firebase_uid, onboarding_data)


@router.post("/sync-all", summary="전체 사용자 동기화")
def sync_all_users_from_firebase():
    """Firebase Auth의 모든 사용자를 DB에 동기화 (전체 업데이트)"""
    return user_service.sync_all_from_firebase()
