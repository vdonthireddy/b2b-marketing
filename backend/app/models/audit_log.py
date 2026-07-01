import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # created, updated, deleted
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # journey, stage, persona
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class JourneySnapshot(Base):
    __tablename__ = "journey_snapshots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("journeys.id"), nullable=False, index=True)
    snapshot_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
