-- Create user_activity_logs table for ML recommendation model
-- Migration: 04_create_activity_logs.sql

-- users 테이블이 존재할 때만 실행
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users') THEN
        CREATE TABLE IF NOT EXISTS user_activity_logs (
            -- Primary key
            id VARCHAR(26) PRIMARY KEY,
            
            -- User identification
            user_id VARCHAR(26) NOT NULL,
            firebase_uid VARCHAR(128) NOT NULL,
            
            -- Session tracking
            session_id VARCHAR(50) NOT NULL,
            
            -- Event information
            event_type VARCHAR(50) NOT NULL,
            event_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            page VARCHAR(50),
            
            -- Location related
            location_query VARCHAR(255),
            location_address VARCHAR(255),
            location_lat FLOAT,
            location_lon FLOAT,
            location_method VARCHAR(50),
            
            -- Search filter related
            search_radius_km FLOAT,
            selected_large_categories TEXT[],
            selected_middle_categories TEXT[],
            sort_by VARCHAR(50),
            period VARCHAR(20),
            
            -- Ranking page related
            selected_city VARCHAR(100),
            selected_region VARCHAR(100),
            selected_grades TEXT[],
            
            -- Click/Interaction related
            clicked_diner_idx VARCHAR(50),
            clicked_diner_name VARCHAR(255),
            display_position INTEGER,
            
            -- Additional metadata
            additional_data JSONB,
            user_agent TEXT,
            ip_address VARCHAR(45),
            
            -- Foreign key constraint
            CONSTRAINT fk_user_activity_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    END IF;
END $$;

-- Create indexes for performance (테이블이 존재할 때만)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_activity_logs') THEN
        CREATE INDEX IF NOT EXISTS idx_user_activity_user_id ON user_activity_logs(user_id);
        CREATE INDEX IF NOT EXISTS idx_user_activity_firebase_uid ON user_activity_logs(firebase_uid);
        CREATE INDEX IF NOT EXISTS idx_user_activity_session_id ON user_activity_logs(session_id);
        CREATE INDEX IF NOT EXISTS idx_user_activity_event_type ON user_activity_logs(event_type);
        CREATE INDEX IF NOT EXISTS idx_user_activity_timestamp ON user_activity_logs(event_timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_user_activity_clicked_diner ON user_activity_logs(clicked_diner_idx) 
            WHERE clicked_diner_idx IS NOT NULL;

        -- Composite indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_user_activity_user_event ON user_activity_logs(user_id, event_type, event_timestamp DESC);
        CREATE INDEX IF NOT EXISTS idx_user_activity_session_event ON user_activity_logs(session_id, event_timestamp);
    END IF;
END $$;

-- Comments for documentation (테이블이 존재할 때만)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_activity_logs') THEN
        COMMENT ON TABLE user_activity_logs IS '사용자 활동 로그 - ML 추천 모델 학습용';
        COMMENT ON COLUMN user_activity_logs.id IS 'ULID (Universally Lexicographically Sortable Identifier)';
        COMMENT ON COLUMN user_activity_logs.user_id IS '사용자 ID (users 테이블 FK)';
        COMMENT ON COLUMN user_activity_logs.firebase_uid IS 'Firebase UID';
        COMMENT ON COLUMN user_activity_logs.session_id IS '세션 ID (연속된 행동 그룹화)';
        COMMENT ON COLUMN user_activity_logs.event_type IS '이벤트 유형 (location_search, diner_click 등)';
        COMMENT ON COLUMN user_activity_logs.event_timestamp IS '이벤트 발생 시각';
        COMMENT ON COLUMN user_activity_logs.page IS '이벤트 발생 페이지';
        COMMENT ON COLUMN user_activity_logs.location_query IS '검색한 위치 키워드';
        COMMENT ON COLUMN user_activity_logs.location_address IS '주소';
        COMMENT ON COLUMN user_activity_logs.location_lat IS '위도';
        COMMENT ON COLUMN user_activity_logs.location_lon IS '경도';
        COMMENT ON COLUMN user_activity_logs.location_method IS '위치 설정 방법 (geolocation/search)';
        COMMENT ON COLUMN user_activity_logs.search_radius_km IS '검색 반경 (km)';
        COMMENT ON COLUMN user_activity_logs.selected_large_categories IS '선택한 대분류 카테고리 배열';
        COMMENT ON COLUMN user_activity_logs.selected_middle_categories IS '선택한 중분류 카테고리 배열';
        COMMENT ON COLUMN user_activity_logs.sort_by IS '정렬 방식';
        COMMENT ON COLUMN user_activity_logs.period IS '기간 필터';
        COMMENT ON COLUMN user_activity_logs.selected_city IS '선택한 도시';
        COMMENT ON COLUMN user_activity_logs.selected_region IS '선택한 상세 지역';
        COMMENT ON COLUMN user_activity_logs.selected_grades IS '선택한 쩝슐랭 등급 배열';
        COMMENT ON COLUMN user_activity_logs.clicked_diner_idx IS '클릭한 음식점 ID';
        COMMENT ON COLUMN user_activity_logs.clicked_diner_name IS '클릭한 음식점 이름';
        COMMENT ON COLUMN user_activity_logs.display_position IS '표시된 위치/순위';
        COMMENT ON COLUMN user_activity_logs.additional_data IS '기타 추가 정보 (JSONB)';
        COMMENT ON COLUMN user_activity_logs.user_agent IS '브라우저 정보';
        COMMENT ON COLUMN user_activity_logs.ip_address IS 'IP 주소 (선택적)';
    END IF;
END $$;

-- Event types reference (for documentation)
-- location_search: 위치 검색
-- location_set: 위치 설정 완료
-- filter_change: 검색 필터 변경
-- sort_change: 정렬 방식 변경
-- category_select: 카테고리 선택
-- diner_click: 음식점 클릭
-- ranking_view: 랭킹 페이지 조회
-- search_filter_view: 검색 필터 페이지 조회

