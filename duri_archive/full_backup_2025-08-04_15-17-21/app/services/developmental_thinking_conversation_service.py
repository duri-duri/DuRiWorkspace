#!/usr/bin/env python3
"""
DevelopmentalThinkingConversationSystem - Phase 11
발전적 사고 대화 시스템

기능:
- 성장 지향적 대화 정밀도
- 학습 진도 인식 대화
- 발전적 사고 촉진
- 성장 단계별 맞춤 대화
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


class DevelopmentalStage(Enum):
    """발전 단계"""

    INFANT = "infant"  # 0-2세
    TODDLER = "toddler"  # 2-4세
    PRESCHOOL = "preschool"  # 4-6세
    EARLY_SCHOOL = "early_school"  # 6-9세
    MIDDLE_SCHOOL = "middle_school"  # 9-12세
    ADOLESCENT = "adolescent"  # 12-18세
    ADULT = "adult"  # 18세 이상


class GrowthOrientation(Enum):
    """성장 지향성"""

    COGNITIVE_DEVELOPMENT = "cognitive_development"
    EMOTIONAL_GROWTH = "emotional_growth"
    SOCIAL_SKILLS = "social_skills"
    CREATIVE_EXPRESSION = "creative_expression"
    PHYSICAL_DEVELOPMENT = "physical_development"
    MORAL_DEVELOPMENT = "moral_development"
    OTHER = "other"


class LearningProgressLevel(Enum):
    """학습 진도 수준"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


@dataclass
class DevelopmentalContext:
    """발전 맥락"""

    developmental_stage: DevelopmentalStage
    age: int
    current_abilities: List[str]
    learning_goals: List[str]
    growth_areas: List[str]
    family_support_level: float


@dataclass
class GrowthAnalysis:
    """성장 분석"""

    id: str
    conversation_id: str
    developmental_stage: DevelopmentalStage
    growth_orientation: GrowthOrientation
    learning_progress: LearningProgressLevel
    growth_potential: float
    support_needed: List[str]
    next_steps: List[str]
    timestamp: datetime


@dataclass
class DevelopmentalResponse:
    """발전적 응답"""

    id: str
    analysis_id: str
    original_message: str
    developmental_response: str
    growth_elements: List[str]
    learning_encouragement: List[str]
    next_development_steps: List[str]
    confidence_score: float
    timestamp: datetime
    notes: Optional[str] = None


@dataclass
class DevelopmentalPattern:
    """발전 패턴"""

    stage: DevelopmentalStage
    growth_orientation: GrowthOrientation
    trigger_phrases: List[str]
    developmental_responses: List[str]
    learning_activities: List[str]
    success_rate: float


