"""
Base HTTP client for all API integrations.
Provides retry logic, timeout handling, and error standardization.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

import aiohttp
import structlog
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import settings

logger = structlog.get_logger(__name__)

RETRY_EXCEPTIONS = (
    aiohttp.ClientConnectionError,
    aiohttp.ServerTimeoutError,
    asyncio.TimeoutError,
)


def create_retry_decorator(max_attempts: int = 3):
    return retry(
        retry=retry_if_exception_type(RETRY_EXCEPTIONS),
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )


class BaseAPIClient(ABC):
    """Abstract base for all external API integrations."""

    BASE_URL: str = ""
    TIMEOUT: int = 30

    def __init__(self):
        self._session: Optional[aiohttp.ClientSession] = None
        self.logger = structlog.get_logger(self.__class__.__name__)

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                headers=self._default_headers(),
            )
        return self._session

    def _default_headers(self) -> Dict[str, str]:
        return {
            "User-Agent": "ResearchAI/1.0 (research platform; contact@researchai.com)",
            "Accept": "application/json",
        }

    async def _get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        session = await self._get_session()
        async with session.get(url, params=params, headers=headers) as response:
            response.raise_for_status()
            return await response.json()

    async def _get_text(self, url: str, params: Optional[Dict] = None) -> str:
        session = await self._get_session()
        async with session.get(url, params=params) as response:
            response.raise_for_status()
            return await response.text()

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
