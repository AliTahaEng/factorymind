"""Model management endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from api_service.models.db_models import ModelVersion
from api_service.container import get_container
from api_service.api.deps import require_operator
from datetime import datetime, timezone

router = APIRouter(prefix="/models", tags=["models"])


@router.get("")
async def list_models(current_user: dict = Depends(require_operator)):
    container = get_container()
    async with container.session_factory() as session:
        result = await session.execute(select(ModelVersion).order_by(ModelVersion.created_at.desc()))
        models = result.scalars().all()
        return [
            {
                "id": m.id, "model_name": m.model_name, "version": m.version,
                "status": m.status, "accuracy": m.accuracy, "f1_score": m.f1_score,
                "promoted_at": m.promoted_at, "created_at": m.created_at,
            }
            for m in models
        ]


@router.post("/{model_name}/promote", status_code=200)
async def promote_model(model_name: str, version: str, current_user: dict = Depends(require_operator)):
    container = get_container()
    async with container.session_factory() as session:
        result = await session.execute(
            select(ModelVersion).where(
                ModelVersion.model_name == model_name,
                ModelVersion.version == version,
            )
        )
        mv = result.scalar_one_or_none()
        if not mv:
            raise HTTPException(status_code=404, detail="Model version not found")
        mv.status = "production"
        mv.promoted_at = datetime.now(timezone.utc)
        await session.commit()
        return {"status": "promoted", "model_name": model_name, "version": version}


@router.post("/{model_name}/rollback", status_code=200)
async def rollback_model(model_name: str, current_user: dict = Depends(require_operator)):
    container = get_container()
    async with container.session_factory() as session:
        result = await session.execute(
            select(ModelVersion).where(
                ModelVersion.model_name == model_name,
                ModelVersion.status == "production",
            ).order_by(ModelVersion.promoted_at.desc())
        )
        current_prod = result.scalar_one_or_none()
        if current_prod:
            current_prod.status = "archived"
            await session.commit()
        return {"status": "rolled_back", "model_name": model_name}
