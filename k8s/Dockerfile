# Simple Python-based Dockerfile for Server service
# FastAPI HTTP server - no gRPC server needed

FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app:/app/gen/python" \
    SERVER_DIR="/app" \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT="8000"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY server/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - copy contents of server/ to /app/
# This allows Python to find config.py, db.py, etc. directly
COPY server/ /app/
COPY schemas/ /app/schemas/
COPY proto/ /app/proto/

# Copy pre-generated gRPC code (for composer and runner)
COPY server/gen/python /app/gen/python

# Generate gRPC code from proto files (for any new/updated protos)
RUN python -m grpc_tools.protoc \
    -I /app/proto \
    -I /usr/local/lib/python3.12/site-packages \
    --python_out=/app/gen/python \
    --grpc_python_out=/app/gen/python \
    /app/proto/composer/v1/server_composer.proto \
    /app/proto/common/timestamp.proto 2>&1 || true

# Expose HTTP port
EXPOSE 8000

# Run server (FastAPI via uvicorn)
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]