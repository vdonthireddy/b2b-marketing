from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.services.ai_service import AIService
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/ai", tags=["ai"])


class SuggestionRequest(BaseModel):
    stage_name: str
    journey_context: str = ""


class PersonaSuggestionRequest(BaseModel):
    industry: str = ""
    role: str = ""


@router.post("/suggest/goals")
async def suggest_goals(
    data: SuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """Get AI-suggested goals for a journey stage."""
    service = AIService()
    suggestions = await service.suggest_goals(data.stage_name, data.journey_context)
    return {"suggestions": suggestions}


@router.post("/suggest/touchpoints")
async def suggest_touchpoints(
    data: SuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """Get AI-suggested touchpoints for a journey stage."""
    service = AIService()
    suggestions = await service.suggest_touchpoints(data.stage_name, data.journey_context)
    return {"suggestions": suggestions}


@router.post("/suggest/content")
async def suggest_content(
    data: SuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """Get AI-suggested content types for a journey stage."""
    service = AIService()
    suggestions = await service.suggest_content(data.stage_name, data.journey_context)
    return {"suggestions": suggestions}


@router.post("/suggest/persona")
async def suggest_persona(
    data: PersonaSuggestionRequest,
    current_user: User = Depends(get_current_user),
):
    """Get AI-suggested persona details."""
    service = AIService()
    suggestion = await service.suggest_persona(data.industry, data.role)
    return {"suggestion": suggestion}
