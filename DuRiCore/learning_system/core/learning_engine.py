#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 엔진 (Learning Engine)

학습 시스템의 핵심 엔진으로, 모든 학습 활동을 조율하고 관리합니다.
- 학습 세션 관리
- 학습 프로세스 조율
- 학습 결과 통합
- 학습 성과 평가
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningSessionStatus(Enum):
    """학습 세션 상태"""

    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LearningProcessType(Enum):
    """학습 프로세스 유형"""

    CONTINUOUS = "continuous"
    ADAPTIVE = "adaptive"
    META = "meta"
    SELF_DIRECTED = "self_directed"
    COGNITIVE_META = "cognitive_meta"


@dataclass
class LearningSession:
    """학습 세션"""

    session_id: str
    process_type: LearningProcessType
    status: LearningSessionStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    context: Dict[str, Any] = field(default_factory=dict)
    results: Dict[str, Any] = field(default_factory=dict)
    performance_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningProcess:
    """학습 프로세스"""

    process_id: str
    process_type: LearningProcessType
    session_id: str
    status: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    output_data: Dict[str, Any] = field(default_factory=dict)
    performance_score: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class LearningResult:
    """학습 결과"""

    result_id: str
    session_id: str
    process_type: LearningProcessType
    overall_score: float = 0.0
    efficiency_score: float = 0.0
    quality_score: float = 0.0
    insights_discovered: List[str] = field(default_factory=list)
    knowledge_gained: List[str] = field(default_factory=list)
    improvements_suggested: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class LearningEngine:
    """학습 엔진"""

    def __init__(self):
        """초기화"""
        self.active_sessions: Dict[str, LearningSession] = {}
        self.completed_sessions: List[LearningSession] = []
        self.learning_processes: Dict[str, LearningProcess] = {}
        self.learning_results: List[LearningResult] = []

        # 성능 메트릭
        self.performance_metrics = {
            "total_sessions": 0,
            "active_sessions": 0,
            "completed_sessions": 0,
            "average_session_duration": 0.0,
            "average_performance_score": 0.0,
            "success_rate": 0.0,
        }

        logger.info("학습 엔진 초기화 완료")

    async def create_learning_session(
        self, process_type: LearningProcessType, context: Dict[str, Any] = None
    ) -> str:
        """학습 세션 생성"""
        session_id = f"session_{int(time.time())}_{process_type.value}"

        session = LearningSession(
            session_id=session_id,
            process_type=process_type,
            status=LearningSessionStatus.PENDING,
            start_time=datetime.now(),
            context=context or {},
        )

        self.active_sessions[session_id] = session
        self.performance_metrics["total_sessions"] += 1
        self.performance_metrics["active_sessions"] += 1

        logger.info(f"학습 세션 생성: {session_id} ({process_type.value})")
        return session_id

    async def start_learning_session(self, session_id: str) -> bool:
        """학습 세션 시작"""
        if session_id not in self.active_sessions:
            logger.error(f"세션을 찾을 수 없음: {session_id}")
            return False

        session = self.active_sessions[session_id]
        session.status = LearningSessionStatus.ACTIVE
        session.start_time = datetime.now()

        logger.info(f"학습 세션 시작: {session_id}")
        return True

    async def complete_learning_session(
        self, session_id: str, results: Dict[str, Any] = None
    ) -> bool:
        """학습 세션 완료"""
        if session_id not in self.active_sessions:
            logger.error(f"세션을 찾을 수 없음: {session_id}")
            return False

        session = self.active_sessions[session_id]
        session.status = LearningSessionStatus.COMPLETED
        session.end_time = datetime.now()
        session.duration = session.end_time - session.start_time
        session.results = results or {}

        # 성능 메트릭 계산
        await self._calculate_session_metrics(session)

        # 완료된 세션 이동
        self.completed_sessions.append(session)
        del self.active_sessions[session_id]

        self.performance_metrics["active_sessions"] -= 1
        self.performance_metrics["completed_sessions"] += 1

        logger.info(f"학습 세션 완료: {session_id} (지속시간: {session.duration})")
        return True

    async def create_learning_process(
        self,
        session_id: str,
        process_type: LearningProcessType,
        input_data: Dict[str, Any] = None,
    ) -> str:
        """학습 프로세스 생성"""
        process_id = f"process_{int(time.time())}_{process_type.value}"

        process = LearningProcess(
            process_id=process_id,
            process_type=process_type,
            session_id=session_id,
            status="pending",
            start_time=datetime.now(),
            input_data=input_data or {},
        )

        self.learning_processes[process_id] = process

        logger.info(f"학습 프로세스 생성: {process_id} ({process_type.value})")
        return process_id

    async def execute_learning_process(self, process_id: str) -> Dict[str, Any]:
        """학습 프로세스 실행"""
        if process_id not in self.learning_processes:
            logger.error(f"프로세스를 찾을 수 없음: {process_id}")
            return {}

        process = self.learning_processes[process_id]
        process.status = "active"
        process.start_time = datetime.now()

        try:
            # 프로세스 타입에 따른 실행
            output_data = await self._execute_process_by_type(process)

            process.status = "completed"
            process.end_time = datetime.now()
            process.duration = (process.end_time - process.start_time).total_seconds()
            process.output_data = output_data
            process.performance_score = await self._calculate_process_score(process)

            logger.info(f"학습 프로세스 완료: {process_id} (점수: {process.performance_score:.2f})")
            return output_data

        except Exception as e:
            process.status = "failed"
            process.end_time = datetime.now()
            logger.error(f"학습 프로세스 실패: {process_id} - {e}")
            return {}

    async def _execute_process_by_type(self, process: LearningProcess) -> Dict[str, Any]:
        """프로세스 타입에 따른 실행"""
        if process.process_type == LearningProcessType.CONTINUOUS:
            return await self._execute_continuous_learning(process)
        elif process.process_type == LearningProcessType.ADAPTIVE:
            return await self._execute_adaptive_learning(process)
        elif process.process_type == LearningProcessType.META:
            return await self._execute_meta_learning(process)
        elif process.process_type == LearningProcessType.SELF_DIRECTED:
            return await self._execute_self_directed_learning(process)
        elif process.process_type == LearningProcessType.COGNITIVE_META:
            return await self._execute_cognitive_meta_learning(process)
        else:
            return {"error": "알 수 없는 프로세스 타입"}

    async def _execute_continuous_learning(self, process: LearningProcess) -> Dict[str, Any]:
        """지속적 학습 실행"""
        # 지속적 학습 로직 구현
        return {
            "learning_type": "continuous",
            "knowledge_gained": ["새로운 지식 1", "새로운 지식 2"],
            "insights_discovered": ["통찰 1", "통찰 2"],
            "efficiency_score": 0.85,
        }

    async def _execute_adaptive_learning(self, process: LearningProcess) -> Dict[str, Any]:
        """적응적 학습 실행"""
        # 적응적 학습 로직 구현
        return {
            "learning_type": "adaptive",
            "adaptation_score": 0.78,
            "performance_improvement": 0.15,
            "strategy_adjustments": ["전략 조정 1", "전략 조정 2"],
        }

    async def _execute_meta_learning(self, process: LearningProcess) -> Dict[str, Any]:
        """메타 학습 실행"""
        # 메타 학습 로직 구현
        return {
            "learning_type": "meta",
            "meta_insights": ["메타 통찰 1", "메타 통찰 2"],
            "learning_patterns": ["패턴 1", "패턴 2"],
            "strategy_optimizations": ["최적화 1", "최적화 2"],
        }

    async def _execute_self_directed_learning(self, process: LearningProcess) -> Dict[str, Any]:
        """자기 주도적 학습 실행"""
        # 자기 주도적 학습 로직 구현
        return {
            "learning_type": "self_directed",
            "curiosity_triggers": ["호기심 트리거 1", "호기심 트리거 2"],
            "discovered_problems": ["발견된 문제 1", "발견된 문제 2"],
            "learning_goals": ["학습 목표 1", "학습 목표 2"],
        }

    async def _execute_cognitive_meta_learning(self, process: LearningProcess) -> Dict[str, Any]:
        """인지 메타 학습 실행"""
        # 인지 메타 학습 로직 구현
        return {
            "learning_type": "cognitive_meta",
            "cognitive_patterns": ["인지 패턴 1", "인지 패턴 2"],
            "meta_cognitive_insights": ["메타 인지 통찰 1", "메타 인지 통찰 2"],
            "learning_efficiency": 0.92,
        }

    async def _calculate_process_score(self, process: LearningProcess) -> float:
        """프로세스 점수 계산"""
        # 기본 점수 계산 로직
        base_score = 0.5

        # 지속시간 기반 보정
        if process.duration:
            duration_factor = min(process.duration / 60.0, 1.0)  # 1분 기준
            base_score *= duration_factor

        # 출력 데이터 품질 기반 보정
        if process.output_data:
            quality_factor = len(process.output_data) / 10.0  # 데이터 양 기준
            base_score *= min(quality_factor, 1.0)

        return min(base_score, 1.0)

    async def _calculate_session_metrics(self, session: LearningSession):
        """세션 메트릭 계산"""
        if session.duration:
            duration_seconds = session.duration.total_seconds()
            session.performance_metrics["duration_seconds"] = duration_seconds

            # 평균 지속시간 업데이트
            total_duration = sum(
                s.duration.total_seconds() for s in self.completed_sessions if s.duration
            )
            self.performance_metrics["average_session_duration"] = total_duration / len(
                self.completed_sessions
            )

    async def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 상태 조회"""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
            return {
                "session_id": session.session_id,
                "status": session.status.value,
                "process_type": session.process_type.value,
                "start_time": session.start_time.isoformat(),
                "duration": str(session.duration) if session.duration else None,
            }
        return None

    async def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        return {
            "performance_metrics": self.performance_metrics,
            "active_sessions_count": len(self.active_sessions),
            "completed_sessions_count": len(self.completed_sessions),
            "total_processes": len(self.learning_processes),
            "recent_sessions": [
                {
                    "session_id": s.session_id,
                    "process_type": s.process_type.value,
                    "status": s.status.value,
                    "duration": str(s.duration) if s.duration else None,
                }
                for s in self.completed_sessions[-5:]  # 최근 5개 세션
            ],
        }

    async def cleanup_old_sessions(self, days: int = 7):
        """오래된 세션 정리"""
        cutoff_date = datetime.now() - timedelta(days=days)

        # 완료된 세션에서 오래된 것들 제거
        self.completed_sessions = [s for s in self.completed_sessions if s.created_at > cutoff_date]

        logger.info(f"오래된 세션 정리 완료 (기준: {days}일 전)")
