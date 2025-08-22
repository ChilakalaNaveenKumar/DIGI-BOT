"""
Logging Configuration

Structured logging setup for the Digi Setu AI application.
"""

import logging
import sys
from typing import Any, Dict

import structlog
from structlog.stdlib import LoggerFactory

from app.core.simple_config import get_settings

settings = get_settings()


def setup_logging() -> None:
    """Configure structured logging for the application."""
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.LOG_FORMAT == "json" 
            else structlog.dev.ConsoleRenderer(colors=True)
        ],
        context_class=dict,
        logger_factory=LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.LOG_LEVEL.upper()),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if settings.DATABASE_ECHO else logging.WARNING
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


class LoggingMiddleware:
    """Middleware for request/response logging."""
    
    def __init__(self, app):
        self.app = app
        self.logger = get_logger(__name__)
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        request_info = {
            "method": scope["method"],
            "path": scope["path"],
            "query_string": scope["query_string"].decode(),
            "client": scope.get("client"),
        }
        
        self.logger.info("Request started", **request_info)
        
        # Wrap send to capture response info
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                self.logger.info(
                    "Request completed",
                    status_code=message["status"],
                    **request_info
                )
            await send(message)
        
        await self.app(scope, receive, send_wrapper)


def log_ai_interaction(
    provider: str,
    model: str,
    tokens_used: int,
    duration: float,
    success: bool,
    error: str = None
) -> None:
    """Log AI provider interactions."""
    logger = get_logger("ai_interaction")
    
    log_data = {
        "provider": provider,
        "model": model,
        "tokens_used": tokens_used,
        "duration_seconds": duration,
        "success": success
    }
    
    if error:
        log_data["error"] = error
        logger.error("AI interaction failed", **log_data)
    else:
        logger.info("AI interaction completed", **log_data)


def log_database_operation(
    operation: str,
    table: str,
    duration: float,
    success: bool,
    error: str = None
) -> None:
    """Log database operations."""
    logger = get_logger("database")
    
    log_data = {
        "operation": operation,
        "table": table,
        "duration_seconds": duration,
        "success": success
    }
    
    if error:
        log_data["error"] = error
        logger.error("Database operation failed", **log_data)
    else:
        logger.debug("Database operation completed", **log_data)


def log_user_action(
    user_id: int,
    action: str,
    resource: str,
    resource_id: str = None,
    metadata: Dict[str, Any] = None
) -> None:
    """Log user actions for audit trail."""
    logger = get_logger("user_action")
    
    log_data = {
        "user_id": user_id,
        "action": action,
        "resource": resource
    }
    
    if resource_id:
        log_data["resource_id"] = resource_id
    
    if metadata:
        log_data["metadata"] = metadata
    
    logger.info("User action", **log_data)
