# Scaffold AI Backend

FastAPI + LangGraph backend for the Scaffold AI platform.

## Development

```bash
# Install dependencies
uv sync

# Run development server
uv run uvicorn scaffold_ai.main:app --reload

# Run tests
uv run pytest
```

## API Endpoints

- `GET /` - Health check
- `GET /health` - Health status
- `POST /api/chat` - Process chat messages through LangGraph
- `GET /api/graph` - Get sample graph for testing
