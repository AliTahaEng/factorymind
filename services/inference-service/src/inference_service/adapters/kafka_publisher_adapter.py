"""Kafka publisher adapter wrapping confluent-kafka Producer."""
import asyncio
import logging

from confluent_kafka import Producer

from inference_service.interfaces.i_message_publisher import IMessagePublisher

logger = logging.getLogger(__name__)


class KafkaPublisherAdapter(IMessagePublisher):
    def __init__(self, bootstrap_servers: str):
        self._producer = Producer({
            "bootstrap.servers": bootstrap_servers,
            "queue.buffering.max.messages": 10_000,
            "linger.ms": 10,
        })

    async def publish(self, topic: str, key: bytes, value: bytes) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(
            None,
            lambda: self._producer.produce(topic=topic, key=key, value=value)
        )
        self._producer.poll(0)

    async def flush(self) -> None:
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, lambda: self._producer.flush(timeout=10))
