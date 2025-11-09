from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class Vector(BaseModel):
    """사용자 벡터 데이터"""

    id: str = Field(
        ..., min_length=1, description="벡터의 고유 ID. 유저 ID 또는 식당 ID"
    )
    embedding: List[float] = Field(..., min_length=1, description="임베딩 벡터")


class StoreVectorsRequest(BaseModel):
    """Request model for storing vectors to FAISS index"""

    vectors: List[Vector] = Field(..., min_length=1, description="추가할 벡터 리스트")

    class Config:
        json_schema_extra = {
            "example": {
                "vectors": [
                    {"id": "user_123", "embedding": [0.1, 0.2, 0.3]},
                    {"id": "user_456", "embedding": [0.4, 0.5, 0.6]},
                ]
            }
        }


class StoreVectorsResponse(BaseModel):
    """Response model for storing vectors to FAISS index"""

    num_vectors: int = Field(..., description="Number of indexed vectors")
    vector_dimension: int = Field(..., description="Vector dimension")


class SimilarRequest(BaseModel):
    query_id: str = Field(..., min_length=1, description="유사도를 계산할 쿼리 ID")
    query_vector: List[float] = Field(
        ...,
        min_length=1,
        description="쿼리 벡터 (유저가 식당에 부여한 점수 벡터 또는 유저 임베딩 벡터)",
    )
    top_k: int = Field(default=5, ge=1, le=50, description="반환할 검색 결과의 수")

    class Config:
        json_schema_extra = {
            "example": {
                "query_id": "user_999",
                "query_vector": [0.1, 0.3, 0.7],
                "top_k": 5,
            }
        }


class SimilarResult(BaseModel):
    id: str
    score: float


class SimilarResponse(BaseModel):
    query_id: str
    neighbors: List[SimilarResult]
