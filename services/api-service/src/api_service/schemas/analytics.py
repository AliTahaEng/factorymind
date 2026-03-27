"""Analytics schemas."""
from datetime import datetime
from pydantic import BaseModel
from typing import Any


class DefectRatePoint(BaseModel):
    period: datetime | str
    total: int
    defects: int
    defect_rate_pct: float | None


class DefectRateSummary(BaseModel):
    data: list[DefectRatePoint]
    days: int


class ModelPerformanceSummary(BaseModel):
    models: list[dict[str, Any]]
