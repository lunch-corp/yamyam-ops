"""
Kakao 데이터 관련 SQL 쿼리 통합 파일
"""

# ============================================
# Kakao Diner Queries
# ============================================

# 기본 정보 업로드용 (CSV 업로드) - PROCESSING_CONFIG와 일치하도록 업데이트
INSERT_KAKAO_DINER_BASIC = """
    INSERT INTO kakao_diner (
        id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
        diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
        diner_road_address, diner_num_address, diner_phone,
        diner_lat, diner_lon, diner_open_time,
        diner_grade, hidden_score, bayesian_score
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (diner_idx) DO UPDATE SET
        diner_name = EXCLUDED.diner_name,
        diner_tag = EXCLUDED.diner_tag,
        diner_menu_name = EXCLUDED.diner_menu_name,
        diner_menu_price = EXCLUDED.diner_menu_price,
        diner_review_cnt = EXCLUDED.diner_review_cnt,
        diner_review_avg = EXCLUDED.diner_review_avg,
        diner_blog_review_cnt = EXCLUDED.diner_blog_review_cnt,
        diner_review_tags = EXCLUDED.diner_review_tags,
        diner_road_address = EXCLUDED.diner_road_address,
        diner_num_address = EXCLUDED.diner_num_address,
        diner_phone = EXCLUDED.diner_phone,
        diner_lat = EXCLUDED.diner_lat,
        diner_lon = EXCLUDED.diner_lon,
        diner_open_time = EXCLUDED.diner_open_time,
        diner_grade = EXCLUDED.diner_grade,
        hidden_score = EXCLUDED.hidden_score,
        bayesian_score = EXCLUDED.bayesian_score,
        updated_at = CURRENT_TIMESTAMP
"""

UPDATE_KAKAO_DINER_CATEGORY = """
    UPDATE kakao_diner SET
        diner_category_large = %s,
        diner_category_middle = %s,
        diner_category_small = %s,
        diner_category_detail = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
"""

UPDATE_KAKAO_DINER_MENU = """
    UPDATE kakao_diner SET
        diner_menu_name = %s,
        diner_menu_price = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
"""

UPDATE_KAKAO_DINER_REVIEW = """
    UPDATE kakao_diner SET
        diner_review_cnt = %s,
        diner_review_avg = %s,
        diner_blog_review_cnt = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
"""

UPDATE_KAKAO_DINER_TAGS = """
    UPDATE kakao_diner SET
        diner_tag = %s,
        diner_review_tags = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
"""

UPDATE_KAKAO_DINER_GRADE_BAYESIAN = """
    UPDATE kakao_diner SET
        diner_grade = %s,
        bayesian_score = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
"""

UPDATE_KAKAO_DINER_HIDDEN_SCORE = """
    UPDATE kakao_diner SET
        hidden_score = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
"""

# 카테고리 테이블 관련 쿼리
INSERT_KAKAO_CATEGORY = """
    INSERT INTO kakao_diner_category (
        diner_idx, industry_category, diner_category_large,
        diner_category_middle, diner_category_small, diner_category_detail
    ) VALUES (%s, %s, %s, %s, %s, %s)
    ON CONFLICT (diner_idx) DO UPDATE SET
        industry_category = EXCLUDED.industry_category,
        diner_category_large = EXCLUDED.diner_category_large,
        diner_category_middle = EXCLUDED.diner_category_middle,
        diner_category_small = EXCLUDED.diner_category_small,
        diner_category_detail = EXCLUDED.diner_category_detail,
        updated_at = CURRENT_TIMESTAMP
"""

# 조회 쿼리
GET_KAKAO_DINER_BY_IDX = """
    SELECT id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
           diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
           diner_road_address, diner_num_address, diner_phone,
           diner_lat, diner_lon, diner_open_time,
           diner_grade, hidden_score, bayesian_score,
           diner_category_large, diner_category_middle, diner_category_small, diner_category_detail,
           crawled_at, updated_at
    FROM kakao_diner WHERE diner_idx = %s
"""

