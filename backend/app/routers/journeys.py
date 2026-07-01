from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.journey import JourneyCreate, JourneyUpdate, JourneyResponse, JourneyListResponse
from app.schemas.stage import StageCreate, StageUpdate, StageReorder, StageItemCreate, StageItemUpdate, StageItemResponse
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services.journey_service import JourneyService
from app.middleware.auth import get_current_user
from app.middleware.rbac import require_editor, require_viewer, require_admin
from app.models.user import User

router = APIRouter(prefix="/api/journeys", tags=["journeys"])


# --- Journey CRUD ---

@router.get("", response_model=PaginatedResponse)
async def list_journeys(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """List all journeys for the current team."""
    service = JourneyService(db)
    return await service.list_journeys(current_user.team_id, page, page_size)


@router.post("", response_model=JourneyResponse)
async def create_journey(
    data: JourneyCreate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new journey with default stages."""
    service = JourneyService(db)
    journey = await service.create_journey(
        team_id=current_user.team_id,
        user_id=current_user.id,
        name=data.name,
        description=data.description,
    )
    return _build_journey_response(journey)


@router.get("/{journey_id}", response_model=JourneyResponse)
async def get_journey(
    journey_id: str,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Get a journey with all stages and nested data."""
    service = JourneyService(db)
    journey = await service.get_journey(journey_id, current_user.team_id)
    return _build_journey_response(journey)


@router.put("/{journey_id}", response_model=JourneyResponse)
async def update_journey(
    journey_id: str,
    data: JourneyUpdate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update journey metadata."""
    service = JourneyService(db)
    journey = await service.update_journey(
        journey_id, current_user.team_id, current_user.id,
        **data.model_dump(exclude_none=True),
    )
    return _build_journey_response(journey)


@router.delete("/{journey_id}", response_model=MessageResponse)
async def delete_journey(
    journey_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a journey (admin only)."""
    service = JourneyService(db)
    await service.delete_journey(journey_id, current_user.team_id, current_user.id)
    return MessageResponse(message="Journey deleted")


# --- Stage endpoints ---

@router.post("/{journey_id}/stages")
async def add_stage(
    journey_id: str,
    data: StageCreate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Add a stage to a journey."""
    service = JourneyService(db)
    stage = await service.add_stage(
        journey_id, current_user.team_id, current_user.id,
        name=data.name, description=data.description,
        icon=data.icon, color=data.color, position=data.position,
    )
    return {"id": stage.id, "name": stage.name, "position": stage.position}


@router.put("/{journey_id}/stages/reorder")
async def reorder_stages(
    journey_id: str,
    data: StageReorder,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Reorder stages within a journey."""
    service = JourneyService(db)
    stages = await service.reorder_stages(journey_id, current_user.team_id, data.stage_ids)
    return [{"id": s.id, "name": s.name, "position": s.position} for s in stages]


@router.put("/stages/{stage_id}")
async def update_stage(
    stage_id: str,
    data: StageUpdate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update a stage."""
    service = JourneyService(db)
    stage = await service.update_stage(
        stage_id, current_user.team_id, current_user.id,
        **data.model_dump(exclude_none=True),
    )
    return {"id": stage.id, "name": stage.name}


@router.delete("/stages/{stage_id}", response_model=MessageResponse)
async def delete_stage(
    stage_id: str,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a stage."""
    service = JourneyService(db)
    await service.delete_stage(stage_id, current_user.team_id, current_user.id)
    return MessageResponse(message="Stage deleted")


# --- Stage item endpoints (goals, touchpoints, content) ---

@router.post("/stages/{stage_id}/{item_type}")
async def add_stage_item(
    stage_id: str,
    item_type: str,
    data: StageItemCreate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Add a goal, touchpoint, or content item to a stage."""
    service = JourneyService(db)
    item = await service.add_stage_item(
        stage_id, current_user.team_id, item_type,
        data.text, data.content_type,
    )
    return StageItemResponse.model_validate(item)


@router.put("/stages/items/{item_id}/{item_type}")
async def update_stage_item(
    item_id: str,
    item_type: str,
    data: StageItemUpdate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update a stage sub-item."""
    service = JourneyService(db)
    item = await service.update_stage_item(
        item_id, item_type, data.text, data.content_type,
    )
    return StageItemResponse.model_validate(item)


@router.delete("/stages/items/{item_id}/{item_type}", response_model=MessageResponse)
async def delete_stage_item(
    item_id: str,
    item_type: str,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a stage sub-item."""
    service = JourneyService(db)
    await service.delete_stage_item(item_id, item_type)
    return MessageResponse(message="Item deleted")


# --- Helper ---

def _build_journey_response(journey) -> JourneyResponse:
    """Build a JourneyResponse from a Journey model."""
    from app.schemas.journey import StageResponse, StageItemResponse, PersonaBasicResponse

    stages = []
    for s in sorted(journey.stages, key=lambda x: x.position):
        stages.append(StageResponse(
            id=s.id, journey_id=s.journey_id, name=s.name,
            description=s.description, icon=s.icon, color=s.color,
            position=s.position, created_at=s.created_at, updated_at=s.updated_at,
            goals=[StageItemResponse(id=g.id, text=g.text, position=g.position) for g in s.goals],
            touchpoints=[StageItemResponse(id=t.id, text=t.text, position=t.position) for t in s.touchpoints],
            content=[StageItemResponse(id=c.id, text=c.text, position=c.position, content_type=c.content_type) for c in s.content],
        ))

    personas = []
    for jp in journey.personas:
        if jp.persona:
            personas.append(PersonaBasicResponse(
                id=jp.persona.id, name=jp.persona.name,
                role_title=jp.persona.role_title, avatar_color=jp.persona.avatar_color,
            ))

    return JourneyResponse(
        id=journey.id, team_id=journey.team_id, name=journey.name,
        description=journey.description, status=journey.status.value,
        created_by=journey.created_by,
        creator_name=journey.creator.name if journey.creator else None,
        stages=stages, personas=personas,
        created_at=journey.created_at, updated_at=journey.updated_at,
    )
