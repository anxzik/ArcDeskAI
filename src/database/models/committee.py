"""Committee model - represents cross-functional decision bodies."""

from sqlalchemy import Column, String, Text, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin


# Association table for committee membership (many-to-many)
committee_members = Table(
    "committee_members",
    Base.metadata,
    Column(
        "committee_id",
        UUID(as_uuid=True),
        ForeignKey("committees.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "desk_id",
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Committee(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents a committee within the organization.

    Committees are cross-functional groups that make decisions
    or oversee specific areas. They have a chair and multiple members.
    """

    __tablename__ = "committees"

    # Basic Information
    committee_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the committee",
    )

    name = Column(
        String(200),
        nullable=False,
        comment="Committee name",
    )

    purpose = Column(
        Text,
        nullable=True,
        comment="Purpose and responsibilities of the committee",
    )

    meeting_frequency = Column(
        String(100),
        nullable=True,
        comment="How often the committee meets (e.g., 'weekly', 'as-needed')",
    )

    # Committee Leadership
    chair_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL", use_alter=True, name="fk_committee_chair"),
        nullable=True,
        comment="ID of the committee chair",
    )

    # Relationships
    chair = relationship(
        "AgentDesk",
        foreign_keys=[chair_id],
    )

    members = relationship(
        "AgentDesk",
        secondary=committee_members,
        back_populates="committees",
    )

    def __repr__(self) -> str:
        return f"<Committee(committee_id='{self.committee_id}', name='{self.name}')>"
