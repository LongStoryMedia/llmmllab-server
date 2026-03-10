# Server Makefile
# Manages build, test, and deployment of the server service

.PHONY: all build test lint start deploy build-image proto postgres postgres-stop clean help

all: build test

# =============================================================================
# Build (Python)
# =============================================================================

build:
	@echo "Building server..."
	@. .venv/bin/activate && python -m compileall .
	@echo "Server build complete"

# =============================================================================
# Testing
# =============================================================================

test:
	@echo "Running server tests..."
	@. .venv/bin/activate && pytest test/ -v
	@echo "Server tests complete"

test-unit:
	@echo "Running server unit tests..."
	@. .venv/bin/activate && pytest test/unit/ -v
	@echo "Server unit tests complete"

test-integration:
	@echo "Running server integration tests..."
	@. .venv/bin/activate && pytest test/integration/ -v
	@echo "Server integration tests complete"

test-cover:
	@echo "Running server tests with coverage..."
	@. .venv/bin/activate && pytest test/ --cov=server --cov-report=html
	@echo "Coverage report generated in htmlcov/index.html"

# =============================================================================
# Linting
# =============================================================================

lint:
	@echo "Running server linting..."
	@. .venv/bin/activate && PYTHONPATH="gen/python:." pylint --rcfile=.pylintrc server/ --disable=C,R,W0622,W0611,W0613,W0718,W0511 --max-line-length=120 --jobs=4
	@echo "Server linting complete"

lint-fix:
	@echo "Auto-fixing server linting issues..."
	@. .venv/bin/activate && pylint server/ --disable=C,R,W0622,W0611,W0613,W0718,W0511 --max-line-length=120 --jobs=4 --fix
	@echo "Server linting auto-fix complete"

# =============================================================================
# Development
# =============================================================================

start:
	@echo "Starting server in development mode..."
	@. .venv/bin/activate && IMAGE_DIR=/tmp/images CONFIG_DIR=/tmp/config PYTHONPATH="gen/python:." python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload

start-debug:
	@echo "Starting server with debug mode..."
	@. .venv/bin/activate && PYTHONPATH="gen/python:/home/lsm/Nextcloud/llmmllab:." python -m uvicorn app:app --host 0.0.0.0 --port 8000 --reload --log-level debug

# =============================================================================
# Proto Generation
# =============================================================================

proto:
	@echo "Generating server proto code..."
	@cd ../proto && make generate-server
	@echo "Server proto code generated"

# =============================================================================
# PostgreSQL (Local Development)
# =============================================================================

postgres:
	@echo "Starting PostgreSQL locally..."
	@chmod +x ./k8s/postgres/init-db.sh
	@docker compose -f k8s/postgres/local-docker-compose.yaml up -d
	@echo "PostgreSQL started on port 5432"
	@echo "Run 'make postgres-stop' to stop PostgreSQL"

postgres-stop:
	@echo "Stopping PostgreSQL..."
	@docker compose -f k8s/postgres/local-docker-compose.yaml down
	@echo "PostgreSQL stopped"

# =============================================================================
# Build
# =============================================================================

build-image:
	@echo "Building server Docker image..."
	@chmod +x ./k8s/build.sh
	@DOCKER_TAG=$(shell git rev-parse --abbrev-ref HEAD | tr '/' '.') ./k8s/build.sh

# =============================================================================
# Deployment
# =============================================================================

deploy: build-image
	@echo "Deploying server to k8s..."
	@chmod +x ./k8s/apply.sh
	@DOCKER_TAG=$(shell git rev-parse --abbrev-ref HEAD | tr '/' '.') ./k8s/apply.sh
	@kubectl rollout restart deployment llmmll-server -n llmmll --wait=true
	@echo "Server deployed successfully"

# =============================================================================
# Cleanup
# =============================================================================

clean:
	@echo "Cleaning server artifacts..."
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf __pycache__/
	rm -rf server/__pycache__/
	rm -rf server/*/__pycache__/
	rm -rf server/*/*/__pycache__/
	rm -rf server/*/*/*/__pycache__/
	rm -rf server/*/*/*/*/__pycache__/
	rm -rf server/*/*/*/*/*/__pycache__/
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Server artifacts cleaned"

# =============================================================================
# Help
# =============================================================================

help:
	@echo "Server Makefile"
	@echo ""
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  build           - Build the server"
	@echo "  test            - Run all server tests"
	@echo "  test-unit       - Run unit tests"
	@echo "  test-integration - Run integration tests"
	@echo "  test-cover      - Run tests with coverage report"
	@echo "  lint            - Run linting"
	@echo "  lint-fix        - Auto-fix linting issues"
	@echo "  start           - Start server in dev mode"
	@echo "  start-debug     - Start server with debug logging"
	@echo "  proto           - Generate proto code"
	@echo "  postgres        - Start PostgreSQL locally (Docker Compose)"
	@echo "  postgres-stop   - Stop PostgreSQL locally"
	@echo "  build-image     - Build Docker image"
	@echo "  deploy          - Build and deploy to k8s"
	@echo "  clean           - Clean artifacts"
	@echo "  help            - Show this help message"