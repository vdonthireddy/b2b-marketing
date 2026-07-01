from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse, RefreshTokenRequest
from app.services.auth_service import AuthService
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user and create a team."""
    service = AuthService(db)
    result = await service.register(
        email=data.email, password=data.password,
        name=data.name, team_name=data.team_name
    )
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=UserResponse.model_validate(result["user"]),
    )


@router.post("/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return tokens."""
    service = AuthService(db)
    result = await service.login(email=data.email, password=data.password)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=UserResponse.model_validate(result["user"]),
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """Refresh an access token."""
    service = AuthService(db)
    result = await service.refresh(data.refresh_token)
    return TokenResponse(
        access_token=result["access_token"],
        refresh_token=result["refresh_token"],
        user=UserResponse.model_validate(result["user"]),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)
