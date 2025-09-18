from typing import List, Tuple, Dict, Optional
from .scoring import novelty_score, coherence_score, brevity_prior
from .utils import tokenize

DEFAULT_WEIGHTS = {"novelty": 0.45, "coherence": 0.40, "brevity": 0.15}

def score_candidate(prompt: str, text: str, weights: Optional[Dict[str, float]] = None) -> Dict[str, float]:
    """Return per-metric scores and composite S in [0,1]."""
    if not isinstance(text, str) or not text.strip():
        return {"novelty": 0.0, "coherence": 0.0, "brevity": 0.0, "S": 0.0}
    weights = weights or DEFAULT_WEIGHTS
    p_tokens = tokenize(prompt)
    t_tokens = tokenize(text)
    n = novelty_score(p_tokens, t_tokens)
    c = coherence_score(t_tokens)
    b = brevity_prior(t_tokens)
    s = max(0.0, min(1.0, weights["novelty"]*n + weights["coherence"]*c + weights["brevity"]*b))
    return {"novelty": n, "coherence": c, "brevity": b, "S": s}

def rank(prompt: str, candidates: List[str], weights: Optional[Dict[str, float]] = None, k: int = 1
         ) -> List[Tuple[int, float, Dict[str, float]]]:
    """Return top-k as list of (index, S, breakdown)."""
    if not candidates:
        return []
    scores = []
    for i, c in enumerate(candidates):
        br = score_candidate(prompt, c, weights=weights)
        scores.append((i, br["S"], br))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[:max(1, min(k, len(scores)))]
