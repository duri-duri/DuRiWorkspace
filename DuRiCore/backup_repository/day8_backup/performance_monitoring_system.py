#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 7 - 성능 모니터링 시스템
실시간 성능 모니터링, 성능 지표 분석, 알림 및 경고 시스템
"""

import asyncio
import json
import logging
import math
import random
import statistics
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)


class MonitoringStatus(Enum):
    """모니터링 상태 열거형"""

    ACTIVE = "active"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"


class AlertLevel(Enum):
    """알림 레벨 열거형"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class PerformanceMetric(Enum):
    """성능 지표 열거형"""

    CPU_USAGE = "cpu_usage"
    MEMORY_USAGE = "memory_usage"
    RESPONSE_TIME = "response_time"
    THROUGHPUT = "throughput"
    ERROR_RATE = "error_rate"
    AVAILABILITY = "availability"


@dataclass
class PerformanceData:
    """성능 데이터"""

    data_id: str
    metric_type: PerformanceMetric
    value: float
    timestamp: datetime
    metadata: Dict[str, Any]


@dataclass
class PerformanceAlert:
    """성능 알림"""

    alert_id: str
    alert_level: AlertLevel
    metric_type: PerformanceMetric
    current_value: float
    threshold_value: float
    message: str
    timestamp: datetime
    resolved: bool


@dataclass
class PerformanceReport:
    """성능 보고서"""

    report_id: str
    monitoring_period: float
    metrics_collected: int
    alerts_generated: int
    performance_trends: Dict[str, Any]
    recommendations: List[str]
    created_at: datetime


