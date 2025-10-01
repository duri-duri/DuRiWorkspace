#!/usr/bin/env python3
"""
A/B 테스트 러너 스모크 테스트
기존 테스트와 호환되는 새로운 스모크 테스트
"""
import json
import os
from pathlib import Path
import sys
import tempfile

import pytest

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ab_test_runner import ABTestRunner


class TestABRunnerSmoke:
    """A/B 테스트 러너 스모크 테스트"""

    def test_runner_initialization(self):
        """러너 초기화 테스트"""
        # 임시 설정 파일 생성
        config = {
            "day": 36,
            "variants": ["A", "B"],
            "metrics": {"primary": "latency_ms"},
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)
            assert runner.config["day"] == 36
            assert runner.config["variants"] == ["A", "B"]
        finally:
            os.unlink(config_path)

    def test_csv_to_variants(self):
        """CSV 변환 테스트"""
        # 임시 CSV 파일 생성
        csv_content = """variant,latency_ms
A,120
A,115
B,135
B,140"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            # 임시 설정 파일 생성
            config = {"day": 36}
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                import yaml

                yaml.dump(config, f)
                config_path = f.name

            try:
                runner = ABTestRunner(config_path)
                group_a, group_b = runner.csv_to_variants(
                    csv_path, "latency_ms", "variant"
                )

                assert len(group_a) == 2
                assert len(group_b) == 2
                assert group_a == [120, 115]
                assert group_b == [135, 140]
            finally:
                os.unlink(config_path)
        finally:
            os.unlink(csv_path)

    def test_run_from_csv(self):
        """CSV 실행 테스트"""
        # 임시 CSV 파일 생성
        csv_content = """variant,latency_ms
A,120
A,115
A,125
B,135
B,140
B,132"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(csv_content)
            csv_path = f.name

        try:
            # 임시 설정 파일 생성
            config = {"day": 36}
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                import yaml

                yaml.dump(config, f)
                config_path = f.name

            try:
                # 임시 출력 디렉토리 생성
                with tempfile.TemporaryDirectory() as output_dir:
                    runner = ABTestRunner(config_path)
                    result = runner.run_from_csv(
                        csv_path=csv_path,
                        metric_col="latency_ms",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="smoke_test",
                    )

                    # 결과 검증
                    assert result["source"] == "csv"
                    assert result["exp_id"] == "smoke_test"
                    assert result["n_A"] == 3
                    assert result["n_B"] == 3
                    assert "t_stat" in result
                    assert "df" in result
                    assert "objective_delta" in result
                    assert "cohens_d" in result
                    assert result["gate_pass"] is None
                    assert result["gate_reasons"] == ["csv_mode_no_gate"]

                    # 출력 파일 확인 (새로운 타임스탬프 구조)
                    output_dir_path = Path(output_dir) / "smoke_test"
                    assert output_dir_path.exists()

                    # 타임스탬프 파일 찾기
                    jsonl_files = list(output_dir_path.glob("smoke_test-*.jsonl"))
                    assert len(jsonl_files) == 1
                    output_file = jsonl_files[0]

                    # JSONL 파일 내용 확인
                    with open(output_file, "r") as f:
                        saved_result = json.loads(f.read())
                        assert saved_result["exp_id"] == "smoke_test"
                        assert "created_at_utc" in saved_result
                        assert "test_type" in saved_result
            finally:
                os.unlink(config_path)
        finally:
            os.unlink(csv_path)

    def test_legacy_mode_compatibility(self):
        """기존 모드 호환성 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 36, "variants": ["A", "B"]}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 기존 모드 실행 (게이트 없이)
            result = runner.run_legacy_mode(day=36, variant="A", seed=42)

            # 기존 결과 구조 확인
            assert "objective_delta" in result
            assert "t_stat" in result
            assert "gate_pass" in result
            assert "gate_reasons" in result
        finally:
            os.unlink(config_path)

    def test_error_handling(self):
        """오류 처리 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 36}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 존재하지 않는 CSV 파일
            with pytest.raises(FileNotFoundError):
                runner.run_from_csv(
                    csv_path="nonexistent.csv",
                    metric_col="latency_ms",
                    group_col="variant",
                )

            # 샘플 수 부족
            csv_content = """variant,latency_ms
A,120
B,135"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(csv_content)
                csv_path = f.name

            try:
                with pytest.raises(ValueError, match="Need ≥2 samples per variant"):
                    runner.run_from_csv(
                        csv_path=csv_path, metric_col="latency_ms", group_col="variant"
                    )
            finally:
                os.unlink(csv_path)
        finally:
            os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
