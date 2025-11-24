from pydantic import BaseModel, Field


class UserCFRequest(BaseModel):
    liked_diner_ids: list[int] = Field(
        ...,
        description="List of diner ids which user gave when initial taste discovery",
    )
    scores_of_liked_diner_ids: list[int] = Field(
        ..., description="List of scores which user gave when initial taste discovery"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "liked_diner_ids": [2000734287, 12386670, 8431628],
                    "scores_of_liked_diner_ids": [5, 4, 5],
                }
            ]
        }
    }


class UserCFResponse(BaseModel):
    reviewer_id: int = Field(
        ..., description="Reviewer id in kakao review data matched by user cf"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "reviewer_id": 3933744720,
                }
            ]
        }
    }
