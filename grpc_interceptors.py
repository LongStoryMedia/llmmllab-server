"""
gRPC interceptors for server-side and client-side cross-cutting concerns.

This module provides:
- Authentication interceptor: Adds JWT tokens to outgoing requests and validates them on incoming requests
- Logging interceptor: Logs all gRPC calls with timing and metadata
- Metrics interceptor: Collects metrics for monitoring and observability
- Compression interceptor: Compresses large messages for efficient transmission
"""

import asyncio
import time
import logging
from typing import Any, Callable, Optional
from dataclasses import dataclass

import grpc
from grpc import StatusCode

# grpc.aio.ClientCallDetails.metadata is typed as _Metadata which is an internal type
# It accepts either None or a Mapping[str, str] or Sequence[Tuple[str, str]]
# We use type: ignore for metadata type issues as they are internal to grpc
from grpc.aio import ClientCallDetails

from middleware.auth import TokenValidationResult, get_auth_middleware
import config

logger = logging.getLogger(__name__)

# Constants
AUTHORIZATION_HEADER = "authorization"
BEARER_PREFIX = "Bearer "
BEARER_PREFIX_LENGTH = len(BEARER_PREFIX)


# =============================================================================
# Authentication Interceptor
# =============================================================================


@dataclass
class AuthContext:
    """Authentication context extracted from a request."""

    token: Optional[str] = None
    valid: bool = False
    claims: Optional[dict] = None
    user_id: Optional[str] = None
    error: Optional[str] = None


class AuthenticationUnaryUnaryServerInterceptor:
    """Server interceptor that validates authentication tokens on unary-unary calls."""

    def __init__(self, jwks_uri: Optional[str] = None):
        self.jwks_uri = jwks_uri or getattr(
            config, "AUTH_JWKS_URI", "https://auth.example.com/.well-known/jwks.json"
        )
        self._auth_middleware = None

    @property
    def auth_middleware(self):
        """Get or create the auth middleware singleton."""
        if self._auth_middleware is None:
            self._auth_middleware = get_auth_middleware(self.jwks_uri)
        return self._auth_middleware

    async def intercept_unary_unary(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        request: Any,
        context: grpc.ServicerContext,
    ) -> Any:
        """Intercept a unary-unary call and validate authentication."""
        token = await self._extract_token(context)

        auth_context = await self._validate_token(token)

        if not auth_context.valid:
            context.set_code(StatusCode.UNAUTHENTICATED)
            context.set_details(auth_context.error or "Invalid authentication token")
            return None

        # Add auth context to context for handlers to access (using a private attribute)
        setattr(context, "auth_context", auth_context)

        # Continue with the call
        return await continuation(request, context)

    async def _extract_token(self, context: grpc.ServicerContext) -> Optional[str]:
        """Extract token from invocation metadata."""
        metadata = dict(context.invocation_metadata() or [])
        token_val = metadata.get(AUTHORIZATION_HEADER, "")
        if isinstance(token_val, bytes):
            return token_val.decode("utf-8")
        return token_val

    async def _validate_token(self, token: Optional[str]) -> AuthContext:
        """Validate JWT token and return auth context."""
        if token is None or not token:
            return AuthContext(error="Missing authentication token")

        # Remove Bearer prefix if present
        if token.startswith(BEARER_PREFIX):
            token = token[BEARER_PREFIX_LENGTH:]

        try:
            # Use the existing JWTValidator from middleware.auth
            result: TokenValidationResult = (
                await self.auth_middleware.validator.validate_token(token)
            )

            return AuthContext(
                token=token,
                valid=True,
                claims=result.claims,
                user_id=result.user_id,
            )

        except grpc.RpcError:
            # Re-raise gRPC errors (including those converted from HTTPException)
            raise
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return AuthContext(error=f"Authentication failed: {str(e)}")


