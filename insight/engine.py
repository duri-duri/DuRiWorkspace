import re
from typing import Dict, List, Optional, Tuple

_splitter = re.compile(r"[^\w]+", re.UNICODE)


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _splitter.split(text or "") if t]


def ngrams(tokens: List[str], n: int):
    if n <= 0:
        return []
    return (tuple(tokens[i : i + n]) for i in range(max(0, len(tokens) - n + 1)))


def softclip(x: float, k: float = 5.0) -> float:
    """s-shaped squashing to [0,1) for penalty normalization."""
    import math

    return 1.0 - math.exp(-k * max(0.0, x))


def novelty_score(prompt_tokens: List[str], text_tokens: List[str]) -> float:
    """Unique-token ratio vs repetition penalty; reduces if overlap with prompt is too large."""
    if not text_tokens:
        return 0.0
    uniq = len(set(text_tokens))
    base = uniq / max(1, len(text_tokens))  # 0..1
    # Penalize 3-gram repetition
    tri = list(ngrams(text_tokens, 3))
    rep = 0.0
    if tri:
        seen = {}
        for t in tri:
            seen[t] = seen.get(t, 0) + 1
        repeats = sum(v - 1 for v in seen.values() if v > 1)
        rep = softclip(repeats / max(1, len(tri)), k=8.0)  # 0..~; clip to 0..1
    # Penalize prompt overlap heavy reuse
    overlap = len(set(text_tokens) & set(prompt_tokens)) / max(1, len(set(text_tokens)))
    overlap_pen = softclip(max(0.0, overlap - 0.3) / 0.7, k=5.0)  # tolerate 30%
    score = max(0.0, min(1.0, base * (1.0 - 0.6 * rep) * (1.0 - 0.5 * overlap_pen)))
    return score


def coherence_score(text_tokens: List[str]) -> float:
    """Lightweight cohesion using anchor words & bigram churn penalty."""
    if not text_tokens:
        return 0.0
    # Anchor words (connector/pronouns) to encourage linkage
    anchors = {
        "and",
        "or",
        "because",
        "so",
        "then",
        "therefore",
        "hence",
        "but",
        "however",
        "thus",
        "since",
        "when",
        "while",
        "if",
        "we",
        "it",
        "this",
        "that",
        "these",
        "those",
    }
    anchor_ratio = len([t for t in text_tokens if t in anchors]) / max(
        1, len(text_tokens)
    )
    # Bigram churn: too random progression lowers score
    bg = list(ngrams(text_tokens, 2))
    churn = 0.0
    if bg:
        seen = {}
        for b in bg:
            seen[b] = seen.get(b, 0) + 1
        uniq_bg = len(seen)
        churn = 1.0 - (uniq_bg / max(1, len(bg)))  # more repeats => lower churn
    # We want some anchors (0.05~0.2) and moderate churn (~0.3)
    anchor_term = 1.0 - abs(anchor_ratio - 0.12) / 0.12
    churn_term = 1.0 - abs(churn - 0.35) / 0.35
    score = max(0.0, min(1.0, 0.6 * max(0.0, anchor_term) + 0.4 * max(0.0, churn_term)))
    return score


def brevity_prior(text_tokens: List[str], mu: int = 120, sigma: int = 60) -> float:
    """Gaussian prior peaking at mu tokens, clipped to [0,1]."""
    import math

    n = len(text_tokens)
    if n == 0:
        return 0.0
    z = (n - mu) / max(1.0, sigma)
    return max(0.0, min(1.0, math.exp(-0.5 * z * z)))


DEFAULT_WEIGHTS = {"novelty": 0.45, "coherence": 0.40, "brevity": 0.15}


def score_candidate(
    prompt: str, text: str, weights: Optional[Dict[str, float]] = None
) -> Dict[str, float]:
    """Return per-metric scores and composite S in [0,1]."""
    if not isinstance(text, str) or not text.strip():
        return {"novelty": 0.0, "coherence": 0.0, "brevity": 0.0, "S": 0.0}
    weights = weights or DEFAULT_WEIGHTS
    p_tokens = tokenize(prompt)
    t_tokens = tokenize(text)
    n = novelty_score(p_tokens, t_tokens)
    c = coherence_score(t_tokens)
    b = brevity_prior(t_tokens)
    s = max(
        0.0,
        min(
            1.0,
            weights["novelty"] * n + weights["coherence"] * c + weights["brevity"] * b,
        ),
    )
    return {"novelty": n, "coherence": c, "brevity": b, "S": s}


def rank(
    prompt: str,
    candidates: List[str],
    weights: Optional[Dict[str, float]] = None,
    k: int = 1,
) -> List[Tuple[int, float, Dict[str, float]]]:
    """Return top-k as list of (index, S, breakdown)."""
    if not candidates:
        return []
    scores = []
    for i, c in enumerate(candidates):
        br = score_candidate(prompt, c, weights=weights)
        scores.append((i, br["S"], br))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[: max(1, min(k, len(scores)))]
