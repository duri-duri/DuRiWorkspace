#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 시스템 - 고급 언어 생성 엔진

고급적인 언어 생성을 수행하는 핵심 엔진입니다.
- 대화 생성
- 감정적 표현 생성
- 맥락 기반 생성
- 다국어 생성
- 창의적 생성
"""

import json
import time
import logging
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from ..generation.conversational_generator import ConversationalGenerator
from ..generation.emotional_generator import EmotionalGenerator
from ..generation.contextual_generator import ContextualGenerator
from ..generation.multilingual_generator import MultilingualGenerator
from ..generation.creative_generator import CreativeGenerator
from .data_structures import LanguageGenerationResult, LanguageGenerationType

logger = logging.getLogger(__name__)

class AdvancedLanguageGenerationEngine:
    """고급 언어 생성 엔진"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.generation_cache = {}
        self.conversational_generator = ConversationalGenerator()
        self.emotional_generator = EmotionalGenerator()
        self.contextual_generator = ContextualGenerator()
        self.multilingual_generator = MultilingualGenerator()
        self.creative_generator = CreativeGenerator()
        
        self.logger.info("고급 언어 생성 엔진 초기화 완료")
    
    async def generate_language(self, context: Dict[str, Any], generation_type: LanguageGenerationType) -> LanguageGenerationResult:
        """고급 언어 생성 (의미 분석 결과 반영 강화)"""
        try:
            generation_id = f"generation_{int(time.time())}"
            
            # 캐시 확인
            cache_key = hashlib.md5(f"{json.dumps(context, sort_keys=True) if context else '{}'}_{generation_type.value}".encode()).hexdigest()
            if cache_key in self.generation_cache:
                return self.generation_cache[cache_key]
            
            # 의미 분석 결과 추출 (새로 추가)
            semantic_analysis = context.get('semantic_analysis', {})
            learning_insights = context.get('learning_insights', [])
            key_concepts = context.get('keywords', [])
            confidence_score = context.get('confidence_score', 0.5)
            
            # 의미 분석 결과를 컨텍스트에 반영
            enhanced_context = context.copy() if context else {}
            if semantic_analysis:
                enhanced_context.update(semantic_analysis)
            if learning_insights:
                enhanced_context['learning_insights'] = learning_insights
            if key_concepts:
                enhanced_context['key_concepts'] = key_concepts
            enhanced_context['semantic_confidence'] = confidence_score
            
            # 생성 유형에 따른 처리
            if generation_type == LanguageGenerationType.CONVERSATIONAL_RESPONSE:
                generated_text = await self.conversational_generator.generate_response(enhanced_context)
            elif generation_type == LanguageGenerationType.EMOTIONAL_EXPRESSION:
                generated_text = await self.emotional_generator.generate_emotional_expression(enhanced_context)
            elif generation_type == LanguageGenerationType.CONTEXTUAL_GENERATION:
                generated_text = await self.contextual_generator.generate_contextual_text(enhanced_context)
            elif generation_type == LanguageGenerationType.MULTILINGUAL_GENERATION:
                generated_text = await self.multilingual_generator.generate_multilingual_text(enhanced_context)
            elif generation_type == LanguageGenerationType.CREATIVE_WRITING:
                generated_text = await self.creative_generator.generate_creative_text(enhanced_context)
            else:
                generated_text = await self.conversational_generator.generate_response(enhanced_context)
            
            # 감정적 표현 분석
            emotional_expression = await self.emotional_generator.analyze_emotional_expression(generated_text)
            
            # 맥락 관련성 평가 (의미 분석 결과 반영)
            contextual_relevance = await self.contextual_generator.evaluate_contextual_relevance(generated_text, enhanced_context)
            
            # 다국어 지원
            multilingual_support = await self.multilingual_generator.get_multilingual_support(generated_text, enhanced_context)
            
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
                confidence_score=confidence_score
            )
            
            # 캐시 저장
            self.generation_cache[cache_key] = generation_result
            
            return generation_result
        except Exception as e:
            self.logger.error(f"고급 언어 생성 중 오류 발생: {e}")
            return self._create_fallback_generation_result(context, generation_type)
    
    def _calculate_generation_confidence(self, generated_text: str, emotional_expression: str, 
                                       contextual_relevance: float, context: Dict[str, Any] = None) -> float:
        """생성 신뢰도 계산 (의미 분석 결과 반영)"""
        try:
            # 텍스트 품질 평가
            text_quality = min(1.0, len(generated_text.strip()) / 100.0)  # 기본 품질 점수
            
            # 감정적 표현 평가
            emotion_quality = 1.0 if emotional_expression else 0.5
            
            # 맥락 관련성 평가
            context_quality = max(0.0, min(1.0, contextual_relevance))
            
            # 의미 분석 결과 반영 (새로 추가)
            semantic_quality = 0.5  # 기본값
            if context:
                # 키 컨셉 반영
                key_concepts = context.get('key_concepts', [])
                if key_concepts:
                    semantic_quality = min(1.0, semantic_quality + len(key_concepts) * 0.1)
                
                # 학습 통찰 반영
                learning_insights = context.get('learning_insights', [])
                if learning_insights:
                    semantic_quality = min(1.0, semantic_quality + len(learning_insights) * 0.1)
                
                # 의미 분석 신뢰도 반영
                semantic_confidence = context.get('semantic_confidence', 0.5)
                semantic_quality = min(1.0, semantic_quality + semantic_confidence * 0.2)
            
            # 통합 신뢰도 (의미 분석 가중치 추가)
            confidence = (
                text_quality * 0.3 +           # 텍스트 품질 (30%)
                emotion_quality * 0.2 +        # 감정적 표현 (20%)
                context_quality * 0.3 +        # 맥락 관련성 (30%)
                semantic_quality * 0.2         # 의미 분석 (20%)
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.error(f"생성 신뢰도 계산 실패: {e}")
            return 0.5  # 기본값 반환
    
    def _create_fallback_generation_result(self, context: Dict[str, Any], generation_type: LanguageGenerationType) -> LanguageGenerationResult:
        """폴백 생성 결과 생성"""
        return LanguageGenerationResult(
            generation_id=f"fallback_{int(time.time())}",
            source_context=context or {},
            generation_type=generation_type,
            generated_text="죄송합니다. 응답을 생성하는 중에 오류가 발생했습니다.",
            emotional_expression="중립",
            contextual_relevance=0.0,
            multilingual_support={},
            confidence_score=0.0
        )
