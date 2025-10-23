from __future__ import annotations

from statistics import mean


def aggregate(results: list[dict]) -> dict:
    success_rate = (
        mean(1.0 if r.get("ok") else 0.0 for r in results) if results else 0.0
    )
    latency_ms = mean(r.get("latency_ms", 0) for r in results) if results else 0.0
    return {
        "success_rate": round(success_rate, 3),
        "latency_ms": round(latency_ms, 1),
        "n": len(results),
    }
