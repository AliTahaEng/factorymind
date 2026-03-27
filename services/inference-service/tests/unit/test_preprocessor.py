"""Test image preprocessing."""
import io
import numpy as np
import pytest
from PIL import Image

from inference_service.services.preprocessor import decode_and_preprocess


def _make_jpeg(width=100, height=100) -> bytes:
    img = Image.new("RGB", (width, height), color=(128, 64, 32))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_decode_returns_correct_shape():
    jpeg = _make_jpeg(200, 150)
    arr = decode_and_preprocess(jpeg, width=640, height=640)
    assert arr.shape == (640, 640, 3)


def test_decode_normalizes_to_0_1():
    jpeg = _make_jpeg()
    arr = decode_and_preprocess(jpeg)
    assert arr.dtype == np.float32
    assert arr.min() >= 0.0
    assert arr.max() <= 1.0
