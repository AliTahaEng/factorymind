"""
E2E tests for the inference service endpoints.
"""
import pytest
import httpx

from conftest import INFERENCE_BASE_URL
from fixtures.images import create_black_png


@pytest.fixture
async def infer_client() -> httpx.AsyncClient:
    """Per-test async client pointed at the inference service."""
    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=30.0) as client:
        yield client


@pytest.mark.asyncio
async def test_health_check(infer_client: httpx.AsyncClient):
    """GET /health returns 200 and {"status": "ok"}."""
    response = await infer_client.get("/health")
    assert response.status_code == 200, (
        f"Expected 200 from /health, got {response.status_code}: {response.text}"
    )
    data = response.json()
    assert data.get("status") == "ok", f"Expected status=ok, got: {data}"


@pytest.mark.asyncio
async def test_readiness_check(infer_client: httpx.AsyncClient):
    """GET /ready returns 200."""
    response = await infer_client.get("/ready")
    assert response.status_code == 200, (
        f"Expected 200 from /ready, got {response.status_code}: {response.text}"
    )


@pytest.mark.asyncio
async def test_infer_with_fake_image(infer_client: httpx.AsyncClient):
    """POST /infer with a 100x100 black PNG returns defect_probability, has_defect, defects."""
    image_bytes = create_black_png(width=100, height=100)

    response = await infer_client.post(
        "/infer",
        files={"file": ("test.png", image_bytes, "image/png")},
    )
    assert response.status_code == 200, (
        f"Expected 200 from /infer, got {response.status_code}: {response.text}"
    )
    data = response.json()

    assert "defect_probability" in data, f"Missing defect_probability in: {data}"
    assert "has_defect" in data, f"Missing has_defect in: {data}"
    assert "defects" in data, f"Missing defects in: {data}"

    assert isinstance(data["defect_probability"], (int, float)), (
        f"defect_probability should be numeric, got: {type(data['defect_probability'])}"
    )
    assert 0.0 <= data["defect_probability"] <= 1.0, (
        f"defect_probability out of range [0,1]: {data['defect_probability']}"
    )
    assert isinstance(data["has_defect"], bool), (
        f"has_defect should be bool, got: {type(data['has_defect'])}"
    )
    assert isinstance(data["defects"], list), (
        f"defects should be a list, got: {type(data['defects'])}"
    )


@pytest.mark.asyncio
async def test_metrics_endpoint(infer_client: httpx.AsyncClient):
    """GET /metrics returns 200 with Prometheus text format."""
    response = await infer_client.get("/metrics")
    assert response.status_code == 200, (
        f"Expected 200 from /metrics, got {response.status_code}: {response.text}"
    )
    content_type = response.headers.get("content-type", "")
    body = response.text
    # Prometheus text format starts with # HELP or # TYPE lines
    assert "# HELP" in body or "# TYPE" in body or "text/plain" in content_type, (
        f"Response does not look like Prometheus text format. "
        f"Content-Type: {content_type}, body[:200]: {body[:200]}"
    )
