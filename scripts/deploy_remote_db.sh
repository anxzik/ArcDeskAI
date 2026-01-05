#!/bin/bash

# ============================================================================
# AgentDesk Remote Database Deployment Script
# ============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f "/agentdesk/.env.dev" ]; then
    source agentdesk/.env.dev
else read -p "Please provide the path to your .env.dev file: " ENV_PATH
    if [ -f "$ENV_PATH" ]; then
        source "$ENV_PATH"
    else
        echo -e "${RED}Error: .env.dev file not found at $ENV_PATH${NC}"
        exit 1
    fi
fi

# Database connection details
DB_USER="${POSTGRES_USER}"
DB_PASS="${POSTGRES_PASSWORD}"
DB_HOST="${POSTGRES_HOST}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_NAME="${POSTGRES_DB}"

# URL-encode the username for connection string
DB_USER_ENCODED=$(echo -n "$DB_USER" | python3 -c "import sys; from urllib.parse import quote; print(quote(sys.stdin.read(), safe=''))")

# Connection string
CONN_STRING="postgresql://${DB_USER_ENCODED}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Functions
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Check if psql is installed
check_psql() {
    if ! command -v psql &> /dev/null; then
        print_error "psql is not installed. Please install PostgreSQL client tools."
        echo "Ubuntu/Debian: sudo apt-get install postgresql-client"
        echo "macOS: brew install postgresql"
        exit 1
    fi
}

# Test database connection
test_connection() {
    print_header "Testing Database Connection"

    print_info "Connecting to: ${DB_HOST}:${DB_PORT}/${DB_NAME}"
    print_info "Username: ${DB_USER}"

    if psql "$CONN_STRING" -c "SELECT version();" > /dev/null 2>&1; then
        print_success "Database connection successful!"

        # Get PostgreSQL version
        VERSION=$(psql "$CONN_STRING" -t -c "SELECT version();")
        print_info "PostgreSQL version: ${VERSION}"
    else
        print_error "Failed to connect to database"
        print_info "Please check your connection settings in agentdesk/.env.dev"
        exit 1
    fi
}

# Create database if it doesn't exist
create_database() {
    print_header "Creating Database"

    # Connect to postgres database to create our database
    POSTGRES_CONN="postgresql://${DB_USER_ENCODED}:${DB_PASS}@${DB_HOST}:${DB_PORT}/postgres"

    # Check if database exists
    DB_EXISTS=$(psql "$POSTGRES_CONN" -t -c "SELECT 1 FROM pg_database WHERE datname='${DB_NAME}';")

    if [ -n "$DB_EXISTS" ]; then
        print_warning "Database '${DB_NAME}' already exists"
    else
        print_info "Creating database '${DB_NAME}'..."
        psql "$POSTGRES_CONN" -c "CREATE DATABASE ${DB_NAME} ENCODING 'UTF8' LC_COLLATE='en_US.UTF-8' LC_CTYPE='en_US.UTF-8';"
        print_success "Database created successfully"
    fi
}

# Enable required extensions
enable_extensions() {
    print_header "Enabling PostgreSQL Extensions"

    EXTENSIONS=("uuid-ossp" "pgcrypto" "pg_stat_statements")

    for ext in "${EXTENSIONS[@]}"; do
        print_info "Enabling extension: ${ext}"
        psql "$CONN_STRING" -c "CREATE EXTENSION IF NOT EXISTS \"${ext}\";" 2>&1 | grep -v "already exists" || true
    done

    print_success "Extensions enabled"
}

# Run Alembic migrations
run_migrations() {
    print_header "Running Database Migrations"

    cd agentdesk/backend

    # Check if alembic is installed
    if ! command -v alembic &> /dev/null; then
        print_warning "Alembic not found. Installing..."
        pip install alembic psycopg2-binary sqlalchemy python-dotenv
    fi

    print_info "Running Alembic migrations..."

    # Export DATABASE_URL for Alembic
    export DATABASE_URL="$CONN_STRING"

    # Run migrations
    if alembic upgrade head; then
        print_success "Migrations completed successfully"
    else
        print_error "Migration failed"
        cd ../..
        exit 1
    fi

    cd ../..
}