class AuthenticationUnaryStreamServerInterceptor:
    """Server interceptor that validates authentication tokens on unary-stream calls."""

    def __init__(self, jwks_uri: Optional[str] = None):
        self.jwks_uri = jwks_uri or getattr(
            config, "AUTH_JWKS_URI", "https://auth.example.com/.well-known/jwks.json"
        )
        self._auth_middleware = None

    @property
    def auth_middleware(self):
        """Get or create the auth middleware singleton."""
        if self._auth_middleware is None:
            self._auth_middleware = get_auth_middleware(self.jwks_uri)
        return self._auth_middleware

    async def intercept_unary_stream(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        request: Any,
        context: grpc.ServicerContext,
    ) -> Any:
        """Intercept a unary-stream call and validate authentication."""
        token = await self._extract_token(context)

        auth_context = await self._validate_token(token)

        if not auth_context.valid:
            context.set_code(StatusCode.UNAUTHENTICATED)
            context.set_details(auth_context.error or "Invalid authentication token")
            return

        setattr(context, "auth_context", auth_context)
        return await continuation(request, context)

    async def _extract_token(self, context: grpc.ServicerContext) -> Optional[str]:
        """Extract token from invocation metadata."""
        metadata = dict(context.invocation_metadata() or [])
        token_val = metadata.get(AUTHORIZATION_HEADER, "")
        if isinstance(token_val, bytes):
            return token_val.decode("utf-8")
        return token_val

    async def _validate_token(self, token: Optional[str]) -> AuthContext:
        """Validate JWT token and return auth context."""
        if token is None or not token:
            return AuthContext(error="Missing authentication token")

        # Remove Bearer prefix if present
        if token.startswith(BEARER_PREFIX):
            token = token[BEARER_PREFIX_LENGTH:]

        try:
            # Use the existing JWTValidator from middleware.auth
            result: TokenValidationResult = (
                await self.auth_middleware.validator.validate_token(token)
            )

            return AuthContext(
                token=token,
                valid=True,
                claims=result.claims,
                user_id=result.user_id,
            )

        except grpc.RpcError:
            raise
        except Exception as e:
            logger.warning(f"Token validation failed: {e}")
            return AuthContext(error=f"Authentication failed: {str(e)}")


# =============================================================================
# Logging Interceptor
# =============================================================================


class LoggingUnaryUnaryServerInterceptor:
    """Server interceptor that logs unary-unary calls."""

    async def intercept_unary_unary(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        request: Any,
        context: grpc.ServicerContext,
    ) -> Any:
        """Log a unary-unary call."""
        method = handler_call_details.method
        start_time = time.time()

        logger.debug(f"Starting gRPC call: {method}")

        try:
            response = await continuation(request, context)
            elapsed = time.time() - start_time

            logger.debug(f"Completed gRPC call: {method} in {elapsed:.3f}s")
            return response

        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed gRPC call: {method} in {elapsed:.3f}s: {e}")
            raise


class LoggingUnaryStreamServerInterceptor:
    """Server interceptor that logs unary-stream calls."""

    async def intercept_unary_stream(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        request: Any,
        context: grpc.ServicerContext,
    ) -> Any:
        """Log a unary-stream call."""
        method = handler_call_details.method
        start_time = time.time()

        logger.debug(f"Starting streaming gRPC call: {method}")

        try:
            return await continuation(request, context)
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(f"Failed streaming gRPC call: {method} in {elapsed:.3f}s: {e}")
            raise


# =============================================================================
# Metrics Interceptor
# =============================================================================


class MetricsUnaryUnaryServerInterceptor:
    """Server interceptor that collects metrics for unary-unary calls."""

    def __init__(self):
        self._metrics = {
            "requests_total": 0,
            "requests_success": 0,
            "requests_failed": 0,
            "request_duration_seconds": 0.0,
        }
        self._lock = asyncio.Lock()

    async def intercept_unary_unary(
        self,
        continuation: Callable,
        handler_call_details: grpc.HandlerCallDetails,
        request: Any,
        context: grpc.ServicerContext,
    ) -> Any:
        """Collect metrics for a unary-unary call."""
        method = handler_call_details.method
        start_time = time.time()

        try:
            response = await continuation(request, context)
            elapsed = time.time() - start_time

            async with self._lock:
                self._metrics["requests_total"] += 1
                self._metrics["requests_success"] += 1
                self._metrics["request_duration_seconds"] += elapsed

            return response

        except Exception as e:
            elapsed = time.time() - start_time

            async with self._lock:
                self._metrics["requests_total"] += 1
                self._metrics["requests_failed"] += 1
                self._metrics["request_duration_seconds"] += elapsed

            raise

    def get_metrics(self) -> dict:
        """Get current metrics."""
        return self._metrics.copy()


# =============================================================================
# Compression Interceptor
# =============================================================================


