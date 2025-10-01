"""
Phase 10: 기본 교훈 추출 시스템 (BasicLessonExtractor)
경험에서 핵심 교훈 자동 추출, 가족 특성에 맞는 지혜 형성, 다음 세대 전달 준비
"""

import json
import logging
import re
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LessonCategory(Enum):
    """교훈 카테고리 정의"""

    LIFE_WISDOM = "life_wisdom"
    FAMILY_DYNAMICS = "family_dynamics"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    PROBLEM_SOLVING = "problem_solving"
    COMMUNICATION = "communication"
    PERSONAL_GROWTH = "personal_growth"
    RELATIONSHIP_SKILLS = "relationship_skills"
    CREATIVITY = "creativity"


class LessonComplexity(Enum):
    """교훈 복잡도 정의"""

    BASIC = "basic"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class LessonApplicability(Enum):
    """교훈 적용성 정의"""

    UNIVERSAL = "universal"
    FAMILY_SPECIFIC = "family_specific"
    SITUATION_SPECIFIC = "situation_specific"
    PERSONAL_SPECIFIC = "personal_specific"


@dataclass
class ExtractedLesson:
    """추출된 교훈 데이터 구조"""

    id: str
    title: str
    description: str
    category: LessonCategory
    complexity: LessonComplexity
    applicability: LessonApplicability
    key_points: List[str]
    examples: List[str]
    family_context: Dict[str, Any]
    emotional_context: Dict[str, Any]
    learning_context: Dict[str, Any]
    confidence_score: float  # 0.0 to 1.0
    generational_value: float  # 0.0 to 1.0
    extraction_timestamp: datetime
    source_experiences: List[str]
    tags: List[str]
    next_generation_ready: bool

    def __post_init__(self):
        if self.extraction_timestamp is None:
            self.extraction_timestamp = datetime.now()


@dataclass
class LessonPattern:
    """교훈 패턴 데이터 구조"""

    id: str
    pattern_type: str
    frequency: int
    common_elements: List[str]
    family_members_involved: List[str]
    emotional_contexts: List[str]
    learning_contexts: List[str]
    pattern_significance: float  # 0.0 to 1.0
    generational_potential: float  # 0.0 to 1.0


@dataclass
class WisdomCollection:
    """지혜 수집 데이터 구조"""

    id: str
    title: str
    description: str
    lessons: List[str]
    family_specific_insights: List[str]
    universal_truths: List[str]
    generational_advice: List[str]
    collection_timestamp: datetime
    maturity_level: float  # 0.0 to 1.0
    completeness_score: float  # 0.0 to 1.0


