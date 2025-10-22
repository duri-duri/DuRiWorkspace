def tune_confidence(base: float) -> float:
    return max(0.0, min(base + 0.05, 1.0))
