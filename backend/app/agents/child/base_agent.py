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
from app.utils.query_cleaner import normalize_query


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

        query = normalize_query(query)
        self.logger.info("Agent starting search", agent=self.agent_name, query=query[:100])

        try:
            raw_results = await asyncio.wait_for(
                self._search_sources(query, max_results),
                timeout=self.timeout,
            )

            source_results = []
            for raw in raw_results:
                if not isinstance(raw, dict) or not raw.get("title"):
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
                    confidence_score=self._calculate_confidence(raw, query=query),
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

    @staticmethod
    def _calculate_relevance(raw: dict, query: Optional[str] = None) -> float:
        """
        Calculates semantic/keyword relevance of a paper to the query.
        Returns a float between 0.0 and 1.0.
        """
        if not query or not query.strip():
            return 0.5

        import re
        query_clean = query.lower().strip()
        title = (raw.get("title") or "").lower()
        abstract = (raw.get("abstract") or raw.get("summary") or "").lower()

        STOP_WORDS = {
            "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "of",
            "with", "by", "from", "as", "is", "are", "was", "were", "what",
            "how", "why", "when", "where", "into", "versus", "vs", "about",
            "make", "paper", "research", "overview", "study", "review",
        }

        tokens = [w for w in re.findall(r"\b[a-z0-9]+\b", query_clean) if len(w) >= 3 and w not in STOP_WORDS]
        if not tokens:
            return 0.5

        # Check full phrase presence
        phrase_in_title = query_clean in title
        phrase_in_abstract = query_clean in abstract

        # Match tokens
        title_matches = sum(1 for t in tokens if t in title)
        abstract_matches = sum(1 for t in tokens if t in abstract)

        total = len(tokens)
        title_ratio = title_matches / total
        abstract_ratio = abstract_matches / total

        # Absolute mismatch filter:
        # If multi-token query (e.g. "artificial intelligence") and 0 tokens appear in title and abstract
        if total >= 2 and title_matches == 0 and abstract_matches == 0:
            return 0.0

        # Incidental mention filter: 0 in title and only 1 token in abstract (e.g. "artificial formula" in breast milk)
        if total >= 2 and title_matches == 0 and abstract_matches <= 1:
            return 0.05

        rel = 0.0
        if phrase_in_title:
            rel += 0.55
        elif title_ratio > 0:
            rel += title_ratio * 0.40

        if phrase_in_abstract:
            rel += 0.25
        elif abstract_ratio > 0:
            rel += abstract_ratio * 0.20

        return min(round(rel, 3), 1.0)

    def _calculate_confidence(self, raw: dict, query: Optional[str] = None) -> float:
        """
        Confidence scoring combining metadata credibility (quality) and topic relevance.
        Higher score = trustworthy + highly relevant result.
        """
        quality = 0.35  # base quality

        # Has DOI → peer-reviewed
        if raw.get("doi"):
            quality += 0.20

        # Has abstract → real content
        if raw.get("abstract") and len(raw.get("abstract", "")) > 100:
            quality += 0.15

        # Has authors
        if raw.get("authors"):
            quality += 0.10

        # Has publisher
        if raw.get("publisher"):
            quality += 0.05

        # Has publication date
        if raw.get("publication_date"):
            quality += 0.05

        # High citation count
        citations = raw.get("citation_count", raw.get("cited_by_count", 0))
        if citations and citations > 100:
            quality += 0.10
        elif citations and citations > 10:
            quality += 0.05

        quality_score = min(quality, 1.0)

        # Relevance scoring
        if query:
            relevance = self._calculate_relevance(raw, query)
            if relevance == 0.0:
                # Completely irrelevant: discard by giving minimal score
                return 0.05
            if relevance < 0.10:
                # Marginally matched incidental term: cap heavily so verifier drops it
                return min(round(quality_score * 0.15, 2), 0.12)

            # Blended score: 65% relevance, 35% metadata quality
            composite = (relevance * 0.65) + (quality_score * 0.35)
            return min(round(composite, 2), 1.0)

        return min(round(quality_score, 2), 1.0)
