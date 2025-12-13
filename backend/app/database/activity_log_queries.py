"""
Activity Log 관련 SQL 쿼리
"""

# Activity Log CRUD 쿼리
INSERT_ACTIVITY_LOG = """
INSERT INTO user_activity_logs (
    id, user_id, firebase_uid, session_id, event_type, page,
    location_query, location_address, location_lat, location_lon, location_method,
    search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
    selected_city, selected_region, selected_grades,
    clicked_diner_idx, clicked_diner_name, display_position,
    additional_data, user_agent, ip_address
)
VALUES (
    %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s,
    %s, %s, %s
)
RETURNING id, user_id, firebase_uid, session_id, event_type, event_timestamp, page,
          location_query, location_address, location_lat, location_lon, location_method,
          search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
          selected_city, selected_region, selected_grades,
          clicked_diner_idx, clicked_diner_name, display_position,
          additional_data, user_agent, ip_address
"""

GET_ACTIVITY_LOGS_BY_USER = """
SELECT id, user_id, firebase_uid, session_id, event_type, event_timestamp, page,
       location_query, location_address, location_lat, location_lon, location_method,
       search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
       selected_city, selected_region, selected_grades,
       clicked_diner_idx, clicked_diner_name, display_position,
       additional_data, user_agent, ip_address
FROM user_activity_logs
WHERE user_id = %s
ORDER BY event_timestamp DESC
LIMIT %s OFFSET %s
"""

GET_ACTIVITY_LOGS_BY_FIREBASE_UID = """
SELECT id, user_id, firebase_uid, session_id, event_type, event_timestamp, page,
       location_query, location_address, location_lat, location_lon, location_method,
       search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
       selected_city, selected_region, selected_grades,
       clicked_diner_idx, clicked_diner_name, display_position,
       additional_data, user_agent, ip_address
FROM user_activity_logs
WHERE firebase_uid = %s
ORDER BY event_timestamp DESC
LIMIT %s OFFSET %s
"""

GET_ACTIVITY_LOGS_BY_SESSION = """
SELECT id, user_id, firebase_uid, session_id, event_type, event_timestamp, page,
       location_query, location_address, location_lat, location_lon, location_method,
       search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
       selected_city, selected_region, selected_grades,
       clicked_diner_idx, clicked_diner_name, display_position,
       additional_data, user_agent, ip_address
FROM user_activity_logs
WHERE session_id = %s
ORDER BY event_timestamp
"""

GET_ACTIVITY_LOGS_BY_TYPE = """
SELECT id, user_id, firebase_uid, session_id, event_type, event_timestamp, page,
       location_query, location_address, location_lat, location_lon, location_method,
       search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
       selected_city, selected_region, selected_grades,
       clicked_diner_idx, clicked_diner_name, display_position,
       additional_data, user_agent, ip_address
FROM user_activity_logs
WHERE event_type = %s
ORDER BY event_timestamp DESC
LIMIT %s OFFSET %s
"""

GET_ACTIVITY_LOGS_WITH_FILTER = """
SELECT id, user_id, firebase_uid, session_id, event_type, event_timestamp, page,
       location_query, location_address, location_lat, location_lon, location_method,
       search_radius_km, selected_large_categories, selected_middle_categories, sort_by, period,
       selected_city, selected_region, selected_grades,
       clicked_diner_idx, clicked_diner_name, display_position,
       additional_data, user_agent, ip_address
FROM user_activity_logs
WHERE firebase_uid = %s
  AND (%s IS NULL OR event_type = %s)
  AND (%s IS NULL OR page = %s)
  AND (%s IS NULL OR event_timestamp >= %s)
  AND (%s IS NULL OR event_timestamp <= %s)
ORDER BY event_timestamp DESC
LIMIT %s OFFSET %s
"""

# ML 학습용 데이터 추출 쿼리
GET_LOGS_FOR_ML = """
SELECT
    user_id,
    firebase_uid,
    session_id,
    event_type,
    event_timestamp,
    page,
    location_lat,
    location_lon,
    search_radius_km,
    selected_large_categories,
    selected_middle_categories,
    sort_by,
    clicked_diner_idx,
    display_position
FROM user_activity_logs
WHERE (%s IS NULL OR event_timestamp >= %s)
  AND (%s IS NULL OR event_timestamp <= %s)
  AND (%s IS NULL OR event_type = ANY(%s))
ORDER BY user_id, session_id, event_timestamp
"""

# 통계 쿼리
COUNT_LOGS_BY_EVENT_TYPE = """
SELECT event_type, COUNT(*) as count
FROM user_activity_logs
WHERE event_timestamp >= %s
  AND event_timestamp <= %s
GROUP BY event_type
ORDER BY count DESC
"""

GET_TOP_CLICKED_DINERS = """
SELECT
    clicked_diner_idx,
    clicked_diner_name,
    COUNT(*) as click_count
FROM user_activity_logs
WHERE event_type = 'diner_click'
  AND clicked_diner_idx IS NOT NULL
  AND event_timestamp >= %s
  AND event_timestamp <= %s
GROUP BY clicked_diner_idx, clicked_diner_name
ORDER BY click_count DESC
LIMIT %s
"""

GET_USER_PREFERRED_CATEGORIES = """
SELECT
    firebase_uid,
    UNNEST(selected_large_categories) as category,
    COUNT(*) as selection_count
FROM user_activity_logs
WHERE firebase_uid = %s
  AND selected_large_categories IS NOT NULL
GROUP BY firebase_uid, category
ORDER BY selection_count DESC
"""
