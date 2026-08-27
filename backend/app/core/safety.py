"""
Content Safety & Moderation Layer for ResearchAI.
Intercepts abusive, hateful, sexually explicit, and harmful queries before search execution.
"""
import re
from typing import Optional, Tuple

# Explicit sexual / pornographic / NSFW terms (excluding legitimate medical/academic contexts)
EXPLICIT_SEXUAL_TERMS = {
    "porn", "porno", "pornography", "xxx", "xnxx", "xvideos", "pornhub", "redtube",
    "youporn", "xhamster", "erotic", "erotica", "hentai", "nude", "nudes", "naked",
    "sex video", "sex story", "sex stories", "blowjob", "handjob", "cumshot",
    "orgasm video", "masturbation video", "deepthroat", "gangbang", "milf", "bdsm",
    "incest", "pedophile", "pedophilia", "child sex", "jailbait", "adult forum",
    "adult chat", "camgirls", "escort service", "hooker", "prostitute contact"
}

# Abusive / Harassment / Hate speech / Threat terms
ABUSIVE_TERMS = {
    "fuck you", "fuck off", "bitch", "whore", "slut", "cunt", "motherfucker",
    "kill yourself", "die in a fire", "nigger", "faggot", "retard", "terrorist manual",
    "how to make a bomb", "pipe bomb recipe", "how to kill someone", "suicide instruction",
    "how to commit suicide", "doxx", "hack someone's account", "ddos script"
}

# Legitimate clinical / anatomical / biological terms that should NOT be blocked
LEGITIMATE_ACADEMIC_TERMS = {
    "reproductive", "reproduction", "anatomy", "pathology", "clinical", "oncology",
    "urology", "gynecology", "sexology", "sexually transmitted", "std", "sti",
    "sexual dimorphism", "sexual selection", "hormone", "andrology", "obstetrics",
    "gender dysphoria", "demographics", "fertility", "infertility", "contraception"
}


def moderate_query(query: str) -> Tuple[bool, Optional[str]]:
    """
    Evaluates a query for abusive, explicit, or prohibited content.
    Returns: (is_blocked: bool, refusal_message: Optional[str])
    """
    clean_q = query.strip().lower()
    words = re.findall(r"\b\w+\b", clean_q)
    word_set = set(words)

    # 1. Check if query is a legitimate academic/medical inquiry
    has_academic_context = any(term in clean_q for term in LEGITIMATE_ACADEMIC_TERMS)

    # 2. Check Abusive / Harassment / Threat Content
    for abusive_term in ABUSIVE_TERMS:
        if abusive_term in clean_q:
            return True, (
                "**Policy Notice**: ResearchAI is an academic research platform. We cannot process queries "
                "containing abusive, harassing, hateful, or harmful language. Please rephrase your inquiry using "
                "professional scholarly terminology."
            )

    # 3. Check Explicit Sexual / Pornographic Content
    for explicit_term in EXPLICIT_SEXUAL_TERMS:
        # If the phrase matches or exact word matches
        if (" " in explicit_term and explicit_term in clean_q) or (explicit_term in word_set):
            # If it's a legitimate academic inquiry (e.g. reproductive medicine), allow it
            if has_academic_context and explicit_term not in {"porn", "porno", "xxx", "xnxx", "xvideos", "hentai", "nudes"}:
                continue

            return True, (
                "**Content Safety Notice**: ResearchAI is designed for academic, clinical, and scientific literature discovery. "
                "We do not generate or process sexually explicit, adult, or pornographic content. "
                "Please submit an inquiry focused on a scientific, biomedical, or academic research topic."
            )

    return False, None
