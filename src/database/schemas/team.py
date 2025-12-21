"""Pydantic schemas for Team entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class TeamBase(BaseModel):
    """Base schema for Team with common fields."""

    team_id: str = Field(..., max_length=50, description="Unique team identifier")
    name: str = Field(..., max_length=200, description="Team name")
    description: Optional[str] = Field(None, description="Team description and focus area")


class TeamCreate(TeamBase):
    """Schema for creating a new Team."""

    lead_id: Optional[UUID] = Field(None, description="Team lead desk ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "team_id": "backend-team",
                "name": "Backend Development Team",
                "description": "Responsible for API and database development",
                "lead_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    )


class TeamUpdate(BaseModel):
    """Schema for updating a Team (all fields optional)."""

    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    lead_id: Optional[UUID] = None


class TeamResponse(TeamBase):
    """Schema for Team response."""

    id: UUID
    lead_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class TeamListResponse(BaseModel):
    """Schema for paginated list of Teams."""

    items: list[TeamResponse]
    total: int
    page: int
    page_size: int