class PerformanceMonitoringSystem:
    """성능 모니터링 시스템"""

    def __init__(self):
        self.monitoring_status = MonitoringStatus.STOPPED
        self.performance_data = []
        self.active_alerts = []
        self.alert_history = []

        # 모니터링 설정
        self.monitoring_interval = 5.0  # 5초
        self.data_retention_hours = 24
        self.max_data_points = 10000

        # 알림 임계값
        self.alert_thresholds = {
            PerformanceMetric.CPU_USAGE: {"warning": 0.7, "critical": 0.9},
            PerformanceMetric.MEMORY_USAGE: {"warning": 0.8, "critical": 0.95},
            PerformanceMetric.RESPONSE_TIME: {"warning": 1.0, "critical": 2.0},
            PerformanceMetric.THROUGHPUT: {"warning": 50.0, "critical": 30.0},
            PerformanceMetric.ERROR_RATE: {"warning": 0.02, "critical": 0.05},
            PerformanceMetric.AVAILABILITY: {"warning": 0.99, "critical": 0.95},
        }

        # 성능 지표 가중치
        self.metric_weights = {
            PerformanceMetric.CPU_USAGE: 0.2,
            PerformanceMetric.MEMORY_USAGE: 0.2,
            PerformanceMetric.RESPONSE_TIME: 0.25,
            PerformanceMetric.THROUGHPUT: 0.15,
            PerformanceMetric.ERROR_RATE: 0.1,
            PerformanceMetric.AVAILABILITY: 0.1,
        }

        logger.info("성능 모니터링 시스템 초기화 완료")

    async def monitor_real_time_performance(
        self, system_metrics: Dict[str, Any]
    ) -> List[PerformanceData]:
        """실시간 성능 모니터링"""
        try:
            logger.info("실시간 성능 모니터링 시작")

            performance_data_list = []

            # 각 성능 지표 수집
            for metric_type in PerformanceMetric:
                if metric_type.value in system_metrics:
                    value = system_metrics[metric_type.value]

                    # 성능 데이터 생성
                    performance_data = PerformanceData(
                        data_id=f"data_{int(time.time())}_{random.randint(1000, 9999)}",
                        metric_type=metric_type,
                        value=value,
                        timestamp=datetime.now(),
                        metadata={"source": "real_time_monitoring"},
                    )

                    performance_data_list.append(performance_data)

                    # 데이터 저장
                    self.performance_data.append(performance_data)

                    # 알림 확인
                    await self._check_performance_alerts(performance_data)

            # 데이터 정리 (최대 개수 초과 시)
            await self._cleanup_old_data()

            logger.info(f"실시간 성능 모니터링 완료: {len(performance_data_list)}개 지표 수집")
            return performance_data_list

        except Exception as e:
            logger.error(f"실시간 성능 모니터링 실패: {e}")
            return []

    async def analyze_performance_trends(self, trend_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        try:
            logger.info("성능 트렌드 분석 시작")

            analysis_result = {
                "overall_trend": "stable",
                "metric_trends": {},
                "anomalies": [],
                "predictions": {},
                "recommendations": [],
            }

            # 각 지표별 트렌드 분석
            for metric_type in PerformanceMetric:
                metric_data = [
                    data for data in self.performance_data if data.metric_type == metric_type
                ]
                if len(metric_data) >= 2:
                    trend_analysis = await self._analyze_metric_trend(metric_data)
                    analysis_result["metric_trends"][metric_type.value] = trend_analysis

            # 전체 트렌드 분석
            overall_trend = await self._analyze_overall_trend()
            analysis_result["overall_trend"] = overall_trend

            # 이상 징후 탐지
            anomalies = await self._detect_anomalies()
            analysis_result["anomalies"] = anomalies

            # 성능 예측
            predictions = await self._predict_performance()
            analysis_result["predictions"] = predictions

            # 권장사항 생성
            recommendations = await self._generate_trend_recommendations(analysis_result)
            analysis_result["recommendations"] = recommendations

            logger.info("성능 트렌드 분석 완료")
            return analysis_result

        except Exception as e:
            logger.error(f"성능 트렌드 분석 실패: {e}")
            return {"error": str(e)}

    async def generate_performance_alerts(
        self, alert_conditions: Dict[str, Any]
    ) -> List[PerformanceAlert]:
        """성능 알림 생성"""
        try:
            logger.info("성능 알림 생성 시작")

            alerts = []

            # 현재 성능 데이터 기반 알림 생성
            for performance_data in self.performance_data[-10:]:  # 최근 10개 데이터
                alert = await self._create_performance_alert(performance_data)
                if alert:
                    alerts.append(alert)
                    self.active_alerts.append(alert)

            # 조건 기반 알림 생성
            condition_alerts = await self._create_condition_based_alerts(alert_conditions)
            alerts.extend(condition_alerts)

            logger.info(f"성능 알림 생성 완료: {len(alerts)}개 알림")
            return alerts

        except Exception as e:
            logger.error(f"성능 알림 생성 실패: {e}")
            return []

    async def validate_performance_improvements(
        self, improvement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 개선 검증"""
        try:
            logger.info("성능 개선 검증 시작")

            validation_result = {
                "improvement_verified": False,
                "improvement_score": 0.0,
                "improvement_details": {},
                "validation_confidence": 0.0,
            }

            # 개선 효과 측정
            improvement_score = await self._measure_improvement_effect(improvement_data)
            validation_result["improvement_score"] = improvement_score

            # 개선 검증
            improvement_verified = improvement_score > 0.1  # 10% 이상 개선
            validation_result["improvement_verified"] = improvement_verified

            # 개선 세부사항
            improvement_details = await self._analyze_improvement_details(improvement_data)
            validation_result["improvement_details"] = improvement_details

            # 검증 신뢰도
            validation_confidence = await self._calculate_validation_confidence(improvement_data)
            validation_result["validation_confidence"] = validation_confidence

            logger.info(f"성능 개선 검증 완료: {improvement_verified}")
            return validation_result

        except Exception as e:
            logger.error(f"성능 개선 검증 실패: {e}")
            return {"error": str(e)}

    async def _check_performance_alerts(self, performance_data: PerformanceData) -> None:
        """성능 알림 확인"""
        metric_type = performance_data.metric_type
        current_value = performance_data.value

        if metric_type in self.alert_thresholds:
            thresholds = self.alert_thresholds[metric_type]

            # 경고 레벨 확인
            if current_value >= thresholds["critical"]:
                alert_level = AlertLevel.CRITICAL
            elif current_value >= thresholds["warning"]:
                alert_level = AlertLevel.WARNING
            else:
                return  # 알림 없음

            # 알림 생성
            alert = PerformanceAlert(
                alert_id=f"alert_{int(time.time())}_{random.randint(1000, 9999)}",
                alert_level=alert_level,
                metric_type=metric_type,
                current_value=current_value,
                threshold_value=thresholds[
                    "warning" if alert_level == AlertLevel.WARNING else "critical"
                ],
                message=f"{metric_type.value} 지표가 {alert_level.value} 레벨에 도달했습니다: {current_value:.3f}",
                timestamp=datetime.now(),
                resolved=False,
            )

            self.active_alerts.append(alert)
            self.alert_history.append(alert)

            logger.warning(f"성능 알림 생성: {alert.message}")

    async def _analyze_metric_trend(self, metric_data: List[PerformanceData]) -> Dict[str, Any]:
        """개별 지표 트렌드 분석"""
        if len(metric_data) < 2:
            return {"trend": "insufficient_data"}

        values = [data.value for data in metric_data]

        # 트렌드 계산
        if len(values) >= 2:
            trend_direction = "increasing" if values[-1] > values[0] else "decreasing"
            trend_magnitude = abs(values[-1] - values[0])
            trend_stability = statistics.stdev(values) if len(values) > 1 else 0.0
        else:
            trend_direction = "stable"
            trend_magnitude = 0.0
            trend_stability = 0.0

        return {
            "trend": trend_direction,
            "magnitude": trend_magnitude,
            "stability": trend_stability,
            "current_value": values[-1] if values else 0.0,
            "average_value": statistics.mean(values) if values else 0.0,
        }

    async def _analyze_overall_trend(self) -> str:
        """전체 트렌드 분석"""
        if not self.performance_data:
            return "no_data"

        # 최근 데이터와 이전 데이터 비교
        recent_data = (
            self.performance_data[-10:]
            if len(self.performance_data) >= 10
            else self.performance_data
        )
        previous_data = self.performance_data[-20:-10] if len(self.performance_data) >= 20 else []

        if not previous_data:
            return "insufficient_data"

        # 가중 평균 성능 계산
        recent_performance = await self._calculate_weighted_performance(recent_data)
        previous_performance = await self._calculate_weighted_performance(previous_data)

        if recent_performance > previous_performance * 1.05:
            return "improving"
        elif recent_performance < previous_performance * 0.95:
            return "declining"
        else:
            return "stable"

    async def _detect_anomalies(self) -> List[Dict[str, Any]]:
        """이상 징후 탐지"""
        anomalies = []

        for metric_type in PerformanceMetric:
            metric_data = [
                data for data in self.performance_data if data.metric_type == metric_type
            ]
            if len(metric_data) >= 5:
                values = [data.value for data in metric_data]
                mean_value = statistics.mean(values)
                std_value = statistics.stdev(values) if len(values) > 1 else 0.0

                # 최근 값이 평균에서 2 표준편차 이상 벗어나면 이상 징후
                latest_value = values[-1]
                if abs(latest_value - mean_value) > 2 * std_value:
                    anomalies.append(
                        {
                            "metric_type": metric_type.value,
                            "current_value": latest_value,
                            "expected_range": [
                                mean_value - 2 * std_value,
                                mean_value + 2 * std_value,
                            ],
                            "severity": (
                                "high"
                                if abs(latest_value - mean_value) > 3 * std_value
                                else "medium"
                            ),
                        }
                    )

        return anomalies

    async def _predict_performance(self) -> Dict[str, Any]:
        """성능 예측"""
        predictions = {}

        for metric_type in PerformanceMetric:
            metric_data = [
                data for data in self.performance_data if data.metric_type == metric_type
            ]
            if len(metric_data) >= 5:
                values = [data.value for data in metric_data]

                # 간단한 선형 예측
                if len(values) >= 2:
                    trend = (values[-1] - values[0]) / len(values)
                    predicted_value = values[-1] + trend

                    predictions[metric_type.value] = {
                        "predicted_value": predicted_value,
                        "confidence": 0.7,  # 간단한 예측이므로 낮은 신뢰도
                        "trend": "increasing" if trend > 0 else "decreasing",
                    }

        return predictions

    async def _generate_trend_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """트렌드 기반 권장사항 생성"""
        recommendations = []

        # 전체 트렌드 기반 권장사항
        overall_trend = analysis_result.get("overall_trend", "stable")
        if overall_trend == "declining":
            recommendations.append("전체 성능이 하락하고 있습니다. 최적화가 필요합니다.")
        elif overall_trend == "improving":
            recommendations.append("전체 성능이 개선되고 있습니다. 현재 설정을 유지하세요.")

        # 개별 지표 기반 권장사항
        metric_trends = analysis_result.get("metric_trends", {})
        for metric_name, trend_data in metric_trends.items():
            trend = trend_data.get("trend", "stable")
            if trend == "increasing" and metric_name in [
                "cpu_usage",
                "memory_usage",
                "response_time",
                "error_rate",
            ]:
                recommendations.append(
                    f"{metric_name} 지표가 증가하고 있습니다. 모니터링을 강화하세요."
                )
            elif trend == "decreasing" and metric_name in [
                "throughput",
                "availability",
            ]:
                recommendations.append(
                    f"{metric_name} 지표가 감소하고 있습니다. 성능 개선이 필요합니다."
                )

        # 이상 징후 기반 권장사항
        anomalies = analysis_result.get("anomalies", [])
        for anomaly in anomalies:
            metric_type = anomaly["metric_type"]
            severity = anomaly["severity"]
            recommendations.append(
                f"{metric_type} 지표에서 {severity} 수준의 이상 징후가 감지되었습니다."
            )

        return recommendations

    async def _create_performance_alert(
        self, performance_data: PerformanceData
    ) -> Optional[PerformanceAlert]:
        """성능 알림 생성"""
        metric_type = performance_data.metric_type
        current_value = performance_data.value

        if metric_type in self.alert_thresholds:
            thresholds = self.alert_thresholds[metric_type]

            # 임계값 확인
            if current_value >= thresholds["critical"]:
                alert_level = AlertLevel.CRITICAL
            elif current_value >= thresholds["warning"]:
                alert_level = AlertLevel.WARNING
            else:
                return None

            return PerformanceAlert(
                alert_id=f"alert_{int(time.time())}_{random.randint(1000, 9999)}",
                alert_level=alert_level,
                metric_type=metric_type,
                current_value=current_value,
                threshold_value=thresholds[
                    "warning" if alert_level == AlertLevel.WARNING else "critical"
                ],
                message=f"{metric_type.value} 지표 알림: {current_value:.3f}",
                timestamp=datetime.now(),
                resolved=False,
            )

        return None

    async def _create_condition_based_alerts(
        self, alert_conditions: Dict[str, Any]
    ) -> List[PerformanceAlert]:
        """조건 기반 알림 생성"""
        alerts = []

        for condition, threshold in alert_conditions.items():
            if condition in [metric.value for metric in PerformanceMetric]:
                metric_type = PerformanceMetric(condition)
                current_value = random.uniform(0.0, 1.0)  # 시뮬레이션

                if current_value >= threshold:
                    alert = PerformanceAlert(
                        alert_id=f"condition_alert_{int(time.time())}",
                        alert_level=AlertLevel.WARNING,
                        metric_type=metric_type,
                        current_value=current_value,
                        threshold_value=threshold,
                        message=f"조건 기반 알림: {condition} = {current_value:.3f}",
                        timestamp=datetime.now(),
                        resolved=False,
                    )
                    alerts.append(alert)

        return alerts

    async def _measure_improvement_effect(self, improvement_data: Dict[str, Any]) -> float:
        """개선 효과 측정"""
        before_performance = improvement_data.get("before_performance", 0.0)
        after_performance = improvement_data.get("after_performance", 0.0)

        if before_performance > 0:
            improvement_score = (after_performance - before_performance) / before_performance
            return max(improvement_score, 0.0)

        return 0.0

    async def _analyze_improvement_details(
        self, improvement_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개선 세부사항 분석"""
        details = {
            "performance_improvement": 0.0,
            "stability_improvement": 0.0,
            "efficiency_improvement": 0.0,
        }

        # 성능 개선 분석
        if "before_performance" in improvement_data and "after_performance" in improvement_data:
            before = improvement_data["before_performance"]
            after = improvement_data["after_performance"]
            details["performance_improvement"] = (after - before) / before if before > 0 else 0.0

        # 안정성 개선 분석
        if "before_stability" in improvement_data and "after_stability" in improvement_data:
            before = improvement_data["before_stability"]
            after = improvement_data["after_stability"]
            details["stability_improvement"] = (after - before) / before if before > 0 else 0.0

        # 효율성 개선 분석
        if "before_efficiency" in improvement_data and "after_efficiency" in improvement_data:
            before = improvement_data["before_efficiency"]
            after = improvement_data["after_efficiency"]
            details["efficiency_improvement"] = (after - before) / before if before > 0 else 0.0

        return details

    async def _calculate_validation_confidence(self, improvement_data: Dict[str, Any]) -> float:
        """검증 신뢰도 계산"""
        confidence_factors = []

        # 데이터 품질
        if "data_quality" in improvement_data:
            confidence_factors.append(improvement_data["data_quality"])

        # 측정 정확도
        if "measurement_accuracy" in improvement_data:
            confidence_factors.append(improvement_data["measurement_accuracy"])

        # 샘플 크기
        if "sample_size" in improvement_data:
            sample_size = improvement_data["sample_size"]
            sample_confidence = min(sample_size / 100.0, 1.0)  # 100개 이상이면 최대 신뢰도
            confidence_factors.append(sample_confidence)

        # 시간 범위
        if "time_range" in improvement_data:
            time_range = improvement_data["time_range"]
            time_confidence = min(time_range / 3600.0, 1.0)  # 1시간 이상이면 최대 신뢰도
            confidence_factors.append(time_confidence)

        return statistics.mean(confidence_factors) if confidence_factors else 0.5

    async def _calculate_weighted_performance(
        self, performance_data: List[PerformanceData]
    ) -> float:
        """가중 평균 성능 계산"""
        if not performance_data:
            return 0.0

        weighted_sum = 0.0
        total_weight = 0.0

        for data in performance_data:
            weight = self.metric_weights.get(data.metric_type, 0.1)
            weighted_sum += data.value * weight
            total_weight += weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    async def _cleanup_old_data(self) -> None:
        """오래된 데이터 정리"""
        if len(self.performance_data) > self.max_data_points:
            # 가장 오래된 데이터부터 삭제
            self.performance_data = self.performance_data[-self.max_data_points :]
            logger.info(f"오래된 성능 데이터 정리 완료: {self.max_data_points}개 유지")


async def test_performance_monitoring_system():
    """성능 모니터링 시스템 테스트"""
    print("=== 성능 모니터링 시스템 테스트 시작 ===")

    monitoring_system = PerformanceMonitoringSystem()

    # 1. 실시간 성능 모니터링 테스트
    print("1. 실시간 성능 모니터링 테스트")
    system_metrics = {
        "cpu_usage": random.uniform(0.3, 0.9),
        "memory_usage": random.uniform(0.4, 0.95),
        "response_time": random.uniform(0.1, 2.5),
        "throughput": random.uniform(30.0, 150.0),
        "error_rate": random.uniform(0.0, 0.08),
        "availability": random.uniform(0.92, 0.999),
    }

    performance_data = await monitoring_system.monitor_real_time_performance(system_metrics)
    print(f"   - 수집된 성능 데이터: {len(performance_data)}개")
    print(f"   - 활성 알림: {len(monitoring_system.active_alerts)}개")

    # 2. 성능 트렌드 분석 테스트
    print("2. 성능 트렌드 분석 테스트")
    trend_data = [{"timestamp": datetime.now(), "metrics": system_metrics}]

    trend_analysis = await monitoring_system.analyze_performance_trends(trend_data)
    print(f"   - 전체 트렌드: {trend_analysis.get('overall_trend', 'unknown')}")
    print(f"   - 지표별 트렌드: {len(trend_analysis.get('metric_trends', {}))}개")
    print(f"   - 이상 징후: {len(trend_analysis.get('anomalies', []))}개")

    # 3. 성능 알림 생성 테스트
    print("3. 성능 알림 생성 테스트")
    alert_conditions = {"cpu_usage": 0.8, "memory_usage": 0.9, "response_time": 1.5}

    alerts = await monitoring_system.generate_performance_alerts(alert_conditions)
    print(f"   - 생성된 알림: {len(alerts)}개")

    # 4. 성능 개선 검증 테스트
    print("4. 성능 개선 검증 테스트")
    improvement_data = {
        "before_performance": 0.75,
        "after_performance": 0.85,
        "before_stability": 0.8,
        "after_stability": 0.9,
        "data_quality": 0.9,
        "measurement_accuracy": 0.95,
        "sample_size": 150,
        "time_range": 7200,  # 2시간
    }

    validation_result = await monitoring_system.validate_performance_improvements(improvement_data)
    print(f"   - 개선 검증: {validation_result.get('improvement_verified', False)}")
    print(f"   - 개선 점수: {validation_result.get('improvement_score', 0.0):.3f}")
    print(f"   - 검증 신뢰도: {validation_result.get('validation_confidence', 0.0):.3f}")

    print("=== 성능 모니터링 시스템 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_performance_monitoring_system())
