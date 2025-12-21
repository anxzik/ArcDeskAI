"""Pydantic schemas for TaskRoutingRule entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class TaskRoutingRuleBase(BaseModel):
    """Base schema for TaskRoutingRule with common fields."""

    rule_id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    keywords: list[str] = Field(default_factory=list, description="Keywords to match")
    priority_threshold: Optional[int] = Field(None, ge=1, le=4, description="Min priority (1-4)")
    assigned_role: Optional[str] = Field(None, max_length=100)
    rule_priority: int = Field(default=0, description="Rule priority (higher = higher priority)")


class TaskRoutingRuleCreate(TaskRoutingRuleBase):
    """Schema for creating a new TaskRoutingRule."""

    assigned_to_id: Optional[UUID] = Field(None, description="Desk to assign to")
    escalation_desk_id: Optional[UUID] = Field(None, description="Escalation desk")
    notify_committee_id: Optional[UUID] = Field(None, description="Committee to notify")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "rule_id": "security-routing",
                "name": "Security Task Routing",
                "keywords": ["security", "vulnerability", "auth"],
                "priority_threshold": 3,
                "assigned_role": "security_analyst",
                "rule_priority": 10,
            }
        }
    )


class TaskRoutingRuleUpdate(BaseModel):
    """Schema for updating a TaskRoutingRule (all fields optional)."""

    name: Optional[str] = Field(None, max_length=200)
    keywords: Optional[list[str]] = None
    priority_threshold: Optional[int] = Field(None, ge=1, le=4)
    assigned_to_id: Optional[UUID] = None
    assigned_role: Optional[str] = Field(None, max_length=100)
    escalation_desk_id: Optional[UUID] = None
    notify_committee_id: Optional[UUID] = None
    rule_priority: Optional[int] = None


class TaskRoutingRuleResponse(TaskRoutingRuleBase):
    """Schema for TaskRoutingRule response."""

    id: UUID
    assigned_to_id: Optional[UUID] = None
    escalation_desk_id: Optional[UUID] = None
    notify_committee_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaskRoutingRuleListResponse(BaseModel):
    """Schema for paginated list of TaskRoutingRules."""

    items: list[TaskRoutingRuleResponse]
    total: int
    page: int
    page_size: int
