# AgentDesk - Quick Start Guide

## Project Overview
AgentDesk is a hierarchical multi-agent AI system that enables LLM agents to collaborate within defined organizational structures.

## Project Structure

```
agentdesk/
├── src/
│   ├── __init__.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── agent.py              # AgentDesk class
│   │   ├── hierarchy.py          # OrganizationStructure
│   │   ├── tasks.py              # Task management
│   │   ├── memory.py             # Agent memory system
│   │   └── qa.py                 # QA/QI pipeline
│   │
│   ├── llm/
│   │   ├── __init__.py
│   │   ├── base.py               # Base LLM interface
│   │   ├── anthropic_client.py   # Claude integration
│   │   ├── openai_client.py      # GPT integration
│   │   ├── local_client.py       # Ollama/local models
│   │   └── router.py             # LLM provider router
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI app
│   │   ├── routes/
│   │   │   ├── desks.py
│   │   │   ├── tasks.py
│   │   │   ├── organization.py
│   │   │   └── websockets.py
│   │   └── schemas.py            # Pydantic models
│   │
│   ├── plugins/
│   │   ├── __init__.py
│   │   ├── base.py               # Plugin base class
│   │   ├── manager.py            # Plugin manager
│   │   └── builtin/
│   │       ├── github.py
│   │       ├── slack.py
│   │       └── jira.py
│   │
│   ├── ui/
│   │   ├── electron/             # Electron app
│   │   │   ├── main.js
│   │   │   ├── preload.js
│   │   │   └── package.json
│   │   └── web/                  # React frontend
│   │       ├── src/
│   │       │   ├── components/
│   │       │   ├── pages/
│   │       │   ├── hooks/
│   │       │   └── App.tsx
│   │       └── package.json
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py             # SQLAlchemy models
│   │   ├── migrations/           # Alembic migrations
│   │   └── session.py            # Database session
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py             # Configuration management
│       ├── logging.py            # Logging setup
│       └── security.py           # Security utilities
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
│
├── configs/
│   ├── organizations/            # Sample org configs
│   │   ├── dev_team.yaml
│   │   ├── research_lab.yaml
│   │   └── startup.yaml
│   └── agent_templates/          # Reusable agent configs
│       ├── cto.yaml
│       ├── senior_dev.yaml
│       └── qa_engineer.yaml
│
├── plugins/                      # User-installed plugins
│   └── README.md
│
├── scripts/
│   ├── setup.sh                  # Initial setup
│   ├── run_dev.sh                # Development server
│   └── deploy.sh                 # Deployment script
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── plugin_development.md
│   └── user_guide.md
│
├── .env.example
├── .gitignore
├── pyproject.toml               # Poetry dependencies
├── docker-compose.yml           # Local development
├── Dockerfile
├── LICENSE
└── README.md
```

## Initial Setup

### Prerequisites
- Python 3.11+
- Node.js 18+ (for UI)
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose (optional but recommended)

### Step 1: Clone and Setup Environment

```bash
# Create project directory
mkdir agentdesk && cd agentdesk

# Initialize git
git init

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Poetry (alternative to pip)
curl -sSL https://install.python-poetry.org | python3 -
```

### Step 2: Initialize Poetry Project

```bash
# Initialize pyproject.toml
poetry init --no-interaction

# Add core dependencies
poetry add \
    fastapi \
    uvicorn[standard] \
    sqlalchemy \
    alembic \
    redis \
    pydantic \
    pydantic-settings \
    python-dotenv \
    anthropic \
    openai \
    langchain \
    langchain-anthropic \
    langchain-openai \
    chromadb \
    asyncio \
    aiohttp \
    websockets \
    pyyaml \
    click \
    rich \
    typer

# Add development dependencies
poetry add --group dev \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    ruff \
    mypy \
    pre-commit \
    httpx
```

### Step 3: Create Configuration Files

