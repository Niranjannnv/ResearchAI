"""Google Books and Open Library integrations."""
from typing import Any, Dict, List, Optional

from app.integrations.base import BaseAPIClient, create_retry_decorator
from app.core.config import settings


class GoogleBooksClient(BaseAPIClient):
    BASE_URL = "https://www.googleapis.com/books/v1"

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {
            "q": query,
            "maxResults": min(max_results, 40),
            "orderBy": "relevance",
            "printType": "books",
            "projection": "full",
        }
        if settings.GOOGLE_BOOKS_API_KEY:
            params["key"] = settings.GOOGLE_BOOKS_API_KEY
        try:
            data = await self._get(f"{self.BASE_URL}/volumes", params=params)
            return [self._parse_volume(v) for v in data.get("items", [])]
        except Exception as e:
            self.logger.warning("Google Books search failed", error=str(e))
            return []

    def _parse_volume(self, volume: Dict[str, Any]) -> Dict[str, Any]:
        info = volume.get("volumeInfo", {})
        access = volume.get("accessInfo", {})
        return {
            "title": info.get("title", "Untitled"),
            "authors": info.get("authors", []),
            "abstract": info.get("description"),
            "publisher": info.get("publisher"),
            "doi": None,
            "publication_date": info.get("publishedDate"),
            "url": info.get("infoLink") or access.get("webReaderLink"),
            "source_type": "book",
            "isbn": next(iter([i["identifier"] for i in info.get("industryIdentifiers", []) if i.get("type") == "ISBN_13"]), None),
            "page_count": info.get("pageCount"),
        }


class OpenLibraryClient(BaseAPIClient):
    BASE_URL = "https://openlibrary.org"

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        params = {
            "q": query,
            "limit": min(max_results, 100),
            "fields": "key,title,author_name,first_publish_year,publisher,isbn,subject,cover_i",
        }
        try:
            data = await self._get(f"{self.BASE_URL}/search.json", params=params)
            return [self._parse_doc(d) for d in data.get("docs", [])]
        except Exception as e:
            self.logger.warning("Open Library search failed", error=str(e))
            return []

    def _parse_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        key = doc.get("key", "")
        isbn_list = doc.get("isbn", [])
        return {
            "title": doc.get("title", "Untitled"),
            "authors": doc.get("author_name", []),
            "abstract": None,
            "publisher": (doc.get("publisher") or [None])[0],
            "doi": None,
            "publication_date": str(doc.get("first_publish_year")) if doc.get("first_publish_year") else None,
            "url": f"https://openlibrary.org{key}",
            "source_type": "book",
            "isbn": isbn_list[0] if isbn_list else None,
        }
