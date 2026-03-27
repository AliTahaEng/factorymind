"""
Root conftest.py for FactoryMind integration and E2E tests.
"""
import asyncio
import os
import time

import httpx
import pytest

API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8000")
INFERENCE_BASE_URL = os.environ.get("INFERENCE_BASE_URL", "http://localhost:8001")

ADMIN_USERNAME = os.environ.get("TEST_ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.environ.get("TEST_ADMIN_PASSWORD", "admin")


async def wait_for_service(url: str, timeout: int = 60) -> None:
    """Poll GET {url}/health until it returns 200 or timeout is reached."""
    health_url = url.rstrip("/") + "/health"
    deadline = time.monotonic() + timeout
    last_exc: Exception | None = None
    async with httpx.AsyncClient() as client:
        while time.monotonic() < deadline:
            try:
                response = await client.get(health_url, timeout=5.0)
                if response.status_code == 200:
                    return
            except Exception as exc:  # noqa: BLE001
                last_exc = exc
            await asyncio.sleep(2)
    raise TimeoutError(
        f"Service at {health_url} did not become healthy within {timeout}s. "
        f"Last error: {last_exc}"
    )


@pytest.fixture(scope="session")
def event_loop():
    """Create a single event loop for the entire test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def http_client() -> httpx.AsyncClient:
    """Shared async HTTP client for the test session."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
async def inference_client() -> httpx.AsyncClient:
    """Shared async HTTP client pointing at the inference service."""
    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
async def auth_token(http_client: httpx.AsyncClient) -> str:
    """Log in as admin and return the JWT access token."""
    response = await http_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, (
        f"Admin login failed: {response.status_code} {response.text}"
    )
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, f"No token in login response: {data}"
    return token


@pytest.fixture(scope="session")
async def auth_headers(auth_token: str) -> dict:
    """Return Authorization headers with the admin JWT."""
    return {"Authorization": f"Bearer {auth_token}"}
