"""AgentDesk model - represents an AI agent workspace."""

from sqlalchemy import Column, String, Integer, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..base import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin
from ..schemas.common import AgentRoleEnum, DeskStatusEnum


class AgentDesk(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents an AI agent's workspace and configuration.

    An AgentDesk is the core entity representing an individual AI agent
    within the organization. It contains the agent's role, configuration,
    hierarchy position, and current state.
    """

    __tablename__ = "agent_desks"

    # Basic Information
    desk_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the desk (e.g., 'cto-001')",
    )

    title = Column(
        String(200),
        nullable=False,
        comment="Job title (e.g., 'Chief Technology Officer')",
    )

    role = Column(
        SQLEnum(AgentRoleEnum, name="agent_role"),
        nullable=False,
        index=True,
        comment="Business role of the agent",
    )

    # Configuration
    llm_config = Column(
        JSONB,
        nullable=False,
        comment="LLM configuration (provider, model, temperature, etc.)",
    )

    capabilities = Column(
        ARRAY(String),
        default=[],
        nullable=False,
        comment="List of agent capabilities",
    )

    # Hierarchy
    hierarchy_level = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Level in organizational hierarchy (0=top)",
    )

    # Status
    status = Column(
        SQLEnum(DeskStatusEnum, name="desk_status"),
        default=DeskStatusEnum.IDLE,
        nullable=False,
        index=True,
        comment="Current status of the agent desk",
    )

    # Memory and Context
    memory = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Agent memory (conversation history, learnings, context)",
    )

    # Relationships - Self-referential hierarchy
    reports_to_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        comment="ID of the manager this desk reports to",
    )

    # Relationships - Team membership
    team_id = Column(
        UUID(as_uuid=True),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
        comment="ID of the team this desk belongs to",
    )

    # Relationships - Manager/subordinate
    manager = relationship(
        "AgentDesk",
        remote_side="AgentDesk.id",
        backref="subordinates",
        foreign_keys=[reports_to_id],
    )

    # Relationships - Team
    team = relationship(
        "Team",
        back_populates="members",
        foreign_keys=[team_id],
    )

    # Relationships - Tasks
    created_tasks = relationship(
        "Task",
        foreign_keys="Task.created_by_id",
        back_populates="creator",
        cascade="all, delete-orphan",
    )

    assigned_tasks = relationship(
        "Task",
        foreign_keys="Task.assigned_to_id",
        back_populates="assignee",
    )

    qa_tasks = relationship(
        "Task",
        foreign_keys="Task.qa_assigned_to_id",
        back_populates="qa_reviewer",
    )

    # Relationships - Committee membership
    committees = relationship(
        "Committee",
        secondary="committee_members",
        back_populates="members",
    )

    def __repr__(self) -> str:
        return f"<AgentDesk(desk_id='{self.desk_id}', title='{self.title}', role='{self.role.value}')>"
