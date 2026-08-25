"""Semantic Scholar API integration."""
from typing import Any, Dict, List, Optional

from app.integrations.base import BaseAPIClient, create_retry_decorator
from app.core.config import settings


class SemanticScholarClient(BaseAPIClient):
    BASE_URL = "https://api.semanticscholar.org/graph/v1"

    def _default_headers(self) -> Dict[str, str]:
        headers = super()._default_headers()
        if settings.SEMANTIC_SCHOLAR_API_KEY:
            headers["x-api-key"] = settings.SEMANTIC_SCHOLAR_API_KEY
        return headers

    FIELDS = "paperId,title,authors,abstract,year,publicationDate,journal,externalIds,openAccessPdf,citationCount,referenceCount,url"

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        params = {
            "query": query,
            "limit": min(max_results, 100),
            "fields": self.FIELDS,
        }
        try:
            data = await self._get(f"{self.BASE_URL}/paper/search", params=params)
            return [self._parse_paper(p) for p in data.get("data", [])]
        except Exception as e:
            self.logger.warning("Semantic Scholar search failed", error=str(e))
            return []

    def _parse_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        authors = [a.get("name", "") for a in paper.get("authors", [])]
        journal = paper.get("journal") or {}
        ext_ids = paper.get("externalIds") or {}
        doi = ext_ids.get("DOI")

        pdf = paper.get("openAccessPdf") or {}
        url = pdf.get("url") or paper.get("url") or f"https://www.semanticscholar.org/paper/{paper.get('paperId')}"

        return {
            "title": paper.get("title", "Untitled"),
            "authors": authors,
            "abstract": paper.get("abstract"),
            "publisher": journal.get("name"),
            "doi": doi,
            "publication_date": paper.get("publicationDate") or str(paper.get("year", "")),
            "url": url,
            "source_type": "academic_paper",
            "citation_count": paper.get("citationCount", 0),
        }
