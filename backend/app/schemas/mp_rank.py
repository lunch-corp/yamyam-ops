from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class MostPopularRankRequest(BaseModel):
    """MP Rank 요청 스키마"""

    diner_category_large: Optional[str] = Field(None, description="대분류 카테고리")
    diner_category_middle: Optional[str] = Field(None, description="중분류 카테고리")
    rank_method: str = Field(
        default="rating",
        description="순위 방식: rating, review_count, distance, yamyam_popularity",
    )
    lat: Optional[float] = Field(None, ge=-90, le=90, description="위도")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="경도")
    period: str = Field(default="all", description="기간: 1M, 3M, 6M, all")
    reference_date: Optional[Union[str, datetime]] = Field(
        None, description="기준 날짜 (YYYY-MM-DD)"
    )
    topk: int = Field(default=10, ge=1, le=100, description="반환 개수")
    min_review_count: int = Field(default=5, ge=0, description="최소 리뷰 수")


class MostPopularRankResponse(BaseModel):
    """MP Rank 응답 스키마"""

    diner_ids: List[int] = Field(..., description="음식점 ID 목록")
    count: int = Field(..., description="음식점 수")
    rank_method: str = Field(..., description="순위 방식")
    period: str = Field(..., description="적용 기간")
    filters: dict = Field(..., description="적용 필터")


class MostPopularRankError(BaseModel):
    """에러 응답 스키마"""

    detail: Union[str, List[str]] = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
