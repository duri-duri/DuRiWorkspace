#!/usr/bin/env python3
"""
메트릭 생성 및 노출 테스트 스크립트
"""

import argparse
import os
import signal
import sys
import time

# 경로 설정
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from duri_core.core.metrics import maybe_expose_metrics_port, observe_phase, start_demo_load  # noqa: E402


def test_metrics():
    """메트릭 생성 및 노출 테스트"""
    print("🚀 메트릭 테스트 시작")

    # 1. 메트릭 포트 설정
    print("\n1️⃣ 메트릭 포트 설정...")
    port = int(os.getenv("PROM_PORT", "9108"))
    maybe_expose_metrics_port(port)
    print(f"✅ 메트릭 포트 {port}에서 노출")

    # 2. Phase별 메트릭 생성
    print("\n2️⃣ Phase별 메트릭 생성...")

    phases = ["plan", "edit", "test", "promote", "gate_enter", "gate_decide"]

    for phase in phases:
        print(f"   📊 {phase} phase 메트릭 생성 중...")
        with observe_phase(phase):
            # 시뮬레이션된 작업 시간
            time.sleep(0.1)
        print(f"   ✅ {phase} phase 완료")

    # 3. 메트릭 확인 안내
    print("\n3️⃣ 메트릭 확인...")
    print(f"   📊 메트릭 엔드포인트: http://localhost:{port}/metrics")
    print("   📊 확인할 메트릭:")
    print('      - latency_seconds_bucket{phase="plan"}')
    print('      - latency_seconds_bucket{phase="edit"}')
    print('      - latency_seconds_bucket{phase="test"}')

    print("\n🎯 메트릭 테스트 완료")


def serve_metrics(
    port: int,
    demo_load: bool = False,
    interval: float = 0.2,
    min_s: float = 0.05,
    max_s: float = 0.25,
):
    """메트릭 서버 모드 (프로세스 유지)"""
    print(f"🚀 메트릭 서버 모드 시작 (포트 {port})")

    if demo_load:
        print("🧪 demo-load 스레드 시작 (exporter와 같은 프로세스)")
        start_demo_load(interval_s=interval, min_s=min_s, max_s=max_s)

    print("💡 Ctrl+C로 종료")

    # 메인 스레드에서 블로킹 (프로세스 생존 보장)
    try:
        signal.pause()
    except KeyboardInterrupt:
        print("\n🛑 메트릭 서버 종료")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--serve", action="store_true", help="서버 모드(프로세스 유지)")
    parser.add_argument("--demo-load", action="store_true", help="동일 프로세스에서 지속 로드 생성")
    parser.add_argument("--port", type=int, default=int(os.getenv("PROM_PORT", "9108")))
    parser.add_argument("--interval", type=float, default=0.2, help="로드 간격(초)")
    parser.add_argument("--min", dest="min_s", type=float, default=0.05, help="작업 최소(초)")
    parser.add_argument("--max", dest="max_s", type=float, default=0.25, help="작업 최대(초)")
    args = parser.parse_args()

    if args.serve:
        # 서버 모드: 메트릭을 먼저 생성한 후 서버 시작
        print("🚀 메트릭 생성 중...")
        test_metrics()
        print("🚀 메트릭 서버 시작...")
        serve_metrics(args.port, args.demo_load, args.interval, args.min_s, args.max_s)
    else:
        # 원샷(기존 동작): 관측 후 짧게 대기
        test_metrics()
        time.sleep(2)
