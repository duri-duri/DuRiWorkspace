#!/usr/bin/env python3
"""
DuRi Readiness Tracker - 실시간 readiness fail rate 계산
"""

import time
from collections import deque
from threading import RLock
from typing import Optional
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("readiness_tracker")

class ReadinessTracker:
    """Readiness probe 실패율을 rolling window로 추적하는 클래스"""
    
    def __init__(self, window_sec: int = 900):
        """
        Args:
            window_sec: 추적할 시간 윈도우 (기본 15분)
        """
        self.window_sec = window_sec
        self.lock = RLock()
        self.events = deque()  # (timestamp, success: bool)
        
        logger.info(f"ReadinessTracker 초기화: window_sec={window_sec}")
    
    def record(self, success: bool, probe_type: str = "readiness"):
        """
        Readiness probe 결과 기록
        
        Args:
            success: probe 성공 여부
            probe_type: probe 타입 (readiness, liveness 등)
        """
        with self.lock:
            now = time.time()
            self.events.append((now, success))
            self._prune(now)
            
            if not success:
                logger.warning(f"Readiness probe 실패: type={probe_type}, timestamp={now}")
    
    def fail_rate(self, window_sec: Optional[int] = None) -> float:
        """
        현재 fail rate 계산
        
        Args:
            window_sec: 계산할 윈도우 (None이면 기본값 사용)
            
        Returns:
            fail rate (0.0 ~ 1.0)
        """
        with self.lock:
            now = time.time()
            window = window_sec or self.window_sec
            self._prune(now)
            
            if not self.events:
                return 0.0
            
            # 윈도우 내 이벤트만 필터링
            cutoff = now - window
            window_events = [(ts, success) for ts, success in self.events if ts >= cutoff]
            
            if not window_events:
                return 0.0
            
            fails = sum(1 for _, success in window_events if not success)
            total = len(window_events)
            fail_rate = fails / total
            
            logger.debug(f"Readiness fail rate 계산: {fails}/{total} = {fail_rate:.4f}")
            return fail_rate
    
    def success_rate(self, window_sec: Optional[int] = None) -> float:
        """성공률 계산 (1 - fail_rate)"""
        return 1.0 - self.fail_rate(window_sec)
    
    def stats(self) -> dict:
        """현재 통계 정보 반환"""
        with self.lock:
            now = time.time()
            self._prune(now)
            
            if not self.events:
                return {
                    "total_events": 0,
                    "success_count": 0,
                    "fail_count": 0,
                    "fail_rate": 0.0,
                    "success_rate": 1.0,
                    "window_sec": self.window_sec,
                    "oldest_event": None,
                    "newest_event": None
                }
            
            success_count = sum(1 for _, success in self.events if success)
            fail_count = len(self.events) - success_count
            fail_rate = fail_count / len(self.events)
            
            return {
                "total_events": len(self.events),
                "success_count": success_count,
                "fail_count": fail_count,
                "fail_rate": fail_rate,
                "success_rate": 1.0 - fail_rate,
                "window_sec": self.window_sec,
                "oldest_event": self.events[0][0] if self.events else None,
                "newest_event": self.events[-1][0] if self.events else None
            }
    
    def _prune(self, now: float):
        """오래된 이벤트 제거"""
        cutoff = now - self.window_sec
        pruned_count = 0
        
        while self.events and self.events[0][0] < cutoff:
            self.events.popleft()
            pruned_count += 1
        
        if pruned_count > 0:
            logger.debug(f"ReadinessTracker 이벤트 정리: {pruned_count}개 제거")
    
    def reset(self):
        """모든 이벤트 초기화"""
        with self.lock:
            count = len(self.events)
            self.events.clear()
            logger.info(f"ReadinessTracker 초기화: {count}개 이벤트 제거")

# 전역 인스턴스
readiness_tracker = ReadinessTracker()

def get_readiness_fail_rate(window_sec: int = 900) -> float:
    """
    전역 readiness tracker에서 fail rate 가져오기
    
    Args:
        window_sec: 계산할 윈도우 (기본 15분)
        
    Returns:
        fail rate (0.0 ~ 1.0)
    """
    return readiness_tracker.fail_rate(window_sec)

def record_readiness_probe(success: bool, probe_type: str = "readiness"):
    """
    Readiness probe 결과 기록
    
    Args:
        success: probe 성공 여부
        probe_type: probe 타입
    """
    readiness_tracker.record(success, probe_type)
