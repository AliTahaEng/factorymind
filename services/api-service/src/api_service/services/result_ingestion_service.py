"""Background Kafka consumer that writes processed-results to PostgreSQL."""
import asyncio
import io
import logging
from datetime import datetime, timezone

import fastavro
from confluent_kafka import Consumer, KafkaError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from api_service.models.db_models import Inspection

logger = logging.getLogger(__name__)

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


class ResultIngestionService:
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str, session_factory: async_sessionmaker):
        self._config = {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
        self._topic = topic
        self._session_factory = session_factory
        self._running = False
        self._consumer: Consumer | None = None

    async def start(self) -> None:
        self._consumer = Consumer(self._config)
        self._consumer.subscribe([self._topic])
        self._running = True
        asyncio.create_task(self._consume_loop())
        logger.info("ResultIngestionService started consuming %s", self._topic)

    async def stop(self) -> None:
        self._running = False
        if self._consumer:
            self._consumer.close()

    async def _consume_loop(self) -> None:
        loop = asyncio.get_event_loop()
        while self._running:
            msg = await loop.run_in_executor(None, lambda: self._consumer.poll(timeout=1.0))
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                logger.error("Kafka error: %s", msg.error())
                continue
            try:
                record = fastavro.schemaless_reader(io.BytesIO(msg.value()), _PARSED_SCHEMA)
                async with self._session_factory() as session:
                    inspection = Inspection(
                        inspection_id=record["inspection_id"],
                        image_id=record["image_id"],
                        camera_id="unknown",
                        is_defective=record["defect_detected"],
                        defect_score=record["confidence"],
                        anomaly_score=record["anomaly_score"],
                        classification_label=record.get("defect_type"),
                        bounding_boxes=record.get("bounding_boxes", []),
                        processing_time_ms=record["processing_time_ms"],
                        model_version=record["model_version"],
                    )
                    session.add(inspection)
                    await session.commit()
            except Exception as exc:
                logger.error("Error ingesting result: %s", exc, exc_info=True)
