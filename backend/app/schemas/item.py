from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)
    description: str | None = None
    location: str | None = Field(None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    category: str | None = Field(None, max_length=100)
    description: str | None = None
    location: str | None = Field(None, max_length=255)


class Item(ItemBase):
    id: str  # ULID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ItemResponse(BaseModel):
    id: str  # ULID
    name: str
    category: str | None
    description: str | None
    location: str | None
    created_at: str
    updated_at: str
