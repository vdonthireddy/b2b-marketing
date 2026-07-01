from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from app.models.journey import Journey, JourneyStatus
from app.models.stage import Stage, StageGoal, StageTouchpoint, StageContent
from app.models.persona import JourneyPersona
from app.models.audit_log import AuditLog
from app.models.user import User
from fastapi import HTTPException, status


# Default 8 stages from the Ruler Analytics customer journey framework
DEFAULT_STAGES = [
    {"name": "Awareness", "icon": "👁️", "color": "#6366f1", "description": "How visitors find your brand through search, social, and paid channels"},
    {"name": "Engagement", "icon": "💬", "color": "#8b5cf6", "description": "Transform visitors into interested parties through content and interaction"},
    {"name": "Subscribe", "icon": "📧", "color": "#a855f7", "description": "Convert engaged users into subscribers through gated content or demos"},
    {"name": "Conversion", "icon": "💰", "color": "#00d4aa", "description": "The point where money or time is exchanged for your product or service"},
    {"name": "Excite", "icon": "✨", "color": "#f59e0b", "description": "Deliver the 'Aha' moment — wonder and understanding collide"},
    {"name": "Ascend", "icon": "📈", "color": "#38bdf8", "description": "Upsell and expand usage through higher tiers or additional features"},
    {"name": "Advocate", "icon": "❤️", "color": "#f97316", "description": "Customer freely promotes your company and shares testimonials"},
    {"name": "Promoter", "icon": "🚀", "color": "#ec4899", "description": "Customer generates referrals that convert into new business"},
]


