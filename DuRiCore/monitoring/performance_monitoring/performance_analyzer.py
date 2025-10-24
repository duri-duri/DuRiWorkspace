#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-4: 성능 분석 모듈

성능 메트릭을 분석하고 트렌드를 파악하는 모듈입니다.
- 성능 트렌드 분석
- 성능 패턴 감지
- 성능 예측
- 성능 최적화 제안
"""

import logging
import statistics
import time
import uuid
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

from scipy import stats

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """분석 유형"""

    TREND = "trend"
    PATTERN = "pattern"
    PREDICTION = "prediction"
    OPTIMIZATION = "optimization"
    ANOMALY = "anomaly"


class TrendDirection(Enum):
    """트렌드 방향"""

    IMPROVING = "improving"
    DECLINING = "declining"
    STABLE = "stable"
    FLUCTUATING = "fluctuating"


@dataclass
class PerformanceTrend:
    """성능 트렌드"""

    trend_id: str
    metric_name: str
    trend_direction: TrendDirection
    trend_strength: float  # 0.0-1.0
    confidence: float  # 0.0-1.0
    start_time: datetime
    end_time: datetime
    data_points: int
    slope: float
    intercept: float
    r_squared: float
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformancePattern:
    """성능 패턴"""

    pattern_id: str
    pattern_type: str
    pattern_description: str
    metric_name: str
    frequency: float
    amplitude: float
    phase: float
    confidence: float  # 0.0-1.0
    detected_at: datetime = field(default_factory=datetime.now)


@dataclass
class PerformancePrediction:
    """성능 예측"""

    prediction_id: str
    metric_name: str
    predicted_value: float
    confidence: float  # 0.0-1.0
    prediction_horizon: timedelta
    prediction_time: datetime
    factors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class OptimizationSuggestion:
    """최적화 제안"""

    suggestion_id: str
    suggestion_type: str
    suggestion_title: str
    suggestion_description: str
    expected_improvement: float  # 0.0-1.0
    implementation_difficulty: str  # easy, medium, hard
    priority: str  # low, medium, high, critical
    affected_metrics: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class PerformanceAnalyzer:
    """성능 분석기"""

    def __init__(self):
        """초기화"""
        self.trends: List[PerformanceTrend] = []
        self.patterns: List[PerformancePattern] = []
        self.predictions: List[PerformancePrediction] = []
        self.optimization_suggestions: List[OptimizationSuggestion] = []

        # 분석 설정
        self.analysis_config = {
            "trend_analysis_window": timedelta(hours=1),
            "pattern_detection_threshold": 0.7,
            "prediction_horizon": timedelta(hours=1),
            "min_data_points": 10,
            "confidence_threshold": 0.6,
        }

        # 성능 메트릭
        self.performance_metrics = {
            "total_trends_analyzed": 0,
            "total_patterns_detected": 0,
            "total_predictions_made": 0,
            "total_suggestions_generated": 0,
            "average_analysis_time": 0.0,
        }

        logger.info("성능 분석기 초기화 완료")

    async def analyze_trends(self, metrics: List[Any], metric_name: str) -> Optional[PerformanceTrend]:
        """트렌드 분석"""
        try:
            if len(metrics) < self.analysis_config["min_data_points"]:
                logger.warning(f"트렌드 분석을 위한 데이터가 부족합니다: {len(metrics)}개")
                return None

            # 시간과 값 추출
            timestamps = [m.timestamp for m in metrics]
            values = [m.value for m in metrics]

            # 시간을 숫자로 변환 (초 단위)
            time_nums = [(t - timestamps[0]).total_seconds() for t in timestamps]

            # 선형 회귀 분석
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_nums, values)
            r_squared = r_value**2

            # 트렌드 방향 결정
            if abs(slope) < 0.01:
                trend_direction = TrendDirection.STABLE
            elif slope > 0:
                trend_direction = TrendDirection.IMPROVING
            else:
                trend_direction = TrendDirection.DECLINING

            # 트렌드 강도 계산
            trend_strength = min(1.0, abs(slope) * 100)

            # 신뢰도 계산
            confidence = min(1.0, r_squared * 0.8 + 0.2)

            trend = PerformanceTrend(
                trend_id=f"trend_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                metric_name=metric_name,
                trend_direction=trend_direction,
                trend_strength=trend_strength,
                confidence=confidence,
                start_time=timestamps[0],
                end_time=timestamps[-1],
                data_points=len(metrics),
                slope=slope,
                intercept=intercept,
                r_squared=r_squared,
            )

            self.trends.append(trend)
            self.performance_metrics["total_trends_analyzed"] += 1

            logger.info(f"트렌드 분석 완료: {trend.trend_id} ({trend_direction.value})")
            return trend

        except Exception as e:
            logger.error(f"트렌드 분석 실패: {e}")
            return None

    async def detect_patterns(self, metrics: List[Any], metric_name: str) -> List[PerformancePattern]:
        """패턴 감지"""
        try:
            patterns = []

            if len(metrics) < self.analysis_config["min_data_points"]:
                return patterns

            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]

            # 1. 주기성 패턴 감지
            periodic_pattern = await self._detect_periodic_pattern(values, timestamps, metric_name)
            if periodic_pattern:
                patterns.append(periodic_pattern)

            # 2. 계절성 패턴 감지
            seasonal_pattern = await self._detect_seasonal_pattern(values, timestamps, metric_name)
            if seasonal_pattern:
                patterns.append(seasonal_pattern)

            # 3. 이상 패턴 감지
            anomaly_pattern = await self._detect_anomaly_pattern(values, timestamps, metric_name)
            if anomaly_pattern:
                patterns.append(anomaly_pattern)

            self.patterns.extend(patterns)
            self.performance_metrics["total_patterns_detected"] += len(patterns)

            logger.info(f"패턴 감지 완료: {len(patterns)}개 패턴 발견")
            return patterns

        except Exception as e:
            logger.error(f"패턴 감지 실패: {e}")
            return []

    async def predict_performance(self, metrics: List[Any], metric_name: str) -> Optional[PerformancePrediction]:
        """성능 예측"""
        try:
            if len(metrics) < self.analysis_config["min_data_points"]:
                return None

            values = [m.value for m in metrics]
            timestamps = [m.timestamp for m in metrics]

            # 간단한 선형 예측
            time_nums = [(t - timestamps[0]).total_seconds() for t in timestamps]
            slope, intercept, r_value, p_value, std_err = stats.linregress(time_nums, values)

            # 예측 시간 계산
            prediction_time = timestamps[-1] + self.analysis_config["prediction_horizon"]
            prediction_time_num = (prediction_time - timestamps[0]).total_seconds()

            # 예측값 계산
            predicted_value = slope * prediction_time_num + intercept

            # 신뢰도 계산
            confidence = min(1.0, r_value**2 * 0.8 + 0.2)

            prediction = PerformancePrediction(
                prediction_id=f"pred_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                metric_name=metric_name,
                predicted_value=predicted_value,
                confidence=confidence,
                prediction_horizon=self.analysis_config["prediction_horizon"],
                prediction_time=prediction_time,
                factors=["linear_trend", "historical_data"],
            )

            self.predictions.append(prediction)
            self.performance_metrics["total_predictions_made"] += 1

            logger.info(f"성능 예측 완료: {prediction.prediction_id} ({predicted_value:.2f})")
            return prediction

        except Exception as e:
            logger.error(f"성능 예측 실패: {e}")
            return None

    async def generate_optimization_suggestions(
        self, metrics: List[Any], metric_name: str
    ) -> List[OptimizationSuggestion]:
        """최적화 제안 생성"""
        try:
            suggestions = []

            if len(metrics) < self.analysis_config["min_data_points"]:
                return suggestions

            values = [m.value for m in metrics]
            current_value = values[-1]
            avg_value = statistics.mean(values)

            # 1. 성능 저하 감지
            if current_value < avg_value * 0.8:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"sugg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    suggestion_type="performance_improvement",
                    suggestion_title=f"{metric_name} 성능 개선",
                    suggestion_description=f"{metric_name}의 성능이 평균 대비 20% 이상 저하되었습니다. 최적화가 필요합니다.",  # noqa: E501
                    expected_improvement=0.2,
                    implementation_difficulty="medium",
                    priority="high",
                    affected_metrics=[metric_name],
                )
                suggestions.append(suggestion)

            # 2. 변동성 감지
            std_dev = statistics.stdev(values) if len(values) > 1 else 0
            if std_dev > avg_value * 0.3:
                suggestion = OptimizationSuggestion(
                    suggestion_id=f"sugg_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    suggestion_type="stability_improvement",
                    suggestion_title=f"{metric_name} 안정성 개선",
                    suggestion_description=f"{metric_name}의 변동성이 높습니다. 안정화가 필요합니다.",
                    expected_improvement=0.15,
                    implementation_difficulty="hard",
                    priority="medium",
                    affected_metrics=[metric_name],
                )
                suggestions.append(suggestion)

            self.optimization_suggestions.extend(suggestions)
            self.performance_metrics["total_suggestions_generated"] += len(suggestions)

            logger.info(f"최적화 제안 생성 완료: {len(suggestions)}개 제안")
            return suggestions

        except Exception as e:
            logger.error(f"최적화 제안 생성 실패: {e}")
            return []

    async def _detect_periodic_pattern(
        self, values: List[float], timestamps: List[datetime], metric_name: str
    ) -> Optional[PerformancePattern]:
        """주기성 패턴 감지"""
        try:
            if len(values) < 20:
                return None

            # FFT를 사용한 주기성 분석 (간단한 구현)
            time_diffs = [(timestamps[i] - timestamps[i - 1]).total_seconds() for i in range(1, len(timestamps))]
            avg_time_diff = statistics.mean(time_diffs)

            # 간단한 주기성 검사
            if len(set(time_diffs)) < len(time_diffs) * 0.8:
                return PerformancePattern(
                    pattern_id=f"pattern_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    pattern_type="periodic",
                    pattern_description=f"{metric_name}에서 주기적 패턴이 감지되었습니다.",
                    metric_name=metric_name,
                    frequency=1.0 / avg_time_diff if avg_time_diff > 0 else 0.0,
                    amplitude=statistics.stdev(values) if len(values) > 1 else 0.0,
                    phase=0.0,
                    confidence=0.7,
                )

            return None

        except Exception as e:
            logger.error(f"주기성 패턴 감지 실패: {e}")
            return None

    async def _detect_seasonal_pattern(
        self, values: List[float], timestamps: List[datetime], metric_name: str
    ) -> Optional[PerformancePattern]:
        """계절성 패턴 감지"""
        try:
            if len(values) < 24:
                return None

            # 시간대별 평균 계산
            hourly_averages = defaultdict(list)
            for i, timestamp in enumerate(timestamps):
                hour = timestamp.hour
                hourly_averages[hour].append(values[i])

            # 시간대별 변동성 계산
            hourly_std = {
                hour: statistics.stdev(vals) if len(vals) > 1 else 0 for hour, vals in hourly_averages.items()
            }

            # 계절성 검사
            if len(hourly_std) > 6 and max(hourly_std.values()) > min(hourly_std.values()) * 2:
                return PerformancePattern(
                    pattern_id=f"pattern_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    pattern_type="seasonal",
                    pattern_description=f"{metric_name}에서 계절적 패턴이 감지되었습니다.",
                    metric_name=metric_name,
                    frequency=24.0,  # 24시간 주기
                    amplitude=max(hourly_std.values()),
                    phase=0.0,
                    confidence=0.6,
                )

            return None

        except Exception as e:
            logger.error(f"계절성 패턴 감지 실패: {e}")
            return None

    async def _detect_anomaly_pattern(
        self, values: List[float], timestamps: List[datetime], metric_name: str
    ) -> Optional[PerformancePattern]:
        """이상 패턴 감지"""
        try:
            if len(values) < 10:
                return None

            mean_value = statistics.mean(values)
            std_value = statistics.stdev(values) if len(values) > 1 else 0

            # 이상값 감지 (3-sigma 규칙)
            anomalies = []
            for i, value in enumerate(values):
                if abs(value - mean_value) > 3 * std_value:
                    anomalies.append(i)

            if len(anomalies) > 0:
                return PerformancePattern(
                    pattern_id=f"pattern_{int(time.time())}_{uuid.uuid4().hex[:8]}",
                    pattern_type="anomaly",
                    pattern_description=f"{metric_name}에서 {len(anomalies)}개의 이상 패턴이 감지되었습니다.",
                    metric_name=metric_name,
                    frequency=len(anomalies) / len(values),
                    amplitude=max(values) - min(values),
                    phase=0.0,
                    confidence=0.8,
                )

            return None

        except Exception as e:
            logger.error(f"이상 패턴 감지 실패: {e}")
            return None

    async def get_analysis_report(self, metric_name: str = None) -> Dict[str, Any]:
        """분석 보고서 생성"""
        try:
            report = {
                "analysis_summary": {
                    "total_trends": len(self.trends),
                    "total_patterns": len(self.patterns),
                    "total_predictions": len(self.predictions),
                    "total_suggestions": len(self.optimization_suggestions),
                },
                "performance_metrics": self.performance_metrics.copy(),
                "recent_trends": [],
                "recent_patterns": [],
                "recent_predictions": [],
                "recent_suggestions": [],
            }

            # 최근 트렌드
            recent_trends = [t for t in self.trends if not metric_name or t.metric_name == metric_name]
            report["recent_trends"] = [self._trend_to_dict(t) for t in recent_trends[-5:]]

            # 최근 패턴
            recent_patterns = [p for p in self.patterns if not metric_name or p.metric_name == metric_name]
            report["recent_patterns"] = [self._pattern_to_dict(p) for p in recent_patterns[-5:]]

            # 최근 예측
            recent_predictions = [
                pred for pred in self.predictions if not metric_name or pred.metric_name == metric_name
            ]
            report["recent_predictions"] = [self._prediction_to_dict(pred) for pred in recent_predictions[-5:]]

            # 최근 제안
            recent_suggestions = [
                s for s in self.optimization_suggestions if not metric_name or metric_name in s.affected_metrics
            ]
            report["recent_suggestions"] = [self._suggestion_to_dict(s) for s in recent_suggestions[-5:]]

            return report

        except Exception as e:
            logger.error(f"분석 보고서 생성 실패: {e}")
            return {}

    def _trend_to_dict(self, trend: PerformanceTrend) -> Dict[str, Any]:
        """트렌드를 딕셔너리로 변환"""
        return {
            "trend_id": trend.trend_id,
            "metric_name": trend.metric_name,
            "trend_direction": trend.trend_direction.value,
            "trend_strength": trend.trend_strength,
            "confidence": trend.confidence,
            "start_time": trend.start_time.isoformat(),
            "end_time": trend.end_time.isoformat(),
            "data_points": trend.data_points,
        }

    def _pattern_to_dict(self, pattern: PerformancePattern) -> Dict[str, Any]:
        """패턴을 딕셔너리로 변환"""
        return {
            "pattern_id": pattern.pattern_id,
            "pattern_type": pattern.pattern_type,
            "pattern_description": pattern.pattern_description,
            "metric_name": pattern.metric_name,
            "frequency": pattern.frequency,
            "confidence": pattern.confidence,
            "detected_at": pattern.detected_at.isoformat(),
        }

    def _prediction_to_dict(self, prediction: PerformancePrediction) -> Dict[str, Any]:
        """예측을 딕셔너리로 변환"""
        return {
            "prediction_id": prediction.prediction_id,
            "metric_name": prediction.metric_name,
            "predicted_value": prediction.predicted_value,
            "confidence": prediction.confidence,
            "prediction_time": prediction.prediction_time.isoformat(),
            "created_at": prediction.created_at.isoformat(),
        }

    def _suggestion_to_dict(self, suggestion: OptimizationSuggestion) -> Dict[str, Any]:
        """제안을 딕셔너리로 변환"""
        return {
            "suggestion_id": suggestion.suggestion_id,
            "suggestion_type": suggestion.suggestion_type,
            "suggestion_title": suggestion.suggestion_title,
            "expected_improvement": suggestion.expected_improvement,
            "priority": suggestion.priority,
            "created_at": suggestion.created_at.isoformat(),
        }
