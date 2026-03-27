"""
Image generation helpers for FactoryMind tests.

All functions return raw PNG bytes suitable for multipart/form-data uploads.
Requires Pillow (PIL).
"""
import io
import random

from PIL import Image


def create_black_png(width: int = 224, height: int = 224) -> bytes:
    """Return bytes of a solid-black PNG of the given dimensions."""
    img = Image.new("RGB", (width, height), color=(0, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_white_png(width: int = 224, height: int = 224) -> bytes:
    """Return bytes of a solid-white PNG of the given dimensions."""
    img = Image.new("RGB", (width, height), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def create_random_png(width: int = 224, height: int = 224) -> bytes:
    """Return bytes of a PNG filled with random RGB pixel noise."""
    pixel_data = [
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        for _ in range(width * height)
    ]
    img = Image.new("RGB", (width, height))
    img.putdata(pixel_data)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()
