"""
파일 업로드 API 엔드포인트
"""

import logging
from typing import Dict

from fastapi import APIRouter, File, Query, UploadFile

from app.services.upload_service import UploadService

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
upload_service = UploadService()


@router.post(
    "/kakao/restaurants/basic", tags=["uploads"], summary="음식점 기본 정보 업로드"
)
async def upload_restaurant_basic_data(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> Dict:
    """
    카카오 음식점 기본 정보 업로드

    diner_basic.csv 파일을 업로드하여 기본 음식점 정보를 등록합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - diner_name: 음식점 이름 (str)
    - diner_num_address: 지번 주소 (str)
    - diner_road_address: 도로명 주소 (str)
    - diner_phone: 전화번호 (str)
    - diner_open_time: 영업시간 (str)
    - diner_lat: 위도 (float, nullable)
    - diner_lon: 경도 (float, nullable)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_basic(file, dry_run)


@router.post(
    "/kakao/restaurants/categories", tags=["uploads"], summary="음식점 카테고리 업로드"
)
async def upload_restaurant_categories(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> Dict:
    """
    카카오 음식점 카테고리 정보 업로드

    diner_categories.csv 파일을 업로드하여 음식점 카테고리 정보를 등록합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - diner_category_large: 대분류 카테고리 (str)
    - diner_category_middle: 중분류 카테고리 (str)
    - diner_category_small: 소분류 카테고리 (str)
    - diner_category_detail: 세부 카테고리 (str)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_categories(file, dry_run)


@router.post("/kakao/restaurants/menus", tags=["uploads"], summary="음식점 메뉴 업로드")
async def upload_restaurant_menus(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> Dict:
    """
    카카오 음식점 메뉴 정보 업로드

    diner_menus.csv 파일을 업로드하여 음식점 메뉴 정보를 등록합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - diner_menu_name: 메뉴 이름 (str)
    - diner_menu_price: 메뉴 가격 (str)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_menus(file, dry_run)


@router.post(
    "/kakao/restaurants/reviews", tags=["uploads"], summary="음식점 리뷰 통계 업로드"
)
async def upload_restaurant_reviews(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> Dict:
    """
    카카오 음식점 리뷰 통계 업로드

    diner_reviews.csv 파일을 업로드하여 음식점 리뷰 통계 정보를 등록합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - diner_review_cnt: 리뷰 개수 (int, 기본값: 0)
    - diner_review_avg: 리뷰 평점 (float, 기본값: 0.0)
    - diner_blog_review_cnt: 블로그 리뷰 개수 (float, 기본값: 0.0)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_reviews(file, dry_run)


@router.post("/kakao/restaurants/tags", tags=["uploads"], summary="음식점 태그 업로드")
async def upload_restaurant_tags(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> Dict:
    """
    카카오 음식점 태그 정보 업로드

    diner_tags.csv 파일을 업로드하여 음식점 태그 정보를 등록합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - diner_tag: 음식점 태그 (str)
    - diner_review_tags: 리뷰 태그 (str)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_tags(file, dry_run)


@router.post(
    "/kakao/restaurants/bulk", tags=["uploads"], summary="음식점 데이터 일괄 업로드"
)
async def bulk_upload_restaurant_data(
    diner_basic: UploadFile = File(...),
    diner_categories: UploadFile = File(None),
    diner_menus: UploadFile = File(None),
    diner_reviews: UploadFile = File(None),
    diner_tags: UploadFile = File(None),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> Dict:
    """
    카카오 음식점 데이터 일괄 업로드

    여러 파일을 한 번에 업로드하여 음식점 데이터베이스를 업데이트합니다.
    diner_basic은 필수이며, 나머지는 선택사항입니다.

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.bulk_upload_all_files(
        diner_basic, diner_categories, diner_menus, diner_reviews, diner_tags, dry_run
    )