GET_KAKAO_DINER_BY_ID = """
    SELECT id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
           diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
           diner_road_address, diner_num_address, diner_phone,
           diner_lat, diner_lon, diner_open_time,
           diner_grade, hidden_score, bayesian_score,
           diner_category_large, diner_category_middle, diner_category_small, diner_category_detail,
           crawled_at, updated_at
    FROM kakao_diner WHERE id = %s
"""

GET_ALL_KAKAO_DINERS = """
    SELECT id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
           diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
           diner_road_address, diner_num_address, diner_phone,
           diner_lat, diner_lon, diner_open_time,
           diner_category_large, diner_category_middle, diner_category_small, diner_category_detail,
           diner_grade, hidden_score, bayesian_score,
           crawled_at, updated_at
    FROM kakao_diner ORDER BY diner_review_avg DESC NULLS LAST, diner_blog_review_cnt DESC
    LIMIT %s OFFSET %s
"""

GET_ALL_KAKAO_DINERS_API = """
    SELECT id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
           diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
           diner_road_address, diner_num_address, diner_phone,
           diner_lat, diner_lon, diner_open_time,
           diner_grade, hidden_score, bayesian_score,
           crawled_at, updated_at
    FROM kakao_diner ORDER BY id LIMIT %s OFFSET %s
"""

COUNT_KAKAO_DINERS = """
    SELECT COUNT(*) FROM kakao_diner
"""

# 존재 확인 쿼리
CHECK_KAKAO_DINER_EXISTS_BY_IDX = """
    SELECT 1 FROM kakao_diner WHERE diner_idx = %s
"""

# 업데이트 쿼리
UPDATE_KAKAO_DINER_BY_IDX = """
    UPDATE kakao_diner SET
        diner_name = %s, diner_tag = %s, diner_menu_name = %s, diner_menu_price = %s,
        diner_review_cnt = %s, diner_review_avg = %s, diner_blog_review_cnt = %s,
        diner_review_tags = %s, diner_road_address = %s, diner_num_address = %s,
        diner_phone = %s, diner_lat = %s, diner_lon = %s,
        diner_grade = %s, hidden_score = %s, bayesian_score = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
    RETURNING id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
              diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
              diner_road_address, diner_num_address, diner_phone,
              diner_lat, diner_lon, diner_open_time,
              diner_grade, hidden_score, bayesian_score,
              crawled_at, updated_at
"""

# 삭제 쿼리
DELETE_KAKAO_DINER_BY_IDX = """
    DELETE FROM kakao_diner WHERE diner_idx = %s RETURNING id
"""

DELETE_ALL_KAKAO_DINERS = """
    DELETE FROM kakao_diner
"""

# ============================================
# Kakao Reviewer Queries
# ============================================

# 카카오 리뷰어 생성
INSERT_KAKAO_REVIEWER = """
    INSERT INTO kakao_reviewer (
        id, reviewer_id, reviewer_user_name,
        reviewer_review_cnt, reviewer_avg, badge_grade, badge_level
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (reviewer_id) DO UPDATE SET
        reviewer_user_name = EXCLUDED.reviewer_user_name,
        reviewer_review_cnt = EXCLUDED.reviewer_review_cnt,
        reviewer_avg = EXCLUDED.reviewer_avg,
        badge_grade = EXCLUDED.badge_grade,
        badge_level = EXCLUDED.badge_level,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id, reviewer_id, reviewer_user_name,
              reviewer_review_cnt, reviewer_avg, badge_grade, badge_level,
              crawled_at, updated_at
"""

# 카카오 리뷰어 조회
GET_KAKAO_REVIEWER_BY_ID = """
    SELECT id, reviewer_id, reviewer_user_name,
           reviewer_review_cnt, reviewer_avg, badge_grade, badge_level,
           crawled_at, updated_at
    FROM kakao_reviewer WHERE reviewer_id = %s
"""

