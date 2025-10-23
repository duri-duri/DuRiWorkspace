#!/usr/bin/env python3
"""
DuRi 고급 메타-학습 시스템
ChatGPT가 제안한 핵심 병목 제거 시스템
"""

import json
import logging
import math
import random
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class LearningTargetType(Enum):
    """학습 목표 타입"""

    PERFORMANCE = "performance"
    ACCURACY = "accuracy"
    MEMORY_EFFICIENCY = "memory_efficiency"
    STABILITY = "stability"
    COMPLEXITY_REDUCTION = "complexity_reduction"


class StrategyType(Enum):
    """개선 전략 타입"""

    REFACTOR = "refactor"
    OPTIMIZE = "optimize"
    RESTRUCTURE = "restructure"
    SIMPLIFY = "simplify"
    CACHE = "cache"
    PARALLELIZE = "parallelize"


class FailurePattern(Enum):
    """실패 패턴 분류"""

    COMPLEXITY_INCREASE = "complexity_increase"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    MEMORY_OVERFLOW = "memory_overflow"
    LOGIC_ERROR = "logic_error"
    TIMEOUT = "timeout"
    UNEXPECTED_BEHAVIOR = "unexpected_behavior"


@dataclass
class LearningTarget:
    """학습 목표 정의"""

    target_type: LearningTargetType
    current_value: float
    target_value: float
    weight: float = 1.0
    tolerance: float = 0.1
    is_achieved: bool = False


@dataclass
class StrategyPerformance:
    """전략 성능 기록"""

    strategy_type: StrategyType
    success_count: int = 0
    failure_count: int = 0
    total_improvement: float = 0.0
    average_improvement: float = 0.0
    last_used: Optional[datetime] = None
    confidence: float = 0.5


@dataclass
class FailureAnalysis:
    """실패 분석 결과"""

    pattern: FailurePattern
    root_cause: str
    affected_metrics: List[str]
    strategy_used: StrategyType
    code_pattern: str
    external_factors: List[str]
    confidence: float


class LearningTargetManager:
    """학습 목표 관리자 - ChatGPT 제안 #1"""

    def __init__(self):
        self.targets: Dict[LearningTargetType, LearningTarget] = {}
        self.learning_complete = False
        self.iteration_count = 0
        self.max_iterations = 100
        logger.info("LearningTargetManager 초기화 완료")

    def set_target(
        self,
        target_type: LearningTargetType,
        current: float,
        target: float,
        weight: float = 1.0,
        tolerance: float = 0.1,
    ):
        """학습 목표 설정"""
        self.targets[target_type] = LearningTarget(
            target_type=target_type,
            current_value=current,
            target_value=target,
            weight=weight,
            tolerance=tolerance,
        )
        logger.info(f"학습 목표 설정: {target_type.value} {current} → {target}")

    def update_progress(self, target_type: LearningTargetType, new_value: float):
        """목표 진행도 업데이트"""
        if target_type in self.targets:
            target = self.targets[target_type]
            target.current_value = new_value

            # 목표 달성 확인
            if abs(new_value - target.target_value) <= target.tolerance:
                target.is_achieved = True
                logger.info(f"목표 달성: {target_type.value} = {new_value}")

            # 전체 목표 달성 확인
            self._check_overall_completion()

    def _check_overall_completion(self):
        """전체 목표 달성 확인"""
        achieved_count = sum(
            1 for target in self.targets.values() if target.is_achieved
        )
        total_count = len(self.targets)

        if achieved_count >= total_count * 0.8:  # 80% 달성 시 완료
            self.learning_complete = True
            logger.info("🎉 모든 학습 목표 달성!")

    def should_continue_learning(self) -> bool:
        """학습 계속 여부 결정"""
        if self.learning_complete:
            return False

        if self.iteration_count >= self.max_iterations:
            logger.warning("최대 반복 횟수 도달")
            return False

        # 개선률이 임계치 미만이면 중단
        recent_improvements = self._get_recent_improvements()
        if recent_improvements and max(recent_improvements) < 0.05:  # 5% 미만 개선
            logger.info("개선률 임계치 미달로 학습 중단")
            return False

        return True

    def _get_recent_improvements(self) -> List[float]:
        """최근 개선률 조회 (실제로는 DB에서 조회)"""
        return [0.1, 0.05, 0.02, 0.01]  # 시뮬레이션

    def get_priority_target(self) -> Optional[LearningTargetType]:
        """우선순위가 높은 목표 반환"""
        for target_type, target in self.targets.items():
            if not target.is_achieved:
                progress = (
                    target.current_value - target.target_value
                ) / target.target_value
                if progress < 0.5:  # 50% 미만 달성
                    return target_type
        return None

    def get_overall_progress(self) -> float:
        """전체 진행도 계산"""
        if not self.targets:
            return 0.0

        total_progress = 0.0
        total_weight = 0.0

        for target in self.targets.values():
            progress = min(1.0, target.current_value / target.target_value)
            total_progress += progress * target.weight
            total_weight += target.weight

        return total_progress / total_weight if total_weight > 0 else 0.0


