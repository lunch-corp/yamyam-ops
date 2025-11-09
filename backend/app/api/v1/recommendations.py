import logging

from fastapi import APIRouter, HTTPException

from app.schemas.recommendation import (
    DummyIndexConfig,
    DummyIndexStatus,
    SimilarUsersRequest,
    SimilarUsersResponse,
)
from app.services.recommendation_service import DummyUserCFService

router = APIRouter()
logger = logging.getLogger(__name__)

cf_service = DummyUserCFService()


@router.post(
    "/dummy/index",
    response_model=DummyIndexStatus,
    summary="더미 사용자 FAISS 인덱스 재생성",
)
def rebuild_dummy_index(config: DummyIndexConfig) -> DummyIndexStatus:
    """랜덤 더미 사용자-다이너 상호작용을 기반으로 새로운 FAISS 인덱스를 생성합니다."""
    status = cf_service.build_index(config)
    logger.info(
        "Rebuilt dummy FAISS index with %s users and %s diners",
        status.num_users,
        status.num_diners,
    )
    return status


@router.post(
    "/dummy/similar-users",
    response_model=SimilarUsersResponse,
    summary="유사 사용자 검색",
)
def get_similar_users(payload: SimilarUsersRequest) -> SimilarUsersResponse:
    """
    입력받은 사용자 점수 벡터를 기반으로 FAISS 인덱스에서 유사한 사용자들을 검색합니다.
    점수 벡터의 차원이 인덱스 차원과 일치하지 않으면 400을 반환합니다.
    """
    try:
        return cf_service.get_similar_users(payload.scores, payload.top_k)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
