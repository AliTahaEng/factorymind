"""Verify Avro schemas are valid and can serialize/deserialize."""
import io
import time
import uuid

import fastavro

from src.schemas import PROCESSED_RESULT_SCHEMA, RAW_INSPECTION_SCHEMA


def test_raw_inspection_schema_serializes() -> None:
    record = {
        "image_id": str(uuid.uuid4()),
        "camera_id": "camera-01",
        "product_category": "bottle",
        "image_bytes": b"\x00\x01\x02",
        "timestamp": int(time.time() * 1000),
        "conveyor_speed": 1.5,
    }
    parsed = fastavro.parse_schema(RAW_INSPECTION_SCHEMA)
    buf = io.BytesIO()
    fastavro.schemaless_writer(buf, parsed, record)
    buf.seek(0)
    result = fastavro.schemaless_reader(buf, parsed)
    assert result["image_id"] == record["image_id"]
    assert result["product_category"] == "bottle"


def test_processed_result_schema_serializes() -> None:
    record = {
        "image_id": str(uuid.uuid4()),
        "inspection_id": str(uuid.uuid4()),
        "defect_detected": True,
        "defect_type": "scratch",
        "confidence": 0.94,
        "anomaly_score": 0.72,
        "bounding_boxes": [
            {"x": 0.1, "y": 0.2, "w": 0.3, "h": 0.4, "label": "scratch", "confidence": 0.94}
        ],
        "model_version": "v1.0.0",
        "processing_time_ms": 47,
        "timestamp": int(time.time() * 1000),
    }
    parsed = fastavro.parse_schema(PROCESSED_RESULT_SCHEMA)
    buf = io.BytesIO()
    fastavro.schemaless_writer(buf, parsed, record)
    buf.seek(0)
    result = fastavro.schemaless_reader(buf, parsed)
    assert result["defect_type"] == "scratch"
    assert abs(result["confidence"] - 0.94) < 0.001
