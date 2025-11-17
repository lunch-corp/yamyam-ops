from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class RankMethod(str, Enum):
    rating = "rating"
    review_count = "review_count"
    distance = "distance"
    yamyam_popularity = "yamyam_popularity"


class MostPopularRankRequest(BaseModel):
    """MP Rank 요청 스키마"""

    diner_category_large: Optional[str] = Field(None, description="대분류 카테고리")
    diner_category_middle: Optional[str] = Field(None, description="중분류 카테고리")
    rank_method: RankMethod = Field(
        default=RankMethod.rating,
        description="순위 방식: rating, review_count, distance, yamyam_popularity",
    )
    lat: Optional[float] = Field(None, ge=-90, le=90, description="위도")
    lon: Optional[float] = Field(None, ge=-180, le=180, description="경도")
    period: str = Field(default="all", description="기간: 1M, 3M, 6M, all")
    reference_date: Optional[datetime] = Field(
        None, description="기준 날짜 (YYYY-MM-DD)"
    )
    topk: int = Field(default=10, ge=1, le=100, description="반환 개수")
    min_review_count: int = Field(default=5, ge=0, description="최소 리뷰 수")

    @field_validator("reference_date", mode="before")
    @classmethod
    def parse_reference_date(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            return datetime.strptime(v, "%Y-%m-%d")
        raise ValueError(f"Unsupported type for reference_date: {type(v)}")


class MostPopularRankResponse(BaseModel):
    """MP Rank 응답 스키마"""

    diner_ids: List[int] = Field(..., description="음식점 ID 목록")
    count: int = Field(..., description="음식점 수")
    rank_method: RankMethod = Field(..., description="순위 방식")
    period: str = Field(..., description="적용 기간")
    filters: dict = Field(..., description="적용 필터")


class MostPopularRankError(BaseModel):
    """에러 응답 스키마"""

    detail: Union[str, List[str]] = Field(..., description="에러 메시지")
    error_code: Optional[str] = Field(None, description="에러 코드")
