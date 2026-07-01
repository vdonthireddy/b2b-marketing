from pydantic import BaseModel
from datetime import datetime


class StageItemResponse(BaseModel):
    id: str
    text: str
    position: int
    content_type: str | None = None

    model_config = {"from_attributes": True}


class StageResponse(BaseModel):
    id: str
    journey_id: str
    name: str
    description: str | None = None
    icon: str
    color: str
    position: int
    goals: list[StageItemResponse] = []
    touchpoints: list[StageItemResponse] = []
    content: list[StageItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JourneyCreate(BaseModel):
    name: str
    description: str | None = None


class JourneyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: str | None = None


class PersonaBasicResponse(BaseModel):
    id: str
    name: str
    role_title: str | None = None
    avatar_color: str

    model_config = {"from_attributes": True}


class CollaboratorResponse(BaseModel):
    user_id: str
    role: str
    user_name: str | None = None
    user_email: str | None = None

    model_config = {"from_attributes": True}


class JourneyResponse(BaseModel):
    id: str
    team_id: str
    name: str
    description: str | None = None
    status: str
    created_by: str
    creator_name: str | None = None
    stages: list[StageResponse] = []
    personas: list[PersonaBasicResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class JourneyListResponse(BaseModel):
    id: str
    name: str
    description: str | None = None
    status: str
    stage_count: int = 0
    persona_count: int = 0
    creator_name: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
