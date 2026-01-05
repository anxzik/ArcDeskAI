"""
Multi-tenant database models for AgentDesk
Scalable, robust PostgreSQL schema with Row-Level Security support
"""
from sqlalchemy import (
    Column, Integer, String, ForeignKey, DateTime, Text, Boolean,
    Numeric, JSON, Enum, Index, CheckConstraint, UniqueConstraint,
    Table, BigInteger
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from .database import Base
import datetime
import enum
import uuid


# ============================================================================
# ENUMS
# ============================================================================

class RoleType(str, enum.Enum):
    """Agent/Desk role types"""
    EXECUTIVE = "executive"
    SENIOR_ENGINEER = "senior_engineer"
    ENGINEER = "engineer"
    QA_ENGINEER = "qa_engineer"
    SECURITY_ENGINEER = "security_engineer"
    RESEARCHER = "researcher"
    WRITER = "writer"
    EDITOR = "editor"
    SUPPORT_L1 = "support_l1"
    SUPPORT_L2 = "support_l2"
    SUPPORT_L3 = "support_l3"
    CUSTOM = "custom"


class TaskStatus(str, enum.Enum):
    """Task lifecycle status"""
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TaskPriority(str, enum.Enum):
    """Task priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class QAStageStatus(str, enum.Enum):
    """QA stage status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class LLMProvider(str, enum.Enum):
    """LLM provider types"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    LOCAL = "local"
    AZURE = "azure"
    CUSTOM = "custom"


class SubscriptionTier(str, enum.Enum):
    """Subscription tiers for organizations"""
    FREE = "free"
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class AuditAction(str, enum.Enum):
    """Audit log action types"""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    ACCESS = "access"
    EXECUTE = "execute"
    DELEGATE = "delegate"
    APPROVE = "approve"
    REJECT = "reject"


# ============================================================================
# CORE TENANT/ORGANIZATION TABLES
# ============================================================================

class Organization(Base):
    """
    Multi-tenant organization/company table
    All data is scoped to an organization for complete tenant isolation
    """
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)

    # Subscription & billing
    subscription_tier = Column(Enum(SubscriptionTier), default=SubscriptionTier.FREE, nullable=False)
    subscription_status = Column(String(50), default="active")
    subscription_expires_at = Column(DateTime(timezone=True), nullable=True)

    # Resource limits (enforced by application)
    max_desks = Column(Integer, default=10)
    max_tasks_per_month = Column(Integer, default=1000)
    max_llm_cost_per_month = Column(Numeric(10, 2), default=100.00)

    # Settings
    settings = Column(JSONB, default={})
    meta_data = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Soft delete

    # Relationships
    users = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    desks = relationship("Desk", back_populates="organization", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="organization", cascade="all, delete-orphan")
    workflows = relationship("Workflow", back_populates="organization", cascade="all, delete-orphan")
    knowledge_bases = relationship("KnowledgeBase", back_populates="organization", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_org_slug', 'slug'),
        Index('idx_org_created', 'created_at'),
    )


class User(Base):
    """
    Human users who manage organizations and interact with agents
    """
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth-only users

    # Profile
    full_name = Column(String(255))
    avatar_url = Column(String(500))

    # Access control
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)  # Org admin
    is_superuser = Column(Boolean, default=False)  # Platform superuser

    # Authentication
    last_login_at = Column(DateTime(timezone=True))
    email_verified_at = Column(DateTime(timezone=True))

    # Settings
    preferences = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id", back_populates="created_by")

    __table_args__ = (
        Index('idx_user_org', 'organization_id'),
        Index('idx_user_email', 'email'),
    )


# ============================================================================
# DESK & AGENT TABLES
# ============================================================================

class Desk(Base):
    """
    Agent desk - represents a position/role in the organization
    Supports hierarchical reporting structure
    """
    __tablename__ = "desks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Identification
    desk_id = Column(String(100), nullable=False)  # User-friendly ID like "cto-001"
    title = Column(String(255), nullable=False)
    role = Column(Enum(RoleType), nullable=False)

    # Hierarchy
    reports_to_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="SET NULL"), nullable=True)
    hierarchy_level = Column(Integer, default=1)  # 1 = top level
    hierarchy_path = Column(String(500))  # Materialized path like "cto-001/dev-senior-001"

    # LLM Configuration
    llm_provider = Column(Enum(LLMProvider), nullable=False)
    llm_model = Column(String(100), nullable=False)
    llm_config = Column(JSONB, default={})  # Temperature, max_tokens, etc.

    # Capabilities & Skills
    capabilities = Column(ARRAY(String), default=list)
    skills = Column(JSONB, default={})

    # State
    is_active = Column(Boolean, default=True)
    status = Column(String(50), default="available")  # available, busy, offline

    # Settings
    system_prompt = Column(Text)
    instructions = Column(Text)
    meta_data = Column(JSONB, default={})

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="desks")
    reports_to = relationship("Desk", remote_side=[id], backref="subordinates")
    assigned_tasks = relationship("Task", foreign_keys="Task.assigned_to_id", back_populates="assigned_to")
    agent_sessions = relationship("AgentSession", back_populates="desk", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint('organization_id', 'desk_id', name='uq_org_desk_id'),
        Index('idx_desk_org', 'organization_id'),
        Index('idx_desk_reports_to', 'reports_to_id'),
        Index('idx_desk_hierarchy', 'hierarchy_path'),
        Index('idx_desk_role', 'role'),
    )


class AgentSession(Base):
    """
    Tracks individual agent execution sessions
    Links to conversation history and tool usage
    """
    __tablename__ = "agent_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="CASCADE"), nullable=False)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)

    # Session metadata
    session_type = Column(String(50))  # task_execution, review, communication
    status = Column(String(50), default="active")

    # Conversation tracking
    conversation_id = Column(UUID(as_uuid=True))
    message_count = Column(Integer, default=0)

    # Cost tracking
    input_tokens = Column(BigInteger, default=0)
    output_tokens = Column(BigInteger, default=0)
    total_cost = Column(Numeric(10, 6), default=0.0)

    # Performance
    started_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    duration_seconds = Column(Integer)

    # Results
    result = Column(JSONB)
    error = Column(Text)

    # Relationships
    desk = relationship("Desk", back_populates="agent_sessions")
    task = relationship("Task", back_populates="agent_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_session_desk', 'desk_id'),
        Index('idx_session_task', 'task_id'),
        Index('idx_session_started', 'started_at'),
    )


# ============================================================================
# TASK & WORKFLOW TABLES
# ============================================================================

class Task(Base):
    """
    Task/work item that can be assigned to agents
    Supports delegation and hierarchical review
    """
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Identification
    task_number = Column(Integer, autoincrement=True)  # Human-readable task number
    title = Column(String(500), nullable=False)
    description = Column(Text)

    # Assignment & delegation
    created_by_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="SET NULL"), nullable=True)
    delegated_from_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="SET NULL"), nullable=True)
    parent_task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=True)

    # Status & priority
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)

    # Workflow
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.id", ondelete="SET NULL"), nullable=True)
    current_stage = Column(String(100))

    # Scheduling
    due_date = Column(DateTime(timezone=True), nullable=True)
    estimated_hours = Column(Numeric(8, 2))
    actual_hours = Column(Numeric(8, 2))

    # Requirements & deliverables
    acceptance_criteria = Column(JSONB, default=list)
    deliverables = Column(JSONB, default=list)

    # Context & metadata
    tags = Column(ARRAY(String), default=list)
    context = Column(JSONB, default={})
    meta_data = Column(JSONB, default={})

    # Results
    result = Column(JSONB)
    output_artifacts = Column(JSONB, default=list)  # URLs, file paths, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="tasks")
    created_by = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    assigned_to = relationship("Desk", foreign_keys=[assigned_to_id], back_populates="assigned_tasks")
    delegated_from = relationship("Desk", foreign_keys=[delegated_from_id])
    parent_task = relationship("Task", remote_side=[id], backref="subtasks")
    workflow = relationship("Workflow", back_populates="tasks")
    qa_reviews = relationship("QAReview", back_populates="task", cascade="all, delete-orphan")
    agent_sessions = relationship("AgentSession", back_populates="task")

    __table_args__ = (
        UniqueConstraint('organization_id', 'task_number', name='uq_org_task_number'),
        Index('idx_task_org', 'organization_id'),
        Index('idx_task_assigned', 'assigned_to_id'),
        Index('idx_task_status', 'status'),
        Index('idx_task_priority', 'priority'),
        Index('idx_task_created', 'created_at'),
        Index('idx_task_parent', 'parent_task_id'),
    )


class Workflow(Base):
    """
    Workflow template defining stages and transitions
    """
    __tablename__ = "workflows"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Workflow definition
    stages = Column(JSONB, nullable=False)  # Array of stage objects
    transitions = Column(JSONB, default={})  # Stage transition rules

    # QA Pipeline configuration
    qa_enabled = Column(Boolean, default=False)
    qa_stages = Column(JSONB, default=list)

    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    meta_data = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="workflows")
    tasks = relationship("Task", back_populates="workflow")

    __table_args__ = (
        Index('idx_workflow_org', 'organization_id'),
        Index('idx_workflow_active', 'is_active'),
    )


# ============================================================================
# QA/QI PIPELINE TABLES
# ============================================================================

class QAReview(Base):
    """
    Quality assurance review for a task
    Supports multi-stage review pipeline
    """
    __tablename__ = "qa_reviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)

    # Review metadata
    stage_name = Column(String(100), nullable=False)
    stage_order = Column(Integer, default=1)
    review_type = Column(String(50))  # automated_test, code_review, security_scan, peer_review

    # Reviewer
    reviewer_desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="SET NULL"), nullable=True)
    reviewer_type = Column(String(50))  # agent, human, automated

    # Status & results
    status = Column(Enum(QAStageStatus), default=QAStageStatus.PENDING, nullable=False)
    score = Column(Numeric(5, 2))  # 0-100 quality score
    passed = Column(Boolean)

    # Feedback
    findings = Column(JSONB, default=list)  # Issues, suggestions, notes
    feedback = Column(Text)
    recommendations = Column(JSONB, default=list)

    # Metrics
    metrics = Column(JSONB, default={})  # Code coverage, security score, etc.

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    task = relationship("Task", back_populates="qa_reviews")
    reviewer_desk = relationship("Desk")

    __table_args__ = (
        Index('idx_qa_task', 'task_id'),
        Index('idx_qa_status', 'status'),
        Index('idx_qa_reviewer', 'reviewer_desk_id'),
    )


# ============================================================================
# COMMUNICATION & COLLABORATION
# ============================================================================

class Message(Base):
    """
    Messages between agents, or between agents and users
    Part of agent session conversations
    """
    __tablename__ = "messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("agent_sessions.id", ondelete="CASCADE"), nullable=False)

    # Message details
    role = Column(String(50), nullable=False)  # user, assistant, system, tool
    content = Column(Text, nullable=False)

    # Metadata
    meta_data = Column(JSONB, default={})
    tool_calls = Column(JSONB)
    tool_results = Column(JSONB)

    # Tokens & cost
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
    cost = Column(Numeric(10, 6), default=0.0)

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    # Relationships
    session = relationship("AgentSession", back_populates="messages")

    __table_args__ = (
        Index('idx_message_session', 'session_id'),
        Index('idx_message_created', 'created_at'),
    )


class Delegation(Base):
    """
    Tracks task delegation between agents
    """
    __tablename__ = "delegations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)

    from_desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="CASCADE"), nullable=False)
    to_desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="CASCADE"), nullable=False)

    reason = Column(Text)
    instructions = Column(Text)
    context = Column(JSONB, default={})

    # Status
    status = Column(String(50), default="pending")  # pending, accepted, rejected, completed

    # Response
    response = Column(Text)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    # Relationships
    task = relationship("Task")
    from_desk = relationship("Desk", foreign_keys=[from_desk_id])
    to_desk = relationship("Desk", foreign_keys=[to_desk_id])

    __table_args__ = (
        Index('idx_delegation_task', 'task_id'),
        Index('idx_delegation_from', 'from_desk_id'),
        Index('idx_delegation_to', 'to_desk_id'),
        Index('idx_delegation_created', 'created_at'),
    )


# ============================================================================
# KNOWLEDGE BASE & DATA SOURCES
# ============================================================================

class KnowledgeBase(Base):
    """
    Knowledge base containing information agents can access
    """
    __tablename__ = "knowledge_bases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Configuration
    embedding_model = Column(String(100))
    vector_store_config = Column(JSONB, default={})

    is_active = Column(Boolean, default=True)
    meta_data = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    organization = relationship("Organization", back_populates="knowledge_bases")
    data_sources = relationship("DataSource", back_populates="knowledge_base", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_kb_org', 'organization_id'),
    )


class DataSource(Base):
    """
    Data source for knowledge base
    """
    __tablename__ = "data_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    knowledge_base_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_bases.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False)  # github, web, file, api, database
    uri = Column(String(1000), nullable=False)

    # Sync configuration
    sync_enabled = Column(Boolean, default=True)
    sync_frequency = Column(String(50))  # hourly, daily, weekly, manual
    last_synced_at = Column(DateTime(timezone=True), nullable=True)

    # Authentication
    credentials = Column(JSONB)  # Encrypted credentials

    # Stats
    document_count = Column(Integer, default=0)
    total_size_bytes = Column(BigInteger, default=0)

    meta_data = Column(JSONB, default={})

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # Relationships
    knowledge_base = relationship("KnowledgeBase", back_populates="data_sources")

    __table_args__ = (
        Index('idx_ds_kb', 'knowledge_base_id'),
        Index('idx_ds_type', 'source_type'),
    )


# ============================================================================
# COST TRACKING & BILLING
# ============================================================================

class CostTracking(Base):
    """
    Track LLM API costs per organization
    Partitioned by month for scalability
    """
    __tablename__ = "cost_tracking"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Resource identification
    desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="SET NULL"), nullable=True)
    task_id = Column(UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True)
    session_id = Column(UUID(as_uuid=True), ForeignKey("agent_sessions.id", ondelete="SET NULL"), nullable=True)

    # LLM details
    provider = Column(Enum(LLMProvider), nullable=False)
    model = Column(String(100), nullable=False)

    # Usage metrics
    input_tokens = Column(BigInteger, default=0)
    output_tokens = Column(BigInteger, default=0)
    total_tokens = Column(BigInteger, default=0)

    # Cost
    input_cost = Column(Numeric(10, 6), default=0.0)
    output_cost = Column(Numeric(10, 6), default=0.0)
    total_cost = Column(Numeric(10, 6), default=0.0)

    # Metadata
    meta_data = Column(JSONB, default={})

    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    billing_month = Column(String(7), nullable=False)  # YYYY-MM for partitioning

    # Relationships
    organization = relationship("Organization")
    desk = relationship("Desk")
    task = relationship("Task")
    session = relationship("AgentSession")

    __table_args__ = (
        Index('idx_cost_org_month', 'organization_id', 'billing_month'),
        Index('idx_cost_desk', 'desk_id'),
        Index('idx_cost_task', 'task_id'),
        Index('idx_cost_created', 'created_at'),
    )


# ============================================================================
# AUDIT & SECURITY
# ============================================================================

class AuditLog(Base):
    """
    Comprehensive audit log for compliance and security
    Tracks all significant actions in the system
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    desk_id = Column(UUID(as_uuid=True), ForeignKey("desks.id", ondelete="SET NULL"), nullable=True)
    actor_type = Column(String(50), nullable=False)  # user, agent, system

    # Action
    action = Column(Enum(AuditAction), nullable=False)
    resource_type = Column(String(100), nullable=False)  # task, desk, workflow, etc.
    resource_id = Column(UUID(as_uuid=True))

    # Details
    description = Column(Text)
    changes = Column(JSONB)  # Before/after state
    meta_data = Column(JSONB, default={})

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Timestamp
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")
    desk = relationship("Desk")

    __table_args__ = (
        Index('idx_audit_org_created', 'organization_id', 'created_at'),
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_desk', 'desk_id'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_resource', 'resource_type', 'resource_id'),
    )


class APIKey(Base):
    """
    API keys for programmatic access
    """
    __tablename__ = "api_keys"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)

    name = Column(String(255), nullable=False)
    key_hash = Column(String(255), nullable=False, unique=True)  # Hash of the actual key
    key_prefix = Column(String(20), nullable=False)  # First chars for identification

    # Permissions
    scopes = Column(ARRAY(String), default=list)

    # Status
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Usage tracking
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(BigInteger, default=0)

    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow)

    # Relationships
    organization = relationship("Organization")
    user = relationship("User")

    __table_args__ = (
        Index('idx_apikey_org', 'organization_id'),
        Index('idx_apikey_hash', 'key_hash'),
    )
