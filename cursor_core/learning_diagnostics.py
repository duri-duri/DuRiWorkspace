#!/usr/bin/env python3
"""
DuRi 메타-코딩 학습 진단 시스템
DuRi가 자기 자신의 코드를 분석하고 개선하는 시스템
"""

import ast
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List

import psutil

logger = logging.getLogger(__name__)


@dataclass
class CodeAnalysisResult:
    """코드 분석 결과"""

    module_name: str
    complexity_score: float
    performance_score: float
    maintainability_score: float
    improvement_suggestions: List[str]
    execution_time: float
    memory_usage: float


@dataclass
class PerformanceMetrics:
    """성능 메트릭"""

    response_time: float
    accuracy: float
    efficiency: float
    resource_usage: float
    overall_score: float


class CodeAnalyzer:
    """DuRi 코드 분석기"""

    def __init__(self):
        self.analysis_history: List[CodeAnalysisResult] = []
        logger.info("CodeAnalyzer 초기화 완료")

    def analyze_module(self, module_path: str) -> CodeAnalysisResult:
        """모듈 분석"""
        try:
            with open(module_path, "r", encoding="utf-8") as f:
                source_code = f.read()

            tree = ast.parse(source_code)

            # 복잡도 분석
            complexity = self._calculate_complexity(tree)

            # 성능 분석
            performance = self._analyze_performance(module_path)

            # 유지보수성 분석
            maintainability = self._analyze_maintainability(tree)

            # 개선 제안
            suggestions = self._generate_improvement_suggestions(tree, complexity, performance)

            result = CodeAnalysisResult(
                module_name=module_path,
                complexity_score=complexity,
                performance_score=performance,
                maintainability_score=maintainability,
                improvement_suggestions=suggestions,
                execution_time=0.0,
                memory_usage=0.0,
            )

            self.analysis_history.append(result)
            logger.info(f"모듈 분석 완료: {module_path}")
            return result

        except Exception as e:
            logger.error(f"모듈 분석 실패: {e}")
            return CodeAnalysisResult(
                module_name=module_path,
                complexity_score=0.0,
                performance_score=0.0,
                maintainability_score=0.0,
                improvement_suggestions=["분석 실패"],
                execution_time=0.0,
                memory_usage=0.0,
            )

    def _calculate_complexity(self, tree: ast.AST) -> float:
        """순환 복잡도 계산"""
        complexity = 0
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.While, ast.For, ast.ExceptHandler)):
                complexity += 1
            elif isinstance(node, ast.FunctionDef):
                complexity += 1
        return complexity

    def _analyze_performance(self, module_path: str) -> float:
        """성능 분석"""
        try:
            # 간단한 성능 지표 계산
            file_size = os.path.getsize(module_path)  # noqa: F841
            with open(module_path, "r") as f:
                lines = f.readlines()

            # 코드 라인 수, 함수 수 등 기반 성능 점수
            line_count = len(lines)
            function_count = sum(1 for line in lines if line.strip().startswith("def "))

            # 성능 점수 계산 (간단한 휴리스틱)
            performance_score = max(0, 100 - (line_count * 0.1) - (function_count * 2))
            return performance_score / 100.0

        except Exception as e:
            logger.error(f"성능 분석 실패: {e}")
            return 0.5

    def _analyze_maintainability(self, tree: ast.AST) -> float:
        """유지보수성 분석"""
        try:
            # 간단한 유지보수성 지표
            function_count = len([n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)])
            class_count = len([n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)])  # noqa: F841

            # 함수당 평균 라인 수 계산
            total_lines = 0
            for node in ast.walk(tree):
                if hasattr(node, "lineno"):
                    total_lines = max(total_lines, node.lineno)

            avg_lines_per_function = total_lines / max(function_count, 1)

            # 유지보수성 점수 계산
            maintainability_score = max(0, 100 - avg_lines_per_function * 2)
            return maintainability_score / 100.0

        except Exception as e:
            logger.error(f"유지보수성 분석 실패: {e}")
            return 0.5

    def _generate_improvement_suggestions(self, tree: ast.AST, complexity: float, performance: float) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        if complexity > 10:
            suggestions.append("복잡도가 높습니다. 함수를 더 작은 단위로 분해하세요.")

        if performance < 0.6:
            suggestions.append("성능이 낮습니다. 알고리즘 최적화를 고려하세요.")

        # 함수 길이 분석
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if len(node.body) > 20:
                    suggestions.append(f"함수 '{node.name}'이 너무 깁니다. 분해를 고려하세요.")

        return suggestions