class ImprovementSelector:
    """개선 전략 선택기 - ChatGPT 제안 #2 (다중 무장 밴딧 기반)"""

    def __init__(self):
        self.strategies: Dict[StrategyType, StrategyPerformance] = {}
        self.exploration_rate = 0.3
        self.confidence_threshold = 0.7
        self._initialize_strategies()
        logger.info("ImprovementSelector 초기화 완료")

    def _initialize_strategies(self):
        """전략 초기화"""
        for strategy in StrategyType:
            self.strategies[strategy] = StrategyPerformance(
                strategy_type=strategy, confidence=0.5  # 초기 신뢰도
            )

    def select_strategy(self, context: Dict[str, Any]) -> StrategyType:
        """상황에 맞는 최적 전략 선택"""
        # 1. 탐험 vs 활용 결정
        if random.random() < self.exploration_rate:
            return self._explore_new_strategy()
        else:
            return self._exploit_best_strategy()

    def _explore_new_strategy(self) -> StrategyType:
        """새로운 전략 탐험"""
        # 사용 빈도가 낮은 전략 우선 선택
        unused_strategies = [
            strategy
            for strategy, perf in self.strategies.items()
            if perf.success_count + perf.failure_count < 3
        ]

        if unused_strategies:
            return random.choice(unused_strategies)
        else:
            # 신뢰도가 낮은 전략 선택
            low_confidence = [
                strategy
                for strategy, perf in self.strategies.items()
                if perf.confidence < self.confidence_threshold
            ]
            return (
                random.choice(low_confidence)
                if low_confidence
                else random.choice(list(self.strategies.keys()))
            )

    def _exploit_best_strategy(self) -> StrategyType:
        """최고 성능 전략 활용"""
        # UCB1 (Upper Confidence Bound) 알고리즘 적용
        best_strategy = None
        best_score = -float("inf")

        for strategy, perf in self.strategies.items():
            if perf.success_count + perf.failure_count == 0:
                continue

            # UCB1 점수 계산
            exploitation = perf.average_improvement
            exploration = math.sqrt(
                2
                * math.log(self._get_total_trials())
                / (perf.success_count + perf.failure_count)
            )
            ucb_score = exploitation + exploration

            if ucb_score > best_score:
                best_score = ucb_score
                best_strategy = strategy

        return (
            best_strategy
            if best_strategy
            else random.choice(list(self.strategies.keys()))
        )

    def _get_total_trials(self) -> int:
        """총 시도 횟수"""
        return sum(
            perf.success_count + perf.failure_count for perf in self.strategies.values()
        )

    def update_strategy_performance(
        self, strategy: StrategyType, success: bool, improvement: float
    ):
        """전략 성능 업데이트"""
        if strategy not in self.strategies:
            return

        perf = self.strategies[strategy]

        if success:
            perf.success_count += 1
            perf.total_improvement += improvement
        else:
            perf.failure_count += 1

        # 평균 개선률 계산
        total_attempts = perf.success_count + perf.failure_count
        if total_attempts > 0:
            perf.average_improvement = (
                perf.total_improvement / perf.success_count
                if perf.success_count > 0
                else 0
            )

        # 신뢰도 계산 (Thompson Sampling 기반)
        success_rate = (
            perf.success_count / total_attempts if total_attempts > 0 else 0.5
        )
        perf.confidence = success_rate

        perf.last_used = datetime.now()

        logger.info(
            f"전략 성능 업데이트: {strategy.value}, 성공: {success}, 개선률: {improvement:.3f}"
        )

    def get_strategy_recommendations(self) -> List[Tuple[StrategyType, float]]:
        """전략 추천 목록"""
        recommendations = []

        for strategy, perf in self.strategies.items():
            if (
                perf.success_count + perf.failure_count >= 3
            ):  # 충분한 데이터가 있는 전략만
                score = perf.average_improvement * perf.confidence
                recommendations.append((strategy, score))

        # 점수 순으로 정렬
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations


