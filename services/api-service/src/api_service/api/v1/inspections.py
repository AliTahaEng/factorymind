"""Inspection history endpoints."""
from fastapi import APIRouter, Query, Depends
from api_service.schemas.inspection import InspectionRead, InspectionList
from api_service.container import get_container
from api_service.api.deps import get_current_user

router = APIRouter(prefix="/inspections", tags=["inspections"])


@router.get("", response_model=InspectionList)
async def list_inspections(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    current_user: dict = Depends(get_current_user),
):
    container = get_container()
    offset = (page - 1) * page_size
    async with container.session_factory() as session:
        from api_service.adapters.pg_inspection_repo import PgInspectionRepository
        repo = PgInspectionRepository(session)
        items = await repo.list_recent(limit=page_size, offset=offset)
        return InspectionList(
            items=[InspectionRead.model_validate(i) for i in items],
            total=len(items),
            page=page,
            page_size=page_size,
        )


@router.get("/{inspection_id}", response_model=InspectionRead)
async def get_inspection(
    inspection_id: str,
    current_user: dict = Depends(get_current_user),
):
    container = get_container()
    async with container.session_factory() as session:
        from api_service.adapters.pg_inspection_repo import PgInspectionRepository
        from fastapi import HTTPException
        repo = PgInspectionRepository(session)
        item = await repo.get_by_id(inspection_id)
        if not item:
            raise HTTPException(status_code=404, detail="Inspection not found")
        return InspectionRead.model_validate(item)
