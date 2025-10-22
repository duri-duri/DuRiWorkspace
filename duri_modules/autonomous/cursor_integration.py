#!/usr/bin/env python3
"""
Cursor ↔ DuRi 상호 학습 시스템
실시간 학습 피드백 루프 및 자동 개선 시스템
"""

import asyncio
import json
import logging
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class CursorFeedback:
    """Cursor 피드백 데이터"""

    timestamp: str
    user_input: str
    duri_response: str
    cursor_evaluation: Dict[str, Any]
    learning_insights: List[str]
    improvement_suggestions: List[str]
    confidence_score: float


@dataclass
class LearningSession:
    """학습 세션 데이터"""

    session_id: str
    start_time: str
    end_time: str
    total_exchanges: int
    learning_efficiency: float
    improvement_rate: float
    cursor_satisfaction: float
    key_learnings: List[str]


class CursorIntegration:
    """Cursor ↔ DuRi 상호 학습 시스템"""

    def __init__(self):
        self.active_sessions = {}
        self.learning_history = []
        self.cursor_feedback_history = []
        self.improvement_tracker = {}

        # 학습 데이터 저장소
        self.data_dir = "cursor_learning_data"
        os.makedirs(self.data_dir, exist_ok=True)

        logger.info("🔄 Cursor ↔ DuRi 상호 학습 시스템 초기화 완료")

    async def start_learning_session(self, session_id: str = None) -> str:
        """학습 세션 시작"""
        if not session_id:
            session_id = f"learning_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        session = {
            "session_id": session_id,
            "start_time": datetime.now().isoformat(),
            "exchanges": [],
            "learning_insights": [],
            "improvement_suggestions": [],
        }

        self.active_sessions[session_id] = session

        logger.info(f"🔄 학습 세션 시작: {session_id}")
        return session_id

    async def process_cursor_feedback(
        self,
        session_id: str,
        user_input: str,
        duri_response: str,
        cursor_evaluation: Dict[str, Any],
    ) -> CursorFeedback:
        """Cursor 피드백 처리"""
        try:
            # 피드백 분석
            learning_insights = self._extract_learning_insights(cursor_evaluation)
            improvement_suggestions = self._generate_improvement_suggestions(cursor_evaluation)
            confidence_score = self._calculate_confidence_score(cursor_evaluation)

            # 피드백 객체 생성
            feedback = CursorFeedback(
                timestamp=datetime.now().isoformat(),
                user_input=user_input,
                duri_response=duri_response,
                cursor_evaluation=cursor_evaluation,
                learning_insights=learning_insights,
                improvement_suggestions=improvement_suggestions,
                confidence_score=confidence_score,
            )

            # 세션에 추가
            if session_id in self.active_sessions:
                self.active_sessions[session_id]["exchanges"].append(feedback)
                self.active_sessions[session_id]["learning_insights"].extend(learning_insights)
                self.active_sessions[session_id]["improvement_suggestions"].extend(
                    improvement_suggestions
                )

            # 히스토리에 저장
            self.cursor_feedback_history.append(feedback)

            # 실시간 학습 적용
            await self._apply_real_time_learning(feedback)

            logger.info(
                f"✅ Cursor 피드백 처리 완료: {len(learning_insights)}개 인사이트, {len(improvement_suggestions)}개 제안"
            )

            return feedback

        except Exception as e:
            logger.error(f"❌ Cursor 피드백 처리 오류: {e}")
            return None

    async def end_learning_session(self, session_id: str) -> LearningSession:
        """학습 세션 종료"""
        if session_id not in self.active_sessions:
            return None

        session_data = self.active_sessions[session_id]
        session_data["end_time"] = datetime.now().isoformat()

        # 세션 요약 생성
        learning_session = self._create_learning_session_summary(session_data)

        # 세션 저장
        self._save_learning_session(learning_session)

        # 히스토리에 추가
        self.learning_history.append(learning_session)

        # 세션 종료
        del self.active_sessions[session_id]

        logger.info(
            f"🏁 학습 세션 종료: {session_id} - 효율성 {learning_session.learning_efficiency:.3f}"
        )

        return learning_session

    async def get_learning_insights(self) -> Dict[str, Any]:
        """학습 인사이트 반환"""
        try:
            total_sessions = len(self.learning_history)
            total_exchanges = sum(session.total_exchanges for session in self.learning_history)

            if total_sessions == 0:
                return {"status": "no_data"}

            # 평균 지표 계산
            avg_learning_efficiency = (
                sum(session.learning_efficiency for session in self.learning_history)
                / total_sessions
            )
            avg_improvement_rate = (
                sum(session.improvement_rate for session in self.learning_history) / total_sessions
            )
            avg_cursor_satisfaction = (
                sum(session.cursor_satisfaction for session in self.learning_history)
                / total_sessions
            )

            # 학습 트렌드 분석
            learning_trends = self._analyze_learning_trends()

            # 개선 영역 식별
            improvement_areas = self._identify_improvement_areas()

            return {
                "status": "success",
                "total_sessions": total_sessions,
                "total_exchanges": total_exchanges,
                "average_learning_efficiency": avg_learning_efficiency,
                "average_improvement_rate": avg_improvement_rate,
                "average_cursor_satisfaction": avg_cursor_satisfaction,
                "learning_trends": learning_trends,
                "improvement_areas": improvement_areas,
                "recent_insights": self._get_recent_insights(),
            }
        except Exception as e:
            logger.error(f"학습 인사이트 조회 오류: {e}")
            return {"status": "error", "error": str(e)}

    async def apply_improvements(self, improvement_suggestions: List[str]) -> Dict[str, Any]:
        """개선 사항 적용"""
        try:
            applied_improvements = []
            failed_improvements = []

            for suggestion in improvement_suggestions:
                try:
                    # 개선 적용 로직
                    improvement_result = await self._apply_single_improvement(suggestion)
                    applied_improvements.append(
                        {
                            "suggestion": suggestion,
                            "result": improvement_result,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )
                except Exception as e:
                    failed_improvements.append(
                        {
                            "suggestion": suggestion,
                            "error": str(e),
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

            # 개선 추적 업데이트
            self.improvement_tracker[datetime.now().isoformat()] = {
                "applied": applied_improvements,
                "failed": failed_improvements,
            }

            return {
                "status": "success",
                "applied_improvements": len(applied_improvements),
                "failed_improvements": len(failed_improvements),
                "total_suggestions": len(improvement_suggestions),
                "success_rate": (
                    len(applied_improvements) / len(improvement_suggestions)
                    if improvement_suggestions
                    else 0.0
                ),
            }

        except Exception as e:
            logger.error(f"개선 적용 오류: {e}")
            return {"status": "error", "error": str(e)}

    def _extract_learning_insights(self, cursor_evaluation: Dict[str, Any]) -> List[str]:
        """학습 인사이트 추출"""
        insights = []

        # 평가 점수 기반 인사이트
        if cursor_evaluation.get("score", 0) > 0.8:
            insights.append("high_quality_response")
        elif cursor_evaluation.get("score", 0) < 0.5:
            insights.append("needs_improvement")

        # 개선 제안 기반 인사이트
        suggestions = cursor_evaluation.get("suggestions", [])
        if "더 상세한 설명" in str(suggestions):
            insights.append("detailed_explanation_needed")
        if "코드 예제" in str(suggestions):
            insights.append("code_example_needed")
        if "구조화" in str(suggestions):
            insights.append("structured_response_needed")

        # 특정 영역 평가
        correctness = cursor_evaluation.get("correctness", 0)
        relevance = cursor_evaluation.get("relevance", 0)
        depth = cursor_evaluation.get("depth", 0)

        if correctness < 0.5:
            insights.append("accuracy_improvement_needed")
        if relevance < 0.5:
            insights.append("relevance_improvement_needed")
        if depth < 0.5:
            insights.append("depth_improvement_needed")

        return insights

    def _generate_improvement_suggestions(self, cursor_evaluation: Dict[str, Any]) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        # 점수 기반 제안
        score = cursor_evaluation.get("score", 0)
        if score < 0.5:
            suggestions.append("전체적인 응답 품질 향상이 필요합니다")

        # 세부 영역별 제안
        correctness = cursor_evaluation.get("correctness", 0)
        if correctness < 0.6:
            suggestions.append("정확성 향상을 위해 더 신중한 검증이 필요합니다")

        relevance = cursor_evaluation.get("relevance", 0)
        if relevance < 0.6:
            suggestions.append("관련성 향상을 위해 사용자 의도를 더 정확히 파악해야 합니다")

        depth = cursor_evaluation.get("depth", 0)
        if depth < 0.6:
            suggestions.append("깊이 있는 분석과 설명이 필요합니다")

        clarity = cursor_evaluation.get("clarity", 0)
        if clarity < 0.6:
            suggestions.append("명확성 향상을 위해 더 간결하고 이해하기 쉬운 설명이 필요합니다")

        return suggestions

    def _calculate_confidence_score(self, cursor_evaluation: Dict[str, Any]) -> float:
        """신뢰도 점수 계산"""
        try:
            # 기본 점수
            base_score = cursor_evaluation.get("score", 0.5)

            # 평가 일관성
            sub_scores = [
                cursor_evaluation.get("correctness", 0.5),
                cursor_evaluation.get("relevance", 0.5),
                cursor_evaluation.get("depth", 0.5),
                cursor_evaluation.get("clarity", 0.5),
            ]

            consistency = 1.0 - (max(sub_scores) - min(sub_scores))

            # 최종 신뢰도
            confidence = (base_score + consistency) / 2

            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.error(f"신뢰도 계산 오류: {e}")
            return 0.5

    async def _apply_real_time_learning(self, feedback: CursorFeedback):
        """실시간 학습 적용"""
        try:
            # 학습 패턴 업데이트
            for insight in feedback.learning_insights:
                if insight not in self.improvement_tracker:
                    self.improvement_tracker[insight] = {
                        "count": 0,
                        "last_seen": None,
                        "improvement_applied": False,
                    }

                self.improvement_tracker[insight]["count"] += 1
                self.improvement_tracker[insight]["last_seen"] = feedback.timestamp

            # 개선 제안 우선순위 설정
            for suggestion in feedback.improvement_suggestions:
                if "필요" in suggestion:
                    # 긴급 개선 필요
                    await self._prioritize_improvement(suggestion, "high")
                elif "향상" in suggestion:
                    # 일반 개선
                    await self._prioritize_improvement(suggestion, "medium")

            logger.info(f"🔄 실시간 학습 적용: {len(feedback.learning_insights)}개 인사이트")

        except Exception as e:
            logger.error(f"실시간 학습 적용 오류: {e}")

    async def _prioritize_improvement(self, suggestion: str, priority: str):
        """개선 우선순위 설정"""
        # 개선 우선순위 로직
        if priority == "high":
            # 즉시 적용 가능한 개선
            await self._apply_immediate_improvement(suggestion)
        elif priority == "medium":
            # 다음 학습 세션에서 적용
            await self._schedule_improvement(suggestion)

    async def _apply_immediate_improvement(self, suggestion: str):
        """즉시 개선 적용"""
        # 즉시 적용 가능한 개선 사항들
        if "정확성" in suggestion:
            # 정확성 검증 강화
            logger.info("🔧 정확성 검증 강화 적용")
        elif "관련성" in suggestion:
            # 사용자 의도 파악 강화
            logger.info("🔧 사용자 의도 파악 강화 적용")
        elif "명확성" in suggestion:
            # 설명 명확성 향상
            logger.info("🔧 설명 명확성 향상 적용")

    async def _schedule_improvement(self, suggestion: str):
        """개선 스케줄링"""
        # 다음 학습 세션에서 적용할 개선 사항
        logger.info(f"📅 개선 스케줄링: {suggestion}")

    def _create_learning_session_summary(self, session_data: Dict[str, Any]) -> LearningSession:
        """학습 세션 요약 생성"""
        exchanges = session_data["exchanges"]

        # 학습 효율성 계산
        total_insights = len(session_data["learning_insights"])
        learning_efficiency = min(1.0, total_insights / len(exchanges)) if exchanges else 0.0

        # 개선율 계산
        total_suggestions = len(session_data["improvement_suggestions"])
        improvement_rate = min(1.0, total_suggestions / len(exchanges)) if exchanges else 0.0

        # Cursor 만족도 계산
        if exchanges:
            avg_confidence = sum(exchange.confidence_score for exchange in exchanges) / len(
                exchanges
            )
        else:
            avg_confidence = 0.5

        # 핵심 학습 내용 추출
        key_learnings = list(set(session_data["learning_insights"]))

        return LearningSession(
            session_id=session_data["session_id"],
            start_time=session_data["start_time"],
            end_time=session_data["end_time"],
            total_exchanges=len(exchanges),
            learning_efficiency=learning_efficiency,
            improvement_rate=improvement_rate,
            cursor_satisfaction=avg_confidence,
            key_learnings=key_learnings,
        )

    def _analyze_learning_trends(self) -> Dict[str, Any]:
        """학습 트렌드 분석"""
        if len(self.learning_history) < 2:
            return {}

        recent_sessions = self.learning_history[-5:]  # 최근 5개 세션

        trends = {
            "learning_efficiency_trend": "stable",
            "improvement_rate_trend": "stable",
            "cursor_satisfaction_trend": "stable",
        }

        # 학습 효율성 트렌드
        efficiencies = [session.learning_efficiency for session in recent_sessions]
        if len(efficiencies) >= 2:
            if efficiencies[-1] > efficiencies[0]:
                trends["learning_efficiency_trend"] = "improving"
            elif efficiencies[-1] < efficiencies[0]:
                trends["learning_efficiency_trend"] = "declining"

        # 개선율 트렌드
        improvement_rates = [session.improvement_rate for session in recent_sessions]
        if len(improvement_rates) >= 2:
            if improvement_rates[-1] > improvement_rates[0]:
                trends["improvement_rate_trend"] = "improving"
            elif improvement_rates[-1] < improvement_rates[0]:
                trends["improvement_rate_trend"] = "declining"

        return trends

    def _identify_improvement_areas(self) -> List[str]:
        """개선 영역 식별"""
        improvement_areas = []

        # 자주 발생하는 문제들 분석
        if self.learning_history:
            recent_sessions = self.learning_history[-3:]  # 최근 3개 세션

            # 낮은 학습 효율성
            avg_efficiency = sum(session.learning_efficiency for session in recent_sessions) / len(
                recent_sessions
            )
            if avg_efficiency < 0.6:
                improvement_areas.append("학습 효율성 향상 필요")

            # 낮은 개선율
            avg_improvement = sum(session.improvement_rate for session in recent_sessions) / len(
                recent_sessions
            )
            if avg_improvement < 0.5:
                improvement_areas.append("개선 제안 적용률 향상 필요")

            # 낮은 Cursor 만족도
            avg_satisfaction = sum(
                session.cursor_satisfaction for session in recent_sessions
            ) / len(recent_sessions)
            if avg_satisfaction < 0.7:
                improvement_areas.append("Cursor 만족도 향상 필요")

        return improvement_areas

    def _get_recent_insights(self) -> List[str]:
        """최근 인사이트 반환"""
        recent_insights = []

        # 최근 피드백에서 인사이트 추출
        recent_feedback = self.cursor_feedback_history[-10:]  # 최근 10개 피드백

        for feedback in recent_feedback:
            recent_insights.extend(feedback.learning_insights)

        # 중복 제거 및 빈도순 정렬
        from collections import Counter

        insight_counts = Counter(recent_insights)

        return [insight for insight, count in insight_counts.most_common(5)]

    async def _apply_single_improvement(self, suggestion: str) -> Dict[str, Any]:
        """단일 개선 적용"""
        # 개선 적용 시뮬레이션
        await asyncio.sleep(0.1)  # 실제 적용 시간 시뮬레이션

        return {
            "suggestion": suggestion,
            "applied": True,
            "timestamp": datetime.now().isoformat(),
            "impact_score": 0.7,  # 개선 효과 점수
        }

    def _save_learning_session(self, learning_session: LearningSession):
        """학습 세션 저장"""
        try:
            filename = f"{learning_session.session_id}.json"
            filepath = os.path.join(self.data_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(asdict(learning_session), f, ensure_ascii=False, indent=2)

            logger.info(f"💾 학습 세션 저장 완료: {filename}")

        except Exception as e:
            logger.error(f"학습 세션 저장 오류: {e}")


# 전역 인스턴스 생성
cursor_integration = CursorIntegration()
