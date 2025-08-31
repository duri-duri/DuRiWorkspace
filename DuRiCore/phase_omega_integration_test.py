#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: 통합 테스트 시스템

이 모듈은 Phase Ω의 모든 시스템들을 통합 테스트하는 시스템입니다.
각 시스템의 개별 테스트와 통합 테스트를 수행합니다.

주요 기능:
- 개별 시스템 테스트
- 통합 시스템 테스트
- 성능 테스트
- 안정성 테스트
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union
import numpy as np

# Phase Ω 시스템들 import
from survival_instinct_engine import SurvivalInstinctEngine, SurvivalStatus, Threat, SurvivalGoal, SurvivalStatusEnum
from self_goal_generator import SelfGoalGenerator, CurrentState, ImprovementArea, SelfGoal, ImprovementAreaEnum
from evolution_system import EvolutionSystem, EvolutionProgress, AdaptationResult, EvolutionResult, SurvivalStrategy
from survival_assessment_system import SurvivalAssessmentSystem, RiskAssessment, ResourceAssessment, SurvivalScore, Recommendation
from phase_omega_integration import DuRiPhaseOmega, PhaseOmegaResult, IntegrationContext

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestType(Enum):
    """테스트 유형 열거형"""
    UNIT = "unit"
    INTEGRATION = "integration"
    PERFORMANCE = "performance"
    STABILITY = "stability"
    STRESS = "stress"


