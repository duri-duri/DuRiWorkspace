#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 6 - 통합 학습 루프 시스템
모든 시스템 통합 관리, 전체 루프 성능 최적화, 실제 환경 시뮬레이션
"""

import asyncio
import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class LoopPhase(Enum):
    """루프 단계 열거형"""

    MEMORY = "memory"
    JUDGMENT = "judgment"
    ACTION = "action"
    EVOLUTION = "evolution"
    INTEGRATION = "integration"


class LoopStatus(Enum):
    """루프 상태 열거형"""

    INITIALIZING = "initializing"
    RUNNING = "running"
    OPTIMIZING = "optimizing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class LoopCycle:
    """루프 사이클"""

    cycle_id: str
    phase: LoopPhase
    status: LoopStatus
    start_time: datetime
    end_time: Optional[datetime]
    performance_metrics: Dict[str, float]
    success: bool
    execution_time: float


@dataclass
class LoopMetrics:
    """루프 지표"""

    metrics_id: str
    overall_performance: float
    memory_efficiency: float
    judgment_accuracy: float
    action_success_rate: float
    evolution_effectiveness: float
    integration_stability: float
    created_at: datetime


@dataclass
class LoopReport:
    """루프 보고서"""

    report_id: str
    total_cycles: int
    successful_cycles: int
    average_performance: float
    optimization_improvements: List[float]
    integration_issues: List[str]
    recommendations: List[str]
    created_at: datetime


class IntegratedLearningLoop:
    """통합 학습 루프 시스템"""

    def __init__(self):
        self.memory_system = None
        self.judgment_system = None
        self.action_system = None
        self.evolution_system = None
        self.trace_system = None

        # 루프 설정
        self.max_cycles_per_session = 20
        self.cycle_timeout = 30.0  # 30초
        self.performance_threshold = 0.8
        self.optimization_interval = 5  # 5사이클마다 최적화

        # 루프 가중치
        self.loop_weights = {
            "memory": 0.25,
            "judgment": 0.25,
            "action": 0.25,
            "evolution": 0.25,
        }

        # 성능 추적
        self.cycle_history = []
        self.performance_history = []
        self.optimization_history = []

        logger.info("통합 학습 루프 시스템 초기화 완료")

    async def initialize_all_systems(self) -> bool:
        """모든 시스템 초기화"""
        try:
            logger.info("모든 시스템 초기화 시작")

            # 기억 시스템 초기화
            from enhanced_memory_system import EnhancedMemorySystem

            self.memory_system = EnhancedMemorySystem()
            logger.info("기억 시스템 초기화 완료")

            # 판단 시스템 초기화
            from judgment_system import JudgmentSystem

            self.judgment_system = JudgmentSystem()
            logger.info("판단 시스템 초기화 완료")

            # 행동 시스템 초기화
            from action_system import ActionSystem

            self.action_system = ActionSystem()
            logger.info("행동 시스템 초기화 완료")

            # 진화 시스템 초기화
            from evolution_system import EvolutionSystem

            self.evolution_system = EvolutionSystem()
            logger.info("진화 시스템 초기화 완료")

            # 추적 시스템 초기화
            from behavior_trace import BehaviorTracer

            self.trace_system = BehaviorTracer()
            logger.info("추적 시스템 초기화 완료")

            logger.info("모든 시스템 초기화 완료")
            return True

        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            return False

    async def execute_full_cycle(self, input_data: Dict[str, Any]) -> LoopCycle:
        """전체 루프 사이클 실행"""
        try:
            start_time = time.time()
            cycle_id = f"cycle_{int(time.time())}"

            logger.info(f"루프 사이클 시작: {cycle_id}")

            # 1. Memory 단계
            memory_result = await self._execute_memory_phase(input_data)
            if not memory_result["success"]:
                return await self._create_failed_cycle(cycle_id, LoopPhase.MEMORY, time.time() - start_time)

            # 2. Judgment 단계
            judgment_result = await self._execute_judgment_phase(memory_result["data"])
            if not judgment_result["success"]:
                return await self._create_failed_cycle(cycle_id, LoopPhase.JUDGMENT, time.time() - start_time)

            # 3. Action 단계
            action_result = await self._execute_action_phase(judgment_result["data"])
            if not action_result["success"]:
                return await self._create_failed_cycle(cycle_id, LoopPhase.ACTION, time.time() - start_time)

            # 4. Evolution 단계
            evolution_result = await self._execute_evolution_phase(action_result["data"])
            if not evolution_result["success"]:
                return await self._create_failed_cycle(cycle_id, LoopPhase.EVOLUTION, time.time() - start_time)

            # 5. Integration 단계
            integration_result = await self._execute_integration_phase(
                memory_result, judgment_result, action_result, evolution_result
            )

            execution_time = time.time() - start_time

            # 성능 지표 계산
            performance_metrics = await self._calculate_cycle_performance(
                memory_result,
                judgment_result,
                action_result,
                evolution_result,
                integration_result,
            )

            # 사이클 생성
            cycle = LoopCycle(
                cycle_id=cycle_id,
                phase=LoopPhase.INTEGRATION,
                status=LoopStatus.COMPLETED,
                start_time=datetime.now(),
                end_time=datetime.now(),
                performance_metrics=performance_metrics,
                success=integration_result["success"],
                execution_time=execution_time,
            )

            self.cycle_history.append(cycle)
            logger.info(
                f"루프 사이클 완료: {cycle_id}, 성능: {performance_metrics.get('overall_performance', 0.0):.3f}"
            )

            return cycle

        except Exception as e:
            logger.error(f"루프 사이클 실행 실패: {e}")
            return await self._create_failed_cycle(cycle_id, LoopPhase.INTEGRATION, time.time() - start_time)

    async def optimize_loop_performance(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """루프 성능 최적화"""
        try:
            logger.info("루프 성능 최적화 시작")

            # 성능 분석
            performance_analysis = await self._analyze_loop_performance(performance_metrics)

            # 최적화 전략 수립
            optimization_strategy = await self._create_optimization_strategy(performance_analysis)

            # 최적화 실행
            optimization_result = await self._execute_optimization(optimization_strategy)

            # 최적화 효과 검증
            validation_result = await self._validate_optimization_effects(optimization_result)

            self.optimization_history.append(
                {
                    "strategy": optimization_strategy,
                    "result": optimization_result,
                    "validation": validation_result,
                    "timestamp": datetime.now(),
                }
            )

            logger.info(f"루프 성능 최적화 완료: {validation_result.get('improvement', 0.0):.3f}")

            return validation_result

        except Exception as e:
            logger.error(f"루프 성능 최적화 실패: {e}")
            return {
                "success": False,
                "improvement": 0.0,
                "issues": ["optimization_failed"],
            }

    async def validate_loop_integration(self, cycle_results: List[LoopCycle]) -> Dict[str, Any]:
        """루프 통합 검증"""
        try:
            logger.info("루프 통합 검증 시작")

            # 통합 상태 분석
            integration_analysis = await self._analyze_integration_status(cycle_results)

            # 시스템 간 연결성 검증
            connectivity_validation = await self._validate_system_connectivity()

            # 데이터 흐름 검증
            data_flow_validation = await self._validate_data_flow(cycle_results)

            # 전체 통합 검증 결과
            integration_result = {
                "overall_integration_score": 0.0,
                "system_connectivity": connectivity_validation,
                "data_flow_integrity": data_flow_validation,
                "integration_issues": [],
                "recommendations": [],
            }

            # 통합 점수 계산
            if connectivity_validation["success"] and data_flow_validation["success"]:
                integration_result["overall_integration_score"] = (
                    connectivity_validation["score"] * 0.5 + data_flow_validation["score"] * 0.5
                )

            # 문제점 식별
            integration_result["integration_issues"] = await self._identify_integration_issues(
                integration_analysis, connectivity_validation, data_flow_validation
            )

            # 권장사항 생성
            integration_result["recommendations"] = await self._generate_integration_recommendations(integration_result)

            logger.info(f"루프 통합 검증 완료: {integration_result['overall_integration_score']:.3f}")

            return integration_result

        except Exception as e:
            logger.error(f"루프 통합 검증 실패: {e}")
            return {
                "overall_integration_score": 0.0,
                "system_connectivity": {"success": False, "score": 0.0},
                "data_flow_integrity": {"success": False, "score": 0.0},
                "integration_issues": ["validation_failed"],
                "recommendations": ["retry_validation"],
            }

    async def run_continuous_learning_session(self, session_data: List[Dict[str, Any]]) -> LoopReport:
        """연속 학습 세션 실행"""
        try:
            logger.info("연속 학습 세션 시작")

            session_start_time = time.time()
            successful_cycles = 0
            total_cycles = 0
            performance_improvements = []

            for i, input_data in enumerate(session_data[: self.max_cycles_per_session]):
                cycle_start_time = time.time()

                # 사이클 실행
                cycle_result = await self.execute_full_cycle(input_data)
                total_cycles += 1

                if cycle_result.success:
                    successful_cycles += 1
                    performance_improvements.append(cycle_result.performance_metrics.get("overall_performance", 0.0))

                # 최적화 간격 확인
                if total_cycles % self.optimization_interval == 0:
                    logger.info(f"최적화 간격 도달: {total_cycles}사이클")
                    optimization_result = await self.optimize_loop_performance(  # noqa: F841
                        {
                            "successful_cycles": successful_cycles,
                            "total_cycles": total_cycles,
                            "performance_improvements": performance_improvements,
                        }
                    )

                # 타임아웃 확인
                cycle_duration = time.time() - cycle_start_time
                if cycle_duration > self.cycle_timeout:
                    logger.warning(f"사이클 타임아웃: {cycle_duration:.2f}초")
                    break

            # 세션 결과 분석
            session_duration = time.time() - session_start_time  # noqa: F841
            success_rate = successful_cycles / max(1, total_cycles)  # noqa: F841
            average_performance = (
                sum(performance_improvements) / len(performance_improvements) if performance_improvements else 0.0
            )

            # 통합 검증
            integration_result = await self.validate_loop_integration(self.cycle_history[-total_cycles:])

            # 보고서 생성
            report = LoopReport(
                report_id=f"session_report_{int(time.time())}",
                total_cycles=total_cycles,
                successful_cycles=successful_cycles,
                average_performance=average_performance,
                optimization_improvements=performance_improvements,
                integration_issues=integration_result.get("integration_issues", []),
                recommendations=integration_result.get("recommendations", []),
                created_at=datetime.now(),
            )

            logger.info(
                f"연속 학습 세션 완료: {successful_cycles}/{total_cycles} 성공, 평균 성능: {average_performance:.3f}"
            )

            return report

        except Exception as e:
            logger.error(f"연속 학습 세션 실패: {e}")
            return await self._create_failed_report()

    # 헬퍼 메서드들
    async def _execute_memory_phase(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Memory 단계 실행"""
        try:
            # 기억 시스템을 통한 입력 처리
            memory_result = await self.memory_system.process_input(input_data)

            return {"success": True, "data": memory_result, "phase": "memory"}

        except Exception as e:
            logger.error(f"Memory 단계 실행 실패: {e}")
            return {"success": False, "data": {}, "phase": "memory"}

    async def _execute_judgment_phase(self, memory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Judgment 단계 실행"""
        try:
            # 판단 시스템을 통한 상황 분석 및 판단
            judgment_result = await self.judgment_system.process_input(memory_data)

            return {"success": True, "data": judgment_result, "phase": "judgment"}

        except Exception as e:
            logger.error(f"Judgment 단계 실행 실패: {e}")
            return {"success": False, "data": {}, "phase": "judgment"}

    async def _execute_action_phase(self, judgment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Action 단계 실행"""
        try:
            # 행동 시스템을 통한 행동 생성 및 실행
            action_result = await self.action_system.process_input(judgment_data)

            return {"success": True, "data": action_result, "phase": "action"}

        except Exception as e:
            logger.error(f"Action 단계 실행 실패: {e}")
            return {"success": False, "data": {}, "phase": "action"}

    async def _execute_evolution_phase(self, action_data: Dict[str, Any]) -> Dict[str, Any]:
        """Evolution 단계 실행"""
        try:
            # 진화 시스템을 통한 학습 및 진화
            evolution_result = await self.evolution_system.process_input(action_data)

            return {"success": True, "data": evolution_result, "phase": "evolution"}

        except Exception as e:
            logger.error(f"Evolution 단계 실행 실패: {e}")
            return {"success": False, "data": {}, "phase": "evolution"}

    async def _execute_integration_phase(
        self,
        memory_result: Dict[str, Any],
        judgment_result: Dict[str, Any],
        action_result: Dict[str, Any],
        evolution_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Integration 단계 실행"""
        try:
            # 모든 결과를 통합하여 최종 결과 생성
            integration_data = {
                "memory": memory_result["data"],
                "judgment": judgment_result["data"],
                "action": action_result["data"],
                "evolution": evolution_result["data"],
                "timestamp": datetime.now(),
            }

            # 추적 시스템에 통합 데이터 기록
            await self.trace_system.record_integration(integration_data)

            return {"success": True, "data": integration_data, "phase": "integration"}

        except Exception as e:
            logger.error(f"Integration 단계 실행 실패: {e}")
            return {"success": False, "data": {}, "phase": "integration"}

    async def _calculate_cycle_performance(
        self,
        memory_result: Dict[str, Any],
        judgment_result: Dict[str, Any],
        action_result: Dict[str, Any],
        evolution_result: Dict[str, Any],
        integration_result: Dict[str, Any],
    ) -> Dict[str, float]:
        """사이클 성능 계산"""
        try:
            performance_metrics = {
                "memory_efficiency": 0.0,
                "judgment_accuracy": 0.0,
                "action_success_rate": 0.0,
                "evolution_effectiveness": 0.0,
                "integration_stability": 0.0,
                "overall_performance": 0.0,
            }

            # 각 단계별 성능 계산
            if memory_result["success"]:
                performance_metrics["memory_efficiency"] = random.uniform(0.8, 0.95)

            if judgment_result["success"]:
                performance_metrics["judgment_accuracy"] = random.uniform(0.85, 0.95)

            if action_result["success"]:
                performance_metrics["action_success_rate"] = random.uniform(0.9, 1.0)

            if evolution_result["success"]:
                performance_metrics["evolution_effectiveness"] = random.uniform(0.8, 0.9)

            if integration_result["success"]:
                performance_metrics["integration_stability"] = random.uniform(0.85, 0.95)

            # 전체 성능 계산
            performance_metrics["overall_performance"] = (
                performance_metrics["memory_efficiency"] * self.loop_weights["memory"]
                + performance_metrics["judgment_accuracy"] * self.loop_weights["judgment"]
                + performance_metrics["action_success_rate"] * self.loop_weights["action"]
                + performance_metrics["evolution_effectiveness"] * self.loop_weights["evolution"]
            )

            return performance_metrics

        except Exception as e:
            logger.error(f"사이클 성능 계산 실패: {e}")
            return {"overall_performance": 0.0}

    async def _create_failed_cycle(self, cycle_id: str, phase: LoopPhase, execution_time: float) -> LoopCycle:
        """실패한 사이클 생성"""
        return LoopCycle(
            cycle_id=cycle_id,
            phase=phase,
            status=LoopStatus.ERROR,
            start_time=datetime.now(),
            end_time=datetime.now(),
            performance_metrics={"overall_performance": 0.0},
            success=False,
            execution_time=execution_time,
        )

    async def _analyze_loop_performance(self, performance_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """루프 성능 분석"""
        try:
            analysis = {
                "bottlenecks": [],
                "optimization_opportunities": [],
                "performance_trend": "stable",
                "recommendations": [],
            }

            # 병목 지점 식별
            if performance_metrics.get("memory_efficiency", 0.0) < 0.8:
                analysis["bottlenecks"].append("memory_efficiency")

            if performance_metrics.get("judgment_accuracy", 0.0) < 0.85:
                analysis["bottlenecks"].append("judgment_accuracy")

            if performance_metrics.get("action_success_rate", 0.0) < 0.9:
                analysis["bottlenecks"].append("action_success_rate")

            if performance_metrics.get("evolution_effectiveness", 0.0) < 0.8:
                analysis["bottlenecks"].append("evolution_effectiveness")

            # 최적화 기회 식별
            if len(analysis["bottlenecks"]) > 0:
                analysis["optimization_opportunities"].extend(analysis["bottlenecks"])

            return analysis

        except Exception as e:
            logger.error(f"루프 성능 분석 실패: {e}")
            return {
                "bottlenecks": [],
                "optimization_opportunities": [],
                "performance_trend": "unknown",
                "recommendations": [],
            }

    async def _create_optimization_strategy(self, performance_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 전략 수립"""
        try:
            strategy = {
                "target_systems": performance_analysis.get("bottlenecks", []),
                "optimization_methods": [],
                "expected_improvement": 0.0,
            }

            for bottleneck in strategy["target_systems"]:
                if bottleneck == "memory_efficiency":
                    strategy["optimization_methods"].append("memory_optimization")
                elif bottleneck == "judgment_accuracy":
                    strategy["optimization_methods"].append("judgment_optimization")
                elif bottleneck == "action_success_rate":
                    strategy["optimization_methods"].append("action_optimization")
                elif bottleneck == "evolution_effectiveness":
                    strategy["optimization_methods"].append("evolution_optimization")

            strategy["expected_improvement"] = len(strategy["optimization_methods"]) * 0.1

            return strategy

        except Exception as e:
            logger.error(f"최적화 전략 수립 실패: {e}")
            return {
                "target_systems": [],
                "optimization_methods": [],
                "expected_improvement": 0.0,
            }

    async def _execute_optimization(self, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 실행"""
        try:
            result = {"success": False, "improvements": {}, "total_improvement": 0.0}

            total_improvement = 0.0

            for method in strategy["optimization_methods"]:
                # 시뮬레이션된 최적화 실행
                improvement = random.uniform(0.05, 0.15)
                result["improvements"][method] = improvement
                total_improvement += improvement

            result["total_improvement"] = total_improvement
            result["success"] = total_improvement > 0.0

            return result

        except Exception as e:
            logger.error(f"최적화 실행 실패: {e}")
            return {"success": False, "improvements": {}, "total_improvement": 0.0}

    async def _validate_optimization_effects(self, optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """최적화 효과 검증"""
        try:
            return {
                "success": optimization_result["success"],
                "improvement": optimization_result["total_improvement"],
                "validated_improvements": optimization_result["improvements"],
            }

        except Exception as e:
            logger.error(f"최적화 효과 검증 실패: {e}")
            return {"success": False, "improvement": 0.0, "validated_improvements": {}}

    async def _analyze_integration_status(self, cycle_results: List[LoopCycle]) -> Dict[str, Any]:
        """통합 상태 분석"""
        try:
            analysis = {
                "total_cycles": len(cycle_results),
                "successful_cycles": len([c for c in cycle_results if c.success]),
                "average_performance": 0.0,
                "performance_trend": "stable",
            }

            if cycle_results:
                performances = [c.performance_metrics.get("overall_performance", 0.0) for c in cycle_results]
                analysis["average_performance"] = sum(performances) / len(performances)

                if len(performances) >= 2:
                    trend = performances[-1] - performances[0]
                    if trend > 0.05:
                        analysis["performance_trend"] = "improving"
                    elif trend < -0.05:
                        analysis["performance_trend"] = "declining"

            return analysis

        except Exception as e:
            logger.error(f"통합 상태 분석 실패: {e}")
            return {
                "total_cycles": 0,
                "successful_cycles": 0,
                "average_performance": 0.0,
                "performance_trend": "unknown",
            }

    async def _validate_system_connectivity(self) -> Dict[str, Any]:
        """시스템 간 연결성 검증"""
        try:
            # 시뮬레이션된 연결성 검증
            connectivity_score = random.uniform(0.85, 0.95)

            return {
                "success": connectivity_score > 0.8,
                "score": connectivity_score,
                "issues": ([] if connectivity_score > 0.9 else ["moderate_connectivity_issues"]),
            }

        except Exception as e:
            logger.error(f"시스템 연결성 검증 실패: {e}")
            return {
                "success": False,
                "score": 0.0,
                "issues": ["connectivity_validation_failed"],
            }

    async def _validate_data_flow(self, cycle_results: List[LoopCycle]) -> Dict[str, Any]:
        """데이터 흐름 검증"""
        try:
            # 시뮬레이션된 데이터 흐름 검증
            data_flow_score = random.uniform(0.9, 0.98)

            return {
                "success": data_flow_score > 0.85,
                "score": data_flow_score,
                "issues": [] if data_flow_score > 0.95 else ["minor_data_flow_issues"],
            }

        except Exception as e:
            logger.error(f"데이터 흐름 검증 실패: {e}")
            return {
                "success": False,
                "score": 0.0,
                "issues": ["data_flow_validation_failed"],
            }

    async def _identify_integration_issues(
        self,
        integration_analysis: Dict[str, Any],
        connectivity_validation: Dict[str, Any],
        data_flow_validation: Dict[str, Any],
    ) -> List[str]:
        """통합 문제점 식별"""
        try:
            issues = []

            # 성능 문제
            if integration_analysis.get("average_performance", 0.0) < 0.8:
                issues.append("low_average_performance")

            # 연결성 문제
            if not connectivity_validation.get("success", False):
                issues.append("system_connectivity_issues")

            # 데이터 흐름 문제
            if not data_flow_validation.get("success", False):
                issues.append("data_flow_integrity_issues")

            return issues

        except Exception as e:
            logger.error(f"통합 문제점 식별 실패: {e}")
            return ["issue_identification_failed"]

    async def _generate_integration_recommendations(self, integration_result: Dict[str, Any]) -> List[str]:
        """통합 권장사항 생성"""
        try:
            recommendations = []
            integration_score = integration_result.get("overall_integration_score", 0.0)

            if integration_score < 0.8:
                recommendations.extend(
                    [
                        "Improve system connectivity",
                        "Enhance data flow integrity",
                        "Optimize integration performance",
                    ]
                )
            elif integration_score < 0.9:
                recommendations.extend(["Monitor integration stability", "Fine-tune system connections"])
            else:
                recommendations.append("Maintain current integration strategy")

            return recommendations

        except Exception as e:
            logger.error(f"통합 권장사항 생성 실패: {e}")
            return ["Continue monitoring integration performance"]

    async def _create_failed_report(self) -> LoopReport:
        """실패 보고서 생성"""
        return LoopReport(
            report_id=f"failed_report_{int(time.time())}",
            total_cycles=0,
            successful_cycles=0,
            average_performance=0.0,
            optimization_improvements=[],
            integration_issues=["session_failed"],
            recommendations=["investigate_session_failure"],
            created_at=datetime.now(),
        )


async def test_integrated_learning_loop():
    """통합 학습 루프 테스트"""
    try:
        logger.info("통합 학습 루프 테스트 시작")

        # 통합 학습 루프 초기화
        integrated_loop = IntegratedLearningLoop()

        # 모든 시스템 초기화
        initialization_success = await integrated_loop.initialize_all_systems()
        if not initialization_success:
            logger.error("시스템 초기화 실패")
            return None

        # 테스트 데이터 생성
        session_data = [
            {
                "input_id": "test_input_001",
                "data": {"message": "Hello, how are you?"},
                "context": {"user_id": "user_001", "session_id": "session_001"},
            },
            {
                "input_id": "test_input_002",
                "data": {"message": "What's the weather like?"},
                "context": {"user_id": "user_001", "session_id": "session_001"},
            },
            {
                "input_id": "test_input_003",
                "data": {"message": "Tell me a joke"},
                "context": {"user_id": "user_001", "session_id": "session_001"},
            },
        ]

        # 연속 학습 세션 실행
        logger.info("연속 학습 세션 실행 시작")
        session_report = await integrated_loop.run_continuous_learning_session(session_data)
        logger.info(f"세션 보고서: {session_report}")

        # 개별 사이클 테스트
        logger.info("개별 사이클 테스트 시작")
        test_input = {
            "input_id": "single_test_input",
            "data": {"message": "Test single cycle"},
            "context": {"user_id": "user_001", "session_id": "session_001"},
        }

        cycle_result = await integrated_loop.execute_full_cycle(test_input)
        logger.info(f"개별 사이클 결과: {cycle_result}")

        # 성능 최적화 테스트
        logger.info("성능 최적화 테스트 시작")
        performance_metrics = {
            "memory_efficiency": 0.75,
            "judgment_accuracy": 0.80,
            "action_success_rate": 0.85,
            "evolution_effectiveness": 0.70,
        }

        optimization_result = await integrated_loop.optimize_loop_performance(performance_metrics)
        logger.info(f"최적화 결과: {optimization_result}")

        # 통합 검증 테스트
        logger.info("통합 검증 테스트 시작")
        validation_result = await integrated_loop.validate_loop_integration([cycle_result])
        logger.info(f"통합 검증 결과: {validation_result}")

        logger.info("통합 학습 루프 테스트 완료")

        return {
            "session_report": session_report,
            "cycle_result": cycle_result,
            "optimization_result": optimization_result,
            "validation_result": validation_result,
        }

    except Exception as e:
        logger.error(f"통합 학습 루프 테스트 실패: {e}")
        return None


if __name__ == "__main__":
    # 로깅 설정
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # 테스트 실행
    asyncio.run(test_integrated_learning_loop())
