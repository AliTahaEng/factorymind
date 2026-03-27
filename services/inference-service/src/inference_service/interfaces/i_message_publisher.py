"""Abstract interface for message publishers."""
from abc import ABC, abstractmethod


class IMessagePublisher(ABC):
    @abstractmethod
    async def publish(self, topic: str, key: bytes, value: bytes) -> None:
        ...

    @abstractmethod
    async def flush(self) -> None:
        ...
