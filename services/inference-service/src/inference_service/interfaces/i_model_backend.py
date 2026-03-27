"""Abstract interface for ML model backends."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
import numpy as np


@dataclass
class ModelInput:
    image: np.ndarray  # shape (H, W, 3), dtype float32, values in [0, 1]
    model_name: str
    request_id: str


@dataclass
class ModelOutput:
    model_name: str
    request_id: str
    raw_outputs: dict[str, Any] = field(default_factory=dict)
    # Parsed fields populated by EnsembleService
    defect_detected: bool = False
    confidence: float = 0.0
    anomaly_score: float = 0.0
    bounding_boxes: list[dict] = field(default_factory=list)
    latency_ms: float = 0.0


class IModelBackend(ABC):
    @abstractmethod
    async def infer(self, model_input: ModelInput) -> ModelOutput:
        """Run inference and return structured output."""
        ...

    @abstractmethod
    async def health_check(self) -> bool:
        """Return True if backend is reachable."""
        ...
