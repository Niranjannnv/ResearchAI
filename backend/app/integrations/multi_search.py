"""
Multi-Search Integration — aggregates results from multiple free search APIs
in parallel so every query hits more sources without needing paid keys.

Free APIs used (all require zero API key):
  1. DuckDuckGo HTML endpoint
  2. Wikipedia REST API
  3. Bing Web Search scraper (HTML)
  4. Google Custom Search JSON API (optional key via GOOGLE_CSE_KEY + GOOGLE_CSE_CX)
  5. SearXNG public instances (public.searx.be)
  6. Mojeek Search API (free tier, no key needed for basic use)
  7. GitHub code/doc search (for technical topics)
"""
import asyncio
import urllib.parse
from typing import Any, Dict, List, Optional

import aiohttp
import structlog
from bs4 import BeautifulSoup

from app.core.config import settings
from app.integrations.base import BaseAPIClient

logger = structlog.get_logger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

JSON_HEADERS = {
    "User-Agent": "ResearchAI/1.0 (research platform)",
    "Accept": "application/json",
}


async def _fetch_html(url: str, params: Optional[Dict] = None, timeout: int = 15) -> str:
    try:
        async with aiohttp.ClientSession(headers=HEADERS) as session:
            async with session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                return await resp.text()
    except Exception as e:
        logger.warning("HTTP fetch failed", url=url, error=str(e))
        return ""


async def _fetch_json(url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None, timeout: int = 15) -> Any:
    try:
        async with aiohttp.ClientSession(headers=headers or JSON_HEADERS) as session:
            async with session.get(
                url, params=params, timeout=aiohttp.ClientTimeout(total=timeout)
            ) as resp:
                resp.raise_for_status()
                return await resp.json()
    except Exception as e:
        logger.warning("JSON fetch failed", url=url, error=str(e))
        return {}


BLOCKED_KEYWORDS = {
    "xnxx", "xvideos", "pornhub", "redtube", "youporn", "xhamster",
    "sex stories", "adult forum", "camgirls", "erotic", "nsfw", "warez",
}


def _is_safe_result(title: str, url: str, snippet: str) -> bool:
    """Filter out adult domains, spam networks, and malicious sites."""
    combined = f"{title} {url} {snippet}".lower()
    for kw in BLOCKED_KEYWORDS:
        if kw in combined:
            return False
    return True


def _build_result(title: str, url: str, snippet: str = "", publisher: str = "", date: str = "", source_type: str = "web") -> Optional[Dict]:
    if not _is_safe_result(title, url, snippet):
        return None

    return {
        "title": title,
        "authors": [],
        "abstract": snippet,
        "publisher": publisher or urllib.parse.urlparse(url).netloc,
        "doi": None,
        "publication_date": date or None,
        "url": url,
        "source_type": source_type,
    }


# ─── 1. DuckDuckGo HTML ───────────────────────────────────────────────────────

async def duckduckgo_search(query: str, max_results: int = 10) -> List[Dict]:
    """Zero-config free DuckDuckGo HTML search."""
    html = await _fetch_html("https://html.duckduckgo.com/html/", params={"q": query})
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    results = []
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
        results.append(_build_result(
            title=title_el.get_text(strip=True),
            url=actual_url,
            snippet=snippet_el.get_text(strip=True) if snippet_el else "",
        ))
        if len(results) >= max_results:
            break
    return results


# ─── 2. Wikipedia REST API ────────────────────────────────────────────────────

async def wikipedia_search(query: str, max_results: int = 5) -> List[Dict]:
    """Free Wikipedia REST search — returns article summaries."""
    data = await _fetch_json(
        "https://en.wikipedia.org/w/api.php",
        params={
            "action": "opensearch",
            "search": query,
            "limit": max_results,
            "namespace": 0,
            "format": "json",
        },
    )
    results = []
    if isinstance(data, list) and len(data) >= 4:
        titles, snippets, urls = data[1], data[2], data[3]
        for i, title in enumerate(titles):
            results.append(_build_result(
                title=title,
                url=urls[i] if i < len(urls) else "",
                snippet=snippets[i] if i < len(snippets) else "",
                publisher="Wikipedia",
                source_type="encyclopedia",
            ))
    return results


async def wikipedia_summary(title: str) -> Dict:
    """Fetch full Wikipedia article summary for richer context."""
    data = await _fetch_json(
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}",
    )
    if data and data.get("title"):
        return _build_result(
            title=data.get("title", ""),
            url=data.get("content_urls", {}).get("desktop", {}).get("page", ""),
            snippet=data.get("extract", ""),
            publisher="Wikipedia",
            source_type="encyclopedia",
        )
    return {}


# ─── 3. SearXNG (public instance, no key needed) ─────────────────────────────

SEARXNG_INSTANCES = [
    "https://search.ononoki.org",
    "https://searx.be",
    "https://opnxng.com",
]


async def searxng_search(query: str, max_results: int = 10) -> List[Dict]:
    """SearXNG public instance meta-search — aggregates Bing, Google, etc."""
    for instance in SEARXNG_INSTANCES:
        data = await _fetch_json(
            f"{instance}/search",
            params={
                "q": query,
                "format": "json",
                "language": "en",
                "categories": "general",
                "safesearch": 1,
            },
            timeout=12,
        )
        if data and data.get("results"):
            results = []
            for r in data["results"][:max_results]:
                results.append(_build_result(
                    title=r.get("title", ""),
                    url=r.get("url", ""),
                    snippet=r.get("content", ""),
                    publisher=r.get("engine", ""),
                    date=r.get("publishedDate", ""),
                ))
            return results
    return []


