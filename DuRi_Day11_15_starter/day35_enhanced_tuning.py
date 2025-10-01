#!/usr/bin/env python3
"""
Day 35 Enhanced: 멀티목표 목적함수(J) 파라미터 튜닝 시스템 (개선판)
- 기존 day35_pack의 장점 + PoU 시스템 통합 + 실시간 모니터링
"""

import asyncio
import json
import logging
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import yaml

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Metrics:
    """성능 지표"""

    latency_ms: float
    accuracy: float
    explainability: float
    failure_rate: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class Utilities:
    """유틸리티 점수 (0-1)"""

    latency: float
    accuracy: float
    explainability: float
    failure: float

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


@dataclass
class ObjectiveResult:
    """목적함수 결과"""

    metrics: Metrics
    utilities: Utilities
    weights: Dict[str, float]
    J: float
    constraints_ok: bool
    violations: List[str]
    preset_name: str
    timestamp: datetime

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["timestamp"] = self.timestamp.isoformat()
        return result


class EnhancedObjectiveEvaluator:
    """개선된 목적함수 평가 시스템"""

    def __init__(self, config_path: str = None):
        self.config = self._load_config(config_path)
        self.evaluation_history = []

        logger.info("EnhancedObjectiveEvaluator 초기화 완료")

    def _load_config(self, config_path: str = None) -> Dict[str, Any]:
        """설정 로드 (기본값 또는 파일에서)"""
        if config_path and Path(config_path).exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)

        # 기본 설정 (day35_pack 기반 + 개선)
        return {
            "version": 2,
            "objective": {
                "form": "weighted_sum",
                "epsilon": 1.0e-6,
                "transforms": {
                    "latency": {
                        "kind": "logistic_inverse",
                        "target_ms": 1000,  # PoU 목표: 1000ms
                        "k_ms": 200,
                    },
                    "accuracy": {"kind": "linear_minmax", "min": 0.80, "max": 0.98},
                    "explainability": {
                        "kind": "linear_minmax",
                        "min": 0.60,
                        "max": 0.95,
                    },
                    "failure": {
                        "kind": "logistic_inverse",
                        "target_rate": 0.005,  # PoU 목표: 0.5%
                        "k_rate": 0.002,
                    },
                },
            },
            "weights": {
                "balanced": {
                    "latency": 0.25,
                    "accuracy": 0.35,
                    "explainability": 0.25,
                    "failure": 0.15,
                },
                "speed": {
                    "latency": 0.45,
                    "accuracy": 0.30,
                    "explainability": 0.15,
                    "failure": 0.10,
                },
                "quality": {
                    "latency": 0.15,
                    "accuracy": 0.45,
                    "explainability": 0.30,
                    "failure": 0.10,
                },
                "safety_first": {
                    "latency": 0.15,
                    "accuracy": 0.30,
                    "explainability": 0.15,
                    "failure": 0.40,
                },
                # PoU 특화 프리셋 추가
                "pou_optimized": {
                    "latency": 0.30,
                    "accuracy": 0.40,
                    "explainability": 0.20,
                    "failure": 0.10,
                },
            },
            "acceptance_criteria": {
                "max_p95_latency_ms": 1500,  # PoU 기준
                "min_accuracy": 0.85,
                "min_explainability": 0.70,
                "max_failure_rate": 0.01,
            },
        }

    def _normalize_value(self, value: float) -> float:
        """값 정규화 (0-1 또는 0-100 → 0-1)"""
        if value is None:
            return 0.0
        value = float(value)
        if value > 1.000001:  # 퍼센트로 처리
            return max(0.0, min(1.0, value / 100.0))
        return max(0.0, min(1.0, value))

    def _sigmoid(self, x: float) -> float:
        """시그모이드 함수"""
        return 1.0 / (1.0 + math.exp(-x))

    def _calculate_latency_utility(self, latency_ms: float) -> float:
        """지연시간 유틸리티 계산"""
        cfg = self.config["objective"]["transforms"]["latency"]
        target = float(cfg["target_ms"])
        k = float(cfg["k_ms"])
        return max(0.0, min(1.0, 1.0 - self._sigmoid((latency_ms - target) / k)))

    def _calculate_failure_utility(self, failure_rate: float) -> float:
        """실패율 유틸리티 계산"""
        cfg = self.config["objective"]["transforms"]["failure"]
        target = float(cfg["target_rate"])
        k = float(cfg["k_rate"])
        return max(0.0, min(1.0, 1.0 - self._sigmoid((failure_rate - target) / k)))

    def _calculate_linear_minmax_utility(
        self, value: float, min_val: float, max_val: float
    ) -> float:
        """선형 minmax 유틸리티 계산"""
        if max_val <= min_val:
            return 0.0
        return max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))

    def _calculate_utilities(self, metrics: Metrics) -> Utilities:
        """모든 유틸리티 계산"""
        transforms = self.config["objective"]["transforms"]

        # 지연시간 유틸리티
        latency_util = self._calculate_latency_utility(metrics.latency_ms)

        # 정확도 유틸리티
        acc_cfg = transforms["accuracy"]
        accuracy_util = self._calculate_linear_minmax_utility(
            metrics.accuracy, acc_cfg["min"], acc_cfg["max"]
        )

        # 설명성 유틸리티
        exp_cfg = transforms["explainability"]
        explainability_util = self._calculate_linear_minmax_utility(
            metrics.explainability, exp_cfg["min"], exp_cfg["max"]
        )

        # 실패율 유틸리티
        failure_util = self._calculate_failure_utility(metrics.failure_rate)

        return Utilities(
            latency=latency_util,
            accuracy=accuracy_util,
            explainability=explainability_util,
            failure=failure_util,
        )

    def _check_constraints(self, metrics: Metrics) -> Tuple[bool, List[str]]:
        """제약 조건 검사"""
        criteria = self.config["acceptance_criteria"]
        violations = []

        if metrics.latency_ms > criteria["max_p95_latency_ms"]:
            violations.append(f"latency_ms > {criteria['max_p95_latency_ms']}")

        if metrics.accuracy < criteria["min_accuracy"]:
            violations.append(f"accuracy < {criteria['min_accuracy']}")

        if metrics.explainability < criteria["min_explainability"]:
            violations.append(f"explainability < {criteria['min_explainability']}")

        if metrics.failure_rate > criteria["max_failure_rate"]:
            violations.append(f"failure_rate > {criteria['max_failure_rate']}")

        return len(violations) == 0, violations

    def evaluate(
        self, metrics: Metrics, preset_name: str = "balanced"
    ) -> ObjectiveResult:
        """목적함수 평가"""
        # 가중치 로드
        weights = self.config["weights"].get(
            preset_name, self.config["weights"]["balanced"]
        )

        # 유틸리티 계산
        utilities = self._calculate_utilities(metrics)

        # 목적함수 J 계산
        J = (
            weights["latency"] * utilities.latency
            + weights["accuracy"] * utilities.accuracy
            + weights["explainability"] * utilities.explainability
            + weights["failure"] * utilities.failure
        )

        # 제약 조건 검사
        constraints_ok, violations = self._check_constraints(metrics)

        # 결과 생성
        result = ObjectiveResult(
            metrics=metrics,
            utilities=utilities,
            weights=weights,
            J=J,
            constraints_ok=constraints_ok,
            violations=violations,
            preset_name=preset_name,
            timestamp=datetime.now(),
        )

        # 히스토리에 추가
        self.evaluation_history.append(result)

        return result

    def compare_presets(self, metrics: Metrics) -> Dict[str, ObjectiveResult]:
        """모든 프리셋 비교"""
        results = {}
        for preset_name in self.config["weights"].keys():
            results[preset_name] = self.evaluate(metrics, preset_name)
        return results

    def find_optimal_preset(self, metrics: Metrics) -> Tuple[str, ObjectiveResult]:
        """최적 프리셋 찾기"""
        comparisons = self.compare_presets(metrics)

        # 제약 조건을 만족하는 것 중에서 J가 가장 높은 것 선택
        valid_results = {k: v for k, v in comparisons.items() if v.constraints_ok}

        if not valid_results:
            # 제약 조건을 만족하는 것이 없으면 J가 가장 높은 것 선택
            best_preset = max(comparisons.keys(), key=lambda k: comparisons[k].J)
            return best_preset, comparisons[best_preset]

        best_preset = max(valid_results.keys(), key=lambda k: valid_results[k].J)
        return best_preset, valid_results[best_preset]

    def generate_report(self, results: Dict[str, ObjectiveResult]) -> str:
        """비교 보고서 생성"""
        report = f"""
# Day 35 멀티목표 목적함수(J) 분석 보고서

## 성능 지표
- **지연시간**: {results['balanced'].metrics.latency_ms:.0f}ms
- **정확도**: {results['balanced'].metrics.accuracy:.2%}
- **설명성**: {results['balanced'].metrics.explainability:.2%}
- **실패율**: {results['balanced'].metrics.failure_rate:.3%}

## 프리셋별 목적함수(J) 비교
"""
        for preset_name, result in results.items():
            status = "✅" if result.constraints_ok else "❌"
            report += f"- **{preset_name}**: J = {result.J:.4f} {status}\n"

        # 최적 프리셋 찾기
        optimal_preset, optimal_result = self.find_optimal_preset(
            results["balanced"].metrics
        )

        report += f"""
## 권장 프리셋
- **최적 프리셋**: {optimal_preset}
- **목적함수 값**: {optimal_result.J:.4f}
- **제약 조건**: {'통과' if optimal_result.constraints_ok else '위반'}

## 개선 방향
"""
        utilities = optimal_result.utilities
        if utilities.latency < 0.5:
            report += "- 지연시간 개선 필요\n"
        if utilities.accuracy < 0.7:
            report += "- 정확도 개선 필요\n"
        if utilities.explainability < 0.6:
            report += "- 설명성 개선 필요\n"
        if utilities.failure < 0.5:
            report += "- 실패율 감소 필요\n"

        return report


