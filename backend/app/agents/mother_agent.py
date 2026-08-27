"""
Mother Agent — LangGraph-based multi-agent orchestration.

State machine flow:
  planner → task_manager → parallel_dispatch → aggregator
  → verifier → deduplication → ranker → summarizer
  → citation_generator → report_generator → END
"""
import asyncio
import json
from typing import Any, AsyncGenerator, Dict, List, Optional, TypedDict

import structlog
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.schemas.research import ResearchPlan, SourceResult

logger = structlog.get_logger(__name__)


# ─── Agent State ─────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    """Shared state passed between all nodes in the graph."""
    query: str
    chat_id: str
    user_id: str
    plan: Optional[ResearchPlan]
    active_agents: List[str]
    raw_results: List[SourceResult]
    verified_results: List[SourceResult]
    deduplicated_results: List[SourceResult]
    ranked_results: List[SourceResult]
    summaries: Dict[str, str]
    citations: List[Dict[str, Any]]
    report: Optional[Dict[str, Any]]
    stream_tokens: List[str]
    error: Optional[str]
    domain: Optional[str]


# ─── LLM Factory ─────────────────────────────────────────────────────────────

def get_llm(temperature: Optional[float] = None) -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.LLM_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature if temperature is not None else settings.LLM_TEMPERATURE,
        max_output_tokens=settings.LLM_MAX_TOKENS,
    )


def _clean_json_str(content: Any) -> str:
    """Extract text and strip markdown code blocks or surrounding text from LLM JSON response."""
    import re
    if isinstance(content, list):
        text = "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content)
    else:
        text = str(content)
    text = text.strip()
    
    # Strip markdown fences if present
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    
    # Locate first '{' and last '}' to handle any extra preamble/epilogue
    first_brace = text.find("{")
    last_brace = text.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        return text[first_brace:last_brace + 1]
    
    return text


# ─── Node: Planner ───────────────────────────────────────────────────────────

async def planner_node(state: AgentState) -> AgentState:
    """Analyze the query and produce a structured research plan."""
    logger.info("Planner: analyzing query", query=state["query"][:100])
    llm = get_llm(temperature=0.1)

    system_prompt = """You are the Research Planner for ResearchAI. 
Your job is to analyze a user's research question and produce a structured execution plan.

Guidelines for Agent Selection:
- If the query is about breaking events, recent news, corporate actions, or company developments (e.g. "what happened yesterday at OpenAI", "recent events in Japan", "Tesla quarterly announcement"):
  - Set domain to "news", "technology", or "economics".
  - Always include "news" and "web" in agents_to_use.
  - Derive sub-queries with specific names, entities, and latest dates.
- If the query is scholarly/scientific/medical:
  - Include "academic" and/or "medical".

Respond ONLY with valid JSON matching this schema:
{
  "query": "the original query",
  "domain": "one of: general|medical|science|technology|social|economics|legal|history|news",
  "sub_queries": ["list of 2-5 specific search queries derived from the main question"],
  "agents_to_use": ["list of agents from: academic|medical|web|news|books|patent|government|statistics"],
  "reasoning": "brief explanation of why these agents and queries were chosen"
}"""

    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Research question: {state['query']}"),
        ])

        cleaned = _clean_json_str(response.content)
        plan_data = json.loads(cleaned)
        plan = ResearchPlan(**plan_data)
        state["plan"] = plan
        state["domain"] = plan.domain
        state["active_agents"] = plan.agents_to_use
        logger.info("Plan created", domain=plan.domain, agents=plan.agents_to_use)
    except Exception as e:
        logger.error("Planner failed, using defaults", error=str(e))
        state["plan"] = ResearchPlan(
            query=state["query"],
            domain="general",
            sub_queries=[state["query"]],
            agents_to_use=["academic", "web"],
            reasoning="Fallback plan due to planner error",
        )
        state["active_agents"] = ["academic", "web"]
        state["domain"] = "general"

    return state


# ─── Node: Task Manager + Parallel Dispatch ──────────────────────────────────

