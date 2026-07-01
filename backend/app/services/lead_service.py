from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.lead import Lead
from app.schemas.lead import LeadCreate, LeadUpdate
from fastapi import HTTPException, status


class LeadService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_leads(
        self, journey_id: str | None = None, stage_id: str | None = None,
        persona_id: str | None = None, page: int = 1, page_size: int = 20
    ) -> dict:
        """List leads with filtering and pagination."""
        query = select(Lead)
        count_query = select(func.count(Lead.id))

        if journey_id:
            query = query.where(Lead.journey_id == journey_id)
            count_query = count_query.where(Lead.journey_id == journey_id)
        if stage_id:
            query = query.where(Lead.stage_id == stage_id)
            count_query = count_query.where(Lead.stage_id == stage_id)
        if persona_id:
            query = query.where(Lead.persona_id == persona_id)
            count_query = count_query.where(Lead.persona_id == persona_id)

        # Count total
        total = (await self.db.execute(count_query)).scalar() or 0

        # Fetch page
        query = query.order_by(Lead.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
        result = await self.db.execute(query)
        leads = result.scalars().all()

        return {
            "items": leads,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_lead(self, lead_id: str) -> Lead:
        """Get a single lead by ID."""
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        lead = result.scalar_one_or_none()
        if not lead:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
        return lead

    async def create_lead(self, lead_data: LeadCreate) -> Lead:
        """Create a new lead."""
        lead = Lead(**lead_data.model_dump())
        self.db.add(lead)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def update_lead(self, lead_id: str, lead_data: LeadUpdate) -> Lead:
        """Update a lead."""
        lead = await self.get_lead(lead_id)
        
        updates = lead_data.model_dump(exclude_unset=True)
        for field, value in updates.items():
            setattr(lead, field, value)
            
        self.db.add(lead)
        await self.db.flush()
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def delete_lead(self, lead_id: str) -> None:
        """Delete a lead."""
        lead = await self.get_lead(lead_id)
        await self.db.delete(lead)
        await self.db.commit()
