"""
Server Application.

The server is the DB gateway and API endpoint provider for the llmmllab system.
It handles:
- Database access (PostgreSQL, Redis, in-memory storage)
- API endpoints (OpenAI-compatible, Anthropic-compatible)
- Communication with runner and composer services
- User authentication and authorization

gRPC Clients:
- ComposerClient: Interface for workflow composition and execution
- RunnerClient: Interface for pipeline management and execution
"""

from typing import Any, Optional, AsyncIterator, Protocol, Dict

from google.protobuf.timestamp_pb2 import Timestamp
from composer.v1 import server_composer_pb2, server_composer_pb2_grpc
from runner.v1 import runner_pb2, runner_pb2_grpc

from db import Storage
from config import (
    AUTH_ISSUER,
    AUTH_AUDIENCE,
    AUTH_CLIENT_ID,
    AUTH_CLIENT_SECRET,
    AUTH_JWKS_URI,
    DB_CONNECTION_STRING,
    REDIS_ENABLED,
    REDIS_HOST,
    REDIS_PORT,
    REDIS_PASSWORD,
    REDIS_DB,
    REDIS_CONVERSATION_TTL,
    REDIS_MESSAGE_TTL,
    REDIS_SUMMARY_TTL,
    REDIS_POOL_SIZE,
    REDIS_MIN_IDLE_CONNECTIONS,
    REDIS_CONNECT_TIMEOUT,
    HF_HOME,
    MESSAGES_BEFORE_SUMMARY,
    INFERENCE_SERVICES_OLLAMA_BASE_URL,
    INFERENCE_SERVICES_SD_BASE_URL,
    INFERENCE_SERVICES_HOST,
    INFERENCE_SERVICES_PORT,
    INTERNAL_API_KEY,
    VLLM_MODEL,
    VLLM_TENSOR_PARALLEL_SIZE,
    VLLM_GPU_MEMORY_UTILIZATION,
    VLLM_MAX_MODEL_LEN,
    VLLM_DTYPE,
    VLLM_TRUST_REMOTE_CODE,
    OPENAI_DEFAULT_MAX_TOKENS,
    OPENAI_DEFAULT_TEMPERATURE,
    OPENAI_MAX_CONCURRENT_REQUESTS,
)
from datetime import datetime

import grpc as grpcio
from grpc.aio import Channel

# Runner imports are handled in TYPE_CHECKING block above
# from runner.v1 import (
#     runner_pb2 as composer_runner_pb2,
#     runner_pb2_grpc as composer_runner_pb2_grpc,
# )


