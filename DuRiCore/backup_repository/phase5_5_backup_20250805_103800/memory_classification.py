#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 2 - 기억 분류 시스템
4가지 기억 타입 자동 분류 및 태깅 시스템
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import logging
import math
import re
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """기억 타입 열거형"""

    EXPERIENCE = "experience"  # 경험 기억
    KNOWLEDGE = "knowledge"  # 지식 기억
    PATTERN = "pattern"  # 패턴 기억
    EMOTION = "emotion"  # 감정 기억


class ClassificationMethod(Enum):
    """분류 방법 열거형"""

    KEYWORD = "keyword"  # 키워드 기반
    CONTEXT = "context"  # 컨텍스트 기반
    SEMANTIC = "semantic"  # 의미 기반
    HYBRID = "hybrid"  # 하이브리드


@dataclass
class ClassificationResult:
    """분류 결과"""

    memory_type: MemoryType
    confidence: float
    method: ClassificationMethod
    keywords_found: List[str]
    context_indicators: List[str]
    reasoning: str


@dataclass
class TagInfo:
    """태그 정보"""

    tag: str
    confidence: float
    source: str
    category: str


class MemoryClassifier:
    """기억 분류 시스템"""

    def __init__(self):
        # 키워드 사전
        self.keyword_dictionary = {
            MemoryType.EXPERIENCE: {
                "primary": [
                    "경험",
                    "발생",
                    "일어났다",
                    "했다",
                    "했다",
                    "만났다",
                    "갔다",
                    "왔다",
                ],
                "secondary": ["오늘", "어제", "지난주", "이번주", "그때", "그날"],
                "context": ["친구", "가족", "회사", "학교", "집", "카페", "영화관"],
            },
            MemoryType.KNOWLEDGE: {
                "primary": [
                    "알다",
                    "이해",
                    "학습",
                    "정보",
                    "지식",
                    "배웠다",
                    "알게되었다",
                    "깨달았다",
                ],
                "secondary": [
                    "책",
                    "강의",
                    "수업",
                    "강의",
                    "튜토리얼",
                    "문서",
                    "매뉴얼",
                ],
                "context": ["공부", "연구", "조사", "분석", "실험", "테스트"],
            },
            MemoryType.PATTERN: {
                "primary": [
                    "패턴",
                    "반복",
                    "규칙",
                    "습관",
                    "경향",
                    "항상",
                    "늘",
                    "보통",
                ],
                "secondary": ["매번", "언제나", "대부분", "주로", "자주", "가끔"],
                "context": ["행동", "생각", "감정", "반응", "결과", "결과"],
            },
            MemoryType.EMOTION: {
                "primary": [
                    "감정",
                    "기분",
                    "느낌",
                    "행복",
                    "슬픔",
                    "화남",
                    "기쁨",
                    "우울",
                ],
                "secondary": [
                    "좋다",
                    "나쁘다",
                    "재미있다",
                    "지루하다",
                    "짜증나다",
                    "신기하다",
                ],
                "context": ["마음", "심리", "상태", "분위기", "기분", "감정"],
            },
        }

        # 감정 키워드 사전
        self.emotion_keywords = {
            "positive": [
                "행복",
                "기쁨",
                "즐거움",
                "신기",
                "재미",
                "좋다",
                "만족",
                "감동",
            ],
            "negative": [
                "슬픔",
                "화남",
                "짜증",
                "우울",
                "실망",
                "걱정",
                "불안",
                "스트레스",
            ],
            "neutral": ["보통", "그냥", "평범", "무덤덤", "차분", "평온"],
        }

        # 컨텍스트 패턴
        self.context_patterns = {
            "learning": r"(학습|공부|배우|이해|알다|깨달)",
            "experience": r"(경험|발생|일어나|하다|만나|가다|오다)",
            "emotion": r"(감정|기분|느낌|마음|심리)",
            "pattern": r"(패턴|반복|규칙|습관|경향|항상|늘)",
        }

        # 분류 임계값
        self.confidence_threshold = 0.6
        self.minimum_confidence = 0.3

        logger.info("기억 분류 시스템 초기화 완료")

    async def classify_memory(
        self, content: str, context: Dict[str, Any]
    ) -> ClassificationResult:
        """메모리 분류 (주 메서드)"""
        try:
            # 여러 분류 방법 시도
            results = []

            # 1. 키워드 기반 분류
            keyword_result = self._classify_by_keywords(content, context)
            results.append(keyword_result)

            # 2. 컨텍스트 기반 분류
            context_result = self._classify_by_context(content, context)
            results.append(context_result)

            # 3. 의미 기반 분류
            semantic_result = self._classify_by_semantics(content, context)
            results.append(semantic_result)

            # 4. 하이브리드 분류 (최종 결정)
            final_result = self._hybrid_classification(results, content, context)

            logger.info(
                f"메모리 분류 완료: {final_result.memory_type.value} (신뢰도: {final_result.confidence:.3f})"
            )
            return final_result

        except Exception as e:
            logger.error(f"메모리 분류 오류: {e}")
            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.5,
                method=ClassificationMethod.KEYWORD,
                keywords_found=[],
                context_indicators=[],
                reasoning="분류 오류로 인한 기본값",
            )

    def _classify_by_keywords(
        self, content: str, context: Dict[str, Any]
    ) -> ClassificationResult:
        """키워드 기반 분류"""
        try:
            scores = {}
            keywords_found = {}

            for memory_type, keywords in self.keyword_dictionary.items():
                score = 0
                found_keywords = []

                # 주 키워드 검색
                for keyword in keywords["primary"]:
                    if keyword in content:
                        score += 3
                        found_keywords.append(keyword)

                # 보조 키워드 검색
                for keyword in keywords["secondary"]:
                    if keyword in content:
                        score += 2
                        found_keywords.append(keyword)

                # 컨텍스트 키워드 검색
                for keyword in keywords["context"]:
                    if keyword in content:
                        score += 1
                        found_keywords.append(keyword)

                scores[memory_type] = score
                keywords_found[memory_type] = found_keywords

            # 최고 점수 선택
            if scores:
                best_type = max(scores, key=scores.get)
                max_score = scores[best_type]

                # 신뢰도 계산 (최대 점수 기준)
                confidence = min(1.0, max_score / 10.0)

                return ClassificationResult(
                    memory_type=best_type,
                    confidence=confidence,
                    method=ClassificationMethod.KEYWORD,
                    keywords_found=keywords_found.get(best_type, []),
                    context_indicators=[],
                    reasoning=f"키워드 기반 분류: {best_type.value} (점수: {max_score})",
                )

            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.3,
                method=ClassificationMethod.KEYWORD,
                keywords_found=[],
                context_indicators=[],
                reasoning="키워드 없음으로 인한 기본값",
            )

        except Exception as e:
            logger.error(f"키워드 분류 오류: {e}")
            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.3,
                method=ClassificationMethod.KEYWORD,
                keywords_found=[],
                context_indicators=[],
                reasoning=f"키워드 분류 오류: {e}",
            )

    def _classify_by_context(
        self, content: str, context: Dict[str, Any]
    ) -> ClassificationResult:
        """컨텍스트 기반 분류"""
        try:
            context_indicators = []
            scores = {}

            # 컨텍스트 정보 분석
            if "emotion" in context:
                scores[MemoryType.EMOTION] = 5
                context_indicators.append("emotion")

            if "learning" in context:
                scores[MemoryType.KNOWLEDGE] = 5
                context_indicators.append("learning")

            if "experience" in context:
                scores[MemoryType.EXPERIENCE] = 5
                context_indicators.append("experience")

            if "pattern" in context:
                scores[MemoryType.PATTERN] = 5
                context_indicators.append("pattern")

            # 패턴 매칭
            for pattern_name, pattern in self.context_patterns.items():
                if re.search(pattern, content):
                    if pattern_name == "learning":
                        scores[MemoryType.KNOWLEDGE] = (
                            scores.get(MemoryType.KNOWLEDGE, 0) + 3
                        )
                    elif pattern_name == "experience":
                        scores[MemoryType.EXPERIENCE] = (
                            scores.get(MemoryType.EXPERIENCE, 0) + 3
                        )
                    elif pattern_name == "emotion":
                        scores[MemoryType.EMOTION] = (
                            scores.get(MemoryType.EMOTION, 0) + 3
                        )
                    elif pattern_name == "pattern":
                        scores[MemoryType.PATTERN] = (
                            scores.get(MemoryType.PATTERN, 0) + 3
                        )

                    context_indicators.append(pattern_name)

            # 최고 점수 선택
            if scores:
                best_type = max(scores, key=scores.get)
                max_score = scores[best_type]
                confidence = min(1.0, max_score / 8.0)

                return ClassificationResult(
                    memory_type=best_type,
                    confidence=confidence,
                    method=ClassificationMethod.CONTEXT,
                    keywords_found=[],
                    context_indicators=context_indicators,
                    reasoning=f"컨텍스트 기반 분류: {best_type.value} (점수: {max_score})",
                )

            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.3,
                method=ClassificationMethod.CONTEXT,
                keywords_found=[],
                context_indicators=[],
                reasoning="컨텍스트 정보 없음",
            )

        except Exception as e:
            logger.error(f"컨텍스트 분류 오류: {e}")
            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.3,
                method=ClassificationMethod.CONTEXT,
                keywords_found=[],
                context_indicators=[],
                reasoning=f"컨텍스트 분류 오류: {e}",
            )

    def _classify_by_semantics(
        self, content: str, context: Dict[str, Any]
    ) -> ClassificationResult:
        """의미 기반 분류"""
        try:
            # 감정 분석
            emotion_score = self._analyze_emotion(content)

            # 문장 구조 분석
            sentence_structure = self._analyze_sentence_structure(content)

            # 의미적 특징 분석
            semantic_features = self._analyze_semantic_features(content)

            # 종합 점수 계산
            scores = {}

            # 감정 점수
            if emotion_score > 0.5:
                scores[MemoryType.EMOTION] = emotion_score * 5

            # 문장 구조 점수
            if sentence_structure["is_experience"]:
                scores[MemoryType.EXPERIENCE] = scores.get(MemoryType.EXPERIENCE, 0) + 3

            if sentence_structure["is_knowledge"]:
                scores[MemoryType.KNOWLEDGE] = scores.get(MemoryType.KNOWLEDGE, 0) + 3

            if sentence_structure["is_pattern"]:
                scores[MemoryType.PATTERN] = scores.get(MemoryType.PATTERN, 0) + 3

            # 의미적 특징 점수
            for feature, value in semantic_features.items():
                if feature == "learning_related" and value > 0.5:
                    scores[MemoryType.KNOWLEDGE] = (
                        scores.get(MemoryType.KNOWLEDGE, 0) + 2
                    )
                elif feature == "experience_related" and value > 0.5:
                    scores[MemoryType.EXPERIENCE] = (
                        scores.get(MemoryType.EXPERIENCE, 0) + 2
                    )
                elif feature == "pattern_related" and value > 0.5:
                    scores[MemoryType.PATTERN] = scores.get(MemoryType.PATTERN, 0) + 2

            # 최고 점수 선택
            if scores:
                best_type = max(scores, key=scores.get)
                max_score = scores[best_type]
                confidence = min(1.0, max_score / 8.0)

                return ClassificationResult(
                    memory_type=best_type,
                    confidence=confidence,
                    method=ClassificationMethod.SEMANTIC,
                    keywords_found=[],
                    context_indicators=[],
                    reasoning=f"의미 기반 분류: {best_type.value} (점수: {max_score})",
                )

            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.3,
                method=ClassificationMethod.SEMANTIC,
                keywords_found=[],
                context_indicators=[],
                reasoning="의미적 특징 부족",
            )

        except Exception as e:
            logger.error(f"의미 분류 오류: {e}")
            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.3,
                method=ClassificationMethod.SEMANTIC,
                keywords_found=[],
                context_indicators=[],
                reasoning=f"의미 분류 오류: {e}",
            )

    def _hybrid_classification(
        self, results: List[ClassificationResult], content: str, context: Dict[str, Any]
    ) -> ClassificationResult:
        """하이브리드 분류 (최종 결정)"""
        try:
            # 신뢰도 가중 평균 계산
            weighted_scores = {}
            total_confidence = 0

            for result in results:
                if result.confidence > self.minimum_confidence:
                    if result.memory_type not in weighted_scores:
                        weighted_scores[result.memory_type] = 0

                    weighted_scores[result.memory_type] += result.confidence
                    total_confidence += result.confidence

            if weighted_scores and total_confidence > 0:
                # 최고 점수 선택
                best_type = max(weighted_scores, key=weighted_scores.get)
                final_confidence = weighted_scores[best_type] / total_confidence

                # 모든 키워드와 컨텍스트 인디케이터 수집
                all_keywords = []
                all_context_indicators = []
                all_reasoning = []

                for result in results:
                    if result.memory_type == best_type:
                        all_keywords.extend(result.keywords_found)
                        all_context_indicators.extend(result.context_indicators)
                        all_reasoning.append(result.reasoning)

                return ClassificationResult(
                    memory_type=best_type,
                    confidence=final_confidence,
                    method=ClassificationMethod.HYBRID,
                    keywords_found=list(set(all_keywords)),
                    context_indicators=list(set(all_context_indicators)),
                    reasoning=f"하이브리드 분류: {' + '.join(all_reasoning)}",
                )

            # 기본값 반환
            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.5,
                method=ClassificationMethod.HYBRID,
                keywords_found=[],
                context_indicators=[],
                reasoning="하이브리드 분류 실패로 인한 기본값",
            )

        except Exception as e:
            logger.error(f"하이브리드 분류 오류: {e}")
            return ClassificationResult(
                memory_type=MemoryType.EXPERIENCE,
                confidence=0.5,
                method=ClassificationMethod.HYBRID,
                keywords_found=[],
                context_indicators=[],
                reasoning=f"하이브리드 분류 오류: {e}",
            )

    def _analyze_emotion(self, content: str) -> float:
        """감정 분석"""
        try:
            positive_count = sum(
                1 for word in self.emotion_keywords["positive"] if word in content
            )
            negative_count = sum(
                1 for word in self.emotion_keywords["negative"] if word in content
            )
            neutral_count = sum(
                1 for word in self.emotion_keywords["neutral"] if word in content
            )

            total_emotion_words = positive_count + negative_count + neutral_count

            if total_emotion_words > 0:
                return total_emotion_words / len(content.split())

            return 0.0

        except Exception as e:
            logger.error(f"감정 분석 오류: {e}")
            return 0.0

    def _analyze_sentence_structure(self, content: str) -> Dict[str, bool]:
        """문장 구조 분석"""
        try:
            structure = {
                "is_experience": False,
                "is_knowledge": False,
                "is_pattern": False,
            }

            # 경험 문장 패턴
            experience_patterns = [
                r"했다$",
                r"했다$",
                r"갔다$",
                r"왔다$",
                r"만났다$",
                r"일어났다$",
                r"발생했다$",
                r"경험했다$",
            ]

            # 지식 문장 패턴
            knowledge_patterns = [
                r"알게되었다$",
                r"배웠다$",
                r"이해했다$",
                r"깨달았다$",
                r"학습했다$",
                r"알다$",
                r"이해하다$",
            ]

            # 패턴 문장 패턴
            pattern_patterns = [
                r"항상$",
                r"늘$",
                r"보통$",
                r"자주$",
                r"가끔$",
                r"패턴$",
                r"반복$",
                r"규칙$",
                r"습관$",
            ]

            # 패턴 매칭
            for pattern in experience_patterns:
                if re.search(pattern, content):
                    structure["is_experience"] = True
                    break

            for pattern in knowledge_patterns:
                if re.search(pattern, content):
                    structure["is_knowledge"] = True
                    break

            for pattern in pattern_patterns:
                if re.search(pattern, content):
                    structure["is_pattern"] = True
                    break

            return structure

        except Exception as e:
            logger.error(f"문장 구조 분석 오류: {e}")
            return {"is_experience": False, "is_knowledge": False, "is_pattern": False}

    def _analyze_semantic_features(self, content: str) -> Dict[str, float]:
        """의미적 특징 분석"""
        try:
            features = {
                "learning_related": 0.0,
                "experience_related": 0.0,
                "pattern_related": 0.0,
                "emotion_related": 0.0,
            }

            # 학습 관련 특징
            learning_words = ["학습", "공부", "배우", "이해", "알다", "깨달"]
            learning_count = sum(1 for word in learning_words if word in content)
            features["learning_related"] = min(1.0, learning_count / 3.0)

            # 경험 관련 특징
            experience_words = [
                "경험",
                "발생",
                "일어나",
                "하다",
                "만나",
                "가다",
                "오다",
            ]
            experience_count = sum(1 for word in experience_words if word in content)
            features["experience_related"] = min(1.0, experience_count / 3.0)

            # 패턴 관련 특징
            pattern_words = ["패턴", "반복", "규칙", "습관", "경향", "항상", "늘"]
            pattern_count = sum(1 for word in pattern_words if word in content)
            features["pattern_related"] = min(1.0, pattern_count / 3.0)

            # 감정 관련 특징
            emotion_words = (
                self.emotion_keywords["positive"]
                + self.emotion_keywords["negative"]
                + self.emotion_keywords["neutral"]
            )
            emotion_count = sum(1 for word in emotion_words if word in content)
            features["emotion_related"] = min(1.0, emotion_count / 5.0)

            return features

        except Exception as e:
            logger.error(f"의미적 특징 분석 오류: {e}")
            return {
                "learning_related": 0.0,
                "experience_related": 0.0,
                "pattern_related": 0.0,
                "emotion_related": 0.0,
            }