GET_ALL_KAKAO_REVIEWERS = """
    SELECT id, reviewer_id, reviewer_user_name,
           reviewer_review_cnt, reviewer_avg, badge_grade, badge_level,
           crawled_at, updated_at
    FROM kakao_reviewer ORDER BY reviewer_review_cnt DESC, reviewer_avg DESC
"""

GET_ALL_KAKAO_REVIEWERS_PAGINATED = """
    SELECT id, reviewer_id, reviewer_user_name,
           reviewer_review_cnt, reviewer_avg, badge_grade, badge_level,
           crawled_at, updated_at
    FROM kakao_reviewer ORDER BY reviewer_review_cnt DESC, reviewer_avg DESC
    LIMIT %s OFFSET %s
"""

# 존재 확인 쿼리
CHECK_KAKAO_REVIEWER_EXISTS = """
    SELECT 1 FROM kakao_reviewer WHERE reviewer_id = %s
"""

# 업데이트 쿼리
UPDATE_KAKAO_REVIEWER_BY_ID = """
    UPDATE kakao_reviewer SET
        reviewer_user_name = %s, reviewer_review_cnt = %s, reviewer_avg = %s,
        badge_grade = %s, badge_level = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE reviewer_id = %s
    RETURNING id, reviewer_id, reviewer_user_name,
              reviewer_review_cnt, reviewer_avg, badge_grade, badge_level,
              crawled_at, updated_at
"""

# 삭제 쿼리
DELETE_KAKAO_REVIEWER_BY_ID = """
    DELETE FROM kakao_reviewer WHERE reviewer_id = %s RETURNING id
"""

COUNT_KAKAO_REVIEWERS = """
    SELECT COUNT(*) FROM kakao_reviewer
"""

GET_TOP_REVIEWERS = """
    SELECT id, reviewer_id, reviewer_user_name,
           reviewer_review_cnt, reviewer_avg, badge_grade, badge_level,
           crawled_at, updated_at
    FROM kakao_reviewer
    ORDER BY reviewer_review_cnt DESC, reviewer_avg DESC
    LIMIT %s
"""

# ============================================
# Kakao Review Queries
# ============================================

# 카카오 리뷰 생성
INSERT_KAKAO_REVIEW = """
    INSERT INTO kakao_review (
        id, diner_idx, reviewer_id, review_id,
        reviewer_review, reviewer_review_date, reviewer_review_score
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (review_id) DO UPDATE SET
        diner_idx = EXCLUDED.diner_idx,
        reviewer_id = EXCLUDED.reviewer_id,
        reviewer_review = EXCLUDED.reviewer_review,
        reviewer_review_date = EXCLUDED.reviewer_review_date,
        reviewer_review_score = EXCLUDED.reviewer_review_score,
        updated_at = CURRENT_TIMESTAMP
    RETURNING id, diner_idx, reviewer_id, review_id,
              reviewer_review, reviewer_review_date, reviewer_review_score,
              crawled_at, updated_at
"""

# 카카오 리뷰 조회 (상세 정보 포함)
GET_KAKAO_REVIEW_BY_ID = """
    SELECT kr.id, kr.diner_idx, kr.reviewer_id, kr.review_id,
           kr.reviewer_review, kr.reviewer_review_date, kr.reviewer_review_score,
           kr.crawled_at, kr.updated_at,
           kd.diner_name, kd.diner_tag,
           kr2.reviewer_user_name
    FROM kakao_review kr
    LEFT JOIN kakao_diner kd ON kr.diner_idx = kd.diner_idx
    LEFT JOIN kakao_reviewer kr2 ON kr.reviewer_id = kr2.reviewer_id
    WHERE kr.review_id = %s
"""

GET_ALL_KAKAO_REVIEWS = """
    SELECT kr.id, kr.diner_idx, kr.reviewer_id, kr.review_id,
           kr.reviewer_review, kr.reviewer_review_date, kr.reviewer_review_score,
           kr.crawled_at, kr.updated_at,
           kd.diner_name, kd.diner_tag,
           kr2.reviewer_user_name
    FROM kakao_review kr
    LEFT JOIN kakao_diner kd ON kr.diner_idx = kd.diner_idx
    LEFT JOIN kakao_reviewer kr2 ON kr.reviewer_id = kr2.reviewer_id
    ORDER BY kr.reviewer_review_score DESC, kr.crawled_at DESC
"""

