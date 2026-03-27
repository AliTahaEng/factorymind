"""Kafka consumer adapter wrapping confluent-kafka."""
import asyncio
import logging
from typing import AsyncIterator

from confluent_kafka import Consumer, KafkaError, KafkaException

from inference_service.interfaces.i_message_consumer import IMessageConsumer, ConsumedMessage

logger = logging.getLogger(__name__)


class KafkaConsumerAdapter(IMessageConsumer):
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str):
        self._config = {
            "bootstrap.servers": bootstrap_servers,
            "group.id": group_id,
            "auto.offset.reset": "earliest",
            "enable.auto.commit": True,
        }
        self._topic = topic
        self._consumer: Consumer | None = None
        self._running = False

    async def start(self) -> None:
        self._consumer = Consumer(self._config)
        self._consumer.subscribe([self._topic])
        self._running = True
        logger.info("Kafka consumer started on topic=%s group=%s", self._topic, self._config["group.id"])

    async def stop(self) -> None:
        self._running = False
        if self._consumer:
            self._consumer.close()
            self._consumer = None
        logger.info("Kafka consumer stopped")

    async def messages(self) -> AsyncIterator[ConsumedMessage]:
        while self._running:
            msg = await asyncio.get_event_loop().run_in_executor(
                None, lambda: self._consumer.poll(timeout=1.0)
            )
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                raise KafkaException(msg.error())
            yield ConsumedMessage(
                key=msg.key(),
                value=msg.value(),
                topic=msg.topic(),
                partition=msg.partition(),
                offset=msg.offset(),
            )
