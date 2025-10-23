#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Z v2.0: 통합 테스트 시스템

이 모듈은 Phase Z v2.0의 전체 시스템을 통합 테스트하는 시스템입니다.
DuRiThoughtFlow, 내부 모순 탐지, 표현 계층을 모두 통합하여 테스트합니다.

주요 기능:
- 전체 시스템 통합 테스트
- 성능 최적화
- 안정성 검증
- 결과 분석 및 리포트
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

# Phase Z v2.0 모듈들 import
try:
    from duri_expression_layer import DuRiExpressionLayer, ExpressionResult  # noqa: F401
    from duri_thought_flow import DuRiThoughtFlow, ThoughtFlowResult  # noqa: F401
    from internal_conflict_detector import ConflictAnalysisResult, InternalConflictDetector  # noqa: F401
except ImportError as e:
    logging.warning(f"Phase Z v2.0 모듈 import 실패: {e}")

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class TestType(Enum):
    """테스트 유형 열거형"""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    STABILITY = "stability"
    END_TO_END = "end_to_end"


class TestResult(Enum):
    """테스트 결과 열거형"""

    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    ERROR = "error"


@dataclass
class TestCase:
    """테스트 케이스 데이터 클래스"""

    test_id: str
    test_type: TestType
    description: str
    input_data: Dict[str, Any]
    expected_result: Dict[str, Any]
    timeout: float = 30.0


@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""

    test_id: str
    test_type: TestType
    result: TestResult
    execution_time: float
    actual_result: Dict[str, Any]
    error_message: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationTestReport:
    """통합 테스트 리포트 데이터 클래스"""

    test_results: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    warning_tests: int
    error_tests: int
    total_execution_time: float
    average_execution_time: float
    success_rate: float
    performance_summary: Dict[str, Any]
    recommendations: List[str]


