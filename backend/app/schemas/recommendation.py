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


class PersonalRecRequest(BaseModel):
    firebase_uid: str = Field(..., description="Unique id from firebase")
    diner_ids: list[int] = Field(
        ...,
        description="List of diner ids after first filtering",
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "firebase_uid": "643UVNQPFFVZXjgRULFjaDMztLE2",
                    "diner_ids": [2000734287, 12386670, 8431628],
                }
            ]
        }
    }


class PersonalRecResponse(BaseModel):
    diner_ids: list[int] = Field(
        ...,
        description="List of ranked diner ids after dot product embeddings",
    )
    scores: list[float] = Field(
        ...,
        description="List of scores related to each diner_id",
    )
