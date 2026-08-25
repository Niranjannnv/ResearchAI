"""
Application configuration using pydantic-settings.
All values are read from environment variables / .env file.
"""
from functools import lru_cache
from typing import Any, List, Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ─── Application ─────────────────────────────────────────────────
    APP_NAME: str = "ResearchAI"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "change-me-in-production"
    ALLOWED_ORIGINS: Any = ["http://localhost:3000"]
    TRUSTED_HOSTS: Any = ["localhost", "127.0.0.1"]

    @field_validator("ALLOWED_ORIGINS", "TRUSTED_HOSTS", mode="before")
    @classmethod
    def parse_list_fields(cls, v):
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [item.strip() for item in v.split(",") if item.strip()]
        return v

    # ─── Database ─────────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+asyncpg://researchai:researchai_secret@localhost:5432/researchai_db"
    SYNC_DATABASE_URL: str = "postgresql://researchai:researchai_secret@localhost:5432/researchai_db"

    # ─── Redis ────────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None

    # ─── JWT ──────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "change-me-jwt-secret"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ─── Google OAuth ─────────────────────────────────────────────────
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:3001"

    # ─── SMTP Email ───────────────────────────────────────────────────
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAILS_FROM_EMAIL: Optional[str] = None
    EMAILS_FROM_NAME: str = "ResearchAI"

    # ─── LLM ──────────────────────────────────────────────────────────
    LLM_PROVIDER: str = "gemini"
    GOOGLE_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    LLM_MODEL: str = "gemini-1.5-pro"
    LLM_TEMPERATURE: float = 0.2
    LLM_MAX_TOKENS: int = 8192

    # ─── Search APIs ──────────────────────────────────────────────────
    BRAVE_SEARCH_API_KEY: Optional[str] = None
    SERPAPI_KEY: Optional[str] = None
    TAVILY_API_KEY: Optional[str] = None

    # ─── Free Academic Extra ───────────────────────────────────────────
    CORE_API_KEY: Optional[str] = None          # core.ac.uk — free key for higher rate limit
    GOOGLE_CSE_KEY: Optional[str] = None        # Google Custom Search (100/day free)
    GOOGLE_CSE_CX: Optional[str] = None         # Google Custom Search engine ID

    # ─── Academic APIs ────────────────────────────────────────────────
    NCBI_API_KEY: Optional[str] = None
    SEMANTIC_SCHOLAR_API_KEY: Optional[str] = None
    OPENALEX_EMAIL: Optional[str] = None
    CROSSREF_PLUS_TOKEN: Optional[str] = None
    GOOGLE_BOOKS_API_KEY: Optional[str] = None

    # ─── Email ────────────────────────────────────────────────────────
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@researchai.com"

    # ─── File Storage ─────────────────────────────────────────────────
    REPORTS_DIR: str = "./reports"
    MAX_REPORT_SIZE_MB: int = 50

    # ─── Rate Limiting ────────────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 60
    LOGIN_RATE_LIMIT_PER_MINUTE: int = 10

    # ─── Agent Configuration ──────────────────────────────────────────
    AGENT_TIMEOUT_SECONDS: int = 30
    MAX_RESULTS_PER_AGENT: int = 10
    MAX_PARALLEL_AGENTS: int = 8

    # ─── Celery ───────────────────────────────────────────────────────
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"

    # ─── Logging ──────────────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
