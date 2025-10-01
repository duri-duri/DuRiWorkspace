#!/usr/bin/env python3
"""
FamilyConversationPrecisionSystem - Phase 11
가족 특화 대화 정밀도 시스템

기능:
- 가족 관계에 특화된 대화 정밀도 분석
- 가족 맥락에 맞는 정확한 응답 생성
- 가족 관계별 맞춤형 대화 스타일
- 대화 정밀도 학습 및 개선
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


class FamilyRelationship(Enum):
    """가족 관계"""

    PARENT_CHILD = "parent_child"
    SPOUSE = "spouse"
    SIBLING = "sibling"
    GRANDPARENT_GRANDCHILD = "grandparent_grandchild"
    EXTENDED_FAMILY = "extended_family"
    OTHER = "other"


class ConversationPrecisionLevel(Enum):
    """대화 정밀도 수준"""

    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class FamilyContextType(Enum):
    """가족 맥락 유형"""

    DAILY_LIFE = "daily_life"
    EMOTIONAL_SUPPORT = "emotional_support"
    EDUCATION = "education"
    DISCIPLINE = "discipline"
    CELEBRATION = "celebration"
    CRISIS = "crisis"
    OTHER = "other"


@dataclass
class FamilyContext:
    """가족 맥락"""

    relationship: FamilyRelationship
    context_type: FamilyContextType
    family_member_ages: List[int]
    family_values: List[str]
    current_situation: str
    emotional_state: str
    communication_style: str


@dataclass
class PrecisionAnalysis:
    """정밀도 분석"""

    id: str
    message_id: str
    relationship_accuracy: float
    context_appropriateness: float
    emotional_sensitivity: float
    family_value_alignment: float
    overall_precision: float
    improvement_suggestions: List[str]
    timestamp: datetime


@dataclass
class PrecisionResponse:
    """정밀도 응답"""

    id: str
    analysis_id: str
    original_message: str
    precision_enhanced_response: str
    relationship_specific_elements: List[str]
    context_appropriate_phrases: List[str]
    emotional_support_elements: List[str]
    confidence_score: float
    timestamp: datetime
    notes: Optional[str] = None


@dataclass
class FamilyPrecisionPattern:
    """가족 정밀도 패턴"""

    relationship: FamilyRelationship
    context_type: FamilyContextType
    trigger_phrases: List[str]
    appropriate_responses: List[str]
    emotional_tone: str
    success_rate: float


class FamilyConversationPrecisionSystem:
    """가족 특화 대화 정밀도 시스템"""

    def __init__(self):
        self.precision_analyses: List[PrecisionAnalysis] = []
        self.precision_responses: List[PrecisionResponse] = []
        self.family_precision_patterns: List[FamilyPrecisionPattern] = []
        self.family_context: Dict[str, Any] = {}

        # 가족 관계별 정밀도 패턴 초기화
        self._initialize_family_precision_patterns()

        logger.info("FamilyConversationPrecisionSystem 초기화 완료")

    def _initialize_family_precision_patterns(self):
        """가족 정밀도 패턴 초기화"""
        # 부모-자식 관계 패턴
        parent_child_pattern = FamilyPrecisionPattern(
            relationship=FamilyRelationship.PARENT_CHILD,
            context_type=FamilyContextType.DAILY_LIFE,
            trigger_phrases=["아이", "자식", "아들", "딸", "키우", "육아"],
            appropriate_responses=[
                "사랑으로 기르는 것이 가장 중요해요.",
                "아이의 성장을 지켜보는 기쁨을 느껴보세요.",
                "인내심을 가지고 아이와 소통해보세요.",
            ],
            emotional_tone="따뜻하고 격려적",
            success_rate=0.85,
        )

        # 배우자 관계 패턴
        spouse_pattern = FamilyPrecisionPattern(
            relationship=FamilyRelationship.SPOUSE,
            context_type=FamilyContextType.EMOTIONAL_SUPPORT,
            trigger_phrases=["남편", "아내", "배우자", "부부", "결혼"],
            appropriate_responses=[
                "서로를 이해하고 존중하는 마음이 중요해요.",
                "소통을 통해 더 깊은 관계를 만들어보세요.",
                "함께 성장하는 부부가 되어보세요.",
            ],
            emotional_tone="지지적이고 공감적",
            success_rate=0.80,
        )

        # 형제자매 관계 패턴
        sibling_pattern = FamilyPrecisionPattern(
            relationship=FamilyRelationship.SIBLING,
            context_type=FamilyContextType.DAILY_LIFE,
            trigger_phrases=["형", "누나", "동생", "형제", "자매"],
            appropriate_responses=[
                "형제자매는 평생의 친구예요.",
                "서로를 지지하고 도와주는 관계를 만들어보세요.",
                "함께 성장하는 기쁨을 느껴보세요.",
            ],
            emotional_tone="친근하고 우정적",
            success_rate=0.75,
        )

        self.family_precision_patterns.extend(
            [parent_child_pattern, spouse_pattern, sibling_pattern]
        )

    def analyze_conversation_precision(
        self, message: str, family_context: Dict[str, Any]
    ) -> PrecisionAnalysis:
        """대화 정밀도 분석"""
        try:
            analysis_id = f"precision_analysis_{len(self.precision_analyses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 관계 정확도 분석
            relationship_accuracy = self._analyze_relationship_accuracy(
                message, family_context
            )

            # 맥락 적절성 분석
            context_appropriateness = self._analyze_context_appropriateness(
                message, family_context
            )

            # 감정 민감도 분석
            emotional_sensitivity = self._analyze_emotional_sensitivity(
                message, family_context
            )

            # 가족 가치 정렬 분석
            family_value_alignment = self._analyze_family_value_alignment(
                message, family_context
            )

            # 전체 정밀도 계산
            overall_precision = (
                relationship_accuracy
                + context_appropriateness
                + emotional_sensitivity
                + family_value_alignment
            ) / 4

            # 개선 제안 생성
            improvement_suggestions = self._generate_improvement_suggestions(
                relationship_accuracy,
                context_appropriateness,
                emotional_sensitivity,
                family_value_alignment,
            )

            precision_analysis = PrecisionAnalysis(
                id=analysis_id,
                message_id=f"message_{len(self.precision_analyses) + 1}",
                relationship_accuracy=relationship_accuracy,
                context_appropriateness=context_appropriateness,
                emotional_sensitivity=emotional_sensitivity,
                family_value_alignment=family_value_alignment,
                overall_precision=overall_precision,
                improvement_suggestions=improvement_suggestions,
                timestamp=datetime.now(),
            )

            self.precision_analyses.append(precision_analysis)
            logger.info(f"대화 정밀도 분석 완료: {analysis_id}")

            return precision_analysis

        except Exception as e:
            logger.error(f"대화 정밀도 분석 실패: {e}")
            raise

    def _analyze_relationship_accuracy(
        self, message: str, family_context: Dict[str, Any]
    ) -> float:
        """관계 정확도 분석"""
        message_lower = message.lower()

        # 가족 관계 키워드 매칭
        relationship_keywords = {
            FamilyRelationship.PARENT_CHILD: [
                "아이",
                "자식",
                "아들",
                "딸",
                "키우",
                "육아",
                "부모",
            ],
            FamilyRelationship.SPOUSE: ["남편", "아내", "배우자", "부부", "결혼"],
            FamilyRelationship.SIBLING: ["형", "누나", "동생", "형제", "자매"],
            FamilyRelationship.GRANDPARENT_GRANDCHILD: [
                "할아버지",
                "할머니",
                "손자",
                "손녀",
                "조부모",
            ],
            FamilyRelationship.EXTENDED_FAMILY: ["삼촌", "이모", "사촌", "친척"],
        }

        # 메시지에서 관계 키워드 확인
        matched_relationships = []
        for relationship, keywords in relationship_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                matched_relationships.append(relationship)

        # 관계 정확도 계산
        if matched_relationships:
            # 가장 적합한 관계 선택 (첫 번째 매칭)
            target_relationship = matched_relationships[0]

            # 관계별 정밀도 점수
            relationship_scores = {
                FamilyRelationship.PARENT_CHILD: 0.9,
                FamilyRelationship.SPOUSE: 0.85,
                FamilyRelationship.SIBLING: 0.8,
                FamilyRelationship.GRANDPARENT_GRANDCHILD: 0.75,
                FamilyRelationship.EXTENDED_FAMILY: 0.7,
            }

            return relationship_scores.get(target_relationship, 0.5)

        return 0.3  # 관계 키워드가 없으면 낮은 점수

    def _analyze_context_appropriateness(
        self, message: str, family_context: Dict[str, Any]
    ) -> float:
        """맥락 적절성 분석"""
        message_lower = message.lower()

        # 맥락별 키워드
        context_keywords = {
            FamilyContextType.DAILY_LIFE: ["일상", "하루", "생활", "루틴", "습관"],
            FamilyContextType.EMOTIONAL_SUPPORT: [
                "감정",
                "기분",
                "마음",
                "위로",
                "지지",
            ],
            FamilyContextType.EDUCATION: ["학습", "교육", "배움", "성장", "발달"],
            FamilyContextType.DISCIPLINE: ["훈육", "규칙", "제한", "벌", "교정"],
            FamilyContextType.CELEBRATION: ["축하", "기념", "파티", "선물", "행복"],
            FamilyContextType.CRISIS: ["위기", "문제", "어려움", "도움", "해결"],
        }

        # 메시지에서 맥락 키워드 확인
        matched_contexts = []
        for context_type, keywords in context_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                matched_contexts.append(context_type)

        # 맥락 적절성 계산
        if matched_contexts:
            # 가장 적합한 맥락 선택
            target_context = matched_contexts[0]

            # 맥락별 적절성 점수
            context_scores = {
                FamilyContextType.EMOTIONAL_SUPPORT: 0.9,
                FamilyContextType.DAILY_LIFE: 0.85,
                FamilyContextType.EDUCATION: 0.8,
                FamilyContextType.CELEBRATION: 0.75,
                FamilyContextType.DISCIPLINE: 0.7,
                FamilyContextType.CRISIS: 0.65,
            }

            return context_scores.get(target_context, 0.5)

        return 0.4  # 맥락 키워드가 없으면 낮은 점수

    def _analyze_emotional_sensitivity(
        self, message: str, family_context: Dict[str, Any]
    ) -> float:
        """감정 민감도 분석"""
        message_lower = message.lower()

        # 감정 관련 키워드
        emotional_keywords = [
            "사랑",
            "기쁨",
            "슬픔",
            "화남",
            "걱정",
            "감사",
            "미안",
            "고마워",
            "행복",
            "우울",
            "스트레스",
            "안도",
            "희망",
            "실망",
            "분노",
            "평온",
        ]

        # 감정 키워드 개수 계산
        emotional_word_count = sum(
            1 for keyword in emotional_keywords if keyword in message_lower
        )

        # 감정 민감도 점수 계산
        if emotional_word_count > 0:
            sensitivity_score = min(1.0, 0.3 + (emotional_word_count * 0.1))
        else:
            sensitivity_score = 0.3

        return sensitivity_score

    def _analyze_family_value_alignment(
        self, message: str, family_context: Dict[str, Any]
    ) -> float:
        """가족 가치 정렬 분석"""
        message_lower = message.lower()

        # 가족 가치 키워드
        family_value_keywords = [
            "사랑",
            "소통",
            "이해",
            "존중",
            "신뢰",
            "지지",
            "성장",
            "화합",
            "인내",
            "용서",
            "감사",
            "희생",
            "책임",
            "협력",
            "창의성",
            "평등",
        ]

        # 가족 가치 키워드 개수 계산
        value_word_count = sum(
            1 for keyword in family_value_keywords if keyword in message_lower
        )

        # 가족 가치 정렬 점수 계산
        if value_word_count > 0:
            alignment_score = min(1.0, 0.4 + (value_word_count * 0.08))
        else:
            alignment_score = 0.4

        return alignment_score

    def _generate_improvement_suggestions(
        self,
        relationship_accuracy: float,
        context_appropriateness: float,
        emotional_sensitivity: float,
        family_value_alignment: float,
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        if relationship_accuracy < 0.7:
            suggestions.append("가족 관계를 더 명확히 표현해보세요.")

        if context_appropriateness < 0.7:
            suggestions.append("상황에 맞는 적절한 표현을 사용해보세요.")

        if emotional_sensitivity < 0.6:
            suggestions.append("감정을 더 자세히 표현해보세요.")

        if family_value_alignment < 0.6:
            suggestions.append("가족의 가치관을 고려한 표현을 사용해보세요.")

        if not suggestions:
            suggestions.append("이미 좋은 대화 정밀도를 보이고 있습니다!")

        return suggestions

    def generate_precision_enhanced_response(
        self,
        original_message: str,
        family_context: Dict[str, Any],
        precision_analysis: PrecisionAnalysis,
    ) -> PrecisionResponse:
        """정밀도 향상 응답 생성"""
        try:
            response_id = f"precision_response_{len(self.precision_responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 관계별 특화 요소 추출
            relationship_specific_elements = (
                self._extract_relationship_specific_elements(
                    original_message, family_context
                )
            )

            # 맥락 적절한 구문 생성
            context_appropriate_phrases = self._generate_context_appropriate_phrases(
                original_message, family_context
            )

            # 감정 지원 요소 생성
            emotional_support_elements = self._generate_emotional_support_elements(
                original_message, family_context
            )

            # 정밀도 향상 응답 생성
            precision_enhanced_response = self._create_precision_enhanced_response(
                original_message,
                relationship_specific_elements,
                context_appropriate_phrases,
                emotional_support_elements,
            )

            # 신뢰도 점수 계산
            confidence_score = self._calculate_precision_confidence_score(
                precision_analysis, precision_enhanced_response
            )

            precision_response = PrecisionResponse(
                id=response_id,
                analysis_id=precision_analysis.id,
                original_message=original_message,
                precision_enhanced_response=precision_enhanced_response,
                relationship_specific_elements=relationship_specific_elements,
                context_appropriate_phrases=context_appropriate_phrases,
                emotional_support_elements=emotional_support_elements,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
            )

            self.precision_responses.append(precision_response)
            logger.info(f"정밀도 향상 응답 생성: {response_id}")

            return precision_response

        except Exception as e:
            logger.error(f"정밀도 향상 응답 생성 실패: {e}")
            raise

    def _extract_relationship_specific_elements(
        self, message: str, family_context: Dict[str, Any]
    ) -> List[str]:
        """관계별 특화 요소 추출"""
        elements = []

        # 부모-자식 관계 요소
        if any(word in message.lower() for word in ["아이", "자식", "키우"]):
            elements.extend(["사랑으로 기르기", "성장 지켜보기", "인내심"])

        # 배우자 관계 요소
        if any(word in message.lower() for word in ["남편", "아내", "부부"]):
            elements.extend(["상호 이해", "소통", "함께 성장"])

        # 형제자매 관계 요소
        if any(word in message.lower() for word in ["형", "동생", "형제"]):
            elements.extend(["우정", "지지", "함께 성장"])

        return elements

    def _generate_context_appropriate_phrases(
        self, message: str, family_context: Dict[str, Any]
    ) -> List[str]:
        """맥락 적절한 구문 생성"""
        phrases = []

        # 감정 지원 맥락
        if any(word in message.lower() for word in ["슬퍼", "화나", "걱정"]):
            phrases.extend(
                ["마음을 이해해드릴게요", "함께 해결해보아요", "지지해드릴게요"]
            )

        # 일상 맥락
        if any(word in message.lower() for word in ["하루", "일상", "생활"]):
            phrases.extend(["일상의 소중함", "함께하는 시간", "작은 기쁨"])

        # 교육 맥락
        if any(word in message.lower() for word in ["배우", "교육", "성장"]):
            phrases.extend(["함께 배우기", "성장의 기쁨", "지지하는 마음"])

        return phrases

    def _generate_emotional_support_elements(
        self, message: str, family_context: Dict[str, Any]
    ) -> List[str]:
        """감정 지원 요소 생성"""
        elements = []

        # 감정 상태에 따른 지원 요소
        if any(word in message.lower() for word in ["슬퍼", "우울"]):
            elements.extend(["공감", "위로", "지지"])
        elif any(word in message.lower() for word in ["화나", "짜증"]):
            elements.extend(["이해", "차분함", "해결책"])
        elif any(word in message.lower() for word in ["기뻐", "행복"]):
            elements.extend(["함께 기뻐하기", "축하", "지지"])
        elif any(word in message.lower() for word in ["걱정", "불안"]):
            elements.extend(["안심", "함께 생각하기", "지지"])

        return elements

    def _create_precision_enhanced_response(
        self,
        original_message: str,
        relationship_elements: List[str],
        context_phrases: List[str],
        emotional_elements: List[str],
    ) -> str:
        """정밀도 향상 응답 생성"""
        # 기본 응답 구조
        enhanced_response = "가족의 관점에서 생각해보니, "

        # 관계별 특화 요소 추가
        if relationship_elements:
            enhanced_response += f"{', '.join(relationship_elements)}이 중요해요. "

        # 맥락 적절한 구문 추가
        if context_phrases:
            enhanced_response += f"{', '.join(context_phrases)}을 통해 "

        # 감정 지원 요소 추가
        if emotional_elements:
            enhanced_response += f"{', '.join(emotional_elements)}의 마음으로 "

        # 원래 메시지에 대한 응답
        enhanced_response += (
            "함께 해결해보아요. 가족의 사랑과 이해가 가장 큰 힘이 될 거예요."
        )

        return enhanced_response

    def _calculate_precision_confidence_score(
        self, precision_analysis: PrecisionAnalysis, enhanced_response: str
    ) -> float:
        """정밀도 신뢰도 점수 계산"""
        # 기본 점수
        base_score = precision_analysis.overall_precision

        # 응답 길이 점수
        word_count = len(enhanced_response.split())
        length_score = min(0.1, word_count * 0.005)

        # 가족 관련 키워드 점수
        family_keywords = ["가족", "사랑", "이해", "함께", "지지", "소통"]
        keyword_count = sum(
            1 for keyword in family_keywords if keyword in enhanced_response.lower()
        )
        keyword_score = min(0.1, keyword_count * 0.02)

        return min(1.0, base_score + length_score + keyword_score)

    def get_precision_statistics(self) -> Dict[str, Any]:
        """정밀도 통계 제공"""
        try:
            total_analyses = len(self.precision_analyses)
            total_responses = len(self.precision_responses)

            # 정밀도 수준별 통계
            precision_level_stats = {}
            for level in ConversationPrecisionLevel:
                level_analyses = [
                    a
                    for a in self.precision_analyses
                    if self._get_precision_level(a.overall_precision) == level
                ]
                precision_level_stats[level.value] = len(level_analyses)

            # 관계별 통계
            relationship_stats = {}
            for relationship in FamilyRelationship:
                relationship_patterns = [
                    p
                    for p in self.family_precision_patterns
                    if p.relationship == relationship
                ]
                relationship_stats[relationship.value] = len(relationship_patterns)

            # 평균 정밀도 점수
            avg_overall_precision = (
                sum(a.overall_precision for a in self.precision_analyses)
                / len(self.precision_analyses)
                if self.precision_analyses
                else 0
            )

            # 평균 신뢰도 점수
            avg_confidence = (
                sum(r.confidence_score for r in self.precision_responses)
                / len(self.precision_responses)
                if self.precision_responses
                else 0
            )

            statistics = {
                "total_analyses": total_analyses,
                "total_responses": total_responses,
                "precision_level_stats": precision_level_stats,
                "relationship_stats": relationship_stats,
                "average_overall_precision": avg_overall_precision,
                "average_confidence": avg_confidence,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info("정밀도 통계 생성 완료")
            return statistics

        except Exception as e:
            logger.error(f"정밀도 통계 생성 실패: {e}")
            return {}

    def _get_precision_level(
        self, precision_score: float
    ) -> ConversationPrecisionLevel:
        """정밀도 점수를 수준으로 변환"""
        if precision_score >= 0.8:
            return ConversationPrecisionLevel.EXCELLENT
        elif precision_score >= 0.6:
            return ConversationPrecisionLevel.GOOD
        elif precision_score >= 0.4:
            return ConversationPrecisionLevel.FAIR
        else:
            return ConversationPrecisionLevel.POOR

    def export_precision_data(self) -> Dict[str, Any]:
        """정밀도 데이터 내보내기"""
        try:
            export_data = {
                "precision_analyses": [
                    asdict(analysis) for analysis in self.precision_analyses
                ],
                "precision_responses": [
                    asdict(response) for response in self.precision_responses
                ],
                "family_precision_patterns": [
                    asdict(pattern) for pattern in self.family_precision_patterns
                ],
                "export_date": datetime.now().isoformat(),
            }

            logger.info("정밀도 데이터 내보내기 완료")
            return export_data

        except Exception as e:
            logger.error(f"정밀도 데이터 내보내기 실패: {e}")
            return {}

    def import_precision_data(self, data: Dict[str, Any]):
        """정밀도 데이터 가져오기"""
        try:
            # 정밀도 분석 가져오기
            for analysis_data in data.get("precision_analyses", []):
                # datetime 객체 변환
                if "timestamp" in analysis_data:
                    analysis_data["timestamp"] = datetime.fromisoformat(
                        analysis_data["timestamp"]
                    )

                precision_analysis = PrecisionAnalysis(**analysis_data)
                self.precision_analyses.append(precision_analysis)

            # 정밀도 응답 가져오기
            for response_data in data.get("precision_responses", []):
                # datetime 객체 변환
                if "timestamp" in response_data:
                    response_data["timestamp"] = datetime.fromisoformat(
                        response_data["timestamp"]
                    )

                precision_response = PrecisionResponse(**response_data)
                self.precision_responses.append(precision_response)

            # 가족 정밀도 패턴 가져오기
            for pattern_data in data.get("family_precision_patterns", []):
                family_precision_pattern = FamilyPrecisionPattern(**pattern_data)
                self.family_precision_patterns.append(family_precision_pattern)

            logger.info("정밀도 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"정밀도 데이터 가져오기 실패: {e}")
            raise


# 테스트 함수
def test_family_conversation_precision_system():
    """가족 대화 정밀도 시스템 테스트"""
    print("🎯 FamilyConversationPrecisionSystem 테스트 시작...")

    # 시스템 초기화
    precision_system = FamilyConversationPrecisionSystem()

    # 가족 맥락 설정
    family_context = {
        "relationship": "parent_child",
        "family_member_ages": [35, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
        "current_situation": "일상적인 대화",
        "emotional_state": "차분함",
        "communication_style": "따뜻하고 격려적",
    }

    # 1. 대화 정밀도 분석
    test_message = "아이가 학교에서 친구와 다퉈서 속상해해요. 어떻게 대처해야 할까요?"
    precision_analysis = precision_system.analyze_conversation_precision(
        test_message, family_context
    )
    print(
        f"✅ 대화 정밀도 분석: {precision_analysis.overall_precision:.2f} 전체 정밀도"
    )
    print(f"   관계 정확도: {precision_analysis.relationship_accuracy:.2f}")
    print(f"   맥락 적절성: {precision_analysis.context_appropriateness:.2f}")
    print(f"   감정 민감도: {precision_analysis.emotional_sensitivity:.2f}")
    print(f"   가족 가치 정렬: {precision_analysis.family_value_alignment:.2f}")
    print(f"   개선 제안: {precision_analysis.improvement_suggestions}")

    # 2. 정밀도 향상 응답 생성
    precision_response = precision_system.generate_precision_enhanced_response(
        test_message, family_context, precision_analysis
    )
    print(f"✅ 정밀도 향상 응답: {precision_response.confidence_score:.2f} 신뢰도")
    print(f"   원래 메시지: {precision_response.original_message}")
    print(f"   향상된 응답: {precision_response.precision_enhanced_response}")
    print(f"   관계별 특화 요소: {precision_response.relationship_specific_elements}")
    print(f"   맥락 적절한 구문: {precision_response.context_appropriate_phrases}")
    print(f"   감정 지원 요소: {precision_response.emotional_support_elements}")

    # 3. 정밀도 통계
    statistics = precision_system.get_precision_statistics()
    print(
        f"✅ 정밀도 통계: {statistics['total_analyses']}개 분석, {statistics['total_responses']}개 응답"
    )
    print(f"   정밀도 수준별: {statistics['precision_level_stats']}")
    print(f"   관계별: {statistics['relationship_stats']}")
    print(f"   평균 전체 정밀도: {statistics['average_overall_precision']:.2f}")
    print(f"   평균 신뢰도: {statistics['average_confidence']:.2f}")

    # 4. 데이터 내보내기/가져오기
    export_data = precision_system.export_precision_data()
    print(
        f"✅ 정밀도 데이터 내보내기: {len(export_data['precision_analyses'])}개 분석, {len(export_data['precision_responses'])}개 응답"
    )

    print("🎉 FamilyConversationPrecisionSystem 테스트 완료!")


if __name__ == "__main__":
    test_family_conversation_precision_system()
