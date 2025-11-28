import logging

from fastapi import APIRouter, status

from app.schemas.recommendation import (
    PersonalRecRequest,
    PersonalRecResponse,
    UserCFRequest,
    UserCFResponse,
)
from app.services.recommendation_service import RecommendationService

router = APIRouter()
recommendation_service = RecommendationService()


@router.post(
    "/user/similar",
    response_model=UserCFResponse,
    status_code=status.HTTP_200_OK,
    summary="Get most similar reviewer_id using user_cf",
)
async def get_most_similar_user(request: UserCFRequest):
    """
    Find most similar user using User Based CF.
    """
    logging.info(
        f"Request data - liked_diner_ids: {request.liked_diner_ids}, scores: {request.scores_of_liked_diner_ids}"
    )
    most_similar_reviewer_id = (
        recommendation_service.get_most_similar_reviewer_with_user_cf(
            liked_diner_ids=request.liked_diner_ids,
            scores_of_liked_diner_ids=request.scores_of_liked_diner_ids,
        )
    )
    return UserCFResponse(reviewer_id=most_similar_reviewer_id)


@router.post(
    "/personal",
    response_model=PersonalRecResponse,
    status_code=status.HTTP_200_OK,
    summary="Rank diner_ids using trained embeddings",
)
async def get_personalized_ranked_diners(request: PersonalRecRequest):
    """
    Given list of diner_ids, rank them by dot product btw user and diner embeddings.
    """
    logging.info(
        f"Request data - firebase_uid: {request.firebase_uid}, diner_ids: {request.diner_ids[:10]}"
    )
    diner_ids, scores = recommendation_service.get_personalized_ranked_diners(
        firebase_uid=request.firebase_uid,
        diner_ids=request.diner_ids,
    )
    return PersonalRecResponse(diner_ids=diner_ids, scores=scores)
