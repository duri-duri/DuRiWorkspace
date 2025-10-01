#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: Evolution Integration Test System

이 모듈은 Phase Ω 진화 통합 시스템의 테스트를 담당합니다.
Self-Rewriting, Genetic Programming, MetaCoder가 제대로 통합되어 작동하는지 검증합니다.

주요 기능:
- Self-Rewriting Module 테스트
- Genetic Programming Engine 테스트
- MetaCoder Engine 테스트
- 통합 시스템 테스트
- 진화 결과 검증
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

from genetic_evolution_engine import EvolutionConfig, GeneticEvolutionEngine
from meta_coder import CodeAnalysis, MetaCoder
from phase_omega_evolution_integration import DuRiEvolutionIntegration, EvolutionSession

# 테스트 대상 모듈들 import
from self_rewriting_module import CodeAssessment, SelfRewritingModule

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""

    test_name: str
    success: bool
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None


@dataclass
class TestSuiteResult:
    """테스트 스위트 결과 데이터 클래스"""

    suite_name: str
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_time: float
    results: List[TestResult]
    overall_success: bool


class PhaseOmegaEvolutionTest:
    """Phase Ω 진화 통합 테스트 시스템"""

    def __init__(self):
        """초기화"""
        self.test_results: List[TestResult] = []
        self.test_suites: List[TestSuiteResult] = []

        # 테스트 대상 모듈들
        self.self_rewriter = SelfRewritingModule()
        self.genetic_engine = GeneticEvolutionEngine()
        self.meta_coder = MetaCoder()
        self.evolution_integration = DuRiEvolutionIntegration()

        logger.info("Phase Ω Evolution Test 초기화 완료")

    async def run_all_tests(self) -> TestSuiteResult:
        """모든 테스트 실행"""
        try:
            logger.info("🧪 전체 테스트 실행 시작")
            start_time = time.time()

            # 테스트 스위트 실행
            test_suites = [
                await self._test_self_rewriting_module(),
                await self._test_genetic_evolution_engine(),
                await self._test_meta_coder_engine(),
                await self._test_evolution_integration(),
                await self._test_integration_workflow(),
            ]

            # 전체 결과 집계
            total_tests = sum(suite.total_tests for suite in test_suites)
            passed_tests = sum(suite.passed_tests for suite in test_suites)
            failed_tests = sum(suite.failed_tests for suite in test_suites)
            total_time = time.time() - start_time

            overall_success = all(suite.overall_success for suite in test_suites)

            # 전체 결과 생성
            overall_result = TestSuiteResult(
                suite_name="Phase Ω Evolution Integration Test",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                results=[result for suite in test_suites for result in suite.results],
                overall_success=overall_success,
            )

            self.test_suites.append(overall_result)

            logger.info(
                f"✅ 전체 테스트 완료: {passed_tests}/{total_tests} 통과, 시간={total_time:.2f}초"
            )

            return overall_result

        except Exception as e:
            logger.error(f"전체 테스트 실행 실패: {e}")
            return TestSuiteResult(
                suite_name="Phase Ω Evolution Integration Test",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                total_time=0.0,
                results=[],
                overall_success=False,
            )

    async def _test_self_rewriting_module(self) -> TestSuiteResult:
        """Self-Rewriting Module 테스트"""
        try:
            logger.info("🔧 Self-Rewriting Module 테스트 시작")
            start_time = time.time()
            results = []

            # 1. 코드 평가 테스트
            assessment_result = await self._test_code_assessment()
            results.append(assessment_result)

            # 2. 개선 제안 테스트
            proposal_result = await self._test_improvement_proposal()
            results.append(proposal_result)

            # 3. 안전한 재작성 테스트
            rewriting_result = await self._test_safe_rewriting()
            results.append(rewriting_result)

            # 결과 집계
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.success)
            failed_tests = total_tests - passed_tests
            total_time = time.time() - start_time

            suite_result = TestSuiteResult(
                suite_name="Self-Rewriting Module Test",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                results=results,
                overall_success=failed_tests == 0,
            )

            logger.info(
                f"✅ Self-Rewriting Module 테스트 완료: {passed_tests}/{total_tests} 통과"
            )

            return suite_result

        except Exception as e:
            logger.error(f"Self-Rewriting Module 테스트 실패: {e}")
            return TestSuiteResult(
                suite_name="Self-Rewriting Module Test",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                total_time=0.0,
                results=[],
                overall_success=False,
            )

    async def _test_genetic_evolution_engine(self) -> TestSuiteResult:
        """Genetic Evolution Engine 테스트"""
        try:
            logger.info("🧬 Genetic Evolution Engine 테스트 시작")
            start_time = time.time()
            results = []

            # 1. 인구 생성 테스트
            population_result = await self._test_population_generation()
            results.append(population_result)

            # 2. 적합도 평가 테스트
            fitness_result = await self._test_fitness_evaluation()
            results.append(fitness_result)

            # 3. 진화 실행 테스트
            evolution_result = await self._test_evolution_execution()
            results.append(evolution_result)

            # 결과 집계
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.success)
            failed_tests = total_tests - passed_tests
            total_time = time.time() - start_time

            suite_result = TestSuiteResult(
                suite_name="Genetic Evolution Engine Test",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                results=results,
                overall_success=failed_tests == 0,
            )

            logger.info(
                f"✅ Genetic Evolution Engine 테스트 완료: {passed_tests}/{total_tests} 통과"
            )

            return suite_result

        except Exception as e:
            logger.error(f"Genetic Evolution Engine 테스트 실패: {e}")
            return TestSuiteResult(
                suite_name="Genetic Evolution Engine Test",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                total_time=0.0,
                results=[],
                overall_success=False,
            )

    async def _test_meta_coder_engine(self) -> TestSuiteResult:
        """MetaCoder Engine 테스트"""
        try:
            logger.info("🤖 MetaCoder Engine 테스트 시작")
            start_time = time.time()
            results = []

            # 1. 모듈 파싱 테스트
            parsing_result = await self._test_module_parsing()
            results.append(parsing_result)

            # 2. 리팩토링 제안 테스트
            refactoring_result = await self._test_refactoring_proposal()
            results.append(refactoring_result)

            # 3. 검증 및 적용 테스트
            validation_result = await self._test_validation_and_apply()
            results.append(validation_result)

            # 결과 집계
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.success)
            failed_tests = total_tests - passed_tests
            total_time = time.time() - start_time

            suite_result = TestSuiteResult(
                suite_name="MetaCoder Engine Test",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                results=results,
                overall_success=failed_tests == 0,
            )

            logger.info(
                f"✅ MetaCoder Engine 테스트 완료: {passed_tests}/{total_tests} 통과"
            )

            return suite_result

        except Exception as e:
            logger.error(f"MetaCoder Engine 테스트 실패: {e}")
            return TestSuiteResult(
                suite_name="MetaCoder Engine Test",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                total_time=0.0,
                results=[],
                overall_success=False,
            )

    async def _test_evolution_integration(self) -> TestSuiteResult:
        """Evolution Integration 테스트"""
        try:
            logger.info("🔗 Evolution Integration 테스트 시작")
            start_time = time.time()
            results = []

            # 1. 진화 세션 생성 테스트
            session_result = await self._test_evolution_session_creation()
            results.append(session_result)

            # 2. 진화 사이클 실행 테스트
            cycle_result = await self._test_evolution_cycle_execution()
            results.append(cycle_result)

            # 3. 진화 결과 검증 테스트
            validation_result = await self._test_evolution_result_validation()
            results.append(validation_result)

            # 결과 집계
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.success)
            failed_tests = total_tests - passed_tests
            total_time = time.time() - start_time

            suite_result = TestSuiteResult(
                suite_name="Evolution Integration Test",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                results=results,
                overall_success=failed_tests == 0,
            )

            logger.info(
                f"✅ Evolution Integration 테스트 완료: {passed_tests}/{total_tests} 통과"
            )

            return suite_result

        except Exception as e:
            logger.error(f"Evolution Integration 테스트 실패: {e}")
            return TestSuiteResult(
                suite_name="Evolution Integration Test",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                total_time=0.0,
                results=[],
                overall_success=False,
            )

    async def _test_integration_workflow(self) -> TestSuiteResult:
        """통합 워크플로우 테스트"""
        try:
            logger.info("🔄 통합 워크플로우 테스트 시작")
            start_time = time.time()
            results = []

            # 1. 전체 진화 워크플로우 테스트
            workflow_result = await self._test_complete_evolution_workflow()
            results.append(workflow_result)

            # 2. 성능 테스트
            performance_result = await self._test_performance()
            results.append(performance_result)

            # 3. 안정성 테스트
            stability_result = await self._test_stability()
            results.append(stability_result)

            # 결과 집계
            total_tests = len(results)
            passed_tests = sum(1 for r in results if r.success)
            failed_tests = total_tests - passed_tests
            total_time = time.time() - start_time

            suite_result = TestSuiteResult(
                suite_name="Integration Workflow Test",
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                total_time=total_time,
                results=results,
                overall_success=failed_tests == 0,
            )

            logger.info(
                f"✅ 통합 워크플로우 테스트 완료: {passed_tests}/{total_tests} 통과"
            )

            return suite_result

        except Exception as e:
            logger.error(f"통합 워크플로우 테스트 실패: {e}")
            return TestSuiteResult(
                suite_name="Integration Workflow Test",
                total_tests=0,
                passed_tests=0,
                failed_tests=1,
                total_time=0.0,
                results=[],
                overall_success=False,
            )

    # Self-Rewriting Module 테스트 메서드들
    async def _test_code_assessment(self) -> TestResult:
        """코드 평가 테스트"""
        try:
            start_time = time.time()

            # 테스트용 모듈 경로들 (여러 옵션 시도)
            test_modules = [
                "duri_thought_flow.py",
                "DuRiCore/duri_thought_flow.py",
                "../duri_thought_flow.py",
                "phase_omega_integration.py",
                "DuRiCore/phase_omega_integration.py",
            ]

            test_module = None
            for module_path in test_modules:
                if os.path.exists(module_path):
                    test_module = module_path
                    break

            if not test_module:
                # 파일이 없으면 테스트용 코드로 대체
                test_code = """
def example_function():
    return "test"
"""
                # 임시 파일 생성
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(test_code)
                    test_module = f.name

                try:
                    # 코드 평가 실행
                    assessment = await self.self_rewriter.assess_self_code(test_module)

                    # 결과 검증
                    success = (
                        assessment is not None
                        and hasattr(assessment, "complexity_score")
                        and hasattr(assessment, "performance_score")
                        and hasattr(assessment, "maintainability_score")
                        and 0 <= assessment.complexity_score <= 1
                        and 0 <= assessment.performance_score <= 1
                        and 0 <= assessment.maintainability_score <= 1
                    )

                    details = {
                        "module_path": test_module,
                        "complexity_score": (
                            assessment.complexity_score if assessment else 0
                        ),
                        "performance_score": (
                            assessment.performance_score if assessment else 0
                        ),
                        "maintainability_score": (
                            assessment.maintainability_score if assessment else 0
                        ),
                    }

                    return TestResult(
                        test_name="Code Assessment Test",
                        success=success,
                        execution_time=time.time() - start_time,
                        details=details,
                    )

                finally:
                    # 임시 파일 정리
                    if os.path.exists(test_module):
                        os.unlink(test_module)
            else:
                # 실제 파일이 있는 경우
                assessment = await self.self_rewriter.assess_self_code(test_module)

                # 결과 검증
                success = (
                    assessment is not None
                    and hasattr(assessment, "complexity_score")
                    and hasattr(assessment, "performance_score")
                    and hasattr(assessment, "maintainability_score")
                    and 0 <= assessment.complexity_score <= 1
                    and 0 <= assessment.performance_score <= 1
                    and 0 <= assessment.maintainability_score <= 1
                )

                details = {
                    "module_path": test_module,
                    "complexity_score": (
                        assessment.complexity_score if assessment else 0
                    ),
                    "performance_score": (
                        assessment.performance_score if assessment else 0
                    ),
                    "maintainability_score": (
                        assessment.maintainability_score if assessment else 0
                    ),
                }

                return TestResult(
                    test_name="Code Assessment Test",
                    success=success,
                    execution_time=time.time() - start_time,
                    details=details,
                )

        except Exception as e:
            return TestResult(
                test_name="Code Assessment Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_improvement_proposal(self) -> TestResult:
        """개선 제안 테스트"""
        try:
            start_time = time.time()

            # 테스트용 코드
            test_code = """
def example_function():
    result = 0
    for i in range(10):
        result += i
    return result
"""

            # 테스트용 평가 생성
            assessment = CodeAssessment(
                module_path="test_module.py",
                complexity_score=0.7,
                performance_score=0.6,
                maintainability_score=0.5,
                bug_potential=0.3,
            )

            # 개선 제안 생성
            proposal = await self.self_rewriter.generate_alternative(
                test_code, assessment
            )

            # 결과 검증
            success = (
                proposal is not None
                and hasattr(proposal, "proposal_id")
                and hasattr(proposal, "rewrite_type")
                and hasattr(proposal, "expected_impact")
                and proposal.expected_impact >= 0
            )

            details = {
                "proposal_id": proposal.proposal_id if proposal else None,
                "rewrite_type": proposal.rewrite_type.value if proposal else None,
                "expected_impact": proposal.expected_impact if proposal else 0,
            }

            return TestResult(
                test_name="Improvement Proposal Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Improvement Proposal Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_safe_rewriting(self) -> TestResult:
        """안전한 재작성 테스트"""
        try:
            start_time = time.time()

            # 테스트용 코드
            test_code = """
def safe_function():
    return "test"
"""

            # 임시 파일 생성
            import tempfile

            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(test_code)
                temp_path = f.name

            try:
                # 안전한 재작성 실행
                result = await self.self_rewriter.safely_rewrite(temp_path, test_code)

                # 결과 검증
                success = result is not None and hasattr(result, "success")

                details = {
                    "success": result.success if result else False,
                    "status": result.status.value if result else None,
                }

                return TestResult(
                    test_name="Safe Rewriting Test",
                    success=success,
                    execution_time=time.time() - start_time,
                    details=details,
                )

            finally:
                # 임시 파일 정리
                if os.path.exists(temp_path):
                    os.unlink(temp_path)

        except Exception as e:
            return TestResult(
                test_name="Safe Rewriting Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    # Genetic Evolution Engine 테스트 메서드들
    async def _test_population_generation(self) -> TestResult:
        """인구 생성 테스트"""
        try:
            start_time = time.time()

            # 시드 코드
            seed_code = """
def example_function():
    return 42
"""

            # 인구 생성
            population = await self.genetic_engine.generate_population(seed_code, 10)

            # 결과 검증
            success = (
                population is not None
                and len(population) == 10
                and all(
                    hasattr(individual, "individual_id") for individual in population
                )
            )

            details = {
                "population_size": len(population) if population else 0,
                "individual_ids": (
                    [ind.individual_id for ind in population] if population else []
                ),
            }

            return TestResult(
                test_name="Population Generation Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Population Generation Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_fitness_evaluation(self) -> TestResult:
        """적합도 평가 테스트"""
        try:
            start_time = time.time()

            # 테스트용 개체 생성
            from genetic_evolution_engine import GeneticIndividual

            individual = GeneticIndividual(
                individual_id="test_individual",
                code_structure="""
def test_function():
    return "test"
""",
            )

            # 적합도 평가
            fitness_score = await self.genetic_engine.evaluate_fitness(individual)

            # 결과 검증
            success = (
                fitness_score is not None
                and 0 <= fitness_score <= 1
                and hasattr(individual, "fitness_score")
            )

            details = {
                "fitness_score": fitness_score,
                "individual_id": individual.individual_id,
            }

            return TestResult(
                test_name="Fitness Evaluation Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Fitness Evaluation Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_evolution_execution(self) -> TestResult:
        """진화 실행 테스트"""
        try:
            start_time = time.time()

            # 시드 코드
            seed_code = """
def example_function():
    return 42
"""

            # 진화 실행
            result = await self.genetic_engine.evolve_capabilities(
                seed_code, "테스트 목표"
            )

            # 결과 검증
            success = (
                result is not None
                and hasattr(result, "success")
                and hasattr(result, "final_fitness")
                and hasattr(result, "total_generations")
            )

            details = {
                "success": result.success if result else False,
                "final_fitness": result.final_fitness if result else 0,
                "total_generations": result.total_generations if result else 0,
            }

            return TestResult(
                test_name="Evolution Execution Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Evolution Execution Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    # MetaCoder Engine 테스트 메서드들
    async def _test_module_parsing(self) -> TestResult:
        """모듈 파싱 테스트"""
        try:
            start_time = time.time()

            # 테스트용 모듈 경로들 (여러 옵션 시도)
            test_modules = [
                "duri_thought_flow.py",
                "DuRiCore/duri_thought_flow.py",
                "../duri_thought_flow.py",
                "phase_omega_integration.py",
                "DuRiCore/phase_omega_integration.py",
            ]

            test_module = None
            for module_path in test_modules:
                if os.path.exists(module_path):
                    test_module = module_path
                    break

            if not test_module:
                # 파일이 없으면 테스트용 코드로 대체
                test_code = """
def example_function():
    return "test"

class ExampleClass:
    def __init__(self):
        self.value = 42
"""
                # 임시 파일 생성
                import tempfile

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".py", delete=False
                ) as f:
                    f.write(test_code)
                    test_module = f.name

                try:
                    # 모듈 파싱
                    analysis = await self.meta_coder.parse_module(test_module)

                    # 결과 검증
                    success = (
                        analysis is not None
                        and hasattr(analysis, "module_path")
                        and hasattr(analysis, "functions")
                        and hasattr(analysis, "classes")
                    )

                    details = {
                        "module_path": test_module,
                        "functions_count": len(analysis.functions) if analysis else 0,
                        "classes_count": len(analysis.classes) if analysis else 0,
                    }

                    return TestResult(
                        test_name="Module Parsing Test",
                        success=success,
                        execution_time=time.time() - start_time,
                        details=details,
                    )

                finally:
                    # 임시 파일 정리
                    if os.path.exists(test_module):
                        os.unlink(test_module)
            else:
                # 실제 파일이 있는 경우
                analysis = await self.meta_coder.parse_module(test_module)

                # 결과 검증
                success = (
                    analysis is not None
                    and hasattr(analysis, "module_path")
                    and hasattr(analysis, "functions")
                    and hasattr(analysis, "classes")
                )

                details = {
                    "module_path": analysis.module_path if analysis else None,
                    "functions_count": len(analysis.functions) if analysis else 0,
                    "classes_count": len(analysis.classes) if analysis else 0,
                }

                return TestResult(
                    test_name="Module Parsing Test",
                    success=success,
                    execution_time=time.time() - start_time,
                    details=details,
                )

        except Exception as e:
            return TestResult(
                test_name="Module Parsing Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_refactoring_proposal(self) -> TestResult:
        """리팩토링 제안 테스트"""
        try:
            start_time = time.time()

            # 테스트용 AST 생성
            import ast

            test_code = """
def example_function():
    return 42
"""
            tree = ast.parse(test_code)

            # 리팩토링 제안
            proposal = await self.meta_coder.refactor_code(tree, "성능 최적화")

            # 결과 검증
            success = (
                proposal is not None
                and hasattr(proposal, "proposal_id")
                and hasattr(proposal, "refactor_type")
                and hasattr(proposal, "expected_impact")
            )

            details = {
                "proposal_id": proposal.proposal_id if proposal else None,
                "refactor_type": proposal.refactor_type.value if proposal else None,
                "expected_impact": proposal.expected_impact if proposal else 0,
            }

            return TestResult(
                test_name="Refactoring Proposal Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Refactoring Proposal Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_validation_and_apply(self) -> TestResult:
        """검증 및 적용 테스트"""
        try:
            start_time = time.time()

            # 테스트용 코드
            test_code = """
def test_function():
    return "test"
"""

            # 검증 및 적용
            test_suite = ["test_basic"]
            result = await self.meta_coder.validate_and_apply(test_code, test_suite)

            # 결과 검증
            success = (
                result is not None
                and hasattr(result, "success")
                and hasattr(result, "quality_improvement")
            )

            details = {
                "success": result.success if result else False,
                "quality_improvement": result.quality_improvement if result else 0,
            }

            return TestResult(
                test_name="Validation and Apply Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Validation and Apply Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    # Evolution Integration 테스트 메서드들
    async def _test_evolution_session_creation(self) -> TestResult:
        """진화 세션 생성 테스트"""
        try:
            start_time = time.time()

            # 진화 세션 생성
            session = await self.evolution_integration.start_evolution_session(
                "테스트 목표"
            )

            # 결과 검증
            success = (
                session is not None
                and hasattr(session, "session_id")
                and hasattr(session, "target_goal")
                and session.target_goal == "테스트 목표"
            )

            details = {
                "session_id": session.session_id if session else None,
                "target_goal": session.target_goal if session else None,
            }

            return TestResult(
                test_name="Evolution Session Creation Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Evolution Session Creation Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_evolution_cycle_execution(self) -> TestResult:
        """진화 사이클 실행 테스트"""
        try:
            start_time = time.time()

            # 진화 세션 생성
            session = await self.evolution_integration.start_evolution_session(
                "테스트 목표"
            )

            # 진화 사이클 실행
            result = await self.evolution_integration.execute_evolution_cycle(session)

            # 결과 검증
            success = (
                result is not None
                and hasattr(result, "success")
                and hasattr(result, "evolution_time")
            )

            details = {
                "success": result.success if result else False,
                "evolution_time": result.evolution_time if result else 0,
            }

            return TestResult(
                test_name="Evolution Cycle Execution Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Evolution Cycle Execution Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_evolution_result_validation(self) -> TestResult:
        """진화 결과 검증 테스트"""
        try:
            start_time = time.time()

            # 진화 세션 생성 및 실행
            session = await self.evolution_integration.start_evolution_session(
                "테스트 목표"
            )
            result = await self.evolution_integration.execute_evolution_cycle(session)

            # 결과 검증
            success = (
                result is not None
                and hasattr(result, "improvements_made")
                and hasattr(result, "quality_improvement")
                and hasattr(result, "performance_improvement")
            )

            details = {
                "improvements_count": len(result.improvements_made) if result else 0,
                "quality_improvement": result.quality_improvement if result else 0,
                "performance_improvement": (
                    result.performance_improvement if result else 0
                ),
            }

            return TestResult(
                test_name="Evolution Result Validation Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Evolution Result Validation Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    # 통합 워크플로우 테스트 메서드들
    async def _test_complete_evolution_workflow(self) -> TestResult:
        """전체 진화 워크플로우 테스트"""
        try:
            start_time = time.time()

            # 전체 진화 워크플로우 실행
            session = await self.evolution_integration.start_evolution_session(
                "통합 테스트 목표"
            )
            result = await self.evolution_integration.execute_evolution_cycle(session)

            # 결과 검증
            success = (
                result is not None
                and result.success
                and len(session.steps) > 0
                and all(
                    step.status.value in ["completed", "failed"]
                    for step in session.steps
                )
            )

            details = {
                "session_id": session.session_id,
                "steps_count": len(session.steps),
                "overall_success": result.success if result else False,
            }

            return TestResult(
                test_name="Complete Evolution Workflow Test",
                success=success,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Complete Evolution Workflow Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_performance(self) -> TestResult:
        """성능 테스트"""
        try:
            start_time = time.time()

            # 성능 테스트 실행
            session = await self.evolution_integration.start_evolution_session(
                "성능 테스트"
            )
            result = await self.evolution_integration.execute_evolution_cycle(session)

            # 성능 검증 (5초 이내 완료)
            performance_ok = result.evolution_time < 5.0 if result else False

            details = {
                "evolution_time": result.evolution_time if result else 0,
                "performance_threshold": 5.0,
                "performance_ok": performance_ok,
            }

            return TestResult(
                test_name="Performance Test",
                success=performance_ok,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Performance Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )

    async def _test_stability(self) -> TestResult:
        """안정성 테스트"""
        try:
            start_time = time.time()

            # 안정성 테스트 (여러 번 실행)
            success_count = 0
            total_runs = 3

            for i in range(total_runs):
                try:
                    session = await self.evolution_integration.start_evolution_session(
                        f"안정성 테스트 {i+1}"
                    )
                    result = await self.evolution_integration.execute_evolution_cycle(
                        session
                    )

                    if result and result.success:
                        success_count += 1

                except Exception:
                    pass

            # 안정성 검증 (80% 이상 성공)
            stability_ok = success_count / total_runs >= 0.8

            details = {
                "success_count": success_count,
                "total_runs": total_runs,
                "success_rate": success_count / total_runs,
                "stability_threshold": 0.8,
            }

            return TestResult(
                test_name="Stability Test",
                success=stability_ok,
                execution_time=time.time() - start_time,
                details=details,
            )

        except Exception as e:
            return TestResult(
                test_name="Stability Test",
                success=False,
                execution_time=time.time() - start_time,
                details={},
                error_message=str(e),
            )


async def main():
    """메인 함수"""
    # Phase Ω Evolution Test 인스턴스 생성
    test_system = PhaseOmegaEvolutionTest()

    # 전체 테스트 실행
    result = await test_system.run_all_tests()

    # 결과 출력
    print("\n" + "=" * 80)
    print("🧪 Phase Ω Evolution Integration Test 결과")
    print("=" * 80)

    print(f"\n📊 전체 결과:")
    print(f"  - 총 테스트 수: {result.total_tests}")
    print(f"  - 통과한 테스트: {result.passed_tests}")
    print(f"  - 실패한 테스트: {result.failed_tests}")
    print(
        f"  - 통과율: {result.passed_tests/result.total_tests*100:.1f}%"
        if result.total_tests > 0
        else "  - 통과율: N/A"
    )
    print(f"  - 총 실행 시간: {result.total_time:.2f}초")
    print(f"  - 전체 성공 여부: {'✅ 성공' if result.overall_success else '❌ 실패'}")

    print(f"\n🔍 상세 결과:")
    for test_result in result.results:
        status = "✅ 통과" if test_result.success else "❌ 실패"
        print(
            f"  - {test_result.test_name}: {status} ({test_result.execution_time:.2f}초)"
        )

        if test_result.error_message:
            print(f"    오류: {test_result.error_message}")

        if test_result.details:
            for key, value in test_result.details.items():
                print(f"    {key}: {value}")

    return result


if __name__ == "__main__":
    asyncio.run(main())
