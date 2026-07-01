from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str
    team_name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: str | None = None
    role: str
    team_id: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TeamResponse(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    created_at: datetime
    member_count: int = 0

    model_config = {"from_attributes": True}


class InviteRequest(BaseModel):
    email: EmailStr
    role: str = "editor"
