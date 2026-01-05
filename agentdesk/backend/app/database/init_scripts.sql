-- ============================================================================
-- PostgreSQL Initialization Scripts for AgentDesk
-- Optimizations, RLS Policies, Functions, and Triggers
-- ============================================================================

-- ============================================================================
-- Performance Optimizations
-- ============================================================================

-- Enable pg_stat_statements for query performance monitoring
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Enable pgcrypto for encryption functions
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enable uuid-ossp for UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Custom Functions
-- ============================================================================

-- Function to update updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate session duration
CREATE OR REPLACE FUNCTION calculate_session_duration()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.completed_at IS NOT NULL AND NEW.started_at IS NOT NULL THEN
        NEW.duration_seconds = EXTRACT(EPOCH FROM (NEW.completed_at - NEW.started_at))::INTEGER;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to update hierarchy path when desk hierarchy changes
CREATE OR REPLACE FUNCTION update_desk_hierarchy_path()
RETURNS TRIGGER AS $$
DECLARE
    parent_path TEXT;
BEGIN
    IF NEW.reports_to_id IS NULL THEN
        -- Top level desk
        NEW.hierarchy_path = NEW.desk_id;
        NEW.hierarchy_level = 1;
    ELSE
        -- Get parent's path and level
        SELECT hierarchy_path, hierarchy_level INTO parent_path, NEW.hierarchy_level
        FROM desks WHERE id = NEW.reports_to_id;

        NEW.hierarchy_path = parent_path || '/' || NEW.desk_id;
        NEW.hierarchy_level = NEW.hierarchy_level + 1;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to track cost in cost_tracking table from agent_sessions
CREATE OR REPLACE FUNCTION track_session_cost()
RETURNS TRIGGER AS $$
DECLARE
    org_id UUID;
    desk_org_id UUID;
    current_month VARCHAR(7);
BEGIN
    -- Only track when session is completed
    IF NEW.completed_at IS NOT NULL AND OLD.completed_at IS NULL THEN
        -- Get organization_id from desk
        SELECT organization_id INTO desk_org_id FROM desks WHERE id = NEW.desk_id;

        -- Get current billing month
        current_month = TO_CHAR(NEW.completed_at, 'YYYY-MM');

        -- Insert cost tracking record
        INSERT INTO cost_tracking (
            id,
            organization_id,
            desk_id,
            task_id,
            session_id,
            provider,
            model,
            input_tokens,
            output_tokens,
            total_tokens,
            total_cost,
            billing_month,
            created_at
        )
        SELECT
            uuid_generate_v4(),
            desk_org_id,
            NEW.desk_id,
            NEW.task_id,
            NEW.id,
            d.llm_provider,
            d.llm_model,
            NEW.input_tokens,
            NEW.output_tokens,
            NEW.input_tokens + NEW.output_tokens,
            NEW.total_cost,
            current_month,
            NEW.completed_at
        FROM desks d
        WHERE d.id = NEW.desk_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Triggers
-- ============================================================================

-- Trigger to auto-update updated_at on organizations
DROP TRIGGER IF EXISTS trigger_organizations_updated_at ON organizations;
CREATE TRIGGER trigger_organizations_updated_at
    BEFORE UPDATE ON organizations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on users
DROP TRIGGER IF EXISTS trigger_users_updated_at ON users;
CREATE TRIGGER trigger_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on desks
DROP TRIGGER IF EXISTS trigger_desks_updated_at ON desks;
CREATE TRIGGER trigger_desks_updated_at
    BEFORE UPDATE ON desks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on tasks
DROP TRIGGER IF EXISTS trigger_tasks_updated_at ON tasks;
CREATE TRIGGER trigger_tasks_updated_at
    BEFORE UPDATE ON tasks
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on workflows
DROP TRIGGER IF EXISTS trigger_workflows_updated_at ON workflows;
CREATE TRIGGER trigger_workflows_updated_at
    BEFORE UPDATE ON workflows
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on knowledge_bases
DROP TRIGGER IF EXISTS trigger_knowledge_bases_updated_at ON knowledge_bases;
CREATE TRIGGER trigger_knowledge_bases_updated_at
    BEFORE UPDATE ON knowledge_bases
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to auto-update updated_at on data_sources
DROP TRIGGER IF EXISTS trigger_data_sources_updated_at ON data_sources;
CREATE TRIGGER trigger_data_sources_updated_at
    BEFORE UPDATE ON data_sources
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Trigger to calculate session duration
DROP TRIGGER IF EXISTS trigger_session_duration ON agent_sessions;
CREATE TRIGGER trigger_session_duration
    BEFORE UPDATE ON agent_sessions
    FOR EACH ROW
    EXECUTE FUNCTION calculate_session_duration();

-- Trigger to update desk hierarchy path
DROP TRIGGER IF EXISTS trigger_desk_hierarchy ON desks;
CREATE TRIGGER trigger_desk_hierarchy
    BEFORE INSERT OR UPDATE OF reports_to_id ON desks
    FOR EACH ROW
    EXECUTE FUNCTION update_desk_hierarchy_path();