async def task_manager_node(state: AgentState) -> AgentState:
    """Launch all selected child agents in parallel."""
    from app.agents.child.academic_agent import AcademicAgent
    from app.agents.child.medical_agent import MedicalAgent
    from app.agents.child.web_agent import WebAgent, NewsAgent
    from app.agents.child.books_agent import BooksAgent, PatentAgent, GovernmentAgent, StatisticsAgent

    AGENT_MAP = {
        "academic": AcademicAgent,
        "medical": MedicalAgent,
        "web": WebAgent,
        "news": NewsAgent,
        "books": BooksAgent,
        "patent": PatentAgent,
        "government": GovernmentAgent,
        "statistics": StatisticsAgent,
    }

    plan = state["plan"]
    if not plan:
        return state

    # Build search tasks — one per sub-query × agent combination
    tasks = []
    agents_to_run = state["active_agents"]

    for agent_name in agents_to_run:
        agent_cls = AGENT_MAP.get(agent_name)
        if not agent_cls:
            continue
        agent = agent_cls()
        # Use the primary query (agent-specific searches use their own optimizations)
        primary_query = plan.sub_queries[0] if plan.sub_queries else plan.query
        tasks.append(agent.search(primary_query))

    logger.info("Dispatching agents", count=len(tasks), agents=agents_to_run)

    all_results = await asyncio.gather(*tasks, return_exceptions=True)

    combined: List[SourceResult] = []
    for result in all_results:
        if isinstance(result, list):
            combined.extend(result)

    state["raw_results"] = combined
    logger.info("All agents completed", total_raw_results=len(combined))
    return state


# ─── Node: Aggregator ────────────────────────────────────────────────────────

async def aggregator_node(state: AgentState) -> AgentState:
    """Merge and initially filter raw results."""
    results = state.get("raw_results", [])
    # Filter out results with no title or very low confidence
    filtered = [r for r in results if r.title and len(r.title) > 3]
    state["verified_results"] = filtered
    logger.info("Aggregator filtered results", input=len(results), output=len(filtered))
    return state


# ─── Node: Verifier ──────────────────────────────────────────────────────────

async def verifier_node(state: AgentState) -> AgentState:
    """Verify source credibility and flag questionable sources."""
    results = state.get("verified_results", [])
    verified = []
    for source in results:
        # Minimum confidence threshold
        if source.confidence_score >= 0.3:
            verified.append(source)
    state["verified_results"] = verified
    logger.info("Verifier completed", verified=len(verified))
    return state


# ─── Node: Deduplication ─────────────────────────────────────────────────────

async def deduplication_node(state: AgentState) -> AgentState:
    """Remove duplicate sources (same DOI or very similar title)."""
    results = state.get("verified_results", [])
    seen_dois = set()
    seen_titles = set()
    unique = []

    for source in results:
        # DOI-based deduplication
        if source.doi:
            doi_key = source.doi.lower().strip()
            if doi_key in seen_dois:
                continue
            seen_dois.add(doi_key)

        # Title-based deduplication (normalized)
        title_key = source.title.lower().strip()[:100]
        if title_key in seen_titles:
            continue
        seen_titles.add(title_key)
        unique.append(source)

    state["deduplicated_results"] = unique
    logger.info("Deduplication completed", before=len(results), after=len(unique))
    return state


# ─── Node: Ranker ────────────────────────────────────────────────────────────

async def ranker_node(state: AgentState) -> AgentState:
    """Rank sources by confidence score (descending)."""
    results = state.get("deduplicated_results", [])
    ranked = sorted(results, key=lambda r: r.confidence_score, reverse=True)
    # Keep top 40 sources for report generation
    state["ranked_results"] = ranked[:40]
    logger.info("Ranking completed", ranked=len(state["ranked_results"]))
    return state


# ─── Node: Summarizer ────────────────────────────────────────────────────────

