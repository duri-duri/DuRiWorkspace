#!/usr/bin/env python3
"""
DuRi Alert Dedupe - 경고 노이즈 억제를 위한 디듀프 시스템 (Day 76 메모리 관리 강화)
"""

import hashlib
import time
import os
from collections import OrderedDict, defaultdict, deque
from threading import RLock
from typing import List, Dict, Any, Optional
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("alert_dedupe")

class DedupeCache:
    """알람 디듀프를 위한 TTL 캐시 (Day 76 메모리 관리 강화)"""
    
    def __init__(self, ttl_sec: int = None, max_keys: int = None):
        """
        Args:
            ttl_sec: TTL (ENV에서 가져오거나 기본값 사용)
            max_keys: 최대 키 수 (ENV에서 가져오거나 기본값 사용)
        """
        # Day 76: ENV에서 설정 가져오기
        self.ttl = ttl_sec or int(os.getenv("DURI_ALERT_DEDUPE_TTL_SEC", "600"))
        self.max = max_keys or int(os.getenv("DURI_ALERT_DEDUPE_MAX_KEYS", "512"))
        self.store = OrderedDict()  # key -> (timestamp, metadata)
        
        # Day 76: 메모리 관리 메트릭
        self.evictions_count = 0
        self.last_eviction_time = 0
        
        logger.info(f"DedupeCache 초기화: ttl={self.ttl}s, max_keys={self.max}")
    
    def seen(self, key: str, metadata: Dict[str, Any] = None) -> bool:
        """
        키가 이미 본 것인지 확인
        
        Args:
            key: 디듀프 키
            metadata: 추가 메타데이터
            
        Returns:
            이미 본 키면 True, 새로운 키면 False
        """
        now = time.time()
        
        # 만료된 키 제거
        self._purge_expired(now)
        
        if key in self.store:
            # 기존 키 - 맨 뒤로 이동 (LRU)
            self.store.move_to_end(key)
            return True
        
        # 새로운 키 추가
        self.store[key] = (now, metadata or {})
        
        # 최대 키 수 초과 시 오래된 키 제거
        if len(self.store) > self.max:
            oldest_key = self.store.popitem(last=False)[0]
            self.evictions_count += 1
            self.last_eviction_time = now
            logger.debug(f"DedupeCache 키 제거: {oldest_key}")
        
        return False
    
    def get_metadata(self, key: str) -> Dict[str, Any]:
        """키의 메타데이터 가져오기"""
        if key in self.store:
            return self.store[key][1]
        return {}
    
    def stats(self) -> Dict[str, Any]:
        """캐시 통계 반환 (Day 76: 메모리 관리 메트릭 포함)"""
        now = time.time()
        self._purge_expired(now)
        
        return {
            "total_keys": len(self.store),
            "ttl_sec": self.ttl,
            "max_keys": self.max,
            "evictions_count": self.evictions_count,
            "evictions_per_sec": self.evictions_count / max(1, now - self.last_eviction_time) if self.last_eviction_time > 0 else 0,
            "memory_usage_estimate": len(self.store) * 100,  # 대략적인 메모리 사용량 (바이트)
            "oldest_key": min(self.store.keys()) if self.store else None,
            "newest_key": max(self.store.keys()) if self.store else None
        }
    
    def _purge_expired(self, now: float):
        """만료된 키 제거"""
        expired_keys = []
        
        for key, (timestamp, _) in self.store.items():
            if now - timestamp > self.ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            self.store.pop(key, None)
        
        if expired_keys:
            logger.debug(f"DedupeCache 만료된 키 제거: {len(expired_keys)}개")
    
    def clear(self):
        """모든 키 제거"""
        count = len(self.store)
        self.store.clear()
        self.evictions_count = 0
        self.last_eviction_time = 0
        logger.info(f"DedupeCache 초기화: {count}개 키 제거")

