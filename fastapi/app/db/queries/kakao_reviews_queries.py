"""
Kakao Reviews 관련 SQL 쿼리
"""

# Kakao Reviews CRUD 쿼리
INSERT_KAKAO_REVIEW = """
    INSERT INTO kakao_review (kakao_place_id, kakao_user_id, kakao_review_id, rating, review_text, review_date)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id, kakao_place_id, kakao_user_id, kakao_review_id, rating, review_text, review_date, crawled_at, updated_at
"""

GET_KAKAO_REVIEW_BY_REVIEW_ID = """
    SELECT kr.id, kr.kakao_place_id, kr.kakao_user_id, kr.kakao_review_id, kr.rating, kr.review_text, kr.review_date, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kr2.username as reviewer_name
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    WHERE kr.kakao_review_id = %s
"""

GET_ALL_KAKAO_REVIEWS = """
    SELECT kr.id, kr.kakao_place_id, kr.kakao_user_id, kr.kakao_review_id, kr.rating, kr.review_text, kr.review_date, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kr2.username as reviewer_name
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    ORDER BY kr.review_date DESC LIMIT %s OFFSET %s
"""

GET_KAKAO_REVIEWS_BY_DINER = """
    SELECT kr.id, kr.kakao_place_id, kr.kakao_user_id, kr.kakao_review_id, kr.rating, kr.review_text, kr.review_date, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kr2.username as reviewer_name
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    WHERE kr.kakao_place_id = %s
    ORDER BY kr.review_date DESC LIMIT %s OFFSET %s
"""

GET_KAKAO_REVIEWS_BY_REVIEWER = """
    SELECT kr.id, kr.kakao_place_id, kr.kakao_user_id, kr.kakao_review_id, kr.rating, kr.review_text, kr.review_date, kr.crawled_at, kr.updated_at,
           kd.name as diner_name, kr2.username as reviewer_name
    FROM kakao_review kr
    JOIN kakao_diner kd ON kr.kakao_place_id = kd.kakao_place_id
    JOIN kakao_reviewer kr2 ON kr.kakao_user_id = kr2.kakao_user_id
    WHERE kr.kakao_user_id = %s
    ORDER BY kr.review_date DESC LIMIT %s OFFSET %s
"""

UPDATE_KAKAO_REVIEW = """
    UPDATE kakao_review SET
        rating = %s, review_text = %s, review_date = %s, updated_at = CURRENT_TIMESTAMP
    WHERE kakao_review_id = %s
    RETURNING id, kakao_place_id, kakao_user_id, kakao_review_id, rating, review_text, review_date, crawled_at, updated_at
"""

DELETE_KAKAO_REVIEW = """
    DELETE FROM kakao_review WHERE kakao_review_id = %s
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
