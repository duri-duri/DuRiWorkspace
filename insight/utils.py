import re
from typing import Iterable, List, Tuple

_splitter = re.compile(r"[^\w]+", re.UNICODE)


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in _splitter.split(text or "") if t]


def ngrams(tokens: List[str], n: int) -> Iterable[Tuple[str, ...]]:
    if n <= 0:
        return []
    return (tuple(tokens[i : i + n]) for i in range(max(0, len(tokens) - n + 1)))


def softclip(x: float, k: float = 5.0) -> float:
    """s-shaped squashing to [0,1) for penalty normalization."""
    import math

    return 1.0 - math.exp(-k * max(0.0, x))
