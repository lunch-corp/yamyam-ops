import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.v1 import (  # item_kakao_mappings,; items,; kakao_diners,; kakao_reviewers,; kakao_reviews,; recommend,; reviews,
    upload,
    users,
)
from .core.config import settings
from .core.db import db

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리"""
    # 시작 시 실행
    logger.info("yamyam API 서버 시작")

    # 데이터베이스 테이블 생성
    try:
        db.create_tables()
        logger.info("데이터베이스 테이블 초기화 완료")
    except Exception as e:
        logger.error(f"데이터베이스 초기화 실패: {e}")
        raise

    yield
    # 종료 시 실행
    logger.info("yamyam API 서버 종료")


# FastAPI 앱 생성
app = FastAPI(
    title="yamyam API",
    description="음식 추천 시스템 API",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS 미들웨어 설정
allowed_origins = [
    "http://what2eat.streamlit.app",
    "https://what2eat.streamlit.app",
    "http://localhost:8501",
    "http://localhost:3000",
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 등록
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(upload.router, prefix="/upload")

# TODO: 부분적으로 완성된 API들 (임시 비활성화)
# app.include_router(items.router, prefix="/items", tags=["items"])
# app.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
# app.include_router(recommend.router, prefix="/recommend", tags=["recommendations"])

# TODO: 미완성된 API들 (임시 비활성화)
# app.include_router(kakao_diners.router, prefix="/kakao/diners", tags=["kakao-diners"])
# app.include_router(
#     kakao_reviewers.router, prefix="/kakao/reviewers", tags=["kakao-reviewers"]
# )
# app.include_router(
#     kakao_reviews.router, prefix="/kakao/reviews", tags=["kakao-reviews"]
# )
# app.include_router(
#     item_kakao_mappings.router, prefix="/mappings", tags=["item-kakao-mappings"]
# )


@app.get("/")
def root():
    """root endpoint"""
    return {
        "message": "🍜 yamyam API에 오신 것을 환영합니다!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    """health check endpoint"""
    return {"status": "healthy", "service": "yamyam-api", "version": "1.0.0"}


@app.get("/info")
def get_info():
    """service information"""
    return {
        "service": "yamyam API",
        "version": "1.0.0",
        "environment": settings.environment,
        "debug": settings.debug,
        "endpoints": {
            "users": "/users",
            "upload": "/upload",
            "docs": "/docs",
            "health": "/health",
            # "items": "/items",  # 임시 비활성화
            # "reviews": "/reviews",  # 임시 비활성화
            # "recommendations": "/recommend",  # 임시 비활성화
            # "kakao_diners": "/kakao/diners",  # 임시 비활성화
            # "kakao_reviewers": "/kakao/reviewers",  # 임시 비활성화
            # "kakao_reviews": "/kakao/reviews",  # 임시 비활성화
            # "mappings": "/mappings",  # 임시 비활성화
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
