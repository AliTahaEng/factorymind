"""Integration tests for API routes."""
import io
import pytest
from PIL import Image
from httpx import AsyncClient, ASGITransport
from inference_service.main import create_app
from inference_service.config import Settings
from inference_service import container as _container_module


@pytest.fixture(autouse=True)
def reset_container():
    _container_module._container = None
    yield
    _container_module._container = None


@pytest.fixture
async def client():
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_ready(client):
    resp = await client.get("/ready")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ready"
