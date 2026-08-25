"""
Unit tests for Child Agents and formatting utilities.
"""
import pytest
from app.agents.child.base_agent import BaseChildAgent
from app.agents.mother_agent import _format_apa, _format_mla, _format_chicago
from app.schemas.research import SourceResult

class DummyTestAgent(BaseChildAgent):
    agent_name = "Dummy Test Agent"
    agent_type = "test"

    async def _search_sources(self, query: str, max_results: int):
        return [
            {
                "title": "Quantum Computing Frontiers",
                "authors": ["Alice Smith", "Bob Jones"],
                "abstract": "A comprehensive study on quantum entanglement in silicon architectures with long coherence times.",
                "publisher": "Physical Review",
                "doi": "10.1103/PhysRev.99.12345",
                "publication_date": "2024-05-12",
                "url": "https://doi.org/10.1103/PhysRev.99.12345",
                "citation_count": 42
            }
        ]

@pytest.mark.asyncio
async def test_base_child_agent_execution_and_confidence():
    agent = DummyTestAgent()
    results = await agent.search("quantum", max_results=5)
    assert len(results) == 1
    source = results[0]
    assert source.title == "Quantum Computing Frontiers"
    assert source.authors == ["Alice Smith", "Bob Jones"]
    assert source.confidence_score > 0.7  # DOI + abstract + authors + publisher + citations boost

def test_citation_generators():
    source = SourceResult(
        title="Deep Learning in Genomics",
        authors=["John Doe", "Jane Roe"],
        publisher="Nature Genetics",
        doi="10.1038/s41588-024-001",
        publication_date="2024-01-15",
        url="https://doi.org/10.1038/s41588-024-001",
        agent_type="academic"
    )

    apa = _format_apa(source)
    assert "John Doe, & Jane Roe (2024). Deep Learning in Genomics." in apa
    assert "https://doi.org/10.1038/s41588-024-001" in apa

    mla = _format_mla(source)
    assert "John Doe, et al." in mla
    assert '"Deep Learning in Genomics."' in mla

    chicago = _format_chicago(source)
    assert 'John Doe. "Deep Learning in Genomics."' in chicago
    assert "(2024)" in chicago