class JourneyService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_journeys(self, team_id: str, page: int = 1, page_size: int = 20) -> dict:
        """List all journeys for a team with pagination."""
        # Count total
        count_query = select(func.count(Journey.id)).where(Journey.team_id == team_id)
        total = (await self.db.execute(count_query)).scalar() or 0

        # Fetch page
        query = (
            select(Journey)
            .where(Journey.team_id == team_id)
            .order_by(Journey.updated_at.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        result = await self.db.execute(query)
        journeys = result.scalars().all()

        items = []
        for j in journeys:
            items.append({
                "id": j.id,
                "name": j.name,
                "description": j.description,
                "status": j.status.value,
                "stage_count": len(j.stages),
                "persona_count": len(j.personas),
                "creator_name": j.creator.name if j.creator else None,
                "created_at": j.created_at,
                "updated_at": j.updated_at,
            })

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def get_journey(self, journey_id: str, team_id: str) -> Journey:
        """Get a journey with all nested data."""
        result = await self.db.execute(
            select(Journey).where(Journey.id == journey_id, Journey.team_id == team_id)
        )
        journey = result.scalar_one_or_none()

        if not journey:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journey not found")

        return journey

    async def create_journey(
        self, team_id: str, user_id: str, name: str, description: str | None = None,
        include_default_stages: bool = True
    ) -> Journey:
        """Create a new journey with optional default stages."""
        # Check for unique name constraint
        existing_result = await self.db.execute(select(Journey).where(Journey.name == name))
        if existing_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A journey with this name already exists. Please choose a unique name."
            )

        journey = Journey(
            team_id=team_id,
            name=name,
            description=description,
            created_by=user_id,
        )
        self.db.add(journey)
        await self.db.flush()

        # Add default stages
        if include_default_stages:
            for i, stage_data in enumerate(DEFAULT_STAGES):
                stage = Stage(
                    journey_id=journey.id,
                    name=stage_data["name"],
                    description=stage_data["description"],
                    icon=stage_data["icon"],
                    color=stage_data["color"],
                    position=i,
                )
                self.db.add(stage)

        # Audit log
        self.db.add(AuditLog(
            team_id=team_id, user_id=user_id,
            action="created", entity_type="journey", entity_id=journey.id,
            details={"name": name},
        ))

        await self.db.flush()
        await self.db.commit()

        # Re-fetch to get stages loaded
        return await self.get_journey(journey.id, team_id)

    async def update_journey(
        self, journey_id: str, team_id: str, user_id: str, **updates
    ) -> Journey:
        """Update journey metadata."""
        journey = await self.get_journey(journey_id, team_id)

        # Check unique name constraint if name is changing
        if "name" in updates:
            new_name = updates["name"]
            existing_result = await self.db.execute(
                select(Journey).where(Journey.name == new_name, Journey.id != journey_id)
            )
            if existing_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="A journey with this name already exists. Please choose a unique name."
                )

        for field, value in updates.items():
            if value is not None and hasattr(journey, field):
                if field == "status":
                    value = JourneyStatus(value)
                setattr(journey, field, value)

        self.db.add(AuditLog(
            team_id=team_id, user_id=user_id,
            action="updated", entity_type="journey", entity_id=journey_id,
            details=updates,
        ))

        await self.db.flush()
        return journey

    async def delete_journey(self, journey_id: str, team_id: str, user_id: str) -> None:
        """Delete a journey and all its data."""
        journey = await self.get_journey(journey_id, team_id)

        self.db.add(AuditLog(
            team_id=team_id, user_id=user_id,
            action="deleted", entity_type="journey", entity_id=journey_id,
            details={"name": journey.name},
        ))

        await self.db.delete(journey)

    # --- Stage operations ---

    async def add_stage(
        self, journey_id: str, team_id: str, user_id: str,
        name: str, description: str | None = None, icon: str = "📌",
        color: str = "#6366f1", position: int | None = None
    ) -> Stage:
        """Add a stage to a journey."""
        journey = await self.get_journey(journey_id, team_id)

        if position is None:
            position = len(journey.stages)

        # Shift existing stages
        for s in journey.stages:
            if s.position >= position:
                s.position += 1

        stage = Stage(
            journey_id=journey_id,
            name=name,
            description=description,
            icon=icon,
            color=color,
            position=position,
        )
        self.db.add(stage)
        await self.db.flush()
        return stage

    async def update_stage(
        self, stage_id: str, team_id: str, user_id: str, **updates
    ) -> Stage:
        """Update a stage's properties."""
        result = await self.db.execute(
            select(Stage).join(Journey).where(Stage.id == stage_id, Journey.team_id == team_id)
        )
        stage = result.scalar_one_or_none()
        if not stage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

        for field, value in updates.items():
            if value is not None and hasattr(stage, field):
                setattr(stage, field, value)

        await self.db.flush()
        return stage

    async def delete_stage(self, stage_id: str, team_id: str, user_id: str) -> None:
        """Delete a stage."""
        result = await self.db.execute(
            select(Stage).join(Journey).where(Stage.id == stage_id, Journey.team_id == team_id)
        )
        stage = result.scalar_one_or_none()
        if not stage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

        await self.db.delete(stage)

    async def reorder_stages(self, journey_id: str, team_id: str, stage_ids: list[str]) -> list[Stage]:
        """Reorder stages by setting positions based on the provided ID order."""
        journey = await self.get_journey(journey_id, team_id)

        stage_map = {s.id: s for s in journey.stages}
        for i, sid in enumerate(stage_ids):
            if sid in stage_map:
                stage_map[sid].position = i

        await self.db.flush()
        return sorted(journey.stages, key=lambda s: s.position)

    # --- Sub-item operations (goals, touchpoints, content) ---

    async def add_stage_item(
        self, stage_id: str, team_id: str, item_type: str, text: str,
        content_type: str | None = None
    ):
        """Add a goal, touchpoint, or content item to a stage."""
        result = await self.db.execute(
            select(Stage).join(Journey).where(Stage.id == stage_id, Journey.team_id == team_id)
        )
        stage = result.scalar_one_or_none()
        if not stage:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stage not found")

        if item_type == "goal":
            item = StageGoal(stage_id=stage_id, text=text, position=len(stage.goals))
        elif item_type == "touchpoint":
            item = StageTouchpoint(stage_id=stage_id, text=text, position=len(stage.touchpoints))
        elif item_type == "content":
            item = StageContent(stage_id=stage_id, text=text, content_type=content_type or "general", position=len(stage.content))
        else:
            raise HTTPException(status_code=400, detail=f"Invalid item type: {item_type}")

        self.db.add(item)
        await self.db.flush()
        return item

    async def update_stage_item(self, item_id: str, item_type: str, text: str | None = None, content_type: str | None = None):
        """Update a stage sub-item."""
        model_map = {"goal": StageGoal, "touchpoint": StageTouchpoint, "content": StageContent}
        model = model_map.get(item_type)
        if not model:
            raise HTTPException(status_code=400, detail=f"Invalid item type: {item_type}")

        result = await self.db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        if text is not None:
            item.text = text
        if content_type is not None and item_type == "content":
            item.content_type = content_type

        await self.db.flush()
        return item

    async def delete_stage_item(self, item_id: str, item_type: str):
        """Delete a stage sub-item."""
        model_map = {"goal": StageGoal, "touchpoint": StageTouchpoint, "content": StageContent}
        model = model_map.get(item_type)
        if not model:
            raise HTTPException(status_code=400, detail=f"Invalid item type: {item_type}")

        result = await self.db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")

        await self.db.delete(item)
