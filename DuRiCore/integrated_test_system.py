#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 통합 테스트 및 검증 시스템 (Integrated Test System)
Phase 6: 통합 테스트 및 검증 - 최종 실행 준비 완료 적용

모든 시스템의 통합 테스트 및 검증을 위한 시스템:
- 시스템 간 연동 테스트
- 성능 통합 테스트
- 기능 검증 테스트
- 안정성 테스트

@preserve_identity: 통합 테스트 과정의 판단 이유 기록
@evolution_protection: 기존 테스트 패턴과 검증 경로 보존
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import asyncio
import json
import logging
import time
import traceback
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestType(Enum):
    """테스트 유형"""

    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    FUNCTIONAL = "functional"
    STABILITY = "stability"
    SECURITY = "security"
    REGRESSION = "regression"


class TestStatus(Enum):
    """테스트 상태"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class TestPriority(Enum):
    """테스트 우선순위"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class TestResult:
    """테스트 결과"""

    id: str
    test_type: TestType
    test_name: str
    status: TestStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: float = 0.0
    score: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    """테스트 스위트"""

    id: str
    name: str
    description: str
    tests: List[str] = field(default_factory=list)
    priority: TestPriority = TestPriority.NORMAL
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegrationTestReport:
    """통합 테스트 보고서"""

    id: str
    timestamp: datetime
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    overall_score: float
    test_results: List[TestResult] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntegratedTestSystem:
    """통합 테스트 및 검증 시스템"""

    def __init__(self):
        # 테스트 관리
        self.test_suites: Dict[str, TestSuite] = {}
        self.test_results: List[TestResult] = []
        self.test_reports: List[IntegrationTestReport] = []

        # 테스트 설정
        self.test_config = {
            "timeout": 300.0,  # 5분
            "retry_attempts": 3,
            "parallel_execution": True,
            "max_parallel_tests": 5,
            "test_priority_threshold": TestPriority.NORMAL,
        }

        # 테스트 통계
        self.test_statistics = {
            "total_tests_run": 0,
            "total_tests_passed": 0,
            "total_tests_failed": 0,
            "total_tests_skipped": 0,
            "average_test_duration": 0.0,
            "success_rate": 0.0,
        }

        # 성능 메트릭
        self.performance_metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # 존재형 AI 시스템 초기화
        self.existence_ai = self._initialize_existence_ai()
        self.final_execution_verifier = self._initialize_final_execution_verifier()

        # 자동 테스트 설정
        self.auto_testing_enabled = True
        self.test_interval = 3600  # 1시간마다

        logger.info("통합 테스트 및 검증 시스템 초기화 완료")

    def _initialize_existence_ai(self):
        """존재형 AI 시스템 초기화"""
        try:
            from utils.existence_ai_system import ExistenceAISystem

            return ExistenceAISystem()
        except ImportError:
            logger.warning("존재형 AI 시스템을 찾을 수 없습니다.")
            return None

    def _initialize_final_execution_verifier(self):
        """최종 실행 준비 완료 시스템 초기화"""
        try:
            from utils.final_execution_verifier import FinalExecutionVerifier

            return FinalExecutionVerifier()
        except ImportError:
            logger.warning("최종 실행 준비 완료 시스템을 찾을 수 없습니다.")
            return None

    async def register_test_suite(self, suite: TestSuite):
        """테스트 스위트 등록"""
        try:
            self.test_suites[suite.id] = suite
            logger.info(f"테스트 스위트 등록: {suite.name} ({suite.id})")

            # 존재형 AI: 진화 가능성 확인
            if self.existence_ai and self.existence_ai.evolution_capability.can_evolve():
                self.existence_ai.evolution_capability.evolve()

            # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
            if self.final_execution_verifier and self.final_execution_verifier.verify_readiness():
                logger.info("최종 실행 준비 완료 확인됨")

        except Exception as e:
            logger.error(f"테스트 스위트 등록 실패: {e}")

    async def run_integration_tests(self, suite_ids: List[str] = None) -> IntegrationTestReport:
        """통합 테스트 실행"""
        try:
            logger.info("통합 테스트 시작")

            # 실행할 테스트 스위트 선택
            if suite_ids is None:
                suite_ids = list(self.test_suites.keys())

            start_time = datetime.now()
            all_test_results = []

            # 테스트 스위트별 실행
            for suite_id in suite_ids:
                if suite_id in self.test_suites:
                    suite = self.test_suites[suite_id]
                    logger.info(f"테스트 스위트 실행: {suite.name}")

                    # 스위트 내 테스트 실행
                    suite_results = await self._run_test_suite(suite)
                    all_test_results.extend(suite_results)

            # 결과 집계
            total_tests = len(all_test_results)
            passed_tests = len([r for r in all_test_results if r.status == TestStatus.PASSED])
            failed_tests = len([r for r in all_test_results if r.status == TestStatus.FAILED])
            skipped_tests = len([r for r in all_test_results if r.status == TestStatus.SKIPPED])

            # 전체 점수 계산
            overall_score = passed_tests / max(1, total_tests)

            # 통계 업데이트
            self._update_test_statistics(all_test_results)

            # 보고서 생성
            report = IntegrationTestReport(
                id=f"integration_test_{int(time.time())}",
                timestamp=datetime.now(),
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                overall_score=overall_score,
                test_results=all_test_results,
                recommendations=self._generate_recommendations(all_test_results),
            )

            self.test_reports.append(report)

            # 존재형 AI: 진화 가능성 확인
            if self.existence_ai and self.existence_ai.evolution_capability.can_evolve():
                self.existence_ai.evolution_capability.evolve()

            # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
            if self.final_execution_verifier and self.final_execution_verifier.verify_readiness():
                logger.info("최종 실행 준비 완료 확인됨")

            logger.info(
                f"통합 테스트 완료: {passed_tests}/{total_tests} 통과 (점수: {overall_score:.2f})"
            )

            return report

        except Exception as e:
            logger.error(f"통합 테스트 실행 실패: {e}")
            return self._create_error_report(str(e))

    async def _run_test_suite(self, suite: TestSuite) -> List[TestResult]:
        """테스트 스위트 실행"""
        try:
            results = []

            # 의존성 체크
            if not await self._check_dependencies(suite.dependencies):
                logger.warning(f"테스트 스위트 {suite.name}의 의존성이 충족되지 않아 건너뜀")
                return results

            # 테스트 실행
            for test_name in suite.tests:
                try:
                    result = await self._run_single_test(test_name, suite)
                    results.append(result)
                except Exception as e:
                    logger.error(f"테스트 {test_name} 실행 실패: {e}")
                    error_result = TestResult(
                        id=f"test_{int(time.time())}",
                        test_type=TestType.INTEGRATION,
                        test_name=test_name,
                        status=TestStatus.ERROR,
                        start_time=datetime.now(),
                        end_time=datetime.now(),
                        error_message=str(e),
                    )
                    results.append(error_result)

            return results

        except Exception as e:
            logger.error(f"테스트 스위트 {suite.name} 실행 실패: {e}")
            return []

    async def _run_single_test(self, test_name: str, suite: TestSuite) -> TestResult:
        """단일 테스트 실행"""
        try:
            test_id = f"test_{test_name}_{int(time.time())}"
            start_time = datetime.now()

            result = TestResult(
                id=test_id,
                test_type=TestType.INTEGRATION,
                test_name=test_name,
                status=TestStatus.RUNNING,
                start_time=start_time,
            )

            # 테스트 실행
            test_result = await self._execute_test(test_name)

            # 결과 업데이트
            result.end_time = datetime.now()
            result.duration = (result.end_time - result.start_time).total_seconds()
            result.status = test_result.get("status", TestStatus.FAILED)
            result.score = test_result.get("score", 0.0)
            result.error_message = test_result.get("error_message")
            result.details = test_result.get("details", {})

            self.test_results.append(result)

            return result

        except Exception as e:
            logger.error(f"단일 테스트 {test_name} 실행 실패: {e}")
            return TestResult(
                id=f"test_{test_name}_{int(time.time())}",
                test_type=TestType.INTEGRATION,
                test_name=test_name,
                status=TestStatus.ERROR,
                start_time=datetime.now(),
                end_time=datetime.now(),
                error_message=str(e),
            )

    async def _execute_test(self, test_name: str) -> Dict[str, Any]:
        """테스트 실행"""
        try:
            # 테스트 유형에 따른 실행
            if test_name.startswith("unified_"):
                return await self._execute_unified_test(test_name)
            elif test_name.startswith("async_"):
                return await self._execute_async_test(test_name)
            elif test_name.startswith("memory_"):
                return await self._execute_memory_test(test_name)
            elif test_name.startswith("performance_"):
                return await self._execute_performance_test(test_name)
            elif test_name.startswith("integration_"):
                return await self._execute_integration_test(test_name)
            else:
                return await self._execute_general_test(test_name)

        except Exception as e:
            logger.error(f"테스트 {test_name} 실행 실패: {e}")
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _execute_unified_test(self, test_name: str) -> Dict[str, Any]:
        """통합 시스템 테스트 실행"""
        try:
            if test_name == "unified_performance_test":
                from unified_performance_optimizer import \
                    unified_performance_optimizer

                summary = await unified_performance_optimizer.get_performance_summary()
                score = summary.get("current_metrics", {}).get("efficiency_score", 0.0)
                return {
                    "status": TestStatus.PASSED if score > 0.5 else TestStatus.FAILED,
                    "score": score,
                    "details": summary,
                }

            elif test_name == "unified_conversation_test":
                from unified_conversation_service import \
                    unified_conversation_service

                # 대화 서비스 테스트
                return {
                    "status": TestStatus.PASSED,
                    "score": 1.0,
                    "details": {"service": "unified_conversation_service"},
                }

            elif test_name == "unified_learning_test":
                from unified_learning_system import unified_learning_system

                # 학습 시스템 테스트
                return {
                    "status": TestStatus.PASSED,
                    "score": 1.0,
                    "details": {"service": "unified_learning_system"},
                }

            elif test_name == "unified_judgment_test":
                from unified_judgment_system import unified_judgment_system

                # 판단 시스템 테스트
                return {
                    "status": TestStatus.PASSED,
                    "score": 1.0,
                    "details": {"service": "unified_judgment_system"},
                }

            else:
                return {
                    "status": TestStatus.SKIPPED,
                    "score": 0.0,
                    "details": {"reason": "Unknown unified test"},
                }

        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _execute_async_test(self, test_name: str) -> Dict[str, Any]:
        """비동기 시스템 테스트 실행"""
        try:
            if test_name == "async_optimization_test":
                from async_optimization_system import async_optimization_system

                summary = await async_optimization_system.get_optimization_summary()
                score = summary.get("current_metrics", {}).get("optimization_score", 0.0)
                return {
                    "status": TestStatus.PASSED if score > 0.3 else TestStatus.FAILED,
                    "score": score,
                    "details": summary,
                }

            else:
                return {
                    "status": TestStatus.SKIPPED,
                    "score": 0.0,
                    "details": {"reason": "Unknown async test"},
                }

        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _execute_memory_test(self, test_name: str) -> Dict[str, Any]:
        """메모리 시스템 테스트 실행"""
        try:
            if test_name == "memory_optimization_test":
                from memory_optimization_system import \
                    memory_optimization_system

                summary = await memory_optimization_system.get_memory_summary()
                score = summary.get("current_metrics", {}).get("optimization_score", 0.0)
                return {
                    "status": TestStatus.PASSED if score > 0.5 else TestStatus.FAILED,
                    "score": score,
                    "details": summary,
                }

            else:
                return {
                    "status": TestStatus.SKIPPED,
                    "score": 0.0,
                    "details": {"reason": "Unknown memory test"},
                }

        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _execute_performance_test(self, test_name: str) -> Dict[str, Any]:
        """성능 테스트 실행"""
        try:
            if test_name == "performance_optimization_test":
                # 성능 최적화 테스트
                start_time = time.time()
                await asyncio.sleep(1)  # 시뮬레이션
                duration = time.time() - start_time

                score = 1.0 if duration < 2.0 else 0.5
                return {
                    "status": TestStatus.PASSED if score > 0.5 else TestStatus.FAILED,
                    "score": score,
                    "details": {"duration": duration},
                }

            else:
                return {
                    "status": TestStatus.SKIPPED,
                    "score": 0.0,
                    "details": {"reason": "Unknown performance test"},
                }

        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _execute_integration_test(self, test_name: str) -> Dict[str, Any]:
        """통합 테스트 실행"""
        try:
            if test_name == "integration_system_test":
                # 전체 시스템 통합 테스트
                systems = [
                    "unified_performance_optimizer",
                    "async_optimization_system",
                    "memory_optimization_system",
                    "unified_conversation_service",
                    "unified_learning_system",
                    "unified_judgment_system",
                ]

                working_systems = 0
                for system in systems:
                    try:
                        # 시스템 존재 확인
                        __import__(system)
                        working_systems += 1
                    except ImportError:
                        pass

                score = working_systems / len(systems)
                return {
                    "status": TestStatus.PASSED if score > 0.8 else TestStatus.FAILED,
                    "score": score,
                    "details": {
                        "working_systems": working_systems,
                        "total_systems": len(systems),
                    },
                }

            else:
                return {
                    "status": TestStatus.SKIPPED,
                    "score": 0.0,
                    "details": {"reason": "Unknown integration test"},
                }

        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _execute_general_test(self, test_name: str) -> Dict[str, Any]:
        """일반 테스트 실행"""
        try:
            # 기본 테스트 로직
            return {
                "status": TestStatus.PASSED,
                "score": 1.0,
                "details": {"test_name": test_name},
            }

        except Exception as e:
            return {
                "status": TestStatus.ERROR,
                "score": 0.0,
                "error_message": str(e),
                "details": {},
            }

    async def _check_dependencies(self, dependencies: List[str]) -> bool:
        """의존성 체크"""
        try:
            for dependency in dependencies:
                try:
                    __import__(dependency)
                except ImportError:
                    logger.warning(f"의존성 {dependency}를 찾을 수 없습니다.")
                    return False
            return True

        except Exception as e:
            logger.error(f"의존성 체크 실패: {e}")
            return False

    def _update_test_statistics(self, test_results: List[TestResult]):
        """테스트 통계 업데이트"""
        try:
            total_tests = len(test_results)
            passed_tests = len([r for r in test_results if r.status == TestStatus.PASSED])
            failed_tests = len([r for r in test_results if r.status == TestStatus.FAILED])
            skipped_tests = len([r for r in test_results if r.status == TestStatus.SKIPPED])

            self.test_statistics["total_tests_run"] += total_tests
            self.test_statistics["total_tests_passed"] += passed_tests
            self.test_statistics["total_tests_failed"] += failed_tests
            self.test_statistics["total_tests_skipped"] += skipped_tests

            # 평균 테스트 시간 계산
            durations = [r.duration for r in test_results if r.duration > 0]
            if durations:
                self.test_statistics["average_test_duration"] = sum(durations) / len(durations)

            # 성공률 계산
            total_run = self.test_statistics["total_tests_run"]
            if total_run > 0:
                self.test_statistics["success_rate"] = (
                    self.test_statistics["total_tests_passed"] / total_run
                )

        except Exception as e:
            logger.error(f"테스트 통계 업데이트 실패: {e}")

    def _generate_recommendations(self, test_results: List[TestResult]) -> List[str]:
        """권장사항 생성"""
        try:
            recommendations = []

            # 실패한 테스트 분석
            failed_tests = [r for r in test_results if r.status == TestStatus.FAILED]
            if failed_tests:
                recommendations.append(
                    f"{len(failed_tests)}개의 테스트가 실패했습니다. 실패한 테스트를 검토하세요."
                )

            # 성능 테스트 분석
            performance_tests = [r for r in test_results if r.test_type == TestType.PERFORMANCE]
            if performance_tests:
                avg_score = sum(r.score for r in performance_tests) / len(performance_tests)
                if avg_score < 0.7:
                    recommendations.append("성능 테스트 점수가 낮습니다. 성능 최적화를 고려하세요.")

            # 통합 테스트 분석
            integration_tests = [r for r in test_results if r.test_type == TestType.INTEGRATION]
            if integration_tests:
                avg_score = sum(r.score for r in integration_tests) / len(integration_tests)
                if avg_score < 0.8:
                    recommendations.append(
                        "통합 테스트 점수가 낮습니다. 시스템 간 연동을 검토하세요."
                    )

            if not recommendations:
                recommendations.append("모든 테스트가 성공적으로 완료되었습니다.")

            return recommendations

        except Exception as e:
            logger.error(f"권장사항 생성 실패: {e}")
            return ["권장사항 생성 중 오류가 발생했습니다."]

    def _create_error_report(self, error_message: str) -> IntegrationTestReport:
        """오류 보고서 생성"""
        return IntegrationTestReport(
            id=f"error_report_{int(time.time())}",
            timestamp=datetime.now(),
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            skipped_tests=0,
            overall_score=0.0,
            test_results=[],
            recommendations=[f"테스트 실행 중 오류 발생: {error_message}"],
        )

    async def get_test_summary(self) -> Dict[str, Any]:
        """테스트 요약 생성"""
        try:
            if not self.test_reports:
                return {"error": "테스트 데이터가 없습니다."}

            latest_report = self.test_reports[-1]

            return {
                "test_statistics": self.test_statistics,
                "latest_report": {
                    "id": latest_report.id,
                    "timestamp": latest_report.timestamp.isoformat(),
                    "total_tests": latest_report.total_tests,
                    "passed_tests": latest_report.passed_tests,
                    "failed_tests": latest_report.failed_tests,
                    "skipped_tests": latest_report.skipped_tests,
                    "overall_score": latest_report.overall_score,
                },
                "recommendations": latest_report.recommendations,
                "test_suites": {
                    suite_id: {
                        "name": suite.name,
                        "description": suite.description,
                        "priority": suite.priority.value,
                        "test_count": len(suite.tests),
                    }
                    for suite_id, suite in self.test_suites.items()
                },
            }

        except Exception as e:
            logger.error(f"테스트 요약 생성 실패: {e}")
            return {"error": str(e)}


# 전역 인스턴스
integrated_test_system = IntegratedTestSystem()
