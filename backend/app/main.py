import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import (
    activity_logs,
    auth,
    items,
    kakao_diners,
    kakao_reviewers,
    kakao_reviews,
    recommendation,
    redis,
    reviews,
    upload,
    users,
    vector_db,
    x_bot,
)
from app.core.config import settings
from app.core.db import db
from app.core.redis_db import redis_db

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("yamyam API 서버 시작")

    # 데이터베이스 마이그레이션 실행 (옵션)
    if settings.run_migrations:
        try:
            from app.core.migrations import run_migrations

            logger.info("데이터베이스 마이그레이션 실행 중...")
            run_migrations()
            logger.info("데이터베이스 마이그레이션 완료")
        except Exception as e:
            logger.error(f"마이그레이션 실행 중 오류 발생: {e}")
            import traceback

            logger.error(f"마이그레이션 오류 상세: {traceback.format_exc()}")
            logger.warning("마이그레이션 실패했지만 서버는 계속 실행합니다.")
    else:
        logger.info(
            "데이터베이스 마이그레이션이 비활성화되어 있습니다. (RUN_MIGRATIONS=false)"
        )

    # 데이터베이스 테이블 생성
    try:
        db.create_tables()
        logger.info("데이터베이스 테이블 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise

    # Redis 연결 확인
    try:
        client = await redis_db.get_client()
        redis.redis_service.redis_client = client  # RedisService에 client 할당
        await redis.redis_service.initialize_data()
        logger.info("Redis 연결 및 초기화 완료")
    except Exception as e:
        logger.error(f"Redis 초기화 실패: {e}")

    yield

    # 종료 시 실행
    logger.info("yamyam API 서버 종료 중...")

    # Redis 연결 종료
    try:
        await redis_db.close()
        logger.info("Redis 연결 종료 완료")
    except Exception as e:
        logger.error(f"Redis 종료 실패: {e}")

    logger.info("yamyam API 서버 종료 완료")


# FastAPI 앱 생성
app = FastAPI(
    title="yamyam API",
    description="음식 추천 시스템 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(
    activity_logs.router, prefix="/activity-logs", tags=["activity-logs"]
)
app.include_router(items.router, prefix="/items", tags=["items"])
app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
app.include_router(upload.router, prefix="/upload")
app.include_router(kakao_diners.router, prefix="/kakao/diners", tags=["kakao-diners"])
app.include_router(
    kakao_reviews.router, prefix="/kakao/reviews", tags=["kakao-reviews"]
)
app.include_router(
    kakao_reviewers.router, prefix="/kakao/reviewers", tags=["kakao-reviewers"]
)
app.include_router(vector_db.router, prefix="/vector_db", tags=["vector-db"])
app.include_router(redis.router, prefix="/redis", tags=["redis"])
app.include_router(recommendation.router, prefix="/rec", tags=["recommendation"])
app.include_router(x_bot.router, prefix="/api/v1/x-bot", tags=["x-bot"])


@app.get("/")
def root():
    """root endpoint"""
    return {
        "message": "🍜 yamyam API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """health check endpoint"""
    # Redis 상태 확인
    redis_status = "healthy"
    try:
        is_connected = await redis_db.ping()
        if not is_connected:
            redis_status = "unhealthy"
    except Exception:
        redis_status = "unavailable"

    return {
        "status": "healthy",
        "service": "yamyam-api",
        "version": "1.0.0",
        "redis": redis_status,
    }


@app.get("/info")
def get_info():
    """service information"""
    return {
        "service": "yamyam API",
        "version": "1.0.0",
        "environment": settings.environment,
        "debug": settings.debug,
        "endpoints": {
            "auth": "/auth",
            "users": "/users",
            "activity_logs": "/activity-logs",
            "items": "/items",
            "reviews": "/reviews",
            "upload": "/upload",
            "kakao_diners": "/kakao/diners",
            "kakao_reviews": "/kakao/reviews",
            "kakao_reviewers": "/kakao/reviewers",
            "vector_db": "/vector_db",
            "redis": "/redis",
            "x_bot": "/api/v1/x-bot",
            "docs": "/docs",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
