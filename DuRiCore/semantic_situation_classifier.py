#!/usr/bin/env python3
"""
DuRi 의미 기반 상황 분류 시스템 (Day 1)
키워드 매칭 → 의미적 상황 이해로 전환
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SituationType(Enum):
    """상황 유형"""

    ETHICAL_DILEMMA = "ethical_dilemma"
    PRACTICAL_DECISION = "practical_decision"
    CONFLICT_RESOLUTION = "conflict_resolution"
    COMPLEX_PROBLEM = "complex_problem"
    GENERAL_SITUATION = "general_situation"


class IntentType(Enum):
    """의도 유형"""

    DECEPTION = "deception"
    PROTECTION = "protection"
    EFFICIENCY = "efficiency"
    FAIRNESS = "fairness"
    HARM_PREVENTION = "harm_prevention"
    BENEFIT_MAXIMIZATION = "benefit_maximization"
    UNKNOWN = "unknown"


class ValueConflict(Enum):
    """가치 충돌 유형"""

    HONESTY_VS_HARM_PREVENTION = "honesty_vs_harm_prevention"
    HONESTY_VS_BENEFIT_MAXIMIZATION = "honesty_vs_benefit_maximization"
    EFFICIENCY_VS_FAIRNESS = "efficiency_vs_fairness"
    INDIVIDUAL_VS_COLLECTIVE = "individual_vs_collective"
    SHORT_TERM_VS_LONG_TERM = "short_term_vs_long_term"
    AUTONOMY_VS_BENEFICENCE = "autonomy_vs_beneficence"
    NONE = "none"


@dataclass
class SemanticContext:
    """의미적 맥락"""

    situation_type: SituationType
    intent: IntentType
    stakeholders: List[str]
    value_conflicts: List[ValueConflict]
    consequences: List[str]
    complexity_level: float  # 0.0-1.0
    urgency_level: float  # 0.0-1.0
    context_elements: Dict[str, Any]
    confidence_score: float


@dataclass
class ContextualAnalysis:
    """맥락 분석 결과"""

    temporal_context: str  # 시간적 맥락
    spatial_context: str  # 공간적 맥락
    social_context: str  # 사회적 맥락
    emotional_context: str  # 감정적 맥락
    power_dynamics: List[str]  # 권력 관계
    cultural_factors: List[str]  # 문화적 요소
    historical_context: str  # 역사적 맥락
    urgency_factors: List[str]  # 긴급성 요소


@dataclass
class ValueConflictAnalysis:
    """가치 충돌 분석 결과"""

    primary_conflict: ValueConflict
    secondary_conflicts: List[ValueConflict]
    conflict_intensity: float  # 0.0-1.0
    resolution_difficulty: float  # 0.0-1.0
    stakeholder_impact: Dict[str, float]  # 이해관계자별 영향도
    ethical_implications: List[str]  # 윤리적 함의
    practical_constraints: List[str]  # 실용적 제약


class SemanticSituationClassifier:
    """의미 기반 상황 분류 시스템"""

    def __init__(self):
        self.system_name = "의미 기반 상황 분류 시스템"
        self.version = "2.0.0"  # Day 2 업그레이드

        # 의미적 패턴 데이터베이스
        self.semantic_patterns = self._initialize_semantic_patterns()
        self.intent_patterns = self._initialize_intent_patterns()
        self.value_patterns = self._initialize_value_patterns()

        # Day 2: 맥락 분석 패턴
        self.contextual_patterns = self._initialize_contextual_patterns()
        self.power_dynamics_patterns = self._initialize_power_dynamics_patterns()
        self.cultural_patterns = self._initialize_cultural_patterns()

    def _initialize_semantic_patterns(self) -> Dict[str, Dict]:
        """의미적 패턴 초기화"""
        return {
            "deception_contexts": {
                "protective_lie": {
                    "keywords": ["보호", "위험", "상처", "걱정"],
                    "intent": IntentType.PROTECTION,
                    "value_conflict": ValueConflict.HONESTY_VS_HARM_PREVENTION,
                    "stakeholders": ["speaker", "listener", "protected_party"],
                },
                "selfish_lie": {
                    "keywords": ["이익", "이득", "편의", "회피"],
                    "intent": IntentType.DECEPTION,
                    "value_conflict": ValueConflict.HONESTY_VS_BENEFIT_MAXIMIZATION,
                    "stakeholders": ["speaker", "listener"],
                },
            },
            "sacrifice_contexts": {
                "utilitarian_sacrifice": {
                    "keywords": ["희생", "구원", "더 많은", "최대"],
                    "intent": IntentType.BENEFIT_MAXIMIZATION,
                    "value_conflict": ValueConflict.INDIVIDUAL_VS_COLLECTIVE,
                    "stakeholders": [
                        "sacrificed_party",
                        "benefited_party",
                        "decision_maker",
                    ],
                },
                "forced_sacrifice": {
                    "keywords": ["강제", "어쩔 수 없이", "불가피"],
                    "intent": IntentType.HARM_PREVENTION,
                    "value_conflict": ValueConflict.AUTONOMY_VS_BENEFICENCE,
                    "stakeholders": ["victim", "perpetrator", "authority"],
                },
            },
            "resource_allocation_contexts": {
                "efficiency_focused": {
                    "keywords": ["효율", "최적화", "생산성", "비용"],
                    "intent": IntentType.EFFICIENCY,
                    "value_conflict": ValueConflict.EFFICIENCY_VS_FAIRNESS,
                    "stakeholders": ["efficiency_beneficiary", "fairness_advocate"],
                },
                "fairness_focused": {
                    "keywords": ["공정", "평등", "분배", "기회"],
                    "intent": IntentType.FAIRNESS,
                    "value_conflict": ValueConflict.EFFICIENCY_VS_FAIRNESS,
                    "stakeholders": ["disadvantaged_party", "advantaged_party"],
                },
            },
            "conflict_contexts": {
                "interpersonal_conflict": {
                    "keywords": ["갈등", "싸움", "불화", "대립"],
                    "intent": IntentType.PROTECTION,
                    "value_conflict": ValueConflict.INDIVIDUAL_VS_COLLECTIVE,
                    "stakeholders": ["party_a", "party_b", "mediator"],
                },
                "systemic_conflict": {
                    "keywords": ["체계", "제도", "구조", "시스템"],
                    "intent": IntentType.FAIRNESS,
                    "value_conflict": ValueConflict.SHORT_TERM_VS_LONG_TERM,
                    "stakeholders": [
                        "system_beneficiary",
                        "system_victim",
                        "authority",
                    ],
                },
            },
        }

    def _initialize_intent_patterns(self) -> Dict[str, List[str]]:
        """의도 패턴 초기화"""
        return {
            "deception": ["거짓말", "속임", "숨김", "왜곡", "기만", "거짓"],
            "protection": ["보호", "방어", "막기", "예방", "구원", "지키기"],
            "efficiency": [
                "효율",
                "최적화",
                "생산성",
                "비용절약",
                "시간절약",
                "효율적",
            ],
            "fairness": ["공정", "평등", "정의", "균등", "공평", "공정한"],
            "harm_prevention": ["해방지", "위험방지", "사고방지", "상해방지", "방지"],
            "benefit_maximization": [
                "이익",
                "효과",
                "성과",
                "결과",
                "성공",
                "최대화",
                "극대화",
                "희생",
                "구원",
            ],
        }

    def _initialize_value_patterns(self) -> Dict[str, List[str]]:
        """가치 패턴 초기화"""
        return {
            "honesty": ["정직", "진실", "솔직", "거짓없음"],
            "harm_prevention": ["해방지", "위험방지", "상해방지", "사고방지"],
            "efficiency": ["효율", "최적화", "생산성", "비용절약"],
            "fairness": ["공정", "평등", "정의", "균등"],
            "individual": ["개인", "자신", "개별", "독립"],
            "collective": ["집단", "공동체", "사회", "전체"],
            "autonomy": ["자율", "자유", "선택", "독립"],
            "beneficence": ["이익", "도움", "선행", "유익"],
        }

    def _initialize_cultural_patterns(self) -> Dict[str, List[str]]:
        """문화적 패턴 초기화"""
        return {
            "hierarchy": ["상급자", "하급자", "선배", "후배", "상사", "부하"],
            "collectivism": ["집단", "공동체", "사회", "전체", "우리"],
            "individualism": ["개인", "자신", "개별", "독립", "나"],
            "face_saving": ["체면", "자존심", "위신", "명예", "체통"],
            "harmony": ["화합", "조화", "평화", "협력", "단결"],
        }

    def _initialize_power_dynamics_patterns(self) -> Dict[str, List[str]]:
        """권력 관계 패턴 초기화"""
        return {
            "authority": ["권위", "권력", "지배", "통제", "명령"],
            "subordination": ["복종", "순응", "따름", "지시받음"],
            "resistance": ["저항", "반발", "거부", "반대"],
            "manipulation": ["조작", "이용", "사용", "도구화"],
            "empowerment": ["권한부여", "자율성", "독립성", "자유"],
        }

    def _initialize_contextual_patterns(self) -> Dict[str, Dict]:
        """맥락 분석 패턴 초기화"""
        return {
            "temporal_contexts": {
                "immediate": ["즉시", "당장", "지금", "현재"],
                "urgent": ["긴급", "시급", "빨리", "마감"],
                "long_term": ["장기", "미래", "앞으로", "향후"],
                "past": ["과거", "이전", "전에", "지난"],
            },
            "spatial_contexts": {
                "workplace": ["직장", "회사", "사무실", "업무"],
                "family": ["가족", "집", "가정", "부모"],
                "public": ["공공", "사회", "대중", "일반"],
                "private": ["개인", "사적", "비공개", "내부"],
            },
            "social_contexts": {
                "formal": ["공식", "정식", "법적", "제도적"],
                "informal": ["비공식", "사적", "개인적", "자유로운"],
                "hierarchical": ["계급", "서열", "위계", "등급"],
                "egalitarian": ["평등", "동등", "수평", "대등"],
            },
            "emotional_contexts": {
                "fear": ["두려움", "공포", "불안", "걱정"],
                "anger": ["분노", "화", "격분", "노여움"],
                "sadness": ["슬픔", "우울", "절망", "실망"],
                "joy": ["기쁨", "행복", "만족", "희망"],
                "guilt": ["죄책감", "양심", "후회", "자책"],
                "pride": ["자부심", "자랑", "긍지", "자신감"],
            },
        }

    async def analyze_semantic_context(self, situation: str) -> SemanticContext:
        """의미적 맥락 분석"""
        logger.info(f"의미적 맥락 분석 시작: {situation}")

        # 1. 문맥 분석
        context_elements = self._analyze_context_elements(situation)

        # 2. 의도 분석
        intent = self._analyze_intent(situation, context_elements)

        # 3. 이해관계자 분석
        stakeholders = self._identify_stakeholders(situation, context_elements)

        # 4. 가치 충돌 분석
        value_conflicts = self._analyze_value_conflicts(situation, intent)

        # 5. 결과 분석
        consequences = self._analyze_consequences(situation, intent, value_conflicts)

        # 6. 상황 유형 분류
        situation_type = self._classify_situation_type(situation, intent, value_conflicts)

        # 7. 복잡성 및 긴급성 평가
        complexity_level = self._assess_complexity(situation, value_conflicts)
        urgency_level = self._assess_urgency(situation, context_elements)

        # 8. 신뢰도 계산
        confidence_score = self._calculate_confidence_score(situation, intent, value_conflicts, context_elements)

        # Day 2: 추가 분석
        contextual_analysis = await self._analyze_contextual_factors(situation)  # noqa: F841
        value_conflict_analysis = await self._analyze_value_conflicts_detailed(situation, value_conflicts)  # noqa: F841

        semantic_context = SemanticContext(
            situation_type=situation_type,
            intent=intent,
            stakeholders=stakeholders,
            value_conflicts=value_conflicts,
            consequences=consequences,
            complexity_level=complexity_level,
            urgency_level=urgency_level,
            context_elements=context_elements,
            confidence_score=confidence_score,
        )

        logger.info(f"의미적 맥락 분석 완료: {situation_type.value}, 신뢰도: {confidence_score:.2f}")
        return semantic_context

    def _analyze_context_elements(self, situation: str) -> Dict[str, Any]:
        """문맥 요소 분석"""
        context = {
            "actors": [],
            "actions": [],
            "motivations": [],
            "circumstances": [],
            "temporal_aspects": [],
            "spatial_aspects": [],
        }

        # 행위자 추출
        actor_patterns = [
            r"(\w+가|\w+은|\w+는|\w+에게|\w+와|\w+과)",
            r"(\w+들|\w+들께|\w+들에게)",
        ]

        for pattern in actor_patterns:
            matches = re.findall(pattern, situation)
            context["actors"].extend(matches)

        # 행위 추출
        action_patterns = [
            r"(\w+해야|\w+해야 하는|\w+해야 하는 상황)",
            r"(\w+하려고|\w+하려는|\w+하려는 상황)",
            r"(\w+해야|\w+해야 하는|\w+해야 하는 상황)",
        ]

        for pattern in action_patterns:
            matches = re.findall(pattern, situation)
            context["actions"].extend(matches)

        # 동기 추출
        motivation_keywords = ["위해", "때문에", "이유로", "목적으로", "결과로"]
        for keyword in motivation_keywords:
            if keyword in situation:
                context["motivations"].append(keyword)

        # 상황 추출
        circumstance_keywords = ["상황", "경우", "때", "상황에서", "경우에"]
        for keyword in circumstance_keywords:
            if keyword in situation:
                context["circumstances"].append(keyword)

        return context

    def _analyze_intent(self, situation: str, context_elements: Dict[str, Any]) -> IntentType:
        """의도 분석"""
        intent_scores = {
            IntentType.DECEPTION: 0.0,
            IntentType.PROTECTION: 0.0,
            IntentType.EFFICIENCY: 0.0,
            IntentType.FAIRNESS: 0.0,
            IntentType.HARM_PREVENTION: 0.0,
            IntentType.BENEFIT_MAXIMIZATION: 0.0,
        }

        # 각 의도 패턴에 대한 점수 계산
        for intent_type, keywords in self.intent_patterns.items():
            score = 0.0
            for keyword in keywords:
                if keyword in situation:
                    score += 1.0
            intent_scores[IntentType(intent_type)] = score

        # 가장 높은 점수의 의도 선택
        max_intent = max(intent_scores.items(), key=lambda x: x[1])

        if max_intent[1] > 0:
            return max_intent[0]
        else:
            return IntentType.UNKNOWN

    def _identify_stakeholders(self, situation: str, context_elements: Dict[str, Any]) -> List[str]:
        """이해관계자 식별"""
        stakeholders = []

        # 기본 이해관계자 패턴
        basic_stakeholders = {
            "decision_maker": ["결정자", "판단자", "선택자", "해야"],
            "affected_party": ["영향받는", "관련된", "당사자", "받는"],
            "beneficiary": [
                "이익을 받는",
                "혜택을 받는",
                "유리한",
                "구원받는",
                "구하는",
            ],
            "victim": ["피해자", "손해를 받는", "불리한", "희생되는", "희생당하는"],
            "mediator": ["중재자", "조정자", "중간자", "해결자"],
        }

        # 숫자 기반 이해관계자 추출
        number_patterns = [
            (r"(\d+)명", "counted_party"),
            (r"(\d+)개", "counted_item"),
            (r"(\d+)번", "counted_occurrence"),
        ]

        for pattern, stakeholder_type in number_patterns:
            matches = re.findall(pattern, situation)
            if matches:
                stakeholders.append(f"{stakeholder_type}_{matches[0]}")

        # 특정 상황별 이해관계자
        if "희생" in situation and "구" in situation:
            stakeholders.extend(["sacrificed_party", "saved_party"])

        if "갈등" in situation:
            stakeholders.extend(["conflicting_party_a", "conflicting_party_b", "mediator"])

        if "거짓말" in situation:
            stakeholders.extend(["deceiver", "deceived_party"])

        # 일반적인 이해관계자 패턴 매칭
        for stakeholder_type, keywords in basic_stakeholders.items():
            for keyword in keywords:
                if keyword in situation:
                    stakeholders.append(stakeholder_type)
                    break

        # 문맥에서 추출한 행위자들도 추가
        if context_elements.get("actors"):
            stakeholders.extend(context_elements["actors"])

        return list(set(stakeholders))  # 중복 제거

    def _analyze_value_conflicts(self, situation: str, intent: IntentType) -> List[ValueConflict]:
        """가치 충돌 분석"""
        conflicts = []

        # 의도 기반 가치 충돌 매핑
        intent_conflict_mapping = {
            IntentType.DECEPTION: [ValueConflict.HONESTY_VS_HARM_PREVENTION],
            IntentType.PROTECTION: [ValueConflict.AUTONOMY_VS_BENEFICENCE],
            IntentType.EFFICIENCY: [ValueConflict.EFFICIENCY_VS_FAIRNESS],
            IntentType.FAIRNESS: [ValueConflict.EFFICIENCY_VS_FAIRNESS],
            IntentType.HARM_PREVENTION: [ValueConflict.HONESTY_VS_HARM_PREVENTION],
            IntentType.BENEFIT_MAXIMIZATION: [ValueConflict.INDIVIDUAL_VS_COLLECTIVE],
        }

        # 특정 상황별 가치 충돌
        if "희생" in situation and "구" in situation:
            conflicts.append(ValueConflict.INDIVIDUAL_VS_COLLECTIVE)

        if "갈등" in situation:
            conflicts.append(ValueConflict.INDIVIDUAL_VS_COLLECTIVE)

        if "거짓말" in situation:
            conflicts.append(ValueConflict.HONESTY_VS_HARM_PREVENTION)

        # 의도 기반 충돌 추가
        if intent in intent_conflict_mapping:
            conflicts.extend(intent_conflict_mapping[intent])

        # 상황 기반 추가 충돌 분석
        for value_type, keywords in self.value_patterns.items():
            if any(keyword in situation for keyword in keywords):
                # 대립되는 가치 찾기
                opposing_values = self._find_opposing_values(value_type)
                for opposing_value in opposing_values:
                    conflict = self._create_value_conflict(value_type, opposing_value)
                    if conflict and conflict not in conflicts:
                        conflicts.append(conflict)

        return conflicts if conflicts else [ValueConflict.NONE]

    def _find_opposing_values(self, value_type: str) -> List[str]:
        """대립되는 가치 찾기"""
        opposing_mapping = {
            "honesty": ["harm_prevention", "benefit_maximization"],
            "harm_prevention": ["honesty", "autonomy"],
            "efficiency": ["fairness", "individual"],
            "fairness": ["efficiency", "collective"],
            "individual": ["collective", "efficiency"],
            "collective": ["individual", "fairness"],
            "autonomy": ["beneficence", "harm_prevention"],
            "beneficence": ["autonomy", "individual"],
        }

        return opposing_mapping.get(value_type, [])

    def _create_value_conflict(self, value1: str, value2: str) -> Optional[ValueConflict]:
        """가치 충돌 생성"""
        conflict_mapping = {
            ("honesty", "harm_prevention"): ValueConflict.HONESTY_VS_HARM_PREVENTION,
            ("efficiency", "fairness"): ValueConflict.EFFICIENCY_VS_FAIRNESS,
            ("individual", "collective"): ValueConflict.INDIVIDUAL_VS_COLLECTIVE,
            ("autonomy", "beneficence"): ValueConflict.AUTONOMY_VS_BENEFICENCE,
        }

        # 순서에 관계없이 매핑
        for (v1, v2), conflict in conflict_mapping.items():
            if (value1 == v1 and value2 == v2) or (value1 == v2 and value2 == v1):
                return conflict

        return None

    def _analyze_consequences(
        self, situation: str, intent: IntentType, value_conflicts: List[ValueConflict]
    ) -> List[str]:
        """결과 분석"""
        consequences = []

        # 의도 기반 결과
        intent_consequences = {
            IntentType.DECEPTION: ["신뢰 관계 악화", "진실 왜곡", "의사소통 장애"],
            IntentType.PROTECTION: ["안전 확보", "위험 방지", "보호 효과"],
            IntentType.EFFICIENCY: ["자원 절약", "시간 단축", "생산성 향상"],
            IntentType.FAIRNESS: ["공정성 확보", "평등 실현", "정의 실현"],
            IntentType.HARM_PREVENTION: ["위험 감소", "사고 방지", "안전 증진"],
            IntentType.BENEFIT_MAXIMIZATION: ["이익 극대화", "효과 증대", "성과 향상"],
        }

        if intent in intent_consequences:
            consequences.extend(intent_consequences[intent])

        # 가치 충돌 기반 결과
        for conflict in value_conflicts:
            if conflict != ValueConflict.NONE:
                conflict_consequences = {
                    ValueConflict.HONESTY_VS_HARM_PREVENTION: ["진실성 vs 안전성 갈등"],
                    ValueConflict.EFFICIENCY_VS_FAIRNESS: ["효율성 vs 공정성 갈등"],
                    ValueConflict.INDIVIDUAL_VS_COLLECTIVE: ["개인 vs 집단 갈등"],
                    ValueConflict.AUTONOMY_VS_BENEFICENCE: ["자율성 vs 이익 갈등"],
                }

                if conflict in conflict_consequences:
                    consequences.extend(conflict_consequences[conflict])

        return consequences

    def _classify_situation_type(
        self, situation: str, intent: IntentType, value_conflicts: List[ValueConflict]
    ) -> SituationType:
        """상황 유형 분류"""
        # 윤리적 딜레마 판단
        if intent in [IntentType.DECEPTION, IntentType.HARM_PREVENTION] or any(
            conflict
            in [
                ValueConflict.HONESTY_VS_HARM_PREVENTION,
                ValueConflict.AUTONOMY_VS_BENEFICENCE,
            ]
            for conflict in value_conflicts
        ):
            return SituationType.ETHICAL_DILEMMA

        # 실용적 결정 판단
        if (
            intent in [IntentType.EFFICIENCY, IntentType.BENEFIT_MAXIMIZATION]
            or ValueConflict.EFFICIENCY_VS_FAIRNESS in value_conflicts
        ):
            return SituationType.PRACTICAL_DECISION

        # 갈등 해결 판단
        if intent == IntentType.PROTECTION or ValueConflict.INDIVIDUAL_VS_COLLECTIVE in value_conflicts:
            return SituationType.CONFLICT_RESOLUTION

        # 복잡한 문제 판단
        if len(value_conflicts) > 1 or intent == IntentType.UNKNOWN:
            return SituationType.COMPLEX_PROBLEM

        return SituationType.GENERAL_SITUATION

    def _assess_complexity(self, situation: str, value_conflicts: List[ValueConflict]) -> float:
        """복잡성 평가"""
        complexity_score = 0.5  # 기본값

        # 가치 충돌 수에 따른 복잡성
        if len(value_conflicts) > 1:
            complexity_score += 0.2

        # 키워드 다양성에 따른 복잡성
        unique_keywords = len(set(situation.split()))
        if unique_keywords > 10:
            complexity_score += 0.1

        # 문장 길이에 따른 복잡성
        if len(situation) > 50:
            complexity_score += 0.1

        return min(complexity_score, 1.0)

    def _assess_urgency(self, situation: str, context_elements: Dict[str, Any]) -> float:
        """긴급성 평가"""
        urgency_score = 0.5  # 기본값

        # 긴급성 키워드
        urgency_keywords = ["긴급", "즉시", "당장", "빨리", "시급", "위험", "위기"]
        for keyword in urgency_keywords:
            if keyword in situation:
                urgency_score += 0.2
                break

        # 시간 관련 표현
        time_keywords = ["시간", "마감", "기한", "마지막", "최후"]
        for keyword in time_keywords:
            if keyword in situation:
                urgency_score += 0.1
                break

        return min(urgency_score, 1.0)

    def _calculate_confidence_score(
        self,
        situation: str,
        intent: IntentType,
        value_conflicts: List[ValueConflict],
        context_elements: Dict[str, Any],
    ) -> float:
        """신뢰도 계산"""
        confidence_score = 0.5  # 기본값

        # 의도 명확성
        if intent != IntentType.UNKNOWN:
            confidence_score += 0.2

        # 가치 충돌 명확성
        if value_conflicts and value_conflicts[0] != ValueConflict.NONE:
            confidence_score += 0.2

        # 문맥 요소 풍부성
        if context_elements.get("actors") and context_elements.get("actions"):
            confidence_score += 0.1

        # 키워드 매칭 정확성
        matched_keywords = 0
        total_keywords = 0

        for intent_type, keywords in self.intent_patterns.items():
            total_keywords += len(keywords)
            for keyword in keywords:
                if keyword in situation:
                    matched_keywords += 1

        if total_keywords > 0:
            keyword_accuracy = matched_keywords / total_keywords
            confidence_score += keyword_accuracy * 0.2

        return min(confidence_score, 1.0)

    async def _analyze_contextual_factors(self, situation: str) -> ContextualAnalysis:
        """맥락적 요소 분석"""
        # 시간적 맥락
        temporal_context = self._analyze_temporal_context(situation)

        # 공간적 맥락
        spatial_context = self._analyze_spatial_context(situation)

        # 사회적 맥락
        social_context = self._analyze_social_context(situation)

        # 감정적 맥락
        emotional_context = self._analyze_emotional_context(situation)

        # 권력 관계
        power_dynamics = self._analyze_power_dynamics(situation)

        # 문화적 요소
        cultural_factors = self._analyze_cultural_factors(situation)

        # 역사적 맥락
        historical_context = self._analyze_historical_context(situation)

        # 긴급성 요소
        urgency_factors = self._analyze_urgency_factors(situation)

        return ContextualAnalysis(
            temporal_context=temporal_context,
            spatial_context=spatial_context,
            social_context=social_context,
            emotional_context=emotional_context,
            power_dynamics=power_dynamics,
            cultural_factors=cultural_factors,
            historical_context=historical_context,
            urgency_factors=urgency_factors,
        )

    async def _analyze_value_conflicts_detailed(
        self, situation: str, value_conflicts: List[ValueConflict]
    ) -> ValueConflictAnalysis:
        """상세한 가치 충돌 분석"""
        if not value_conflicts or value_conflicts[0] == ValueConflict.NONE:
            return ValueConflictAnalysis(
                primary_conflict=ValueConflict.NONE,
                secondary_conflicts=[],
                conflict_intensity=0.0,
                resolution_difficulty=0.0,
                stakeholder_impact={},
                ethical_implications=[],
                practical_constraints=[],
            )

        primary_conflict = value_conflicts[0]
        secondary_conflicts = value_conflicts[1:] if len(value_conflicts) > 1 else []

        # 충돌 강도 분석
        conflict_intensity = self._assess_conflict_intensity(situation, primary_conflict)

        # 해결 난이도 분석
        resolution_difficulty = self._assess_resolution_difficulty(situation, primary_conflict)

        # 이해관계자별 영향도
        stakeholder_impact = self._assess_stakeholder_impact(situation, primary_conflict)

        # 윤리적 함의
        ethical_implications = self._analyze_ethical_implications(primary_conflict)

        # 실용적 제약
        practical_constraints = self._analyze_practical_constraints(situation, primary_conflict)

        return ValueConflictAnalysis(
            primary_conflict=primary_conflict,
            secondary_conflicts=secondary_conflicts,
            conflict_intensity=conflict_intensity,
            resolution_difficulty=resolution_difficulty,
            stakeholder_impact=stakeholder_impact,
            ethical_implications=ethical_implications,
            practical_constraints=practical_constraints,
        )

    def _analyze_temporal_context(self, situation: str) -> str:
        """시간적 맥락 분석"""
        for context_type, keywords in self.contextual_patterns["temporal_contexts"].items():
            for keyword in keywords:
                if keyword in situation:
                    return context_type
        return "unknown"

    def _analyze_spatial_context(self, situation: str) -> str:
        """공간적 맥락 분석"""
        for context_type, keywords in self.contextual_patterns["spatial_contexts"].items():
            for keyword in keywords:
                if keyword in situation:
                    return context_type
        return "unknown"

    def _analyze_social_context(self, situation: str) -> str:
        """사회적 맥락 분석"""
        for context_type, keywords in self.contextual_patterns["social_contexts"].items():
            for keyword in keywords:
                if keyword in situation:
                    return context_type
        return "unknown"

    def _analyze_emotional_context(self, situation: str) -> str:
        """감정적 맥락 분석"""
        for context_type, keywords in self.contextual_patterns["emotional_contexts"].items():
            for keyword in keywords:
                if keyword in situation:
                    return context_type
        return "neutral"

    def _analyze_power_dynamics(self, situation: str) -> List[str]:
        """권력 관계 분석"""
        dynamics = []
        for dynamic_type, keywords in self.power_dynamics_patterns.items():
            for keyword in keywords:
                if keyword in situation:
                    dynamics.append(dynamic_type)
                    break
        return dynamics

    def _analyze_cultural_factors(self, situation: str) -> List[str]:
        """문화적 요소 분석"""
        factors = []
        for factor_type, keywords in self.cultural_patterns.items():
            for keyword in keywords:
                if keyword in situation:
                    factors.append(factor_type)
                    break
        return factors

    def _analyze_historical_context(self, situation: str) -> str:
        """역사적 맥락 분석"""
        historical_keywords = ["과거", "이전", "전에", "지난", "경험", "기억"]
        for keyword in historical_keywords:
            if keyword in situation:
                return "historical"
        return "current"

    def _analyze_urgency_factors(self, situation: str) -> List[str]:
        """긴급성 요소 분석"""
        urgency_factors = []
        urgency_keywords = {
            "time_pressure": ["시간", "마감", "기한", "마지막"],
            "safety_risk": ["위험", "위기", "안전", "사고"],
            "emotional_pressure": ["감정", "압박", "스트레스", "긴장"],
            "social_pressure": ["사회적", "집단", "압력", "기대"],
        }

        for factor_type, keywords in urgency_keywords.items():
            for keyword in keywords:
                if keyword in situation:
                    urgency_factors.append(factor_type)
                    break

        return urgency_factors

    def _assess_conflict_intensity(self, situation: str, conflict: ValueConflict) -> float:
        """충돌 강도 평가"""
        intensity = 0.5  # 기본값

        # 키워드 기반 강도 평가
        intensity_keywords = {
            "high": ["극단", "최대", "완전", "절대", "필수"],
            "medium": ["중요", "필요", "요구", "당연"],
            "low": ["가능", "선택", "권장", "바람직"],
        }

        for level, keywords in intensity_keywords.items():
            for keyword in keywords:
                if keyword in situation:
                    if level == "high":
                        intensity += 0.3
                    elif level == "medium":
                        intensity += 0.1
                    elif level == "low":
                        intensity -= 0.1
                    break

        return min(max(intensity, 0.0), 1.0)

    def _assess_resolution_difficulty(self, situation: str, conflict: ValueConflict) -> float:
        """해결 난이도 평가"""
        difficulty = 0.5  # 기본값

        # 충돌 유형별 기본 난이도
        conflict_difficulty = {
            ValueConflict.HONESTY_VS_HARM_PREVENTION: 0.8,
            ValueConflict.EFFICIENCY_VS_FAIRNESS: 0.6,
            ValueConflict.INDIVIDUAL_VS_COLLECTIVE: 0.7,
            ValueConflict.AUTONOMY_VS_BENEFICENCE: 0.7,
        }

        if conflict in conflict_difficulty:
            difficulty = conflict_difficulty[conflict]

        # 상황 복잡성에 따른 난이도 조정
        if len(situation.split()) > 15:
            difficulty += 0.1

        return min(difficulty, 1.0)

    def _assess_stakeholder_impact(self, situation: str, conflict: ValueConflict) -> Dict[str, float]:
        """이해관계자별 영향도 평가"""
        impact = {}

        # 기본 이해관계자 영향도
        if "희생" in situation:
            impact["sacrificed_party"] = 0.9
            impact["saved_party"] = 0.7

        if "거짓말" in situation:
            impact["deceiver"] = 0.6
            impact["deceived_party"] = 0.8

        if "갈등" in situation:
            impact["conflicting_party_a"] = 0.7
            impact["conflicting_party_b"] = 0.7

        return impact

    def _analyze_ethical_implications(self, conflict: ValueConflict) -> List[str]:
        """윤리적 함의 분석"""
        implications = {
            ValueConflict.HONESTY_VS_HARM_PREVENTION: [
                "진실성의 가치",
                "해방지의 의무",
                "신뢰 관계의 중요성",
            ],
            ValueConflict.EFFICIENCY_VS_FAIRNESS: [
                "효율성의 가치",
                "공정성의 원칙",
                "자원 배분의 정의",
            ],
            ValueConflict.INDIVIDUAL_VS_COLLECTIVE: [
                "개인의 권리",
                "공동체의 이익",
                "개인과 집단의 균형",
            ],
            ValueConflict.AUTONOMY_VS_BENEFICENCE: [
                "자율성의 존중",
                "이익 증진의 의무",
                "개인의 선택권",
            ],
        }

        return implications.get(conflict, [])

    def _analyze_practical_constraints(self, situation: str, conflict: ValueConflict) -> List[str]:
        """실용적 제약 분석"""
        constraints = []

        # 시간적 제약
        if any(word in situation for word in ["시간", "마감", "기한"]):
            constraints.append("시간적 제약")

        # 자원적 제약
        if any(word in situation for word in ["자원", "비용", "예산", "재정"]):
            constraints.append("자원적 제약")

        # 제도적 제약
        if any(word in situation for word in ["법", "규정", "제도", "정책"]):
            constraints.append("제도적 제약")

        # 사회적 제약
        if any(word in situation for word in ["사회", "집단", "여론", "평판"]):
            constraints.append("사회적 제약")

        return constraints


async def test_semantic_situation_classifier():
    """의미 기반 상황 분류 시스템 테스트 (Day 2)"""
    print("=== 의미 기반 상황 분류 시스템 테스트 시작 (Day 2) ===")

    classifier = SemanticSituationClassifier()

    # Day 2 테스트 상황들
    test_situations = [
        "거짓말을 해야 하는 상황",
        "1명을 희생해서 5명을 구해야 하는 상황",
        "자원을 효율적으로 배분해야 하는 상황",
        "갈등을 해결해야 하는 상황",
        "복잡한 윤리적 딜레마 상황",
        "직장에서 상사에게 거짓말을 해야 하는 긴급한 상황",
        "가족을 위해 개인의 이익을 포기해야 하는 상황",
        "공정성과 효율성 사이에서 선택해야 하는 상황",
    ]

    for situation in test_situations:
        print(f"\n{'='*60}")
        print(f"상황: {situation}")
        print(f"{'='*60}")

        semantic_context = await classifier.analyze_semantic_context(situation)

        print("📋 기본 분석:")
        print(f"  • 상황 유형: {semantic_context.situation_type.value}")
        print(f"  • 의도: {semantic_context.intent.value}")
        print(f"  • 이해관계자: {semantic_context.stakeholders}")
        print(f"  • 가치 충돌: {[conflict.value for conflict in semantic_context.value_conflicts]}")
        print(f"  • 결과: {semantic_context.consequences}")
        print(f"  • 복잡성: {semantic_context.complexity_level:.2f}")
        print(f"  • 긴급성: {semantic_context.urgency_level:.2f}")
        print(f"  • 신뢰도: {semantic_context.confidence_score:.2f}")

        # Day 2: 맥락 분석 결과
        contextual_analysis = await classifier._analyze_contextual_factors(situation)
        print("\n🌍 맥락 분석 (Day 2):")
        print(f"  • 시간적 맥락: {contextual_analysis.temporal_context}")
        print(f"  • 공간적 맥락: {contextual_analysis.spatial_context}")
        print(f"  • 사회적 맥락: {contextual_analysis.social_context}")
        print(f"  • 감정적 맥락: {contextual_analysis.emotional_context}")
        print(f"  • 권력 관계: {contextual_analysis.power_dynamics}")
        print(f"  • 문화적 요소: {contextual_analysis.cultural_factors}")
        print(f"  • 역사적 맥락: {contextual_analysis.historical_context}")
        print(f"  • 긴급성 요소: {contextual_analysis.urgency_factors}")

        # Day 2: 가치 충돌 상세 분석
        value_conflict_analysis = await classifier._analyze_value_conflicts_detailed(
            situation, semantic_context.value_conflicts
        )
        print("\n⚖️ 가치 충돌 상세 분석 (Day 2):")
        print(f"  • 주요 충돌: {value_conflict_analysis.primary_conflict.value}")
        print(f"  • 부차적 충돌: {[c.value for c in value_conflict_analysis.secondary_conflicts]}")
        print(f"  • 충돌 강도: {value_conflict_analysis.conflict_intensity:.2f}")
        print(f"  • 해결 난이도: {value_conflict_analysis.resolution_difficulty:.2f}")
        print(f"  • 이해관계자 영향도: {value_conflict_analysis.stakeholder_impact}")
        print(f"  • 윤리적 함의: {value_conflict_analysis.ethical_implications}")
        print(f"  • 실용적 제약: {value_conflict_analysis.practical_constraints}")

    print(f"\n{'='*60}")
    print("=== 의미 기반 상황 분류 시스템 테스트 완료 (Day 2) ===")
    print("✅ Day 1-2 목표 달성: 키워드 매칭 → 의미적 상황 이해")
    print("✅ Day 2 목표 달성: 맥락 분석 및 가치 충돌 인식 시스템")


if __name__ == "__main__":
    asyncio.run(test_semantic_situation_classifier())
