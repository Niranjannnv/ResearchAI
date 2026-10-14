"""
Async SQLAlchemy database engine and session management.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# ─── Engine ───────────────────────────────────────────────────────────────────
db_url = settings.DATABASE_URL
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

connect_args = {}
if "neon.tech" in db_url or "sslmode=" in db_url or "ssl=" in db_url:
    connect_args["ssl"] = True
    if "?" in db_url:
        db_url = db_url.split("?")[0]

engine_kwargs = {"echo": settings.APP_DEBUG}
if not db_url.startswith("sqlite"):
    engine_kwargs.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
    })
    if connect_args:
        engine_kwargs["connect_args"] = connect_args

engine = create_async_engine(
    db_url,
    **engine_kwargs,
)

# ─── Session factory ──────────────────────────────────────────────────────────
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


# ─── Base class for all ORM models ────────────────────────────────────────────
class Base(DeclarativeBase):
    pass


# ─── Database initialization ──────────────────────────────────────────────────
async def create_tables() -> None:
    """Create all tables if they don't exist (used in non-migration dev setups)."""
    import app.models  # noqa: F401
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ─── Dependency injection ─────────────────────────────────────────────────────
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
