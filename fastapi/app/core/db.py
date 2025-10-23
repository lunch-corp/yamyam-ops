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

    def create_tables(self):
        """모든 테이블을 생성합니다 (모델 기반)"""
        try:
            from app.models.base import Base

            Base.metadata.create_all(bind=self.engine)

            # ULID 기본값 설정 함수 실행
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT set_ulid_defaults();")
                conn.commit()
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
