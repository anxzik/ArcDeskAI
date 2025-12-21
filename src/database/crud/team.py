"""CRUD operations for Team model."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.team import Team
from ..schemas.team import TeamCreate, TeamUpdate
from .base import CRUDBase


class CRUDTeam(CRUDBase[Team, TeamCreate, TeamUpdate]):
    """CRUD operations for Team with custom methods."""

    async def get_by_team_id(
        self,
        session: AsyncSession,
        team_id: str
    ) -> Optional[Team]:
        """
        Get team by team_id string.

        Args:
            session: Database session
            team_id: Team ID string (e.g., 'backend-team')

        Returns:
            Team instance or None
        """
        result = await session.execute(
            select(Team).where(Team.team_id == team_id)
        )
        return result.scalar_one_or_none()

    async def get_with_members(
        self,
        session: AsyncSession,
        team_id: UUID
    ) -> Optional[Team]:
        """
        Get team with members loaded.

        Args:
            session: Database session
            team_id: Team UUID

        Returns:
            Team instance with members or None
        """
        result = await session.execute(
            select(Team)
            .where(Team.id == team_id)
            .options(selectinload(Team.members))
        )
        return result.scalar_one_or_none()


# Create singleton instance
team = CRUDTeam(Team)
