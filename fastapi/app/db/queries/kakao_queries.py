"""
Kakao 데이터 관련 SQL 쿼리
"""

# Kakao Diner 관련 쿼리

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

# API용 쿼리는 CSV 업로드로 대체되어 제거됨

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
    SELECT * FROM kakao_diner WHERE diner_idx = %s
"""

# kakao_place_id 제거로 인해 삭제됨

GET_ALL_KAKAO_DINERS = """
    SELECT * FROM kakao_diner ORDER BY diner_idx LIMIT %s OFFSET %s
"""

GET_ALL_KAKAO_DINERS_API = """
    SELECT * FROM kakao_diner ORDER BY id LIMIT %s OFFSET %s
"""

COUNT_KAKAO_DINERS = """
    SELECT COUNT(*) FROM kakao_diner
"""

# 업데이트 쿼리는 CSV 업로드로 대체됨

# 삭제 쿼리
DELETE_KAKAO_DINER = """
    DELETE FROM kakao_diner WHERE diner_idx = %s
"""

# kakao_place_id 제거로 인해 삭제됨

DELETE_ALL_KAKAO_DINERS = """
    DELETE FROM kakao_diner
"""

# Item-Kakao Mapping 관련 쿼리
GET_ITEM_KAKAO_MAPPING_WITH_DETAILS = """
    SELECT ikm.id, ikm.item_id, ikm.diner_idx, ikm.mapping_type,
           ikm.confidence_score, ikm.created_at, ikm.updated_at,
           i.name as item_name, i.category as item_category,
           kd.diner_name as kakao_diner_name, kd.diner_tag as kakao_diner_category
    FROM item_kakao_mapping ikm
    JOIN items i ON ikm.item_id = i.id
    JOIN kakao_diner kd ON ikm.diner_idx = kd.diner_idx
    WHERE ikm.id = %s
"""

# 추천 시스템 관련 쿼리
GET_USER_REVIEWS_FOR_RECOMMENDATION = """
    SELECT i.id, i.name, i.category, r.score
    FROM reviews r
    JOIN items i ON r.item_id = i.id
    WHERE r.account_id = %s
    ORDER BY r.score DESC
"""

GET_POPULAR_ITEMS_FOR_RECOMMENDATION = """
    SELECT i.id, i.name, i.category, AVG(r.score) as avg_score
    FROM items i
    LEFT JOIN reviews r ON i.id = r.item_id
    GROUP BY i.id, i.name, i.category
    ORDER BY avg_score DESC NULLS LAST, i.id
    LIMIT %s
"""

GET_SIMILAR_ITEMS_BY_CATEGORY = """
    SELECT i.id, i.name, i.category, AVG(r.score) as avg_score
    FROM items i
    LEFT JOIN reviews r ON i.id = r.item_id
    WHERE i.category = %s AND i.id != %s
    GROUP BY i.id, i.name, i.category
    ORDER BY avg_score DESC NULLS LAST, i.id
    LIMIT %s
"""
