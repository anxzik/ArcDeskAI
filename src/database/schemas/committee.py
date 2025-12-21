"""Pydantic schemas for Committee entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class CommitteeBase(BaseModel):
    """Base schema for Committee with common fields."""

    committee_id: str = Field(..., max_length=50, description="Unique committee identifier")
    name: str = Field(..., max_length=200, description="Committee name")
    purpose: Optional[str] = Field(None, description="Purpose and responsibilities")
    meeting_frequency: Optional[str] = Field(
        None,
        max_length=100,
        description="Meeting frequency (e.g., 'weekly', 'as-needed')"
    )


class CommitteeCreate(CommitteeBase):
    """Schema for creating a new Committee."""

    chair_id: Optional[UUID] = Field(None, description="Committee chair desk ID")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "committee_id": "security-committee",
                "name": "Security Review Committee",
                "purpose": "Review and approve security-related decisions",
                "meeting_frequency": "weekly",
                "chair_id": "550e8400-e29b-41d4-a716-446655440000",
            }
        }
    )


class CommitteeUpdate(BaseModel):
    """Schema for updating a Committee (all fields optional)."""

    name: Optional[str] = Field(None, max_length=200)
    purpose: Optional[str] = None
    meeting_frequency: Optional[str] = Field(None, max_length=100)
    chair_id: Optional[UUID] = None


class CommitteeResponse(CommitteeBase):
    """Schema for Committee response."""

    id: UUID
    chair_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class CommitteeListResponse(BaseModel):
    """Schema for paginated list of Committees."""

    items: list[CommitteeResponse]
    total: int
    page: int
    page_size: int