class ComposerGRPCClient:
    """
    gRPC client for communicating with the Composer service.

    This client is used by the server to:
    - Compose workflows
    - Execute workflows
    - Create initial workflow state
    - Clear workflow caches
    """

    def __init__(self, target: str = "localhost:50051"):
        """
        Initialize the Composer gRPC client.

        Args:
            target: Target address for the Composer service
        """
        self.target = target
        self._channel: Optional[Channel] = None
        self._stub: Optional[server_composer_pb2_grpc.ComposerServiceStub] = None

    @property
    def channel(self) -> Channel:
        """Get or create the gRPC channel."""
        if self._channel is None:
            self._channel = grpcio.aio.insecure_channel(self.target)
        return self._channel

    @property
    def stub(self) -> server_composer_pb2_grpc.ComposerServiceStub:
        """Get or create the gRPC stub."""
        if self._stub is None:
            self._stub = server_composer_pb2_grpc.ComposerServiceStub(self.channel)
        return self._stub

    async def compose_workflow(
        self,
        user_id: str,
        workflow_type: str,
        model_name: str,
        timestamp: Optional[datetime] = None,
        user_config: Optional[Dict[str, str]] = None,
        timeout: float = 30.0,
    ) -> server_composer_pb2.WorkflowHandle:
        """
        Compose a new workflow from requirements.

        Args:
            user_id: User ID for the workflow
            workflow_type: Type of workflow to create
            model_name: Model to use for the workflow
            timestamp: Optional timestamp for the workflow
            user_config: Optional user configuration overrides
            timeout: Request timeout in seconds (default: 30)

        Returns:
            WorkflowHandle with the created workflow ID
        """

        request = server_composer_pb2.ComposeWorkflowRequest(
            user_id=user_id,
            workflow_type=workflow_type,
            model_name=model_name,
            timestamp=timestamp
            or server_composer_pb2.Timestamp(seconds=int(datetime.now().timestamp())),
            user_config=user_config or {},
        )
        return await self._stub.ComposeWorkflow(request, timeout=timeout)

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_state: server_composer_pb2.WorkflowState,
        stream_events: bool = True,
        timeout: float = 60.0,
    ) -> Any:
        """
        Execute a workflow with streaming responses.

        Args:
            workflow_id: ID of the workflow to execute
            initial_state: Initial state for the workflow
            stream_events: Whether to stream events or return final result
            timeout: Request timeout in seconds (default: 60)

        Returns:
            Async iterator of ChatResponse messages
        """
        request = server_composer_pb2.ExecuteWorkflowRequest(
            workflow_id=workflow_id,
            initial_state=initial_state,
            stream_events=stream_events,
        )
        return self._stub.ExecuteWorkflow(request, timeout=timeout)

    async def create_initial_state(
        self,
        user_id: str,
        conversation_id: int,
        workflow_type: str,
        timeout: float = 30.0,
    ) -> server_composer_pb2.WorkflowState:
        """
        Create initial state for a workflow.

        Args:
            user_id: User ID for the workflow
            conversation_id: Conversation ID to base state on
            workflow_type: Type of workflow to create state for
            timeout: Request timeout in seconds (default: 30)

        Returns:
            WorkflowState with initial state data
        """
        request = server_composer_pb2.CreateInitialStateRequest(
            user_id=user_id,
            conversation_id=conversation_id,
            workflow_type=workflow_type,
        )
        return await self._stub.CreateInitialState(request, timeout=timeout)

    async def clear_workflow_cache(
        self,
        user_id: str,
        timeout: float = 30.0,
    ) -> server_composer_pb2.ClearWorkflowCacheResponse:
        """
        Clear cached workflows for a user.

        Args:
            user_id: User ID whose cache should be cleared
            timeout: Request timeout in seconds (default: 30)

        Returns:
            ClearWorkflowCacheResponse with results
        """
        request = server_composer_pb2.ClearWorkflowCacheRequest(user_id=user_id)
        return await self._stub.ClearWorkflowCache(request, timeout=timeout)

    async def close(self):
        """Close the gRPC channel."""
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None


def create_composer_channel(target: str = "localhost:50051") -> Channel:
    """
    Create a gRPC channel to the Composer service.

    Args:
        target: Target address for the Composer service

    Returns:
        gRPC Channel instance
    """
    return grpcio.aio.insecure_channel(target)


# Aliases for backwards compatibility
settings = None  # Placeholder - settings not used in this module

# Global storage instance
_storage: Optional[Storage] = None


def get_storage() -> Storage:
    """Get the global storage instance."""
    global _storage
    if _storage is None:
        raise RuntimeError("Storage not initialized. Call initialize_storage() first.")
    return _storage


async def initialize_storage() -> Storage:
    """Initialize the global storage instance."""
    global _storage
    if _storage is None:
        _storage = Storage()
        await _storage.initialize(DB_CONNECTION_STRING)
    return _storage


async def shutdown_storage() -> None:
    """Shutdown the global storage instance."""
    global _storage
    if _storage is not None:
        await _storage.close()
        _storage = None


