"""CRUD operations for Metric model."""

from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.metric import Metric
from ..schemas.metric import MetricCreate, MetricUpdate
from .base import CRUDBase


class CRUDMetric(CRUDBase[Metric, MetricCreate, MetricUpdate]):
    """CRUD operations for Metric with custom methods."""

    async def get_by_metric_id(
        self,
        session: AsyncSession,
        metric_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Metric]:
        """
        Get metrics by metric_id (time-series).

        Args:
            session: Database session
            metric_id: Metric ID string
            skip: Offset
            limit: Limit

        Returns:
            List of Metric instances ordered by creation time
        """
        result = await session.execute(
            select(Metric)
            .where(Metric.metric_id == metric_id)
            .order_by(Metric.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_type(
        self,
        session: AsyncSession,
        metric_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Metric]:
        """
        Get metrics by type.

        Args:
            session: Database session
            metric_type: Metric type (counter, gauge, etc.)
            skip: Offset
            limit: Limit

        Returns:
            List of Metric instances
        """
        result = await session.execute(
            select(Metric)
            .where(Metric.metric_type == metric_type)
            .order_by(Metric.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# Create singleton instance
metric = CRUDMetric(Metric)
