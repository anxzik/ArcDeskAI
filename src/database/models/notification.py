"""Notification model - event notifications and alerts."""

from sqlalchemy import Column, String, Text, Boolean
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from .base import UUIDMixin, TimestampMixin


class Notification(Base, UUIDMixin, TimestampMixin):
    """
    Represents a notification or alert in the system.

    Notifications are generated for important events and can be
    sent through various channels (Slack, email, PagerDuty, etc.).
    """

    __tablename__ = "notifications"

    # Basic Information
    notification_id = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique identifier for the notification",
    )

    event_type = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Type of event that triggered this notification",
    )

    title = Column(
        String(500),
        nullable=False,
        comment="Notification title",
    )

    message = Column(
        Text,
        nullable=False,
        comment="Notification message content",
    )

    # Channel Configuration
    channels = Column(
        JSONB,
        nullable=False,
        comment="Channels to send notification to (slack, email, etc.)",
    )

    # Recipients
    recipients = Column(
        JSONB,
        nullable=False,
        comment="List of recipients (desk IDs, email addresses, etc.)",
    )

    # Status
    sent = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Whether the notification has been sent",
    )

    # Metadata
    metadata_json = Column(
        "metadata",
        JSONB,
        default={},
        nullable=False,
        comment="Additional notification metadata",
    )

    def __repr__(self) -> str:
        return f"<Notification(notification_id='{self.notification_id}', event_type='{self.event_type}')>"
