#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-4: 모니터링 패키지

성능 모니터링 및 알림 시스템을 제공하는 패키지입니다.
"""

# Alert System 모듈
from .alert_system.performance_alert_manager import (AlertChannel, AlertLevel,
                                                     AlertNotification,
                                                     AlertRule, AlertStatus,
                                                     PerformanceAlert,
                                                     PerformanceAlertManager)
# Performance Monitoring 모듈
from .performance_monitoring.metric_collector import (MetricCollection,
                                                      MetricCollector,
                                                      MetricStatus, MetricType,
                                                      PerformanceMetric)
from .performance_monitoring.performance_analyzer import (
    AnalysisType, OptimizationSuggestion, PerformanceAnalyzer,
    PerformancePattern, PerformancePrediction, PerformanceTrend,
    TrendDirection)

# 패키지 버전
__version__ = "2.4.0"

# 주요 클래스들
__all__ = [
    # Performance Monitoring
    "MetricCollector",
    "PerformanceMetric",
    "MetricCollection",
    "MetricType",
    "MetricStatus",
    "PerformanceAnalyzer",
    "PerformanceTrend",
    "PerformancePattern",
    "PerformancePrediction",
    "OptimizationSuggestion",
    "AnalysisType",
    "TrendDirection",
    # Alert System
    "PerformanceAlertManager",
    "AlertRule",
    "PerformanceAlert",
    "AlertNotification",
    "AlertLevel",
    "AlertStatus",
    "AlertChannel",
]
