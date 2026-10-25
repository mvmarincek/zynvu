import re
import unicodedata

from zynvu.contracts import Requirements

KEYWORDS = {
    "coding": r"\b(cod\w*|program\w*|python|javascript|software|code|coding)\b",
    "vision": r"\b(imag\w*|visao|vision|tela|screen|foto\w*)\b",
    "asr": r"\b(transcri\w*|voz|audio|speech|voice)\b",
    "tts": r"\b(falar|sintese|tts)\b",
    "memory": r"\b(memoria|lembr\w*|document\w*|rag|memory)\b",
    "mcp": r"\b(mcp|github|slack|linear|notion|gmail|conector\w*)\b",
    "decision": r"\b(decis\w*|rotea\w*|routing)\b",
}


def parse_goal(goal: str) -> Requirements:
    """Offline keyword extraction; explicit Requirements overrides this heuristic."""
    text = "".join(
        c for c in unicodedata.normalize("NFD", goal.lower()) if not unicodedata.combining(c)
    )
    capabilities = ["conversation"]
    capabilities.extend(role for role, pattern in KEYWORDS.items() if re.search(pattern, text))
    return Requirements(user_goal=goal, capabilities=capabilities)
