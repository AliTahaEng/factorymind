"""
E2E tests for the inspection endpoints.
"""
import uuid
import pytest
import httpx

from conftest import API_BASE_URL


@pytest.fixture
async def authed_client(auth_headers: dict) -> httpx.AsyncClient:
    """Per-test client pre-loaded with admin auth headers."""
    async with httpx.AsyncClient(
        base_url=API_BASE_URL,
        headers=auth_headers,
        timeout=30.0,
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_list_inspections_empty(authed_client: httpx.AsyncClient):
    """GET /api/v1/inspections on a fresh DB returns 200 with an empty items list."""
    response = await authed_client.get("/api/v1/inspections")
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}: {response.text}"
    )
    data = response.json()
    # Accept both paginated {"items": [], "total": 0} and plain list []
    if isinstance(data, dict):
        items = data.get("items", data.get("results", []))
    else:
        items = data
    assert isinstance(items, list), f"Expected items to be a list, got: {type(items)}"


@pytest.mark.asyncio
async def test_list_inspections_pagination(authed_client: httpx.AsyncClient):
    """Insert 25 test records and paginate with page=1&size=10 — expect 10 items and total=25."""
    # Insert 25 records via the API (POST /api/v1/inspections)
    created_ids = []
    for i in range(25):
        payload = {
            "image_url": f"s3://test-bucket/test-image-{i:03d}.png",
            "camera_id": f"cam-test-{i % 5}",
            "metadata": {"sequence": i, "test": True},
        }
        resp = await authed_client.post("/api/v1/inspections", json=payload)
        # Accept 200 or 201
        assert resp.status_code in (200, 201), (
            f"Failed to create inspection {i}: {resp.status_code} {resp.text}"
        )
        created_ids.append(resp.json().get("id"))

    try:
        # Request page 1, size 10
        list_resp = await authed_client.get(
            "/api/v1/inspections",
            params={"page": 1, "size": 10},
        )
        assert list_resp.status_code == 200
        data = list_resp.json()

        if isinstance(data, dict):
            items = data.get("items", data.get("results", []))
            total = data.get("total", data.get("count", None))
        else:
            items = data
            total = None

        assert len(items) == 10, f"Expected 10 items per page, got {len(items)}"
        if total is not None:
            assert total >= 25, f"Expected total >= 25, got {total}"
    finally:
        # Clean up created records
        for record_id in created_ids:
            if record_id:
                await authed_client.delete(f"/api/v1/inspections/{record_id}")


@pytest.mark.asyncio
async def test_get_inspection_by_id(authed_client: httpx.AsyncClient):
    """Insert a record, fetch it by ID, and assert all fields match."""
    payload = {
        "image_url": "s3://test-bucket/single-test-image.png",
        "camera_id": "cam-single-test",
        "metadata": {"purpose": "id-lookup-test"},
    }
    create_resp = await authed_client.post("/api/v1/inspections", json=payload)
    assert create_resp.status_code in (200, 201), (
        f"Failed to create inspection: {create_resp.status_code} {create_resp.text}"
    )
    created = create_resp.json()
    record_id = created.get("id")
    assert record_id, f"Created inspection has no id: {created}"

    try:
        get_resp = await authed_client.get(f"/api/v1/inspections/{record_id}")
        assert get_resp.status_code == 200, (
            f"Expected 200 fetching by id, got {get_resp.status_code}: {get_resp.text}"
        )
        fetched = get_resp.json()
        assert fetched.get("id") == record_id
        assert fetched.get("camera_id") == payload["camera_id"]
        assert fetched.get("image_url") == payload["image_url"]
    finally:
        await authed_client.delete(f"/api/v1/inspections/{record_id}")


@pytest.mark.asyncio
async def test_get_inspection_not_found(authed_client: httpx.AsyncClient):
    """GET /api/v1/inspections/{random-uuid} returns 404."""
    random_id = str(uuid.uuid4())
    response = await authed_client.get(f"/api/v1/inspections/{random_id}")
    assert response.status_code == 404, (
        f"Expected 404 for unknown inspection id, got {response.status_code}: {response.text}"
    )
