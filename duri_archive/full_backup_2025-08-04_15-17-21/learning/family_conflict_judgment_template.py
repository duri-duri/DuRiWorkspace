"""
🧠 사고 템플릿 - 가족 갈등 상황 판단

1. 갈등의 본질이 무엇인가? (원인 분석)
2. 각각의 아이가 어떤 감정과 논리를 갖고 있는가? (입장 분석)
3. 현재 갈등이 심화될 경우 발생할 수 있는 위험은?
4. 두 입장 중 어느 쪽이 더 즉각적인 중재를 요하는가?
5. 중립적 입장에서 양쪽 모두를 공감하면서, **갈등을 줄이는 방향의 중재안** 제시

💡 핵심 기준:
- 감정의 심각성 + 갈등의 파급력 + 공정한 중재
- '누가 옳은가'보다 '누구에게 더 큰 도움이 필요한가'가 중심 기준
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """갈등 유형"""

    RESOURCE_COMPETITION = "resource_competition"  # 자원 경쟁
    ATTENTION_SEEKING = "attention_seeking"  # 관심 요구
    RULE_VIOLATION = "rule_violation"  # 규칙 위반
    PERSONAL_SPACE = "personal_space"  # 개인 공간
    ACHIEVEMENT_COMPARISON = "achievement_comparison"  # 성취 비교


class EmotionIntensity(Enum):
    """감정 강도"""

    MILD = "mild"  # 약함
    MODERATE = "moderate"  # 보통
    INTENSE = "intense"  # 강함
    CRITICAL = "critical"  # 위험


@dataclass
class ChildPerspective:
    """아이의 관점"""

    child_id: str
    age: int
    emotional_state: str
    logical_reasoning: str
    needs: List[str]
    urgency_level: EmotionIntensity
    support_required: bool


@dataclass
class ConflictAnalysis:
    """갈등 분석"""

    conflict_id: str
    conflict_type: ConflictType
    root_cause: str
    children_involved: List[ChildPerspective]
    escalation_risks: List[str]
    immediate_intervention_needed: bool
    mediation_priority: str
    created_at: datetime


@dataclass
class MediationPlan:
    """중재 계획"""

    plan_id: str
    conflict_analysis: ConflictAnalysis
    mediation_strategy: str
    immediate_actions: List[str]
    long_term_solutions: List[str]
    fairness_considerations: List[str]
    success_criteria: List[str]
    created_at: datetime


class FamilyConflictJudgmentTemplate:
    """가족 갈등 상황 판단 템플릿"""

    def __init__(self):
        self.conflict_analyses = []
        self.mediation_plans = []
        self.judgment_history = []

    def analyze_family_conflict(self, conflict_description: str) -> ConflictAnalysis:
        """가족 갈등 분석"""
        logger.info("🧠 가족 갈등 분석 시작")

        conflict_id = f"conflict_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 1. 갈등의 본질 분석
        root_cause = self._analyze_conflict_essence(conflict_description)

        # 2. 갈등 유형 분류
        conflict_type = self._classify_conflict_type(conflict_description)

        # 3. 아이들의 관점 분석
        children_perspectives = self._analyze_children_perspectives(
            conflict_description
        )

        # 4. 갈등 심화 위험 분석
        escalation_risks = self._analyze_escalation_risks(
            conflict_description, children_perspectives
        )

        # 5. 즉각적 중재 필요성 판단
        immediate_intervention = self._assess_immediate_intervention(
            children_perspectives, escalation_risks
        )

        # 6. 중재 우선순위 결정
        mediation_priority = self._determine_mediation_priority(
            children_perspectives, escalation_risks
        )

        analysis = ConflictAnalysis(
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            root_cause=root_cause,
            children_involved=children_perspectives,
            escalation_risks=escalation_risks,
            immediate_intervention_needed=immediate_intervention,
            mediation_priority=mediation_priority,
            created_at=datetime.now(),
        )

        self.conflict_analyses.append(analysis)
        logger.info(f"✅ 갈등 분석 완료: {conflict_id}")

        return analysis

    def _analyze_conflict_essence(self, description: str) -> str:
        """갈등의 본질 분석"""
        description_lower = description.lower()

        if any(word in description_lower for word in ["장난감", "물건", "소유"]):
            return "자원 소유권에 대한 갈등 - 공유와 소유의 개념 차이"
        elif any(word in description_lower for word in ["관심", "집중", "무시"]):
            return "부모의 관심과 인정에 대한 경쟁 - 애정과 인정의 욕구"
        elif any(word in description_lower for word in ["규칙", "금지", "허용"]):
            return "규칙과 자유에 대한 인식 차이 - 권한과 책임의 불균형"
        elif any(word in description_lower for word in ["공간", "방", "영역"]):
            return "개인 공간과 영역에 대한 갈등 - 경계와 독립성"
        elif any(word in description_lower for word in ["성적", "능력", "비교"]):
            return "성취와 능력에 대한 비교 갈등 - 자존감과 경쟁"
        else:
            return "일반적인 형제간 갈등 - 다양한 요인의 복합적 작용"

    def _classify_conflict_type(self, description: str) -> ConflictType:
        """갈등 유형 분류"""
        description_lower = description.lower()

        if any(word in description_lower for word in ["장난감", "물건", "가져가"]):
            return ConflictType.RESOURCE_COMPETITION
        elif any(word in description_lower for word in ["관심", "무시", "집중"]):
            return ConflictType.ATTENTION_SEEKING
        elif any(word in description_lower for word in ["규칙", "금지", "허용"]):
            return ConflictType.RULE_VIOLATION
        elif any(word in description_lower for word in ["방", "공간", "영역"]):
            return ConflictType.PERSONAL_SPACE
        elif any(word in description_lower for word in ["성적", "능력", "비교"]):
            return ConflictType.ACHIEVEMENT_COMPARISON
        else:
            return ConflictType.RESOURCE_COMPETITION  # 기본값

    def _analyze_children_perspectives(
        self, description: str
    ) -> List[ChildPerspective]:
        """아이들의 관점 분석"""
        perspectives = []

        # 첫 번째 아이 분석
        child1 = ChildPerspective(
            child_id="child_1",
            age=random.randint(5, 12),
            emotional_state=self._analyze_emotional_state("첫 번째 아이"),
            logical_reasoning=self._analyze_logical_reasoning("첫 번째 아이"),
            needs=self._identify_needs("첫 번째 아이"),
            urgency_level=self._assess_urgency("첫 번째 아이"),
            support_required=self._assess_support_need("첫 번째 아이"),
        )
        perspectives.append(child1)

        # 두 번째 아이 분석
        child2 = ChildPerspective(
            child_id="child_2",
            age=random.randint(5, 12),
            emotional_state=self._analyze_emotional_state("두 번째 아이"),
            logical_reasoning=self._analyze_logical_reasoning("두 번째 아이"),
            needs=self._identify_needs("두 번째 아이"),
            urgency_level=self._assess_urgency("두 번째 아이"),
            support_required=self._assess_support_need("두 번째 아이"),
        )
        perspectives.append(child2)

        return perspectives

    def _analyze_emotional_state(self, child_role: str) -> str:
        """감정 상태 분석"""
        emotional_states = [
            "분노와 좌절감으로 인한 공격적 반응",
            "상처받은 감정으로 인한 위축된 반응",
            "불안과 불안정감으로 인한 방어적 반응",
            "실망과 좌절로 인한 무력한 반응",
            "분노와 권리 의식으로 인한 적극적 반응",
        ]
        return random.choice(emotional_states)

    def _analyze_logical_reasoning(self, child_role: str) -> str:
        """논리적 사고 분석"""
        reasoning_patterns = [
            "자신의 권리가 침해되었다고 생각하여 정당성을 주장",
            "형제의 행동이 부당하다고 판단하여 시정을 요구",
            "자신의 노력과 기여가 인정받지 못한다고 느낌",
            "형제가 특별 대우를 받는다고 생각하여 불평등을 지적",
            "자신의 영역이 침범되었다고 느껴 경계를 설정하려 함",
        ]
        return random.choice(reasoning_patterns)

    def _identify_needs(self, child_role: str) -> List[str]:
        """욕구 식별"""
        all_needs = [
            "인정과 칭찬",
            "공정한 대우",
            "개인 공간과 시간",
            "부모의 관심과 사랑",
            "자신의 의견 존중",
            "규칙의 일관성",
            "형제와의 평등한 관계",
        ]
        return random.sample(all_needs, random.randint(2, 4))

    def _assess_urgency(self, child_role: str) -> EmotionIntensity:
        """긴급성 평가"""
        intensities = [
            EmotionIntensity.MILD,
            EmotionIntensity.MODERATE,
            EmotionIntensity.INTENSE,
            EmotionIntensity.CRITICAL,
        ]
        return random.choice(intensities)

    def _assess_support_need(self, child_role: str) -> bool:
        """지원 필요성 평가"""
        return random.choice([True, False])

    def _analyze_escalation_risks(
        self, description: str, children: List[ChildPerspective]
    ) -> List[str]:
        """갈등 심화 위험 분석"""
        risks = []

        # 감정 강도 기반 위험
        for child in children:
            if child.urgency_level == EmotionIntensity.CRITICAL:
                risks.append(f"{child.child_id}: 감정적 폭발로 인한 물리적 충돌 가능성")
            elif child.urgency_level == EmotionIntensity.INTENSE:
                risks.append(f"{child.child_id}: 지속적인 감정적 상처와 관계 악화")

        # 갈등 유형별 위험
        if any(child.support_required for child in children):
            risks.append("지원이 필요한 아이의 자존감 저하 및 위축")

        if (
            len(
                [
                    c
                    for c in children
                    if c.urgency_level
                    in [EmotionIntensity.INTENSE, EmotionIntensity.CRITICAL]
                ]
            )
            > 1
        ):
            risks.append("양쪽 모두의 감정이 격화되어 중재가 어려워질 위험")

        # 일반적 위험
        risks.extend(
            [
                "형제간 관계의 장기적 악화",
                "부모에 대한 신뢰도 저하",
                "가족 전체의 분위기 악화",
            ]
        )

        return risks

    def _assess_immediate_intervention(
        self, children: List[ChildPerspective], risks: List[str]
    ) -> bool:
        """즉각적 중재 필요성 평가"""
        # 위험도가 높은 경우
        if any("물리적 충돌" in risk for risk in risks):
            return True

        # 감정 강도가 높은 경우
        if any(
            child.urgency_level in [EmotionIntensity.INTENSE, EmotionIntensity.CRITICAL]
            for child in children
        ):
            return True

        # 지원이 필요한 아이가 있는 경우
        if any(child.support_required for child in children):
            return True

        return False

    def _determine_mediation_priority(
        self, children: List[ChildPerspective], risks: List[str]
    ) -> str:
        """중재 우선순위 결정"""
        # 감정 강도가 가장 높은 아이 우선
        max_urgency_child = max(children, key=lambda c: c.urgency_level.value)

        # 지원 필요성이 높은 아이 우선
        support_needed_children = [c for c in children if c.support_required]

        if support_needed_children:
            priority_child = support_needed_children[0]
            return f"{priority_child.child_id} 우선 지원 (지원 필요성 높음)"
        else:
            return f"{max_urgency_child.child_id} 우선 중재 (감정 강도 높음)"

    def create_mediation_plan(
        self, conflict_analysis: ConflictAnalysis
    ) -> MediationPlan:
        """중재 계획 생성"""
        logger.info("🤝 중재 계획 생성 시작")

        plan_id = f"mediation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 중재 전략 결정
        mediation_strategy = self._determine_mediation_strategy(conflict_analysis)

        # 즉각적 행동 계획
        immediate_actions = self._plan_immediate_actions(conflict_analysis)

        # 장기적 해결책
        long_term_solutions = self._plan_long_term_solutions(conflict_analysis)

        # 공정성 고려사항
        fairness_considerations = self._consider_fairness(conflict_analysis)

        # 성공 기준
        success_criteria = self._define_success_criteria(conflict_analysis)

        plan = MediationPlan(
            plan_id=plan_id,
            conflict_analysis=conflict_analysis,
            mediation_strategy=mediation_strategy,
            immediate_actions=immediate_actions,
            long_term_solutions=long_term_solutions,
            fairness_considerations=fairness_considerations,
            success_criteria=success_criteria,
            created_at=datetime.now(),
        )

        self.mediation_plans.append(plan)
        logger.info(f"✅ 중재 계획 생성 완료: {plan_id}")

        return plan

    def _determine_mediation_strategy(self, analysis: ConflictAnalysis) -> str:
        """중재 전략 결정"""
        if analysis.immediate_intervention_needed:
            return "즉각적 감정 진정 + 단계적 갈등 해결"
        elif analysis.conflict_type == ConflictType.RESOURCE_COMPETITION:
            return "공유 규칙 수립 + 교대 사용 체계"
        elif analysis.conflict_type == ConflictType.ATTENTION_SEEKING:
            return "개별 관심 시간 확보 + 공동 활동 기회 제공"
        elif analysis.conflict_type == ConflictType.RULE_VIOLATION:
            return "규칙 재정의 + 일관된 적용"
        elif analysis.conflict_type == ConflictType.PERSONAL_SPACE:
            return "개인 영역 존중 + 공유 공간 규칙"
        else:
            return "대화 중심 갈등 해결 + 상호 이해 증진"

    def _plan_immediate_actions(self, analysis: ConflictAnalysis) -> List[str]:
        """즉각적 행동 계획"""
        actions = []

        if analysis.immediate_intervention_needed:
            actions.extend(
                [
                    "감정이 격화된 아이들을 물리적으로 분리",
                    "각자의 감정 상태를 인정하고 진정시킴",
                    "즉각적인 안전과 평온 확보",
                ]
            )

        actions.extend(
            [
                "양쪽의 입장을 차분히 듣고 공감 표현",
                "갈등의 원인을 객관적으로 분석하여 설명",
                "양쪽 모두의 감정과 논리를 인정함",
            ]
        )

        return actions

    def _plan_long_term_solutions(self, analysis: ConflictAnalysis) -> List[str]:
        """장기적 해결책 계획"""
        solutions = []

        if analysis.conflict_type == ConflictType.RESOURCE_COMPETITION:
            solutions.extend(
                [
                    "공유 물건 사용 시간표 작성",
                    "개인 소유물과 공유 물건 구분 명확화",
                    "교대 사용 규칙 수립 및 시행",
                ]
            )
        elif analysis.conflict_type == ConflictType.ATTENTION_SEEKING:
            solutions.extend(
                [
                    "각 아이와의 개별 시간 확보",
                    "형제가 함께하는 특별 활동 기회 제공",
                    "각자의 성취를 개별적으로 인정하는 방식",
                ]
            )
        elif analysis.conflict_type == ConflictType.RULE_VIOLATION:
            solutions.extend(
                [
                    "가족 규칙을 함께 정하고 합의",
                    "규칙 위반 시 일관된 결과 적용",
                    "규칙의 이유와 목적을 명확히 설명",
                ]
            )

        solutions.extend(
            [
                "정기적인 가족 대화 시간 확보",
                "갈등 해결 방법을 함께 학습",
                "형제간 긍정적 관계 증진 활동",
            ]
        )

        return solutions

    def _consider_fairness(self, analysis: ConflictAnalysis) -> List[str]:
        """공정성 고려사항"""
        considerations = [
            "양쪽 모두의 감정과 논리를 동등하게 인정",
            "나이와 발달 단계를 고려한 차별적 대우 지양",
            "각자의 개성과 욕구를 존중하는 개별적 접근",
            "형제간 평등한 권리와 의무 보장",
            "부모의 편애나 편향 지양",
        ]

        # 특별한 고려사항 추가
        for child in analysis.children_involved:
            if child.support_required:
                considerations.append(f"{child.child_id}: 추가적 지원과 관심 제공")
            if child.urgency_level == EmotionIntensity.CRITICAL:
                considerations.append(f"{child.child_id}: 즉각적인 감정적 지원 필요")

        return considerations

    def _define_success_criteria(self, analysis: ConflictAnalysis) -> List[str]:
        """성공 기준 정의"""
        criteria = [
            "양쪽 모두의 감정이 진정되고 평온함",
            "갈등의 원인이 해결되거나 개선됨",
            "형제간 관계가 악화되지 않고 유지됨",
            "양쪽 모두가 중재 결과에 만족함",
            "유사한 갈등의 재발 가능성이 줄어듦",
        ]

        # 갈등 유형별 특화 기준
        if analysis.conflict_type == ConflictType.RESOURCE_COMPETITION:
            criteria.append("자원 사용에 대한 명확한 규칙이 수립되고 지켜짐")
        elif analysis.conflict_type == ConflictType.ATTENTION_SEEKING:
            criteria.append("각 아이가 충분한 관심과 인정을 받음")
        elif analysis.conflict_type == ConflictType.RULE_VIOLATION:
            criteria.append("규칙이 명확해지고 일관되게 적용됨")

        return criteria

    def execute_judgment_process(self, conflict_description: str) -> Dict[str, Any]:
        """판단 과정 실행"""
        logger.info("🎯 가족 갈등 판단 과정 시작")

        # 1. 갈등 분석
        conflict_analysis = self.analyze_family_conflict(conflict_description)

        # 2. 중재 계획 생성
        mediation_plan = self.create_mediation_plan(conflict_analysis)

        # 3. 판단 결과 종합
        judgment_result = {
            "conflict_analysis": conflict_analysis,
            "mediation_plan": mediation_plan,
            "key_insights": self._generate_key_insights(
                conflict_analysis, mediation_plan
            ),
            "recommendations": self._generate_recommendations(
                conflict_analysis, mediation_plan
            ),
            "success_probability": self._assess_success_probability(
                conflict_analysis, mediation_plan
            ),
        }

        self.judgment_history.append(judgment_result)
        logger.info("✅ 판단 과정 완료")

        return judgment_result

    def _generate_key_insights(
        self, analysis: ConflictAnalysis, plan: MediationPlan
    ) -> List[str]:
        """핵심 통찰 생성"""
        insights = []

        # 갈등 본질에 대한 통찰
        insights.append(f"갈등의 본질: {analysis.root_cause}")

        # 감정 강도에 대한 통찰
        for child in analysis.children_involved:
            if child.urgency_level in [
                EmotionIntensity.INTENSE,
                EmotionIntensity.CRITICAL,
            ]:
                insights.append(f"{child.child_id}: 즉각적인 감정적 지원이 필요함")

        # 중재 우선순위에 대한 통찰
        insights.append(f"중재 우선순위: {analysis.mediation_priority}")

        # 전략적 통찰
        insights.append(f"중재 전략: {plan.mediation_strategy}")

        return insights

    def _generate_recommendations(
        self, analysis: ConflictAnalysis, plan: MediationPlan
    ) -> List[str]:
        """권고사항 생성"""
        recommendations = []

        # 즉각적 권고
        if analysis.immediate_intervention_needed:
            recommendations.append(
                "즉각적인 중재가 필요합니다 - 감정이 격화될 위험이 있습니다"
            )

        # 전략적 권고
        recommendations.append(f"중재 전략: {plan.mediation_strategy}")

        # 장기적 권고
        recommendations.append("장기적으로는 갈등 예방 시스템 구축이 필요합니다")

        # 공정성 권고
        recommendations.append("양쪽 모두의 입장을 공감하면서 공정한 중재를 시도하세요")

        return recommendations

    def _assess_success_probability(
        self, analysis: ConflictAnalysis, plan: MediationPlan
    ) -> float:
        """성공 확률 평가"""
        base_probability = 0.7

        # 긍정적 요인
        if not analysis.immediate_intervention_needed:
            base_probability += 0.1

        if (
            len(
                [
                    c
                    for c in analysis.children_involved
                    if c.urgency_level == EmotionIntensity.MILD
                ]
            )
            > 0
        ):
            base_probability += 0.05

        # 부정적 요인
        if any(
            c.urgency_level == EmotionIntensity.CRITICAL
            for c in analysis.children_involved
        ):
            base_probability -= 0.15

        if len(analysis.escalation_risks) > 3:
            base_probability -= 0.1

        return max(0.0, min(1.0, base_probability))


# 전역 인스턴스
_family_conflict_judgment = None


def get_family_conflict_judgment() -> FamilyConflictJudgmentTemplate:
    """전역 가족 갈등 판단 템플릿 인스턴스 반환"""
    global _family_conflict_judgment
    if _family_conflict_judgment is None:
        _family_conflict_judgment = FamilyConflictJudgmentTemplate()
    return _family_conflict_judgment


def execute_family_conflict_judgment(conflict_description: str) -> Dict[str, Any]:
    """가족 갈등 판단 실행"""
    system = get_family_conflict_judgment()
    return system.execute_judgment_process(conflict_description)


if __name__ == "__main__":
    # 가족 갈등 판단 템플릿 데모
    print("🧠 가족 갈등 상황 판단 템플릿 시작")

    # 샘플 갈등 상황
    conflict_scenario = "형과 동생이 장난감을 가지고 다투고 있습니다. 형은 '내가 먼저 가져간 거야'라고 하고, 동생은 '나도 하고 싶어'라고 울고 있습니다."

    result = execute_family_conflict_judgment(conflict_scenario)

    print(f"\n📋 갈등 분석 결과:")
    print(f"   갈등 유형: {result['conflict_analysis'].conflict_type.value}")
    print(f"   근본 원인: {result['conflict_analysis'].root_cause}")
    print(
        f"   즉각적 중재 필요: {'예' if result['conflict_analysis'].immediate_intervention_needed else '아니오'}"
    )

    print(f"\n🤝 중재 계획:")
    print(f"   전략: {result['mediation_plan'].mediation_strategy}")
    print(f"   즉각적 행동: {len(result['mediation_plan'].immediate_actions)}개")
    print(f"   장기적 해결책: {len(result['mediation_plan'].long_term_solutions)}개")

    print(f"\n💡 핵심 통찰:")
    for insight in result["key_insights"]:
        print(f"   - {insight}")

    print(f"\n📈 성공 확률: {result['success_probability']:.1%}")
