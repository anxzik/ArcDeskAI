"""OrganizationStructure model - represents the overall organization."""

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from .base import UUIDMixin, TimestampMixin


class OrganizationStructure(Base, UUIDMixin, TimestampMixin):
    """
    Represents the overall organization structure.

    This is typically a singleton entity that contains metadata
    about the organization as a whole.
    """

    __tablename__ = "organizations"

    # Basic Information
    org_name = Column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
        comment="Organization name",
    )

    description = Column(
        Text,
        nullable=True,
        comment="Organization description",
    )

    # Configuration
    config = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Organization-wide configuration settings",
    )

    # Metadata
    metadata_json = Column(
        "metadata",
        JSONB,
        default={},
        nullable=False,
        comment="Additional organization metadata",
    )

    def __repr__(self) -> str:
        return f"<OrganizationStructure(org_name='{self.org_name}')>"
