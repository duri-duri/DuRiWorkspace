#!/usr/bin/env python3
"""
DuRi 리스크 분석기 정책 테스트
"""

import pytest
import math
from DuRiCore.risk_management.intelligent_risk_analyzer import IntelligentRiskAnalyzer

class TestRiskPolicy:
    """리스크 분석기 정책 테스트"""
    
    def test_nan_is_zero_with_warn(self, caplog):
        """NaN 값은 0으로 클램프하고 경고 로그"""
        analyzer = IntelligentRiskAnalyzer()
        
        with caplog.at_level("WARNING"):
            result = analyzer.analyze_risk({"cpu_usage": math.nan, "memory_usage": 50})
            
            assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
            assert result["input_values"]["cpu_usage"] == 0.0
            assert any("NaN/Inf 입력 감지" in record.message for record in caplog.records)
    
    def test_inf_is_zero_with_warn(self, caplog):
        """Inf 값은 0으로 클램프하고 경고 로그"""
        analyzer = IntelligentRiskAnalyzer()
        
        with caplog.at_level("WARNING"):
            result = analyzer.analyze_risk({"cpu_usage": math.inf, "memory_usage": 50})
            
            assert result["risk_level"] in ["LOW", "MEDIUM", "HIGH"]
            assert result["input_values"]["cpu_usage"] == 0.0
            assert any("NaN/Inf 입력 감지" in record.message for record in caplog.records)
    
    def test_negative_values_clamped(self):
        """음수 값은 0으로 클램프"""
        analyzer = IntelligentRiskAnalyzer()
        
        result = analyzer.analyze_risk({"cpu_usage": -10, "memory_usage": -5})
        
        assert result["input_values"]["cpu_usage"] == 0.0
        assert result["input_values"]["memory_usage"] == 0.0
        assert result["risk_level"] == "LOW"
    
    def test_values_over_100_clamped(self):
        """100 초과 값은 100으로 클램프"""
        analyzer = IntelligentRiskAnalyzer()
        
        result = analyzer.analyze_risk({"cpu_usage": 150, "memory_usage": 200})
        
        assert result["input_values"]["cpu_usage"] == 100.0
        assert result["input_values"]["memory_usage"] == 100.0
        assert result["risk_level"] == "HIGH"
    
    def test_invalid_input_types_with_warn(self, caplog):
        """잘못된 타입 입력은 0으로 대체하고 경고 로그"""
        analyzer = IntelligentRiskAnalyzer()
        
        with caplog.at_level("WARNING"):
            result = analyzer.analyze_risk({"cpu_usage": "invalid", "memory_usage": None})
            
            assert result["input_values"]["cpu_usage"] == 0.0
            assert result["input_values"]["memory_usage"] == 0.0
            assert any("비정상 입력" in record.message for record in caplog.records)
    
    def test_empty_metrics_handled(self):
        """빈 메트릭은 기본값으로 처리"""
        analyzer = IntelligentRiskAnalyzer()
        
        result = analyzer.analyze_risk({})
        
        assert result["input_values"]["cpu_usage"] == 0.0
        assert result["input_values"]["memory_usage"] == 0.0
        assert result["risk_level"] == "LOW"
    
    def test_none_metrics_handled(self):
        """None 메트릭은 기본값으로 처리"""
        analyzer = IntelligentRiskAnalyzer()
        
        result = analyzer.analyze_risk(None)
        
        assert result["input_values"]["cpu_usage"] == 0.0
        assert result["input_values"]["memory_usage"] == 0.0
        assert result["risk_level"] == "LOW"
    
    def test_analysis_time_recorded(self):
        """분석 시간이 기록되는지 확인"""
        analyzer = IntelligentRiskAnalyzer()
        
        result = analyzer.analyze_risk({"cpu_usage": 50, "memory_usage": 60})
        
        assert "analysis_time_ms" in result
        assert isinstance(result["analysis_time_ms"], (int, float))
        assert result["analysis_time_ms"] >= 0
    
    def test_analysis_stats_tracked(self):
        """분석 통계가 추적되는지 확인"""
        analyzer = IntelligentRiskAnalyzer()
        
        # 초기 상태
        stats = analyzer.get_analysis_stats()
        initial_count = stats["total_analyses"]
        
        # 분석 실행
        analyzer.analyze_risk({"cpu_usage": 50, "memory_usage": 60})
        
        # 통계 업데이트 확인
        stats = analyzer.get_analysis_stats()
        assert stats["total_analyses"] == initial_count + 1
        assert stats["analyzer_status"] == "active"
