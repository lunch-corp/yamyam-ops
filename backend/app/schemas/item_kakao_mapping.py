from typing import Optional

from pydantic import BaseModel, Field


class ItemKakaoMappingBase(BaseModel):
    item_id: str  # ULID
    diner_idx: int = Field(..., description="카카오 음식점 인덱스")
    mapping_type: str = Field("manual", max_length=20)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ItemKakaoMappingCreate(ItemKakaoMappingBase):
    pass


class ItemKakaoMappingUpdate(BaseModel):
    mapping_type: Optional[str] = Field(None, max_length=20)
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class ItemKakaoMapping(ItemKakaoMappingBase):
    id: str  # ULID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ItemKakaoMappingResponse(BaseModel):
    id: str  # ULID
    item_id: str  # ULID
    diner_idx: int
    mapping_type: str
    confidence_score: Optional[float]
    created_at: str
    updated_at: str


class ItemKakaoMappingWithDetails(ItemKakaoMappingResponse):
    item_name: Optional[str]
    item_category: Optional[str]
    diner_name: Optional[str]
    diner_tag: Optional[str]
