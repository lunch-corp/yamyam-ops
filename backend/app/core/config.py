import json

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # 데이터베이스 설정
    database_url: str = "postgresql://yamyam:yamyam_pass@postgres:5432/yamyamdb"

    # Redis 설정
    redis_url: str = "redis://redis:6379"
    redis_max_batch_size: int = 1000  # 기본 배치 크기

    # FAISS 서버 설정
    faiss_server_url: str | None = "http://faiss:7000"

    # JWT 설정
    jwt_secret_key: str = "your-secret-key-here-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # 15분
    refresh_token_expire_days: int = 7  # 7일

    # Firebase 설정 (파일 경로 또는 JSON 문자열)
    # GOOGLE_APPLICATION_CREDENTIALS 환경 변수로 파일 경로 지정 (권장)
    # 또는 FIREBASE_KEY 환경 변수로 JSON 문자열 전달
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

    # config path
    config_root_path: str = "/app/config/beta"
    node2vec_config_path: str = "/app/config/beta/models/graph/node2vec.yaml"

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
