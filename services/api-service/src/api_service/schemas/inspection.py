"""Inspection schemas."""
from datetime import datetime
from pydantic import BaseModel


class BoundingBoxRead(BaseModel):
    x: float
    y: float
    w: float
    h: float
    label: str
    confidence: float


class InspectionRead(BaseModel):
    inspection_id: str
    image_id: str
    camera_id: str
    product_id: str | None
    is_defective: bool
    defect_score: float
    anomaly_score: float
    classification_label: str | None
    bounding_boxes: list[BoundingBoxRead] = []
    processing_time_ms: int
    model_version: str | None
    inspected_at: datetime

    class Config:
        from_attributes = True


class InspectionList(BaseModel):
    items: list[InspectionRead]
    total: int
    page: int
    page_size: int
