"""
Medical Agent — searches 5 free medical/biomedical databases simultaneously:
  1. PubMed NCBI      — gold standard biomedical literature
  2. PubMed (clinical)— clinical trials + systematic reviews
  3. Europe PMC       — 30M+ life sciences papers + preprints
  4. CORE             — open-access biomedical papers
  5. WHO IRIS         — WHO official publications & reports
"""
import asyncio
from typing import List

from app.agents.child.base_agent import BaseChildAgent
from app.integrations.pubmed import PubMedClient
from app.integrations.free_academic import EuropePMCClient, COREClient


class MedicalAgent(BaseChildAgent):
    """Searches PubMed + Europe PMC + CORE + WHO for comprehensive medical coverage."""
    agent_name = "Medical Agent"
    agent_type = "medical"

    def __init__(self):
        super().__init__()
        self.pubmed = PubMedClient()
        self.europe_pmc = EuropePMCClient()
        self.core = COREClient()

    async def _search_sources(self, query: str, max_results: int) -> List[dict]:
        from app.integrations.multi_search import duckduckgo_search

        per_source = max(max_results // 5, 2)

        results = await asyncio.gather(
            # PubMed primary search
            self.pubmed.search(query, max_results=per_source + 2),
            # PubMed clinical / systematic review focused
            self.pubmed.search(
                f"{query} clinical trial OR systematic review OR meta-analysis",
                max_results=per_source,
            ),
            # Europe PMC — indexed preprints + all PMC content
            self.europe_pmc.search(query, max_results=per_source),
            # CORE open-access medical papers
            self.core.search(f"{query} medical health clinical", max_results=per_source),
            # WHO IRIS official publications
            duckduckgo_search(
                f"{query} site:iris.who.int OR site:apps.who.int OR site:who.int/publications",
                max_results=per_source,
            ),
            return_exceptions=True,
        )

        combined = []
        seen: set = set()
        for batch in results:
            if isinstance(batch, list):
                for r in batch:
                    key = r.get("doi") or r.get("url") or r.get("title", "")
                    key = (key or "")[:120]
                    if key and key not in seen:
                        seen.add(key)
                        combined.append(r)

        return combined[:max_results]
