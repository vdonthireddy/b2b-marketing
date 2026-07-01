from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.export_service import ExportService
from app.middleware.auth import get_current_user
from app.middleware.rbac import require_viewer, require_editor
from app.models.user import User
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/{journey_id}/json")
async def export_json(
    journey_id: str,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Export a journey as JSON."""
    service = ExportService(db)
    data = await service.export_json(journey_id, current_user.team_id)
    return Response(
        content=json.dumps(data, indent=2, default=str),
        media_type="application/json",
        headers={"Content-Disposition": f'attachment; filename="journey-{journey_id}.json"'},
    )


@router.get("/{journey_id}/csv")
async def export_csv(
    journey_id: str,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Export journey stages as CSV."""
    service = ExportService(db)
    csv_content = await service.export_csv(journey_id, current_user.team_id)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="journey-{journey_id}.csv"'},
    )


@router.get("/{journey_id}/pdf")
async def export_pdf(
    journey_id: str,
    current_user: User = Depends(require_viewer),
    db: AsyncSession = Depends(get_db),
):
    """Export journey as a PDF report."""
    service = ExportService(db)
    pdf_bytes = await service.export_pdf(journey_id, current_user.team_id)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="journey-{journey_id}.pdf"'},
    )


class ImportRequest(BaseModel):
    data: dict


@router.post("/import/json")
async def import_json(
    body: ImportRequest,
    current_user: User = Depends(require_editor),
    db: AsyncSession = Depends(get_db),
):
    """Import a journey from JSON data."""
    service = ExportService(db)
    journey_id = await service.import_json(current_user.team_id, current_user.id, body.data)
    return {"message": "Journey imported", "journey_id": journey_id}
