from __future__ import annotations

import json
import os
import random
import threading
import time
from typing import Any, Dict

from DuRiCore.reasoning_engine.core.reasoning_engine import ReasoningEngine
from DuRiCore.unified.reasoning.service import UnifiedReasoningService

MIRROR = int(os.getenv("DURI_UNIFIED_REASONING_MIRROR", "0") or 0)
REPORT = os.getenv("DURI_MIRROR_REPORT", "var/reports/mirror_reasoning.jsonl")

_engine = ReasoningEngine()
_unified = UnifiedReasoningService()


def _bg(payload: Dict[str, Any], primary: Dict[str, Any]) -> None:
    try:
        u = _unified.process(dict(payload))
        rec = {"ts": time.time(), "payload": payload, "primary": primary, "unified": u}
        os.makedirs(os.path.dirname(REPORT), exist_ok=True)
        with open(REPORT, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except Exception as e:
        rec = {"ts": time.time(), "payload": payload, "error": str(e)}
        with open(REPORT + ".err", "a", encoding="utf-8") as f:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def handle(payload: Dict[str, Any]) -> Dict[str, Any]:
    """기존 엔진 결과를 즉시 반환. 샘플링된 일부만 통합 파사드에 '섀도우'로 보내 기록."""
    primary = _engine.process(payload)
    if MIRROR > 0 and random.randint(1, 100) <= MIRROR:
        threading.Thread(target=_bg, args=(payload, primary), daemon=True).start()
    return primary
