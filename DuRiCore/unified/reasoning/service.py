from __future__ import annotations
from typing import Dict, Any
from DuRiCore.reasoning_engine.core.reasoning_engine import ReasoningEngine

class UnifiedReasoningService:
    """
    통합 추론 서비스:
      - 기본 경로: 기존 ReasoningEngine(process) 호출
      - 전략 지시가 있을 때: strategies REGISTRY 경유
    """
    def __init__(self) -> None:
        self.engine = ReasoningEngine()
    
    def process(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        strat = (payload or {}).get("strategy")
        if strat:
            # 기존 전략 모듈 활용
            try:
                from DuRiCore.reasoning_engine.strategies.deductive_solver import DeductiveSolver
                from DuRiCore.reasoning_engine.strategies.inductive_solver import InductiveSolver
                from DuRiCore.reasoning_engine.strategies.abductive_solver import AbductiveSolver
                
                strategy_map = {
                    "deductive": DeductiveSolver,
                    "inductive": InductiveSolver,
                    "abductive": AbductiveSolver
                }
                cls = strategy_map.get(str(strat).lower())
                if cls:
                    return cls().solve(payload)
            except ImportError:
                pass
        return self.engine.process(payload)
