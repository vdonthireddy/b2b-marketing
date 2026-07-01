from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse
from app.schemas.common import MessageResponse
from app.services.persona_service import PersonaService
from app.middleware.auth import get_current_user
from app.middleware.rbac import require_editor, require_viewer
from app.models.user import User
from pydantic import BaseModel

router = APIRouter(prefix="/api/personas", tags=["personas"])


@router.get("", response_model=list[PersonaResponse])
async def list_personas(
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """List all personas for the current team."""
    service = PersonaService(db)
    personas = await service.list_personas(current_user.team_id)
    return [PersonaResponse.model_validate(p) for p in personas]


@router.post("", response_model=PersonaResponse)
async def create_persona(
    data: PersonaCreate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new persona."""
    service = PersonaService(db)
    persona = await service.create_persona(
        team_id=current_user.team_id,
        user_id=current_user.id,
        **data.model_dump(),
    )
    return PersonaResponse.model_validate(persona)


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: str,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Get a persona."""
    service = PersonaService(db)
    persona = await service.get_persona(persona_id, current_user.team_id)
    return PersonaResponse.model_validate(persona)


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: str,
    data: PersonaUpdate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update a persona."""
    service = PersonaService(db)
    persona = await service.update_persona(
        persona_id, current_user.team_id, current_user.id,
        **data.model_dump(exclude_none=True),
    )
    return PersonaResponse.model_validate(persona)


@router.delete("/{persona_id}", response_model=MessageResponse)
async def delete_persona(
    persona_id: str,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a persona."""
    service = PersonaService(db)
    await service.delete_persona(persona_id, current_user.team_id, current_user.id)
    return MessageResponse(message="Persona deleted")


class LinkPersonaRequest(BaseModel):
    persona_id: str


@router.post("/journeys/{journey_id}/link", response_model=MessageResponse)
async def link_persona(
    journey_id: str,
    data: LinkPersonaRequest,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Link a persona to a journey."""
    service = PersonaService(db)
    await service.link_persona_to_journey(journey_id, data.persona_id, current_user.team_id)
    return MessageResponse(message="Persona linked")


@router.delete("/journeys/{journey_id}/link/{persona_id}", response_model=MessageResponse)
async def unlink_persona(
    journey_id: str,
    persona_id: str,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Unlink a persona from a journey."""
    service = PersonaService(db)
    await service.unlink_persona_from_journey(journey_id, persona_id, current_user.team_id)
    return MessageResponse(message="Persona unlinked")
