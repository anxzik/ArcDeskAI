"""Team model - represents organizational teams."""

from sqlalchemy import Column, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from ..base import Base
from .base import UUIDMixin, TimestampMixin, SoftDeleteMixin


class Team(Base, UUIDMixin, TimestampMixin, SoftDeleteMixin):
    """
    Represents a team within the organization.

    Teams are groups of agents that work together on related tasks.
    Each team has a lead and multiple members.
    """

    __tablename__ = "teams"

    # Basic Information
    team_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the team (e.g., 'backend-team')",
    )

    name = Column(
        String(200),
        nullable=False,
        comment="Team name",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Team description and focus area",
    )

    # Team Leadership
    lead_id = Column(
        UUID(as_uuid=True),
        ForeignKey("agent_desks.id", ondelete="SET NULL", use_alter=True, name="fk_team_lead"),
        nullable=True,
        comment="ID of the team lead",
    )

    # Relationships
    lead = relationship(
        "AgentDesk",
        foreign_keys=[lead_id],
    )

    members = relationship(
        "AgentDesk",
        foreign_keys="AgentDesk.team_id",
        back_populates="team",
    )

    def __repr__(self) -> str:
        return f"<Team(team_id='{self.team_id}', name='{self.name}')>"
