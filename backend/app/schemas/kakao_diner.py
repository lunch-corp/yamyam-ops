from typing import Optional

from pydantic import BaseModel, Field


class KakaoDinerBase(BaseModel):
    diner_idx: int = Field(..., description="카카오 음식점 고유 인덱스")
    diner_name: str = Field(
        ..., min_length=1, max_length=255, description="음식점 이름"
    )
    diner_tag: Optional[str] = Field(None, description="음식점 태그")
    diner_menu_name: Optional[str] = Field(None, description="대표 메뉴명")
    diner_menu_price: Optional[str] = Field(None, description="메뉴 가격")
    diner_review_cnt: str = Field(..., description="리뷰 개수 (문자열)")
    diner_review_avg: float = Field(..., ge=0, le=5, description="평균 평점")
    diner_blog_review_cnt: float = Field(..., ge=0, description="블로그 리뷰 개수")
    diner_review_tags: Optional[str] = Field(None, description="리뷰 태그")
    diner_road_address: Optional[str] = Field(None, description="도로명 주소")
    diner_num_address: Optional[str] = Field(None, description="지번 주소")
    diner_phone: Optional[str] = Field(None, max_length=50, description="전화번호")
    diner_lat: float = Field(..., ge=-90, le=90, description="위도")
    diner_lon: float = Field(..., ge=-180, le=180, description="경도")


class KakaoDinerCreate(KakaoDinerBase):
    pass


class KakaoDinerUpdate(BaseModel):
    diner_name: Optional[str] = Field(None, min_length=1, max_length=255)
    diner_tag: Optional[str] = None
    diner_menu_name: Optional[str] = None
    diner_menu_price: Optional[str] = None
    diner_review_cnt: Optional[str] = None
    diner_review_avg: Optional[float] = Field(None, ge=0, le=5)
    diner_blog_review_cnt: Optional[float] = Field(None, ge=0)
    diner_review_tags: Optional[str] = None
    diner_road_address: Optional[str] = None
    diner_num_address: Optional[str] = None
    diner_phone: Optional[str] = Field(None, max_length=50)
    diner_lat: Optional[float] = Field(None, ge=-90, le=90)
    diner_lon: Optional[float] = Field(None, ge=-180, le=180)


class KakaoDiner(KakaoDinerBase):
    id: str  # ULID
    crawled_at: str
    updated_at: str

    class Config:
        from_attributes = True


class KakaoDinerResponse(BaseModel):
    id: str  # ULID
    diner_idx: int
    diner_name: str
    diner_tag: Optional[str]
    diner_menu_name: Optional[str]
    diner_menu_price: Optional[str]
    diner_review_cnt: str
    diner_review_avg: float
    diner_blog_review_cnt: float
    diner_review_tags: Optional[str]
    diner_road_address: Optional[str]
    diner_num_address: Optional[str]
    diner_phone: Optional[str]
    diner_lat: float
    diner_lon: float
    diner_category_large: Optional[str]
    diner_category_middle: Optional[str]
    diner_category_small: Optional[str]
    diner_category_detail: Optional[str]
    crawled_at: str
    updated_at: str
