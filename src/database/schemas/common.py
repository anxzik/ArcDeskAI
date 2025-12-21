"""Common Pydantic schemas and enums used across the API."""

from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel, Field, ConfigDict


class AgentRoleEnum(str, Enum):
    """Standard business roles for agents."""

    EXECUTIVE = "executive"
    MANAGER = "manager"
    SENIOR_ENGINEER = "senior_engineer"
    ENGINEER = "engineer"
    JUNIOR_ENGINEER = "junior_engineer"
    QA_ENGINEER = "qa_engineer"
    SECURITY_ANALYST = "security_analyst"
    RESEARCHER = "researcher"


class DeskStatusEnum(str, Enum):
    """Current status of an agent desk."""

    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"


class TaskStatusEnum(str, Enum):
    """Status of tasks in the system."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class PriorityEnum(int, Enum):
    """Task priority levels."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class LLMConfigSchema(BaseModel):
    """Configuration for LLM provider."""

    provider: str = Field(
        ...,
        description="LLM provider (anthropic, openai, local, etc.)",
        examples=["anthropic", "openai"],
    )
    model: str = Field(
        ...,
        description="Model identifier",
        examples=["claude-sonnet-4-20250514", "gpt-4"],
    )
    temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Temperature for model generation",
    )
    max_tokens: int = Field(
        default=4000,
        ge=1,
        le=200000,
        description="Maximum tokens for model generation",
    )
    api_key: Optional[str] = Field(
        default=None,
        description="API key for the provider (optional, can use env vars)",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-20250514",
                "temperature": 0.7,
                "max_tokens": 4000,
            }
        }
    )


class ConversationTurn(BaseModel):
    """A single conversation turn in agent memory."""

    role: str = Field(..., description="Role in conversation (user, assistant, system)")
    content: str = Field(..., description="Content of the message")
    timestamp: str = Field(..., description="ISO timestamp of the turn")


class Learning(BaseModel):
    """A learning or insight recorded by the agent."""

    content: str = Field(..., description="The learning content")
    timestamp: str = Field(..., description="ISO timestamp when learned")


class AgentMemorySchema(BaseModel):
    """Agent's memory and context."""

    conversation_history: list[ConversationTurn] = Field(
        default_factory=list,
        description="History of conversations",
    )
    learnings: list[Learning] = Field(
        default_factory=list,
        description="Recorded learnings and insights",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Custom context data",
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "conversation_history": [
                    {
                        "role": "user",
                        "content": "Complete this task",
                        "timestamp": "2025-01-15T10:30:00",
                    }
                ],
                "learnings": [
                    {
                        "content": "Learned about async patterns",
                        "timestamp": "2025-01-15T11:00:00",
                    }
                ],
                "context": {"last_task_id": "task_0001"},
            }
        }
    )
