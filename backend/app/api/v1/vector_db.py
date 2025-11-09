import logging

from fastapi import APIRouter, HTTPException

from app.schemas.vector_db import (
    StoreVectorsRequest,
    StoreVectorsResponse,
    SimilarRequest,
    SimilarResponse,
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
        response = vector_db_service.store_vectors(
            vector_type=request.vector_type,
            vectors=request.vectors,
            normalize=request.normalize,
        )
        logger.info(
            "Updated FAISS index for %s. Total ids: %s, vector dimension: %s",
            request.vector_type.value,
            response.num_vectors,
            response.vector_dimension,
        )
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/similar", response_model=SimilarResponse, summary="내적 기반 검색")
def get_similar(payload: SimilarRequest) -> SimilarResponse:
    """
    입력받은 ID와 점수 벡터를 기반으로 FAISS 인덱스에서 내적 기반 유사 벡터 검색합니다.
    점수 벡터의 차원이 인덱스 차원과 일치하지 않으면 400을 반환합니다.
    """
    try:
        return vector_db_service.get_similar(
            payload.vector_type,
            payload.query_id,
            payload.query_vector,
            payload.top_k,
            payload.filtering_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
