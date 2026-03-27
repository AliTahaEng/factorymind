"""Background Kafka consumer worker: consume raw-inspections → infer → publish processed-results."""
import asyncio
import io
import logging
import time

import fastavro

from inference_service.interfaces.i_message_consumer import IMessageConsumer
from inference_service.interfaces.i_message_publisher import IMessagePublisher
from inference_service.services.ensemble_service import EnsembleInferenceService

logger = logging.getLogger(__name__)

# Avro schemas for deserializing input and serializing output
_RAW_SCHEMA = {
    "type": "record", "name": "RawInspection", "namespace": "com.factorymind",
    "fields": [
        {"name": "image_id", "type": "string"},
        {"name": "camera_id", "type": "string"},
        {"name": "product_category", "type": "string"},
        {"name": "image_bytes", "type": "bytes"},
        {"name": "timestamp", "type": "long"},
        {"name": "conveyor_speed", "type": "float", "default": 1.0},
    ],
}

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

_PARSED_RAW_SCHEMA = fastavro.parse_schema(_RAW_SCHEMA)
_PARSED_RESULT_SCHEMA = fastavro.parse_schema(_RESULT_SCHEMA)


class ConsumerWorker:
    def __init__(
        self,
        consumer: IMessageConsumer,
        publisher: IMessagePublisher,
        ensemble: EnsembleInferenceService,
        output_topic: str,
    ):
        self._consumer = consumer
        self._publisher = publisher
        self._ensemble = ensemble
        self._output_topic = output_topic
        self._running = False

    async def start(self) -> None:
        await self._consumer.start()
        self._running = True
        asyncio.create_task(self._process_loop())
        logger.info("ConsumerWorker started")

    async def stop(self) -> None:
        self._running = False
        await self._consumer.stop()
        await self._publisher.flush()
        logger.info("ConsumerWorker stopped")

    async def _process_loop(self) -> None:
        async for msg in self._consumer.messages():
            if not self._running:
                break
            try:
                record = fastavro.schemaless_reader(io.BytesIO(msg.value), _PARSED_RAW_SCHEMA)
                result = await self._ensemble.run(record["image_id"], record["image_bytes"])
                buf = io.BytesIO()
                fastavro.schemaless_writer(buf, _PARSED_RESULT_SCHEMA, {
                    "image_id": result.image_id,
                    "inspection_id": result.inspection_id,
                    "defect_detected": result.defect_detected,
                    "defect_type": result.defect_type,
                    "confidence": result.confidence,
                    "anomaly_score": result.anomaly_score,
                    "bounding_boxes": [b.model_dump() for b in result.bounding_boxes],
                    "model_version": result.model_version,
                    "processing_time_ms": result.processing_time_ms,
                    "timestamp": result.timestamp,
                })
                await self._publisher.publish(
                    topic=self._output_topic,
                    key=record["image_id"].encode(),
                    value=buf.getvalue(),
                )
            except Exception as exc:
                logger.error("Error processing message: %s", exc, exc_info=True)
