# llmmllab-server

FastAPI inference service for llmmllab. Provides OpenAI-compatible REST API, Anthropic-compatible endpoints, and gRPC services.

## Overview

The llmmllab-server provides:

- OpenAI-compatible REST API endpoints
- Anthropic-compatible messages API endpoints
- gRPC services for inter-service communication (Composer, Runner)
- Model inference orchestration
- Multi-tier caching (in-memory → Redis → PostgreSQL)

## Architecture

```
server/
├── app.py                  # FastAPI app entry point
├── config.py               # Configuration management
├── routers/                # API routers
│   ├── openai/             # OpenAI-compatible endpoints
│   ├── anthropic/          # Anthropic-compatible endpoints
│   └── common/             # Shared endpoints (models, files)
├── middleware/             # Request/response middleware
│   ├── auth.py             # Authentication
│   ├── db.py               # Database initialization
│   └── validation.py       # Request validation
├── db/                     # Database layer
│   ├── multi_tier_cache.py # User config caching (memory → Redis → DB)
│   └── postgres.py         # PostgreSQL client
├── grpc_client.py          # gRPC client for inter-service communication
├── grpc_interceptors.py    # gRPC interceptors
├── gen/                    # Generated code (do not edit)
│   └── python/             # Python generated code
│       └── server_composer/v1/  # Composer gRPC modules
├── models/                 # Pydantic models (auto-generated)
├── utils/                  # Utilities
└── test/                   # Test suite
```

## Installation

```bash
# Create a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Code Generation

The server uses gRPC for inter-service communication and Pydantic models generated from YAML schemas.

**Generate gRPC code from proto files:**
```bash
make proto
```

This generates Python gRPC code from the proto files in `../proto/`.

**Generate models from YAML schemas:**
```bash
# From the llmmllab-schemas repository
make gen-python
make gen-typescript
```

This generates Python Pydantic models and TypeScript types from the YAML schemas.

### Local Development Database

For local development, you can run PostgreSQL using Docker Compose:

```bash
# Start PostgreSQL
make postgres

# Stop PostgreSQL
make postgres-stop
```

The PostgreSQL container is configured with:
- User: `lsm`
- Password: `postgres` (default, configurable via `POSTGRES_PASSWORD` env var)
- Database: `llmmll`
- Port: `5432` (default)

**Environment variables for local PostgreSQL:**
- `POSTGRES_USER` - Database user (default: `lsm`)
- `POSTGRES_PASSWORD` - Database password (default: `postgres`)
- `POSTGRES_DB` - Database name (default: `llmmll`)
- `POSTGRES_PORT` - Port to expose (default: `5432`)

When running locally, configure your server with:
```bash
DB_CONNECTION_STRING=postgresql://lsm:postgres@localhost:5432/llmmll
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Usage

### Development

```bash
# Start FastAPI server
make start

# Start with debug logging
make start-debug

# Run tests
make test

# Run linting
make lint
```

### Build & Deploy

```bash
# Build Docker image
make build-image

# Deploy to k8s
make deploy
```

## Dependencies

- **llmmllab-schemas** - YAML schema definitions (for models)
- **llmmllab-proto** - Protocol Buffer definitions (for gRPC)
- **llmmllab-composer** - gRPC service for workflow orchestration
- **llmmllab-runner** - gRPC service for model execution

## API Documentation

When running the server, visit:
- REST API docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## gRPC Clients

The server provides gRPC client interfaces for inter-service communication:

**ComposerClient**:
- `compose_workflow()` - Create a workflow via Composer service
- `execute_workflow()` - Execute a workflow with streaming
- `create_initial_state()` - Create initial workflow state
- `clear_workflow_cache()` - Clear cached workflows
- `health_check()` - Check Composer service health

**RunnerClient**:
- `execute_pipeline()` - Execute a pipeline via Runner service
- `get_model_info()` - Get model information
- `generate_embeddings()` - Generate embeddings for texts
- `get_cache_stats()` - Get pipeline cache statistics
- `evict_pipeline()` - Evict a pipeline from cache
- `health_check()` - Check Runner service health

## Provider Compatibility

The server implements both OpenAI and Anthropic compatible endpoints:

- **OpenAI**: `routers/openai/` - Chat, completions, embeddings, images
- **Anthropic**: `routers/anthropic/` - Messages, beta tools

These share the underlying runner/pipeline infrastructure.

## Environment Variables

Key environment variables for the server:

- `DB_CONNECTION_STRING`: PostgreSQL connection string
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration
- `AUTH_JWKS_URI`: JWT authentication JWKS endpoint
- `HF_HOME`: Hugging Face cache directory
- `LOG_LEVEL`: Logging level (trace, debug, info, warning, error)