GET_ALL_KAKAO_REVIEWS_PAGINATED = """
    SELECT kr.id, kr.diner_idx, kr.reviewer_id, kr.review_id,
           kr.reviewer_review, kr.reviewer_review_date, kr.reviewer_review_score,
           kr.crawled_at, kr.updated_at, kr2.reviewer_user_name
    FROM kakao_review kr
    LEFT JOIN kakao_reviewer kr2 ON kr.reviewer_id = kr2.reviewer_id
    ORDER BY kr.reviewer_review_score DESC, kr.crawled_at DESC LIMIT %s OFFSET %s
"""

# 필터링이 있는 경우의 기본 쿼리 템플릿
GET_KAKAO_REVIEWS_BASE_QUERY = """
    SELECT kr.id, kr.diner_idx, kr.reviewer_id, kr.review_id,
           kr.reviewer_review, kr.reviewer_review_date, kr.reviewer_review_score,
           kr.crawled_at, kr.updated_at,
           kd.diner_name, kd.diner_tag,
           kr2.reviewer_user_name
    FROM kakao_review kr
    LEFT JOIN kakao_diner kd ON kr.diner_idx = kd.diner_idx
    LEFT JOIN kakao_reviewer kr2 ON kr.reviewer_id = kr2.reviewer_id
"""

GET_KAKAO_REVIEWS_BY_DINER = """
    SELECT kr.id, kr.diner_idx, kr.reviewer_id, kr.review_id,
           kr.reviewer_review, kr.reviewer_review_date, kr.reviewer_review_score,
           kr.crawled_at, kr.updated_at,
           kd.diner_name, kd.diner_tag,
           kr2.reviewer_user_name
    FROM kakao_review kr
    LEFT JOIN kakao_diner kd ON kr.diner_idx = kd.diner_idx
    LEFT JOIN kakao_reviewer kr2 ON kr.reviewer_id = kr2.reviewer_id
    WHERE kr.diner_idx = %s
    ORDER BY kr.reviewer_review_score DESC, kr.crawled_at DESC LIMIT %s OFFSET %s
"""

GET_KAKAO_REVIEWS_BY_REVIEWER = """
    SELECT kr.id, kr.diner_idx, kr.reviewer_id, kr.review_id,
           kr.reviewer_review, kr.reviewer_review_date, kr.reviewer_review_score,
           kr.crawled_at, kr.updated_at,
           kd.diner_name, kd.diner_tag,
           kr2.reviewer_user_name
    FROM kakao_review kr
    LEFT JOIN kakao_diner kd ON kr.diner_idx = kd.diner_idx
    LEFT JOIN kakao_reviewer kr2 ON kr.reviewer_id = kr2.reviewer_id
    WHERE kr.reviewer_id = %s
    ORDER BY kr.reviewer_review_score DESC, kr.crawled_at DESC LIMIT %s OFFSET %s
"""

# 존재 확인 쿼리
CHECK_KAKAO_REVIEW_EXISTS = """
    SELECT 1 FROM kakao_review WHERE review_id = %s
"""

CHECK_KAKAO_DINER_EXISTS_BY_IDX = """
    SELECT 1 FROM kakao_diner WHERE diner_idx = %s
"""

CHECK_KAKAO_REVIEW_DUPLICATE = """
    SELECT 1 FROM kakao_review WHERE review_id = %s
"""

# 업데이트 쿼리
UPDATE_KAKAO_REVIEW_BY_ID = """
    UPDATE kakao_review SET
        reviewer_review = %s, reviewer_review_date = %s, reviewer_review_score = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE review_id = %s
    RETURNING id, diner_idx, reviewer_id, review_id,
              reviewer_review, reviewer_review_date, reviewer_review_score,
              crawled_at, updated_at
"""

