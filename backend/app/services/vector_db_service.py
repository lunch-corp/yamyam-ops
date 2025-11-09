from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Dict, List

import faiss
import numpy as np

from app.schemas.vector_db import (
    Vector,
    VectorType,
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
        self._artifacts: Dict[VectorType, _IndexArtifacts] = {}

    def get_similar(
        self,
        vector_type: VectorType,
        query_id: str,
        diner_scores: List[float],
        top_k: int,
        filtering_ids: List[str] = None,
    ) -> SimilarResponse:
        """입력받은 ID와 점수 벡터를 기반으로 FAISS 인덱스에서 내적 기반 유사 벡터 검색"""
        artifacts = self._ensure_index(vector_type)

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
        filtering_set = set(filtering_ids) if filtering_ids else set()
        search_k = min(top_k + 1, len(artifacts.ids))
        search_scores, indices = artifacts.index.search(query_vec, search_k)

        # top_k개 반환 (필터링 적용)
        neighbors = []
        for idx, score in zip(indices[0], search_scores[0]):
            vec_id = artifacts.ids[idx]
            if vec_id not in filtering_set:
                neighbors.append({"id": vec_id, "score": float(score)})
                if len(neighbors) >= top_k:
                    break

        return SimilarResponse(query_id=query_id, neighbors=neighbors)

    def store_vectors(
        self, vector_type: VectorType, vectors: List[Vector], normalize: bool
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
        if vector_type in self._artifacts:
            artifacts = self._artifacts[vector_type]
            if dimension != artifacts.index.d:
                raise ValueError(
                    f"Vector dimension {dimension} does not match index dimension {artifacts.index.d}"
                )
            artifacts.index.add(vectors)
            artifacts.ids.extend(ids)
            # Update embeddings by concatenating
            artifacts.embeddings = np.vstack([artifacts.embeddings, vectors])
        else:
            # Create new index if doesn't exist
            index = faiss.IndexFlatIP(dimension)
            index.add(vectors)
            self._artifacts[vector_type] = _IndexArtifacts(
                index=index,
                ids=ids,
                embeddings=vectors,
            )

        logger.info(
            "Updated FAISS index for %s. Total ids: %s, vector dimension: %s",
            vector_type.value,
            len(self._artifacts[vector_type].ids),
            dimension,
        )

        return StoreVectorsResponse(
            num_vectors=len(self._artifacts[vector_type].ids),
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

    def _ensure_index(self, vector_type: VectorType) -> _IndexArtifacts:
        if vector_type not in self._artifacts:
            raise RuntimeError(
                f"FAISS index for {vector_type.value} is not initialized. call build_index first."
            )
        return self._artifacts[vector_type]
