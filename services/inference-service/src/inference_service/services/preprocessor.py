"""Image preprocessing pipeline."""
import io
import logging
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def decode_and_preprocess(image_bytes: bytes, width: int = 640, height: int = 640) -> np.ndarray:
    """Decode JPEG/PNG bytes, resize, normalize to [0, 1] float32. Returns (H, W, 3)."""
    with Image.open(io.BytesIO(image_bytes)) as img:
        img = img.convert("RGB").resize((width, height), Image.BILINEAR)
        arr = np.array(img, dtype=np.float32) / 255.0
    return arr
