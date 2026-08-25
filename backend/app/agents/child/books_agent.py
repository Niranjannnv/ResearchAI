"""
Books Agent     — Google Books + Open Library + Internet Archive texts
Patent Agent    — Google Patents + Justia + Espacenet (via multi-search)
Government Agent— .gov / WHO / UN / Europa via DuckDuckGo + Bing + SearXNG
Statistics Agent— World Bank + UN Data + Our World In Data + Statista (multi-search)
"""
import asyncio
from typing import List

from app.agents.child.base_agent import BaseChildAgent
from app.integrations.google_books import GoogleBooksClient, OpenLibraryClient


# ─── Books Agent ─────────────────────────────────────────────────────────────

class BooksAgent(BaseChildAgent):
    """Google Books + Open Library + Internet Archive books & texts."""
    agent_name = "Books Agent"
    agent_type = "book"

    def __init__(self):
        super().__init__()
        self.google_books = GoogleBooksClient()
        self.open_library = OpenLibraryClient()

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        from app.integrations.multi_search import internet_archive_search

        per_source = max(max_results // 3, 3)

        results = await asyncio.gather(
            self.google_books.search(query, max_results=per_source),
            self.open_library.search(query, max_results=per_source),
            # Internet Archive has millions of free books & academic texts
            internet_archive_search(f"{query} book", max_results=per_source),
            return_exceptions=True,
        )
        combined = []
        seen_urls: set = set()
        for batch in results:
            if isinstance(batch, list):
                for r in batch:
                    url = r.get("url", "")
                    if url not in seen_urls and r.get("title"):
                        seen_urls.add(url)
                        combined.append(r)
        return combined[:max_results]


# ─── Patent Agent ─────────────────────────────────────────────────────────────

class PatentAgent(BaseChildAgent):
    """Patent Agent — searches Google Patents, Justia, Espacenet, and FreePatentsOnline."""
    agent_name = "Patent Agent"
    agent_type = "patent"

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        from app.integrations.multi_search import (
            duckduckgo_search, bing_search, searxng_search
        )

        per_source = max(max_results // 3, 3)

        # Multiple patent-specific queries across different engines
        results = await asyncio.gather(
            duckduckgo_search(
                f"{query} patent site:patents.google.com OR site:patents.justia.com",
                max_results=per_source,
            ),
            bing_search(
                f"{query} patent site:patents.google.com OR site:freepatentsonline.com",
                max_results=per_source,
            ),
            searxng_search(
                f"{query} patent invention",
                max_results=per_source,
            ),
            duckduckgo_search(
                f"{query} site:worldwide.espacenet.com",
                max_results=per_source,
            ),
            return_exceptions=True,
        )

        combined = []
        seen_urls: set = set()
        for batch in results:
            if isinstance(batch, list):
                for r in batch:
                    url = r.get("url", "")
                    if url not in seen_urls and r.get("title"):
                        seen_urls.add(url)
                        r["source_type"] = "patent"
                        combined.append(r)
        return combined[:max_results]


# ─── Government Agent ─────────────────────────────────────────────────────────

class GovernmentAgent(BaseChildAgent):
    """Government Agent — searches .gov, WHO, UN, Europa via multiple engines."""
    agent_name = "Government Agent"
    agent_type = "government"

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        from app.integrations.multi_search import (
            duckduckgo_search, bing_search, searxng_search
        )

        per_source = max(max_results // 3, 3)

        results = await asyncio.gather(
            # DuckDuckGo restricted to gov/international org domains
            duckduckgo_search(
                f"{query} site:gov OR site:who.int OR site:un.org OR site:europa.eu",
                max_results=per_source,
            ),
            # Bing gov search
            bing_search(
                f"{query} site:gov OR site:cdc.gov OR site:nih.gov OR site:worldbank.org",
                max_results=per_source,
            ),
            # SearXNG general + government filter
            searxng_search(
                f"{query} government report official",
                max_results=per_source,
            ),
            # Direct CDC/NIH/WHO document search
            duckduckgo_search(
                f"{query} site:cdc.gov OR site:nih.gov OR site:paho.org OR site:ecdc.europa.eu",
                max_results=per_source,
            ),
            return_exceptions=True,
        )

        combined = []
        seen_urls: set = set()
        for batch in results:
            if isinstance(batch, list):
                for r in batch:
                    url = r.get("url", "")
                    if url not in seen_urls and r.get("title"):
                        seen_urls.add(url)
                        r["source_type"] = "government_publication"
                        combined.append(r)
        return combined[:max_results]


# ─── Statistics Agent ─────────────────────────────────────────────────────────

class StatisticsAgent(BaseChildAgent):
    """Statistics Agent — World Bank + UN + Our World In Data + Kaggle datasets."""
    agent_name = "Statistics Agent"
    agent_type = "statistics"

    def __init__(self):
        super().__init__()
        from app.integrations.world_bank import WorldBankClient
        self.world_bank = WorldBankClient()

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        from app.integrations.multi_search import (
            duckduckgo_search, bing_search, searxng_search
        )

        per_source = max(max_results // 4, 3)

        results = await asyncio.gather(
            # World Bank API (structured data)
            self.world_bank.search_indicators(query, max_results=per_source),
            # Our World In Data, UN Data, Statista
            duckduckgo_search(
                f"{query} statistics data site:ourworldindata.org OR site:data.un.org OR site:statista.com",
                max_results=per_source,
            ),
            # Bing for data.gov and open data portals
            bing_search(
                f"{query} dataset statistics site:data.gov OR site:data.worldbank.org OR site:kaggle.com",
                max_results=per_source,
            ),
            # SearXNG for any report/chart/dataset
            searxng_search(
                f"{query} statistics dataset report figures",
                max_results=per_source,
            ),
            # CDC WONDER / WHO GHO databases
            duckduckgo_search(
                f"{query} data site:who.int OR site:gho.who.int OR site:apps.who.int",
                max_results=per_source,
            ),
            return_exceptions=True,
        )

        combined = []
        seen_urls: set = set()
        for batch in results:
            if isinstance(batch, list):
                for r in batch:
                    url = r.get("url", "")
                    if url not in seen_urls and r.get("title"):
                        seen_urls.add(url)
                        r.setdefault("source_type", "statistics")
                        combined.append(r)
        return combined[:max_results]
