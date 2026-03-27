"""Analytics endpoints."""
from fastapi import APIRouter, Query, Depends
from api_service.schemas.analytics import DefectRateSummary, DefectRatePoint, ModelPerformanceSummary
from api_service.container import get_container
from api_service.api.deps import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/defect-rates", response_model=DefectRateSummary)
async def defect_rates(
    days: int = Query(7, ge=1, le=90),
    current_user: dict = Depends(get_current_user),
):
    container = get_container()
    async with container.session_factory() as session:
        from api_service.adapters.pg_analytics_repo import PgAnalyticsRepository
        repo = PgAnalyticsRepository(session)
        data = await repo.get_defect_rates(days=days)
        return DefectRateSummary(
            data=[DefectRatePoint(**row) for row in data],
            days=days,
        )


@router.get("/model-performance", response_model=ModelPerformanceSummary)
async def model_performance(current_user: dict = Depends(get_current_user)):
    container = get_container()
    async with container.session_factory() as session:
        from api_service.adapters.pg_analytics_repo import PgAnalyticsRepository
        repo = PgAnalyticsRepository(session)
        data = await repo.get_model_performance()
        return ModelPerformanceSummary(models=data)
