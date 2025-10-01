#!/usr/bin/env python3
"""
Day41~43: PoU Pilot Rollup 회귀 테스트
스키마/롤업 회귀 누락을 탐지하는 최소 테스트
"""

import json
import os
import pathlib
import subprocess
import tempfile

import pytest


def test_rollup_keys():
    """롤업 출력 키 보증 테스트"""
    # 롤업 실행
    subprocess.check_call(["make", "rollup"])

    # 메트릭 파일 로드
    metrics_file = "slo_sla_dashboard_v1/metrics.json"
    assert pathlib.Path(metrics_file).exists(), f"Metrics file {metrics_file} not found"

    with open(metrics_file, "r") as f:
        metrics = json.load(f)

    # 필수 키 존재 확인
    required_keys = ["p_error", "p_timeout", "explain_score", "total_entries"]
    for key in required_keys:
        assert key in metrics, f"Required key '{key}' missing from metrics"

    # 값 타입 확인
    assert isinstance(metrics["p_error"], (int, float)), "p_error must be numeric"
    assert isinstance(metrics["p_timeout"], (int, float)), "p_timeout must be numeric"
    assert isinstance(metrics["total_entries"], int), "total_entries must be integer"

    # explain_score는 None일 수 있음
    if metrics["explain_score"] is not None:
        assert isinstance(
            metrics["explain_score"], (int, float)
        ), "explain_score must be numeric"


def test_domain_alias_normalization():
    """도메인 별칭 정규화 테스트"""
    # 임시 로그 파일 생성
    with tempfile.TemporaryDirectory() as temp_dir:
        # 각 도메인별 별칭 테스트
        test_cases = [
            ("med", "medical"),
            ("code", "coding"),
            ("rehabilitation", "rehab"),
        ]

        for alias, canonical in test_cases:
            # 임시 로그 파일 생성
            log_file = os.path.join(temp_dir, f"{alias}_pilot_v2_logs", "logs.jsonl")
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            # 테스트 로그 엔트리 생성
            test_entry = {
                "timestamp": "2025-09-16T05:00:00.000Z",
                "domain": alias,
                "user_id": "test_user",
                "session_id": "test_session",
                "event_type": "task_complete",
                "metrics": {
                    "latency_ms": 500,
                    "success_rate": 0.95,
                    "quality_score": 85,
                    "error_count": 0,
                    "canary_flag": False,
                },
                "metadata": {
                    "version": "v1",
                    "environment": "prod",
                    "region": "us-west-2",
                },
                "schema_version": "1.0.0",
            }

            with open(log_file, "w") as f:
                f.write(json.dumps(test_entry) + "\n")

            # 검증 실행
            result = subprocess.run(
                ["python", "tools/validate_pilot_logs.py", "--log-file", log_file],
                capture_output=True,
                text=True,
            )

            # 정규화된 도메인으로 검증 성공 확인
            assert (
                result.returncode == 0
            ), f"Validation failed for {alias}: {result.stderr}"


def test_schema_version_required():
    """스키마 버전 필수 필드 테스트"""
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, "test_logs.jsonl")

        # schema_version 없는 엔트리 (실패해야 함)
        invalid_entry = {
            "timestamp": "2025-09-16T05:00:00.000Z",
            "domain": "medical",
            "user_id": "test_user",
            "session_id": "test_session",
            "event_type": "task_complete",
            "metrics": {
                "latency_ms": 500,
                "success_rate": 0.95,
                "quality_score": 85,
                "error_count": 0,
                "canary_flag": False,
            },
            "metadata": {"version": "v1", "environment": "prod", "region": "us-west-2"},
            # schema_version 누락
        }

        with open(log_file, "w") as f:
            f.write(json.dumps(invalid_entry) + "\n")

        # 검증 실행 (실패해야 함)
        result = subprocess.run(
            ["python", "tools/validate_pilot_logs.py", "--log-file", log_file],
            capture_output=True,
            text=True,
        )

        # 실패 확인
        assert result.returncode != 0, "Validation should fail without schema_version"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