-- Trigger to track session costs
DROP TRIGGER IF EXISTS trigger_track_session_cost ON agent_sessions;
CREATE TRIGGER trigger_track_session_cost
    AFTER UPDATE ON agent_sessions
    FOR EACH ROW
    EXECUTE FUNCTION track_session_cost();

-- ============================================================================
-- Row-Level Security (RLS) Policies
-- ============================================================================

-- Policy for organizations - users can only see their own organization
DROP POLICY IF EXISTS org_isolation_policy ON organizations;
CREATE POLICY org_isolation_policy ON organizations
    USING (id = current_setting('app.current_org_id', true)::UUID);

-- Policy for users - users can only see users in their organization
DROP POLICY IF EXISTS user_org_isolation ON users;
CREATE POLICY user_org_isolation ON users
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for desks - users can only see desks in their organization
DROP POLICY IF EXISTS desk_org_isolation ON desks;
CREATE POLICY desk_org_isolation ON desks
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for tasks - users can only see tasks in their organization
DROP POLICY IF EXISTS task_org_isolation ON tasks;
CREATE POLICY task_org_isolation ON tasks
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for workflows - users can only see workflows in their organization
DROP POLICY IF EXISTS workflow_org_isolation ON workflows;
CREATE POLICY workflow_org_isolation ON workflows
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for knowledge_bases - users can only see knowledge bases in their organization
DROP POLICY IF EXISTS kb_org_isolation ON knowledge_bases;
CREATE POLICY kb_org_isolation ON knowledge_bases
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for cost_tracking - users can only see costs for their organization
DROP POLICY IF EXISTS cost_org_isolation ON cost_tracking;
CREATE POLICY cost_org_isolation ON cost_tracking
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for audit_logs - users can only see audit logs for their organization
DROP POLICY IF EXISTS audit_org_isolation ON audit_logs;
CREATE POLICY audit_org_isolation ON audit_logs
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- Policy for api_keys - users can only see API keys for their organization
DROP POLICY IF EXISTS apikey_org_isolation ON api_keys;
CREATE POLICY apikey_org_isolation ON api_keys
    USING (organization_id = current_setting('app.current_org_id', true)::UUID);

-- ============================================================================
-- Additional Indexes for Performance
-- ============================================================================

-- GIN indexes for JSONB columns to enable faster JSON queries
CREATE INDEX IF NOT EXISTS idx_org_settings_gin ON organizations USING GIN (settings);
CREATE INDEX IF NOT EXISTS idx_org_metadata_gin ON organizations USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_desk_llm_config_gin ON desks USING GIN (llm_config);
CREATE INDEX IF NOT EXISTS idx_desk_skills_gin ON desks USING GIN (skills);
CREATE INDEX IF NOT EXISTS idx_task_context_gin ON tasks USING GIN (context);
CREATE INDEX IF NOT EXISTS idx_task_metadata_gin ON tasks USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_message_metadata_gin ON messages USING GIN (metadata);

-- Partial indexes for common queries
CREATE INDEX IF NOT EXISTS idx_desks_active ON desks (organization_id, is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_tasks_active ON tasks (organization_id, status) WHERE status NOT IN ('completed', 'cancelled');
CREATE INDEX IF NOT EXISTS idx_tasks_overdue ON tasks (organization_id, due_date) WHERE due_date < NOW() AND status NOT IN ('completed', 'cancelled');

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_tasks_org_status_priority ON tasks (organization_id, status, priority);
CREATE INDEX IF NOT EXISTS idx_sessions_desk_date ON agent_sessions (desk_id, started_at DESC);
CREATE INDEX IF NOT EXISTS idx_cost_org_month_provider ON cost_tracking (organization_id, billing_month, provider);

-- Text search indexes for full-text search capabilities
CREATE INDEX IF NOT EXISTS idx_tasks_title_fts ON tasks USING GIN (to_tsvector('english', title));
CREATE INDEX IF NOT EXISTS idx_tasks_description_fts ON tasks USING GIN (to_tsvector('english', description));

-- ============================================================================
-- Materialized Views for Analytics
-- ============================================================================

-- View for organization cost summary by month
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_org_cost_summary AS
SELECT
    organization_id,
    billing_month,
    provider,
    COUNT(*) as transaction_count,
    SUM(input_tokens) as total_input_tokens,
    SUM(output_tokens) as total_output_tokens,
    SUM(total_tokens) as total_tokens,
    SUM(total_cost) as total_cost,
    AVG(total_cost) as avg_cost_per_request
FROM cost_tracking
GROUP BY organization_id, billing_month, provider;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_cost_summary_unique
    ON mv_org_cost_summary (organization_id, billing_month, provider);

-- View for desk performance metrics
CREATE MATERIALIZED VIEW IF NOT EXISTS mv_desk_performance AS
SELECT
    d.organization_id,
    d.id as desk_id,
    d.desk_id as desk_identifier,
    d.title,
    COUNT(DISTINCT t.id) as total_tasks,
    COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END) as completed_tasks,
    COUNT(DISTINCT CASE WHEN t.status IN ('in_progress', 'assigned') THEN t.id END) as active_tasks,
    AVG(EXTRACT(EPOCH FROM (t.completed_at - t.started_at))) as avg_completion_time_seconds,
    SUM(COALESCE(ct.total_cost, 0)) as total_cost