class TestStatus(Enum):
    """테스트 상태 열거형"""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class TestResult:
    """테스트 결과 데이터 클래스"""
    test_id: str
    test_type: TestType
    test_name: str
    status: TestStatus
    execution_time: float
    success: bool
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class TestSuite:
    """테스트 스위트 데이터 클래스"""
    suite_id: str
    suite_name: str
    tests: List[TestResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    skipped_tests: int
    execution_time: float
    success_rate: float


class PhaseOmegaIntegrationTest:
    """Phase Ω 통합 테스트 시스템"""
    
    def __init__(self):
        """초기화"""
        # Phase Ω 시스템들
        self.survival_engine = SurvivalInstinctEngine()
        self.goal_generator = SelfGoalGenerator()
        self.evolution_system = EvolutionSystem()
        self.survival_assessment = SurvivalAssessmentSystem()
        self.phase_omega = DuRiPhaseOmega()
        
        # 테스트 결과 저장
        self.test_results = []
        self.test_suites = []
        
        # 테스트 설정
        self.test_config = {
            "enable_unit_tests": True,
            "enable_integration_tests": True,
            "enable_performance_tests": True,
            "enable_stability_tests": True,
            "max_execution_time": 300.0,  # 5분
            "retry_count": 3
        }
        
        logger.info("Phase Ω 통합 테스트 시스템 초기화 완료")
    
    async def run_all_tests(self) -> TestSuite:
        """모든 테스트 실행"""
        try:
            start_time = time.time()
            suite_id = f"test_suite_{int(time.time())}"
            
            logger.info("🚀 Phase Ω 통합 테스트 시작...")
            
            # 테스트 결과 초기화
            test_results = []
            
            # 1. 단위 테스트
            if self.test_config["enable_unit_tests"]:
                unit_test_results = await self._run_unit_tests()
                test_results.extend(unit_test_results)
            
            # 2. 통합 테스트
            if self.test_config["enable_integration_tests"]:
                integration_test_results = await self._run_integration_tests()
                test_results.extend(integration_test_results)
            
            # 3. 성능 테스트
            if self.test_config["enable_performance_tests"]:
                performance_test_results = await self._run_performance_tests()
                test_results.extend(performance_test_results)
            
            # 4. 안정성 테스트
            if self.test_config["enable_stability_tests"]:
                stability_test_results = await self._run_stability_tests()
                test_results.extend(stability_test_results)
            
            # 테스트 스위트 생성
            execution_time = time.time() - start_time
            passed_tests = len([t for t in test_results if t.status == TestStatus.PASSED])
            failed_tests = len([t for t in test_results if t.status == TestStatus.FAILED])
            skipped_tests = len([t for t in test_results if t.status == TestStatus.SKIPPED])
            total_tests = len(test_results)
            success_rate = passed_tests / total_tests if total_tests > 0 else 0.0
            
            test_suite = TestSuite(
                suite_id=suite_id,
                suite_name="Phase Ω 통합 테스트 스위트",
                tests=test_results,
                total_tests=total_tests,
                passed_tests=passed_tests,
                failed_tests=failed_tests,
                skipped_tests=skipped_tests,
                execution_time=execution_time,
                success_rate=success_rate
            )
            
            self.test_suites.append(test_suite)
            
            logger.info(f"✅ Phase Ω 통합 테스트 완료: {passed_tests}/{total_tests} 성공 ({success_rate:.1%})")
            
            return test_suite
            
        except Exception as e:
            logger.error(f"Phase Ω 통합 테스트 실패: {e}")
            return await self._create_failed_test_suite(str(e))
    
    async def _run_unit_tests(self) -> List[TestResult]:
        """단위 테스트 실행"""
        try:
            test_results = []
            
            # 1. 생존 본능 엔진 테스트
            survival_engine_tests = await self._test_survival_instinct_engine()
            test_results.extend(survival_engine_tests)
            
            # 2. 자가 목표 생성기 테스트
            goal_generator_tests = await self._test_self_goal_generator()
            test_results.extend(goal_generator_tests)
            
            # 3. 진화 시스템 테스트
            evolution_system_tests = await self._test_evolution_system()
            test_results.extend(evolution_system_tests)
            
            # 4. 생존 평가 시스템 테스트
            survival_assessment_tests = await self._test_survival_assessment_system()
            test_results.extend(survival_assessment_tests)
            
            return test_results
            
        except Exception as e:
            logger.error(f"단위 테스트 실행 실패: {e}")
            return []
    
    async def _run_integration_tests(self) -> List[TestResult]:
        """통합 테스트 실행"""
        try:
            test_results = []
            
            # 1. Phase Ω 통합 시스템 테스트
            integration_tests = await self._test_phase_omega_integration()
            test_results.extend(integration_tests)
            
            # 2. 시스템 간 상호작용 테스트
            interaction_tests = await self._test_system_interactions()
            test_results.extend(interaction_tests)
            
            return test_results
            
        except Exception as e:
            logger.error(f"통합 테스트 실행 실패: {e}")
            return []
    
    async def _run_performance_tests(self) -> List[TestResult]:
        """성능 테스트 실행"""
        try:
            test_results = []
            
            # 1. 응답 시간 테스트
            response_time_tests = await self._test_response_times()
            test_results.extend(response_time_tests)
            
            # 2. 처리량 테스트
            throughput_tests = await self._test_throughput()
            test_results.extend(throughput_tests)
            
            # 3. 메모리 사용량 테스트
            memory_tests = await self._test_memory_usage()
            test_results.extend(memory_tests)
            
            return test_results
            
        except Exception as e:
            logger.error(f"성능 테스트 실행 실패: {e}")
            return []
    
    async def _run_stability_tests(self) -> List[TestResult]:
        """안정성 테스트 실행"""
        try:
            test_results = []
            
            # 1. 장시간 실행 테스트
            long_running_tests = await self._test_long_running()
            test_results.extend(long_running_tests)
            
            # 2. 오류 복구 테스트
            error_recovery_tests = await self._test_error_recovery()
            test_results.extend(error_recovery_tests)
            
            # 3. 부하 테스트
            stress_tests = await self._test_stress()
            test_results.extend(stress_tests)
            
            return test_results
            
        except Exception as e:
            logger.error(f"안정성 테스트 실행 실패: {e}")
            return []
    
    async def _test_survival_instinct_engine(self) -> List[TestResult]:
        """생존 본능 엔진 테스트"""
        test_results = []
        
        try:
            # 테스트 1: 생존 상태 평가
            start_time = time.time()
            survival_status = await self.survival_engine.assess_survival_status()
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="survival_engine_assessment",
                test_type=TestType.UNIT,
                test_name="생존 상태 평가 테스트",
                status=TestStatus.PASSED if survival_status else TestStatus.FAILED,
                execution_time=execution_time,
                success=survival_status is not None,
                metrics={"survival_probability": survival_status.survival_probability if survival_status else 0.0}
            )
            test_results.append(test_result)
            
            # 테스트 2: 위협 식별
            start_time = time.time()
            threats = await self.survival_engine.identify_threats({})
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="survival_engine_threats",
                test_type=TestType.UNIT,
                test_name="위협 식별 테스트",
                status=TestStatus.PASSED,
                execution_time=execution_time,
                success=True,
                metrics={"threat_count": len(threats)}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="survival_engine_error",
                test_type=TestType.UNIT,
                test_name="생존 본능 엔진 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_self_goal_generator(self) -> List[TestResult]:
        """자가 목표 생성기 테스트"""
        test_results = []
        
        try:
            # 테스트 1: 현재 상태 분석
            start_time = time.time()
            current_state = await self.goal_generator.analyze_current_state()
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="goal_generator_analysis",
                test_type=TestType.UNIT,
                test_name="현재 상태 분석 테스트",
                status=TestStatus.PASSED if current_state else TestStatus.FAILED,
                execution_time=execution_time,
                success=current_state is not None,
                metrics={"confidence_score": current_state.confidence_score if current_state else 0.0}
            )
            test_results.append(test_result)
            
            # 테스트 2: 자가 목표 생성
            if current_state:
                start_time = time.time()
                improvement_areas = await self.goal_generator.identify_improvement_areas(current_state)
                self_goals = await self.goal_generator.generate_self_goals(current_state, improvement_areas)
                execution_time = time.time() - start_time
                
                test_result = TestResult(
                    test_id="goal_generator_goals",
                    test_type=TestType.UNIT,
                    test_name="자가 목표 생성 테스트",
                    status=TestStatus.PASSED,
                    execution_time=execution_time,
                    success=True,
                    metrics={"goal_count": len(self_goals)}
                )
                test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="goal_generator_error",
                test_type=TestType.UNIT,
                test_name="자가 목표 생성기 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_evolution_system(self) -> List[TestResult]:
        """진화 시스템 테스트"""
        test_results = []
        
        try:
            # 테스트 1: 진화 진행도 평가
            start_time = time.time()
            evolution_progress = await self.evolution_system.evaluate_evolution_progress()
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="evolution_progress",
                test_type=TestType.UNIT,
                test_name="진화 진행도 평가 테스트",
                status=TestStatus.PASSED if evolution_progress else TestStatus.FAILED,
                execution_time=execution_time,
                success=evolution_progress is not None,
                metrics={"evolution_score": evolution_progress.evolution_score if evolution_progress else 0.0}
            )
            test_results.append(test_result)
            
            # 테스트 2: 환경 적응
            start_time = time.time()
            adaptation_result = await self.evolution_system.adapt_to_environment({"magnitude": 0.5})
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="evolution_adaptation",
                test_type=TestType.UNIT,
                test_name="환경 적응 테스트",
                status=TestStatus.PASSED,
                execution_time=execution_time,
                success=True,
                metrics={"adaptation_score": adaptation_result.adaptation_score}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="evolution_system_error",
                test_type=TestType.UNIT,
                test_name="진화 시스템 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_survival_assessment_system(self) -> List[TestResult]:
        """생존 평가 시스템 테스트"""
        test_results = []
        
        try:
            # 테스트 1: 환경적 위험 평가
            start_time = time.time()
            risk_assessments = await self.survival_assessment.assess_environmental_risks()
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="survival_assessment_risks",
                test_type=TestType.UNIT,
                test_name="환경적 위험 평가 테스트",
                status=TestStatus.PASSED,
                execution_time=execution_time,
                success=True,
                metrics={"risk_count": len(risk_assessments)}
            )
            test_results.append(test_result)
            
            # 테스트 2: 생존 점수 계산
            start_time = time.time()
            resource_assessments = await self.survival_assessment.evaluate_resource_availability()
            survival_score = await self.survival_assessment.calculate_survival_score(risk_assessments, resource_assessments)
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="survival_assessment_score",
                test_type=TestType.UNIT,
                test_name="생존 점수 계산 테스트",
                status=TestStatus.PASSED if survival_score else TestStatus.FAILED,
                execution_time=execution_time,
                success=survival_score is not None,
                metrics={"survival_score": survival_score.overall_score if survival_score else 0.0}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="survival_assessment_error",
                test_type=TestType.UNIT,
                test_name="생존 평가 시스템 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_phase_omega_integration(self) -> List[TestResult]:
        """Phase Ω 통합 시스템 테스트"""
        test_results = []
        
        try:
            # 테스트 1: 실제 Phase Ω 통합 프로세스 실행
            start_time = time.time()
            
            # 실제 입력 데이터로 테스트
            test_input = {
                "user_query": "Phase Ω가 제대로 작동하는지 확인해주세요",
                "context": {
                    "system_health": 0.8,
                    "resource_availability": 0.7,
                    "environmental_factors": {"stability": 0.6}
                }
            }
            
            result = await self.phase_omega.process_with_survival_instinct(test_input)
            execution_time = time.time() - start_time
            
            # 실제 결과 검증
            success = (
                result is not None and
                result.success and
                result.survival_status is not None and
                len(result.self_goals) > 0 and
                result.integration_time > 0
            )
            
            test_result = TestResult(
                test_id="phase_omega_integration",
                test_type=TestType.INTEGRATION,
                test_name="Phase Ω 통합 프로세스 테스트",
                status=TestStatus.PASSED if success else TestStatus.FAILED,
                execution_time=execution_time,
                success=success,
                metrics={
                    "survival_probability": result.survival_status.survival_probability if result and result.survival_status else 0.0,
                    "goal_count": len(result.self_goals) if result else 0,
                    "integration_time": result.integration_time if result else 0.0
                }
            )
            test_results.append(test_result)
            
            # 테스트 2: 생존 본능이 실제로 작동하는지 확인
            if result and result.survival_status:
                survival_working = (
                    result.survival_status.survival_probability > 0 and
                    result.survival_status.survival_probability <= 1 and
                    result.survival_status.status in [SurvivalStatusEnum.CRITICAL, SurvivalStatusEnum.DANGEROUS, 
                                                     SurvivalStatusEnum.STABLE, SurvivalStatusEnum.SECURE, SurvivalStatusEnum.THRIVING]
                )
                
                test_result = TestResult(
                    test_id="survival_instinct_working",
                    test_type=TestType.INTEGRATION,
                    test_name="생존 본능 작동 테스트",
                    status=TestStatus.PASSED if survival_working else TestStatus.FAILED,
                    execution_time=0.0,
                    success=survival_working,
                    metrics={"survival_status": result.survival_status.status.value if result.survival_status else "unknown"}
                )
                test_results.append(test_result)
            
            # 테스트 3: 자가 목표가 실제로 생성되는지 확인
            if result and result.self_goals:
                goals_working = all(
                    goal.goal_id and goal.title and goal.description and goal.priority
                    for goal in result.self_goals
                )
                
                test_result = TestResult(
                    test_id="self_goals_working",
                    test_type=TestType.INTEGRATION,
                    test_name="자가 목표 생성 테스트",
                    status=TestStatus.PASSED if goals_working else TestStatus.FAILED,
                    execution_time=0.0,
                    success=goals_working,
                    metrics={"goal_count": len(result.self_goals)}
                )
                test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="phase_omega_error",
                test_type=TestType.INTEGRATION,
                test_name="Phase Ω 통합 시스템 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_system_interactions(self) -> List[TestResult]:
        """시스템 간 상호작용 테스트"""
        test_results = []
        
        try:
            # 생존 엔진과 목표 생성기 상호작용
            start_time = time.time()
            survival_status = await self.survival_engine.assess_survival_status()
            current_state = await self.goal_generator.analyze_current_state()
            
            if survival_status and current_state:
                improvement_areas = await self.goal_generator.identify_improvement_areas(current_state)
                self_goals = await self.goal_generator.generate_self_goals(current_state, improvement_areas)
                execution_time = time.time() - start_time
                
                test_result = TestResult(
                    test_id="system_interactions",
                    test_type=TestType.INTEGRATION,
                    test_name="시스템 간 상호작용 테스트",
                    status=TestStatus.PASSED,
                    execution_time=execution_time,
                    success=True,
                    metrics={"goals_generated": len(self_goals)}
                )
                test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="system_interactions_error",
                test_type=TestType.INTEGRATION,
                test_name="시스템 간 상호작용 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_response_times(self) -> List[TestResult]:
        """응답 시간 테스트"""
        test_results = []
        
        try:
            # 생존 엔진 응답 시간
            start_time = time.time()
            await self.survival_engine.assess_survival_status()
            response_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="response_time_survival",
                test_type=TestType.PERFORMANCE,
                test_name="생존 엔진 응답 시간 테스트",
                status=TestStatus.PASSED if response_time < 1.0 else TestStatus.FAILED,
                execution_time=response_time,
                success=response_time < 1.0,
                metrics={"response_time": response_time}
            )
            test_results.append(test_result)
            
            # 목표 생성기 응답 시간
            start_time = time.time()
            current_state = await self.goal_generator.analyze_current_state()
            response_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="response_time_goals",
                test_type=TestType.PERFORMANCE,
                test_name="목표 생성기 응답 시간 테스트",
                status=TestStatus.PASSED if response_time < 1.0 else TestStatus.FAILED,
                execution_time=response_time,
                success=response_time < 1.0,
                metrics={"response_time": response_time}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="response_time_error",
                test_type=TestType.PERFORMANCE,
                test_name="응답 시간 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_throughput(self) -> List[TestResult]:
        """처리량 테스트"""
        test_results = []
        
        try:
            # 동시 요청 처리 테스트
            start_time = time.time()
            tasks = []
            for i in range(10):
                task = self.survival_engine.assess_survival_status()
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            execution_time = time.time() - start_time
            
            success_count = len([r for r in results if not isinstance(r, Exception)])
            
            test_result = TestResult(
                test_id="throughput_test",
                test_type=TestType.PERFORMANCE,
                test_name="처리량 테스트",
                status=TestStatus.PASSED if success_count >= 8 else TestStatus.FAILED,
                execution_time=execution_time,
                success=success_count >= 8,
                metrics={"success_rate": success_count / 10, "throughput": 10 / execution_time}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="throughput_error",
                test_type=TestType.PERFORMANCE,
                test_name="처리량 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_memory_usage(self) -> List[TestResult]:
        """메모리 사용량 테스트"""
        test_results = []
        
        try:
            import psutil
            import os
            
            process = psutil.Process(os.getpid())
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # 메모리 사용량이 많은 작업 실행
            for i in range(100):
                await self.survival_engine.assess_survival_status()
            
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            test_result = TestResult(
                test_id="memory_usage",
                test_type=TestType.PERFORMANCE,
                test_name="메모리 사용량 테스트",
                status=TestStatus.PASSED if memory_increase < 100 else TestStatus.FAILED,
                execution_time=0.0,
                success=memory_increase < 100,
                metrics={"memory_increase_mb": memory_increase}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="memory_usage_error",
                test_type=TestType.PERFORMANCE,
                test_name="메모리 사용량 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_long_running(self) -> List[TestResult]:
        """장시간 실행 테스트"""
        test_results = []
        
        try:
            # 30초 동안 지속적인 작업 실행
            start_time = time.time()
            iteration_count = 0
            
            while time.time() - start_time < 30:
                await self.survival_engine.assess_survival_status()
                iteration_count += 1
                await asyncio.sleep(0.1)
            
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="long_running",
                test_type=TestType.STABILITY,
                test_name="장시간 실행 테스트",
                status=TestStatus.PASSED,
                execution_time=execution_time,
                success=True,
                metrics={"iterations": iteration_count, "avg_time_per_iteration": execution_time / iteration_count}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="long_running_error",
                test_type=TestType.STABILITY,
                test_name="장시간 실행 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_error_recovery(self) -> List[TestResult]:
        """오류 복구 테스트"""
        test_results = []
        
        try:
            # 잘못된 입력으로 테스트
            start_time = time.time()
            
            # None 입력 테스트
            try:
                await self.survival_engine.assess_survival_status(None)
                recovery_success = True
            except Exception:
                recovery_success = False
            
            execution_time = time.time() - start_time
            
            test_result = TestResult(
                test_id="error_recovery",
                test_type=TestType.STABILITY,
                test_name="오류 복구 테스트",
                status=TestStatus.PASSED if recovery_success else TestStatus.FAILED,
                execution_time=execution_time,
                success=recovery_success,
                metrics={"recovery_success": recovery_success}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="error_recovery_error",
                test_type=TestType.STABILITY,
                test_name="오류 복구 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _test_stress(self) -> List[TestResult]:
        """부하 테스트"""
        test_results = []
        
        try:
            # 동시에 많은 요청 처리
            start_time = time.time()
            tasks = []
            for i in range(50):
                task = self.survival_engine.assess_survival_status()
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            execution_time = time.time() - start_time
            
            success_count = len([r for r in results if not isinstance(r, Exception)])
            success_rate = success_count / 50
            
            test_result = TestResult(
                test_id="stress_test",
                test_type=TestType.STABILITY,
                test_name="부하 테스트",
                status=TestStatus.PASSED if success_rate >= 0.8 else TestStatus.FAILED,
                execution_time=execution_time,
                success=success_rate >= 0.8,
                metrics={"success_rate": success_rate, "total_requests": 50}
            )
            test_results.append(test_result)
            
        except Exception as e:
            test_result = TestResult(
                test_id="stress_test_error",
                test_type=TestType.STABILITY,
                test_name="부하 테스트",
                status=TestStatus.FAILED,
                execution_time=0.0,
                success=False,
                error_message=str(e)
            )
            test_results.append(test_result)
        
        return test_results
    
    async def _create_failed_test_suite(self, error_message: str) -> TestSuite:
        """실패한 테스트 스위트 생성"""
        return TestSuite(
            suite_id=f"failed_suite_{int(time.time())}",
            suite_name="실패한 테스트 스위트",
            tests=[],
            total_tests=0,
            passed_tests=0,
            failed_tests=1,
            skipped_tests=0,
            execution_time=0.0,
            success_rate=0.0
        )
    
    async def generate_test_report(self, test_suite: TestSuite) -> Dict[str, Any]:
        """테스트 보고서 생성"""
        try:
            report = {
                "test_suite_id": test_suite.suite_id,
                "test_suite_name": test_suite.suite_name,
                "execution_time": test_suite.execution_time,
                "total_tests": test_suite.total_tests,
                "passed_tests": test_suite.passed_tests,
                "failed_tests": test_suite.failed_tests,
                "skipped_tests": test_suite.skipped_tests,
                "success_rate": test_suite.success_rate,
                "timestamp": datetime.now().isoformat(),
                "test_results": []
            }
            
            for test in test_suite.tests:
                test_info = {
                    "test_id": test.test_id,
                    "test_name": test.test_name,
                    "test_type": test.test_type.value,
                    "status": test.status.value,
                    "execution_time": test.execution_time,
                    "success": test.success,
                    "error_message": test.error_message,
                    "metrics": test.metrics
                }
                report["test_results"].append(test_info)
            
            return report
            
        except Exception as e:
            logger.error(f"테스트 보고서 생성 실패: {e}")
            return {"error": str(e)}


async def main():
    """메인 함수"""
    # Phase Ω 통합 테스트 시스템 초기화
    test_system = PhaseOmegaIntegrationTest()
    
    # 모든 테스트 실행
    print("🚀 Phase Ω 통합 테스트 시작...")
    test_suite = await test_system.run_all_tests()
    
    # 테스트 결과 출력
    print(f"\n📊 테스트 결과 요약:")
    print(f"✅ 성공한 테스트: {test_suite.passed_tests}/{test_suite.total_tests}")
    print(f"❌ 실패한 테스트: {test_suite.failed_tests}")
    print(f"⏭️  건너뛴 테스트: {test_suite.skipped_tests}")
    print(f"📈 성공률: {test_suite.success_rate:.1%}")
    print(f"⏱️  총 실행 시간: {test_suite.execution_time:.2f}초")
    
    # 상세 결과 출력
    print(f"\n📋 상세 테스트 결과:")
    for test in test_suite.tests:
        status_emoji = "✅" if test.status == TestStatus.PASSED else "❌" if test.status == TestStatus.FAILED else "⏭️"
        print(f"{status_emoji} {test.test_name}: {test.status.value} ({test.execution_time:.2f}초)")
        if test.error_message:
            print(f"   오류: {test.error_message}")
    
    # 테스트 보고서 생성
    report = await test_system.generate_test_report(test_suite)
    print(f"\n📄 테스트 보고서 생성 완료")
    
    # JSON 파일로 저장
    with open("phase_omega_test_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"💾 테스트 보고서가 'phase_omega_test_report.json'에 저장되었습니다")


if __name__ == "__main__":
    asyncio.run(main()) 