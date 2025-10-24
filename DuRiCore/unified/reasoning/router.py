from __future__ import annotations

import os
import random
from typing import Any, Dict

from DuRiCore.reasoning_engine.core.reasoning_engine import ReasoningEngine  # 기존 파사드 유지
from DuRiCore.unified.reasoning.service import UnifiedReasoningService

_svc = UnifiedReasoningService()
_base = ReasoningEngine()


def _use_unified(prob: int) -> bool:
    mode = os.getenv("DURI_UNIFIED_REASONING_MODE", "auto").lower()
    if mode == "force":
        return True
    if mode == "off":
        return False
    # auto 모드: 확률 기반
    return random.randint(1, 100) <= max(0, min(100, prob))


def process(payload: Dict[str, Any]) -> Dict[str, Any]:
    rollout = int(os.getenv("DURI_UNIFIED_REASONING_ROLLOUT", "0"))
    if _use_unified(rollout):
        return _svc.process(payload)
    return _base.process(payload)
