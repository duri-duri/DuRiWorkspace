#!/usr/bin/env python3
"""
DuRi 인지 대역폭 관리 시스템
레벨별 자극 처리량 제한 및 과부하 방지 시스템
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logger = logging.getLogger(__name__)


class StimulusType(Enum):
    """자극 타입 정의"""

    SENSORY = "sensory"  # 감각적 자극 (색, 소리, 촉각)
    EMOTIONAL = "emotional"  # 감정적 자극 (기쁨, 슬픔, 분노)
    COGNITIVE = "cognitive"  # 인지적 자극 (문제, 질문, 학습)
    SOCIAL = "social"  # 사회적 자극 (대화, 상호작용)
    CREATIVE = "creative"  # 창의적 자극 (상상, 창작)


class ProcessingStatus(Enum):
    """처리 상태"""

    PENDING = "pending"  # 대기 중
    PROCESSING = "processing"  # 처리 중
    COMPLETED = "completed"  # 완료
    REJECTED = "rejected"  # 거부됨 (대역폭 초과)
    OVERLOAD = "overload"  # 과부하 상태


@dataclass
class StimulusItem:
    """자극 아이템"""

    id: str
    stimulus: str
    stimulus_type: StimulusType
    intensity: float  # 0.0-1.0
    timestamp: str
    source: str
    priority: float = 0.5  # 0.0-1.0
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    response: Optional[str] = None
    emotion_impact: Optional[Dict[str, float]] = None


@dataclass
class BandwidthConfig:
    """대역폭 설정"""

    level: int
    max_daily_stimuli: int
    max_concurrent_processing: int
    processing_cooldown: float  # 초
    overload_threshold: float  # 과부하 임계값
    recovery_time: float  # 복구 시간 (초)


class CognitiveBandwidthManager:
    """인지 대역폭 관리 시스템"""

    def __init__(self):
        self.current_level = 1
        self.bandwidth_configs = self._initialize_bandwidth_configs()
        self.current_config = self.bandwidth_configs[self.current_level]

        # 처리 큐
        self.pending_queue = deque()
        self.processing_queue = deque()
        self.completed_queue = deque()

        # 통계
        self.daily_stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_rejected": 0,
            "overload_count": 0,
            "start_time": datetime.now().isoformat(),
        }

        # 과부하 상태
        self.overload_status = {
            "is_overloaded": False,
            "overload_start": None,
            "recovery_time": None,
            "consecutive_overloads": 0,
        }

        # 자극 히스토리 (최근 24시간)
        self.stimulus_history = deque(maxlen=1000)

        # 흥미 기반 필터링
        self.interest_patterns = {
            "재미": 0.8,
            "색깔": 0.7,
            "소리": 0.6,
            "이야기": 0.9,
            "놀이": 0.8,
            "친구": 0.7,
            "궁금": 0.8,
            "새로": 0.7,
            "기쁘": 0.6,
            "좋아": 0.6,
        }

        logger.info("인지 대역폭 관리 시스템 초기화 완료")

    def _initialize_bandwidth_configs(self) -> Dict[int, BandwidthConfig]:
        """레벨별 대역폭 설정 초기화"""
        return {
            1: BandwidthConfig(  # 신생아
                level=1,
                max_daily_stimuli=5,
                max_concurrent_processing=1,
                processing_cooldown=30.0,
                overload_threshold=0.8,
                recovery_time=300.0,
            ),
            2: BandwidthConfig(  # 유아기 전기
                level=2,
                max_daily_stimuli=15,
                max_concurrent_processing=2,
                processing_cooldown=20.0,
                overload_threshold=0.8,
                recovery_time=240.0,
            ),
            3: BandwidthConfig(  # 유아기 후기
                level=3,
                max_daily_stimuli=30,
                max_concurrent_processing=3,
                processing_cooldown=15.0,
                overload_threshold=0.8,
                recovery_time=180.0,
            ),
            4: BandwidthConfig(  # 소아기
                level=4,
                max_daily_stimuli=60,
                max_concurrent_processing=5,
                processing_cooldown=10.0,
                overload_threshold=0.8,
                recovery_time=120.0,
            ),
            5: BandwidthConfig(  # 학령기
                level=5,
                max_daily_stimuli=200,
                max_concurrent_processing=10,
                processing_cooldown=5.0,
                overload_threshold=0.8,
                recovery_time=60.0,
            ),
            6: BandwidthConfig(  # 사춘기
                level=6,
                max_daily_stimuli=500,
                max_concurrent_processing=20,
                processing_cooldown=3.0,
                overload_threshold=0.8,
                recovery_time=30.0,
            ),
            7: BandwidthConfig(  # 청년기
                level=7,
                max_daily_stimuli=1000,
                max_concurrent_processing=50,
                processing_cooldown=1.0,
                overload_threshold=0.8,
                recovery_time=15.0,
            ),
            8: BandwidthConfig(  # 성인기
                level=8,
                max_daily_stimuli=2000,
                max_concurrent_processing=100,
                processing_cooldown=0.5,
                overload_threshold=0.8,
                recovery_time=10.0,
            ),
        }

    def receive_stimulus(
        self,
        stimulus: str,
        stimulus_type: StimulusType,
        intensity: float = 0.5,
        source: str = "external",
    ) -> Dict[str, Any]:
        """자극 수신 및 처리"""

        # 1. 과부하 상태 확인
        if self.overload_status["is_overloaded"]:
            return self._handle_overload_rejection(stimulus)

        # 2. 일일 처리량 확인
        if self.daily_stats["total_processed"] >= self.current_config.max_daily_stimuli:
            return self._handle_daily_limit_rejection(stimulus)

        # 3. 흥미 기반 필터링
        interest_score = self._calculate_interest_score(stimulus)
        if interest_score < 0.1:  # 흥미 임계값을 낮춤 (0.3 → 0.1)
            return self._handle_low_interest_rejection(stimulus, interest_score)

        # 4. 자극 아이템 생성
        stimulus_item = StimulusItem(
            id=f"stimulus_{int(time.time() * 1000)}",
            stimulus=stimulus,
            stimulus_type=stimulus_type,
            intensity=intensity,
            timestamp=datetime.now().isoformat(),
            source=source,
            priority=interest_score,
        )

        # 5. 처리 큐에 추가
        self.pending_queue.append(stimulus_item)
        self.stimulus_history.append(stimulus_item)
        self.daily_stats["total_received"] += 1

        # 6. 처리 시도
        processing_result = self._attempt_processing(stimulus_item)

        return {
            "status": "received",
            "stimulus_id": stimulus_item.id,
            "interest_score": interest_score,
            "processing_result": processing_result,
            "bandwidth_status": self.get_bandwidth_status(),
        }

    def _handle_overload_rejection(self, stimulus: str) -> Dict[str, Any]:
        """과부하 상태에서의 거부 처리"""
        self.daily_stats["total_rejected"] += 1

        return {
            "status": "rejected",
            "reason": "overload",
            "stimulus": stimulus,
            "overload_status": self.overload_status,
            "recovery_time": self.overload_status.get("recovery_time"),
        }

    def _handle_daily_limit_rejection(self, stimulus: str) -> Dict[str, Any]:
        """일일 처리량 한계 거부 처리"""
        self.daily_stats["total_rejected"] += 1

        return {
            "status": "rejected",
            "reason": "daily_limit_exceeded",
            "stimulus": stimulus,
            "daily_stats": self.daily_stats,
            "max_daily_stimuli": self.current_config.max_daily_stimuli,
        }

    def _handle_low_interest_rejection(
        self, stimulus: str, interest_score: float
    ) -> Dict[str, Any]:
        """낮은 흥미 자극 거부 처리"""
        self.daily_stats["total_rejected"] += 1

        return {
            "status": "rejected",
            "reason": "low_interest",
            "stimulus": stimulus,
            "interest_score": interest_score,
            "threshold": 0.3,
        }

    def _calculate_interest_score(self, stimulus: str) -> float:
        """흥미 점수 계산"""
        stimulus_lower = stimulus.lower()
        total_score = 0.0
        matched_patterns = 0

        for pattern, weight in self.interest_patterns.items():
            if pattern in stimulus_lower:
                total_score += weight
                matched_patterns += 1

        # 기본 점수 (모든 자극에 대해)
        base_score = 0.2

        if matched_patterns > 0:
            average_score = total_score / matched_patterns
            return min(1.0, base_score + average_score)
        else:
            return base_score

    def _attempt_processing(self, stimulus_item: StimulusItem) -> Dict[str, Any]:
        """자극 처리 시도"""

        # 1. 동시 처리량 확인
        if len(self.processing_queue) >= self.current_config.max_concurrent_processing:
            return {
                "status": "queued",
                "queue_position": len(self.pending_queue),
                "estimated_wait_time": len(self.pending_queue)
                * self.current_config.processing_cooldown,
            }

        # 2. 처리 시작
        stimulus_item.processing_status = ProcessingStatus.PROCESSING
        self.processing_queue.append(stimulus_item)

        # 3. 과부하 위험도 계산
        overload_risk = self._calculate_overload_risk()

        if overload_risk > self.current_config.overload_threshold:
            # 과부하 상태로 전환
            self._enter_overload_state()
            return {
                "status": "overload_triggered",
                "overload_risk": overload_risk,
                "threshold": self.current_config.overload_threshold,
            }

        # 4. 정상 처리
        self.daily_stats["total_processed"] += 1

        return {
            "status": "processing",
            "overload_risk": overload_risk,
            "processing_capacity": self.current_config.max_concurrent_processing
            - len(self.processing_queue),
        }

    def _calculate_overload_risk(self) -> float:
        """과부하 위험도 계산"""
        # 처리 중인 자극 수
        processing_count = len(self.processing_queue)
        max_processing = self.current_config.max_concurrent_processing

        # 최근 자극 빈도
        recent_stimuli = len(
            [
                s
                for s in self.stimulus_history
                if (
                    datetime.now()
                    - datetime.fromisoformat(s.timestamp.replace("Z", "+00:00"))
                ).seconds
                < 300
            ]
        )

        # 과부하 위험도 계산
        processing_risk = processing_count / max_processing
        frequency_risk = min(
            1.0, recent_stimuli / (self.current_config.max_daily_stimuli * 0.1)
        )

        return (processing_risk * 0.6) + (frequency_risk * 0.4)

    def _enter_overload_state(self):
        """과부하 상태 진입"""
        self.overload_status["is_overloaded"] = True
        self.overload_status["overload_start"] = datetime.now().isoformat()
        self.overload_status["recovery_time"] = datetime.now() + timedelta(
            seconds=self.current_config.recovery_time
        )
        self.overload_status["consecutive_overloads"] += 1
        self.daily_stats["overload_count"] += 1

        # 처리 중인 자극들을 대기 상태로 변경
        for item in self.processing_queue:
            item.processing_status = ProcessingStatus.PENDING
            self.pending_queue.appendleft(item)

        self.processing_queue.clear()

    def check_overload_recovery(self):
        """과부하 복구 확인"""
        if not self.overload_status["is_overloaded"]:
            return

        recovery_time = self.overload_status["recovery_time"]
        if recovery_time and datetime.now() >= recovery_time:
            self._exit_overload_state()

    def _exit_overload_state(self):
        """과부하 상태 해제"""
        self.overload_status["is_overloaded"] = False
        self.overload_status["overload_start"] = None
        self.overload_status["recovery_time"] = None

    def update_level(self, new_level: int):
        """레벨 업데이트"""
        if new_level in self.bandwidth_configs:
            self.current_level = new_level
            self.current_config = self.bandwidth_configs[new_level]

            # 레벨 업데이트 시 통계 초기화
            self.daily_stats = {
                "total_received": 0,
                "total_processed": 0,
                "total_rejected": 0,
                "overload_count": 0,
                "start_time": datetime.now().isoformat(),
            }

    def get_bandwidth_status(self) -> Dict[str, Any]:
        """대역폭 상태 반환"""
        return {
            "current_level": self.current_level,
            "config": asdict(self.current_config),
            "daily_stats": self.daily_stats,
            "overload_status": self.overload_status,
            "queue_status": {
                "pending": len(self.pending_queue),
                "processing": len(self.processing_queue),
                "completed": len(self.completed_queue),
            },
            "overload_risk": self._calculate_overload_risk(),
        }

    def get_processing_recommendations(self) -> Dict[str, Any]:
        """처리 권장사항 반환"""
        overload_risk = self._calculate_overload_risk()

        recommendations = {
            "should_process": overload_risk < 0.7,
            "should_pause": overload_risk > 0.8,
            "should_reduce_intensity": overload_risk > 0.6,
            "optimal_stimulus_interval": self.current_config.processing_cooldown,
            "max_concurrent_safe": max(
                1, self.current_config.max_concurrent_processing - 1
            ),
        }

        return recommendations


# 전역 인스턴스
cognitive_bandwidth_manager = CognitiveBandwidthManager()
