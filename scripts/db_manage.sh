#!/bin/bash

# ============================================================================
# AgentDesk Database Management Script
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
DB_CONTAINER="agentdesk_postgres"
DB_NAME="agentdesk_dev"
DB_USER="agentdesk"
BACKUP_DIR="./backups"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Command: setup
cmd_setup() {
    print_info "Setting up AgentDesk database..."

    # Start database
    docker-compose up -d db redis

    # Wait for PostgreSQL to be ready
    print_info "Waiting for PostgreSQL to be ready..."
    sleep 5

    until docker exec $DB_CONTAINER pg_isready -U $DB_USER -d $DB_NAME > /dev/null 2>&1; do
        echo -n "."
        sleep 1
    done
    echo ""

    # Run migrations
    print_info "Running database migrations..."
    cd agentdesk/backend
    alembic upgrade head
    cd ../..

    # Apply init scripts
    print_info "Applying initialization scripts..."
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME < agentdesk/backend/app/database/init_scripts.sql

    print_success "Database setup complete!"
}

# Command: backup
cmd_backup() {
    mkdir -p $BACKUP_DIR
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$BACKUP_DIR/agentdesk_backup_${TIMESTAMP}.dump"

    print_info "Creating backup..."
    docker exec $DB_CONTAINER pg_dump -U $DB_USER -d $DB_NAME -F c > $BACKUP_FILE

    print_success "Backup created: $BACKUP_FILE"
}

# Command: restore
cmd_restore() {
    if [ -z "$1" ]; then
        print_error "Please specify backup file to restore"
        exit 1
    fi

    if [ ! -f "$1" ]; then
        print_error "Backup file not found: $1"
        exit 1
    fi

    print_info "Restoring from backup: $1"
    print_info "WARNING: This will drop and recreate the database!"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        print_info "Restore cancelled"
        exit 0
    fi

    docker exec -i $DB_CONTAINER pg_restore -U $DB_USER -d $DB_NAME -c < $1

    print_success "Database restored successfully"
}

# Command: reset
cmd_reset() {
    print_info "WARNING: This will delete all data and reset the database!"
    read -p "Are you sure? (yes/no): " confirm

    if [ "$confirm" != "yes" ]; then
        print_info "Reset cancelled"
        exit 0
    fi

    print_info "Stopping services..."
    docker-compose down

    print_info "Removing database volume..."
    docker volume rm arcdeskai_postgres_data || true

    print_info "Starting fresh database..."
    cmd_setup

    print_success "Database reset complete"
}

# Command: migrate
cmd_migrate() {
    print_info "Running database migrations..."
    cd agentdesk/backend
    alembic upgrade head
    cd ../..
    print_success "Migrations complete"
}

# Command: rollback
cmd_rollback() {
    print_info "Rolling back last migration..."
    cd agentdesk/backend
    alembic downgrade -1
    cd ../..
    print_success "Rollback complete"
}

# Command: shell
cmd_shell() {
    print_info "Opening PostgreSQL shell..."
    docker exec -it $DB_CONTAINER psql -U $DB_USER -d $DB_NAME
}

# Command: stats
cmd_stats() {
    print_info "Database Statistics:"
    echo ""

    # Database size
    echo "Database Size:"
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \
        "SELECT pg_size_pretty(pg_database_size('$DB_NAME'));"
    echo ""

    # Table sizes
    echo "Top 10 Tables by Size:"
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \
        "SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
         FROM pg_tables
         WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
         ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
         LIMIT 10;"
    echo ""

    # Connection count
    echo "Active Connections:"
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c \
        "SELECT count(*) FROM pg_stat_activity;"
    echo ""
}

# Command: vacuum
cmd_vacuum() {
    print_info "Running VACUUM ANALYZE on database..."
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "VACUUM ANALYZE;"
    print_success "VACUUM ANALYZE complete"
}

# Command: refresh-views
cmd_refresh_views() {
    print_info "Refreshing materialized views..."
    docker exec $DB_CONTAINER psql -U $DB_USER -d $DB_NAME -c "SELECT refresh_all_mv();"
    print_success "Materialized views refreshed"
}

