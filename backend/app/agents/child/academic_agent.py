"""
Academic Agent — searches 8 free academic databases simultaneously:
  1. OpenAlex        — 250M+ scholarly works
  2. Crossref        — 150M+ DOI records
  3. Semantic Scholar— 200M+ papers with citation graph
  4. arXiv           — preprints (physics, CS, math, biology)
  5. CORE            — 220M+ open-access full-text papers
  6. DOAJ            — 20,000+ open-access journals
  7. Europe PMC      — 30M+ life sciences papers
  8. bioRxiv/medRxiv — latest preprints
"""
import asyncio
from typing import List

from app.agents.child.base_agent import BaseChildAgent
from app.integrations.openalex import OpenAlexClient
from app.integrations.crossref import CrossrefClient
from app.integrations.semantic_scholar import SemanticScholarClient
from app.integrations.arxiv import ArXivClient
from app.integrations.free_academic import COREClient, DOAJClient, EuropePMCClient, BaseRxivClient


class AcademicAgent(BaseChildAgent):
    """Searches 8 free academic databases in parallel for comprehensive coverage."""
    agent_name = "Academic Agent"
    agent_type = "academic"

    def __init__(self):
        super().__init__()
        self.openalex = OpenAlexClient()
        self.crossref = CrossrefClient()
        self.semantic_scholar = SemanticScholarClient()
        self.arxiv = ArXivClient()
        self.core = COREClient()
        self.doaj = DOAJClient()
        self.europe_pmc = EuropePMCClient()
        self.rxiv = BaseRxivClient()

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        per_source = max(max_results // 8, 2)

        results = await asyncio.gather(
            self.openalex.search_works(query, max_results=per_source),
            self.crossref.search(query, max_results=per_source),
            self.semantic_scholar.search(query, max_results=per_source),
            self.arxiv.search(query, max_results=per_source),
            self.core.search(query, max_results=per_source),
            self.doaj.search_articles(query, max_results=per_source),
            self.europe_pmc.search(query, max_results=per_source),
            self.rxiv.search(query, max_results=per_source),
            return_exceptions=True,
        )

        combined = []
        seen: set = set()
        for batch in results:
            if isinstance(batch, list):
                for r in batch:
                    key = (r.get("doi") or r.get("url") or r.get("title", ""))[:120]
                    if key and key not in seen:
                        seen.add(key)
                        combined.append(r)

        return combined[:max_results]
