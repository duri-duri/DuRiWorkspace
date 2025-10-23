#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 3 - 판단 시스템
상황 분석, 의사결정, 판단 품질 평가 통합 시스템
"""

import asyncio
import json
import logging
import math
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class JudgmentType(Enum):
    """판단 타입 열거형"""

    RULE_BASED = "rule_based"  # 규칙 기반
    ML_BASED = "ml_based"  # 머신러닝 기반
    ETHICAL = "ethical"  # 윤리적 판단
    HYBRID = "hybrid"  # 하이브리드


class DecisionConfidence(Enum):
    """의사결정 신뢰도 열거형"""

    LOW = "low"  # 낮음 (0.0-0.3)
    MEDIUM = "medium"  # 중간 (0.3-0.7)
    HIGH = "high"  # 높음 (0.7-1.0)


@dataclass
class SituationAnalysis:
    """상황 분석 결과"""

    situation_type: str
    context_elements: List[str]
    key_factors: List[str]
    risk_level: float
    urgency_level: float
    complexity_score: float
    confidence: float
    analysis_method: str


@dataclass
class DecisionResult:
    """의사결정 결과"""

    decision: str
    reasoning: str
    confidence: float
    alternatives: List[str]
    risk_assessment: Dict[str, float]
    ethical_score: float
    judgment_type: JudgmentType
    created_at: datetime


@dataclass
class JudgmentQuality:
    """판단 품질 평가"""

    accuracy_score: float
    consistency_score: float
    ethical_score: float
    efficiency_score: float
    overall_score: float
    feedback: List[str]
    improvement_suggestions: List[str]


class JudgmentSystem:
    """판단 시스템"""

    def __init__(self):
        self.situation_patterns = {}
        self.decision_rules = {}
        self.ethical_guidelines = {}
        self.quality_metrics = {}

        # 판단 임계값
        self.confidence_threshold = 0.7
        self.ethical_threshold = 0.8
        self.quality_threshold = 0.75

        # 성능 설정
        self.max_analysis_time = 5.0  # 초
        self.max_decision_time = 2.0  # 초

        logger.info("판단 시스템 초기화 완료")

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 처리 (통합 루프용)"""
        try:
            # 메모리 데이터에서 상황 정보 추출
            memory_data = input_data.get("data", {})
            content = memory_data.get("content", "")
            context = memory_data.get("context", {})

            # 상황 분석
            situation_analysis = await self.analyze_situation(
                {"content": content}, context
            )

            # 의사결정
            available_actions = ["proceed", "wait", "reconsider", "escalate"]
            constraints = {"time_limit": 10.0, "resource_limit": 0.8}
            decision_result = await self.make_decision(
                situation_analysis, available_actions, constraints
            )

            return {
                "success": True,
                "situation_analysis": situation_analysis,
                "decision_result": decision_result,
                "data": {
                    "content": content,
                    "context": context,
                    "decision": decision_result.decision,
                    "confidence": decision_result.confidence,
                },
            }

        except Exception as e:
            logger.error(f"판단 시스템 입력 처리 실패: {e}")
            return {"success": False, "error": str(e), "data": {}}

    async def analyze_situation(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> SituationAnalysis:
        """상황 분석"""
        try:
            start_time = datetime.now()

            # 1. 입력 데이터 분석
            data_analysis = await self._analyze_input_data(input_data)

            # 2. 컨텍스트 추출
            context_elements = await self._extract_context_elements(context)

            # 3. 상황 패턴 인식
            situation_pattern = await self._recognize_situation_pattern(
                input_data, context
            )

            # 4. 핵심 요소 식별
            key_factors = await self._identify_key_factors(input_data, context)

            # 5. 위험도 및 긴급도 평가
            risk_level = await self._assess_risk_level(input_data, context)
            urgency_level = await self._assess_urgency_level(input_data, context)

            # 6. 복잡도 계산
            complexity_score = await self._calculate_complexity(input_data, context)

            # 7. 신뢰도 계산
            confidence = await self._calculate_analysis_confidence(
                data_analysis, context_elements, situation_pattern
            )

            analysis_time = (datetime.now() - start_time).total_seconds()

            return SituationAnalysis(
                situation_type=situation_pattern.get("type", "unknown"),
                context_elements=context_elements,
                key_factors=key_factors,
                risk_level=risk_level,
                urgency_level=urgency_level,
                complexity_score=complexity_score,
                confidence=confidence,
                analysis_method=f"comprehensive_analysis_{analysis_time:.2f}s",
            )

        except Exception as e:
            logger.error(f"상황 분석 오류: {e}")
            return SituationAnalysis(
                situation_type="error",
                context_elements=[],
                key_factors=[],
                risk_level=0.5,
                urgency_level=0.5,
                complexity_score=0.5,
                confidence=0.3,
                analysis_method="error_fallback",
            )

    async def make_decision(
        self,
        situation_analysis: SituationAnalysis,
        available_actions: List[str],
        constraints: Dict[str, Any],
    ) -> DecisionResult:
        """의사결정 수행"""
        try:
            start_time = datetime.now()

            # 1. 규칙 기반 의사결정
            rule_decision = await self._rule_based_decision(
                situation_analysis, available_actions, constraints
            )

            # 2. 머신러닝 기반 의사결정
            ml_decision = await self._ml_based_decision(
                situation_analysis, available_actions, constraints
            )

            # 3. 윤리적 판단
            ethical_review = await self._ethical_review(
                rule_decision, ml_decision, situation_analysis
            )

            # 4. 최종 의사결정 (하이브리드)
            final_decision = await self._hybrid_decision(
                rule_decision, ml_decision, ethical_review
            )

            # 5. 대안 생성
            alternatives = await self._generate_alternatives(
                situation_analysis, available_actions
            )

            # 6. 위험 평가
            risk_assessment = await self._assess_decision_risk(
                final_decision, situation_analysis
            )

            decision_time = (datetime.now() - start_time).total_seconds()

            return DecisionResult(
                decision=final_decision["action"],
                reasoning=final_decision["reasoning"],
                confidence=final_decision["confidence"],
                alternatives=alternatives,
                risk_assessment=risk_assessment,
                ethical_score=ethical_review["score"],
                judgment_type=JudgmentType.HYBRID,
                created_at=datetime.now(),
            )

        except Exception as e:
            logger.error(f"의사결정 오류: {e}")
            return DecisionResult(
                decision="error_fallback",
                reasoning=f"의사결정 오류: {e}",
                confidence=0.3,
                alternatives=[],
                risk_assessment={"error": 1.0},
                ethical_score=0.5,
                judgment_type=JudgmentType.RULE_BASED,
                created_at=datetime.now(),
            )

    async def evaluate_judgment_quality(
        self,
        situation_analysis: SituationAnalysis,
        decision_result: DecisionResult,
        outcome: Dict[str, Any],
    ) -> JudgmentQuality:
        """판단 품질 평가"""
        try:
            # 1. 정확도 평가
            accuracy_score = await self._evaluate_accuracy(decision_result, outcome)

            # 2. 일관성 평가
            consistency_score = await self._evaluate_consistency(
                decision_result, situation_analysis
            )

            # 3. 윤리성 평가
            ethical_score = await self._evaluate_ethical_quality(
                decision_result, outcome
            )

            # 4. 효율성 평가
            efficiency_score = await self._evaluate_efficiency(decision_result, outcome)

            # 5. 종합 점수 계산
            overall_score = (
                accuracy_score + consistency_score + ethical_score + efficiency_score
            ) / 4

            # 6. 피드백 생성
            feedback = await self._generate_feedback(
                accuracy_score, consistency_score, ethical_score, efficiency_score
            )

            # 7. 개선 제안
            improvement_suggestions = await self._generate_improvement_suggestions(
                accuracy_score, consistency_score, ethical_score, efficiency_score
            )

            return JudgmentQuality(
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                ethical_score=ethical_score,
                efficiency_score=efficiency_score,
                overall_score=overall_score,
                feedback=feedback,
                improvement_suggestions=improvement_suggestions,
            )

        except Exception as e:
            logger.error(f"판단 품질 평가 오류: {e}")
            return JudgmentQuality(
                accuracy_score=0.5,
                consistency_score=0.5,
                ethical_score=0.5,
                efficiency_score=0.5,
                overall_score=0.5,
                feedback=[f"평가 오류: {e}"],
                improvement_suggestions=["시스템 오류 수정 필요"],
            )

    # 내부 메서드들 (기본 구현)
    async def _analyze_input_data(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 분석"""
        try:
            analysis = {
                "data_type": type(input_data).__name__,
                "data_size": len(str(input_data)),
                "key_fields": (
                    list(input_data.keys()) if isinstance(input_data, dict) else []
                ),
                "complexity": self._calculate_data_complexity(input_data),
                "quality_score": self._assess_data_quality(input_data),
            }
            return analysis
        except Exception as e:
            logger.error(f"입력 데이터 분석 오류: {e}")
            return {"error": str(e)}

    async def _extract_context_elements(self, context: Dict[str, Any]) -> List[str]:
        """컨텍스트 요소 추출"""
        try:
            elements = []
            for key, value in context.items():
                if isinstance(value, str):
                    elements.append(f"{key}:{value}")
                elif isinstance(value, (int, float)):
                    elements.append(f"{key}:{value}")
                elif isinstance(value, dict):
                    elements.extend([f"{key}.{k}:{v}" for k, v in value.items()])
                elif isinstance(value, list):
                    elements.append(f"{key}:{len(value)}_items")
            return elements
        except Exception as e:
            logger.error(f"컨텍스트 요소 추출 오류: {e}")
            return []

    async def _recognize_situation_pattern(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """상황 패턴 인식"""
        try:
            patterns = {
                "learning": ["학습", "공부", "배우", "이해"],
                "decision": ["결정", "선택", "판단", "결론"],
                "problem": ["문제", "오류", "실패", "위험"],
                "opportunity": ["기회", "가능성", "잠재력", "성장"],
                "conflict": ["갈등", "충돌", "대립", "문제"],
            }

            content = str(input_data) + str(context)
            matched_patterns = []

            for pattern_name, keywords in patterns.items():
                if any(keyword in content for keyword in keywords):
                    matched_patterns.append(pattern_name)

            return {
                "type": matched_patterns[0] if matched_patterns else "general",
                "patterns": matched_patterns,
                "confidence": len(matched_patterns) / len(patterns),
            }
        except Exception as e:
            logger.error(f"상황 패턴 인식 오류: {e}")
            return {"type": "unknown", "patterns": [], "confidence": 0.0}

    async def _identify_key_factors(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> List[str]:
        """핵심 요소 식별"""
        try:
            factors = []
            if "importance" in context:
                factors.append("importance")
            if "urgency" in context:
                factors.append("urgency")
            if "risk" in context:
                factors.append("risk")
            if "content" in input_data:
                factors.append("content_analysis")
            if "emotion" in context:
                factors.append("emotional_context")
            if "memory" in context:
                factors.append("memory_context")
            return factors
        except Exception as e:
            logger.error(f"핵심 요소 식별 오류: {e}")
            return []

    async def _assess_risk_level(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """위험도 평가"""
        try:
            risk_score = 0.0
            if "risk" in context:
                risk_score += float(context["risk"])
            if "danger" in str(input_data).lower():
                risk_score += 0.3
            if "error" in str(input_data).lower():
                risk_score += 0.2
            if "fail" in str(input_data).lower():
                risk_score += 0.2
            return min(1.0, risk_score)
        except Exception as e:
            logger.error(f"위험도 평가 오류: {e}")
            return 0.5

    async def _assess_urgency_level(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """긴급도 평가"""
        try:
            urgency_score = 0.0
            if "urgency" in context:
                urgency_score += float(context["urgency"])
            if "immediate" in str(input_data).lower():
                urgency_score += 0.4
            if "now" in str(input_data).lower():
                urgency_score += 0.3
            if "quick" in str(input_data).lower():
                urgency_score += 0.2
            return min(1.0, urgency_score)
        except Exception as e:
            logger.error(f"긴급도 평가 오류: {e}")
            return 0.5

    async def _calculate_complexity(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> float:
        """복잡도 계산"""
        try:
            complexity = 0.0
            data_size = len(str(input_data)) + len(str(context))
            complexity += min(0.3, data_size / 1000)
            element_count = len(input_data) + len(context)
            complexity += min(0.3, element_count / 10)
            if "complex" in str(input_data).lower():
                complexity += 0.2
            if "multiple" in str(input_data).lower():
                complexity += 0.2
            return min(1.0, complexity)
        except Exception as e:
            logger.error(f"복잡도 계산 오류: {e}")
            return 0.5

    async def _calculate_analysis_confidence(
        self,
        data_analysis: Dict[str, Any],
        context_elements: List[str],
        situation_pattern: Dict[str, Any],
    ) -> float:
        """분석 신뢰도 계산"""
        try:
            confidence = 0.5
            if "quality_score" in data_analysis:
                confidence += data_analysis["quality_score"] * 0.3
            if context_elements:
                confidence += min(0.2, len(context_elements) / 10)
            if "confidence" in situation_pattern:
                confidence += situation_pattern["confidence"] * 0.3
            return min(1.0, confidence)
        except Exception as e:
            logger.error(f"분석 신뢰도 계산 오류: {e}")
            return 0.5

    async def _rule_based_decision(
        self,
        situation_analysis: SituationAnalysis,
        available_actions: List[str],
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        """규칙 기반 의사결정"""
        try:
            if situation_analysis.risk_level > 0.7:
                action = "high_risk_action"
                reasoning = "위험도가 높아 보수적 접근 필요"
                confidence = 0.8
            elif situation_analysis.urgency_level > 0.7:
                action = "urgent_action"
                reasoning = "긴급도가 높아 신속한 대응 필요"
                confidence = 0.7
            elif situation_analysis.complexity_score > 0.7:
                action = "complex_analysis_action"
                reasoning = "복잡도가 높아 상세 분석 필요"
                confidence = 0.6
            else:
                action = "standard_action"
                reasoning = "표준적인 접근 방식 적용"
                confidence = 0.5

            return {
                "action": action,
                "reasoning": reasoning,
                "confidence": confidence,
                "method": "rule_based",
            }
        except Exception as e:
            logger.error(f"규칙 기반 의사결정 오류: {e}")
            return {
                "action": "error_fallback",
                "reasoning": f"규칙 기반 의사결정 오류: {e}",
                "confidence": 0.3,
                "method": "rule_based",
            }

    async def _ml_based_decision(
        self,
        situation_analysis: SituationAnalysis,
        available_actions: List[str],
        constraints: Dict[str, Any],
    ) -> Dict[str, Any]:
        """머신러닝 기반 의사결정"""
        try:
            features = [
                situation_analysis.risk_level,
                situation_analysis.urgency_level,
                situation_analysis.complexity_score,
                situation_analysis.confidence,
            ]

            weighted_score = sum(features) / len(features)

            if weighted_score > 0.7:
                action = "aggressive_action"
                reasoning = "높은 신뢰도로 적극적 접근"
                confidence = weighted_score
            elif weighted_score > 0.4:
                action = "balanced_action"
                reasoning = "균형잡힌 접근 방식"
                confidence = weighted_score
            else:
                action = "conservative_action"
                reasoning = "보수적 접근 방식"
                confidence = 0.5

            return {
                "action": action,
                "reasoning": reasoning,
                "confidence": confidence,
                "method": "ml_based",
            }
        except Exception as e:
            logger.error(f"ML 기반 의사결정 오류: {e}")
            return {
                "action": "error_fallback",
                "reasoning": f"ML 기반 의사결정 오류: {e}",
                "confidence": 0.3,
                "method": "ml_based",
            }

    async def _ethical_review(
        self,
        rule_decision: Dict[str, Any],
        ml_decision: Dict[str, Any],
        situation_analysis: SituationAnalysis,
    ) -> Dict[str, Any]:
        """윤리적 검토"""
        try:
            ethical_score = 0.5

            if situation_analysis.risk_level > 0.8:
                ethical_score -= 0.2

            if situation_analysis.urgency_level > 0.8:
                ethical_score -= 0.1

            if rule_decision["confidence"] > ml_decision["confidence"]:
                ethical_score += 0.1

            return {
                "score": max(0.0, min(1.0, ethical_score)),
                "considerations": ["위험도 고려", "긴급도 고려", "의사결정 방법 고려"],
                "recommendation": "ethical_balanced_approach",
            }
        except Exception as e:
            logger.error(f"윤리적 검토 오류: {e}")
            return {
                "score": 0.5,
                "considerations": [f"윤리적 검토 오류: {e}"],
                "recommendation": "error_fallback",
            }

    async def _hybrid_decision(
        self,
        rule_decision: Dict[str, Any],
        ml_decision: Dict[str, Any],
        ethical_review: Dict[str, Any],
    ) -> Dict[str, Any]:
        """하이브리드 의사결정"""
        try:
            rule_weight = rule_decision["confidence"]
            ml_weight = ml_decision["confidence"]
            ethical_weight = ethical_review["score"]

            if rule_weight > ml_weight:
                final_decision = rule_decision
                reasoning = f"규칙 기반 의사결정 선택 (신뢰도: {rule_weight:.3f})"
            else:
                final_decision = ml_decision
                reasoning = f"ML 기반 의사결정 선택 (신뢰도: {ml_weight:.3f})"

            if ethical_review["score"] < 0.5:
                reasoning += " (윤리적 고려사항 적용)"

            return {
                "action": final_decision["action"],
                "reasoning": reasoning,
                "confidence": (rule_weight + ml_weight + ethical_weight) / 3,
                "method": "hybrid",
            }
        except Exception as e:
            logger.error(f"하이브리드 의사결정 오류: {e}")
            return {
                "action": "error_fallback",
                "reasoning": f"하이브리드 의사결정 오류: {e}",
                "confidence": 0.3,
                "method": "hybrid",
            }

    async def _generate_alternatives(
        self, situation_analysis: SituationAnalysis, available_actions: List[str]
    ) -> List[str]:
        """대안 생성"""
        try:
            alternatives = []

            if situation_analysis.risk_level > 0.7:
                alternatives.append("risk_mitigation_action")

            if situation_analysis.urgency_level > 0.7:
                alternatives.append("rapid_response_action")

            if situation_analysis.complexity_score > 0.7:
                alternatives.append("detailed_analysis_action")

            alternatives.extend(
                ["wait_and_observe", "consult_expert", "gather_more_info"]
            )

            return alternatives[:5]
        except Exception as e:
            logger.error(f"대안 생성 오류: {e}")
            return ["error_fallback"]

    async def _assess_decision_risk(
        self, decision: Dict[str, Any], situation_analysis: SituationAnalysis
    ) -> Dict[str, float]:
        """의사결정 위험 평가"""
        try:
            risk_assessment = {}
            risk_assessment["base_risk"] = situation_analysis.risk_level
            risk_assessment["confidence_risk"] = 1.0 - decision["confidence"]
            risk_assessment["complexity_risk"] = (
                situation_analysis.complexity_score * 0.5
            )
            risk_assessment["total_risk"] = (
                risk_assessment["base_risk"]
                + risk_assessment["confidence_risk"]
                + risk_assessment["complexity_risk"]
            ) / 3

            return risk_assessment
        except Exception as e:
            logger.error(f"의사결정 위험 평가 오류: {e}")
            return {"error": 1.0}

    async def _evaluate_accuracy(
        self, decision_result: DecisionResult, outcome: Dict[str, Any]
    ) -> float:
        """정확도 평가"""
        try:
            accuracy = 0.5
            accuracy += decision_result.confidence * 0.3
            accuracy += decision_result.ethical_score * 0.2
            return min(1.0, accuracy)
        except Exception as e:
            logger.error(f"정확도 평가 오류: {e}")
            return 0.5

    async def _evaluate_consistency(
        self, decision_result: DecisionResult, situation_analysis: SituationAnalysis
    ) -> float:
        """일관성 평가"""
        try:
            consistency = 0.5

            if (
                situation_analysis.risk_level > 0.7
                and "risk" in decision_result.decision.lower()
            ):
                consistency += 0.2

            if (
                situation_analysis.urgency_level > 0.7
                and "urgent" in decision_result.decision.lower()
            ):
                consistency += 0.2

            consistency += decision_result.confidence * 0.1

            return min(1.0, consistency)
        except Exception as e:
            logger.error(f"일관성 평가 오류: {e}")
            return 0.5

    async def _evaluate_ethical_quality(
        self, decision_result: DecisionResult, outcome: Dict[str, Any]
    ) -> float:
        """윤리적 품질 평가"""
        try:
            return decision_result.ethical_score
        except Exception as e:
            logger.error(f"윤리적 품질 평가 오류: {e}")
            return 0.5

    async def _evaluate_efficiency(
        self, decision_result: DecisionResult, outcome: Dict[str, Any]
    ) -> float:
        """효율성 평가"""
        try:
            efficiency = 0.5
            efficiency += decision_result.confidence * 0.3

            if 2 <= len(decision_result.alternatives) <= 5:
                efficiency += 0.2

            return min(1.0, efficiency)
        except Exception as e:
            logger.error(f"효율성 평가 오류: {e}")
            return 0.5

    async def _generate_feedback(
        self,
        accuracy_score: float,
        consistency_score: float,
        ethical_score: float,
        efficiency_score: float,
    ) -> List[str]:
        """피드백 생성"""
        try:
            feedback = []

            if accuracy_score < 0.6:
                feedback.append("정확도 개선 필요")

            if consistency_score < 0.6:
                feedback.append("일관성 개선 필요")

            if ethical_score < 0.6:
                feedback.append("윤리적 고려사항 강화 필요")

            if efficiency_score < 0.6:
                feedback.append("효율성 개선 필요")

            if not feedback:
                feedback.append("전반적으로 양호한 판단")

            return feedback
        except Exception as e:
            logger.error(f"피드백 생성 오류: {e}")
            return [f"피드백 생성 오류: {e}"]

    async def _generate_improvement_suggestions(
        self,
        accuracy_score: float,
        consistency_score: float,
        ethical_score: float,
        efficiency_score: float,
    ) -> List[str]:
        """개선 제안 생성"""
        try:
            suggestions = []

            if accuracy_score < 0.6:
                suggestions.append("더 많은 데이터 수집 필요")
                suggestions.append("분석 방법 개선 필요")

            if consistency_score < 0.6:
                suggestions.append("의사결정 기준 표준화 필요")
                suggestions.append("상황 분석 정확도 향상 필요")

            if ethical_score < 0.6:
                suggestions.append("윤리적 가이드라인 강화 필요")
                suggestions.append("윤리적 검토 프로세스 개선 필요")

            if efficiency_score < 0.6:
                suggestions.append("의사결정 프로세스 최적화 필요")
                suggestions.append("자동화 수준 향상 필요")

            if not suggestions:
                suggestions.append("현재 수준 유지 권장")

            return suggestions
        except Exception as e:
            logger.error(f"개선 제안 생성 오류: {e}")
            return [f"개선 제안 생성 오류: {e}"]

    def _calculate_data_complexity(self, data: Any) -> float:
        """데이터 복잡도 계산"""
        try:
            if isinstance(data, dict):
                return min(1.0, len(data) / 10)
            elif isinstance(data, list):
                return min(1.0, len(data) / 20)
            else:
                return 0.1
        except:
            return 0.5

    def _assess_data_quality(self, data: Any) -> float:
        """데이터 품질 평가"""
        try:
            if data is None:
                return 0.0
            elif isinstance(data, dict) and len(data) > 0:
                return 0.8
            elif isinstance(data, list) and len(data) > 0:
                return 0.7
            else:
                return 0.5
        except:
            return 0.5


# 테스트 함수
async def test_judgment_system():
    """판단 시스템 테스트"""
    print("=== DuRiCore Phase 5 Day 3 - 판단 시스템 테스트 ===")

    # 시스템 초기화
    judgment_system = JudgmentSystem()

    # 테스트 데이터
    test_input = {
        "content": "중요한 프로젝트에서 위험한 상황이 발생했습니다. 긴급한 의사결정이 필요합니다.",
        "priority": "high",
        "context": "business_critical",
    }

    test_context = {
        "risk_level": 0.8,
        "urgency": 0.9,
        "importance": "critical",
        "stakeholders": ["management", "team", "clients"],
    }

    available_actions = [
        "immediate_action",
        "consult_expert",
        "gather_more_info",
        "delegate_task",
        "postpone_decision",
    ]

    constraints = {
        "time_limit": "2_hours",
        "budget_limit": "high",
        "ethical_considerations": "strict",
    }

    # 1. 상황 분석 테스트
    print("\n1. 상황 분석 테스트")
    situation_analysis = await judgment_system.analyze_situation(
        test_input, test_context
    )
    print(f"상황 타입: {situation_analysis.situation_type}")
    print(f"위험도: {situation_analysis.risk_level:.3f}")
    print(f"긴급도: {situation_analysis.urgency_level:.3f}")
    print(f"복잡도: {situation_analysis.complexity_score:.3f}")
    print(f"신뢰도: {situation_analysis.confidence:.3f}")
    print(f"핵심 요소: {situation_analysis.key_factors}")

    # 2. 의사결정 테스트
    print("\n2. 의사결정 테스트")
    decision_result = await judgment_system.make_decision(
        situation_analysis, available_actions, constraints
    )
    print(f"결정: {decision_result.decision}")
    print(f"추론: {decision_result.reasoning}")
    print(f"신뢰도: {decision_result.confidence:.3f}")
    print(f"윤리적 점수: {decision_result.ethical_score:.3f}")
    print(f"대안: {decision_result.alternatives}")
    print(f"위험 평가: {decision_result.risk_assessment}")

    # 3. 판단 품질 평가 테스트
    print("\n3. 판단 품질 평가 테스트")
    outcome = {
        "success": True,
        "time_taken": "1.5_hours",
        "stakeholder_satisfaction": 0.8,
    }

    quality = await judgment_system.evaluate_judgment_quality(
        situation_analysis, decision_result, outcome
    )
    print(f"정확도: {quality.accuracy_score:.3f}")
    print(f"일관성: {quality.consistency_score:.3f}")
    print(f"윤리성: {quality.ethical_score:.3f}")
    print(f"효율성: {quality.efficiency_score:.3f}")
    print(f"종합 점수: {quality.overall_score:.3f}")
    print(f"피드백: {quality.feedback}")
    print(f"개선 제안: {quality.improvement_suggestions}")

    print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_judgment_system())
