"""
Structured logging configuration using structlog.
"""
import logging
import sys

import structlog

from app.core.config import settings


def configure_logging() -> None:
    """Configure structlog for JSON or human-readable output."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.LOG_FORMAT == "json":
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also configure standard library logging to use structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=log_level,
    )

    # Suppress noisy loggers
    for logger_name in ["uvicorn.access", "sqlalchemy.engine", "httpx"]:
        logging.getLogger(logger_name).setLevel(logging.WARNING)


def get_logger(name: str = __name__):
    return structlog.get_logger(name)
