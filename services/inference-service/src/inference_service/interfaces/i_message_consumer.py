"""Abstract interface for message consumers."""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator


@dataclass
class ConsumedMessage:
    key: bytes | None
    value: bytes
    topic: str
    partition: int
    offset: int


class IMessageConsumer(ABC):
    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def stop(self) -> None:
        ...

    @abstractmethod
    def messages(self) -> AsyncIterator[ConsumedMessage]:
        ...
