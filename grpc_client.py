"""
gRPC client for composer service communication.

This module provides gRPC client implementations for the Server->Composer
communication path using the ComposerService defined in server_composer.v1.
"""

from typing import Optional, Dict, Any, AsyncIterator
from datetime import datetime

import grpc as grpcio
from grpc.aio import Channel

from server_composer.v1 import (
    server_composer_pb2,
    server_composer_pb2_grpc,
)
from runner.v1 import (
    composer_runner_pb2,
    composer_runner_pb2_grpc,
)


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
            timestamp=timestamp or server_composer_pb2.Timestamp(
                seconds=int(datetime.now().timestamp())
            ),
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