#!/usr/bin/env python3
"""
DuRiCore Phase 5 - 통합 학습 시스템
Memory → Judgment → Action → Evolution 전체 루프 통합 시스템
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# 기존 시스템들 import (실제 구현에서는 각 파일에서 import)
# from enhanced_memory_system import EnhancedMemorySystem
# from judgment_system import JudgmentSystem
# from action_system import ActionSystem
# from behavior_trace import BehaviorTracer, TraceType, TraceStatus


class LearningCycleStatus(Enum):
    """학습 사이클 상태 열거형"""

    INITIALIZED = "initialized"
    MEMORY_ACCESSED = "memory_accessed"
    JUDGMENT_COMPLETED = "judgment_completed"
    ACTION_EXECUTED = "action_executed"
    EVOLUTION_UPDATED = "evolution_updated"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class LearningCycle:
    """학습 사이클"""

    cycle_id: str
    status: LearningCycleStatus
    input_data: Dict[str, Any]
    memory_result: Optional[Dict[str, Any]]
    judgment_result: Optional[Dict[str, Any]]
    action_result: Optional[Dict[str, Any]]
    evolution_result: Optional[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    created_at: datetime
    completed_at: Optional[datetime]


class IntegratedLearningSystem:
    """통합 학습 시스템"""

    def __init__(self):
        # 기존 시스템들 초기화 (실제 구현에서는 각 시스템 인스턴스 생성)
        # self.memory_system = EnhancedMemorySystem()
        # self.judgment_system = JudgmentSystem()
        # self.action_system = ActionSystem()
        # self.behavior_tracer = BehaviorTracer()

        # 통합 설정
        self.enable_tracing = True
        self.enable_evolution = True
        self.performance_threshold = 0.8

        # 사이클 관리
        self.active_cycles = {}
        self.completed_cycles = []
        self.performance_history = []

        logger.info("통합 학습 시스템 초기화 완료")

    async def execute_learning_cycle(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> LearningCycle:
        """학습 사이클 실행"""
        try:
            # 사이클 시작
            cycle_id = f"cycle_{int(time.time())}"
            cycle = LearningCycle(
                cycle_id=cycle_id,
                status=LearningCycleStatus.INITIALIZED,
                input_data=input_data,
                memory_result=None,
                judgment_result=None,
                action_result=None,
                evolution_result=None,
                performance_metrics={},
                created_at=datetime.now(),
                completed_at=None,
            )

            self.active_cycles[cycle_id] = cycle

            # 1. 메모리 접근
            await self._execute_memory_phase(cycle, input_data, context)

            # 2. 판단 수행
            await self._execute_judgment_phase(cycle, input_data, context)

            # 3. 행동 실행
            await self._execute_action_phase(cycle, input_data, context)

            # 4. 진화 업데이트 (선택적)
            if self.enable_evolution:
                await self._execute_evolution_phase(cycle, input_data, context)

            # 사이클 완료
            cycle.status = LearningCycleStatus.COMPLETED
            cycle.completed_at = datetime.now()

            # 성능 메트릭 계산
            cycle.performance_metrics = await self._calculate_performance_metrics(cycle)

            # 완료된 사이클 저장
            self.completed_cycles.append(cycle)
            del self.active_cycles[cycle_id]

            # 성능 히스토리 업데이트
            self.performance_history.append(
                {
                    "cycle_id": cycle_id,
                    "timestamp": cycle.created_at,
                    "success": cycle.status == LearningCycleStatus.COMPLETED,
                    "metrics": cycle.performance_metrics,
                }
            )

            logger.info(f"학습 사이클 완료: {cycle_id}")
            return cycle

        except Exception as e:
            logger.error(f"학습 사이클 실행 실패: {e}")
            if cycle_id in self.active_cycles:
                cycle = self.active_cycles[cycle_id]
                cycle.status = LearningCycleStatus.FAILED
                cycle.completed_at = datetime.now()
            raise

    async def _execute_memory_phase(
        self, cycle: LearningCycle, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> None:
        """메모리 단계 실행"""
        try:
            cycle.status = LearningCycleStatus.MEMORY_ACCESSED

            # 실제 구현에서는 EnhancedMemorySystem 사용
            # memory_result = await self.memory_system.retrieve_memory(input_data, context)

            # 시뮬레이션된 메모리 결과
            memory_result = {
                "memory_id": f"mem_{cycle.cycle_id}",
                "retrieved_memories": [
                    {
                        "id": "mem_001",
                        "content": "긴급 상황 대응 방법",
                        "type": "experience",
                        "importance": 0.8,
                        "associations": ["emergency", "response", "system_error"],
                    }
                ],
                "relevance_score": 0.85,
                "access_time": 0.1,
            }

            cycle.memory_result = memory_result
            logger.info(f"메모리 단계 완료: {cycle.cycle_id}")

        except Exception as e:
            logger.error(f"메모리 단계 실패: {e}")
            raise

    async def _execute_judgment_phase(
        self, cycle: LearningCycle, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> None:
        """판단 단계 실행"""
        try:
            cycle.status = LearningCycleStatus.JUDGMENT_COMPLETED

            # 실제 구현에서는 JudgmentSystem 사용
            # judgment_result = await self.judgment_system.analyze_situation(input_data, context)

            # 시뮬레이션된 판단 결과
            judgment_result = {
                "judgment_id": f"judg_{cycle.cycle_id}",
                "situation_type": "emergency",
                "decision": "immediate_response",
                "confidence": 0.85,
                "reasoning": "긴급 상황이므로 즉시 대응 필요",
                "alternatives": ["wait_and_observe", "escalate"],
                "risk_assessment": {"time_risk": 0.3, "resource_risk": 0.2},
                "ethical_score": 0.7,
                "analysis_time": 0.2,
            }

            cycle.judgment_result = judgment_result
            logger.info(f"판단 단계 완료: {cycle.cycle_id}")

        except Exception as e:
            logger.error(f"판단 단계 실패: {e}")
            raise

    async def _execute_action_phase(
        self, cycle: LearningCycle, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> None:
        """행동 단계 실행"""
        try:
            cycle.status = LearningCycleStatus.ACTION_EXECUTED

            # 실제 구현에서는 ActionSystem 사용
            # action_result = await self.action_system.execute_action(cycle.judgment_result)

            # 시뮬레이션된 행동 결과
            action_result = {
                "action_id": f"act_{cycle.cycle_id}",
                "action_type": "immediate",
                "behavior_type": "response",
                "strategy": "urgent",
                "priority": 0.9,
                "success": True,
                "effectiveness_score": 0.85,
                "efficiency_score": 0.8,
                "learning_points": [
                    "긴급 상황 대응 패턴 학습",
                    "빠른 응답의 중요성 확인",
                ],
                "execution_time": 0.3,
            }

            cycle.action_result = action_result
            logger.info(f"행동 단계 완료: {cycle.cycle_id}")

        except Exception as e:
            logger.error(f"행동 단계 실패: {e}")
            raise

    async def _execute_evolution_phase(
        self, cycle: LearningCycle, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> None:
        """진화 단계 실행"""
        try:
            cycle.status = LearningCycleStatus.EVOLUTION_UPDATED

            # 성능 평가
            performance_score = await self._evaluate_cycle_performance(cycle)

            # 진화 결정
            if performance_score < self.performance_threshold:
                evolution_result = {
                    "evolution_id": f"evol_{cycle.cycle_id}",
                    "evolution_type": "performance_improvement",
                    "improvement_score": 0.1,
                    "changes_applied": [
                        "판단 정확도 향상",
                        "행동 효율성 개선",
                        "메모리 접근 최적화",
                    ],
                    "performance_impact": {
                        "judgment_accuracy": 0.05,
                        "action_efficiency": 0.03,
                        "memory_access_speed": 0.02,
                    },
                    "stability_score": 0.9,
                }
            else:
                evolution_result = {
                    "evolution_id": f"evol_{cycle.cycle_id}",
                    "evolution_type": "maintenance",
                    "improvement_score": 0.0,
                    "changes_applied": [],
                    "performance_impact": {},
                    "stability_score": 1.0,
                }

            cycle.evolution_result = evolution_result
            logger.info(f"진화 단계 완료: {cycle.cycle_id}")

        except Exception as e:
            logger.error(f"진화 단계 실패: {e}")
            raise

    async def _evaluate_cycle_performance(self, cycle: LearningCycle) -> float:
        """사이클 성능 평가"""
        try:
            if not cycle.action_result:
                return 0.0

            # 성능 점수 계산
            effectiveness = cycle.action_result.get("effectiveness_score", 0.0)
            efficiency = cycle.action_result.get("efficiency_score", 0.0)
            success = cycle.action_result.get("success", False)

            # 가중 평균
            performance_score = (
                effectiveness * 0.4 + efficiency * 0.3 + (1.0 if success else 0.0) * 0.3
            )

            return performance_score

        except Exception as e:
            logger.error(f"성능 평가 실패: {e}")
            return 0.0

    async def _calculate_performance_metrics(self, cycle: LearningCycle) -> Dict[str, float]:
        """성능 메트릭 계산"""
        try:
            metrics = {}

            # 메모리 성능
            if cycle.memory_result:
                metrics["memory_access_time"] = cycle.memory_result.get("access_time", 0.0)
                metrics["memory_relevance"] = cycle.memory_result.get("relevance_score", 0.0)

            # 판단 성능
            if cycle.judgment_result:
                metrics["judgment_time"] = cycle.judgment_result.get("analysis_time", 0.0)
                metrics["judgment_confidence"] = cycle.judgment_result.get("confidence", 0.0)
                metrics["judgment_ethical_score"] = cycle.judgment_result.get("ethical_score", 0.0)

            # 행동 성능
            if cycle.action_result:
                metrics["action_execution_time"] = cycle.action_result.get("execution_time", 0.0)
                metrics["action_effectiveness"] = cycle.action_result.get(
                    "effectiveness_score", 0.0
                )
                metrics["action_efficiency"] = cycle.action_result.get("efficiency_score", 0.0)
                metrics["action_success"] = (
                    1.0 if cycle.action_result.get("success", False) else 0.0
                )

            # 진화 성능
            if cycle.evolution_result:
                metrics["evolution_improvement"] = cycle.evolution_result.get(
                    "improvement_score", 0.0
                )
                metrics["evolution_stability"] = cycle.evolution_result.get("stability_score", 0.0)

            # 전체 성능
            if cycle.completed_at and cycle.created_at:
                metrics["total_cycle_time"] = (
                    cycle.completed_at - cycle.created_at
                ).total_seconds()

            return metrics

        except Exception as e:
            logger.error(f"성능 메트릭 계산 실패: {e}")
            return {}

    async def analyze_system_performance(self) -> Dict[str, Any]:
        """시스템 성능 분석"""
        try:
            if not self.completed_cycles:
                return {"message": "분석할 완료된 사이클이 없습니다."}

            # 기본 통계
            total_cycles = len(self.completed_cycles)
            successful_cycles = sum(
                1 for c in self.completed_cycles if c.status == LearningCycleStatus.COMPLETED
            )
            success_rate = successful_cycles / total_cycles if total_cycles > 0 else 0.0

            # 평균 성능 메트릭
            avg_metrics = {}
            if self.completed_cycles:
                metric_keys = self.completed_cycles[0].performance_metrics.keys()
                for key in metric_keys:
                    values = [c.performance_metrics.get(key, 0.0) for c in self.completed_cycles]
                    avg_metrics[key] = sum(values) / len(values)

            # 성능 트렌드 분석
            recent_cycles = (
                self.completed_cycles[-10:]
                if len(self.completed_cycles) >= 10
                else self.completed_cycles
            )
            recent_success_rate = (
                sum(1 for c in recent_cycles if c.status == LearningCycleStatus.COMPLETED)
                / len(recent_cycles)
                if recent_cycles
                else 0.0
            )

            return {
                "total_cycles": total_cycles,
                "success_rate": success_rate,
                "recent_success_rate": recent_success_rate,
                "average_metrics": avg_metrics,
                "performance_trend": (
                    "improving"
                    if recent_success_rate > success_rate
                    else ("stable" if recent_success_rate == success_rate else "declining")
                ),
            }

        except Exception as e:
            logger.error(f"시스템 성능 분석 실패: {e}")
            raise

    async def get_evolution_recommendations(self) -> List[Dict[str, Any]]:
        """진화 권장사항 생성"""
        try:
            recommendations = []

            # 성능 분석
            performance = await self.analyze_system_performance()

            # 성공률 기반 권장사항
            if performance.get("success_rate", 0.0) < 0.8:
                recommendations.append(
                    {
                        "type": "success_rate_improvement",
                        "priority": "high",
                        "description": "전체 성공률 향상을 위한 시스템 개선 필요",
                        "target_metric": "success_rate",
                        "current_value": performance.get("success_rate", 0.0),
                        "target_value": 0.8,
                    }
                )

            # 응답 시간 기반 권장사항
            avg_cycle_time = performance.get("average_metrics", {}).get("total_cycle_time", 0.0)
            if avg_cycle_time > 1.0:
                recommendations.append(
                    {
                        "type": "response_time_optimization",
                        "priority": "medium",
                        "description": "사이클 시간 단축을 위한 시스템 최적화 필요",
                        "target_metric": "total_cycle_time",
                        "current_value": avg_cycle_time,
                        "target_value": 1.0,
                    }
                )

            # 효과성 기반 권장사항
            avg_effectiveness = performance.get("average_metrics", {}).get(
                "action_effectiveness", 0.0
            )
            if avg_effectiveness < 0.8:
                recommendations.append(
                    {
                        "type": "effectiveness_improvement",
                        "priority": "high",
                        "description": "행동 효과성 향상을 위한 학습 패턴 개선 필요",
                        "target_metric": "action_effectiveness",
                        "current_value": avg_effectiveness,
                        "target_value": 0.8,
                    }
                )

            return recommendations

        except Exception as e:
            logger.error(f"진화 권장사항 생성 실패: {e}")
            raise


async def test_integrated_learning_system():
    """통합 학습 시스템 테스트"""
    print("=== DuRiCore Phase 5 - 통합 학습 시스템 테스트 ===")

    # 통합 학습 시스템 초기화
    learning_system = IntegratedLearningSystem()

    # 테스트 시나리오들
    test_scenarios = [
        {
            "name": "긴급 상황 대응",
            "input_data": {
                "situation": "시스템 오류 발생",
                "urgency": "high",
                "context": "프로덕션 환경",
            },
            "context": {
                "available_resources": ["cpu", "memory"],
                "time_constraints": 60,
                "risk_tolerance": "low",
            },
        },
        {
            "name": "일반 학습 상황",
            "input_data": {
                "situation": "새로운 패턴 학습",
                "urgency": "low",
                "context": "개발 환경",
            },
            "context": {
                "available_resources": ["cpu", "memory", "storage"],
                "time_constraints": 300,
                "risk_tolerance": "medium",
            },
        },
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['name']} 테스트")
        print(f"입력: {scenario['input_data']}")

        # 학습 사이클 실행
        cycle = await learning_system.execute_learning_cycle(
            scenario["input_data"], scenario["context"]
        )

        print(f"사이클 결과:")
        print(f"- 사이클 ID: {cycle.cycle_id}")
        print(f"- 상태: {cycle.status.value}")
        print(f"- 성공 여부: {cycle.status == LearningCycleStatus.COMPLETED}")
        print(f"- 총 소요시간: {cycle.performance_metrics.get('total_cycle_time', 0.0):.3f}초")
        print(
            f"- 메모리 접근 시간: {cycle.performance_metrics.get('memory_access_time', 0.0):.3f}초"
        )
        print(f"- 판단 시간: {cycle.performance_metrics.get('judgment_time', 0.0):.3f}초")
        print(
            f"- 행동 실행 시간: {cycle.performance_metrics.get('action_execution_time', 0.0):.3f}초"
        )
        print(f"- 행동 효과성: {cycle.performance_metrics.get('action_effectiveness', 0.0):.3f}")
        print(f"- 행동 효율성: {cycle.performance_metrics.get('action_efficiency', 0.0):.3f}")

        if cycle.evolution_result:
            print(f"- 진화 개선 점수: {cycle.evolution_result.get('improvement_score', 0.0):.3f}")

    # 시스템 성능 분석
    print("\n시스템 성능 분석:")
    performance = await learning_system.analyze_system_performance()
    print(f"- 총 사이클: {performance.get('total_cycles', 0)}")
    print(f"- 성공률: {performance.get('success_rate', 0.0):.3f}")
    print(f"- 최근 성공률: {performance.get('recent_success_rate', 0.0):.3f}")
    print(f"- 성능 트렌드: {performance.get('performance_trend', 'unknown')}")

    # 진화 권장사항
    print("\n진화 권장사항:")
    recommendations = await learning_system.get_evolution_recommendations()
    for rec in recommendations:
        print(f"- {rec['type']}: {rec['description']}")
        print(f"  우선순위: {rec['priority']}")
        print(f"  현재값: {rec['current_value']:.3f} -> 목표값: {rec['target_value']:.3f}")

    print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_integrated_learning_system())
