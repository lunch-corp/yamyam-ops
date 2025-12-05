import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings


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

    def create_tables(self):
        """모든 테이블을 생성합니다 (모델 기반)"""
        try:
            from app.models.base import Base

            Base.metadata.create_all(bind=self.engine)

            # ULID 기본값 설정 함수 실행 (함수가 존재하는 경우에만)
            # ULID는 Python 레벨에서 생성되므로 이 함수는 선택적입니다
            try:
                with self.get_connection() as conn:
                    cursor = conn.cursor()
                    # 함수 존재 여부 확인
                    cursor.execute("""
                        SELECT EXISTS (
                            SELECT 1 FROM pg_proc 
                            WHERE proname = 'set_ulid_defaults'
                        );
                    """)
                    function_exists = cursor.fetchone()[0]

                    if function_exists:
                        cursor.execute("SELECT set_ulid_defaults();")
                        conn.commit()
                        logging.info("ULID 기본값 설정 함수 실행 완료")
                    else:
                        logging.debug(
                            "set_ulid_defaults() 함수가 없습니다. ULID는 Python 레벨에서 생성됩니다."
                        )
                    cursor.close()
            except Exception as e:
                # 함수 실행 실패는 치명적이지 않음 (ULID는 Python에서 생성됨)
                logging.warning(f"ULID 기본값 설정 함수 실행 중 오류 (무시됨): {e}")

            logging.info("데이터베이스 테이블 생성 완료")
        except Exception as e:
            logging.error(f"테이블 생성 중 오류: {e}")
            raise

    def get_session(self):
        """SQLAlchemy 세션을 반환합니다"""
        return self.SessionLocal()


# 전역 데이터베이스 인스턴스
db = Database()
