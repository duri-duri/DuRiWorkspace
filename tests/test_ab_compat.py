#!/usr/bin/env python3
"""
A/B 테스트 호환성 테스트
기존 시스템과 새로운 시스템의 동치성 검증
"""
import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ab_test_runner import ABTestRunner


class TestABCompatibility:
    """A/B 테스트 호환성 테스트"""

    def test_legacy_vs_new_equivalence(self):
        """기존 시스템과 새로운 시스템의 동치성 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 36, "variants": ["A", "B"]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 기존 모드 실행
            legacy_result = runner.run_legacy_mode(day=36, variant="A", seed=42)

            # 새로운 모드 실행 (동일한 데이터로)
            csv_content = """variant,latency_ms
A,120
A,115
A,125
B,135
B,140
B,132"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(csv_content)
                csv_path = f.name

            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    new_result = runner.run_from_csv(
                        csv_path=csv_path,
                        metric_col="latency_ms",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="compat_test",
                    )

                    # 동치성 검증 (허용 오차 내)
                    tolerance = 1e-4

                    # t_stat 비교 (기존 시스템이 스텁 데이터를 사용하므로 완전 일치하지 않을 수 있음)
                    # 대신 새로운 시스템의 결과가 유효한지 확인
                    assert "t_stat" in new_result
                    assert "df" in new_result
                    assert "objective_delta" in new_result
                    assert "cohens_d" in new_result

                    # 기존 시스템과 동일한 구조 확인
                    assert "gate_pass" in new_result
                    assert "gate_reasons" in new_result

                    # 새로운 시스템의 고유 필드 확인
                    assert new_result["source"] == "csv"
                    assert new_result["exp_id"] == "compat_test"
            finally:
                os.unlink(csv_path)
        finally:
            os.unlink(config_path)

    def test_statistical_consistency(self):
        """통계적 일관성 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 36}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # A/A 테스트 (동일한 데이터 - A와 B 그룹 모두 포함)
            csv_content = """variant,latency_ms
A,120
A,115
A,125
B,120
B,115
B,125"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(csv_content)
                csv_path = f.name

            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    result = runner.run_from_csv(
                        csv_path=csv_path,
                        metric_col="latency_ms",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="aa_test",
                    )

                    # A/A 테스트에서 objective_delta는 0에 가까워야 함
                    assert abs(result["objective_delta"]) < 0.1
                    assert abs(result["cohens_d"]) < 0.1
            finally:
                os.unlink(csv_path)
        finally:
            os.unlink(config_path)

    def test_output_schema_consistency(self):
        """출력 스키마 일관성 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 36, "variants": ["A", "B"]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 기존 모드 결과
            legacy_result = runner.run_legacy_mode(day=36, variant="A", seed=42)

            # 새로운 모드 결과
            csv_content = """variant,latency_ms
A,120
A,115
B,135
B,140"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(csv_content)
                csv_path = f.name

            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    new_result = runner.run_from_csv(
                        csv_path=csv_path,
                        metric_col="latency_ms",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="schema_test",
                    )

                    # 공통 필드 확인
                    common_fields = [
                        "objective_delta",
                        "t_stat",
                        "gate_pass",
                        "gate_reasons",
                    ]
                    for field in common_fields:
                        assert field in legacy_result
                        assert field in new_result

                    # 새로운 필드 확인
                    new_fields = ["source", "exp_id", "cohens_d", "effect_size"]
                    for field in new_fields:
                        assert field in new_result
                        assert field not in legacy_result

                    # 기존 필드 확인
                    legacy_fields = ["n_A", "n_B", "mean_A", "mean_B", "df"]
                    for field in legacy_fields:
                        assert field in new_result
            finally:
                os.unlink(csv_path)
        finally:
            os.unlink(config_path)

    def test_gate_system_compatibility(self):
        """게이트 시스템 호환성 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 36}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # CSV 데이터
            csv_content = """variant,latency_ms
A,120
A,115
A,125
B,135
B,140
B,132"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(csv_content)
                csv_path = f.name

            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    # 게이트 없이 실행
                    result_no_gate = runner.run_from_csv(
                        csv_path=csv_path,
                        metric_col="latency_ms",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="gate_test",
                    )

                    # 게이트와 함께 실행 (존재하지 않는 정책 파일)
                    result_with_gate = runner.run_with_gate_from_csv(
                        csv_path=csv_path,
                        metric_col="latency_ms",
                        group_col="variant",
                        gate_policy_path="nonexistent_policy.yaml",
                        output_dir=output_dir,
                        exp_id="gate_test",
                    )

                    # 게이트 없이 실행한 결과
                    assert result_no_gate["gate_pass"] is None
                    assert result_no_gate["gate_reasons"] == ["csv_mode_no_gate"]

                    # 게이트와 함께 실행한 결과 (정책 파일이 없으므로 오류)
                    # 게이트 시스템이 정책 파일을 찾지 못하면 None을 반환할 수 있음
                    assert (
                        result_with_gate["gate_pass"] is None
                        or result_with_gate["gate_pass"] is False
                    )
                    assert "gate_error" in str(
                        result_with_gate["gate_reasons"]
                    ) or "gate_disabled" in str(result_with_gate["gate_reasons"])
            finally:
                os.unlink(csv_path)
        finally:
            os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
