"""
ResearchAI Backend — Application Entry Point
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.database import create_tables
from app.core.logging import configure_logging
from app.core.redis import get_redis_client

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifecycle manager."""
    configure_logging()
    logger.info("Starting ResearchAI backend", env=settings.APP_ENV)

    # Initialize database tables
    await create_tables()
    logger.info("Database tables ready")

    # Warm up Redis connection
    redis = await get_redis_client()
    await redis.ping()
    logger.info("Redis connection established")

    yield

    # Cleanup
    logger.info("Shutting down ResearchAI backend")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="AI-powered Multi-Agent Research Platform API",
        version="1.0.0",
        docs_url="/api/docs" if settings.APP_DEBUG else None,
        redoc_url="/api/redoc" if settings.APP_DEBUG else None,
        openapi_url="/api/openapi.json" if settings.APP_DEBUG else None,
        lifespan=lifespan,
    )

    # ─── Middleware ───────────────────────────────────────────────────
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    if settings.APP_ENV == "production":
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=settings.TRUSTED_HOSTS,
        )

    # ─── Routers ─────────────────────────────────────────────────────
    app.include_router(api_router, prefix="/api/v1")

    # ─── Health check ─────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "version": "1.0.0", "service": "ResearchAI"}

    # ─── Global exception handler ─────────────────────────────────────
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error("Unhandled exception", exc=str(exc), path=request.url.path)
        return JSONResponse(
            status_code=500,
            content={"detail": "An internal error occurred. Please try again."},
        )

    return app


app = create_app()
