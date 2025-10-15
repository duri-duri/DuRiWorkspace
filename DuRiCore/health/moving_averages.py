#!/usr/bin/env python3
"""
DuRi Moving Averages - 대시보드 이동평균 메트릭 (Day 76 최적화)
"""

import time
from collections import deque
from threading import RLock
from typing import Dict, Any, Optional, List
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("moving_averages")

class MovingAverageTracker:
    """이동평균 추적기"""
    
    def __init__(self, window_sec: int = 900):  # 기본 15분
        """
        Args:
            window_sec: 이동평균 윈도우 (초 단위)
        """
        self.window_sec = window_sec
        self.lock = RLock()
        self.data_points = deque()  # (timestamp, value)
        
        logger.info(f"MovingAverageTracker 초기화: window_sec={window_sec}")
    
    def add_point(self, value: float, timestamp: Optional[float] = None):
        """
        데이터 포인트 추가
        
        Args:
            value: 값
            timestamp: 타임스탬프 (None이면 현재 시간)
        """
        if timestamp is None:
            timestamp = time.time()
        
        with self.lock:
            self.data_points.append((timestamp, value))
            self._prune(timestamp)
    
    def get_average(self, window_sec: Optional[int] = None) -> float:
        """
        이동평균 계산
        
        Args:
            window_sec: 윈도우 크기 (None이면 기본값 사용)
            
        Returns:
            이동평균값
        """
        with self.lock:
            now = time.time()
            window = window_sec or self.window_sec
            self._prune(now)
            
            if not self.data_points:
                return 0.0
            
            # 윈도우 내 데이터만 필터링
            cutoff = now - window
            window_data = [(ts, val) for ts, val in self.data_points if ts >= cutoff]
            
            if not window_data:
                return 0.0
            
            # 평균 계산
            total = sum(val for _, val in window_data)
            count = len(window_data)
            average = total / count
            
            logger.debug(f"이동평균 계산: {count}개 포인트, 평균={average:.4f}")
            return average
    
    def get_stats(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        with self.lock:
            now = time.time()
            self._prune(now)
            
            if not self.data_points:
                return {
                    "total_points": 0,
                    "window_sec": self.window_sec,
                    "average": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "oldest_point": None,
                    "newest_point": None
                }
            
            values = [val for _, val in self.data_points]
            
            return {
                "total_points": len(self.data_points),
                "window_sec": self.window_sec,
                "average": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "oldest_point": self.data_points[0][0],
                "newest_point": self.data_points[-1][0]
            }
    
    def _prune(self, now: float):
        """오래된 데이터 포인트 제거"""
        cutoff = now - self.window_sec
        pruned_count = 0
        
        while self.data_points and self.data_points[0][0] < cutoff:
            self.data_points.popleft()
            pruned_count += 1
        
        if pruned_count > 0:
            logger.debug(f"MovingAverageTracker 데이터 정리: {pruned_count}개 제거")
    
    def reset(self):
        """모든 데이터 초기화"""
        with self.lock:
            count = len(self.data_points)
            self.data_points.clear()
            logger.info(f"MovingAverageTracker 초기화: {count}개 포인트 제거")

class MetricsTracker:
    """메트릭 추적기 (p95, error_rate, readiness_fail_rate) - Day 76 최적화"""
    
    def __init__(self):
        self.p95_latency = MovingAverageTracker(900)  # 15분
        self.error_rate = MovingAverageTracker(900)   # 15분
        self.readiness_fail_rate = MovingAverageTracker(900)  # 15분
        
        # Day 76: raw ring buffer 최적화 (트렌드 시리즈용)
        self.raw_points = deque()  # (ts, p95_ms, err, readfail)
        self.raw_lock = RLock()
        self.max_raw_points = 10000  # 최대 10k 포인트
        self.max_retention_sec = 7200  # 최대 2시간 보존
        
        logger.info("MetricsTracker 초기화 완료 (Day 76 최적화)")
    
    def record_p95_latency(self, latency_ms: float):
        """P95 지연시간 기록"""
        self.p95_latency.add_point(latency_ms)
    
    def record_error_rate(self, error_rate: float):
        """오류율 기록"""
        self.error_rate.add_point(error_rate)
    
    def record_readiness_fail_rate(self, fail_rate: float):
        """Readiness 실패율 기록"""
        self.readiness_fail_rate.add_point(fail_rate)
    
    def record_all(self, p95_ms: float, err: float, readfail: float, ts: Optional[float] = None):
        """
        Day 76: 모든 메트릭을 raw buffer에 기록 (최적화된 버전)
        
        Args:
            p95_ms: P95 지연시간 (ms)
            err: 오류율 (0.0 ~ 1.0)
            readfail: Readiness 실패율 (0.0 ~ 1.0)
            ts: 타임스탬프 (None이면 현재 시간)
        """
        if ts is None:
            ts = time.time()
        
        with self.raw_lock:
            self.raw_points.append((ts, p95_ms, err, readfail))
            
            # Day 76: 최적화된 정리 (시간 기반 + 용량 기반)
            cutoff = ts - self.max_retention_sec
            pruned_count = 0
            
            # 시간 기반 정리
            while self.raw_points and self.raw_points[0][0] < cutoff:
                self.raw_points.popleft()
                pruned_count += 1
            
            # 용량 기반 정리 (최대 포인트 수 초과 시)
            while len(self.raw_points) > self.max_raw_points:
                self.raw_points.popleft()
                pruned_count += 1
            
            if pruned_count > 0:
                logger.debug(f"Raw points 정리: {pruned_count}개 제거")
    
    def resample(self, window_sec: int = 3600, step_sec: int = 60) -> Dict[str, Any]:
        """
        Day 76: 트렌드 시리즈 리샘플링 (O(n) 단일 패스 최적화)
        
        Args:
            window_sec: 윈도우 크기 (기본 1시간)
            step_sec: 스텝 크기 (기본 1분)
            
        Returns:
            리샘플된 시계열 데이터
        """
        now = time.time()
        start = now - window_sec
        
        # Day 76: 락 범위 최소화 (필터링만 락 내에서)
        with self.raw_lock:
            # 윈도우 내 포인트만 필터링
            pts = [(ts, p95, err, rf) for ts, p95, err, rf in self.raw_points if ts >= start]
        
        if not pts:
            return {"step": step_sec, "series": [], "window_sec": window_sec}
        
        # Day 76: O(n) 단일 패스 리샘플링
        series = []
        i = 0  # 포인트 인덱스
        n = len(pts)
        cur = start
        
        while cur < now:
            nxt = cur + step_sec
            
            # 현재 버킷에 속하는 포인트들 누적 (단일 패스)
            count = 0
            sum_p95 = 0.0
            sum_err = 0.0
            sum_rf = 0.0
            
            while i < n and pts[i][0] < nxt:
                ts, p95, err, rf = pts[i]
                sum_p95 += p95
                sum_err += err
                sum_rf += rf
                count += 1
                i += 1
            
            # 버킷 데이터 추가
            if count > 0:
                series.append({
                    "t": int(nxt),
                    "p95_ms": round(sum_p95 / count, 2),
                    "error_rate": round(sum_err / count, 4),
                    "readiness_fail_rate": round(sum_rf / count, 4)
                })
            else:
                series.append({
                    "t": int(nxt),
                    "p95_ms": 0.0,
                    "error_rate": 0.0,
                    "readiness_fail_rate": 0.0
                })
            
            cur = nxt
        
        logger.debug(f"트렌드 리샘플링 완료: {len(series)}개 버킷, {n}개 포인트 처리")
        return {"step": step_sec, "series": series, "window_sec": window_sec}
    
    def get_moving_averages(self) -> Dict[str, Any]:
        """이동평균 메트릭 반환"""
        return {
            "p95_latency_ms_ma15m": self.p95_latency.get_average(),
            "error_rate_ma15m": self.error_rate.get_average(),
            "readiness_fail_rate_ma15m": self.readiness_fail_rate.get_average(),
            "window_sec": 900,
            "timestamp": time.time()
        }
    
    def get_detailed_stats(self) -> Dict[str, Any]:
        """상세 통계 반환"""
        with self.raw_lock:
            raw_count = len(self.raw_points)
        
        return {
            "p95_latency": self.p95_latency.get_stats(),
            "error_rate": self.error_rate.get_stats(),
            "readiness_fail_rate": self.readiness_fail_rate.get_stats(),
            "raw_points_count": raw_count,
            "max_raw_points": self.max_raw_points,
            "max_retention_sec": self.max_retention_sec,
            "timestamp": time.time()
        }
    
    def reset_all(self):
        """모든 메트릭 초기화"""
        self.p95_latency.reset()
        self.error_rate.reset()
        self.readiness_fail_rate.reset()
        
        with self.raw_lock:
            count = len(self.raw_points)
            self.raw_points.clear()
            logger.info(f"MetricsTracker 모든 메트릭 초기화: raw_points {count}개 제거")

# 전역 인스턴스
metrics_tracker = MetricsTracker()

def record_metrics(p95_latency_ms: float, error_rate: float, readiness_fail_rate: float):
    """
    메트릭 기록 (Day 76: raw buffer에도 기록)
    
    Args:
        p95_latency_ms: P95 지연시간 (ms)
        error_rate: 오류율 (0.0 ~ 1.0)
        readiness_fail_rate: Readiness 실패율 (0.0 ~ 1.0)
    """
    metrics_tracker.record_p95_latency(p95_latency_ms)
    metrics_tracker.record_error_rate(error_rate)
    metrics_tracker.record_readiness_fail_rate(readiness_fail_rate)
    # Day 76: raw buffer에도 기록
    metrics_tracker.record_all(p95_latency_ms, error_rate, readiness_fail_rate)

def get_moving_averages() -> Dict[str, Any]:
    """이동평균 메트릭 가져오기"""
    return metrics_tracker.get_moving_averages()

def get_metrics_stats() -> Dict[str, Any]:
    """메트릭 통계 가져오기"""
    return metrics_tracker.get_detailed_stats()

def get_trends(window_sec: int = 3600, step_sec: int = 60) -> Dict[str, Any]:
    """Day 76: 트렌드 시리즈 가져오기 (최적화된 버전)"""
    return metrics_tracker.resample(window_sec, step_sec)
