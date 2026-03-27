"""
Data drift simulation tests.

These tests use FakeTritonAdapter (ENABLE_TRITON=false), so they validate response
structure rather than actual model drift detection. The structure verifies that if a
real model were in place, drift signals could be captured from the same response fields.
"""
import asyncio
import io
import random

import httpx
import pytest

from conftest import INFERENCE_BASE_URL
from fixtures.images import create_black_png, create_white_png, create_random_png


def _make_infer_request(
    client: httpx.AsyncClient,
    image_bytes: bytes,
    filename: str = "drift_test.png",
) -> "asyncio.coroutines":
    return client.post(
        "/infer",
        files={"file": (filename, image_bytes, "image/png")},
    )


def _assert_valid_response(data: dict) -> None:
    """Assert that an /infer response has the expected structure."""
    assert "defect_probability" in data, f"Missing defect_probability: {data}"
    assert "has_defect" in data, f"Missing has_defect: {data}"
    assert "defects" in data, f"Missing defects: {data}"
    assert 0.0 <= data["defect_probability"] <= 1.0, (
        f"defect_probability out of range: {data['defect_probability']}"
    )
    assert isinstance(data["has_defect"], bool)
    assert isinstance(data["defects"], list)


@pytest.mark.asyncio
async def test_defect_rate_baseline():
    """
    Send 100 'normal' (black / low-entropy) images through /infer.
    With FakeTritonAdapter the avg defect_probability should be deterministic;
    we assert it stays below 0.3 to confirm the fake adapter is not artificially
    inflating rates for clean images.
    """
    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=30.0) as client:
        tasks = [
            _make_infer_request(client, create_black_png(224, 224))
            for _ in range(100)
        ]
        responses = await asyncio.gather(*tasks)

    probabilities = []
    for resp in responses:
        assert resp.status_code == 200, (
            f"Expected 200, got {resp.status_code}: {resp.text}"
        )
        data = resp.json()
        _assert_valid_response(data)
        probabilities.append(data["defect_probability"])

    avg_prob = sum(probabilities) / len(probabilities)
    assert avg_prob < 0.3, (
        f"Average defect_probability for baseline images is {avg_prob:.4f}, "
        "expected < 0.3 for normal images."
    )


@pytest.mark.asyncio
async def test_defect_rate_drift():
    """
    Send 100 'defective' images (white, high-brightness).
    With FakeTritonAdapter we cannot assert true drift detection, but we validate
    that all responses conform to the expected structure — a prerequisite for real
    drift monitoring.
    """
    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=30.0) as client:
        tasks = [
            _make_infer_request(client, create_white_png(224, 224), "defective.png")
            for _ in range(100)
        ]
        responses = await asyncio.gather(*tasks)

    for i, resp in enumerate(responses):
        assert resp.status_code == 200, (
            f"Request {i} failed: {resp.status_code} {resp.text}"
        )
        _assert_valid_response(resp.json())


@pytest.mark.asyncio
async def test_pixel_distribution_shift():
    """
    Send images with varying brightness levels (from black to white, and random).
    Assert that all responses have a valid structure regardless of pixel distribution.
    """
    async with httpx.AsyncClient(base_url=INFERENCE_BASE_URL, timeout=30.0) as client:
        image_variants = (
            [create_black_png(224, 224)] * 10
            + [create_white_png(224, 224)] * 10
            + [create_random_png(224, 224) for _ in range(10)]
        )
        tasks = [
            _make_infer_request(client, img, f"brightness_{i}.png")
            for i, img in enumerate(image_variants)
        ]
        responses = await asyncio.gather(*tasks)

    for i, resp in enumerate(responses):
        assert resp.status_code == 200, (
            f"Request {i} failed: {resp.status_code} {resp.text}"
        )
        data = resp.json()
        _assert_valid_response(data)
        # Additional structural checks
        assert isinstance(data["defect_probability"], (int, float))
        assert isinstance(data["defects"], list)
