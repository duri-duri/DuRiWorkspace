"""
DuRi AutoRetrospector (자동 회고 시스템)

DuRi의 자동 회고 및 메타 학습 분석 시스템입니다.
"""

import logging
import time
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from duri_core.memory.memory_sync import MemoryType, get_memory_sync
from duri_core.memory.meta_learning_data import (
    ErrorPattern,
    ImprovementSuggestion,
    LearningStrategyUpdate,
    MetaLearningData,
    MetaLearningType,
    PerformancePattern,
    get_meta_learning_data_manager,
)
from duri_core.utils.fallback_handler import get_fallback_handler
from duri_core.utils.log_analyzer import get_log_analyzer

# 기존 시스템 import
from duri_core.utils.performance_monitor import get_performance_monitor

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """분석 결과"""

    analysis_id: str
    analysis_type: str
    confidence: float
    findings: List[str]
    recommendations: List[str]
    performance_impact: float
    analysis_duration: float


class AutoRetrospector:
    """DuRi의 자동 회고 및 메타 학습 분석 시스템"""

    def __init__(self):
        """AutoRetrospector 초기화"""
        self.performance_monitor = get_performance_monitor()
        self.log_analyzer = get_log_analyzer()
        self.fallback_handler = get_fallback_handler()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()

        # 분석 설정
        self.analysis_interval = 3600  # 1시간마다 분석
        self.last_analysis_time = None
        self.analysis_history: List[AnalysisResult] = []

        logger.info("AutoRetrospector 초기화 완료")

    def reflect_on_learning_cycle(
        self, improvement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """학습 사이클 전체에 대한 메타 반성 - 기존 reflect_on_chatgpt_feedback 패턴 활용"""
        try:
            logger.info("🧠 학습 사이클 메타 반성 시작")

            reflection = {
                "timestamp": datetime.now().isoformat(),
                "learning_cycle_data": improvement_result,
                "accepted_criticisms": [],
                "disagreements": [],
                "improvement_proposal": {},
                "self_assessment": {},
                "meta_analysis": {},
            }

            # 학습 약점 분석 (기존 패턴 활용)
            reflection["accepted_criticisms"] = self._analyze_learning_weaknesses(
                improvement_result
            )

            # 학습 전략에 대한 의견 차이 식별
            reflection["disagreements"] = self._identify_learning_disagreements(
                improvement_result
            )

            # 학습 개선안 생성
            reflection["improvement_proposal"] = self._generate_learning_improvements(
                improvement_result
            )

            # 학습 성과 자체 평가
            reflection["self_assessment"] = self._assess_learning_performance(
                improvement_result
            )

            # 메타 분석 결과
            reflection["meta_analysis"] = self._perform_meta_analysis(
                improvement_result
            )

            # 반성 기록 저장
            self.analysis_history.append(
                AnalysisResult(
                    analysis_id=f"learning_cycle_{uuid.uuid4().hex[:8]}",
                    analysis_type="learning_cycle_reflection",
                    confidence=reflection["self_assessment"].get("confidence", 0.0),
                    findings=reflection["accepted_criticisms"],
                    recommendations=reflection["improvement_proposal"].get(
                        "specific_improvements", []
                    ),
                    performance_impact=reflection["self_assessment"].get(
                        "performance_score", 0.0
                    ),
                    analysis_duration=0.0,
                )
            )

            logger.info(
                f"✅ 학습 사이클 메타 반성 완료 - 약점: {len(reflection['accepted_criticisms'])}개, 개선안: {len(reflection['improvement_proposal'].get('specific_improvements', []))}개"
            )
            return reflection

        except Exception as e:
            logger.error(f"❌ 학습 사이클 메타 반성 오류: {e}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "accepted_criticisms": [],
                "disagreements": [],
                "improvement_proposal": {},
                "self_assessment": {"confidence": 0.0, "performance_score": 0.0},
            }

    def _analyze_learning_weaknesses(
        self, improvement_result: Dict[str, Any]
    ) -> List[str]:
        """학습 약점 분석 - 기존 패턴 활용"""
        weaknesses = []

        # 학습 점수 기반 약점 식별
        learning_score = improvement_result.get("learning_score", 0.0)
        if learning_score < 0.5:
            weaknesses.append(f"전체 학습 점수가 낮음 (점수: {learning_score:.3f})")

        # 자율 액션 기반 약점 식별
        autonomous_actions = improvement_result.get("autonomous_actions", [])
        if len(autonomous_actions) < 2:
            weaknesses.append("자율 학습 액션이 부족함")

        # 개선 방향 기반 약점 식별
        improvement_direction = improvement_result.get("improvement_direction", {})
        if improvement_direction.get("needs_optimization"):
            weaknesses.append("성능 최적화가 필요함")
        if improvement_direction.get("needs_adaptation"):
            weaknesses.append("학습 방식 적응이 필요함")
        if improvement_direction.get("needs_restructuring"):
            weaknesses.append("학습 구조 개선이 필요함")

        return weaknesses

    def _identify_learning_disagreements(
        self, improvement_result: Dict[str, Any]
    ) -> List[str]:
        """학습 전략에 대한 의견 차이 식별"""
        disagreements = []

        # 학습 점수와 신뢰도 간의 불일치
        learning_score = improvement_result.get("learning_score", 0.0)
        confidence = improvement_result.get("confidence", 0.0)
        if abs(learning_score - confidence) > 0.3:
            disagreements.append("학습 점수와 신뢰도 간의 불일치가 있습니다")

        # 자율 액션의 효과성에 대한 의견 차이
        autonomous_actions = improvement_result.get("autonomous_actions", [])
        if autonomous_actions:
            impact_scores = [
                action.get("impact_score", 0.0) for action in autonomous_actions
            ]
            avg_impact = sum(impact_scores) / len(impact_scores)
            if avg_impact < 0.5:
                disagreements.append("자율 액션의 예상 효과가 낮습니다")

        return disagreements

    def _generate_learning_improvements(
        self, improvement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """학습 개선안 생성 - 기존 패턴 활용"""
        improvements = {
            "specific_improvements": [],
            "priority": "medium",
            "reasoning": "",
            "code_examples": [],
            "structure_changes": [],
        }

        # 학습 점수 기반 개선안
        learning_score = improvement_result.get("learning_score", 0.0)
        if learning_score < 0.4:
            improvements["priority"] = "critical"
            improvements["specific_improvements"].append(
                "학습 알고리즘 전면 재검토 필요"
            )
        elif learning_score < 0.6:
            improvements["priority"] = "high"
            improvements["specific_improvements"].append("학습 전략 부분적 조정 필요")

        # 자율 액션 기반 개선안
        autonomous_actions = improvement_result.get("autonomous_actions", [])
        for action in autonomous_actions:
            action_type = action.get("action_type", "")
            if action_type == "optimization":
                improvements["specific_improvements"].append(
                    "성능 최적화 알고리즘 강화"
                )
            elif action_type == "adaptation":
                improvements["specific_improvements"].append(
                    "적응적 학습 메커니즘 개선"
                )
            elif action_type == "restructuring":
                improvements["specific_improvements"].append("학습 구조 모듈화 개선")

        # 개선 이유 생성
        improvements["reasoning"] = (
            f"학습 점수 {learning_score:.3f}를 {learning_score + 0.2:.3f}로 향상시키기 위한 개선안"
        )

        return improvements

    def _assess_learning_performance(
        self, improvement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """학습 성과 자체 평가"""
        assessment = {
            "confidence": 0.0,
            "performance_score": 0.0,
            "strengths": [],
            "weaknesses": [],
            "overall_rating": "neutral",
        }

        # 성과 점수 계산
        learning_score = improvement_result.get("learning_score", 0.0)
        confidence = improvement_result.get("confidence", 0.0)
        assessment["performance_score"] = learning_score
        assessment["confidence"] = confidence

        # 강점 분석
        if learning_score > 0.7:
            assessment["strengths"].append("높은 학습 성과 달성")
            assessment["overall_rating"] = "excellent"
        elif learning_score > 0.5:
            assessment["strengths"].append("안정적인 학습 진행")
            assessment["overall_rating"] = "good"
        else:
            assessment["weaknesses"].append("학습 성과 개선 필요")
            assessment["overall_rating"] = "needs_improvement"

        # 자율성 평가
        autonomous_actions = improvement_result.get("autonomous_actions", [])
        if len(autonomous_actions) > 2:
            assessment["strengths"].append("높은 자율 학습 능력")
        else:
            assessment["weaknesses"].append("자율 학습 능력 향상 필요")

        return assessment

    def _perform_meta_analysis(
        self, improvement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메타 분석 수행"""
        return {
            "learning_pattern": "autonomous_improvement",
            "cycle_efficiency": improvement_result.get("learning_score", 0.0),
            "autonomous_decision_quality": len(
                improvement_result.get("autonomous_actions", [])
            ),
            "improvement_potential": 1.0
            - improvement_result.get("learning_score", 0.0),
        }

    def should_run_analysis(self) -> bool:
        """분석을 실행해야 하는지 확인합니다."""
        if self.last_analysis_time is None:
            return True

        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last.total_seconds() >= self.analysis_interval

    def get_analysis_history(self, limit: int = 10) -> List[AnalysisResult]:
        """분석 기록을 반환합니다."""
        return self.analysis_history[-limit:]

    def get_auto_retrospector(self) -> "AutoRetrospector":
        """AutoRetrospector 인스턴스를 반환합니다."""
        return self


def get_auto_retrospector() -> AutoRetrospector:
    """AutoRetrospector 인스턴스를 반환합니다."""
    return AutoRetrospector()