# 삭제 쿼리
DELETE_KAKAO_REVIEW_BY_ID = """
    DELETE FROM kakao_review WHERE review_id = %s RETURNING id
"""

COUNT_KAKAO_REVIEWS = """
    SELECT COUNT(*) FROM kakao_review
"""

# ============================================
# Review Photos Queries
# ============================================

# 리뷰 사진 생성
INSERT_REVIEW_PHOTO = """
    INSERT INTO review_photos (
        id, review_id, photo_url, original_photo_id,
        media_type, status, display_order, view_count
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        review_id = EXCLUDED.review_id,
        photo_url = EXCLUDED.photo_url,
        original_photo_id = EXCLUDED.original_photo_id,
        media_type = EXCLUDED.media_type,
        status = EXCLUDED.status,
        display_order = EXCLUDED.display_order,
        view_count = EXCLUDED.view_count
    RETURNING id, review_id, photo_url, original_photo_id,
              media_type, status, display_order, view_count, created_at
"""

COUNT_KAKAO_REVIEWS_BY_DINER = """
    SELECT COUNT(*) FROM kakao_review WHERE diner_idx = %s
"""

COUNT_KAKAO_REVIEWS_BY_REVIEWER = """
    SELECT COUNT(*) FROM kakao_review WHERE reviewer_id = %s
"""

# ============================================
# Kakao Diner Open Hours Queries
# ============================================

# 영업시간 정보 생성 (UPSERT)
INSERT_KAKAO_DINER_OPEN_HOURS = """
    INSERT INTO kakao_diner_open_hours (
        id, diner_idx, day_of_week, is_open, start_time, end_time, description
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (diner_idx, day_of_week) DO UPDATE SET
        is_open = EXCLUDED.is_open,
        start_time = EXCLUDED.start_time,
        end_time = EXCLUDED.end_time,
        description = EXCLUDED.description,
        updated_at = CURRENT_TIMESTAMP
"""

# 특정 음식점의 영업시간 조회
GET_KAKAO_DINER_OPEN_HOURS_BY_DINER_IDX = """
    SELECT id, diner_idx, day_of_week, is_open, start_time, end_time, description,
           created_at, updated_at
    FROM kakao_diner_open_hours
    WHERE diner_idx = %s
    ORDER BY day_of_week
"""

# 특정 음식점의 특정 요일 영업시간 조회
GET_KAKAO_DINER_OPEN_HOURS_BY_DINER_AND_DAY = """
    SELECT id, diner_idx, day_of_week, is_open, start_time, end_time, description,
           created_at, updated_at
    FROM kakao_diner_open_hours
    WHERE diner_idx = %s AND day_of_week = %s
"""

# ID로 영업시간 조회
GET_KAKAO_DINER_OPEN_HOURS_BY_ID = """
    SELECT id, diner_idx, day_of_week, is_open, start_time, end_time, description,
           created_at, updated_at
    FROM kakao_diner_open_hours
    WHERE id = %s
"""

# 영업시간 업데이트
UPDATE_KAKAO_DINER_OPEN_HOURS_BY_ID = """
    UPDATE kakao_diner_open_hours SET
        diner_idx = %s,
        day_of_week = %s,
        is_open = %s,
        start_time = %s,
        end_time = %s,
        description = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, diner_idx, day_of_week, is_open, start_time, end_time, description,
              created_at, updated_at
"""

# ID로 영업시간 삭제
DELETE_KAKAO_DINER_OPEN_HOURS_BY_ID = """
    DELETE FROM kakao_diner_open_hours WHERE id = %s RETURNING id
"""

# 특정 음식점의 영업시간 삭제
DELETE_KAKAO_DINER_OPEN_HOURS_BY_DINER_IDX = """
    DELETE FROM kakao_diner_open_hours WHERE diner_idx = %s
"""

