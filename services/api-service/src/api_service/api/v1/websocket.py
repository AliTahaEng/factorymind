"""WebSocket live feed endpoint."""
import asyncio
import io
import json
import logging

import fastavro
from confluent_kafka import Consumer, KafkaError
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from api_service.container import get_container

logger = logging.getLogger(__name__)
router = APIRouter(tags=["websocket"])

_RESULT_SCHEMA = {
    "type": "record", "name": "ProcessedResult", "namespace": "com.factorymind",
    "fields": [
        {"name": "image_id", "type": "string"},
        {"name": "inspection_id", "type": "string"},
        {"name": "defect_detected", "type": "boolean"},
        {"name": "defect_type", "type": ["null", "string"], "default": None},
        {"name": "confidence", "type": "float"},
        {"name": "anomaly_score", "type": "float"},
        {"name": "bounding_boxes", "type": {"type": "array", "items": {
            "type": "record", "name": "BoundingBox", "fields": [
                {"name": "x", "type": "float"}, {"name": "y", "type": "float"},
                {"name": "w", "type": "float"}, {"name": "h", "type": "float"},
                {"name": "label", "type": "string"}, {"name": "confidence", "type": "float"},
            ]
        }}},
        {"name": "model_version", "type": "string"},
        {"name": "processing_time_ms", "type": "int"},
        {"name": "timestamp", "type": "long"},
    ],
}
_PARSED_SCHEMA = fastavro.parse_schema(_RESULT_SCHEMA)


@router.websocket("/ws/live-feed")
async def live_feed(websocket: WebSocket):
    await websocket.accept()
    container = get_container()
    consumer = Consumer({
        "bootstrap.servers": container.settings.kafka_bootstrap_servers,
        "group.id": f"ws-live-{id(websocket)}",
        "auto.offset.reset": "latest",
    })
    consumer.subscribe([container.settings.kafka_results_topic])
    loop = asyncio.get_event_loop()
    try:
        while True:
            msg = await loop.run_in_executor(None, lambda: consumer.poll(timeout=0.5))
            if msg is None:
                await asyncio.sleep(0.05)
                continue
            if msg.error():
                continue
            try:
                record = fastavro.schemaless_reader(io.BytesIO(msg.value()), _PARSED_SCHEMA)
                payload = {
                    "image_id": record["image_id"],
                    "inspection_id": record["inspection_id"],
                    "defect_detected": record["defect_detected"],
                    "defect_type": record.get("defect_type"),
                    "confidence": record["confidence"],
                    "anomaly_score": record["anomaly_score"],
                    "timestamp": record["timestamp"],
                }
                await websocket.send_text(json.dumps(payload))
            except Exception as exc:
                logger.warning("WS parse error: %s", exc)
    except WebSocketDisconnect:
        pass
    finally:
        consumer.close()
