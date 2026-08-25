"""arXiv API integration — preprints in physics, math, CS, and more."""
import xml.etree.ElementTree as ET
from typing import Any, Dict, List

from app.integrations.base import BaseAPIClient, create_retry_decorator


class ArXivClient(BaseAPIClient):
    BASE_URL = "http://export.arxiv.org/api"
    NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": min(max_results, 50),
            "sortBy": "relevance",
            "sortOrder": "descending",
        }
        try:
            text = await self._get_text(f"{self.BASE_URL}/query", params=params)
            return self._parse_feed(text)
        except Exception as e:
            self.logger.warning("arXiv search failed", error=str(e))
            return []

    def _parse_feed(self, xml_text: str) -> List[Dict[str, Any]]:
        root = ET.fromstring(xml_text)
        results = []
        for entry in root.findall("atom:entry", self.NS):
            title = entry.findtext("atom:title", namespaces=self.NS) or "Untitled"
            abstract = entry.findtext("atom:summary", namespaces=self.NS) or ""
            published = entry.findtext("atom:published", namespaces=self.NS) or ""

            authors = [
                a.findtext("atom:name", namespaces=self.NS) or "Unknown"
                for a in entry.findall("atom:author", self.NS)
            ]

            link = ""
            doi = None
            for lnk in entry.findall("atom:link", self.NS):
                rel = lnk.get("rel", "")
                if rel == "alternate":
                    link = lnk.get("href", "")
                if lnk.get("title") == "doi":
                    doi = lnk.get("href", "").replace("http://dx.doi.org/", "")

            arxiv_id = (entry.findtext("atom:id", namespaces=self.NS) or "").split("/abs/")[-1]

            results.append({
                "title": title.strip(),
                "authors": authors,
                "abstract": abstract.strip(),
                "publisher": "arXiv",
                "doi": doi,
                "publication_date": published[:10] if published else None,
                "url": link or f"https://arxiv.org/abs/{arxiv_id}",
                "source_type": "preprint",
                "arxiv_id": arxiv_id,
            })
        return results
