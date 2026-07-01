from pydantic import BaseModel, EmailStr
from datetime import datetime


class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    company: str
    job_title: str | None = None
    status: str = "new"
    value: float = 0.0
    journey_id: str
    stage_id: str | None = None
    persona_id: str | None = None


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    company: str | None = None
    job_title: str | None = None
    status: str | None = None
    value: float | None = None
    journey_id: str | None = None
    stage_id: str | None = None
    persona_id: str | None = None


class LeadStageResponse(BaseModel):
    id: str
    name: str
    icon: str
    color: str

    model_config = {"from_attributes": True}


class LeadResponse(LeadBase):
    id: str
    created_at: datetime
    updated_at: datetime
    stage: LeadStageResponse | None = None

    model_config = {"from_attributes": True}
