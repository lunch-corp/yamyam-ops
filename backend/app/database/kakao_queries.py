"""
Kakao 데이터 관련 SQL 쿼리 통합 파일
"""

# ============================================
# Kakao Diner Queries
# ============================================

# 기본 정보 업로드용 (CSV 업로드) - PROCESSING_CONFIG와 일치하도록 업데이트
INSERT_KAKAO_DINER_BASIC = """
    INSERT INTO kakao_diner (
        diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
        diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
        diner_road_address, diner_num_address, diner_phone,
        diner_lat, diner_lon, diner_open_time
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
           crawled_at, updated_at
    FROM kakao_diner WHERE diner_idx = %s
"""

GET_ALL_KAKAO_DINERS = """
    SELECT id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
           diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
           diner_road_address, diner_num_address, diner_phone,
           diner_lat, diner_lon, diner_open_time,
           crawled_at, updated_at
    FROM kakao_diner ORDER BY diner_review_avg DESC NULLS LAST, diner_blog_review_cnt DESC
    LIMIT %s OFFSET %s
"""

GET_ALL_KAKAO_DINERS_API = """
    SELECT id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
           diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
           diner_road_address, diner_num_address, diner_phone,
           diner_lat, diner_lon, diner_open_time,
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
        diner_phone = %s, diner_lat = %s, diner_lon = %s, updated_at = CURRENT_TIMESTAMP
    WHERE diner_idx = %s
    RETURNING id, diner_idx, diner_name, diner_tag, diner_menu_name, diner_menu_price,
              diner_review_cnt, diner_review_avg, diner_blog_review_cnt, diner_review_tags,
              diner_road_address, diner_num_address, diner_phone,
              diner_lat, diner_lon, diner_open_time,
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
        id, kakao_user_id, nickname, profile_image_url,
        review_count, follower_count, following_count, is_verified
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, kakao_user_id, nickname, profile_image_url,
              review_count, follower_count, following_count, is_verified,
              crawled_at, updated_at
"""

# 카카오 리뷰어 조회
GET_KAKAO_REVIEWER_BY_USER_ID = """
    SELECT id, kakao_user_id, nickname, profile_image_url,
           review_count, follower_count, following_count, is_verified,
           crawled_at, updated_at
    FROM kakao_reviewer WHERE kakao_user_id = %s
"""

GET_ALL_KAKAO_REVIEWERS = """
    SELECT id, kakao_user_id, nickname, profile_image_url,
           review_count, follower_count, following_count, is_verified,
           crawled_at, updated_at
    FROM kakao_reviewer ORDER BY review_count DESC, follower_count DESC
    LIMIT %s OFFSET %s
"""

# 존재 확인 쿼리
CHECK_KAKAO_REVIEWER_EXISTS = """
    SELECT 1 FROM kakao_reviewer WHERE kakao_user_id = %s
"""

# 업데이트 쿼리
UPDATE_KAKAO_REVIEWER_BY_USER_ID = """
    UPDATE kakao_reviewer SET
        nickname = %s, profile_image_url = %s, review_count = %s,
        follower_count = %s, following_count = %s, is_verified = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE kakao_user_id = %s
    RETURNING id, kakao_user_id, nickname, profile_image_url,
              review_count, follower_count, following_count, is_verified,
              crawled_at, updated_at
"""

# 삭제 쿼리
DELETE_KAKAO_REVIEWER_BY_USER_ID = """
    DELETE FROM kakao_reviewer WHERE kakao_user_id = %s RETURNING id
"""

COUNT_KAKAO_REVIEWERS = """
    SELECT COUNT(*) FROM kakao_reviewer
"""

GET_TOP_REVIEWERS = """
    SELECT id, kakao_user_id, nickname, profile_image_url,
           review_count, follower_count, following_count, is_verified,
           crawled_at, updated_at
    FROM kakao_reviewer 
    ORDER BY review_count DESC, follower_count DESC 
    LIMIT %s
"""

# ============================================
# Kakao Review Queries
# ============================================

# 카카오 리뷰 생성
INSERT_KAKAO_REVIEW = """
    INSERT INTO kakao_review (
        id, kakao_review_id, kakao_place_id, kakao_user_id, rating,
        review_text, review_images, visit_date, visit_type, helpful_count
    )
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, kakao_review_id, kakao_place_id, kakao_user_id, rating,
              review_text, review_images, visit_date, visit_type, helpful_count,
              crawled_at, updated_at
"""

