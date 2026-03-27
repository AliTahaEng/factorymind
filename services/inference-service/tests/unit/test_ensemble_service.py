"""Test ensemble inference with fake adapters."""
import asyncio
import io
import numpy as np
import pytest
from PIL import Image

from inference_service.adapters.fake_triton_adapter import FakeTritonAdapter
from inference_service.services.ensemble_service import EnsembleInferenceService


def _make_jpeg() -> bytes:
    img = Image.new("RGB", (100, 100), color=(50, 100, 150))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
def ensemble():
    fake = FakeTritonAdapter(defect_probability=0.0)  # always healthy, never defect
    return EnsembleInferenceService(
        yolo_backend=fake,
        vit_backend=fake,
        anomaly_backend=fake,
    )


@pytest.mark.asyncio
async def test_ensemble_returns_result(ensemble):
    jpeg = _make_jpeg()
    result = await ensemble.run("img-001", jpeg)
    assert result.image_id == "img-001"
    assert isinstance(result.defect_detected, bool)
    assert 0.0 <= result.confidence <= 1.0
    assert result.processing_time_ms >= 0


@pytest.mark.asyncio
async def test_ensemble_always_defect():
    fake = FakeTritonAdapter(defect_probability=1.0)
    svc = EnsembleInferenceService(
        yolo_backend=fake,
        vit_backend=fake,
        anomaly_backend=fake,
        yolo_conf_threshold=0.0,
        anomaly_threshold=0.0,
        vit_threshold=0.0,
    )
    result = await svc.run("img-002", _make_jpeg())
    assert result.defect_detected is True
