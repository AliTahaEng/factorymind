"""FastAPI route handlers for inference service."""
import io
import logging
import time

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from pydantic import BaseModel

from inference_service.schemas.result import InferenceResult

logger = logging.getLogger(__name__)

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str = "0.1.0"


class InferRequest(BaseModel):
    image_id: str
    image_bytes: bytes  # base64 or raw bytes


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok")


@router.get("/ready", response_model=HealthResponse)
async def ready():
    return HealthResponse(status="ready")


@router.post("/infer", response_model=InferenceResult)
async def infer_endpoint(file: UploadFile = File(...)):
    """Accept an uploaded image file and run ensemble inference."""
    from fastapi import Request
    image_bytes = await file.read()
    # Retrieve ensemble service from app state
    from starlette.requests import Request as StarletteRequest
    # We'll access the container via a global for simplicity
    from inference_service.container import get_container
    container = get_container()
    try:
        result = await container.ensemble.run(
            image_id=f"upload-{int(time.time() * 1000)}",
            image_bytes=image_bytes,
        )
        return result
    except Exception as exc:
        logger.error("Inference error: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    from fastapi.responses import Response
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
