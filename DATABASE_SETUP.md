# AgentDesk PostgreSQL Database Setup

A comprehensive, scalable, multi-tenant PostgreSQL database designed for AgentDesk's hierarchical AI agent organization system.

## Features

- **Multi-Tenancy**: Complete tenant isolation using Row-Level Security (RLS)
- **Scalability**: Optimized indexes, partitioning-ready, materialized views
- **Robustness**: ACID compliance, foreign key constraints, audit logging
- **Enterprise-Ready**: Cost tracking, API key management, comprehensive monitoring
- **Developer-Friendly**: Docker setup, automatic migrations, sample data

## Quick Start

### 1. Start the Database

```bash
# Start PostgreSQL, Redis, and pgAdmin
docker-compose up -d db redis

# Optional: Start with pgAdmin for database management
docker-compose --profile dev up -d
```

### 2. Apply Migrations

```bash
cd agentdesk/backend

# Run Alembic migrations
alembic upgrade head
```

### 3. Initialize the Database

```bash
# The init_scripts.sql file runs automatically on first startup
# To manually apply optimizations:
docker exec -i agentdesk_postgres psql -U agentdesk -d agentdesk_dev < app/database/init_scripts.sql
```

### 4. Verify Setup

```bash
# Connect to PostgreSQL
docker exec -it agentdesk_postgres psql -U agentdesk -d agentdesk_dev

# Check tables
\dt

# Check indexes
\di

# Check materialized views
\dm
```

## Database Schema

### Core Tables

#### Organizations (Tenants)
- **organizations**: Multi-tenant companies/organizations
  - Subscription tiers and billing
  - Resource limits (max desks, tasks, costs)
  - Soft delete support

#### Users & Authentication
- **users**: Human users managing organizations
  - Email/password authentication
  - OAuth support
  - Role-based access control
- **api_keys**: API keys for programmatic access
  - Scoped permissions
  - Usage tracking

#### Agent Hierarchy
- **desks**: Agent positions in organizational hierarchy
  - Hierarchical reporting structure (reports_to_id)
  - Materialized hierarchy paths
  - LLM configuration per desk
  - Capabilities and skills
- **agent_sessions**: Individual agent execution sessions
  - Conversation tracking
  - Token and cost tracking
  - Performance metrics

#### Task Management
- **tasks**: Work items assignable to agents
  - Status workflow (pending → assigned → in_progress → in_review → completed)
  - Priority levels
  - Delegation support
  - Parent/child task relationships
- **workflows**: Workflow templates
  - Stage definitions
  - QA pipeline integration
  - Transition rules
- **delegations**: Task delegation tracking between agents

#### Quality Assurance
- **qa_reviews**: Multi-stage quality review pipeline
  - Automated tests
  - Code review
  - Security scans
  - Peer review
  - Quality scoring

#### Communication
- **messages**: Agent conversation messages
  - Role-based (user, assistant, system, tool)
  - Token and cost tracking
  - Tool call/result storage

#### Knowledge Base
- **knowledge_bases**: Vector databases for agent knowledge
  - Embedding configuration
  - Vector store integration
- **data_sources**: Knowledge base data sources
  - GitHub, web, file, API sources
  - Sync scheduling
  - Credential management

#### Monitoring & Compliance
- **cost_tracking**: LLM API cost tracking
  - Per organization, desk, task, session
  - Token usage metrics
  - Monthly billing aggregation
- **audit_logs**: Comprehensive audit trail
  - All CRUD operations
  - Actor tracking (user/agent/system)
  - Before/after state changes
  - IP and user agent tracking

## Multi-Tenancy

### Row-Level Security (RLS)

All tables enforce tenant isolation through PostgreSQL Row-Level Security:

```sql
-- Example: Set current organization context
SET app.current_org_id = 'your-org-uuid-here';

-- All queries are automatically scoped to this organization
SELECT * FROM desks;  -- Only returns desks for current org
```

### Application Integration

```python
from sqlalchemy import event
from app.database.database import engine

# Set organization context for all database sessions
@event.listens_for(engine, "connect")
def set_current_org(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute(f"SET app.current_org_id = '{current_user.organization_id}'")
    cursor.close()
```

## Performance Optimizations

### Indexes

