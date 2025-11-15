"""
Most Popular Rank API
음식점 인기도 순위 기반 추천 API
"""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.mp_rank import MostPopularRankRequest, MostPopularRankResponse
from app.services.mp_rank_service import MostPopularRankService

router = APIRouter(tags=["mp-rank"])
logger = logging.getLogger(__name__)


@router.post(
    "/rank",
    response_model=MostPopularRankResponse,
    summary="인기 음식점 필터링 조회",
    description="""
    음식점 인기도 순위를 필터링 조회
    rank_method: rating(평점), review_count(리뷰수), distance(거리), yamyam_popularity(얌얌지표)
    period: 1M, 3M, 6M, all
    카테고리 필터: diner_category_large, diner_category_middle
    """,
)
def get_most_popular_rank(request: MostPopularRankRequest) -> MostPopularRankResponse:
    """인기 음식점 순위 조회"""
    try:
        logger.info(f"MP Rank 요청: {request.model_dump()}")
        service = MostPopularRankService()
        result = service.get_top_diners(request)
        logger.info(f"MP Rank 응답: {result.count}개 음식점")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"MP Rank 오류: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류: {str(e)}",
        )


@router.get("/health", summary="MP Rank API 상태 확인")
def health_check():
    """API 상태 확인"""
    return {
        "status": "healthy",
        "service": "mp-rank",
        "description": "음식점 인기도 순위 API",
    }