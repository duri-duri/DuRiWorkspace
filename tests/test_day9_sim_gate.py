#!/usr/bin/env python3
"""
Day 9: 시뮬레이션 Gate 테스트
seed 고정으로 p95/timeout/missing 판정을 수행합니다.
"""

import unittest
import json
from pathlib import Path
from typing import Dict, Any

class TestDay9SimGate(unittest.TestCase):
    """Day 9 시뮬레이션 Gate 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Day 9 설정 로드
        try:
            from DuRiCore.config_new.provider import build_provider
            self.provider = build_provider()
        except ImportError:
            self.fail("DuRiCore.config_new.provider를 임포트할 수 없습니다")
        
        # Day 9 결과 파일 경로
        self.latency_result_path = Path("var/reports/day9_latency_result.json")
        self.sweep_result_path = Path("var/reports/day9_sim_sweep.json")
        self.junit_result_path = Path("var/reports/junit_day9_alerts.xml")
    
    def test_day9_config_loaded(self):
        """Day 9 설정이 올바르게 로드되었는지 확인"""
        # Day 9 섹션 존재 확인
        day9_config = self.provider.section("day9")
        self.assertIsInstance(day9_config, dict, "Day 9 설정이 딕셔너리가 아닙니다")
        
        # 필수 설정값 확인
        required_keys = [
            "alert_latency_p95_ms",
            "alert_timeout_rate", 
            "alert_missing_rate",
            "sweep"
        ]
        
        for key in required_keys:
            self.assertIn(key, day9_config, f"Day 9 설정에 {key}가 없습니다")
        
        # 스위프 설정 확인
        sweep_config = day9_config.get("sweep", {})
        self.assertIn("intensities", sweep_config, "스위프 설정에 intensities가 없습니다")
        self.assertIn("concurrencies", sweep_config, "스위프 설정에 concurrencies가 없습니다")
    
    def test_day9_latency_result_exists(self):
        """Day 9 단일 측정 결과 파일이 존재하는지 확인"""
        self.assertTrue(
            self.latency_result_path.exists(),
            f"Day 9 단일 측정 결과 파일이 존재하지 않습니다: {self.latency_result_path}"
        )
    
    def test_day9_sweep_result_exists(self):
        """Day 9 스위프 결과 파일이 존재하는지 확인"""
        self.assertTrue(
            self.sweep_result_path.exists(),
            f"Day 9 스위프 결과 파일이 존재하지 않습니다: {self.sweep_result_path}"
        )
    
    def test_day9_latency_result_structure(self):
        """Day 9 단일 측정 결과 구조가 올바른지 확인"""
        with self.latency_result_path.open('r', encoding='utf-8') as f:
            result = json.load(f)
        
        # 필수 필드 확인
        required_fields = [
            "p95_ms", "timeout_rate", "missing_rate", 
            "delivered", "total"
        ]
        
        for field in required_fields:
            self.assertIn(field, result, f"결과에 {field} 필드가 없습니다")
        
        # 데이터 타입 확인
        self.assertIsInstance(result["p95_ms"], (int, float), "p95_ms가 숫자가 아닙니다")
        self.assertIsInstance(result["timeout_rate"], (int, float), "timeout_rate가 숫자가 아닙니다")
        self.assertIsInstance(result["missing_rate"], (int, float), "missing_rate가 숫자가 아닙니다")
        self.assertIsInstance(result["delivered"], int, "delivered가 정수가 아닙니다")
        self.assertIsInstance(result["total"], int, "total이 정수가 아닙니다")
    
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
                    "intensity", "concurrency"
                ]
                
                for field in required_fields:
                    self.assertIn(field, result, f"결과 {i}에 {field} 필드가 없습니다")
                
                # 스위프 정보 확인
                self.assertIn(result["intensity"], [0.2, 0.5, 0.8], 
                             f"결과 {i}의 intensity가 예상값이 아닙니다")
                self.assertIn(result["concurrency"], [1, 5, 10], 
                             f"결과 {i}의 concurrency가 예상값이 아닙니다")
    
    def test_day9_metrics_thresholds(self):
        """Day 9 메트릭이 임계값을 충족하는지 확인"""
        # 설정값 로드
        p95_threshold = self.provider.get("day9.alert_latency_p95_ms", 1500)
        timeout_threshold = self.provider.get("day9.alert_timeout_rate", 0.02)
        missing_threshold = self.provider.get("day9.alert_missing_rate", 0.005)
        
        # 단일 측정 결과 로드
        with self.latency_result_path.open('r', encoding='utf-8') as f:
            latency_result = json.load(f)
        
        # P95 지연시간 임계값 확인
        p95_actual = latency_result["p95_ms"]
        self.assertLessEqual(
            p95_actual, p95_threshold,
            f"P95 지연시간 {p95_actual}ms가 임계값 {p95_threshold}ms를 초과합니다"
        )
        
        # 타임아웃 비율 임계값 확인
        timeout_actual = latency_result["timeout_rate"]
        self.assertLessEqual(
            timeout_actual, timeout_threshold,
            f"타임아웃 비율 {timeout_actual}가 임계값 {timeout_threshold}를 초과합니다"
        )
        
        # 누락 비율 임계값 확인
        missing_actual = latency_result["missing_rate"]
        self.assertLessEqual(
            missing_actual, missing_threshold,
            f"누락 비율 {missing_actual}가 임계값 {missing_threshold}를 초과합니다"
        )
        
        print(f"[OK] Day 9 메트릭 임계값 충족:")
        print(f"  P95 지연시간: {p95_actual}ms <= {p95_threshold}ms")
        print(f"  타임아웃 비율: {timeout_actual} <= {timeout_threshold}")
        print(f"  누락 비율: {missing_actual} <= {missing_threshold}")
    
    def test_day9_sweep_consistency(self):
        """Day 9 스위프 결과의 일관성을 확인"""
        with self.sweep_result_path.open('r', encoding='utf-8') as f:
            results = json.load(f)
        
        # 강도별 결과 일관성 확인
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
    
    def test_day9_junit_result_exists(self):
        """Day 9 JUnit 결과 파일이 존재하는지 확인"""
        self.assertTrue(
            self.junit_result_path.exists(),
            f"Day 9 JUnit 결과 파일이 존재하지 않습니다: {self.junit_result_path}"
        )
    
    def test_day9_junit_result_structure(self):
        """Day 9 JUnit 결과 파일 구조가 올바른지 확인"""
        with self.junit_result_path.open('r', encoding='utf-8') as f:
            content = f.read()
        
        # XML 구조 확인
        self.assertIn('<?xml version="1.0" encoding="UTF-8"?>', content, "XML 선언이 없습니다")
        self.assertIn('<testsuite name="day9_alerts"', content, "testsuite 태그가 없습니다")
        self.assertIn('<testcase classname="alerts" name="p95_latency"', content, "p95_latency 테스트케이스가 없습니다")
        self.assertIn('<testcase classname="alerts" name="timeout_rate"', content, "timeout_rate 테스트케이스가 없습니다")
        self.assertIn('<testcase classname="alerts" name="missing_rate"', content, "missing_rate 테스트케이스가 없습니다")
        
        # 실패 여부 확인
        if 'failures="0"' in content:
            print("[OK] Day 9 JUnit 결과: 모든 테스트 통과")
        else:
            print("[WARNING] Day 9 JUnit 결과: 일부 테스트 실패")

if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)
