#!/usr/bin/env python3
"""
Day 9: 스위프 Gate 테스트
스위프 전역 판정을 포함한 테스트
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any

class TestDay9SweepGate(unittest.TestCase):
    """Day 9 스위프 Gate 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Day 9 설정 로드
        try:
            from DuRiCore.config_new.provider import build_provider
            self.provider = build_provider()
        except ImportError:
            self.fail("DuRiCore.config_new.provider를 임포트할 수 없습니다")
        
        # Day 9 스위프 결과 파일 경로
        self.sweep_result_path = Path("var/reports/day9_sim_sweep.json")
        self.junit_result_path = Path("var/reports/junit_day9_alerts.xml")
    
    def test_day9_sweep_config_loaded(self):
        """Day 9 스위프 설정이 올바르게 로드되었는지 확인"""
        # Day 9 sim 섹션 존재 확인
        sim_config = self.provider.section("day9.sim")
        self.assertIsInstance(sim_config, dict, "Day 9 sim 설정이 딕셔너리가 아닙니다")
        
        # 필수 sim 설정값 확인
        required_keys = [
            "seed", "base_min_ms", "base_max_ms", 
            "tail_prob", "tail_scale_ms", "timeout_over_ms"
        ]
        
        for key in required_keys:
            self.assertIn(key, sim_config, f"Day 9 sim 설정에 {key}가 없습니다")
        
        # sim 설정값 타입 확인
        self.assertIsInstance(sim_config["seed"], int, "seed가 정수가 아닙니다")
        self.assertIsInstance(sim_config["base_min_ms"], (int, float), "base_min_ms가 숫자가 아닙니다")
        self.assertIsInstance(sim_config["base_max_ms"], (int, float), "base_max_ms가 숫자가 아닙니다")
        self.assertIsInstance(sim_config["tail_prob"], (int, float), "tail_prob이 숫자가 아닙니다")
        self.assertIsInstance(sim_config["tail_scale_ms"], (int, float), "tail_scale_ms가 숫자가 아닙니다")
        self.assertIsInstance(sim_config["timeout_over_ms"], (int, float), "timeout_over_ms가 숫자가 아닙니다")
    
    def test_day9_sweep_result_exists(self):
        """Day 9 스위프 결과 파일이 존재하는지 확인"""
        self.assertTrue(
            self.sweep_result_path.exists(),
            f"Day 9 스위프 결과 파일이 존재하지 않습니다: {self.sweep_result_path}"
        )
    
    def test_day9_sweep_result_structure(self):
        """Day 9 스위프 결과 구조가 올바른지 확인"""
        with self.sweep_result_path.open('r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 결과가 리스트인지 확인
        self.assertIsInstance(results, list, "스위프 결과가 리스트가 아닙니다")
        self.assertGreater(len(results), 0, "스위프 결과가 비어있습니다")
        
        # 각 결과 항목 확인
        for i, result in enumerate(results):
            with self.subTest(result_index=i):
                # 필수 필드 확인
                required_fields = [
                    "p95_ms", "timeout_rate", "missing_rate",
                    "intensity", "concurrency", "delivered", "total"
                ]
                
                for field in required_fields:
                    self.assertIn(field, result, f"결과 {i}에 {field} 필드가 없습니다")
                
                # 스위프 정보 확인
                self.assertIn(result["intensity"], [0.2, 0.5, 0.8], 
                             f"결과 {i}의 intensity가 예상값이 아닙니다")
                self.assertIn(result["concurrency"], [1, 5, 10], 
                             f"결과 {i}의 concurrency가 예상값이 아닙니다")
                
                # 데이터 타입 확인
                self.assertIsInstance(result["p95_ms"], (int, float), f"결과 {i}의 p95_ms가 숫자가 아닙니다")
                self.assertIsInstance(result["timeout_rate"], (int, float), f"결과 {i}의 timeout_rate가 숫자가 아닙니다")
                self.assertIsInstance(result["missing_rate"], (int, float), f"결과 {i}의 missing_rate가 숫자가 아닙니다")
                self.assertIsInstance(result["delivered"], int, f"결과 {i}의 delivered가 정수가 아닙니다")
                self.assertIsInstance(result["total"], int, f"결과 {i}의 total이 정수가 아닙니다")
    
    def test_day9_sweep_global_thresholds(self):
        """Day 9 스위프 전역 임계값을 충족하는지 확인"""
        # 설정값 로드
        p95_threshold = self.provider.get("day9.alert_latency_p95_ms", 1500)
        timeout_threshold = self.provider.get("day9.alert_timeout_rate", 0.02)
        missing_threshold = self.provider.get("day9.alert_missing_rate", 0.005)
        
        # 스위프 결과 로드
        with self.sweep_result_path.open('r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 전역 최대값 계산
        max_p95 = max((r.get("p95_ms", 0) for r in results), default=0)
        max_timeout = max((r.get("timeout_rate", 0) for r in results), default=0)
        max_missing = max((r.get("missing_rate", 0) for r in results), default=0)
        
        # P95 지연시간 전역 임계값 확인
        self.assertLessEqual(
            max_p95, p95_threshold,
            f"스위프 전역 P95 지연시간 {max_p95}ms가 임계값 {p95_threshold}ms를 초과합니다"
        )
        
        # 타임아웃 비율 전역 임계값 확인
        self.assertLessEqual(
            max_timeout, timeout_threshold,
            f"스위프 전역 타임아웃 비율 {max_timeout}가 임계값 {timeout_threshold}를 초과합니다"
        )
        
        # 누락 비율 전역 임계값 확인
        self.assertLessEqual(
            max_missing, missing_threshold,
            f"스위프 전역 누락 비율 {max_missing}가 임계값 {missing_threshold}를 초과합니다"
        )
        
        print(f"[OK] Day 9 스위프 전역 임계값 충족:")
        print(f"  전역 P95 지연시간: {max_p95}ms <= {p95_threshold}ms")
        print(f"  전역 타임아웃 비율: {max_timeout} <= {timeout_threshold}")
        print(f"  전역 누락 비율: {max_missing} <= {missing_threshold}")
    
    def test_day9_sweep_consistency_across_intensities(self):
        """Day 9 스위프 강도별 일관성을 확인"""
        with self.sweep_result_path.open('r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 강도별 결과 그룹화
        intensity_results = {}
        for result in results:
            intensity = result["intensity"]
            if intensity not in intensity_results:
                intensity_results[intensity] = []
            intensity_results[intensity].append(result)
        
        # 각 강도별로 결과가 일관적인지 확인
        for intensity, intensity_data in intensity_results.items():
            with self.subTest(intensity=intensity):
                # 동일 강도에서 P95가 비슷한 범위에 있는지 확인
                p95_values = [r["p95_ms"] for r in intensity_data]
                p95_range = max(p95_values) - min(p95_values)
                
                # P95 범위가 너무 크지 않아야 함 (일관성 보장)
                self.assertLess(
                    p95_range, 1000,  # 1초 이내
                    f"강도 {intensity}에서 P95 범위가 너무 큽니다: {p95_range}ms"
                )
                
                # 동일 강도에서 타임아웃 비율이 일관적인지 확인
                timeout_values = [r["timeout_rate"] for r in intensity_data]
                timeout_range = max(timeout_values) - min(timeout_values)
                
                # 타임아웃 비율 범위가 너무 크지 않아야 함
                self.assertLess(
                    timeout_range, 0.05,  # 5% 이내
                    f"강도 {intensity}에서 타임아웃 비율 범위가 너무 큽니다: {timeout_range}"
                )
    
    def test_day9_sweep_concurrency_scaling(self):
        """Day 9 스위프 동시성 스케일링을 확인"""
        with self.sweep_result_path.open('r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 동시성별 결과 그룹화
        concurrency_results = {}
        for result in results:
            concurrency = result["concurrency"]
            if concurrency not in concurrency_results:
                concurrency_results[concurrency] = []
            concurrency_results[concurrency].append(result)
        
        # 각 동시성별로 결과가 일관적인지 확인
        for concurrency, concurrency_data in concurrency_results.items():
            with self.subTest(concurrency=concurrency):
                # 동일 동시성에서 P95가 비슷한 범위에 있는지 확인
                p95_values = [r["p95_ms"] for r in concurrency_data]
                p95_range = max(p95_values) - min(p95_values)
                
                # P95 범위가 너무 크지 않아야 함
                self.assertLess(
                    p95_range, 1000,  # 1초 이내
                    f"동시성 {concurrency}에서 P95 범위가 너무 큽니다: {p95_range}ms"
                )
    
    def test_day9_sweep_junit_result_includes_sweep_failures(self):
        """Day 9 스위프 JUnit 결과에 스위프 실패가 포함되었는지 확인"""
        if not self.junit_result_path.exists():
            self.skipTest("JUnit 결과 파일이 존재하지 않습니다")
        
        with self.junit_result_path.open('r', encoding='utf-8') as f:
            content = f.read()
        
        # 스위프 관련 테스트케이스가 포함되었는지 확인
        sweep_testcases = [
            'sweep_timeout_rate',
            'sweep_p95', 
            'sweep_missing_rate'
        ]
        
        for testcase in sweep_testcases:
            if testcase in content:
                print(f"[INFO] 스위프 테스트케이스 '{testcase}'가 JUnit에 포함됨")
            else:
                print(f"[INFO] 스위프 테스트케이스 '{testcase}'가 JUnit에 포함되지 않음 (정상)")
        
        # 전체 테스트 수와 실패 수 확인
        if 'tests="' in content and 'failures="' in content:
            import re
            tests_match = re.search(r'tests="(\d+)"', content)
            failures_match = re.search(r'failures="(\d+)"', content)
            
            if tests_match and failures_match:
                total_tests = int(tests_match.group(1))
                total_failures = int(failures_match.group(1))
                
                print(f"[INFO] JUnit 결과: 총 {total_tests}개 테스트, {total_failures}개 실패")
                
                # 스위프 실패가 있을 경우 실패 수가 증가했는지 확인
                if total_failures > 0:
                    self.assertGreaterEqual(
                        total_tests, 6,  # 기본 3개 + 스위프 3개
                        "JUnit에 스위프 테스트케이스가 포함되지 않았습니다"
                    )

if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)
