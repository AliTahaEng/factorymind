"""PostgreSQL implementation of IInspectionRepository."""
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from api_service.interfaces.i_inspection_repo import IInspectionRepository
from api_service.models.db_models import Inspection


class PgInspectionRepository(IInspectionRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def save(self, inspection: Inspection) -> Inspection:
        self._session.add(inspection)
        await self._session.flush()
        await self._session.refresh(inspection)
        return inspection

    async def get_by_id(self, inspection_id: str) -> Inspection | None:
        result = await self._session.execute(
            select(Inspection).where(Inspection.inspection_id == inspection_id)
        )
        return result.scalar_one_or_none()

    async def list_recent(self, limit: int = 50, offset: int = 0) -> Sequence[Inspection]:
        result = await self._session.execute(
            select(Inspection).order_by(desc(Inspection.inspected_at)).offset(offset).limit(limit)
        )
        return result.scalars().all()
