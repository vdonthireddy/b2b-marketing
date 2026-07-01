import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class JourneyStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"


class Journey(Base):
    __tablename__ = "journeys"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[JourneyStatus] = mapped_column(SAEnum(JourneyStatus), default=JourneyStatus.DRAFT)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    stages: Mapped[list["Stage"]] = relationship(
        "Stage", back_populates="journey", lazy="selectin",
        cascade="all, delete-orphan", order_by="Stage.position"
    )
    collaborators: Mapped[list["JourneyCollaborator"]] = relationship(
        "JourneyCollaborator", back_populates="journey", lazy="selectin",
        cascade="all, delete-orphan"
    )
    personas: Mapped[list["JourneyPersona"]] = relationship(
        "JourneyPersona", back_populates="journey", lazy="selectin",
        cascade="all, delete-orphan"
    )
    creator: Mapped["User"] = relationship("User", lazy="selectin")


# Avoid circular import
from app.models.stage import Stage  # noqa: E402
from app.models.persona import JourneyPersona  # noqa: E402


class JourneyCollaborator(Base):
    __tablename__ = "journey_collaborators"

    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("journeys.id"), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), primary_key=True)
    role: Mapped[str] = mapped_column(String(20), default="editor")
    joined_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    journey: Mapped[Journey] = relationship("Journey", back_populates="collaborators")
    user: Mapped["User"] = relationship("User", lazy="selectin")


from app.models.user import User  # noqa: E402, F811