class MemoryTagger:
    """메모리 태깅 시스템"""

    def __init__(self):
        self.tag_categories = {
            "emotion": ["행복", "슬픔", "화남", "기쁨", "우울", "짜증", "신기", "재미"],
            "topic": ["학습", "경험", "패턴", "감정", "일상", "일", "여가"],
            "importance": ["중요", "보통", "덜중요", "매우중요"],
            "time": ["오늘", "어제", "지난주", "이번주", "최근", "과거"],
        }

        logger.info("메모리 태깅 시스템 초기화 완료")

    async def extract_tags(
        self,
        content: str,
        context: Dict[str, Any],
        classification_result: ClassificationResult,
    ) -> List[TagInfo]:
        """태그 추출"""
        try:
            tags = []

            # 1. 분류 결과 기반 태그
            tags.extend(self._extract_classification_tags(classification_result))

            # 2. 내용 기반 태그
            tags.extend(self._extract_content_tags(content))

            # 3. 컨텍스트 기반 태그
            tags.extend(self._extract_context_tags(context))

            # 4. 자동 생성 태그
            tags.extend(
                self._generate_auto_tags(content, context, classification_result)
            )

            # 중복 제거 및 정렬
            unique_tags = self._deduplicate_tags(tags)

            logger.info(f"태그 추출 완료: {len(unique_tags)}개")
            return unique_tags

        except Exception as e:
            logger.error(f"태그 추출 오류: {e}")
            return []

    def _extract_classification_tags(
        self, classification_result: ClassificationResult
    ) -> List[TagInfo]:
        """분류 결과 기반 태그 추출"""
        tags = []

        # 메모리 타입 태그
        tags.append(
            TagInfo(
                tag=classification_result.memory_type.value,
                confidence=classification_result.confidence,
                source="classification",
                category="type",
            )
        )

        # 키워드 태그
        for keyword in classification_result.keywords_found:
            tags.append(
                TagInfo(
                    tag=keyword,
                    confidence=0.8,
                    source="classification",
                    category="keyword",
                )
            )

        return tags

    def _extract_content_tags(self, content: str) -> List[TagInfo]:
        """내용 기반 태그 추출"""
        tags = []

        # 카테고리별 태그 검색
        for category, tag_list in self.tag_categories.items():
            for tag in tag_list:
                if tag in content:
                    tags.append(
                        TagInfo(
                            tag=tag, confidence=0.7, source="content", category=category
                        )
                    )

        # 시간 관련 태그
        time_patterns = {
            "오늘": r"오늘",
            "어제": r"어제",
            "지난주": r"지난주",
            "이번주": r"이번주",
            "최근": r"최근",
        }

        for time_tag, pattern in time_patterns.items():
            if re.search(pattern, content):
                tags.append(
                    TagInfo(
                        tag=time_tag, confidence=0.9, source="content", category="time"
                    )
                )

        return tags

    def _extract_context_tags(self, context: Dict[str, Any]) -> List[TagInfo]:
        """컨텍스트 기반 태그 추출"""
        tags = []

        for key, value in context.items():
            if isinstance(value, str):
                tags.append(
                    TagInfo(
                        tag=f"{key}:{value}",
                        confidence=0.8,
                        source="context",
                        category="context",
                    )
                )
            elif isinstance(value, (int, float)):
                tags.append(
                    TagInfo(
                        tag=f"{key}:{value}",
                        confidence=0.8,
                        source="context",
                        category="context",
                    )
                )

        return tags

    def _generate_auto_tags(
        self,
        content: str,
        context: Dict[str, Any],
        classification_result: ClassificationResult,
    ) -> List[TagInfo]:
        """자동 태그 생성"""
        tags = []

        # 길이 기반 태그
        content_length = len(content)
        if content_length > 100:
            tags.append(
                TagInfo(tag="긴내용", confidence=0.6, source="auto", category="length")
            )
        elif content_length < 20:
            tags.append(
                TagInfo(
                    tag="짧은내용", confidence=0.6, source="auto", category="length"
                )
            )

        # 신뢰도 기반 태그
        if classification_result.confidence > 0.8:
            tags.append(
                TagInfo(
                    tag="높은신뢰도",
                    confidence=0.9,
                    source="auto",
                    category="confidence",
                )
            )
        elif classification_result.confidence < 0.5:
            tags.append(
                TagInfo(
                    tag="낮은신뢰도",
                    confidence=0.9,
                    source="auto",
                    category="confidence",
                )
            )

        # 방법 기반 태그
        tags.append(
            TagInfo(
                tag=f"분류방법:{classification_result.method.value}",
                confidence=0.9,
                source="auto",
                category="method",
            )
        )

        return tags

    def _deduplicate_tags(self, tags: List[TagInfo]) -> List[TagInfo]:
        """태그 중복 제거"""
        seen_tags = set()
        unique_tags = []

        for tag in tags:
            tag_key = f"{tag.tag}:{tag.category}"
            if tag_key not in seen_tags:
                seen_tags.add(tag_key)
                unique_tags.append(tag)

        # 신뢰도 순으로 정렬
        unique_tags.sort(key=lambda x: x.confidence, reverse=True)

        return unique_tags