class DevelopmentalThinkingConversationSystem:
    """발전적 사고 대화 시스템"""

    def __init__(self):
        self.growth_analyses: List[GrowthAnalysis] = []
        self.developmental_responses: List[DevelopmentalResponse] = []
        self.developmental_patterns: List[DevelopmentalPattern] = []
        self.family_context: Dict[str, Any] = {}

        # 발전 패턴 초기화
        self._initialize_developmental_patterns()

        logger.info("DevelopmentalThinkingConversationSystem 초기화 완료")

    def _initialize_developmental_patterns(self):
        """발전 패턴 초기화"""
        # 유아기 패턴
        infant_pattern = DevelopmentalPattern(
            stage=DevelopmentalStage.INFANT,
            growth_orientation=GrowthOrientation.PHYSICAL_DEVELOPMENT,
            trigger_phrases=["아기", "걷기", "말하기", "먹기", "잠자기"],
            developmental_responses=[
                "아기의 자연스러운 성장을 지켜보세요.",
                "안전한 환경에서 자유롭게 탐험할 수 있도록 도와주세요.",
                "사랑과 관심으로 아기의 기본 욕구를 충족시켜주세요.",
            ],
            learning_activities=["탐색 놀이", "기본 운동", "언어 자극"],
            success_rate=0.9,
        )

        # 걸음마기 패턴
        toddler_pattern = DevelopmentalPattern(
            stage=DevelopmentalStage.TODDLER,
            growth_orientation=GrowthOrientation.SOCIAL_SKILLS,
            trigger_phrases=["걸음마", "자기주장", "놀이", "친구", "규칙"],
            developmental_responses=[
                "자기주장을 인정하면서도 적절한 한계를 설정해주세요.",
                "다른 아이들과의 상호작용을 격려해주세요.",
                "일상적인 규칙과 루틴을 만들어주세요.",
            ],
            learning_activities=["협동 놀이", "기본 규칙 학습", "감정 표현"],
            success_rate=0.85,
        )

        # 유치원기 패턴
        preschool_pattern = DevelopmentalPattern(
            stage=DevelopmentalStage.PRESCHOOL,
            growth_orientation=GrowthOrientation.CREATIVE_EXPRESSION,
            trigger_phrases=["창작", "그리기", "상상", "이야기", "놀이"],
            developmental_responses=[
                "창의적 표현을 자유롭게 할 수 있도록 도와주세요.",
                "상상력을 키우는 활동을 격려해주세요.",
                "자신의 생각과 감정을 표현할 수 있도록 지지해주세요.",
            ],
            learning_activities=["창작 활동", "이야기 나누기", "상상 놀이"],
            success_rate=0.8,
        )

        self.developmental_patterns.extend(
            [infant_pattern, toddler_pattern, preschool_pattern]
        )

    def analyze_developmental_thinking(
        self, message: str, family_context: Dict[str, Any]
    ) -> GrowthAnalysis:
        """발전적 사고 분석"""
        try:
            analysis_id = f"growth_analysis_{len(self.growth_analyses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 발전 단계 결정
            developmental_stage = self._determine_developmental_stage(
                message, family_context
            )

            # 성장 지향성 분석
            growth_orientation = self._analyze_growth_orientation(
                message, family_context
            )

            # 학습 진도 수준 결정
            learning_progress = self._determine_learning_progress(
                message, family_context
            )

            # 성장 잠재력 계산
            growth_potential = self._calculate_growth_potential(
                message, developmental_stage, growth_orientation
            )

            # 필요한 지원 분석
            support_needed = self._analyze_support_needed(
                message, developmental_stage, growth_orientation
            )

            # 다음 단계 제안
            next_steps = self._suggest_next_steps(
                developmental_stage, growth_orientation, learning_progress
            )

            growth_analysis = GrowthAnalysis(
                id=analysis_id,
                conversation_id=f"conversation_{len(self.growth_analyses) + 1}",
                developmental_stage=developmental_stage,
                growth_orientation=growth_orientation,
                learning_progress=learning_progress,
                growth_potential=growth_potential,
                support_needed=support_needed,
                next_steps=next_steps,
                timestamp=datetime.now(),
            )

            self.growth_analyses.append(growth_analysis)
            logger.info(f"발전적 사고 분석 완료: {analysis_id}")

            return growth_analysis

        except Exception as e:
            logger.error(f"발전적 사고 분석 실패: {e}")
            raise

    def _determine_developmental_stage(
        self, message: str, family_context: Dict[str, Any]
    ) -> DevelopmentalStage:
        """발전 단계 결정"""
        message_lower = message.lower()

        # 연령 기반 결정
        if "age" in family_context:
            age = family_context["age"]
            if age < 2:
                return DevelopmentalStage.INFANT
            elif age < 4:
                return DevelopmentalStage.TODDLER
            elif age < 6:
                return DevelopmentalStage.PRESCHOOL
            elif age < 9:
                return DevelopmentalStage.EARLY_SCHOOL
            elif age < 12:
                return DevelopmentalStage.MIDDLE_SCHOOL
            elif age < 18:
                return DevelopmentalStage.ADOLESCENT
            else:
                return DevelopmentalStage.ADULT

        # 메시지 내용 기반 결정
        if any(word in message_lower for word in ["아기", "걷기", "말하기", "먹기"]):
            return DevelopmentalStage.INFANT
        elif any(
            word in message_lower for word in ["걸음마", "자기주장", "놀이", "친구"]
        ):
            return DevelopmentalStage.TODDLER
        elif any(
            word in message_lower for word in ["창작", "그리기", "상상", "이야기"]
        ):
            return DevelopmentalStage.PRESCHOOL
        elif any(word in message_lower for word in ["학습", "학교", "숙제", "친구"]):
            return DevelopmentalStage.EARLY_SCHOOL
        elif any(
            word in message_lower for word in ["자기주장", "감정", "관계", "성장"]
        ):
            return DevelopmentalStage.ADOLESCENT
        else:
            return DevelopmentalStage.ADULT

    def _analyze_growth_orientation(
        self, message: str, family_context: Dict[str, Any]
    ) -> GrowthOrientation:
        """성장 지향성 분석"""
        message_lower = message.lower()

        # 인지 발달
        if any(
            word in message_lower
            for word in ["학습", "배우", "생각", "이해", "문제해결"]
        ):
            return GrowthOrientation.COGNITIVE_DEVELOPMENT

        # 정서적 성장
        elif any(
            word in message_lower for word in ["감정", "기분", "마음", "위로", "지지"]
        ):
            return GrowthOrientation.EMOTIONAL_GROWTH

        # 사회적 기술
        elif any(
            word in message_lower for word in ["친구", "관계", "소통", "협력", "공유"]
        ):
            return GrowthOrientation.SOCIAL_SKILLS

        # 창의적 표현
        elif any(
            word in message_lower for word in ["창작", "그리기", "상상", "예술", "표현"]
        ):
            return GrowthOrientation.CREATIVE_EXPRESSION

        # 신체 발달
        elif any(
            word in message_lower for word in ["운동", "놀이", "걷기", "뛰기", "건강"]
        ):
            return GrowthOrientation.PHYSICAL_DEVELOPMENT

        # 도덕적 발달
        elif any(
            word in message_lower for word in ["도덕", "윤리", "선악", "책임", "양심"]
        ):
            return GrowthOrientation.MORAL_DEVELOPMENT

        else:
            return GrowthOrientation.OTHER

    def _determine_learning_progress(
        self, message: str, family_context: Dict[str, Any]
    ) -> LearningProgressLevel:
        """학습 진도 수준 결정"""
        message_lower = message.lower()

        # 학습 관련 키워드 개수
        learning_keywords = ["배우", "학습", "이해", "성장", "발전", "진보", "향상"]
        learning_word_count = sum(
            1 for keyword in learning_keywords if keyword in message_lower
        )

        # 복잡성 분석
        word_count = len(message.split())
        complexity_score = word_count / 20  # 20단어를 기준으로

        # 종합 점수 계산
        total_score = learning_word_count * 0.3 + complexity_score * 0.7

        if total_score >= 0.8:
            return LearningProgressLevel.MASTER
        elif total_score >= 0.6:
            return LearningProgressLevel.ADVANCED
        elif total_score >= 0.4:
            return LearningProgressLevel.INTERMEDIATE
        else:
            return LearningProgressLevel.BEGINNER

    def _calculate_growth_potential(
        self, message: str, stage: DevelopmentalStage, orientation: GrowthOrientation
    ) -> float:
        """성장 잠재력 계산"""
        base_score = 0.5

        # 발전 단계별 점수
        stage_scores = {
            DevelopmentalStage.INFANT: 0.9,
            DevelopmentalStage.TODDLER: 0.85,
            DevelopmentalStage.PRESCHOOL: 0.8,
            DevelopmentalStage.EARLY_SCHOOL: 0.75,
            DevelopmentalStage.MIDDLE_SCHOOL: 0.7,
            DevelopmentalStage.ADOLESCENT: 0.65,
            DevelopmentalStage.ADULT: 0.6,
        }
        stage_score = stage_scores.get(stage, 0.5)

        # 성장 지향성별 점수
        orientation_scores = {
            GrowthOrientation.COGNITIVE_DEVELOPMENT: 0.1,
            GrowthOrientation.EMOTIONAL_GROWTH: 0.1,
            GrowthOrientation.SOCIAL_SKILLS: 0.1,
            GrowthOrientation.CREATIVE_EXPRESSION: 0.1,
            GrowthOrientation.PHYSICAL_DEVELOPMENT: 0.1,
            GrowthOrientation.MORAL_DEVELOPMENT: 0.1,
            GrowthOrientation.OTHER: 0.05,
        }
        orientation_score = orientation_scores.get(orientation, 0.05)

        return min(1.0, base_score + stage_score + orientation_score)

    def _analyze_support_needed(
        self, message: str, stage: DevelopmentalStage, orientation: GrowthOrientation
    ) -> List[str]:
        """필요한 지원 분석"""
        support_needed = []

        if stage == DevelopmentalStage.INFANT:
            support_needed.extend(["안전한 환경", "기본 욕구 충족", "언어 자극"])

        elif stage == DevelopmentalStage.TODDLER:
            support_needed.extend(
                ["자기주장 인정", "적절한 한계 설정", "사회적 상호작용"]
            )

        elif stage == DevelopmentalStage.PRESCHOOL:
            support_needed.extend(["창의적 표현", "상상력 발달", "감정 표현"])

        elif stage == DevelopmentalStage.EARLY_SCHOOL:
            support_needed.extend(["학습 동기", "자신감", "친구 관계"])

        elif stage == DevelopmentalStage.ADOLESCENT:
            support_needed.extend(["자기 정체성", "감정 조절", "독립성"])

        # 성장 지향성별 추가 지원
        if orientation == GrowthOrientation.EMOTIONAL_GROWTH:
            support_needed.append("감정 인식 및 표현")
        elif orientation == GrowthOrientation.SOCIAL_SKILLS:
            support_needed.append("사회적 기술 발달")
        elif orientation == GrowthOrientation.CREATIVE_EXPRESSION:
            support_needed.append("창의적 활동")

        return support_needed

    def _suggest_next_steps(
        self,
        stage: DevelopmentalStage,
        orientation: GrowthOrientation,
        progress: LearningProgressLevel,
    ) -> List[str]:
        """다음 단계 제안"""
        next_steps = []

        # 발전 단계별 다음 단계
        if stage == DevelopmentalStage.INFANT:
            next_steps.extend(["기본 운동 발달", "언어 자극 강화", "탐색 활동 확대"])

        elif stage == DevelopmentalStage.TODDLER:
            next_steps.extend(
                ["자기주장과 협력의 균형", "사회적 상호작용 확대", "기본 규칙 이해"]
            )

        elif stage == DevelopmentalStage.PRESCHOOL:
            next_steps.extend(
                ["창의적 표현 활동", "상상력 발달 놀이", "감정 표현 연습"]
            )

        elif stage == DevelopmentalStage.EARLY_SCHOOL:
            next_steps.extend(["학습 동기 강화", "자신감 향상", "친구 관계 발달"])

        elif stage == DevelopmentalStage.ADOLESCENT:
            next_steps.extend(["자기 정체성 탐색", "감정 조절 기술", "독립성 발달"])

        # 학습 진도별 다음 단계
        if progress == LearningProgressLevel.BEGINNER:
            next_steps.append("기본 개념 이해")
        elif progress == LearningProgressLevel.INTERMEDIATE:
            next_steps.append("실습과 적용")
        elif progress == LearningProgressLevel.ADVANCED:
            next_steps.append("심화 학습")
        elif progress == LearningProgressLevel.MASTER:
            next_steps.append("다른 사람 가르치기")

        return next_steps

    def generate_developmental_response(
        self,
        original_message: str,
        family_context: Dict[str, Any],
        growth_analysis: GrowthAnalysis,
    ) -> DevelopmentalResponse:
        """발전적 응답 생성"""
        try:
            response_id = f"developmental_response_{len(self.developmental_responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 성장 요소 추출
            growth_elements = self._extract_growth_elements(
                original_message, growth_analysis
            )

            # 학습 격려 요소 생성
            learning_encouragement = self._generate_learning_encouragement(
                growth_analysis
            )

            # 다음 발전 단계 제안
            next_development_steps = self._generate_next_development_steps(
                growth_analysis
            )

            # 발전적 응답 생성
            developmental_response = self._create_developmental_response(
                original_message,
                growth_elements,
                learning_encouragement,
                next_development_steps,
                growth_analysis,
            )

            # 신뢰도 점수 계산
            confidence_score = self._calculate_developmental_confidence_score(
                growth_analysis, developmental_response
            )

            developmental_response_obj = DevelopmentalResponse(
                id=response_id,
                analysis_id=growth_analysis.id,
                original_message=original_message,
                developmental_response=developmental_response,
                growth_elements=growth_elements,
                learning_encouragement=learning_encouragement,
                next_development_steps=next_development_steps,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
            )

            self.developmental_responses.append(developmental_response_obj)
            logger.info(f"발전적 응답 생성: {response_id}")

            return developmental_response_obj

        except Exception as e:
            logger.error(f"발전적 응답 생성 실패: {e}")
            raise

    def _extract_growth_elements(
        self, message: str, growth_analysis: GrowthAnalysis
    ) -> List[str]:
        """성장 요소 추출"""
        elements = []

        # 발전 단계별 성장 요소
        if growth_analysis.developmental_stage == DevelopmentalStage.INFANT:
            elements.extend(["기본 운동 발달", "언어 자극", "탐색 활동"])

        elif growth_analysis.developmental_stage == DevelopmentalStage.TODDLER:
            elements.extend(["자기주장 발달", "사회적 상호작용", "기본 규칙 이해"])

        elif growth_analysis.developmental_stage == DevelopmentalStage.PRESCHOOL:
            elements.extend(["창의적 표현", "상상력 발달", "감정 표현"])

        # 성장 지향성별 요소
        if growth_analysis.growth_orientation == GrowthOrientation.EMOTIONAL_GROWTH:
            elements.append("감정 인식 및 조절")
        elif growth_analysis.growth_orientation == GrowthOrientation.SOCIAL_SKILLS:
            elements.append("사회적 기술")
        elif (
            growth_analysis.growth_orientation == GrowthOrientation.CREATIVE_EXPRESSION
        ):
            elements.append("창의적 표현")

        return elements

    def _generate_learning_encouragement(
        self, growth_analysis: GrowthAnalysis
    ) -> List[str]:
        """학습 격려 요소 생성"""
        encouragement = []

        # 학습 진도별 격려
        if growth_analysis.learning_progress == LearningProgressLevel.BEGINNER:
            encouragement.extend(
                ["천천히 시작해보세요", "기본부터 차근차근", "실수해도 괜찮아요"]
            )

        elif growth_analysis.learning_progress == LearningProgressLevel.INTERMEDIATE:
            encouragement.extend(
                ["잘 하고 있어요", "조금 더 도전해보세요", "실습해보세요"]
            )

        elif growth_analysis.learning_progress == LearningProgressLevel.ADVANCED:
            encouragement.extend(
                ["훌륭해요", "더 깊이 탐구해보세요", "다른 사람에게 가르쳐보세요"]
            )

        elif growth_analysis.learning_progress == LearningProgressLevel.MASTER:
            encouragement.extend(
                [
                    "전문가 수준이에요",
                    "다른 사람을 도와주세요",
                    "새로운 도전을 해보세요",
                ]
            )

        return encouragement

    def _generate_next_development_steps(
        self, growth_analysis: GrowthAnalysis
    ) -> List[str]:
        """다음 발전 단계 생성"""
        return growth_analysis.next_steps

    def _create_developmental_response(
        self,
        original_message: str,
        growth_elements: List[str],
        learning_encouragement: List[str],
        next_steps: List[str],
        growth_analysis: GrowthAnalysis,
    ) -> str:
        """발전적 응답 생성"""
        response = f"현재 {growth_analysis.developmental_stage.value} 단계에서 "

        # 성장 요소 추가
        if growth_elements:
            response += f"{', '.join(growth_elements)}에 집중하고 있어요. "

        # 학습 격려 추가
        if learning_encouragement:
            response += f"{learning_encouragement[0]}. "

        # 다음 단계 제안
        if next_steps:
            response += f"다음으로는 {next_steps[0]}을 시도해보세요. "

        # 가족 지원 강조
        response += "가족의 지지와 격려가 가장 큰 힘이 될 거예요."

        return response

    def _calculate_developmental_confidence_score(
        self, growth_analysis: GrowthAnalysis, response: str
    ) -> float:
        """발전적 신뢰도 점수 계산"""
        # 기본 점수
        base_score = growth_analysis.growth_potential

        # 응답 길이 점수
        word_count = len(response.split())
        length_score = min(0.1, word_count * 0.005)

        # 발전 관련 키워드 점수
        development_keywords = ["성장", "발전", "학습", "진보", "향상", "발달"]
        keyword_count = sum(
            1 for keyword in development_keywords if keyword in response.lower()
        )
        keyword_score = min(0.1, keyword_count * 0.02)

        return min(1.0, base_score + length_score + keyword_score)

    def get_developmental_statistics(self) -> Dict[str, Any]:
        """발전적 통계 제공"""
        try:
            total_analyses = len(self.growth_analyses)
            total_responses = len(self.developmental_responses)

            # 발전 단계별 통계
            stage_stats = {}
            for stage in DevelopmentalStage:
                stage_analyses = [
                    a for a in self.growth_analyses if a.developmental_stage == stage
                ]
                stage_stats[stage.value] = len(stage_analyses)

            # 성장 지향성별 통계
            orientation_stats = {}
            for orientation in GrowthOrientation:
                orientation_analyses = [
                    a
                    for a in self.growth_analyses
                    if a.growth_orientation == orientation
                ]
                orientation_stats[orientation.value] = len(orientation_analyses)

            # 학습 진도별 통계
            progress_stats = {}
            for progress in LearningProgressLevel:
                progress_analyses = [
                    a for a in self.growth_analyses if a.learning_progress == progress
                ]
                progress_stats[progress.value] = len(progress_analyses)

            # 평균 성장 잠재력
            avg_growth_potential = (
                sum(a.growth_potential for a in self.growth_analyses)
                / len(self.growth_analyses)
                if self.growth_analyses
                else 0
            )

            # 평균 신뢰도
            avg_confidence = (
                sum(r.confidence_score for r in self.developmental_responses)
                / len(self.developmental_responses)
                if self.developmental_responses
                else 0
            )

            statistics = {
                "total_analyses": total_analyses,
                "total_responses": total_responses,
                "stage_stats": stage_stats,
                "orientation_stats": orientation_stats,
                "progress_stats": progress_stats,
                "average_growth_potential": avg_growth_potential,
                "average_confidence": avg_confidence,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info("발전적 통계 생성 완료")
            return statistics

        except Exception as e:
            logger.error(f"발전적 통계 생성 실패: {e}")
            return {}

    def export_developmental_data(self) -> Dict[str, Any]:
        """발전적 데이터 내보내기"""
        try:
            export_data = {
                "growth_analyses": [
                    asdict(analysis) for analysis in self.growth_analyses
                ],
                "developmental_responses": [
                    asdict(response) for response in self.developmental_responses
                ],
                "developmental_patterns": [
                    asdict(pattern) for pattern in self.developmental_patterns
                ],
                "export_date": datetime.now().isoformat(),
            }

            logger.info("발전적 데이터 내보내기 완료")
            return export_data

        except Exception as e:
            logger.error(f"발전적 데이터 내보내기 실패: {e}")
            return {}

    def import_developmental_data(self, data: Dict[str, Any]):
        """발전적 데이터 가져오기"""
        try:
            # 성장 분석 가져오기
            for analysis_data in data.get("growth_analyses", []):
                # datetime 객체 변환
                if "timestamp" in analysis_data:
                    analysis_data["timestamp"] = datetime.fromisoformat(
                        analysis_data["timestamp"]
                    )

                growth_analysis = GrowthAnalysis(**analysis_data)
                self.growth_analyses.append(growth_analysis)

            # 발전적 응답 가져오기
            for response_data in data.get("developmental_responses", []):
                # datetime 객체 변환
                if "timestamp" in response_data:
                    response_data["timestamp"] = datetime.fromisoformat(
                        response_data["timestamp"]
                    )

                developmental_response = DevelopmentalResponse(**response_data)
                self.developmental_responses.append(developmental_response)

            # 발전 패턴 가져오기
            for pattern_data in data.get("developmental_patterns", []):
                developmental_pattern = DevelopmentalPattern(**pattern_data)
                self.developmental_patterns.append(developmental_pattern)

            logger.info("발전적 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"발전적 데이터 가져오기 실패: {e}")
            raise


# 테스트 함수
def test_developmental_thinking_conversation_system():
    """발전적 사고 대화 시스템 테스트"""
    print("🧠 DevelopmentalThinkingConversationSystem 테스트 시작...")

    # 시스템 초기화
    developmental_system = DevelopmentalThinkingConversationSystem()

    # 가족 맥락 설정
    family_context = {
        "age": 5,
        "family_type": "nuclear",
        "children_count": 2,
        "children_ages": [5, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
    }

    # 1. 발전적 사고 분석
    test_message = "아이가 그림 그리기를 좋아하는데, 창의력을 더 키워주고 싶어요."
    growth_analysis = developmental_system.analyze_developmental_thinking(
        test_message, family_context
    )
    print(f"✅ 발전적 사고 분석: {growth_analysis.developmental_stage.value} 단계")
    print(f"   성장 지향성: {growth_analysis.growth_orientation.value}")
    print(f"   학습 진도: {growth_analysis.learning_progress.value}")
    print(f"   성장 잠재력: {growth_analysis.growth_potential:.2f}")
    print(f"   필요한 지원: {growth_analysis.support_needed}")
    print(f"   다음 단계: {growth_analysis.next_steps}")

    # 2. 발전적 응답 생성
    developmental_response = developmental_system.generate_developmental_response(
        test_message, family_context, growth_analysis
    )
    print(f"✅ 발전적 응답: {developmental_response.confidence_score:.2f} 신뢰도")
    print(f"   원래 메시지: {developmental_response.original_message}")
    print(f"   발전적 응답: {developmental_response.developmental_response}")
    print(f"   성장 요소: {developmental_response.growth_elements}")
    print(f"   학습 격려: {developmental_response.learning_encouragement}")
    print(f"   다음 발전 단계: {developmental_response.next_development_steps}")

    # 3. 발전적 통계
    statistics = developmental_system.get_developmental_statistics()
    print(
        f"✅ 발전적 통계: {statistics['total_analyses']}개 분석, {statistics['total_responses']}개 응답"
    )
    print(f"   발전 단계별: {statistics['stage_stats']}")
    print(f"   성장 지향성별: {statistics['orientation_stats']}")
    print(f"   학습 진도별: {statistics['progress_stats']}")
    print(f"   평균 성장 잠재력: {statistics['average_growth_potential']:.2f}")
    print(f"   평균 신뢰도: {statistics['average_confidence']:.2f}")

    # 4. 데이터 내보내기/가져오기
    export_data = developmental_system.export_developmental_data()
    print(
        f"✅ 발전적 데이터 내보내기: {len(export_data['growth_analyses'])}개 분석, {len(export_data['developmental_responses'])}개 응답"
    )

    print("🎉 DevelopmentalThinkingConversationSystem 테스트 완료!")


if __name__ == "__main__":
    test_developmental_thinking_conversation_system()
