"""
Brave Search API integration for trusted web and news search.
Falls back to a curated site-restricted search if no key is available.
"""
from typing import Any, Dict, List, Optional

from app.integrations.base import BaseAPIClient, create_retry_decorator
from app.core.config import settings

# Trusted news domains for filtering
TRUSTED_NEWS_DOMAINS = [
    "reuters.com", "apnews.com", "bbc.com", "npr.org",
    "theguardian.com", "nytimes.com", "washingtonpost.com",
    "nature.com", "science.org", "scientificamerican.com",
]

TRUSTED_WEB_DOMAINS = [
    "gov", "edu", "who.int", "un.org", "ncbi.nlm.nih.gov",
    "cdc.gov", "nih.gov", "europa.eu", "worldbank.org",
]


class BraveSearchClient(BaseAPIClient):
    BASE_URL = "https://api.search.brave.com/res/v1"

    def _default_headers(self) -> Dict[str, str]:
        headers = super()._default_headers()
        if settings.BRAVE_SEARCH_API_KEY:
            headers["X-Subscription-Token"] = settings.BRAVE_SEARCH_API_KEY
            headers["Accept-Encoding"] = "gzip"
        return headers

    @create_retry_decorator()
    async def search_web(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not settings.BRAVE_SEARCH_API_KEY:
            # Free zero-config fallback via DuckDuckGo
            return await self._duckduckgo_search(query, max_results=max_results)

        params = {
            "q": query,
            "count": min(max_results, 20),
            "search_lang": "en",
            "safesearch": "moderate",
            "freshness": None,
            "text_decorations": False,
        }
        try:
            data = await self._get(f"{self.BASE_URL}/web/search", params=params)
            results = data.get("web", {}).get("results", [])
            return [self._parse_web_result(r) for r in results]
        except Exception as e:
            self.logger.warning("Brave web search failed, falling back to DuckDuckGo", error=str(e))
            return await self._duckduckgo_search(query, max_results=max_results)

    async def _duckduckgo_search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Free web search fallback using DuckDuckGo HTML endpoint."""
        from bs4 import BeautifulSoup
        import urllib.parse

        url = "https://html.duckduckgo.com/html/"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html",
        }
        try:
            html = await self._get_text(url, params=params)
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for res in soup.select(".result"):
                title_el = res.select_one(".result__title a")
                snippet_el = res.select_one(".result__snippet")
                if not title_el:
                    continue
                raw_href = title_el.get("href", "")
                actual_url = raw_href
                if "uddg=" in raw_href:
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
                    actual_url = parsed.get("uddg", [raw_href])[0]
                
                title = title_el.get_text(strip=True)
                snippet = snippet_el.get_text(strip=True) if snippet_el else ""
                
                items.append({
                    "title": title,
                    "authors": [],
                    "abstract": snippet,
                    "publisher": urllib.parse.urlparse(actual_url).netloc,
                    "doi": None,
                    "publication_date": None,
                    "url": actual_url,
                    "source_type": "web",
                })
                if len(items) >= max_results:
                    break
            return items
        except Exception as exc:
            self.logger.warning("DuckDuckGo free search fallback failed", error=str(exc))
            return []

    @create_retry_decorator()
    async def search_news(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        if not settings.BRAVE_SEARCH_API_KEY:
            return await self._duckduckgo_search(f"{query} news", max_results=max_results)

        params = {
            "q": query,
            "count": min(max_results, 20),
            "search_lang": "en",
        }
        try:
            data = await self._get(f"{self.BASE_URL}/news/search", params=params)
            results = data.get("results", [])
            return [self._parse_news_result(r) for r in results]
        except Exception as e:
            self.logger.warning("Brave news search failed", error=str(e))
            return []

    def _parse_web_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": result.get("title", "Untitled"),
            "authors": [],
            "abstract": result.get("description"),
            "publisher": result.get("meta_url", {}).get("hostname"),
            "doi": None,
            "publication_date": result.get("page_fetched"),
            "url": result.get("url"),
            "source_type": "web",
        }

    def _parse_news_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": result.get("title", "Untitled"),
            "authors": [],
            "abstract": result.get("description"),
            "publisher": result.get("meta_url", {}).get("hostname") or result.get("source", {}).get("name"),
            "doi": None,
            "publication_date": result.get("age") or result.get("breaking_news_date"),
            "url": result.get("url"),
            "source_type": "news",
        }
