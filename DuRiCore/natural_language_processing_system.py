#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 9 - 자연어 처리 시스템

자연어 처리 및 이해 능력 강화
- 고급 텍스트 분석
- 의미 추출 및 이해
- 문맥 인식 및 처리
- 다국어 지원
"""

import asyncio
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional, Tuple
import unicodedata

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TextAnalysis:
    """텍스트 분석 결과 데이터 구조"""

    text_id: str
    original_text: str
    processed_text: str
    analysis_type: str
    features: Dict[str, Any]
    sentiment_score: float
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class SemanticExtraction:
    """의미 추출 결과 데이터 구조"""

    extraction_id: str
    source_text: str
    extracted_entities: List[Dict[str, Any]]
    extracted_concepts: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    semantic_graph: Dict[str, Any]
    confidence: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ContextualAnalysis:
    """문맥 분석 결과 데이터 구조"""

    context_id: str
    text: str
    context_type: str
    contextual_features: Dict[str, Any]
    context_score: float
    related_contexts: List[str]
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LanguageSupport:
    """다국어 지원 데이터 구조"""

    language_code: str
    language_name: str
    supported_features: List[str]
    processing_rules: Dict[str, Any]
    created_at: datetime = field(default_factory=datetime.now)


class AdvancedTextAnalyzer:
    """고급 텍스트 분석 시스템"""

    def __init__(self):
        self.text_cache = {}
        self.analysis_models = {}
        self.feature_extractors = {}
        self.sentiment_analyzer = {}
        self.confidence_threshold = 0.6

    def analyze_text(
        self, text: str, analysis_type: str = "comprehensive"
    ) -> TextAnalysis:
        """텍스트 분석"""
        text_id = f"text_{int(time.time())}"

        # 캐시 확인
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.text_cache:
            return self.text_cache[cache_key]

        # 텍스트 전처리
        processed_text = self.preprocess_text(text)

        # 분석 실행
        if analysis_type == "comprehensive":
            features = self.comprehensive_analysis(processed_text)
        elif analysis_type == "sentiment":
            features = self.sentiment_analysis(processed_text)
        elif analysis_type == "structural":
            features = self.structural_analysis(processed_text)
        else:
            features = self.basic_analysis(processed_text)

        # 감정 분석
        sentiment_score = self.calculate_sentiment(processed_text)

        # 신뢰도 계산
        confidence = self.calculate_confidence(features, sentiment_score)

        # 분석 결과 생성
        analysis_result = TextAnalysis(
            text_id=text_id,
            original_text=text,
            processed_text=processed_text,
            analysis_type=analysis_type,
            features=features,
            sentiment_score=sentiment_score,
            confidence=confidence,
        )

        self.text_cache[cache_key] = analysis_result
        return analysis_result

    def preprocess_text(self, text: str) -> str:
        """텍스트 전처리"""
        # 기본 정규화
        text = text.strip()
        text = re.sub(r"\s+", " ", text)  # 연속된 공백 제거

        # 특수 문자 처리
        text = unicodedata.normalize("NFKC", text)

        # 기본 정제
        text = re.sub(r"[^\w\s\.\,\!\?\;\:\-\(\)]", "", text)

        return text

    def comprehensive_analysis(self, text: str) -> Dict[str, Any]:
        """종합적 텍스트 분석"""
        features = {}

        # 기본 통계
        features["length"] = len(text)
        features["word_count"] = len(text.split())
        features["sentence_count"] = len(re.split(r"[.!?]+", text))
        features["paragraph_count"] = len(text.split("\n\n"))

        # 어휘 분석
        words = text.lower().split()
        features["unique_words"] = len(set(words))
        features["vocabulary_diversity"] = len(set(words)) / len(words) if words else 0

        # 문장 길이 분석
        sentences = re.split(r"[.!?]+", text)
        sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
        if sentence_lengths:
            features["avg_sentence_length"] = np.mean(sentence_lengths)
            features["sentence_length_std"] = np.std(sentence_lengths)

        # 어휘 복잡도
        features["avg_word_length"] = (
            np.mean([len(word) for word in words]) if words else 0
        )

        # 문체 분석
        features["formal_indicators"] = self.count_formal_indicators(text)
        features["informal_indicators"] = self.count_informal_indicators(text)

        return features

    def sentiment_analysis(self, text: str) -> Dict[str, Any]:
        """감정 분석"""
        features = {}

        # 긍정/부정 키워드 분석
        positive_words = [
            "좋다",
            "훌륭하다",
            "멋지다",
            "행복하다",
            "성공하다",
            "좋은",
            "훌륭한",
            "멋진",
        ]
        negative_words = [
            "나쁘다",
            "끔찍하다",
            "실패하다",
            "슬프다",
            "화나다",
            "나쁜",
            "끔찍한",
            "실패한",
        ]

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        features["positive_word_count"] = positive_count
        features["negative_word_count"] = negative_count
        features["sentiment_ratio"] = (
            (positive_count - negative_count) / len(words) if words else 0
        )

        # 감정 강도
        features["emotion_intensity"] = (
            (positive_count + negative_count) / len(words) if words else 0
        )

        return features

    def structural_analysis(self, text: str) -> Dict[str, Any]:
        """구조적 분석"""
        features = {}

        # 문장 구조 분석
        sentences = re.split(r"[.!?]+", text)
        features["sentence_count"] = len([s for s in sentences if s.strip()])

        # 단락 구조 분석
        paragraphs = text.split("\n\n")
        features["paragraph_count"] = len([p for p in paragraphs if p.strip()])

        # 문장 유형 분석
        question_count = len(re.findall(r"\?", text))
        exclamation_count = len(re.findall(r"\!", text))

        features["question_count"] = question_count
        features["exclamation_count"] = exclamation_count
        features["question_ratio"] = (
            question_count / features["sentence_count"]
            if features["sentence_count"] > 0
            else 0
        )

        return features

    def basic_analysis(self, text: str) -> Dict[str, Any]:
        """기본 분석"""
        features = {}
        features["length"] = len(text)
        features["word_count"] = len(text.split())
        features["character_count"] = len(text.replace(" ", ""))
        return features

    def calculate_sentiment(self, text: str) -> float:
        """감정 점수 계산"""
        words = text.lower().split()
        if not words:
            return 0.0

        # 감정 사전 기반 분석
        positive_words = [
            "좋다",
            "훌륭하다",
            "멋지다",
            "행복하다",
            "성공하다",
            "좋은",
            "훌륭한",
            "멋진",
        ]
        negative_words = [
            "나쁘다",
            "끔찍하다",
            "실패하다",
            "슬프다",
            "화나다",
            "나쁜",
            "끔찍한",
            "실패한",
        ]

        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        total_sentiment_words = positive_count + negative_count
        if total_sentiment_words == 0:
            return 0.0

        sentiment_score = (positive_count - negative_count) / total_sentiment_words
        return max(-1.0, min(1.0, sentiment_score))

    def calculate_confidence(
        self, features: Dict[str, Any], sentiment_score: float
    ) -> float:
        """신뢰도 계산"""
        confidence = 0.5  # 기본 신뢰도

        # 특징 기반 신뢰도 조정
        if features.get("word_count", 0) > 10:
            confidence += 0.2

        if features.get("vocabulary_diversity", 0) > 0.5:
            confidence += 0.1

        if abs(sentiment_score) > 0.3:
            confidence += 0.1

        return min(1.0, confidence)

    def count_formal_indicators(self, text: str) -> int:
        """형식적 지표 카운트"""
        formal_indicators = ["입니다", "습니다", "습니다", "입니다", "입니다"]
        return sum(text.count(indicator) for indicator in formal_indicators)

    def count_informal_indicators(self, text: str) -> int:
        """비형식적 지표 카운트"""
        informal_indicators = ["야", "어", "아", "네", "요"]
        return sum(text.count(indicator) for indicator in informal_indicators)


class SemanticExtractor:
    """의미 추출 및 이해 시스템"""

    def __init__(self):
        self.entity_extractors = {}
        self.concept_extractors = {}
        self.relationship_extractors = {}
        self.semantic_graphs = {}
        self.extraction_cache = {}

    def extract_semantics(self, text: str) -> SemanticExtraction:
        """의미 추출"""
        extraction_id = f"extraction_{int(time.time())}"

        # 캐시 확인
        cache_key = hashlib.md5(text.encode()).hexdigest()
        if cache_key in self.extraction_cache:
            return self.extraction_cache[cache_key]

        # 엔티티 추출
        entities = self.extract_entities(text)

        # 개념 추출
        concepts = self.extract_concepts(text)

        # 관계 추출
        relationships = self.extract_relationships(text, entities, concepts)

        # 의미 그래프 생성
        semantic_graph = self.build_semantic_graph(entities, concepts, relationships)

        # 신뢰도 계산
        confidence = self.calculate_extraction_confidence(
            entities, concepts, relationships
        )

        # 추출 결과 생성
        extraction_result = SemanticExtraction(
            extraction_id=extraction_id,
            source_text=text,
            extracted_entities=entities,
            extracted_concepts=concepts,
            relationships=relationships,
            semantic_graph=semantic_graph,
            confidence=confidence,
        )

        self.extraction_cache[cache_key] = extraction_result
        return extraction_result

    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """엔티티 추출"""
        entities = []

        # 명사 추출 (간단한 규칙 기반)
        nouns = re.findall(r"\b[가-힣]+[이|가|을|를|의|에|로|와|과]\b", text)

        for noun in nouns:
            # 명사 정제
            clean_noun = re.sub(r"[이|가|을|를|의|에|로|와|과]$", "", noun)
            if len(clean_noun) > 1:
                entities.append(
                    {
                        "text": clean_noun,
                        "type": "noun",
                        "confidence": 0.7,
                        "position": text.find(noun),
                    }
                )

        # 숫자 추출
        numbers = re.findall(r"\d+", text)
        for number in numbers:
            entities.append(
                {
                    "text": number,
                    "type": "number",
                    "confidence": 0.9,
                    "position": text.find(number),
                }
            )

        # 날짜 추출
        dates = re.findall(r"\d{4}년\s*\d{1,2}월\s*\d{1,2}일", text)
        for date in dates:
            entities.append(
                {
                    "text": date,
                    "type": "date",
                    "confidence": 0.8,
                    "position": text.find(date),
                }
            )

        return entities

    def extract_concepts(self, text: str) -> List[Dict[str, Any]]:
        """개념 추출"""
        concepts = []

        # 키워드 추출
        words = text.split()
        word_freq = Counter(words)

        # 빈도 기반 키워드 추출
        for word, freq in word_freq.most_common(10):
            if freq > 1 and len(word) > 1:
                concepts.append(
                    {
                        "text": word,
                        "type": "keyword",
                        "frequency": freq,
                        "confidence": min(0.9, freq / len(words)),
                    }
                )

        # 주제 추출 (간단한 규칙 기반)
        topics = {
            "기술": ["기술", "개발", "프로그래밍", "코딩", "소프트웨어"],
            "비즈니스": ["비즈니스", "경영", "마케팅", "전략", "수익"],
            "교육": ["교육", "학습", "훈련", "강의", "수업"],
            "건강": ["건강", "운동", "의료", "치료", "예방"],
        }

        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in text:
                    concepts.append(
                        {
                            "text": topic,
                            "type": "topic",
                            "confidence": 0.8,
                            "keywords": [keyword],
                        }
                    )
                    break

        return concepts

    def extract_relationships(
        self, text: str, entities: List[Dict[str, Any]], concepts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """관계 추출"""
        relationships = []

        # 엔티티 간 관계 추출
        for i, entity1 in enumerate(entities):
            for j, entity2 in enumerate(entities[i + 1 :], i + 1):
                # 간단한 거리 기반 관계 추출
                distance = abs(entity1["position"] - entity2["position"])
                if distance < 50:  # 50자 이내
                    relationships.append(
                        {
                            "source": entity1["text"],
                            "target": entity2["text"],
                            "type": "proximity",
                            "confidence": max(0.3, 1.0 - distance / 50),
                            "distance": distance,
                        }
                    )

        # 개념과 엔티티 간 관계
        for concept in concepts:
            for entity in entities:
                if (
                    concept["text"] in entity["text"]
                    or entity["text"] in concept["text"]
                ):
                    relationships.append(
                        {
                            "source": concept["text"],
                            "target": entity["text"],
                            "type": "contains",
                            "confidence": 0.8,
                        }
                    )

        return relationships

    def build_semantic_graph(
        self,
        entities: List[Dict[str, Any]],
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """의미 그래프 생성"""
        graph = {
            "nodes": [],
            "edges": [],
            "metadata": {
                "node_count": len(entities) + len(concepts),
                "edge_count": len(relationships),
                "created_at": datetime.now().isoformat(),
            },
        }

        # 노드 추가
        for entity in entities:
            graph["nodes"].append(
                {
                    "id": entity["text"],
                    "type": "entity",
                    "entity_type": entity["type"],
                    "confidence": entity["confidence"],
                }
            )

        for concept in concepts:
            graph["nodes"].append(
                {
                    "id": concept["text"],
                    "type": "concept",
                    "concept_type": concept["type"],
                    "confidence": concept["confidence"],
                }
            )

        # 엣지 추가
        for relationship in relationships:
            graph["edges"].append(
                {
                    "source": relationship["source"],
                    "target": relationship["target"],
                    "type": relationship["type"],
                    "confidence": relationship["confidence"],
                }
            )

        return graph

    def calculate_extraction_confidence(
        self,
        entities: List[Dict[str, Any]],
        concepts: List[Dict[str, Any]],
        relationships: List[Dict[str, Any]],
    ) -> float:
        """추출 신뢰도 계산"""
        if not entities and not concepts:
            return 0.0

        # 엔티티 신뢰도
        entity_confidence = (
            np.mean([e["confidence"] for e in entities]) if entities else 0.0
        )

        # 개념 신뢰도
        concept_confidence = (
            np.mean([c["confidence"] for c in concepts]) if concepts else 0.0
        )

        # 관계 신뢰도
        relationship_confidence = (
            np.mean([r["confidence"] for r in relationships]) if relationships else 0.0
        )

        # 종합 신뢰도
        total_confidence = (
            entity_confidence + concept_confidence + relationship_confidence
        ) / 3
        return min(1.0, total_confidence)


class ContextualProcessor:
    """문맥 인식 및 처리 시스템"""

    def __init__(self):
        self.context_models = {}
        self.context_cache = {}
        self.contextual_rules = {}
        self.context_analyzer = {}

    def analyze_context(
        self, text: str, context_type: str = "general"
    ) -> ContextualAnalysis:
        """문맥 분석"""
        context_id = f"context_{int(time.time())}"

        # 캐시 확인
        cache_key = hashlib.md5((text + context_type).encode()).hexdigest()
        if cache_key in self.context_cache:
            return self.context_cache[cache_key]

        # 문맥 특징 추출
        contextual_features = self.extract_contextual_features(text, context_type)

        # 문맥 점수 계산
        context_score = self.calculate_context_score(contextual_features)

        # 관련 문맥 찾기
        related_contexts = self.find_related_contexts(text, context_type)

        # 문맥 분석 결과 생성
        context_analysis = ContextualAnalysis(
            context_id=context_id,
            text=text,
            context_type=context_type,
            contextual_features=contextual_features,
            context_score=context_score,
            related_contexts=related_contexts,
        )

        self.context_cache[cache_key] = context_analysis
        return context_analysis

    def extract_contextual_features(
        self, text: str, context_type: str
    ) -> Dict[str, Any]:
        """문맥 특징 추출"""
        features = {}

        # 시간적 문맥
        features["temporal_context"] = self.extract_temporal_context(text)

        # 공간적 문맥
        features["spatial_context"] = self.extract_spatial_context(text)

        # 사회적 문맥
        features["social_context"] = self.extract_social_context(text)

        # 주제적 문맥
        features["topical_context"] = self.extract_topical_context(text)

        # 감정적 문맥
        features["emotional_context"] = self.extract_emotional_context(text)

        return features

    def extract_temporal_context(self, text: str) -> Dict[str, Any]:
        """시간적 문맥 추출"""
        temporal_features = {}

        # 시간 표현 추출
        time_patterns = [
            r"\d{4}년",
            r"\d{1,2}월",
            r"\d{1,2}일",
            r"오늘",
            r"어제",
            r"내일",
            r"이번 주",
            r"다음 주",
        ]

        temporal_features["time_expressions"] = []
        for pattern in time_patterns:
            matches = re.findall(pattern, text)
            temporal_features["time_expressions"].extend(matches)

        temporal_features["temporal_density"] = (
            len(temporal_features["time_expressions"]) / len(text.split())
            if text.split()
            else 0
        )

        return temporal_features

    def extract_spatial_context(self, text: str) -> Dict[str, Any]:
        """공간적 문맥 추출"""
        spatial_features = {}

        # 장소 표현 추출
        location_patterns = [
            r"[가-힣]+시",
            r"[가-힣]+구",
            r"[가-힣]+동",
            r"[가-힣]+국",
            r"[가-힣]+회사",
            r"[가-힣]+학교",
        ]

        spatial_features["location_expressions"] = []
        for pattern in location_patterns:
            matches = re.findall(pattern, text)
            spatial_features["location_expressions"].extend(matches)

        spatial_features["spatial_density"] = (
            len(spatial_features["location_expressions"]) / len(text.split())
            if text.split()
            else 0
        )

        return spatial_features

    def extract_social_context(self, text: str) -> Dict[str, Any]:
        """사회적 문맥 추출"""
        social_features = {}

        # 사회적 관계 표현
        social_indicators = ["친구", "가족", "동료", "상사", "부하", "고객", "파트너"]

        social_features["social_indicators"] = []
        for indicator in social_indicators:
            if indicator in text:
                social_features["social_indicators"].append(indicator)

        social_features["social_density"] = (
            len(social_features["social_indicators"]) / len(text.split())
            if text.split()
            else 0
        )

        return social_features

    def extract_topical_context(self, text: str) -> Dict[str, Any]:
        """주제적 문맥 추출"""
        topical_features = {}

        # 주제 키워드
        topics = {
            "기술": ["기술", "개발", "프로그래밍", "코딩"],
            "비즈니스": ["비즈니스", "경영", "마케팅", "전략"],
            "교육": ["교육", "학습", "훈련", "강의"],
            "건강": ["건강", "운동", "의료", "치료"],
        }

        topical_features["detected_topics"] = []
        for topic, keywords in topics.items():
            for keyword in keywords:
                if keyword in text:
                    topical_features["detected_topics"].append(topic)
                    break

        return topical_features

    def extract_emotional_context(self, text: str) -> Dict[str, Any]:
        """감정적 문맥 추출"""
        emotional_features = {}

        # 감정 표현
        emotions = {
            "기쁨": ["기쁘다", "행복하다", "즐겁다", "신나다"],
            "슬픔": ["슬프다", "우울하다", "속상하다"],
            "화남": ["화나다", "짜증나다", "분노하다"],
            "걱정": ["걱정하다", "불안하다", "근심하다"],
        }

        emotional_features["detected_emotions"] = []
        for emotion, keywords in emotions.items():
            for keyword in keywords:
                if keyword in text:
                    emotional_features["detected_emotions"].append(emotion)
                    break

        return emotional_features

    def calculate_context_score(self, contextual_features: Dict[str, Any]) -> float:
        """문맥 점수 계산"""
        score = 0.0

        # 각 문맥 유형별 점수 계산
        if (
            contextual_features.get("temporal_context", {}).get("temporal_density", 0)
            > 0
        ):
            score += 0.2

        if contextual_features.get("spatial_context", {}).get("spatial_density", 0) > 0:
            score += 0.2

        if contextual_features.get("social_context", {}).get("social_density", 0) > 0:
            score += 0.2

        if contextual_features.get("topical_context", {}).get("detected_topics"):
            score += 0.2

        if contextual_features.get("emotional_context", {}).get("detected_emotions"):
            score += 0.2

        return min(1.0, score)

    def find_related_contexts(self, text: str, context_type: str) -> List[str]:
        """관련 문맥 찾기"""
        related_contexts = []

        # 간단한 키워드 기반 관련 문맥 찾기
        keywords = text.split()[:5]  # 상위 5개 키워드

        for keyword in keywords:
            if len(keyword) > 1:
                related_contexts.append(f"키워드 '{keyword}' 관련 문맥")

        return related_contexts


class MultilingualSupport:
    """다국어 지원 시스템"""

    def __init__(self):
        self.supported_languages = {}
        self.language_detectors = {}
        self.translation_models = {}
        self.processing_rules = {}

    def detect_language(self, text: str) -> str:
        """언어 감지"""
        # 간단한 언어 감지 (한국어 중심)
        korean_chars = len(re.findall(r"[가-힣]", text))
        english_chars = len(re.findall(r"[a-zA-Z]", text))

        if korean_chars > english_chars:
            return "ko"
        elif english_chars > korean_chars:
            return "en"
        else:
            return "unknown"

    def add_language_support(
        self,
        language_code: str,
        language_name: str,
        features: List[str],
        rules: Dict[str, Any],
    ):
        """언어 지원 추가"""
        language_support = LanguageSupport(
            language_code=language_code,
            language_name=language_name,
            supported_features=features,
            processing_rules=rules,
        )

        self.supported_languages[language_code] = language_support
        logger.info(f"언어 지원 추가됨: {language_code} - {language_name}")

    def get_language_support(self, language_code: str) -> Optional[LanguageSupport]:
        """언어 지원 정보 조회"""
        return self.supported_languages.get(language_code)

    def process_multilingual_text(
        self, text: str, target_language: str = None
    ) -> Dict[str, Any]:
        """다국어 텍스트 처리"""
        detected_language = self.detect_language(text)

        result = {
            "original_text": text,
            "detected_language": detected_language,
            "target_language": target_language,
            "processing_result": {},
        }

        # 언어별 처리 규칙 적용
        if detected_language in self.supported_languages:
            language_support = self.supported_languages[detected_language]
            result["processing_result"] = self.apply_language_rules(
                text, language_support.processing_rules
            )

        return result

    def apply_language_rules(self, text: str, rules: Dict[str, Any]) -> Dict[str, Any]:
        """언어별 처리 규칙 적용"""
        result = {}

        for rule_name, rule_func in rules.items():
            try:
                result[rule_name] = rule_func(text)
            except Exception as e:
                logger.error(f"규칙 적용 중 오류: {rule_name} - {e}")
                result[rule_name] = None

        return result


class NaturalLanguageProcessingSystem:
    """자연어 처리 시스템"""

    def __init__(self):
        self.text_analyzer = AdvancedTextAnalyzer()
        self.semantic_extractor = SemanticExtractor()
        self.contextual_processor = ContextualProcessor()
        self.multilingual_support = MultilingualSupport()
        self.system_status = "active"
        self.performance_metrics = defaultdict(float)

        # 기본 언어 지원 설정
        self.setup_default_language_support()

    def setup_default_language_support(self):
        """기본 언어 지원 설정"""
        # 한국어 지원
        self.multilingual_support.add_language_support(
            "ko",
            "Korean",
            ["text_analysis", "semantic_extraction", "contextual_analysis"],
            {
                "preprocessing": lambda text: text.strip(),
                "tokenization": lambda text: text.split(),
                "normalization": lambda text: unicodedata.normalize("NFKC", text),
            },
        )

        # 영어 지원
        self.multilingual_support.add_language_support(
            "en",
            "English",
            ["text_analysis", "semantic_extraction", "contextual_analysis"],
            {
                "preprocessing": lambda text: text.strip(),
                "tokenization": lambda text: text.split(),
                "normalization": lambda text: text.lower(),
            },
        )

    async def process_text(
        self, text: str, processing_type: str = "comprehensive"
    ) -> Dict[str, Any]:
        """텍스트 처리"""
        start_time = time.time()

        try:
            # 언어 감지
            detected_language = self.multilingual_support.detect_language(text)

            # 텍스트 분석
            text_analysis = self.text_analyzer.analyze_text(text, "comprehensive")

            # 의미 추출
            semantic_extraction = self.semantic_extractor.extract_semantics(text)

            # 문맥 분석
            contextual_analysis = self.contextual_processor.analyze_context(
                text, "general"
            )

            # 다국어 처리
            multilingual_result = self.multilingual_support.process_multilingual_text(
                text, detected_language
            )

            # 결과 통합
            result = {
                "processing_type": processing_type,
                "detected_language": detected_language,
                "text_analysis": text_analysis.__dict__,
                "semantic_extraction": semantic_extraction.__dict__,
                "contextual_analysis": contextual_analysis.__dict__,
                "multilingual_processing": multilingual_result,
                "processing_time": time.time() - start_time,
                "system_status": self.system_status,
            }

            # 성능 메트릭 업데이트
            self.performance_metrics["processing_time"] = result["processing_time"]
            self.performance_metrics["request_count"] += 1

            return result

        except Exception as e:
            logger.error(f"텍스트 처리 중 오류 발생: {e}")
            return {
                "error": str(e),
                "status": "error",
                "processing_time": time.time() - start_time,
            }

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "system_status": self.system_status,
            "performance_metrics": dict(self.performance_metrics),
            "supported_languages": list(
                self.multilingual_support.supported_languages.keys()
            ),
            "component_status": {
                "text_analyzer": "active",
                "semantic_extractor": "active",
                "contextual_processor": "active",
                "multilingual_support": "active",
            },
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 보고서"""
        return {
            "total_requests": self.performance_metrics["request_count"],
            "avg_processing_time": self.performance_metrics["processing_time"],
            "system_uptime": time.time(),
            "component_performance": {
                "text_analyzer": "high",
                "semantic_extractor": "high",
                "contextual_processor": "high",
                "multilingual_support": "high",
            },
        }