# ─── 4. Google Custom Search (optional — uses free 100 req/day quota) ─────────

async def google_cse_search(query: str, max_results: int = 10) -> List[Dict]:
    """Google Custom Search JSON API — free 100 queries/day."""
    key = getattr(settings, "GOOGLE_CSE_KEY", None)
    cx = getattr(settings, "GOOGLE_CSE_CX", None)
    if not key or not cx:
        return []
    data = await _fetch_json(
        "https://www.googleapis.com/customsearch/v1",
        params={
            "key": key,
            "cx": cx,
            "q": query,
            "num": min(max_results, 10),
        },
    )
    items = data.get("items", []) if isinstance(data, dict) else []
    return [
        _build_result(
            title=item.get("title", ""),
            url=item.get("link", ""),
            snippet=item.get("snippet", ""),
            publisher=item.get("displayLink", ""),
        )
        for item in items
    ]


# ─── 5. Bing Web Search (HTML scraper, no key) ───────────────────────────────

async def bing_search(query: str, max_results: int = 10) -> List[Dict]:
    """Bing web search via HTML scraping — zero config."""
    html = await _fetch_html(
        "https://www.bing.com/search",
        params={"q": query, "count": max_results, "setlang": "en"},
    )
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for item in soup.select("li.b_algo"):
        title_el = item.select_one("h2 a")
        snippet_el = item.select_one(".b_caption p, .b_algoSlug")
        if not title_el:
            continue
        results.append(_build_result(
            title=title_el.get_text(strip=True),
            url=title_el.get("href", ""),
            snippet=snippet_el.get_text(strip=True) if snippet_el else "",
        ))
        if len(results) >= max_results:
            break
    return results


# ─── 6. Mojeek Search (independent search engine, free) ──────────────────────

async def mojeek_search(query: str, max_results: int = 10) -> List[Dict]:
    """Mojeek.com — independent search engine with its own index, no key needed."""
    html = await _fetch_html(
        "https://www.mojeek.com/search",
        params={"q": query, "fmt": "text"},
    )
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    results = []
    for item in soup.select("ul.results li"):
        title_el = item.select_one("a.title")
        snippet_el = item.select_one("p.s")
        if not title_el:
            continue
        results.append(_build_result(
            title=title_el.get_text(strip=True),
            url=title_el.get("href", ""),
            snippet=snippet_el.get_text(strip=True) if snippet_el else "",
        ))
        if len(results) >= max_results:
            break
    return results


# ─── 7. Internet Archive / Wayback CDX ───────────────────────────────────────

async def internet_archive_search(query: str, max_results: int = 5) -> List[Dict]:
    """Internet Archive full-text search for free archived pages/texts."""
    data = await _fetch_json(
        "https://archive.org/advancedsearch.php",
        params={
            "q": query,
            "fl[]": ["identifier", "title", "creator", "description", "date", "subject"],
            "rows": max_results,
            "page": 1,
            "output": "json",
        },
    )
    docs = data.get("response", {}).get("docs", []) if isinstance(data, dict) else []
    return [
        _build_result(
            title=doc.get("title", "Untitled") if isinstance(doc.get("title"), str) else (doc.get("title") or [""])[0],
            url=f"https://archive.org/details/{doc.get('identifier', '')}",
            snippet=doc.get("description", "") if isinstance(doc.get("description"), str) else "",
            publisher="Internet Archive",
            date=doc.get("date", ""),
            source_type="archive",
        )
        for doc in docs
        if doc.get("identifier")
    ]


# ─── Aggregated Multi-Search ─────────────────────────────────────────────────

async def multi_web_search(query: str, max_results: int = 15) -> List[Dict]:
    """
    Run all free search engines in parallel and merge unique results.
    Automatically deduplicates by URL.
    """
    per_source = max(max_results // 4, 3)

    tasks = await asyncio.gather(
        duckduckgo_search(query, max_results=per_source),
        wikipedia_search(query, max_results=3),
        searxng_search(query, max_results=per_source),
        bing_search(query, max_results=per_source),
        mojeek_search(query, max_results=per_source),
        internet_archive_search(query, max_results=3),
        google_cse_search(query, max_results=per_source),
        return_exceptions=True,
    )

    seen_urls: set = set()
    merged: List[Dict] = []
    for batch in tasks:
        if isinstance(batch, list):
            for item in batch:
                if not item or not isinstance(item, dict):
                    continue
                url = item.get("url", "")
                if url and url not in seen_urls and item.get("title"):
                    seen_urls.add(url)
                    merged.append(item)

    return merged[:max_results]


async def multi_news_search(query: str, max_results: int = 15) -> List[Dict]:
    """
    Run news-specific searches from multiple sources in parallel.
    """
    news_query = f"{query} news"
    per_source = max(max_results // 3, 3)

    tasks = await asyncio.gather(
        duckduckgo_search(news_query, max_results=per_source),
        searxng_search(f"{query} news latest", max_results=per_source),
        bing_search(f"{query} news 2024 2025", max_results=per_source),
        return_exceptions=True,
    )

    seen_urls: set = set()
    merged: List[Dict] = []
    for batch in tasks:
        if isinstance(batch, list):
            for item in batch:
                if not item or not isinstance(item, dict):
                    continue
                url = item.get("url", "")
                if url and url not in seen_urls and item.get("title"):
                    seen_urls.add(url)
                    item["source_type"] = "news"
                    merged.append(item)

    return merged[:max_results]
