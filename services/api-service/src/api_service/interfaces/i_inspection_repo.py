"""Interface for inspection repository."""
from abc import ABC, abstractmethod
from typing import Sequence
from api_service.models.db_models import Inspection


class IInspectionRepository(ABC):
    @abstractmethod
    async def save(self, inspection: Inspection) -> Inspection:
        ...

    @abstractmethod
    async def get_by_id(self, inspection_id: str) -> Inspection | None:
        ...

    @abstractmethod
    async def list_recent(self, limit: int = 50, offset: int = 0) -> Sequence[Inspection]:
        ...
