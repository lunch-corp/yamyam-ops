from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class VectorType(str, Enum):
    """벡터 타입 열거형"""

    USER_N2V_VEC = "user_n2v_vec"
    DINER_N2V_VEC = "diner_n2v_vec"


class Vector(BaseModel):
    """사용자 벡터 데이터"""

    id: str = Field(
        ..., min_length=1, description="벡터의 고유 ID. 유저 ID 또는 식당 ID"
    )
    embedding: list[float] = Field(..., min_length=1, description="임베딩 벡터")


class StoreVectorsRequest(BaseModel):
    """Request model for storing vectors to FAISS index"""

    vector_type: VectorType = Field(
        ..., description="벡터 타입 (user_cf_vec, user_n2v_vec, diner_n2v_vec)"
    )
    vectors: list[Vector] = Field(..., min_length=1, description="추가할 벡터 리스트")
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
    query_vector: list[float] = Field(
        ...,
        min_length=1,
        description="쿼리 벡터 (유저가 식당에 부여한 점수 벡터 또는 유저 임베딩 벡터)",
    )
    top_k: int = Field(default=5, ge=1, le=50, description="반환할 검색 결과의 수")
    filtering_ids: list[str] = Field(
        default_factory=list,
        description="필터링할 ID 리스트 (검색 결과에서 제외할 ID들)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "vector_type": "diner_n2v_vec",
                "query_id": "3933744720",
                "query_vector": [
                    -0.12561821937561035,
                    -0.03369925171136856,
                    -0.39972561597824097,
                    -0.6673964858055115,
                    0.11689186841249466,
                    0.5598220825195312,
                    -0.34878936409950256,
                    -0.5005061626434326,
                    -0.8800399303436279,
                    0.47142294049263,
                    -0.29236698150634766,
                    -1.1601372957229614,
                    -0.0975121557712555,
                    0.07908879220485687,
                    0.5002485513687134,
                    -0.2787158787250519,
                    1.1575356721878052,
                    0.4767698347568512,
                    0.06968090683221817,
                    -0.3087456524372101,
                    -1.0148934125900269,
                    0.16138163208961487,
                    -0.04065752029418945,
                    0.527062714099884,
                    0.5510784983634949,
                    0.23201680183410645,
                    0.7762333750724792,
                    0.16958439350128174,
                    -0.18376557528972626,
                    -0.4413832426071167,
                    0.14043107628822327,
                    -0.6219544410705566,
                ],
                "top_k": 5,
                "filtering_ids": ["1642119072", "243733683"],
            }
        }


class SimilarResult(BaseModel):
    id: str
    score: float


class SimilarResponse(BaseModel):
    query_id: str
    neighbors: list[SimilarResult]


class SearchVectorRequest(BaseModel):
    """Request model for searching a vector by ID"""

    vector_type: VectorType = Field(
        ..., description="벡터 타입 (user_n2v_vec, diner_n2v_vec)"
    )
    id: str = Field(..., min_length=1, description="검색할 벡터의 id")

    class Config:
        json_schema_extra = {
            "example": {
                "vector_type": "user_n2v_vec",
                "id": "3933744720",
            }
        }


class SearchVectorResponse(BaseModel):
    """Response model for searching a vector by ID"""

    id: str = Field(..., description="The ID of the vector")
    embedding: list[float] = Field(..., description="The embedding vector")
    vector_type: VectorType = Field(..., description="The type of the vector")
