"""Pydantic schemas for Task and Artifact entities."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .common import TaskStatusEnum, PriorityEnum


# Artifact Schemas
class ArtifactBase(BaseModel):
    """Base schema for Artifact with common fields."""

    artifact_id: str = Field(..., max_length=50)
    artifact_type: str = Field(..., max_length=100, description="Type (code, document, etc.)")
    content: str = Field(..., description="Artifact content")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")


class ArtifactCreate(ArtifactBase):
    """Schema for creating a new Artifact."""

    task_id: UUID = Field(..., description="ID of the task this artifact belongs to")


class ArtifactUpdate(BaseModel):
    """Schema for updating an Artifact."""

    artifact_type: Optional[str] = Field(None, max_length=100)
    content: Optional[str] = None
    metadata: Optional[dict] = None


class ArtifactResponse(ArtifactBase):
    """Schema for Artifact response."""

    id: UUID
    task_id: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Task Schemas
class TaskBase(BaseModel):
    """Base schema for Task with common fields."""

    task_id: str = Field(..., max_length=50)
    title: str = Field(..., max_length=500)
    description: str = Field(..., description="Detailed task description")
    priority: PriorityEnum = Field(default=PriorityEnum.MEDIUM)
    qa_required: bool = Field(default=True)


class TaskCreate(TaskBase):
    """Schema for creating a new Task."""

    created_by_id: UUID = Field(..., description="Creator desk ID")
    assigned_to_id: Optional[UUID] = Field(None, description="Assignee desk ID")
    qa_assigned_to_id: Optional[UUID] = Field(None, description="QA reviewer desk ID")
    parent_task_id: Optional[UUID] = Field(None, description="Parent task ID for subtasks")
    status: TaskStatusEnum = Field(default=TaskStatusEnum.PENDING)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "task_id": "task_0001",
                "title": "Implement user authentication",
                "description": "Create a secure authentication system with JWT tokens",
                "priority": 3,
                "qa_required": True,
                "created_by_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "pending",
            }
        }
    )


class TaskUpdate(BaseModel):
    """Schema for updating a Task (all fields optional)."""

    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[PriorityEnum] = None
    assigned_to_id: Optional[UUID] = None
    qa_assigned_to_id: Optional[UUID] = None
    qa_required: Optional[bool] = None
    completed_at: Optional[datetime] = None


class TaskResponse(TaskBase):
    """Schema for Task response."""

    id: UUID
    status: TaskStatusEnum
    created_by_id: Optional[UUID] = None
    assigned_to_id: Optional[UUID] = None
    qa_assigned_to_id: Optional[UUID] = None
    parent_task_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TaskWithArtifacts(TaskResponse):
    """Schema for Task response including artifacts."""

    artifacts: list[ArtifactResponse] = []


class TaskListResponse(BaseModel):
    """Schema for paginated list of Tasks."""

    items: list[TaskResponse]
    total: int
    page: int
    page_size: int
