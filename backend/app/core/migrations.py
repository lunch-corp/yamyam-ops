"""
데이터베이스 마이그레이션 모듈
Alembic 대신 직접 SQL을 실행하는 방식으로 마이그레이션을 관리합니다.
"""

import logging

from app.core.db import db

logger = logging.getLogger(__name__)


def check_column_exists(table_name: str, column_name: str) -> bool:
    """컬럼이 존재하는지 확인"""
    try:
        with db.get_cursor() as (cursor, conn):
            query = """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = %s AND column_name = %s
            """
            cursor.execute(query, (table_name, column_name))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"컬럼 존재 확인 중 오류 발생: {e}")
        return False


def add_column_if_not_exists(
    table_name: str,
    column_name: str,
    column_type: str,
    nullable: bool = True,
    default_value: str = None,
) -> bool:
    """컬럼이 없으면 추가"""
    try:
        # 컬럼이 이미 존재하는지 확인
        if check_column_exists(table_name, column_name):
            logger.info(f"컬럼 {table_name}.{column_name}은(는) 이미 존재합니다.")
            return False

        # 컬럼 추가 SQL 생성
        parts = [column_name, column_type]

        if default_value:
            parts.append(f"DEFAULT {default_value}")

        if not nullable:
            parts.append("NOT NULL")

        alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {' '.join(parts)}"

        with db.get_cursor() as (cursor, conn):
            cursor.execute(alter_sql)
            conn.commit()
            logger.info(f"컬럼 {table_name}.{column_name} 추가 완료")
            return True
    except Exception as e:
        logger.error(f"컬럼 추가 중 오류 발생: {e}")
        raise


def check_index_exists(table_name: str, index_name: str) -> bool:
    """인덱스가 존재하는지 확인"""
    try:
        with db.get_cursor() as (cursor, conn):
            query = """
                SELECT indexname
                FROM pg_indexes
                WHERE tablename = %s AND indexname = %s
            """
            cursor.execute(query, (table_name, index_name))
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"인덱스 존재 확인 중 오류 발생: {e}")
        return False


