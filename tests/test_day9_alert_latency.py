#!/usr/bin/env python3
"""
Day 9: 알림 지연 Gate 테스트
기존 Day 8 SLO Gate와 연동하여 Day 9 알림 지연 임계값을 검증합니다.
"""

import json
import unittest
from pathlib import Path
from typing import Dict, Any

class TestDay9AlertLatency(unittest.TestCase):
    """Day 9 알림 지연 Gate 테스트"""
    
    def setUp(self):
        """테스트 설정"""
        # Day 9 설정 로드
        config_path = Path("DuRiCore/config/thresholds.yaml")
        if config_path.exists():
            try:
                import yaml
                with config_path.open('r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
            except ImportError:
                # yaml이 없는 경우 기본 설정 사용
                self.config = self._get_default_config()
        else:
            self.config = self._get_default_config()
        
        # Day 9 요약 메트릭 로드
        summary_path = Path("var/metrics/day9_summary.json")
        if summary_path.exists():
            with summary_path.open('r', encoding='utf-8') as f:
                self.summary = json.load(f)
        else:
            self.fail("Day 9 요약 파일이 존재하지 않습니다: var/metrics/day9_summary.json")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """기본 Day 9 설정 반환"""
        return {
            "day9": {
                "alert_latency": {
                    "p95_ms_max": 5000,
                    "timeout_rate_max": 0.01
                }
            }
        }
    
    def test_day9_config_loaded(self):
        """Day 9 설정이 올바르게 로드되었는지 확인"""
        self.assertIn("day9", self.config, "Day 9 설정이 로드되지 않았습니다")
        self.assertIn("alert_latency", self.config["day9"], "Day 9 alert_latency 설정이 없습니다")
        
        alert_config = self.config["day9"]["alert_latency"]
        self.assertIn("p95_ms_max", alert_config, "p95_ms_max 설정이 없습니다")
        self.assertIn("timeout_rate_max", alert_config, "timeout_rate_max 설정이 없습니다")
    
    def test_day9_summary_loaded(self):
        """Day 9 요약 메트릭이 올바르게 로드되었는지 확인"""
        required_fields = ["count", "ok", "timeouts", "timeout_rate", "p95_ms"]
        for field in required_fields:
            self.assertIn(field, self.summary, f"Day 9 요약에 {field} 필드가 없습니다")
    
    def test_day9_alert_latency_p95(self):
        """Day 9 알림 지연 P95가 임계값을 초과하지 않는지 확인"""
        p95_ms = self.summary.get("p95_ms")
        self.assertIsNotNone(p95_ms, "p95_ms가 None입니다")
        
        threshold = self.config["day9"]["alert_latency"]["p95_ms_max"]
        self.assertLessEqual(
            p95_ms, threshold,
            f"알림 지연 P95 {p95_ms:.3f}ms가 임계값 {threshold}ms를 초과합니다"
        )
        
        print(f"[OK] 알림 지연 P95: {p95_ms:.3f}ms <= {threshold}ms")
    
    def test_day9_timeout_rate(self):
        """Day 9 타임아웃 비율이 임계값을 초과하지 않는지 확인"""
        timeout_rate = self.summary.get("timeout_rate")
        self.assertIsNotNone(timeout_rate, "timeout_rate가 None입니다")
        
        threshold = self.config["day9"]["alert_latency"]["timeout_rate_max"]
        self.assertLessEqual(
            timeout_rate, threshold,
            f"타임아웃 비율 {timeout_rate:.6f}가 임계값 {threshold:.6f}를 초과합니다"
        )
        
        print(f"[OK] 타임아웃 비율: {timeout_rate:.6f} <= {threshold:.6f}")
    
    def test_day9_simulation_completeness(self):
        """Day 9 시뮬레이션이 완전하게 실행되었는지 확인"""
        count = self.summary.get("count", 0)
        ok_count = self.summary.get("ok", 0)
        timeout_count = self.summary.get("timeouts", 0)
        
        # 최소 시뮬레이션 횟수 확인
        min_iterations = 10
        self.assertGreaterEqual(
            count, min_iterations,
            f"시뮬레이션 횟수가 부족합니다: {count} < {min_iterations}"
        )
        
        # 성공률 확인 (타임아웃이 너무 많으면 안됨)
        success_rate = ok_count / count if count > 0 else 0
        min_success_rate = 0.8  # 최소 80% 성공률
        self.assertGreaterEqual(
            success_rate, min_success_rate,
            f"시뮬레이션 성공률이 너무 낮습니다: {success_rate:.3f} < {min_success_rate}"
        )
        
        print(f"[OK] 시뮬레이션 완성도: {count}회 실행, {ok_count}회 성공, {timeout_count}회 타임아웃")
    
    def test_day9_metrics_consistency(self):
        """Day 9 메트릭의 일관성 확인"""
        p50_ms = self.summary.get("p50_ms")
        p95_ms = self.summary.get("p95_ms")
        max_ms = self.summary.get("max_ms")
        
        if all(x is not None for x in [p50_ms, p95_ms, max_ms]):
            # P50 <= P95 <= Max 관계 확인
            self.assertLessEqual(
                p50_ms, p95_ms,
                f"P50({p50_ms:.3f}ms) > P95({p95_ms:.3f}ms) - 통계적 오류"
            )
            
            self.assertLessEqual(
                p95_ms, max_ms,
                f"P95({p95_ms:.3f}ms) > Max({max_ms:.3f}ms) - 통계적 오류"
            )
            
            print(f"[OK] 메트릭 일관성: P50({p50_ms:.3f}ms) <= P95({p95_ms:.3f}ms) <= Max({max_ms:.3f}ms)")
    
    def test_day9_prometheus_export(self):
        """Day 9 메트릭이 Prometheus Export에 포함되었는지 확인"""
        prometheus_path = Path("var/metrics/prometheus.txt")
        self.assertTrue(
            prometheus_path.exists(),
            "Prometheus Export 파일이 존재하지 않습니다"
        )
        
        # Day 9 메트릭 확인
        prometheus_content = prometheus_path.read_text(encoding='utf-8')
        day9_metrics = [
            "alert_latency_p95_ms{source=\"day9\"}",
            "alert_timeout_rate{source=\"day9\"}"
        ]
        
        for metric in day9_metrics:
            self.assertIn(
                metric, prometheus_content,
                f"Prometheus Export에 Day 9 메트릭이 없습니다: {metric}"
            )
        
        print("[OK] Day 9 메트릭이 Prometheus Export에 포함되었습니다")

if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)