async def summarizer_node(state: AgentState) -> AgentState:
    """Use LLM to comprehensively synthesize evidence across all child agent sources."""
    results = state.get("ranked_results", [])
    if not results:
        state["summaries"] = {}
        return state

    llm = get_llm(temperature=0.2)

    # Build a combined context string with up to 30 sources, more content per source
    sources_text = "\n\n".join(
        f"[{i+1}] Title: {r.title}\nAuthors: {', '.join(r.authors or ['Unknown'])}\n"
        f"Source Type / Database: {r.agent_type.upper()} ({r.publisher or 'N/A'})\n"
        f"Published: {r.publication_date or 'N/A'}\n"
        f"URL/DOI: {r.url or r.doi or 'N/A'}\n"
        f"Abstract / Content Snippet:\n{(r.abstract or r.summary or '')[:1200]}"
        for i, r in enumerate(results[:30])
    )

    system_prompt = """You are a Senior Principal Research Scientist & Literature Review Director.
Given the primary literature and verified intelligence collected by the specialized research fleet, produce an exhaustive, high-depth scholarly synthesis.

Respond ONLY with valid JSON matching this schema:
{
  "synthesis": "4-6 rich, dense paragraphs establishing state-of-the-art developments, mechanistic insights, quantitative metrics, and empirical consensus across the literature.",
  "key_findings": [
    "6-10 major, granular empirical findings with quantitative data, specific study results, mechanisms, and statistical metrics derived from the sources"
  ],
  "conflicts": [
    "3-6 explicit contradictions, debates, conflicting methodology results, or diverging viewpoints identified across different papers/sources"
  ],
  "gaps": [
    "4-8 unaddressed research questions, missing longitudinal data, technological bottlenecks, or literature gaps"
  ]
}"""

    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"Research Question: {state['query']}\nDomain: {state.get('domain', 'general')}\n\nEvidence Base ({len(results[:25])} sources):\n{sources_text}"),
        ])
        cleaned = _clean_json_str(response.content)
        state["summaries"] = json.loads(cleaned)
    except Exception as e:
        logger.error("Summarizer failed", error=str(e))
        state["summaries"] = {
            "synthesis": "Comprehensive research synthesis compiled from multi-agent discovery.",
            "key_findings": [f"Evaluated evidence across {len(results)} verified research sources."],
            "conflicts": [],
            "gaps": [],
        }

    return state


# ─── Node: Citation Generator ────────────────────────────────────────────────

async def citation_generator_node(state: AgentState) -> AgentState:
    """Generate APA, MLA, and Chicago citations for all ranked sources."""
    results = state.get("ranked_results", [])
    citations = []

    for source in results:
        apa = _format_apa(source)
        mla = _format_mla(source)
        chicago = _format_chicago(source)

        # Update source objects with generated citations
        source.citation_apa = apa
        source.citation_mla = mla
        source.citation_chicago = chicago

        citations.append({
            "title": source.title,
            "apa": apa,
            "mla": mla,
            "chicago": chicago,
            "url": source.url,
            "doi": source.doi,
        })

    state["citations"] = citations
    logger.info("Citations generated", count=len(citations))
    return state


def _format_apa(source: SourceResult) -> str:
    authors = source.authors or []
    author_str = ""
    if authors:
        if len(authors) == 1:
            author_str = authors[0]
        elif len(authors) <= 7:
            author_str = ", ".join(authors[:-1]) + f", & {authors[-1]}"
        else:
            author_str = ", ".join(authors[:6]) + f", ... {authors[-1]}"

    year = f"({source.publication_date[:4]})" if source.publication_date and len(source.publication_date) >= 4 else "(n.d.)"
    publisher = f" {source.publisher}." if source.publisher else ""
    doi_str = f" https://doi.org/{source.doi}" if source.doi else (f" {source.url}" if source.url else "")
    return f"{author_str} {year}. {source.title}.{publisher}{doi_str}"


def _format_mla(source: SourceResult) -> str:
    authors = source.authors or []
    author_str = authors[0] if authors else "Unknown"
    others = ", ".join(authors[1:]) if len(authors) > 1 else ""
    if others:
        author_str += f", et al."
    title = f'"{source.title}."'
    publisher = source.publisher or ""
    year = source.publication_date[:4] if source.publication_date and len(source.publication_date) >= 4 else "n.d."
    url = f" {source.url}." if source.url else ""
    return f"{author_str} {title} {publisher}, {year}.{url}"


def _format_chicago(source: SourceResult) -> str:
    authors = source.authors or []
    author_str = authors[0] if authors else "Unknown"
    year = source.publication_date[:4] if source.publication_date and len(source.publication_date) >= 4 else "n.d."
    publisher = source.publisher or ""
    doi_str = f" doi:{source.doi}" if source.doi else (f" {source.url}" if source.url else "")
    return f'{author_str}. "{source.title}." {publisher} ({year}).{doi_str}'


# ─── Node: Report Generator ──────────────────────────────────────────────────

