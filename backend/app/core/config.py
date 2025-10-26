from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 데이터베이스 설정
    database_url: str = "postgresql://yamyam:yamyam_pass@postgres:5432/yamyamdb"

    # Redis 설정
    redis_url: str = "redis://redis:6379"

    # FAISS 서버 설정
    faiss_server_url: str = "http://faiss:7000"

    # JWT 설정
    jwt_secret_key: str = "your-secret-key-here-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 15  # 15분
    refresh_token_expire_days: int = 7  # 7일

    # Firebase 설정
    firebase_project_id: Optional[str] = None
    firebase_private_key_id: Optional[str] = None
    firebase_private_key: Optional[str] = None
    firebase_client_email: Optional[str] = None
    firebase_client_id: Optional[str] = None
    firebase_auth_uri: Optional[str] = None
    firebase_token_uri: Optional[str] = None

    # 환경 설정
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


# 전역 설정 인스턴스
settings = Settings()
