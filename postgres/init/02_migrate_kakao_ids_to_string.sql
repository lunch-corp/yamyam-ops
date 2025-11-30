-- Kakao ID 타입 마이그레이션 스크립트
-- reviewer_id, review_id 컬럼을 integer에서 varchar로 변경
-- PostgreSQL 13+ 버전 필요
--
-- 실행 전 주의사항:
-- 1. 프로덕션 DB 백업 필수
-- 2. 트랜잭션으로 안전하게 실행
-- 3. 롤백 가능하도록 작성됨

BEGIN;

-- ============================================
-- 1. Foreign Key 제약조건 제거
-- ============================================
ALTER TABLE IF EXISTS kakao_review 
    DROP CONSTRAINT IF EXISTS kakao_review_reviewer_id_fkey;

-- ============================================
-- 2. 인덱스 제거 (타입 변경 전)
-- ============================================
-- kakao_review 테이블의 인덱스 제거
DROP INDEX IF EXISTS ix_kakao_review_reviewer_id;
DROP INDEX IF EXISTS ix_kakao_review_review_id;

-- kakao_reviewer 테이블의 인덱스 제거
DROP INDEX IF EXISTS ix_kakao_reviewer_reviewer_id;

-- ============================================
-- 3. 컬럼 타입 변경 (integer → varchar)
-- ============================================
-- kakao_reviewer.reviewer_id: integer → varchar
ALTER TABLE IF EXISTS kakao_reviewer 
    ALTER COLUMN reviewer_id TYPE VARCHAR USING reviewer_id::VARCHAR;

-- kakao_review.reviewer_id: integer → varchar
ALTER TABLE IF EXISTS kakao_review 
    ALTER COLUMN reviewer_id TYPE VARCHAR USING reviewer_id::VARCHAR;

-- kakao_review.review_id: integer → varchar
ALTER TABLE IF EXISTS kakao_review 
    ALTER COLUMN review_id TYPE VARCHAR USING review_id::VARCHAR;

-- ============================================
-- 4. Foreign Key 제약조건 재생성 (테이블이 존재할 때만)
-- ============================================
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'kakao_review')
       AND EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'kakao_reviewer')
       AND NOT EXISTS (
           SELECT FROM information_schema.table_constraints 
           WHERE constraint_name = 'kakao_review_reviewer_id_fkey'
           AND table_name = 'kakao_review'
       ) THEN
        ALTER TABLE kakao_review 
            ADD CONSTRAINT kakao_review_reviewer_id_fkey 
            FOREIGN KEY (reviewer_id) 
            REFERENCES kakao_reviewer(reviewer_id);
    END IF;
END $$;

-- ============================================
-- 5. 인덱스 재생성 (테이블이 존재할 때만)
-- ============================================
-- kakao_reviewer.reviewer_id UNIQUE 인덱스
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'kakao_reviewer') THEN
        CREATE UNIQUE INDEX IF NOT EXISTS ix_kakao_reviewer_reviewer_id 
            ON kakao_reviewer USING btree (reviewer_id);
    END IF;
END $$;

-- kakao_review.reviewer_id 인덱스
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'kakao_review') THEN
        CREATE INDEX IF NOT EXISTS ix_kakao_review_reviewer_id 
            ON kakao_review USING btree (reviewer_id);
    END IF;
END $$;

-- kakao_review.review_id UNIQUE 인덱스
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'kakao_review') THEN
        CREATE UNIQUE INDEX IF NOT EXISTS ix_kakao_review_review_id 
            ON kakao_review USING btree (review_id);
    END IF;
END $$;

COMMIT;

-- 마이그레이션 완료 메시지
DO $$
BEGIN
    RAISE NOTICE 'Kakao ID 타입 마이그레이션 완료: integer → varchar';
END $$;

