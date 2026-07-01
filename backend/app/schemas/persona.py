from pydantic import BaseModel
from datetime import datetime


class PersonaCreate(BaseModel):
    name: str
    role_title: str | None = None
    company_size: str | None = None
    goals: str | None = None
    pain_points: str | None = None
    motivations: str | None = None
    avatar_color: str = "#6366f1"


class PersonaUpdate(BaseModel):
    name: str | None = None
    role_title: str | None = None
    company_size: str | None = None
    goals: str | None = None
    pain_points: str | None = None
    motivations: str | None = None
    avatar_color: str | None = None


class PersonaResponse(BaseModel):
    id: str
    team_id: str
    name: str
    role_title: str | None = None
    company_size: str | None = None
    goals: str | None = None
    pain_points: str | None = None
    motivations: str | None = None
    avatar_color: str
    created_by: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
