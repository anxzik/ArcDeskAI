"""Pydantic schemas for AgentDesk entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict

from .common import AgentRoleEnum, DeskStatusEnum, LLMConfigSchema, AgentMemorySchema


class DeskBase(BaseModel):
    """Base schema for AgentDesk with common fields."""

    desk_id: str = Field(..., max_length=50, description="Unique desk identifier")
    title: str = Field(..., max_length=200, description="Job title")
    role: AgentRoleEnum = Field(..., description="Business role")
    capabilities: list[str] = Field(default_factory=list, description="List of capabilities")
    hierarchy_level: int = Field(default=0, ge=0, description="Hierarchy level (0=top)")


class DeskCreate(DeskBase):
    """Schema for creating a new AgentDesk."""

    llm_config: LLMConfigSchema = Field(..., description="LLM configuration")
    reports_to_id: Optional[UUID] = Field(None, description="Manager desk ID")
    team_id: Optional[UUID] = Field(None, description="Team ID")
    status: DeskStatusEnum = Field(default=DeskStatusEnum.IDLE, description="Initial status")
    memory: AgentMemorySchema = Field(
        default_factory=lambda: AgentMemorySchema(),
        description="Initial memory state"
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "desk_id": "cto-001",
                "title": "Chief Technology Officer",
                "role": "executive",
                "llm_config": {
                    "provider": "anthropic",
                    "model": "claude-sonnet-4-20250514",
                    "temperature": 0.7,
                    "max_tokens": 4000,
                },
                "capabilities": ["strategic_planning", "architecture_design"],
                "hierarchy_level": 1,
                "status": "idle",
            }
        }
    )


class DeskUpdate(BaseModel):
    """Schema for updating an AgentDesk (all fields optional)."""

    title: Optional[str] = Field(None, max_length=200)
    role: Optional[AgentRoleEnum] = None
    llm_config: Optional[LLMConfigSchema] = None
    capabilities: Optional[list[str]] = None
    hierarchy_level: Optional[int] = Field(None, ge=0)
    reports_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    status: Optional[DeskStatusEnum] = None
    memory: Optional[AgentMemorySchema] = None


class DeskResponse(DeskBase):
    """Schema for AgentDesk response."""

    id: UUID
    llm_config: dict
    reports_to_id: Optional[UUID] = None
    team_id: Optional[UUID] = None
    status: DeskStatusEnum
    memory: dict
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DeskListResponse(BaseModel):
    """Schema for paginated list of AgentDesks."""

    items: list[DeskResponse]
    total: int
    page: int
    page_size: int
