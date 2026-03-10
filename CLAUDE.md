# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in the llmmllab-server repository.

## Commands

### Development

```bash
# Start server in development mode
make start

# Start with debug logging
make start-debug

# Run tests
make test

# Run linting
make lint
```

### Integration

```bash
# Build and deploy to k8s
make deploy

# Build Docker image only
make build-image
```

### Validation & Linting

```bash
make validate       # Python compileall + Pyright type check
make lint
```

### Code Generation

```bash
# Regenerate gRPC code from proto files
make proto

# Regenerate models from YAML schemas
# (run from llmmllab-schemas repo)
make gen-python
make gen-typescript
```

## Architecture

### Structure

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

### Key Architectural Patterns

**Schema-Driven Development**: All data contracts are defined as YAML schemas in llmmllab-schemas. The `schema2code` tool generates `server/models/*.py` and `ui/src/types/*.ts` from these. **Never edit generated model files directly** — edit the YAML schema and regenerate.

**Provider Compatibility**: The server implements both OpenAI-compatible endpoints (`routers/openai/`) and Anthropic-compatible endpoints (`routers/anthropic/`). These share the underlying runner/pipeline infrastructure.

**Streaming**: Chat and image responses stream token-by-token. The streaming architecture is documented in `docs/PIPELINE_DOCUMENTATION_OVERVIEW.md`.

**gRPC Clients**: The server provides gRPC client interfaces for inter-service communication with Composer and Runner services.

**Multi-Tier Caching**: User config flows in-memory → Redis → PostgreSQL. See `docs/multi_tier_user_config_caching.md`.

### Key Entry Points

| Component | Entry Point |
|-----------|-------------|
| FastAPI app | `server.app:app` |
| OpenAI chat endpoint | `server/routers/openai/chat.py` |
| Anthropic messages endpoint | `server/routers/anthropic/messages.py` |
| gRPC client (Composer) | `server.ComposerClient` or `server.get_composer_client()` |
| gRPC client (Runner) | `server.RunnerClient` or `server.get_runner_client()` |
| gRPC client (Protocol) | `server.ComposerClientProtocol`, `server.RunnerClientProtocol` |

### gRPC Clients

The server provides gRPC client interfaces for inter-service communication. The gRPC code is generated to `server/gen/python/`:

**ComposerClient**:
- `compose_workflow()`: Create a workflow via Composer service
- `execute_workflow()`: Execute a workflow with streaming
- `create_initial_state()`: Create initial workflow state
- `clear_workflow_cache()`: Clear cached workflows
- `health_check()`: Check Composer service health

**RunnerClient**:
- `execute_pipeline()`: Execute a pipeline via Runner service
- `get_model_info()`: Get model information
- `generate_embeddings()`: Generate embeddings for texts
- `get_cache_stats()`: Get pipeline cache statistics
- `evict_pipeline()`: Evict a pipeline from cache
- `health_check()`: Check Runner service health

**Protocol Interfaces** (for type-safe DI):
- `server.ComposerClientProtocol`
- `server.RunnerClientProtocol`

Use `server.get_composer_client()` and `server.get_runner_client()` to get singleton instances.

**gRPC Package Structure**:
```
server/gen/python/
├── common/              # Common protobuf types (timestamp)
│   └── timestamp_pb2.py
└── server_composer/v1/  # ComposerService definitions
    ├── server_composer_pb2.py
    └── server_composer_pb2_grpc.py
```

### Configuration

- Python type checking: `pyrightconfig.json` (Python 3.12, basic mode)
- ESLint: `ui/.eslintrc.cjs` (xo + TypeScript + React hooks, 2-space indent)

### Environment Variables

Key environment variables for the server:

- `DB_CONNECTION_STRING`: PostgreSQL connection string
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration
- `AUTH_JWKS_URI`: JWT authentication JWKS endpoint
- `HF_HOME`: Hugging Face cache directory
- `LOG_LEVEL`: Logging level (trace, debug, info, warning, error)

## Dependencies

- **llmmllab-schemas** - YAML schema definitions (for models)
- **llmmllab-proto** - Protocol Buffer definitions (for gRPC)
- **llmmllab-composer** - gRPC service for workflow orchestration
- **llmmllab-runner** - gRPC service for model execution