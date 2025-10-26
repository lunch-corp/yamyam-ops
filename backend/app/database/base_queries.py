"""
기본 테이블 관련 SQL 쿼리
"""

# Users 관련 쿼리
CHECK_USER_EXISTS = "SELECT id FROM users WHERE account_id = %s"
CHECK_USER_DUPLICATE = "SELECT id FROM users WHERE account_id = %s"

# Items 관련 쿼리
CHECK_ITEM_EXISTS = "SELECT id FROM items WHERE id = %s"

# Reviews 관련 쿼리
CHECK_REVIEW_EXISTS = "SELECT id FROM reviews WHERE id = %s"
CHECK_REVIEW_DUPLICATE = "SELECT id FROM reviews WHERE account_id = %s AND item_id = %s"

# Kakao Diner 관련 쿼리
CHECK_KAKAO_DINER_EXISTS_BY_PLACE_ID = (
    "SELECT id FROM kakao_diner WHERE kakao_place_id = %s"
)

# Kakao Reviewer 관련 쿼리
CHECK_KAKAO_REVIEWER_EXISTS = "SELECT id FROM kakao_reviewer WHERE kakao_user_id = %s"

# Kakao Review 관련 쿼리
CHECK_KAKAO_REVIEW_EXISTS = "SELECT id FROM kakao_review WHERE kakao_review_id = %s"
CHECK_KAKAO_REVIEW_DUPLICATE = "SELECT id FROM kakao_review WHERE kakao_review_id = %s"
