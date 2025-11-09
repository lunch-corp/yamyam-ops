from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class UserVector(BaseModel):
    """사용자 벡터 데이터"""

    user_id: str = Field(..., min_length=1, description="사용자 ID")
    embedding: List[float] = Field(..., min_length=1, description="사용자 임베딩 벡터")


class StoreVectorsRequest(BaseModel):
    """Request model for storing vectors to FAISS index"""

    vectors: List[UserVector] = Field(
        ..., min_length=1, description="추가할 사용자 벡터 리스트"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "vectors": [
                    {"user_id": "user_123", "embedding": [0.1, 0.2, 0.3]},
                    {"user_id": "user_456", "embedding": [0.4, 0.5, 0.6]},
                ]
            }
        }


class StoreVectorsResponse(BaseModel):
    """Response model for storing vectors to FAISS index"""

    num_users: int = Field(..., description="Number of indexed users")
    vector_dimension: int = Field(..., description="Vector dimension")


class SimilarUsersRequest(BaseModel):
    user_id: str = Field(
        ..., min_length=1, description="유사도를 계산할 대상 사용자 ID"
    )
    diner_scores: List[float] = Field(
        ...,
        min_length=1,
        description="사용자가 각 식당(다이너)에 매긴 점수 리스트",
    )
    top_k: int = Field(default=5, ge=1, le=50, description="반환할 유사 사용자 수")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": "user_999",
                "diner_scores": [0.1, 0.3, 0.7],
                "top_k": 5,
            }
        }


class SimilarUser(BaseModel):
    user_id: str
    score: float


class SimilarUsersResponse(BaseModel):
    query_user_id: str
    neighbors: List[SimilarUser]
