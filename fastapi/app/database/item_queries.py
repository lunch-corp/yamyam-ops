"""
Items 관련 SQL 쿼리 통합 파일
"""

# ============================================
# Items Queries
# ============================================

# Items CRUD 쿼리
INSERT_ITEM = """
    INSERT INTO items (name, category, description, address, phone, latitude, longitude, rating, price_range)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    RETURNING id, name, category, description, address, phone, latitude, longitude, rating, price_range, created_at, updated_at
"""

GET_ITEM_BY_ID_WITH_CATEGORY = """
    SELECT id, name, category FROM items WHERE id = %s
"""

GET_ALL_ITEMS = """
    SELECT id, name, category, description, address, phone, latitude, longitude, rating, price_range, created_at, updated_at
    FROM items ORDER BY created_at DESC LIMIT %s OFFSET %s
"""

UPDATE_ITEM = """
    UPDATE items SET
        name = %s, category = %s, description = %s, address = %s, phone = %s,
        latitude = %s, longitude = %s, rating = %s, price_range = %s, updated_at = CURRENT_TIMESTAMP
    WHERE id = %s
    RETURNING id, name, category, description, address, phone, latitude, longitude, rating, price_range, created_at, updated_at
"""

DELETE_ITEM = """
    DELETE FROM items WHERE id = %s
"""

COUNT_ITEMS = """
    SELECT COUNT(*) FROM items
"""

SEARCH_ITEMS_BY_NAME = """
    SELECT id, name, category, description, address, phone, latitude, longitude, rating, price_range, created_at, updated_at
    FROM items WHERE name ILIKE %s ORDER BY name LIMIT %s OFFSET %s
"""

SEARCH_ITEMS_BY_CATEGORY = """
    SELECT id, name, category, description, address, phone, latitude, longitude, rating, price_range, created_at, updated_at
    FROM items WHERE category = %s ORDER BY name LIMIT %s OFFSET %s
"""
