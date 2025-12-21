"""Workflow and WorkflowStep models."""

from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..base import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin


class Workflow(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents a workflow definition.

    Workflows are complex multi-step processes that can be triggered
    by specific events and route work through multiple agents.
    """

    __tablename__ = "workflows"

    # Basic Information
    workflow_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the workflow",
    )

    name = Column(
        String(200),
        nullable=False,
        comment="Workflow name",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Workflow description",
    )

    # Trigger Configuration
    trigger = Column(
        JSONB,
        nullable=False,
        comment="Trigger configuration (type, conditions, keywords)",
    )

    # Metadata
    config = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Additional workflow configuration",
    )

    # Relationships
    steps = relationship(
        "WorkflowStep",
        back_populates="workflow",
        cascade="all, delete-orphan",
        order_by="WorkflowStep.step_order",
    )

    def __repr__(self) -> str:
        return f"<Workflow(workflow_id='{self.workflow_id}', name='{self.name}')>"


class WorkflowStep(Base, UUIDMixin, TimestampMixin):
    """
    Represents a single step within a workflow.

    Each workflow consists of multiple ordered steps, where each
    step can be assigned to a specific role or desk and may have
    conditional logic.
    """

    __tablename__ = "workflow_steps"

    # Basic Information
    step_name = Column(
        String(200),
        nullable=False,
        comment="Name of this workflow step",
    )

    step_order = Column(
        Integer,
        nullable=False,
        comment="Order of this step in the workflow (0-indexed)",
    )

    # Assignment
    assigned_role = Column(
        String(100),
        nullable=True,
        comment="Role assigned to this step (e.g., 'senior_engineer')",
    )

    assigned_desk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        comment="Specific desk assigned to this step",
    )

    # Conditions and Configuration
    conditions = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Conditional logic for step execution",
    )

    timeout_minutes = Column(
        Integer,
        nullable=True,
        comment="Timeout for this step in minutes",
    )

    # Relationships
    workflow_id = Column(
        UUID(as_uuid=True),
        ForeignKey("workflows.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the workflow this step belongs to",
    )

    workflow = relationship("Workflow", back_populates="steps")

    assigned_desk = relationship("AgentDesk", foreign_keys=[assigned_desk_id])

    def __repr__(self) -> str:
        return f"<WorkflowStep(step_name='{self.step_name}', order={self.step_order})>"
