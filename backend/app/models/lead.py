import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, func, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    company: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(100), nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="new")
    value: Mapped[float] = mapped_column(Float, default=0.0)
    
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("journeys.id"), nullable=False, index=True)
    stage_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("stages.id"), nullable=True, index=True)
    persona_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("personas.id"), nullable=True, index=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    journey: Mapped["Journey"] = relationship("Journey", lazy="selectin")
    stage: Mapped["Stage"] = relationship("Stage", lazy="selectin")
    persona: Mapped["Persona"] = relationship("Persona", lazy="selectin")


from app.models.journey import Journey  # noqa: E402
from app.models.stage import Stage  # noqa: E402
from app.models.persona import Persona  # noqa: E402
