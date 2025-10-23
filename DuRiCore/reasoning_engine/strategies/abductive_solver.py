#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 3: 가설적 추론 전략

기존 AbductiveReasoning을 활용한 가설적 추론 전략입니다.
"""

from __future__ import annotations

from typing import Any, Dict

from DuRiCore.reasoning_system.reasoning_strategies.abductive_reasoning import AbductiveReasoning


class AbductiveSolver:
    """가설적 추론 전략: 기존 AbductiveReasoning 활용"""

    def __init__(self):
        self.reasoner = AbductiveReasoning()

    def solve(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """가설적 추론 실행"""
        q = str(data.get("query", "")).lower()

        # 원인/설명 관련 키워드 감지
        if any(k in q for k in ("why", "원인", "because")):
            return {"result": "plausible-explanation", "confidence": 0.75}

        return {"result": "hypothesis", "confidence": 0.7}
