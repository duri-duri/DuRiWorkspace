from __future__ import annotations

from typing import Any, Dict

from DuRiCore.reasoning_engine.core.reasoning_engine import ReasoningEngine

# 전략 레지스트리는 옵션 의존성으로 취급
try:
    from DuRiCore.reasoning_engine.strategies.registry import get_strategy
except Exception:
    get_strategy = None  # 전략 미구현 시 None


class UnifiedReasoningService:
    """
    통합 추론 서비스:
      - 기본 경로: 기존 ReasoningEngine(process) 호출
      - 전략 지시가 있을 때: strategies REGISTRY 경유(있을 때만)
    """

    def __init__(self) -> None:
        self.engine = ReasoningEngine()

    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        strat = (payload or {}).get("strategy")
        if strat and get_strategy:
            cls = get_strategy(str(strat).lower())
            return cls().solve(payload)
        return self.engine.process(payload)
