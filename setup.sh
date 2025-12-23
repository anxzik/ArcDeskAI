#!/bin/bash
# AgentDesk Quick Setup Script
# This script helps you get started with AgentDesk development

set -e  # Exit on error

echo "🚀 AgentDesk Setup Script"
echo "========================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.11 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d " " -f 2 | cut -d "." -f 1,2)
echo "✅ Python $PYTHON_VERSION found"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "⚠️  Docker not found. Install Docker for the full experience."
    DOCKER_AVAILABLE=false
else
    echo "✅ Docker found"
    DOCKER_AVAILABLE=true
fi

# Check Git
if ! command -v git &> /dev/null; then
    echo "⚠️  Git not found. Install Git to version control your project."
    GIT_AVAILABLE=false
else
    echo "✅ Git found"
    GIT_AVAILABLE=true
fi

echo ""
echo "📁 Setting up project structure..."

# Create project directory
read -p "Enter project directory name (default: agentdesk): " PROJECT_DIR
PROJECT_DIR=${PROJECT_DIR:-agentdesk}

if [ -d "$PROJECT_DIR" ]; then
    read -p "Directory $PROJECT_DIR already exists. Continue? (y/n): " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        echo "Setup cancelled."
        exit 0
    fi
else
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

# Create directory structure
echo "Creating directory structure..."
mkdir -p src/{core,llm,api,plugins,ui,database,utils}
mkdir -p tests/{unit,integration,fixtures}
mkdir -p configs/{organizations,agent_templates}
mkdir -p plugins
mkdir -p scripts
mkdir -p docs

# Copy core files if available
if [ -f "../agentdesk_core.py" ]; then
    cp ../agentdesk_core.py src/core/agent.py
    echo "✅ Copied core agent implementation"
fi

if [ -f "../agentdesk_cli.py" ]; then
    cp ../agentdesk_cli.py ./agentdesk
    chmod +x ./agentdesk
    echo "✅ Copied CLI tool"
fi

if [ -f "../cybersec_org_config.yaml" ]; then
    cp ../cybersec_org_config.yaml configs/organizations/
    echo "✅ Copied sample organization config"
fi

# Initialize Git if available
if [ "$GIT_AVAILABLE" = true ]; then
    if [ ! -d ".git" ]; then
        read -p "Initialize Git repository? (y/n): " INIT_GIT
        if [ "$INIT_GIT" = "y" ]; then
            git init
            
            # Create .gitignore
            cat > .gitignore << 'GITIGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Environment
.env
.env.local
*.env

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# Database
*.db
*.sqlite
*.sqlite3

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# AgentDesk specific
.agentdesk/
GITIGNORE
            
            echo "✅ Git repository initialized"
        fi
    fi
fi

# Create .env.example
echo "Creating .env.example..."
cat > .env.example << 'ENVFILE'
# API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here
OPENAI_API_KEY=your_openai_key_here

# Database
DATABASE_URL=postgresql://agentdesk:agentdesk_dev@localhost:5432/agentdesk
REDIS_URL=redis://localhost:6379/0

# Application
ENV=development
DEBUG=true
SECRET_KEY=change-this-to-a-random-secret-key
LOG_LEVEL=INFO

# LLM Settings
DEFAULT_LLM_PROVIDER=anthropic
DEFAULT_LLM_MODEL=claude-sonnet-4-20250514
MAX_CONCURRENT_AGENTS=10
TASK_TIMEOUT=300

# API Settings
API_HOST=0.0.0.0
API_PORT=8000
ENVFILE

cp .env.example .env
echo "✅ Created .env file (remember to add your API keys!)"

# Create docker-compose.yml if Docker is available
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "Creating docker-compose.yml..."
    cat > docker-compose.yml << 'DOCKERCOMPOSE'
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

volumes:
  postgres_data:
  redis_data:
DOCKERCOMPOSE
    echo "✅ Created docker-compose.yml"
fi

# Setup Python virtual environment
echo ""
read -p "Create Python virtual environment? (y/n): " CREATE_VENV
if [ "$CREATE_VENV" = "y" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment created"
    echo ""
    echo "To activate it:"
    echo "  source venv/bin/activate  (Linux/Mac)"
    echo "  venv\\Scripts\\activate     (Windows)"
fi

# Install Poetry if requested
echo ""
read -p "Install Poetry for dependency management? (y/n): " INSTALL_POETRY
if [ "$INSTALL_POETRY" = "y" ]; then
    if ! command -v poetry &> /dev/null; then
        curl -sSL https://install.python-poetry.org | python3 -
        echo "✅ Poetry installed"
    else
        echo "✅ Poetry already installed"
    fi
    
    # Initialize poetry project
    if [ ! -f "pyproject.toml" ]; then
        poetry init --no-interaction --name agentdesk
        echo "✅ Poetry project initialized"
    fi
fi

# Create README
echo "Creating README.md..."
cat > README.md << 'README'
# AgentDesk

Hierarchical Multi-Agent AI Organization System

## Quick Start

1. Activate virtual environment:
   ```bash
   source venv/bin/activate  # Linux/Mac
   ```

2. Install dependencies:
   ```bash
   poetry install
   # or
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. Start infrastructure (if using Docker):
   ```bash
   docker-compose up -d
   ```

5. Run the example:
   ```bash
   python src/core/agent.py
   ```

## Documentation

See the `docs/` directory for detailed documentation.

## License

MIT
README
echo "✅ Created README.md"

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Edit .env with your API keys"
if [ "$DOCKER_AVAILABLE" = true ]; then
    echo "  3. Start infrastructure: docker-compose up -d"
fi
echo "  4. Install dependencies with Poetry or pip"
echo "  5. Read PROJECT_SUMMARY.md for implementation guide"
echo ""
echo "Happy coding! 🚀"
