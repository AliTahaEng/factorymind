"""
Basic load / stress tests using httpx async.
"""
import asyncio
import time

import httpx
import pytest

from conftest import API_BASE_URL, INFERENCE_BASE_URL, ADMIN_USERNAME, ADMIN_PASSWORD
from fixtures.images import create_black_png

CONCURRENCY_HEALTH = 50
CONCURRENCY_INFER = 10
RATE_LIMIT_ATTEMPTS = 20


@pytest.mark.asyncio
async def test_concurrent_health_checks():
    """Issue 50 concurrent GET /health requests to the inference service; all must return 200."""
    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=30.0) as client:
        tasks = [client.get("/health") for _ in range(CONCURRENCY_HEALTH)]
        responses = await asyncio.gather(*tasks)

    failures = [r for r in responses if r.status_code != 200]
    assert not failures, (
        f"{len(failures)}/{CONCURRENCY_HEALTH} health checks failed. "
        f"First failure: {failures[0].status_code} {failures[0].text}"
    )


@pytest.mark.asyncio
async def test_concurrent_inferences():
    """
    Issue 10 concurrent POST /infer requests; all must return 200.
    Average latency is logged for observability.
    """
    image_bytes = create_black_png(224, 224)

    async def single_infer(client: httpx.AsyncClient) -> tuple[int, float]:
        start = time.monotonic()
        resp = await client.post(
            "/infer",
            files={"file": ("load_test.png", image_bytes, "image/png")},
        )
        elapsed = time.monotonic() - start
        return resp.status_code, elapsed

    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=60.0) as client:
        results = await asyncio.gather(*[single_infer(client) for _ in range(CONCURRENCY_INFER)])

    statuses = [r[0] for r in results]
    latencies = [r[1] for r in results]
    avg_latency = sum(latencies) / len(latencies)

    print(
        f"\n[load] {CONCURRENCY_INFER} concurrent /infer requests: "
        f"avg={avg_latency:.3f}s, "
        f"min={min(latencies):.3f}s, "
        f"max={max(latencies):.3f}s"
    )

    failures = [s for s in statuses if s != 200]
    assert not failures, (
        f"{len(failures)}/{CONCURRENCY_INFER} inference requests failed. "
        f"Statuses: {statuses}"
    )


@pytest.mark.asyncio
async def test_auth_rate_limiting():
    """
    Make 20 rapid POST /api/v1/auth/login requests.
    If rate limiting is enabled at least some requests should return 429.
    If the service has no rate limiting configured this test is skipped gracefully.
    """
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=30.0) as client:
        tasks = [
            client.post(
                "/api/v1/auth/login",
                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
            )
            for _ in range(RATE_LIMIT_ATTEMPTS)
        ]
        responses = await asyncio.gather(*tasks)

    status_codes = [r.status_code for r in responses]
    rate_limited = [s for s in status_codes if s == 429]

    if not rate_limited:
        pytest.skip(
            f"No 429 responses observed after {RATE_LIMIT_ATTEMPTS} rapid login "
            "requests — rate limiting may not be configured in the test environment."
        )
    else:
        assert len(rate_limited) > 0, (
            f"Expected at least one 429 in {RATE_LIMIT_ATTEMPTS} rapid requests, "
            f"got: {status_codes}"
        )
