"""
Kakao 음식점 영업시간 스키마
"""

from datetime import datetime, time

from pydantic import BaseModel, Field


class KakaoDinerOpenHoursBase(BaseModel):
    """영업시간 기본 스키마"""

    diner_idx: int = Field(..., description="카카오 음식점 고유 인덱스")
    day_of_week: int = Field(..., ge=0, le=6, description="요일 (0=월요일, 6=일요일)")
    is_open: bool = Field(True, description="영업 여부")
    start_time: time | None = Field(None, description="영업 시작 시간")
    end_time: time | None = Field(None, description="영업 종료 시간")
    description: str | None = Field(
        None, description="추가 설명 (휴무일, 24시간 영업 등)"
    )


class KakaoDinerOpenHoursCreate(KakaoDinerOpenHoursBase):
    """영업시간 생성 스키마"""

    pass


class KakaoDinerOpenHoursUpdate(BaseModel):
    """영업시간 업데이트 스키마 (모든 필드 optional)"""

    diner_idx: int | None = Field(None, description="카카오 음식점 고유 인덱스")
    day_of_week: int | None = Field(
        None, ge=0, le=6, description="요일 (0=월요일, 6=일요일)"
    )
    is_open: bool | None = Field(None, description="영업 여부")
    start_time: time | None = Field(None, description="영업 시작 시간")
    end_time: time | None = Field(None, description="영업 종료 시간")
    description: str | None = Field(
        None, description="추가 설명 (휴무일, 24시간 영업 등)"
    )


class KakaoDinerOpenHoursResponse(KakaoDinerOpenHoursBase):
    """영업시간 응답 스키마"""

    id: str  # ULID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
