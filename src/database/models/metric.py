"""Metric model - KPI tracking and analytics."""

from sqlalchemy import Column, String, Float, Integer
from sqlalchemy.dialects.postgresql import JSONB

from ..base import Base
from .base import UUIDMixin, TimestampMixin


class Metric(Base, UUIDMixin, TimestampMixin):
    """
    Represents a metric or KPI in the system.

    Metrics track performance and system health over time.
    They support time-series data for dashboards and analytics.
    """

    __tablename__ = "metrics"

    # Basic Information
    metric_id = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Identifier for the metric (e.g., 'task_completion_rate')",
    )

    metric_name = Column(
        String(200),
        nullable=False,
        comment="Human-readable metric name",
    )

    metric_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of metric (counter, gauge, histogram, etc.)",
    )

    # Value
    value_float = Column(
        Float,
        nullable=True,
        comment="Numeric value for the metric",
    )

    value_int = Column(
        Integer,
        nullable=True,
        comment="Integer value for the metric",
    )

    # Dimensions and Tags
    dimensions = Column(
        JSONB,
        default={},
        nullable=False,
        comment="Dimensions/tags for grouping (e.g., desk_id, team_id)",
    )

    # Metadata
    metadata_json = Column(
        "metadata",
        JSONB,
        default={},
        nullable=False,
        comment="Additional metric metadata",
    )

    def __repr__(self) -> str:
        return f"<Metric(metric_id='{self.metric_id}', metric_name='{self.metric_name}')>"
