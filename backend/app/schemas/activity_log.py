from typing import Any, Optional

from pydantic import BaseModel, Field


class ActivityLogCreate(BaseModel):
    """활동 로그 생성 스키마"""

    # User identification
    firebase_uid: str = Field(..., max_length=128)
    session_id: str = Field(..., max_length=50)

    # Event information
    event_type: str = Field(..., max_length=50)
    page: Optional[str] = Field(None, max_length=50)

    # Location related
    location_query: Optional[str] = Field(None, max_length=255)
    location_address: Optional[str] = Field(None, max_length=255)
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_method: Optional[str] = Field(None, max_length=50)

    # Search filter related
    search_radius_km: Optional[float] = None
    selected_large_categories: Optional[list[str]] = None
    selected_middle_categories: Optional[list[str]] = None
    sort_by: Optional[str] = Field(None, max_length=50)
    period: Optional[str] = Field(None, max_length=20)

    # Ranking page related
    selected_city: Optional[str] = Field(None, max_length=100)
    selected_region: Optional[str] = Field(None, max_length=100)
    selected_grades: Optional[list[str]] = None

    # Click/Interaction related
    clicked_diner_idx: Optional[str] = Field(None, max_length=50)
    clicked_diner_name: Optional[str] = Field(None, max_length=255)
    display_position: Optional[int] = None

    # Additional metadata
    additional_data: Optional[dict[str, Any]] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = Field(None, max_length=45)


class ActivityLogResponse(BaseModel):
    """활동 로그 응답 스키마"""

    id: str
    user_id: str
    firebase_uid: str
    session_id: str
    event_type: str
    event_timestamp: str
    page: Optional[str] = None

    # Location related
    location_query: Optional[str] = None
    location_address: Optional[str] = None
    location_lat: Optional[float] = None
    location_lon: Optional[float] = None
    location_method: Optional[str] = None

    # Search filter related
    search_radius_km: Optional[float] = None
    selected_large_categories: Optional[list[str]] = None
    selected_middle_categories: Optional[list[str]] = None
    sort_by: Optional[str] = None
    period: Optional[str] = None

    # Ranking page related
    selected_city: Optional[str] = None
    selected_region: Optional[str] = None
    selected_grades: Optional[list[str]] = None

    # Click/Interaction related
    clicked_diner_idx: Optional[str] = None
    clicked_diner_name: Optional[str] = None
    display_position: Optional[int] = None

    # Additional metadata
    additional_data: Optional[dict[str, Any]] = None
    user_agent: Optional[str] = None
    ip_address: Optional[str] = None


class ActivityLogFilter(BaseModel):
    """활동 로그 조회 필터"""

    event_type: Optional[str] = None
    page: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    limit: int = Field(100, ge=1, le=1000)
    offset: int = Field(0, ge=0)


class ActivityLogExport(BaseModel):
    """ML 학습용 데이터 추출 요청"""

    start_date: Optional[str] = None
    end_date: Optional[str] = None
    event_types: Optional[list[str]] = None
    format: str = Field("json", pattern="^(json|csv)$")
