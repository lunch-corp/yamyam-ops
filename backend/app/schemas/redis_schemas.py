from typing import Any

from pydantic import BaseModel, Field, field_validator


class RedisCreateRequest(BaseModel):
    items: dict[str, Any] = Field(
        ..., description="Key-value dictionary to create", min_length=1
    )
    expire: int | None = Field(
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
                # Single user recommendation - candidate diners
                {
                    "items": {
                        "user:1783192:candidate_diner_ids": [
                            "57812123",
                            "84903251",
                            "23145678",
                        ]
                    },
                    "expire": 3600,
                },
                # Single user recommendation - both candidate and ranked
                {
                    "items": {
                        "user:1783192:candidate_diner_ids": [
                            "57812123",
                            "84903251",
                            "23145678",
                        ],
                        "user:1783192:ranked_diner_ids": [
                            "57812123",
                            "23145678",
                            "84903251",
                        ],
                    },
                    "expire": 3600,
                },
                # Single diner similarity
                {
                    "items": {
                        "diner:57812123:similar_diner_ids": [
                            "84903251",
                            "23145678",
                            "91234567",
                        ]
                    },
                    "expire": 7200,
                },
                # Multiple users and diners
                {
                    "items": {
                        "user:1783192:candidate_diner_ids": ["57812123", "84903251"],
                        "user:1783192:ranked_diner_ids": ["57812123", "84903251"],
                        "user:2894561:candidate_diner_ids": ["12456789", "98765432"],
                        "user:2894561:ranked_diner_ids": ["98765432", "12456789"],
                        "diner:57812123:similar_diner_ids": ["84903251", "23145678"],
                    },
                    "expire": 3600,
                },
            ]
        }
    }


class RedisReadRequest(BaseModel):
    keys: list[str] = Field(..., description="List of keys to read", min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                # Read single user's candidate diners
                {"keys": ["user:1783192:candidate_diner_ids"]},
                # Read single user's both properties
                {
                    "keys": [
                        "user:1783192:candidate_diner_ids",
                        "user:1783192:ranked_diner_ids",
                    ]
                },
                # Read single diner similarity
                {"keys": ["diner:57812123:similar_diner_ids"]},
                # Read multiple mixed types
                {
                    "keys": [
                        "user:1783192:candidate_diner_ids",
                        "user:1783192:ranked_diner_ids",
                        "diner:57812123:similar_diner_ids",
                        "diner:84903251:similar_diner_ids",
                    ]
                },
            ]
        }
    }


class RedisUpdateRequest(BaseModel):
    items: dict[str, Any] = Field(
        ..., description="Key-value dictionary to update", min_length=1
    )
    expire: int | None = Field(
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
                # Update user recommendations
                {
                    "items": {
                        "user:1783192:candidate_diner_ids": [
                            "57812123",
                            "91234567",
                            "45678901",
                        ],
                        "user:1783192:ranked_diner_ids": [
                            "91234567",
                            "57812123",
                            "45678901",
                        ],
                    },
                    "expire": 7200,
                },
                # Update diner similarities
                {
                    "items": {
                        "diner:57812123:similar_diner_ids": [
                            "84903251",
                            "65432109",
                            "11223344",
                        ]
                    },
                    "expire": 7200,
                },
                # Update multiple keys
                {
                    "items": {
                        "user:1783192:candidate_diner_ids": ["57812123", "84903251"],
                        "user:1783192:ranked_diner_ids": ["84903251", "57812123"],
                        "diner:57812123:similar_diner_ids": ["84903251", "23145678"],
                    },
                    "expire": 7200,
                },
            ]
        }
    }


class RedisDeleteRequest(BaseModel):
    keys: list[str] = Field(..., description="List of keys to delete", min_length=1)

    model_config = {
        "json_schema_extra": {
            "examples": [
                # Delete single user property
                {"keys": ["user:1783192:candidate_diner_ids"]},
                # Delete all user properties
                {
                    "keys": [
                        "user:1783192:candidate_diner_ids",
                        "user:1783192:ranked_diner_ids",
                    ]
                },
                # Delete single diner similarity
                {"keys": ["diner:57812123:similar_diner_ids"]},
                # Delete multiple mixed types
                {
                    "keys": [
                        "user:1783192:candidate_diner_ids",
                        "user:1783192:ranked_diner_ids",
                        "diner:57812123:similar_diner_ids",
                        "diner:84903251:similar_diner_ids",
                    ]
                },
            ]
        }
    }


class RedisResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: dict[str, Any] = Field(..., description="Result for each key")
    stats: dict[str, int] = Field(..., description="Operation statistics")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Created 1 key(s)",
                    "data": {"user:1783192:candidate_diner_ids": True},
                    "stats": {"total": 1, "succeeded": 1, "failed": 0},
                },
                {
                    "success": True,
                    "message": "Created 3 key(s)",
                    "data": {
                        "user:1783192:candidate_diner_ids": True,
                        "user:1783192:ranked_diner_ids": True,
                        "diner:57812123:similar_diner_ids": True,
                    },
                    "stats": {"total": 3, "succeeded": 3, "failed": 0},
                },
            ]
        }
    }


class RedisReadResponse(BaseModel):
    success: bool = Field(..., description="Operation success status")
    message: str = Field(..., description="Response message")
    data: dict[str, Any] = Field(
        ..., description="Value for each key (null if not found)"
    )
    stats: dict[str, int] = Field(..., description="Read statistics")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "success": True,
                    "message": "Read 1 key(s)",
                    "data": {
                        "user:1783192:candidate_diner_ids": ["57812123", "84903251"]
                    },
                    "stats": {"total": 1, "found": 1, "not_found": 0},
                },
                {
                    "success": True,
                    "message": "Read 3/4 key(s)",
                    "data": {
                        "user:1783192:candidate_diner_ids": ["57812123", "84903251"],
                        "user:1783192:ranked_diner_ids": ["57812123", "84903251"],
                        "diner:57812123:similar_diner_ids": ["84903251", "23145678"],
                        "diner:99999999:similar_diner_ids": None,
                    },
                    "stats": {"total": 4, "found": 3, "not_found": 1},
                },
            ]
        }
    }
