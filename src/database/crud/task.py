"""CRUD operations for Task and Artifact models."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.task import Task, Artifact
from ..schemas.task import TaskCreate, TaskUpdate, ArtifactCreate, ArtifactUpdate
from .base import CRUDBase


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """CRUD operations for Task with custom methods."""

    async def get_by_task_id(
        self,
        session: AsyncSession,
        task_id: str
    ) -> Optional[Task]:
        """
        Get task by task_id string.

        Args:
            session: Database session
            task_id: Task ID string (e.g., 'task_0001')

        Returns:
            Task instance or None
        """
        result = await session.execute(
            select(Task).where(Task.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        session: AsyncSession,
        status: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks by status.

        Args:
            session: Database session
            status: TaskStatus enum value
            skip: Offset
            limit: Limit

        Returns:
            List of Task instances
        """
        result = await session.execute(
            select(Task)
            .where(Task.status == status)
            .offset(skip)
            .limit(limit)
            .options(selectinload(Task.artifacts))
        )
        return list(result.scalars().all())

    async def get_assigned_to(
        self,
        session: AsyncSession,
        desk_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks assigned to a specific desk.

        Args:
            session: Database session
            desk_id: Assignee desk UUID
            skip: Offset
            limit: Limit

        Returns:
            List of Task instances
        """
        result = await session.execute(
            select(Task)
            .where(Task.assigned_to_id == desk_id)
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_subtasks(
        self,
        session: AsyncSession,
        parent_task_id: UUID
    ) -> List[Task]:
        """
        Get all subtasks of a parent task.

        Args:
            session: Database session
            parent_task_id: Parent task UUID

        Returns:
            List of Task instances
        """
        result = await session.execute(
            select(Task).where(Task.parent_task_id == parent_task_id)
        )
        return list(result.scalars().all())

    async def get_with_artifacts(
        self,
        session: AsyncSession,
        task_id: UUID
    ) -> Optional[Task]:
        """
        Get task with artifacts loaded.

        Args:
            session: Database session
            task_id: Task UUID

        Returns:
            Task instance with artifacts or None
        """
        result = await session.execute(
            select(Task)
            .where(Task.id == task_id)
            .options(selectinload(Task.artifacts))
        )
        return result.scalar_one_or_none()


class CRUDArtifact(CRUDBase[Artifact, ArtifactCreate, ArtifactUpdate]):
    """CRUD operations for Artifact."""

    async def get_by_artifact_id(
        self,
        session: AsyncSession,
        artifact_id: str
    ) -> Optional[Artifact]:
        """
        Get artifact by artifact_id string.

        Args:
            session: Database session
            artifact_id: Artifact ID string

        Returns:
            Artifact instance or None
        """
        result = await session.execute(
            select(Artifact).where(Artifact.artifact_id == artifact_id)
        )
        return result.scalar_one_or_none()

    async def get_by_task(
        self,
        session: AsyncSession,
        task_id: UUID
    ) -> List[Artifact]:
        """
        Get all artifacts for a task.

        Args:
            session: Database session
            task_id: Task UUID

        Returns:
            List of Artifact instances
        """
        result = await session.execute(
            select(Artifact).where(Artifact.task_id == task_id)
        )
        return list(result.scalars().all())


# Create singleton instances
task = CRUDTask(Task)
artifact = CRUDArtifact(Artifact)