class FailurePatternClassifier:
    """실패 패턴 분류기 - ChatGPT 제안 #3"""

    def __init__(self):
        self.failure_patterns: Dict[FailurePattern, Dict[str, Any]] = {}
        self.pattern_database: List[FailureAnalysis] = []
        self._initialize_patterns()
        logger.info("FailurePatternClassifier 초기화 완료")

    def _initialize_patterns(self):
        """패턴 초기화"""
        self.failure_patterns = {
            FailurePattern.COMPLEXITY_INCREASE: {
                "indicators": [
                    "cyclomatic_complexity",
                    "function_length",
                    "nesting_depth",
                ],
                "thresholds": {"complexity": 10, "length": 50, "depth": 5},
            },
            FailurePattern.PERFORMANCE_DEGRADATION: {
                "indicators": ["execution_time", "memory_usage", "cpu_usage"],
                "thresholds": {"time": 1.0, "memory": 100, "cpu": 80},
            },
            FailurePattern.MEMORY_OVERFLOW: {
                "indicators": ["memory_usage", "memory_leak", "garbage_collection"],
                "thresholds": {"usage": 200, "leak": 0.1, "gc_frequency": 10},
            },
            FailurePattern.LOGIC_ERROR: {
                "indicators": ["exception_count", "error_rate", "unexpected_output"],
                "thresholds": {"exceptions": 1, "error_rate": 0.1, "unexpected": 1},
            },
            FailurePattern.TIMEOUT: {
                "indicators": [
                    "execution_time",
                    "timeout_threshold",
                    "resource_contention",
                ],
                "thresholds": {"time": 5.0, "timeout": 10.0, "contention": 0.8},
            },
            FailurePattern.UNEXPECTED_BEHAVIOR: {
                "indicators": [
                    "output_variance",
                    "state_inconsistency",
                    "side_effects",
                ],
                "thresholds": {"variance": 0.2, "inconsistency": 1, "side_effects": 2},
            },
        }

    def classify_failure(
        self,
        strategy_used: StrategyType,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float],
        error_message: Optional[str] = None,
        code_context: Optional[str] = None,
    ) -> FailureAnalysis:
        """실패 패턴 분류"""

        # 1. 메트릭 변화 분석
        metric_changes = self._analyze_metric_changes(metrics_before, metrics_after)

        # 2. 패턴 매칭
        matched_patterns = self._match_failure_patterns(metric_changes, error_message)

        # 3. 루트 원인 분석
        root_cause = self._analyze_root_cause(
            matched_patterns, strategy_used, code_context
        )

        # 4. 신뢰도 계산
        confidence = self._calculate_confidence(matched_patterns, metric_changes)

        # 5. 영향받은 메트릭 식별
        affected_metrics = self._identify_affected_metrics(metric_changes)

        # 6. 외부 요인 분석
        external_factors = self._analyze_external_factors(metrics_after)

        # 가장 가능성 높은 패턴 선택
        primary_pattern = (
            max(matched_patterns, key=lambda x: x[1])[0]
            if matched_patterns
            else FailurePattern.UNEXPECTED_BEHAVIOR
        )

        analysis = FailureAnalysis(
            pattern=primary_pattern,
            root_cause=root_cause,
            affected_metrics=affected_metrics,
            strategy_used=strategy_used,
            code_pattern=code_context or "unknown",
            external_factors=external_factors,
            confidence=confidence,
        )

        # 데이터베이스에 저장
        self.pattern_database.append(analysis)

        logger.info(
            f"실패 패턴 분류: {primary_pattern.value}, 신뢰도: {confidence:.2f}"
        )

        return analysis

    def _analyze_metric_changes(
        self, before: Dict[str, float], after: Dict[str, float]
    ) -> Dict[str, float]:
        """메트릭 변화 분석"""
        changes = {}
        for metric in before:
            if metric in after:
                changes[metric] = (after[metric] - before[metric]) / max(
                    before[metric], 0.01
                )
        return changes

    def _match_failure_patterns(
        self, changes: Dict[str, float], error_message: Optional[str]
    ) -> List[Tuple[FailurePattern, float]]:
        """패턴 매칭"""
        matches = []

        for pattern, config in self.failure_patterns.items():
            score = 0.0
            indicators = config["indicators"]
            thresholds = config["thresholds"]

            # 메트릭 기반 매칭
            for indicator in indicators:
                if indicator in changes:
                    change = changes[indicator]
                    threshold = thresholds.get(indicator, 0.1)

                    if abs(change) > threshold:
                        score += 0.3
                    elif abs(change) > threshold * 0.5:
                        score += 0.1

            # 에러 메시지 기반 매칭
            if error_message:
                error_keywords = self._get_error_keywords(pattern)
                for keyword in error_keywords:
                    if keyword.lower() in error_message.lower():
                        score += 0.4

            if score > 0.1:  # 임계치 이상인 경우만
                matches.append((pattern, score))

        return matches

    def _get_error_keywords(self, pattern: FailurePattern) -> List[str]:
        """패턴별 에러 키워드"""
        keywords = {
            FailurePattern.COMPLEXITY_INCREASE: ["complex", "nested", "deep"],
            FailurePattern.PERFORMANCE_DEGRADATION: ["slow", "timeout", "performance"],
            FailurePattern.MEMORY_OVERFLOW: ["memory", "overflow", "leak"],
            FailurePattern.LOGIC_ERROR: ["error", "exception", "invalid"],
            FailurePattern.TIMEOUT: ["timeout", "hung", "blocked"],
            FailurePattern.UNEXPECTED_BEHAVIOR: ["unexpected", "wrong", "incorrect"],
        }
        return keywords.get(pattern, [])

    def _analyze_root_cause(
        self,
        matches: List[Tuple[FailurePattern, float]],
        strategy: StrategyType,
        code_context: Optional[str],
    ) -> str:
        """루트 원인 분석"""
        if not matches:
            return "알 수 없는 실패 원인"

        primary_pattern = matches[0][0]

        root_causes = {
            FailurePattern.COMPLEXITY_INCREASE: f"{strategy.value} 전략이 코드 복잡도를 증가시켰습니다",
            FailurePattern.PERFORMANCE_DEGRADATION: f"{strategy.value} 전략이 성능을 저하시켰습니다",
            FailurePattern.MEMORY_OVERFLOW: f"{strategy.value} 전략이 메모리 사용량을 증가시켰습니다",
            FailurePattern.LOGIC_ERROR: f"{strategy.value} 전략이 로직 오류를 발생시켰습니다",
            FailurePattern.TIMEOUT: f"{strategy.value} 전략이 실행 시간을 초과시켰습니다",
            FailurePattern.UNEXPECTED_BEHAVIOR: f"{strategy.value} 전략이 예상치 못한 동작을 유발했습니다",
        }

        return root_causes.get(primary_pattern, "알 수 없는 실패 원인")

    def _calculate_confidence(
        self, matches: List[Tuple[FailurePattern, float]], changes: Dict[str, float]
    ) -> float:
        """신뢰도 계산"""
        if not matches:
            return 0.1

        # 가장 높은 점수
        max_score = max(score for _, score in matches)

        # 매칭된 패턴 수
        pattern_count = len(matches)

        # 메트릭 변화의 명확성
        change_clarity = sum(1 for change in changes.values() if abs(change) > 0.1)

        confidence = min(
            1.0, (max_score * 0.6 + pattern_count * 0.2 + change_clarity * 0.2)
        )

        return confidence

    def _identify_affected_metrics(self, changes: Dict[str, float]) -> List[str]:
        """영향받은 메트릭 식별"""
        return [metric for metric, change in changes.items() if abs(change) > 0.05]

    def _analyze_external_factors(self, metrics: Dict[str, float]) -> List[str]:
        """외부 요인 분석"""
        factors = []

        if metrics.get("cpu_usage", 0) > 80:
            factors.append("높은 CPU 사용률")

        if metrics.get("memory_usage", 0) > 100:
            factors.append("높은 메모리 사용률")

        if metrics.get("disk_io", 0) > 50:
            factors.append("높은 디스크 I/O")

        return factors

    def get_failure_statistics(self) -> Dict[str, Any]:
        """실패 통계"""
        if not self.pattern_database:
            return {"total_failures": 0, "pattern_distribution": {}}

        pattern_counts = {}
        strategy_failures = {}

        for analysis in self.pattern_database:
            # 패턴별 카운트
            pattern_name = analysis.pattern.value
            pattern_counts[pattern_name] = pattern_counts.get(pattern_name, 0) + 1

            # 전략별 실패
            strategy_name = analysis.strategy_used.value
            if strategy_name not in strategy_failures:
                strategy_failures[strategy_name] = []
            strategy_failures[strategy_name].append(analysis.pattern.value)

        return {
            "total_failures": len(self.pattern_database),
            "pattern_distribution": pattern_counts,
            "strategy_failures": strategy_failures,
            "average_confidence": sum(a.confidence for a in self.pattern_database)
            / len(self.pattern_database),
        }


