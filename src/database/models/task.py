"""Task and Artifact models."""

from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Text,
    Boolean,
    ForeignKey,
    Enum as SQLEnum,
    DateTime,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..base import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin
from ..schemas.common import TaskStatusEnum, PriorityEnum


# Association table for task dependencies (many-to-many)
task_dependencies = Table(
    "task_dependencies",
    Base.metadata,
    Column(
        "task_id",
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "depends_on_id",
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Task(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents a task in the system.

    Tasks are the work items that agents process. They support
    hierarchical structure (parent/subtasks), dependencies,
    QA pipeline, and priority management.
    """

    __tablename__ = "tasks"

    # Basic Information
    task_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the task (e.g., 'task_0001')",
    )

    title = Column(
        String(500),
        nullable=False,
        comment="Task title",
    )

    description = Column(
        Text,
        nullable=False,
        comment="Detailed task description",
    )

    # Status and Priority
    status = Column(
        SQLEnum(TaskStatusEnum, name="task_status"),
        default=TaskStatusEnum.PENDING,
        nullable=False,
        index=True,
        comment="Current status of the task",
    )

    priority = Column(
        SQLEnum(PriorityEnum, name="priority"),
        default=PriorityEnum.MEDIUM,
        nullable=False,
        index=True,
        comment="Task priority level",
    )

    # Assignment
    created_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID of the desk that created this task",
    )

    assigned_to_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID of the desk assigned to this task",
    )

    # QA Pipeline
    qa_required = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Whether QA review is required",
    )

    qa_assigned_to_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID of the desk assigned for QA review",
    )

    # Hierarchy - Parent/subtask relationships
    parent_task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
        comment="ID of the parent task (if this is a subtask)",
    )

    # Timestamps
    completed_at = Column(
        DateTime,
        nullable=True,
        comment="Timestamp when task was completed",
    )

    # Relationships - AgentDesk
    creator = relationship(
        "AgentDesk",
        foreign_keys=[created_by_id],
        back_populates="created_tasks",
    )

    assignee = relationship(
        "AgentDesk",
        foreign_keys=[assigned_to_id],
        back_populates="assigned_tasks",
    )

    qa_reviewer = relationship(
        "AgentDesk",
        foreign_keys=[qa_assigned_to_id],
        back_populates="qa_tasks",
    )

    # Relationships - Parent/subtasks
    parent_task = relationship(
        "Task",
        remote_side="Task.id",
        backref="subtasks",
        foreign_keys=[parent_task_id],
    )

    # Relationships - Dependencies (many-to-many)
    dependencies = relationship(
        "Task",
        secondary=task_dependencies,
        primaryjoin=id == task_dependencies.c.task_id,
        secondaryjoin=id == task_dependencies.c.depends_on_id,
        backref="dependent_tasks",
    )

    # Relationships - Artifacts
    artifacts = relationship(
        "Artifact",
        back_populates="task",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Task(task_id='{self.task_id}', title='{self.title}', status='{self.status.value}')>"


class Artifact(Base, UUIDMixin, TimestampMixin):
    """
    Represents an output artifact from a task.

    Artifacts are the deliverables produced by agents when completing tasks.
    They can be code, documents, analyses, or any other type of output.
    """

    __tablename__ = "artifacts"

    # Basic Information
    artifact_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the artifact",
    )

    artifact_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of artifact (code, document, analysis, etc.)",
    )

    # Content
    content = Column(
        Text,
        nullable=False,
        comment="The actual content of the artifact",
    )

    metadata_json = Column(
        "metadata",
        JSONB,
        default={},
        nullable=False,
        comment="Additional metadata about the artifact",
    )

    # Relationships - Task
    task_id = Column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="ID of the task this artifact belongs to",
    )

    task = relationship("Task", back_populates="artifacts")

    def __repr__(self) -> str:
        return f"<Artifact(artifact_id='{self.artifact_id}', type='{self.artifact_type}')>"
