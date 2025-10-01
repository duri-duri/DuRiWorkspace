#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 12 - 통합 언어 이해 및 생성 시스템

기존 언어 관련 시스템들을 통합하고 새로운 기능을 추가하여 완전한 언어 이해 및 생성 시스템 구현
- 심층 언어 이해: 맥락 기반 대화 및 감정적 언어 표현
- 자연어 처리 고도화: 고급 자연어 처리 능력
- 감정적 언어 표현: 감정을 담은 자연스러운 언어 생성
- 다국어 처리 능력: 다양한 언어 처리 및 생성
"""

import asyncio
import hashlib
import json
import logging
import re
import time
import unicodedata
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from integrated_social_intelligence_system import IntegratedSocialIntelligenceSystem

# 기존 시스템들 import
from natural_language_processing_system import NaturalLanguageProcessingSystem

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LanguageUnderstandingType(Enum):
    """언어 이해 유형"""

    CONVERSATION_ANALYSIS = "conversation_analysis"  # 대화 분석
    INTENT_RECOGNITION = "intent_recognition"  # 의도 인식
    CONTEXT_UNDERSTANDING = "context_understanding"  # 맥락 이해
    SEMANTIC_ANALYSIS = "semantic_analysis"  # 의미 분석
    EMOTION_DETECTION = "emotion_detection"  # 감정 감지
    MULTILINGUAL_PROCESSING = "multilingual_processing"  # 다국어 처리


class LanguageGenerationType(Enum):
    """언어 생성 유형"""

    CONVERSATIONAL_RESPONSE = "conversational_response"  # 대화 응답
    EMOTIONAL_EXPRESSION = "emotional_expression"  # 감정적 표현
    CONTEXTUAL_GENERATION = "contextual_generation"  # 맥락 기반 생성
    MULTILINGUAL_GENERATION = "multilingual_generation"  # 다국어 생성
    CREATIVE_WRITING = "creative_writing"  # 창의적 글쓰기


@dataclass
class LanguageUnderstandingResult:
    """언어 이해 결과 데이터 구조"""

    understanding_id: str
    source_text: str
    understanding_type: LanguageUnderstandingType
    intent: str
    key_concepts: List[str]
    emotional_tone: str
    context_meaning: str
    learning_insights: List[str]
    confidence_score: float
    multilingual_analysis: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LanguageGenerationResult:
    """언어 생성 결과 데이터 구조"""

    generation_id: str
    source_context: Dict[str, Any]
    generation_type: LanguageGenerationType
    generated_text: str
    emotional_expression: str
    contextual_relevance: float
    confidence_score: float
    multilingual_support: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntegratedLanguageResult:
    """통합 언어 처리 결과 데이터 구조"""

    result_id: str
    understanding_result: LanguageUnderstandingResult
    generation_result: LanguageGenerationResult
    integration_score: float
    system_performance: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


class DeepLanguageUnderstandingEngine:
    """심층 언어 이해 엔진"""

    def __init__(self):
        self.understanding_cache = {}
        self.context_analyzer = ContextAnalyzer()
        self.emotion_analyzer = EmotionAnalyzer()
        self.intent_recognizer = IntentRecognizer()
        self.semantic_analyzer = SemanticAnalyzer()
        self.multilingual_processor = MultilingualProcessor()

    async def understand_language(
        self, text: str, context: Dict[str, Any] = None
    ) -> LanguageUnderstandingResult:
        """심층 언어 이해"""
        understanding_id = f"understanding_{int(time.time())}"

        # 캐시 확인
        cache_key = hashlib.md5(
            f"{text}_{json.dumps(context, sort_keys=True)}".encode()
        ).hexdigest()
        if cache_key in self.understanding_cache:
            return self.understanding_cache[cache_key]

        # 1. 맥락 분석
        context_analysis = await self.context_analyzer.analyze_context(text, context)

        # 2. 감정 분석
        emotion_analysis = await self.emotion_analyzer.analyze_emotion(text, context)

        # 3. 의도 인식
        intent_analysis = await self.intent_recognizer.recognize_intent(text, context)

        # 4. 의미 분석
        semantic_analysis = await self.semantic_analyzer.analyze_semantics(
            text, context
        )

        # 5. 다국어 처리
        multilingual_analysis = await self.multilingual_processor.process_multilingual(
            text, context
        )

        # 6. 통합 분석
        understanding_result = LanguageUnderstandingResult(
            understanding_id=understanding_id,
            source_text=text,
            understanding_type=LanguageUnderstandingType.CONVERSATION_ANALYSIS,
            intent=intent_analysis.get("primary_intent", ""),
            key_concepts=semantic_analysis.get("key_concepts", []),
            emotional_tone=emotion_analysis.get("primary_emotion", ""),
            context_meaning=context_analysis.get("context_meaning", ""),
            learning_insights=semantic_analysis.get("learning_insights", []),
            confidence_score=self._calculate_understanding_confidence(
                context_analysis, emotion_analysis, intent_analysis, semantic_analysis
            ),
            multilingual_analysis=multilingual_analysis,
        )

        # 캐시 저장
        self.understanding_cache[cache_key] = understanding_result

        return understanding_result

    def _calculate_understanding_confidence(
        self,
        context_analysis: Dict,
        emotion_analysis: Dict,
        intent_analysis: Dict,
        semantic_analysis: Dict,
    ) -> float:
        """이해 신뢰도 계산"""
        scores = [
            context_analysis.get("confidence", 0.0),
            emotion_analysis.get("confidence", 0.0),
            intent_analysis.get("confidence", 0.0),
            semantic_analysis.get("confidence", 0.0),
        ]
        return np.mean(scores)


class AdvancedLanguageGenerationEngine:
    """고급 언어 생성 엔진"""

    def __init__(self):
        self.generation_cache = {}
        self.conversational_generator = ConversationalGenerator()
        self.emotional_generator = EmotionalGenerator()
        self.contextual_generator = ContextualGenerator()
        self.multilingual_generator = MultilingualGenerator()
        self.creative_generator = CreativeGenerator()

    async def generate_language(
        self, context: Dict[str, Any], generation_type: LanguageGenerationType
    ) -> LanguageGenerationResult:
        """고급 언어 생성 (의미 분석 결과 반영 강화)"""
        generation_id = f"generation_{int(time.time())}"

        # 캐시 확인
        cache_key = hashlib.md5(
            f"{json.dumps(context, sort_keys=True)}_{generation_type.value}".encode()
        ).hexdigest()
        if cache_key in self.generation_cache:
            return self.generation_cache[cache_key]

        # 의미 분석 결과 추출 (새로 추가)
        semantic_analysis = context.get("semantic_analysis", {})
        learning_insights = context.get("learning_insights", [])
        key_concepts = context.get("keywords", [])
        confidence_score = context.get("confidence_score", 0.5)

        # 의미 분석 결과를 컨텍스트에 반영
        enhanced_context = context.copy()
        if semantic_analysis:
            enhanced_context.update(semantic_analysis)
        if learning_insights:
            enhanced_context["learning_insights"] = learning_insights
        if key_concepts:
            enhanced_context["key_concepts"] = key_concepts
        enhanced_context["semantic_confidence"] = confidence_score

        # 생성 유형에 따른 처리
        if generation_type == LanguageGenerationType.CONVERSATIONAL_RESPONSE:
            generated_text = await self.conversational_generator.generate_response(
                enhanced_context
            )
        elif generation_type == LanguageGenerationType.EMOTIONAL_EXPRESSION:
            generated_text = (
                await self.emotional_generator.generate_emotional_expression(
                    enhanced_context
                )
            )
        elif generation_type == LanguageGenerationType.CONTEXTUAL_GENERATION:
            generated_text = await self.contextual_generator.generate_contextual_text(
                enhanced_context
            )
        elif generation_type == LanguageGenerationType.MULTILINGUAL_GENERATION:
            generated_text = (
                await self.multilingual_generator.generate_multilingual_text(
                    enhanced_context
                )
            )
        elif generation_type == LanguageGenerationType.CREATIVE_WRITING:
            generated_text = await self.creative_generator.generate_creative_text(
                enhanced_context
            )
        else:
            generated_text = await self.conversational_generator.generate_response(
                enhanced_context
            )

        # 감정적 표현 분석
        emotional_expression = (
            await self.emotional_generator.analyze_emotional_expression(generated_text)
        )

        # 맥락 관련성 평가 (의미 분석 결과 반영)
        contextual_relevance = (
            await self.contextual_generator.evaluate_contextual_relevance(
                generated_text, enhanced_context
            )
        )

        # 다국어 지원
        multilingual_support = (
            await self.multilingual_generator.get_multilingual_support(
                generated_text, enhanced_context
            )
        )

        # 신뢰도 계산 (의미 분석 결과 반영)
        confidence_score = self._calculate_generation_confidence(
            generated_text, emotional_expression, contextual_relevance, enhanced_context
        )

        generation_result = LanguageGenerationResult(
            generation_id=generation_id,
            source_context=enhanced_context,
            generation_type=generation_type,
            generated_text=generated_text,
            emotional_expression=emotional_expression,
            contextual_relevance=contextual_relevance,
            multilingual_support=multilingual_support,
            confidence_score=confidence_score,
        )

        # 캐시 저장
        self.generation_cache[cache_key] = generation_result

        return generation_result

    def _calculate_generation_confidence(
        self,
        generated_text: str,
        emotional_expression: str,
        contextual_relevance: float,
        context: Dict[str, Any] = None,
    ) -> float:
        """생성 신뢰도 계산 (의미 분석 결과 반영)"""
        try:
            # 텍스트 품질 평가
            text_quality = min(
                1.0, len(generated_text.strip()) / 100.0
            )  # 기본 품질 점수

            # 감정적 표현 평가
            emotion_quality = 1.0 if emotional_expression else 0.5

            # 맥락 관련성 평가
            context_quality = max(0.0, min(1.0, contextual_relevance))

            # 의미 분석 결과 반영 (새로 추가)
            semantic_quality = 0.5  # 기본값
            if context:
                # 키 컨셉 반영
                key_concepts = context.get("key_concepts", [])
                if key_concepts:
                    semantic_quality = min(
                        1.0, semantic_quality + len(key_concepts) * 0.1
                    )

                # 학습 통찰 반영
                learning_insights = context.get("learning_insights", [])
                if learning_insights:
                    semantic_quality = min(
                        1.0, semantic_quality + len(learning_insights) * 0.1
                    )

                # 의미 분석 신뢰도 반영
                semantic_confidence = context.get("semantic_confidence", 0.5)
                semantic_quality = min(
                    1.0, semantic_quality + semantic_confidence * 0.2
                )

            # 통합 신뢰도 (의미 분석 가중치 추가)
            confidence = (
                text_quality * 0.3  # 텍스트 품질 (30%)
                + emotion_quality * 0.2  # 감정적 표현 (20%)
                + context_quality * 0.3  # 맥락 관련성 (30%)
                + semantic_quality * 0.2  # 의미 분석 (20%)
            )

            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.error(f"생성 신뢰도 계산 실패: {e}")
            return 0.5  # 기본값 반환


class ContextAnalyzer:
    """맥락 분석기"""

    async def analyze_context(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """맥락 분석"""
        # 시간적 맥락
        temporal_context = self._extract_temporal_context(text)

        # 공간적 맥락
        spatial_context = self._extract_spatial_context(text)

        # 사회적 맥락
        social_context = self._extract_social_context(text)

        # 주제적 맥락
        topical_context = self._extract_topical_context(text)

        # 감정적 맥락
        emotional_context = self._extract_emotional_context(text)

        # 통합 맥락 의미
        context_meaning = self._integrate_context_meaning(
            temporal_context,
            spatial_context,
            social_context,
            topical_context,
            emotional_context,
        )

        return {
            "temporal_context": temporal_context,
            "spatial_context": spatial_context,
            "social_context": social_context,
            "topical_context": topical_context,
            "emotional_context": emotional_context,
            "context_meaning": context_meaning,
            "confidence": 0.85,
        }

    def _extract_temporal_context(self, text: str) -> Dict[str, Any]:
        """시간적 맥락 추출"""
        # 시간 관련 키워드 패턴
        time_patterns = [
            r"오늘|어제|내일|이번|다음|지난|이전",
            r"년|월|일|시|분|초",
            r"아침|점심|저녁|밤|새벽",
        ]

        temporal_keywords = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            temporal_keywords.extend(matches)

        return {
            "temporal_keywords": temporal_keywords,
            "temporal_relevance": len(temporal_keywords) / len(text.split()),
        }

    def _extract_spatial_context(self, text: str) -> Dict[str, Any]:
        """공간적 맥락 추출"""
        # 공간 관련 키워드 패턴
        spatial_patterns = [
            r"집|학교|회사|병원|상점|공원|역|공항",
            r"위|아래|앞|뒤|왼쪽|오른쪽|안|밖",
            r"서울|부산|대구|인천|광주|대전|울산",
        ]

        spatial_keywords = []
        for pattern in spatial_patterns:
            matches = re.findall(pattern, text)
            spatial_keywords.extend(matches)

        return {
            "spatial_keywords": spatial_keywords,
            "spatial_relevance": len(spatial_keywords) / len(text.split()),
        }

    def _extract_social_context(self, text: str) -> Dict[str, Any]:
        """사회적 맥락 추출"""
        # 사회적 관계 키워드
        social_keywords = re.findall(
            r"가족|친구|동료|선생님|학생|부모|자식|형제|자매", text
        )

        return {
            "social_keywords": social_keywords,
            "social_relevance": len(social_keywords) / len(text.split()),
        }

    def _extract_topical_context(self, text: str) -> Dict[str, Any]:
        """주제적 맥락 추출"""
        # 주제 관련 키워드
        topic_keywords = re.findall(
            r"학습|교육|일|취미|운동|음식|여행|영화|음악|책", text
        )

        return {
            "topic_keywords": topic_keywords,
            "topic_relevance": len(topic_keywords) / len(text.split()),
        }

    def _extract_emotional_context(self, text: str) -> Dict[str, Any]:
        """감정적 맥락 추출"""
        # 감정 관련 키워드
        emotion_keywords = re.findall(
            r"기쁨|슬픔|화남|놀람|두려움|사랑|미움|희망|절망|감사", text
        )

        return {
            "emotion_keywords": emotion_keywords,
            "emotion_relevance": len(emotion_keywords) / len(text.split()),
        }

    def _integrate_context_meaning(
        self,
        temporal_context: Dict,
        spatial_context: Dict,
        social_context: Dict,
        topical_context: Dict,
        emotional_context: Dict,
    ) -> str:
        """맥락 의미 통합"""
        context_elements = []

        if temporal_context["temporal_relevance"] > 0.1:
            context_elements.append("시간적 맥락이 중요한 대화")

        if spatial_context["spatial_relevance"] > 0.1:
            context_elements.append("공간적 맥락이 중요한 대화")

        if social_context["social_relevance"] > 0.1:
            context_elements.append("사회적 관계가 중요한 대화")

        if topical_context["topic_relevance"] > 0.1:
            context_elements.append("특정 주제에 관한 대화")

        if emotional_context["emotion_relevance"] > 0.1:
            context_elements.append("감정적 표현이 중요한 대화")

        if not context_elements:
            return "일반적인 대화"

        return " + ".join(context_elements)


class EmotionAnalyzer:
    """감정 분석기"""

    def __init__(self):
        self.emotion_keywords = {
            "기쁨": ["기쁘다", "행복하다", "즐겁다", "신나다", "좋다", "만족하다"],
            "슬픔": ["슬프다", "우울하다", "속상하다", "아프다", "힘들다", "지치다"],
            "화남": ["화나다", "짜증나다", "분하다", "열받다", "화가나다", "답답하다"],
            "놀람": ["놀랍다", "깜짝", "어이없다", "헐", "와", "대박"],
            "두려움": ["무섭다", "겁나다", "불안하다", "걱정되다", "무서워하다"],
            "사랑": ["사랑하다", "좋아하다", "그립다", "보고싶다", "아끼다"],
            "미움": ["싫다", "미워하다", "짜증나다", "답답하다", "화나다"],
            "희망": ["희망적이다", "기대하다", "꿈꾸다", "바라다", "원하다"],
            "절망": ["절망적이다", "포기하다", "실망하다", "허탈하다"],
            "감사": ["감사하다", "고맙다", "은혜롭다", "축복받다"],
        }

    async def analyze_emotion(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """감정 분석"""
        emotion_scores = {}

        # 각 감정별 점수 계산
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            emotion_scores[emotion] = score

        # 주요 감정 결정
        primary_emotion = (
            max(emotion_scores.items(), key=lambda x: x[1])[0]
            if emotion_scores
            else "중립"
        )

        # 감정 강도 계산
        total_emotion_words = sum(emotion_scores.values())
        emotion_intensity = min(total_emotion_words / len(text.split()), 1.0)

        return {
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_scores,
            "emotion_intensity": emotion_intensity,
            "confidence": 0.8 if emotion_scores else 0.5,
        }


class IntentRecognizer:
    """의도 인식기"""

    def __init__(self):
        self.intent_patterns = {
            "질문": [r"\?$", r"무엇|어떤|어디|언제|누가|왜|어떻게"],
            "요청": [r"해주세요", r"부탁", r"도와", r"좀", r"해달라"],
            "명령": [r"해라", r"하라", r"해야", r"필요", r"해야지"],
            "감정표현": [r"기쁘다", r"슬프다", r"화나다", r"좋다", r"싫다"],
            "정보제공": [r"~입니다", r"~이에요", r"~야", r"~다"],
            "동의": [r"맞다", r"그렇다", r"옳다", r"좋다", r"네"],
            "반대": [r"아니다", r"틀렸다", r"싫다", r"안된다", r"아니요"],
        }

    async def recognize_intent(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """의도 인식"""
        intent_scores = {}

        # 각 의도별 점수 계산
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text)
                score += len(matches)
            intent_scores[intent] = score

        # 주요 의도 결정
        primary_intent = (
            max(intent_scores.items(), key=lambda x: x[1])[0]
            if intent_scores
            else "일반"
        )

        return {
            "primary_intent": primary_intent,
            "intent_scores": intent_scores,
            "confidence": 0.8 if intent_scores else 0.5,
        }


class SemanticAnalyzer:
    """의미 분석기"""

    async def analyze_semantics(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """의미 분석"""
        # 키워드 추출
        keywords = self._extract_keywords(text)

        # 핵심 개념 추출
        key_concepts = self._extract_key_concepts(text)

        # 학습 통찰 추출
        learning_insights = self._extract_learning_insights(text, context)

        return {
            "keywords": keywords,
            "key_concepts": key_concepts,
            "learning_insights": learning_insights,
            "confidence": 0.85,
        }

    def _extract_keywords(self, text: str) -> List[str]:
        """키워드 추출"""
        # 기본 키워드 추출 (실제로는 더 정교한 NLP 기법 사용)
        words = text.split()
        word_freq = Counter(words)
        keywords = [word for word, freq in word_freq.most_common(5) if len(word) > 1]
        return keywords

    def _extract_key_concepts(self, text: str) -> List[str]:
        """핵심 개념 추출"""
        # 핵심 개념 패턴
        concept_patterns = [
            r"학습|교육|지식|기술|능력|경험",
            r"가족|친구|관계|소통|이해|사랑",
            r"목표|계획|실행|결과|성공|실패",
            r"문제|해결|도전|어려움|극복|성장",
        ]

        concepts = []
        for pattern in concept_patterns:
            matches = re.findall(pattern, text)
            concepts.extend(matches)

        return list(set(concepts))

    def _extract_learning_insights(
        self, text: str, context: Dict[str, Any] = None
    ) -> List[str]:
        """학습 통찰 추출"""
        insights = []

        # 학습 관련 패턴
        learning_patterns = [
            r"배우다|학습하다|익히다|훈련하다",
            r"경험하다|체험하다|실습하다",
            r"이해하다|깨닫다|알다|알게되다",
        ]

        for pattern in learning_patterns:
            if re.search(pattern, text):
                insights.append("학습 경험 관련")
                break

        # 성장 관련 패턴
        growth_patterns = [
            r"성장하다|발전하다|향상되다|개선되다",
            r"변화하다|달라지다|바뀌다",
        ]

        for pattern in growth_patterns:
            if re.search(pattern, text):
                insights.append("성장 및 발전 관련")
                break

        return insights


class MultilingualProcessor:
    """다국어 처리기"""

    def __init__(self):
        self.supported_languages = ["ko", "en", "ja", "zh", "es", "fr", "de"]
        self.language_detectors = {
            "ko": self._detect_korean,
            "en": self._detect_english,
            "ja": self._detect_japanese,
            "zh": self._detect_chinese,
        }

    async def process_multilingual(
        self, text: str, context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """다국어 처리"""
        # 언어 감지
        detected_language = self._detect_language(text)

        # 언어별 처리
        language_specific_analysis = await self._process_language_specific(
            text, detected_language
        )

        return {
            "detected_language": detected_language,
            "language_specific_analysis": language_specific_analysis,
            "multilingual_support": True,
        }

    def _detect_language(self, text: str) -> str:
        """언어 감지"""
        for lang_code, detector in self.language_detectors.items():
            if detector(text):
                return lang_code
        return "ko"  # 기본값

    def _detect_korean(self, text: str) -> bool:
        """한국어 감지"""
        korean_pattern = re.compile(r"[가-힣]")
        return bool(korean_pattern.search(text))

    def _detect_english(self, text: str) -> bool:
        """영어 감지"""
        english_pattern = re.compile(r"[a-zA-Z]")
        return bool(english_pattern.search(text))

    def _detect_japanese(self, text: str) -> bool:
        """일본어 감지"""
        japanese_pattern = re.compile(r"[あ-んア-ン]")
        return bool(japanese_pattern.search(text))

    def _detect_chinese(self, text: str) -> bool:
        """중국어 감지"""
        chinese_pattern = re.compile(r"[\u4e00-\u9fff]")
        return bool(chinese_pattern.search(text))

    async def _process_language_specific(
        self, text: str, language: str
    ) -> Dict[str, Any]:
        """언어별 특화 처리"""
        if language == "ko":
            return self._process_korean(text)
        elif language == "en":
            return self._process_english(text)
        else:
            return {"language": language, "processed": True}

    def _process_korean(self, text: str) -> Dict[str, Any]:
        """한국어 특화 처리"""
        return {
            "language": "ko",
            "processed": True,
            "features": ["한글 처리", "조사 분석", "어미 분석"],
        }

    def _process_english(self, text: str) -> Dict[str, Any]:
        """영어 특화 처리"""
        return {
            "language": "en",
            "processed": True,
            "features": ["영어 처리", "시제 분석", "품사 분석"],
        }


class ConversationalGenerator:
    """대화 생성기"""

    async def generate_response(self, context: Dict[str, Any]) -> str:
        """대화 응답 생성"""
        # 맥락 분석
        intent = context.get("intent", "일반")
        emotion = context.get("emotion", "중립")
        topic = context.get("topic", "일반")

        # 의도별 응답 생성
        if intent == "질문":
            return self._generate_question_response(context)
        elif intent == "요청":
            return self._generate_request_response(context)
        elif intent == "감정표현":
            return self._generate_emotional_response(context)
        else:
            return self._generate_general_response(context)

    def _generate_question_response(self, context: Dict[str, Any]) -> str:
        """질문 응답 생성"""
        topic = context.get("topic", "일반")
        return f"{topic}에 대한 답변을 드리겠습니다. 구체적으로 말씀해 주시면 더 정확한 답변을 드릴 수 있습니다."

    def _generate_request_response(self, context: Dict[str, Any]) -> str:
        """요청 응답 생성"""
        return "네, 도와드리겠습니다. 어떤 도움이 필요하신지 구체적으로 말씀해 주세요."

    def _generate_emotional_response(self, context: Dict[str, Any]) -> str:
        """감정 표현 응답 생성"""
        emotion = context.get("emotion", "중립")
        if emotion == "기쁨":
            return "정말 기쁘시겠네요! 함께 기뻐해 드리고 싶습니다."
        elif emotion == "슬픔":
            return "마음이 아프시겠어요. 제가 옆에서 함께 있어드릴게요."
        elif emotion == "화남":
            return "화가 나시는 것 같아요. 차분히 이야기해 보세요."
        else:
            return "그런 감정을 느끼고 계시는군요. 더 자세히 이야기해 주세요."

    def _generate_general_response(self, context: Dict[str, Any]) -> str:
        """일반 응답 생성"""
        return (
            "이해했습니다. 더 구체적으로 말씀해 주시면 더 나은 도움을 드릴 수 있습니다."
        )


class EmotionalGenerator:
    """감정적 표현 생성기"""

    async def generate_emotional_expression(self, context: Dict[str, Any]) -> str:
        """감정적 표현 생성"""
        emotion = context.get("emotion", "중립")
        intensity = context.get("emotion_intensity", 0.5)

        if emotion == "기쁨":
            if intensity > 0.7:
                return "정말 정말 기뻐요! 마음이 가벼워지는 것 같아요!"
            else:
                return "기쁘네요. 좋은 일이 있으신가요?"
        elif emotion == "슬픔":
            if intensity > 0.7:
                return "정말 마음이 아프시겠어요. 제가 함께 있어드릴게요."
            else:
                return "슬픈 일이 있으신가요? 이야기해 주세요."
        elif emotion == "화남":
            if intensity > 0.7:
                return "정말 화가 나시는 것 같아요. 차분히 생각해 보세요."
            else:
                return "화가 나시는군요. 어떤 일이 있으셨나요?"
        else:
            return "감정을 표현해 주셔서 감사합니다."

    async def analyze_emotional_expression(self, text: str) -> str:
        """감정적 표현 분석"""
        emotion_keywords = {
            "기쁨": ["기뻐요", "좋아요", "행복해요", "즐거워요"],
            "슬픔": ["아프시겠어요", "슬프시겠어요", "힘드시겠어요"],
            "화남": ["화가 나시는", "짜증나시는", "답답하시는"],
            "사랑": ["사랑", "좋아", "그립", "보고싶"],
        }

        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return emotion

        return "중립"


class ContextualGenerator:
    """맥락 기반 생성기"""

    async def generate_contextual_text(self, context: Dict[str, Any]) -> str:
        """맥락 기반 텍스트 생성"""
        context_type = context.get("context_type", "일반")

        if context_type == "학습":
            return "학습에 대한 이야기를 나누고 계시는군요. 어떤 부분에서 도움이 필요하신가요?"
        elif context_type == "가족":
            return "가족에 대한 이야기네요. 가족 관계는 정말 중요한 부분이에요."
        elif context_type == "일":
            return "일에 대한 이야기를 하고 계시는군요. 어떤 어려움이 있으신가요?"
        else:
            return "맥락을 고려한 응답을 드리고 싶습니다. 더 구체적으로 말씀해 주세요."

    async def evaluate_contextual_relevance(
        self, text: str, context: Dict[str, Any]
    ) -> float:
        """맥락 관련성 평가"""
        # 간단한 관련성 평가 (실제로는 더 정교한 방법 사용)
        context_keywords = context.get("keywords", [])
        text_words = text.split()

        if not context_keywords:
            return 0.5

        relevant_words = sum(1 for word in text_words if word in context_keywords)
        relevance = relevant_words / len(text_words) if text_words else 0.0

        return min(relevance, 1.0)


class MultilingualGenerator:
    """다국어 생성기"""

    async def generate_multilingual_text(self, context: Dict[str, Any]) -> str:
        """다국어 텍스트 생성"""
        target_language = context.get("target_language", "ko")

        if target_language == "en":
            return "I understand. Please tell me more specifically so I can help you better."
        elif target_language == "ja":
            return "理解しました。より具体的にお聞かせください。"
        elif target_language == "zh":
            return "我明白了。请更具体地告诉我，这样我就能更好地帮助您。"
        else:
            return "이해했습니다. 더 구체적으로 말씀해 주시면 더 나은 도움을 드릴 수 있습니다."

    async def get_multilingual_support(
        self, text: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """다국어 지원 정보"""
        return {
            "supported_languages": ["ko", "en", "ja", "zh"],
            "current_language": "ko",
            "translation_available": True,
        }


class CreativeGenerator:
    """창의적 생성기"""

    async def generate_creative_text(self, context: Dict[str, Any]) -> str:
        """창의적 텍스트 생성"""
        topic = context.get("topic", "일반")

        creative_responses = {
            "학습": "학습은 마치 정원을 가꾸는 것과 같아요. 꾸준한 관심과 사랑으로 아름다운 꽃을 피울 수 있답니다.",
            "가족": "가족은 마치 나무의 뿌리와 같아요. 깊고 튼튼한 뿌리가 있어야 푸른 잎과 아름다운 꽃이 피어날 수 있어요.",
            "성장": "성장은 마치 나비가 되는 과정과 같아요. 때로는 어려움을 겪지만, 그 과정을 통해 더 아름다워질 수 있어요.",
            "일반": "모든 경험은 우리를 성장시키는 소중한 선물이에요. 어떤 어려움이 있더라도 함께 극복해 나갈 수 있을 거예요.",
        }

        return creative_responses.get(topic, creative_responses["일반"])


class IntegratedLanguageUnderstandingGenerationSystem:
    """통합 언어 이해 및 생성 시스템"""

    def __init__(self):
        self.system_name = "통합 언어 이해 및 생성 시스템"
        self.version = "1.0.0"
        self.deep_understanding_engine = DeepLanguageUnderstandingEngine()
        self.advanced_generation_engine = AdvancedLanguageGenerationEngine()
        self.nlp_system = NaturalLanguageProcessingSystem()
        self.social_intelligence_system = IntegratedSocialIntelligenceSystem()

        # 성능 메트릭
        self.performance_metrics = defaultdict(float)
        self.system_status = "active"

        logger.info(f"🚀 {self.system_name} v{self.version} 초기화 완료")

    async def process_language(
        self,
        text: str,
        context: Dict[str, Any] = None,
        generation_type: LanguageGenerationType = LanguageGenerationType.CONVERSATIONAL_RESPONSE,
    ) -> IntegratedLanguageResult:
        """통합 언어 처리"""
        start_time = time.time()

        try:
            logger.info("=== 통합 언어 이해 및 생성 시스템 시작 ===")

            # 1. 빈 입력 처리 시 division by zero 예외 방지 로직 추가
            if not text or not text.strip():
                logger.warning("빈 텍스트 입력 감지, 기본값으로 처리")
                text = "일반적인 대화"

            # 2. 심층 언어 이해
            understanding_result = (
                await self.deep_understanding_engine.understand_language(text, context)
            )

            # 3. 고급 언어 생성 (의미 분석 결과가 언어 생성 가중치에 제대로 반영되도록 연결 보강)
            generation_context = {
                "intent": understanding_result.intent,
                "emotion": understanding_result.emotional_tone,
                "topic": (
                    understanding_result.key_concepts[0]
                    if understanding_result.key_concepts
                    else "일반"
                ),
                "context_type": understanding_result.context_meaning,
                "keywords": understanding_result.key_concepts,
                "learning_insights": understanding_result.learning_insights,  # 의미 분석 결과 추가
                "confidence_score": understanding_result.confidence_score,  # 이해 신뢰도 추가
                "semantic_analysis": {
                    "key_concepts": understanding_result.key_concepts,
                    "learning_insights": understanding_result.learning_insights,
                },
            }

            generation_result = await self.advanced_generation_engine.generate_language(
                generation_context, generation_type
            )

            # 4. 통합 분석 (integration_score 계산식 재조정 및 0.0~1.0 정규화 적용)
            integration_score = self._calculate_integration_score(
                understanding_result, generation_result
            )

            # 5. 성능 메트릭 업데이트
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time, integration_score)

            # 6. 결과 생성
            result = IntegratedLanguageResult(
                result_id=f"result_{int(time.time())}",
                understanding_result=understanding_result,
                generation_result=generation_result,
                integration_score=integration_score,
                system_performance={
                    "processing_time": processing_time,
                    "system_status": self.system_status,
                    "performance_metrics": dict(self.performance_metrics),
                },
            )

            logger.info(
                f"✅ 통합 언어 처리 완료 (소요시간: {processing_time:.2f}초, 통합점수: {integration_score:.2f})"
            )

            return result

        except Exception as e:
            logger.error(f"통합 언어 처리 실패: {e}")
            raise

    def _calculate_integration_score(
        self,
        understanding_result: LanguageUnderstandingResult,
        generation_result: LanguageGenerationResult,
    ) -> float:
        """통합 점수 계산 (재조정 및 0.0~1.0 정규화 적용)"""
        try:
            # 이해 점수 (0.0~1.0 정규화)
            understanding_score = max(
                0.0, min(1.0, understanding_result.confidence_score)
            )

            # 생성 점수 (0.0~1.0 정규화)
            generation_score = max(0.0, min(1.0, generation_result.confidence_score))

            # 맥락 관련성 점수 (0.0~1.0 정규화)
            contextual_score = max(
                0.0, min(1.0, generation_result.contextual_relevance)
            )

            # 의미 분석 결과 반영 (새로운 가중치 추가)
            semantic_score = 0.0
            if understanding_result.key_concepts:
                semantic_score = min(1.0, len(understanding_result.key_concepts) * 0.1)
            if understanding_result.learning_insights:
                semantic_score = min(
                    1.0,
                    semantic_score + len(understanding_result.learning_insights) * 0.1,
                )

            # 통합 점수 (가중 평균) - 재조정된 가중치
            integration_score = (
                understanding_score * 0.35  # 이해 점수 (35%)
                + generation_score * 0.35  # 생성 점수 (35%)
                + contextual_score * 0.20  # 맥락 관련성 (20%)
                + semantic_score * 0.10  # 의미 분석 (10%)
            )

            # 0.0~1.0 정규화 적용
            normalized_score = max(0.0, min(1.0, integration_score))

            return normalized_score

        except Exception as e:
            logger.error(f"통합 점수 계산 실패: {e}")
            return 0.5  # 기본값 반환

    def _update_performance_metrics(
        self, processing_time: float, integration_score: float
    ):
        """성능 메트릭 업데이트 (division by zero 예외 방지)"""
        try:
            self.performance_metrics["total_processing_time"] += processing_time

            # division by zero 예외 방지
            current_count = self.performance_metrics.get("request_count", 0)
            new_count = current_count + 1

            if new_count > 0:
                self.performance_metrics["average_processing_time"] = (
                    self.performance_metrics["total_processing_time"] / new_count
                )

                # 평균 통합 점수 계산 (division by zero 예외 방지)
                current_avg = self.performance_metrics.get(
                    "average_integration_score", 0.0
                )
                self.performance_metrics["average_integration_score"] = (
                    current_avg * current_count + integration_score
                ) / new_count

            self.performance_metrics["request_count"] = new_count

        except Exception as e:
            logger.error(f"성능 메트릭 업데이트 실패: {e}")
            # 기본값 설정
            self.performance_metrics["request_count"] = (
                self.performance_metrics.get("request_count", 0) + 1
            )
            self.performance_metrics["average_processing_time"] = processing_time
            self.performance_metrics["average_integration_score"] = integration_score

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "status": self.system_status,
            "performance_metrics": dict(self.performance_metrics),
            "timestamp": datetime.now().isoformat(),
        }

    async def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 조회"""
        return {
            "system_name": self.system_name,
            "version": self.version,
            "performance_metrics": dict(self.performance_metrics),
            "system_health": "healthy" if self.system_status == "active" else "warning",
            "timestamp": datetime.now().isoformat(),
        }


