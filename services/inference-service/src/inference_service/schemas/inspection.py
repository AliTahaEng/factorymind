"""Pydantic models for incoming inspection messages."""
from pydantic import BaseModel


class InspectionMessage(BaseModel):
    image_id: str
    camera_id: str
    product_category: str
    image_bytes: bytes
    timestamp: int
    conveyor_speed: float = 1.0