# 특정 요일에 영업하는 음식점 조회
GET_DINERS_OPEN_ON_DAY = """
    SELECT DISTINCT diner_idx
    FROM kakao_diner_open_hours
    WHERE day_of_week = %s AND is_open = TRUE
"""

# 특정 시간대에 영업하는 음식점 조회
GET_DINERS_OPEN_AT_TIME = """
    SELECT DISTINCT diner_idx
    FROM kakao_diner_open_hours
    WHERE day_of_week = %s 
      AND is_open = TRUE
      AND start_time <= %s
      AND end_time >= %s
"""

# ============================================
# Kakao Diner Menu Queries
# ============================================

# 메뉴 생성 (UPSERT)
INSERT_KAKAO_DINER_MENU = """
    INSERT INTO kakao_diner_menus (
        id, diner_idx, name, product_id, price, is_ai_mate, 
        photo_url, is_recommend, "desc", mod_at
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO UPDATE SET
        diner_idx = EXCLUDED.diner_idx,
        name = EXCLUDED.name,
        product_id = EXCLUDED.product_id,
        price = EXCLUDED.price,
        is_ai_mate = EXCLUDED.is_ai_mate,
        photo_url = EXCLUDED.photo_url,
        is_recommend = EXCLUDED.is_recommend,
        "desc" = EXCLUDED."desc",
        mod_at = EXCLUDED.mod_at,
        updated_at = CURRENT_TIMESTAMP
"""

# 메뉴 ID로 조회
GET_KAKAO_DINER_MENU_BY_ID = """
    SELECT id, diner_idx, name, product_id, price, is_ai_mate,
           photo_url, is_recommend, "desc", mod_at,
           created_at, updated_at
    FROM kakao_diner_menus
    WHERE id = %s
"""

# diner_idx로 메뉴 목록 조회
GET_KAKAO_DINER_MENUS_BY_DINER_IDX = """
    SELECT id, diner_idx, name, product_id, price, is_ai_mate,
           photo_url, is_recommend, "desc", mod_at,
           created_at, updated_at
    FROM kakao_diner_menus
    WHERE diner_idx = %s
    ORDER BY is_recommend DESC NULLS LAST, name
"""

# 메뉴 목록 조회 (필터링 지원)
GET_KAKAO_DINER_MENUS_BASE = """
    SELECT id, diner_idx, name, product_id, price, is_ai_mate,
           photo_url, is_recommend, "desc", mod_at,
           created_at, updated_at
    FROM kakao_diner_menus
"""

# 메뉴 업데이트
UPDATE_KAKAO_DINER_MENU_BY_ID = """
    UPDATE kakao_diner_menus SET
        diner_idx = %s,
        name = %s,
        product_id = %s,
        price = %s,
        is_ai_mate = %s,
        photo_url = %s,
        is_recommend = %s,
        "desc" = %s,
        mod_at = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, diner_idx, name, product_id, price, is_ai_mate,
              photo_url, is_recommend, "desc", mod_at,
              created_at, updated_at
"""

# 메뉴 삭제
DELETE_KAKAO_DINER_MENU_BY_ID = """
    DELETE FROM kakao_diner_menus WHERE id = %s RETURNING id
"""

# diner_idx로 메뉴 삭제
DELETE_KAKAO_DINER_MENUS_BY_DINER_IDX = """
    DELETE FROM kakao_diner_menus WHERE diner_idx = %s
"""

# 메뉴 개수 조회
COUNT_KAKAO_DINER_MENUS = """
    SELECT COUNT(*) FROM kakao_diner_menus
"""

# diner_idx로 메뉴 개수 조회
COUNT_KAKAO_DINER_MENUS_BY_DINER_IDX = """
    SELECT COUNT(*) FROM kakao_diner_menus WHERE diner_idx = %s
"""

# ============================================
# Kakao Diner AI Data Queries
# ============================================

