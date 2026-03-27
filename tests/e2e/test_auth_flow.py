"""
E2E tests for the authentication flow (login, /me, logout).
"""
import pytest
import httpx

from conftest import API_BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD


@pytest.fixture
async def fresh_client() -> httpx.AsyncClient:
    """A per-test client with no pre-set auth headers."""
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.mark.asyncio
async def test_login_success(fresh_client: httpx.AsyncClient):
    """POST /api/v1/auth/login with valid credentials returns 200 and a token."""
    response = await fresh_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
    data = response.json()
    token = data.get("access_token") or data.get("token")
    assert token, f"Response missing access_token / token field: {data}"
    assert isinstance(token, str) and len(token) > 0


@pytest.mark.asyncio
async def test_login_invalid_credentials(fresh_client: httpx.AsyncClient):
    """POST /api/v1/auth/login with wrong password returns 401."""
    response = await fresh_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": "definitely-wrong-password"},
    )
    assert response.status_code == 401, (
        f"Expected 401 for bad credentials, got {response.status_code}: {response.text}"
    )


@pytest.mark.asyncio
async def test_get_me_authenticated(fresh_client: httpx.AsyncClient):
    """GET /api/v1/auth/me with a valid JWT returns user fields."""
    # Obtain token first
    login_resp = await fresh_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token") or login_resp.json().get("token")

    me_resp = await fresh_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert me_resp.status_code == 200, (
        f"Expected 200 from /me, got {me_resp.status_code}: {me_resp.text}"
    )
    me_data = me_resp.json()
    # Expect at minimum an id/username/email field
    assert any(field in me_data for field in ("id", "username", "email", "sub")), (
        f"User object missing identifying field: {me_data}"
    )


@pytest.mark.asyncio
async def test_get_me_unauthenticated(fresh_client: httpx.AsyncClient):
    """GET /api/v1/auth/me without a token returns 401."""
    response = await fresh_client.get("/api/v1/auth/me")
    assert response.status_code == 401, (
        f"Expected 401 without auth header, got {response.status_code}: {response.text}"
    )


@pytest.mark.asyncio
async def test_logout(fresh_client: httpx.AsyncClient):
    """POST /api/v1/auth/logout invalidates the token so /me returns 401."""
    # Log in
    login_resp = await fresh_client.post(
        "/api/v1/auth/login",
        json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
    )
    assert login_resp.status_code == 200
    token = login_resp.json().get("access_token") or login_resp.json().get("token")
    headers = {"Authorization": f"Bearer {token}"}

    # Confirm /me works before logout
    me_before = await fresh_client.get("/api/v1/auth/me", headers=headers)
    assert me_before.status_code == 200

    # Logout
    logout_resp = await fresh_client.post("/api/v1/auth/logout", headers=headers)
    assert logout_resp.status_code in (200, 204), (
        f"Expected 200/204 from logout, got {logout_resp.status_code}: {logout_resp.text}"
    )

    # /me should now be rejected
    me_after = await fresh_client.get("/api/v1/auth/me", headers=headers)
    assert me_after.status_code == 401, (
        f"Expected 401 after logout, got {me_after.status_code}: {me_after.text}"
    )
