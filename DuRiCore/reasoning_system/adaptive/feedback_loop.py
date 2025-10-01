#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 피드백 루프 시스템

추론 결과를 학습 시스템에 피드백하는 시스템입니다.
- 피드백 내용 생성
- 피드백 점수 계산
- 학습 영향도 계산
- 적응 제안 생성
"""

from dataclasses import dataclass
from datetime import datetime
import logging
import time
from typing import Any, Dict, List, Optional

from ..data_structures import ReasoningFeedback, ReasoningSession

logger = logging.getLogger(__name__)


class FeedbackLoopSystem:
    """피드백 루프 시스템"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.feedback_history = []
        self.learning_impact_scores = []
        self.logger.info("피드백 루프 시스템 초기화 완료")

    async def process_reasoning_feedback(
        self, reasoning_session: ReasoningSession
    ) -> ReasoningFeedback:
        """추론 결과를 학습 시스템에 피드백"""
        try:
            feedback_id = f"feedback_{int(time.time())}"

            # 피드백 생성
            feedback_content = await self._generate_feedback_content(reasoning_session)
            feedback_score = await self._calculate_feedback_score(reasoning_session)
            learning_impact = await self._calculate_learning_impact(reasoning_session)
            adaptation_suggestions = await self._generate_adaptation_suggestions(
                reasoning_session
            )

            feedback = ReasoningFeedback(
                feedback_id=feedback_id,
                session_id=reasoning_session.session_id,
                feedback_type="reasoning_performance",
                feedback_content=feedback_content,
                feedback_score=feedback_score,
                learning_impact=learning_impact,
                adaptation_suggestions=adaptation_suggestions,
            )

            self.feedback_history.append(feedback)
            return feedback
        except Exception as e:
            self.logger.error(f"피드백 처리 중 오류 발생: {e}")
            return self._create_fallback_feedback(reasoning_session)

    async def _generate_feedback_content(
        self, reasoning_session: ReasoningSession
    ) -> str:
        """피드백 내용 생성"""
        try:
            content_parts = []

            # 성능 평가
            if reasoning_session.confidence_score >= 0.8:
                content_parts.append("우수한 추론 성능")
            elif reasoning_session.confidence_score >= 0.6:
                content_parts.append("양호한 추론 성능")
            else:
                content_parts.append("개선이 필요한 추론 성능")

            # 적응도 평가
            if reasoning_session.adaptation_score >= 0.7:
                content_parts.append("높은 상황 적응도")
            else:
                content_parts.append("상황 적응도 향상 필요")

            # 효율성 평가
            if reasoning_session.efficiency_score >= 0.8:
                content_parts.append("높은 추론 효율성")
            else:
                content_parts.append("추론 효율성 개선 필요")

            return "; ".join(content_parts)
        except Exception as e:
            self.logger.error(f"피드백 내용 생성 중 오류: {e}")
            return "기본 피드백 내용"

    async def _calculate_feedback_score(
        self, reasoning_session: ReasoningSession
    ) -> float:
        """피드백 점수 계산"""
        try:
            # 신뢰도, 적응도, 효율성의 가중 평균
            weights = {"confidence": 0.4, "adaptation": 0.3, "efficiency": 0.3}

            score = (
                reasoning_session.confidence_score * weights["confidence"]
                + reasoning_session.adaptation_score * weights["adaptation"]
                + reasoning_session.efficiency_score * weights["efficiency"]
            )

            return score
        except Exception as e:
            self.logger.error(f"피드백 점수 계산 중 오류: {e}")
            return 0.5

    async def _calculate_learning_impact(
        self, reasoning_session: ReasoningSession
    ) -> float:
        """학습 영향도 계산"""
        try:
            # 추론 과정에서의 학습 기회 평가
            learning_opportunities = len(reasoning_session.reasoning_steps)
            learning_insights = len(reasoning_session.learning_feedback)

            impact_score = (learning_opportunities * 0.6 + learning_insights * 0.4) / 10
            return min(impact_score, 1.0)
        except Exception as e:
            self.logger.error(f"학습 영향도 계산 중 오류: {e}")
            return 0.5

    async def _generate_adaptation_suggestions(
        self, reasoning_session: ReasoningSession
    ) -> List[str]:
        """적응 제안 생성"""
        try:
            suggestions = []

            # 신뢰도 기반 제안
            if reasoning_session.confidence_score < 0.6:
                suggestions.append("추론 방식 다양화")
                suggestions.append("정보 수집 강화")

            # 적응도 기반 제안
            if reasoning_session.adaptation_score < 0.5:
                suggestions.append("상황 인식 능력 향상")
                suggestions.append("유연한 사고 방식 개발")

            # 효율성 기반 제안
            if reasoning_session.efficiency_score < 0.7:
                suggestions.append("추론 과정 최적화")
                suggestions.append("불필요한 단계 제거")

            return suggestions
        except Exception as e:
            self.logger.error(f"적응 제안 생성 중 오류: {e}")
            return ["기본 적응 제안"]

    def _create_fallback_feedback(
        self, reasoning_session: ReasoningSession
    ) -> ReasoningFeedback:
        """폴백 피드백 생성"""
        return ReasoningFeedback(
            feedback_id=f"fallback_{int(time.time())}",
            session_id=reasoning_session.session_id,
            feedback_type="fallback",
            feedback_content="기본 피드백 내용",
            feedback_score=0.5,
            learning_impact=0.5,
            adaptation_suggestions=["기본 적응 제안"],
        )
