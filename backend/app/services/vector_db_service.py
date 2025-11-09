from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

import faiss
import numpy as np

from app.schemas.vector_db import (
    Vector,
    StoreVectorsResponse,
    SimilarResponse,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _IndexArtifacts:
    index: faiss.IndexFlatIP
    ids: List[str]
    embeddings: np.ndarray


class VectorDBService:
    """FAISS 벡터 데이터베이스 서비스"""

    def __init__(self) -> None:
        self._artifacts: _IndexArtifacts | None = None

    def get_similar(
        self, query_id: str, diner_scores: List[float], top_k: int
    ) -> SimilarResponse:
        """입력받은 ID와 점수 벡터를 기반으로 FAISS 인덱스에서 내적 기반 유사 벡터 검색"""
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
            query_vec, min(top_k + 1, len(artifacts.ids))
        )

        # top_k개 반환
        neighbors = [
            {"id": artifacts.ids[idx], "score": float(score)}
            for idx, score in zip(indices[0], search_scores[0])
        ][:top_k]

        return SimilarResponse(query_id=query_id, neighbors=neighbors)

    def store_vectors(
        self, vectors: List[Vector], normalize: bool
    ) -> StoreVectorsResponse:
        """
        Add new vectors to existing FAISS index or create if not exists.
        """
        if not vectors:
            raise ValueError("vectors cannot be empty")

        # Extract IDs and embeddings from Vector objects
        ids = [vec.id for vec in vectors]
        vectors = np.array([vec.embedding for vec in vectors], dtype=np.float32)

        if vectors.ndim != 2:
            raise ValueError("Vectors must be 2-dimensional")

        # 정규화
        if normalize:
            vectors = self._normalize_embeddings(vectors, ids)

        # If index exists, append; otherwise create new
        dimension = vectors.shape[1]
        if self._artifacts is not None:
            if dimension != self._artifacts.index.d:
                raise ValueError(
                    f"Vector dimension {dimension} does not match index dimension {self._artifacts.index.d}"
                )
            self._artifacts.index.add(vectors)
            self._artifacts.ids.extend(ids)
            # Update embeddings by concatenating
            self._artifacts.embeddings = np.vstack(
                [self._artifacts.embeddings, vectors]
            )
        else:
            # Create new index if doesn't exist
            index = faiss.IndexFlatIP(dimension)
            index.add(vectors)
            self._artifacts = _IndexArtifacts(
                index=index,
                ids=ids,
                embeddings=vectors,
            )

        logger.info(
            "Updated FAISS index. Total ids: %s, vector dimension: %s",
            len(ids),
            dimension,
        )

        return StoreVectorsResponse(
            num_vectors=len(ids),
            vector_dimension=dimension,
        )

    def _normalize_embeddings(
        self, embeddings: np.ndarray, ids: List[str]
    ) -> np.ndarray:
        """벡터 정규화 (L2 norm)"""
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)

        # 영벡터 방지
        zero_norm_mask = norms.squeeze() == 0
        if np.any(zero_norm_mask):
            raise ValueError(
                f"Zero vectors are not allowed. Found zero vectors for ids: "
                f"{[ids[i] for i in np.where(zero_norm_mask)[0]]}"
            )

        return embeddings / norms

    def _ensure_index(self) -> _IndexArtifacts:
        if self._artifacts is None:
            raise RuntimeError(
                "FAISS index is not initialized. call build_index first."
            )
        return self._artifacts
