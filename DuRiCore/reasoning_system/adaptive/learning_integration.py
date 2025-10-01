#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 학습 연동 인터페이스

추론과 학습 시스템을 실시간으로 연동하는 인터페이스입니다.
- 관련 지식 검색
- 학습 인사이트 생성
- 적응 제안 생성
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..data_structures import ReasoningSession

logger = logging.getLogger(__name__)


class LearningIntegrationInterface:
    """학습 연동 인터페이스"""

    def __init__(self, learning_system=None):
        self.logger = logging.getLogger(__name__)
        self.learning_system = learning_system
        self.integration_history = []
        self.logger.info("학습 연동 인터페이스 초기화 완료")

    async def integrate_learning_with_reasoning(
        self, reasoning_session: ReasoningSession
    ) -> Dict[str, Any]:
        """추론과 학습의 실시간 연동"""
        try:
            integration_result = {
                "integration_id": f"integration_{int(time.time())}",
                "session_id": reasoning_session.session_id,
                "learning_insights": [],
                "knowledge_applied": [],
                "adaptation_suggestions": [],
            }

            # 학습 시스템에서 관련 지식 검색
            relevant_knowledge = await self._search_relevant_knowledge(
                reasoning_session
            )
            integration_result["knowledge_applied"] = relevant_knowledge

            # 추론 과정에서 학습 인사이트 생성
            learning_insights = await self._generate_learning_insights(
                reasoning_session
            )
            integration_result["learning_insights"] = learning_insights

            # 적응 제안 생성
            adaptation_suggestions = await self._generate_adaptation_suggestions(
                reasoning_session
            )
            integration_result["adaptation_suggestions"] = adaptation_suggestions

            return integration_result
        except Exception as e:
            self.logger.error(f"학습 연동 중 오류 발생: {e}")
            return self._create_fallback_integration_result(reasoning_session)

    async def _search_relevant_knowledge(
        self, reasoning_session: ReasoningSession
    ) -> List[Dict[str, Any]]:
        """관련 지식 검색"""
        try:
            # 추론 컨텍스트와 유형에 따른 지식 검색
            search_criteria = {
                "context": reasoning_session.context.value,
                "reasoning_type": reasoning_session.reasoning_type.value,
                "input_data": reasoning_session.input_data,
            }

            # 학습 시스템에서 관련 지식 검색 (시뮬레이션)
            relevant_knowledge = [
                {
                    "knowledge_id": f"knowledge_{int(time.time())}",
                    "content": f"관련 지식: {reasoning_session.context.value}",
                    "relevance_score": 0.85,
                    "confidence": 0.9,
                }
            ]

            return relevant_knowledge
        except Exception as e:
            self.logger.error(f"관련 지식 검색 중 오류: {e}")
            return []

    async def _generate_learning_insights(
        self, reasoning_session: ReasoningSession
    ) -> List[str]:
        """학습 인사이트 생성"""
        try:
            insights = []

            # 추론 과정 분석
            if reasoning_session.reasoning_steps:
                insights.append(
                    f"추론 단계 수: {len(reasoning_session.reasoning_steps)}"
                )
                insights.append(f"추론 유형: {reasoning_session.reasoning_type.value}")
                insights.append(f"추론 컨텍스트: {reasoning_session.context.value}")

            # 성능 분석
            if reasoning_session.confidence_score > 0.8:
                insights.append("높은 신뢰도로 추론 완료")
            elif reasoning_session.confidence_score < 0.5:
                insights.append("낮은 신뢰도 - 추가 학습 필요")

            return insights
        except Exception as e:
            self.logger.error(f"학습 인사이트 생성 중 오류: {e}")
            return []

    async def _generate_adaptation_suggestions(
        self, reasoning_session: ReasoningSession
    ) -> List[str]:
        """적응 제안 생성"""
        try:
            suggestions = []

            # 신뢰도 기반 제안
            if reasoning_session.confidence_score < 0.6:
                suggestions.append("추론 방식 변경 고려")
                suggestions.append("추가 정보 수집 필요")

            # 효율성 기반 제안
            if reasoning_session.efficiency_score < 0.7:
                suggestions.append("추론 과정 최적화 필요")
                suggestions.append("단계 간소화 고려")

            # 적응도 기반 제안
            if reasoning_session.adaptation_score < 0.5:
                suggestions.append("상황 적응 능력 향상 필요")
                suggestions.append("다양한 추론 방식 연습")

            return suggestions
        except Exception as e:
            self.logger.error(f"적응 제안 생성 중 오류: {e}")
            return []

    def _create_fallback_integration_result(
        self, reasoning_session: ReasoningSession
    ) -> Dict[str, Any]:
        """폴백 연동 결과 생성"""
        return {
            "integration_id": f"fallback_{int(time.time())}",
            "session_id": reasoning_session.session_id,
            "learning_insights": ["기본 학습 인사이트"],
            "knowledge_applied": [],
            "adaptation_suggestions": ["기본 적응 제안"],
        }
