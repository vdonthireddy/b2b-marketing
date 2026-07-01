from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.persona import Persona, JourneyPersona
from app.models.journey import Journey
from app.models.audit_log import AuditLog
from fastapi import HTTPException, status


class PersonaService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_personas(self, team_id: str) -> list[Persona]:
        """List all personas for a team."""
        result = await self.db.execute(
            select(Persona).where(Persona.team_id == team_id).order_by(Persona.created_at.desc())
        )
        return list(result.scalars().all())

    async def get_persona(self, persona_id: str, team_id: str) -> Persona:
        """Get a single persona."""
        result = await self.db.execute(
            select(Persona).where(Persona.id == persona_id, Persona.team_id == team_id)
        )
        persona = result.scalar_one_or_none()
        if not persona:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Persona not found")
        return persona

    async def create_persona(self, team_id: str, user_id: str, **data) -> Persona:
        """Create a new persona."""
        persona = Persona(team_id=team_id, created_by=user_id, **data)
        self.db.add(persona)
        await self.db.flush()

        self.db.add(AuditLog(
            team_id=team_id, user_id=user_id,
            action="created", entity_type="persona", entity_id=persona.id,
            details={"name": data.get("name")},
        ))

        await self.db.flush()
        return persona

    async def update_persona(self, persona_id: str, team_id: str, user_id: str, **updates) -> Persona:
        """Update a persona."""
        persona = await self.get_persona(persona_id, team_id)

        for field, value in updates.items():
            if value is not None and hasattr(persona, field):
                setattr(persona, field, value)

        await self.db.flush()
        return persona

    async def delete_persona(self, persona_id: str, team_id: str, user_id: str) -> None:
        """Delete a persona."""
        persona = await self.get_persona(persona_id, team_id)

        self.db.add(AuditLog(
            team_id=team_id, user_id=user_id,
            action="deleted", entity_type="persona", entity_id=persona_id,
            details={"name": persona.name},
        ))

        await self.db.delete(persona)

    async def link_persona_to_journey(self, journey_id: str, persona_id: str, team_id: str) -> None:
        """Link a persona to a journey."""
        # Verify both exist in team
        result = await self.db.execute(
            select(Journey).where(Journey.id == journey_id, Journey.team_id == team_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Journey not found")

        await self.get_persona(persona_id, team_id)

        # Check if already linked
        result = await self.db.execute(
            select(JourneyPersona).where(
                JourneyPersona.journey_id == journey_id,
                JourneyPersona.persona_id == persona_id,
            )
        )
        if result.scalar_one_or_none():
            return  # Already linked

        link = JourneyPersona(journey_id=journey_id, persona_id=persona_id)
        self.db.add(link)
        await self.db.flush()

    async def unlink_persona_from_journey(self, journey_id: str, persona_id: str, team_id: str) -> None:
        """Unlink a persona from a journey."""
        result = await self.db.execute(
            select(JourneyPersona).where(
                JourneyPersona.journey_id == journey_id,
                JourneyPersona.persona_id == persona_id,
            )
        )
        link = result.scalar_one_or_none()
        if link:
            await self.db.delete(link)
