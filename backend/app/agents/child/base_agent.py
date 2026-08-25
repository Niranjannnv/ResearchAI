"""
Base Child Agent — all specialized agents inherit from this.
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import List, Optional

import structlog

from app.core.config import settings
from app.schemas.research import SourceResult


class BaseChildAgent(ABC):
    """
    Abstract base for all specialized child agents.
    Each agent searches one or more data sources and returns SourceResult objects.
    """

    agent_name: str = "base"
    agent_type: str = "base"

    def __init__(self):
        self.logger = structlog.get_logger(self.__class__.__name__)
        self.timeout = settings.AGENT_TIMEOUT_SECONDS
        self.max_results = settings.MAX_RESULTS_PER_AGENT

    @abstractmethod
    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        """Subclasses implement their specific API calls here."""
        ...

    async def search(self, query: str, max_results: Optional[int] = None) -> List[SourceResult]:
        """
        Public method called by the Task Manager.
        Runs search with timeout, logs execution, and normalizes results.
        """
        max_results = max_results or self.max_results
        start_time = time.monotonic()

        self.logger.info("Agent starting search", agent=self.agent_name, query=query[:100])

        try:
            raw_results = await asyncio.wait_for(
                self._search_sources(query, max_results),
                timeout=self.timeout,
            )

            source_results = []
            for raw in raw_results:
                if not raw.get("title"):
                    continue
                source = SourceResult(
                    title=raw.get("title", "Untitled")[:500],
                    authors=raw.get("authors", []),
                    abstract=raw.get("abstract"),
                    summary=None,  # Will be filled by Summarizer
                    publisher=raw.get("publisher"),
                    doi=raw.get("doi"),
                    publication_date=raw.get("publication_date"),
                    url=raw.get("url"),
                    source_type=raw.get("source_type", self.agent_type),
                    agent_type=self.agent_type,
                    confidence_score=self._calculate_confidence(raw),
                )
                source_results.append(source)

            duration = (time.monotonic() - start_time) * 1000
            self.logger.info(
                "Agent search completed",
                agent=self.agent_name,
                results=len(source_results),
                duration_ms=round(duration, 2),
            )
            return source_results

        except asyncio.TimeoutError:
            self.logger.warning("Agent timed out", agent=self.agent_name, timeout=self.timeout)
            return []
        except Exception as e:
            self.logger.error("Agent search error", agent=self.agent_name, error=str(e))
            return []

    def _calculate_confidence(self, raw: dict) -> float:
        """
        Heuristic confidence scoring based on available metadata.
        Higher score = more trustworthy/complete result.
        """
        score = 0.5  # base

        # Has DOI → peer-reviewed
        if raw.get("doi"):
            score += 0.15

        # Has abstract → real content
        if raw.get("abstract") and len(raw.get("abstract", "")) > 100:
            score += 0.10

        # Has authors
        if raw.get("authors"):
            score += 0.10

        # Has publisher
        if raw.get("publisher"):
            score += 0.05

        # Has publication date
        if raw.get("publication_date"):
            score += 0.05

        # High citation count
        citations = raw.get("citation_count", raw.get("cited_by_count", 0))
        if citations and citations > 100:
            score += 0.10
        elif citations and citations > 10:
            score += 0.05

        return min(round(score, 2), 1.0)
