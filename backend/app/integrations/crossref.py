"""Crossref API integration — DOI metadata and journal articles."""
from typing import Any, Dict, List

from app.integrations.base import BaseAPIClient, create_retry_decorator
from app.core.config import settings


class CrossrefClient(BaseAPIClient):
    BASE_URL = "https://api.crossref.org"

    def _default_headers(self) -> Dict[str, str]:
        headers = super()._default_headers()
        email = settings.OPENALEX_EMAIL or "contact@researchai.com"
        headers["User-Agent"] = f"ResearchAI/1.0 (mailto:{email})"
        if settings.CROSSREF_PLUS_TOKEN:
            headers["Crossref-Plus-API-Token"] = f"Bearer {settings.CROSSREF_PLUS_TOKEN}"
        return headers

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        params = {
            "query": query,
            "rows": min(max_results, 100),
            "select": "DOI,title,author,abstract,published,container-title,publisher,URL,type,is-referenced-by-count",
        }
        try:
            data = await self._get(f"{self.BASE_URL}/works", params=params)
            items = data.get("message", {}).get("items", [])
            return [self._parse_item(item) for item in items]
        except Exception as e:
            self.logger.warning("Crossref search failed", error=str(e))
            return []

    def _parse_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        authors = []
        for a in item.get("author", []):
            name = f"{a.get('family', '')}, {a.get('given', '')}".strip(", ")
            if name:
                authors.append(name)

        # Publication date
        pub = item.get("published") or item.get("published-print") or {}
        date_parts = pub.get("date-parts", [[]])[0]
        pub_date = "-".join(str(p) for p in date_parts) if date_parts else None

        journal = item.get("container-title", [])
        journal_name = journal[0] if journal else None

        title_list = item.get("title", [])
        title = title_list[0] if title_list else "Untitled"

        return {
            "title": title,
            "authors": authors,
            "abstract": item.get("abstract", ""),
            "publisher": item.get("publisher") or journal_name,
            "doi": item.get("DOI"),
            "publication_date": pub_date,
            "url": item.get("URL") or (f"https://doi.org/{item.get('DOI')}" if item.get("DOI") else None),
            "source_type": item.get("type", "journal-article"),
            "citation_count": item.get("is-referenced-by-count", 0),
        }
