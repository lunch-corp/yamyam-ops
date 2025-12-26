import logging

from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.kakao_diner import (
    FilteredDinerResponse,
    KakaoDinerCreate,
    KakaoDinerResponse,
    KakaoDinerSortRequest,
    KakaoDinerUpdate,
    SearchDinerResponse,
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
    "/filtered",
    response_model=list[FilteredDinerResponse],
    tags=["kakao-restaurants"],
    summary="카카오 음식점 필터링 (지역/카테고리)",
)
def filter_restaurants(
    limit: int | None = Query(
        None,
        ge=1,
        le=1000,
        description="반환할 최대 레코드 수 (top-k), None이면 전체 반환",
    ),
    offset: int | None = Query(None, ge=0, description="페이지네이션 오프셋"),
    diner_category_large: list[str] | None = Query(
        None, description="대분류 카테고리 (여러 개 가능)"
    ),
    diner_category_middle: list[str] | None = Query(
        None, description="중분류 카테고리 (여러 개 가능)"
    ),
    diner_category_small: list[str] | None = Query(
        None, description="소분류 카테고리 (여러 개 가능)"
    ),
    diner_category_detail: list[str] | None = Query(
        None, description="세부 카테고리 (여러 개 가능)"
    ),
    min_review_count: int | None = Query(None, ge=0, description="최소 리뷰 개수"),
    user_lat: float | None = Query(
        None, ge=-90, le=90, description="사용자 위도 (거리 필터용)"
    ),
    user_lon: float | None = Query(
        None, ge=-180, le=180, description="사용자 경도 (거리 필터용)"
    ),
    radius_km: float | None = Query(None, gt=0, description="검색 반경 (km)"),
    n: int | None = Query(
        None,
        ge=1,
        description="랜덤 샘플링 개수 (지정 시 필터링된 결과에서 n개 랜덤 반환, None이면 샘플링 안 함)",
    ),
):
    """
    카카오 음식점 필터링 (지역/카테고리)

    **필터링 조건:**
    - 카테고리: 대/중/소/세부 카테고리로 필터링
    - 거리: 사용자 위치 기준 반경 내 검색 (user_lat, user_lon, radius_km 모두 필요)
    - 리뷰 수: 최소 리뷰 개수 이상만 조회

    **정렬:**
    - 기본 정렬: bayesian_score DESC (인기도 점수순)

    **랜덤 샘플링:**
    - n이 지정되면, 필터링된 결과 중에서 n개를 랜덤하게 반환
    - n이 None이면 정렬된 순서대로 반환 (limit 적용)
    """
    return diner_service.get_list_filtered(
        limit=limit,
        offset=offset,
        diner_category_large=diner_category_large,
        diner_category_middle=diner_category_middle,
        diner_category_small=diner_category_small,
        diner_category_detail=diner_category_detail,
        min_review_count=min_review_count,
        user_lat=user_lat,
        user_lon=user_lon,
        radius_km=radius_km,
        n=n,
    )


