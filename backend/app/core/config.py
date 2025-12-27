import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 데이터베이스 설정
    database_url: str = "postgresql://yamyam:yamyam_pass@postgres:5432/yamyamdb"

    # Redis 설정
    redis_url: str = "redis://redis:6379"

    @field_validator("database_url", mode="before")
    @classmethod
    def validate_database_url(cls, v):
        """빈 문자열이거나 localhost인 경우 Docker 환경에 맞게 수정"""
        if not v or v.strip() == "":
            return "postgresql://yamyam:yamyam_pass@postgres:5432/yamyamdb"
        # localhost를 postgres로 변경 (Docker Compose 환경)
        if isinstance(v, str) and "localhost" in v and "postgres" not in v:
            return v.replace("localhost", "postgres")
        return v

    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, v):
        """빈 문자열이거나 localhost인 경우 Docker 환경에 맞게 수정"""
        if not v or v.strip() == "":
            return "redis://redis:6379"
        # localhost를 redis로 변경 (Docker Compose 환경)
        if isinstance(v, str) and "localhost" in v and "redis" not in v:
            return v.replace("localhost", "redis")
        return v

    redis_max_batch_size: int = 1000  # 기본 배치 크기

    # FAISS 서버 설정
    faiss_server_url: str | None = "http://faiss:7000"

    # JWT 설정
    jwt_secret_key: str = "your-secret-key-here-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # 15분
    refresh_token_expire_days: int = 7  # 7일

    # Firebase 설정
    # FIREBASE_KEY 환경 변수로 Firebase 서비스 계정 JSON 문자열 전달
    firebase_key: str | None = None

    # CORS 설정
    allowed_origins: list[str] | str = [
        "http://localhost:8501",
        "http://localhost:3000",
        "http://localhost",
    ]

    # 환경 설정
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    # 데이터베이스 마이그레이션 설정
    run_migrations: bool = True  # 기본값: True (마이그레이션 실행)

    # config path
    config_root_path: str = "/app/config/beta"
    node2vec_config_path: str = "/app/config/beta/models/graph/node2vec.yaml"

    @field_validator("run_migrations", mode="before")
    @classmethod
    def parse_run_migrations(cls, v):
        """RUN_MIGRATIONS 환경 변수를 bool로 변환"""
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            # 문자열을 소문자로 변환하여 비교
            return v.lower() in ("true", "1", "yes", "on")
        # 기본값은 True
        return True

    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_allowed_origins(cls, v):
        """ALLOWED_ORIGINS를 JSON 문자열 또는 리스트로 파싱"""
        if isinstance(v, str):
            try:
                # JSON 문자열을 리스트로 파싱
                return json.loads(v)
            except json.JSONDecodeError:
                # 쉼표로 구분된 문자열을 리스트로 변환
                return [origin.strip() for origin in v.split(",")]
        return v

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        # 명시적 환경 변수 매핑
        env_prefix="",
    )


# 전역 설정 인스턴스
settings = Settings()
