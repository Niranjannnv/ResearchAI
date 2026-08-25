"""
Web Agent  — searches across DuckDuckGo, Bing, SearXNG, Wikipedia,
             Mojeek, Internet Archive, and Google CSE (if configured).
News Agent — searches DuckDuckGo News, Bing News, and SearXNG News in parallel.

All search engines used are free / require no API key by default.
"""
import asyncio
from typing import List

from app.agents.child.base_agent import BaseChildAgent
from app.integrations.multi_search import multi_web_search, multi_news_search


class WebAgent(BaseChildAgent):
    """Aggregates results from 6+ free web search engines in parallel."""
    agent_name = "Web Agent"
    agent_type = "web"

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        # Primary: multi-engine web search across trusted sources
        results = await multi_web_search(query, max_results=max_results)

        # If still thin, add a site-restricted pass for gov/edu
        if len(results) < max_results // 2:
            from app.integrations.multi_search import duckduckgo_search
            gov_results = await duckduckgo_search(
                f"{query} site:gov OR site:edu OR site:who.int",
                max_results=5,
            )
            existing_urls = {r.get("url") for r in results}
            for r in gov_results:
                if r.get("url") not in existing_urls:
                    results.append(r)

        return results[:max_results]


class NewsAgent(BaseChildAgent):
    """Aggregates news results from DuckDuckGo, Bing, and SearXNG in parallel."""
    agent_name = "News Agent"
    agent_type = "news"

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        return await multi_news_search(query, max_results=max_results)
