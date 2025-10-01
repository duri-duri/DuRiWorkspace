from __future__ import annotations

from typing import Any, Dict


class UnifiedLearningEvolutionService:
    """
    학습/진화 통합 파사드:
      - 기존 unified_learning_system.py 활용
      - 학습, 진화 명령을 하나의 엔드포인트로 수집해 기존 모듈에 위임
    """

    def __init__(self, learn=None, evolve=None) -> None:
        self.learn = learn
        self.evolve = evolve
        # 기존 통합 학습 시스템 활용
        try:
            from DuRiCore.unified_learning_system import (
                UnifiedLearningSystem as ExistingSystem,
            )

            self.existing_system = ExistingSystem()
        except ImportError:
            self.existing_system = None

    def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        mode = (payload or {}).get("mode", "learn")

        # 기존 시스템이 있으면 활용
        if self.existing_system:
            try:
                if mode == "learn":
                    return self.existing_system.process_learning_request(payload)
                elif mode == "evolve":
                    return self.existing_system.process_evolution_request(payload)
            except Exception:
                pass

        # 폴백: 직접 라우팅
        if mode == "learn" and callable(self.learn):
            return self.learn(payload)
        if mode == "evolve" and callable(self.evolve):
            return self.evolve(payload)
        return {"result": "le:noop", "confidence": 0.5}
