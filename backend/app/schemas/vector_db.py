from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class UserVector(BaseModel):
    """사용자 벡터 데이터"""

    user_id: str = Field(..., min_length=1, description="사용자 ID")
    embedding: List[float] = Field(..., min_length=1, description="사용자 임베딩 벡터")


class IndexCreateRequest(BaseModel):
    """벡터 인덱스 생성 요청"""

    vectors: List[UserVector] = Field(
        ..., min_length=1, description="인덱싱할 사용자 벡터 리스트"
    )


class IndexCreateResponse(BaseModel):
    """벡터 인덱스 생성 응답"""

    num_users: int = Field(..., description="인덱싱된 사용자 수")
    vector_dimension: int = Field(..., description="벡터 차원")


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


class SimilarUser(BaseModel):
    user_id: str
    score: float


class SimilarUsersResponse(BaseModel):
    query_user_id: str
    neighbors: List[SimilarUser]
