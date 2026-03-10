# Simple Python-based Dockerfile for Server service
# FastAPI HTTP server - no gRPC server needed

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/server:/app/server/gen/python" \
    SERVER_DIR="/app/server" \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT="8000"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY schemas/ ./schemas/
COPY proto/ ./proto/

# Generate gRPC code from proto files
RUN python -m grpc_tools.protoc \
    -I ./proto \
    -I /usr/local/lib/python3.12/site-packages \
    --python_out=./server/gen/python \
    --grpc_python_out=./server/gen/python \
    ./proto/composer/v1/server_composer.proto \
    ./proto/common/timestamp.proto 2>&1 || true

# Expose HTTP port
EXPOSE 8000

# Run server (FastAPI via uvicorn)
CMD ["python", "-m", "uvicorn", "server.app:app", "--host", "0.0.0.0", "--port", "8000"]