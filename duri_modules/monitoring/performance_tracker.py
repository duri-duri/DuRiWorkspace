#!/usr/bin/env python3
"""
성능 모니터링 시스템 - DuRi의 성장 과정 추적
"""

from collections import defaultdict, deque
from datetime import datetime, timedelta
import json
import os
import statistics
import time
from typing import Any, Dict, List


class PerformanceTracker:
    """DuRi 시스템 성능 추적 및 모니터링"""

    def __init__(self):
        self.response_times = defaultdict(list)  # 엔드포인트별 응답 시간
        self.error_counts = defaultdict(int)  # 엔드포인트별 오류 수
        self.request_counts = defaultdict(int)  # 엔드포인트별 요청 수
        self.learning_metrics = defaultdict(list)  # 학습 관련 메트릭
        self.system_health = {
            "overall_status": "healthy",
            "last_check": datetime.now().isoformat(),
            "uptime": 0,
            "total_requests": 0,
            "total_errors": 0,
        }
        self.start_time = datetime.now()

    def track_request(
        self,
        endpoint: str,
        response_time: float,
        success: bool = True,
        error_message: str = None,
    ):
        """요청 추적"""
        timestamp = datetime.now()

        # 응답 시간 기록
        self.response_times[endpoint].append(
            {
                "timestamp": timestamp.isoformat(),
                "response_time": response_time,
                "success": success,
            }
        )

        # 요청 수 증가
        self.request_counts[endpoint] += 1

        # 오류 추적
        if not success:
            self.error_counts[endpoint] += 1
            if error_message:
                self._log_error(endpoint, error_message, timestamp)

        # 시스템 전체 통계 업데이트
        self._update_system_health()

        print(
            f"📊 성능 추적: {endpoint} - {response_time:.3f}초 ({'성공' if success else '실패'})"
        )

    def track_learning_metric(
        self, metric_name: str, value: float, metadata: Dict[str, Any] = None
    ):
        """학습 메트릭 추적"""
        timestamp = datetime.now()

        self.learning_metrics[metric_name].append(
            {
                "timestamp": timestamp.isoformat(),
                "value": value,
                "metadata": metadata or {},
            }
        )

        print(f"📈 학습 메트릭: {metric_name} = {value:.3f}")

    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 생성"""
        # 시스템 건강도 업데이트
        self._update_system_health()

        summary = {
            "system_health": self.system_health,
            "endpoint_performance": {},
            "learning_metrics": {},
            "recommendations": [],
        }

        # 엔드포인트별 성능 분석
        for endpoint in self.response_times:
            response_times = [
                req["response_time"] for req in self.response_times[endpoint]
            ]
            if response_times:
                # 안전한 error_rate 계산
                total_requests = self.request_counts.get(endpoint, 0)
                total_errors = self.error_counts.get(endpoint, 0)
                error_rate = (
                    total_errors / total_requests if total_requests > 0 else 0.0
                )

                summary["endpoint_performance"][endpoint] = {
                    "avg_response_time": statistics.mean(response_times),
                    "max_response_time": max(response_times),
                    "min_response_time": min(response_times),
                    "total_requests": total_requests,
                    "error_rate": error_rate,
                    "recent_performance": self._get_recent_performance(endpoint),
                }

        # 학습 메트릭 분석
        for metric_name in self.learning_metrics:
            values = [metric["value"] for metric in self.learning_metrics[metric_name]]
            if values:
                summary["learning_metrics"][metric_name] = {
                    "current_value": values[-1],
                    "avg_value": statistics.mean(values),
                    "trend": self._calculate_trend(values),
                    "total_measurements": len(values),
                }

        # 성능 권장사항 생성
        summary["recommendations"] = self._generate_recommendations(summary)

        return summary

    def _get_recent_performance(
        self, endpoint: str, minutes: int = 5
    ) -> Dict[str, Any]:
        """최근 성능 데이터"""
        recent_requests = [
            req
            for req in self.response_times[endpoint]
            if datetime.fromisoformat(req["timestamp"])
            > datetime.now() - timedelta(minutes=minutes)
        ]

        if not recent_requests:
            return {"avg_response_time": 0, "request_count": 0}

        recent_times = [req["response_time"] for req in recent_requests]
        return {
            "avg_response_time": statistics.mean(recent_times),
            "request_count": len(recent_requests),
        }

    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        if len(values) < 2:
            return "stable"

        recent_avg = statistics.mean(values[-5:]) if len(values) >= 5 else values[-1]
        earlier_avg = statistics.mean(values[:5]) if len(values) >= 5 else values[0]

        if recent_avg > earlier_avg * 1.1:
            return "improving"
        elif recent_avg < earlier_avg * 0.9:
            return "declining"
        else:
            return "stable"

    def _update_system_health(self):
        """시스템 건강도 업데이트"""
        total_requests = sum(self.request_counts.values())
        total_errors = sum(self.error_counts.values())

        error_rate = total_errors / total_requests if total_requests > 0 else 0

        self.system_health.update(
            {
                "total_requests": total_requests,
                "total_errors": total_errors,
                "error_rate": error_rate,
                "uptime": (datetime.now() - self.start_time).total_seconds(),
                "last_check": datetime.now().isoformat(),
            }
        )

        # 전체 상태 판단
        if error_rate > 0.2:  # 20% 이상 오류
            self.system_health["overall_status"] = "critical"
        elif error_rate > 0.1:  # 10% 이상 오류
            self.system_health["overall_status"] = "warning"
        else:
            self.system_health["overall_status"] = "healthy"

    def _log_error(self, endpoint: str, error_message: str, timestamp: datetime):
        """오류 로그"""
        error_log = {
            "endpoint": endpoint,
            "error_message": error_message,
            "timestamp": timestamp.isoformat(),
        }

        # 오류 로그 파일에 저장
        error_log_path = "/tmp/duri_error_logs.json"
        try:
            if os.path.exists(error_log_path):
                with open(error_log_path, "r") as f:
                    error_logs = json.load(f)
            else:
                error_logs = []

            error_logs.append(error_log)

            with open(error_log_path, "w") as f:
                json.dump(error_logs, f, indent=2)
        except Exception as e:
            print(f"오류 로그 저장 실패: {e}")

    def _generate_recommendations(self, summary: Dict[str, Any]) -> List[str]:
        """성능 권장사항 생성"""
        recommendations = []

        # 응답 시간 권장사항
        for endpoint, perf in summary["endpoint_performance"].items():
            if perf["avg_response_time"] > 2.0:
                recommendations.append(
                    f"{endpoint}: 응답 시간이 2초를 초과합니다. 최적화가 필요합니다."
                )
            elif perf["error_rate"] > 0.05:
                recommendations.append(
                    f"{endpoint}: 오류율이 5%를 초과합니다. 안정성 개선이 필요합니다."
                )

        # 학습 메트릭 권장사항
        for metric_name, metric_data in summary["learning_metrics"].items():
            if metric_data["trend"] == "declining":
                recommendations.append(
                    f"{metric_name}: 학습 효과가 감소하고 있습니다. 학습 방법 개선이 필요합니다."
                )

        # 시스템 전체 권장사항
        if summary["system_health"]["error_rate"] > 0.1:
            recommendations.append(
                "전체 시스템 오류율이 높습니다. 시스템 안정성 점검이 필요합니다."
            )

        return recommendations

    def get_health_check(self) -> Dict[str, Any]:
        """건강도 확인"""
        try:
            return {
                "status": self.system_health.get("overall_status", "unknown"),
                "uptime_seconds": self.system_health.get("uptime", 0),
                "total_requests": self.system_health.get("total_requests", 0),
                "error_rate": self.system_health.get("error_rate", 0.0),
                "last_check": self.system_health.get(
                    "last_check", datetime.now().isoformat()
                ),
            }
        except Exception as e:
            print(f"건강도 확인 오류: {e}")
            return {
                "status": "error",
                "uptime_seconds": 0,
                "total_requests": 0,
                "error_rate": 0.0,
                "last_check": datetime.now().isoformat(),
            }

    def get_statistics(self) -> Dict[str, Any]:
        """통계 정보 반환"""
        try:
            summary = self.get_performance_summary()
            health = self.get_health_check()

            return {
                "performance_summary": summary,
                "health_check": health,
                "total_endpoints": len(self.request_counts),
                "total_learning_metrics": len(self.learning_metrics),
                "timestamp": datetime.now().isoformat(),
            }
        except Exception as e:
            print(f"통계 생성 오류: {e}")
            return {"error": str(e)}

    def get_summary(self) -> Dict[str, Any]:
        """요약 정보 반환 (get_performance_summary의 별칭)"""
        return self.get_performance_summary()


# 모듈 인스턴스 생성
performance_tracker = PerformanceTracker()
