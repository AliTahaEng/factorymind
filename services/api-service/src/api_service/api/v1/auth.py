"""Authentication endpoints."""
import logging
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api_service.schemas.auth import LoginRequest, TokenResponse, UserCreate, UserRead
from api_service.models.db_models import User
from api_service.container import get_container
from api_service.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
_bearer = HTTPBearer(auto_error=False)


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest):
    container = get_container()
    async with container.session_factory() as session:
        result = await session.execute(select(User).where(User.username == req.username))
        user = result.scalar_one_or_none()
        if not user or not container.auth_service.verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
        access_token, expires_in = container.auth_service.create_access_token(str(user.id), user.role)
        refresh_token = container.auth_service.create_refresh_token(str(user.id))
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )


@router.post("/logout", status_code=204)
async def logout(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    current_user: dict = Depends(get_current_user),
):
    if credentials:
        container = get_container()
        await container.auth_service.logout(credentials.credentials)


@router.get("/me", response_model=UserRead)
async def me(current_user: dict = Depends(get_current_user)):
    container = get_container()
    async with container.session_factory() as session:
        result = await session.execute(select(User).where(User.id == current_user["sub"]))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserRead(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role,
            is_active=user.is_active,
        )


@router.post("/register", response_model=UserRead, status_code=201)
async def register(req: UserCreate):
    """Register a new user (admin only in production, open for demo)."""
    container = get_container()
    async with container.session_factory() as session:
        existing = await session.execute(select(User).where(User.username == req.username))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Username already exists")
        user = User(
            username=req.username,
            hashed_password=container.auth_service.hash_password(req.password),
            email=req.email,
            role=req.role,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return UserRead(id=str(user.id), username=user.username, email=user.email, role=user.role, is_active=user.is_active)
