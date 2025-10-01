#!/usr/bin/env python3
"""
DuRi 인지 대역폭 관리 시스템 - 간소화된 버전
함수 depth 2단계 제한, 조건-매핑 방식 적용
"""

import logging
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StimulusType(Enum):
    """자극 타입 정의"""

    SENSORY = "sensory"
    EMOTIONAL = "emotional"
    COGNITIVE = "cognitive"
    SOCIAL = "social"
    CREATIVE = "creative"


class ProcessingStatus(Enum):
    """처리 상태"""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    REJECTED = "rejected"
    OVERLOAD = "overload"


@dataclass
class StimulusItem:
    """자극 아이템"""

    id: str
    stimulus: str
    stimulus_type: StimulusType
    intensity: float
    timestamp: str
    source: str
    priority: float = 0.5
    processing_status: ProcessingStatus = ProcessingStatus.PENDING
    response: Optional[str] = None
    emotion_impact: Optional[Dict[str, float]] = None


@dataclass
class BandwidthConfig:
    """대역폭 설정"""

    level: int
    max_daily_stimuli: int
    max_concurrent_processing: int
    processing_cooldown: float
    overload_threshold: float
    recovery_time: float


class CognitiveBandwidthManager:
    """인지 대역폭 관리 시스템 - 간소화된 버전"""

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

        # 자극 히스토리
        self.stimulus_history = deque(maxlen=1000)

        # 흥미 기반 필터링 (조건-매핑 방식)
        self.interest_patterns = {
            "재미": 0.8,
            "색깔": 0.7,
            "소리": 0.6,
            "이야기": 0.9,
            "놀이": 0.8,
            "친구": 0.7,
            "학습": 0.6,
            "창작": 0.7,
            "문제": 0.5,
            "도움": 0.8,
        }

        logger.info("인지 대역폭 관리 시스템 초기화 완료")

    def _initialize_bandwidth_configs(self) -> Dict[int, BandwidthConfig]:
        """대역폭 설정 초기화 (조건-매핑 방식)"""
        return {
            1: BandwidthConfig(1, 5, 1, 2.0, 0.8, 30.0),  # 신생아
            2: BandwidthConfig(2, 10, 2, 1.5, 0.8, 25.0),  # 유아기 전기
            3: BandwidthConfig(3, 15, 3, 1.0, 0.8, 20.0),  # 유아기 후기
            4: BandwidthConfig(4, 20, 4, 0.8, 0.8, 15.0),  # 소아기
            5: BandwidthConfig(5, 25, 5, 0.6, 0.8, 12.0),  # 학령기
            6: BandwidthConfig(6, 30, 6, 0.5, 0.8, 10.0),  # 사춘기
            7: BandwidthConfig(7, 35, 7, 0.4, 0.8, 8.0),  # 청년기
            8: BandwidthConfig(8, 40, 8, 0.3, 0.8, 5.0),  # 성인기
        }

    def receive_stimulus(
        self,
        stimulus: str,
        stimulus_type: StimulusType,
        intensity: float = 0.5,
        source: str = "external",
    ) -> Dict[str, Any]:
        """자극 수신 처리"""
        # 1. 과부하 상태 확인
        if self.overload_status["is_overloaded"]:
            return self._handle_overload_rejection(stimulus)

        # 2. 일일 한계 확인
        if self.daily_stats["total_received"] >= self.current_config.max_daily_stimuli:
            return self._handle_daily_limit_rejection(stimulus)

        # 3. 흥미 점수 계산
        interest_score = self._calculate_interest_score(stimulus)

        # 4. 흥미 기반 필터링
        if interest_score < 0.3:  # 낮은 흥미
            return self._handle_low_interest_rejection(stimulus, interest_score)

        # 5. 자극 아이템 생성
        stimulus_item = StimulusItem(
            id=f"stimulus_{datetime.now().timestamp()}",
            stimulus=stimulus,
            stimulus_type=stimulus_type,
            intensity=intensity,
            timestamp=datetime.now().isoformat(),
            source=source,
            priority=interest_score,
        )

        # 6. 처리 시도
        processing_result = self._attempt_processing(stimulus_item)

        # 7. 통계 업데이트
        self.daily_stats["total_received"] += 1
        self.stimulus_history.append(stimulus_item)

        return processing_result

    def _handle_overload_rejection(self, stimulus: str) -> Dict[str, Any]:
        """과부하 거부 처리"""
        self.daily_stats["total_rejected"] += 1
        return {
            "status": "rejected",
            "reason": "overload",
            "stimulus": stimulus,
            "recovery_time": self.overload_status["recovery_time"],
        }

    def _handle_daily_limit_rejection(self, stimulus: str) -> Dict[str, Any]:
        """일일 한계 거부 처리"""
        self.daily_stats["total_rejected"] += 1
        return {
            "status": "rejected",
            "reason": "daily_limit_exceeded",
            "stimulus": stimulus,
            "daily_limit": self.current_config.max_daily_stimuli,
        }

    def _handle_low_interest_rejection(
        self, stimulus: str, interest_score: float
    ) -> Dict[str, Any]:
        """낮은 흥미 거부 처리"""
        self.daily_stats["total_rejected"] += 1
        return {
            "status": "rejected",
            "reason": "low_interest",
            "stimulus": stimulus,
            "interest_score": interest_score,
        }

    def _calculate_interest_score(self, stimulus: str) -> float:
        """흥미 점수 계산 (조건-매핑 방식)"""
        total_score = 0.0
        total_weight = 0.0

        for pattern, weight in self.interest_patterns.items():
            if pattern in stimulus:
                total_score += weight
                total_weight += 1.0

        if total_weight == 0:
            return 0.5  # 기본 점수

        return total_score / total_weight

    def _attempt_processing(self, stimulus_item: StimulusItem) -> Dict[str, Any]:
        """처리 시도"""
        # 1. 과부하 위험 계산
        overload_risk = self._calculate_overload_risk()

        # 2. 과부하 임계값 확인
        if overload_risk > self.current_config.overload_threshold:
            self._enter_overload_state()
            return self._handle_overload_rejection(stimulus_item.stimulus)

        # 3. 처리 큐에 추가
        self.pending_queue.append(stimulus_item)
        stimulus_item.processing_status = ProcessingStatus.PROCESSING

        # 4. 처리 완료 시뮬레이션
        self.daily_stats["total_processed"] += 1
        stimulus_item.processing_status = ProcessingStatus.COMPLETED
        self.completed_queue.append(stimulus_item)

        return {
            "status": "processed",
            "stimulus": stimulus_item.stimulus,
            "processing_time": self.current_config.processing_cooldown,
            "overload_risk": overload_risk,
        }

    def _calculate_overload_risk(self) -> float:
        """과부하 위험 계산"""
        # 간소화된 과부하 위험 계산
        processing_count = len(self.processing_queue)
        recent_stimuli = len(
            [
                s
                for s in self.stimulus_history
                if (datetime.now() - datetime.fromisoformat(s.timestamp)).seconds < 60
            ]
        )

        # 처리 중인 자극 비율
        processing_ratio = (
            processing_count / self.current_config.max_concurrent_processing
        )

        # 최근 자극 빈도
        frequency_ratio = recent_stimuli / 10  # 1분당 10개 기준

        # 과부하 위험 = 처리 비율 + 빈도 비율
        overload_risk = (processing_ratio + frequency_ratio) / 2
        return min(1.0, overload_risk)

    def _enter_overload_state(self):
        """과부하 상태 진입"""
        self.overload_status["is_overloaded"] = True
        self.overload_status["overload_start"] = datetime.now().isoformat()
        self.overload_status["recovery_time"] = datetime.now() + timedelta(
            seconds=self.current_config.recovery_time
        )
        self.overload_status["consecutive_overloads"] += 1
        self.daily_stats["overload_count"] += 1

        logger.warning(f"과부하 상태 진입 - 레벨 {self.current_level}")

    def check_overload_recovery(self):
        """과부하 복구 확인"""
        if not self.overload_status["is_overloaded"]:
            return

        if datetime.now() >= self.overload_status["recovery_time"]:
            self._exit_overload_state()

    def _exit_overload_state(self):
        """과부하 상태 해제"""
        self.overload_status["is_overloaded"] = False
        self.overload_status["overload_start"] = None
        self.overload_status["recovery_time"] = None

        logger.info(f"과부하 상태 해제 - 레벨 {self.current_level}")

    def update_level(self, new_level: int):
        """레벨 업데이트"""
        if new_level in self.bandwidth_configs:
            self.current_level = new_level
            self.current_config = self.bandwidth_configs[new_level]

            # 레벨 변경 시 통계 초기화
            self.daily_stats = {
                "total_received": 0,
                "total_processed": 0,
                "total_rejected": 0,
                "overload_count": 0,
                "start_time": datetime.now().isoformat(),
            }

            logger.info(f"대역폭 레벨 업데이트: {new_level}")

    def get_bandwidth_status(self) -> Dict[str, Any]:
        """대역폭 상태 반환"""
        return {
            "current_level": self.current_level,
            "config": {
                "max_daily_stimuli": self.current_config.max_daily_stimuli,
                "max_concurrent_processing": self.current_config.max_concurrent_processing,
                "processing_cooldown": self.current_config.processing_cooldown,
                "overload_threshold": self.current_config.overload_threshold,
                "recovery_time": self.current_config.recovery_time,
            },
            "daily_stats": self.daily_stats,
            "overload_status": self.overload_status,
            "queue_status": {
                "pending": len(self.pending_queue),
                "processing": len(self.processing_queue),
                "completed": len(self.completed_queue),
            },
        }

    def get_processing_recommendations(self) -> Dict[str, Any]:
        """처리 권장사항 반환"""
        overload_risk = self._calculate_overload_risk()

        return {
            "should_process": not self.overload_status["is_overloaded"],
            "should_pause": overload_risk > 0.7,
            "should_reduce_intensity": overload_risk > 0.5,
            "optimal_stimulus_interval": self.current_config.processing_cooldown,
            "max_concurrent_safe": max(
                1, self.current_config.max_concurrent_processing - 1
            ),
            "overload_risk": overload_risk,
        }
