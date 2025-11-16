import logging

from fastapi import APIRouter

from app.core.db import db

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/",
    tags=["kakao-data"],
    summary="카카오 데이터 메모리 로드",
)
def preload_restaurants():
    """kakao_diner 테이블 데이터를 메모리에 미리 로드합니다"""
    try:
        db.preload_kakao_data()
        return {
            "success": True,
            "message": "Successfully preloaded 4 kakao data",
        }
    except Exception as e:
        logger.error(f"Failed to preload kakao data: {e}")
        raise e