FROM desks d
LEFT JOIN tasks t ON t.assigned_to_id = d.id
LEFT JOIN cost_tracking ct ON ct.desk_id = d.id
WHERE d.deleted_at IS NULL
GROUP BY d.organization_id, d.id, d.desk_id, d.title;

CREATE UNIQUE INDEX IF NOT EXISTS idx_mv_desk_perf_unique
    ON mv_desk_performance (desk_id);

-- ============================================================================
-- Helper Functions for Applications
-- ============================================================================

-- Function to get organization stats
CREATE OR REPLACE FUNCTION get_organization_stats(org_id UUID)
RETURNS TABLE (
    total_desks INTEGER,
    active_desks INTEGER,
    total_tasks INTEGER,
    active_tasks INTEGER,
    completed_tasks INTEGER,
    total_cost_this_month NUMERIC
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(DISTINCT d.id)::INTEGER as total_desks,
        COUNT(DISTINCT CASE WHEN d.is_active THEN d.id END)::INTEGER as active_desks,
        COUNT(DISTINCT t.id)::INTEGER as total_tasks,
        COUNT(DISTINCT CASE WHEN t.status IN ('in_progress', 'assigned', 'in_review') THEN t.id END)::INTEGER as active_tasks,
        COUNT(DISTINCT CASE WHEN t.status = 'completed' THEN t.id END)::INTEGER as completed_tasks,
        COALESCE(SUM(ct.total_cost), 0) as total_cost_this_month
    FROM organizations o
    LEFT JOIN desks d ON d.organization_id = o.id AND d.deleted_at IS NULL
    LEFT JOIN tasks t ON t.organization_id = o.id
    LEFT JOIN cost_tracking ct ON ct.organization_id = o.id
        AND ct.billing_month = TO_CHAR(NOW(), 'YYYY-MM')
    WHERE o.id = org_id
    GROUP BY o.id;
END;
$$ LANGUAGE plpgsql;

-- Function to refresh all materialized views
CREATE OR REPLACE FUNCTION refresh_all_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_org_cost_summary;
    REFRESH MATERIALIZED VIEW CONCURRENTLY mv_desk_performance;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Partitioning Setup for Large Tables
-- ============================================================================

-- Note: For production at scale, consider partitioning these tables:
-- 1. cost_tracking - partition by billing_month (range partitioning)
-- 2. audit_logs - partition by created_at (range partitioning)
-- 3. messages - partition by created_at (range partitioning)

-- Example partitioning for cost_tracking (commented out, enable when needed):
/*
-- Convert cost_tracking to partitioned table
ALTER TABLE cost_tracking RENAME TO cost_tracking_old;

CREATE TABLE cost_tracking (
    LIKE cost_tracking_old INCLUDING ALL
) PARTITION BY RANGE (billing_month);

-- Create partitions for each month
CREATE TABLE cost_tracking_2026_01 PARTITION OF cost_tracking
    FOR VALUES FROM ('2026-01') TO ('2026-02');

-- Add more partitions as needed...

-- Migrate data
INSERT INTO cost_tracking SELECT * FROM cost_tracking_old;

-- Drop old table
DROP TABLE cost_tracking_old;
*/

-- ============================================================================
-- Comments for Documentation
-- ============================================================================

COMMENT ON TABLE organizations IS 'Multi-tenant organizations/companies. All data is scoped to an organization.';
COMMENT ON TABLE users IS 'Human users who manage organizations and interact with agents.';
COMMENT ON TABLE desks IS 'Agent desks representing positions/roles in the organizational hierarchy.';
COMMENT ON TABLE tasks IS 'Work items that can be assigned to agents with full lifecycle tracking.';
COMMENT ON TABLE agent_sessions IS 'Individual agent execution sessions with conversation and cost tracking.';
COMMENT ON TABLE messages IS 'Messages in agent conversations with token and cost tracking.';
COMMENT ON TABLE qa_reviews IS 'Quality assurance reviews with multi-stage pipeline support.';
COMMENT ON TABLE delegations IS 'Task delegation tracking between agents in the hierarchy.';
COMMENT ON TABLE workflows IS 'Workflow templates defining stages, transitions, and QA pipelines.';
COMMENT ON TABLE knowledge_bases IS 'Knowledge bases containing information for agent access.';
COMMENT ON TABLE data_sources IS 'Data sources for knowledge bases with sync capabilities.';
COMMENT ON TABLE cost_tracking IS 'LLM API cost tracking per organization, desk, task, and session.';
COMMENT ON TABLE audit_logs IS 'Comprehensive audit log for compliance and security.';
COMMENT ON TABLE api_keys IS 'API keys for programmatic access with usage tracking.';

-- ============================================================================
-- Initial Data Seed (Optional)
-- ============================================================================

-- You can add default data here, such as:
-- - Default workflows
-- - System roles
-- - Subscription tiers
