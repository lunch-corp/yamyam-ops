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


@router.post("/kakao/review-photos", tags=["uploads"], summary="리뷰 사진 정보 업로드")
async def upload_review_photos(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 리뷰 사진 정보 업로드

    review_photos.csv 파일을 업로드하여 리뷰 사진 정보를 등록합니다.
    동일한 id가 이미 존재하는 경우 UPSERT로 새 데이터로 업데이트됩니다.

    **필수 컬럼:**
    - review_id: 리뷰 고유 ID (String, kakao_review.review_id와 일치해야 함)
    - photo_url: 이미지 URL (Text)

    **선택 컬럼:**
    - original_photo_id: 원본 사진 ID (Integer, nullable)
    - media_type: 미디어 타입 (String, 기본값: "PHOTO")
    - status: 상태 (String, nullable)
    - display_order: 표시 순서 (Integer, 기본값: 0)
    - view_count: 조회수 (Integer, 기본값: 0)

    **주의사항:**
    - review_id는 kakao_review 테이블에 존재해야 합니다 (ForeignKey 제약조건)
    - id는 ULID로 자동 생성됩니다

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_review_photos(file, dry_run)


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


@router.post(
    "/kakao/restaurants/open-hours",
    tags=["uploads"],
    summary="음식점 영업시간 업로드",
)
async def upload_restaurant_open_hours(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 음식점 영업시간 업로드

    diner_open_hours.csv 파일을 업로드하여 음식점 영업시간 정보를 등록합니다.
    동일한 diner_idx와 day_of_week 조합이 이미 존재하는 경우 UPSERT로 새 데이터로 업데이트됩니다.

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - day_of_week: 요일 (int, 0=월요일, 1=화요일, ..., 6=일요일)
    - is_open: 영업 여부 (bool)

    **선택 컬럼:**
    - start_time: 영업 시작 시간 (str, 'HH:MM:SS' 형식, nullable)
    - end_time: 영업 종료 시간 (str, 'HH:MM:SS' 형식, nullable)
    - description: 추가 설명 (str, nullable - '휴무일', '24시간 영업' 등)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_open_hours(file, dry_run)


@router.post(
    "/kakao/restaurants/menus-new",
    tags=["uploads"],
    summary="음식점 메뉴 목록 업로드 (새 테이블)",
)
async def upload_restaurant_menus_new(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 음식점 메뉴 목록 CSV 파일 업로드

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)
    - name: 메뉴 이름 (str)
    - product_id: 상품 ID (str)

    **선택 컬럼:**
    - price: 가격 (float)
    - is_ai_mate: AI 메이트 메뉴 여부 (bool)
    - photo_url: 메뉴 사진 URL (str)
    - is_recommend: 추천 메뉴 여부 (bool)
    - desc: 메뉴 설명 (str)
    - mod_at: 수정 시각 (datetime)

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_menus_new(file, dry_run)


@router.post(
    "/kakao/restaurants/ai-data",
    tags=["uploads"],
    summary="음식점 AI 데이터 업로드",
)
async def upload_restaurant_ai_data(
    file: UploadFile = File(...),
    dry_run: bool = Query(False, description="실제 DB 작업 없이 검증만 수행"),
) -> dict:
    """
    카카오 음식점 AI 데이터 CSV 파일 업로드

    **필수 컬럼:**
    - diner_idx: 음식점 고유 인덱스 (int)

    **선택 컬럼:**
    - ai_bottom_sheet_title: AI 생성 제목 (str)
    - ai_bottom_sheet_summary: AI 생성 요약 (str)
    - ai_bottom_sheet_sheets: AI 생성 시트 데이터 (JSON 문자열)
    - ai_bottom_sheet_landing_url: 랜딩 URL (str)
    - blog_summaries: 블로그 요약 데이터 (JSON 문자열)

    **참고:**
    - ai_bottom_sheet_sheets와 blog_summaries는 JSON 문자열 형식으로 제공되어야 합니다.
    - all_keywords는 자동으로 생성됩니다 (JSONB 필드에서 keywords 추출).
    - 동일한 diner_idx가 이미 존재하는 경우 UPSERT로 새 데이터로 업데이트됩니다.

    dry_run=True인 경우 실제 DB 작업 없이 파일 검증만 수행합니다.
    """
    return await upload_service.upload_diner_ai_data(file, dry_run)
