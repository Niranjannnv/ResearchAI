"""
CORE API — 220M+ open-access research papers (free, no key required for basic use).
DOAJ     — Directory of Open Access Journals (100% free, no key).

Both are entirely free with generous rate limits.
"""
import urllib.parse
from typing import Any, Dict, List

from app.integrations.base import BaseAPIClient, create_retry_decorator


class COREClient(BaseAPIClient):
    """
    CORE.ac.uk — world's largest open-access research aggregator.
    Free API: 10 req/min without key, 100 req/min with free key.
    Docs: https://core.ac.uk/services/api
    """
    BASE_URL = "https://api.core.ac.uk/v3"

    def _default_headers(self) -> Dict[str, str]:
        headers = super()._default_headers()
        # Optional: set CORE_API_KEY in .env for higher rate limits
        from app.core.config import settings
        key = getattr(settings, "CORE_API_KEY", None)
        if key:
            headers["Authorization"] = f"Bearer {key}"
        return headers

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            data = await self._get(
                f"{self.BASE_URL}/search/works",
                params={
                    "q": query,
                    "limit": min(max_results, 100),
                    "offset": 0,
                    "exclude": "fullText",
                },
            )
            results = []
            for item in data.get("results", [])[:max_results]:
                authors = [
                    a.get("name", "") for a in item.get("authors", []) if a.get("name")
                ]
                results.append({
                    "title": item.get("title", "Untitled"),
                    "authors": authors,
                    "abstract": item.get("abstract", ""),
                    "publisher": item.get("publisher") or item.get("journals", [{}])[0].get("title", ""),
                    "doi": item.get("doi"),
                    "publication_date": str(item.get("publishedDate", item.get("yearPublished", "")))[:10],
                    "url": item.get("downloadUrl") or item.get("sourceFulltextUrls", [None])[0],
                    "source_type": "open_access_paper",
                    "citation_count": item.get("citationCount", 0),
                })
            return results
        except Exception as e:
            self.logger.warning("CORE search failed", error=str(e))
            return []


class DOAJClient(BaseAPIClient):
    """
    Directory of Open Access Journals — 100% free, no API key needed.
    Covers 20,000+ peer-reviewed open-access journals.
    """
    BASE_URL = "https://doaj.org/api/search/articles"

    @create_retry_decorator()
    async def search_articles(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            data = await self._get(
                f"{self.BASE_URL}/{urllib.parse.quote(query)}",
                params={
                    "page": 1,
                    "pageSize": min(max_results, 100),
                },
            )
            results = []
            for item in data.get("results", [])[:max_results]:
                bibjson = item.get("bibjson", {})
                authors = [
                    a.get("name", "") for a in bibjson.get("author", []) if a.get("name")
                ]
                journal = bibjson.get("journal", {})
                links = bibjson.get("link", [])
                url = next((l.get("url") for l in links if l.get("type") == "fulltext"), None)
                results.append({
                    "title": bibjson.get("title", "Untitled"),
                    "authors": authors,
                    "abstract": bibjson.get("abstract", ""),
                    "publisher": journal.get("publisher", ""),
                    "doi": bibjson.get("identifier", [{}])[0].get("id") if bibjson.get("identifier") else None,
                    "publication_date": f"{bibjson.get('year', '')}-{bibjson.get('month', '01'):0>2}-01",
                    "url": url or f"https://doaj.org/article/{item.get('id', '')}",
                    "source_type": "open_access_journal",
                })
            return results
        except Exception as e:
            self.logger.warning("DOAJ search failed", error=str(e))
            return []


class EuropePMCClient(BaseAPIClient):
    """
    Europe PMC — free full-text life sciences literature.
    30M+ articles including PubMed, preprints, and clinical trials.
    Free API, no key required.
    Docs: https://europepmc.org/RestfulWebService
    """
    BASE_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest"

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        try:
            data = await self._get(
                f"{self.BASE_URL}/search",
                params={
                    "query": query,
                    "resultType": "core",
                    "pageSize": min(max_results, 100),
                    "format": "json",
                    "sort": "CITED desc",
                },
            )
            results = []
            for item in data.get("resultList", {}).get("result", [])[:max_results]:
                authors_str = item.get("authorString", "")
                authors = [a.strip() for a in authors_str.split(",")][:10] if authors_str else []
                results.append({
                    "title": item.get("title", "Untitled"),
                    "authors": authors,
                    "abstract": item.get("abstractText", ""),
                    "publisher": item.get("journalTitle", item.get("bookOrReportDetails", {}).get("publisher", "")),
                    "doi": item.get("doi"),
                    "publication_date": str(item.get("pubYear", "")),
                    "url": (
                        f"https://europepmc.org/article/{item.get('source', 'MED')}/{item.get('id', '')}"
                        if item.get("id") else None
                    ),
                    "source_type": "biomedical_paper",
                    "citation_count": item.get("citedByCount", 0),
                })
            return results
        except Exception as e:
            self.logger.warning("Europe PMC search failed", error=str(e))
            return []


class BaseRxivClient(BaseAPIClient):
    """
    bioRxiv + medRxiv preprint server API — free, no key needed.
    Covers life sciences and medical preprints.
    """
    BASE_URL = "https://api.biorxiv.org"

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search via biorxiv/medrxiv detail endpoint (latest preprints)."""
        # biorxiv API uses date-range queries; for text search we use Europe PMC
        # which indexes preprints. Here we fetch recent preprints on a topic.
        try:
            import urllib.parse
            # Use the biorxiv search via query string
            from app.integrations.multi_search import duckduckgo_search
            results = await duckduckgo_search(
                f"{query} site:biorxiv.org OR site:medrxiv.org preprint",
                max_results=max_results,
            )
            for r in results:
                r["source_type"] = "preprint"
            return results
        except Exception as e:
            self.logger.warning("Preprint search failed", error=str(e))
            return []
