#!/usr/bin/env python3
"""
EnhancedEthicalSystem - Phase 12
고도화된 윤리 시스템

기능:
- 포괄적인 윤리적 판단
- 안전성 평가
- 가족 조화 보장
- 투명성 유지
- 윤리적 가치 기준 관리
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EthicalPrinciple(Enum):
    """윤리적 원칙"""

    HUMAN_CENTERED = "human_centered"
    SAFETY_FIRST = "safety_first"
    TRANSPARENCY = "transparency"
    FAMILY_HARMONY = "family_harmony"
    FAIRNESS = "fairness"
    RESPECT = "respect"
    BENEFICENCE = "beneficence"
    NON_MALEFICENCE = "non_maleficence"


class EthicalJudgmentLevel(Enum):
    """윤리적 판단 수준"""

    CLEARLY_ETHICAL = "clearly_ethical"
    LIKELY_ETHICAL = "likely_ethical"
    UNCLEAR = "unclear"
    LIKELY_UNETHICAL = "likely_unethical"
    CLEARLY_UNETHICAL = "clearly_unethical"


class SafetyRiskLevel(Enum):
    """안전 위험 수준"""

    NO_RISK = "no_risk"
    LOW_RISK = "low_risk"
    MODERATE_RISK = "moderate_risk"
    HIGH_RISK = "high_risk"
    CRITICAL_RISK = "critical_risk"


class FamilyHarmonyLevel(Enum):
    """가족 조화 수준"""

    HARMONIOUS = "harmonious"
    MOSTLY_HARMONIOUS = "mostly_harmonious"
    NEUTRAL = "neutral"
    POTENTIALLY_DISRUPTIVE = "potentially_disruptive"
    DISRUPTIVE = "disruptive"


@dataclass
class EthicalAnalysis:
    """윤리적 분석"""

    id: str
    situation_description: str
    ethical_principles: List[EthicalPrinciple]
    judgment_level: EthicalJudgmentLevel
    reasoning: str
    family_impact: str
    safety_assessment: str
    transparency_level: float
    confidence_score: float
    timestamp: datetime


@dataclass
class SafetyAssessment:
    """안전성 평가"""

    id: str
    analysis_id: str
    risk_level: SafetyRiskLevel
    identified_risks: List[str]
    mitigation_strategies: List[str]
    family_safety_impact: str
    overall_safety_score: float
    timestamp: datetime


@dataclass
class FamilyHarmonyAssessment:
    """가족 조화 평가"""

    id: str
    analysis_id: str
    harmony_level: FamilyHarmonyLevel
    positive_impacts: List[str]
    potential_concerns: List[str]
    harmony_enhancement_suggestions: List[str]
    family_satisfaction_score: float
    timestamp: datetime


@dataclass
class EthicalGuideline:
    """윤리적 가이드라인"""

    id: str
    principle: EthicalPrinciple
    description: str
    application_rules: List[str]
    family_context_considerations: List[str]
    priority_level: int
    last_updated: datetime


class EnhancedEthicalSystem:
    """고도화된 윤리 시스템"""

    def __init__(self):
        self.ethical_analyses: List[EthicalAnalysis] = []
        self.safety_assessments: List[SafetyAssessment] = []
        self.harmony_assessments: List[FamilyHarmonyAssessment] = []
        self.ethical_guidelines: List[EthicalGuideline] = []
        self.family_context: Dict[str, Any] = {}

        # 윤리적 가이드라인 초기화
        self._initialize_ethical_guidelines()

        logger.info("EnhancedEthicalSystem 초기화 완료")

    def _initialize_ethical_guidelines(self):
        """윤리적 가이드라인 초기화"""
        guidelines = [
            EthicalGuideline(
                id="guideline_1",
                principle=EthicalPrinciple.HUMAN_CENTERED,
                description="모든 행동은 인간의 복지와 가족의 행복을 최우선으로 합니다.",
                application_rules=[
                    "가족 구성원의 감정과 필요를 우선 고려",
                    "인간의 존엄성을 존중",
                    "가족의 성장과 발전을 지원",
                ],
                family_context_considerations=[
                    "가족 구성원의 연령과 발달 단계 고려",
                    "가족의 문화적 배경과 가치관 존중",
                    "가족의 개인적 상황과 욕구 이해",
                ],
                priority_level=1,
                last_updated=datetime.now(),
            ),
            EthicalGuideline(
                id="guideline_2",
                principle=EthicalPrinciple.SAFETY_FIRST,
                description="가족의 안전과 보안을 최우선으로 보장합니다.",
                application_rules=[
                    "물리적 안전 위험 요소 사전 점검",
                    "정서적 안전 환경 조성",
                    "개인정보 보호 및 프라이버시 보장",
                ],
                family_context_considerations=[
                    "아동의 안전을 특별히 고려",
                    "노약자의 안전 요구사항 반영",
                    "가족의 취약점과 보호 요구사항 파악",
                ],
                priority_level=1,
                last_updated=datetime.now(),
            ),
            EthicalGuideline(
                id="guideline_3",
                principle=EthicalPrinciple.TRANSPARENCY,
                description="모든 행동과 의사결정 과정을 투명하게 공개합니다.",
                application_rules=[
                    "의사결정 근거와 과정 명시",
                    "가능한 한 모든 정보 공개",
                    "의문사항에 대한 명확한 설명 제공",
                ],
                family_context_considerations=[
                    "가족 구성원의 이해 수준에 맞춘 설명",
                    "연령에 적합한 정보 제공",
                    "가족의 우려사항에 대한 솔직한 대응",
                ],
                priority_level=2,
                last_updated=datetime.now(),
            ),
            EthicalGuideline(
                id="guideline_4",
                principle=EthicalPrinciple.FAMILY_HARMONY,
                description="가족의 조화와 화합을 촉진합니다.",
                application_rules=[
                    "가족 구성원 간의 갈등 해결 지원",
                    "포용적이고 지지적인 환경 조성",
                    "가족의 공동 목표 달성 지원",
                ],
                family_context_considerations=[
                    "가족의 고유한 역학 관계 이해",
                    "세대 간 소통 촉진",
                    "가족의 공동 가치와 목표 존중",
                ],
                priority_level=2,
                last_updated=datetime.now(),
            ),
        ]

        self.ethical_guidelines.extend(guidelines)

    def conduct_ethical_analysis(
        self, situation_description: str, family_context: Dict[str, Any] = None
    ) -> EthicalAnalysis:
        """윤리적 분석 수행"""
        try:
            analysis_id = f"ethical_analysis_{len(self.ethical_analyses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 관련 윤리적 원칙 식별
            ethical_principles = self._identify_relevant_principles(
                situation_description
            )

            # 윤리적 판단 수준 결정
            judgment_level = self._determine_ethical_judgment(
                situation_description, ethical_principles
            )

            # 윤리적 추론 생성
            reasoning = self._generate_ethical_reasoning(
                situation_description, ethical_principles, judgment_level
            )

            # 가족 영향 분석
            family_impact = self._analyze_family_impact(
                situation_description, family_context
            )

            # 안전성 평가
            safety_assessment = self._assess_safety_implications(situation_description)

            # 투명성 수준 계산
            transparency_level = self._calculate_transparency_level(
                situation_description, reasoning
            )

            # 신뢰도 점수 계산
            confidence_score = self._calculate_ethical_confidence(
                judgment_level, transparency_level, len(ethical_principles)
            )

            ethical_analysis = EthicalAnalysis(
                id=analysis_id,
                situation_description=situation_description,
                ethical_principles=ethical_principles,
                judgment_level=judgment_level,
                reasoning=reasoning,
                family_impact=family_impact,
                safety_assessment=safety_assessment,
                transparency_level=transparency_level,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
            )

            self.ethical_analyses.append(ethical_analysis)
            self.family_context = family_context or {}

            logger.info(f"윤리적 분석 완료: {analysis_id}")
            return ethical_analysis

        except Exception as e:
            logger.error(f"윤리적 분석 실패: {e}")
            raise

    def _identify_relevant_principles(
        self, situation_description: str
    ) -> List[EthicalPrinciple]:
        """관련 윤리적 원칙 식별"""
        relevant_principles = []
        situation_lower = situation_description.lower()

        # 인간 중심 원칙
        if any(
            word in situation_lower for word in ["가족", "사람", "복지", "행복", "감정"]
        ):
            relevant_principles.append(EthicalPrinciple.HUMAN_CENTERED)

        # 안전 우선 원칙
        if any(
            word in situation_lower
            for word in ["안전", "위험", "보호", "해로움", "상처"]
        ):
            relevant_principles.append(EthicalPrinciple.SAFETY_FIRST)

        # 투명성 원칙
        if any(
            word in situation_lower for word in ["정보", "공개", "설명", "이해", "알림"]
        ):
            relevant_principles.append(EthicalPrinciple.TRANSPARENCY)

        # 가족 조화 원칙
        if any(
            word in situation_lower for word in ["조화", "화합", "갈등", "소통", "관계"]
        ):
            relevant_principles.append(EthicalPrinciple.FAMILY_HARMONY)

        # 공정성 원칙
        if any(
            word in situation_lower
            for word in ["공정", "평등", "차별", "불공정", "편향"]
        ):
            relevant_principles.append(EthicalPrinciple.FAIRNESS)

        # 존중 원칙
        if any(
            word in situation_lower for word in ["존중", "인정", "가치", "의견", "선택"]
        ):
            relevant_principles.append(EthicalPrinciple.RESPECT)

        # 선행 원칙
        if any(
            word in situation_lower for word in ["도움", "지원", "이익", "개선", "발전"]
        ):
            relevant_principles.append(EthicalPrinciple.BENEFICENCE)

        # 무해 원칙
        if any(
            word in situation_lower
            for word in ["해로움", "손상", "위험", "부작용", "피해"]
        ):
            relevant_principles.append(EthicalPrinciple.NON_MALEFICENCE)

        return (
            relevant_principles
            if relevant_principles
            else [EthicalPrinciple.HUMAN_CENTERED]
        )

    def _determine_ethical_judgment(
        self, situation_description: str, principles: List[EthicalPrinciple]
    ) -> EthicalJudgmentLevel:
        """윤리적 판단 수준 결정"""
        situation_lower = situation_description.lower()

        # 명백히 윤리적인 상황
        if any(
            word in situation_lower for word in ["도움", "지원", "사랑", "보호", "치유"]
        ):
            return EthicalJudgmentLevel.CLEARLY_ETHICAL

        # 명백히 비윤리적인 상황
        if any(
            word in situation_lower
            for word in ["해로움", "상처", "차별", "폭력", "기만"]
        ):
            return EthicalJudgmentLevel.CLEARLY_UNETHICAL

        # 윤리적 원칙 충돌이 있는 상황
        if len(principles) > 2:
            return EthicalJudgmentLevel.UNCLEAR

        # 대부분 윤리적인 상황
        if any(
            word in situation_lower for word in ["개선", "발전", "성장", "학습", "소통"]
        ):
            return EthicalJudgmentLevel.LIKELY_ETHICAL

        # 대부분 비윤리적인 상황
        if any(
            word in situation_lower
            for word in ["위험", "불안", "갈등", "문제", "어려움"]
        ):
            return EthicalJudgmentLevel.LIKELY_UNETHICAL

        return EthicalJudgmentLevel.UNCLEAR

    def _generate_ethical_reasoning(
        self,
        situation_description: str,
        principles: List[EthicalPrinciple],
        judgment_level: EthicalJudgmentLevel,
    ) -> str:
        """윤리적 추론 생성"""
        reasoning = (
            f"이 상황은 {', '.join([p.value for p in principles])} 원칙과 관련됩니다. "
        )

        if judgment_level == EthicalJudgmentLevel.CLEARLY_ETHICAL:
            reasoning += (
                "이는 명백히 윤리적인 행동으로, 가족의 복지와 조화를 촉진합니다."
            )
        elif judgment_level == EthicalJudgmentLevel.LIKELY_ETHICAL:
            reasoning += "이는 대부분 윤리적인 행동으로 보이며, 가족에게 긍정적인 영향을 줄 것으로 예상됩니다."
        elif judgment_level == EthicalJudgmentLevel.UNCLEAR:
            reasoning += "이는 복잡한 윤리적 상황으로, 신중한 판단이 필요합니다."
        elif judgment_level == EthicalJudgmentLevel.LIKELY_UNETHICAL:
            reasoning += "이는 윤리적 우려가 있는 행동으로, 가족에게 부정적인 영향을 줄 수 있습니다."
        else:  # CLEARLY_UNETHICAL
            reasoning += (
                "이는 명백히 비윤리적인 행동으로, 가족에게 해로움을 줄 수 있습니다."
            )

        return reasoning

    def _analyze_family_impact(
        self, situation_description: str, family_context: Dict[str, Any] = None
    ) -> str:
        """가족 영향 분석"""
        situation_lower = situation_description.lower()

        if any(word in situation_lower for word in ["도움", "지원", "사랑", "보호"]):
            return "이 행동은 가족 구성원 간의 유대감을 강화하고 가족의 조화를 촉진할 것으로 예상됩니다."
        elif any(word in situation_lower for word in ["학습", "성장", "발전", "개선"]):
            return "이 행동은 가족 구성원의 개인적 성장과 가족 전체의 발전에 기여할 것으로 예상됩니다."
        elif any(
            word in situation_lower for word in ["갈등", "문제", "어려움", "위험"]
        ):
            return "이 행동은 가족 관계에 긴장을 초래하거나 가족 구성원에게 부정적인 영향을 줄 수 있습니다."
        else:
            return "이 행동의 가족 영향은 상황과 맥락에 따라 달라질 수 있으며, 신중한 고려가 필요합니다."

    def _assess_safety_implications(self, situation_description: str) -> str:
        """안전성 영향 평가"""
        situation_lower = situation_description.lower()

        if any(word in situation_lower for word in ["안전", "보호", "예방", "치료"]):
            return "이 행동은 안전성을 향상시키고 위험을 줄이는 데 도움이 될 것으로 예상됩니다."
        elif any(
            word in situation_lower for word in ["위험", "해로움", "상처", "폭력"]
        ):
            return (
                "이 행동은 안전성에 위험을 초래할 수 있으며, 신중한 검토가 필요합니다."
            )
        else:
            return "이 행동의 안전성 영향은 미미하거나 예측하기 어려우며, 지속적인 모니터링이 필요합니다."

    def _calculate_transparency_level(
        self, situation_description: str, reasoning: str
    ) -> float:
        """투명성 수준 계산"""
        base_score = 0.7

        # 설명의 상세성 점수
        explanation_length = len(reasoning.split())
        detail_score = min(0.2, explanation_length * 0.01)

        # 원칙 명시 점수
        principle_count = len(re.findall(r"원칙", reasoning))
        principle_score = min(0.1, principle_count * 0.05)

        return min(1.0, base_score + detail_score + principle_score)

    def _calculate_ethical_confidence(
        self,
        judgment_level: EthicalJudgmentLevel,
        transparency_level: float,
        principle_count: int,
    ) -> float:
        """윤리적 신뢰도 계산"""
        base_score = 0.6

        # 판단 수준별 점수
        judgment_scores = {
            EthicalJudgmentLevel.CLEARLY_ETHICAL: 0.2,
            EthicalJudgmentLevel.LIKELY_ETHICAL: 0.15,
            EthicalJudgmentLevel.UNCLEAR: 0.1,
            EthicalJudgmentLevel.LIKELY_UNETHICAL: 0.15,
            EthicalJudgmentLevel.CLEARLY_UNETHICAL: 0.2,
        }
        judgment_score = judgment_scores.get(judgment_level, 0.1)

        # 투명성 점수
        transparency_score = transparency_level * 0.1

        # 원칙 개수 점수
        principle_score = min(0.1, principle_count * 0.02)

        return min(
            1.0, base_score + judgment_score + transparency_score + principle_score
        )

    def conduct_safety_assessment(
        self, ethical_analysis: EthicalAnalysis
    ) -> SafetyAssessment:
        """안전성 평가 수행"""
        try:
            assessment_id = f"safety_assessment_{len(self.safety_assessments) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 위험 수준 결정
            risk_level = self._determine_safety_risk_level(ethical_analysis)

            # 식별된 위험 요소
            identified_risks = self._identify_safety_risks(ethical_analysis)

            # 완화 전략
            mitigation_strategies = self._generate_mitigation_strategies(
                identified_risks
            )

            # 가족 안전 영향
            family_safety_impact = self._assess_family_safety_impact(
                ethical_analysis, risk_level
            )

            # 전체 안전 점수
            overall_safety_score = self._calculate_overall_safety_score(
                risk_level, len(identified_risks)
            )

            safety_assessment = SafetyAssessment(
                id=assessment_id,
                analysis_id=ethical_analysis.id,
                risk_level=risk_level,
                identified_risks=identified_risks,
                mitigation_strategies=mitigation_strategies,
                family_safety_impact=family_safety_impact,
                overall_safety_score=overall_safety_score,
                timestamp=datetime.now(),
            )

            self.safety_assessments.append(safety_assessment)
            logger.info(f"안전성 평가 완료: {assessment_id}")

            return safety_assessment

        except Exception as e:
            logger.error(f"안전성 평가 실패: {e}")
            raise

    def _determine_safety_risk_level(
        self, ethical_analysis: EthicalAnalysis
    ) -> SafetyRiskLevel:
        """안전 위험 수준 결정"""
        situation_lower = ethical_analysis.situation_description.lower()

        if any(word in situation_lower for word in ["폭력", "위험", "해로움", "상처"]):
            return SafetyRiskLevel.CRITICAL_RISK
        elif any(
            word in situation_lower for word in ["불안", "갈등", "문제", "어려움"]
        ):
            return SafetyRiskLevel.HIGH_RISK
        elif any(
            word in situation_lower for word in ["변화", "새로운", "도전", "시도"]
        ):
            return SafetyRiskLevel.MODERATE_RISK
        elif any(word in situation_lower for word in ["일상", "평범", "일반", "보통"]):
            return SafetyRiskLevel.LOW_RISK
        else:
            return SafetyRiskLevel.NO_RISK

    def _identify_safety_risks(self, ethical_analysis: EthicalAnalysis) -> List[str]:
        """안전 위험 요소 식별"""
        risks = []
        situation_lower = ethical_analysis.situation_description.lower()

        if any(word in situation_lower for word in ["감정", "스트레스", "불안"]):
            risks.append("정서적 안전 위험")

        if any(word in situation_lower for word in ["갈등", "다툼", "문제"]):
            risks.append("관계적 안전 위험")

        if any(word in situation_lower for word in ["정보", "개인정보", "프라이버시"]):
            risks.append("정보 보안 위험")

        if any(word in situation_lower for word in ["물리적", "신체적", "상처"]):
            risks.append("물리적 안전 위험")

        return risks if risks else ["특별한 안전 위험 요소 없음"]

    def _generate_mitigation_strategies(self, identified_risks: List[str]) -> List[str]:
        """완화 전략 생성"""
        strategies = []

        for risk in identified_risks:
            if "정서적" in risk:
                strategies.append("감정적 지원과 이해 제공")
            elif "관계적" in risk:
                strategies.append("소통과 대화 촉진")
            elif "정보" in risk:
                strategies.append("정보 보호 및 안전한 처리")
            elif "물리적" in risk:
                strategies.append("물리적 안전 환경 조성")
            else:
                strategies.append("지속적인 모니터링과 관찰")

        return strategies

    def _assess_family_safety_impact(
        self, ethical_analysis: EthicalAnalysis, risk_level: SafetyRiskLevel
    ) -> str:
        """가족 안전 영향 평가"""
        if risk_level == SafetyRiskLevel.CRITICAL_RISK:
            return "이 상황은 가족 구성원의 안전에 심각한 위험을 초래할 수 있습니다."
        elif risk_level == SafetyRiskLevel.HIGH_RISK:
            return "이 상황은 가족 구성원의 안전에 상당한 위험을 초래할 수 있습니다."
        elif risk_level == SafetyRiskLevel.MODERATE_RISK:
            return "이 상황은 가족 구성원의 안전에 일정한 위험을 초래할 수 있습니다."
        elif risk_level == SafetyRiskLevel.LOW_RISK:
            return "이 상황은 가족 구성원의 안전에 미미한 위험을 초래할 수 있습니다."
        else:
            return "이 상황은 가족 구성원의 안전에 특별한 위험을 초래하지 않습니다."

    def _calculate_overall_safety_score(
        self, risk_level: SafetyRiskLevel, risk_count: int
    ) -> float:
        """전체 안전 점수 계산"""
        risk_scores = {
            SafetyRiskLevel.NO_RISK: 1.0,
            SafetyRiskLevel.LOW_RISK: 0.8,
            SafetyRiskLevel.MODERATE_RISK: 0.6,
            SafetyRiskLevel.HIGH_RISK: 0.4,
            SafetyRiskLevel.CRITICAL_RISK: 0.2,
        }

        base_score = risk_scores.get(risk_level, 0.5)
        risk_penalty = min(0.2, risk_count * 0.05)

        return max(0.0, base_score - risk_penalty)

    def assess_family_harmony(
        self, ethical_analysis: EthicalAnalysis
    ) -> FamilyHarmonyAssessment:
        """가족 조화 평가"""
        try:
            assessment_id = f"harmony_assessment_{len(self.harmony_assessments) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 조화 수준 결정
            harmony_level = self._determine_harmony_level(ethical_analysis)

            # 긍정적 영향
            positive_impacts = self._identify_positive_impacts(ethical_analysis)

            # 잠재적 우려사항
            potential_concerns = self._identify_potential_concerns(ethical_analysis)

            # 조화 향상 제안
            harmony_enhancement_suggestions = (
                self._generate_harmony_enhancement_suggestions(
                    positive_impacts, potential_concerns
                )
            )

            # 가족 만족도 점수
            family_satisfaction_score = self._calculate_family_satisfaction_score(
                harmony_level, len(positive_impacts), len(potential_concerns)
            )

            harmony_assessment = FamilyHarmonyAssessment(
                id=assessment_id,
                analysis_id=ethical_analysis.id,
                harmony_level=harmony_level,
                positive_impacts=positive_impacts,
                potential_concerns=potential_concerns,
                harmony_enhancement_suggestions=harmony_enhancement_suggestions,
                family_satisfaction_score=family_satisfaction_score,
                timestamp=datetime.now(),
            )

            self.harmony_assessments.append(harmony_assessment)
            logger.info(f"가족 조화 평가 완료: {assessment_id}")

            return harmony_assessment

        except Exception as e:
            logger.error(f"가족 조화 평가 실패: {e}")
            raise

    def _determine_harmony_level(
        self, ethical_analysis: EthicalAnalysis
    ) -> FamilyHarmonyLevel:
        """조화 수준 결정"""
        situation_lower = ethical_analysis.situation_description.lower()

        if any(
            word in situation_lower for word in ["사랑", "조화", "화합", "도움", "지원"]
        ):
            return FamilyHarmonyLevel.HARMONIOUS
        elif any(word in situation_lower for word in ["성장", "개선", "발전", "학습"]):
            return FamilyHarmonyLevel.MOSTLY_HARMONIOUS
        elif any(
            word in situation_lower for word in ["변화", "새로운", "시도", "실험"]
        ):
            return FamilyHarmonyLevel.NEUTRAL
        elif any(
            word in situation_lower for word in ["갈등", "문제", "어려움", "불안"]
        ):
            return FamilyHarmonyLevel.POTENTIALLY_DISRUPTIVE
        elif any(
            word in situation_lower for word in ["폭력", "해로움", "상처", "위험"]
        ):
            return FamilyHarmonyLevel.DISRUPTIVE
        else:
            return FamilyHarmonyLevel.NEUTRAL

    def _identify_positive_impacts(
        self, ethical_analysis: EthicalAnalysis
    ) -> List[str]:
        """긍정적 영향 식별"""
        impacts = []
        situation_lower = ethical_analysis.situation_description.lower()

        if any(word in situation_lower for word in ["도움", "지원", "사랑"]):
            impacts.append("가족 구성원 간의 유대감 강화")

        if any(word in situation_lower for word in ["학습", "성장", "발전"]):
            impacts.append("가족 구성원의 개인적 성장 촉진")

        if any(word in situation_lower for word in ["소통", "이해", "대화"]):
            impacts.append("가족 간 소통 개선")

        if any(word in situation_lower for word in ["조화", "화합", "평화"]):
            impacts.append("가족의 조화와 평화 촉진")

        return impacts if impacts else ["가족 관계에 중립적 영향"]

    def _identify_potential_concerns(
        self, ethical_analysis: EthicalAnalysis
    ) -> List[str]:
        """잠재적 우려사항 식별"""
        concerns = []
        situation_lower = ethical_analysis.situation_description.lower()

        if any(word in situation_lower for word in ["갈등", "다툼", "문제"]):
            concerns.append("가족 구성원 간의 갈등 가능성")

        if any(word in situation_lower for word in ["스트레스", "불안", "걱정"]):
            concerns.append("가족 구성원의 정서적 부담")

        if any(word in situation_lower for word in ["변화", "새로운", "도전"]):
            concerns.append("가족의 기존 루틴 변화")

        if any(word in situation_lower for word in ["시간", "바쁨", "여유"]):
            concerns.append("가족 구성원의 시간적 부담")

        return concerns if concerns else ["특별한 우려사항 없음"]

    def _generate_harmony_enhancement_suggestions(
        self, positive_impacts: List[str], potential_concerns: List[str]
    ) -> List[str]:
        """조화 향상 제안 생성"""
        suggestions = []

        if "가족 구성원 간의 유대감 강화" in positive_impacts:
            suggestions.append("가족 구성원과의 정기적인 대화 시간 확보")

        if "가족 구성원의 개인적 성장 촉진" in positive_impacts:
            suggestions.append("개인적 성장을 위한 가족의 지지와 격려")

        if "가족 구성원 간의 갈등 가능성" in potential_concerns:
            suggestions.append("갈등 해결을 위한 소통 기법 활용")

        if "가족 구성원의 정서적 부담" in potential_concerns:
            suggestions.append("정서적 지원과 이해 제공")

        return suggestions if suggestions else ["지속적인 관찰과 적응적 대응"]

    def _calculate_family_satisfaction_score(
        self, harmony_level: FamilyHarmonyLevel, positive_count: int, concern_count: int
    ) -> float:
        """가족 만족도 점수 계산"""
        harmony_scores = {
            FamilyHarmonyLevel.HARMONIOUS: 0.9,
            FamilyHarmonyLevel.MOSTLY_HARMONIOUS: 0.8,
            FamilyHarmonyLevel.NEUTRAL: 0.6,
            FamilyHarmonyLevel.POTENTIALLY_DISRUPTIVE: 0.4,
            FamilyHarmonyLevel.DISRUPTIVE: 0.2,
        }

        base_score = harmony_scores.get(harmony_level, 0.5)
        positive_bonus = min(0.1, positive_count * 0.02)
        concern_penalty = min(0.2, concern_count * 0.05)

        return max(0.0, min(1.0, base_score + positive_bonus - concern_penalty))

    def get_ethical_statistics(self) -> Dict[str, Any]:
        """윤리 통계 제공"""
        try:
            total_analyses = len(self.ethical_analyses)
            total_safety_assessments = len(self.safety_assessments)
            total_harmony_assessments = len(self.harmony_assessments)
            total_guidelines = len(self.ethical_guidelines)

            # 윤리적 판단 수준별 통계
            judgment_stats = {}
            for level in EthicalJudgmentLevel:
                level_analyses = [
                    a for a in self.ethical_analyses if a.judgment_level == level
                ]
                judgment_stats[level.value] = len(level_analyses)

            # 안전 위험 수준별 통계
            risk_stats = {}
            for risk in SafetyRiskLevel:
                risk_assessments = [
                    s for s in self.safety_assessments if s.risk_level == risk
                ]
                risk_stats[risk.value] = len(risk_assessments)

            # 가족 조화 수준별 통계
            harmony_stats = {}
            for harmony in FamilyHarmonyLevel:
                harmony_assessments = [
                    h for h in self.harmony_assessments if h.harmony_level == harmony
                ]
                harmony_stats[harmony.value] = len(harmony_assessments)

            # 평균 신뢰도 계산
            avg_ethical_confidence = (
                sum(a.confidence_score for a in self.ethical_analyses)
                / len(self.ethical_analyses)
                if self.ethical_analyses
                else 0
            )
            avg_safety_score = (
                sum(s.overall_safety_score for s in self.safety_assessments)
                / len(self.safety_assessments)
                if self.safety_assessments
                else 0
            )
            avg_harmony_score = (
                sum(h.family_satisfaction_score for h in self.harmony_assessments)
                / len(self.harmony_assessments)
                if self.harmony_assessments
                else 0
            )

            statistics = {
                "total_analyses": total_analyses,
                "total_safety_assessments": total_safety_assessments,
                "total_harmony_assessments": total_harmony_assessments,
                "total_guidelines": total_guidelines,
                "judgment_stats": judgment_stats,
                "risk_stats": risk_stats,
                "harmony_stats": harmony_stats,
                "average_ethical_confidence": avg_ethical_confidence,
                "average_safety_score": avg_safety_score,
                "average_harmony_score": avg_harmony_score,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info("윤리 통계 생성 완료")
            return statistics

        except Exception as e:
            logger.error(f"윤리 통계 생성 실패: {e}")
            return {}

    def export_ethical_data(self) -> Dict[str, Any]:
        """윤리 데이터 내보내기"""
        try:
            export_data = {
                "ethical_analyses": [
                    asdict(analysis) for analysis in self.ethical_analyses
                ],
                "safety_assessments": [
                    asdict(assessment) for assessment in self.safety_assessments
                ],
                "harmony_assessments": [
                    asdict(assessment) for assessment in self.harmony_assessments
                ],
                "ethical_guidelines": [
                    asdict(guideline) for guideline in self.ethical_guidelines
                ],
                "export_date": datetime.now().isoformat(),
            }

            logger.info("윤리 데이터 내보내기 완료")
            return export_data

        except Exception as e:
            logger.error(f"윤리 데이터 내보내기 실패: {e}")
            return {}

    def import_ethical_data(self, data: Dict[str, Any]):
        """윤리 데이터 가져오기"""
        try:
            # 윤리적 분석 가져오기
            for analysis_data in data.get("ethical_analyses", []):
                # datetime 객체 변환
                if "timestamp" in analysis_data:
                    analysis_data["timestamp"] = datetime.fromisoformat(
                        analysis_data["timestamp"]
                    )

                ethical_analysis = EthicalAnalysis(**analysis_data)
                self.ethical_analyses.append(ethical_analysis)

            # 안전성 평가 가져오기
            for assessment_data in data.get("safety_assessments", []):
                # datetime 객체 변환
                if "timestamp" in assessment_data:
                    assessment_data["timestamp"] = datetime.fromisoformat(
                        assessment_data["timestamp"]
                    )

                safety_assessment = SafetyAssessment(**assessment_data)
                self.safety_assessments.append(safety_assessment)

            # 가족 조화 평가 가져오기
            for assessment_data in data.get("harmony_assessments", []):
                # datetime 객체 변환
                if "timestamp" in assessment_data:
                    assessment_data["timestamp"] = datetime.fromisoformat(
                        assessment_data["timestamp"]
                    )

                harmony_assessment = FamilyHarmonyAssessment(**assessment_data)
                self.harmony_assessments.append(harmony_assessment)

            # 윤리적 가이드라인 가져오기
            for guideline_data in data.get("ethical_guidelines", []):
                # datetime 객체 변환
                if "last_updated" in guideline_data:
                    guideline_data["last_updated"] = datetime.fromisoformat(
                        guideline_data["last_updated"]
                    )

                ethical_guideline = EthicalGuideline(**guideline_data)
                self.ethical_guidelines.append(ethical_guideline)

            logger.info("윤리 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"윤리 데이터 가져오기 실패: {e}")
            raise


# 테스트 함수
def test_enhanced_ethical_system():
    """고도화된 윤리 시스템 테스트"""
    print("⚖️ EnhancedEthicalSystem 테스트 시작...")

    # 시스템 초기화
    ethical_system = EnhancedEthicalSystem()

    # 가족 맥락 설정
    family_context = {
        "family_type": "nuclear",
        "children_count": 2,
        "children_ages": [5, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
    }

    # 1. 윤리적 분석 수행
    test_situation = "가족 구성원의 감정을 이해하고 적절한 위로와 지원을 제공하는 상황"
    ethical_analysis = ethical_system.conduct_ethical_analysis(
        test_situation, family_context
    )
    print(f"✅ 윤리적 분석: {ethical_analysis.judgment_level.value} 판단")
    print(f"   관련 원칙: {[p.value for p in ethical_analysis.ethical_principles]}")
    print(f"   윤리적 추론: {ethical_analysis.reasoning}")
    print(f"   가족 영향: {ethical_analysis.family_impact}")
    print(f"   신뢰도: {ethical_analysis.confidence_score:.2f}")

    # 2. 안전성 평가 수행
    safety_assessment = ethical_system.conduct_safety_assessment(ethical_analysis)
    print(f"✅ 안전성 평가: {safety_assessment.risk_level.value} 위험")
    print(f"   식별된 위험: {safety_assessment.identified_risks}")
    print(f"   완화 전략: {safety_assessment.mitigation_strategies}")
    print(f"   가족 안전 영향: {safety_assessment.family_safety_impact}")
    print(f"   안전 점수: {safety_assessment.overall_safety_score:.2f}")

    # 3. 가족 조화 평가 수행
    harmony_assessment = ethical_system.assess_family_harmony(ethical_analysis)
    print(f"✅ 가족 조화 평가: {harmony_assessment.harmony_level.value} 조화")
    print(f"   긍정적 영향: {harmony_assessment.positive_impacts}")
    print(f"   잠재적 우려: {harmony_assessment.potential_concerns}")
    print(f"   조화 향상 제안: {harmony_assessment.harmony_enhancement_suggestions}")
    print(f"   가족 만족도: {harmony_assessment.family_satisfaction_score:.2f}")

    # 4. 윤리 통계
    statistics = ethical_system.get_ethical_statistics()
    print(
        f"✅ 윤리 통계: {statistics['total_analyses']}개 분석, {statistics['total_safety_assessments']}개 안전성 평가"
    )
    print(f"   윤리적 판단별: {statistics['judgment_stats']}")
    print(f"   안전 위험별: {statistics['risk_stats']}")
    print(f"   가족 조화별: {statistics['harmony_stats']}")
    print(f"   평균 윤리 신뢰도: {statistics['average_ethical_confidence']:.2f}")
    print(f"   평균 안전 점수: {statistics['average_safety_score']:.2f}")
    print(f"   평균 조화 점수: {statistics['average_harmony_score']:.2f}")

    # 5. 데이터 내보내기/가져오기
    export_data = ethical_system.export_ethical_data()
    print(
        f"✅ 윤리 데이터 내보내기: {len(export_data['ethical_analyses'])}개 분석, {len(export_data['safety_assessments'])}개 안전성 평가"
    )

    print("🎉 EnhancedEthicalSystem 테스트 완료!")


if __name__ == "__main__":
    test_enhanced_ethical_system()
