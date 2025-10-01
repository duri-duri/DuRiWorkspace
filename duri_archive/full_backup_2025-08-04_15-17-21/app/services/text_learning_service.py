#!/usr/bin/env python3
"""
TextBasedLearningSystem - Phase 11
텍스트 기반 학습 시스템

기능:
- 블로그, 기사, 논문 등 텍스트 기반 학습
- 텍스트 내용 분석 및 지식 추출
- 가족 맥락에 맞는 학습 내용 필터링
- 학습 진도 추적 및 관리
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


class TextType(Enum):
    """텍스트 유형"""

    BLOG = "blog"
    ARTICLE = "article"
    PAPER = "paper"
    NEWS = "news"
    BOOK = "book"
    MAGAZINE = "magazine"
    OTHER = "other"


class LearningCategory(Enum):
    """학습 카테고리"""

    FAMILY_RELATIONSHIP = "family_relationship"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    LIFE_SKILLS = "life_skills"
    KNOWLEDGE = "knowledge"
    CREATIVITY = "creativity"
    WISDOM = "wisdom"
    OTHER = "other"


class LearningLevel(Enum):
    """학습 수준"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


@dataclass
class TextContent:
    """텍스트 콘텐츠"""

    id: str
    title: str
    content: str
    text_type: TextType
    source_url: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[datetime] = None
    word_count: int = 0
    reading_time_minutes: int = 0


@dataclass
class ExtractedKnowledge:
    """추출된 지식"""

    id: str
    text_content_id: str
    key_concepts: List[str]
    main_ideas: List[str]
    family_relevant_insights: List[str]
    learning_category: LearningCategory
    learning_level: LearningLevel
    confidence_score: float
    extraction_date: datetime
    notes: Optional[str] = None


@dataclass
class LearningProgress:
    """학습 진도"""

    text_content_id: str
    completion_percentage: float
    understanding_score: float
    family_application_score: float
    last_accessed: datetime
    total_time_spent_minutes: int = 0
    review_count: int = 0


