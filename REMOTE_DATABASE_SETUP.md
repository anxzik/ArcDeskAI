# Remote PostgreSQL Database Setup Guide

This guide will help you set up the AgentDesk database on your remote PostgreSQL server accessible via pgAdmin at http://patterns.phlevel.pro:8080/

## Connection Details

- **pgAdmin URL**: http://patterns.phlevel.pro:8080/
- **Database Host**: patterns.phlevel.pro
- **Database Port**: 5432
- **Username**: a.archer@architsec.com
- **Password**: adminpassword
- **Database Name**: agentdesk_prod

## Step 1: Access pgAdmin

1. Open your browser and navigate to http://patterns.phlevel.pro:8080/
2. Log in with your credentials:
   - Email: a.archer@architsec.com
   - Password: adminpassword

## Step 2: Create the Database

1. In pgAdmin, right-click on "Databases" under your server
2. Select "Create" → "Database"
3. Enter the following details:
   - **Database**: agentdesk_prod
   - **Owner**: a.archer@architsec.com
   - **Encoding**: UTF8
   - **Template**: template0
   - **Locale**: en_US.UTF-8
4. Click "Save"

## Step 3: Enable Required Extensions

1. Right-click on the `agentdesk_prod` database
2. Select "Query Tool"
3. Run the following SQL commands:

```sql
-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
```

## Step 4: Deploy the Database Schema

You have two options to deploy the schema:

### Option A: Using Alembic Migrations (Recommended)

1. Ensure your `.env.dev` file is configured with the remote database URL
2. Run the migration from your local machine:

```bash
cd agentdesk/backend

# Install dependencies if not already installed
pip install alembic psycopg2-binary sqlalchemy

# Run migrations
alembic upgrade head
```

### Option B: Using pgAdmin Query Tool

1. In pgAdmin, open the Query Tool for `agentdesk_prod` database
2. Open the migration file: `agentdesk/backend/migrations/versions/001_create_multi_tenant_schema.py`
3. Copy the SQL statements from the `upgrade()` function and paste them into the Query Tool
4. Execute the statements

Alternatively, you can execute the migration file directly:

1. Go to "Tools" → "Query Tool" in pgAdmin
2. Click "Open File" and select: `agentdesk/backend/app/database/init_scripts.sql`
3. Execute the script

## Step 5: Apply Initialization Scripts

1. In pgAdmin Query Tool for `agentdesk_prod`, run the initialization script:

```bash
# From your local machine, you can also run:
psql "postgresql://a.archer%40architsec.com:adminpassword@patterns.phlevel.pro:5432/agentdesk_prod" \
  -f agentdesk/backend/app/database/init_scripts.sql
```

Or copy the contents of `agentdesk/backend/app/database/init_scripts.sql` and paste it into pgAdmin's Query Tool.

## Step 6: Verify the Setup

Run the following queries in pgAdmin to verify the setup:

```sql
-- Check that all tables were created
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;

-- Check that enum types were created
SELECT typname
FROM pg_type
WHERE typcategory = 'E'
ORDER BY typname;

-- Check that indexes were created
SELECT indexname, tablename
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- Check that RLS is enabled
SELECT schemaname, tablename, rowsecurity
FROM pg_tables
WHERE schemaname = 'public' AND rowsecurity = true;

-- Check extensions
SELECT extname, extversion
FROM pg_extension
WHERE extname IN ('uuid-ossp', 'pgcrypto', 'pg_stat_statements');
```

## Step 7: Update Backend Configuration

The `.env.dev` file has already been updated with your remote database credentials. Verify it contains:

```bash
POSTGRES_USER=a.archer@architsec.com
POSTGRES_PASSWORD=adminpassword
POSTGRES_DB=agentdesk_prod
POSTGRES_HOST=patterns.phlevel.pro
POSTGRES_PORT=5432

# URL-encoded connection string (@ is encoded as %40)
DATABASE_URL=postgresql://a.archer%40architsec.com:adminpassword@patterns.phlevel.pro:5432/agentdesk_prod
```

## Step 8: Test Connection from Application

Test the connection from your application:

