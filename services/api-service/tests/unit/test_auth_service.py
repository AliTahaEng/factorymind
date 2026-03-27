"""Test AuthService."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from api_service.config import Settings
from api_service.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    settings = Settings(
        jwt_secret_key="test-secret-key-that-is-long-enough",
        database_url="postgresql+asyncpg://x:x@localhost/x",
        redis_url="redis://localhost/0",
        kafka_bootstrap_servers="localhost:9092",
        schema_registry_url="http://localhost:8081",
    )
    token_store = AsyncMock()
    token_store.is_blacklisted.return_value = False
    return AuthService(settings=settings, token_store=token_store)


def test_hash_and_verify_password(auth_service):
    hashed = auth_service.hash_password("my-secret-password")
    assert auth_service.verify_password("my-secret-password", hashed)
    assert not auth_service.verify_password("wrong-password", hashed)


def test_create_access_token(auth_service):
    token, expires_in = auth_service.create_access_token("user-123", "operator")
    assert isinstance(token, str)
    assert expires_in == 60 * 60  # 60 minutes in seconds


@pytest.mark.asyncio
async def test_verify_token(auth_service):
    token, _ = auth_service.create_access_token("user-456", "viewer")
    payload = await auth_service.verify_token(token)
    assert payload["sub"] == "user-456"
    assert payload["role"] == "viewer"
