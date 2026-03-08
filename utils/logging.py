"""
Logging utilities for the server application.
"""

import logging
import os
from typing import Optional


class LLMMLLogger:
    """Custom logger with structured logging support."""

    def __init__(self, name: str = "llmmllab"):
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self._get_log_level())
        self._configure_handler()

    def _get_log_level(self) -> int:
        """Get log level from environment or default."""
        level_map = {
            "TRACE": logging.DEBUG,
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        return level_map.get(os.environ.get("LOG_LEVEL", "INFO").upper(), logging.INFO)

    def _configure_handler(self) -> None:
        """Configure log handler."""
        if not self._logger.handlers:
            handler = logging.StreamHandler()
            handler.setLevel(self._get_log_level())
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)

    def bind(self, **kwargs) -> "LLMMLLogger":
        """Create a new logger instance with bound context."""
        new_logger = LLMMLLogger(self._logger.name)
        new_logger._bound_context = kwargs
        return new_logger

    def _log(self, level: int, message: str, **kwargs) -> None:
        """Internal log method with structured context."""
        context = getattr(self, "_bound_context", {})
        if context:
            message = f"{message} | context={context}"
        self._logger.log(level, message, **kwargs)

    def trace(self, message: str, **kwargs) -> None:
        """Log at trace level."""
        self._log(logging.DEBUG, message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """Log at debug level."""
        self._logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        """Log at info level."""
        self._logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """Log at warning level."""
        self._logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """Log at error level."""
        self._logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """Log at critical level."""
        self._logger.critical(message, **kwargs)


# Global logger instance
llmmllogger = LLMMLLogger()