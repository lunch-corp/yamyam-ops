-- yamyam 데이터베이스 초기화 스크립트
-- PostgreSQL 13+ 버전 필요
-- 
-- 주의: 테이블 스키마는 SQLAlchemy 모델(app/models/)에서 자동 생성됩니다.
-- 이 파일은 데이터베이스 함수와 트리거만 정의합니다.

-- PostGIS 확장 활성화 (지리 공간 데이터 처리)
CREATE EXTENSION IF NOT EXISTS postgis;

-- ULID 생성 함수 (PostgreSQL용)
CREATE OR REPLACE FUNCTION generate_ulid() RETURNS VARCHAR(26) AS $$
DECLARE
    timestamp_part VARCHAR(10);
    random_part VARCHAR(16);
    ulid VARCHAR(26);
BEGIN
    -- 타임스탬프 부분 (48비트, 밀리초 단위)
    timestamp_part := LPAD(TO_CHAR(EXTRACT(EPOCH FROM NOW()) * 1000, 'FM999999999999'), 10, '0');
    
    -- 랜덤 부분 (80비트)
    random_part := LPAD(TO_CHAR(FLOOR(RANDOM() * 281474976710655), 'FM999999999999999999'), 16, '0');
    
    -- ULID 조합
    ulid := timestamp_part || random_part;
    
    RETURN ulid;
END;
$$ LANGUAGE plpgsql;

-- 트리거 함수 생성 (updated_at 자동 업데이트)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- 모든 테이블의 id 컬럼에 ULID 기본값 설정
-- SQLAlchemy가 테이블을 생성한 후에 실행됩니다.
CREATE OR REPLACE FUNCTION set_ulid_defaults()
RETURNS VOID AS $$
BEGIN
    -- 모든 테이블의 id 컬럼에 ULID 기본값 설정
    ALTER TABLE IF EXISTS users ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS items ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS reviews ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS user_preferences ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS embeddings_metadata ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS kakao_diner ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS kakao_reviewer ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS kakao_review ALTER COLUMN id SET DEFAULT generate_ulid();
    ALTER TABLE IF EXISTS item_kakao_mapping ALTER COLUMN id SET DEFAULT generate_ulid();
END;
$$ LANGUAGE plpgsql;