class FailureTracker:
    """Day 76: 상위 실패 원인 집계를 위한 추적기 (견고성 강화)"""
    
    def __init__(self, window_sec: int = 3600):
        """
        Args:
            window_sec: 추적할 시간 윈도우 (기본 1시간)
        """
        self.window_sec = window_sec
        self.failure_history = deque()  # (timestamp, failure_reasons, alert_key)
        self.lock = RLock()
        
        logger.info(f"FailureTracker 초기화: window_sec={window_sec}")
    
    def record_failure(self, failure_reasons: List[str], alert_key: str):
        """
        실패 기록
        
        Args:
            failure_reasons: 실패 이유 리스트
            alert_key: 알람 키
        """
        now = time.time()
        
        with self.lock:
            self.failure_history.append((now, failure_reasons, alert_key))
            self._prune(now)
    
    def get_top_failures(self, window_sec: Optional[int] = None, top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Day 76: 상위 실패 원인 집계 (견고성 강화)
        
        Args:
            window_sec: 집계할 윈도우 (None이면 기본값 사용)
            top_n: 상위 N개 반환 (최대 100)
            
        Returns:
            상위 실패 원인 리스트
        """
        with self.lock:
            now = time.time()
            
            # Day 76: window=0 보호 (최소 60초)
            window = max(60, window_sec or self.window_sec)
            
            # Day 76: top_n 상한선 (최대 100)
            top_n = min(100, max(1, top_n))
            
            self._prune(now)
            
            if not self.failure_history:
                return []
            
            # 윈도우 내 실패만 필터링
            cutoff = now - window
            window_failures = [
                (ts, reasons, key) for ts, reasons, key in self.failure_history 
                if ts >= cutoff
            ]
            
            if not window_failures:
                return []
            
            # 실패 원인별 카운팅
            failure_counts = defaultdict(int)
            failure_details = defaultdict(lambda: {
                "count": 0,
                "first_seen": float('inf'),
                "last_seen": 0,
                "reasons": set()
            })
            
            for ts, reasons, key in window_failures:
                # 실패 이유를 정렬하여 일관성 보장
                sorted_reasons = sorted(reasons)
                reason_key = "|".join(sorted_reasons)
                
                failure_counts[reason_key] += 1
                details = failure_details[reason_key]
                details["count"] += 1
                details["first_seen"] = min(details["first_seen"], ts)
                details["last_seen"] = max(details["last_seen"], ts)
                details["reasons"].update(reasons)
            
            # 상위 N개 정렬
            top_failures = []
            for reason_key, count in sorted(failure_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]:
                details = failure_details[reason_key]
                
                # Day 76: frequency 계산 보호 (window=0 방지)
                frequency = count / (window / 60) if window > 0 else 0.0
                
                top_failures.append({
                    "failure_key": reason_key,
                    "count": count,
                    "first_seen": details["first_seen"],
                    "last_seen": details["last_seen"],
                    "reasons": list(details["reasons"]),
                    "frequency": round(frequency, 4)  # 분당 빈도
                })
            
            logger.debug(f"상위 실패 원인 집계: {len(top_failures)}개 (window={window}s, top_n={top_n})")
            return top_failures
    
    def get_failures_paginated(self, window_sec: Optional[int] = None, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
        """
        Day 76: 페이징된 실패 원인 조회
        
        Args:
            window_sec: 집계할 윈도우
            page: 페이지 번호 (1부터 시작)
            per_page: 페이지당 항목 수
            
        Returns:
            페이징된 실패 원인 결과
        """
        # 파라미터 검증
        page = max(1, page)
        per_page = min(100, max(1, per_page))
        
        # 전체 결과 가져오기
        all_failures = self.get_top_failures(window_sec, top_n=1000)  # 충분히 큰 수
        
        # 페이징 계산
        total = len(all_failures)
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        
        # 페이지 데이터 추출
        page_failures = all_failures[start_idx:end_idx]
        
        return {
            "failures": page_failures,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
                "has_next": end_idx < total,
                "has_prev": page > 1
            }
        }
    
    def _prune(self, now: float):
        """오래된 실패 기록 제거"""
        cutoff = now - self.window_sec
        pruned_count = 0
        
        while self.failure_history and self.failure_history[0][0] < cutoff:
            self.failure_history.popleft()
            pruned_count += 1
        
        if pruned_count > 0:
            logger.debug(f"FailureTracker 실패 기록 정리: {pruned_count}개 제거")
    
    def reset(self):
        """모든 실패 기록 초기화"""
        with self.lock:
            count = len(self.failure_history)
            self.failure_history.clear()
            logger.info(f"FailureTracker 초기화: {count}개 실패 기록 제거")

class AlertSampler:
    """Day 76: 알림 폭주 방지를 위한 샘플링"""
    
    def __init__(self, max_alerts_per_sec: int = 5):
        """
        Args:
            max_alerts_per_sec: 초당 최대 알림 수
        """
        self.max_alerts_per_sec = max_alerts_per_sec
        self.alert_timestamps = deque()
        self.lock = RLock()
        
        logger.info(f"AlertSampler 초기화: max_alerts_per_sec={max_alerts_per_sec}")
    
    def should_send_alert(self) -> bool:
        """
        알림 전송 여부 결정 (샘플링)
        
        Returns:
            전송해야 하면 True, 샘플링으로 제한되면 False
        """
        now = time.time()
        
        with self.lock:
            # 1초 이전 타임스탬프 제거
            cutoff = now - 1.0
            while self.alert_timestamps and self.alert_timestamps[0] < cutoff:
                self.alert_timestamps.popleft()
            
            # 현재 초 내 알림 수 확인
            if len(self.alert_timestamps) >= self.max_alerts_per_sec:
                logger.debug(f"알림 샘플링: 초당 {len(self.alert_timestamps)}개 알림으로 제한")
                return False
            
            # 알림 타임스탬프 추가
            self.alert_timestamps.append(now)
            return True

def alarm_key(reasons: List[str]) -> str:
    """
    실패 이유 리스트로부터 디듀프 키 생성
    
    Args:
        reasons: 실패 이유 리스트
        
    Returns:
        SHA1 해시 기반 디듀프 키
    """
    # 정렬하여 일관성 보장
    sorted_reasons = sorted(reasons)
    payload = "|".join(sorted_reasons)
    
    # SHA1 해시 생성
    key = hashlib.sha1(payload.encode('utf-8')).hexdigest()
    
    logger.debug(f"알람 키 생성: reasons={reasons} -> key={key}")
    return key

def canary_failure_key(canary_ok: bool, recommendation: str, failure_reasons: List[str]) -> str:
    """
    카나리 실패 전용 디듀프 키 생성
    
    Args:
        canary_ok: 카나리 상태
        recommendation: 권장사항
        failure_reasons: 실패 이유 리스트
        
    Returns:
        카나리 실패 디듀프 키
    """
    # 카나리 실패가 아닌 경우 빈 키 반환
    if canary_ok:
        return ""
    
    # 실패 이유 + 권장사항으로 키 생성
    all_reasons = failure_reasons + [f"recommendation:{recommendation}"]
    return alarm_key(all_reasons)

def integrity_failure_key(integrity_ok: bool, integrity_status: str, 
                         modified_files: List[str], missing_files: List[str]) -> str:
    """
    무결성 실패 전용 디듀프 키 생성
    
    Args:
        integrity_ok: 무결성 상태
        integrity_status: 무결성 상태 문자열
        modified_files: 수정된 파일 리스트
        missing_files: 누락된 파일 리스트
        
    Returns:
        무결성 실패 디듀프 키
    """
    # 무결성 검증 통과한 경우 빈 키 반환
    if integrity_ok:
        return ""
    
    # 무결성 실패 이유로 키 생성
    reasons = [f"integrity_status:{integrity_status}"]
    
    if modified_files:
        reasons.append(f"modified_files:{len(modified_files)}")
    
    if missing_files:
        reasons.append(f"missing_files:{len(missing_files)}")
    
    return alarm_key(reasons)

# 전역 인스턴스
dedupe_cache = DedupeCache()
failure_tracker = FailureTracker()
alert_sampler = AlertSampler()

def should_send_alert(alert_type: str, key: str, metadata: Dict[str, Any] = None) -> bool:
    """
    알람 전송 여부 결정 (Day 76: 샘플링 포함)
    
    Args:
        alert_type: 알람 타입 (canary, integrity, slo 등)
        key: 디듀프 키
        metadata: 추가 메타데이터
        
    Returns:
        전송해야 하면 True, 중복이면 False
    """
    if not key:  # 빈 키는 전송하지 않음
        return False
    
    # Day 76: 샘플링 확인
    if not alert_sampler.should_send_alert():
        return False
    
    # 타입별 키 생성
    full_key = f"{alert_type}:{key}"
    
    # 이미 본 키인지 확인
    is_duplicate = dedupe_cache.seen(full_key, metadata)
    
    if is_duplicate:
        logger.debug(f"알람 디듀프: {alert_type} 키 {key} 중복 감지")
        return False
    
    logger.info(f"알람 전송: {alert_type} 키 {key} 새로운 알람")
    return True

def record_failure(failure_reasons: List[str], alert_key: str):
    """Day 76: 실패 기록"""
    failure_tracker.record_failure(failure_reasons, alert_key)

def get_top_failures(window_sec: int = 3600, top_n: int = 10) -> List[Dict[str, Any]]:
    """Day 76: 상위 실패 원인 가져오기 (견고성 강화)"""
    return failure_tracker.get_top_failures(window_sec, top_n)

def get_failures_paginated(window_sec: int = 3600, page: int = 1, per_page: int = 10) -> Dict[str, Any]:
    """Day 76: 페이징된 실패 원인 가져오기"""
    return failure_tracker.get_failures_paginated(window_sec, page, per_page)

def get_alert_stats() -> Dict[str, Any]:
    """알람 통계 반환 (Day 76: 메모리 관리 메트릭 포함)"""
    return {
        "dedupe_cache": dedupe_cache.stats(),
        "failure_tracker": {
            "total_failures": len(failure_tracker.failure_history),
            "window_sec": failure_tracker.window_sec
        },
        "alert_sampler": {
            "max_alerts_per_sec": alert_sampler.max_alerts_per_sec,
            "current_alerts_in_window": len(alert_sampler.alert_timestamps)
        },
        "timestamp": time.time()
    }