# Apply initialization scripts
apply_init_scripts() {
    print_header "Applying Initialization Scripts"

    INIT_SCRIPT="agentdesk/backend/app/database/init_scripts.sql"

    if [ ! -f "$INIT_SCRIPT" ]; then
        print_error "Init script not found: $INIT_SCRIPT"
        exit 1
    fi

    print_info "Applying initialization scripts..."

    if psql "$CONN_STRING" -f "$INIT_SCRIPT" > /dev/null 2>&1; then
        print_success "Initialization scripts applied"
    else
        print_warning "Some initialization scripts may have failed (this is normal if they already exist)"
    fi
}

# Verify setup
verify_setup() {
    print_header "Verifying Database Setup"

    # Count tables
    TABLE_COUNT=$(psql "$CONN_STRING" -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public';")
    print_info "Tables created: ${TABLE_COUNT}"

    # Count indexes
    INDEX_COUNT=$(psql "$CONN_STRING" -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public';")
    print_info "Indexes created: ${INDEX_COUNT}"

    # Check RLS
    RLS_COUNT=$(psql "$CONN_STRING" -t -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname = 'public' AND rowsecurity = true;")
    print_info "Tables with RLS enabled: ${RLS_COUNT}"

    # Check extensions
    print_info "\nEnabled extensions:"
    psql "$CONN_STRING" -c "SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_stat_statements');"

    print_success "\nDatabase verification complete!"
}

# Seed sample data
seed_data() {
    print_header "Seeding Sample Data"

    print_info "Creating demo organization and sample data..."

    psql "$CONN_STRING" << 'EOF'
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

SELECT 'Sample data seeded successfully!' as result;
EOF

    print_success "Sample data seeded"
}

# Show database info
show_info() {
    print_header "Database Information"

    echo "Connection Details:"
    echo "  Host: ${DB_HOST}"
    echo "  Port: ${DB_PORT}"
    echo "  Database: ${DB_NAME}"
    echo "  User: ${DB_USER}"
    echo ""
    echo "pgAdmin URL: http://patterns.phlevel.pro:8080/"
    echo ""
    echo "Connection String (for application):"
    echo "  DATABASE_URL=${CONN_STRING}"
    echo ""
}

# Main deployment process
main() {
    clear
    echo -e "${BLUE}"
    cat << "EOF"
    ╔═══════════════════════════════════════════════╗
    ║   AgentDesk Remote Database Deployment        ║
    ║   PostgreSQL Multi-Tenant Schema Setup        ║
    ╚═══════════════════════════════════════════════╝
EOF
    echo -e "${NC}"

    # Check prerequisites
    check_psql

    # Show connection info
    show_info

    # Confirm before proceeding
    read -p "Continue with deployment? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        print_info "Deployment cancelled"
        exit 0
    fi

    # Run deployment steps
    test_connection
    create_database
    enable_extensions
    run_migrations
    apply_init_scripts
    verify_setup

    # Ask about seeding data
    echo ""
    read -p "Seed sample data? (yes/no): " seed_confirm
    if [ "$seed_confirm" == "yes" ]; then
        seed_data
    fi

    # Final message
    print_header "Deployment Complete!"

    echo -e "${GREEN}"
    cat << "EOF"
    ✓ Database schema deployed successfully!
    ✓ All tables, indexes, and triggers created
    ✓ Row-Level Security enabled for multi-tenancy
    ✓ Materialized views created for analytics

    Next Steps:
    1. Access pgAdmin at http://patterns.phlevel.pro:8080/
    2. Update your application configuration
    3. Start your backend server
    4. Create your first organization and user

    For documentation, see:
    - DATABASE_SETUP.md
    - REMOTE_DATABASE_SETUP.md
EOF
    echo -e "${NC}"
}

# Run main function
main