class PerformanceScorer:
    """성능 점수 계산기"""

    def __init__(self):
        self.performance_history: List[PerformanceMetrics] = []
        logger.info("PerformanceScorer 초기화 완료")

    def measure_performance(self, func, *args, **kwargs) -> PerformanceMetrics:
        """함수 성능 측정"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss

        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = None  # noqa: F841
            success = False
            logger.error(f"함수 실행 실패: {e}")

        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss

        execution_time = end_time - start_time
        memory_usage = (end_memory - start_memory) / 1024 / 1024  # MB

        # 성능 점수 계산
        response_time_score = max(0, 1 - execution_time / 10)  # 10초 기준
        accuracy_score = 1.0 if success else 0.0
        efficiency_score = max(0, 1 - memory_usage / 100)  # 100MB 기준
        resource_score = max(0, 1 - (execution_time + memory_usage / 10) / 20)

        overall_score = (response_time_score + accuracy_score + efficiency_score + resource_score) / 4

        metrics = PerformanceMetrics(
            response_time=execution_time,
            accuracy=accuracy_score,
            efficiency=efficiency_score,
            resource_usage=memory_usage,
            overall_score=overall_score,
        )

        self.performance_history.append(metrics)
        return metrics

    def get_average_performance(self) -> float:
        """평균 성능 점수"""
        if not self.performance_history:
            return 0.0
        return sum(m.overall_score for m in self.performance_history) / len(self.performance_history)


class ImprovementStrategist:
    """개선 전략 수립기"""

    def __init__(self):
        self.improvement_history: List[Dict[str, Any]] = []
        logger.info("ImprovementStrategist 초기화 완료")

    def generate_improvement_plan(self, analysis_result: CodeAnalysisResult) -> Dict[str, Any]:
        """개선 계획 생성"""
        plan = {
            "target_module": analysis_result.module_name,
            "priority": "high" if analysis_result.complexity_score > 0.7 else "medium",
            "strategies": [],
            "estimated_impact": 0.0,
        }

        # 복잡도 기반 전략
        if analysis_result.complexity_score > 0.7:
            plan["strategies"].append(
                {
                    "type": "refactor",
                    "description": "함수 분해 및 모듈화",
                    "impact": 0.3,
                }
            )

        # 성능 기반 전략
        if analysis_result.performance_score < 0.6:
            plan["strategies"].append({"type": "optimize", "description": "알고리즘 최적화", "impact": 0.4})

        # 유지보수성 기반 전략
        if analysis_result.maintainability_score < 0.5:
            plan["strategies"].append({"type": "restructure", "description": "코드 구조 개선", "impact": 0.2})

        # 예상 영향도 계산
        total_impact = sum(strategy["impact"] for strategy in plan["strategies"])
        plan["estimated_impact"] = min(1.0, total_impact)

        self.improvement_history.append(plan)
        return plan


class MetaLearningLogger:
    """메타 학습 로거"""

    def __init__(self):
        self.growth_log: List[Dict[str, Any]] = []
        logger.info("MetaLearningLogger 초기화 완료")

    def log_improvement_attempt(
        self,
        module_name: str,
        before_metrics: PerformanceMetrics,
        after_metrics: PerformanceMetrics,
        improvement_plan: Dict[str, Any],
        success: bool,
    ) -> None:
        """개선 시도 로깅"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "module_name": module_name,
            "before_metrics": {
                "response_time": before_metrics.response_time,
                "overall_score": before_metrics.overall_score,
            },
            "after_metrics": {
                "response_time": after_metrics.response_time,
                "overall_score": after_metrics.overall_score,
            },
            "improvement_plan": improvement_plan,
            "success": success,
            "improvement_rate": (after_metrics.overall_score - before_metrics.overall_score)
            / max(before_metrics.overall_score, 0.01),
        }

        self.growth_log.append(log_entry)
        logger.info(f"개선 시도 로깅: {module_name}, 성공: {success}, 개선률: {log_entry['improvement_rate']:.2%}")

    def get_growth_statistics(self) -> Dict[str, Any]:
        """성장 통계"""
        if not self.growth_log:
            return {"total_attempts": 0, "success_rate": 0.0, "avg_improvement": 0.0}

        total_attempts = len(self.growth_log)
        successful_attempts = sum(1 for log in self.growth_log if log["success"])
        success_rate = successful_attempts / total_attempts

        improvements = [log["improvement_rate"] for log in self.growth_log if log["success"]]
        avg_improvement = sum(improvements) / len(improvements) if improvements else 0.0

        return {
            "total_attempts": total_attempts,
            "success_rate": success_rate,
            "avg_improvement": avg_improvement,
            "recent_attempts": (self.growth_log[-5:] if len(self.growth_log) >= 5 else self.growth_log),
        }


