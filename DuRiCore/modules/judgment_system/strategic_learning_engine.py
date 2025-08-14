#!/usr/bin/env python3
"""
DuRi 전략 학습 엔진 - 확장 버전
판단 결과를 관찰하고 패턴을 분석하여 전략적 통찰을 도출
"""

import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class StrategicLearningEngine:
    def __init__(self):
        self.history = []
        self.latest_trace = None

    def observe_decision(self, situation, action, reasoning):
        """
        판단 결과를 입력받아 전략적 학습을 위한 기록을 남깁니다.
        """
        trace = {
            "timestamp": datetime.now().isoformat(),
            "situation": situation,
            "action": action,
            "reasoning": reasoning
        }
        
        self.history.append(trace)
        self.latest_trace = trace
        
        return trace

    def generate_strategic_insight(self):
        """
        누적된 판단 기록을 바탕으로 전략적 통찰을 생성합니다.
        """
        if not self.history:
            return "아직 학습된 판단이 없습니다."

        summary = "DuRi가 전략적으로 판단한 흐름 요약:\n"
        for idx, h in enumerate(self.history):
            summary += f"{idx+1}. 상황: {h['situation']} → 행동: {h['action']} (이유: {h['reasoning']})\n"

        return summary

    def get_latest_trace(self):
        """
        최신 판단 추적 데이터를 반환합니다.
        """
        return self.latest_trace

    def get_all_traces(self):
        """
        모든 판단 추적 데이터를 반환합니다.
        """
        return self.history

    def export_traces(self):
        """
        판단 추적 데이터를 JSON 형태로 내보냅니다.
        """
        return {
            "total_traces": len(self.history),
            "latest_trace": self.latest_trace,
            "all_traces": self.history,
            "exported_at": datetime.now().isoformat()
        }
