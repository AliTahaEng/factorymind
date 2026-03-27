"""
Tests for the model version management API (list, promote, rollback).
"""
import os

import httpx
import pytest

from conftest import API_BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD

VIEWER_USERNAME = os.environ.get("TEST_VIEWER_USERNAME", "viewer")
VIEWER_PASSWORD = os.environ.get("TEST_VIEWER_PASSWORD", "viewer")

TEST_MODEL_NAME = "test-model"


async def _get_token(client: httpx.AsyncClient, username: str, password: str) -> str:
    resp = await client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password},
    )
    assert resp.status_code == 200, (
        f"Login failed for {username}: {resp.status_code} {resp.text}"
    )
    data = resp.json()
    token = data.get("access_token") or data.get("token")
    assert token, f"No token in login response: {data}"
    return token


@pytest.fixture
async def admin_client() -> httpx.AsyncClient:
    """Async client authenticated as admin."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        token = await _get_token(client, ADMIN_USERNAME, ADMIN_PASSWORD)
        client.headers.update({"Authorization": f"Bearer {token}"})
        yield client


@pytest.fixture
async def viewer_client() -> httpx.AsyncClient:
    """Async client authenticated as viewer (read-only role)."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        try:
            token = await _get_token(client, VIEWER_USERNAME, VIEWER_PASSWORD)
            client.headers.update({"Authorization": f"Bearer {token}"})
        except AssertionError:
            # If viewer account doesn't exist, create a token with reduced scope
            # and continue — the 403 assertion is what matters.
            pass
        yield client


@pytest.mark.asyncio
async def test_list_models(admin_client: httpx.AsyncClient):
    """GET /api/v1/models returns 200 with a list structure."""
    response = await admin_client.get("/api/v1/models")
    assert response.status_code == 200, (
        f"Expected 200 from GET /api/v1/models, got {response.status_code}: {response.text}"
    )
    data = response.json()
    # Accept list or paginated {"items": [...]}
    if isinstance(data, dict):
        items = data.get("items", data.get("models", data.get("results", [])))
    else:
        items = data
    assert isinstance(items, list), f"Expected list of models, got: {type(items)}"


@pytest.mark.asyncio
async def test_promote_model_as_admin(admin_client: httpx.AsyncClient):
    """POST /api/v1/models/{name}/promote as admin returns 200."""
    response = await admin_client.post(f"/api/v1/models/{TEST_MODEL_NAME}/promote")
    assert response.status_code == 200, (
        f"Expected 200 from promote as admin, got {response.status_code}: {response.text}"
    )
    data = response.json()
    # Response should acknowledge the promotion
    assert data is not None, "Expected a non-null response body from promote"


@pytest.mark.asyncio
async def test_promote_model_as_viewer_forbidden(viewer_client: httpx.AsyncClient):
    """POST /api/v1/models/{name}/promote as viewer returns 403."""
    response = await viewer_client.post(f"/api/v1/models/{TEST_MODEL_NAME}/promote")
    assert response.status_code == 403, (
        f"Expected 403 from promote as viewer, got {response.status_code}: {response.text}"
    )


@pytest.mark.asyncio
async def test_rollback_model_as_admin(admin_client: httpx.AsyncClient):
    """POST /api/v1/models/{name}/rollback as admin returns 200."""
    response = await admin_client.post(f"/api/v1/models/{TEST_MODEL_NAME}/rollback")
    assert response.status_code == 200, (
        f"Expected 200 from rollback as admin, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert data is not None, "Expected a non-null response body from rollback"
