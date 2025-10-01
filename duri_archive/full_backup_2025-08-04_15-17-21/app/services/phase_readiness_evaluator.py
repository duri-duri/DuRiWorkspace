#!/usr/bin/env python3
"""
PhaseReadinessEvaluator - Phase 12+
단계 준비도 평가 시스템

목적:
- 현재 Phase의 완성도 평가
- 다음 Phase 진입 준비도 검토
- 안전한 진화 결정 지원
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReadinessLevel(Enum):
    """준비도 수준"""

    NOT_READY = "not_ready"
    PARTIALLY_READY = "partially_ready"
    READY = "ready"
    EXCELLENT = "excellent"


class EvaluationCriteria(Enum):
    """평가 기준"""

    FUNCTIONALITY = "functionality"
    STABILITY = "stability"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"


@dataclass
class PhaseAssessment:
    """단계 평가"""

    id: str
    phase_number: int
    assessment_date: datetime
    readiness_level: ReadinessLevel
    completion_percentage: float
    critical_issues: List[str]
    minor_issues: List[str]
    strengths: List[str]
    recommendations: List[str]
    confidence_score: float


@dataclass
class EvolutionDecision:
    """진화 결정"""

    id: str
    current_phase: int
    target_phase: int
    decision_type: str  # "proceed", "wait", "revert"
    reasoning: str
    risk_assessment: Dict[str, Any]
    required_actions: List[str]
    estimated_effort: str
    timestamp: datetime


class PhaseReadinessEvaluator:
    """단계 준비도 평가 시스템"""

    def __init__(self):
        self.assessments: List[PhaseAssessment] = []
        self.evolution_decisions: List[EvolutionDecision] = []
        self.phase_requirements: Dict[int, Dict[str, Any]] = {}

        # Phase별 요구사항 정의
        self._initialize_phase_requirements()

        logger.info("PhaseReadinessEvaluator 초기화 완료")

    def _initialize_phase_requirements(self):
        """Phase별 요구사항 초기화"""
        self.phase_requirements = {
            11: {
                "required_systems": [
                    "TextBasedLearningSystem",
                    "SubtitleBasedLearningSystem",
                    "LLMInterface",
                    "BasicConversationSystem",
                    "FamilyConversationPrecisionSystem",
                    "DevelopmentalThinkingConversationSystem",
                    "SelfModelEnhancer",
                    "EnhancedEthicalSystem",
                    "SelfExplanationBooster",
                ],
                "min_completion_percentage": 90.0,
                "critical_systems": ["SelfExplanationBooster", "EnhancedEthicalSystem"],
                "integration_requirements": [
                    "text_llm",
                    "subtitle_conversation",
                    "self_ethical",
                ],
            },
            12: {
                "required_systems": [
                    "EthicalConversationSystem",
                    "NarrativeMemoryEnhancer",
                    "EmotionalConversationSystem",
                    "ChatGPTLearningInterface",
                    "MultiAILearningSystem",
                ],
                "min_completion_percentage": 80.0,
                "critical_systems": [
                    "EthicalConversationSystem",
                    "NarrativeMemoryEnhancer",
                ],
                "integration_requirements": [
                    "ethical_conversation",
                    "narrative_emotional",
                    "multi_ai_learning",
                ],
            },
        }

    def evaluate_phase_readiness(
        self, phase_number: int, current_systems: Dict[str, Any]
    ) -> PhaseAssessment:
        """단계 준비도 평가"""
        assessment_id = f"phase_assessment_{phase_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        if phase_number not in self.phase_requirements:
            raise ValueError(f"Phase {phase_number}의 요구사항이 정의되지 않았습니다.")

        requirements = self.phase_requirements[phase_number]

        # 시스템 완성도 평가
        completion_percentage = self._calculate_completion_percentage(
            current_systems, requirements
        )

        # 문제점 식별
        critical_issues = self._identify_critical_issues(current_systems, requirements)
        minor_issues = self._identify_minor_issues(current_systems, requirements)

        # 강점 식별
        strengths = self._identify_strengths(current_systems, requirements)

        # 권장사항 생성
        recommendations = self._generate_recommendations(
            critical_issues, minor_issues, completion_percentage
        )

        # 준비도 수준 결정
        readiness_level = self._determine_readiness_level(
            completion_percentage, critical_issues
        )

        # 신뢰도 점수 계산
        confidence_score = self._calculate_confidence_score(
            completion_percentage, len(critical_issues), len(minor_issues)
        )

        assessment = PhaseAssessment(
            id=assessment_id,
            phase_number=phase_number,
            assessment_date=datetime.now(),
            readiness_level=readiness_level,
            completion_percentage=completion_percentage,
            critical_issues=critical_issues,
            minor_issues=minor_issues,
            strengths=strengths,
            recommendations=recommendations,
            confidence_score=confidence_score,
        )

        self.assessments.append(assessment)
        logger.info(f"Phase {phase_number} 준비도 평가 완료: {readiness_level.value}")

        return assessment

    def _calculate_completion_percentage(
        self, current_systems: Dict[str, Any], requirements: Dict[str, Any]
    ) -> float:
        """완성도 백분율 계산"""
        required_systems = requirements.get("required_systems", [])
        critical_systems = requirements.get("critical_systems", [])

        if not required_systems:
            return 0.0

        # 시스템별 가중치 계산
        total_weight = len(required_systems)
        critical_weight = len(critical_systems) * 2  # 중요 시스템은 2배 가중치

        completed_weight = 0

        for system in required_systems:
            if system in current_systems:
                system_status = current_systems[system]
                if system_status.get("status") == "completed":
                    if system in critical_systems:
                        completed_weight += 2
                    else:
                        completed_weight += 1

        completion_percentage = (
            completed_weight / (total_weight + critical_weight)
        ) * 100
        return min(100.0, completion_percentage)

    def _identify_critical_issues(
        self, current_systems: Dict[str, Any], requirements: Dict[str, Any]
    ) -> List[str]:
        """중요 이슈 식별"""
        issues = []
        critical_systems = requirements.get("critical_systems", [])

        for system in critical_systems:
            if system not in current_systems:
                issues.append(f"중요 시스템 '{system}'이 구현되지 않았습니다.")
            elif current_systems[system].get("status") != "completed":
                issues.append(f"중요 시스템 '{system}'이 완료되지 않았습니다.")

        # 통합 요구사항 체크
        integration_requirements = requirements.get("integration_requirements", [])
        for integration in integration_requirements:
            if not self._check_integration_status(integration, current_systems):
                issues.append(f"통합 요구사항 '{integration}'이 충족되지 않았습니다.")

        return issues

    def _identify_minor_issues(
        self, current_systems: Dict[str, Any], requirements: Dict[str, Any]
    ) -> List[str]:
        """사소한 이슈 식별"""
        issues = []
        required_systems = requirements.get("required_systems", [])

        for system in required_systems:
            if system not in current_systems:
                issues.append(f"시스템 '{system}'이 구현되지 않았습니다.")
            elif current_systems[system].get("status") != "completed":
                issues.append(f"시스템 '{system}'이 완료되지 않았습니다.")
            elif current_systems[system].get("test_coverage", 0) < 80:
                issues.append(f"시스템 '{system}'의 테스트 커버리지가 부족합니다.")

        return issues

    def _identify_strengths(
        self, current_systems: Dict[str, Any], requirements: Dict[str, Any]
    ) -> List[str]:
        """강점 식별"""
        strengths = []

        # 완료된 시스템 수
        completed_systems = [
            s for s in current_systems.values() if s.get("status") == "completed"
        ]
        if len(completed_systems) > 0:
            strengths.append(f"{len(completed_systems)}개 시스템이 완료되었습니다.")

        # 높은 테스트 커버리지
        high_coverage_systems = [
            s for s in current_systems.values() if s.get("test_coverage", 0) >= 90
        ]
        if len(high_coverage_systems) > 0:
            strengths.append(
                f"{len(high_coverage_systems)}개 시스템이 높은 테스트 커버리지를 보유합니다."
            )

        # 안정적인 시스템
        stable_systems = [
            s for s in current_systems.values() if s.get("stability_score", 0) >= 0.8
        ]
        if len(stable_systems) > 0:
            strengths.append(f"{len(stable_systems)}개 시스템이 안정적으로 작동합니다.")

        return strengths if strengths else ["특별한 강점이 식별되지 않았습니다."]

    def _generate_recommendations(
        self,
        critical_issues: List[str],
        minor_issues: List[str],
        completion_percentage: float,
    ) -> List[str]:
        """권장사항 생성"""
        recommendations = []

        # 중요 이슈 기반 권장사항
        if critical_issues:
            recommendations.append("중요 이슈를 우선적으로 해결해야 합니다.")
            recommendations.append("중요 시스템의 완성을 최우선으로 진행하세요.")

        # 완성도 기반 권장사항
        if completion_percentage < 80:
            recommendations.append("완성도를 80% 이상으로 높여야 합니다.")
        elif completion_percentage < 90:
            recommendations.append("완성도를 90% 이상으로 높이는 것이 권장됩니다.")

        # 사소한 이슈 기반 권장사항
        if minor_issues:
            recommendations.append("사소한 이슈들을 해결하여 품질을 향상시키세요.")

        # 테스트 관련 권장사항
        if completion_percentage >= 90:
            recommendations.append("포괄적인 통합 테스트를 수행하세요.")
            recommendations.append("다음 단계 진입을 위한 최종 검토를 진행하세요.")

        return (
            recommendations
            if recommendations
            else ["현재 상태로 다음 단계 진입이 가능합니다."]
        )

    def _determine_readiness_level(
        self, completion_percentage: float, critical_issues: List[str]
    ) -> ReadinessLevel:
        """준비도 수준 결정"""
        if critical_issues:
            return ReadinessLevel.NOT_READY
        elif completion_percentage < 70:
            return ReadinessLevel.NOT_READY
        elif completion_percentage < 80:
            return ReadinessLevel.PARTIALLY_READY
        elif completion_percentage < 90:
            return ReadinessLevel.READY
        else:
            return ReadinessLevel.EXCELLENT

    def _calculate_confidence_score(
        self,
        completion_percentage: float,
        critical_issues_count: int,
        minor_issues_count: int,
    ) -> float:
        """신뢰도 점수 계산"""
        base_score = completion_percentage / 100

        # 중요 이슈에 따른 감점
        critical_penalty = critical_issues_count * 0.2

        # 사소한 이슈에 따른 감점
        minor_penalty = minor_issues_count * 0.05

        final_score = base_score - critical_penalty - minor_penalty
        return max(0.0, min(1.0, final_score))

    def _check_integration_status(
        self, integration_name: str, current_systems: Dict[str, Any]
    ) -> bool:
        """통합 상태 확인"""
        # 실제 구현에서는 더 정교한 통합 검사 로직이 필요
        integration_checks = {
            "text_llm": lambda: "TextBasedLearningSystem" in current_systems
            and "LLMInterface" in current_systems,
            "subtitle_conversation": lambda: "SubtitleBasedLearningSystem"
            in current_systems
            and "BasicConversationSystem" in current_systems,
            "self_ethical": lambda: "SelfExplanationBooster" in current_systems
            and "EnhancedEthicalSystem" in current_systems,
            "ethical_conversation": lambda: "EthicalConversationSystem"
            in current_systems,
            "narrative_emotional": lambda: "NarrativeMemoryEnhancer" in current_systems
            and "EmotionalConversationSystem" in current_systems,
            "multi_ai_learning": lambda: "MultiAILearningSystem" in current_systems,
        }

        check_function = integration_checks.get(integration_name, lambda: False)
        return check_function()

    def make_evolution_decision(
        self, current_phase: int, target_phase: int, assessment: PhaseAssessment
    ) -> EvolutionDecision:
        """진화 결정"""
        decision_id = f"evolution_decision_{current_phase}_to_{target_phase}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 결정 로직
        if assessment.readiness_level == ReadinessLevel.NOT_READY:
            decision_type = "wait"
            reasoning = "준비도가 부족하여 대기해야 합니다."
            required_actions = ["중요 이슈 해결", "완성도 향상"]
            estimated_effort = "2-3일"
        elif assessment.readiness_level == ReadinessLevel.PARTIALLY_READY:
            decision_type = "wait"
            reasoning = "부분적으로 준비되었지만 추가 작업이 필요합니다."
            required_actions = ["사소한 이슈 해결", "테스트 강화"]
            estimated_effort = "1-2일"
        elif assessment.readiness_level == ReadinessLevel.READY:
            decision_type = "proceed"
            reasoning = "준비도가 충분하여 다음 단계로 진행할 수 있습니다."
            required_actions = ["최종 검토", "통합 테스트"]
            estimated_effort = "0.5-1일"
        else:  # EXCELLENT
            decision_type = "proceed"
            reasoning = "준비도가 우수하여 즉시 다음 단계로 진행할 수 있습니다."
            required_actions = ["빠른 검토", "진행"]
            estimated_effort = "0.5일"

        # 위험도 평가
        risk_assessment = {
            "technical_risk": (
                "low"
                if assessment.readiness_level
                in [ReadinessLevel.READY, ReadinessLevel.EXCELLENT]
                else "medium"
            ),
            "stability_risk": "low" if len(assessment.critical_issues) == 0 else "high",
            "integration_risk": (
                "low" if assessment.completion_percentage >= 90 else "medium"
            ),
        }

        decision = EvolutionDecision(
            id=decision_id,
            current_phase=current_phase,
            target_phase=target_phase,
            decision_type=decision_type,
            reasoning=reasoning,
            risk_assessment=risk_assessment,
            required_actions=required_actions,
            estimated_effort=estimated_effort,
            timestamp=datetime.now(),
        )

        self.evolution_decisions.append(decision)
        logger.info(
            f"진화 결정 생성: {current_phase} → {target_phase} ({decision_type})"
        )

        return decision

    def get_evaluation_statistics(self) -> Dict[str, Any]:
        """평가 통계 제공"""
        total_assessments = len(self.assessments)
        total_decisions = len(self.evolution_decisions)

        # 준비도 수준별 통계
        readiness_stats = {}
        for level in ReadinessLevel:
            level_assessments = [
                a for a in self.assessments if a.readiness_level == level
            ]
            readiness_stats[level.value] = len(level_assessments)

        # 결정 유형별 통계
        decision_stats = {}
        for decision in self.evolution_decisions:
            decision_type = decision.decision_type
            if decision_type not in decision_stats:
                decision_stats[decision_type] = 0
            decision_stats[decision_type] += 1

        statistics = {
            "total_assessments": total_assessments,
            "total_decisions": total_decisions,
            "readiness_statistics": readiness_stats,
            "decision_statistics": decision_stats,
            "last_updated": datetime.now().isoformat(),
        }

        logger.info("평가 통계 생성 완료")
        return statistics

    def export_evaluation_data(self) -> Dict[str, Any]:
        """평가 데이터 내보내기"""
        return {
            "assessments": [asdict(a) for a in self.assessments],
            "evolution_decisions": [asdict(d) for d in self.evolution_decisions],
            "phase_requirements": self.phase_requirements,
            "export_date": datetime.now().isoformat(),
        }


# 테스트 함수
def test_phase_readiness_evaluator():
    """단계 준비도 평가 시스템 테스트"""
    print("📊 PhaseReadinessEvaluator 테스트 시작...")

    evaluator = PhaseReadinessEvaluator()

    # 1. Phase 11 준비도 평가
    current_systems = {
        "TextBasedLearningSystem": {
            "status": "completed",
            "test_coverage": 95,
            "stability_score": 0.9,
        },
        "SubtitleBasedLearningSystem": {
            "status": "completed",
            "test_coverage": 92,
            "stability_score": 0.85,
        },
        "LLMInterface": {
            "status": "completed",
            "test_coverage": 88,
            "stability_score": 0.8,
        },
        "BasicConversationSystem": {
            "status": "completed",
            "test_coverage": 90,
            "stability_score": 0.85,
        },
        "FamilyConversationPrecisionSystem": {
            "status": "completed",
            "test_coverage": 87,
            "stability_score": 0.8,
        },
        "DevelopmentalThinkingConversationSystem": {
            "status": "completed",
            "test_coverage": 85,
            "stability_score": 0.8,
        },
        "SelfModelEnhancer": {
            "status": "completed",
            "test_coverage": 93,
            "stability_score": 0.9,
        },
        "EnhancedEthicalSystem": {
            "status": "completed",
            "test_coverage": 91,
            "stability_score": 0.85,
        },
        "SelfExplanationBooster": {
            "status": "completed",
            "test_coverage": 89,
            "stability_score": 0.85,
        },
    }

    assessment = evaluator.evaluate_phase_readiness(11, current_systems)
    print(f"✅ Phase 11 준비도 평가: {assessment.readiness_level.value}")
    print(f"   완성도: {assessment.completion_percentage:.1f}%")
    print(f"   신뢰도: {assessment.confidence_score:.2f}")
    print(f"   중요 이슈: {len(assessment.critical_issues)}개")
    print(f"   사소한 이슈: {len(assessment.minor_issues)}개")

    # 2. 진화 결정
    evolution_decision = evaluator.make_evolution_decision(11, 12, assessment)
    print(f"✅ 진화 결정: {evolution_decision.decision_type}")
    print(f"   이유: {evolution_decision.reasoning}")
    print(f"   예상 노력: {evolution_decision.estimated_effort}")
    print(f"   위험도: {evolution_decision.risk_assessment}")

    # 3. 통계
    statistics = evaluator.get_evaluation_statistics()
    print(
        f"✅ 평가 통계: {statistics['total_assessments']}개 평가, {statistics['total_decisions']}개 결정"
    )
    print(f"   준비도 통계: {statistics['readiness_statistics']}")
    print(f"   결정 통계: {statistics['decision_statistics']}")

    # 4. 데이터 내보내기
    export_data = evaluator.export_evaluation_data()
    print(f"✅ 평가 데이터 내보내기: {len(export_data['assessments'])}개 평가")

    print("🎉 PhaseReadinessEvaluator 테스트 완료!")


if __name__ == "__main__":
    test_phase_readiness_evaluator()
