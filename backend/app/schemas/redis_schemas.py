from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


class RedisCreateRequest(BaseModel):
    items: Dict[str, Any] = Field(
        ..., description="Key-value dictionary to create", min_length=1
    )
    expire: Optional[int] = Field(
        None, description="Expiration time in seconds for all keys", ge=1
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError("items must contain at least one key-value pair")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"items": {"1783192": {"diner_ids": ["57812123"]}}, "expire": 3600},
                {
                    "items": {
                        "1783192": {"diner_ids": ["57812123", "84903251", "23145678"]},
                        "2894561": {"diner_ids": ["12456789", "98765432"]},
                        "3145927": {"diner_ids": ["45678901"]},
                    },
                    "expire": 3600,
                },
            ]
        }
    }


class RedisReadRequest(BaseModel):
    keys: List[str] = Field(..., description="List of keys to read", min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"keys": ["1783192"]},
                {"keys": ["1783192", "2894561", "3145927"]},
            ]
        }
    }


class RedisUpdateRequest(BaseModel):
    items: Dict[str, Any] = Field(
        ..., description="Key-value dictionary to update", min_length=1
    )
    expire: Optional[int] = Field(
        None, description="Expiration time in seconds for all keys", ge=1
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError("items must contain at least one key-value pair")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": {"1783192": {"diner_ids": ["57812123", "91234567"]}},
                    "expire": 7200,
                },
                {
                    "items": {
                        "1783192": {
                            "diner_ids": [
                                "57812123",
                                "84903251",
                                "23145678",
                                "65432109",
                            ]
                        },
                        "2894561": {"diner_ids": ["12456789"]},
                    },
                    "expire": 7200,
                },
            ]
        }
    }


class RedisDeleteRequest(BaseModel):
    keys: List[str] = Field(..., description="List of keys to delete", min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"keys": ["1783192"]},
                {"keys": ["1783192", "2894561", "3145927"]},
            ]
        }
    }


class RedisResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(..., description="Result for each key")
    stats: Dict[str, int] = Field(..., description="Operation statistics")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Operation completed successfully",
                    "data": {"1783192": True},
                    "stats": {"total": 1, "succeeded": 1, "failed": 0},
                },
                {
                    "success": True,
                    "message": "Operation completed with partial success",
                    "data": {"1783192": True, "2894561": True, "3145927": False},
                    "stats": {"total": 3, "succeeded": 2, "failed": 1},
                },
            ]
        }
    }


class RedisReadResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: Dict[str, Any] = Field(
        ..., description="Value for each key (null if not found)"
    )
    stats: Dict[str, int] = Field(..., description="Read statistics")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Read completed successfully",
                    "data": {"1783192": {"diner_ids": ["57812123", "84903251"]}},
                    "stats": {"total": 1, "found": 1, "not_found": 0},
                },
                {
                    "success": True,
                    "message": "Read completed with partial results",
                    "data": {
                        "1783192": {"diner_ids": ["57812123", "84903251"]},
                        "2894561": {"diner_ids": ["12456789"]},
                        "3145927": None,
                    },
                    "stats": {"total": 3, "found": 2, "not_found": 1},
                },
            ]
        }
    }