- **B-tree indexes**: Primary keys, foreign keys, frequently queried columns
- **GIN indexes**: JSONB columns for fast JSON queries
- **Composite indexes**: Multi-column indexes for common query patterns
- **Partial indexes**: Filtered indexes for specific conditions
- **Full-text search indexes**: Text search on task titles/descriptions

### Materialized Views

- **mv_org_cost_summary**: Aggregated cost metrics per organization/month
- **mv_desk_performance**: Desk performance and productivity metrics

Refresh materialized views:

```sql
-- Refresh all views
SELECT refresh_all_mv();

-- Or individually
REFRESH MATERIALIZED VIEW CONCURRENTLY mv_org_cost_summary;
```

### Query Performance

```sql
-- View query performance
SELECT * FROM pg_stat_statements ORDER BY mean_exec_time DESC LIMIT 10;

-- Analyze query plan
EXPLAIN ANALYZE SELECT * FROM tasks WHERE organization_id = 'uuid';
```

## Database Functions

### Auto-Update Triggers

- **update_updated_at_column()**: Automatically updates `updated_at` timestamps
- **calculate_session_duration()**: Calculates session duration on completion
- **update_desk_hierarchy_path()**: Maintains materialized hierarchy paths
- **track_session_cost()**: Automatically tracks costs to cost_tracking table

### Utility Functions

- **get_organization_stats(org_id)**: Get comprehensive organization statistics
- **refresh_all_mv()**: Refresh all materialized views

## Scaling Considerations

### Partitioning

For production at scale, partition large tables by time:

```sql
-- Example: Partition cost_tracking by month
CREATE TABLE cost_tracking_2026_01 PARTITION OF cost_tracking
    FOR VALUES FROM ('2026-01') TO ('2026-02');

-- Create partitions automatically with pg_partman
CREATE EXTENSION pg_partman;
```

Recommended partitioning:
- **cost_tracking**: By `billing_month` (range partitioning)
- **audit_logs**: By `created_at` (range partitioning, monthly)
- **messages**: By `created_at` (range partitioning, weekly)

### Connection Pooling

Current settings in docker-compose.yml:
- Max connections: 200
- Recommended pool size: 20 per application instance
- Max overflow: 40

For production, use PgBouncer for connection pooling:

```yaml
pgbouncer:
  image: pgbouncer/pgbouncer
  environment:
    - DATABASES_HOST=db
    - DATABASES_PORT=5432
    - DATABASES_DBNAME=agentdesk
    - POOL_MODE=transaction
    - MAX_CLIENT_CONN=1000
    - DEFAULT_POOL_SIZE=25
```

### Read Replicas

For read-heavy workloads:

```python
# Configure read replica in SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Write to primary
engine_write = create_engine(DATABASE_URL)

# Read from replica
engine_read = create_engine(DATABASE_REPLICA_URL)

# Use routing
class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None):
        if self._flushing:
            return engine_write
        else:
            return engine_read
```

## Backup & Recovery

### Automated Backups

```bash
# Daily backup script
#!/bin/bash
BACKUP_DIR="/backups/agentdesk"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker exec agentdesk_postgres pg_dump \
  -U agentdesk \
  -d agentdesk_dev \
  -F c \
  -f /tmp/backup_${TIMESTAMP}.dump

docker cp agentdesk_postgres:/tmp/backup_${TIMESTAMP}.dump \
  ${BACKUP_DIR}/backup_${TIMESTAMP}.dump
```

### Point-in-Time Recovery

Enable WAL archiving in production:

```yaml
db:
  command:
    - "-c"
    - "wal_level=replica"
    - "-c"
    - "archive_mode=on"
    - "-c"
    - "archive_command='cp %p /archive/%f'"
```

### Restore

```bash
# Restore from backup
docker exec -i agentdesk_postgres pg_restore \
  -U agentdesk \
  -d agentdesk_dev \
  -c \
  /path/to/backup.dump
```

## Monitoring

### pgAdmin Access

Access pgAdmin at http://localhost:5050

- Email: admin@agentdesk.dev
- Password: admin

Add server connection:
- Host: db (or localhost if using host network)
- Port: 5432
- Username: agentdesk
- Password: agentdesk_dev_password

### Query Performance

```sql
-- Top slow queries
SELECT
    query,
    calls,
    total_exec_time,
    mean_exec_time,
    max_exec_time
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 20;

-- Table sizes
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Index usage
SELECT
    schemaname,
    tablename,
    indexname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY idx_scan DESC;
```