# AI 데이터 생성 (UPSERT)
INSERT_KAKAO_DINER_AI_DATA = """
    INSERT INTO kakao_diner_ai_data (
        id, diner_idx, ai_bottom_sheet_title, ai_bottom_sheet_summary,
        ai_bottom_sheet_sheets, ai_bottom_sheet_landing_url, blog_summaries, all_keywords
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (diner_idx) DO UPDATE SET
        ai_bottom_sheet_title = EXCLUDED.ai_bottom_sheet_title,
        ai_bottom_sheet_summary = EXCLUDED.ai_bottom_sheet_summary,
        ai_bottom_sheet_sheets = EXCLUDED.ai_bottom_sheet_sheets,
        ai_bottom_sheet_landing_url = EXCLUDED.ai_bottom_sheet_landing_url,
        blog_summaries = EXCLUDED.blog_summaries,
        all_keywords = EXCLUDED.all_keywords,
        updated_at = CURRENT_TIMESTAMP
"""

# AI 데이터 ID로 조회
GET_KAKAO_DINER_AI_DATA_BY_ID = """
    SELECT id, diner_idx, ai_bottom_sheet_title, ai_bottom_sheet_summary,
           ai_bottom_sheet_sheets, ai_bottom_sheet_landing_url, blog_summaries, all_keywords,
           created_at, updated_at
    FROM kakao_diner_ai_data
    WHERE id = %s
"""

# AI 데이터 diner_idx로 조회
GET_KAKAO_DINER_AI_DATA_BY_DINER_IDX = """
    SELECT id, diner_idx, ai_bottom_sheet_title, ai_bottom_sheet_summary,
           ai_bottom_sheet_sheets, ai_bottom_sheet_landing_url, blog_summaries, all_keywords,
           created_at, updated_at
    FROM kakao_diner_ai_data
    WHERE diner_idx = %s
"""

# AI 데이터 업데이트
UPDATE_KAKAO_DINER_AI_DATA_BY_ID = """
    UPDATE kakao_diner_ai_data SET
        diner_idx = %s,
        ai_bottom_sheet_title = %s,
        ai_bottom_sheet_summary = %s,
        ai_bottom_sheet_sheets = %s,
        ai_bottom_sheet_landing_url = %s,
        blog_summaries = %s,
        all_keywords = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, diner_idx, ai_bottom_sheet_title, ai_bottom_sheet_summary,
              ai_bottom_sheet_sheets, ai_bottom_sheet_landing_url, blog_summaries, all_keywords,
              created_at, updated_at
"""

# AI 데이터 삭제
DELETE_KAKAO_DINER_AI_DATA_BY_ID = """
    DELETE FROM kakao_diner_ai_data WHERE id = %s RETURNING id
"""

# AI 데이터 diner_idx로 삭제
DELETE_KAKAO_DINER_AI_DATA_BY_DINER_IDX = """
    DELETE FROM kakao_diner_ai_data WHERE diner_idx = %s RETURNING id
"""

# AI 데이터 개수 조회
COUNT_KAKAO_DINER_AI_DATA = """
    SELECT COUNT(*) FROM kakao_diner_ai_data
"""

# AI 데이터 CSV 업로드용 (UPSERT, all_keywords는 서비스에서 생성)
# updated_at 컬럼이 없을 수 있으므로 조건부로 처리
INSERT_KAKAO_DINER_AI_DATA_CSV = """
    INSERT INTO kakao_diner_ai_data (
        id, diner_idx, ai_bottom_sheet_title, ai_bottom_sheet_summary,
        ai_bottom_sheet_sheets, ai_bottom_sheet_landing_url, blog_summaries
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (diner_idx) DO UPDATE SET
        ai_bottom_sheet_title = EXCLUDED.ai_bottom_sheet_title,
        ai_bottom_sheet_summary = EXCLUDED.ai_bottom_sheet_summary,
        ai_bottom_sheet_sheets = EXCLUDED.ai_bottom_sheet_sheets,
        ai_bottom_sheet_landing_url = EXCLUDED.ai_bottom_sheet_landing_url,
        blog_summaries = EXCLUDED.blog_summaries
"""