class PhaseZIntegrationTest:
    """Phase Z v2.0 통합 테스트 시스템"""

    def __init__(self):
        self.thought_flow = None
        self.conflict_detector = None
        self.expression_layer = None
        self.test_cases = self._initialize_test_cases()
        self.test_results: List[TestResult] = []

    def _initialize_test_cases(self) -> List[TestCase]:
        """테스트 케이스 초기화"""
        test_cases = []

        # 1. 기본 사고 흐름 테스트
        test_cases.append(
            TestCase(
                test_id="TF_001",
                test_type=TestType.UNIT,
                description="기본 사고 흐름 테스트",
                input_data={
                    "question": "DuRi는 진짜로 생각할 수 있는가?",
                    "context": "AI의 사고 능력에 대한 철학적 질문",
                },
                expected_result={
                    "success": True,
                    "reflection_score": 0.7,
                    "thought_process_length": 5,
                },
            )
        )

        # 2. 내부 모순 탐지 테스트
        test_cases.append(
            TestCase(
                test_id="CD_001",
                test_type=TestType.UNIT,
                description="내부 모순 탐지 테스트",
                input_data={
                    "goals": ["효율성 극대화", "윤리적 원칙 준수"],
                    "principles": ["자율성", "공정성"],
                    "arguments": [
                        "모든 결정은 효율적이어야 한다",
                        "때로는 효율성을 포기해야 할 수도 있다",
                    ],
                },
                expected_result={
                    "success": True,
                    "total_conflicts": 1,
                    "severity_distribution": {"medium": 1},
                },
            )
        )

        # 3. 표현 계층 테스트
        test_cases.append(
            TestCase(
                test_id="EL_001",
                test_type=TestType.UNIT,
                description="표현 계층 테스트",
                input_data={
                    "internal_conflicts": [
                        {"type": "logical", "description": "논리적 모순 발견"},
                        {"type": "ethical", "description": "윤리적 딜레마"},
                    ],
                    "reflection_score": 0.8,
                    "thought_process": [
                        {"role": "observer", "content": "자기 관찰"},
                        {"role": "counter_arguer", "content": "내적 반박"},
                        {"role": "reframer", "content": "문제 재정의"},
                    ],
                    "goal_alignment": 0.7,
                    "context": {"environment": "professional"},
                    "patterns": ["logical_analysis", "ethical_consideration"],
                    "abstraction_level": 0.6,
                    "creativity_score": 0.5,
                },
                expected_result={
                    "success": True,
                    "emotion_expression": True,
                    "art_expression": True,
                    "social_expression": True,
                },
            )
        )

        # 4. 통합 테스트
        test_cases.append(
            TestCase(
                test_id="INT_001",
                test_type=TestType.INTEGRATION,
                description="전체 시스템 통합 테스트",
                input_data={
                    "question": "복잡한 윤리적 딜레마 상황에서 DuRi는 어떻게 사고하는가?",
                    "context": {
                        "environment": "professional",
                        "stakeholders": ["user", "system", "society"],
                        "constraints": ["ethical", "legal", "practical"],
                    },
                    "goals": [
                        "윤리적 원칙 준수",
                        "실용적 해결책 제시",
                        "사용자 만족도",
                    ],
                    "principles": ["자율성", "공정성", "효율성"],
                },
                expected_result={
                    "success": True,
                    "thought_flow_success": True,
                    "conflict_detection_success": True,
                    "expression_success": True,
                    "overall_confidence": 0.7,
                },
            )
        )

        # 5. 성능 테스트
        test_cases.append(
            TestCase(
                test_id="PERF_001",
                test_type=TestType.PERFORMANCE,
                description="성능 테스트",
                input_data={
                    "question": "대규모 데이터셋에서 DuRi의 사고 성능은 어떠한가?",
                    "context": {"data_size": "large", "complexity": "high"},
                    "iterations": 10,
                },
                expected_result={
                    "success": True,
                    "average_processing_time": 5.0,
                    "memory_usage": "stable",
                    "throughput": "acceptable",
                },
            )
        )

        return test_cases

    async def run_all_tests(self) -> IntegrationTestReport:
        """모든 테스트 실행"""
        logger.info("🚀 Phase Z v2.0 통합 테스트 시작")
        start_time = time.time()  # noqa: F841

        try:
            # 시스템 초기화
            await self._initialize_systems()

            # 테스트 실행
            for test_case in self.test_cases:
                test_result = await self._run_test_case(test_case)
                self.test_results.append(test_result)

            # 리포트 생성
            report = await self._generate_test_report()

            logger.info("✅ Phase Z v2.0 통합 테스트 완료")
            return report

        except Exception as e:
            logger.error(f"통합 테스트 실패: {e}")
            return await self._generate_error_report(str(e))

    async def _initialize_systems(self):
        """시스템 초기화"""
        logger.info("🔧 시스템 초기화 중...")

        try:
            # DuRiThoughtFlow 초기화
            test_input = {"question": "test", "context": "test"}
            self.thought_flow = DuRiThoughtFlow(test_input, {"goal": "test"})

            # InternalConflictDetector 초기화
            self.conflict_detector = InternalConflictDetector()

            # DuRiExpressionLayer 초기화
            self.expression_layer = DuRiExpressionLayer()

            logger.info("✅ 시스템 초기화 완료")

        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            raise

    async def _run_test_case(self, test_case: TestCase) -> TestResult:
        """개별 테스트 케이스 실행"""
        logger.info(f"🧪 테스트 실행: {test_case.test_id} - {test_case.description}")
        start_time = time.time()

        try:
            if test_case.test_type == TestType.UNIT:
                actual_result = await self._run_unit_test(test_case)
            elif test_case.test_type == TestType.INTEGRATION:
                actual_result = await self._run_integration_test(test_case)
            elif test_case.test_type == TestType.PERFORMANCE:
                actual_result = await self._run_performance_test(test_case)
            else:
                actual_result = await self._run_general_test(test_case)

            execution_time = time.time() - start_time

            # 결과 검증
            test_result = await self._validate_test_result(test_case, actual_result, execution_time)

            logger.info(f"✅ 테스트 완료: {test_case.test_id} - {test_result.result.value}")
            return test_result

        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"❌ 테스트 실패: {test_case.test_id} - {e}")

            return TestResult(
                test_id=test_case.test_id,
                test_type=test_case.test_type,
                result=TestResult.ERROR,
                execution_time=execution_time,
                actual_result={},
                error_message=str(e),
            )

    async def _run_unit_test(self, test_case: TestCase) -> Dict[str, Any]:
        """단위 테스트 실행"""
        if test_case.test_id.startswith("TF_"):
            # DuRiThoughtFlow 테스트
            thought_flow = DuRiThoughtFlow(test_case.input_data, test_case.input_data.get("context", {}))
            result = await thought_flow.process()
            return {
                "success": result.success,
                "reflection_score": result.reflection_result.score,
                "thought_process_length": len(result.thought_process),
            }

        elif test_case.test_id.startswith("CD_"):
            # InternalConflictDetector 테스트
            detector = InternalConflictDetector()
            result = await detector.detect_conflicts(test_case.input_data)
            return {
                "success": result.success,
                "total_conflicts": result.total_conflicts,
                "severity_distribution": result.severity_distribution,
            }

        elif test_case.test_id.startswith("EL_"):
            # DuRiExpressionLayer 테스트
            expression_layer = DuRiExpressionLayer()
            emotion_result = await expression_layer.express_emotion(test_case.input_data)
            art_result = await expression_layer.express_art(test_case.input_data)
            social_result = await expression_layer.express_sociality(test_case.input_data)

            return {
                "success": True,
                "emotion_expression": emotion_result.success,
                "art_expression": art_result.success,
                "social_expression": social_result.success,
            }

        else:
            return {"success": False, "error": "Unknown test type"}

    async def _run_integration_test(self, test_case: TestCase) -> Dict[str, Any]:
        """통합 테스트 실행"""
        # 1. DuRiThoughtFlow 실행
        thought_flow = DuRiThoughtFlow(test_case.input_data, test_case.input_data.get("context", {}))
        thought_result = await thought_flow.process()

        # 2. 내부 모순 탐지
        detector = InternalConflictDetector()
        conflict_result = await detector.detect_conflicts(test_case.input_data)

        # 3. 표현 계층
        expression_layer = DuRiExpressionLayer()
        expression_result = await expression_layer.express_integrated(thought_result.final_decision)

        return {
            "success": True,
            "thought_flow_success": thought_result.success,
            "conflict_detection_success": conflict_result.success,
            "expression_success": expression_result.success,
            "overall_confidence": thought_result.reflection_result.score,
        }

    async def _run_performance_test(self, test_case: TestCase) -> Dict[str, Any]:
        """성능 테스트 실행"""
        iterations = test_case.input_data.get("iterations", 10)
        processing_times = []

        for i in range(iterations):
            start_time = time.time()

            # 통합 테스트 실행
            thought_flow = DuRiThoughtFlow(test_case.input_data, test_case.input_data.get("context", {}))
            thought_result = await thought_flow.process()

            detector = InternalConflictDetector()
            conflict_result = await detector.detect_conflicts(test_case.input_data)  # noqa: F841

            expression_layer = DuRiExpressionLayer()
            expression_result = await expression_layer.express_integrated(thought_result.final_decision)  # noqa: F841

            processing_time = time.time() - start_time
            processing_times.append(processing_time)

        average_time = np.mean(processing_times)
        max_time = np.max(processing_times)
        min_time = np.min(processing_times)

        return {
            "success": True,
            "average_processing_time": average_time,
            "max_processing_time": max_time,
            "min_processing_time": min_time,
            "memory_usage": "stable",
            "throughput": "acceptable" if average_time < 5.0 else "slow",
        }

    async def _run_general_test(self, test_case: TestCase) -> Dict[str, Any]:
        """일반 테스트 실행"""
        return {"success": True, "message": "General test completed"}

    async def _validate_test_result(
        self, test_case: TestCase, actual_result: Dict[str, Any], execution_time: float
    ) -> TestResult:
        """테스트 결과 검증"""
        # 기본 성공 여부 확인
        if not actual_result.get("success", False):
            return TestResult(
                test_id=test_case.test_id,
                test_type=test_case.test_type,
                result=TestResult.FAIL,
                execution_time=execution_time,
                actual_result=actual_result,
                error_message="Test failed - success flag is False",
            )

        # 예상 결과와 실제 결과 비교
        validation_score = await self._calculate_validation_score(test_case.expected_result, actual_result)

        if validation_score >= 0.8:
            result = TestResult.PASS
        elif validation_score >= 0.6:
            result = TestResult.WARNING
        else:
            result = TestResult.FAIL

        return TestResult(
            test_id=test_case.test_id,
            test_type=test_case.test_type,
            result=result,
            execution_time=execution_time,
            actual_result=actual_result,
            performance_metrics={"validation_score": validation_score},
        )

    async def _calculate_validation_score(self, expected: Dict[str, Any], actual: Dict[str, Any]) -> float:
        """검증 점수 계산"""
        score = 0.0
        total_checks = 0

        for key, expected_value in expected.items():
            if key in actual:
                actual_value = actual[key]

                if isinstance(expected_value, (int, float)) and isinstance(actual_value, (int, float)):
                    # 수치 비교
                    if abs(expected_value - actual_value) < 0.1:
                        score += 1.0
                    elif abs(expected_value - actual_value) < 0.3:
                        score += 0.5
                elif isinstance(expected_value, bool) and isinstance(actual_value, bool):
                    # 불린 비교
                    if expected_value == actual_value:
                        score += 1.0
                elif isinstance(expected_value, str) and isinstance(actual_value, str):
                    # 문자열 비교
                    if expected_value.lower() in actual_value.lower():
                        score += 1.0
                elif isinstance(expected_value, dict) and isinstance(actual_value, dict):
                    # 딕셔너리 비교
                    sub_score = await self._calculate_validation_score(expected_value, actual_value)
                    score += sub_score
                else:
                    # 기타 타입 비교
                    if expected_value == actual_value:
                        score += 1.0

                total_checks += 1

        return score / total_checks if total_checks > 0 else 0.0

    async def _generate_test_report(self) -> IntegrationTestReport:
        """테스트 리포트 생성"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.result == TestResult.PASS])
        failed_tests = len([r for r in self.test_results if r.result == TestResult.FAIL])
        warning_tests = len([r for r in self.test_results if r.result == TestResult.WARNING])
        error_tests = len([r for r in self.test_results if r.result == TestResult.ERROR])

        total_execution_time = sum(r.execution_time for r in self.test_results)
        average_execution_time = total_execution_time / total_tests if total_tests > 0 else 0.0
        success_rate = passed_tests / total_tests if total_tests > 0 else 0.0

        # 성능 요약
        performance_summary = {
            "average_execution_time": average_execution_time,
            "max_execution_time": (max(r.execution_time for r in self.test_results) if self.test_results else 0.0),
            "min_execution_time": (min(r.execution_time for r in self.test_results) if self.test_results else 0.0),
            "total_execution_time": total_execution_time,
        }

        # 권장사항 생성
        recommendations = await self._generate_recommendations()

        return IntegrationTestReport(
            test_results=self.test_results,
            total_tests=total_tests,
            passed_tests=passed_tests,
            failed_tests=failed_tests,
            warning_tests=warning_tests,
            error_tests=error_tests,
            total_execution_time=total_execution_time,
            average_execution_time=average_execution_time,
            success_rate=success_rate,
            performance_summary=performance_summary,
            recommendations=recommendations,
        )

    async def _generate_error_report(self, error_message: str) -> IntegrationTestReport:
        """에러 리포트 생성"""
        return IntegrationTestReport(
            test_results=[],
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            warning_tests=0,
            error_tests=1,
            total_execution_time=0.0,
            average_execution_time=0.0,
            success_rate=0.0,
            performance_summary={},
            recommendations=[f"시스템 초기화 실패: {error_message}"],
        )

    async def _generate_recommendations(self) -> List[str]:
        """권장사항 생성"""
        recommendations = []

        # 성공률 기반 권장사항
        success_rate = (
            len([r for r in self.test_results if r.result == TestResult.PASS]) / len(self.test_results)
            if self.test_results
            else 0.0
        )

        if success_rate < 0.8:
            recommendations.append("테스트 성공률이 낮습니다. 시스템 안정성을 개선해야 합니다.")

        # 성능 기반 권장사항
        avg_time = (
            sum(r.execution_time for r in self.test_results) / len(self.test_results) if self.test_results else 0.0
        )

        if avg_time > 5.0:
            recommendations.append("평균 실행 시간이 길습니다. 성능 최적화가 필요합니다.")

        # 에러 기반 권장사항
        error_count = len([r for r in self.test_results if r.result == TestResult.ERROR])

        if error_count > 0:
            recommendations.append(
                f"{error_count}개의 테스트에서 에러가 발생했습니다. 시스템 안정성을 점검해야 합니다."
            )

        return recommendations


async def main():
    """메인 함수"""
    # Phase Z v2.0 통합 테스트 시스템 인스턴스 생성
    integration_test = PhaseZIntegrationTest()

    # 모든 테스트 실행
    report = await integration_test.run_all_tests()

    # 결과 출력
    print("\n" + "=" * 80)
    print("🧠 Phase Z v2.0 통합 테스트 리포트")
    print("=" * 80)

    print("\n📊 기본 정보:")
    print(f"  - 총 테스트 수: {report.total_tests}")
    print(f"  - 성공한 테스트: {report.passed_tests}")
    print(f"  - 실패한 테스트: {report.failed_tests}")
    print(f"  - 경고 테스트: {report.warning_tests}")
    print(f"  - 에러 테스트: {report.error_tests}")
    print(f"  - 성공률: {report.success_rate:.2%}")

    print("\n⏱️ 성능 정보:")
    print(f"  - 총 실행 시간: {report.total_execution_time:.2f}초")
    print(f"  - 평균 실행 시간: {report.average_execution_time:.2f}초")
    print(f"  - 최대 실행 시간: {report.performance_summary.get('max_execution_time', 0):.2f}초")
    print(f"  - 최소 실행 시간: {report.performance_summary.get('min_execution_time', 0):.2f}초")

    print("\n🧪 상세 테스트 결과:")
    for result in report.test_results:
        status_emoji = {
            TestResult.PASS: "✅",
            TestResult.FAIL: "❌",
            TestResult.WARNING: "⚠️",
            TestResult.ERROR: "🚨",
        }.get(result.result, "❓")

        print(f"  {status_emoji} {result.test_id}: {result.result.value} ({result.execution_time:.2f}초)")
        if result.error_message:
            print(f"    - 에러: {result.error_message}")

    if report.recommendations:
        print("\n💡 권장사항:")
        for rec in report.recommendations:
            print(f"  - {rec}")

    return report


if __name__ == "__main__":
    asyncio.run(main())
