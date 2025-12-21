"""CRUD operations for AgentDesk model."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.agent_desk import AgentDesk
from ..schemas.agent_desk import DeskCreate, DeskUpdate
from .base import CRUDBase


class CRUDAgentDesk(CRUDBase[AgentDesk, DeskCreate, DeskUpdate]):
    """CRUD operations for AgentDesk with custom methods."""

    async def get_by_desk_id(
        self,
        session: AsyncSession,
        desk_id: str
    ) -> Optional[AgentDesk]:
        """
        Get desk by desk_id string.

        Args:
            session: Database session
            desk_id: Desk ID string (e.g., 'cto-001')

        Returns:
            AgentDesk instance or None
        """
        result = await session.execute(
            select(AgentDesk).where(AgentDesk.desk_id == desk_id)
        )
        return result.scalar_one_or_none()

    async def get_subordinates(
        self,
        session: AsyncSession,
        desk_id: UUID
    ) -> List[AgentDesk]:
        """
        Get all direct subordinates of a desk.

        Args:
            session: Database session
            desk_id: Manager desk UUID

        Returns:
            List of subordinate AgentDesk instances
        """
        result = await session.execute(
            select(AgentDesk)
            .where(AgentDesk.reports_to_id == desk_id)
            .options(selectinload(AgentDesk.team))
        )
        return list(result.scalars().all())

    async def get_hierarchy_chain(
        self,
        session: AsyncSession,
        desk_id: UUID
    ) -> List[AgentDesk]:
        """
        Get the reporting chain from desk to top.

        Args:
            session: Database session
            desk_id: Starting desk UUID

        Returns:
            List of AgentDesk instances in hierarchy (bottom to top)
        """
        chain = []
        current_desk = await self.get(session, desk_id)

        while current_desk:
            chain.append(current_desk)
            if current_desk.reports_to_id:
                current_desk = await self.get(session, current_desk.reports_to_id)
            else:
                break

        return chain

    async def get_by_role(
        self,
        session: AsyncSession,
        role: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentDesk]:
        """
        Get desks by role.

        Args:
            session: Database session
            role: AgentRole enum value
            skip: Offset
            limit: Limit

        Returns:
            List of AgentDesk instances
        """
        result = await session.execute(
            select(AgentDesk)
            .where(AgentDesk.role == role)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_team(
        self,
        session: AsyncSession,
        team_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AgentDesk]:
        """
        Get desks by team.

        Args:
            session: Database session
            team_id: Team UUID
            skip: Offset
            limit: Limit

        Returns:
            List of AgentDesk instances
        """
        result = await session.execute(
            select(AgentDesk)
            .where(AgentDesk.team_id == team_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())


# Create singleton instance
agent_desk = CRUDAgentDesk(AgentDesk)
