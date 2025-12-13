"""
Users 관련 SQL 쿼리
"""

# Users CRUD 쿼리
CHECK_USER_EXISTS = "SELECT 1 FROM users WHERE firebase_uid = %s"
CHECK_USER_EXISTS_BY_ID = "SELECT 1 FROM users WHERE id = %s"

INSERT_USER = """
INSERT INTO users (id, firebase_uid, name, email, display_name, photo_url, kakao_reviewer_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
RETURNING id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
          created_at, updated_at,
          is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
          location, location_method, user_lat, user_lon,
          birth_year, gender, dining_companions,
          regular_budget, special_budget,
          spice_level, allergies, dislikes,
          food_preferences_large, food_preferences_middle,
          restaurant_ratings
"""

GET_USER_BY_ID = """
SELECT id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
       created_at, updated_at,
       is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
       location, location_method, user_lat, user_lon,
       birth_year, gender, dining_companions,
       regular_budget, special_budget,
       spice_level, allergies, dislikes,
       food_preferences_large, food_preferences_middle,
       restaurant_ratings
FROM users WHERE id = %s
"""

GET_USER_BY_FIREBASE_UID = """
SELECT id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
       created_at, updated_at,
       is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
       location, location_method, user_lat, user_lon,
       birth_year, gender, dining_companions,
       regular_budget, special_budget,
       spice_level, allergies, dislikes,
       food_preferences_large, food_preferences_middle,
       restaurant_ratings
FROM users WHERE firebase_uid = %s
"""

GET_USER_ID_BY_FIREBASE_UID = """
SELECT id FROM users WHERE firebase_uid = %s
"""

GET_ALL_USERS = """
SELECT id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
       created_at, updated_at,
       is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
       location, location_method, user_lat, user_lon,
       birth_year, gender, dining_companions,
       regular_budget, special_budget,
       spice_level, allergies, dislikes,
       food_preferences_large, food_preferences_middle,
       restaurant_ratings
FROM users ORDER BY created_at DESC LIMIT %s OFFSET %s
"""

UPDATE_USER_BY_ID = """
UPDATE users SET
    {fields}
    updated_at = CURRENT_TIMESTAMP
WHERE id = %s
RETURNING id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
          created_at, updated_at,
          is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
          location, location_method, user_lat, user_lon,
          birth_year, gender, dining_companions,
          regular_budget, special_budget,
          spice_level, allergies, dislikes,
          food_preferences_large, food_preferences_middle,
          restaurant_ratings
"""

UPDATE_USER_BY_FIREBASE_UID = """
UPDATE users SET
    {fields}
    updated_at = CURRENT_TIMESTAMP
WHERE firebase_uid = %s
RETURNING id, firebase_uid, name, email, display_name, photo_url, kakao_reviewer_id,
          created_at, updated_at
"""

DELETE_USER_BY_ID = """
DELETE FROM users WHERE id = %s RETURNING id
"""

COUNT_USERS = """
SELECT COUNT(*) FROM users
"""

# Firebase 동기화 관련 쿼리
INSERT_USER_FOR_SYNC = """
INSERT INTO users (id, firebase_uid, name, email, display_name, photo_url, kakao_reviewer_id)
VALUES (%s, %s, %s, %s, %s, %s, %s)
"""

INSERT_USER_FROM_FIREBASE = """
INSERT INTO users (id, firebase_uid, name, email, display_name, photo_url)
VALUES (%s, %s, %s, %s, %s, %s)
RETURNING id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
          created_at, updated_at,
          is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
          location, location_method, user_lat, user_lon,
          birth_year, gender, dining_companions,
          regular_budget, special_budget,
          spice_level, allergies, dislikes,
          food_preferences_large, food_preferences_middle,
          restaurant_ratings
"""

# 온보딩 데이터 업데이트 쿼리
UPDATE_USER_ONBOARDING = """
UPDATE users SET
    is_personalization_enabled = %s,
    has_completed_onboarding = %s,
    onboarding_completed_at = %s,
    location = %s,
    location_method = %s,
    user_lat = %s,
    user_lon = %s,
    birth_year = %s,
    gender = %s,
    dining_companions = %s,
    regular_budget = %s,
    special_budget = %s,
    spice_level = %s,
    allergies = %s,
    dislikes = %s,
    food_preferences_large = %s,
    food_preferences_middle = %s,
    restaurant_ratings = %s,
    updated_at = CURRENT_TIMESTAMP
WHERE firebase_uid = %s
RETURNING id, firebase_uid, kakao_reviewer_id, name, email, display_name, photo_url,
          created_at, updated_at,
          is_personalization_enabled, has_completed_onboarding, onboarding_completed_at,
          location, location_method, user_lat, user_lon,
          birth_year, gender, dining_companions,
          regular_budget, special_budget,
          spice_level, allergies, dislikes,
          food_preferences_large, food_preferences_middle,
          restaurant_ratings
"""

# 레거시 쿼리들 (필요시 제거 가능)
GET_USER_BY_ACCOUNT_ID = """
SELECT id, account_id, name, email, created_at, updated_at
FROM users WHERE account_id = %s
"""

UPDATE_USER_BY_ACCOUNT_ID = """
UPDATE users SET
    name = %s, email = %s, updated_at = CURRENT_TIMESTAMP
WHERE account_id = %s
RETURNING id, account_id, name, email, created_at, updated_at
"""

DELETE_USER_BY_ACCOUNT_ID = """
DELETE FROM users WHERE account_id = %s
"""