class PoUPerformanceMonitor:
    """PoU 성능 모니터링 시스템"""

    def __init__(self):
        self.evaluator = EnhancedObjectiveEvaluator()
        self.performance_history = []

        logger.info("PoUPerformanceMonitor 초기화 완료")

    def load_pou_metrics(self, domain: str) -> Metrics:
        """PoU 도메인별 성능 지표 로드"""
        # 실제 환경에서는 PoU 로그에서 로드
        # 여기서는 시뮬레이션 데이터 사용

        if domain == "medical":
            return Metrics(
                latency_ms=654.8,  # Day 31-34 평균
                accuracy=0.878,  # Day 31-34 평균
                explainability=0.970,  # Day 31-34 평균
                failure_rate=0.0012,  # Day 31-34 평균
            )
        elif domain == "rehab":
            return Metrics(
                latency_ms=602.0,  # Day 32 최적화 결과
                accuracy=0.917,  # Day 32 최적화 결과
                explainability=0.967,  # Day 32 최적화 결과
                failure_rate=0.0002,  # Day 32 최적화 결과
            )
        elif domain == "coding":
            return Metrics(
                latency_ms=700.0,  # Day 33 예상
                accuracy=0.900,  # Day 33 예상
                explainability=0.950,  # Day 33 예상
                failure_rate=0.0008,  # Day 33 예상
            )
        else:
            # 전체 평균
            return Metrics(
                latency_ms=652.3,
                accuracy=0.898,
                explainability=0.962,
                failure_rate=0.0007,
            )

    async def monitor_domain(self, domain: str) -> Dict[str, ObjectiveResult]:
        """도메인별 성능 모니터링"""
        logger.info(f"{domain} 도메인 성능 모니터링 시작")

        metrics = self.load_pou_metrics(domain)
        results = self.evaluator.compare_presets(metrics)

        # 히스토리에 저장
        self.performance_history.append(
            {"domain": domain, "timestamp": datetime.now(), "results": results}
        )

        return results

    async def monitor_all_domains(self) -> Dict[str, Dict[str, ObjectiveResult]]:
        """모든 도메인 모니터링"""
        domains = ["medical", "rehab", "coding", "overall"]
        all_results = {}

        for domain in domains:
            all_results[domain] = await self.monitor_domain(domain)

        return all_results

    def generate_comprehensive_report(
        self, all_results: Dict[str, Dict[str, ObjectiveResult]]
    ) -> str:
        """종합 보고서 생성"""
        report = f"""
# Day 35 PoU 멀티목표 최적화 종합 보고서

## 도메인별 성능 분석
"""

        for domain, results in all_results.items():
            optimal_preset, optimal_result = self.evaluator.find_optimal_preset(
                results["balanced"].metrics
            )

            report += f"""
### {domain.upper()} 도메인
- **최적 프리셋**: {optimal_preset}
- **목적함수(J)**: {optimal_result.J:.4f}
- **지연시간**: {optimal_result.metrics.latency_ms:.0f}ms
- **정확도**: {optimal_result.metrics.accuracy:.2%}
- **설명성**: {optimal_result.metrics.explainability:.2%}
- **실패율**: {optimal_result.metrics.failure_rate:.3%}
- **제약 조건**: {'통과' if optimal_result.constraints_ok else '위반'}
"""

        # 전체 권장사항
        report += """
## 전체 권장사항
1. **pou_optimized 프리셋** 적용 권장
2. **실시간 모니터링** 시스템 구축
3. **Day36 A/B 테스트** 준비
4. **주기적 파라미터 재튜닝** 필요
"""

        return report


async def main():
    """메인 함수"""
    logger.info("Day 35 Enhanced: 멀티목표 목적함수 파라미터 튜닝 시작")

    # PoU 성능 모니터링 시스템 초기화
    monitor = PoUPerformanceMonitor()

    # 모든 도메인 모니터링
    all_results = await monitor.monitor_all_domains()

    # 종합 보고서 생성
    report = monitor.generate_comprehensive_report(all_results)

    # 보고서 저장
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"day35_enhanced_report_{timestamp}.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)

    logger.info(f"Day 35 Enhanced 완료. 보고서 저장: {report_file}")

    # 결과 출력
    print("\n" + "=" * 60)
    print("Day 35 Enhanced: 멀티목표 목적함수 파라미터 튜닝 결과")
    print("=" * 60)

    for domain, results in all_results.items():
        optimal_preset, optimal_result = monitor.evaluator.find_optimal_preset(
            results["balanced"].metrics
        )
        print(f"{domain.upper()}: {optimal_preset} (J={optimal_result.J:.4f})")

    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
