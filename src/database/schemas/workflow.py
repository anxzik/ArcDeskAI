"""Pydantic schemas for Workflow and WorkflowStep entities."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


# WorkflowStep Schemas
class WorkflowStepBase(BaseModel):
    """Base schema for WorkflowStep with common fields."""

    step_name: str = Field(..., max_length=200)
    step_order: int = Field(..., ge=0, description="Step order (0-indexed)")
    assigned_role: Optional[str] = Field(None, max_length=100)
    conditions: dict = Field(default_factory=dict, description="Conditional logic")
    timeout_minutes: Optional[int] = Field(None, ge=1)


class WorkflowStepCreate(WorkflowStepBase):
    """Schema for creating a new WorkflowStep."""

    workflow_id: UUID = Field(..., description="Parent workflow ID")
    assigned_desk_id: Optional[UUID] = Field(None, description="Specific desk assignment")


class WorkflowStepUpdate(BaseModel):
    """Schema for updating a WorkflowStep."""

    step_name: Optional[str] = Field(None, max_length=200)
    step_order: Optional[int] = Field(None, ge=0)
    assigned_role: Optional[str] = Field(None, max_length=100)
    assigned_desk_id: Optional[UUID] = None
    conditions: Optional[dict] = None
    timeout_minutes: Optional[int] = Field(None, ge=1)


class WorkflowStepResponse(WorkflowStepBase):
    """Schema for WorkflowStep response."""

    id: UUID
    workflow_id: UUID
    assigned_desk_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Workflow Schemas
class WorkflowBase(BaseModel):
    """Base schema for Workflow with common fields."""

    workflow_id: str = Field(..., max_length=50)
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    trigger: dict = Field(..., description="Trigger configuration")
    config: dict = Field(default_factory=dict, description="Additional configuration")


class WorkflowCreate(WorkflowBase):
    """Schema for creating a new Workflow."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "workflow_id": "code-review-workflow",
                "name": "Code Review Workflow",
                "description": "Multi-step code review process",
                "trigger": {
                    "type": "task_created",
                    "keywords": ["code", "review"],
                },
                "config": {"auto_assign": True},
            }
        }
    )


class WorkflowUpdate(BaseModel):
    """Schema for updating a Workflow (all fields optional)."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    trigger: Optional[dict] = None
    config: Optional[dict] = None


class WorkflowResponse(WorkflowBase):
    """Schema for Workflow response."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class WorkflowWithSteps(WorkflowResponse):
    """Schema for Workflow response including steps."""

    steps: list[WorkflowStepResponse] = []


class WorkflowListResponse(BaseModel):
    """Schema for paginated list of Workflows."""

    items: list[WorkflowResponse]
    total: int
    page: int
    page_size: int
