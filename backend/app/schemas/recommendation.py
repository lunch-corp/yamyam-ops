from pydantic import BaseModel, Field


class UserCFRequest(BaseModel):
    liked_diner_ids: list[int] = Field(
        ...,
        description="List of diner ids which user gave when initial taste discovery",
    )
    scores_of_liked_diner_ids: list[int] = Field(
        ..., description="List of scores which user gave when initial taste discovery"
    )


class UserCFResponse(BaseModel):
    reviewer_id: int = Field(
        ..., description="Reviewer id in kakao review data matched by user cf"
    )
