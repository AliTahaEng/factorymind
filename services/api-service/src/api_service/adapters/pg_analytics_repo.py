"""PostgreSQL analytics queries."""
from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from api_service.interfaces.i_analytics_repo import IAnalyticsRepository


class PgAnalyticsRepository(IAnalyticsRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_defect_rates(self, days: int = 7) -> list[dict[str, Any]]:
        sql = text("""
            SELECT
                date_trunc('hour', inspected_at) AS period,
                count(*) AS total,
                sum(CASE WHEN is_defective THEN 1 ELSE 0 END) AS defects,
                round(
                    100.0 * sum(CASE WHEN is_defective THEN 1 ELSE 0 END) / NULLIF(count(*), 0), 2
                ) AS defect_rate_pct
            FROM inspections
            WHERE inspected_at >= now() - make_interval(days => :days)
            GROUP BY 1
            ORDER BY 1 DESC
            LIMIT 168
        """)
        result = await self._session.execute(sql, {"days": days})
        return [dict(row._mapping) for row in result]

    async def get_model_performance(self) -> list[dict[str, Any]]:
        sql = text("""
            SELECT
                model_name, version, status, accuracy, f1_score, promoted_at, created_at
            FROM model_versions
            ORDER BY created_at DESC
            LIMIT 20
        """)
        result = await self._session.execute(sql)
        return [dict(row._mapping) for row in result]
