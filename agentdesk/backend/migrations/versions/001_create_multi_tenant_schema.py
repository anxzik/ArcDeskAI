"""Create multi-tenant AgentDesk schema

Revision ID: 001_multi_tenant
Revises: b7072bbd0120
Create Date: 2026-01-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_multi_tenant'
down_revision: Union[str, Sequence[str], None] = 'b7072bbd0120'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade to multi-tenant schema."""

    # Create ENUM types with raw SQL
    op.execute("""
        CREATE TYPE roletype AS ENUM (
            'executive', 'senior_engineer', 'engineer', 'qa_engineer',
            'security_engineer', 'researcher', 'writer', 'editor',
            'support_l1', 'support_l2', 'support_l3', 'custom'
        )
    """)

    op.execute("""
        CREATE TYPE taskstatus AS ENUM (
            'pending', 'assigned', 'in_progress', 'blocked', 'in_review',
            'approved', 'rejected', 'completed', 'cancelled'
        )
    """)

    op.execute("""
        CREATE TYPE taskpriority AS ENUM ('critical', 'high', 'medium', 'low')
    """)

    op.execute("""
        CREATE TYPE qastagestatus AS ENUM ('pending', 'in_progress', 'passed', 'failed', 'skipped')
    """)

    op.execute("""
        CREATE TYPE llmprovider AS ENUM ('anthropic', 'openai', 'google', 'local', 'azure', 'custom')
    """)

    op.execute("""
        CREATE TYPE subscriptiontier AS ENUM ('free', 'starter', 'professional', 'enterprise')
    """)

    op.execute("""
        CREATE TYPE auditaction AS ENUM ('create', 'update', 'delete', 'access', 'execute', 'delegate', 'approve', 'reject')
    """)

    # ========================================================================
    # Organizations (Tenants)
    # ========================================================================
    op.create_table(
        'organizations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(100), unique=True, nullable=False),
        sa.Column('subscription_tier', sa.Enum(name='subscriptiontier'), nullable=False, server_default='free'),
        sa.Column('subscription_status', sa.String(50), server_default='active'),
        sa.Column('subscription_expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('max_desks', sa.Integer, server_default='10'),
        sa.Column('max_tasks_per_month', sa.Integer, server_default='1000'),
        sa.Column('max_llm_cost_per_month', sa.Numeric(10, 2), server_default='100.00'),
        sa.Column('settings', postgresql.JSONB, server_default='{}'),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_org_slug', 'organizations', ['slug'])
    op.create_index('idx_org_created', 'organizations', ['created_at'])
    op.create_index('idx_org_name', 'organizations', ['name'])

    # ========================================================================
    # Users
    # ========================================================================
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('username', sa.String(100), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=True),
        sa.Column('full_name', sa.String(255)),
        sa.Column('avatar_url', sa.String(500)),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_admin', sa.Boolean, server_default='false'),
        sa.Column('is_superuser', sa.Boolean, server_default='false'),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_verified_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('preferences', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_user_org', 'users', ['organization_id'])
    op.create_index('idx_user_email', 'users', ['email'])

    # ========================================================================
    # Desks
    # ========================================================================
    op.create_table(
        'desks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('desk_id', sa.String(100), nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('role', sa.Enum(name='roletype'), nullable=False),
        sa.Column('reports_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('hierarchy_level', sa.Integer, server_default='1'),
        sa.Column('hierarchy_path', sa.String(500)),
        sa.Column('llm_provider', sa.Enum(name='llmprovider'), nullable=False),
        sa.Column('llm_model', sa.String(100), nullable=False),
        sa.Column('llm_config', postgresql.JSONB, server_default='{}'),
        sa.Column('capabilities', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('skills', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('status', sa.String(50), server_default='available'),
        sa.Column('system_prompt', sa.Text),
        sa.Column('instructions', sa.Text),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reports_to_id'], ['desks.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('organization_id', 'desk_id', name='uq_org_desk_id'),
    )
    op.create_index('idx_desk_org', 'desks', ['organization_id'])
    op.create_index('idx_desk_reports_to', 'desks', ['reports_to_id'])
    op.create_index('idx_desk_hierarchy', 'desks', ['hierarchy_path'])
    op.create_index('idx_desk_role', 'desks', ['role'])

    # ========================================================================
    # Workflows
    # ========================================================================
    op.create_table(
        'workflows',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('stages', postgresql.JSONB, nullable=False),
        sa.Column('transitions', postgresql.JSONB, server_default='{}'),
        sa.Column('qa_enabled', sa.Boolean, server_default='false'),
        sa.Column('qa_stages', postgresql.JSONB, server_default='[]'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('is_default', sa.Boolean, server_default='false'),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_workflow_org', 'workflows', ['organization_id'])
    op.create_index('idx_workflow_active', 'workflows', ['is_active'])

    # ========================================================================
    # Tasks
    # ========================================================================
    op.create_table(
        'tasks',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_number', sa.Integer, autoincrement=True),
        sa.Column('title', sa.String(500), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('created_by_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('assigned_to_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('delegated_from_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('parent_task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('status', sa.Enum(name='taskstatus'), nullable=False, server_default='pending'),
        sa.Column('priority', sa.Enum(name='taskpriority'), nullable=False, server_default='medium'),
        sa.Column('workflow_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('current_stage', sa.String(100)),
        sa.Column('due_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('estimated_hours', sa.Numeric(8, 2)),
        sa.Column('actual_hours', sa.Numeric(8, 2)),
        sa.Column('acceptance_criteria', postgresql.JSONB, server_default='[]'),
        sa.Column('deliverables', postgresql.JSONB, server_default='[]'),
        sa.Column('tags', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('context', postgresql.JSONB, server_default='{}'),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('result', postgresql.JSONB),
        sa.Column('output_artifacts', postgresql.JSONB, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['assigned_to_id'], ['desks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['delegated_from_id'], ['desks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['parent_task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='SET NULL'),
        sa.UniqueConstraint('organization_id', 'task_number', name='uq_org_task_number'),
    )
    op.create_index('idx_task_org', 'tasks', ['organization_id'])
    op.create_index('idx_task_assigned', 'tasks', ['assigned_to_id'])
    op.create_index('idx_task_status', 'tasks', ['status'])
    op.create_index('idx_task_priority', 'tasks', ['priority'])
    op.create_index('idx_task_created', 'tasks', ['created_at'])
    op.create_index('idx_task_parent', 'tasks', ['parent_task_id'])

    # ========================================================================
    # Agent Sessions
    # ========================================================================
    op.create_table(
        'agent_sessions',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('desk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_type', sa.String(50)),
        sa.Column('status', sa.String(50), server_default='active'),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True)),
        sa.Column('message_count', sa.Integer, server_default='0'),
        sa.Column('input_tokens', sa.BigInteger, server_default='0'),
        sa.Column('output_tokens', sa.BigInteger, server_default='0'),
        sa.Column('total_cost', sa.Numeric(10, 6), server_default='0.0'),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('result', postgresql.JSONB),
        sa.Column('error', sa.Text),
        sa.ForeignKeyConstraint(['desk_id'], ['desks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_session_desk', 'agent_sessions', ['desk_id'])
    op.create_index('idx_session_task', 'agent_sessions', ['task_id'])
    op.create_index('idx_session_started', 'agent_sessions', ['started_at'])

    # ========================================================================
    # Messages
    # ========================================================================
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(50), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('tool_calls', postgresql.JSONB),
        sa.Column('tool_results', postgresql.JSONB),
        sa.Column('input_tokens', sa.Integer, server_default='0'),
        sa.Column('output_tokens', sa.Integer, server_default='0'),
        sa.Column('cost', sa.Numeric(10, 6), server_default='0.0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['session_id'], ['agent_sessions.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_message_session', 'messages', ['session_id'])
    op.create_index('idx_message_created', 'messages', ['created_at'])

    # ========================================================================
    # QA Reviews
    # ========================================================================
    op.create_table(
        'qa_reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('stage_name', sa.String(100), nullable=False),
        sa.Column('stage_order', sa.Integer, server_default='1'),
        sa.Column('review_type', sa.String(50)),
        sa.Column('reviewer_desk_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('reviewer_type', sa.String(50)),
        sa.Column('status', sa.Enum(name='qastagestatus'), nullable=False, server_default='pending'),
        sa.Column('score', sa.Numeric(5, 2)),
        sa.Column('passed', sa.Boolean),
        sa.Column('findings', postgresql.JSONB, server_default='[]'),
        sa.Column('feedback', sa.Text),
        sa.Column('recommendations', postgresql.JSONB, server_default='[]'),
        sa.Column('metrics', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reviewer_desk_id'], ['desks.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_qa_task', 'qa_reviews', ['task_id'])
    op.create_index('idx_qa_status', 'qa_reviews', ['status'])
    op.create_index('idx_qa_reviewer', 'qa_reviews', ['reviewer_desk_id'])

    # ========================================================================
    # Delegations
    # ========================================================================
    op.create_table(
        'delegations',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('from_desk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('to_desk_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', sa.Text),
        sa.Column('instructions', sa.Text),
        sa.Column('context', postgresql.JSONB, server_default='{}'),
        sa.Column('status', sa.String(50), server_default='pending'),
        sa.Column('response', sa.Text),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['from_desk_id'], ['desks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['to_desk_id'], ['desks.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_delegation_task', 'delegations', ['task_id'])
    op.create_index('idx_delegation_from', 'delegations', ['from_desk_id'])
    op.create_index('idx_delegation_to', 'delegations', ['to_desk_id'])
    op.create_index('idx_delegation_created', 'delegations', ['created_at'])

    # ========================================================================
    # Knowledge Bases
    # ========================================================================
    op.create_table(
        'knowledge_bases',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('embedding_model', sa.String(100)),
        sa.Column('vector_store_config', postgresql.JSONB, server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_kb_org', 'knowledge_bases', ['organization_id'])

    # ========================================================================
    # Data Sources
    # ========================================================================
    op.create_table(
        'data_sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('knowledge_base_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source_type', sa.String(50), nullable=False),
        sa.Column('uri', sa.String(1000), nullable=False),
        sa.Column('sync_enabled', sa.Boolean, server_default='true'),
        sa.Column('sync_frequency', sa.String(50)),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('credentials', postgresql.JSONB),
        sa.Column('document_count', sa.Integer, server_default='0'),
        sa.Column('total_size_bytes', sa.BigInteger, server_default='0'),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['knowledge_base_id'], ['knowledge_bases.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_ds_kb', 'data_sources', ['knowledge_base_id'])
    op.create_index('idx_ds_type', 'data_sources', ['source_type'])

    # ========================================================================
    # Cost Tracking
    # ========================================================================
    op.create_table(
        'cost_tracking',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('desk_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('session_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('provider', sa.Enum(name='llmprovider'), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('input_tokens', sa.BigInteger, server_default='0'),
        sa.Column('output_tokens', sa.BigInteger, server_default='0'),
        sa.Column('total_tokens', sa.BigInteger, server_default='0'),
        sa.Column('input_cost', sa.Numeric(10, 6), server_default='0.0'),
        sa.Column('output_cost', sa.Numeric(10, 6), server_default='0.0'),
        sa.Column('total_cost', sa.Numeric(10, 6), server_default='0.0'),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('billing_month', sa.String(7), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['desk_id'], ['desks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['session_id'], ['agent_sessions.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_cost_org_month', 'cost_tracking', ['organization_id', 'billing_month'])
    op.create_index('idx_cost_desk', 'cost_tracking', ['desk_id'])
    op.create_index('idx_cost_task', 'cost_tracking', ['task_id'])
    op.create_index('idx_cost_created', 'cost_tracking', ['created_at'])

    # ========================================================================
    # Audit Logs
    # ========================================================================
    op.create_table(
        'audit_logs',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('desk_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('actor_type', sa.String(50), nullable=False),
        sa.Column('action', sa.Enum(name='auditaction'), nullable=False),
        sa.Column('resource_type', sa.String(100), nullable=False),
        sa.Column('resource_id', postgresql.UUID(as_uuid=True)),
        sa.Column('description', sa.Text),
        sa.Column('changes', postgresql.JSONB),
        sa.Column('meta_data', postgresql.JSONB, server_default='{}'),
        sa.Column('ip_address', sa.String(45)),
        sa.Column('user_agent', sa.String(500)),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['desk_id'], ['desks.id'], ondelete='SET NULL'),
    )
    op.create_index('idx_audit_org_created', 'audit_logs', ['organization_id', 'created_at'])
    op.create_index('idx_audit_user', 'audit_logs', ['user_id'])
    op.create_index('idx_audit_desk', 'audit_logs', ['desk_id'])
    op.create_index('idx_audit_action', 'audit_logs', ['action'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])

    # ========================================================================
    # API Keys
    # ========================================================================
    op.create_table(
        'api_keys',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('organization_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), unique=True, nullable=False),
        sa.Column('key_prefix', sa.String(20), nullable=False),
        sa.Column('scopes', postgresql.ARRAY(sa.String), server_default='{}'),
        sa.Column('is_active', sa.Boolean, server_default='true'),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('usage_count', sa.BigInteger, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
    )
    op.create_index('idx_apikey_org', 'api_keys', ['organization_id'])
    op.create_index('idx_apikey_hash', 'api_keys', ['key_hash'])

    # ========================================================================
    # Enable Row-Level Security (RLS) for multi-tenancy
    # ========================================================================
    # Note: RLS policies should be defined based on application requirements
    # This enables the feature at the table level

    tables_with_rls = [
        'organizations', 'users', 'desks', 'tasks', 'agent_sessions',
        'messages', 'qa_reviews', 'delegations', 'workflows',
        'knowledge_bases', 'data_sources', 'cost_tracking', 'audit_logs', 'api_keys'
    ]

    for table in tables_with_rls:
        op.execute(f'ALTER TABLE {table} ENABLE ROW LEVEL SECURITY')


def downgrade() -> None:
    """Downgrade schema."""

    # Drop all tables
    op.drop_table('api_keys')
    op.drop_table('audit_logs')
    op.drop_table('cost_tracking')
    op.drop_table('data_sources')
    op.drop_table('knowledge_bases')
    op.drop_table('delegations')
    op.drop_table('qa_reviews')
    op.drop_table('messages')
    op.drop_table('agent_sessions')
    op.drop_table('tasks')
    op.drop_table('workflows')
    op.drop_table('desks')
    op.drop_table('users')
    op.drop_table('organizations')

    # Drop ENUM types
    op.execute('DROP TYPE IF EXISTS auditaction')
    op.execute('DROP TYPE IF EXISTS subscriptiontier')
    op.execute('DROP TYPE IF EXISTS llmprovider')
    op.execute('DROP TYPE IF EXISTS qastagestatus')
    op.execute('DROP TYPE IF EXISTS taskpriority')
    op.execute('DROP TYPE IF EXISTS taskstatus')
    op.execute('DROP TYPE IF EXISTS roletype')