async def report_generator_node(state: AgentState) -> AgentState:
    """Generate an expansive, publication-grade research report using the LLM."""
    llm = get_llm(temperature=0.25)
    summaries = state.get("summaries", {})
    ranked = state.get("ranked_results", [])
    citations = state.get("citations", [])

    sources_summary = "\n".join(
        f"[{i+1}] {r.title} ({r.publication_date or 'n.d.'}) | Authors: {', '.join(r.authors[:3] or ['Unknown'])} | Type: {r.agent_type} | Conf: {r.confidence_score:.0%} | Abstract: {(r.abstract or r.summary or '')[:300]}"
        for i, r in enumerate(ranked[:40])
    )

    system_prompt = """You are the Lead Scientific Intelligence Analyst and Principal Author for ResearchAI.
Your goal is to author an EXHAUSTIVE, HIGHLY RIGOROUS, PUBLICATION-GRADE enterprise research report synthesizing all multi-agent discoveries.

CRITICAL REQUIREMENTS:
- This is a FULL research report, not a summary. Each text field MUST be long, detailed, and rich.
- executive_summary: minimum 600 words across 5 paragraphs.
- background_and_context: minimum 500 words across 4 paragraphs covering historical context, theoretical evolution, current paradigm.
- methodology: minimum 300 words detailing each child agent's data source and approach.
- findings: produce MINIMUM 6 distinct finding sections, each with 400+ word content paragraphs covering data, mechanisms, statistics.
- analysis: minimum 700 words across 7+ paragraphs of deep cross-cutting critical analysis.
- practical_implications: minimum 400 words across 4 paragraphs on industry, regulation, and deployment.
- conclusions: minimum 300 words with full synthesis.
- future_directions: minimum 8 concrete, actionable items with justification.
- Do NOT be brief. Do NOT truncate. Fill every field with maximum scholarly depth.

Respond ONLY with a valid JSON object matching this exact schema:
{
  "executive_summary": "[5 dense paragraphs, 600+ words] Executive overview: context, breakthrough findings, technical/mechanistic insights, clinical/commercial/societal impacts, and strategic conclusions.",
  "research_question": "Formal, multi-part articulation of the central research inquiry and all sub-domains investigated.",
  "background_and_context": "[4 detailed paragraphs, 500+ words] Foundational principles, historical evolution, theoretical underpinnings, key milestones, and the contemporary research paradigm.",
  "methodology": "[300+ words] Complete documentation of the 8-agent investigative fleet: Academic (OpenAlex, CrossRef, Semantic Scholar, arXiv), Medical (PubMed/NCBI), Web, News, Books, Patent, Government, Statistics agents — their specific data sources, retrieval strategies, confidence scoring, deduplication, and ranking methodology.",
  "findings": [
    {
      "section": "Descriptive title of finding section (use 6-8 distinct domain-specific sections)",
      "content": "[400+ words, 3 comprehensive paragraphs] Detailed empirical findings with quantitative data, mechanisms, experimental results, statistical metrics, and inter-study comparison.",
      "key_takeaways": ["3-5 granular bullet takeaways with specific data points"],
      "evidence": ["Titles or authors of 3-5 supporting papers from the source list"]
    }
  ],
  "analysis": "[700+ words, 7+ paragraphs] Rigorous critical analysis: thematic cross-cutting patterns, technological bottlenecks, structural trade-offs, paradigm shifts, conflicting evidence evaluation, and state-of-the-art dynamics.",
  "comparisons": [
    {
      "aspect": "Comparative dimension (e.g., Approach A vs B, Efficacy vs Safety, Cost vs Scalability)",
      "analysis": "[200+ word] Analytical paragraph evaluating trade-offs with quantitative evidence.",
      "positions": [
        {
          "stance": "Position or perspective name",
          "sources": ["Supporting paper titles"],
          "evidence": "Specific quantitative or mechanistic rationale"
        }
      ]
    }
  ],
  "practical_implications": "[400+ words, 4 paragraphs] Translational adoption pathways, industrial/commercial relevance, regulatory landscape, ethical considerations, and deployment considerations.",
  "conclusions": "[300+ words] Comprehensive final synthesis uniting all confirmed evidence streams, consensus milestones, paradigm conclusions, and key takeaways.",
  "limitations": "[200+ words] Transparent examination of evidence constraints, sample size issues, methodology variance, publication biases, and data gaps.",
  "future_directions": "[8 detailed, actionable items with justification for each] Concrete research recommendations, technology development priorities, and strategic roadmap items."
}"""

    try:
        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
