"""Pydantic models for inference results."""
from pydantic import BaseModel


class BoundingBox(BaseModel):
    x: float
    y: float
    w: float
    h: float
    label: str
    confidence: float


class InferenceResult(BaseModel):
    image_id: str
    inspection_id: str
    defect_detected: bool
    defect_type: str | None = None
    confidence: float
    anomaly_score: float
    bounding_boxes: list[BoundingBox] = []
    model_version: str = "ensemble-v1"
    processing_time_ms: int
    timestamp: int
