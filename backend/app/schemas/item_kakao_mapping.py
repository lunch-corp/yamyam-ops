from pydantic import BaseModel, Field


class ItemKakaoMappingBase(BaseModel):
    item_id: str  # ULID
    diner_idx: int = Field(..., description="카카오 음식점 인덱스")
    mapping_type: str = Field("manual", max_length=20)
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)


class ItemKakaoMappingCreate(ItemKakaoMappingBase):
    pass


class ItemKakaoMappingUpdate(BaseModel):
    mapping_type: str | None = Field(None, max_length=20)
    confidence_score: float | None = Field(None, ge=0.0, le=1.0)


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
    confidence_score: float | None
    created_at: str
    updated_at: str


class ItemKakaoMappingWithDetails(ItemKakaoMappingResponse):
    item_name: str | None
    item_category: str | None
    diner_name: str | None
    diner_tag: str | None
