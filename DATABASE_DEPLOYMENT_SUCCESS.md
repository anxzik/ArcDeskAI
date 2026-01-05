# Database Deployment Complete ✓

## Deployment Summary

Your multi-tenant PostgreSQL database has been successfully deployed to DigitalOcean!

**Database**: `arcdesk` on DigitalOcean Managed PostgreSQL
**Host**: `arcdesk-do-user-13688835-0.l.db.ondigitalocean.com:25060`
**SSL Mode**: Required

---

## What Was Deployed

### ✓ 14 Core Tables
1. **organizations** - Multi-tenant organization management
2. **users** - User accounts scoped to organizations
3. **desks** - AI agent desks with hierarchy
4. **tasks** - Task management with workflow support
5. **workflows** - Customizable workflow definitions
6. **agent_sessions** - Agent conversation sessions
7. **messages** - Conversation message history
8. **qa_reviews** - Quality assurance reviews
9. **delegations** - Task delegation tracking
10. **knowledge_bases** - RAG knowledge base management
11. **data_sources** - External data source integrations
12. **cost_tracking** - LLM cost monitoring per org/desk/task
13. **audit_logs** - Complete audit trail
14. **api_keys** - API key management

### ✓ 7 Enum Types
- `roletype` - Desk roles (executive, engineer, qa_engineer, etc.)
- `taskstatus` - Task lifecycle states
- `taskpriority` - Task priority levels
- `qastagestatus` - QA review states
- `llmprovider` - LLM provider types (anthropic, openai, google, etc.)
- `subscriptiontier` - Subscription levels
- `auditaction` - Audit action types

### ✓ 50+ Performance Indexes
All tables have optimized indexes for:
- Foreign key relationships
- Frequently queried columns
- Time-based queries
- Organization scoping

### ✓ 9 Automated Triggers
- **Auto-updating timestamps**: `updated_at` columns automatically maintained
- **Hierarchy path maintenance**: Desk hierarchy automatically calculated
- **Billing month tracking**: Cost tracking automatically tagged by month

### ✓ Row-Level Security (RLS)
All 14 tables have RLS policies enabled for complete multi-tenant isolation:
- Organizations can only see their own data
- Access controlled via `app.current_org_id` session variable
- Cascading policies through foreign key relationships

### ✓ 2 Materialized Views for Analytics
1. **mv_org_cost_summary** - Organization cost analytics by month/provider
2. **mv_desk_performance** - Desk performance metrics and task completion rates

---

## Quick Start Guide

### Setting Organization Context

To enable RLS, set the current organization before queries:

```sql
-- Set organization context
SET app.current_org_id = 'your-org-uuid-here';

-- Now all queries automatically scope to this organization
SELECT * FROM tasks;  -- Only sees tasks for this org
```

### Creating Your First Organization

```sql
INSERT INTO organizations (name, slug, subscription_tier)
VALUES ('My Company', 'my-company', 'professional')
RETURNING id;
```

### Creating a User

```sql
INSERT INTO users (organization_id, email, username, full_name)
VALUES (
    'org-uuid-here',
    'user@example.com',
    'john_doe',
    'John Doe'
)
RETURNING id;
```

### Creating an AI Desk

```sql
INSERT INTO desks (
    organization_id,
    desk_id,
    title,
    role,
    llm_provider,
    llm_model
)
VALUES (
    'org-uuid-here',
    'senior-eng-001',
    'Senior Software Engineer',
    'senior_engineer',
    'anthropic',
    'claude-3-5-sonnet-20241022'
)
RETURNING id;
```

### Creating a Task

```sql
INSERT INTO tasks (
    organization_id,
    title,
    description,
    created_by_id,
    assigned_to_id,
    priority
)
VALUES (
    'org-uuid-here',
    'Implement user authentication',
    'Add JWT-based authentication to the API',
    'user-uuid-here',
    'desk-uuid-here',
    'high'
)
RETURNING id, task_number;
```

---

## Connection Information

### Python (SQLAlchemy)

```python
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://doadmin:${POSTGRES_PASSWORD}@arcdesk-do-user-13688835-0.l.db.ondigitalocean.com:25060/arcdesk?sslmode=require"

# Or load from environment
import os
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# Set organization context for multi-tenancy
with engine.connect() as conn:
    conn.execute("SET app.current_org_id = %s", (org_id,))
    result = conn.execute("SELECT * FROM tasks")
```

### Python (psycopg2)

```python
import psycopg2

import os

conn = psycopg2.connect(
    host="arcdesk-do-user-13688835-0.l.db.ondigitalocean.com",
    port=25060,
    database="arcdesk",
    user="doadmin",
    password=os.getenv("POSTGRES_PASSWORD"),  # Load from environment
    sslmode="require"
)
```

### Environment Variables

Your `.env` files are already configured:
- `/home/arch/Dev/ArcDeskAI/agentdesk/backend/.env`
- `/home/arch/Dev/ArcDeskAI/agentdesk/.env.dev`

---

## Analytics & Reporting

### Refresh Materialized Views

```sql
-- Refresh cost summary (do this daily/weekly)
REFRESH MATERIALIZED VIEW mv_org_cost_summary;

-- Refresh desk performance (do this daily)
REFRESH MATERIALIZED VIEW mv_desk_performance;
```

### Query Organization Costs

```sql
SELECT
    billing_month,
    provider,
    active_desks,
    tasks_processed,
    total_cost,
    avg_cost_per_call
FROM mv_org_cost_summary
WHERE organization_id = 'your-org-id'
ORDER BY billing_month DESC;
```

### Query Desk Performance

```sql
SELECT
    title,
    role,
    total_tasks,
    completed_tasks,
    avg_completion_hours,
    total_llm_cost
FROM mv_desk_performance
WHERE organization_id = 'your-org-id'
ORDER BY total_tasks DESC;
```

---

## Maintenance Commands

### Check Database Size

```sql
SELECT
    pg_size_pretty(pg_database_size('arcdesk')) as db_size,
    pg_size_pretty(pg_total_relation_size('tasks')) as tasks_table_size;
```

### Monitor Active Connections

```sql
SELECT
    datname,
    count(*) as connections
FROM pg_stat_activity
WHERE datname = 'arcdesk'
GROUP BY datname;
```

### Vacuum and Analyze (run monthly)

```sql
VACUUM ANALYZE;
```

---

## Security Best Practices

1. **Never commit credentials** - Already protected in `.gitignore`
2. **Use RLS policies** - Always set `app.current_org_id` before queries
3. **Rotate API keys regularly** - Use the `api_keys` table
4. **Monitor audit logs** - Check `audit_logs` table regularly
5. **Review cost tracking** - Monitor `cost_tracking` table for anomalies

---

## Next Steps

1. **Seed sample data** - Create your first organization, users, and desks
2. **Set up automated backups** - Configure DigitalOcean automated backups
3. **Create application middleware** - Implement automatic RLS context setting
4. **Set up monitoring** - Monitor costs, performance, and errors
5. **Create database roles** - Set up read-only and admin roles as needed

---

## Support Files

- **Schema documentation**: `/home/arch/Dev/ArcDeskAI/DATABASE_SETUP.md`
- **Remote setup guide**: `/home/arch/Dev/ArcDeskAI/REMOTE_DATABASE_SETUP.md`
- **Security notice**: `/home/arch/Dev/ArcDeskAI/SECURITY_NOTICE.md`

---

**Deployment Date**: January 5, 2025
**Database Version**: PostgreSQL 18.1 (DigitalOcean Managed)
**Schema Version**: 001_multi_tenant
