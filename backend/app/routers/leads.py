from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.common import MessageResponse
from app.services.lead_service import LeadService
from app.middleware.rbac import require_editor, require_viewer
from app.models.user import User

router = APIRouter(prefix="/api/leads", tags=["leads"])


@router.get("", response_model=dict)
async def list_leads(
    journey_id: str | None = None,
    stage_id: str | None = None,
    persona_id: str | None = None,
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """List leads with filtering and pagination."""
    service = LeadService(db)
    result = await service.list_leads(
        journey_id=journey_id,
        stage_id=stage_id,
        persona_id=persona_id,
        page=page,
        page_size=page_size
    )
    
    # Validate each item using Pydantic
    items = [LeadResponse.model_validate(item) for item in result["items"]]
    
    return {
        "items": items,
        "total": result["total"],
        "page": result["page"],
        "page_size": result["page_size"],
        "total_pages": result["total_pages"],
    }


@router.post("", response_model=LeadResponse)
async def create_lead(
    data: LeadCreate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Create a new lead."""
    service = LeadService(db)
    lead = await service.create_lead(data)
    return LeadResponse.model_validate(lead)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: str,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Get a single lead by ID."""
    service = LeadService(db)
    lead = await service.get_lead(lead_id)
    return LeadResponse.model_validate(lead)


@router.put("/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: str,
    data: LeadUpdate,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing lead."""
    service = LeadService(db)
    lead = await service.update_lead(lead_id, data)
    return LeadResponse.model_validate(lead)


@router.delete("/{lead_id}", response_model=MessageResponse)
async def delete_lead(
    lead_id: str,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Delete a lead."""
    service = LeadService(db)
    await service.delete_lead(lead_id)
    return MessageResponse(message="Lead deleted successfully")
