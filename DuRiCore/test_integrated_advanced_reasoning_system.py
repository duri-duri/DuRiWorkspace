#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 14 - 통합 고급 추론 시스템 테스트

Day 14의 모든 고급 추론 시스템들을 통합 테스트
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, List

# 테스트 대상 시스템 import
try:
    from integrated_advanced_reasoning_system import (
        AdvancedReasoningLevel, Day14PerformanceMetrics,
        IntegratedAdvancedReasoningSystem, ReasoningContext,
        SystemIntegrationStatus)
except ImportError as e:
    logging.error(f"시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AdvancedReasoningSystemTester:
    """고급 추론 시스템 테스터"""

    def __init__(self):
        self.system = IntegratedAdvancedReasoningSystem()
        self.test_results = []

    async def run_comprehensive_test(self) -> Dict[str, Any]:
        """종합 테스트 실행"""
        logger.info("=== Day 14 통합 고급 추론 시스템 종합 테스트 시작 ===")

        start_time = time.time()

        # 1. 기본 기능 테스트
        basic_test_result = await self._test_basic_functionality()

        # 2. 적응적 추론 테스트
        adaptive_reasoning_result = await self._test_adaptive_reasoning()

        # 3. 일관성 강화 테스트
        consistency_enhancement_result = await self._test_consistency_enhancement()

        # 4. 통합 성공도 개선 테스트
        integration_success_result = await self._test_integration_success()

        # 5. 효율성 최적화 테스트
        efficiency_optimization_result = await self._test_efficiency_optimization()

        # 6. 통합 시스템 테스트
        integrated_system_result = await self._test_integrated_system()

        # 7. 성능 테스트
        performance_result = await self._test_performance()

        # 8. Day 14 목표 달성도 테스트
        day14_goals_result = await self._test_day14_goals()

        # 9. 결과 종합
        total_time = time.time() - start_time

        comprehensive_result = {
            "test_id": f"day14_comprehensive_test_{int(time.time())}",
            "test_time": datetime.now().isoformat(),
            "total_execution_time": total_time,
            "test_results": {
                "basic_functionality": basic_test_result,
                "adaptive_reasoning": adaptive_reasoning_result,
                "consistency_enhancement": consistency_enhancement_result,
                "integration_success": integration_success_result,
                "efficiency_optimization": efficiency_optimization_result,
                "integrated_system": integrated_system_result,
                "performance": performance_result,
                "day14_goals": day14_goals_result,
            },
            "overall_status": "completed",
            "success_rate": self._calculate_success_rate(
                [
                    basic_test_result,
                    adaptive_reasoning_result,
                    consistency_enhancement_result,
                    integration_success_result,
                    efficiency_optimization_result,
                    integrated_system_result,
                    performance_result,
                    day14_goals_result,
                ]
            ),
        }

        self.test_results.append(comprehensive_result)

        logger.info(
            f"=== Day 14 통합 고급 추론 시스템 종합 테스트 완료 (총 {total_time:.3f}초) ==="
        )
        return comprehensive_result

    async def _test_basic_functionality(self) -> Dict[str, Any]:
        """기본 기능 테스트"""
        logger.info("기본 기능 테스트 시작")

        try:
            # 시스템 초기화 테스트
            system_status = await self.system.get_system_status()

            # 기본 입력 데이터 생성
            test_input = {
                "complexity": 0.6,
                "urgency": 0.7,
                "quality_requirement": 0.8,
                "time_constraint": 0.5,
                "resource_availability": 0.8,
                "reasoning_steps": [
                    {"id": "step1", "type": "analysis", "content": "문제 분석"},
                    {"id": "step2", "type": "synthesis", "content": "해결책 종합"},
                ],
                "knowledge_elements": [
                    {
                        "id": "knowledge1",
                        "type": "fact",
                        "content": "기본 사실",
                        "confidence": 0.9,
                    },
                    {
                        "id": "knowledge2",
                        "type": "inference",
                        "content": "추론 결과",
                        "confidence": 0.8,
                    },
                ],
                "knowledge_sources": [
                    {"id": "source1", "type": "database", "reliability": 0.9},
                    {"id": "source2", "type": "expert", "reliability": 0.8},
                ],
            }

            # 기본 추론 처리 테스트
            reasoning_session = await self.system.process_advanced_reasoning(
                ReasoningContext.PROBLEM_SOLVING, test_input
            )

            result = {
                "status": "success",
                "system_status": system_status,
                "reasoning_session_id": reasoning_session.session_id,
                "reasoning_level": reasoning_session.reasoning_level.value,
                "system_status_value": reasoning_session.system_status.value,
                "performance_metrics": reasoning_session.performance_metrics,
            }

            logger.info("기본 기능 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"기본 기능 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_adaptive_reasoning(self) -> Dict[str, Any]:
        """적응적 추론 테스트"""
        logger.info("적응적 추론 테스트 시작")

        try:
            # 다양한 컨텍스트에서의 적응적 추론 테스트
            contexts = [
                ReasoningContext.PROBLEM_SOLVING,
                ReasoningContext.DECISION_MAKING,
                ReasoningContext.LEARNING,
                ReasoningContext.CREATION,
            ]

            adaptive_results = []
            for context in contexts:
                test_input = {
                    "complexity": 0.7,
                    "urgency": 0.6,
                    "context_type": context.value,
                }

                reasoning_session = await self.system.process_advanced_reasoning(
                    context, test_input
                )
                adaptive_results.append(
                    {
                        "context": context.value,
                        "reasoning_type": reasoning_session.reasoning_results.get(
                            "adaptive_reasoning", {}
                        ).get("reasoning_type", "unknown"),
                        "confidence_score": reasoning_session.reasoning_results.get(
                            "adaptive_reasoning", {}
                        ).get("confidence_score", 0.0),
                        "adaptation_score": reasoning_session.reasoning_results.get(
                            "adaptive_reasoning", {}
                        ).get("adaptation_score", 0.0),
                    }
                )

            result = {
                "status": "success",
                "adaptive_results": adaptive_results,
                "average_confidence": sum(
                    r["confidence_score"] for r in adaptive_results
                )
                / len(adaptive_results),
                "average_adaptation": sum(
                    r["adaptation_score"] for r in adaptive_results
                )
                / len(adaptive_results),
            }

            logger.info("적응적 추론 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"적응적 추론 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_consistency_enhancement(self) -> Dict[str, Any]:
        """일관성 강화 테스트"""
        logger.info("일관성 강화 테스트 시작")

        try:
            # 일관성 강화 테스트 데이터
            test_input = {
                "reasoning_steps": [
                    {"id": "step1", "type": "premise", "content": "전제 1"},
                    {"id": "step2", "type": "conclusion", "content": "결론 1"},
                    {"id": "step3", "type": "premise", "content": "전제 2"},
                    {"id": "step4", "type": "conclusion", "content": "결론 2"},
                ],
                "knowledge_elements": [
                    {"id": "elem1", "type": "fact", "value": "A", "confidence": 0.9},
                    {"id": "elem2", "type": "fact", "value": "B", "confidence": 0.8},
                    {
                        "id": "elem3",
                        "type": "inference",
                        "value": "C",
                        "confidence": 0.7,
                    },
                ],
                "knowledge_sources": [
                    {"id": "source1", "type": "database", "reliability": 0.9},
                    {"id": "source2", "type": "expert", "reliability": 0.8},
                ],
            }

            reasoning_session = await self.system.process_advanced_reasoning(
                ReasoningContext.ANALYSIS, test_input
            )

            consistency_result = reasoning_session.reasoning_results.get(
                "consistency_enhancement", {}
            )

            result = {
                "status": "success",
                "original_consistency": consistency_result.get(
                    "original_consistency", 0.0
                ),
                "enhanced_consistency": consistency_result.get(
                    "enhanced_consistency", 0.0
                ),
                "improvement_score": consistency_result.get("improvement_score", 0.0),
                "enhancement_methods": consistency_result.get(
                    "enhancement_methods", []
                ),
            }

            logger.info("일관성 강화 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"일관성 강화 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_integration_success(self) -> Dict[str, Any]:
        """통합 성공도 개선 테스트"""
        logger.info("통합 성공도 개선 테스트 시작")

        try:
            # 통합 성공도 테스트 데이터
            test_input = {
                "knowledge_elements": [
                    {
                        "id": "elem1",
                        "type": "fact",
                        "value": "X",
                        "importance": 0.9,
                        "confidence": 0.8,
                    },
                    {
                        "id": "elem2",
                        "type": "fact",
                        "value": "Y",
                        "importance": 0.7,
                        "confidence": 0.9,
                    },
                    {
                        "id": "elem3",
                        "type": "inference",
                        "value": "Z",
                        "importance": 0.8,
                        "confidence": 0.7,
                    },
                ]
            }

            reasoning_session = await self.system.process_advanced_reasoning(
                ReasoningContext.SYNTHESIS, test_input
            )

            integration_result = reasoning_session.reasoning_results.get(
                "integration_success", {}
            )

            result = {
                "status": "success",
                "improvement_score": integration_result.get("improvement_score", 0.0),
                "total_conflicts": integration_result.get("total_conflicts", 0),
                "resolved_conflicts": integration_result.get("resolved_conflicts", 0),
                "total_priorities": integration_result.get("total_priorities", 0),
            }

            logger.info("통합 성공도 개선 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"통합 성공도 개선 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_efficiency_optimization(self) -> Dict[str, Any]:
        """효율성 최적화 테스트"""
        logger.info("효율성 최적화 테스트 시작")

        try:
            # 효율성 최적화 테스트 데이터
            test_input = {
                "complexity": 0.6,
                "urgency": 0.7,
                "quality_requirement": 0.8,
                "time_constraint": 0.5,
                "resource_availability": 0.8,
                "requirements": {
                    "cpu_required": 50.0,
                    "memory_required": 1024.0,
                    "storage_required": 100.0,
                    "network_required": 100.0,
                    "time_required": 300.0,
                },
                "performance_data": {
                    "execution_time": 45.0,
                    "memory_usage": 800.0,
                    "cpu_usage": 0.6,
                    "throughput": 150.0,
                    "quality_score": 0.85,
                },
            }

            reasoning_session = await self.system.process_advanced_reasoning(
                ReasoningContext.EVALUATION, test_input
            )

            efficiency_result = reasoning_session.reasoning_results.get(
                "efficiency_optimization", {}
            )

            result = {
                "status": "success",
                "original_efficiency": efficiency_result.get(
                    "original_efficiency", 0.0
                ),
                "optimized_efficiency": efficiency_result.get(
                    "optimized_efficiency", 0.0
                ),
                "improvement_score": efficiency_result.get("improvement_score", 0.0),
                "strategy": efficiency_result.get("strategy", "unknown"),
            }

            logger.info("효율성 최적화 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"효율성 최적화 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_integrated_system(self) -> Dict[str, Any]:
        """통합 시스템 테스트"""
        logger.info("통합 시스템 테스트 시작")

        try:
            # 통합 시스템 테스트 데이터
            test_input = {
                "complexity": 0.8,
                "urgency": 0.9,
                "quality_requirement": 0.9,
                "time_constraint": 0.7,
                "resource_availability": 0.6,
                "reasoning_steps": [
                    {"id": "step1", "type": "analysis", "content": "복합 문제 분석"},
                    {"id": "step2", "type": "synthesis", "content": "통합 해결책"},
                    {"id": "step3", "type": "evaluation", "content": "해결책 평가"},
                ],
                "knowledge_elements": [
                    {
                        "id": "elem1",
                        "type": "fact",
                        "value": "A",
                        "importance": 0.9,
                        "confidence": 0.9,
                    },
                    {
                        "id": "elem2",
                        "type": "fact",
                        "value": "B",
                        "importance": 0.8,
                        "confidence": 0.8,
                    },
                    {
                        "id": "elem3",
                        "type": "inference",
                        "value": "C",
                        "importance": 0.7,
                        "confidence": 0.7,
                    },
                ],
                "knowledge_sources": [
                    {"id": "source1", "type": "database", "reliability": 0.9},
                    {"id": "source2", "type": "expert", "reliability": 0.8},
                    {"id": "source3", "type": "research", "reliability": 0.85},
                ],
                "requirements": {
                    "cpu_required": 80.0,
                    "memory_required": 2048.0,
                    "storage_required": 500.0,
                    "network_required": 200.0,
                    "time_required": 600.0,
                },
                "performance_data": {
                    "execution_time": 120.0,
                    "memory_usage": 1500.0,
                    "cpu_usage": 0.8,
                    "throughput": 200.0,
                    "quality_score": 0.9,
                },
            }

            reasoning_session = await self.system.process_advanced_reasoning(
                ReasoningContext.INTEGRATED, test_input
            )

            integration_result = reasoning_session.reasoning_results.get(
                "integration_result", {}
            )

            result = {
                "status": "success",
                "overall_score": integration_result.get("overall_score", 0.0),
                "adaptive_reasoning_score": integration_result.get(
                    "adaptive_reasoning_score", 0.0
                ),
                "consistency_enhancement_score": integration_result.get(
                    "consistency_enhancement_score", 0.0
                ),
                "integration_success_score": integration_result.get(
                    "integration_success_score", 0.0
                ),
                "efficiency_optimization_score": integration_result.get(
                    "efficiency_optimization_score", 0.0
                ),
            }

            logger.info("통합 시스템 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"통합 시스템 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_performance(self) -> Dict[str, Any]:
        """성능 테스트"""
        logger.info("성능 테스트 시작")

        try:
            # 성능 테스트 데이터
            test_input = {
                "complexity": 0.5,
                "urgency": 0.5,
                "quality_requirement": 0.5,
                "time_constraint": 0.5,
                "resource_availability": 0.5,
            }

            start_time = time.time()
            reasoning_session = await self.system.process_advanced_reasoning(
                ReasoningContext.PROBLEM_SOLVING, test_input
            )
            execution_time = time.time() - start_time

            performance_metrics = reasoning_session.performance_metrics

            result = {
                "status": "success",
                "execution_time": execution_time,
                "performance_metrics": performance_metrics,
                "system_status": reasoning_session.system_status.value,
            }

            logger.info("성능 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"성능 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    async def _test_day14_goals(self) -> Dict[str, Any]:
        """Day 14 목표 달성도 테스트"""
        logger.info("Day 14 목표 달성도 테스트 시작")

        try:
            # Day 14 성과 보고서 생성
            performance_report = await self.system.get_day14_performance_report()

            # Day 14 목표 달성도 평가
            goals_evaluation = await self.system.evaluate_day14_goals()

            result = {
                "status": "success",
                "performance_report": {
                    "consistency_score": performance_report.consistency_score,
                    "integration_success_score": performance_report.integration_success_score,
                    "efficiency_score": performance_report.efficiency_score,
                    "reasoning_adaptation_score": performance_report.reasoning_adaptation_score,
                    "overall_system_stability": performance_report.overall_system_stability,
                },
                "goals_evaluation": goals_evaluation,
            }

            logger.info("Day 14 목표 달성도 테스트 완료")
            return result

        except Exception as e:
            logger.error(f"Day 14 목표 달성도 테스트 실패: {e}")
            return {"status": "failed", "error": str(e)}

    def _calculate_success_rate(self, test_results: List[Dict[str, Any]]) -> float:
        """성공률 계산"""
        if not test_results:
            return 0.0

        successful_tests = sum(
            1 for result in test_results if result.get("status") == "success"
        )
        return successful_tests / len(test_results)

    async def save_test_results(self, filename: str = None):
        """테스트 결과 저장"""
        if filename is None:
            filename = f"test_results_integrated_advanced_reasoning_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    self.test_results, f, indent=2, ensure_ascii=False, default=str
                )

            logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")
        except Exception as e:
            logger.error(f"테스트 결과 저장 실패: {e}")


async def main():
    """메인 함수"""
    tester = AdvancedReasoningSystemTester()

    # 종합 테스트 실행
    comprehensive_result = await tester.run_comprehensive_test()

    # 결과 출력
    print("\n=== Day 14 통합 고급 추론 시스템 테스트 결과 ===")
    print(f"테스트 ID: {comprehensive_result['test_id']}")
    print(f"총 실행 시간: {comprehensive_result['total_execution_time']:.3f}초")
    print(f"전체 성공률: {comprehensive_result['success_rate']:.2%}")

    # 각 테스트 결과 출력
    for test_name, test_result in comprehensive_result["test_results"].items():
        status = test_result.get("status", "unknown")
        print(f"{test_name}: {status}")

    # Day 14 목표 달성도 출력
    day14_goals = comprehensive_result["test_results"]["day14_goals"]
    if day14_goals.get("status") == "success":
        performance_report = day14_goals["performance_report"]
        goals_evaluation = day14_goals["goals_evaluation"]

        print("\n=== Day 14 목표 달성도 ===")
        print(f"일관성 점수: {performance_report['consistency_score']:.2%} (목표: 60%)")
        print(
            f"통합 성공도: {performance_report['integration_success_score']:.2%} (목표: 60%)"
        )
        print(f"효율성: {performance_report['efficiency_score']:.2%} (목표: 80%)")
        print(
            f"추론 적응력: {performance_report['reasoning_adaptation_score']:.2%} (목표: 70%)"
        )
        print(
            f"전체 시스템 안정성: {performance_report['overall_system_stability']:.2%} (목표: 90%)"
        )

        print(f"\n전체 달성도: {goals_evaluation['total_achievement_rate']:.2%}")
        print(f"전체 상태: {goals_evaluation['overall_status']}")

    # 테스트 결과 저장
    await tester.save_test_results()

    print(f"\n테스트 완료! 결과가 JSON 파일로 저장되었습니다.")


if __name__ == "__main__":
    asyncio.run(main())
