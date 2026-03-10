"""
Server package for llmmllab inference service.

This package provides:
- FastAPI application for inference endpoints
- Database access layer
- gRPC clients for inter-service communication
- Authentication and authorization middleware
"""

from config import CONFIG_DIR, IMAGE_DIR, AUTH_JWKS_URI, DB_CONNECTION_STRING
from db import storage
from grpc_client import (
    ComposerClient,
    RunnerClient,
    get_composer_client,
    get_runner_client,
)
from utils.logging import llmmllogger

__all__ = [
    "CONFIG_DIR",
    "IMAGE_DIR",
    "AUTH_JWKS_URI",
    "DB_CONNECTION_STRING",
    "storage",
    "ComposerClient",
    "RunnerClient",
    "get_composer_client",
    "get_runner_client",
    "llmmllogger",
]
