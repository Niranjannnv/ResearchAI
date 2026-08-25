"""
Redis client factory and utilities for caching and rate limiting.
Provides automatic in-memory fallback for local development when Redis is not running.
"""
import fnmatch
import time
from typing import Any, Dict, List, Optional, Tuple, Union

import redis.asyncio as aioredis
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class InMemoryPipeline:
    def __init__(self, backend: "InMemoryRedis"):
        self.backend = backend
        self.commands: List[Tuple[str, tuple, dict]] = []

    def incr(self, key: str) -> "InMemoryPipeline":
        self.commands.append(("incr", (key,), {}))
        return self

    def expire(self, key: str, seconds: int) -> "InMemoryPipeline":
        self.commands.append(("expire", (key, seconds), {}))
        return self

    async def execute(self) -> List[Any]:
        results = []
        for cmd, args, kwargs in self.commands:
            fn = getattr(self.backend, cmd)
            res = await fn(*args, **kwargs)
            results.append(res)
        self.commands.clear()
        return results


class InMemoryRedis:
    """In-memory Redis mock for local development."""

    def __init__(self):
        self._store: Dict[str, str] = {}
        self._expires: Dict[str, float] = {}

    def _cleanup_key(self, key: str) -> bool:
        if key in self._expires and time.time() > self._expires[key]:
            self._store.pop(key, None)
            self._expires.pop(key, None)
            return True
        return False

    async def ping(self) -> bool:
        return True

    async def get(self, key: str) -> Optional[str]:
        if self._cleanup_key(key):
            return None
        return self._store.get(key)

    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        self._store[key] = str(value)
        if ex:
            self._expires[key] = time.time() + ex
        else:
            self._expires.pop(key, None)
        return True

    async def setex(self, key: str, time_seconds: int, value: str) -> bool:
        return await self.set(key, value, ex=time_seconds)

    async def delete(self, *keys: str) -> int:
        count = 0
        for k in keys:
            if k in self._store:
                self._store.pop(k, None)
                self._expires.pop(k, None)
                count += 1
        return count

    async def incr(self, key: str) -> int:
        self._cleanup_key(key)
        val = int(self._store.get(key, 0)) + 1
        self._store[key] = str(val)
        return val

    async def expire(self, key: str, seconds: int) -> bool:
        if key in self._store:
            self._expires[key] = time.time() + seconds
            return True
        return False

    async def keys(self, pattern: str = "*") -> List[str]:
        # Expire old keys first
        for k in list(self._expires.keys()):
            self._cleanup_key(k)
        return [k for k in self._store.keys() if fnmatch.fnmatch(k, pattern)]

    def pipeline(self) -> InMemoryPipeline:
        return InMemoryPipeline(self)


_redis_client: Optional[Union[aioredis.Redis, InMemoryRedis]] = None


async def get_redis_client() -> Union[aioredis.Redis, InMemoryRedis]:
    """Return a singleton async Redis client or in-memory fallback."""
    global _redis_client
    if _redis_client is None:
        try:
            client = aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
                retry_on_timeout=False,
                max_connections=50,
            )
            await client.ping()
            _redis_client = client
            logger.info("Connected to Redis instance", url=settings.REDIS_URL)
        except Exception as exc:
            logger.warning(
                "Could not connect to Redis server; falling back to in-memory store",
                error=str(exc),
            )
            _redis_client = InMemoryRedis()
    return _redis_client


async def cache_set(key: str, value: str, ttl_seconds: int = 3600) -> None:
    redis = await get_redis_client()
    await redis.setex(key, ttl_seconds, value)


async def cache_get(key: str) -> Optional[str]:
    redis = await get_redis_client()
    return await redis.get(key)


async def cache_delete(key: str) -> None:
    redis = await get_redis_client()
    await redis.delete(key)


async def rate_limit_check(
    key: str,
    max_requests: int,
    window_seconds: int = 60,
) -> tuple[bool, int]:
    """
    Check rate limit using sliding window counter.
    Returns (allowed: bool, remaining: int).
    """
    redis = await get_redis_client()
    pipe = redis.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds)
    results = await pipe.execute()
    count = results[0]
    remaining = max(0, max_requests - count)
    return count <= max_requests, remaining


async def invalidate_user_cache(user_id: str) -> None:
    """Invalidate all cache keys for a specific user."""
    redis = await get_redis_client()
    pattern = f"user:{user_id}:*"
    keys = await redis.keys(pattern)
    if keys:
        await redis.delete(*keys)
