import logging
from typing import List, Optional

from app.schemas.kakao_diner import (
    KakaoDinerCreate,
    KakaoDinerResponse,
    KakaoDinerUpdate,
)
from app.services.kakao_diner_service import KakaoDinerService
from fastapi import APIRouter, Query

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
diner_service = KakaoDinerService()


@router.post(
    "/",
    response_model=KakaoDinerResponse,
    tags=["kakao-restaurants"],
    summary="카카오 음식점 등록",
)
def create_restaurant(
    diner: KakaoDinerCreate,
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
):
    """카카오 음식점 등록"""
    return diner_service.create(diner, dry_run)


@router.get(
    "/",
    response_model=List[KakaoDinerResponse],
    tags=["kakao-restaurants"],
    summary="카카오 음식점 목록 조회",
)
def list_restaurants(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    category: Optional[str] = None,
    min_rating: Optional[float] = None,
):
    """카카오 음식점 목록 조회"""
    return diner_service.get_list(
        skip=skip, limit=limit, category=category, min_rating=min_rating
    )


@router.get(
    "/{kakao_place_id}",
    response_model=KakaoDinerResponse,
    tags=["kakao-restaurants"],
    summary="카카오 음식점 상세 조회",
)
def get_restaurant(kakao_place_id: str):
    """특정 카카오 음식점 상세 조회"""
    return diner_service.get_by_id(kakao_place_id)


@router.put(
    "/{kakao_place_id}",
    response_model=KakaoDinerResponse,
    tags=["kakao-restaurants"],
    summary="카카오 음식점 수정",
)
def update_restaurant(
    kakao_place_id: str,
    diner_update: KakaoDinerUpdate,
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
):
    """카카오 음식점 정보 수정"""
    return diner_service.update(kakao_place_id, diner_update, dry_run)


@router.delete(
    "/{kakao_place_id}", tags=["kakao-restaurants"], summary="카카오 음식점 삭제"
)
def delete_restaurant(
    kakao_place_id: str,
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
):
    """카카오 음식점 삭제"""
    return diner_service.delete(kakao_place_id, dry_run)