```bash
cd agentdesk/backend

# Create a test script
cat > test_connection.py << 'EOF'
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

load_dotenv('.env.dev')

DATABASE_URL = os.getenv('DATABASE_URL')
print(f"Connecting to: {DATABASE_URL.replace(os.getenv('POSTGRES_PASSWORD'), '***')}")

try:
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        print(f"✓ Connected successfully!")
        print(f"PostgreSQL version: {version}")

        # Test table access
        result = conn.execute(text("SELECT COUNT(*) FROM organizations;"))
        count = result.fetchone()[0]
        print(f"✓ Organizations table accessible (count: {count})")

except Exception as e:
    print(f"✗ Connection failed: {e}")
EOF

# Run the test
python test_connection.py
```

## Step 9: Seed Sample Data (Optional)

To add sample data for testing:

```sql
-- In pgAdmin Query Tool, run:

-- Insert sample organization
INSERT INTO organizations (id, name, slug, subscription_tier, created_at)
VALUES (
    uuid_generate_v4(),
    'Demo Organization',
    'demo-org',
    'professional',
    NOW()
);

-- Get the organization ID (save this for next steps)
SELECT id, name, slug FROM organizations WHERE slug = 'demo-org';

-- Replace 'YOUR_ORG_ID' below with the actual UUID from above

-- Insert sample user
INSERT INTO users (id, organization_id, email, username, full_name, is_admin, created_at)
VALUES (
    uuid_generate_v4(),
    'YOUR_ORG_ID',
    'admin@demo.com',
    'admin',
    'Demo Admin',
    true,
    NOW()
);

-- Insert sample desk
INSERT INTO desks (
    id, organization_id, desk_id, title, role,
    llm_provider, llm_model, created_at
)
VALUES (
    uuid_generate_v4(),
    'YOUR_ORG_ID',
    'cto-001',
    'Chief Technology Officer',
    'executive',
    'anthropic',
    'claude-sonnet-4',
    NOW()
);
```

## Troubleshooting

### Cannot Connect to Remote Database

1. **Check Firewall**: Ensure port 5432 is open on the remote server
2. **Check PostgreSQL Configuration**: Verify `pg_hba.conf` allows connections from your IP
3. **Test with psql**:

```bash
psql "postgresql://a.archer%40architsec.com:adminpassword@patterns.phlevel.pro:5432/agentdesk_prod" -c "SELECT 1;"
```

### Permission Denied Errors

1. Verify your user has the necessary permissions:

```sql
-- Grant all privileges on database
GRANT ALL PRIVILEGES ON DATABASE agentdesk_prod TO "a.archer@architsec.com";

-- Grant all privileges on schema
GRANT ALL PRIVILEGES ON SCHEMA public TO "a.archer@architsec.com";

-- Grant all privileges on all tables
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO "a.archer@architsec.com";

-- Grant all privileges on all sequences
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO "a.archer@architsec.com";
```

### SSL/TLS Connection Issues

If the server requires SSL, update your DATABASE_URL:

```bash
DATABASE_URL=postgresql://a.archer%40architsec.com:adminpassword@patterns.phlevel.pro:5432/agentdesk_prod?sslmode=require
```

## Backup and Maintenance

### Create Backup via pgAdmin

1. Right-click on `agentdesk_prod` database
2. Select "Backup..."
3. Choose format: "Custom"
4. Specify filename: `agentdesk_backup_YYYYMMDD.dump`
5. Click "Backup"

### Create Backup via Command Line

```bash
pg_dump "postgresql://a.archer%40architsec.com:adminpassword@patterns.phlevel.pro:5432/agentdesk_prod" \
  -F c \
  -f agentdesk_backup_$(date +%Y%m%d).dump
```

### Restore from Backup

```bash
pg_restore \
  -d "postgresql://a.archer%40architsec.com:adminpassword@patterns.phlevel.pro:5432/agentdesk_prod" \
  -c \
  agentdesk_backup_20260105.dump
```

## Security Recommendations

Since this is a production database:

1. **Change Default Password**: Update the password for `a.archer@architsec.com`
2. **Create Dedicated User**: Consider creating a dedicated database user for the application
3. **Enable SSL**: Require SSL connections for all remote access
4. **Whitelist IPs**: Restrict database access to known IP addresses
5. **Regular Backups**: Set up automated daily backups
6. **Monitor Access**: Review audit logs regularly

## Next Steps

After setting up the database:

1. Configure your application to use the remote database
2. Set up continuous backups
3. Configure monitoring and alerting
4. Set up read replicas if needed for scaling
5. Review and adjust PostgreSQL performance settings

## Support

If you encounter any issues:
- Check the PostgreSQL logs in pgAdmin
- Review the `audit_logs` table for application-level issues
- Contact your database administrator
- Open an issue on the AgentDesk GitHub repository
