"""Pydantic schemas package for API validation."""

from .common import (
    AgentRoleEnum,
    DeskStatusEnum,
    TaskStatusEnum,
    PriorityEnum,
    LLMConfigSchema,
    AgentMemorySchema,
)
from .agent_desk import DeskBase, DeskCreate, DeskUpdate, DeskResponse, DeskListResponse
from .task import (
    TaskBase, TaskCreate, TaskUpdate, TaskResponse, TaskWithArtifacts, TaskListResponse,
    ArtifactBase, ArtifactCreate, ArtifactUpdate, ArtifactResponse
)
from .team import TeamBase, TeamCreate, TeamUpdate, TeamResponse, TeamListResponse
from .committee import CommitteeBase, CommitteeCreate, CommitteeUpdate, CommitteeResponse, CommitteeListResponse
from .workflow import (
    WorkflowBase, WorkflowCreate, WorkflowUpdate, WorkflowResponse, WorkflowWithSteps, WorkflowListResponse,
    WorkflowStepBase, WorkflowStepCreate, WorkflowStepUpdate, WorkflowStepResponse
)
from .routing import TaskRoutingRuleBase, TaskRoutingRuleCreate, TaskRoutingRuleUpdate, TaskRoutingRuleResponse, TaskRoutingRuleListResponse
from .notification import NotificationBase, NotificationCreate, NotificationUpdate, NotificationResponse, NotificationListResponse
from .metric import MetricBase, MetricCreate, MetricUpdate, MetricResponse, MetricListResponse

__all__ = [
    # Common
    "AgentRoleEnum",
    "DeskStatusEnum",
    "TaskStatusEnum",
    "PriorityEnum",
    "LLMConfigSchema",
    "AgentMemorySchema",
    # AgentDesk
    "DeskBase",
    "DeskCreate",
    "DeskUpdate",
    "DeskResponse",
    "DeskListResponse",
    # Task & Artifact
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskWithArtifacts",
    "TaskListResponse",
    "ArtifactBase",
    "ArtifactCreate",
    "ArtifactUpdate",
    "ArtifactResponse",
    # Team
    "TeamBase",
    "TeamCreate",
    "TeamUpdate",
    "TeamResponse",
    "TeamListResponse",
    # Committee
    "CommitteeBase",
    "CommitteeCreate",
    "CommitteeUpdate",
    "CommitteeResponse",
    "CommitteeListResponse",
    # Workflow
    "WorkflowBase",
    "WorkflowCreate",
    "WorkflowUpdate",
    "WorkflowResponse",
    "WorkflowWithSteps",
    "WorkflowListResponse",
    "WorkflowStepBase",
    "WorkflowStepCreate",
    "WorkflowStepUpdate",
    "WorkflowStepResponse",
    # Routing
    "TaskRoutingRuleBase",
    "TaskRoutingRuleCreate",
    "TaskRoutingRuleUpdate",
    "TaskRoutingRuleResponse",
    "TaskRoutingRuleListResponse",
    # Notification
    "NotificationBase",
    "NotificationCreate",
    "NotificationUpdate",
    "NotificationResponse",
    "NotificationListResponse",
    # Metric
    "MetricBase",
    "MetricCreate",
    "MetricUpdate",
    "MetricResponse",
    "MetricListResponse",
]
