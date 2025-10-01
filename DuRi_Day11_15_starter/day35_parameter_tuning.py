#!/usr/bin/env python3
"""
Day 35: 멀티목표 목적함수(J) 파라미터 튜닝 시스템
"""

import asyncio
import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OptimizationStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ParameterType(Enum):
    MEMORY_LIMIT = "memory_limit"
    CPU_LIMIT = "cpu_limit"
    NETWORK_BUFFER = "network_buffer"
    CACHE_SIZE = "cache_size"
    THREAD_POOL_SIZE = "thread_pool_size"
    CONNECTION_POOL_SIZE = "connection_pool_size"


@dataclass
class OptimizationMetrics:
    """최적화 지표"""

    overhead: float
    error_rate: float
    size_increase: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    throughput: float
    user_satisfaction: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class ParameterRange:
    """파라미터 범위"""

    min_value: float
    max_value: float
    step: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class OptimizationResult:
    """최적화 결과"""

    parameters: Dict[str, float]
    metrics: OptimizationMetrics
    objective_value: float
    improvement_rate: float
    status: OptimizationStatus
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        result["status"] = self.status.value
        return result


class MultiObjectiveOptimizer:
    """멀티목표 최적화 시스템"""

    def __init__(self):
        self.optimization_status = OptimizationStatus.IDLE
        self.optimization_history = []

        # 목적함수 가중치 (Day 35 최적화된 값)
        self.objective_weights = {"overhead": 0.55, "error": 0.35, "size": 0.10}

        # 성능 지표 가중치
        self.performance_weights = {
            "cpu_usage": 0.25,
            "memory_usage": 0.25,
            "response_time": 0.20,
            "throughput": 0.15,
            "error_rate": 0.10,
            "user_satisfaction": 0.05,
        }

        # 파라미터 범위 정의
        self.parameter_ranges = {
            ParameterType.MEMORY_LIMIT: ParameterRange(512, 8192, 256),
            ParameterType.CPU_LIMIT: ParameterRange(0.1, 4.0, 0.1),
            ParameterType.NETWORK_BUFFER: ParameterRange(1024, 65536, 1024),
            ParameterType.CACHE_SIZE: ParameterRange(64, 2048, 64),
            ParameterType.THREAD_POOL_SIZE: ParameterRange(2, 32, 2),
            ParameterType.CONNECTION_POOL_SIZE: ParameterRange(5, 100, 5),
        }

        # 최적화 설정
        self.max_iterations = 50
        self.improvement_threshold = 0.05  # 5%
        self.convergence_threshold = 0.01  # 1%

        logger.info("MultiObjectiveOptimizer 초기화 완료")

    def calculate_objective_function(self, metrics: OptimizationMetrics) -> float:
        """목적함수 J 계산"""
        J = (
            self.objective_weights["overhead"] * metrics.overhead
            + self.objective_weights["error"] * metrics.error_rate
            + self.objective_weights["size"] * metrics.size_increase
        )

        # 제약조건 위반 시 페널티 추가
        penalty = 0.0
        if metrics.overhead > 0.05:  # 5% 오버헤드 초과
            penalty += 0.5
        if metrics.error_rate > 0.01:  # 1% 오류율 초과
            penalty += 0.5

        return J + penalty

    def calculate_performance_score(self, metrics: OptimizationMetrics) -> float:
        """성능 점수 계산"""
        score = 0.0

        # CPU 사용률 (낮을수록 좋음)
        score += self.performance_weights["cpu_usage"] * (1.0 - metrics.cpu_usage)

        # 메모리 사용률 (낮을수록 좋음)
        score += self.performance_weights["memory_usage"] * (1.0 - metrics.memory_usage)

        # 응답시간 (낮을수록 좋음, 1000ms 기준)
        response_score = max(0, 1.0 - metrics.response_time / 1000.0)
        score += self.performance_weights["response_time"] * response_score

        # 처리량 (높을수록 좋음, 100 req/s 기준)
        throughput_score = min(1.0, metrics.throughput / 100.0)
        score += self.performance_weights["throughput"] * throughput_score

        # 오류율 (낮을수록 좋음)
        score += self.performance_weights["error_rate"] * (1.0 - metrics.error_rate)

        # 사용자 만족도 (높을수록 좋음)
        score += (
            self.performance_weights["user_satisfaction"] * metrics.user_satisfaction
        )

        return score

    def generate_parameter_combinations(self) -> List[Dict[str, float]]:
        """파라미터 조합 생성"""
        combinations = []

        # 각 파라미터의 가능한 값들 생성
        param_values = {}
        for param_type, param_range in self.parameter_ranges.items():
            values = []
            current = param_range.min_value
            while current <= param_range.max_value:
                values.append(current)
                current += param_range.step
            param_values[param_type.value] = values

        # 조합 생성 (샘플링으로 제한)
        import itertools
        import random

        # 모든 조합이 너무 많으므로 랜덤 샘플링
        sample_size = min(1000, len(list(itertools.product(*param_values.values()))))

        for _ in range(sample_size):
            combination = {}
            for param_type, values in param_values.items():
                combination[param_type] = random.choice(values)
            combinations.append(combination)

        return combinations

    async def simulate_metrics(
        self, parameters: Dict[str, float]
    ) -> OptimizationMetrics:
        """파라미터에 따른 성능 지표 시뮬레이션"""
        # 실제 환경에서는 실제 시스템에서 측정
        # 여기서는 시뮬레이션으로 근사치 계산

        # 메모리 제한에 따른 영향
        memory_factor = parameters["memory_limit"] / 2048.0  # 2048MB 기준

        # CPU 제한에 따른 영향
        cpu_factor = parameters["cpu_limit"] / 1.0  # 1.0 기준

        # 네트워크 버퍼에 따른 영향
        network_factor = parameters["network_buffer"] / 8192.0  # 8192B 기준

        # 캐시 크기에 따른 영향
        cache_factor = parameters["cache_size"] / 512.0  # 512 기준

        # 스레드 풀 크기에 따른 영향
        thread_factor = parameters["thread_pool_size"] / 8.0  # 8 기준

        # 연결 풀 크기에 따른 영향
        connection_factor = parameters["connection_pool_size"] / 20.0  # 20 기준

        # 시뮬레이션된 지표 계산
        overhead = max(0, 0.02 * (1.0 - memory_factor * 0.3 - cpu_factor * 0.2))
        error_rate = max(0, 0.005 * (1.0 - network_factor * 0.4 - cache_factor * 0.3))
        size_increase = max(0, 0.1 * (1.0 - cache_factor * 0.5))

        cpu_usage = min(1.0, 0.6 * (1.0 - cpu_factor * 0.3 + thread_factor * 0.1))
        memory_usage = min(1.0, 0.7 * (1.0 - memory_factor * 0.4 + cache_factor * 0.2))

        response_time = max(
            100,
            800 * (1.0 - memory_factor * 0.2 - cpu_factor * 0.3 - network_factor * 0.2),
        )
        throughput = max(
            50, 120 * (1.0 + thread_factor * 0.2 + connection_factor * 0.1)
        )

        user_satisfaction = min(
            1.0, 0.85 * (1.0 + (1.0 - overhead) * 0.3 + (1.0 - error_rate) * 0.4)
        )

        return OptimizationMetrics(
            overhead=overhead,
            error_rate=error_rate,
            size_increase=size_increase,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=response_time,
            throughput=throughput,
            user_satisfaction=user_satisfaction,
        )

    async def optimize_parameters(self) -> OptimizationResult:
        """파라미터 최적화 실행"""
        logger.info("파라미터 최적화 시작")
        self.optimization_status = OptimizationStatus.RUNNING

        best_result = None
        best_objective_value = float("inf")

        # 파라미터 조합 생성
        parameter_combinations = self.generate_parameter_combinations()
        logger.info(f"총 {len(parameter_combinations)}개 파라미터 조합 생성")

        # 각 조합에 대해 최적화 실행
        for i, parameters in enumerate(parameter_combinations):
            try:
                # 성능 지표 시뮬레이션
                metrics = await self.simulate_metrics(parameters)

                # 목적함수 계산
                objective_value = self.calculate_objective_function(metrics)

                # 성능 점수 계산
                performance_score = self.calculate_performance_score(metrics)

                # 개선율 계산
                improvement_rate = 0.0
                if best_result:
                    improvement_rate = (
                        best_objective_value - objective_value
                    ) / best_objective_value

                # 최적 결과 업데이트
                if objective_value < best_objective_value:
                    best_objective_value = objective_value
                    best_result = OptimizationResult(
                        parameters=parameters,
                        metrics=metrics,
                        objective_value=objective_value,
                        improvement_rate=improvement_rate,
                        status=OptimizationStatus.COMPLETED,
                        timestamp=datetime.now(),
                    )

                # 진행률 로깅
                if (i + 1) % 100 == 0:
                    logger.info(
                        f"진행률: {i + 1}/{len(parameter_combinations)} "
                        f"(목적함수: {objective_value:.4f})"
                    )

            except Exception as e:
                logger.error(f"파라미터 조합 {i} 최적화 실패: {e}")
                continue

        self.optimization_status = OptimizationStatus.COMPLETED
        logger.info(
            f"파라미터 최적화 완료. 최적 목적함수 값: {best_objective_value:.4f}"
        )

        return best_result

    def save_optimization_result(self, result: OptimizationResult, filepath: str):
        """최적화 결과 저장"""
        result_dict = result.to_dict()

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)

        logger.info(f"최적화 결과 저장 완료: {filepath}")

    def load_optimization_result(self, filepath: str) -> Optional[OptimizationResult]:
        """최적화 결과 로드"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            # 데이터 변환
            metrics = OptimizationMetrics(**data["metrics"])
            result = OptimizationResult(
                parameters=data["parameters"],
                metrics=metrics,
                objective_value=data["objective_value"],
                improvement_rate=data["improvement_rate"],
                status=OptimizationStatus(data["status"]),
                timestamp=datetime.fromisoformat(data["timestamp"]),
            )

            logger.info(f"최적화 결과 로드 완료: {filepath}")
            return result

        except Exception as e:
            logger.error(f"최적화 결과 로드 실패: {e}")
            return None


class ParameterTuningSystem:
    """파라미터 튜닝 시스템"""

    def __init__(self):
        self.optimizer = MultiObjectiveOptimizer()
        self.tuning_history = []

        logger.info("ParameterTuningSystem 초기화 완료")

    async def run_tuning(self) -> OptimizationResult:
        """튜닝 실행"""
        logger.info("파라미터 튜닝 시작")

        # 최적화 실행
        result = await self.optimizer.optimize_parameters()

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"day35_optimization_result_{timestamp}.json"
        self.optimizer.save_optimization_result(result, result_file)

        # 튜닝 히스토리에 추가
        self.tuning_history.append(result)

        logger.info("파라미터 튜닝 완료")
        return result

    def generate_report(self, result: OptimizationResult) -> str:
        """튜닝 결과 보고서 생성"""
        report = f"""
