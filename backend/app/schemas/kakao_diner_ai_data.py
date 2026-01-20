"""
카카오 음식점 AI 데이터 스키마
"""

from datetime import datetime

from pydantic import BaseModel, Field


class KakaoDinerAIDataCreate(BaseModel):
    """AI 데이터 생성 스키마"""

    diner_idx: int = Field(..., description="음식점 고유 인덱스")
    ai_bottom_sheet_title: str | None = Field(None, description="AI 생성 제목")
    ai_bottom_sheet_summary: str | None = Field(None, description="AI 생성 요약")
    ai_bottom_sheet_sheets: dict | list | None = Field(
        None, description="AI 생성 시트 데이터 (JSONB)"
    )
    ai_bottom_sheet_landing_url: str | None = Field(None, description="랜딩 URL")
    blog_summaries: dict | list | None = Field(
        None, description="블로그 요약 데이터 (JSONB)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "diner_idx": 1994471601,
                "ai_bottom_sheet_title": "유럽 감성 가득한 여유로운 브런치 공간",
                "ai_bottom_sheet_summary": "감성적인 인테리어와 넓은 공간을 갖춘 브런치 카페로...",
                "ai_bottom_sheet_sheets": [
                    {
                        "title": "추천 메뉴",
                        "keywords": ["명란크림파스타", "페퍼로니피자"],
                        "ui_type": "KEYWORDS",
                    }
                ],
                "ai_bottom_sheet_landing_url": "https://kanana.kakao.com/place/redirect?entry=...",
                "blog_summaries": [
                    {"title": "분위기", "keywords": ["로컬 맛집", "정겨운 분위기"]}
                ],
            }
        }


class KakaoDinerAIDataUpdate(BaseModel):
    """AI 데이터 업데이트 스키마 (모든 필드 optional)"""

    diner_idx: int | None = Field(None, description="음식점 고유 인덱스")
    ai_bottom_sheet_title: str | None = Field(None, description="AI 생성 제목")
    ai_bottom_sheet_summary: str | None = Field(None, description="AI 생성 요약")
    ai_bottom_sheet_sheets: dict | list | None = Field(
        None, description="AI 생성 시트 데이터 (JSONB)"
    )
    ai_bottom_sheet_landing_url: str | None = Field(None, description="랜딩 URL")
    blog_summaries: dict | list | None = Field(
        None, description="블로그 요약 데이터 (JSONB)"
    )


class KakaoDinerAIDataResponse(BaseModel):
    """AI 데이터 응답 스키마"""

    id: str = Field(..., description="ULID")
    diner_idx: int = Field(..., description="음식점 고유 인덱스")
    ai_bottom_sheet_title: str | None = Field(None, description="AI 생성 제목")
    ai_bottom_sheet_summary: str | None = Field(None, description="AI 생성 요약")
    ai_bottom_sheet_sheets: dict | list | None = Field(
        None, description="AI 생성 시트 데이터 (JSONB)"
    )
    ai_bottom_sheet_landing_url: str | None = Field(None, description="랜딩 URL")
    blog_summaries: dict | list | None = Field(
        None, description="블로그 요약 데이터 (JSONB)"
    )
    all_keywords: str | None = Field(None, description="모든 keywords (검색용)")
    created_at: datetime = Field(..., description="생성 시각")
    updated_at: datetime = Field(..., description="수정 시각")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "01HQZX9Y7ZABCDEFGHIJKLMNOP",
                "diner_idx": 1994471601,
                "ai_bottom_sheet_title": "유럽 감성 가득한 여유로운 브런치 공간",
                "ai_bottom_sheet_summary": "감성적인 인테리어와 넓은 공간을 갖춘 브런치 카페로...",
                "ai_bottom_sheet_sheets": [
                    {
                        "title": "추천 메뉴",
                        "keywords": ["명란크림파스타", "페퍼로니피자"],
                        "ui_type": "KEYWORDS",
                    }
                ],
                "ai_bottom_sheet_landing_url": "https://kanana.kakao.com/place/redirect?entry=...",
                "blog_summaries": [
                    {"title": "분위기", "keywords": ["로컬 맛집", "정겨운 분위기"]}
                ],
                "all_keywords": "명란크림파스타 페퍼로니피자 로컬 맛집 정겨운 분위기",
                "created_at": "2024-01-01T00:00:00",
                "updated_at": "2024-01-01T00:00:00",
            }
        }
