import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.recommendation import (
    InitModelResponse,
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


@router.post(
    "/init",
    response_model=InitModelResponse,
    status_code=status.HTTP_200_OK,
    summary="Initialize user_cf model with CSV files",
)
async def initialize_user_cf(
    review_csv: UploadFile = File(..., description="review.csv file"),
    diner_csv: UploadFile = File(..., description="diner.csv file"),
    reviewer_csv: UploadFile = File(..., description="reviewer.csv file"),
    diner_category_csv: UploadFile = File(..., description="diner_category.csv file"),
):
    """
    Initialize user_cf model by uploading CSV files.
    If already initialized, this endpoint does nothing.
    """
    if recommendation_service.is_initialized:
        logging.info("Model already initialized, skipping initialization")
        return InitModelResponse(message="Model already initialized", status="skipped")

    try:
        # Initialize model with file objects directly
        recommendation_service._init_models(
            review_csv_file=review_csv.file,
            diner_csv_file=diner_csv.file,
            reviewer_csv_file=reviewer_csv.file,
            diner_category_csv_file=diner_category_csv.file,
        )

        return InitModelResponse(
            message="Successfully initialized user_cf model", status="success"
        )

    except Exception as e:
        logging.error(f"Failed to initialize model: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to initialize model: {str(e)}",
        )