# Day 35 파라미터 튜닝 결과 보고서

## 최적화 결과
- **목적함수 값**: {result.objective_value:.4f}
- **개선율**: {result.improvement_rate:.2%}
- **최적화 상태**: {result.status.value}
- **실행 시간**: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

## 최적 파라미터
"""
        for param, value in result.parameters.items():
            report += f"- **{param}**: {value}\n"

        report += f"""
## 성능 지표
- **오버헤드**: {result.metrics.overhead:.4f}
- **오류율**: {result.metrics.error_rate:.4f}
- **크기 증가**: {result.metrics.size_increase:.4f}
- **CPU 사용률**: {result.metrics.cpu_usage:.2%}
- **메모리 사용률**: {result.metrics.memory_usage:.2%}
- **응답시간**: {result.metrics.response_time:.0f}ms
- **처리량**: {result.metrics.throughput:.0f} req/s
- **사용자 만족도**: {result.metrics.user_satisfaction:.2%}

## 권장사항
1. 최적화된 파라미터를 시스템에 적용
2. 실제 환경에서 성능 모니터링
3. 주기적인 파라미터 재튜닝
"""
        return report


async def main():
    """메인 함수"""
    logger.info("Day 35: 멀티목표 목적함수 파라미터 튜닝 시작")

    # 튜닝 시스템 초기화
    tuning_system = ParameterTuningSystem()

    # 튜닝 실행
    result = await tuning_system.run_tuning()

    # 결과 보고서 생성
    report = tuning_system.generate_report(result)

    # 보고서 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"day35_tuning_report_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"튜닝 완료. 보고서 저장: {report_file}")

    # 결과 출력
    print("\n" + "=" * 50)
    print("Day 35 파라미터 튜닝 결과")
    print("=" * 50)
    print(f"목적함수 값: {result.objective_value:.4f}")
    print(f"개선율: {result.improvement_rate:.2%}")
    print(f"최적 응답시간: {result.metrics.response_time:.0f}ms")
    print(f"최적 오류율: {result.metrics.error_rate:.4f}")
    print(f"사용자 만족도: {result.metrics.user_satisfaction:.2%}")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
