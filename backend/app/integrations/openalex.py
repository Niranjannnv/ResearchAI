"""
OpenAlex API integration — free, open scholarly works database.
https://docs.openalex.org/
"""
from typing import Any, Dict, List, Optional

from app.integrations.base import BaseAPIClient, create_retry_decorator
from app.core.config import settings


class OpenAlexClient(BaseAPIClient):
    BASE_URL = "https://api.openalex.org"

    def _default_headers(self) -> Dict[str, str]:
        headers = super()._default_headers()
        if settings.OPENALEX_EMAIL:
            # Polite pool — faster rate limits
            headers["User-Agent"] = f"ResearchAI/1.0 (mailto:{settings.OPENALEX_EMAIL})"
        return headers

    @create_retry_decorator()
    async def search_works(
        self,
        query: str,
        max_results: int = 10,
        filters: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search scholarly works on OpenAlex."""
        params = {
            "search": query,
            "per-page": min(max_results, 50),
            "select": "id,title,authorships,abstract_inverted_index,primary_location,publication_date,doi,open_access,cited_by_count,concepts,type",
        }
        if filters:
            params["filter"] = filters

        try:
            data = await self._get(f"{self.BASE_URL}/works", params=params)
            return [self._parse_work(w) for w in data.get("results", [])]
        except Exception as e:
            self.logger.warning("OpenAlex search failed", error=str(e), query=query)
            return []

    def _parse_work(self, work: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize an OpenAlex work object."""
        authorships = work.get("authorships", [])
        authors = [
            a.get("author", {}).get("display_name", "Unknown")
            for a in authorships
        ]

        # Reconstruct abstract from inverted index
        abstract = self._reconstruct_abstract(
            work.get("abstract_inverted_index") or {}
        )

        primary = work.get("primary_location") or {}
        source = primary.get("source") or {}

        return {
            "title": work.get("title", "Untitled"),
            "authors": authors,
            "abstract": abstract,
            "publisher": source.get("display_name"),
            "doi": work.get("doi"),
            "publication_date": work.get("publication_date"),
            "url": primary.get("landing_page_url") or work.get("id"),
            "source_type": "academic_journal",
            "cited_by_count": work.get("cited_by_count", 0),
            "open_access": (work.get("open_access") or {}).get("is_oa", False),
        }

    def _reconstruct_abstract(self, inverted_index: Dict[str, List[int]]) -> Optional[str]:
        """OpenAlex stores abstracts as inverted index — reconstruct the original text."""
        if not inverted_index:
            return None
        words = {}
        for word, positions in inverted_index.items():
            for pos in positions:
                words[pos] = word
        if not words:
            return None
        return " ".join(words[i] for i in sorted(words.keys()))
