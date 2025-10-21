"""
Users 관련 SQL 쿼리
"""

# Users CRUD 쿼리
INSERT_USER = """
    INSERT INTO users (account_id, name, email)
    VALUES (%s, %s, %s)
    RETURNING id, account_id, name, email, created_at, updated_at
"""

GET_USER_BY_ACCOUNT_ID = """
    SELECT id, account_id, name, email, created_at, updated_at
    FROM users WHERE account_id = %s
"""

GET_ALL_USERS = """
    SELECT id, account_id, name, email, created_at, updated_at
    FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s
"""

UPDATE_USER = """
    UPDATE users SET
        name = %s, email = %s, updated_at = CURRENT_TIMESTAMP
    WHERE account_id = %s
    RETURNING id, account_id, name, email, created_at, updated_at
"""

DELETE_USER = """
    DELETE FROM users WHERE account_id = %s
"""

COUNT_USERS = """
    SELECT COUNT(*) FROM users
"""
