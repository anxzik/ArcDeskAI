"""Database models package."""

from .base import TimestampMixin, UUIDMixin, SoftDeleteMixin
from .agent_desk import AgentDesk
from .task import Task, Artifact, task_dependencies
from .team import Team
from .committee import Committee, committee_members
from .organization import OrganizationStructure
from .workflow import Workflow, WorkflowStep
from .routing import TaskRoutingRule
from .notification import Notification
from .metric import Metric

__all__ = [
    # Mixins
    "TimestampMixin",
    "UUIDMixin",
    "SoftDeleteMixin",
    # Core models
    "AgentDesk",
    "Task",
    "Artifact",
    "task_dependencies",
    # Organization models
    "Team",
    "Committee",
    "committee_members",
    "OrganizationStructure",
    # Workflow models
    "Workflow",
    "WorkflowStep",
    # Automation models
    "TaskRoutingRule",
    "Notification",
    "Metric",
]
