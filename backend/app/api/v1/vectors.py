"""
벡터 검색 및 임베딩 관리 API
User-to-User, Item-to-Item 유사도 검색 제공
"""

import logging

import numpy as np
from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_firebase_uid
from app.schemas.vector import (
    EmbeddingVectorCreate,
    EmbeddingVectorResponse,
    IndexRebuildResponse,
    SimilaritySearchRequest,
    VectorSearchResults,
)
from app.services.vector_search_service import vector_search_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post(
    "/embeddings",
    response_model=EmbeddingVectorResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["vectors"],
    summary="임베딩 벡터 저장",
)
def create_embedding(
    embedding: EmbeddingVectorCreate,
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    임베딩 벡터를 데이터베이스에 저장

    - 벡터는 binary 형태로 저장됩니다
    - 동일한 엔티티에 대해 여러 임베딩을 저장할 수 있습니다
    """
    from app.core.db import db
    from app.utils.ulid_utils import generate_ulid

    try:
        # 차원 검증
        if len(embedding.vector) != embedding.dimension:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Vector dimension mismatch: expected {embedding.dimension}, got {len(embedding.vector)}",
            )

        # 벡터를 numpy 배열로 변환
        vector_array = np.array(embedding.vector, dtype=np.float32)
        vector_binary = vector_array.tobytes()

        # 데이터베이스에 저장
        with db.get_cursor() as (cursor, conn):
            cursor.execute(
                """
                INSERT INTO embedding_vectors (id, entity_type, entity_id, embedding_type, dimension, vector_data)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, entity_type, entity_id, embedding_type, dimension
                """,
                (
                    generate_ulid(),
                    embedding.entity_type,
                    embedding.entity_id,
                    embedding.embedding_type,
                    embedding.dimension,
                    vector_binary,
                ),
            )
            result = cursor.fetchone()
            conn.commit()

            return EmbeddingVectorResponse(
                id=result["id"],
                entity_type=result["entity_type"],
                entity_id=result["entity_id"],
                embedding_type=result["embedding_type"],
                dimension=result["dimension"],
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating embedding: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create embedding",
        )


@router.post(
    "/similarity/search",
    response_model=VectorSearchResults,
    tags=["vectors"],
    summary="유사도 검색",
)
def similarity_search(request: SimilaritySearchRequest):
    """
    벡터 유사도 검색

    - 쿼리 벡터와 가장 유사한 엔티티들을 반환합니다
    - 거리(distance)와 유사도(similarity) 점수를 제공합니다
    """
    try:
        # 벡터로 변환
        query_vector = np.array(request.query_vector, dtype=np.float32)

        # 검색
        results = vector_search_service.search(
            request.entity_type, query_vector, k=request.k
        )

        # 응답 생성
        search_results = []
        for entity_id, distance in results:
            # 유사도 = 1 - 정규화된 거리 (거리만으로도 충분)
            # 실제 비즈니스 로직에서는 이 부분을 조정할 수 있습니다
            similarity = max(0.0, 1.0 - distance / 100.0) if distance > 0 else 1.0

            search_results.append(
                {
                    "entity_id": entity_id,
                    "distance": distance,
                    "similarity": similarity,
                }
            )

        return VectorSearchResults(
            query_type=f"{request.entity_type}_similarity",
            total_results=len(search_results),
            results=search_results,
        )

    except Exception as e:
        logger.error(f"Error in similarity search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform similarity search",
        )


@router.post(
    "/similarity/users/{user_id}",
    response_model=VectorSearchResults,
    tags=["vectors"],
    summary="사용자 유사도 검색",
)
def search_similar_users(
    user_id: str,
    k: int = 10,
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    특정 사용자와 유사한 사용자 검색 (User-to-User)

    - 사용자의 임베딩 벡터를 조회하여 유사한 사용자들을 찾습니다
    """
    try:
        # 사용자 임베딩 조회
        user_vector = vector_search_service.get_user_embedding(user_id)
        if user_vector is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No embedding found for user: {user_id}",
            )

        # 검색 (자기 자신 제외)
        results = vector_search_service.search("user", user_vector, k=k + 1)

        # 자기 자신 제외
        filtered_results = [
            (entity_id, distance)
            for entity_id, distance in results
            if entity_id != user_id
        ][:k]

        # 응답 생성
        search_results = []
        for entity_id, distance in filtered_results:
            similarity = max(0.0, 1.0 - distance / 100.0) if distance > 0 else 1.0
            search_results.append(
                {
                    "entity_id": entity_id,
                    "distance": distance,
                    "similarity": similarity,
                }
            )

        return VectorSearchResults(
            query_type="user2user",
            total_results=len(search_results),
            results=search_results,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in user similarity search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform user similarity search",
        )