def create_performance_indexes():
    """성능 최적화를 위한 인덱스 생성"""
    logger.info("성능 최적화 인덱스 생성 시작...")

    # 기본 정렬 인덱스 (High Priority)
    basic_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_bayesian_score ON kakao_diner(bayesian_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_hidden_score ON kakao_diner(hidden_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_review_avg ON kakao_diner(diner_review_avg DESC)",
    ]

    # PostGIS 확장 설치
    postgis_setup = [
        "CREATE EXTENSION IF NOT EXISTS postgis",
    ]

    # 공간 인덱스 (High Priority) - PostGIS GIST 인덱스
    spatial_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_location ON kakao_diner USING GIST (ST_MakePoint(diner_lon, diner_lat))",
    ]

    # PostGIS가 없을 경우 대체 인덱스
    fallback_spatial_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_lat_lon ON kakao_diner(diner_lat, diner_lon)",
    ]

    # 복합 인덱스 (Medium Priority)
    composite_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_cat_large_bayesian ON kakao_diner(diner_category_large, bayesian_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_cat_middle_bayesian ON kakao_diner(diner_category_middle, bayesian_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_cat_large_hidden ON kakao_diner(diner_category_large, hidden_score DESC)",
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_cat_large_rating ON kakao_diner(diner_category_large, diner_review_avg DESC)",
    ]

    # pg_trgm 확장 및 GIN 인덱스 (LIKE 검색 최적화)
    trgm_setup = [
        "CREATE EXTENSION IF NOT EXISTS pg_trgm",
    ]

    trgm_indexes = [
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_cat_large_trgm ON kakao_diner USING GIN (diner_category_large gin_trgm_ops)",
        "CREATE INDEX IF NOT EXISTS idx_kakao_diner_cat_middle_trgm ON kakao_diner USING GIN (diner_category_middle gin_trgm_ops)",
    ]

    # 각 인덱스를 독립적인 트랜잭션으로 생성
    def create_index_safe(index_sql: str, description: str):
        """안전하게 인덱스 생성 (독립 트랜잭션)"""
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(index_sql)
                conn.commit()
                logger.info(f"{description} 생성 완료: {index_sql[:80]}...")
                return True
        except Exception as e:
            logger.warning(f"{description} 생성 실패 (무시): {str(e)[:100]}")
            return False

    # 기본 인덱스 생성
    logger.info("기본 정렬 인덱스 생성 중...")
    for index_sql in basic_indexes:
        create_index_safe(index_sql, "기본 인덱스")

    # PostGIS 확장 설치
    logger.info("PostGIS 확장 설치 중...")
    postgis_available = False
    for setup_sql in postgis_setup:
        if create_index_safe(setup_sql, "PostGIS 확장"):
            postgis_available = True

    # 공간 인덱스 생성
    logger.info("공간 인덱스 생성 중...")
    if postgis_available:
        # PostGIS GIST 인덱스 사용
        for index_sql in spatial_indexes:
            if not create_index_safe(index_sql, "PostGIS GIST 인덱스"):
                # GIST 인덱스 실패 시 일반 인덱스로 대체
                logger.warning(
                    "PostGIS GIST 인덱스 생성 실패, 일반 인덱스로 대체합니다."
                )
                for fallback_sql in fallback_spatial_indexes:
                    create_index_safe(fallback_sql, "공간 인덱스 (대체)")
    else:
        # PostGIS 없으면 일반 인덱스 사용
        logger.warning("PostGIS를 사용할 수 없어 일반 B-tree 인덱스를 사용합니다.")
        for fallback_sql in fallback_spatial_indexes:
            create_index_safe(fallback_sql, "공간 인덱스 (대체)")

    # 복합 인덱스 생성
    logger.info("복합 인덱스 생성 중...")
    for index_sql in composite_indexes:
        create_index_safe(index_sql, "복합 인덱스")

    # pg_trgm 확장 설치
    logger.info("pg_trgm 확장 설치 중...")
    trgm_available = False
    for setup_sql in trgm_setup:
        if create_index_safe(setup_sql, "pg_trgm 확장"):
            trgm_available = True

    # pg_trgm 인덱스 생성 (확장이 설치된 경우만)
    if trgm_available:
        logger.info("LIKE 검색 최적화 인덱스 생성 중...")
        for index_sql in trgm_indexes:
            create_index_safe(index_sql, "pg_trgm 인덱스")
    else:
        logger.warning("pg_trgm 확장을 사용할 수 없어 GIN 인덱스를 건너뜁니다.")

    # 통계 업데이트
    logger.info("테이블 통계 업데이트 중...")
    try:
        with db.get_cursor() as (cursor, conn):
            cursor.execute("ANALYZE kakao_diner")
            conn.commit()
            logger.info("테이블 통계 업데이트 완료")
    except Exception as e:
        logger.warning(f"통계 업데이트 실패 (무시): {e}")

    logger.info("성능 최적화 인덱스 생성 완료")


def run_migrations():
    """모든 마이그레이션 실행"""
    logger.info("데이터베이스 마이그레이션 시작...")

    try:
        # kakao_diner 테이블에 컬럼 추가
        migrations = [
            {
                "table": "kakao_diner",
                "column": "diner_grade",
                "type": "INTEGER",
                "nullable": False,
                "default": "0",
            },
            {
                "table": "kakao_diner",
                "column": "hidden_score",
                "type": "DOUBLE PRECISION",
                "nullable": False,
                "default": "0.0",
            },
            {
                "table": "kakao_diner",
                "column": "bayesian_score",
                "type": "DOUBLE PRECISION",
                "nullable": False,
                "default": "0.0",
            },
        ]

        for migration in migrations:
            add_column_if_not_exists(
                table_name=migration["table"],
                column_name=migration["column"],
                column_type=migration["type"],
                nullable=migration["nullable"],
                default_value=migration["default"],
            )

        # 성능 최적화 인덱스 생성
        create_performance_indexes()

        logger.info("데이터베이스 마이그레이션 완료")
    except Exception as e:
        logger.error(f"마이그레이션 실행 중 오류 발생: {e}")
        raise
