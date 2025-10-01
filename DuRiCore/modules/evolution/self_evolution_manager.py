#!/usr/bin/env python3
"""
DuRi 자기개선 시퀀스 관리 시스템
반성 루프 이후 자동으로 실행되는 자기개선 시퀀스를 관리하는 시스템
"""

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
import json
import os
from typing import Any, Dict, List, Optional


@dataclass
class EvolutionStep:
    """진화 단계 데이터 구조"""

    timestamp: str
    step_type: str  # "belief_update", "rule_update", "behavior_change"
    description: str
    impact_score: float  # 진화에 미친 영향도 (0.0-1.0)
    previous_state: Dict
    new_state: Dict
    trigger_source: str  # 어떤 반성 통찰에서 비롯되었는지


class SelfEvolutionManager:
    """DuRi 자기개선 시퀀스 관리 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SelfEvolutionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.evolution_steps: List[EvolutionStep] = []
            self.core_beliefs: Dict[str, Any] = {}
            self.judgment_rules: Dict[str, Any] = {}
            self.behavior_patterns: Dict[str, Any] = {}
            self.evolution_file = "DuRiCore/memory/evolution_data.json"
            self.beliefs_file = "DuRiCore/memory/core_beliefs.json"
            self.rules_file = "DuRiCore/memory/judgment_rules.json"
            self.behaviors_file = "DuRiCore/memory/behavior_patterns.json"
            self.initialized = True
            self._load_data()

    def _load_data(self):
        """기존 진화 데이터, 신념, 규칙, 행동 패턴들을 로드합니다."""
        try:
            # 진화 데이터 로드
            if os.path.exists(self.evolution_file):
                with open(self.evolution_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.evolution_steps = [
                        EvolutionStep(**step)
                        for step in data.get("evolution_steps", [])
                    ]

            # 핵심 신념 로드
            if os.path.exists(self.beliefs_file):
                with open(self.beliefs_file, "r", encoding="utf-8") as f:
                    self.core_beliefs = json.load(f)

            # 판단 규칙 로드
            if os.path.exists(self.rules_file):
                with open(self.rules_file, "r", encoding="utf-8") as f:
                    self.judgment_rules = json.load(f)

            # 행동 패턴 로드
            if os.path.exists(self.behaviors_file):
                with open(self.behaviors_file, "r", encoding="utf-8") as f:
                    self.behavior_patterns = json.load(f)

        except Exception as e:
            print(f"진화 데이터 로드 실패: {e}")

    def _save_data(self):
        """진화 데이터, 신념, 규칙, 행동 패턴들을 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.evolution_file), exist_ok=True)

            # 진화 데이터 저장
            evolution_data = {
                "evolution_steps": [asdict(step) for step in self.evolution_steps],
                "total_steps": len(self.evolution_steps),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.evolution_file, "w", encoding="utf-8") as f:
                json.dump(evolution_data, f, ensure_ascii=False, indent=2)

            # 핵심 신념 저장
            with open(self.beliefs_file, "w", encoding="utf-8") as f:
                json.dump(self.core_beliefs, f, ensure_ascii=False, indent=2)

            # 판단 규칙 저장
            with open(self.rules_file, "w", encoding="utf-8") as f:
                json.dump(self.judgment_rules, f, ensure_ascii=False, indent=2)

            # 행동 패턴 저장
            with open(self.behaviors_file, "w", encoding="utf-8") as f:
                json.dump(self.behavior_patterns, f, ensure_ascii=False, indent=2)

        except Exception as e:
            print(f"진화 데이터 저장 실패: {e}")

    def execute_self_improvement_sequence(
        self, reflection_insights: List[Any] = None
    ) -> Dict[str, Any]:
        """
        자기개선 시퀀스를 실행합니다.

        Args:
            reflection_insights: 반성 루프에서 생성된 통찰들

        Returns:
            자기개선 시퀀스 실행 결과
        """
        print("🚀 자기개선 시퀀스 시작")

        # reflection_insights가 None이거나 리스트가 아닌 경우 처리
        if reflection_insights is None:
            reflection_insights = []
        elif not isinstance(reflection_insights, list):
            reflection_insights = [reflection_insights] if reflection_insights else []

        # 1. 수정할 신념 또는 판단 규칙 도출
        beliefs_to_update = self._identify_beliefs_to_update(reflection_insights)
        rules_to_update = self._identify_rules_to_update(reflection_insights)

        # 2. CoreBelief 및 Judgment Rule 업데이트
        updated_beliefs = self._update_core_beliefs(beliefs_to_update)
        updated_rules = self._update_judgment_rules(rules_to_update)

        # 3. 행동 패턴 업데이트
        updated_behaviors = self._update_behavior_patterns(reflection_insights)

        # 4. 진화 단계 기록
        evolution_steps = self._record_evolution_steps(
            beliefs_to_update, rules_to_update, updated_behaviors, reflection_insights
        )

        # 5. 데이터 저장
        self._save_data()

        # 6. DuRiThoughtFlow에 기록
        from ..thought_flow.du_ri_thought_flow import DuRiThoughtFlow

        evolution_summary = {
            "beliefs_updated": len(updated_beliefs),
            "rules_updated": len(updated_rules),
            "behaviors_updated": len(updated_behaviors),
            "evolution_steps": len(evolution_steps),
            "timestamp": datetime.now().isoformat(),
        }
        DuRiThoughtFlow.register_stream("self_improvement_sequence", evolution_summary)

        print(
            f"✅ 자기개선 시퀀스 완료: {len(updated_beliefs)}개 신념, {len(updated_rules)}개 규칙, {len(updated_behaviors)}개 행동 패턴 업데이트"
        )

        return {
            "status": "success",
            "beliefs_updated": len(updated_beliefs),
            "rules_updated": len(updated_rules),
            "behaviors_updated": len(updated_behaviors),
            "evolution_steps": len(evolution_steps),
            "evolution_summary": evolution_summary,
        }

    def _identify_beliefs_to_update(self, reflection_insights: List[Any]) -> List[Dict]:
        """수정할 신념들을 도출합니다."""
        beliefs_to_update = []

        if not reflection_insights:
            return beliefs_to_update

        for insight in reflection_insights:
            try:
                # 신뢰도 영향이 큰 통찰만 신념 업데이트 대상으로 선정
                confidence_impact = 0.0
                if hasattr(insight, "confidence_impact"):
                    confidence_impact = getattr(insight, "confidence_impact", 0.0)
                elif isinstance(insight, dict):
                    confidence_impact = insight.get("confidence_impact", 0.0)

                if abs(confidence_impact) > 0.3:
                    belief_update = {
                        "insight_id": (
                            getattr(insight, "judgment_trace_id", "unknown")
                            if hasattr(insight, "judgment_trace_id")
                            else insight.get("judgment_trace_id", "unknown")
                        ),
                        "content": (
                            getattr(insight, "improvement_suggestion", "")
                            if hasattr(insight, "improvement_suggestion")
                            else insight.get("improvement_suggestion", "")
                        ),
                        "confidence_impact": confidence_impact,
                        "priority": abs(confidence_impact),
                    }
                    beliefs_to_update.append(belief_update)
            except Exception as e:
                print(f"신념 업데이트 대상 선정 중 오류: {e}")
                continue

        # 우선순위별 정렬
        beliefs_to_update.sort(key=lambda x: x["priority"], reverse=True)

        return beliefs_to_update

    def _identify_rules_to_update(self, reflection_insights: List[Any]) -> List[Dict]:
        """수정할 판단 규칙들을 도출합니다."""
        rules_to_update = []

        if not reflection_insights:
            return rules_to_update

        for insight in reflection_insights:
            try:
                # 개선 제안이 구체적인 경우만 규칙 업데이트 대상으로 선정
                improvement = ""
                if hasattr(insight, "improvement_suggestion"):
                    improvement = getattr(insight, "improvement_suggestion", "")
                elif isinstance(insight, dict):
                    improvement = insight.get("improvement_suggestion", "")

                if improvement and ";" in improvement:
                    confidence_impact = 0.0
                    if hasattr(insight, "confidence_impact"):
                        confidence_impact = getattr(insight, "confidence_impact", 0.0)
                    elif isinstance(insight, dict):
                        confidence_impact = insight.get("confidence_impact", 0.0)

                    rule_update = {
                        "insight_id": (
                            getattr(insight, "judgment_trace_id", "unknown")
                            if hasattr(insight, "judgment_trace_id")
                            else insight.get("judgment_trace_id", "unknown")
                        ),
                        "condition": (
                            getattr(insight, "analysis", "")
                            if hasattr(insight, "analysis")
                            else insight.get("analysis", "")
                        ),
                        "action": improvement,
                        "confidence_impact": confidence_impact,
                        "priority": abs(confidence_impact),
                    }
                    rules_to_update.append(rule_update)
            except Exception as e:
                print(f"규칙 업데이트 대상 선정 중 오류: {e}")
                continue

        # 우선순위별 정렬
        rules_to_update.sort(key=lambda x: x["priority"], reverse=True)

        return rules_to_update

    def _update_core_beliefs(self, beliefs_to_update: List[Dict]) -> List[str]:
        """핵심 신념을 업데이트합니다."""
        updated_beliefs = []

        for belief_update in beliefs_to_update:
            belief_key = f"belief_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            belief_value = {
                "insight_id": belief_update["insight_id"],
                "content": belief_update["content"],
                "confidence_impact": belief_update["confidence_impact"],
                "created_at": datetime.now().isoformat(),
                "version": "2.0",  # 진화 버전 표시
            }

            self.core_beliefs[belief_key] = belief_value
            updated_beliefs.append(belief_key)

        return updated_beliefs

    def _update_judgment_rules(self, rules_to_update: List[Dict]) -> List[str]:
        """판단 규칙을 업데이트합니다."""
        updated_rules = []

        for rule_update in rules_to_update:
            rule_key = f"rule_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            rule_value = {
                "insight_id": rule_update["insight_id"],
                "condition": rule_update["condition"],
                "action": rule_update["action"],
                "confidence_impact": rule_update["confidence_impact"],
                "created_at": datetime.now().isoformat(),
                "version": "2.0",  # 진화 버전 표시
            }

            self.judgment_rules[rule_key] = rule_value
            updated_rules.append(rule_key)

        return updated_rules

    def _update_behavior_patterns(self, reflection_insights: List[Any]) -> List[str]:
        """행동 패턴을 업데이트합니다."""
        updated_behaviors = []

        if not reflection_insights:
            return updated_behaviors

        for insight in reflection_insights:
            try:
                # 개선 제안을 행동 패턴으로 변환
                improvement = ""
                if hasattr(insight, "improvement_suggestion"):
                    improvement = getattr(insight, "improvement_suggestion", "")
                elif isinstance(insight, dict):
                    improvement = insight.get("improvement_suggestion", "")

                if improvement:
                    confidence_impact = 0.0
                    if hasattr(insight, "confidence_impact"):
                        confidence_impact = getattr(insight, "confidence_impact", 0.0)
                    elif isinstance(insight, dict):
                        confidence_impact = insight.get("confidence_impact", 0.0)

                    behavior_key = (
                        f"behavior_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    )
                    behavior_value = {
                        "insight_id": (
                            getattr(insight, "judgment_trace_id", "unknown")
                            if hasattr(insight, "judgment_trace_id")
                            else insight.get("judgment_trace_id", "unknown")
                        ),
                        "pattern": improvement,
                        "trigger_condition": (
                            getattr(insight, "analysis", "")
                            if hasattr(insight, "analysis")
                            else insight.get("analysis", "")
                        ),
                        "confidence_impact": confidence_impact,
                        "created_at": datetime.now().isoformat(),
                        "version": "2.0",
                    }

                    self.behavior_patterns[behavior_key] = behavior_value
                    updated_behaviors.append(behavior_key)
            except Exception as e:
                print(f"행동 패턴 업데이트 중 오류: {e}")
                continue

        return updated_behaviors

    def _record_evolution_steps(
        self,
        beliefs_to_update: List[Dict],
        rules_to_update: List[Dict],
        updated_behaviors: List[str],
        reflection_insights: List[Any],
    ) -> List[EvolutionStep]:
        """진화 단계들을 기록합니다."""
        evolution_steps = []

        # 신념 업데이트 단계 기록
        if beliefs_to_update:
            step = EvolutionStep(
                timestamp=datetime.now().isoformat(),
                step_type="belief_update",
                description=f"{len(beliefs_to_update)}개 핵심 신념 업데이트",
                impact_score=sum(b["priority"] for b in beliefs_to_update)
                / len(beliefs_to_update),
                previous_state={
                    "beliefs_count": len(self.core_beliefs) - len(beliefs_to_update)
                },
                new_state={"beliefs_count": len(self.core_beliefs)},
                trigger_source="reflection_insights",
            )
            evolution_steps.append(step)
            self.evolution_steps.append(step)

        # 규칙 업데이트 단계 기록
        if rules_to_update:
            step = EvolutionStep(
                timestamp=datetime.now().isoformat(),
                step_type="rule_update",
                description=f"{len(rules_to_update)}개 판단 규칙 업데이트",
                impact_score=sum(r["priority"] for r in rules_to_update)
                / len(rules_to_update),
                previous_state={
                    "rules_count": len(self.judgment_rules) - len(rules_to_update)
                },
                new_state={"rules_count": len(self.judgment_rules)},
                trigger_source="reflection_insights",
            )
            evolution_steps.append(step)
            self.evolution_steps.append(step)

        # 행동 패턴 업데이트 단계 기록
        if updated_behaviors:
            step = EvolutionStep(
                timestamp=datetime.now().isoformat(),
                step_type="behavior_change",
                description=f"{len(updated_behaviors)}개 행동 패턴 업데이트",
                impact_score=0.5,  # 기본 영향도
                previous_state={
                    "behaviors_count": len(self.behavior_patterns)
                    - len(updated_behaviors)
                },
                new_state={"behaviors_count": len(self.behavior_patterns)},
                trigger_source="reflection_insights",
            )
            evolution_steps.append(step)
            self.evolution_steps.append(step)

        return evolution_steps

    def get_evolution_summary(self) -> Dict:
        """진화 요약 정보를 반환합니다."""
        return {
            "total_evolution_steps": len(self.evolution_steps),
            "total_beliefs": len(self.core_beliefs),
            "total_rules": len(self.judgment_rules),
            "total_behaviors": len(self.behavior_patterns),
            "recent_evolution_steps": (
                len(self.evolution_steps[-10:]) if self.evolution_steps else 0
            ),
            "average_impact_score": (
                sum(step.impact_score for step in self.evolution_steps)
                / len(self.evolution_steps)
                if self.evolution_steps
                else 0
            ),
        }

    def apply_updated_beliefs_to_judgment(
        self, context: str, judgment_data: Dict
    ) -> Dict:
        """업데이트된 신념을 바탕으로 판단을 적용합니다."""
        # 최신 신념들을 검토하여 판단에 반영
        relevant_beliefs = []

        for belief_key, belief_value in self.core_beliefs.items():
            # 신념이 판단 맥락과 관련이 있는지 확인
            if self._is_belief_relevant_to_context(belief_value, context):
                relevant_beliefs.append(belief_value)

        # 관련 신념들을 바탕으로 판단 조정
        adjusted_judgment = self._adjust_judgment_with_beliefs(
            judgment_data, relevant_beliefs
        )

        return adjusted_judgment

    def _is_belief_relevant_to_context(self, belief_value: Dict, context: str) -> bool:
        """신념이 주어진 맥락과 관련이 있는지 확인합니다."""
        # 간단한 키워드 매칭 (실제로는 더 정교한 NLP 기법 사용 가능)
        belief_content = belief_value.get("content", "").lower()
        context_lower = context.lower()

        # 공통 키워드가 있는지 확인
        common_words = set(belief_content.split()) & set(context_lower.split())
        return len(common_words) > 0

    def _adjust_judgment_with_beliefs(
        self, judgment_data: Dict, relevant_beliefs: List[Dict]
    ) -> Dict:
        """신념들을 바탕으로 판단을 조정합니다."""
        adjusted_judgment = judgment_data.copy()

        if not relevant_beliefs:
            return adjusted_judgment

        # 신념들의 평균 신뢰도 영향 계산
        total_impact = sum(
            belief.get("confidence_impact", 0.0) for belief in relevant_beliefs
        )
        average_impact = total_impact / len(relevant_beliefs)

        # 판단 신뢰도 조정
        if "confidence_level" in adjusted_judgment:
            current_confidence = adjusted_judgment["confidence_level"]
            adjusted_confidence = max(
                0.0, min(1.0, current_confidence + average_impact * 0.1)
            )
            adjusted_judgment["confidence_level"] = adjusted_confidence

        # 신념 기반 판단 메타데이터 추가
        adjusted_judgment["beliefs_applied"] = len(relevant_beliefs)
        adjusted_judgment["beliefs_impact"] = average_impact

        return adjusted_judgment
