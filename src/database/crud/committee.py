"""CRUD operations for Committee model."""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.committee import Committee
from ..schemas.committee import CommitteeCreate, CommitteeUpdate
from .base import CRUDBase


class CRUDCommittee(CRUDBase[Committee, CommitteeCreate, CommitteeUpdate]):
    """CRUD operations for Committee with custom methods."""

    async def get_by_committee_id(
        self,
        session: AsyncSession,
        committee_id: str
    ) -> Optional[Committee]:
        """
        Get committee by committee_id string.

        Args:
            session: Database session
            committee_id: Committee ID string

        Returns:
            Committee instance or None
        """
        result = await session.execute(
            select(Committee).where(Committee.committee_id == committee_id)
        )
        return result.scalar_one_or_none()

    async def get_with_members(
        self,
        session: AsyncSession,
        committee_id: UUID
    ) -> Optional[Committee]:
        """
        Get committee with members loaded.

        Args:
            session: Database session
            committee_id: Committee UUID

        Returns:
            Committee instance with members or None
        """
        result = await session.execute(
            select(Committee)
            .where(Committee.id == committee_id)
            .options(selectinload(Committee.members))
        )
        return result.scalar_one_or_none()


# Create singleton instance
committee = CRUDCommittee(Committee)