# 테스트 함수
async def test_integrated_language_system():
    """통합 언어 시스템 테스트"""
    logger.info("=== 통합 언어 이해 및 생성 시스템 테스트 시작 ===")

    # 시스템 초기화
    system = IntegratedLanguageUnderstandingGenerationSystem()

    # 테스트 케이스들
    test_cases = [
        {
            "text": "오늘 정말 기뻐요! 새로운 것을 배웠어요.",
            "context": {"topic": "학습", "emotion": "기쁨"},
            "generation_type": LanguageGenerationType.EMOTIONAL_EXPRESSION,
        },
        {
            "text": "가족과 함께하는 시간이 가장 소중해요.",
            "context": {"topic": "가족", "emotion": "사랑"},
            "generation_type": LanguageGenerationType.CONVERSATIONAL_RESPONSE,
        },
        {
            "text": "어려운 문제를 해결하는 방법을 알려주세요.",
            "context": {"topic": "문제해결", "intent": "질문"},
            "generation_type": LanguageGenerationType.CONTEXTUAL_GENERATION,
        },
    ]

    results = []

    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"테스트 케이스 {i}: {test_case['text']}")

        try:
            result = await system.process_language(
                text=test_case["text"],
                context=test_case["context"],
                generation_type=test_case["generation_type"],
            )

            results.append(
                {
                    "test_case": i,
                    "input_text": test_case["text"],
                    "understanding_score": result.understanding_result.confidence_score,
                    "generation_score": result.generation_result.confidence_score,
                    "integration_score": result.integration_score,
                    "generated_text": result.generation_result.generated_text,
                }
            )

            logger.info(f"✅ 테스트 케이스 {i} 완료")
            logger.info(
                f"   이해 점수: {result.understanding_result.confidence_score:.2f}"
            )
            logger.info(
                f"   생성 점수: {result.generation_result.confidence_score:.2f}"
            )
            logger.info(f"   통합 점수: {result.integration_score:.2f}")
            logger.info(f"   생성된 텍스트: {result.generation_result.generated_text}")

        except Exception as e:
            logger.error(f"❌ 테스트 케이스 {i} 실패: {e}")
            results.append({"test_case": i, "error": str(e)})

    # 전체 결과 요약
    successful_tests = [r for r in results if "error" not in r]
    if successful_tests:
        avg_understanding_score = np.mean(
            [r["understanding_score"] for r in successful_tests]
        )
        avg_generation_score = np.mean(
            [r["generation_score"] for r in successful_tests]
        )
        avg_integration_score = np.mean(
            [r["integration_score"] for r in successful_tests]
        )

        logger.info(f"\n=== 테스트 결과 요약 ===")
        logger.info(f"성공한 테스트: {len(successful_tests)}/{len(test_cases)}")
        logger.info(f"평균 이해 점수: {avg_understanding_score:.2f}")
        logger.info(f"평균 생성 점수: {avg_generation_score:.2f}")
        logger.info(f"평균 통합 점수: {avg_integration_score:.2f}")

    # 시스템 상태 조회
    system_status = await system.get_system_status()
    logger.info(f"\n시스템 상태: {system_status['status']}")

    return results


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_integrated_language_system())
