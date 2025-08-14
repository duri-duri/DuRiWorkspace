#!/usr/bin/env python3
"""
Day 9: 알림 지연 측정 함수
기존 Day 8 시스템과 연동하여 알림 지연을 측정합니다.
"""

import argparse
import time
import pathlib
import sys
import json
import logging
from typing import Optional, Tuple

# 기존 시스템과의 연동을 위한 설정
from DuRiCore.core.config import load_thresholds

logger = logging.getLogger("day9_measure")

def wait_for_marker(log_path: str, marker: str, timeout: float) -> float:
    """
    로그 파일에서 마커가 나타날 때까지 대기하고 지연 시간을 ms 단위로 반환합니다.
    
    Args:
        log_path: 모니터링할 로그 파일 경로
        marker: 찾을 마커 문자열
        timeout: 최대 대기 시간 (초)
    
    Returns:
        float: 마커 발견까지의 지연 시간 (밀리초)
    
    Raises:
        RuntimeError: 타임아웃 발생 시
    """
    t0 = time.perf_counter()
    path = pathlib.Path(log_path)
    deadline = t0 + timeout
    pos = 0
    
    logger.debug(f"마커 '{marker}' 대기 시작, 타임아웃: {timeout}초")
    
    while time.perf_counter() < deadline:
        if path.exists():
            try:
                with path.open('r', encoding='utf-8', errors='ignore') as f:
                    f.seek(pos)
                    for line in f:
                        if marker in line:
                            latency_ms = (time.perf_counter() - t0) * 1000.0
                            logger.info(f"마커 '{marker}' 발견, 지연: {latency_ms:.3f}ms")
                            return latency_ms
                    pos = f.tell()
            except (IOError, OSError) as e:
                logger.warning(f"로그 파일 읽기 오류: {e}")
                time.sleep(0.01)
                continue
        
        time.sleep(0.02)  # 20ms 간격으로 폴링
    
    raise RuntimeError(f"타임아웃: 마커 '{marker}'를 {timeout}초 내에 찾을 수 없음")

def measure_alert_latency(trigger_time: float, log_path: str = "var/logs/alerts.log") -> float:
    """
    알림 지연 시간을 측정합니다 (기존 시스템 호환성).
    
    Args:
        trigger_time: 알림 트리거 시간
        log_path: 알림 로그 파일 경로
    
    Returns:
        float: 알림 지연 시간 (초), 실패 시 -1.0
    """
    try:
        start = time.time()
        deadline = start + 5  # 최대 5초 대기
        
        path = pathlib.Path(log_path)
        if not path.exists():
            logger.warning(f"로그 파일이 존재하지 않음: {log_path}")
            return -1.0
        
        while time.time() < deadline:
            try:
                with path.open('r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if abs(entry.get("trigger_time", 0) - trigger_time) < 0.5:
                                latency = entry.get("alert_time", 0) - entry.get("trigger_time", 0)
                                logger.info(f"알림 지연 측정 완료: {latency:.3f}초")
                                return latency
                        except (json.JSONDecodeError, KeyError):
                            continue
            except (IOError, OSError) as e:
                logger.warning(f"로그 파일 읽기 오류: {e}")
            
            time.sleep(0.1)
        
        logger.warning("알림 지연 측정 타임아웃")
        return -1.0
        
    except Exception as e:
        logger.error(f"알림 지연 측정 실패: {e}")
        return -1.0

def main():
    """메인 실행 함수"""
    parser = argparse.ArgumentParser(description="Day 9: 알림 지연 측정")
    parser.add_argument("--log", required=True, help="모니터링할 로그 파일 경로")
    parser.add_argument("--marker", required=True, help="찾을 마커 문자열")
    parser.add_argument("--timeout", type=float, default=10.0, help="타임아웃 (초)")
    parser.add_argument("--config", default="DuRiCore/config/thresholds.yaml", help="설정 파일 경로")
    
    args = parser.parse_args()
    
    try:
        # 기존 Day 9 설정 로드
        config = load_thresholds()
        day9_config = config.get("day9", {})
        timeout = day9_config.get("simulation", {}).get("timeout_seconds", args.timeout)
        
        logger.info(f"Day 9 설정 로드: 타임아웃={timeout}초")
        
        # 마커 대기 및 지연 측정
        latency_ms = wait_for_marker(args.log, args.marker, timeout)
        print(f"{latency_ms:.3f}")
        
    except Exception as e:
        logger.error(f"측정 실패: {e}")
        print("TIMEOUT")
        sys.exit(2)

if __name__ == "__main__":
    main()