@router.post(
    "/sorted",
    response_model=list[KakaoDinerResponse],
    tags=["kakao-restaurants"],
    summary="카카오 음식점 정렬/필터링",
)
def sort_restaurants(request: KakaoDinerSortRequest):
    """
    카카오 음식점 정렬/필터링

    **요청 본문:**
    - diner_ids: 정렬할 음식점 ID 리스트 (ULID)
    - user_id: 사용자 ID (개인화 정렬용, 선택)
    - sort_by: 정렬 기준 (기본값: rating)
    - min_rating: 최소 평점 (선택)
    - user_lat, user_lon: 사용자 위치 (거리 정렬용, 선택)
    - limit, offset: 페이지네이션

    **정렬 기준:**
    - personalization: 개인화 점수순 (user_id 필요)
    - popularity: 인기도 점수순
    - hidden_gem: 숨찐맛 점수순
    - rating: 평점순 (기본값)
    - review_count: 리뷰수순
    - distance: 거리순 (user_lat, user_lon 필요)

    **참고:**
    - 일반적으로 /filtered 엔드포인트의 결과를 받아서 정렬
    - ID 리스트를 기반으로 조회 및 정렬 수행
    """
    return diner_service.get_list_sorted(
        diner_ids=request.diner_ids,
        user_id=request.user_id,
        sort_by=request.sort_by,
        min_rating=request.min_rating,
        user_lat=request.user_lat,
        user_lon=request.user_lon,
        limit=request.limit,
        offset=request.offset,
    )


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
    offset: int | None = Query(None, ge=0, description="페이지네이션 오프셋"),
    diner_category_large: list[str] | None = Query(
        None, description="대분류 카테고리 (여러 개 가능)"
    ),
    diner_category_middle: list[str] | None = Query(
        None, description="중분류 카테고리 (여러 개 가능)"
    ),
    diner_category_small: list[str] | None = Query(
        None, description="소분류 카테고리 (여러 개 가능)"
    ),
    diner_category_detail: list[str] | None = Query(
        None, description="세부 카테고리 (여러 개 가능)"
    ),
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
    카카오 음식점 목록 조회 (DEPRECATED)

    **주의: 이 엔드포인트는 deprecated 되었습니다.**
    - 필터링: GET /filtered 사용
    - 정렬: POST /sorted 사용

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
        offset=offset,
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
    "/search",
    response_model=list[SearchDinerResponse],
    tags=["kakao-restaurants"],
    summary="카카오 음식점 검색",
)
def search_restaurants(
    query: str = Query(..., min_length=2, description="검색어 (최소 2자)"),
    limit: int = Query(10, ge=1, le=100, description="반환할 최대 결과 수"),
    user_lat: float | None = Query(
        None, ge=-90, le=90, description="사용자 위도 (거리 계산용)"
    ),
    user_lon: float | None = Query(
        None, ge=-180, le=180, description="사용자 경도 (거리 계산용)"
    ),
    radius_km: float | None = Query(None, gt=0, description="검색 반경 (km)"),
):
    """
    카카오 음식점 검색 (이름 기반)

    **검색 방식:**
    - 정확한 매칭: 검색어와 정확히 일치하는 음식점
    - 부분 매칭: 검색어가 음식점 이름에 포함된 경우
    - 자모 매칭: 한글 자모 단위로 유사도 계산 (정확한 매칭/부분 매칭이 없을 때)

    **필터링:**
    - radius_km이 지정되면 user_lat, user_lon 기준 반경 내 음식점만 검색

    **정렬:**
    - 정확한 매칭 > 부분 매칭 > 자모 매칭 순
    - 같은 매칭 타입 내에서는 거리순 (거리 정보가 있는 경우)
    """
    return diner_service.search_diners(
        query=query,
        limit=limit,
        user_lat=user_lat,
        user_lon=user_lon,
        radius_km=radius_km,
    )


@router.get(
    "/categories",
    response_model=list[dict],
    tags=["kakao-restaurants"],
    summary="카테고리 통계",
)
def get_category_statistics(
    category_type: str = Query(
        ..., description="분류 단위 (large: 대분류, middle: 중분류)"
    ),
    large_category: str | None = Query(
        None, description="대분류 카테고리명 (중분류 조회 시 필수)"
    ),
):
    """
    카테고리별 음식점 수 통계 조회

    **Parameters:**
    - category_type: 분류 단위
      - "large": 대분류 카테고리별 통계
      - "middle": 중분류 카테고리별 통계 (large_category 필수)
    - large_category: 대분류 카테고리명 (중분류 조회 시 필수)

    **Response:**
    - name: 카테고리명
    - count: 음식점 수

    **Example:**
    - 대분류: GET /categories?category_type=large
    - 중분류: GET /categories?category_type=middle&large_category=한식
    """
    if category_type == "middle" and not large_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="large_category is required when category_type is 'middle'",
        )

    return diner_service.get_category_statistics(
        category_type, large_category if category_type == "middle" else None
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
