"""
Reviews 관련 SQL 쿼리 통합 파일
"""

# ============================================
# Reviews Queries
# ============================================

# Reviews CRUD 쿼리
INSERT_REVIEW = """
    INSERT INTO reviews (account_id, item_id, score, comment)
    VALUES (%s, %s, %s, %s)
    RETURNING id, account_id, item_id, score, comment, created_at, updated_at
"""

GET_REVIEW_BY_ID = """
    SELECT r.id, r.account_id, r.item_id, r.score, r.comment, r.created_at, r.updated_at,
           u.name as user_name, i.name as item_name
    FROM reviews r
    JOIN users u ON r.account_id = u.account_id
    JOIN items i ON r.item_id = i.id
    WHERE r.id = %s
"""

GET_ALL_REVIEWS = """
    SELECT r.id, r.account_id, r.item_id, r.score, r.comment, r.created_at, r.updated_at,
           u.name as user_name, i.name as item_name
    FROM reviews r
    JOIN users u ON r.account_id = u.account_id
    JOIN items i ON r.item_id = i.id
    ORDER BY r.created_at DESC LIMIT %s OFFSET %s
"""

GET_REVIEWS_BY_USER = """
    SELECT r.id, r.account_id, r.item_id, r.score, r.comment, r.created_at, r.updated_at,
           u.name as user_name, i.name as item_name
    FROM reviews r
    JOIN users u ON r.account_id = u.account_id
    JOIN items i ON r.item_id = i.id
    WHERE r.account_id = %s
    ORDER BY r.created_at DESC LIMIT %s OFFSET %s
"""

GET_REVIEWS_BY_ITEM = """
    SELECT r.id, r.account_id, r.item_id, r.score, r.comment, r.created_at, r.updated_at,
           u.name as user_name, i.name as item_name
    FROM reviews r
    JOIN users u ON r.account_id = u.account_id
    JOIN items i ON r.item_id = i.id
    WHERE r.item_id = %s
    ORDER BY r.created_at DESC LIMIT %s OFFSET %s
"""

UPDATE_REVIEW = """
    UPDATE reviews SET
        score = %s, comment = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, account_id, item_id, score, comment, created_at, updated_at
"""

DELETE_REVIEW = """
    DELETE FROM reviews WHERE id = %s
"""

COUNT_REVIEWS = """
    SELECT COUNT(*) FROM reviews
"""

COUNT_REVIEWS_BY_USER = """
    SELECT COUNT(*) FROM reviews WHERE account_id = %s
"""

COUNT_REVIEWS_BY_ITEM = """
    SELECT COUNT(*) FROM reviews WHERE item_id = %s
"""

GET_AVERAGE_RATING_BY_ITEM = """
    SELECT AVG(score) as average_rating, COUNT(*) as review_count
    FROM reviews WHERE item_id = %s
"""
