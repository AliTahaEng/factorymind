"""Test fixtures for API service."""
import pytest
from httpx import AsyncClient, ASGITransport
from api_service import container as _container_module


@pytest.fixture(autouse=True)
def reset_container():
    _container_module._container = None
    yield
    _container_module._container = None
