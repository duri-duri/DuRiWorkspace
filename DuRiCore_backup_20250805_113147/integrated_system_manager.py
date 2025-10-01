#!/usr/bin/env python3
"""
DuRiCore Phase 5.5.2 - 통합 시스템 매니저
기존 시스템들을 통합하여 고급 기능을 제공하는 시스템
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from action_system import ActionSystem
from enhanced_memory_system import EnhancedMemorySystem
from evolution_system import EvolutionSystem
from feedback_system import FeedbackSystem

# 기존 시스템들 import
from judgment_system import JudgmentSystem
from performance_monitoring_system import PerformanceMonitoringSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationResult:
    """통합 결과 데이터 클래스"""

    system_name: str
    status: str
    performance_score: float
    integration_time: float
    error_count: int
    success_rate: float
    created_at: str


class IntegratedSystemManager:
    """통합 시스템 매니저"""

    def __init__(self):
        """초기화"""
        self.judgment_system = JudgmentSystem()
        self.action_system = ActionSystem()
        self.feedback_system = FeedbackSystem()
        self.memory_system = EnhancedMemorySystem()
        self.performance_system = PerformanceMonitoringSystem()
        self.evolution_system = EvolutionSystem()

        self.integration_results = []
        self.system_status = {}
        self.performance_metrics = {}

        logger.info("통합 시스템 매니저 초기화 완료")

    async def initialize_all_systems(self):
        """모든 시스템 초기화"""
        try:
            # 각 시스템은 __init__에서 이미 초기화됨
            # 추가 초기화가 필요한 경우 여기서 처리
            logger.info("모든 시스템 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            return False

    async def run_integrated_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """통합 사이클 실행"""
        start_time = time.time()

        try:
            # 1. 메모리에서 관련 정보 검색
            memory_context = await self._get_memory_context(context)

            # 2. 성능 모니터링 시작
            system_metrics = {
                "cpu_usage": 0.3,
                "memory_usage": 0.4,
                "response_time": 0.1,
                "throughput": 100.0,
                "error_rate": 0.01,
                "availability": 0.999,
            }
            performance_data = (
                await self.performance_system.monitor_real_time_performance(
                    system_metrics
                )
            )

            # 3. 판단 시스템 실행 (메모리 정보 활용)
            judgment_result = await self.judgment_system.judge(
                {**context, "memory_context": memory_context}
            )

            # 4. 행동 시스템 실행
            action_result = await self.action_system.act(judgment_result)

            # 5. 피드백 시스템 실행
            feedback_result = await self.feedback_system.feedback(action_result)

            # 6. 결과를 메모리에 저장
            await self._save_to_memory(judgment_result, action_result, feedback_result)

            # 8. 진화 시스템을 통한 개선
            learning_cycles = [
                {
                    "judgment": judgment_result,
                    "action": action_result,
                    "feedback": feedback_result,
                    "performance": performance_data,
                }
            ]
            evolution_result = await self.evolution_system.evolve_system(
                learning_cycles
            )

            cycle_time = time.time() - start_time

            # 통합 결과 생성
            integrated_result = {
                "cycle_id": f"cycle_{int(time.time() * 1000)}",
                "timestamp": datetime.now().isoformat(),
                "duration": cycle_time,
                "judgment": judgment_result,
                "action": action_result,
                "feedback": feedback_result,
                "memory_context": memory_context,
                "performance_data": performance_data,
                "evolution_result": evolution_result,
                "overall_score": self._calculate_overall_score(
                    judgment_result, action_result, feedback_result, performance_data
                ),
            }

            logger.info(f"통합 사이클 완료: {cycle_time:.3f}초")
            return integrated_result

        except Exception as e:
            logger.error(f"통합 사이클 실행 실패: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _get_memory_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에서 관련 컨텍스트 검색"""
        try:
            # 상황에 관련된 메모리 검색
            relevant_memories = await self.memory_system.search_memories(
                context.get("situation", ""), limit=5
            )

            # 연관 메모리 검색
            associated_memories = []
            if relevant_memories:
                associated_memories = await self.memory_system.get_associated_memories(
                    relevant_memories[0]["id"]
                )

            return {
                "relevant_memories": relevant_memories,
                "associated_memories": associated_memories,
                "memory_count": len(relevant_memories) + len(associated_memories),
            }
        except Exception as e:
            logger.warning(f"메모리 컨텍스트 검색 실패: {e}")
            return {
                "relevant_memories": [],
                "associated_memories": [],
                "memory_count": 0,
            }

    async def _save_to_memory(
        self, judgment_result: Dict, action_result: Dict, feedback_result: Dict
    ):
        """결과를 메모리에 저장"""
        try:
            # 판단 결과 저장
            await self.memory_system.store_memory(
                content=f"판단 결과: {judgment_result.get('decision', 'unknown')}",
                context={
                    "type": "judgment",
                    "decision": judgment_result.get("decision", "unknown"),
                },
                importance=0.7,
            )

            # 행동 결과 저장
            await self.memory_system.store_memory(
                content=f"행동 결과: {action_result.get('action', 'unknown')}",
                context={
                    "type": "action",
                    "action": action_result.get("action", "unknown"),
                },
                importance=0.8,
            )

            # 피드백 결과 저장
            await self.memory_system.store_memory(
                content=f"피드백 결과: {feedback_result.get('feedback', 'unknown')}",
                context={
                    "type": "feedback",
                    "feedback": feedback_result.get("feedback", "unknown"),
                },
                importance=0.6,
            )

            logger.info("결과를 메모리에 저장 완료")
        except Exception as e:
            logger.warning(f"메모리 저장 실패: {e}")

    def _calculate_overall_score(
        self, judgment: Dict, action: Dict, feedback: Dict, performance: List
    ) -> float:
        """전체 점수 계산"""
        try:
            # 각 시스템의 점수 추출
            judgment_score = judgment.get("confidence", 0.0)
            action_score = action.get("effectiveness_score", 0.0)
            feedback_score = feedback.get("evaluation_score", 0.0)

            # 성능 데이터에서 평균 점수 계산
            performance_score = 0.0
            if performance and len(performance) > 0:
                performance_values = [
                    p.value for p in performance if hasattr(p, "value")
                ]
                if performance_values:
                    performance_score = sum(performance_values) / len(
                        performance_values
                    )

            # 가중 평균 계산
            overall_score = (
                judgment_score * 0.3
                + action_score * 0.3
                + feedback_score * 0.2
                + performance_score * 0.2
            )

            return round(overall_score, 3)
        except Exception as e:
            logger.warning(f"전체 점수 계산 실패: {e}")
            return 0.0

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "systems": {
                    "judgment": "active",
                    "action": "active",
                    "feedback": "active",
                    "memory": "active",
                    "performance": "active",
                    "evolution": "active",
                },
                "integration_results": len(self.integration_results),
                "performance_metrics": self.performance_metrics,
            }
            return status
        except Exception as e:
            logger.error(f"시스템 상태 조회 실패: {e}")
            return {"error": str(e)}

    async def run_integration_test(self) -> Dict[str, Any]:
        """통합 테스트 실행"""
        logger.info("통합 시스템 테스트 시작")

        test_context = {
            "situation": "통합 시스템 테스트 상황",
            "priority": "high",
            "complexity": "medium",
        }

        # 통합 사이클 실행
        result = await self.run_integrated_cycle(test_context)

        # 테스트 결과 분석
        test_result = {
            "test_id": f"integration_test_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "success": "error" not in result,
            "duration": result.get("duration", 0),
            "overall_score": result.get("overall_score", 0),
            "details": result,
        }

        logger.info(
            f"통합 테스트 완료: 성공={test_result['success']}, 점수={test_result['overall_score']}"
        )
        return test_result


async def main():
    """메인 함수"""
    logger.info("🚀 DuRiCore Phase 5.5.2 통합 시스템 매니저 시작")

    # 통합 시스템 매니저 생성
    manager = IntegratedSystemManager()

    # 시스템 초기화
    if not await manager.initialize_all_systems():
        logger.error("시스템 초기화 실패")
        return

    # 통합 테스트 실행
    test_result = await manager.run_integration_test()

    # 결과 출력
    print("\n=== 통합 시스템 테스트 결과 ===")
    print(f"테스트 ID: {test_result['test_id']}")
    print(f"성공 여부: {test_result['success']}")
    print(f"실행 시간: {test_result['duration']:.3f}초")
    print(f"전체 점수: {test_result['overall_score']}")

    if test_result["success"]:
        print("✅ 통합 시스템 테스트 성공!")
    else:
        print("❌ 통합 시스템 테스트 실패")

    # 시스템 상태 출력
    status = await manager.get_system_status()
    print(f"\n시스템 상태: {status['systems']}")


if __name__ == "__main__":
    asyncio.run(main())
