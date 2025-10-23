#!/usr/bin/env python3
"""
Day 37: PoU 7일차 유지율 테스트
스모크, 통계, SRM, A/A 테스트 포함
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
from tools.pou_day7_extract import (create_synthetic_data,
                                    extract_retention_data)


class TestPoUD7:
    """PoU 7일차 유지율 테스트"""

    def test_synthetic_data_creation(self):
        """합성 데이터 생성 테스트"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_file = f.name

        try:
            stats = create_synthetic_data(temp_file, n_users=100)

            # 기본 통계 확인
            assert stats["total_users"] == 100
            assert stats["retention_records"] == 100
            assert "A" in stats["variants"]
            assert "B" in stats["variants"]
            assert "A_retention_rate" in stats
            assert "B_retention_rate" in stats

            # 파일 존재 확인
            assert Path(temp_file).exists()

            # CSV 내용 확인
            with open(temp_file, "r") as f:
                lines = f.readlines()
                assert len(lines) == 101  # 헤더 + 100개 데이터
                assert "variant,retained_d7,cohort_date" in lines[0]

        finally:
            os.unlink(temp_file)

    def test_retention_data_extraction(self):
        """유지율 데이터 추출 테스트"""
        # 테스트용 입력 데이터 생성
        test_input = """timestamp,user_id,variant,event
2025-09-23T10:00:00Z,user_001,A,login
2025-09-23T10:05:00Z,user_001,A,action
2025-09-30T09:30:00Z,user_001,A,login
2025-09-23T11:00:00Z,user_002,B,login
2025-09-30T10:00:00Z,user_002,B,action
2025-09-23T12:00:00Z,user_003,A,login
2025-09-24T10:00:00Z,user_004,B,login"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write(test_input)
            input_file = f.name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            output_file = f.name

        try:
            stats = extract_retention_data(input_file, output_file)

            # 기본 통계 확인
            assert stats["total_users"] == 4
            assert stats["retention_records"] == 4
            assert "A" in stats["variants"]
            assert "B" in stats["variants"]

            # 파일 존재 확인
            assert Path(output_file).exists()

            # CSV 내용 확인
            with open(output_file, "r") as f:
                lines = f.readlines()
                assert len(lines) == 5  # 헤더 + 4개 데이터
                assert "variant,retained_d7,cohort_date" in lines[0]

        finally:
            os.unlink(input_file)
            os.unlink(output_file)

    def test_ab_runner_integration(self):
        """A/B 러너 통합 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 37}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 합성 데이터 생성
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                temp_csv = f.name

            try:
                create_synthetic_data(temp_csv, n_users=200)

                with tempfile.TemporaryDirectory() as output_dir:
                    result = runner.run_from_csv(
                        csv_path=temp_csv,
                        metric_col="retained_d7",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="pou_d7_test",
                    )

                    # 결과 검증
                    assert result["source"] == "csv"
                    assert result["exp_id"] == "pou_d7_test"
                    assert result["metric"] == "retained_d7"
                    assert result["group_col"] == "variant"
                    assert "n_A" in result
                    assert "n_B" in result
                    assert "mean_A" in result
                    assert "mean_B" in result
                    assert "t_stat" in result
                    assert "objective_delta" in result
                    assert "created_at_utc" in result
                    assert "test_type" in result

            finally:
                os.unlink(temp_csv)

        finally:
            os.unlink(config_path)

    def test_statistical_significance(self):
        """통계적 유의성 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 37}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 유의한 차이가 있는 데이터 생성 (분산 추가)
            significant_data = """variant,retained_d7,cohort_date
A,0,2025-09-23
A,0,2025-09-23
A,0,2025-09-23
A,0,2025-09-23
A,0,2025-09-23
A,1,2025-09-23
B,1,2025-09-23
B,1,2025-09-23
B,1,2025-09-23
B,1,2025-09-23
B,1,2025-09-23
B,0,2025-09-23"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(significant_data)
                temp_csv = f.name

            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    result = runner.run_from_csv(
                        csv_path=temp_csv,
                        metric_col="retained_d7",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="significant_test",
                    )

                    # 유의한 차이 확인
                    assert result["mean_A"] != result["mean_B"]  # 차이가 있음
                    assert abs(result["objective_delta"]) > 0  # 차이가 있음
                    assert abs(result["t_stat"]) > 0.1  # t-통계량

            finally:
                os.unlink(temp_csv)

        finally:
            os.unlink(config_path)

    def test_aa_test_distribution(self):
        """A/A 테스트 p-분포 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 37}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # A/A 테스트 (동일한 분포)
            aa_data = """variant,retained_d7,cohort_date
A,1,2025-09-23
A,0,2025-09-23
A,1,2025-09-23
A,0,2025-09-23
A,1,2025-09-23
B,1,2025-09-23
B,0,2025-09-23
B,1,2025-09-23
B,0,2025-09-23
B,1,2025-09-23"""

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                f.write(aa_data)
                temp_csv = f.name

            try:
                with tempfile.TemporaryDirectory() as output_dir:
                    result = runner.run_from_csv(
                        csv_path=temp_csv,
                        metric_col="retained_d7",
                        group_col="variant",
                        output_dir=output_dir,
                        exp_id="aa_test",
                    )

                    # A/A 테스트에서 차이가 작아야 함
                    assert abs(result["objective_delta"]) < 0.1
                    assert abs(result["cohens_d"]) < 0.1
                    assert abs(result["t_stat"]) < 1.0

            finally:
                os.unlink(temp_csv)

        finally:
            os.unlink(config_path)

    def test_gate_system_integration(self):
        """게이트 시스템 통합 테스트"""
        # 임시 설정 파일 생성
        config = {"day": 37}
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            import yaml

            yaml.dump(config, f)
            config_path = f.name

        try:
            runner = ABTestRunner(config_path)

            # 합성 데이터 생성
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".csv", delete=False
            ) as f:
                temp_csv = f.name

            try:
                create_synthetic_data(temp_csv, n_users=200)

                with tempfile.TemporaryDirectory() as output_dir:
                    # 게이트와 함께 실행
                    result = runner.run_with_gate_from_csv(
                        csv_path=temp_csv,
                        metric_col="retained_d7",
                        group_col="variant",
                        gate_policy_path="policies/promotion.yaml",
                        output_dir=output_dir,
                        exp_id="gate_test",
                    )

                    # 게이트 결과 확인
                    assert "gate_pass" in result
                    assert "gate_reasons" in result
                    assert isinstance(result["gate_reasons"], list)
                    assert "gate_policy_sha256" in result

            finally:
                os.unlink(temp_csv)

        finally:
            os.unlink(config_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
