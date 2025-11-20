import logging
from typing import List, Optional

from fastapi import APIRouter, Query

from app.schemas.kakao_review import (
    KakaoReviewCreate,
    KakaoReviewResponse,
    KakaoReviewUpdate,
    KakaoReviewWithDetails,
)
from app.services.kakao_review_service import KakaoReviewService

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
review_service = KakaoReviewService()


@router.post(
    "/",
    response_model=KakaoReviewResponse,
    tags=["kakao-reviews"],
    summary="카카오 리뷰 등록",
)
def create_review(review: KakaoReviewCreate):
    """카카오 리뷰 등록"""
    return review_service.create(review)


@router.get(
    "/",
    response_model=List[KakaoReviewWithDetails],
    tags=["kakao-reviews"],
    summary="카카오 리뷰 목록 조회",
)
def list_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    diner_idx: Optional[int] = None,
    reviewer_id: Optional[int] = None,
    min_rating: Optional[float] = None,
):
    """카카오 리뷰 목록 조회"""
    return review_service.get_list(
        skip=skip,
        limit=limit,
        diner_idx=diner_idx,
        reviewer_id=reviewer_id,
        min_rating=min_rating,
    )


@router.get(
    "/{review_id}",
    response_model=KakaoReviewWithDetails,
    tags=["kakao-reviews"],
    summary="카카오 리뷰 상세 조회",
)
def get_review(review_id: int):
    """특정 카카오 리뷰 상세 조회"""
    return review_service.get_by_id(review_id)


@router.put(
    "/{review_id}",
    response_model=KakaoReviewResponse,
    tags=["kakao-reviews"],
    summary="카카오 리뷰 수정",
)
def update_review(review_id: int, review_update: KakaoReviewUpdate):
    """카카오 리뷰 수정"""
    return review_service.update(review_id, review_update)


@router.delete("/{review_id}", tags=["kakao-reviews"], summary="카카오 리뷰 삭제")
def delete_review(review_id: int):
    """카카오 리뷰 삭제"""
    return review_service.delete(review_id)
