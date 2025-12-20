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
