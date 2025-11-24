import logging

from fastapi import APIRouter, status

from app.schemas.recommendation import UserCFRequest, UserCFResponse
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

    Args from Request Body:
        liked_diner_ids (List[int]): List of diner_ids which what2eat users gave ratings.
        scores_of_liked_diner_ids (List[int]): List of scores related with `liked_diner_ids`.

    Returns in Response Body:
        most_similar_reviewer_id (int): Reviewer id using User Based CF.
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
