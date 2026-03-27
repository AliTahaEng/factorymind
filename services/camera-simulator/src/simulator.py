"""Camera simulator — reads MVTec AD images and publishes to Kafka."""
import io
import logging
import time
import uuid
from pathlib import Path

import fastavro
from confluent_kafka import Producer
from PIL import Image

from src.config import Settings
from src.schemas import RAW_INSPECTION_SCHEMA

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

_PARSED_SCHEMA = fastavro.parse_schema(RAW_INSPECTION_SCHEMA)


def _delivery_report(err: object, msg: object) -> None:
    if err:
        logger.error("Message delivery failed: %s", err)


def _build_producer(settings: Settings) -> Producer:
    return Producer(
        {
            "bootstrap.servers": settings.kafka_bootstrap_servers,
            "queue.buffering.max.messages": 10_000,
            "queue.buffering.max.kbytes": 65_536,
            "batch.num.messages": 500,
            "linger.ms": 20,
        }
    )


def _image_to_bytes(path: Path, target_size: tuple[int, int] = (640, 640)) -> bytes:
    """Load image, resize, return JPEG bytes."""
    with Image.open(path) as img:
        img = img.convert("RGB").resize(target_size)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=85)
        return buf.getvalue()


def _collect_images(data_path: Path) -> list[tuple[str, Path]]:
    """Walk MVTec-style directory and return (category, path) pairs."""
    pairs: list[tuple[str, Path]] = []
    if not data_path.exists():
        logger.warning("MVTec data path %s not found — using synthetic images", data_path)
        return pairs
    for category_dir in sorted(data_path.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name
        for split in ["train", "test"]:
            split_dir = category_dir / split
            if not split_dir.exists():
                continue
            for class_dir in sorted(split_dir.iterdir()):
                if not class_dir.is_dir():
                    continue
                for img_path in sorted(class_dir.glob("*.png")):
                    pairs.append((category, img_path))
                for img_path in sorted(class_dir.glob("*.jpg")):
                    pairs.append((category, img_path))
    return pairs


def _make_synthetic_image() -> bytes:
    """Return a 640x640 synthetic JPEG — used when no MVTec data is present."""
    import random
    # Simple gradient image without numpy dependency
    img = Image.new("RGB", (640, 640), color=(
        random.randint(100, 200),
        random.randint(100, 200),
        random.randint(100, 200),
    ))
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=85)
    return buf.getvalue()


def run() -> None:
    settings = Settings()
    producer = _build_producer(settings)
    data_path = Path(settings.mvtec_data_path)
    images = _collect_images(data_path)

    if not images:
        logger.warning("No MVTec images found — generating synthetic images continuously")

    interval = 1.0 / max(settings.images_per_second, 0.01)
    count = 0

    logger.info(
        "Camera simulator starting | camera=%s | rate=%.1f fps | images=%d",
        settings.camera_id,
        settings.images_per_second,
        len(images),
    )

    while True:
        if images:
            idx = count % len(images)
            category, img_path = images[idx]
            try:
                img_bytes = _image_to_bytes(img_path)
            except Exception as exc:
                logger.warning("Failed to read %s: %s", img_path, exc)
                count += 1
                continue
        else:
            category = "synthetic"
            img_bytes = _make_synthetic_image()

        record = {
            "image_id": str(uuid.uuid4()),
            "camera_id": settings.camera_id,
            "product_category": category,
            "image_bytes": img_bytes,
            "timestamp": int(time.time() * 1000),
            "conveyor_speed": 1.0,
        }

        buf = io.BytesIO()
        fastavro.schemaless_writer(buf, _PARSED_SCHEMA, record)

        producer.produce(
            topic="raw-inspections",
            key=record["image_id"].encode(),
            value=buf.getvalue(),
            callback=_delivery_report,
        )
        producer.poll(0)

        count += 1
        if count % 100 == 0:
            logger.info("Published %d images", count)

        time.sleep(interval)


if __name__ == "__main__":
    run()
