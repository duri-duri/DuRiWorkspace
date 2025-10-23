#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 모니터링 시스템 (Learning Monitoring System)

학습 과정을 실시간으로 모니터링하고 추적하는 시스템입니다.
- 학습 진행 상황 모니터링
- 학습 성과 추적
- 학습 패턴 분석
- 학습 최적화 추천
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MonitoringStatus(Enum):
    """모니터링 상태"""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class LearningPhase(Enum):
    """학습 단계"""

    INITIALIZATION = "initialization"
    EXPLORATION = "exploration"
    LEARNING = "learning"
    INTEGRATION = "integration"
    EVALUATION = "evaluation"
    COMPLETION = "completion"


@dataclass
class LearningEvent:
    """학습 이벤트"""

    event_id: str
    event_type: str
    timestamp: datetime
    session_id: str
    phase: LearningPhase
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningMetrics:
    """학습 메트릭"""

    metrics_id: str
    session_id: str
    timestamp: datetime
    progress_score: float  # 0.0-1.0
    efficiency_score: float  # 0.0-1.0
    quality_score: float  # 0.0-1.0
    engagement_score: float  # 0.0-1.0
    overall_score: float  # 0.0-1.0
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LearningPattern:
    """학습 패턴"""

    pattern_id: str
    pattern_type: str
    description: str
    frequency: int
    effectiveness: float  # 0.0-1.0
    context_conditions: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class MonitoringSession:
    """모니터링 세션"""

    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status: MonitoringStatus = MonitoringStatus.ACTIVE
    events: List[LearningEvent] = field(default_factory=list)
    metrics: List[LearningMetrics] = field(default_factory=list)
    patterns: List[LearningPattern] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class LearningMonitoringSystem:
    """학습 모니터링 시스템"""

    def __init__(self):
        """초기화"""
        self.monitoring_sessions: Dict[str, MonitoringSession] = {}
        self.learning_events: List[LearningEvent] = []
        self.learning_metrics: List[LearningMetrics] = []
        self.learning_patterns: List[LearningPattern] = []

        # 성능 메트릭
        self.performance_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "total_events": 0,
            "total_metrics": 0,
            "average_progress": 0.0,
            "average_efficiency": 0.0,
        }

        logger.info("학습 모니터링 시스템 초기화 완료")

    async def start_monitoring_session(self, session_id: str) -> str:
        """모니터링 세션 시작"""
        if session_id in self.monitoring_sessions:
            logger.warning(f"세션이 이미 존재합니다: {session_id}")
            return session_id

        monitoring_session = MonitoringSession(session_id=session_id, start_time=datetime.now())

        self.monitoring_sessions[session_id] = monitoring_session
        self.performance_metrics["total_sessions"] += 1
        self.performance_metrics["active_sessions"] += 1

        logger.info(f"모니터링 세션 시작: {session_id}")
        return session_id

    async def stop_monitoring_session(self, session_id: str) -> bool:
        """모니터링 세션 중지"""
        if session_id not in self.monitoring_sessions:
            logger.error(f"세션을 찾을 수 없음: {session_id}")
            return False

        session = self.monitoring_sessions[session_id]
        session.end_time = datetime.now()
        session.status = MonitoringStatus.STOPPED

        self.performance_metrics["active_sessions"] -= 1

        logger.info(f"모니터링 세션 중지: {session_id}")
        return True

    async def record_learning_event(
        self,
        session_id: str,
        event_type: str,
        phase: LearningPhase,
        data: Dict[str, Any] = None,
    ) -> str:
        """학습 이벤트 기록"""
        if session_id not in self.monitoring_sessions:
            logger.error(f"세션을 찾을 수 없음: {session_id}")
            return ""

        event_id = f"event_{int(time.time())}_{event_type}"

        learning_event = LearningEvent(
            event_id=event_id,
            event_type=event_type,
            timestamp=datetime.now(),
            session_id=session_id,
            phase=phase,
            data=data or {},
            metadata={"recorded_by": "learning_monitor"},
        )

        # 세션에 이벤트 추가
        session = self.monitoring_sessions[session_id]
        session.events.append(learning_event)

        # 전체 이벤트 목록에 추가
        self.learning_events.append(learning_event)
        self.performance_metrics["total_events"] += 1

        logger.info(f"학습 이벤트 기록: {event_id} ({event_type})")
        return event_id

    async def record_learning_metrics(
        self,
        session_id: str,
        progress_score: float = 0.0,
        efficiency_score: float = 0.0,
        quality_score: float = 0.0,
        engagement_score: float = 0.0,
    ) -> str:
        """학습 메트릭 기록"""
        if session_id not in self.monitoring_sessions:
            logger.error(f"세션을 찾을 수 없음: {session_id}")
            return ""

        metrics_id = f"metrics_{int(time.time())}_{session_id}"

        # 전체 점수 계산
        overall_score = (progress_score + efficiency_score + quality_score + engagement_score) / 4.0

        learning_metrics = LearningMetrics(
            metrics_id=metrics_id,
            session_id=session_id,
            timestamp=datetime.now(),
            progress_score=progress_score,
            efficiency_score=efficiency_score,
            quality_score=quality_score,
            engagement_score=engagement_score,
            overall_score=overall_score,
        )

        # 세션에 메트릭 추가
        session = self.monitoring_sessions[session_id]
        session.metrics.append(learning_metrics)

        # 전체 메트릭 목록에 추가
        self.learning_metrics.append(learning_metrics)
        self.performance_metrics["total_metrics"] += 1

        # 성능 메트릭 업데이트
        await self._update_performance_metrics(learning_metrics)

        logger.info(f"학습 메트릭 기록: {metrics_id} (전체 점수: {overall_score:.2f})")
        return metrics_id

    async def analyze_learning_patterns(self, session_id: str = None) -> List[LearningPattern]:
        """학습 패턴 분석"""
        patterns = []

        # 분석할 이벤트들 선택
        if session_id:
            events = [e for e in self.learning_events if e.session_id == session_id]
        else:
            events = self.learning_events

        if not events:
            return patterns

        # 이벤트 타입별 패턴 분석
        event_types = defaultdict(list)
        for event in events:
            event_types[event.event_type].append(event)

        # 패턴 생성
        for event_type, type_events in event_types.items():
            pattern = await self._create_learning_pattern(event_type, type_events)
            if pattern:
                patterns.append(pattern)

        # 세션에 패턴 추가
        if session_id and session_id in self.monitoring_sessions:
            session = self.monitoring_sessions[session_id]
            session.patterns.extend(patterns)

        # 전체 패턴 목록에 추가
        self.learning_patterns.extend(patterns)

        logger.info(f"학습 패턴 분석 완료: {len(patterns)}개 패턴 발견")
        return patterns

    async def _create_learning_pattern(self, event_type: str, events: List[LearningEvent]) -> Optional[LearningPattern]:
        """학습 패턴 생성"""
        if not events:
            return None

        pattern_id = f"pattern_{int(time.time())}_{event_type}"

        # 패턴 분석
        frequency = len(events)
        effectiveness = await self._calculate_pattern_effectiveness(events)

        # 컨텍스트 조건 추출
        context_conditions = []
        for event in events:
            if "context" in event.data:
                context_conditions.append(event.data["context"])

        pattern = LearningPattern(
            pattern_id=pattern_id,
            pattern_type=event_type,
            description=f"{event_type} 이벤트 패턴 (빈도: {frequency})",
            frequency=frequency,
            effectiveness=effectiveness,
            context_conditions=list(set(context_conditions)),  # 중복 제거
        )

        return pattern

    async def _calculate_pattern_effectiveness(self, events: List[LearningEvent]) -> float:
        """패턴 효과성 계산"""
        if not events:
            return 0.0

        # 이벤트의 시간 간격 분석
        timestamps = [event.timestamp for event in events]
        timestamps.sort()

        # 시간 간격의 일관성 계산
        intervals = []
        for i in range(1, len(timestamps)):
            interval = (timestamps[i] - timestamps[i - 1]).total_seconds()
            intervals.append(interval)

        if not intervals:
            return 0.5  # 기본값

        # 간격의 표준편차가 작을수록 효과적
        mean_interval = sum(intervals) / len(intervals)
        variance = sum((interval - mean_interval) ** 2 for interval in intervals) / len(intervals)
        std_dev = variance**0.5

        # 효과성 점수 계산 (간격이 일정할수록 높은 점수)
        effectiveness = max(0.0, 1.0 - (std_dev / max(mean_interval, 1.0)))

        return effectiveness

    async def _update_performance_metrics(self, learning_metrics: LearningMetrics):
        """성능 메트릭 업데이트"""
        # 평균 점수 업데이트
        all_progress_scores = [m.progress_score for m in self.learning_metrics]
        all_efficiency_scores = [m.efficiency_score for m in self.learning_metrics]

        if all_progress_scores:
            self.performance_metrics["average_progress"] = sum(all_progress_scores) / len(all_progress_scores)

        if all_efficiency_scores:
            self.performance_metrics["average_efficiency"] = sum(all_efficiency_scores) / len(all_efficiency_scores)

    async def get_monitoring_status(self, session_id: str = None) -> Dict[str, Any]:
        """모니터링 상태 조회"""
        if session_id:
            # 특정 세션 상태 조회
            if session_id in self.monitoring_sessions:
                session = self.monitoring_sessions[session_id]
                return {
                    "session_id": session.session_id,
                    "status": session.status.value,
                    "start_time": session.start_time.isoformat(),
                    "end_time": (session.end_time.isoformat() if session.end_time else None),
                    "events_count": len(session.events),
                    "metrics_count": len(session.metrics),
                    "patterns_count": len(session.patterns),
                }
            else:
                return {"error": "세션을 찾을 수 없음"}

        # 전체 상태 반환
        return {
            "total_sessions": len(self.monitoring_sessions),
            "active_sessions": len(
                [s for s in self.monitoring_sessions.values() if s.status == MonitoringStatus.ACTIVE]
            ),
            "total_events": len(self.learning_events),
            "total_metrics": len(self.learning_metrics),
            "total_patterns": len(self.learning_patterns),
            "performance_metrics": self.performance_metrics,
            "recent_sessions": [
                {
                    "session_id": s.session_id,
                    "status": s.status.value,
                    "events_count": len(s.events),
                    "metrics_count": len(s.metrics),
                    "start_time": s.start_time.isoformat(),
                }
                for s in list(self.monitoring_sessions.values())[-5:]  # 최근 5개 세션
            ],
        }

    async def get_learning_report(self, session_id: str = None) -> Dict[str, Any]:
        """학습 리포트 생성"""
        if session_id:
            # 특정 세션 리포트
            if session_id not in self.monitoring_sessions:
                return {"error": "세션을 찾을 수 없음"}

            session = self.monitoring_sessions[session_id]
            return await self._generate_session_report(session)
        else:
            # 전체 리포트
            return await self._generate_overall_report()

    async def _generate_session_report(self, session: MonitoringSession) -> Dict[str, Any]:
        """세션 리포트 생성"""
        if not session.metrics:
            return {"error": "메트릭 데이터가 없습니다"}

        # 메트릭 분석
        progress_scores = [m.progress_score for m in session.metrics]
        efficiency_scores = [m.efficiency_score for m in session.metrics]
        quality_scores = [m.quality_score for m in session.metrics]
        engagement_scores = [m.engagement_score for m in session.metrics]
        overall_scores = [m.overall_score for m in session.metrics]

        # 평균 점수 계산
        avg_progress = sum(progress_scores) / len(progress_scores)
        avg_efficiency = sum(efficiency_scores) / len(efficiency_scores)
        avg_quality = sum(quality_scores) / len(quality_scores)
        avg_engagement = sum(engagement_scores) / len(engagement_scores)
        avg_overall = sum(overall_scores) / len(overall_scores)

        # 이벤트 분석
        event_types = defaultdict(int)
        for event in session.events:
            event_types[event.event_type] += 1

        return {
            "session_id": session.session_id,
            "duration": ((session.end_time - session.start_time).total_seconds() if session.end_time else None),
            "metrics_summary": {
                "average_progress": avg_progress,
                "average_efficiency": avg_efficiency,
                "average_quality": avg_quality,
                "average_engagement": avg_engagement,
                "average_overall": avg_overall,
            },
            "events_summary": {
                "total_events": len(session.events),
                "event_types": dict(event_types),
            },
            "patterns_summary": {
                "total_patterns": len(session.patterns),
                "pattern_types": [p.pattern_type for p in session.patterns],
            },
        }

    async def _generate_overall_report(self) -> Dict[str, Any]:
        """전체 리포트 생성"""
        if not self.learning_metrics:
            return {"error": "메트릭 데이터가 없습니다"}

        # 전체 메트릭 분석
        recent_metrics = self.learning_metrics[-50:]  # 최근 50개 메트릭

        avg_progress = sum(m.progress_score for m in recent_metrics) / len(recent_metrics)
        avg_efficiency = sum(m.efficiency_score for m in recent_metrics) / len(recent_metrics)
        avg_quality = sum(m.quality_score for m in recent_metrics) / len(recent_metrics)
        avg_engagement = sum(m.engagement_score for m in recent_metrics) / len(recent_metrics)
        avg_overall = sum(m.overall_score for m in recent_metrics) / len(recent_metrics)

        # 이벤트 분석
        event_types = defaultdict(int)
        for event in self.learning_events[-100:]:  # 최근 100개 이벤트
            event_types[event.event_type] += 1

        return {
            "overall_summary": {
                "total_sessions": len(self.monitoring_sessions),
                "total_events": len(self.learning_events),
                "total_metrics": len(self.learning_metrics),
                "total_patterns": len(self.learning_patterns),
            },
            "performance_summary": {
                "average_progress": avg_progress,
                "average_efficiency": avg_efficiency,
                "average_quality": avg_quality,
                "average_engagement": avg_engagement,
                "average_overall": avg_overall,
            },
            "events_summary": {
                "total_events": len(self.learning_events),
                "event_types": dict(event_types),
            },
            "recent_activity": [
                {
                    "session_id": m.session_id,
                    "overall_score": m.overall_score,
                    "timestamp": m.timestamp.isoformat(),
                }
                for m in recent_metrics[-10:]  # 최근 10개 메트릭
            ],
        }

    async def get_optimization_recommendations(self, session_id: str = None) -> List[Dict[str, Any]]:
        """최적화 추천 생성"""
        recommendations = []

        # 분석할 메트릭 선택
        if session_id:
            metrics = [m for m in self.learning_metrics if m.session_id == session_id]
        else:
            metrics = self.learning_metrics[-20:]  # 최근 20개 메트릭

        if not metrics:
            return [{"error": "분석할 메트릭이 없습니다"}]

        # 성과 기반 추천
        avg_overall = sum(m.overall_score for m in metrics) / len(metrics)

        if avg_overall < 0.6:
            recommendations.append(
                {
                    "type": "performance_improvement",
                    "priority": "high",
                    "description": "전체적인 학습 성과 개선이 필요합니다.",
                    "suggestion": "학습 전략을 재검토하고 최적화하세요.",
                }
            )

        # 개별 점수 기반 추천
        avg_progress = sum(m.progress_score for m in metrics) / len(metrics)
        avg_efficiency = sum(m.efficiency_score for m in metrics) / len(metrics)
        avg_quality = sum(m.quality_score for m in metrics) / len(metrics)
        avg_engagement = sum(m.engagement_score for m in metrics) / len(metrics)

        if avg_progress < 0.6:
            recommendations.append(
                {
                    "type": "progress_improvement",
                    "priority": "medium",
                    "description": "학습 진행도 개선이 필요합니다.",
                    "suggestion": "학습 목표를 더 구체적으로 설정하고 단계별 접근을 시도하세요.",
                }
            )

        if avg_efficiency < 0.6:
            recommendations.append(
                {
                    "type": "efficiency_improvement",
                    "priority": "medium",
                    "description": "학습 효율성 개선이 필요합니다.",
                    "suggestion": "학습 방법을 최적화하고 시간 관리를 개선하세요.",
                }
            )

        if avg_quality < 0.6:
            recommendations.append(
                {
                    "type": "quality_improvement",
                    "priority": "medium",
                    "description": "학습 품질 개선이 필요합니다.",
                    "suggestion": "학습 내용의 깊이를 높이고 이해도를 향상시키세요.",
                }
            )

        if avg_engagement < 0.6:
            recommendations.append(
                {
                    "type": "engagement_improvement",
                    "priority": "medium",
                    "description": "학습 참여도 개선이 필요합니다.",
                    "suggestion": "학습 동기를 높이고 흥미로운 학습 방법을 시도하세요.",
                }
            )

        return recommendations
