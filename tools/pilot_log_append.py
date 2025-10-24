#!/usr/bin/env python3
"""
Day41~43: PoU Pilot Log Appender
기존 로깅 시스템을 활용하여 PoU 파일럿 로그를 효율적으로 생성합니다.
"""

import argparse
import datetime
import json
import os
import random
import sys
from typing import Any, Dict

# 도메인 정규화 매핑 (하위 호환성 유지)
DOMAIN_ALIASES = {
    "medical": "medical",
    "medicine": "medical",
    "med": "medical",
    "rehab": "rehab",
    "rehabilitation": "rehab",
    "coding": "coding",
    "developer": "coding",
    "code": "coding",
}

# 정규화된 도메인별 디렉토리 매핑
DOMAIN_DIRS = {
    "medical": "medical_pilot_v2_logs",
    "rehab": "rehab_pilot_v2_logs",
    "coding": "coding_pilot_v2_logs",
}


def generate_pilot_log_entry(
    domain: str, user_id: str, session_id: str, event_type: str, canary: bool = False
) -> Dict[str, Any]:
    """기존 로깅 패턴을 활용하여 PoU 파일럿 로그 엔트리 생성"""

    # 기존 로깅 시스템의 타임스탬프 형식 활용
    timestamp = datetime.datetime.utcnow().isoformat(timespec="milliseconds") + "Z"

    # 도메인별 특성 (기존 PoU 설정 참조)
    domain_configs = {
        "medical": {
            "latency_range": (200, 800),
            "quality_range": (85, 95),
            "success_range": (0.95, 0.99),
        },
        "rehab": {
            "latency_range": (300, 1000),
            "quality_range": (80, 90),
            "success_range": (0.90, 0.98),
        },
        "coding": {
            "latency_range": (500, 2000),
            "quality_range": (85, 95),
            "success_range": (0.95, 0.99),
        },
    }

    config = domain_configs[domain]

    # 메트릭 생성 (기존 모니터링 패턴 활용)
    metrics = {
        "latency_ms": random.randint(*config["latency_range"]),
        "success_rate": round(random.uniform(*config["success_range"]), 3),
        "quality_score": random.randint(*config["quality_range"]),
        "error_count": random.randint(0, 2) if event_type == "error" else 0,
        "canary_flag": canary,
    }

    # 메타데이터 (기존 시스템 정보 활용)
    metadata = {"version": "v1", "environment": "prod", "region": "us-west-2"}

    return {
        "timestamp": timestamp,
        "domain": domain,
        "user_id": user_id,
        "session_id": session_id,
        "event_type": event_type,
        "metrics": metrics,
        "metadata": metadata,
        "schema_version": "1.0.0",
    }


def append_log_entry(log_file: str, entry: Dict[str, Any]) -> None:
    """기존 JSONL 형식으로 로그 엔트리 추가"""
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")


def generate_session_logs(domain: str, num_sessions: int = 10, canary_percentage: float = 0.1) -> None:
    """세션별 로그 생성 (기존 로깅 패턴 활용)"""

    # 도메인 정규화
    normalized_domain = DOMAIN_ALIASES.get(domain.lower(), domain.lower())
    if normalized_domain not in DOMAIN_DIRS:
        raise ValueError(f"Unknown domain: {domain}. Supported: {list(DOMAIN_ALIASES.keys())}")

    log_file = f"{DOMAIN_DIRS[normalized_domain]}/logs.jsonl"

    for session in range(num_sessions):
        user_id = f"user_{random.randint(1000, 9999)}"
        session_id = f"session_{session}_{random.randint(100, 999)}"
        is_canary = random.random() < canary_percentage

        # 세션 시작
        append_log_entry(
            log_file,
            generate_pilot_log_entry(domain, user_id, session_id, "session_start", is_canary),
        )

        # 작업 완료 (3-7개)
        num_tasks = random.randint(3, 7)
        for task in range(num_tasks):
            append_log_entry(
                log_file,
                generate_pilot_log_entry(domain, user_id, session_id, "task_complete", is_canary),
            )

        # 에러 (10% 확률)
        if random.random() < 0.1:
            append_log_entry(
                log_file,
                generate_pilot_log_entry(domain, user_id, session_id, "error", is_canary),
            )

        # 세션 종료
        append_log_entry(
            log_file,
            generate_pilot_log_entry(domain, user_id, session_id, "session_end", is_canary),
        )


def main():
    parser = argparse.ArgumentParser(description="PoU Pilot Log Generator")
    parser.add_argument(
        "--domain",
        choices=[
            "medical",
            "med",
            "medicine",
            "rehab",
            "rehabilitation",
            "coding",
            "code",
            "developer",
        ],
        required=True,
        help="PoU domain (supports aliases)",
    )
    parser.add_argument("--sessions", type=int, default=10, help="Number of sessions to generate")
    parser.add_argument("--canary", type=float, default=0.1, help="Canary percentage (0.0 to 1.0)")

    args = parser.parse_args()

    # 도메인 정규화
    normalized_domain = DOMAIN_ALIASES.get(args.domain.lower(), args.domain.lower())
    if normalized_domain not in DOMAIN_DIRS:
        print(f"❌ Unknown domain: {args.domain}")
        print(f"   Supported domains: {list(DOMAIN_ALIASES.keys())}")
        sys.exit(1)

    print(f"Generating {args.sessions} sessions for {args.domain} domain (normalized: {normalized_domain})...")
    print(f"Canary percentage: {args.canary * 100:.1f}%")

    generate_session_logs(normalized_domain, args.sessions, args.canary)

    log_file = f"{DOMAIN_DIRS[normalized_domain]}/logs.jsonl"
    print(f"Logs written to: {log_file}")


if __name__ == "__main__":
    main()