class BasicLessonExtractor:
    """
    기본 교훈 추출 시스템
    경험에서 핵심 교훈 자동 추출, 가족 특성에 맞는 지혜 형성, 다음 세대 전달 준비
    """

    def __init__(self):
        self.extracted_lessons: List[ExtractedLesson] = []
        self.lesson_patterns: List[LessonPattern] = []
        self.wisdom_collections: List[WisdomCollection] = []
        self.family_context_memory: Dict[str, Any] = {}
        self.emotional_patterns: Dict[str, List[float]] = {}
        self.learning_patterns: Dict[str, List[float]] = {}
        self.generational_insights: List[Dict] = []

        logger.info("BasicLessonExtractor 초기화 완료")

    def extract_lesson_from_experience(
        self, experience_data: Dict, family_context: Dict = None
    ) -> ExtractedLesson:
        """
        경험에서 교훈 추출
        """
        try:
            # 교훈 카테고리 결정
            category = self._determine_lesson_category(experience_data)

            # 복잡도 결정
            complexity = self._determine_lesson_complexity(experience_data)

            # 적용성 결정
            applicability = self._determine_lesson_applicability(
                experience_data, family_context
            )

            # 핵심 포인트 추출
            key_points = self._extract_key_points(experience_data)

            # 예시 생성
            examples = self._generate_examples(experience_data)

            # 교훈 생성
            lesson = ExtractedLesson(
                id=str(uuid.uuid4()),
                title=self._generate_lesson_title(experience_data),
                description=self._generate_lesson_description(experience_data),
                category=category,
                complexity=complexity,
                applicability=applicability,
                key_points=key_points,
                examples=examples,
                family_context=family_context or {},
                emotional_context=self._extract_emotional_context(experience_data),
                learning_context=self._extract_learning_context(experience_data),
                confidence_score=self._calculate_confidence_score(experience_data),
                generational_value=self._calculate_generational_value(
                    experience_data, family_context
                ),
                extraction_timestamp=datetime.now(),
                source_experiences=[experience_data.get("id", "unknown")],
                tags=self._generate_lesson_tags(experience_data, category),
                next_generation_ready=self._is_next_generation_ready(
                    experience_data, family_context
                ),
            )

            self.extracted_lessons.append(lesson)

            # 패턴 분석 업데이트
            self._update_lesson_patterns(lesson)

            # 지혜 수집 업데이트
            self._update_wisdom_collections(lesson)

            logger.info(f"교훈 추출 완료: {lesson.title}")
            return lesson

        except Exception as e:
            logger.error(f"교훈 추출 실패: {e}")
            raise

    def analyze_lesson_patterns(self) -> Dict:
        """
        교훈 패턴 분석
        """
        try:
            analysis = {
                "total_lessons": len(self.extracted_lessons),
                "category_distribution": self._get_category_distribution(),
                "complexity_distribution": self._get_complexity_distribution(),
                "applicability_distribution": self._get_applicability_distribution(),
                "generational_ready_lessons": len(
                    [l for l in self.extracted_lessons if l.next_generation_ready]
                ),
                "family_specific_lessons": len(
                    [
                        l
                        for l in self.extracted_lessons
                        if l.applicability == LessonApplicability.FAMILY_SPECIFIC
                    ]
                ),
                "universal_lessons": len(
                    [
                        l
                        for l in self.extracted_lessons
                        if l.applicability == LessonApplicability.UNIVERSAL
                    ]
                ),
                "average_confidence": (
                    sum(l.confidence_score for l in self.extracted_lessons)
                    / len(self.extracted_lessons)
                    if self.extracted_lessons
                    else 0
                ),
                "average_generational_value": (
                    sum(l.generational_value for l in self.extracted_lessons)
                    / len(self.extracted_lessons)
                    if self.extracted_lessons
                    else 0
                ),
            }

            return analysis

        except Exception as e:
            logger.error(f"교훈 패턴 분석 실패: {e}")
            raise

    def generate_family_wisdom(self) -> WisdomCollection:
        """
        가족 지혜 생성
        """
        try:
            # 가족 특화 교훈 수집
            family_lessons = [
                l
                for l in self.extracted_lessons
                if l.applicability == LessonApplicability.FAMILY_SPECIFIC
            ]

            # 보편적 교훈 수집
            universal_lessons = [
                l
                for l in self.extracted_lessons
                if l.applicability == LessonApplicability.UNIVERSAL
            ]

            # 세대 전달 준비된 교훈 수집
            generational_lessons = [
                l for l in self.extracted_lessons if l.next_generation_ready
            ]

            wisdom = WisdomCollection(
                id=str(uuid.uuid4()),
                title="가족 지혜 모음",
                description="가족의 경험에서 추출된 지혜와 교훈",
                lessons=[l.id for l in family_lessons + universal_lessons],
                family_specific_insights=self._extract_family_insights(family_lessons),
                universal_truths=self._extract_universal_truths(universal_lessons),
                generational_advice=self._extract_generational_advice(
                    generational_lessons
                ),
                collection_timestamp=datetime.now(),
                maturity_level=self._calculate_wisdom_maturity(),
                completeness_score=self._calculate_wisdom_completeness(),
            )

            self.wisdom_collections.append(wisdom)

            logger.info("가족 지혜 생성 완료")
            return wisdom

        except Exception as e:
            logger.error(f"가족 지혜 생성 실패: {e}")
            raise

    def prepare_next_generation_lessons(self) -> List[Dict]:
        """
        다음 세대 전달 준비된 교훈들
        """
        try:
            ready_lessons = [
                l for l in self.extracted_lessons if l.next_generation_ready
            ]

            prepared_lessons = []
            for lesson in ready_lessons:
                prepared_lesson = {
                    "id": lesson.id,
                    "title": lesson.title,
                    "description": lesson.description,
                    "category": lesson.category.value,
                    "complexity": lesson.complexity.value,
                    "key_points": lesson.key_points,
                    "examples": lesson.examples,
                    "family_context": lesson.family_context,
                    "generational_value": lesson.generational_value,
                    "confidence_score": lesson.confidence_score,
                    "extraction_date": lesson.extraction_timestamp.isoformat(),
                    "tags": lesson.tags,
                }
                prepared_lessons.append(prepared_lesson)

            # 세대 가치 순으로 정렬
            prepared_lessons.sort(key=lambda x: x["generational_value"], reverse=True)

            return prepared_lessons

        except Exception as e:
            logger.error(f"다음 세대 교훈 준비 실패: {e}")
            raise

    def get_lesson_insights(self) -> Dict:
        """
        교훈 통찰력 제공
        """
        try:
            insights = {
                "total_lessons": len(self.extracted_lessons),
                "wisdom_collections": len(self.wisdom_collections),
                "next_generation_ready": len(
                    [l for l in self.extracted_lessons if l.next_generation_ready]
                ),
                "top_categories": self._get_top_lesson_categories(),
                "maturity_progression": self._analyze_maturity_progression(),
                "generational_potential": self._analyze_generational_potential(),
                "family_specific_insights": self._get_family_specific_insights(),
            }

            return insights

        except Exception as e:
            logger.error(f"교훈 통찰력 생성 실패: {e}")
            raise

    def _determine_lesson_category(self, experience_data: Dict) -> LessonCategory:
        """교훈 카테고리 결정"""
        experience_type = experience_data.get("type", "")
        emotional_impact = experience_data.get("emotional_impact", 0)
        learning_value = experience_data.get("learning_value", 0)

        if "family" in experience_type.lower():
            return LessonCategory.FAMILY_DYNAMICS
        elif emotional_impact > 0.5 or emotional_impact < -0.5:
            return LessonCategory.EMOTIONAL_INTELLIGENCE
        elif learning_value > 0.7:
            return LessonCategory.PERSONAL_GROWTH
        elif "problem" in experience_data.get("description", "").lower():
            return LessonCategory.PROBLEM_SOLVING
        elif "communication" in experience_data.get("description", "").lower():
            return LessonCategory.COMMUNICATION
        elif "relationship" in experience_data.get("description", "").lower():
            return LessonCategory.RELATIONSHIP_SKILLS
        elif "creative" in experience_data.get("description", "").lower():
            return LessonCategory.CREATIVITY
        else:
            return LessonCategory.LIFE_WISDOM

    def _determine_lesson_complexity(self, experience_data: Dict) -> LessonComplexity:
        """교훈 복잡도 결정"""
        learning_value = experience_data.get("learning_value", 0)
        emotional_impact = abs(experience_data.get("emotional_impact", 0))
        description_length = len(experience_data.get("description", ""))

        complexity_score = (
            learning_value * 0.4
            + emotional_impact * 0.3
            + min(description_length / 100, 1.0) * 0.3
        )

        if complexity_score > 0.8:
            return LessonComplexity.EXPERT
        elif complexity_score > 0.6:
            return LessonComplexity.ADVANCED
        elif complexity_score > 0.4:
            return LessonComplexity.INTERMEDIATE
        else:
            return LessonComplexity.BASIC

    def _determine_lesson_applicability(
        self, experience_data: Dict, family_context: Dict
    ) -> LessonApplicability:
        """교훈 적용성 결정"""
        if family_context and len(family_context) > 0:
            return LessonApplicability.FAMILY_SPECIFIC
        elif "universal" in experience_data.get("description", "").lower():
            return LessonApplicability.UNIVERSAL
        elif "situation" in experience_data.get("description", "").lower():
            return LessonApplicability.SITUATION_SPECIFIC
        else:
            return LessonApplicability.PERSONAL_SPECIFIC

    def _extract_key_points(self, experience_data: Dict) -> List[str]:
        """핵심 포인트 추출"""
        key_points = []
        description = experience_data.get("description", "")
        emotional_impact = experience_data.get("emotional_impact", 0)
        learning_value = experience_data.get("learning_value", 0)

        # 감정적 교훈
        if emotional_impact > 0.5:
            key_points.append("긍정적인 경험은 성장의 원동력이 됩니다")
        elif emotional_impact < -0.5:
            key_points.append("어려운 상황에서도 배울 점이 있습니다")

        # 학습 가치 교훈
        if learning_value > 0.7:
            key_points.append("실습을 통한 학습이 가장 효과적입니다")

        # 설명에서 핵심 문장 추출
        sentences = description.split(".")
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10 and any(
                keyword in sentence.lower()
                for keyword in ["중요", "배운", "교훈", "학습", "경험", "이해"]
            ):
                key_points.append(sentence)

        return key_points[:5]  # 최대 5개

    def _generate_examples(self, experience_data: Dict) -> List[str]:
        """예시 생성"""
        examples = []
        experience_type = experience_data.get("type", "")
        description = experience_data.get("description", "")

        # 경험 유형별 예시
        if "family" in experience_type.lower():
            examples.append("가족과의 대화에서 서로의 관점을 이해하는 것")
            examples.append("가족 활동을 통해 협력하는 방법")

        if "emotional" in experience_type.lower():
            examples.append("감정을 표현하고 이해하는 방법")
            examples.append("스트레스 상황에서 침착함을 유지하는 것")

        if "learning" in experience_type.lower():
            examples.append("새로운 기술을 배우는 과정")
            examples.append("실수를 통해 개선하는 방법")

        # 설명에서 구체적 예시 추출
        if "예를 들어" in description or "예시" in description:
            example_sentences = re.findall(r"예를 들어[^.]*\.|예시[^.]*\.", description)
            examples.extend(example_sentences)

        return examples[:3]  # 최대 3개

    def _generate_lesson_title(self, experience_data: Dict) -> str:
        """교훈 제목 생성"""
        experience_type = experience_data.get("type", "")
        category = self._determine_lesson_category(experience_data)

        title_templates = {
            LessonCategory.FAMILY_DYNAMICS: "가족 관계에서 배운 교훈",
            LessonCategory.EMOTIONAL_INTELLIGENCE: "감정 관리의 지혜",
            LessonCategory.PERSONAL_GROWTH: "개인 성장의 교훈",
            LessonCategory.PROBLEM_SOLVING: "문제 해결의 방법",
            LessonCategory.COMMUNICATION: "의사소통의 중요성",
            LessonCategory.RELATIONSHIP_SKILLS: "관계 형성의 기술",
            LessonCategory.CREATIVITY: "창의적 사고의 가치",
            LessonCategory.LIFE_WISDOM: "인생의 지혜",
        }

        return title_templates.get(category, "경험에서 배운 교훈")

    def _generate_lesson_description(self, experience_data: Dict) -> str:
        """교훈 설명 생성"""
        description = experience_data.get("description", "")
        emotional_impact = experience_data.get("emotional_impact", 0)
        learning_value = experience_data.get("learning_value", 0)

        base_description = f"{description}을 통해 "

        if learning_value > 0.8:
            base_description += "중요한 교훈을 얻었습니다. "
        elif learning_value > 0.5:
            base_description += "유용한 경험을 했습니다. "
        else:
            base_description += "경험을 쌓았습니다. "

        if emotional_impact > 0.5:
            base_description += "이 경험은 감정적으로 깊은 인상을 남겼습니다."
        elif emotional_impact < -0.5:
            base_description += "이 경험은 도전적이었지만 성장의 기회가 되었습니다."

        return base_description

    def _extract_emotional_context(self, experience_data: Dict) -> Dict[str, Any]:
        """감정적 맥락 추출"""
        return {
            "emotional_impact": experience_data.get("emotional_impact", 0),
            "mood_before": experience_data.get("mood_before"),
            "mood_after": experience_data.get("mood_after"),
            "emotional_intensity": abs(experience_data.get("emotional_impact", 0)),
            "emotional_direction": (
                "positive"
                if experience_data.get("emotional_impact", 0) > 0
                else "negative"
            ),
        }

    def _extract_learning_context(self, experience_data: Dict) -> Dict[str, Any]:
        """학습 맥락 추출"""
        return {
            "learning_value": experience_data.get("learning_value", 0),
            "learning_category": experience_data.get("category", ""),
            "learning_method": experience_data.get("type", ""),
            "duration": experience_data.get("duration_minutes", 0),
            "participants": experience_data.get("participants", []),
        }

    def _calculate_confidence_score(self, experience_data: Dict) -> float:
        """신뢰도 점수 계산"""
        learning_value = experience_data.get("learning_value", 0)
        emotional_clarity = abs(experience_data.get("emotional_impact", 0))
        description_quality = len(experience_data.get("description", "")) / 100

        return min(
            1.0,
            learning_value * 0.4 + emotional_clarity * 0.4 + description_quality * 0.2,
        )

    def _calculate_generational_value(
        self, experience_data: Dict, family_context: Dict
    ) -> float:
        """세대 가치 계산"""
        base_value = experience_data.get("learning_value", 0) * 0.4
        emotional_factor = abs(experience_data.get("emotional_impact", 0)) * 0.3
        family_factor = 0.3 if family_context and len(family_context) > 0 else 0.1

        return min(1.0, base_value + emotional_factor + family_factor)

    def _generate_lesson_tags(
        self, experience_data: Dict, category: LessonCategory
    ) -> List[str]:
        """교훈 태그 생성"""
        tags = [
            category.value,
            experience_data.get("type", ""),
            f"emotional_{'positive' if experience_data.get('emotional_impact', 0) > 0 else 'negative'}",
            f"learning_{'high' if experience_data.get('learning_value', 0) > 0.7 else 'medium' if experience_data.get('learning_value', 0) > 0.4 else 'low'}",
        ]

        if experience_data.get("family_context"):
            tags.append("family_specific")

        return tags

    def _is_next_generation_ready(
        self, experience_data: Dict, family_context: Dict
    ) -> bool:
        """다음 세대 전달 준비 여부"""
        learning_value = experience_data.get("learning_value", 0)
        emotional_impact = abs(experience_data.get("emotional_impact", 0))
        has_family_context = family_context and len(family_context) > 0

        # 높은 학습 가치, 강한 감정적 영향, 가족 맥락이 있는 교훈
        return learning_value > 0.6 and emotional_impact > 0.3 and has_family_context

    def _update_lesson_patterns(self, lesson: ExtractedLesson):
        """교훈 패턴 업데이트"""
        # 카테고리별 패턴
        category_pattern = next(
            (
                p
                for p in self.lesson_patterns
                if p.pattern_type == f"category_{lesson.category.value}"
            ),
            None,
        )

        if category_pattern:
            category_pattern.frequency += 1
            category_pattern.common_elements.append(lesson.title)
        else:
            new_pattern = LessonPattern(
                id=str(uuid.uuid4()),
                pattern_type=f"category_{lesson.category.value}",
                frequency=1,
                common_elements=[lesson.title],
                family_members_involved=[],
                emotional_contexts=[],
                learning_contexts=[],
                pattern_significance=0.5,
                generational_potential=lesson.generational_value,
            )
            self.lesson_patterns.append(new_pattern)

    def _update_wisdom_collections(self, lesson: ExtractedLesson):
        """지혜 수집 업데이트"""
        # 기존 지혜 수집에 교훈 추가
        if self.wisdom_collections:
            latest_wisdom = self.wisdom_collections[-1]
            if lesson.id not in latest_wisdom.lessons:
                latest_wisdom.lessons.append(lesson.id)
                latest_wisdom.completeness_score = self._calculate_wisdom_completeness()

    def _get_category_distribution(self) -> Dict[str, int]:
        """카테고리 분포"""
        distribution = {}
        for lesson in self.extracted_lessons:
            category = lesson.category.value
            distribution[category] = distribution.get(category, 0) + 1
        return distribution

    def _get_complexity_distribution(self) -> Dict[str, int]:
        """복잡도 분포"""
        distribution = {}
        for lesson in self.extracted_lessons:
            complexity = lesson.complexity.value
            distribution[complexity] = distribution.get(complexity, 0) + 1
        return distribution

    def _get_applicability_distribution(self) -> Dict[str, int]:
        """적용성 분포"""
        distribution = {}
        for lesson in self.extracted_lessons:
            applicability = lesson.applicability.value
            distribution[applicability] = distribution.get(applicability, 0) + 1
        return distribution

    def _get_top_lesson_categories(self) -> List[str]:
        """상위 교훈 카테고리"""
        category_counts = {}
        for lesson in self.extracted_lessons:
            category = lesson.category.value
            category_counts[category] = category_counts.get(category, 0) + 1

        sorted_categories = sorted(
            category_counts.items(), key=lambda x: x[1], reverse=True
        )
        return [category for category, _ in sorted_categories[:3]]

    def _analyze_maturity_progression(self) -> Dict:
        """성숙도 진행 분석"""
        if not self.extracted_lessons:
            return {"current_maturity": 0.0, "progression_rate": 0.0}

        # 시간순 정렬
        sorted_lessons = sorted(
            self.extracted_lessons, key=lambda x: x.extraction_timestamp
        )

        # 성숙도 계산 (복잡도와 신뢰도 기반)
        early_lessons = sorted_lessons[: len(sorted_lessons) // 2]
        late_lessons = sorted_lessons[len(sorted_lessons) // 2 :]

        early_maturity = (
            sum(l.confidence_score for l in early_lessons) / len(early_lessons)
            if early_lessons
            else 0
        )
        late_maturity = (
            sum(l.confidence_score for l in late_lessons) / len(late_lessons)
            if late_lessons
            else 0
        )

        current_maturity = late_maturity
        progression_rate = (late_maturity - early_maturity) / max(early_maturity, 0.1)

        return {
            "current_maturity": current_maturity,
            "progression_rate": progression_rate,
            "early_maturity": early_maturity,
            "late_maturity": late_maturity,
        }

    def _analyze_generational_potential(self) -> Dict:
        """세대 잠재력 분석"""
        if not self.extracted_lessons:
            return {"average_potential": 0.0, "high_potential_count": 0}

        generational_values = [l.generational_value for l in self.extracted_lessons]
        average_potential = sum(generational_values) / len(generational_values)
        high_potential_count = len([v for v in generational_values if v > 0.7])

        return {
            "average_potential": average_potential,
            "high_potential_count": high_potential_count,
            "potential_distribution": {
                "high": len([v for v in generational_values if v > 0.7]),
                "medium": len([v for v in generational_values if 0.4 <= v <= 0.7]),
                "low": len([v for v in generational_values if v < 0.4]),
            },
        }

    def _get_family_specific_insights(self) -> List[str]:
        """가족 특화 통찰력"""
        family_lessons = [
            l
            for l in self.extracted_lessons
            if l.applicability == LessonApplicability.FAMILY_SPECIFIC
        ]

        insights = []
        for lesson in family_lessons[:5]:  # 상위 5개
            insights.append(f"{lesson.title}: {lesson.description}")

        return insights

    def _extract_family_insights(
        self, family_lessons: List[ExtractedLesson]
    ) -> List[str]:
        """가족 통찰력 추출"""
        insights = []
        for lesson in family_lessons:
            insights.extend(lesson.key_points)
        return insights[:10]  # 최대 10개

    def _extract_universal_truths(
        self, universal_lessons: List[ExtractedLesson]
    ) -> List[str]:
        """보편적 진리 추출"""
        truths = []
        for lesson in universal_lessons:
            if lesson.generational_value > 0.7:
                truths.append(f"{lesson.title}: {lesson.description}")
        return truths[:5]  # 최대 5개

    def _extract_generational_advice(
        self, generational_lessons: List[ExtractedLesson]
    ) -> List[str]:
        """세대 조언 추출"""
        advice = []
        for lesson in generational_lessons:
            if lesson.next_generation_ready:
                advice.append(f"{lesson.title}: {lesson.description}")
        return advice[:5]  # 최대 5개

    def _calculate_wisdom_maturity(self) -> float:
        """지혜 성숙도 계산"""
        if not self.extracted_lessons:
            return 0.0

        # 평균 신뢰도와 복잡도를 기반으로 성숙도 계산
        avg_confidence = sum(l.confidence_score for l in self.extracted_lessons) / len(
            self.extracted_lessons
        )

        complexity_scores = {
            LessonComplexity.BASIC: 0.25,
            LessonComplexity.INTERMEDIATE: 0.5,
            LessonComplexity.ADVANCED: 0.75,
            LessonComplexity.EXPERT: 1.0,
        }

        avg_complexity = sum(
            complexity_scores[l.complexity] for l in self.extracted_lessons
        ) / len(self.extracted_lessons)

        return avg_confidence * 0.6 + avg_complexity * 0.4

    def _calculate_wisdom_completeness(self) -> float:
        """지혜 완성도 계산"""
        if not self.extracted_lessons:
            return 0.0

        # 다양한 카테고리와 복잡도를 고려한 완성도
        categories_covered = len(set(l.category for l in self.extracted_lessons))
        complexity_levels_covered = len(
            set(l.complexity for l in self.extracted_lessons)
        )

        category_completeness = min(categories_covered / 8, 1.0)  # 8개 카테고리
        complexity_completeness = min(
            complexity_levels_covered / 4, 1.0
        )  # 4개 복잡도 레벨

        return category_completeness * 0.6 + complexity_completeness * 0.4

    def export_lesson_data(self) -> Dict:
        """교훈 데이터 내보내기"""
        return {
            "extracted_lessons": [asdict(lesson) for lesson in self.extracted_lessons],
            "lesson_patterns": [asdict(pattern) for pattern in self.lesson_patterns],
            "wisdom_collections": [
                asdict(wisdom) for wisdom in self.wisdom_collections
            ],
            "generational_insights": self.generational_insights,
            "analysis": self.analyze_lesson_patterns(),
            "insights": self.get_lesson_insights(),
        }

    def import_lesson_data(self, data: Dict):
        """교훈 데이터 가져오기"""
        try:
            # 교훈 데이터 복원
            self.extracted_lessons = []
            for lesson_data in data.get("extracted_lessons", []):
                lesson_data["extraction_timestamp"] = datetime.fromisoformat(
                    lesson_data["extraction_timestamp"]
                )
                lesson_data["category"] = LessonCategory(lesson_data["category"])
                lesson_data["complexity"] = LessonComplexity(lesson_data["complexity"])
                lesson_data["applicability"] = LessonApplicability(
                    lesson_data["applicability"]
                )
                self.extracted_lessons.append(ExtractedLesson(**lesson_data))

            # 패턴 데이터 복원
            self.lesson_patterns = []
            for pattern_data in data.get("lesson_patterns", []):
                self.lesson_patterns.append(LessonPattern(**pattern_data))

            # 지혜 수집 데이터 복원
            self.wisdom_collections = []
            for wisdom_data in data.get("wisdom_collections", []):
                wisdom_data["collection_timestamp"] = datetime.fromisoformat(
                    wisdom_data["collection_timestamp"]
                )
                self.wisdom_collections.append(WisdomCollection(**wisdom_data))

            # 기타 데이터 복원
            self.generational_insights = data.get("generational_insights", [])

            logger.info("교훈 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"교훈 데이터 가져오기 실패: {e}")
            raise