# 테스트 함수
async def test_memory_classification():
    """기억 분류 시스템 테스트"""
    print("=== DuRiCore Phase 5 Day 2 - 기억 분류 시스템 테스트 ===")

    # 분류기 초기화
    classifier = MemoryClassifier()
    tagger = MemoryTagger()

    # 테스트 데이터
    test_cases = [
        {
            "content": "오늘 새로운 머신러닝 알고리즘을 학습했다. 매우 흥미로웠다.",
            "context": {"type": "learning", "emotion": "excited", "importance": "high"},
        },
        {
            "content": "친구와 함께 영화를 봤다. 정말 재미있었다.",
            "context": {
                "type": "experience",
                "emotion": "happy",
                "importance": "medium",
            },
        },
        {
            "content": "코딩할 때 항상 같은 패턴을 사용하는 것을 발견했다.",
            "context": {
                "type": "pattern",
                "emotion": "neutral",
                "importance": "medium",
            },
        },
        {
            "content": "시험 결과가 나왔는데 실망스럽다.",
            "context": {
                "type": "emotion",
                "emotion": "disappointed",
                "importance": "high",
            },
        },
    ]

    # 분류 테스트
    print("\n1. 메모리 분류 테스트")
    for i, test_case in enumerate(test_cases):
        result = await classifier.classify_memory(
            test_case["content"], test_case["context"]
        )
        print(
            f"테스트 {i+1}: {result.memory_type.value} (신뢰도: {result.confidence:.3f})"
        )
        print(f"  내용: {test_case['content'][:50]}...")
        print(f"  방법: {result.method.value}")
        print(f"  키워드: {result.keywords_found}")
        print(f"  추론: {result.reasoning}")
        print()

    # 태깅 테스트
    print("\n2. 메모리 태깅 테스트")
    for i, test_case in enumerate(test_cases):
        classification_result = await classifier.classify_memory(
            test_case["content"], test_case["context"]
        )
        tags = await tagger.extract_tags(
            test_case["content"], test_case["context"], classification_result
        )

        print(f"테스트 {i+1} 태그:")
        for tag in tags[:5]:  # 상위 5개만 출력
            print(f"  - {tag.tag} ({tag.category}, 신뢰도: {tag.confidence:.3f})")
        print()

    print("=== 테스트 완료 ===")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_memory_classification())