class CompressionClientInterceptor:
    """Client interceptor that enables compression for large messages."""

    def __init__(self, compression_algorithm: grpc.Compression = grpc.Compression.Gzip):
        """
        Initialize the compression client interceptor.

        Args:
            compression_algorithm: The compression algorithm to use (default: Gzip)
        """
        self._compression = compression_algorithm

    def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-unary call and enable compression."""
        # Store compression algorithm for use at call time
        # In gRPC, compression is set per-call using the compression keyword argument
        # This interceptor enables compression by returning a wrapper that applies it
        return _CompressedUnaryUnaryCall(
            continuation, client_call_details, request, self._compression
        )

    def intercept_unary_stream(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-stream call and enable compression."""
        return _CompressedUnaryStreamCall(
            continuation, client_call_details, request, self._compression
        )


class CompressionStreamClientInterceptor:
    """Client interceptor that enables compression for streaming requests."""

    def __init__(self, compression_algorithm: grpc.Compression = grpc.Compression.Gzip):
        self._compression = compression_algorithm

    def intercept_stream_unary(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request_iterator: Any,
    ) -> Any:
        """Intercept a stream-unary call and enable compression."""
        return _CompressedStreamUnaryCall(
            continuation, client_call_details, request_iterator, self._compression
        )

    def intercept_stream_stream(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request_iterator: Any,
    ) -> Any:
        """Intercept a stream-stream call and enable compression."""
        return _CompressedStreamStreamCall(
            continuation, client_call_details, request_iterator, self._compression
        )


# =============================================================================
# Compressed Call Wrappers
# =============================================================================


class _CompressedUnaryUnaryCall:
    """Wrapper for unary-unary calls with compression enabled."""

    def __init__(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
        compression: grpc.Compression,
    ):
        self._continuation = continuation
        self._client_call_details = client_call_details
        self._request = request
        self._compression = compression

    def __call__(self) -> Any:
        """Execute the call with compression enabled."""
        # Create new ClientCallDetails with compression header
        metadata = list(self._client_call_details.metadata or [])
        metadata.append((grpc._common._COMPRESSION_CALL_KEY, self._compression))  # type: ignore
        new_details = ClientCallDetails(
            method=self._client_call_details.method,
            timeout=self._client_call_details.timeout,
            metadata=metadata,
            credentials=self._client_call_details.credentials,
            wait_for_ready=self._client_call_details.wait_for_ready,
        )
        return self._continuation(new_details, self._request)


class _CompressedUnaryStreamCall:
    """Wrapper for unary-stream calls with compression enabled."""

    def __init__(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
        compression: grpc.Compression,
    ):
        self._continuation = continuation
        self._client_call_details = client_call_details
        self._request = request
        self._compression = compression

    def __call__(self) -> Any:
        """Execute the call with compression enabled."""
        metadata = list(self._client_call_details.metadata or [])
        metadata.append((grpc._common._COMPRESSION_CALL_KEY, self._compression))  # type: ignore
        new_details = ClientCallDetails(
            method=self._client_call_details.method,
            timeout=self._client_call_details.timeout,
            metadata=metadata,
            credentials=self._client_call_details.credentials,
            wait_for_ready=self._client_call_details.wait_for_ready,
        )
        return self._continuation(new_details, self._request)


class _CompressedStreamUnaryCall:
    """Wrapper for stream-unary calls with compression enabled."""

    def __init__(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request_iterator: Any,
        compression: grpc.Compression,
    ):
        self._continuation = continuation
        self._client_call_details = client_call_details
        self._request_iterator = request_iterator
        self._compression = compression

    def __call__(self) -> Any:
        """Execute the call with compression enabled."""
        metadata = list(self._client_call_details.metadata or [])
        metadata.append((grpc._common._COMPRESSION_CALL_KEY, self._compression))  # type: ignore
        new_details = ClientCallDetails(
            method=self._client_call_details.method,
            timeout=self._client_call_details.timeout,
            metadata=metadata,
            credentials=self._client_call_details.credentials,
            wait_for_ready=self._client_call_details.wait_for_ready,
        )
        return self._continuation(new_details, self._request_iterator)


