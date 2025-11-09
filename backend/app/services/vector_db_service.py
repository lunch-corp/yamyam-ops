from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

import faiss
import numpy as np

from app.schemas.vector_db import (
    IndexCreateRequest,
    IndexCreateResponse,
    SimilarUsersResponse,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _IndexArtifacts:
    index: faiss.IndexFlatIP
    user_ids: List[str]
    embeddings: np.ndarray


class VectorDBService:
    """FAISS 벡터 데이터베이스 서비스"""

    def __init__(self) -> None:
        self._artifacts: _IndexArtifacts | None = None

    def build_index(self, request: IndexCreateRequest) -> IndexCreateResponse:
        """벡터 데이터로부터 FAISS 인덱스 생성"""
        if not request.vectors:
            raise ValueError("vectors list cannot be empty")

        # 벡터 차원 검증
        vector_dim = len(request.vectors[0].embedding)
        if vector_dim == 0:
            raise ValueError("embedding vector cannot be empty")

        # 모든 벡터의 차원이 동일한지 확인
        for vec in request.vectors:
            if len(vec.embedding) != vector_dim:
                raise ValueError(
                    f"All vectors must have the same dimension. "
                    f"Expected {vector_dim}, but found {len(vec.embedding)}"
                )

        user_ids = [vec.user_id for vec in request.vectors]
        embeddings = np.array(
            [vec.embedding for vec in request.vectors], dtype=np.float32
        )

        # 정규화
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # 영벡터 방지
        zero_norm_mask = norms.squeeze() == 0
        if np.any(zero_norm_mask):
            raise ValueError(
                f"Zero vectors are not allowed. Found zero vectors for users: "
                f"{[user_ids[i] for i in np.where(zero_norm_mask)[0]]}"
            )

        embeddings = embeddings / norms

        # FAISS 인덱스 생성 및 추가
        index = faiss.IndexFlatIP(vector_dim)
        index.add(embeddings)

        self._artifacts = _IndexArtifacts(
            index=index,
            user_ids=user_ids,
            embeddings=embeddings,
        )

        logger.info(
            "Built FAISS index with %s users and vector dimension %s",
            len(user_ids),
            vector_dim,
        )

        return IndexCreateResponse(num_users=len(user_ids), vector_dimension=vector_dim)

    def get_similar_users(
        self, user_id: str, diner_scores: List[float], top_k: int
    ) -> SimilarUsersResponse:
        """입력받은 사용자 ID와 점수 벡터를 기반으로 FAISS 인덱스에서 유사 사용자 검색"""
        artifacts = self._ensure_index()

        # 입력 점수를 numpy 배열로 변환
        query_scores = np.array(diner_scores, dtype=np.float32)

        # 인덱스의 차원과 일치하는지 확인
        if len(query_scores) != artifacts.index.d:
            raise ValueError(
                f"Input diner_scores dimension ({len(query_scores)}) does not match "
                f"index dimension ({artifacts.index.d})"
            )

        # 정규화 (인덱스에 저장된 임베딩과 동일한 방식)
        norm = np.linalg.norm(query_scores)
        if norm == 0:
            raise ValueError("Input diner_scores vector cannot be zero vector")
        query_vec = (query_scores / norm).reshape(1, -1)

        # FAISS 검색
        search_scores, indices = artifacts.index.search(
            query_vec, min(top_k + 1, len(artifacts.user_ids))
        )

        # top_k개 반환
        neighbors = [
            {"user_id": artifacts.user_ids[idx], "score": float(score)}
            for idx, score in zip(indices[0], search_scores[0])
        ][:top_k]

        return SimilarUsersResponse(query_user_id=user_id, neighbors=neighbors)

    def _ensure_index(self) -> _IndexArtifacts:
        if self._artifacts is None:
            raise RuntimeError(
                "FAISS index is not initialized. call build_index first."
            )
        return self._artifacts
