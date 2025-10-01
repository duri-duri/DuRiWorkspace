#!/usr/bin/env python3
"""
Day 37: PoU 7일차 유지율 ETL 스크립트
입력: raw 로그 CSV/DB → 출력: A/B CSV
기존 pou_metrics_ingest.py와 통합하여 유지율 계산
"""

import argparse
import csv
from datetime import datetime, timedelta
import json
import logging
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def parse_timestamp(ts_str: str) -> Optional[datetime]:
    """타임스탬프 파싱 (UTC 고정)"""
    try:
        # ISO 8601 형식 지원
        if "T" in ts_str:
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            # UTC로 변환 (naive datetime)
            return dt.replace(tzinfo=None)
        else:
            # YYYY-MM-DD 형식
            return datetime.strptime(ts_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        logger.warning(f"Invalid timestamp format: {ts_str}")
        return None


def extract_retention_data(input_file: str, output_file: str) -> Dict[str, Any]:
    """
    유지율 데이터 추출
    입력: raw 로그 CSV
    출력: A/B 테스트용 CSV
    """
    logger.info(f"Processing input file: {input_file}")

    # 데이터 저장용
    user_events = {}  # user_id -> [(timestamp, variant, event), ...]
    retention_data = []

    # 입력 파일 읽기
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                # 필수 필드 확인
                if not all(
                    key in row for key in ["timestamp", "user_id", "variant", "event"]
                ):
                    logger.warning(f"Missing required fields in row: {row}")
                    continue

                # 타임스탬프 파싱
                timestamp = parse_timestamp(row["timestamp"])
                if timestamp is None:
                    continue

                user_id = row["user_id"].strip()
                variant = row["variant"].strip()
                event = row["event"].strip()

                # 유저별 이벤트 수집
                if user_id not in user_events:
                    user_events[user_id] = []

                user_events[user_id].append((timestamp, variant, event))

    except FileNotFoundError:
        logger.error(f"Input file not found: {input_file}")
        return {"error": "Input file not found"}
    except Exception as e:
        logger.error(f"Error reading input file: {e}")
        return {"error": str(e)}

    # 유지율 계산
    for user_id, events in user_events.items():
        if not events:
            continue

        # 첫 번째 이벤트 (Day0) 찾기
        first_event = min(events, key=lambda x: x[0])
        day0 = first_event[0].date()
        variant = first_event[1]

        # D+7 기간 계산 (±12시간)
        d7_start = (
            datetime.combine(day0, datetime.min.time())
            + timedelta(days=7)
            - timedelta(hours=12)
        )
        d7_end = (
            datetime.combine(day0, datetime.min.time())
            + timedelta(days=7)
            + timedelta(hours=12)
        )

        # D+7 기간 내 이벤트 확인
        retained_d7 = 0
        for timestamp, _, _ in events:
            if d7_start <= timestamp <= d7_end:
                retained_d7 = 1
                break

        # 결과 저장
        retention_data.append(
            {
                "variant": variant,
                "retained_d7": retained_d7,
                "cohort_date": day0.strftime("%Y-%m-%d"),
            }
        )

    # 출력 파일 생성
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            if retention_data:
                writer = csv.DictWriter(
                    f, fieldnames=["variant", "retained_d7", "cohort_date"]
                )
                writer.writeheader()
                writer.writerows(retention_data)
            else:
                # 빈 파일 생성
                writer = csv.DictWriter(
                    f, fieldnames=["variant", "retained_d7", "cohort_date"]
                )
                writer.writeheader()

        logger.info(f"Retention data saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error writing output file: {e}")
        return {"error": str(e)}

    # 통계 정보
    stats = {
        "total_users": len(user_events),
        "retention_records": len(retention_data),
        "variants": list(set(r["variant"] for r in retention_data)),
        "cohort_dates": list(set(r["cohort_date"] for r in retention_data)),
    }

    # 변형별 유지율 계산
    for variant in stats["variants"]:
        variant_data = [r for r in retention_data if r["variant"] == variant]
        if variant_data:
            retention_rate = sum(r["retained_d7"] for r in variant_data) / len(
                variant_data
            )
            stats[f"{variant}_retention_rate"] = retention_rate
            stats[f"{variant}_count"] = len(variant_data)

    return stats


def create_synthetic_data(output_file: str, n_users: int = 1000) -> Dict[str, Any]:
    """
    테스트용 합성 데이터 생성
    """
    logger.info(f"Creating synthetic data with {n_users} users")

    from datetime import datetime, timedelta
    import random

    # 시드 설정 (재현 가능한 결과)
    random.seed(42)

    retention_data = []
    base_date = datetime(2025, 9, 23).date()

    for i in range(n_users):
        user_id = f"user_{i:04d}"
        variant = random.choice(["A", "B"])
        cohort_date = base_date + timedelta(days=random.randint(0, 7))

        # 유지율 시뮬레이션 (A: 40%, B: 45%)
        if variant == "A":
            retention_prob = 0.40
        else:
            retention_prob = 0.45

        retained_d7 = 1 if random.random() < retention_prob else 0

        retention_data.append(
            {
                "variant": variant,
                "retained_d7": retained_d7,
                "cohort_date": cohort_date.strftime("%Y-%m-%d"),
            }
        )

    # 출력 파일 생성
    try:
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(
                f, fieldnames=["variant", "retained_d7", "cohort_date"]
            )
            writer.writeheader()
            writer.writerows(retention_data)

        logger.info(f"Synthetic data saved to: {output_file}")

    except Exception as e:
        logger.error(f"Error writing synthetic data: {e}")
        return {"error": str(e)}

    # 통계 정보
    stats = {
        "total_users": n_users,
        "retention_records": len(retention_data),
        "variants": ["A", "B"],
        "cohort_dates": list(set(r["cohort_date"] for r in retention_data)),
    }

    # 변형별 유지율 계산
    for variant in ["A", "B"]:
        variant_data = [r for r in retention_data if r["variant"] == variant]
        if variant_data:
            retention_rate = sum(r["retained_d7"] for r in variant_data) / len(
                variant_data
            )
            stats[f"{variant}_retention_rate"] = retention_rate
            stats[f"{variant}_count"] = len(variant_data)

    return stats


def main():
    """CLI 인터페이스"""
    parser = argparse.ArgumentParser(description="PoU 7일차 유지율 ETL 스크립트")

    parser.add_argument("--in", dest="input_file", help="입력 파일 경로 (raw 로그 CSV)")
    parser.add_argument(
        "--out", dest="output_file", required=True, help="출력 파일 경로"
    )
    parser.add_argument("--synthetic", action="store_true", help="합성 데이터 생성")
    parser.add_argument(
        "--n-users", type=int, default=1000, help="합성 데이터 사용자 수"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="상세 로그 출력")

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.synthetic:
        # 합성 데이터 생성
        stats = create_synthetic_data(args.output_file, args.n_users)
    else:
        # 실제 데이터 처리
        if not args.input_file:
            parser.error("--in 옵션이 필요합니다 (합성 데이터가 아닌 경우)")

        stats = extract_retention_data(args.input_file, args.output_file)

    # 결과 출력
    if "error" in stats:
        logger.error(f"Processing failed: {stats['error']}")
        sys.exit(1)
    else:
        logger.info("Processing completed successfully")
        print(json.dumps(stats, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