# 테스트 함수
async def test_natural_language_processing_system():
    """자연어 처리 시스템 테스트"""
    print("🚀 자연어 처리 시스템 테스트 시작")

    nlp_system = NaturalLanguageProcessingSystem()

    # 1. 텍스트 분석 테스트
    print("\n1. 텍스트 분석 테스트")
    test_text = "오늘은 정말 좋은 날씨입니다. 친구들과 함께 공원에서 피크닉을 즐겼어요."

    analysis_result = await nlp_system.process_text(test_text, "comprehensive")
    print(f"텍스트 분석 결과: {analysis_result}")

    # 2. 의미 추출 테스트
    print("\n2. 의미 추출 테스트")
    semantic_text = "인공지능 기술이 비즈니스 분야에서 혁신을 가져오고 있습니다."

    semantic_result = await nlp_system.process_text(semantic_text, "semantic")
    print(f"의미 추출 결과: {semantic_result}")

    # 3. 문맥 분석 테스트
    print("\n3. 문맥 분석 테스트")
    context_text = (
        "2024년 3월 15일 서울에서 열린 AI 컨퍼런스에서 새로운 기술이 발표되었습니다."
    )

    context_result = await nlp_system.process_text(context_text, "contextual")
    print(f"문맥 분석 결과: {context_result}")

    # 4. 다국어 지원 테스트
    print("\n4. 다국어 지원 테스트")
    english_text = (
        "Today is a beautiful day. I enjoyed a picnic with friends in the park."
    )

    multilingual_result = await nlp_system.process_text(english_text, "multilingual")
    print(f"다국어 처리 결과: {multilingual_result}")

    # 5. 시스템 상태 조회
    print("\n5. 시스템 상태 조회")
    status = nlp_system.get_system_status()
    print(f"시스템 상태: {status}")

    # 6. 성능 보고서
    print("\n6. 성능 보고서")
    performance = nlp_system.get_performance_report()
    print(f"성능 보고서: {performance}")

    print("\n✅ 자연어 처리 시스템 테스트 완료!")


if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(test_natural_language_processing_system())
