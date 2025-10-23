#!/usr/bin/env python3
"""
DuRi 판단 과정 기록 시스템 (JudgmentTrace)
판단이 발생한 모든 순간에 대해 구조화된 기록을 저장하는 시스템
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class JudgmentTrace:
    """판단 과정 기록 데이터 구조"""

    timestamp: str
    context: str  # 어떤 맥락에서 판단이 발생했는지
    judgment: str  # 어떤 판단이 일어났는지
    reasoning: str  # 그 판단을 하게 된 근거
    outcome: str  # 그 판단으로 이어진 행동 혹은 결정
    confidence_level: float = 0.0  # 판단에 대한 신뢰도 (0.0-1.0)
    tags: List[str] = None  # 판단을 분류하기 위한 태그들

    def __post_init__(self):
        if self.tags is None:
            self.tags = []


class JudgmentTraceLogger:
    """DuRi 판단 과정 기록 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JudgmentTraceLogger, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.traces: List[JudgmentTrace] = []
            self.trace_file = "DuRiCore/memory/judgment_traces.json"
            self.initialized = True
            self._load_traces()

    def _load_traces(self):
        """기존 판단 기록들을 로드합니다."""
        try:
            if os.path.exists(self.trace_file):
                with open(self.trace_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.traces = [
                        JudgmentTrace(**trace) for trace in data.get("traces", [])
                    ]
        except Exception as e:
            print(f"판단 기록 로드 실패: {e}")

    def _save_traces(self):
        """판단 기록들을 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.trace_file), exist_ok=True)
            data = {
                "traces": [asdict(trace) for trace in self.traces],
                "total_traces": len(self.traces),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.trace_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"판단 기록 저장 실패: {e}")

    def record_judgment_trace(
        self,
        context: str,
        judgment: str,
        reasoning: str,
        outcome: str,
        confidence_level: float = 0.0,
        tags: List[str] = None,
    ) -> JudgmentTrace:
        """
        판단 과정을 기록합니다.

        Args:
            context: 어떤 맥락에서 판단이 발생했는지
            judgment: 어떤 판단이 일어났는지
            reasoning: 그 판단을 하게 된 근거
            outcome: 그 판단으로 이어진 행동 혹은 결정
            confidence_level: 판단에 대한 신뢰도 (0.0-1.0)
            tags: 판단을 분류하기 위한 태그들

        Returns:
            생성된 JudgmentTrace 객체
        """
        trace = JudgmentTrace(
            timestamp=datetime.now().isoformat(),
            context=context,
            judgment=judgment,
            reasoning=reasoning,
            outcome=outcome,
            confidence_level=max(0.0, min(1.0, confidence_level)),
            tags=tags or [],
        )

        self.traces.append(trace)
        self._save_traces()

        # DuRiThoughtFlow에도 기록
        from ..thought_flow.du_ri_thought_flow import DuRiThoughtFlow

        DuRiThoughtFlow.register_stream("judgment_trace", asdict(trace))

        return trace

    def get_recent_traces(self, limit: int = 10) -> List[JudgmentTrace]:
        """최근 판단 기록들을 반환합니다."""
        return self.traces[-limit:] if self.traces else []

    def get_traces_by_tags(self, tags: List[str]) -> List[JudgmentTrace]:
        """특정 태그가 포함된 판단 기록들을 반환합니다."""
        if not tags:
            return self.traces

        filtered_traces = []
        for trace in self.traces:
            if any(tag in trace.tags for tag in tags):
                filtered_traces.append(trace)

        return filtered_traces

    def get_traces_by_confidence_range(
        self, min_confidence: float = 0.0, max_confidence: float = 1.0
    ) -> List[JudgmentTrace]:
        """신뢰도 범위에 따른 판단 기록들을 반환합니다."""
        filtered_traces = []
        for trace in self.traces:
            if min_confidence <= trace.confidence_level <= max_confidence:
                filtered_traces.append(trace)

        return filtered_traces

    def get_traces_summary(self) -> Dict:
        """판단 기록 요약 정보를 반환합니다."""
        if not self.traces:
            return {"total_traces": 0, "average_confidence": 0.0}

        total_confidence = sum(trace.confidence_level for trace in self.traces)
        average_confidence = total_confidence / len(self.traces)

        # 태그별 통계
        tag_counts = {}
        for trace in self.traces:
            for tag in trace.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            "total_traces": len(self.traces),
            "average_confidence": round(average_confidence, 3),
            "tag_distribution": tag_counts,
            "recent_traces_count": len(self.get_recent_traces(7)),  # 최근 7개
        }

    def clear_old_traces(self, days_to_keep: int = 30):
        """오래된 판단 기록들을 삭제합니다."""
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)

        filtered_traces = []
        for trace in self.traces:
            trace_timestamp = datetime.fromisoformat(trace.timestamp).timestamp()
            if trace_timestamp >= cutoff_date:
                filtered_traces.append(trace)

        self.traces = filtered_traces
        self._save_traces()
        print(f"오래된 판단 기록 {len(self.traces) - len(filtered_traces)}개 삭제됨")
