"""
활동 로그 API 엔드포인트
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, Query

from app.core.dependencies import get_firebase_uid
from app.schemas.activity_log import (
    ActivityLogCreate,
    ActivityLogExport,
    ActivityLogFilter,
    ActivityLogResponse,
)
from app.services.activity_log_service import activity_log_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ActivityLogResponse, summary="활동 로그 생성")
def create_activity_log(
    log_data: ActivityLogCreate, firebase_uid: str = Depends(get_firebase_uid)
):
    """
    사용자 활동 로그 생성

    - What2Eat에서 사용자 행동 발생 시 호출
    - Firebase ID Token으로 인증
    - ML 추천 모델 학습용 데이터 수집
    """
    # Firebase UID 검증 (요청한 사용자와 로그의 사용자가 일치하는지)
    if log_data.firebase_uid != firebase_uid:
        logger.warning(
            f"Firebase UID mismatch: {firebase_uid} vs {log_data.firebase_uid}"
        )
        # 보안을 위해 요청한 사용자의 UID로 강제 설정
        log_data.firebase_uid = firebase_uid

    return activity_log_service.create_log(log_data)


@router.get(
    "/me", response_model=list[ActivityLogResponse], summary="내 활동 로그 조회"
)
def get_my_activity_logs(
    firebase_uid: str = Depends(get_firebase_uid),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """
    현재 사용자의 활동 로그 조회

    - Firebase ID Token으로 인증
    - 페이지네이션 지원
    """
    return activity_log_service.get_user_logs(firebase_uid, limit, offset)


@router.get(
    "/me/filter",
    response_model=list[ActivityLogResponse],
    summary="필터링된 내 활동 로그 조회",
)
def get_filtered_activity_logs(
    filter_params: ActivityLogFilter = Depends(),
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    필터를 적용한 활동 로그 조회

    - 이벤트 타입, 페이지, 날짜 범위로 필터링
    - Firebase ID Token으로 인증
    """
    return activity_log_service.get_logs_with_filter(firebase_uid, filter_params)


@router.get(
    "/session/{session_id}",
    response_model=list[ActivityLogResponse],
    summary="세션별 활동 로그 조회",
)
def get_session_activity_logs(
    session_id: str, firebase_uid: str = Depends(get_firebase_uid)
):
    """
    특정 세션의 활동 로그 조회

    - 세션 ID로 연속된 사용자 행동 조회
    - Firebase ID Token으로 인증
    """
    logs = activity_log_service.get_session_logs(session_id)

    # 보안: 자신의 세션만 조회 가능
    if logs and logs[0].firebase_uid != firebase_uid:
        logger.warning(f"Unauthorized session access attempt: {firebase_uid}")
        return []

    return logs


@router.get(
    "/type/{event_type}",
    response_model=list[ActivityLogResponse],
    summary="이벤트 타입별 로그 조회",
)
def get_logs_by_event_type(
    event_type: str,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    특정 이벤트 타입의 로그 조회

    - 이벤트 타입: location_search, diner_click 등
    - 자신의 로그만 조회 가능
    """
    all_logs = activity_log_service.get_logs_by_type(event_type, limit, offset)

    # 보안: 자신의 로그만 필터링
    return [log for log in all_logs if log.firebase_uid == firebase_uid]


@router.post("/export", response_model=dict[str, Any], summary="ML 학습용 데이터 추출")
def export_logs_for_ml(export_params: ActivityLogExport):
    """
    ML 학습용 데이터 추출

    - 관리자 전용 (추후 권한 체크 추가 필요)
    - JSON 또는 CSV 형식으로 추출
    - 날짜 범위 및 이벤트 타입 필터링
    """
    # TODO: 관리자 권한 체크 추가
    return activity_log_service.export_logs_for_ml(export_params)


@router.get("/statistics", response_model=dict[str, Any], summary="활동 로그 통계")
def get_activity_statistics(
    start_date: str = Query(None),
    end_date: str = Query(None),
):
    """
    활동 로그 통계 조회

    - 관리자 전용 (추후 권한 체크 추가 필요)
    - 이벤트 타입별 카운트
    - 인기 음식점 TOP 20
    """
    # TODO: 관리자 권한 체크 추가
    return activity_log_service.get_statistics(start_date, end_date)


@router.get("/me/preferences", response_model=dict[str, Any], summary="내 선호도 분석")
def get_my_preferences(firebase_uid: str = Depends(get_firebase_uid)):
    """
    사용자 선호도 분석

    - 선호 카테고리 분석
    - Firebase ID Token으로 인증
    """
    return activity_log_service.get_user_preferences(firebase_uid)