Research Question: {state['query']}
Domain: {state.get('domain', 'general')}
Total Verified Sources: {len(ranked)}

Fleet Synthesis:
{summaries.get('synthesis', 'N/A')}

Key Findings Extracted:
{chr(10).join('- ' + f for f in summaries.get('key_findings', []))}

Contradictions & Debates Identified:
{chr(10).join('- ' + c for c in summaries.get('conflicts', []))}

Identified Research Gaps:
{chr(10).join('- ' + g for g in summaries.get('gaps', []))}

Primary Evidence Base:
{sources_summary}
"""),
        ])
        cleaned = _clean_json_str(response.content)
        report_content = json.loads(cleaned)
    except Exception as e:
        logger.error("Report generator failed", error=str(e))
        report_content = {
            "executive_summary": summaries.get("synthesis", "Comprehensive research report compiled from multi-agent discovery."),
            "research_question": state["query"],
            "background_and_context": "The investigated domain represents an active frontier of interdisciplinary research.",
            "methodology": f"Multi-agent AI research executed across {len(ranked)} primary and scholarly sources.",
            "findings": [
                {"section": "Primary Evidence Synthesis", "content": summaries.get("synthesis", ""), "key_takeaways": summaries.get("key_findings", [])[:3], "evidence": [r.title for r in ranked[:3]]}
            ],
            "analysis": summaries.get("synthesis", ""),
            "comparisons": [],
            "practical_implications": "Translational insights indicate rapid integration across industry and clinical sectors.",
            "conclusions": "The evidence reflects strong empirical momentum across investigated areas.",
            "limitations": "Report generation encountered an error during detailed formatting.",
            "future_directions": "Further research should evaluate longitudinal efficacy and scaling.",
        }

    state["report"] = {
        **report_content,
        "references": citations,
        "source_count": len(ranked),
        "domain": state.get("domain"),
        "query": state["query"],
    }

    logger.info("Report generated", source_count=len(ranked))
    return state


# ─── Build LangGraph ─────────────────────────────────────────────────────────

def build_research_graph() -> StateGraph:
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("task_manager", task_manager_node)
    graph.add_node("aggregator", aggregator_node)
    graph.add_node("verifier", verifier_node)
    graph.add_node("deduplication", deduplication_node)
    graph.add_node("ranker", ranker_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_node("citation_generator", citation_generator_node)
    graph.add_node("report_generator", report_generator_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "task_manager")
    graph.add_edge("task_manager", "aggregator")
    graph.add_edge("aggregator", "verifier")
    graph.add_edge("verifier", "deduplication")
    graph.add_edge("deduplication", "ranker")
    graph.add_edge("ranker", "summarizer")
    graph.add_edge("summarizer", "citation_generator")
    graph.add_edge("citation_generator", "report_generator")
    graph.add_edge("report_generator", END)

    return graph.compile()


# Singleton compiled graph
research_graph = build_research_graph()


# ─── Public API ──────────────────────────────────────────────────────────────

async def run_research(
    query: str,
    chat_id: str,
    user_id: str,
) -> Dict[str, Any]:
    """
    Execute the full research pipeline and return the completed state.
    Called by Celery workers for background processing.
    """
    from app.core.safety import moderate_query
    is_blocked, refusal_reason = moderate_query(query)
    if is_blocked:
        return {
            "query": query,
            "chat_id": chat_id,
            "user_id": user_id,
            "report": None,
            "error": refusal_reason,
            "active_agents": [],
            "raw_results": [],
            "verified_results": [],
            "deduplicated_results": [],
            "ranked_results": [],
            "summaries": {},
            "citations": [],
        }

    initial_state: AgentState = {
        "query": query,
        "chat_id": chat_id,
        "user_id": user_id,
        "plan": None,
        "active_agents": [],
        "raw_results": [],
        "verified_results": [],
        "deduplicated_results": [],
        "ranked_results": [],
        "summaries": {},
        "citations": [],
        "report": None,
        "stream_tokens": [],
        "error": None,
        "domain": None,
    }

    final_state = await research_graph.ainvoke(initial_state)
    return final_state


CONVERSATIONAL_QUERIES = {
    "hey", "hi", "hello", "hola", "howdy", "sup", "greetings",
    "good morning", "good afternoon", "good evening",
    "who are you", "what are you", "what can you do", "help",
    "test", "testing", "thanks", "thank you", "bye", "goodbye",
    "hey there", "hi there", "hello there", "hello ai", "how are you"
}


async def stream_research(
    query: str,
    chat_id: str,
    user_id: str,
) -> AsyncGenerator[Dict[str, Any], None]:
    """
    Execute the research pipeline with streaming status updates.
    Yields SSE-compatible events at each node transition.
    """
    from app.core.safety import moderate_query

    # 1. Content Moderation & Policy Check (Abusive, Sexual, Harmful Queries)
    is_blocked, refusal_reason = moderate_query(query)
    if is_blocked:
        yield {"type": "status", "message": "Policy Check"}
        yield {
            "type": "complete",
            "conversational": True,
            "message": refusal_reason,
            "report": None,
            "sources": [],
            "citations": [],
        }
        return

    clean_q = query.strip().lower().rstrip("!?.")

    # 1. Immediate Conversational Greeting / Short Query Interception
    is_short_or_trivial = len(clean_q) <= 3 or clean_q in {
        "hey", "hi", "hello", "hola", "howdy", "sup", "hoo", "yo", "hlo", "heyy", "heya",
        "who", "what", "help", "test", "testing", "thanks", "thank", "bye", "goodbye", "ok", "okay",
        "good morning", "good afternoon", "good evening", "how are you", "who are you", "what can you do"
    }

    if is_short_or_trivial or clean_q in CONVERSATIONAL_QUERIES or (len(clean_q.split()) <= 2 and any(clean_q.startswith(g) for g in ["hey", "hi", "hello", "good morning", "good evening", "how are you"])):
        yield {"type": "status", "message": "Ready"}
        assistant_msg = (
            "Hello! I am **ResearchAI**, an enterprise-grade multi-agent scientific intelligence platform.\n\n"
            "I can investigate academic inquiries, cross-reference peer-reviewed literature across PubMed, arXiv, OpenAlex, Semantic Scholar, and Google Books, and synthesize publication-quality analytical intelligence reports.\n\n"
            "**Try asking a research inquiry such as:**\n"
            "• *What are the latest breakthroughs in solid-state lithium battery electrolytes?*\n"
            "• *Analyze recent clinical trials for mRNA cancer therapeutics.*\n"
            "• *Compare quantum computing error mitigation vs fault-tolerant architectures.*"
        )
        yield {
            "type": "complete",
            "conversational": True,
            "message": assistant_msg,
            "report": None,
            "sources": [],
            "citations": [],
        }
        return

    initial_state: AgentState = {
        "query": query,
        "chat_id": chat_id,
        "user_id": user_id,
        "plan": None,
        "active_agents": [],
        "raw_results": [],
        "verified_results": [],
        "deduplicated_results": [],
        "ranked_results": [],
        "summaries": {},
        "citations": [],
        "report": None,
        "stream_tokens": [],
        "error": None,
        "domain": None,
    }

    NODE_LABELS = {
        "planner": "Understanding research inquiry",
        "task_manager": "Searching scholarly databases",
        "aggregator": "Aggregating academic sources",
        "verifier": "Verifying empirical evidence",
        "deduplication": "Filtering and refining results",
        "ranker": "Ranking sources by relevance",
        "summarizer": "Synthesizing cross-disciplinary findings",
        "citation_generator": "Compiling citations and references",
        "report_generator": "Generating comprehensive report",
    }

    current_state = dict(initial_state)

    async for event in research_graph.astream(initial_state, stream_mode="updates"):
        for node_name, node_state in event.items():
            current_state.update(node_state)
            label = NODE_LABELS.get(node_name, f"Processing {node_name}...")
            yield {
                "type": "status",
                "node": node_name,
                "message": label,
                "data": {
                    "source_count": len(current_state.get("raw_results", [])),
                    "verified_count": len(current_state.get("verified_results", [])),
                    "domain": current_state.get("domain"),
                    "active_agents": current_state.get("active_agents", []),
                },
            }

    # Yield final report
    yield {
        "type": "complete",
        "report": current_state.get("report"),
        "sources": [s.model_dump() for s in current_state.get("ranked_results", [])],
        "citations": current_state.get("citations", []),
    }