@router.post(
    "/similarity/items/{item_id}",
    response_model=VectorSearchResults,
    tags=["vectors"],
    summary="아이템 유사도 검색",
)
def search_similar_items(
    item_id: str,
    k: int = 10,
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    특정 아이템과 유사한 아이템 검색 (Item-to-Item)

    - 아이템의 임베딩 벡터를 조회하여 유사한 아이템들을 찾습니다
    """
    try:
        # 아이템 임베딩 조회
        item_vector = vector_search_service.get_item_embedding(item_id)
        if item_vector is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No embedding found for item: {item_id}",
            )

        # 검색 (자기 자신 제외)
        results = vector_search_service.search("item", item_vector, k=k + 1)

        # 자기 자신 제외
        filtered_results = [
            (entity_id, distance)
            for entity_id, distance in results
            if entity_id != item_id
        ][:k]

        # 응답 생성
        search_results = []
        for entity_id, distance in filtered_results:
            similarity = max(0.0, 1.0 - distance / 100.0) if distance > 0 else 1.0
            search_results.append(
                {
                    "entity_id": entity_id,
                    "distance": distance,
                    "similarity": similarity,
                }
            )

        return VectorSearchResults(
            query_type="item2item",
            total_results=len(search_results),
            results=search_results,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in item similarity search: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to perform item similarity search",
        )


@router.post(
    "/indexes/{entity_type}/rebuild",
    response_model=IndexRebuildResponse,
    tags=["vectors"],
    summary="인덱스 재구축",
)
def rebuild_index(
    entity_type: str,
    firebase_uid: str = Depends(get_firebase_uid),
):
    """
    FAISS 인덱스 재구축

    - 데이터베이스의 모든 벡터를 기반으로 인덱스를 재구축합니다
    - 벡터가 추가/수정/삭제된 후 실행해야 합니다
    """
    try:
        success = vector_search_service.rebuild_index(entity_type)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to rebuild index",
            )

        # 재구축된 인덱스의 벡터 개수 조회
        total_vectors = 0
        if entity_type in vector_search_service.indexes:
            total_vectors = vector_search_service.indexes[entity_type].ntotal

        return IndexRebuildResponse(
            entity_type=entity_type,
            status="success",
            total_vectors=total_vectors,
            message=f"Index rebuilt successfully with {total_vectors} vectors",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rebuilding index: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to rebuild index",
        )


@router.get(
    "/indexes/{entity_type}/info",
    tags=["vectors"],
    summary="인덱스 정보 조회",
)
def get_index_info(entity_type: str):
    """
    FAISS 인덱스 정보 조회

    - 인덱스에 저장된 벡터 개수와 상태를 반환합니다
    """
    try:
        # 인덱스 로드 시도
        vector_search_service.load_index(entity_type)

        if entity_type not in vector_search_service.indexes:
            return {
                "entity_type": entity_type,
                "status": "not_found",
                "total_vectors": 0,
            }

        index = vector_search_service.indexes[entity_type]
        return {
            "entity_type": entity_type,
            "status": "active",
            "total_vectors": index.ntotal,
            "dimension": index.d,
            "is_trained": getattr(index, "is_trained", True),
        }

    except Exception as e:
        logger.error(f"Error getting index info: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get index info",
        )