class TextBasedLearningSystem:
    """텍스트 기반 학습 시스템"""

    def __init__(self):
        self.text_contents: List[TextContent] = []
        self.extracted_knowledge: List[ExtractedKnowledge] = []
        self.learning_progress: List[LearningProgress] = []
        self.family_context: Dict[str, Any] = {}

        logger.info("TextBasedLearningSystem 초기화 완료")

    def add_text_content(self, content_data: Dict[str, Any]) -> TextContent:
        """텍스트 콘텐츠 추가"""
        try:
            # 기본 정보 설정
            content_id = f"text_{len(self.text_contents) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 텍스트 유형 파싱
            text_type = TextType(content_data.get("text_type", "other"))

            # 단어 수 계산
            word_count = len(content_data.get("content", "").split())

            # 읽기 시간 계산 (평균 분당 200단어)
            reading_time = max(1, word_count // 200)

            text_content = TextContent(
                id=content_id,
                title=content_data.get("title", "제목 없음"),
                content=content_data.get("content", ""),
                text_type=text_type,
                source_url=content_data.get("source_url"),
                author=content_data.get("author"),
                publish_date=content_data.get("publish_date"),
                word_count=word_count,
                reading_time_minutes=reading_time,
            )

            self.text_contents.append(text_content)
            logger.info(f"텍스트 콘텐츠 추가: {text_content.title}")

            return text_content

        except Exception as e:
            logger.error(f"텍스트 콘텐츠 추가 실패: {e}")
            raise

    def extract_knowledge_from_text(self, text_content_id: str) -> ExtractedKnowledge:
        """텍스트에서 지식 추출"""
        try:
            # 텍스트 콘텐츠 찾기
            text_content = next(
                (tc for tc in self.text_contents if tc.id == text_content_id), None
            )
            if not text_content:
                raise ValueError(f"텍스트 콘텐츠를 찾을 수 없습니다: {text_content_id}")

            # 키워드 추출 (간단한 구현)
            words = text_content.content.lower().split()
            word_freq = {}
            for word in words:
                if len(word) > 3:  # 3글자 이상만
                    word_freq[word] = word_freq.get(word, 0) + 1

            # 가장 빈도가 높은 단어들을 키 컨셉으로
            key_concepts = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[
                :10
            ]
            key_concepts = [word for word, freq in key_concepts]

            # 주요 아이디어 추출 (문장 단위로)
            sentences = re.split(r"[.!?]", text_content.content)
            main_ideas = [s.strip() for s in sentences if len(s.strip()) > 20][:5]

            # 가족 관련 인사이트 추출
            family_keywords = [
                "가족",
                "부모",
                "자식",
                "사랑",
                "관계",
                "소통",
                "이해",
                "지지",
                "성장",
            ]
            family_insights = []
            for sentence in sentences:
                if any(keyword in sentence for keyword in family_keywords):
                    family_insights.append(sentence.strip())

            # 학습 카테고리 결정
            learning_category = self._determine_learning_category(text_content.content)

            # 학습 수준 결정
            learning_level = self._determine_learning_level(text_content.content)

            # 신뢰도 점수 계산
            confidence_score = self._calculate_confidence_score(
                text_content, key_concepts, main_ideas
            )

            extracted_knowledge = ExtractedKnowledge(
                id=f"knowledge_{len(self.extracted_knowledge) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                text_content_id=text_content_id,
                key_concepts=key_concepts,
                main_ideas=main_ideas,
                family_relevant_insights=family_insights,
                learning_category=learning_category,
                learning_level=learning_level,
                confidence_score=confidence_score,
                extraction_date=datetime.now(),
            )

            self.extracted_knowledge.append(extracted_knowledge)
            logger.info(f"지식 추출 완료: {extracted_knowledge.id}")

            return extracted_knowledge

        except Exception as e:
            logger.error(f"지식 추출 실패: {e}")
            raise

    def _determine_learning_category(self, content: str) -> LearningCategory:
        """학습 카테고리 결정"""
        content_lower = content.lower()

        if any(word in content_lower for word in ["가족", "부모", "자식", "관계"]):
            return LearningCategory.FAMILY_RELATIONSHIP
        elif any(word in content_lower for word in ["감정", "공감", "이해", "소통"]):
            return LearningCategory.EMOTIONAL_INTELLIGENCE
        elif any(word in content_lower for word in ["기술", "방법", "실습", "훈련"]):
            return LearningCategory.LIFE_SKILLS
        elif any(
            word in content_lower for word in ["창의", "상상", "혁신", "아이디어"]
        ):
            return LearningCategory.CREATIVITY
        elif any(word in content_lower for word in ["지혜", "경험", "교훈", "인생"]):
            return LearningCategory.WISDOM
        else:
            return LearningCategory.KNOWLEDGE

    def _determine_learning_level(self, content: str) -> LearningLevel:
        """학습 수준 결정"""
        word_count = len(content.split())
        avg_word_length = (
            sum(len(word) for word in content.split()) / len(content.split())
            if content.split()
            else 0
        )

        if word_count < 500 and avg_word_length < 4:
            return LearningLevel.BEGINNER
        elif word_count < 1000 and avg_word_length < 5:
            return LearningLevel.INTERMEDIATE
        elif word_count < 2000 and avg_word_length < 6:
            return LearningLevel.ADVANCED
        else:
            return LearningLevel.EXPERT

    def _calculate_confidence_score(
        self, text_content: TextContent, key_concepts: List[str], main_ideas: List[str]
    ) -> float:
        """신뢰도 점수 계산"""
        # 기본 점수
        base_score = 0.5

        # 키 컨셉이 많을수록 높은 점수
        concept_score = min(0.3, len(key_concepts) * 0.03)

        # 주요 아이디어가 많을수록 높은 점수
        idea_score = min(0.2, len(main_ideas) * 0.04)

        # 텍스트 길이가 적절할수록 높은 점수 (너무 짧거나 길지 않음)
        length_score = 0.0
        if 100 <= text_content.word_count <= 2000:
            length_score = 0.1

        return min(1.0, base_score + concept_score + idea_score + length_score)

    def update_learning_progress(
        self, text_content_id: str, progress_data: Dict[str, Any]
    ) -> LearningProgress:
        """학습 진도 업데이트"""
        try:
            # 기존 진도 찾기
            existing_progress = next(
                (
                    p
                    for p in self.learning_progress
                    if p.text_content_id == text_content_id
                ),
                None,
            )

            if existing_progress:
                # 기존 진도 업데이트
                existing_progress.completion_percentage = progress_data.get(
                    "completion_percentage", existing_progress.completion_percentage
                )
                existing_progress.understanding_score = progress_data.get(
                    "understanding_score", existing_progress.understanding_score
                )
                existing_progress.family_application_score = progress_data.get(
                    "family_application_score",
                    existing_progress.family_application_score,
                )
                existing_progress.last_accessed = datetime.now()
                existing_progress.total_time_spent_minutes += progress_data.get(
                    "time_spent_minutes", 0
                )
                existing_progress.review_count += 1

                logger.info(f"학습 진도 업데이트: {text_content_id}")
                return existing_progress
            else:
                # 새로운 진도 생성
                new_progress = LearningProgress(
                    text_content_id=text_content_id,
                    completion_percentage=progress_data.get(
                        "completion_percentage", 0.0
                    ),
                    understanding_score=progress_data.get("understanding_score", 0.0),
                    family_application_score=progress_data.get(
                        "family_application_score", 0.0
                    ),
                    last_accessed=datetime.now(),
                    total_time_spent_minutes=progress_data.get("time_spent_minutes", 0),
                    review_count=1,
                )

                self.learning_progress.append(new_progress)
                logger.info(f"새로운 학습 진도 생성: {text_content_id}")
                return new_progress

        except Exception as e:
            logger.error(f"학습 진도 업데이트 실패: {e}")
            raise

    def get_learning_recommendations(
        self, family_context: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """학습 추천 제공"""
        try:
            recommendations = []

            # 가족 맥락에 맞는 콘텐츠 필터링
            relevant_contents = self._filter_family_relevant_contents(family_context)

            for content in relevant_contents:
                # 해당 콘텐츠의 지식 추출
                knowledge = next(
                    (
                        k
                        for k in self.extracted_knowledge
                        if k.text_content_id == content.id
                    ),
                    None,
                )

                if knowledge:
                    recommendation = {
                        "text_content": asdict(content),
                        "extracted_knowledge": asdict(knowledge),
                        "recommendation_score": self._calculate_recommendation_score(
                            content, knowledge, family_context
                        ),
                        "learning_category": knowledge.learning_category.value,
                        "learning_level": knowledge.learning_level.value,
                    }
                    recommendations.append(recommendation)

            # 추천 점수 순으로 정렬
            recommendations.sort(key=lambda x: x["recommendation_score"], reverse=True)

            logger.info(f"학습 추천 {len(recommendations)}개 생성")
            return recommendations[:10]  # 상위 10개만 반환

        except Exception as e:
            logger.error(f"학습 추천 생성 실패: {e}")
            return []

    def _filter_family_relevant_contents(
        self, family_context: Dict[str, Any] = None
    ) -> List[TextContent]:
        """가족 관련 콘텐츠 필터링"""
        if not family_context:
            return self.text_contents

        # 가족 맥락에 맞는 키워드
        family_keywords = [
            "가족",
            "부모",
            "자식",
            "사랑",
            "관계",
            "소통",
            "이해",
            "지지",
            "성장",
        ]

        relevant_contents = []
        for content in self.text_contents:
            content_lower = content.content.lower()
            if any(keyword in content_lower for keyword in family_keywords):
                relevant_contents.append(content)

        return relevant_contents

    def _calculate_recommendation_score(
        self,
        content: TextContent,
        knowledge: ExtractedKnowledge,
        family_context: Dict[str, Any] = None,
    ) -> float:
        """추천 점수 계산"""
        base_score = knowledge.confidence_score

        # 가족 관련성 점수
        family_relevance = len(knowledge.family_relevant_insights) * 0.1

        # 학습 수준 적합성 점수
        level_score = 0.0
        if knowledge.learning_level == LearningLevel.BEGINNER:
            level_score = 0.2
        elif knowledge.learning_level == LearningLevel.INTERMEDIATE:
            level_score = 0.3
        elif knowledge.learning_level == LearningLevel.ADVANCED:
            level_score = 0.4
        else:
            level_score = 0.5

        return min(1.0, base_score + family_relevance + level_score)

    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계 제공"""
        try:
            total_contents = len(self.text_contents)
            total_knowledge = len(self.extracted_knowledge)
            total_progress = len(self.learning_progress)

            # 카테고리별 통계
            category_stats = {}
            for category in LearningCategory:
                category_knowledge = [
                    k
                    for k in self.extracted_knowledge
                    if k.learning_category == category
                ]
                category_stats[category.value] = len(category_knowledge)

            # 수준별 통계
            level_stats = {}
            for level in LearningLevel:
                level_knowledge = [
                    k for k in self.extracted_knowledge if k.learning_level == level
                ]
                level_stats[level.value] = len(level_knowledge)

            # 평균 신뢰도
            avg_confidence = (
                sum(k.confidence_score for k in self.extracted_knowledge)
                / len(self.extracted_knowledge)
                if self.extracted_knowledge
                else 0
            )

            # 평균 학습 진도
            avg_completion = (
                sum(p.completion_percentage for p in self.learning_progress)
                / len(self.learning_progress)
                if self.learning_progress
                else 0
            )

            statistics = {
                "total_contents": total_contents,
                "total_knowledge": total_knowledge,
                "total_progress": total_progress,
                "category_stats": category_stats,
                "level_stats": level_stats,
                "average_confidence": avg_confidence,
                "average_completion": avg_completion,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info("학습 통계 생성 완료")
            return statistics

        except Exception as e:
            logger.error(f"학습 통계 생성 실패: {e}")
            return {}

    def export_learning_data(self) -> Dict[str, Any]:
        """학습 데이터 내보내기"""
        try:
            export_data = {
                "text_contents": [asdict(content) for content in self.text_contents],
                "extracted_knowledge": [
                    asdict(knowledge) for knowledge in self.extracted_knowledge
                ],
                "learning_progress": [
                    asdict(progress) for progress in self.learning_progress
                ],
                "export_date": datetime.now().isoformat(),
            }

            logger.info("학습 데이터 내보내기 완료")
            return export_data

        except Exception as e:
            logger.error(f"학습 데이터 내보내기 실패: {e}")
            return {}

    def import_learning_data(self, data: Dict[str, Any]):
        """학습 데이터 가져오기"""
        try:
            # 텍스트 콘텐츠 가져오기
            for content_data in data.get("text_contents", []):
                # datetime 객체 변환
                if "publish_date" in content_data and content_data["publish_date"]:
                    content_data["publish_date"] = datetime.fromisoformat(
                        content_data["publish_date"]
                    )

                text_content = TextContent(**content_data)
                self.text_contents.append(text_content)

            # 추출된 지식 가져오기
            for knowledge_data in data.get("extracted_knowledge", []):
                # datetime 객체 변환
                if "extraction_date" in knowledge_data:
                    knowledge_data["extraction_date"] = datetime.fromisoformat(
                        knowledge_data["extraction_date"]
                    )

                extracted_knowledge = ExtractedKnowledge(**knowledge_data)
                self.extracted_knowledge.append(extracted_knowledge)

            # 학습 진도 가져오기
            for progress_data in data.get("learning_progress", []):
                # datetime 객체 변환
                if "last_accessed" in progress_data:
                    progress_data["last_accessed"] = datetime.fromisoformat(
                        progress_data["last_accessed"]
                    )

                learning_progress = LearningProgress(**progress_data)
                self.learning_progress.append(learning_progress)

            logger.info("학습 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"학습 데이터 가져오기 실패: {e}")
            raise


# 테스트 함수
def test_text_learning_system():
    """텍스트 학습 시스템 테스트"""
    print("🧠 TextBasedLearningSystem 테스트 시작...")

    # 시스템 초기화
    text_learning = TextBasedLearningSystem()

    # 1. 텍스트 콘텐츠 추가
    sample_content = {
        "title": "가족 관계 개선을 위한 소통 방법",
        "content": """
        가족 간의 소통은 건강한 관계를 유지하는 핵심 요소입니다.
        서로의 감정을 이해하고 공감하는 것이 중요합니다.
        부모와 자식 간의 대화는 서로의 입장을 고려해야 합니다.
        사랑과 이해를 바탕으로 한 소통이 가족의 화합을 만들어냅니다.
        """,
        "text_type": "article",
        "source_url": "https://example.com/family-communication",
        "author": "가족 상담사 김철수",
    }

    text_content = text_learning.add_text_content(sample_content)
    print(f"✅ 텍스트 콘텐츠 추가: {text_content.title}")

    # 2. 지식 추출
    extracted_knowledge = text_learning.extract_knowledge_from_text(text_content.id)
    print(f"✅ 지식 추출 완료: {len(extracted_knowledge.key_concepts)}개 키 컨셉")
    print(f"   주요 아이디어: {len(extracted_knowledge.main_ideas)}개")
    print(
        f"   가족 관련 인사이트: {len(extracted_knowledge.family_relevant_insights)}개"
    )
    print(f"   학습 카테고리: {extracted_knowledge.learning_category.value}")
    print(f"   학습 수준: {extracted_knowledge.learning_level.value}")
    print(f"   신뢰도 점수: {extracted_knowledge.confidence_score:.2f}")

    # 3. 학습 진도 업데이트
    progress_data = {
        "completion_percentage": 75.0,
        "understanding_score": 80.0,
        "family_application_score": 85.0,
        "time_spent_minutes": 15,
    }

    learning_progress = text_learning.update_learning_progress(
        text_content.id, progress_data
    )
    print(f"✅ 학습 진도 업데이트: {learning_progress.completion_percentage}% 완료")

    # 4. 학습 추천
    family_context = {"family_type": "nuclear", "children_count": 2}
    recommendations = text_learning.get_learning_recommendations(family_context)
    print(f"✅ 학습 추천 {len(recommendations)}개 생성")

    # 5. 학습 통계
    statistics = text_learning.get_learning_statistics()
    print(
        f"✅ 학습 통계 생성: {statistics['total_contents']}개 콘텐츠, {statistics['total_knowledge']}개 지식"
    )

    # 6. 데이터 내보내기/가져오기
    export_data = text_learning.export_learning_data()
    print(f"✅ 학습 데이터 내보내기: {len(export_data['text_contents'])}개 콘텐츠")

    print("🎉 TextBasedLearningSystem 테스트 완료!")


if __name__ == "__main__":
    test_text_learning_system()
