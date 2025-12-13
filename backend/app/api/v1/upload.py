"""
파일 업로드 API 엔드포인트
"""

import logging

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
) -> dict:
    """
    카카오 음식점 기본 정보 업로드

    diner_basic.csv 파일을 업로드하여 기본 음식점 정보를 등록합니다.
    동일한 diner_idx가 이미 존재하는 경우 UPSERT로 새 데이터로 업데이트됩니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int, unique)
    - diner_name: 음식점 이름 (str)
    - diner_tag: 음식점 태그 (str, 리스트 형식은 쉼표로 변환됨)
    - diner_menu_name: 메뉴 이름 (str, 리스트 형식은 쉼표로 변환됨)
    - diner_menu_price: 메뉴 가격 (str, 리스트 형식은 쉼표로 변환됨)
    - diner_review_cnt: 리뷰 개수 (str)
    - diner_review_avg: 리뷰 평균 평점 (float, nullable)
    - diner_blog_review_cnt: 블로그 리뷰 개수 (float, nullable)
    - diner_review_tags: 리뷰 태그 (str, 리스트 형식은 쉼표로 변환됨)
    - diner_road_address: 도로명 주소 (str)
    - diner_num_address: 지번 주소 (str)
    - diner_phone: 전화번호 (str)
    - diner_lat: 위도 (float)
    - diner_lon: 경도 (float)
    - diner_open_time: 영업시간 (str)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_basic(file, dry_run)


@router.post(
    "/kakao/restaurants/categories", tags=["uploads"], summary="음식점 카테고리 업로드"
)
async def upload_restaurant_categories(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
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
) -> dict:
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
) -> dict:
    """
    카카오 음식점 리뷰 통계 업로드

    diner_reviews.csv 파일을 업로드하여 음식점 리뷰 통계 정보를 등록합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - review_id: 리뷰 고유 ID (int)
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
) -> dict:
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
) -> dict:
    """
    카카오 음식점 데이터 일괄 업로드

    여러 파일을 한 번에 업로드하여 음식점 데이터베이스를 업데이트합니다.
    diner_basic은 필수이며, 나머지는 선택사항입니다.

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.bulk_upload_all_files(
        diner_basic, diner_categories, diner_menus, diner_reviews, diner_tags, dry_run
    )


@router.post("/kakao/reviewers", tags=["uploads"], summary="리뷰어 정보 업로드")
async def upload_reviewers(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 리뷰어 정보 업로드

    reviewers.csv 파일을 업로드하여 리뷰어 정보를 등록합니다.
    동일한 reviewer_id가 이미 존재하는 경우 UPSERT로 새 데이터로 업데이트됩니다.

    **필수 컬럼:**
    - reviewer_id: 리뷰어 고유 ID (int, unique)
    - reviewer_review_cnt: 리뷰 개수 (int)
    - reviewer_avg: 평균 평점 (float)
    - badge_grade: 배지 등급 (str)
    - badge_level: 배지 레벨 (int)

    **선택 컬럼:**
    - reviewer_user_name: 리뷰어 사용자명 (str)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_reviewers(file, dry_run)


@router.post("/kakao/reviews", tags=["uploads"], summary="리뷰 정보 업로드")
async def upload_reviews(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 리뷰 정보 업로드

    reviews.csv 파일을 업로드하여 리뷰 정보를 등록합니다.
    동일한 review_id가 이미 존재하는 경우 UPSERT로 새 데이터로 업데이트됩니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - reviewer_id: 리뷰어 고유 ID (int)
    - review_id: 리뷰 고유 ID (int, unique)
    - reviewer_review_score: 리뷰 평점 (float)

    **선택 컬럼:**
    - reviewer_review: 리뷰 내용 (str, nullable - 빈 값 허용)
    - reviewer_review_date: 리뷰 작성일 (str, nullable - 날짜 형식 권장: YYYY-MM-DD)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_reviews(file, dry_run)


@router.post(
    "/kakao/restaurants/grade-bayesian",
    tags=["uploads"],
    summary="음식점 등급 및 베이지안 점수 업로드",
)
async def upload_restaurant_grade_bayesian(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 음식점 등급 및 베이지안 점수 업로드

    diner_grade_bayesian.csv 파일을 업로드하여 음식점 등급과 베이지안 점수를 업데이트합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - diner_grade: 음식점 등급 (int)
    - bayesian_score: 베이지안 평균 점수 (float)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_grade_bayesian(file, dry_run)


@router.post(
    "/kakao/restaurants/hidden-score",
    tags=["uploads"],
    summary="음식점 숨찐맛 점수 업로드",
)
async def upload_restaurant_hidden_score(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 음식점 숨찐맛 점수 업로드

    diner_hidden_score.csv 파일을 업로드하여 음식점 숨찐맛 점수를 업데이트합니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - hidden_score: 숨찐맛 점수 (float)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_hidden_score(file, dry_run)
