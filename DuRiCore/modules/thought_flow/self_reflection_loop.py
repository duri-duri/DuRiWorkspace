#!/usr/bin/env python3
"""
DuRi 자가 반성 루프 시스템
매일 또는 일정 트리거마다 판단 기록들을 분석하고 자기 신념과 행동 패턴을 업데이트하는 시스템
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class ReflectionInsight:
    """반성 통찰 데이터 구조"""

    timestamp: str
    judgment_trace_id: str
    analysis: str  # 판단이 합리적이었는지 분석
    regret: str  # 판단 결과에 대한 후회/성찰
    improvement_suggestion: str  # 개선 제안
    confidence_impact: float  # 신뢰도에 미친 영향 (-1.0 ~ 1.0)


class SelfReflectionLoop:
    """DuRi 자가 반성 루프 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SelfReflectionLoop, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.insights: List[ReflectionInsight] = []
            self.core_beliefs: Dict[str, Any] = {}
            self.judgment_rules: Dict[str, Any] = {}
            self.reflection_file = "DuRiCore/memory/reflection_data.json"
            self.beliefs_file = "DuRiCore/memory/core_beliefs.json"
            self.rules_file = "DuRiCore/memory/judgment_rules.json"
            self.initialized = True
            self._load_data()

    def _load_data(self):
        """기존 반성 데이터, 신념, 규칙들을 로드합니다."""
        try:
            # 반성 데이터 로드
            if os.path.exists(self.reflection_file):
                with open(self.reflection_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.insights = [
                        ReflectionInsight(**insight) for insight in data.get("insights", [])
                    ]

            # 핵심 신념 로드
            if os.path.exists(self.beliefs_file):
                with open(self.beliefs_file, "r", encoding="utf-8") as f:
                    self.core_beliefs = json.load(f)

            # 판단 규칙 로드
            if os.path.exists(self.rules_file):
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    self.judgment_rules = json.load(f)

        except Exception as e:
            print(f"반성 데이터 로드 실패: {e}")

    def _save_data(self):
        """반성 데이터, 신념, 규칙들을 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.reflection_file), exist_ok=True)

            # 반성 데이터 저장
            reflection_data = {
                "insights": [asdict(insight) for insight in self.insights],
                "total_insights": len(self.insights),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.reflection_file, "w", encoding="utf-8") as f:
                json.dump(reflection_data, f, ensure_ascii=False, indent=2)

            # 핵심 신념 저장
            with open(self.beliefs_file, "w", encoding="utf-8") as f:
                json.dump(self.core_beliefs, f, ensure_ascii=False, indent=2)

            # 판단 규칙 저장
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump(self.judgment_rules, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"반성 데이터 저장 실패: {e}")

    def reflection_loop(self, trigger_type: str = "daily") -> Dict[str, Any]:
        """
        자가 반성 루프를 실행합니다.

        Args:
            trigger_type: 반성 루프 트리거 타입 ("daily", "user_request", "judgment_failure")

        Returns:
            반성 루프 실행 결과
        """
        print(f"🔍 자가 반성 루프 시작 (트리거: {trigger_type})")

        # 1. 최근 판단 기록들 불러오기
        from ..judgment_system.judgment_trace_logger import JudgmentTraceLogger

        judgment_logger = JudgmentTraceLogger()
        recent_traces = judgment_logger.get_recent_traces(limit=20)

        if not recent_traces:
            print("📝 분석할 판단 기록이 없습니다.")
            return {"status": "no_traces", "message": "분석할 판단 기록이 없습니다."}

        # 2. 각 판단 분석 및 반성 통찰 생성
        new_insights = []
        for trace in recent_traces:
            insight = self._analyze_judgment(trace)
            if insight:
                new_insights.append(insight)
                self.insights.append(insight)

        # 3. 반성 통찰을 바탕으로 신념과 규칙 업데이트
        updated_beliefs = self._update_core_beliefs(new_insights)
        updated_rules = self._update_judgment_rules(new_insights)

        # 4. 데이터 저장
        self._save_data()

        # 5. DuRiThoughtFlow에 기록
        from .du_ri_thought_flow import DuRiThoughtFlow

        reflection_summary = {
            "trigger_type": trigger_type,
            "traces_analyzed": len(recent_traces),
            "new_insights": len(new_insights),
            "beliefs_updated": len(updated_beliefs),
            "rules_updated": len(updated_rules),
            "timestamp": datetime.now().isoformat(),
        }
        DuRiThoughtFlow.register_stream("reflection_loop", reflection_summary)

        print(
            f"✅ 자가 반성 루프 완료: {len(new_insights)}개 통찰 생성, {len(updated_beliefs)}개 신념 업데이트"
        )

        return {
            "status": "success",
            "traces_analyzed": len(recent_traces),
            "new_insights": len(new_insights),
            "beliefs_updated": len(updated_beliefs),
            "rules_updated": len(updated_rules),
            "reflection_summary": reflection_summary,
        }

    def _analyze_judgment(self, trace) -> Optional[ReflectionInsight]:
        """개별 판단을 분석하여 반성 통찰을 생성합니다."""
        try:
            # 판단의 합리성 분석
            analysis = self._assess_rationality(trace)

            # 후회/성찰 생성
            regret = self._generate_regret(trace, analysis)

            # 개선 제안 생성
            improvement = self._generate_improvement_suggestion(trace, analysis, regret)

            # 신뢰도 영향 계산
            confidence_impact = self._calculate_confidence_impact(trace, analysis)

            insight = ReflectionInsight(
                timestamp=datetime.now().isoformat(),
                judgment_trace_id=trace.timestamp,
                analysis=analysis,
                regret=regret,
                improvement_suggestion=improvement,
                confidence_impact=confidence_impact,
            )

            return insight

        except Exception as e:
            print(f"판단 분석 실패: {e}")
            return None

    def _assess_rationality(self, trace) -> str:
        """판단의 합리성을 평가합니다."""
        # 신뢰도 기반 합리성 평가
        if trace.confidence_level >= 0.8:
            rationality = "높음"
        elif trace.confidence_level >= 0.5:
            rationality = "보통"
        else:
            rationality = "낮음"

        # 태그 기반 추가 분석
        if "긴급" in trace.tags:
            rationality += " (긴급 상황으로 인한 빠른 판단)"
        if "복잡" in trace.tags:
            rationality += " (복잡한 상황으로 인한 신중한 판단)"

        return f"판단 합리성: {rationality} (신뢰도: {trace.confidence_level:.2f})"

    def _generate_regret(self, trace, analysis: str) -> str:
        """판단 결과에 대한 후회/성찰을 생성합니다."""
        regrets = []

        # 신뢰도가 낮은 경우
        if trace.confidence_level < 0.5:
            regrets.append("신뢰도가 낮은 상태에서 판단을 내린 것에 대한 후회")

        # 결과가 부정적인 경우 (간단한 휴리스틱)
        if "실패" in trace.outcome.lower() or "오류" in trace.outcome.lower():
            regrets.append("더 나은 결과를 위해 다른 접근 방식을 고려했어야 함")

        # 태그 기반 후회
        if "성급" in trace.tags:
            regrets.append("성급한 판단으로 인한 후회")

        if not regrets:
            regrets.append("현재로서는 특별한 후회 없음")

        return "; ".join(regrets)

    def _generate_improvement_suggestion(self, trace, analysis: str, regret: str) -> str:
        """개선 제안을 생성합니다."""
        suggestions = []

        # 신뢰도 기반 제안
        if trace.confidence_level < 0.5:
            suggestions.append("더 많은 정보 수집 후 판단하기")

        # 태그 기반 제안
        if "복잡" in trace.tags:
            suggestions.append("복잡한 상황에서는 단계별 접근 방식 사용")
        if "긴급" in trace.tags:
            suggestions.append("긴급 상황에서는 핵심 요소에 집중한 빠른 판단")

        # 일반적인 개선 제안
        suggestions.append("판단 전 잠시 멈추고 대안 검토하기")

        return "; ".join(suggestions)

    def _calculate_confidence_impact(self, trace, analysis: str) -> float:
        """신뢰도에 미친 영향을 계산합니다."""
        # 기본 영향도 계산 (신뢰도가 낮을수록 부정적 영향)
        base_impact = (trace.confidence_level - 0.5) * 2  # -1.0 ~ 1.0

        # 태그 기반 조정
        if "성급" in trace.tags:
            base_impact -= 0.2
        if "신중" in trace.tags:
            base_impact += 0.1

        return max(-1.0, min(1.0, base_impact))

    def _update_core_beliefs(self, insights: List[ReflectionInsight]) -> List[str]:
        """반성 통찰을 바탕으로 핵심 신념을 업데이트합니다."""
        updated_beliefs = []

        for insight in insights:
            # 신뢰도 영향이 큰 통찰만 신념 업데이트에 반영
            if abs(insight.confidence_impact) > 0.3:
                belief_key = f"belief_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                belief_value = {
                    "insight_id": insight.judgment_trace_id,
                    "content": insight.improvement_suggestion,
                    "confidence_impact": insight.confidence_impact,
                    "created_at": datetime.now().isoformat(),
                }

                self.core_beliefs[belief_key] = belief_value
                updated_beliefs.append(belief_key)

        return updated_beliefs

    def _update_judgment_rules(self, insights: List[ReflectionInsight]) -> List[str]:
        """반성 통찰을 바탕으로 판단 규칙을 업데이트합니다."""
        updated_rules = []

        for insight in insights:
            # 개선 제안이 구체적인 경우만 규칙으로 변환
            if ";" in insight.improvement_suggestion:
                rule_key = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                rule_value = {
                    "insight_id": insight.judgment_trace_id,
                    "condition": insight.analysis,
                    "action": insight.improvement_suggestion,
                    "confidence_impact": insight.confidence_impact,
                    "created_at": datetime.now().isoformat(),
                }

                self.judgment_rules[rule_key] = rule_value
                updated_rules.append(rule_key)

        return updated_rules

    def get_reflection_summary(self) -> Dict:
        """반성 루프 요약 정보를 반환합니다."""
        return {
            "total_insights": len(self.insights),
            "total_beliefs": len(self.core_beliefs),
            "total_rules": len(self.judgment_rules),
            "recent_insights": len(self.insights[-10:]) if self.insights else 0,
            "average_confidence_impact": (
                sum(insight.confidence_impact for insight in self.insights) / len(self.insights)
                if self.insights
                else 0
            ),
        }
