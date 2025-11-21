import logging

from fastapi import APIRouter, Query

from app.schemas.kakao_reviewer import (
    KakaoReviewerCreate,
    KakaoReviewerResponse,
    KakaoReviewerUpdate,
)
from app.services.kakao_reviewer_service import KakaoReviewerService

router = APIRouter()
logger = logging.getLogger(__name__)

# 서비스 인스턴스 생성
reviewer_service = KakaoReviewerService()


@router.post(
    "/",
    response_model=KakaoReviewerResponse,
    tags=["kakao-reviewers"],
    summary="카카오 리뷰어 등록",
)
def create_reviewer(reviewer: KakaoReviewerCreate):
    """카카오 리뷰어 등록"""
    return reviewer_service.create(reviewer)


@router.get(
    "/",
    response_model=list[KakaoReviewerResponse],
    tags=["kakao-reviewers"],
    summary="카카오 리뷰어 목록 조회",
)
def list_reviewers(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    min_review_count: int | None = None,
    is_verified: bool | None = None,
):
    """카카오 리뷰어 목록 조회"""
    return reviewer_service.get_list(
        skip=skip,
        limit=limit,
        min_review_count=min_review_count,
        is_verified=is_verified,
    )


@router.get(
    "/{reviewer_id}",
    response_model=KakaoReviewerResponse,
    tags=["kakao-reviewers"],
    summary="카카오 리뷰어 상세 조회",
)
def get_reviewer(reviewer_id: int):
    """특정 카카오 리뷰어 상세 조회"""
    return reviewer_service.get_by_id(reviewer_id)


@router.put(
    "/{reviewer_id}",
    response_model=KakaoReviewerResponse,
    tags=["kakao-reviewers"],
    summary="카카오 리뷰어 수정",
)
def update_reviewer(reviewer_id: int, reviewer_update: KakaoReviewerUpdate):
    """카카오 리뷰어 정보 수정"""
    return reviewer_service.update(reviewer_id, reviewer_update)


@router.delete("/{reviewer_id}", tags=["kakao-reviewers"], summary="카카오 리뷰어 삭제")
def delete_reviewer(reviewer_id: int):
    """카카오 리뷰어 삭제"""
    return reviewer_service.delete(reviewer_id)
