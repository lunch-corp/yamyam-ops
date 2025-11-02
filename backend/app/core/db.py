import logging
from contextlib import contextmanager

import psycopg2
from app.core.config import settings
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self):
        self.connection_string = settings.database_url
        # SQLAlchemy 엔진 생성
        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    @contextmanager
    def get_connection(self):
        """데이터베이스 연결 컨텍스트 매니저"""
        conn = None
        try:
            conn = psycopg2.connect(
                self.connection_string, cursor_factory=RealDictCursor
            )
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logging.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    @contextmanager
    def get_cursor(self):
        """커서 컨텍스트 매니저"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                yield cursor, conn
            except Exception as e:
                conn.rollback()
                logging.error(f"Database cursor error: {e}")
                raise
            finally:
                cursor.close()

    def _ensure_ulid_functions(self, cursor):
        """ULID 관련 함수가 없으면 생성합니다"""
        # generate_ulid 함수 생성
        cursor.execute("""
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
        """)
        
        # update_updated_at_column 함수 생성
        cursor.execute("""
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = CURRENT_TIMESTAMP;
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)
        
        # set_ulid_defaults 함수 생성
        cursor.execute("""
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
        """)
        
        logging.info("ULID 관련 함수 생성 완료")

    def _function_exists(self, cursor, function_name):
        """함수가 존재하는지 확인합니다"""
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1 
                FROM pg_proc p
                JOIN pg_namespace n ON p.pronamespace = n.oid
                WHERE n.nspname = 'public' 
                AND p.proname = %s
            ) AS exists;
        """, (function_name,))
        result = cursor.fetchone()
        return result['exists']

    def create_tables(self):
        """모든 테이블을 생성합니다 (모델 기반)"""
        try:
            from app.models.base import Base

            # 테이블 생성
            Base.metadata.create_all(bind=self.engine)

            # ULID 함수가 없으면 생성하고, ULID 기본값 설정 함수 실행
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # 함수가 존재하는지 확인
                if not self._function_exists(cursor, 'set_ulid_defaults'):
                    logging.info("ULID 함수가 없습니다. 함수를 생성합니다...")
                    self._ensure_ulid_functions(cursor)
                    conn.commit()
                
                # ULID 기본값 설정 함수 실행
                try:
                    cursor.execute("SELECT set_ulid_defaults();")
                    conn.commit()
                    logging.info("ULID 기본값 설정 완료")
                except Exception as e:
                    # 함수가 없거나 실행 실패 시 다시 생성 시도
                    logging.warning(f"set_ulid_defaults 실행 실패, 함수를 재생성합니다: {e}")
                    self._ensure_ulid_functions(cursor)
                    conn.commit()
                    cursor.execute("SELECT set_ulid_defaults();")
                    conn.commit()
                    logging.info("ULID 기본값 설정 완료")
                
                cursor.close()

            logging.info("데이터베이스 테이블 생성 및 ULID 기본값 설정 완료")
        except Exception as e:
            logging.error(f"테이블 생성 중 오류: {e}")
            raise

    def get_session(self):
        """SQLAlchemy 세션을 반환합니다"""
        return self.SessionLocal()


# 전역 데이터베이스 인스턴스
db = Database()
