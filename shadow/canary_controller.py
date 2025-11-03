#!/usr/bin/env python3
"""
Shadow 카나리 제어기 (PI 컨트롤러)
- SSH 카나리 확률 자동 조절 (0% ~ 40%)
- 메트릭 기반 피드백 제어
- 5분 주기로 SSH_CANARY 값 조정
"""

import os
import time
import json
from pathlib import Path

# PI 컨트롤러 파라미터
K_P = 0.1  # 비례 게인
K_I = 0.01  # 적분 게인
MAX_CANARY = 0.4  # 최대 카나리 확률 (40%)
MIN_CANARY = 0.0  # 최소 카나리 확률 (0%)
INITIAL_CANARY = 0.15  # 초기 카나리 확률 (15%)
TARGET_FAIL_RATE = 0.05  # 목표 실패율 (5%)
TARGET_LATENCY_RATIO = 2.0  # 목표 지연 비율 (ssh_p95 / http_p95 <= 2.0)

# 상태 파일 경로
STATE_FILE = Path("var/run/canary_controller.state")


def read_metrics():
    """Prometheus 메트릭 파일에서 값 읽기"""
    metrics_file = Path("var/metrics/transport_metrics.prom")
    if not metrics_file.exists():
        return None
    
    # 간단 파싱: 최근 메트릭만 집계
    ssh_success = 0
    ssh_failure = 0
    http_success = 0
    http_failure = 0
    
    try:
        with open(metrics_file, "r") as f:
            lines = f.readlines()
            # 최근 100줄만 사용 (5분 윈도우 추정)
            for line in lines[-100:]:
                if "duri_shadow_transport_total" in line:
                    if 'mode="ssh"' in line:
                        if 'status="success"' in line:
                            ssh_success += 1
                        elif 'status="failure"' in line:
                            ssh_failure += 1
                    elif 'mode="http"' in line:
                        if 'status="success"' in line:
                            http_success += 1
                        elif 'status="failure"' in line:
                            http_failure += 1
    except Exception:
        return None
    
    # 실패율 계산
    ssh_total = ssh_success + ssh_failure
    http_total = http_success + http_failure
    
    ssh_fail_rate = ssh_failure / ssh_total if ssh_total > 0 else 0.0
    http_fail_rate = http_failure / http_total if http_total > 0 else 0.0
    
    # 지연 시간 추정 (간단 버전: 성공/실패 비율 기반)
    latency_ratio = 1.0  # 기본값 (실제 p95 메트릭 없으면 1.0 가정)
    
    return {
        "ssh_success": ssh_success,
        "ssh_failure": ssh_failure,
        "ssh_total": ssh_total,
        "ssh_fail_rate": ssh_fail_rate,
        "http_success": http_success,
        "http_failure": http_failure,
        "http_total": http_total,
        "http_fail_rate": http_fail_rate,
        "latency_ratio": latency_ratio,
    }


def load_state():
    """상태 파일에서 이전 값 로드"""
    if STATE_FILE.exists():
        try:
            with open(STATE_FILE, "r") as f:
                state = json.load(f)
                return state.get("integral", 0.0), state.get("last_canary", INITIAL_CANARY)
        except Exception:
            pass
    return 0.0, INITIAL_CANARY


def save_state(integral, canary):
    """상태 파일에 현재 값 저장"""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(STATE_FILE, "w") as f:
            json.dump({"integral": integral, "last_canary": canary, "timestamp": time.time()}, f)
    except Exception:
        pass


def calculate_canary(metrics):
    """PI 컨트롤러로 카나리 확률 계산"""
    if metrics is None or metrics["ssh_total"] < 10:
        # 데이터 부족: 초기값 반환
        return INITIAL_CANARY
    
    # 오차 계산 (목표 실패율 대비)
    error = TARGET_FAIL_RATE - metrics["ssh_fail_rate"]
    
    # 상태 로드
    integral, last_canary = load_state()
    
    # 적분 항 업데이트 (과도한 적분 방지)
    integral += error
    integral = max(-1.0, min(1.0, integral))  # 클램핑
    
    # PI 컨트롤러 출력
    output = K_P * error + K_I * integral
    
    # 카나리 확률 업데이트
    new_canary = last_canary + output
    new_canary = max(MIN_CANARY, min(MAX_CANARY, new_canary))
    
    # 폴백 조건 체크
    if metrics["ssh_fail_rate"] > TARGET_FAIL_RATE * 2:  # 10% 초과
        # 즉시 HTTP Only로 폴백
        new_canary = 0.0
        integral = 0.0  # 적분 리셋
    elif metrics["ssh_fail_rate"] > TARGET_FAIL_RATE:  # 5% 초과
        # 점진적 감소
        new_canary = max(0.0, new_canary * 0.8)
    
    # 상태 저장
    save_state(integral, new_canary)
    
    return new_canary


def update_environment(canary_value):
    """환경 변수 파일에 카나리 값 기록"""
    env_file = Path("var/run/canary.env")
    env_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(env_file, "w") as f:
            f.write(f"SSH_CANARY={canary_value:.3f}\n")
    except Exception:
        pass


def main():
    """메인 루프 (5분 주기)"""
    print("[INFO] Shadow 카나리 제어기 시작")
    
    while True:
        try:
            # 메트릭 읽기
            metrics = read_metrics()
            
            # 카나리 확률 계산
            canary_value = calculate_canary(metrics)
            
            # 환경 변수 업데이트
            update_environment(canary_value)
            
            if metrics:
                print(f"[INFO] 카나리 조정: {canary_value:.3f} "
                      f"(SSH 실패율: {metrics['ssh_fail_rate']:.3f}, "
                      f"SSH 총 호출: {metrics['ssh_total']})")
            else:
                print(f"[INFO] 카나리 유지: {canary_value:.3f} (메트릭 데이터 부족)")
            
            # 5분 대기
            time.sleep(300)
            
        except KeyboardInterrupt:
            print("\n[INFO] 카나리 제어기 종료")
            break
        except Exception as e:
            print(f"[ERROR] 카나리 제어기 오류: {e}")
            time.sleep(60)  # 에러 시 1분 대기 후 재시도


if __name__ == "__main__":
    main()

