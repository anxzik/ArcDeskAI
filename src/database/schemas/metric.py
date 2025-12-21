"""Pydantic schemas for Metric entity."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class MetricBase(BaseModel):
    """Base schema for Metric with common fields."""

    metric_id: str = Field(..., max_length=50)
    metric_name: str = Field(..., max_length=200)
    metric_type: str = Field(..., max_length=50, description="counter, gauge, histogram, etc.")
    dimensions: dict = Field(default_factory=dict, description="Dimensions for grouping")


class MetricCreate(MetricBase):
    """Schema for creating a new Metric."""

    value_float: Optional[float] = Field(None, description="Float value")
    value_int: Optional[int] = Field(None, description="Integer value")
    metadata: dict = Field(default_factory=dict, description="Additional metadata")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "metric_id": "task_completion_rate",
                "metric_name": "Task Completion Rate",
                "metric_type": "gauge",
                "value_float": 0.85,
                "dimensions": {"team_id": "backend-team", "period": "daily"},
            }
        }
    )


class MetricUpdate(BaseModel):
    """Schema for updating a Metric (all fields optional)."""

    value_float: Optional[float] = None
    value_int: Optional[int] = None
    dimensions: Optional[dict] = None
    metadata: Optional[dict] = None


class MetricResponse(MetricBase):
    """Schema for Metric response."""

    id: UUID
    value_float: Optional[float] = None
    value_int: Optional[int] = None
    metadata: dict
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MetricListResponse(BaseModel):
    """Schema for paginated list of Metrics."""

    items: list[MetricResponse]
    total: int
    page: int
    page_size: int
