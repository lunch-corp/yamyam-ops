from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import List

import faiss
import numpy as np

from app.schemas.recommendation import (
    DummyIndexConfig,
    DummyIndexStatus,
    SimilarUsersResponse,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _IndexArtifacts:
    index: faiss.IndexFlatIP
    user_ids: List[str]
    embeddings: np.ndarray


class DummyUserCFService:
    """간단한 더미 사용자 기반 CF + FAISS 검색 서비스"""

    def __init__(self) -> None:
        self._artifacts: _IndexArtifacts | None = None
        self.build_index(DummyIndexConfig(num_users=10, num_diners=20, random_seed=42))

    def build_index(self, config: DummyIndexConfig) -> DummyIndexStatus:
        """더미 사용자-다이너 상호작용으로부터 FAISS 인덱스 생성"""
        logger.info(
            "Building FAISS dummy index with num_users=%s num_diners=%s seed=%s",
            config.num_users,
            config.num_diners,
            config.random_seed,
        )

        rng = np.random.default_rng(config.random_seed)
        user_ids = [f"user_{i:04d}" for i in range(config.num_users)]

        # 랜덤 상호작용 행렬 생성 (0~5 사이의 평점 값)
        interactions = rng.integers(
            low=0, high=6, size=(config.num_users, config.num_diners), dtype=np.int32
        )

        # float32로 변환 후 정규화하여 임베딩으로 사용
        embeddings = interactions.astype("float32")
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        # 영벡터 방지: 노름이 0인 경우 난수로 치환
        zero_norm_mask = norms.squeeze() == 0
        if np.any(zero_norm_mask):
            embeddings[zero_norm_mask] = rng.normal(
                size=(zero_norm_mask.sum(), config.num_diners)
            )
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True)

        embeddings = embeddings / norms

        index = faiss.IndexFlatIP(config.num_diners)
        index.add(embeddings)

        self._artifacts = _IndexArtifacts(
            index=index,
            user_ids=user_ids,
            embeddings=embeddings,
        )

        return DummyIndexStatus(num_users=len(user_ids), num_diners=config.num_diners)

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
