"""Auth schemas."""
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class UserCreate(BaseModel):
    username: str
    password: str
    email: str | None = None
    role: str = "viewer"


class UserRead(BaseModel):
    id: str
    username: str
    email: str | None
    role: str
    is_active: bool
