-- Add onboarding columns to users table
-- Migration: 03_add_onboarding_columns.sql

-- users 테이블이 존재할 때만 실행
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        -- 기본 플래그
        ALTER TABLE users ADD COLUMN IF NOT EXISTS is_personalization_enabled BOOLEAN DEFAULT false;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS has_completed_onboarding BOOLEAN DEFAULT false;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS onboarding_completed_at TIMESTAMP WITH TIME ZONE;

        -- 위치 정보
        ALTER TABLE users ADD COLUMN IF NOT EXISTS location VARCHAR(255);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS location_method VARCHAR(50);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS user_lat FLOAT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS user_lon FLOAT;

        -- 기본 정보
        ALTER TABLE users ADD COLUMN IF NOT EXISTS birth_year INTEGER;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS gender VARCHAR(20);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS dining_companions TEXT[];

        -- 식사비 정보
        ALTER TABLE users ADD COLUMN IF NOT EXISTS regular_budget VARCHAR(50);
        ALTER TABLE users ADD COLUMN IF NOT EXISTS special_budget VARCHAR(50);

        -- 취향 정보
        ALTER TABLE users ADD COLUMN IF NOT EXISTS spice_level INTEGER;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS allergies TEXT;
        ALTER TABLE users ADD COLUMN IF NOT EXISTS dislikes TEXT;

        -- 음식 선호도
        ALTER TABLE users ADD COLUMN IF NOT EXISTS food_preferences_large TEXT[];
        ALTER TABLE users ADD COLUMN IF NOT EXISTS food_preferences_middle JSONB;

        -- 평가 데이터
        ALTER TABLE users ADD COLUMN IF NOT EXISTS restaurant_ratings JSONB;

        -- 인덱스 추가 (성능 최적화)
        CREATE INDEX IF NOT EXISTS idx_users_has_completed_onboarding ON users(has_completed_onboarding);
        CREATE INDEX IF NOT EXISTS idx_users_is_personalization_enabled ON users(is_personalization_enabled);

        -- 코멘트 추가
        COMMENT ON COLUMN users.is_personalization_enabled IS '개인화 추천 활성화 여부';
        COMMENT ON COLUMN users.has_completed_onboarding IS '온보딩 완료 여부';
        COMMENT ON COLUMN users.onboarding_completed_at IS '온보딩 완료 시각';
        COMMENT ON COLUMN users.location IS '주요 활동 지역';
        COMMENT ON COLUMN users.location_method IS '위치 설정 방법 (geolocation/search)';
        COMMENT ON COLUMN users.user_lat IS '위도';
        COMMENT ON COLUMN users.user_lon IS '경도';
        COMMENT ON COLUMN users.birth_year IS '출생연도';
        COMMENT ON COLUMN users.gender IS '성별';
        COMMENT ON COLUMN users.dining_companions IS '주요 동행 유형 배열';
        COMMENT ON COLUMN users.regular_budget IS '평소 식사비 범위';
        COMMENT ON COLUMN users.special_budget IS '특별한 날 식사비 범위';
        COMMENT ON COLUMN users.spice_level IS '매운맛 선호도 (0-5)';
        COMMENT ON COLUMN users.allergies IS '알러지 정보';
        COMMENT ON COLUMN users.dislikes IS '못 먹는 음식';
        COMMENT ON COLUMN users.food_preferences_large IS '선호 대분류 카테고리 배열';
        COMMENT ON COLUMN users.food_preferences_middle IS '선호 중분류 카테고리 (대분류별)';
        COMMENT ON COLUMN users.restaurant_ratings IS '음식점 평가 데이터 (rating_key: score)';
    END IF;
END $$;

