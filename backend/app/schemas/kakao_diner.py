from pydantic import BaseModel, Field


class KakaoDinerBase(BaseModel):
    diner_idx: int = Field(..., description="카카오 음식점 고유 인덱스")
    diner_name: str = Field(
        ..., min_length=1, max_length=255, description="음식점 이름"
    )
    diner_tag: str | None = Field(None, description="음식점 태그")
    diner_menu_name: str | None = Field(None, description="대표 메뉴명")
    diner_menu_price: str | None = Field(None, description="메뉴 가격")
    diner_review_cnt: str = Field(..., description="리뷰 개수 (문자열)")
    diner_review_avg: float = Field(..., ge=0, le=5, description="평균 평점")
    diner_blog_review_cnt: float = Field(..., ge=0, description="블로그 리뷰 개수")
    diner_review_tags: str | None = Field(None, description="리뷰 태그")
    diner_road_address: str | None = Field(None, description="도로명 주소")
    diner_num_address: str | None = Field(None, description="지번 주소")
    diner_phone: str | None = Field(None, max_length=50, description="전화번호")
    diner_lat: float = Field(..., ge=-90, le=90, description="위도")
    diner_lon: float = Field(..., ge=-180, le=180, description="경도")


class KakaoDinerCreate(KakaoDinerBase):
    pass


class KakaoDinerUpdate(BaseModel):
    diner_name: str | None = Field(None, min_length=1, max_length=255)
    diner_tag: str | None = None
    diner_menu_name: str | None = None
    diner_menu_price: str | None = None
    diner_review_cnt: str | None = None
    diner_review_avg: float | None = Field(None, ge=0, le=5)
    diner_blog_review_cnt: float | None = Field(None, ge=0)
    diner_review_tags: str | None = None
    diner_road_address: str | None = None
    diner_num_address: str | None = None
    diner_phone: str | None = Field(None, max_length=50)
    diner_lat: float | None = Field(None, ge=-90, le=90)
    diner_lon: float | None = Field(None, ge=-180, le=180)


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
    diner_tag: str | None
    diner_menu_name: str | None
    diner_menu_price: str | None
    diner_review_cnt: str
    diner_review_avg: float
    diner_blog_review_cnt: float
    diner_review_tags: str | None
    diner_road_address: str | None
    diner_num_address: str | None
    diner_phone: str | None
    diner_lat: float
    diner_lon: float
    diner_category_large: str | None
    diner_category_middle: str | None
    diner_category_small: str | None
    diner_category_detail: str | None
    crawled_at: str
    updated_at: str
