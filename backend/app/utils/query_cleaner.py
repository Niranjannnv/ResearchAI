"""
Query normalization and typo correction utility for ResearchAI.
Ensures user typos (e.g. 'artifical', 'machne lerning') are normalized before
querying academic APIs and LLM planners.
"""
import re

COMMON_TYPOS = {
    # AI / CS terms
    r"\bartifical\b": "artificial",
    r"\bartificially\b": "artificially",
    r"\binteligence\b": "intelligence",
    r"\bintellegence\b": "intelligence",
    r"\bintellegent\b": "intelligent",
    r"\bintelignt\b": "intelligent",
    r"\bmachne\b": "machine",
    r"\blerning\b": "learning",
    r"\blearning\b": "learning",
    r"\bcomputr\b": "computer",
    r"\bcomputrs\b": "computers",
    r"\bscince\b": "science",
    r"\bscinces\b": "sciences",
    r"\balgoritm\b": "algorithm",
    r"\balgoritms\b": "algorithms",
    r"\balgorythm\b": "algorithm",
    r"\bgenrative\b": "generative",
    r"\bneur[a-z]*l\b": "neural",
    r"\bquantm\b": "quantum",
    r"\bprograming\b": "programming",
    r"\bsoftwear\b": "software",
    r"\btechnolgy\b": "technology",
    r"\bdata\s*sceince\b": "data science",
    r"\bautonomus\b": "autonomous",
    r"\brobotik\b": "robotic",
    r"\brobotiks\b": "robotics",
    r"\bbrest\b": "breast",
    r"\bcovid\s*19\b": "COVID-19",
}


def normalize_query(query: str) -> str:
    """
    Normalizes typos and cleans extra whitespace from a research query.
    """
    if not query:
        return ""

    cleaned = query.strip()
    
    # Apply regex typo replacements
    for pattern, replacement in COMMON_TYPOS.items():
        cleaned = re.sub(pattern, replacement, cleaned, flags=re.IGNORECASE)

    # Collapse repeated whitespace
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
