import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Enum as SAEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    EDITOR = "editor"
    VIEWER = "viewer"


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    plan: Mapped[str] = mapped_column(String(50), default="free")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    members: Mapped[list["User"]] = relationship("User", back_populates="team", lazy="selectin")
    invitations: Mapped[list["TeamInvitation"]] = relationship("TeamInvitation", back_populates="team", lazy="selectin")


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(512), nullable=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.EDITOR)
    team_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("teams.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    team: Mapped[Team | None] = relationship("Team", back_populates="members", lazy="selectin")


class TeamInvitation(Base):
    __tablename__ = "team_invitations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    team_id: Mapped[str] = mapped_column(String(36), ForeignKey("teams.id"), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole), default=UserRole.EDITOR)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    accepted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    team: Mapped[Team] = relationship("Team", back_populates="invitations", lazy="selectin")
