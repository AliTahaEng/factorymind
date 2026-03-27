"""Test fixtures for inference service."""
import pytest
from httpx import AsyncClient, ASGITransport
from inference_service.main import create_app
from inference_service.config import Settings


@pytest.fixture
def test_settings():
    return Settings(
        kafka_bootstrap_servers="localhost:9092",
        schema_registry_url="http://localhost:8081",
        triton_host="localhost",
        triton_port=8001,
        enable_kafka_consumer=False,
        enable_triton=False,
    )


@pytest.fixture
async def client(test_settings):
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
