#!/usr/bin/env python3
"""
정적 품질 메트릭 수집 스크립트
뮤테이션 테스트와 함께 G1 게이트의 핵심 구성요소
"""

import json
import pathlib
import subprocess
import sys
from typing import Any, Dict


def _run(cmd: list) -> tuple[int, str, str]:
    """명령어 실행 및 결과 반환"""
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


def collect_static_metrics() -> Dict[str, Any]:
    """정적 품질 메트릭 수집"""
    metrics_dir = pathlib.Path("metrics")
    metrics_dir.mkdir(exist_ok=True)

    # Cyclomatic Complexity 수집
    print("📊 Collecting cyclomatic complexity metrics...")
    rc, out, err = _run(
        [
            sys.executable,
            "-m",
            "radon",
            "cc",
            "-s",
            "-j",
            "duri_core",
            "duri_brain",
            "duri_evolution",
        ]
    )

    if rc != 0:
        print(f"⚠️ Radon CC failed: {err}")
        cc_data = {}
    else:
        try:
            cc_data = json.loads(out) if out else {}
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON from radon cc: {out}")
            cc_data = {}

    # Maintainability Index 수집
    print("📊 Collecting maintainability index metrics...")
    rc2, out2, err2 = _run(
        [
            sys.executable,
            "-m",
            "radon",
            "mi",
            "-j",
            "duri_core",
            "duri_brain",
            "duri_evolution",
        ]
    )

    if rc2 != 0:
        print(f"⚠️ Radon MI failed: {err2}")
        mi_data = {}
    else:
        try:
            mi_data = json.loads(out2) if out2 else {}
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON from radon mi: {out2}")
            mi_data = {}

    # Raw Lines of Code 수집
    print("📊 Collecting raw metrics...")
    rc3, out3, err3 = _run(
        [
            sys.executable,
            "-m",
            "radon",
            "raw",
            "-j",
            "duri_core",
            "duri_brain",
            "duri_evolution",
        ]
    )

    raw_data = {}
    if rc3 == 0 and out3:
        try:
            raw_data = json.loads(out3)
        except json.JSONDecodeError:
            print(f"⚠️ Invalid JSON from radon raw: {out3}")

    # 메트릭 데이터 구성
    data = {
        "timestamp": pathlib.Path().cwd().stat().st_mtime,
        "cyclomatic_complexity": cc_data,
        "maintainability_index": mi_data,
        "raw_metrics": raw_data,
        "collection_status": {
            "cc_success": rc == 0,
            "mi_success": rc2 == 0,
            "raw_success": rc3 == 0,
        },
    }

    # 현재 메트릭 저장
    current_file = metrics_dir / "current.json"
    current_file.write_text(json.dumps(data, indent=2))
    print(f"✅ Wrote metrics to {current_file}")

    return data


if __name__ == "__main__":
    try:
        metrics = collect_static_metrics()

        # 간단한 요약 출력
        cc_count = len(metrics.get("cyclomatic_complexity", {}))
        mi_count = len(metrics.get("maintainability_index", {}))

        print("📈 Collected metrics:")
        print(f"  - Cyclomatic complexity: {cc_count} files")
        print(f"  - Maintainability index: {mi_count} files")
        print(f"  - Collection status: {metrics['collection_status']}")

    except Exception as e:
        print(f"❌ Error collecting metrics: {e}")
        sys.exit(1)
