"""CRUD operations package."""

from .base import CRUDBase
from .agent_desk import agent_desk, CRUDAgentDesk
from .task import task, artifact, CRUDTask, CRUDArtifact
from .team import team, CRUDTeam
from .committee import committee, CRUDCommittee
from .workflow import workflow, workflow_step, CRUDWorkflow, CRUDWorkflowStep
from .routing import task_routing_rule, CRUDTaskRoutingRule
from .metric import metric, CRUDMetric

__all__ = [
    # Base
    "CRUDBase",
    # AgentDesk
    "agent_desk",
    "CRUDAgentDesk",
    # Task & Artifact
    "task",
    "artifact",
    "CRUDTask",
    "CRUDArtifact",
    # Team
    "team",
    "CRUDTeam",
    # Committee
    "committee",
    "CRUDCommittee",
    # Workflow
    "workflow",
    "workflow_step",
    "CRUDWorkflow",
    "CRUDWorkflowStep",
    # Routing
    "task_routing_rule",
    "CRUDTaskRoutingRule",
    # Metric
    "metric",
    "CRUDMetric",
]