class DuRiSelfGrowthManager:
    """DuRi 자기 성장 관리자"""

    def __init__(self):
        self.code_analyzer = CodeAnalyzer()
        self.performance_scorer = PerformanceScorer()
        self.improvement_strategist = ImprovementStrategist()
        self.meta_logger = MetaLearningLogger()
        logger.info("DuRiSelfGrowthManager 초기화 완료")

    def analyze_and_improve(self, module_path: str) -> Dict[str, Any]:
        """분석 및 개선 수행"""
        logger.info(f"모듈 분석 및 개선 시작: {module_path}")

        # 1. 현재 상태 분석
        analysis_result = self.code_analyzer.analyze_module(module_path)

        # 2. 현재 성능 측정
        def current_performance_test():
            # 간단한 성능 테스트 (실제로는 더 복잡한 테스트 필요)
            time.sleep(0.1)
            return True

        before_metrics = self.performance_scorer.measure_performance(current_performance_test)

        # 3. 개선 계획 수립
        improvement_plan = self.improvement_strategist.generate_improvement_plan(analysis_result)

        # 4. 개선 시도 (실제로는 코드 수정 로직 필요)
        success = self._attempt_improvement(module_path, improvement_plan)

        # 5. 개선 후 성능 측정
        after_metrics = self.performance_scorer.measure_performance(current_performance_test)

        # 6. 결과 로깅
        self.meta_logger.log_improvement_attempt(module_path, before_metrics, after_metrics, improvement_plan, success)

        return {
            "analysis_result": analysis_result,
            "improvement_plan": improvement_plan,
            "before_metrics": before_metrics,
            "after_metrics": after_metrics,
            "success": success,
            "growth_statistics": self.meta_logger.get_growth_statistics(),
        }

    def _attempt_improvement(self, module_path: str, improvement_plan: Dict[str, Any]) -> bool:
        """개선 시도 (실제 구현 필요)"""
        try:
            # 실제로는 여기서 코드 수정 로직이 들어가야 함
            # 현재는 시뮬레이션
            logger.info(f"개선 시도: {module_path}")
            return True
        except Exception as e:
            logger.error(f"개선 시도 실패: {e}")
            return False

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "total_analyses": len(self.code_analyzer.analysis_history),
            "total_performance_tests": len(self.performance_scorer.performance_history),
            "total_improvement_plans": len(self.improvement_strategist.improvement_history),
            "growth_statistics": self.meta_logger.get_growth_statistics(),
        }


# 전역 인스턴스
self_growth_manager = DuRiSelfGrowthManager()
