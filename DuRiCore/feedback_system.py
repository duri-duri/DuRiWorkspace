#!/usr/bin/env python3
"""
DuRiCore Phase 5.5 - 피드백 시스템
행동 결과 평가, 학습, 개선점 도출 통합 시스템
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """피드백 타입 열거형"""

    POSITIVE = "positive"  # 긍정적 피드백
    NEGATIVE = "negative"  # 부정적 피드백
    NEUTRAL = "neutral"  # 중립적 피드백
    CONSTRUCTIVE = "constructive"  # 건설적 피드백


class LearningType(Enum):
    """학습 타입 열거형"""

    REINFORCEMENT = "reinforcement"  # 강화 학습
    CORRECTIVE = "corrective"  # 수정 학습
    ADAPTIVE = "adaptive"  # 적응 학습
    INNOVATIVE = "innovative"  # 혁신 학습


@dataclass
class FeedbackResult:
    """피드백 결과"""

    feedback_type: FeedbackType
    evaluation_score: float
    learning_points: List[str]
    improvement_suggestions: List[str]
    next_actions: List[str]
    confidence: float
    created_at: datetime


@dataclass
class LearningResult:
    """학습 결과"""

    learning_type: LearningType
    knowledge_gained: List[str]
    skill_improvement: Dict[str, float]
    behavior_change: List[str]
    adaptation_level: float
    innovation_score: float
    created_at: datetime


@dataclass
class ImprovementPlan:
    """개선 계획"""

    improvement_id: str
    priority: float
    description: str
    implementation_steps: List[str]
    expected_impact: Dict[str, float]
    timeline: float
    resources_needed: List[str]
    success_metrics: List[str]
    created_at: datetime


class FeedbackSystem:
    """피드백 시스템"""

    def __init__(self):
        self.evaluator = FeedbackEvaluator()
        self.learner = LearningEngine()
        self.improvement_planner = ImprovementPlanner()

        # 피드백 임계값
        self.positive_threshold = 0.7
        self.negative_threshold = 0.3
        self.learning_threshold = 0.6

        # 성능 설정
        self.max_evaluation_time = 3.0  # 초
        self.max_learning_time = 5.0  # 초

        logger.info("피드백 시스템 초기화 완료")

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 처리 (통합 루프용)"""
        try:
            # 행동 결과에서 피드백 정보 추출
            action_data = input_data.get("data", {})
            action_result = action_data.get("action_result", {})
            performance_metrics = action_data.get("performance_metrics", {})  # noqa: F841

            # 피드백 생성
            feedback_result = await self.feedback(action_result)

            # 학습 수행
            learning_result = await self.learn_from_result(action_result)

            # 개선점 도출
            improvement_plan = await self.identify_improvements(feedback_result)

            return {
                "status": "success",
                "feedback_result": feedback_result,
                "learning_result": learning_result,
                "improvement_plan": improvement_plan,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"피드백 시스템 입력 처리 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def feedback(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """실제 피드백 로직 (오케스트레이터 호출용) - 실제 기능 구현"""
        try:
            logger.info("🔄 실제 피드백 로직 실행")

            # 1. 실제 결과 평가
            evaluation = self._real_evaluate_result(action_result)

            # 2. 실제 학습
            learning_result = self._real_learn_from_result(action_result)

            # 3. 실제 개선점 도출
            improvements = self._real_identify_improvements(evaluation)

            return {
                "phase": "feedback",
                "status": "success",
                "feedback": evaluation.get("feedback_type", "neutral"),
                "learning": learning_result.get("learning_type", "corrective"),
                "evaluation_score": evaluation.get("evaluation_score", 0.5),
                "learning_points": evaluation.get("learning_points", []),
                "improvement_suggestions": evaluation.get("improvement_suggestions", []),
                "next_actions": evaluation.get("next_actions", []),
                "confidence": evaluation.get("confidence", 0.5),
                "evaluation": evaluation,
                "learning_result": learning_result,
                "improvements": improvements,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ 피드백 로직 실행 실패: {e}")
            return {
                "phase": "feedback",
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def main(self) -> Dict[str, Any]:
        """메인 함수 (오케스트레이터 호출용)"""
        try:
            logger.info("🚀 피드백 시스템 메인 함수 실행")

            # 기본 행동 결과로 피드백 실행
            action_result = {
                "action": "system_optimization",
                "result": {"success": True, "performance_improvement": 0.15},
                "effectiveness_score": 0.8,
                "efficiency_score": 0.75,
                "learning_points": ["성능 최적화 성공", "리소스 사용량 감소"],
                "next_actions": ["모니터링 강화", "추가 최적화"],
            }

            return await self.feedback(action_result)

        except Exception as e:
            logger.error(f"❌ 피드백 시스템 메인 함수 실패: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def evaluate_result(self, action_result: Dict[str, Any]) -> FeedbackResult:
        """결과 평가"""
        try:
            return await self.evaluator.evaluate(action_result)
        except Exception as e:
            logger.error(f"결과 평가 실패: {e}")
            raise

    async def learn_from_result(self, action_result: Dict[str, Any]) -> LearningResult:
        """결과로부터 학습"""
        try:
            return await self.learner.learn(action_result)
        except Exception as e:
            logger.error(f"학습 실패: {e}")
            raise

    async def identify_improvements(self, feedback_result: FeedbackResult) -> ImprovementPlan:
        """개선점 도출"""
        try:
            return await self.improvement_planner.create_plan(feedback_result)
        except Exception as e:
            logger.error(f"개선점 도출 실패: {e}")
            raise

    def _real_evaluate_result(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """실제 결과 평가"""
        try:
            effectiveness_score = action_result.get("effectiveness_score", 0.0)
            efficiency_score = action_result.get("efficiency_score", 0.0)
            success = action_result.get("success", False)  # noqa: F841

            # 종합 평가 점수 계산
            overall_score = (effectiveness_score * 0.6) + (efficiency_score * 0.4)

            # 피드백 타입 결정
            if overall_score >= 0.8:
                feedback_type = "positive"
            elif overall_score >= 0.6:
                feedback_type = "constructive"
            elif overall_score >= 0.4:
                feedback_type = "neutral"
            else:
                feedback_type = "negative"

            # 학습 포인트 추출
            learning_points = self._extract_learning_points_real(action_result)

            # 개선 제안 생성
            improvement_suggestions = self._generate_improvement_suggestions_real(overall_score, action_result)

            # 다음 행동 제안
            next_actions = self._suggest_next_actions_real(overall_score, action_result)

            # 신뢰도 계산
            confidence = self._calculate_confidence_real(action_result)

            return {
                "feedback_type": feedback_type,
                "evaluation_score": overall_score,
                "learning_points": learning_points,
                "improvement_suggestions": improvement_suggestions,
                "next_actions": next_actions,
                "confidence": confidence,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"결과 평가 오류: {e}")
            return {
                "feedback_type": "neutral",
                "evaluation_score": 0.5,
                "learning_points": ["평가 오류 발생"],
                "improvement_suggestions": ["시스템 안정성 개선 필요"],
                "next_actions": ["wait", "reconsider"],
                "confidence": 0.3,
                "created_at": datetime.now().isoformat(),
            }

    def _real_learn_from_result(self, action_result: Dict[str, Any]) -> Dict[str, Any]:
        """실제 결과로부터 학습"""
        try:
            effectiveness_score = action_result.get("effectiveness_score", 0.0)
            efficiency_score = action_result.get("efficiency_score", 0.0)
            success = action_result.get("success", False)  # noqa: F841

            # 학습 타입 결정
            if effectiveness_score > 0.8 and efficiency_score > 0.8:
                learning_type = "reinforcement"
            elif effectiveness_score < 0.5 or efficiency_score < 0.5:
                learning_type = "corrective"
            elif effectiveness_score > 0.7 or efficiency_score > 0.7:
                learning_type = "adaptive"
            else:
                learning_type = "innovative"

            # 획득한 지식
            knowledge_gained = self._extract_knowledge_real(action_result)

            # 기술 개선
            skill_improvement = self._calculate_skill_improvement_real(action_result)

            # 행동 변화
            behavior_change = self._identify_behavior_change_real(action_result)

            # 적응 수준
            adaptation_level = self._calculate_adaptation_level_real(action_result)

            # 혁신 점수
            innovation_score = self._calculate_innovation_score_real(action_result)

            return {
                "learning_type": learning_type,
                "knowledge_gained": knowledge_gained,
                "skill_improvement": skill_improvement,
                "behavior_change": behavior_change,
                "adaptation_level": adaptation_level,
                "innovation_score": innovation_score,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"학습 오류: {e}")
            return {
                "learning_type": "corrective",
                "knowledge_gained": ["오류 상황 처리 방법"],
                "skill_improvement": {"error_handling": 0.1},
                "behavior_change": ["오류 대응 강화"],
                "adaptation_level": 0.2,
                "innovation_score": 0.1,
                "created_at": datetime.now().isoformat(),
            }

    def _real_identify_improvements(self, feedback_result: Dict[str, Any]) -> Dict[str, Any]:
        """실제 개선점 도출"""
        try:
            evaluation_score = feedback_result.get("evaluation_score", 0.5)
            feedback_type = feedback_result.get("feedback_type", "neutral")

            # 우선순위 계산
            priority = self._calculate_improvement_priority_real(evaluation_score, feedback_type)

            # 개선 설명
            description = self._generate_improvement_description_real(evaluation_score, feedback_type)

            # 구현 단계
            implementation_steps = self._generate_implementation_steps_real(evaluation_score, feedback_type)

            # 예상 영향
            expected_impact = self._calculate_expected_impact_real(evaluation_score, feedback_type)

            # 타임라인
            timeline = self._estimate_timeline_real(evaluation_score, feedback_type)

            # 필요 리소스
            resources_needed = self._identify_resources_needed_real(evaluation_score, feedback_type)

            # 성공 지표
            success_metrics = self._define_success_metrics_real(evaluation_score, feedback_type)

            return {
                "improvement_id": f"improvement_{int(time.time())}",
                "priority": priority,
                "description": description,
                "implementation_steps": implementation_steps,
                "expected_impact": expected_impact,
                "timeline": timeline,
                "resources_needed": resources_needed,
                "success_metrics": success_metrics,
                "created_at": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"개선점 도출 오류: {e}")
            return {
                "improvement_id": f"error_{int(time.time())}",
                "priority": 0.5,
                "description": "시스템 안정성 개선",
                "implementation_steps": ["오류 처리 강화", "로깅 개선"],
                "expected_impact": {"stability": 0.3, "reliability": 0.2},
                "timeline": 1.0,
                "resources_needed": ["cpu", "memory"],
                "success_metrics": ["오류 감소", "안정성 향상"],
                "created_at": datetime.now().isoformat(),
            }

    def _extract_learning_points_real(self, action_result: Dict[str, Any]) -> List[str]:
        """실제 학습 포인트 추출"""
        learning_points = []

        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)
        success = action_result.get("success", False)

        if success:
            learning_points.append("성공적인 행동 패턴 확인")

        if effectiveness_score > 0.8:
            learning_points.append("효과적인 전략 발견")

        if efficiency_score > 0.8:
            learning_points.append("효율적인 실행 방법 발견")

        if effectiveness_score < 0.5:
            learning_points.append("효과성 개선 필요")

        if efficiency_score < 0.5:
            learning_points.append("효율성 개선 필요")

        if not learning_points:
            learning_points.append("기본 학습 완료")

        return learning_points

    def _generate_improvement_suggestions_real(self, overall_score: float, action_result: Dict[str, Any]) -> List[str]:
        """실제 개선 제안 생성"""
        suggestions = []

        if overall_score < 0.5:
            suggestions.extend(["전략적 접근 방식 개선", "실행 방법 재검토"])
        elif overall_score < 0.7:
            suggestions.extend(["효과성 개선", "효율성 최적화"])
        elif overall_score < 0.8:
            suggestions.append("점진적 개선")
        else:
            suggestions.append("현재 수준 유지")

        return suggestions

    def _suggest_next_actions_real(self, overall_score: float, action_result: Dict[str, Any]) -> List[str]:
        """실제 다음 행동 제안"""
        next_actions = []

        if overall_score > 0.8:
            next_actions.extend(["proceed", "optimize", "expand"])
        elif overall_score > 0.6:
            next_actions.extend(["proceed", "monitor"])
        elif overall_score > 0.4:
            next_actions.extend(["reconsider", "adjust"])
        else:
            next_actions.extend(["reconsider", "escalate"])

        return next_actions

    def _calculate_confidence_real(self, action_result: Dict[str, Any]) -> float:
        """실제 신뢰도 계산"""
        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)

        # 기본 신뢰도
        base_confidence = (effectiveness_score + efficiency_score) / 2

        # 성공 여부에 따른 조정
        if action_result.get("success", False):
            base_confidence += 0.1

        return min(1.0, max(0.0, base_confidence))

    def _extract_knowledge_real(self, action_result: Dict[str, Any]) -> List[str]:
        """실제 지식 추출"""
        knowledge = []

        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)

        if effectiveness_score > 0.7:
            knowledge.append("효과적인 전략 패턴")

        if efficiency_score > 0.7:
            knowledge.append("효율적인 실행 방법")

        if action_result.get("success", False):
            knowledge.append("성공적인 행동 패턴")

        if not knowledge:
            knowledge.append("기본 행동 지식")

        return knowledge

    def _calculate_skill_improvement_real(self, action_result: Dict[str, Any]) -> Dict[str, float]:
        """실제 기술 개선 계산"""
        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)

        improvements = {}

        if effectiveness_score > 0.7:
            improvements["strategic_thinking"] = effectiveness_score * 0.1
        if efficiency_score > 0.7:
            improvements["execution_efficiency"] = efficiency_score * 0.1

        if not improvements:
            improvements["basic_skills"] = 0.05

        return improvements

    def _identify_behavior_change_real(self, action_result: Dict[str, Any]) -> List[str]:
        """실제 행동 변화 식별"""
        changes = []

        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)

        if effectiveness_score > 0.8:
            changes.append("더 효과적인 전략 채택")

        if efficiency_score > 0.8:
            changes.append("더 효율적인 실행 방법 채택")

        if not changes:
            changes.append("기본 행동 패턴 유지")

        return changes

    def _calculate_adaptation_level_real(self, action_result: Dict[str, Any]) -> float:
        """실제 적응 수준 계산"""
        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)

        # 적응 수준은 효과성과 효율성의 평균
        adaptation_level = (effectiveness_score + efficiency_score) / 2

        return min(1.0, max(0.0, adaptation_level))

    def _calculate_innovation_score_real(self, action_result: Dict[str, Any]) -> float:
        """실제 혁신 점수 계산"""
        effectiveness_score = action_result.get("effectiveness_score", 0.0)
        efficiency_score = action_result.get("efficiency_score", 0.0)

        # 혁신 점수는 높은 성과에서 더 높음
        if effectiveness_score > 0.8 and efficiency_score > 0.8:
            innovation_score = 0.9
        elif effectiveness_score > 0.7 or efficiency_score > 0.7:
            innovation_score = 0.7
        else:
            innovation_score = 0.3

        return innovation_score

    def _calculate_improvement_priority_real(self, evaluation_score: float, feedback_type: str) -> float:
        """실제 개선 우선순위 계산"""
        if feedback_type == "negative":
            return 0.9
        elif feedback_type == "neutral":
            return 0.6
        elif feedback_type == "constructive":
            return 0.4
        else:  # positive
            return 0.2

    def _generate_improvement_description_real(self, evaluation_score: float, feedback_type: str) -> str:
        """실제 개선 설명 생성 - 판단 로직 기반 동적 생성"""
        # 컨텍스트 분석
        context = getattr(self, "current_context", {})
        recent_failures = context.get("recent_failures", 0)
        system_performance = context.get("system_performance", 0.5)
        improvement_history = context.get("improvement_history", [])

        if feedback_type == "negative":
            if recent_failures > 3:
                return "연속적인 실패로 인한 긴급한 개선이 필요한 상황"
            elif system_performance < 0.3:
                return "시스템 성능 저하로 인한 긴급한 개선이 필요한 상황"
            else:
                return "긴급한 개선이 필요한 상황"
        elif feedback_type == "neutral":
            if len(improvement_history) > 0 and improvement_history[-1].get("success", False):
                return "이전 개선 효과를 바탕으로 한 점진적 개선이 필요한 상황"
            else:
                return "점진적 개선이 필요한 상황"
        elif feedback_type == "constructive":
            if system_performance > 0.7:
                return "높은 성능 기반의 건설적 개선이 가능한 상황"
            else:
                return "건설적 개선이 가능한 상황"
        else:  # positive
            if system_performance > 0.8:
                return "우수한 성능을 바탕으로 한 현재 수준 유지 및 확장"
            else:
                return "현재 수준 유지 및 확장"

    def _generate_implementation_steps_real(self, evaluation_score: float, feedback_type: str) -> List[str]:
        """실제 구현 단계 생성 - 판단 로직 기반 동적 생성"""
        # 컨텍스트 분석
        context = getattr(self, "current_context", {})
        recent_failures = context.get("recent_failures", 0)
        system_performance = context.get("system_performance", 0.5)
        improvement_history = context.get("improvement_history", [])

        if feedback_type == "negative":
            if recent_failures > 3:
                return [
                    "연속 실패 원인 분석",
                    "긴급 상황 분석",
                    "즉시 개선 실행",
                    "결과 모니터링",
                ]
            elif system_performance < 0.3:
                return [
                    "성능 저하 원인 분석",
                    "긴급 상황 분석",
                    "즉시 개선 실행",
                    "결과 모니터링",
                ]
            else:
                return ["긴급 상황 분석", "즉시 개선 실행", "결과 모니터링"]
        elif feedback_type == "neutral":
            if len(improvement_history) > 0 and improvement_history[-1].get("success", False):
                return ["이전 개선 효과 분석", "상황 분석", "단계적 개선", "효과 측정"]
            else:
                return ["상황 분석", "단계적 개선", "효과 측정"]
        elif feedback_type == "constructive":
            if system_performance > 0.7:
                return [
                    "고성능 기반 분석",
                    "개선 기회 식별",
                    "선택적 개선",
                    "성과 평가",
                ]
            else:
                return ["개선 기회 식별", "선택적 개선", "성과 평가"]
        else:  # positive
            if system_performance > 0.8:
                return [
                    "우수 성능 요인 분석",
                    "성공 요인 분석",
                    "확장 계획 수립",
                    "지속적 모니터링",
                ]
            else:
                return ["성공 요인 분석", "확장 계획 수립", "지속적 모니터링"]

    def _calculate_expected_impact_real(self, evaluation_score: float, feedback_type: str) -> Dict[str, float]:
        """실제 예상 영향 계산"""
        if feedback_type == "negative":
            return {"stability": 0.8, "reliability": 0.7, "performance": 0.6}
        elif feedback_type == "neutral":
            return {"stability": 0.5, "reliability": 0.4, "performance": 0.3}
        elif feedback_type == "constructive":
            return {"stability": 0.3, "reliability": 0.2, "performance": 0.4}
        else:  # positive
            return {"stability": 0.1, "reliability": 0.1, "performance": 0.2}

    def _estimate_timeline_real(self, evaluation_score: float, feedback_type: str) -> float:
        """실제 타임라인 추정"""
        if feedback_type == "negative":
            return 0.5  # 30분
        elif feedback_type == "neutral":
            return 2.0  # 2시간
        elif feedback_type == "constructive":
            return 4.0  # 4시간
        else:  # positive
            return 8.0  # 8시간

    def _identify_resources_needed_real(self, evaluation_score: float, feedback_type: str) -> List[str]:
        """실제 필요 리소스 식별"""
        if feedback_type == "negative":
            return ["cpu", "memory", "network", "emergency_resources"]
        elif feedback_type == "neutral":
            return ["cpu", "memory"]
        elif feedback_type == "constructive":
            return ["cpu", "learning_resources"]
        else:  # positive
            return ["cpu"]

    def _define_success_metrics_real(self, evaluation_score: float, feedback_type: str) -> List[str]:
        """실제 성공 지표 정의 - 판단 로직 기반 동적 생성"""
        # 컨텍스트 분석
        context = getattr(self, "current_context", {})
        recent_failures = context.get("recent_failures", 0)
        system_performance = context.get("system_performance", 0.5)
        improvement_history = context.get("improvement_history", [])

        if feedback_type == "negative":
            if recent_failures > 3:
                return ["연속 실패 패턴 해결", "오류 감소", "안정성 향상", "성능 개선"]
            elif system_performance < 0.3:
                return ["성능 복구", "안정성 향상", "성능 개선", "시스템 안정화"]
            else:
                return ["오류 감소", "안정성 향상", "성능 개선"]
        elif feedback_type == "neutral":
            if len(improvement_history) > 0 and improvement_history[-1].get("success", False):
                return [
                    "이전 개선 효과 유지",
                    "효과성 향상",
                    "효율성 개선",
                    "지속적 개선",
                ]
            else:
                return ["효과성 향상", "효율성 개선"]
        elif feedback_type == "constructive":
            if system_performance > 0.7:
                return ["고성능 유지", "점진적 개선", "학습 효과", "혁신적 접근"]
            else:
                return ["점진적 개선", "학습 효과"]
        else:  # positive
            if system_performance > 0.8:
                return ["우수 성능 유지", "현재 수준 유지", "확장 성공", "지속적 혁신"]
            else:
                return ["현재 수준 유지", "확장 성공"]


class FeedbackEvaluator:
    """피드백 평가기"""

    def __init__(self):
        self.evaluation_criteria = {
            "effectiveness": 0.4,
            "efficiency": 0.3,
            "innovation": 0.2,
            "sustainability": 0.1,
        }

    async def evaluate(self, action_result: Dict[str, Any]) -> FeedbackResult:
        """행동 결과 평가"""
        try:
            # 평가 점수 계산
            effectiveness_score = action_result.get("effectiveness_score", 0.5)
            efficiency_score = action_result.get("efficiency_score", 0.5)

            # 종합 평가 점수
            overall_score = (
                effectiveness_score * self.evaluation_criteria["effectiveness"]
                + efficiency_score * self.evaluation_criteria["efficiency"]
                + 0.6 * self.evaluation_criteria["innovation"]
                + 0.7 * self.evaluation_criteria["sustainability"]
            )

            # 피드백 타입 결정
            if overall_score >= 0.7:
                feedback_type = FeedbackType.POSITIVE
            elif overall_score <= 0.3:
                feedback_type = FeedbackType.NEGATIVE
            else:
                feedback_type = FeedbackType.NEUTRAL

            # 학습 포인트 추출
            learning_points = action_result.get("learning_points", [])

            # 개선 제안 생성
            improvement_suggestions = await self._generate_improvements(overall_score, action_result)

            # 다음 행동 제안
            next_actions = action_result.get("next_actions", [])

            return FeedbackResult(
                feedback_type=feedback_type,
                evaluation_score=overall_score,
                learning_points=learning_points,
                improvement_suggestions=improvement_suggestions,
                next_actions=next_actions,
                confidence=min(overall_score + 0.1, 1.0),
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"평가 실패: {e}")
            raise

    async def _generate_improvements(self, score: float, action_result: Dict[str, Any]) -> List[str]:
        """개선점 생성"""
        improvements = []

        if score < 0.5:
            improvements.append("전략적 접근 방식 개선 필요")
        if score < 0.7:
            improvements.append("실행 방법 최적화 필요")
        if score > 0.8:
            improvements.append("현재 수준 유지 및 확장")

        return improvements


class LearningEngine:
    """학습 엔진"""

    def __init__(self):
        self.learning_patterns = {}
        self.knowledge_base = {}

    async def learn(self, action_result: Dict[str, Any]) -> LearningResult:
        """행동 결과로부터 학습"""
        try:
            # 학습 타입 결정
            if action_result.get("success", False):
                learning_type = LearningType.REINFORCEMENT
            else:
                learning_type = LearningType.CORRECTIVE

            # 지식 획득
            knowledge_gained = action_result.get("learning_points", [])

            # 스킬 개선
            skill_improvement = {
                "effectiveness": action_result.get("effectiveness_score", 0.5),
                "efficiency": action_result.get("efficiency_score", 0.5),
                "adaptation": 0.6,
            }

            # 행동 변화
            behavior_change = ["성능 최적화", "효율성 향상"]

            # 적응 수준
            adaptation_level = 0.7

            # 혁신 점수
            innovation_score = 0.6

            return LearningResult(
                learning_type=learning_type,
                knowledge_gained=knowledge_gained,
                skill_improvement=skill_improvement,
                behavior_change=behavior_change,
                adaptation_level=adaptation_level,
                innovation_score=innovation_score,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"학습 실패: {e}")
            raise


class ImprovementPlanner:
    """개선 계획 수립기"""

    def __init__(self):
        self.improvement_templates = {}

    async def create_plan(self, feedback_result: FeedbackResult) -> ImprovementPlan:
        """개선 계획 생성"""
        try:
            improvement_id = f"improvement_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 우선순위 계산
            priority = 1.0 - feedback_result.evaluation_score

            # 설명 생성
            description = f"피드백 기반 개선 계획 (점수: {feedback_result.evaluation_score:.2f})"

            # 구현 단계
            implementation_steps = [
                "현재 상태 분석",
                "개선점 식별",
                "계획 수립",
                "실행",
                "결과 평가",
            ]

            # 예상 영향
            expected_impact = {
                "effectiveness": 0.1,
                "efficiency": 0.1,
                "overall_score": 0.15,
            }

            # 타임라인
            timeline = 7.0  # 일

            # 필요 리소스
            resources_needed = ["cpu", "memory", "learning"]

            # 성공 지표
            success_metrics = ["성능 향상", "효율성 개선", "안정성 향상"]

            return ImprovementPlan(
                improvement_id=improvement_id,
                priority=priority,
                description=description,
                implementation_steps=implementation_steps,
                expected_impact=expected_impact,
                timeline=timeline,
                resources_needed=resources_needed,
                success_metrics=success_metrics,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"개선 계획 생성 실패: {e}")
            raise


async def test_feedback_system():
    """피드백 시스템 테스트"""
    print("🧪 피드백 시스템 테스트 시작")

    feedback_system = FeedbackSystem()

    # 테스트 데이터
    test_action_result = {
        "action": "system_optimization",
        "result": {"success": True, "performance_improvement": 0.15},
        "effectiveness_score": 0.8,
        "efficiency_score": 0.75,
        "learning_points": ["성능 최적화 성공", "리소스 사용량 감소"],
        "next_actions": ["모니터링 강화", "추가 최적화"],
    }

    # 피드백 실행
    feedback_result = await feedback_system.feedback(test_action_result)

    print(f"✅ 피드백 결과: {feedback_result}")

    return feedback_result


if __name__ == "__main__":
    asyncio.run(test_feedback_system())
