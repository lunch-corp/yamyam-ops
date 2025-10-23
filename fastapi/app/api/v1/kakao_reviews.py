import logging
from typing import List, Optional

from app.schemas.kakao_review import (
    KakaoReviewCreate,
    KakaoReviewResponse,
    KakaoReviewUpdate,
    KakaoReviewWithDetails,
)
from app.services.kakao_review_service import KakaoReviewService
from fastapi import APIRouter, Query

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
    kakao_place_id: Optional[str] = None,
    kakao_user_id: Optional[str] = None,
    min_rating: Optional[int] = None,
):
    """카카오 리뷰 목록 조회"""
    return review_service.get_list(
        skip=skip,
        limit=limit,
        kakao_place_id=kakao_place_id,
        kakao_user_id=kakao_user_id,
        min_rating=min_rating,
    )


@router.get(
    "/{kakao_review_id}",
    response_model=KakaoReviewWithDetails,
    tags=["kakao-reviews"],
    summary="카카오 리뷰 상세 조회",
)
def get_review(kakao_review_id: str):
    """특정 카카오 리뷰 상세 조회"""
    return review_service.get_by_id(kakao_review_id)


@router.put(
    "/{kakao_review_id}",
    response_model=KakaoReviewResponse,
    tags=["kakao-reviews"],
    summary="카카오 리뷰 수정",
)
def update_review(kakao_review_id: str, review_update: KakaoReviewUpdate):
    """카카오 리뷰 수정"""
    return review_service.update(kakao_review_id, review_update)


@router.delete("/{kakao_review_id}", tags=["kakao-reviews"], summary="카카오 리뷰 삭제")
def delete_review(kakao_review_id: str):
    """카카오 리뷰 삭제"""
    return review_service.delete(kakao_review_id)
