"""PubMed / NCBI E-utilities integration — biomedical literature."""
import xml.etree.ElementTree as ET
from typing import Any, Dict, List, Optional

from app.integrations.base import BaseAPIClient, create_retry_decorator
from app.core.config import settings


class PubMedClient(BaseAPIClient):
    BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    def _default_params(self) -> Dict[str, str]:
        params = {"tool": "ResearchAI", "email": "contact@researchai.com", "retmode": "json"}
        if settings.NCBI_API_KEY:
            params["api_key"] = settings.NCBI_API_KEY
        return params

    @create_retry_decorator()
    async def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        # Step 1: ESearch to get PMIDs
        search_params = {
            **self._default_params(),
            "db": "pubmed",
            "term": query,
            "retmax": min(max_results, 100),
            "sort": "relevance",
            "usehistory": "y",
        }
        try:
            search_data = await self._get(f"{self.BASE_URL}/esearch.fcgi", params=search_params)
            pmids = search_data.get("esearchresult", {}).get("idlist", [])
            if not pmids:
                return []

            # Step 2: EFetch to get full records
            return await self._fetch_articles(pmids[:max_results])
        except Exception as e:
            self.logger.warning("PubMed search failed", error=str(e))
            return []

    async def _fetch_articles(self, pmids: List[str]) -> List[Dict[str, Any]]:
        fetch_params = {
            **self._default_params(),
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
        }
        try:
            xml_text = await self._get_text(f"{self.BASE_URL}/efetch.fcgi", params=fetch_params)
            return self._parse_pubmed_xml(xml_text)
        except Exception as e:
            self.logger.warning("PubMed fetch failed", error=str(e))
            return []

    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        results = []
        try:
            root = ET.fromstring(xml_text)
            for article in root.findall(".//PubmedArticle"):
                medline = article.find("MedlineCitation")
                if medline is None:
                    continue

                art = medline.find("Article") or {}
                title = ""
                if art is not None:
                    title_el = art.find("ArticleTitle")
                    title = "".join(title_el.itertext()).strip() if title_el is not None else ""

                # Authors
                authors = []
                author_list = art.find("AuthorList") if art is not None else None
                if author_list is not None:
                    for auth in author_list.findall("Author"):
                        ln = auth.findtext("LastName") or ""
                        fn = auth.findtext("ForeName") or ""
                        name = f"{ln}, {fn}".strip(", ")
                        if name:
                            authors.append(name)

                # Abstract
                abstract_text = ""
                abstract_el = art.find("Abstract") if art is not None else None
                if abstract_el is not None:
                    abstract_text = " ".join(
                        "".join(t.itertext()) for t in abstract_el.findall("AbstractText")
                    )

                # Journal
                journal = ""
                if art is not None:
                    journal_el = art.find(".//Journal/Title")
                    journal = journal_el.text if journal_el is not None else ""

                # Publication date
                pub_date_el = art.find(".//Journal/JournalIssue/PubDate") if art is not None else None
                pub_date = ""
                if pub_date_el is not None:
                    year = pub_date_el.findtext("Year") or ""
                    month = pub_date_el.findtext("Month") or ""
                    pub_date = f"{year}-{month}".strip("-")

                # PMID & DOI
                pmid = medline.findtext("PMID") or ""
                doi = ""
                for id_el in article.findall(".//ArticleId"):
                    if id_el.get("IdType") == "doi":
                        doi = id_el.text or ""

                results.append({
                    "title": title,
                    "authors": authors,
                    "abstract": abstract_text.strip(),
                    "publisher": journal,
                    "doi": doi,
                    "publication_date": pub_date,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                    "source_type": "medical_journal",
                    "pmid": pmid,
                })
        except ET.ParseError as e:
            self.logger.warning("PubMed XML parse error", error=str(e))
        return results
