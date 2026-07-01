import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    company_size: Mapped[str | None] = mapped_column(String(50), nullable=True)  # SMB, Mid-Market, Enterprise
    goals: Mapped[str | None] = mapped_column(Text, nullable=True)
    pain_points: Mapped[str | None] = mapped_column(Text, nullable=True)
    motivations: Mapped[str | None] = mapped_column(Text, nullable=True)
    avatar_color: Mapped[str] = mapped_column(String(20), default="#6366f1")
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    journeys: Mapped[list["JourneyPersona"]] = relationship(
        "JourneyPersona", back_populates="persona", lazy="selectin",
        cascade="all, delete-orphan"
    )


class JourneyPersona(Base):
    __tablename__ = "journey_personas"

    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("journeys.id"), primary_key=True)
    persona_id: Mapped[str] = mapped_column(String(36), ForeignKey("personas.id"), primary_key=True)

    journey: Mapped["Journey"] = relationship("Journey", back_populates="personas")
    persona: Mapped[Persona] = relationship("Persona", back_populates="journeys", lazy="selectin")


from app.models.journey import Journey  # noqa: E402
