"""CRUD operations for Workflow and WorkflowStep models."""

from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.workflow import Workflow, WorkflowStep
from ..schemas.workflow import WorkflowCreate, WorkflowUpdate, WorkflowStepCreate, WorkflowStepUpdate
from .base import CRUDBase


class CRUDWorkflow(CRUDBase[Workflow, WorkflowCreate, WorkflowUpdate]):
    """CRUD operations for Workflow with custom methods."""

    async def get_by_workflow_id(
        self,
        session: AsyncSession,
        workflow_id: str
    ) -> Optional[Workflow]:
        """
        Get workflow by workflow_id string.

        Args:
            session: Database session
            workflow_id: Workflow ID string

        Returns:
            Workflow instance or None
        """
        result = await session.execute(
            select(Workflow).where(Workflow.workflow_id == workflow_id)
        )
        return result.scalar_one_or_none()

    async def get_with_steps(
        self,
        session: AsyncSession,
        workflow_id: UUID
    ) -> Optional[Workflow]:
        """
        Get workflow with steps loaded.

        Args:
            session: Database session
            workflow_id: Workflow UUID

        Returns:
            Workflow instance with steps or None
        """
        result = await session.execute(
            select(Workflow)
            .where(Workflow.id == workflow_id)
            .options(selectinload(Workflow.steps))
        )
        return result.scalar_one_or_none()


class CRUDWorkflowStep(CRUDBase[WorkflowStep, WorkflowStepCreate, WorkflowStepUpdate]):
    """CRUD operations for WorkflowStep."""

    async def get_by_workflow(
        self,
        session: AsyncSession,
        workflow_id: UUID
    ) -> List[WorkflowStep]:
        """
        Get all steps for a workflow.

        Args:
            session: Database session
            workflow_id: Workflow UUID

        Returns:
            List of WorkflowStep instances ordered by step_order
        """
        result = await session.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workflow_id == workflow_id)
            .order_by(WorkflowStep.step_order)
        )
        return list(result.scalars().all())


# Create singleton instances
workflow = CRUDWorkflow(Workflow)
workflow_step = CRUDWorkflowStep(WorkflowStep)
