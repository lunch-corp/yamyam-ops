import logging

from fastapi import APIRouter, HTTPException

from app.schemas.vector_db import (
    StoreVectorsRequest,
    StoreVectorsResponse,
    SimilarUsersRequest,
    SimilarUsersResponse,
)
from app.services.vector_db_service import VectorDBService

router = APIRouter()
logger = logging.getLogger(__name__)

vector_db_service = VectorDBService()


@router.post(
    "/store",
    response_model=StoreVectorsResponse,
    summary="FAISS 벡터 저장",
)
def store_vectors(request: StoreVectorsRequest) -> StoreVectorsResponse:
    """
    기존 FAISS 인덱스에 새로운 사용자 벡터 데이터를 추가합니다.
    인덱스가 존재하지 않으면 새로 생성합니다.
    """
    try:
        response = vector_db_service.store_vectors(request)
        logger.info(
            "Updated FAISS index. Total users: %s, vector dimension: %s",
            response.num_users,
            response.vector_dimension,
        )
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/similar", response_model=SimilarUsersResponse, summary="유사 사용자 검색"
)
def get_similar_users(payload: SimilarUsersRequest) -> SimilarUsersResponse:
    """
    입력받은 사용자 ID와 식당별 점수 벡터를 기반으로 FAISS 인덱스에서 유사한 사용자들을 검색합니다.
    점수 벡터의 차원이 인덱스 차원과 일치하지 않으면 400을 반환합니다.
    """
    try:
        return vector_db_service.get_similar_users(
            payload.user_id, payload.diner_scores, payload.top_k
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
