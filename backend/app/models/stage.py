import uuid
from datetime import datetime
from sqlalchemy import String, Text, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Stage(Base):
    __tablename__ = "stages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    journey_id: Mapped[str] = mapped_column(String(36), ForeignKey("journeys.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    icon: Mapped[str] = mapped_column(String(10), default="📌")
    color: Mapped[str] = mapped_column(String(20), default="#6366f1")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    journey: Mapped["Journey"] = relationship("Journey", back_populates="stages")
    goals: Mapped[list["StageGoal"]] = relationship(
        "StageGoal", back_populates="stage", lazy="selectin",
        cascade="all, delete-orphan", order_by="StageGoal.position"
    )
    touchpoints: Mapped[list["StageTouchpoint"]] = relationship(
        "StageTouchpoint", back_populates="stage", lazy="selectin",
        cascade="all, delete-orphan", order_by="StageTouchpoint.position"
    )
    content: Mapped[list["StageContent"]] = relationship(
        "StageContent", back_populates="stage", lazy="selectin",
        cascade="all, delete-orphan", order_by="StageContent.position"
    )


from app.models.journey import Journey  # noqa: E402


class StageGoal(Base):
    __tablename__ = "stage_goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stage_id: Mapped[str] = mapped_column(String(36), ForeignKey("stages.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    stage: Mapped[Stage] = relationship("Stage", back_populates="goals")


class StageTouchpoint(Base):
    __tablename__ = "stage_touchpoints"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stage_id: Mapped[str] = mapped_column(String(36), ForeignKey("stages.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    stage: Mapped[Stage] = relationship("Stage", back_populates="touchpoints")


class StageContent(Base):
    __tablename__ = "stage_content"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    stage_id: Mapped[str] = mapped_column(String(36), ForeignKey("stages.id"), nullable=False, index=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(50), default="general")
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    stage: Mapped[Stage] = relationship("Stage", back_populates="content")
