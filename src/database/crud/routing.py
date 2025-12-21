"""CRUD operations for TaskRoutingRule model."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.routing import TaskRoutingRule
from ..schemas.routing import TaskRoutingRuleCreate, TaskRoutingRuleUpdate
from .base import CRUDBase


class CRUDTaskRoutingRule(CRUDBase[TaskRoutingRule, TaskRoutingRuleCreate, TaskRoutingRuleUpdate]):
    """CRUD operations for TaskRoutingRule with custom methods."""

    async def get_by_rule_id(
        self,
        session: AsyncSession,
        rule_id: str
    ) -> Optional[TaskRoutingRule]:
        """
        Get routing rule by rule_id string.

        Args:
            session: Database session
            rule_id: Rule ID string

        Returns:
            TaskRoutingRule instance or None
        """
        result = await session.execute(
            select(TaskRoutingRule).where(TaskRoutingRule.rule_id == rule_id)
        )
        return result.scalar_one_or_none()

    async def get_active_rules(
        self,
        session: AsyncSession
    ) -> List[TaskRoutingRule]:
        """
        Get all active routing rules ordered by priority.

        Args:
            session: Database session

        Returns:
            List of TaskRoutingRule instances
        """
        result = await session.execute(
            select(TaskRoutingRule)
            .where(TaskRoutingRule.deleted_at.is_(None))
            .order_by(TaskRoutingRule.rule_priority.desc())
        )
        return list(result.scalars().all())


# Create singleton instance
task_routing_rule = CRUDTaskRoutingRule(TaskRoutingRule)