class _CompressedStreamStreamCall:
    """Wrapper for stream-stream calls with compression enabled."""

    def __init__(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request_iterator: Any,
        compression: grpc.Compression,
    ):
        self._continuation = continuation
        self._client_call_details = client_call_details
        self._request_iterator = request_iterator
        self._compression = compression

    def __call__(self) -> Any:
        """Execute the call with compression enabled."""
        metadata = list(self._client_call_details.metadata or [])
        metadata.append((grpc._common._COMPRESSION_CALL_KEY, self._compression))  # type: ignore
        new_details = ClientCallDetails(
            method=self._client_call_details.method,
            timeout=self._client_call_details.timeout,
            metadata=metadata,
            credentials=self._client_call_details.credentials,
            wait_for_ready=self._client_call_details.wait_for_ready,
        )
        return self._continuation(new_details, self._request_iterator)


# =============================================================================
# Utility Functions
# =============================================================================


def create_auth_token_provider(
    token: Optional[str] = None,
) -> Callable[[], Optional[str]]:
    """
    Create a token provider function for authentication client interceptor.

    Args:
        token: The authentication token to return, or None for unauthenticated

    Returns:
        A callable that returns the auth token
    """

    def provider() -> Optional[str]:
        return token

    return provider


def get_server_interceptors() -> list:
    """
    Get the list of server interceptors to apply.

    Returns:
        List of interceptor instances
    """
    return [
        AuthenticationUnaryUnaryServerInterceptor(),
        AuthenticationUnaryStreamServerInterceptor(),
        LoggingUnaryUnaryServerInterceptor(),
        LoggingUnaryStreamServerInterceptor(),
        MetricsUnaryUnaryServerInterceptor(),
    ]


def get_client_interceptors(token: Optional[str] = None) -> list:
    """
    Get the list of client interceptors to apply.

    Args:
        token: Optional authentication token to include in requests

    Returns:
        List of interceptor instances
    """
    interceptors = []

    # Add authentication interceptor if token provided
    if token:
        interceptors.append(
            AuthenticationClientInterceptor(create_auth_token_provider(token))
        )

    # Add compression interceptor
    interceptors.append(CompressionClientInterceptor())

    return interceptors


def inject_auth_context_to_metadata(
    auth_context: AuthContext, context: grpc.ServicerContext
) -> None:
    """
    Inject authentication context into servicer context metadata.

    Args:
        auth_context: The authentication context to inject
        context: The servicer context to update
    """
    if auth_context and auth_context.valid and auth_context.user_id:
        # Note: This is a simplified approach; actual implementation may need
        # to use context.invocation_metadata() and context.send_initial_metadata()
        pass


# =============================================================================
# Client Authentication Interceptor
# =============================================================================


class AuthenticationClientInterceptor:
    """Client interceptor that adds authentication token to outgoing requests."""

    def __init__(self, token_provider: Callable[[], Optional[str]]):
        """
        Initialize the authentication client interceptor.

        Args:
            token_provider: Callable that returns the auth token, or None if not authenticated
        """
        self._token_provider = token_provider

    def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> Any:
        """Intercept a unary-unary call and add authentication token."""
        token = self._token_provider()

        if token:
            # Add token to metadata (gRPC metadata requires bytes values)
            metadata = list(client_call_details.metadata or [])
            metadata.append(
                (AUTHORIZATION_HEADER, f"{BEARER_PREFIX}{token}".encode("utf-8"))
            )

            # Create new ClientCallDetails with updated metadata
            new_details = ClientCallDetails(
                method=client_call_details.method,
                timeout=client_call_details.timeout,
                metadata=metadata,
                credentials=client_call_details.credentials,
                wait_for_ready=client_call_details.wait_for_ready,
            )
        else:
            new_details = client_call_details

        return continuation(new_details, request)


class AuthenticationStreamClientInterceptor:
    """Client interceptor that adds authentication token to streaming requests."""

    def __init__(self, token_provider: Callable[[], Optional[str]]):
        self._token_provider = token_provider

    def intercept_stream_unary(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request_iterator: Any,
    ) -> Any:
        """Intercept a stream-unary call and add authentication token."""
        token = self._token_provider()

        if token:
            metadata = list(client_call_details.metadata or [])
            metadata.append(
                (AUTHORIZATION_HEADER, f"{BEARER_PREFIX}{token}".encode("utf-8"))
            )

            new_details = ClientCallDetails(
                method=client_call_details.method,
                timeout=client_call_details.timeout,
                metadata=metadata,
                credentials=client_call_details.credentials,
                wait_for_ready=client_call_details.wait_for_ready,
            )
        else:
            new_details = client_call_details

        return continuation(new_details, request_iterator)
