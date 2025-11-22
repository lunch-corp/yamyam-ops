import logging

from fastapi import APIRouter, Query

from app.schemas.kakao_diner import (
    KakaoDinerCreate,
    KakaoDinerResponse,
    KakaoDinerUpdate,
)
from app.services.kakao_diner_service import KakaoDinerService

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
    response_model=list[KakaoDinerResponse],
    tags=["kakao-restaurants"],
    summary="카카오 음식점 목록 조회",
)
def list_restaurants(
    limit: int | None = Query(
        None,
        ge=1,
        le=1000,
        description="반환할 최대 레코드 수 (top-k), None이면 전체 반환",
    ),
    diner_category_large: str | None = Query(None, description="대분류 카테고리"),
    diner_category_middle: str | None = Query(None, description="중분류 카테고리"),
    diner_category_small: str | None = Query(None, description="소분류 카테고리"),
    diner_category_detail: str | None = Query(None, description="세부 카테고리"),
    min_rating: float | None = Query(None, ge=0, le=5, description="최소 평점"),
    user_lat: float | None = Query(
        None, ge=-90, le=90, description="사용자 위도 (거리 필터 및 정렬용)"
    ),
    user_lon: float | None = Query(
        None, ge=-180, le=180, description="사용자 경도 (거리 필터 및 정렬용)"
    ),
    radius_km: float | None = Query(
        None, gt=0, description="검색 반경 (km, 기본 필터)"
    ),
    user_id: str | None = Query(None, description="사용자 ID (개인화 정렬용)"),
    sort_by: str = Query(
        "rating",
        description="정렬 기준 (personalization, popularity, hidden_gem, rating, distance, review_count)",
    ),
):
    """
    카카오 음식점 목록 조회

    **기본 필터링 (항상 적용):**
    - 카테고리: 대/중/소/세부 카테고리로 필터링
    - 거리: 사용자 위치 기준 반경 내 검색 (user_lat, user_lon, radius_km 모두 필요)

    **추가 필터링:**
    - 평점: 최소 평점 이상만 조회

    **정렬 기준 (하나만 선택):**
    - personalization: 개인화 점수순 (user_id 필요)
    - popularity: 인기도 점수순
    - hidden_gem: 숨찐맛 점수순
    - rating: 평점순 (기본값)
    - review_count: 리뷰수순
    - distance: 거리순 (user_lat, user_lon 필요)

    **참고:**
    - 거리는 기본 필터링(radius_km)과 정렬 기준(sort_by=distance) 모두 가능
    - 정렬 기준은 하나만 적용됨
    """
    return diner_service.get_list(
        limit=limit,
        diner_category_large=diner_category_large,
        diner_category_middle=diner_category_middle,
        diner_category_small=diner_category_small,
        diner_category_detail=diner_category_detail,
        min_rating=min_rating,
        user_lat=user_lat,
        user_lon=user_lon,
        radius_km=radius_km,
        user_id=user_id,
        sort_by=sort_by,
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