### Health Checks

```bash
# Database health
docker exec agentdesk_postgres pg_isready -U agentdesk

# Connection count
docker exec agentdesk_postgres psql -U agentdesk -d agentdesk_dev \
  -c "SELECT count(*) FROM pg_stat_activity;"

# Database size
docker exec agentdesk_postgres psql -U agentdesk -d agentdesk_dev \
  -c "SELECT pg_size_pretty(pg_database_size('agentdesk_dev'));"
```

## Security Best Practices

### Production Checklist

- [ ] Change all default passwords
- [ ] Use strong secrets for JWT_SECRET_KEY
- [ ] Enable SSL/TLS for database connections
- [ ] Implement certificate-based authentication
- [ ] Encrypt credentials in data_sources table
- [ ] Set up regular backup rotation
- [ ] Enable audit logging
- [ ] Configure firewall rules
- [ ] Use secrets management (Vault, AWS Secrets Manager)
- [ ] Enable RLS policies in production
- [ ] Implement API rate limiting
- [ ] Set up monitoring and alerting

### SSL Configuration

```yaml
db:
  command:
    - "-c"
    - "ssl=on"
    - "-c"
    - "ssl_cert_file=/var/lib/postgresql/server.crt"
    - "-c"
    - "ssl_key_file=/var/lib/postgresql/server.key"
```

## Troubleshooting

### Common Issues

**Issue**: Cannot connect to database
```bash
# Check if PostgreSQL is running
docker ps | grep postgres

# Check logs
docker logs agentdesk_postgres

# Verify network connectivity
docker exec agentdesk_postgres pg_isready
```

**Issue**: Migration fails
```bash
# Check current migration version
alembic current

# Show migration history
alembic history

# Rollback one version
alembic downgrade -1

# Upgrade to specific version
alembic upgrade <revision_id>
```

**Issue**: Poor query performance
```sql
-- Analyze table statistics
ANALYZE tasks;

-- Reindex table
REINDEX TABLE tasks;

-- Vacuum database
VACUUM ANALYZE;
```

**Issue**: Disk space issues
```bash
# Check disk usage
docker exec agentdesk_postgres df -h

# Clean up old data
docker exec agentdesk_postgres psql -U agentdesk -d agentdesk_dev \
  -c "DELETE FROM audit_logs WHERE created_at < NOW() - INTERVAL '90 days';"

# Vacuum to reclaim space
docker exec agentdesk_postgres psql -U agentdesk -d agentdesk_dev \
  -c "VACUUM FULL;"
```

## Development Tools

### Sample Data

Create sample organization and data:

```sql
-- Insert sample organization
INSERT INTO organizations (id, name, slug, subscription_tier)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Demo Organization',
    'demo-org',
    'professional'
);

-- Set context
SET app.current_org_id = '00000000-0000-0000-0000-000000000001';

-- Insert sample desk
INSERT INTO desks (id, organization_id, desk_id, title, role, llm_provider, llm_model)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'cto-001',
    'Chief Technology Officer',
    'executive',
    'anthropic',
    'claude-sonnet-4'
);
```

### Database Reset

```bash
# Stop all services
docker-compose down

# Remove volumes (WARNING: deletes all data)
docker volume rm arcdeskai_postgres_data

# Start fresh
docker-compose up -d db redis
alembic upgrade head
```

## Architecture Decisions

### Why PostgreSQL?

- **ACID Compliance**: Ensures data integrity for critical business operations
- **JSONB Support**: Flexible schema for agent metadata and configurations
- **Row-Level Security**: Built-in multi-tenancy support
- **Full-text Search**: Native text search capabilities
- **Mature Ecosystem**: Extensive tooling and community support
- **Horizontal Scaling**: Supports sharding and replication

### Why UUIDs?

- **Distributed Systems**: Safe for multi-region deployments
- **Security**: Non-sequential, harder to enumerate
- **Merging**: Easy to merge data from different sources
- **URL-Safe**: No encoding needed for REST APIs

### Why Materialized Views?

- **Performance**: Pre-computed aggregations for dashboards
- **Consistency**: Snapshot-in-time data for reporting
- **Flexibility**: Can be refreshed on-demand or on schedule

## Support

For issues or questions:
- GitHub Issues: https://github.com/anxzik/agentdesk/issues
- Documentation: https://agentdesk.dev/docs
- Email: support@agentdesk.dev
