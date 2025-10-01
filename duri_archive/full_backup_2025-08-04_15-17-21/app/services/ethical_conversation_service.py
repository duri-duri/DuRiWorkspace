#!/usr/bin/env python3
"""
EthicalConversationSystem - Phase 12.1
윤리적 대화 시스템

목적:
- 가족 중심의 윤리적 판단과 대화
- 도덕적 딜레마 해결
- 가족 가치 기반의 윤리적 조언
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


class EthicalPrinciple(Enum):
    """윤리 원칙"""

    FAMILY_HARMONY = "family_harmony"
    LOVE_AND_CARE = "love_and_care"
    HONESTY = "honesty"
    RESPECT = "respect"
    RESPONSIBILITY = "responsibility"
    FAIRNESS = "fairness"
    GROWTH = "growth"


class DilemmaType(Enum):
    """딜레마 유형"""

    FAMILY_CONFLICT = "family_conflict"
    HONESTY_VS_HARM = "honesty_vs_harm"
    INDIVIDUAL_VS_FAMILY = "individual_vs_family"
    GROWTH_VS_STABILITY = "growth_vs_stability"
    TRADITION_VS_CHANGE = "tradition_vs_change"


class EthicalJudgment(Enum):
    """윤리적 판단"""

    CLEARLY_ETHICAL = "clearly_ethical"
    ETHICAL_WITH_CONDITIONS = "ethical_with_conditions"
    ETHICAL_DILEMMA = "ethical_dilemma"
    POTENTIALLY_UNETHICAL = "potentially_unethical"
    CLEARLY_UNETHICAL = "clearly_unethical"


@dataclass
class EthicalAnalysis:
    """윤리적 분석"""

    id: str
    dilemma_description: str
    dilemma_type: DilemmaType
    involved_principles: List[EthicalPrinciple]
    ethical_judgment: EthicalJudgment
    reasoning: str
    recommended_action: str
    alternative_actions: List[str]
    family_impact: str
    confidence_score: float
    timestamp: datetime


@dataclass
class EthicalConversation:
    """윤리적 대화"""

    id: str
    conversation_topic: str
    family_context: Dict[str, Any]
    ethical_analysis: EthicalAnalysis
    conversation_flow: List[str]
    emotional_support: str
    guidance_provided: str
    follow_up_actions: List[str]
    timestamp: datetime


class EthicalConversationSystem:
    """윤리적 대화 시스템"""

    def __init__(self):
        self.ethical_analyses: List[EthicalAnalysis] = []
        self.ethical_conversations: List[EthicalConversation] = []
        self.family_values: List[str] = ["사랑", "소통", "성장", "창의성", "조화"]

        logger.info("EthicalConversationSystem 초기화 완료")

    def analyze_ethical_dilemma(
        self, dilemma_description: str, family_context: Dict[str, Any]
    ) -> EthicalAnalysis:
        """윤리적 딜레마 분석"""
        analysis_id = f"ethical_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 딜레마 유형 판단
        dilemma_type = self._determine_dilemma_type(dilemma_description)

        # 관련 윤리 원칙 식별
        involved_principles = self._identify_involved_principles(
            dilemma_description, family_context
        )

        # 윤리적 판단
        ethical_judgment = self._make_ethical_judgment(
            dilemma_description, involved_principles, family_context
        )

        # 추론 과정
        reasoning = self._generate_ethical_reasoning(
            dilemma_description, involved_principles, family_context
        )

        # 권장 행동
        recommended_action = self._generate_recommended_action(
            dilemma_description, ethical_judgment, family_context
        )

        # 대안 행동들
        alternative_actions = self._generate_alternative_actions(
            dilemma_description, ethical_judgment, family_context
        )

        # 가족 영향
        family_impact = self._assess_family_impact(recommended_action, family_context)

        # 신뢰도 점수
        confidence_score = self._calculate_confidence_score(
            ethical_judgment, involved_principles, family_context
        )

        analysis = EthicalAnalysis(
            id=analysis_id,
            dilemma_description=dilemma_description,
            dilemma_type=dilemma_type,
            involved_principles=involved_principles,
            ethical_judgment=ethical_judgment,
            reasoning=reasoning,
            recommended_action=recommended_action,
            alternative_actions=alternative_actions,
            family_impact=family_impact,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
        )

        self.ethical_analyses.append(analysis)
        logger.info(f"윤리적 딜레마 분석 완료: {ethical_judgment.value}")

        return analysis

    def _determine_dilemma_type(self, dilemma_description: str) -> DilemmaType:
        """딜레마 유형 판단"""
        description_lower = dilemma_description.lower()

        if any(
            word in description_lower
            for word in ["가족", "부모", "자식", "형제", "갈등"]
        ):
            return DilemmaType.FAMILY_CONFLICT
        elif any(
            word in description_lower for word in ["거짓말", "진실", "말하다", "숨기다"]
        ):
            return DilemmaType.HONESTY_VS_HARM
        elif any(
            word in description_lower for word in ["개인", "자신", "가족", "이기적"]
        ):
            return DilemmaType.INDIVIDUAL_VS_FAMILY
        elif any(
            word in description_lower for word in ["성장", "변화", "안정", "현상유지"]
        ):
            return DilemmaType.GROWTH_VS_STABILITY
        elif any(
            word in description_lower for word in ["전통", "새로운", "변화", "습관"]
        ):
            return DilemmaType.TRADITION_VS_CHANGE
        else:
            return DilemmaType.FAMILY_CONFLICT  # 기본값

    def _identify_involved_principles(
        self, dilemma_description: str, family_context: Dict[str, Any]
    ) -> List[EthicalPrinciple]:
        """관련 윤리 원칙 식별"""
        principles = []
        description_lower = dilemma_description.lower()

        # 가족 조화
        if any(word in description_lower for word in ["가족", "조화", "화합", "평화"]):
            principles.append(EthicalPrinciple.FAMILY_HARMONY)

        # 사랑과 돌봄
        if any(word in description_lower for word in ["사랑", "돌봄", "관심", "배려"]):
            principles.append(EthicalPrinciple.LOVE_AND_CARE)

        # 정직
        if any(
            word in description_lower for word in ["정직", "진실", "거짓말", "솔직"]
        ):
            principles.append(EthicalPrinciple.HONESTY)

        # 존중
        if any(word in description_lower for word in ["존중", "인정", "이해", "수용"]):
            principles.append(EthicalPrinciple.RESPECT)

        # 책임
        if any(word in description_lower for word in ["책임", "의무", "약속", "맡다"]):
            principles.append(EthicalPrinciple.RESPONSIBILITY)

        # 공정성
        if any(
            word in description_lower for word in ["공정", "평등", "차별", "불공정"]
        ):
            principles.append(EthicalPrinciple.FAIRNESS)

        # 성장
        if any(word in description_lower for word in ["성장", "발전", "학습", "변화"]):
            principles.append(EthicalPrinciple.GROWTH)

        # 기본 원칙 추가
        if not principles:
            principles.extend(
                [EthicalPrinciple.FAMILY_HARMONY, EthicalPrinciple.LOVE_AND_CARE]
            )

        return list(set(principles))  # 중복 제거

    def _make_ethical_judgment(
        self,
        dilemma_description: str,
        principles: List[EthicalPrinciple],
        family_context: Dict[str, Any],
    ) -> EthicalJudgment:
        """윤리적 판단"""
        # 가족 조화와 사랑이 우선인 경우
        if (
            EthicalPrinciple.FAMILY_HARMONY in principles
            and EthicalPrinciple.LOVE_AND_CARE in principles
        ):
            return EthicalJudgment.CLEARLY_ETHICAL

        # 정직과 가족 조화가 충돌하는 경우
        if (
            EthicalPrinciple.HONESTY in principles
            and EthicalPrinciple.FAMILY_HARMONY in principles
        ):
            return EthicalJudgment.ETHICAL_DILEMMA

        # 개인과 가족이 충돌하는 경우
        if (
            EthicalPrinciple.RESPECT in principles
            and EthicalPrinciple.FAMILY_HARMONY in principles
        ):
            return EthicalJudgment.ETHICAL_WITH_CONDITIONS

        # 성장과 안정이 충돌하는 경우
        if (
            EthicalPrinciple.GROWTH in principles
            and EthicalPrinciple.FAMILY_HARMONY in principles
        ):
            return EthicalJudgment.ETHICAL_WITH_CONDITIONS

        # 기본적으로 가족 중심
        return EthicalJudgment.CLEARLY_ETHICAL

    def _generate_ethical_reasoning(
        self,
        dilemma_description: str,
        principles: List[EthicalPrinciple],
        family_context: Dict[str, Any],
    ) -> str:
        """윤리적 추론 생성"""
        reasoning = f"이 상황을 분석해보면, {', '.join([p.value for p in principles])} 원칙이 관련되어 있습니다. "

        if EthicalPrinciple.FAMILY_HARMONY in principles:
            reasoning += "가족의 조화와 평화가 최우선이어야 합니다. "

        if EthicalPrinciple.LOVE_AND_CARE in principles:
            reasoning += "서로를 사랑하고 돌보는 마음이 중요합니다. "

        if EthicalPrinciple.HONESTY in principles:
            reasoning += "정직함은 가족 간의 신뢰를 위한 기반입니다. "

        reasoning += f"가족의 가치인 {', '.join(self.family_values)}을 고려할 때, "
        reasoning += (
            "모든 구성원이 함께 성장할 수 있는 방향을 선택하는 것이 좋겠습니다."
        )

        return reasoning

    def _generate_recommended_action(
        self,
        dilemma_description: str,
        judgment: EthicalJudgment,
        family_context: Dict[str, Any],
    ) -> str:
        """권장 행동 생성"""
        if judgment == EthicalJudgment.CLEARLY_ETHICAL:
            return "가족과 함께 대화를 나누고, 서로의 마음을 이해하려고 노력하세요."
        elif judgment == EthicalJudgment.ETHICAL_WITH_CONDITIONS:
            return "가족의 조화를 유지하면서도 개인의 성장을 고려한 균형잡힌 접근을 시도해보세요."
        elif judgment == EthicalJudgment.ETHICAL_DILEMMA:
            return "이 상황은 복잡하므로, 가족과 함께 충분한 대화를 통해 최선의 해결책을 찾아보세요."
        else:
            return "가족의 가치를 우선으로 하되, 모든 구성원의 의견을 경청하는 자세가 중요합니다."

    def _generate_alternative_actions(
        self,
        dilemma_description: str,
        judgment: EthicalJudgment,
        family_context: Dict[str, Any],
    ) -> List[str]:
        """대안 행동들 생성"""
        alternatives = []

        if judgment == EthicalJudgment.ETHICAL_DILEMMA:
            alternatives.extend(
                [
                    "가족 회의를 통해 모든 구성원의 의견을 듣기",
                    "단계적으로 변화를 시도해보기",
                    "전문가의 조언을 구하기",
                ]
            )
        else:
            alternatives.extend(
                [
                    "서로의 입장을 바꿔서 생각해보기",
                    "시간을 두고 천천히 결정하기",
                    "가족의 가치를 다시 한번 확인하기",
                ]
            )

        return alternatives

    def _assess_family_impact(
        self, recommended_action: str, family_context: Dict[str, Any]
    ) -> str:
        """가족 영향 평가"""
        return "이 행동은 가족 간의 소통을 증진시키고, 서로에 대한 이해를 깊게 할 것입니다. 단기적으로는 어려움이 있을 수 있지만, 장기적으로는 가족의 유대감을 강화할 것입니다."

    def _calculate_confidence_score(
        self,
        judgment: EthicalJudgment,
        principles: List[EthicalPrinciple],
        family_context: Dict[str, Any],
    ) -> float:
        """신뢰도 점수 계산"""
        base_score = 0.8

        # 판단 유형에 따른 조정
        if judgment == EthicalJudgment.CLEARLY_ETHICAL:
            base_score += 0.1
        elif judgment == EthicalJudgment.ETHICAL_DILEMMA:
            base_score -= 0.1

        # 원칙 수에 따른 조정
        if len(principles) <= 2:
            base_score += 0.05
        else:
            base_score -= 0.05

        return min(1.0, max(0.0, base_score))

    def conduct_ethical_conversation(
        self, topic: str, family_context: Dict[str, Any]
    ) -> EthicalConversation:
        """윤리적 대화 수행"""
        conversation_id = (
            f"ethical_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # 윤리적 분석
        analysis = self.analyze_ethical_dilemma(topic, family_context)

        # 대화 흐름 생성
        conversation_flow = self._generate_conversation_flow(
            topic, analysis, family_context
        )

        # 감정적 지원
        emotional_support = self._generate_emotional_support(analysis, family_context)

        # 지도 제공
        guidance_provided = self._generate_guidance(analysis, family_context)

        # 후속 행동
        follow_up_actions = self._generate_follow_up_actions(analysis, family_context)

        conversation = EthicalConversation(
            id=conversation_id,
            conversation_topic=topic,
            family_context=family_context,
            ethical_analysis=analysis,
            conversation_flow=conversation_flow,
            emotional_support=emotional_support,
            guidance_provided=guidance_provided,
            follow_up_actions=follow_up_actions,
            timestamp=datetime.now(),
        )

        self.ethical_conversations.append(conversation)
        logger.info(f"윤리적 대화 완료: {topic}")

        return conversation

    def _generate_conversation_flow(
        self, topic: str, analysis: EthicalAnalysis, family_context: Dict[str, Any]
    ) -> List[str]:
        """대화 흐름 생성"""
        flow = [
            f"'{topic}'에 대해 함께 생각해보겠습니다.",
            f"이 상황에서 {', '.join([p.value for p in analysis.involved_principles])} 원칙이 중요합니다.",
            analysis.reasoning,
            f"권장하는 행동은: {analysis.recommended_action}",
            "가족과 함께 이 문제를 해결해나가시길 바랍니다.",
        ]
        return flow

    def _generate_emotional_support(
        self, analysis: EthicalAnalysis, family_context: Dict[str, Any]
    ) -> str:
        """감정적 지원 생성"""
        return "이런 상황에서 혼란스럽고 어려운 마음이 드실 수 있습니다. 하지만 가족과 함께라면 어떤 어려움도 이겨낼 수 있습니다. 서로를 믿고 의지하는 마음이 중요합니다."

    def _generate_guidance(
        self, analysis: EthicalAnalysis, family_context: Dict[str, Any]
    ) -> str:
        """지도 생성"""
        return f"가족의 가치인 {', '.join(self.family_values)}을 기억하세요. 서로를 사랑하고 이해하는 마음으로 접근하면 좋은 해결책을 찾을 수 있을 것입니다."

    def _generate_follow_up_actions(
        self, analysis: EthicalAnalysis, family_context: Dict[str, Any]
    ) -> List[str]:
        """후속 행동 생성"""
        actions = [
            "가족과 정기적인 대화 시간을 가지기",
            "서로의 감정을 표현하는 연습하기",
            "가족의 가치를 정기적으로 확인하기",
        ]

        if analysis.ethical_judgment == EthicalJudgment.ETHICAL_DILEMMA:
            actions.append("필요시 전문가의 도움을 구하기")

        return actions

    def get_ethical_statistics(self) -> Dict[str, Any]:
        """윤리적 대화 통계"""
        total_analyses = len(self.ethical_analyses)
        total_conversations = len(self.ethical_conversations)

        # 판단 유형별 통계
        judgment_stats = {}
        for judgment in EthicalJudgment:
            judgment_analyses = [
                a for a in self.ethical_analyses if a.ethical_judgment == judgment
            ]
            judgment_stats[judgment.value] = len(judgment_analyses)

        # 딜레마 유형별 통계
        dilemma_stats = {}
        for dilemma_type in DilemmaType:
            type_analyses = [
                a for a in self.ethical_analyses if a.dilemma_type == dilemma_type
            ]
            dilemma_stats[dilemma_type.value] = len(type_analyses)

        statistics = {
            "total_analyses": total_analyses,
            "total_conversations": total_conversations,
            "judgment_statistics": judgment_stats,
            "dilemma_statistics": dilemma_stats,
            "average_confidence": sum(a.confidence_score for a in self.ethical_analyses)
            / max(1, total_analyses),
            "last_updated": datetime.now().isoformat(),
        }

        logger.info("윤리적 대화 통계 생성 완료")
        return statistics

    def export_ethical_data(self) -> Dict[str, Any]:
        """윤리적 대화 데이터 내보내기"""
        return {
            "ethical_analyses": [asdict(a) for a in self.ethical_analyses],
            "ethical_conversations": [asdict(c) for c in self.ethical_conversations],
            "family_values": self.family_values,
            "export_date": datetime.now().isoformat(),
        }


# 테스트 함수
def test_ethical_conversation_system():
    """윤리적 대화 시스템 테스트"""
    print("⚖️ EthicalConversationSystem 테스트 시작...")

    ethical_system = EthicalConversationSystem()

    # 1. 윤리적 딜레마 분석
    family_context = {
        "family_type": "nuclear",
        "children_count": 2,
        "children_ages": [5, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
    }

    dilemma = "아이가 거짓말을 했는데, 진실을 말하면 상처받을 것 같아요."
    analysis = ethical_system.analyze_ethical_dilemma(dilemma, family_context)

    print(f"✅ 윤리적 딜레마 분석: {analysis.ethical_judgment.value}")
    print(f"   딜레마 유형: {analysis.dilemma_type.value}")
    print(f"   관련 원칙: {[p.value for p in analysis.involved_principles]}")
    print(f"   신뢰도: {analysis.confidence_score:.2f}")
    print(f"   권장 행동: {analysis.recommended_action}")

    # 2. 윤리적 대화 수행
    conversation = ethical_system.conduct_ethical_conversation(dilemma, family_context)

    print(f"✅ 윤리적 대화 완료: {len(conversation.conversation_flow)}개 대화 단계")
    print(f"   감정적 지원: {conversation.emotional_support}")
    print(f"   지도: {conversation.guidance_provided}")
    print(f"   후속 행동: {len(conversation.follow_up_actions)}개")

    # 3. 통계
    statistics = ethical_system.get_ethical_statistics()
    print(
        f"✅ 윤리적 대화 통계: {statistics['total_analyses']}개 분석, {statistics['total_conversations']}개 대화"
    )
    print(f"   평균 신뢰도: {statistics['average_confidence']:.2f}")
    print(f"   판단 통계: {statistics['judgment_statistics']}")

    # 4. 데이터 내보내기
    export_data = ethical_system.export_ethical_data()
    print(
        f"✅ 윤리적 대화 데이터 내보내기: {len(export_data['ethical_analyses'])}개 분석"
    )

    print("🎉 EthicalConversationSystem 테스트 완료!")


if __name__ == "__main__":
    test_ethical_conversation_system()
