import logging
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

from app.core.config import settings


class Database:
    TABLE_NAMES = [
        "kakao_diner",
        "kakao_diner_category",
        "kakao_review",
        "kakao_reviewer",
    ]

    def __init__(self):
        self.connection_string = settings.database_url
        # SQLAlchemy 엔진 생성
        self.engine = create_engine(self.connection_string)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        self._dataset: dict[str, pd.DataFrame] = {}

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

    def list_tables(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Query to get all tables in the public schema
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_type = 'BASE TABLE'
                ORDER BY table_name;
            """)

            # Fetch all results
            tables = cursor.fetchall()

            logging.info(
                f"Table name: {','.join([table['table_name'] for table in tables])}"
            )

    def preload_kakao_data(self):
        """kakao 데이터를 미리 로드합니다"""
        for table_name in self.TABLE_NAMES:
            self._preload_data(table_name)

    def get_dataset(self, dataset_name: str):
        """pre-loaded dataset을 반환합니다

        Args:
            dataset_name: dataset 이름.

        Returns:
            key가 지정된 경우 해당 데이터, 없으면 전체 dataset dict
        """
        try:
            return self._dataset[dataset_name]
        except KeyError as e:
            logging.error(f"존재하지 않은 데이터셋 이름: {e}")
            raise
        except Exception as e:
            logging.error(e)
            raise

    def _preload_data(self, table_name: str):
        """kakao_diner 테이블 데이터를 미리 로드합니다"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(f"SELECT * FROM {table_name};")
                data = pd.DataFrame([dict(row) for row in cursor.fetchall()])
                cursor.close()

                # _dataset에 저장
                self._dataset[table_name] = data
                logging.info(f"{table_name} 테이블 pre-load 완료: {len(data)}개 레코드")
                return len(data)
        except Exception as e:
            logging.error(f"{table_name} 테이블 pre-load 중 오류: {e}")
            raise


# 전역 데이터베이스 인스턴스
db = Database()
