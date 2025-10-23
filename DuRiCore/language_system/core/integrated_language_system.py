#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 언어 시스템 - 통합 언어 이해 및 생성 시스템

언어 이해와 생성을 통합하는 메인 시스템입니다.
- 심층 언어 이해
- 고급 언어 생성
- 통합 분석
- 성능 모니터링
"""

import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from .advanced_generation_engine import AdvancedLanguageGenerationEngine
from .data_structures import (IntegratedLanguageResult,
                              LanguageGenerationResult, LanguageGenerationType,
                              LanguageUnderstandingResult)
from .deep_understanding_engine import DeepLanguageUnderstandingEngine

logger = logging.getLogger(__name__)


class IntegratedLanguageUnderstandingGenerationSystem:
    """통합 언어 이해 및 생성 시스템"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.system_name = "통합 언어 이해 및 생성 시스템"
        self.version = "1.0.0"
        self.deep_understanding_engine = DeepLanguageUnderstandingEngine()
        self.advanced_generation_engine = AdvancedLanguageGenerationEngine()

        # 성능 메트릭
        self.performance_metrics = defaultdict(float)
        self.system_status = "active"

        self.logger.info(f"🚀 {self.system_name} v{self.version} 초기화 완료")

    async def process_language(
        self,
        text: str,
        context: Dict[str, Any] = None,
        generation_type: LanguageGenerationType = LanguageGenerationType.CONVERSATIONAL_RESPONSE,
    ) -> IntegratedLanguageResult:
        """통합 언어 처리"""
        start_time = time.time()

        try:
            self.logger.info("=== 통합 언어 이해 및 생성 시스템 시작 ===")

            # 1. 빈 입력 처리 시 division by zero 예외 방지 로직 추가
            if not text or not text.strip():
                self.logger.warning("빈 텍스트 입력 감지, 기본값으로 처리")
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

            self.logger.info(
                f"✅ 통합 언어 처리 완료 (소요시간: {processing_time:.2f}초, 통합점수: {integration_score:.2f})"
            )

            return result

        except Exception as e:
            self.logger.error(f"통합 언어 처리 실패: {e}")
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
            self.logger.error(f"통합 점수 계산 실패: {e}")
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
            self.logger.error(f"성능 메트릭 업데이트 실패: {e}")
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
