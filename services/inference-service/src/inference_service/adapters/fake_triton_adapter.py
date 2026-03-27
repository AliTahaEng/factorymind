"""Fake Triton adapter — returns synthetic results for testing and when Triton is unavailable."""
import time
import random
from inference_service.interfaces.i_model_backend import IModelBackend, ModelInput, ModelOutput


class FakeTritonAdapter(IModelBackend):
    """Returns deterministic synthetic inference results without a real Triton server."""

    def __init__(self, defect_probability: float = 0.1):
        self._defect_probability = defect_probability

    async def infer(self, model_input: ModelInput) -> ModelOutput:
        start = time.perf_counter()
        is_defect = random.random() < self._defect_probability
        confidence = random.uniform(0.7, 0.99) if is_defect else random.uniform(0.01, 0.3)
        anomaly = random.uniform(0.6, 0.95) if is_defect else random.uniform(0.01, 0.35)
        boxes = []
        if is_defect:
            boxes = [{"x": 0.2, "y": 0.3, "w": 0.1, "h": 0.1, "label": "scratch", "confidence": confidence}]
        latency = (time.perf_counter() - start) * 1000
        return ModelOutput(
            model_name=model_input.model_name,
            request_id=model_input.request_id,
            defect_detected=is_defect,
            confidence=confidence,
            anomaly_score=anomaly,
            bounding_boxes=boxes,
            latency_ms=latency,
        )

    async def health_check(self) -> bool:
        return True
