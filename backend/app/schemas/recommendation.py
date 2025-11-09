from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class DummyIndexConfig(BaseModel):
    num_users: int = Field(
        default=10, ge=2, le=10_000, description="생성할 더미 사용자 수"
    )
    num_diners: int = Field(
        default=20, ge=2, le=1_000, description="사용자-다이너 상호작용 벡터 차원"
    )
    random_seed: int = Field(default=42, description="재현 가능성을 위한 시드 값")


class DummyIndexStatus(BaseModel):
    num_users: int
    num_diners: int


class SimilarUsersRequest(BaseModel):
    user_id: str = Field(
        ..., min_length=1, description="유사도를 계산할 대상 사용자 ID"
    )
    top_k: int = Field(default=5, ge=1, le=50, description="반환할 유사 사용자 수")


class SimilarUser(BaseModel):
    user_id: str
    score: float


class SimilarUsersResponse(BaseModel):
    query_user_id: str
    neighbors: List[SimilarUser]
