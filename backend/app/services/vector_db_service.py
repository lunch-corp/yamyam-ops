from __future__ import annotations

import logging
import os
import pickle
import tempfile
from dataclasses import dataclass

import faiss
import numpy as np
import paramiko
import torch
from yamyam_lab.model.graph.node2vec import Model as Node2Vec

from app.schemas.vector_db import (
    SearchVectorResponse,
    SimilarResponse,
    StoreVectorsResponse,
    Vector,
    VectorType,
)

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class _IndexArtifacts:
    index: faiss.IndexFlatIP
    ids: list[str]
    embeddings: np.ndarray


class VectorDBService:
    """FAISS 벡터 데이터베이스 서비스"""

    def __init__(self) -> None:
        self._artifacts: dict[VectorType, _IndexArtifacts] = {}
        self.node2vec_model: Node2Vec | None = None
        self.user_mapping: dict | None = None
        self.diner_mapping: dict | None = None

        # Load Node2Vec model and mappings from remote SSH server
        try:
            self._load_node2vec_artifacts()
            self._store_node2vec_embeddings()
        except Exception as e:
            logger.error(f"Failed to load Node2Vec artifacts: {e}")
            logger.warning("VectorDBService initialized without Node2Vec artifacts")

    def _download_remote_file(
        self, ssh_client: paramiko.SSHClient, remote_path: str, local_path: str
    ) -> None:
        """Download file from remote server via SFTP"""
        sftp = ssh_client.open_sftp()
        try:
            sftp.get(remote_path, local_path)
            logger.info(f"Downloaded {remote_path} to {local_path}")
        finally:
            sftp.close()

    def _create_ssh_client(
        self, host: str, port: int, user: str, password: str
    ) -> paramiko.SSHClient:
        """Create and connect SSH client"""
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
        )
        return ssh

    def _load_node2vec_artifacts(self) -> None:
        """Load Node2Vec model and data mappings from remote SSH server"""
        # Get environment variables
        remote_host = os.getenv("REMOTE_JSON_HOST")
        remote_port = int(os.getenv("REMOTE_JSON_PORT", "22"))
        remote_user = os.getenv("REMOTE_JSON_USER")
        remote_pass = os.getenv("REMOTE_JSON_PASS")
        remote_weight_path = os.getenv("REMOTE_N2V_WEIGHT_PATH")
        remote_util_path = os.getenv("REMOTE_N2V_UTIL_PATH")

        if not all(
            [
                remote_host,
                remote_user,
                remote_pass,
                remote_weight_path,
                remote_util_path,
            ]
        ):
            logger.warning(
                "Remote SSH configuration incomplete. Skipping Node2Vec artifacts loading."
            )
            return

        # Create temporary files
        with (
            tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as weight_tmp,
            tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as util_tmp,
        ):
            weight_path = weight_tmp.name
            util_path = util_tmp.name

        try:
            logger.info(
                f"Connecting to {remote_host}:{remote_port} to download Node2Vec artifacts..."
            )

            # Establish SSH connection
            ssh = self._create_ssh_client(
                remote_host, remote_port, remote_user, remote_pass
            )

            # Download weight file
            self._download_remote_file(ssh, remote_weight_path, weight_path)

            # Download util file
            self._download_remote_file(ssh, remote_util_path, util_path)

            ssh.close()

            # Load weight checkpoint
            logger.info("Loading Node2Vec model weights...")
            checkpoint = torch.load(weight_path, map_location="cpu")
            config = checkpoint["config"]
            config.inference = True  # inference mode, not training

            # Initialize Node2Vec model with config
            self.node2vec_model = Node2Vec(config=config)

            # Load model state
            self.node2vec_model.load_state_dict(checkpoint["model_state_dict"])
            self.node2vec_model.eval()

            logger.info("Node2Vec model loaded successfully")
            logger.info(
                f"Embedding size: {self.node2vec_model._embedding.weight.size()}"
            )

            # Load data_object.pkl
            logger.info("Loading data mappings...")
            with open(util_path, "rb") as f:
                data_object = pickle.load(f)

            self.diner_mapping = data_object.get("diner_mapping")
            # need to adjust mapped_id set when training node2vec
            self.user_mapping = {
                user_id: mapped_id - len(self.diner_mapping)
                for (user_id, mapped_id) in data_object.get("user_mapping").items()
            }

            logger.info(
                f"Data mappings loaded - Users: {len(self.user_mapping) if self.user_mapping else 0}, "
                f"Diners: {len(self.diner_mapping) if self.diner_mapping else 0}"
            )

            # check if number of user + number of diner = embedding dimension
            if len(self.diner_mapping) + len(
                self.user_mapping
            ) != self.node2vec_model._embedding.weight.size(0):
                raise ValueError("Dimension mismatch!")

            # sanity check for diner
            if len(self.diner_mapping) - 1 != max(self.diner_mapping.values()):
                raise ValueError("Number of diners and index are mismatch!")

            # sanity check for user
            if len(self.user_mapping) - 1 != max(self.user_mapping.values()):
                raise ValueError("Number of users and index are mismatch!")

            # separate diner/user embedding
            self.diner_embedding = self.node2vec_model._embedding.weight[
                : len(self.diner_mapping)
            ]
            self.user_embedding = self.node2vec_model._embedding.weight[
                len(self.diner_mapping) :
            ]

        except Exception as e:
            logger.error(f"Error loading Node2Vec artifacts: {e}")
            raise
        finally:
            # Clean up temporary files
            if os.path.exists(weight_path):
                os.unlink(weight_path)
            if os.path.exists(util_path):
                os.unlink(util_path)

    def _store_node2vec_embeddings(self) -> None:
        """Store Node2Vec embeddings into FAISS indices"""
        if (
            self.node2vec_model is None
            or self.user_mapping is None
            or self.diner_mapping is None
        ):
            logger.warning("Node2Vec artifacts not loaded. Skipping embedding storage.")
            return

        logger.info("Storing Node2Vec embeddings into FAISS indices...")

        # Store diner embeddings
        diner_count = self._store_embeddings(
            vector_type=VectorType.DINER_N2V_VEC,
            embeddings=self.diner_embedding,
            id_mapping=self.diner_mapping,
        )
        logger.info(f"Stored {diner_count} diner embeddings")

        # Store user embeddings
        user_count = self._store_embeddings(
            vector_type=VectorType.USER_N2V_VEC,
            embeddings=self.user_embedding,
            id_mapping=self.user_mapping,
        )
        logger.info(f"Stored {user_count} user embeddings")

    def _store_embeddings(
        self, vector_type: VectorType, embeddings: torch.Tensor, id_mapping: dict
    ) -> int:
        """Helper function to convert embeddings to vectors and store them"""
        vectors = []
        for entity_id, idx in id_mapping.items():
            embedding = embeddings[idx].detach().cpu().numpy().tolist()
            vectors.append(Vector(id=str(int(entity_id)), embedding=embedding))

        self.store_vectors(
            vector_type=vector_type,
            vectors=vectors,
            normalize=False,  # do not normalize embeddings
        )
        return len(vectors)

    def get_similar(
        self,
        vector_type: VectorType,
        query_id: str,
        query_vec: list[float],
        top_k: int = None,
        filtering_ids: list[str] = None,
        norm: bool = False,
    ) -> SimilarResponse:
        """입력받은 ID와 점수 벡터를 기반으로 FAISS 인덱스에서 내적 기반 유사 벡터 검색"""
        artifacts = self._ensure_index(vector_type)

        # 입력 점수를 numpy 배열로 변환
        query_vec = np.array(query_vec, dtype=np.float32)

        if query_vec.sum() == 0:
            raise ValueError("Input query vector cannot be zero vector")

        # 인덱스의 차원과 일치하는지 확인
        if len(query_vec) != artifacts.index.d:
            raise ValueError(
                f"Input query vector dimension ({len(query_vec)}) does not match "
                f"index dimension ({artifacts.index.d})"
            )

        # 정규화 (인덱스에 저장된 임베딩과 동일한 방식)
        if norm:
            query_vec = query_vec / np.linalg.norm(query_vec)

        # Apply filtering by creating a subset index
        if filtering_ids:
            filtering_set = set([str(id) for id in filtering_ids])

            # Get indices and embeddings for filtered IDs
            filtered_indices = [
                i for i, vid in enumerate(artifacts.ids) if vid in filtering_set
            ]

            if not filtered_indices:
                return SimilarResponse(query_id=query_id, neighbors=[])

            filtered_embeddings = artifacts.embeddings[filtered_indices]
            filtered_ids = [artifacts.ids[i] for i in filtered_indices]

            # Create temporary index for filtered vectors
            temp_index = faiss.IndexFlatIP(artifacts.index.d)
            temp_index.add(filtered_embeddings)

            # Search in filtered index
            query_vec = query_vec.reshape(1, -1)
            search_k = len(filtered_indices)
            search_scores, indices = temp_index.search(query_vec, search_k)

            # Map back to original IDs
            neighbors = []
            for idx, score in zip(indices[0], search_scores[0]):
                vec_id = filtered_ids[idx]
                neighbors.append({"id": vec_id, "score": float(score)})
        else:
            # Original search without filtering
            query_vec = query_vec.reshape(1, -1)
            search_k = min(top_k, len(artifacts.ids))
            search_scores, indices = artifacts.index.search(query_vec, search_k)

            neighbors = []
            for idx, score in zip(indices[0], search_scores[0]):
                vec_id = artifacts.ids[idx]
                neighbors.append({"id": vec_id, "score": float(score)})

        return SimilarResponse(query_id=query_id, neighbors=neighbors)

    def store_vectors(
        self, vector_type: VectorType, vectors: list[Vector], normalize: bool
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

    def search_vector(self, vector_type: VectorType, id: str) -> SearchVectorResponse:
        """Search for a vector by its ID and return the embedding"""
        artifacts = self._ensure_index(vector_type)

        try:
            # Find the index of the ID in the list
            idx = artifacts.ids.index(id)
        except ValueError:
            raise ValueError(
                f"ID '{id}' not found in {vector_type.value} index. "
                f"Available IDs: {len(artifacts.ids)}"
            )

        # Get the embedding at that index
        embedding = artifacts.embeddings[idx].tolist()

        return SearchVectorResponse(id=id, embedding=embedding, vector_type=vector_type)

    def _normalize_embeddings(
        self, embeddings: np.ndarray, ids: list[str]
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