class AdvancedMetaLearningSystem:
    """고급 메타-학습 시스템 통합 관리자"""

    def __init__(self):
        self.target_manager = LearningTargetManager()
        self.strategy_selector = ImprovementSelector()
        self.failure_classifier = FailurePatternClassifier()
        self.learning_active = True
        logger.info("AdvancedMetaLearningSystem 초기화 완료")

    def start_learning_session(
        self, targets: Dict[LearningTargetType, Tuple[float, float, float]]
    ):
        """학습 세션 시작"""
        logger.info("🎯 고급 메타-학습 세션 시작")

        # 목표 설정
        for target_type, (current, target, weight) in targets.items():
            self.target_manager.set_target(target_type, current, target, weight)

        self.learning_active = True

    def execute_improvement_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """개선 사이클 실행"""
        if (
            not self.learning_active
            or not self.target_manager.should_continue_learning()
        ):
            return {"status": "completed", "reason": "목표 달성 또는 중단 조건"}

        # 1. 전략 선택
        strategy = self.strategy_selector.select_strategy(context)

        # 2. 개선 시도 (시뮬레이션)
        success, improvement, metrics_before, metrics_after = self._attempt_improvement(
            strategy, context
        )

        # 3. 성능 업데이트
        self.strategy_selector.update_strategy_performance(
            strategy, success, improvement
        )

        # 4. 목표 진행도 업데이트
        if success:
            self._update_target_progress(metrics_after)

        # 5. 실패 분석
        if not success:
            failure_analysis = self.failure_classifier.classify_failure(
                strategy, metrics_before, metrics_after
            )
            logger.warning(f"개선 실패: {failure_analysis.root_cause}")

        # 6. 반복 횟수 증가
        self.target_manager.iteration_count += 1

        return {
            "strategy": strategy.value,
            "success": success,
            "improvement": improvement,
            "progress": self.target_manager.get_overall_progress(),
            "iteration": self.target_manager.iteration_count,
        }

    def _attempt_improvement(
        self, strategy: StrategyType, context: Dict[str, Any]
    ) -> Tuple[bool, float, Dict[str, float], Dict[str, float]]:
        """개선 시도 (시뮬레이션)"""
        # 실제로는 여기서 실제 코드 개선을 수행
        metrics_before = {
            "performance": 0.7,
            "accuracy": 0.8,
            "memory_efficiency": 0.6,
            "stability": 0.9,
        }

        # 전략별 개선 시뮬레이션
        improvement_simulation = {
            StrategyType.REFACTOR: {"success_rate": 0.7, "improvement": 0.1},
            StrategyType.OPTIMIZE: {"success_rate": 0.6, "improvement": 0.15},
            StrategyType.RESTRUCTURE: {"success_rate": 0.5, "improvement": 0.2},
            StrategyType.SIMPLIFY: {"success_rate": 0.8, "improvement": 0.05},
            StrategyType.CACHE: {"success_rate": 0.6, "improvement": 0.12},
            StrategyType.PARALLELIZE: {"success_rate": 0.4, "improvement": 0.25},
        }

        sim = improvement_simulation.get(
            strategy, {"success_rate": 0.5, "improvement": 0.1}
        )

        success = random.random() < sim["success_rate"]
        improvement = sim["improvement"] if success else -0.05

        metrics_after = {
            "performance": metrics_before["performance"] + improvement,
            "accuracy": metrics_before["accuracy"]
            + (improvement * 0.5 if success else -0.02),
            "memory_efficiency": metrics_before["memory_efficiency"]
            + (improvement * 0.3 if success else -0.01),
            "stability": metrics_before["stability"]
            + (improvement * 0.2 if success else -0.03),
        }

        return success, improvement, metrics_before, metrics_after

    def _update_target_progress(self, metrics: Dict[str, float]):
        """목표 진행도 업데이트"""
        for target_type in self.target_manager.targets:
            if target_type.value in metrics:
                self.target_manager.update_progress(
                    target_type, metrics[target_type.value]
                )

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "learning_active": self.learning_active,
            "overall_progress": self.target_manager.get_overall_progress(),
            "iteration_count": self.target_manager.iteration_count,
            "targets": {
                t.value: {
                    "current": tg.current_value,
                    "target": tg.target_value,
                    "achieved": tg.is_achieved,
                }
                for t, tg in self.target_manager.targets.items()
            },
            "strategy_recommendations": [
                (s.value, score)
                for s, score in self.strategy_selector.get_strategy_recommendations()
            ],
            "failure_statistics": self.failure_classifier.get_failure_statistics(),
        }


# 전역 인스턴스
advanced_meta_learning = AdvancedMetaLearningSystem()
