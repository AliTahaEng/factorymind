"""Interface for analytics repository."""
from abc import ABC, abstractmethod
from typing import Any


class IAnalyticsRepository(ABC):
    @abstractmethod
    async def get_defect_rates(self, days: int = 7) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def get_model_performance(self) -> list[dict[str, Any]]:
        ...
