"""TaskRoutingRule model - automated task assignment."""

from sqlalchemy import Column, String, Integer, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin


class TaskRoutingRule(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents a task routing rule for automated assignment.

    Routing rules enable intelligent task delegation based on
    keywords, priority, and other criteria.
    """

    __tablename__ = "task_routing_rules"

    # Basic Information
    rule_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the routing rule",
    )

    name = Column(
        String(200),
        nullable=False,
        comment="Rule name",
    )

    # Matching Criteria
    keywords = Column(
        ARRAY(String),
        default=[],
        nullable=False,
        comment="Keywords to match in task title/description",
    )

    priority_threshold = Column(
        Integer,
        nullable=True,
        comment="Minimum priority level to trigger this rule (1-4)",
    )

    # Assignment
    assigned_to_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        comment="Desk to assign matching tasks to",
    )

    assigned_role = Column(
        String(100),
        nullable=True,
        comment="Role to assign matching tasks to",
    )

    # Escalation
    escalation_desk_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL"),
        nullable=True,
        comment="Desk to escalate to if primary assignment fails",
    )

    # Committee Notification
    notify_committee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("committees.id", ondelete="SET NULL"),
        nullable=True,
        comment="Committee to notify when rule triggers",
    )

    # Priority
    rule_priority = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Priority of this rule (higher number = higher priority)",
    )

    # Relationships
    assigned_to = relationship(
        "AgentDesk",
        foreign_keys=[assigned_to_id],
    )

    escalation_desk = relationship(
        "AgentDesk",
        foreign_keys=[escalation_desk_id],
    )

    notify_committee = relationship(
        "Committee",
        foreign_keys=[notify_committee_id],
    )

    def __repr__(self) -> str:
        return f"<TaskRoutingRule(rule_id='{self.rule_id}', name='{self.name}')>"