# gRPC client interface for Composer service
class ComposerClient:
    """
    gRPC client interface for communicating with the Composer service.

    Uses gRPC for efficient inter-service communication.
    """

    def __init__(self, target: str = "localhost:50051"):
        self.target = target
        self._channel = None
        self._stub = None

    @property
    def channel(self):
        """Get or create gRPC channel."""
        if self._channel is None:
            self._channel = grpcio.aio.insecure_channel(self.target)
        return self._channel

    @property
    def stub(self):
        """Get or create gRPC stub."""
        if self._stub is None:
            self._stub = server_composer_pb2_grpc.ComposerServiceStub(self.channel)
        return self._stub

    async def compose_workflow(
        self,
        user_id: str,
        builder: Any = None,
        workflow_type: str = "ide",
        model_name: Optional[str] = None,
        client_tools: Optional[list] = None,
        tool_choice: Optional[str] = None,
        timeout: float = 30.0,
        **kwargs,
    ):
        """Compose a workflow for the given user via gRPC."""
        import json

        # Serialize builder info and additional kwargs to user_config
        user_config = {"workflow_type": workflow_type}
        if model_name:
            user_config["model_name"] = model_name
        if client_tools:
            user_config["client_tools"] = json.dumps(client_tools)
        if tool_choice:
            user_config["tool_choice"] = tool_choice

        request = server_composer_pb2.ComposeWorkflowRequest(
            user_id=user_id,
            workflow_type=workflow_type,
            model_name=model_name or "",
            timestamp=Timestamp(seconds=int(datetime.now().timestamp())),
            user_config=user_config,
        )
        response = await self.stub.ComposeWorkflow(request, timeout=timeout)
        return {"workflow_id": response.workflow_id}

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_state: dict,
        stream_events: bool = True,
        timeout: float = 60.0,
    ) -> AsyncIterator[Any]:
        """Execute a compiled workflow via gRPC and stream ChatResponse events."""
        state = server_composer_pb2.WorkflowState(
            user_id=initial_state.get("user_id", ""),
            conversation_id=initial_state.get("conversation_id", 0),
            workflow_type=initial_state.get("workflow_type", ""),
            variables=initial_state.get("variables", {}),
        )

        request = server_composer_pb2.ExecuteWorkflowRequest(
            workflow_id=workflow_id,
            initial_state=state,
            stream_events=stream_events,
        )
        # Return the async iterator from the streaming call
        async for response in self.stub.ExecuteWorkflow(request, timeout=timeout):
            yield response

    async def create_initial_state(
        self,
        user_id: str,
        conversation_id: int,
        workflow_type: str = "ide",
        timeout: float = 30.0,
    ):
        """Create initial workflow state via gRPC."""
        request = server_composer_pb2.CreateInitialStateRequest(
            user_id=user_id,
            conversation_id=conversation_id,
            workflow_type=workflow_type,
        )
        response = await self.stub.CreateInitialState(request, timeout=timeout)
        return {
            "user_id": response.user_id,
            "conversation_id": response.conversation_id,
            "workflow_type": response.workflow_type,
            "variables": dict(response.variables),
        }

    async def clear_workflow_cache(self, user_id: str, timeout: float = 30.0):
        """Clear workflow cache for a user via gRPC."""
        request = server_composer_pb2.ClearWorkflowCacheRequest(user_id=user_id)
        response = await self.stub.ClearWorkflowCache(request, timeout=timeout)
        return {"success": response.success, "cleared_count": response.cleared_count}

    async def health_check(self) -> bool:
        """Check if the composer service is healthy."""
        try:
            await self.create_initial_state("health_check_user", 0)
            return True
        except Exception:
            return False

    async def close(self):
        """Close gRPC channel."""
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None


# gRPC client interface for Runner service
class RunnerClient:
    """
    gRPC client interface for communicating with the Runner service.

    Uses gRPC for efficient inter-service communication.
    """

    def __init__(self, target: str = "localhost:50052"):
        self.target = target
        self._channel = None
        self._stub = None

    @property
    def channel(self):
        """Get or create gRPC channel."""
        if self._channel is None:
            self._channel = grpcio.aio.insecure_channel(self.target)
        return self._channel

    @property
    def stub(self):
        """Get or create gRPC stub."""
        if self._stub is None:
            self._stub = composer_runner_pb2_grpc.RunnerServiceStub(self.channel)
        return self._stub

    async def execute_pipeline(
        self,
        pipeline_name: str,
        model_name: str,
        input_data: dict,
        timeout: float = 30.0,
        **kwargs,
    ):
        """Execute a pipeline using the runner service via gRPC."""
        profile = composer_runner_pb2.ModelProfile(
            model_name=model_name,
            provider=kwargs.get("provider", "llama_cpp"),
            task_type=kwargs.get("task_type", "TextToText"),
            model_config={},
        )

        create_request = composer_runner_pb2.CreatePipelineRequest(
            profile=profile,
            priority=kwargs.get("priority", "normal"),
            grammar_type=kwargs.get("grammar_type", "auto"),
            metadata={},
        )

        create_response = await self.stub.CreatePipeline(
            create_request, timeout=timeout
        )
        pipeline_id = create_response.pipeline_id

        execute_request = composer_runner_pb2.ExecutePipelineRequest(
            pipeline_id=pipeline_id,
            input_data=b"",  # TODO: Serialize input_data
            stream_output=True,
        )
        return self.stub.ExecutePipeline(execute_request, timeout=timeout)

    async def get_model_info(self, model_id: str, timeout: float = 30.0):
        """Get information about a specific model via gRPC."""
        # TODO: Implement model info retrieval with gRPC call
        return {"model_id": model_id, "status": "available"}

    async def generate_embeddings(
        self,
        texts: list[str],
        model_name: str,
        dimension: Optional[int] = None,
        timeout: float = 30.0,
    ):
        """Generate embeddings for texts via gRPC."""
        request = composer_runner_pb2.GenerateEmbeddingsRequest(
            texts=texts,
            model_name=model_name,
            dimension=dimension or 0,
        )
        response = await self.stub.GenerateEmbeddings(request, timeout=timeout)
        return {
            "embeddings": [
                {"values": list(e.values), "index": e.index}
                for e in response.embeddings
            ],
            "model_dimension": response.model_dimension,
        }

    async def get_cache_stats(self, pipeline_type: str = "", timeout: float = 30.0):
        """Get pipeline cache statistics via gRPC."""
        request = composer_runner_pb2.GetCacheStatsRequest(pipeline_type=pipeline_type)
        response = await self.stub.GetCacheStats(request, timeout=timeout)
        return {
            "total_pipelines": response.total_pipelines,
            "cached_pipelines": response.cached_pipelines,
            "active_pipelines": response.active_pipelines,
            "total_memory_bytes": response.total_memory_bytes,
            "available_memory_bytes": response.available_memory_bytes,
            "cache_hits": response.cache_hits,
            "cache_misses": response.cache_misses,
            "hit_rate": response.hit_rate,
        }

    async def evict_pipeline(
        self, pipeline_id: str, force: bool = False, timeout: float = 30.0
    ):
        """Evict a pipeline from cache via gRPC."""
        request = composer_runner_pb2.EvictPipelineRequest(
            pipeline_id=pipeline_id,
            force=force,
        )
        response = await self.stub.EvictPipeline(request, timeout=timeout)
        return {
            "success": response.success,
            "freed_memory_bytes": response.freed_memory_bytes,
        }

    async def health_check(self) -> bool:
        """Check if the runner service is healthy."""
        try:
            await self.get_cache_stats()
            return True
        except Exception:
            return False

    async def close(self):
        """Close gRPC channel."""
        if self._channel is not None:
            await self._channel.close()
            self._channel = None
            self._stub = None


