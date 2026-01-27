import json
import os
import re
import socket

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
        """데이터베이스 URL 검증 및 로컬 환경 대응"""

        if not v or v.strip() == "":
            # DATABASE_URL이 없으면 환경 변수로부터 구성 시도
            postgres_user = os.getenv("POSTGRES_USER", "yamyam")
            postgres_password = os.getenv("POSTGRES_PASSWORD", "yamyam_pass")
            postgres_db = os.getenv("POSTGRES_DB", "yamyamdb")
            postgres_port = os.getenv("POSTGRES_PORT", "5432")

            # 로컬 환경 감지: postgres 호스트명을 해석할 수 있는지 확인
            try:
                socket.gethostbyname("postgres")
                # Docker 환경: postgres 호스트명 사용
                host = "postgres"
            except socket.gaierror:
                # 로컬 환경: localhost 사용, 포트는 docker-compose.yml의 매핑된 포트 사용
                host = "localhost"
                # 로컬에서 실행 중인 경우 매핑된 포트 확인 (기본값 5477)
                postgres_port = os.getenv("POSTGRES_PORT", "5477")

            return f"postgresql://{postgres_user}:{postgres_password}@{host}:{postgres_port}/{postgres_db}"

        # DATABASE_URL이 있는 경우, postgres 호스트명을 로컬 환경에서 해석 가능한지 확인
        if isinstance(v, str) and "@postgres:" in v:
            try:
                socket.gethostbyname("postgres")
                # Docker 환경: 그대로 사용
                return v
            except socket.gaierror:
                # postgres:5432 또는 postgres:${POSTGRES_PORT}를 localhost:5477로 변경
                v = re.sub(r"@postgres:(\d+)", r"@localhost:5477", v)
                return v

        return v

    @field_validator("redis_url", mode="before")
    @classmethod
    def validate_redis_url(cls, v):
        """Redis URL 검증 및 로컬 환경 대응"""

        if not v or v.strip() == "":
            # 로컬 환경 감지: redis 호스트명을 해석할 수 있는지 확인
            try:
                socket.gethostbyname("redis")
                # Docker 환경: redis 호스트명 사용
                host = "redis"
                port = "6379"
            except socket.gaierror:
                # 로컬 환경: localhost 사용
                host = "localhost"
                # docker-compose.yml에서 매핑된 포트 확인 (기본값 6379)
                port = os.getenv("REDIS_PORT", "6379")

            return f"redis://{host}:{port}"

        # Redis URL이 있는 경우, redis 호스트명을 로컬 환경에서 해석 가능한지 확인
        if isinstance(v, str) and "redis://redis:" in v:
            try:
                socket.gethostbyname("redis")
                # Docker 환경: 그대로 사용
                return v
            except socket.gaierror:
                # 로컬 환경: redis를 localhost로 변경
                v = v.replace("redis://redis:", "redis://localhost:")
                return v

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

    # Gemini API 설정 (X 봇용, 선택)
    # Google AI Studio에서 발급: https://aistudio.google.com/app/apikey
    # API 키가 없으면 fallback 텍스트 생성 사용
    gemini_api_key: str | None = None

    # X API 인증 (X 봇용)
    # X Developer Portal에서 발급: https://developer.x.com/

    # OAuth 2.0 User Context (트윗 발행용, 권장)
    x_oauth2_access_token: str | None = None  # OAuth 2.0 Access Token
    x_oauth2_refresh_token: str | None = None  # OAuth 2.0 Refresh Token
    x_oauth2_token_expires_at: str | None = None  # 토큰 만료 시간 (ISO 8601 형식)

    # OAuth 2.0 Application-Only (읽기 전용)
    x_client_id: str | None = None  # X Client ID
    x_client_secret: str | None = None  # X Client Secret
    x_bearer_token: str | None = None  # X Bearer Token (직접 사용 시)

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
        extra="ignore",
    )


# 전역 설정 인스턴스
settings = Settings()