# Command: seed
cmd_seed() {
    print_info "Seeding database with sample data..."
    docker exec -i $DB_CONTAINER psql -U $DB_USER -d $DB_NAME << 'EOF'
-- Insert sample organization
INSERT INTO organizations (id, name, slug, subscription_tier, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000001',
    'Demo Organization',
    'demo-org',
    'professional',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert sample user
INSERT INTO users (id, organization_id, email, username, full_name, is_admin, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000001',
    'admin@demo.com',
    'admin',
    'Demo Admin',
    true,
    NOW()
) ON CONFLICT (email) DO NOTHING;

-- Insert sample CTO desk
INSERT INTO desks (id, organization_id, desk_id, title, role, llm_provider, llm_model, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000003',
    '00000000-0000-0000-0000-000000000001',
    'cto-001',
    'Chief Technology Officer',
    'executive',
    'anthropic',
    'claude-sonnet-4',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert sample developer desk
INSERT INTO desks (id, organization_id, desk_id, title, role, llm_provider, llm_model, reports_to_id, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000004',
    '00000000-0000-0000-0000-000000000001',
    'dev-001',
    'Senior Software Engineer',
    'senior_engineer',
    'anthropic',
    'claude-sonnet-4',
    '00000000-0000-0000-0000-000000000003',
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert sample workflow
INSERT INTO workflows (id, organization_id, name, description, stages, qa_enabled, is_default, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000005',
    '00000000-0000-0000-0000-000000000001',
    'Standard Development Workflow',
    'Default workflow for software development tasks',
    '[{"name": "planning", "order": 1}, {"name": "implementation", "order": 2}, {"name": "review", "order": 3}, {"name": "testing", "order": 4}, {"name": "deployment", "order": 5}]'::jsonb,
    true,
    true,
    NOW()
) ON CONFLICT (id) DO NOTHING;

-- Insert sample task
INSERT INTO tasks (id, organization_id, task_number, title, description, created_by_id, assigned_to_id, status, priority, created_at)
VALUES (
    '00000000-0000-0000-0000-000000000006',
    '00000000-0000-0000-0000-000000000001',
    1,
    'Build REST API for user authentication',
    'Implement a secure REST API endpoint for user authentication with JWT tokens',
    '00000000-0000-0000-0000-000000000002',
    '00000000-0000-0000-0000-000000000004',
    'assigned',
    'high',
    NOW()
) ON CONFLICT (id) DO NOTHING;

EOF

    print_success "Sample data seeded successfully"
}

# Command: logs
cmd_logs() {
    docker logs -f $DB_CONTAINER
}

# Help message
show_help() {
    cat << EOF
AgentDesk Database Management Script

Usage: $0 <command> [arguments]

Commands:
  setup              Set up and initialize the database
  backup             Create a database backup
  restore <file>     Restore database from backup file
  reset              Reset database (WARNING: deletes all data)
  migrate            Run pending migrations
  rollback           Rollback last migration
  shell              Open PostgreSQL shell
  stats              Show database statistics
  vacuum             Run VACUUM ANALYZE
  refresh-views      Refresh all materialized views
  seed               Seed database with sample data
  logs               Show database logs
  help               Show this help message

Examples:
  $0 setup
  $0 backup
  $0 restore backups/agentdesk_backup_20260105_120000.dump
  $0 shell
  $0 stats

EOF
}

# Main
case "${1:-}" in
    setup)
        cmd_setup
        ;;
    backup)
        cmd_backup
        ;;
    restore)
        cmd_restore "$2"
        ;;
    reset)
        cmd_reset
        ;;
    migrate)
        cmd_migrate
        ;;
    rollback)
        cmd_rollback
        ;;
    shell)
        cmd_shell
        ;;
    stats)
        cmd_stats
        ;;
    vacuum)
        cmd_vacuum
        ;;
    refresh-views)
        cmd_refresh_views
        ;;
    seed)
        cmd_seed
        ;;
    logs)
        cmd_logs
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: ${1:-}"
        echo ""
        show_help
        exit 1
        ;;
esac
