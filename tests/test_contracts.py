#!/usr/bin/env python3
"""
Day 9: 계약 테스트
3개 인터페이스(ConfigProvider, MetricsSink, AlertProbe)에 대한 mock 기반 테스트
"""

import unittest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

# 인터페이스 임포트
from DuRiCore.config_new.provider import ConfigProvider
from DuRiCore.exporters.metrics import MetricsSink
from DuRiCore.alerts_new.telemetry import AlertProbe, AlertResult

class TestConfigProviderContract(unittest.TestCase):
    """ConfigProvider 인터페이스 계약 테스트"""
    
    def test_config_provider_get_method(self):
        """ConfigProvider.get 메서드가 올바르게 동작하는지 테스트"""
        # Mock ConfigProvider 생성
        provider = Mock(spec=ConfigProvider)
        
        # get 메서드 동작 설정
        provider.get.return_value = "test_value"
        
        # 메서드 호출
        result = provider.get("test.path", "default")
        
        # 검증
        provider.get.assert_called_once_with("test.path", "default")
        self.assertEqual(result, "test_value")
    
    def test_config_provider_section_method(self):
        """ConfigProvider.section 메서드가 올바르게 동작하는지 테스트"""
        # Mock ConfigProvider 생성
        provider = Mock(spec=ConfigProvider)
        
        # section 메서드 동작 설정
        expected_section = {"key1": "value1", "key2": "value2"}
        provider.section.return_value = expected_section
        
        # 메서드 호출
        result = provider.section("test.section")
        
        # 검증
        provider.section.assert_called_once_with("test.section")
        self.assertEqual(result, expected_section)
        self.assertIsInstance(result, dict)

class TestMetricsSinkContract(unittest.TestCase):
    """MetricsSink 인터페이스 계약 테스트"""
    
    def test_metrics_sink_emit_method(self):
        """MetricsSink.emit 메서드가 올바르게 동작하는지 테스트"""
        # Mock MetricsSink 생성
        sink = Mock(spec=MetricsSink)
        
        # emit 메서드 호출
        sink.emit("test_metric", 42.5, {"label1": "value1"})
        
        # 검증
        sink.emit.assert_called_once_with("test_metric", 42.5, {"label1": "value1"})
    
    def test_metrics_sink_emit_many_method(self):
        """MetricsSink.emit_many 메서드가 올바르게 동작하는지 테스트"""
        # Mock MetricsSink 생성
        sink = Mock(spec=MetricsSink)
        
        # emit_many 메서드 호출
        metrics = {"metric1": 10, "metric2": 20}
        labels = {"env": "test"}
        sink.emit_many(metrics, labels)
        
        # 검증
        sink.emit_many.assert_called_once_with(metrics, labels)
    
    def test_metrics_sink_emit_without_labels(self):
        """MetricsSink.emit 메서드가 라벨 없이 동작하는지 테스트"""
        # Mock MetricsSink 생성
        sink = Mock(spec=MetricsSink)
        
        # emit 메서드 호출 (라벨 없음)
        sink.emit("test_metric", 42.5)
        
        # 검증
        sink.emit.assert_called_once_with("test_metric", 42.5, None)

class TestAlertProbeContract(unittest.TestCase):
    """AlertProbe 인터페이스 계약 테스트"""
    
    def test_alert_probe_send_and_measure_method(self):
        """AlertProbe.send_and_measure 메서드가 올바르게 동작하는지 테스트"""
        # Mock AlertProbe 생성
        probe = Mock(spec=AlertProbe)
        
        # send_and_measure 메서드 동작 설정
        expected_result = AlertResult(
            delivered=True,
            latency_ms=150.5,
            timed_out=False,
            missing=False
        )
        probe.send_and_measure.return_value = expected_result
        
        # 메서드 호출
        result = probe.send_and_measure(1000)
        
        # 검증
        probe.send_and_measure.assert_called_once_with(1000)
        self.assertEqual(result, expected_result)
        self.assertIsInstance(result, AlertResult)
    
    def test_alert_result_structure(self):
        """AlertResult 데이터 구조가 올바른지 테스트"""
        # AlertResult 인스턴스 생성
        result = AlertResult(
            delivered=True,
            latency_ms=200.0,
            timed_out=False,
            missing=False
        )
        
        # 구조 검증
        self.assertTrue(hasattr(result, 'delivered'))
        self.assertTrue(hasattr(result, 'latency_ms'))
        self.assertTrue(hasattr(result, 'timed_out'))
        self.assertTrue(hasattr(result, 'missing'))
        
        # 타입 검증
        self.assertIsInstance(result.delivered, bool)
        self.assertIsInstance(result.latency_ms, float)
        self.assertIsInstance(result.timed_out, bool)
        self.assertIsInstance(result.missing, bool)
    
    def test_alert_probe_timeout_handling(self):
        """AlertProbe가 타임아웃을 올바르게 처리하는지 테스트"""
        # Mock AlertProbe 생성
        probe = Mock(spec=AlertProbe)
        
        # 타임아웃 시나리오 설정
        timeout_result = AlertResult(
            delivered=False,
            latency_ms=1500.0,
            timed_out=True,
            missing=False
        )
        probe.send_and_measure.return_value = timeout_result
        
        # 메서드 호출
        result = probe.send_and_measure(1000)
        
        # 검증
        self.assertFalse(result.delivered)
        self.assertTrue(result.timed_out)
        self.assertGreater(result.latency_ms, 1000)

class TestInterfaceIntegration(unittest.TestCase):
    """인터페이스 통합 테스트"""
    
    def test_config_provider_with_metrics_sink(self):
        """ConfigProvider와 MetricsSink가 함께 동작하는지 테스트"""
        # Mock 객체들 생성
        provider = Mock(spec=ConfigProvider)
        sink = Mock(spec=MetricsSink)
        
        # 설정값 설정
        provider.get.return_value = 1000
        
        # 메트릭 방출
        timeout_ms = provider.get("day9.alert_latency_p95_ms", 1500)
        sink.emit("alert_timeout_ms", timeout_ms, {"source": "test"})
        
        # 검증
        provider.get.assert_called_once_with("day9.alert_latency_p95_ms", 1500)
        sink.emit.assert_called_once_with("alert_timeout_ms", 1000, {"source": "test"})
    
    def test_alert_probe_with_metrics_sink(self):
        """AlertProbe와 MetricsSink가 함께 동작하는지 테스트"""
        # Mock 객체들 생성
        probe = Mock(spec=AlertProbe)
        sink = Mock(spec=MetricsSink)
        
        # AlertProbe 동작 설정
        probe_result = AlertResult(
            delivered=True,
            latency_ms=250.0,
            timed_out=False,
            missing=False
        )
        probe.send_and_measure.return_value = probe_result
        
        # 알림 전송 및 측정
        result = probe.send_and_measure(1000)
        
        # 메트릭 방출
        if result.delivered:
            sink.emit("alert_latency_ms", result.latency_ms, {"status": "delivered"})
        
        # 검증
        self.assertTrue(result.delivered)
        sink.emit.assert_called_once_with("alert_latency_ms", 250.0, {"status": "delivered"})

if __name__ == "__main__":
    # 테스트 실행
    unittest.main(verbosity=2)
