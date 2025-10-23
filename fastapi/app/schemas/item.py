from typing import Optional

from pydantic import BaseModel, Field


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)


class ItemCreate(ItemBase):
    pass


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    location: Optional[str] = Field(None, max_length=255)


class Item(ItemBase):
    id: str  # ULID
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


class ItemResponse(BaseModel):
    id: str  # ULID
    name: str
    category: Optional[str]
    description: Optional[str]
    location: Optional[str]
    created_at: str
    updated_at: str
