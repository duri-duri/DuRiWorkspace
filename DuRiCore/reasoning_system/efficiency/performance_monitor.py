#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 성능 모니터링 모듈

실시간 성능 모니터링 및 조정 모듈입니다.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""

    metrics_id: str
    session_id: str
    execution_time: float
    memory_usage: float
    cpu_usage: float
    throughput: float
    quality_score: float
    efficiency_score: float
    timestamp: datetime = field(default_factory=datetime.now)


class PerformanceMonitor:
    """성능 모니터링"""

    def __init__(self):
        self.metrics_history = []
        self.performance_trends = {}

    async def monitor_performance(self, session_id: str, performance_data: Dict[str, Any]) -> PerformanceMetrics:
        """성능 모니터링"""
        metrics_id = f"metrics_{int(time.time())}"

        # 성능 데이터 추출
        execution_time = performance_data.get("execution_time", 0.0)
        memory_usage = performance_data.get("memory_usage", 0.0)
        cpu_usage = performance_data.get("cpu_usage", 0.0)
        throughput = performance_data.get("throughput", 0.0)
        quality_score = performance_data.get("quality_score", 0.0)

        # 효율성 점수 계산
        efficiency_score = await self._calculate_efficiency_score(
            execution_time, memory_usage, cpu_usage, throughput, quality_score
        )

        metrics = PerformanceMetrics(
            metrics_id=metrics_id,
            session_id=session_id,
            execution_time=execution_time,
            memory_usage=memory_usage,
            cpu_usage=cpu_usage,
            throughput=throughput,
            quality_score=quality_score,
            efficiency_score=efficiency_score,
        )

        self.metrics_history.append(metrics)
        return metrics

    async def _calculate_efficiency_score(
        self,
        execution_time: float,
        memory_usage: float,
        cpu_usage: float,
        throughput: float,
        quality_score: float,
    ) -> float:
        """효율성 점수 계산"""
        # 각 메트릭의 가중치
        weights = {
            "execution_time": 0.25,
            "memory_usage": 0.2,
            "cpu_usage": 0.2,
            "throughput": 0.2,
            "quality_score": 0.15,
        }

        # 실행 시간 점수 (짧을수록 좋음)
        time_score = max(0.0, 1.0 - (execution_time / 10.0))  # 10초 기준

        # 메모리 사용량 점수 (적을수록 좋음)
        memory_score = max(0.0, 1.0 - (memory_usage / 8192.0))  # 8GB 기준

        # CPU 사용량 점수 (적을수록 좋음)
        cpu_score = max(0.0, 1.0 - (cpu_usage / 100.0))  # 100% 기준

        # 처리량 점수 (높을수록 좋음)
        throughput_score = min(1.0, throughput / 1000.0)  # 1000 req/s 기준

        # 품질 점수 (높을수록 좋음)
        quality_score_normalized = quality_score

        # 가중 평균 계산
        efficiency_score = (
            time_score * weights["execution_time"]
            + memory_score * weights["memory_usage"]
            + cpu_score * weights["cpu_usage"]
            + throughput_score * weights["throughput"]
            + quality_score_normalized * weights["quality_score"]
        )

        return min(1.0, efficiency_score)

    async def get_performance_trends(self) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        if not self.metrics_history:
            return {}

        # 최근 10개 메트릭 분석
        recent_metrics = self.metrics_history[-10:]

        trends = {
            "average_efficiency": np.mean([m.efficiency_score for m in recent_metrics]),
            "average_execution_time": np.mean([m.execution_time for m in recent_metrics]),
            "average_memory_usage": np.mean([m.memory_usage for m in recent_metrics]),
            "average_cpu_usage": np.mean([m.cpu_usage for m in recent_metrics]),
            "average_throughput": np.mean([m.throughput for m in recent_metrics]),
            "average_quality_score": np.mean([m.quality_score for m in recent_metrics]),
            "trend_direction": "stable",
        }

        # 트렌드 방향 분석
        if len(recent_metrics) >= 2:
            first_efficiency = recent_metrics[0].efficiency_score
            last_efficiency = recent_metrics[-1].efficiency_score

            if last_efficiency > first_efficiency * 1.1:
                trends["trend_direction"] = "improving"
            elif last_efficiency < first_efficiency * 0.9:
                trends["trend_direction"] = "declining"

        return trends