# 카카오 리뷰 조회 (상세 정보 포함)
GET_KAKAO_REVIEW_BY_REVIEW_ID = """
    SELECT kr.id, kr.kakao_review_id, kr.kakao_place_id, kr.kakao_user_id,
           kr.rating, kr.review_text, kr.review_images, kr.visit_date,
           kr.visit_type, kr.helpful_count, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kd.category as diner_category,
           kr2.nickname as reviewer_nickname
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    WHERE kr.kakao_review_id = %s
"""

GET_ALL_KAKAO_REVIEWS = """
    SELECT kr.id, kr.kakao_review_id, kr.kakao_place_id, kr.kakao_user_id,
           kr.rating, kr.review_text, kr.review_images, kr.visit_date,
           kr.visit_type, kr.helpful_count, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kd.category as diner_category,
           kr2.nickname as reviewer_nickname
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    ORDER BY kr.helpful_count DESC, kr.crawled_at DESC LIMIT %s OFFSET %s
"""

# 필터링이 있는 경우의 기본 쿼리 템플릿
GET_KAKAO_REVIEWS_BASE_QUERY = """
    SELECT kr.id, kr.kakao_review_id, kr.kakao_place_id, kr.kakao_user_id,
           kr.rating, kr.review_text, kr.review_images, kr.visit_date,
           kr.visit_type, kr.helpful_count, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kd.category as diner_category,
           kr2.nickname as reviewer_nickname
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
"""

GET_KAKAO_REVIEWS_BY_DINER = """
    SELECT kr.id, kr.kakao_review_id, kr.kakao_place_id, kr.kakao_user_id,
           kr.rating, kr.review_text, kr.review_images, kr.visit_date,
           kr.visit_type, kr.helpful_count, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kd.category as diner_category,
           kr2.nickname as reviewer_nickname
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    WHERE kr.kakao_place_id = %s
    ORDER BY kr.helpful_count DESC, kr.crawled_at DESC LIMIT %s OFFSET %s
"""

GET_KAKAO_REVIEWS_BY_REVIEWER = """
    SELECT kr.id, kr.kakao_review_id, kr.kakao_place_id, kr.kakao_user_id,
           kr.rating, kr.review_text, kr.review_images, kr.visit_date,
           kr.visit_type, kr.helpful_count, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kd.category as diner_category,
           kr2.nickname as reviewer_nickname
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    WHERE kr.kakao_user_id = %s
    ORDER BY kr.helpful_count DESC, kr.crawled_at DESC LIMIT %s OFFSET %s
"""

# 존재 확인 쿼리
CHECK_KAKAO_REVIEW_EXISTS = """
    SELECT 1 FROM kakao_review WHERE kakao_review_id = %s
"""

CHECK_KAKAO_DINER_EXISTS_BY_PLACE_ID = """
    SELECT 1 FROM kakao_diner WHERE kakao_place_id = %s
"""

CHECK_KAKAO_REVIEW_DUPLICATE = """
    SELECT 1 FROM kakao_review WHERE kakao_review_id = %s
"""

# 업데이트 쿼리
UPDATE_KAKAO_REVIEW_BY_REVIEW_ID = """
    UPDATE kakao_review SET
        rating = %s, review_text = %s, review_images = %s,
        visit_date = %s, visit_type = %s, helpful_count = %s,
        updated_at = CURRENT_TIMESTAMP
    WHERE kakao_review_id = %s
    RETURNING id, kakao_review_id, kakao_place_id, kakao_user_id, rating,
              review_text, review_images, visit_date, visit_type, helpful_count,
              crawled_at, updated_at
"""

# 삭제 쿼리
DELETE_KAKAO_REVIEW_BY_REVIEW_ID = """
    DELETE FROM kakao_review WHERE kakao_review_id = %s RETURNING id
"""

COUNT_KAKAO_REVIEWS = """
    SELECT COUNT(*) FROM kakao_review
"""

COUNT_KAKAO_REVIEWS_BY_DINER = """
    SELECT COUNT(*) FROM kakao_review WHERE kakao_place_id = %s
"""

COUNT_KAKAO_REVIEWS_BY_REVIEWER = """
    SELECT COUNT(*) FROM kakao_review WHERE kakao_user_id = %s
"""