#### `.env.example`
```env
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/agentdesk
REDIS_URL=redis://localhost:6379/0

# Application
ENV=development
DEBUG=true
SECRET_KEY=your-secret-key-change-this
LOG_LEVEL=INFO

# LLM Settings
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_LLM_MODEL=claude-sonnet-4-20250514
MAX_CONCURRENT_AGENTS=10
TASK_TIMEOUT=300

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
```

#### `docker-compose.yml`
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: agentdesk
      POSTGRES_PASSWORD: agentdesk_dev
      POSTGRES_DB: agentdesk
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  agentdesk-api:
    build: .
    command: uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://agentdesk:agentdesk_dev@postgres:5432/agentdesk
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
  redis_data:
```

#### `Dockerfile`
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

# Install dependencies
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Copy application
COPY . .

# Expose port
EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Step 4: Sample Organization Configuration

#### `configs/organizations/dev_team.yaml`
```yaml
organization:
  name: "Development Team"
  description: "Standard software development organization"

desks:
  - id: "cto-001"
    title: "Chief Technology Officer"
    role: "executive"
    llm:
      provider: "anthropic"
      model: "claude-sonnet-4-20250514"
      temperature: 0.7
      max_tokens: 4000
    capabilities:
      - strategic_planning
      - architecture_design
      - team_coordination
      - technical_leadership
    hierarchy_level: 1
    
  - id: "eng-manager-001"
    title: "Engineering Manager"
    role: "manager"
    llm:
      provider: "anthropic"
      model: "claude-sonnet-4-20250514"
      temperature: 0.5
    reports_to: "cto-001"
    team_id: "engineering"
    capabilities:
      - project_management
      - code_review
      - mentoring
      - resource_allocation
    hierarchy_level: 2
    
  - id: "senior-dev-001"
    title: "Senior Software Engineer"
    role: "senior_engineer"
    llm:
      provider: "anthropic"
      model: "claude-sonnet-4-20250514"
      temperature: 0.3
    reports_to: "eng-manager-001"
    team_id: "engineering"
    capabilities:
      - code_generation
      - architecture_design
      - code_review
      - debugging
      - documentation
      - testing
    tools:
      - bash
      - python_repl
      - file_operations
      - git
    hierarchy_level: 3
    
  - id: "qa-001"
    title: "QA Engineer"
    role: "qa_engineer"
    llm:
      provider: "openai"
      model: "gpt-4"
      temperature: 0.2
    reports_to: "eng-manager-001"
    team_id: "quality"
    capabilities:
      - testing
      - test_automation
      - quality_assurance
      - bug_reporting
    tools:
      - test_runner
      - coverage_analyzer
    hierarchy_level: 3
    
  - id: "security-001"
    title: "Security Analyst"
    role: "security_analyst"
    llm:
      provider: "anthropic"
      model: "claude-sonnet-4-20250514"
      temperature: 0.1
    reports_to: "cto-001"
    team_id: "security"
    capabilities:
      - security_analysis
      - vulnerability_scanning
      - code_audit
      - compliance_check
    tools:
      - security_scanner
      - dependency_checker
    hierarchy_level: 2

teams:
  - id: "engineering"
    name: "Engineering Team"
    lead: "eng-manager-001"
    members:
      - "eng-manager-001"
      - "senior-dev-001"
      
  - id: "quality"
    name: "Quality Assurance"
    lead: "qa-001"
    members:
      - "qa-001"
      
  - id: "security"
    name: "Security Team"
    lead: "security-001"
    members:
      - "security-001"

committees:
  - id: "architecture-review"
    name: "Architecture Review Board"
    chair: "cto-001"
    members:
      - "cto-001"
      - "senior-dev-001"
      - "security-001"
    purpose: "Review and approve major architectural decisions"
    
  - id: "code-review"
    name: "Code Review Committee"
    chair: "eng-manager-001"
    members:
      - "eng-manager-001"
      - "senior-dev-001"
      - "qa-001"
    purpose: "Ensure code quality standards"

