import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, Team, UserRole
from app.utils.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from fastapi import HTTPException, status


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, email: str, password: str, name: str, team_name: str | None = None) -> dict:
        """Register a new user and optionally create a team."""
        # Check if email already exists
        result = await self.db.execute(select(User).where(User.email == email))
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        # Create team if name provided
        team = None
        if team_name:
            slug = re.sub(r"[^a-z0-9]+", "-", team_name.lower()).strip("-")
            # Check for slug collision
            result = await self.db.execute(select(Team).where(Team.slug == slug))
            if result.scalar_one_or_none():
                import uuid
                slug = f"{slug}-{str(uuid.uuid4())[:8]}"

            team = Team(name=team_name, slug=slug)
            self.db.add(team)
            await self.db.flush()

        # Create user
        user = User(
            email=email,
            password_hash=hash_password(password),
            name=name,
            role=UserRole.ADMIN if team else UserRole.EDITOR,
            team_id=team.id if team else None,
        )
        self.db.add(user)
        await self.db.flush()

        # Generate tokens
        access_token = create_access_token(user.id, user.role.value, user.team_id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    async def login(self, email: str, password: str) -> dict:
        """Authenticate a user and return tokens."""
        result = await self.db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        access_token = create_access_token(user.id, user.role.value, user.team_id)
        refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        }

    async def refresh(self, refresh_token_str: str) -> dict:
        """Refresh an access token."""
        try:
            payload = decode_token(refresh_token_str)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
            )

        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )

        user_id = payload.get("sub")
        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )

        access_token = create_access_token(user.id, user.role.value, user.team_id)
        new_refresh_token = create_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "user": user,
        }
