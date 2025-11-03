"""
벡터 검색 관련 스키마
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class EmbeddingVectorCreate(BaseModel):
    """임베딩 벡터 생성 요청"""

    entity_type: str = Field(..., description="엔티티 타입: 'user' 또는 'item'")
    entity_id: str = Field(..., description="엔티티 ID (ULID)")
    embedding_type: str = Field(
        default="default",
        description="임베딩 타입 (예: 'default', 'category', 'content')",
    )
    vector: List[float] = Field(..., description="벡터 데이터 (1차원 리스트)")
    dimension: int = Field(..., description="벡터 차원")


class EmbeddingVectorResponse(BaseModel):
    """임베딩 벡터 응답"""

    id: str
    entity_type: str
    entity_id: str
    embedding_type: str
    dimension: int


class SimilaritySearchRequest(BaseModel):
    """유사도 검색 요청"""

    entity_type: str = Field(..., description="엔티티 타입: 'user' 또는 'item'")
    query_vector: List[float] = Field(..., description="검색 쿼리 벡터")
    k: int = Field(default=10, ge=1, le=100, description="반환할 결과 개수")


class SimilaritySearchResponse(BaseModel):
    """유사도 검색 응답"""

    entity_id: str
    distance: float
    similarity: float = Field(..., description="유사도 점수 (1 - normalized_distance)")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                "distance": 0.85,
                "similarity": 0.15,
            }
        }


class VectorSearchResults(BaseModel):
    """벡터 검색 결과 목록"""

    query_type: str = Field(..., description="검색 타입")
    total_results: int
    results: List[SimilaritySearchResponse]

    class Config:
        json_schema_extra = {
            "example": {
                "query_type": "user2user",
                "total_results": 10,
                "results": [
                    {
                        "entity_id": "01ARZ3NDEKTSV4RRFFQ69G5FAV",
                        "distance": 0.85,
                        "similarity": 0.15,
                    }
                ],
            }
        }


class UserSimilarityRequest(BaseModel):
    """사용자 유사도 검색 요청"""

    user_id: str = Field(..., description="사용자 ID")
    k: int = Field(default=10, ge=1, le=100, description="반환할 유사 사용자 개수")


class ItemSimilarityRequest(BaseModel):
    """아이템 유사도 검색 요청"""

    item_id: str = Field(..., description="아이템 ID")
    k: int = Field(default=10, ge=1, le=100, description="반환할 유사 아이템 개수")


class IndexRebuildRequest(BaseModel):
    """인덱스 재구축 요청"""

    entity_type: str = Field(..., description="엔티티 타입: 'user' 또는 'item'")


class IndexRebuildResponse(BaseModel):
    """인덱스 재구축 응답"""

    entity_type: str
    status: str
    total_vectors: Optional[int] = None
    message: str