# Protocol interfaces for gRPC clients (for type-safe dependency injection)
class ComposerClientProtocol(Protocol):
    """Protocol interface for Composer gRPC client."""

    async def compose_workflow(
        self,
        user_id: str,
        builder: Any = None,
        workflow_type: str = "ide",
        model_name: Optional[str] = None,
        client_tools: Optional[list] = None,
        tool_choice: Optional[str] = None,
        **kwargs,
    ) -> dict[str, str]: ...

    async def execute_workflow(
        self,
        workflow_id: str,
        initial_state: dict,
        stream_events: bool = True,
    ) -> AsyncIterator[Any]: ...

    async def create_initial_state(
        self,
        user_id: str,
        conversation_id: int,
        workflow_type: str = "ide",
    ) -> dict[str, Any]: ...

    async def clear_workflow_cache(self, user_id: str) -> dict[str, Any]: ...

    async def health_check(self) -> bool: ...

    async def close(self) -> None: ...


class RunnerClientProtocol(Protocol):
    """Protocol interface for Runner gRPC client."""

    async def execute_pipeline(
        self,
        pipeline_name: str,
        model_name: str,
        input_data: dict,
        **kwargs,
    ) -> Any: ...

    async def get_model_info(self, model_id: str) -> dict[str, Any]: ...

    async def generate_embeddings(
        self,
        texts: list[str],
        model_name: str,
        dimension: Optional[int] = None,
    ) -> dict[str, Any]: ...

    async def get_cache_stats(self, pipeline_type: str = "") -> dict[str, Any]: ...

    async def evict_pipeline(
        self,
        pipeline_id: str,
        force: bool = False,
    ) -> dict[str, Any]: ...

    async def health_check(self) -> bool: ...

    async def close(self) -> None: ...


# Global gRPC clients
_composer_client: Optional[ComposerClient] = None
_runner_client: Optional[RunnerClient] = None


def get_composer_client() -> ComposerClient:
    """Get the global Composer gRPC client."""
    global _composer_client
    if _composer_client is None:
        _composer_client = ComposerClient()
    return _composer_client


def get_runner_client() -> RunnerClient:
    """Get the global Runner gRPC client."""
    global _runner_client
    if _runner_client is None:
        _runner_client = RunnerClient()
    return _runner_client


# Type aliases for protocol interfaces
ComposerClientType = ComposerClient | ComposerClientProtocol
RunnerClientType = RunnerClient | RunnerClientProtocol


async def shutdown_clients() -> None:
    """Shutdown all gRPC clients."""
    global _composer_client, _runner_client
    if _composer_client is not None:
        await _composer_client.close()
        _composer_client = None
    if _runner_client is not None:
        await _runner_client.close()
        _runner_client = None
