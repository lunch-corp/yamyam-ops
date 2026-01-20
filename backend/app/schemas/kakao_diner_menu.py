"""
Kakao 음식점 메뉴 스키마
"""

from datetime import datetime

from pydantic import BaseModel, Field


class KakaoDinerMenuBase(BaseModel):
    """메뉴 기본 스키마"""

    diner_idx: int = Field(..., description="카카오 음식점 고유 인덱스")
    name: str = Field(..., min_length=1, max_length=255, description="메뉴 이름")
    product_id: str = Field(..., min_length=1, max_length=255, description="상품 ID")
    price: float | None = Field(None, ge=0, description="가격")
    is_ai_mate: bool | None = Field(None, description="AI 메이트 메뉴 여부")
    photo_url: str | None = Field(None, description="메뉴 사진 URL")
    is_recommend: bool | None = Field(None, description="추천 메뉴 여부")
    desc: str | None = Field(None, description="메뉴 설명")
    mod_at: datetime | None = Field(None, description="수정 시각")


class KakaoDinerMenuCreate(KakaoDinerMenuBase):
    """메뉴 생성 스키마"""

    pass


class KakaoDinerMenuUpdate(BaseModel):
    """메뉴 업데이트 스키마 (모든 필드 optional)"""

    diner_idx: int | None = Field(None, description="카카오 음식점 고유 인덱스")
    name: str | None = Field(
        None, min_length=1, max_length=255, description="메뉴 이름"
    )
    product_id: str | None = Field(
        None, min_length=1, max_length=255, description="상품 ID"
    )
    price: float | None = Field(None, ge=0, description="가격")
    is_ai_mate: bool | None = Field(None, description="AI 메이트 메뉴 여부")
    photo_url: str | None = Field(None, description="메뉴 사진 URL")
    is_recommend: bool | None = Field(None, description="추천 메뉴 여부")
    desc: str | None = Field(None, description="메뉴 설명")
    mod_at: datetime | None = Field(None, description="수정 시각")


class KakaoDinerMenuResponse(KakaoDinerMenuBase):
    """메뉴 응답 스키마"""

    id: str  # ULID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
