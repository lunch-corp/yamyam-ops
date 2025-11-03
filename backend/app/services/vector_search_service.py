"""
벡터 유사도 검색 서비스
FAISS를 사용한 User-to-User 및 Item-to-Item 검색
"""

import logging
import os
import pickle
from typing import List, Optional, Tuple

import faiss
import numpy as np

from app.core.db import db

logger = logging.getLogger(__name__)


class VectorSearchService:
    """FAISS 기반 벡터 유사도 검색 서비스"""

    def __init__(self, dimension: int = 128, index_type: str = "flat"):
        """
        Args:
            dimension: 벡터 차원 (기본값: 128)
            index_type: 인덱스 타입 ("flat", "ivf", "hnsw")
        """
        self.dimension = dimension
        self.index_type = index_type
        self.indexes: dict = {}  # {entity_type: faiss_index}
        self.index_path = os.getenv("FAISS_INDEX_PATH", "./faiss_indices")

        # 인덱스 디렉토리 생성
        os.makedirs(self.index_path, exist_ok=True)

    def _create_index(self, entity_type: str) -> faiss.Index:
        """FAISS 인덱스 생성"""
        if entity_type not in self.indexes:
            if self.index_type == "flat":
                # L2 거리 기반 평면 인덱스 (정확도 높음, 느림)
                index = faiss.IndexFlatL2(self.dimension)
            elif self.index_type == "ivf":
                # IVF 인덱스 (속도-정확도 균형)
                quantizer = faiss.IndexFlatL2(self.dimension)
                index = faiss.IndexIVFFlat(quantizer, self.dimension, 100)
            elif self.index_type == "hnsw":
                # HNSW 인덱스 (빠르고 정확)
                index = faiss.IndexHNSWFlat(self.dimension, 32)
            else:
                raise ValueError(f"Unknown index type: {self.index_type}")

            self.indexes[entity_type] = index
            logger.info(f"Created {self.index_type} index for {entity_type}")

        return self.indexes[entity_type]

    def _get_index_path(self, entity_type: str) -> str:
        """인덱스 파일 경로 반환"""
        return os.path.join(self.index_path, f"{entity_type}_index.faiss")

    def load_index(self, entity_type: str) -> bool:
        """저장된 인덱스 로드"""
        try:
            index_path = self._get_index_path(entity_type)
            if not os.path.exists(index_path):
                logger.warning(f"Index file not found: {index_path}")
                self._create_index(entity_type)
                return True

            index = faiss.read_index(index_path)
            self.indexes[entity_type] = index
            logger.info(f"Loaded {entity_type} index with {index.ntotal} vectors")
            return True
        except Exception as e:
            logger.error(f"Error loading index for {entity_type}: {e}")
            return False

    def save_index(self, entity_type: str) -> bool:
        """인덱스 저장"""
        try:
            if entity_type not in self.indexes:
                logger.warning(f"No index found for {entity_type}")
                return False

            index_path = self._get_index_path(entity_type)
            faiss.write_index(self.indexes[entity_type], index_path)
            logger.info(f"Saved {entity_type} index to {index_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving index for {entity_type}: {e}")
            return False

    def add_vectors(
        self,
        entity_type: str,
        entity_ids: List[str],
        vectors: np.ndarray,
    ) -> bool:
        """
        벡터를 인덱스에 추가

        Args:
            entity_type: 엔티티 타입 ("user", "item")
            entity_ids: 엔티티 ID 리스트
            vectors: 벡터 배열 (n x dimension)

        Returns:
            성공 여부
        """
        try:
            vectors = vectors.astype("float32")

            # 인덱스가 없으면 생성
            if entity_type not in self.indexes:
                self._create_index(entity_type)

            index = self.indexes[entity_type]

            # IVF 인덱스의 경우 트레이닝 필요
            if isinstance(index, faiss.IndexIVFFlat) and not index.is_trained:
                logger.info("Training IVF index...")
                index.train(vectors)

            # 벡터 추가
            index.add(vectors)
            logger.info(
                f"Added {len(vectors)} vectors to {entity_type} index (total: {index.ntotal})"
            )

            # ID 매핑 저장
            self._save_id_mapping(entity_type, entity_ids)

            # 인덱스 저장
            self.save_index(entity_type)

            return True

        except Exception as e:
            logger.error(f"Error adding vectors: {e}")
            return False

    def _save_id_mapping(self, entity_type: str, entity_ids: List[str]):
        """ID 매핑 저장 (인덱스 위치 -> 엔티티 ID)"""
        try:
            mapping_path = os.path.join(self.index_path, f"{entity_type}_mapping.pkl")
            with open(mapping_path, "wb") as f:
                pickle.dump(entity_ids, f)
            logger.debug(f"Saved ID mapping for {entity_type}")
        except Exception as e:
            logger.error(f"Error saving ID mapping: {e}")

    def _load_id_mapping(self, entity_type: str) -> Optional[List[str]]:
        """ID 매핑 로드"""
        try:
            mapping_path = os.path.join(self.index_path, f"{entity_type}_mapping.pkl")
            if not os.path.exists(mapping_path):
                return None

            with open(mapping_path, "rb") as f:
                mapping = pickle.load(f)
            return mapping
        except Exception as e:
            logger.error(f"Error loading ID mapping: {e}")
            return None

    def search(
        self, entity_type: str, query_vector: np.ndarray, k: int = 10
    ) -> List[Tuple[str, float]]:
        """
        유사한 벡터 검색

        Args:
            entity_type: 엔티티 타입 ("user", "item")
            query_vector: 쿼리 벡터 (dimension,)
            k: 반환할 개수

        Returns:
            [(entity_id, distance), ...] 리스트
        """
        try:
            if entity_type not in self.indexes:
                logger.warning(f"No index found for {entity_type}")
                return []

            index = self.indexes[entity_type]
            query_vector = query_vector.astype("float32").reshape(1, -1)

            # k가 실제 벡터 수보다 크면 조정
            k = min(k, index.ntotal)

            # 검색
            distances, indices = index.search(query_vector, k)

            # ID 매핑 로드
            id_mapping = self._load_id_mapping(entity_type)
            if id_mapping is None:
                logger.error(f"No ID mapping found for {entity_type}")
                return []

            # 결과 반환
            results = []
            for idx, dist in zip(indices[0], distances[0]):
                if idx != -1:  # FAISS가 -1을 유효하지 않은 결과로 반환
                    entity_id = id_mapping[idx]
                    results.append((entity_id, float(dist)))

            return results

        except Exception as e:
            logger.error(f"Error searching: {e}")
            return []

    def get_user_embedding(self, user_id: str) -> Optional[np.ndarray]:
        """사용자 임베딩 벡터 조회"""
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    """
                    SELECT vector_data
                    FROM embedding_vectors
                    WHERE entity_type = 'user' AND entity_id = %s
                    AND embedding_type = 'default'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (user_id,),
                )
                result = cursor.fetchone()
                if not result:
                    return None

                vector_data = result["vector_data"]

                # 바이너리 데이터를 numpy 배열로 변환
                vector = np.frombuffer(vector_data, dtype=np.float32).reshape(-1)
                return vector

        except Exception as e:
            logger.error(f"Error getting user embedding: {e}")
            return None

    def get_item_embedding(self, item_id: str) -> Optional[np.ndarray]:
        """아이템 임베딩 벡터 조회"""
        try:
            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    """
                    SELECT vector_data
                    FROM embedding_vectors
                    WHERE entity_type = 'item' AND entity_id = %s
                    AND embedding_type = 'default'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (item_id,),
                )
                result = cursor.fetchone()
                if not result:
                    return None

                vector_data = result["vector_data"]

                # 바이너리 데이터를 numpy 배열로 변환
                vector = np.frombuffer(vector_data, dtype=np.float32).reshape(-1)
                return vector

        except Exception as e:
            logger.error(f"Error getting item embedding: {e}")
            return None

    def rebuild_index(self, entity_type: str) -> bool:
        """인덱스 재구축"""
        try:
            # DB에서 모든 벡터 조회
            with db.get_cursor() as (cursor, conn):
                cursor.execute(
                    """
                    SELECT entity_id, vector_data, dimension
                    FROM embedding_vectors
                    WHERE entity_type = %s
                    ORDER BY entity_id
                    """,
                    (entity_type,),
                )
                results = cursor.fetchall()

            if not results:
                logger.warning(f"No vectors found for {entity_type}")
                return False

            # 벡터와 ID 분리
            entity_ids = []
            vectors = []

            for row in results:
                entity_ids.append(row["entity_id"])
                vector = np.frombuffer(row["vector_data"], dtype=np.float32)
                vectors.append(vector)

            vectors = np.array(vectors)

            # 기존 인덱스 제거하고 새로 생성
            if entity_type in self.indexes:
                del self.indexes[entity_type]

            self._create_index(entity_type)
            return self.add_vectors(entity_type, entity_ids, vectors)

        except Exception as e:
            logger.error(f"Error rebuilding index: {e}")
            return False


# 전역 벡터 검색 서비스 인스턴스
vector_search_service = VectorSearchService()