qa_pipeline:
  enabled: true
  required_for:
    - "code"
    - "documentation"
    - "infrastructure"
  stages:
    - type: "automated_tests"
      agent: "qa-001"
      timeout: 300
      
    - type: "code_review"
      assignee: "senior-dev-001"
      criteria:
        - "code_quality"
        - "best_practices"
        - "documentation"
        
    - type: "security_scan"
      agent: "security-001"
      required_for_priority: ["high", "critical"]
      
    - type: "manager_approval"
      agent: "eng-manager-001"
      required_for_priority: ["critical"]

workflows:
  new_feature:
    name: "New Feature Development"
    steps:
      - name: "Requirements Analysis"
        assigned_role: "manager"
        
      - name: "Design & Architecture"
        assigned_role: "senior_engineer"
        requires_committee: "architecture-review"
        
      - name: "Implementation"
        assigned_role: "senior_engineer"
        
      - name: "Testing"
        assigned_role: "qa_engineer"
        
      - name: "Security Review"
        assigned_role: "security_analyst"
        
      - name: "Deployment Approval"
        assigned_role: "manager"
```

## Running the Project

### Development Mode

```bash
# Start infrastructure
docker-compose up -d postgres redis

# Copy environment file
cp .env.example .env
# Edit .env with your API keys

# Run migrations
poetry run alembic upgrade head

# Start API server
poetry run uvicorn src.api.main:app --reload --port 8000

# In another terminal, start the UI (when ready)
cd src/ui/web
npm install
npm run dev
```

### Full Stack with Docker

```bash
# Build and start all services
docker-compose up --build

# API available at: http://localhost:8000
# Docs available at: http://localhost:8000/docs
```

## First Tasks to Complete

1. **Set up the basic project structure** (follow directory layout above)
2. **Implement core agent system** (use provided agentdesk_core.py as base)
3. **Create FastAPI endpoints** for desk and task management
4. **Integrate Anthropic SDK** for Claude agents
5. **Build simple CLI** for testing without GUI
6. **Add database models** with SQLAlchemy
7. **Implement task queue** with Redis
8. **Create basic React dashboard** for monitoring

## Testing Your Setup

```bash
# Create a simple test script
cat > test_setup.py << 'EOF'
import asyncio
from agentdesk_core import (
    AgentDesk, AgentRole, LLMConfig, 
    OrganizationStructure, Priority
)

async def test():
    org = OrganizationStructure("Test Org")
    
    desk = AgentDesk(
        desk_id="test-001",
        title="Test Agent",
        role=AgentRole.ENGINEER,
        llm_config=LLMConfig(
            provider="anthropic",
            model="claude-sonnet-4-20250514"
        )
    )
    org.add_desk(desk)
    
    task = org.create_task(
        title="Test task",
        description="Testing the system",
        created_by="user-001"
    )
    
    print(f"Created task: {task.task_id}")
    print(f"Organization has {len(org.desks)} desks")
    
asyncio.run(test())
EOF

# Run the test
python test_setup.py
```

## Next Steps

1. **Week 1-2**: Set up infrastructure and core classes
2. **Week 3-4**: Implement LLM integrations and task processing
3. **Week 5-6**: Build API and basic web interface
4. **Week 7-8**: Add QA pipeline and delegation logic

## Resources

- Architecture Document: See `AI_ORG_ARCHITECTURE.md`
- Core Implementation: See `agentdesk_core.py`
- API Documentation: Will be at `/docs` when API is running
- Example Organizations: See `configs/organizations/`

## Troubleshooting

### Common Issues

**Import errors:**
```bash
# Make sure you're in the virtual environment
poetry shell
# Or activate venv
source venv/bin/activate
```

**Database connection failed:**
```bash
# Check PostgreSQL is running
docker-compose ps
# Check connection string in .env
```

**LLM API errors:**
```bash
# Verify API keys are set
echo $ANTHROPIC_API_KEY
# Check .env file has correct keys
```

## Community & Support

- GitHub Issues: [Will be created]
- Documentation: [Will be created]
- Discord: [Will be created]

---

**Ready to start building!** Begin with the core agent system and gradually add features. The modular architecture makes it easy to develop and test components independently.
