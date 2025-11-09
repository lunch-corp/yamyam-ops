from __future__ import annotations

from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class VectorType(str, Enum):
    """벡터 타입 열거형"""

    USER_CF_VEC = "user_cf_vec"
    USER_N2V_VEC = "user_n2v_vec"
    DINER_N2V_VEC = "diner_n2v_vec"


class Vector(BaseModel):
    """사용자 벡터 데이터"""

    id: str = Field(
        ..., min_length=1, description="벡터의 고유 ID. 유저 ID 또는 식당 ID"
    )
    embedding: List[float] = Field(..., min_length=1, description="임베딩 벡터")


class StoreVectorsRequest(BaseModel):
    """Request model for storing vectors to FAISS index"""

    vector_type: VectorType = Field(
        ..., description="벡터 타입 (user_cf_vec, user_n2v_vec, diner_n2v_vec)"
    )
    vectors: List[Vector] = Field(..., min_length=1, description="추가할 벡터 리스트")
    normalize: bool = Field(
        default=True, description="벡터를 정규화할지 여부 (기본값: True)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "vector_type": "user_cf_vec",
                "vectors": [
                    {"id": "user_123", "embedding": [0.1, 0.2, 0.3]},
                    {"id": "user_456", "embedding": [0.4, 0.5, 0.6]},
                ],
                "normalize": True,
            }
        }


class StoreVectorsResponse(BaseModel):
    """Response model for storing vectors to FAISS index"""

    num_vectors: int = Field(..., description="Number of indexed vectors")
    vector_dimension: int = Field(..., description="Vector dimension")


class SimilarRequest(BaseModel):
    vector_type: VectorType = Field(
        ..., description="검색할 벡터 타입 (user_cf_vec, user_n2v_vec, diner_n2v_vec)"
    )
    query_id: str = Field(..., min_length=1, description="유사도를 계산할 쿼리 ID")
    query_vector: List[float] = Field(
        ...,
        min_length=1,
        description="쿼리 벡터 (유저가 식당에 부여한 점수 벡터 또는 유저 임베딩 벡터)",
    )
    top_k: int = Field(default=5, ge=1, le=50, description="반환할 검색 결과의 수")
    filtering_ids: List[str] = Field(
        default_factory=list,
        description="필터링할 ID 리스트 (검색 결과에서 제외할 ID들)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "vector_type": "user_cf_vec",
                "query_id": "user_999",
                "query_vector": [0.1, 0.3, 0.7],
                "top_k": 5,
                "filtering_ids": ["user_123", "user_456"],
            }
        }


class SimilarResult(BaseModel):
    id: str
    score: float


class SimilarResponse(BaseModel):
    query_id: str
    neighbors: List[SimilarResult]
