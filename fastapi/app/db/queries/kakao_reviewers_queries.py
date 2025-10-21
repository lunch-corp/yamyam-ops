"""
Kakao Reviewers 관련 SQL 쿼리
"""

# Kakao Reviewers CRUD 쿼리
INSERT_KAKAO_REVIEWER = """
    INSERT INTO kakao_reviewer (kakao_user_id, username, review_count, average_rating, badge_grade, badge_level)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id, kakao_user_id, username, review_count, average_rating, badge_grade, badge_level, crawled_at, updated_at
"""

GET_KAKAO_REVIEWER_BY_USER_ID = """
    SELECT id, kakao_user_id, username, review_count, average_rating, badge_grade, badge_level, crawled_at, updated_at
    FROM kakao_reviewer WHERE kakao_user_id = %s
"""

GET_ALL_KAKAO_REVIEWERS = """
    SELECT id, kakao_user_id, username, review_count, average_rating, badge_grade, badge_level, crawled_at, updated_at
    FROM kakao_reviewer ORDER BY review_count DESC LIMIT %s OFFSET %s
"""

UPDATE_KAKAO_REVIEWER = """
    UPDATE kakao_reviewer SET
        username = %s, review_count = %s, average_rating = %s, badge_grade = %s, badge_level = %s, updated_at = CURRENT_TIMESTAMP
    WHERE kakao_user_id = %s
    RETURNING id, kakao_user_id, username, review_count, average_rating, badge_grade, badge_level, crawled_at, updated_at
"""

DELETE_KAKAO_REVIEWER = """
    DELETE FROM kakao_reviewer WHERE kakao_user_id = %s
"""

COUNT_KAKAO_REVIEWERS = """
    SELECT COUNT(*) FROM kakao_reviewer
"""

GET_TOP_REVIEWERS = """
    SELECT id, kakao_user_id, username, review_count, average_rating, badge_grade, badge_level, crawled_at, updated_at
    FROM kakao_reviewer 
    ORDER BY review_count DESC, average_rating DESC 
    LIMIT %s
"""
