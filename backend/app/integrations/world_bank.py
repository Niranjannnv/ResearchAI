"""World Bank Open Data API integration."""
from typing import Any, Dict, List

from app.integrations.base import BaseAPIClient, create_retry_decorator


class WorldBankClient(BaseAPIClient):
    BASE_URL = "https://api.worldbank.org/v2"

    @create_retry_decorator()
    async def search_indicators(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search World Bank indicator definitions."""
        params = {
            "format": "json",
            "per_page": min(max_results, 100),
            "mrv": 5,  # Most recent values
        }
        # Search through common indicators
        search_url = f"{self.BASE_URL}/indicator"
        params["searchTerm"] = query
        try:
            data = await self._get(search_url, params=params)
            if isinstance(data, list) and len(data) > 1:
                indicators = data[1] or []
                return [self._parse_indicator(i) for i in indicators if i]
        except Exception as e:
            self.logger.warning("World Bank search failed", error=str(e))
        return []

    @create_retry_decorator()
    async def get_indicator_data(
        self, indicator_id: str, country: str = "all", max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Get specific indicator data across countries."""
        url = f"{self.BASE_URL}/country/{country}/indicator/{indicator_id}"
        params = {
            "format": "json",
            "per_page": min(max_results, 100),
            "mrv": 10,
        }
        try:
            data = await self._get(url, params=params)
            if isinstance(data, list) and len(data) > 1:
                return [self._parse_data_point(d) for d in (data[1] or []) if d and d.get("value") is not None]
        except Exception as e:
            self.logger.warning("World Bank data fetch failed", error=str(e))
        return []

    def _parse_indicator(self, indicator: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": indicator.get("name", "Untitled"),
            "authors": ["World Bank"],
            "abstract": indicator.get("sourceNote"),
            "publisher": "World Bank",
            "doi": None,
            "publication_date": None,
            "url": f"https://data.worldbank.org/indicator/{indicator.get('id')}",
            "source_type": "statistics",
            "indicator_id": indicator.get("id"),
        }

    def _parse_data_point(self, point: Dict[str, Any]) -> Dict[str, Any]:
        indicator = point.get("indicator") or {}
        country = point.get("country") or {}
        return {
            "title": f"{indicator.get('value', '')} — {country.get('value', '')} ({point.get('date', '')})",
            "authors": ["World Bank"],
            "abstract": f"Value: {point.get('value')} for {country.get('value')} in {point.get('date')}",
            "publisher": "World Bank",
            "doi": None,
            "publication_date": str(point.get("date")),
            "url": f"https://data.worldbank.org/indicator/{indicator.get('id')}?locations={point.get('countryiso3code')}",
            "source_type": "statistics",
        }
