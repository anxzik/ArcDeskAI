"""Pydantic schemas for Notification entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class NotificationBase(BaseModel):
    """Base schema for Notification with common fields."""

    notification_id: str = Field(..., max_length=50)
    event_type: str = Field(..., max_length=100, description="Event type that triggered this")
    title: str = Field(..., max_length=500)
    message: str = Field(..., description="Notification message")
    channels: dict = Field(..., description="Channels to send to (slack, email, etc.)")
    recipients: dict = Field(..., description="Recipients (desk IDs, emails, etc.)")


class NotificationCreate(NotificationBase):
    """Schema for creating a new Notification."""

    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "notification_id": "notif_0001",
                "event_type": "task_failed",
                "title": "Task Failed: Authentication Implementation",
                "message": "Task task_0001 has failed and requires attention",
                "channels": {"slack": True, "email": False},
                "recipients": {"desk_ids": ["cto-001"], "slack_channels": ["#alerts"]},
            }
        }
    )


class NotificationUpdate(BaseModel):
    """Schema for updating a Notification (all fields optional)."""

    sent: Optional[bool] = None
    metadata: Optional[dict] = None


class NotificationResponse(NotificationBase):
    """Schema for Notification response."""

    id: UUID
    sent: bool
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationListResponse(BaseModel):
    """Schema for paginated list of Notifications."""

    items: list[NotificationResponse]
    total: int
    page: int
    page_size: int
