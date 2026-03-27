"""Integration tests for health endpoints."""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock, patch
from api_service import container as _container_module
from api_service.config import Settings


@pytest.fixture
async def client():
    """Create test client with mocked container."""
    mock_container = MagicMock()
    mock_container.settings = Settings(
        database_url="postgresql+asyncpg://x:x@localhost/x",
        redis_url="redis://localhost/0",
        jwt_secret_key="test-key",
        kafka_bootstrap_servers="localhost:9092",
        schema_registry_url="http://localhost:8081",
    )
    mock_container.startup = AsyncMock()
    mock_container.shutdown = AsyncMock()
    mock_container.ingestion_service = MagicMock()
    mock_container.ingestion_service.start = AsyncMock()
    mock_container.ingestion_service.stop = AsyncMock()

    from api_service.main import create_app
    app = create_app()

    with patch("api_service.container.init_container", return_value=mock_container):
        with patch("api_service.container._container", mock_container):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_ready_endpoint(client):
    resp = await client.get("/ready")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ready"}
