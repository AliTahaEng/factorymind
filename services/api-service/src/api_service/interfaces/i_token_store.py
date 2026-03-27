"""Interface for token blacklist store."""
from abc import ABC, abstractmethod


class ITokenStore(ABC):
    @abstractmethod
    async def blacklist(self, token: str, ttl_seconds: int) -> None:
        ...

    @abstractmethod
    async def is_blacklisted(self, token: str) -> bool:
        ...
