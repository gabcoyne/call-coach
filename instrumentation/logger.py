"""
Structured JSON logging for request tracing and debugging.

Logs correlation IDs for request tracing and includes coaching session metadata
(call_id, rep_id, dimension, tokens_used) for comprehensive observability.
"""
import json
import logging
import uuid
from typing import Any, Optional, Dict
from datetime import datetime
from contextvars import ContextVar

# Context variables for request tracing
_correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")
_call_id: ContextVar[str] = ContextVar("call_id", default="")
_rep_id: ContextVar[str] = ContextVar("rep_id", default="")
_user_id: ContextVar[str] = ContextVar("user_id", default="")


class CorrelationIdFilter(logging.Filter):
    """Add correlation IDs to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add context variables to log record."""
        record.correlation_id = _correlation_id.get()
        record.call_id = _call_id.get()
        record.rep_id = _rep_id.get()
        record.user_id = _user_id.get()
        return True


class JSONFormatter(logging.Formatter):
    """Format logs as JSON for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add correlation IDs if present
        if correlation_id := getattr(record, "correlation_id", None):
            log_data["correlation_id"] = correlation_id
        if call_id := getattr(record, "call_id", None):
            log_data["call_id"] = call_id
        if rep_id := getattr(record, "rep_id", None):
            log_data["rep_id"] = rep_id
        if user_id := getattr(record, "user_id", None):
            log_data["user_id"] = user_id

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            log_data.update(record.extra)

        return json.dumps(log_data)


class StructuredLogger:
    """Structured logger with correlation ID support."""

    def __init__(self, name: str):
        """Initialize structured logger."""
        self._logger = logging.getLogger(name)

    def set_correlation_id(self, correlation_id: Optional[str] = None) -> str:
        """Set or generate correlation ID for request tracing."""
        if correlation_id is None:
            correlation_id = str(uuid.uuid4())
        _correlation_id.set(correlation_id)
        return correlation_id

    def set_call_context(
        self,
        call_id: Optional[str] = None,
        rep_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ) -> None:
        """Set context for a coaching analysis session."""
        if call_id:
            _call_id.set(call_id)
        if rep_id:
            _rep_id.set(rep_id)
        if user_id:
            _user_id.set(user_id)

    def clear_context(self) -> None:
        """Clear context variables."""
        _correlation_id.set("")
        _call_id.set("")
        _rep_id.set("")
        _user_id.set("")

    def _log(
        self,
        level: int,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Internal logging method with extra data."""
        if extra:
            # Create a custom LogRecord to include extra data
            record = self._logger.makeRecord(
                self._logger.name,
                level,
                "(unknown file)",
                0,
                message,
                (),
                exc_info if exc_info is not None else None,
            )
            record.extra = extra
            self._logger.handle(record)
        else:
            if exc_info:
                self._logger.log(level, message, exc_info=True)
            else:
                self._logger.log(level, message)

    def debug(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log debug message."""
        self._log(logging.DEBUG, message, extra)

    def info(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log info message."""
        self._log(logging.INFO, message, extra)

    def warning(self, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """Log warning message."""
        self._log(logging.WARNING, message, extra)

    def error(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log error message."""
        self._log(logging.ERROR, message, extra, exc_info=exc_info)

    def critical(
        self,
        message: str,
        extra: Optional[Dict[str, Any]] = None,
        exc_info: bool = False,
    ) -> None:
        """Log critical message."""
        self._log(logging.CRITICAL, message, extra, exc_info=exc_info)

    def log_api_request(
        self,
        method: str,
        endpoint: str,
        duration: float,
        status: int,
        response_size: Optional[int] = None,
    ) -> None:
        """Log API request with timing."""
        extra = {
            "event": "api_request",
            "method": method,
            "endpoint": endpoint,
            "duration_ms": round(duration * 1000, 2),
            "status": status,
        }
        if response_size:
            extra["response_size_bytes"] = response_size
        self.info(f"{method} {endpoint} {status}", extra=extra)

    def log_call_analysis(
        self,
        call_id: str,
        rep_id: str,
        duration: float,
        dimensions: list[str],
        tokens_used: int,
    ) -> None:
        """Log call analysis with coaching data."""
        self.set_call_context(call_id=call_id, rep_id=rep_id)
        extra = {
            "event": "call_analysis",
            "call_id": call_id,
            "rep_id": rep_id,
            "dimensions": dimensions,
            "duration_ms": round(duration * 1000, 2),
            "tokens_used": tokens_used,
        }
        self.info("Call analysis completed", extra=extra)

    def log_coaching_session(
        self,
        session_id: str,
        call_id: str,
        rep_id: str,
        dimension: str,
        score: float,
        tokens_used: int,
    ) -> None:
        """Log coaching session creation."""
        self.set_call_context(call_id=call_id, rep_id=rep_id)
        extra = {
            "event": "coaching_session",
            "session_id": session_id,
            "call_id": call_id,
            "rep_id": rep_id,
            "dimension": dimension,
            "score": score,
            "tokens_used": tokens_used,
        }
        self.info("Coaching session created", extra=extra)

    def log_database_query(
        self,
        operation: str,
        table: str,
        duration: float,
        rows_affected: Optional[int] = None,
    ) -> None:
        """Log database query with timing."""
        extra = {
            "event": "db_query",
            "operation": operation,
            "table": table,
            "duration_ms": round(duration * 1000, 2),
        }
        if rows_affected is not None:
            extra["rows_affected"] = rows_affected
        self.debug(f"Query {operation} on {table}", extra=extra)

    def log_cache_operation(
        self,
        operation: str,
        cache_type: str,
        key: str,
        hit: bool,
        duration: Optional[float] = None,
    ) -> None:
        """Log cache operation."""
        extra = {
            "event": "cache_operation",
            "operation": operation,
            "cache_type": cache_type,
            "key": key,
            "hit": hit,
        }
        if duration:
            extra["duration_ms"] = round(duration * 1000, 2)
        self.debug(f"Cache {operation} ({cache_type}): {key} {'hit' if hit else 'miss'}", extra=extra)

    def log_external_api_call(
        self,
        service: str,
        endpoint: str,
        method: str,
        status: int,
        duration: float,
        tokens_used: Optional[int] = None,
    ) -> None:
        """Log external API call (Gong, Claude, etc.)."""
        extra = {
            "event": "external_api_call",
            "service": service,
            "endpoint": endpoint,
            "method": method,
            "status": status,
            "duration_ms": round(duration * 1000, 2),
        }
        if tokens_used:
            extra["tokens_used"] = tokens_used
        self.info(f"{service} API: {method} {endpoint} {status}", extra=extra)


# Global logger instances
_loggers: Dict[str, StructuredLogger] = {}


def get_logger(name: str) -> StructuredLogger:
    """Get or create a structured logger."""
    if name not in _loggers:
        _loggers[name] = StructuredLogger(name)
    return _loggers[name]


def setup_structured_logging(
    log_level: str = "INFO",
    json_format: bool = True,
) -> None:
    """
    Set up structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format if True, standard format otherwise
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    handler = logging.StreamHandler()
    handler.setLevel(getattr(logging, log_level.upper(), logging.INFO))

    # Add correlation ID filter
    handler.addFilter(CorrelationIdFilter())

    # Set formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(correlation_id)s] - %(message)s"
        )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    logging.info("Structured logging initialized (json_format=%s)", json_format)


def get_correlation_id() -> str:
    """Get current correlation ID."""
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set correlation ID for current request."""
    _correlation_id.set(correlation_id)
