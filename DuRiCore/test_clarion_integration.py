#!/usr/bin/env python3
"""
DuRiCore Phase 6.2.5 - CLARION 학습 시스템 통합 테스트
CLARION 학습 시스템이 통합 시스템 매니저에 제대로 통합되었는지 확인
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

from clarion_learning_system import CLARIONLearningSystem, LearningType, ReinforcementType

# 테스트 대상 시스템들
from integrated_system_manager import IntegratedSystemManager

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CLARIONIntegrationTest:
    """CLARION 학습 시스템 통합 테스트"""

    def __init__(self):
        """초기화"""
        self.integrated_manager = IntegratedSystemManager()
        self.clarion_system = CLARIONLearningSystem()
        self.test_results = []

    async def run_comprehensive_test(self):
        """종합 테스트 실행"""
        logger.info("=== CLARION 학습 시스템 통합 테스트 시작 ===")

        test_suites = [
            self.test_clarion_basic_functionality,
            self.test_clarion_integration,
            self.test_learning_pattern_analysis,
            self.test_reinforcement_system,
            self.test_learning_phases,
            self.test_integrated_cycle_with_clarion,
        ]

        for test_suite in test_suites:
            try:
                result = await test_suite()
                self.test_results.append(result)
                logger.info(f"테스트 완료: {result['test_name']} - 성공: {result['success']}")
            except Exception as e:
                error_result = {
                    "test_name": test_suite.__name__,
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }
                self.test_results.append(error_result)
                logger.error(f"테스트 실패: {test_suite.__name__} - {e}")

        # 전체 결과 요약
        await self.generate_test_summary()

    async def test_clarion_basic_functionality(self) -> Dict[str, Any]:
        """CLARION 기본 기능 테스트"""
        test_name = "CLARION 기본 기능 테스트"
        start_time = time.time()

        try:
            # 테스트 로그 데이터
            test_logs = [
                {
                    "context": {"situation": "problem_solving", "complexity": "high"},
                    "action": "analyze_and_plan",
                    "outcome": "success",
                    "success": True,
                    "learning_score": 0.8,
                },
                {
                    "context": {"situation": "routine_task", "complexity": "low"},
                    "action": "automatic_response",
                    "outcome": "success",
                    "success": True,
                    "learning_score": 0.6,
                },
                {
                    "context": {"situation": "new_challenge", "complexity": "medium"},
                    "action": "explore_and_learn",
                    "outcome": "partial_success",
                    "success": False,
                    "learning_score": 0.4,
                },
            ]

            # 로그 처리
            results = []
            for log_data in test_logs:
                result = await self.clarion_system.process_learning_log(log_data)
                results.append(result)

            # 패턴 분석
            pattern_analysis = await self.clarion_system.analyze_learning_patterns()

            # 검증
            assert len(results) == 3, "로그 처리 결과 수가 맞지 않음"
            assert len(self.clarion_system.learning_patterns) > 0, "학습 패턴이 생성되지 않음"
            assert "pattern_frequency" in pattern_analysis, "패턴 분석 결과에 pattern_frequency 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "processed_logs": len(results),
                "generated_patterns": len(self.clarion_system.learning_patterns),
                "pattern_analysis_keys": list(pattern_analysis.keys()),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_clarion_integration(self) -> Dict[str, Any]:
        """CLARION 통합 시스템 테스트"""
        test_name = "CLARION 통합 시스템 테스트"
        start_time = time.time()

        try:
            # 통합 시스템 매니저에서 CLARION 시스템 접근
            clarion_system = self.integrated_manager.clarion_system

            # 학습 로그 처리
            log_data = {
                "context": {"situation": "integration_test", "complexity": "medium"},
                "action": "integrated_learning",
                "outcome": "success",
                "success": True,
                "learning_score": 0.7,
            }

            clarion_result = await clarion_system.process_learning_log(log_data)

            # 통합 사이클에서 CLARION 시스템 실행
            context = {
                "situation": "통합 테스트 상황",
                "available_resources": ["time", "energy", "attention"],
                "emotion": {"type": "focused", "intensity": 0.8},
            }

            clarion_integration_result = await self.integrated_manager._execute_clarion_learning_system(
                {"current_situation": context}
            )

            # 검증
            assert clarion_result.learning_type in [
                LearningType.EXPLICIT,
                LearningType.IMPLICIT,
                LearningType.HYBRID,
            ], "학습 유형이 올바르지 않음"
            assert clarion_result.reinforcement_type in [
                ReinforcementType.POSITIVE,
                ReinforcementType.NEGATIVE,
                ReinforcementType.NEUTRAL,
            ], "강화 유형이 올바르지 않음"
            assert "clarion_result" in clarion_integration_result, "통합 결과에 clarion_result 없음"
            assert "pattern_analysis" in clarion_integration_result, "통합 결과에 pattern_analysis 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "learning_type": clarion_result.learning_type.value,
                "reinforcement_type": clarion_result.reinforcement_type.value,
                "pattern_strength": clarion_result.pattern_strength,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_learning_pattern_analysis(self) -> Dict[str, Any]:
        """학습 패턴 분석 테스트"""
        test_name = "학습 패턴 분석 테스트"
        start_time = time.time()

        try:
            # 다양한 학습 패턴 생성
            test_patterns = [
                {
                    "context": {"task_type": "problem_solving", "difficulty": "high"},
                    "action": "systematic_analysis",
                    "outcome": "success",
                    "success": True,
                    "learning_score": 0.9,
                },
                {
                    "context": {"task_type": "routine_work", "difficulty": "low"},
                    "action": "automatic_execution",
                    "outcome": "success",
                    "success": True,
                    "learning_score": 0.5,
                },
                {
                    "context": {"task_type": "creative_task", "difficulty": "medium"},
                    "action": "explorative_approach",
                    "outcome": "partial_success",
                    "success": False,
                    "learning_score": 0.3,
                },
            ]

            # 패턴 생성
            for log_data in test_patterns:
                await self.clarion_system.process_learning_log(log_data)

            # 패턴 분석
            pattern_analysis = await self.clarion_system.analyze_learning_patterns()

            # 검증
            assert "pattern_frequency" in pattern_analysis, "패턴 빈도 분석 없음"
            assert "reinforcement_effectiveness" in pattern_analysis, "강화 효과 분석 없음"
            assert "phase_analysis" in pattern_analysis, "단계별 분석 없음"
            assert "transfer_analysis" in pattern_analysis, "전이 분석 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "total_patterns": pattern_analysis.get("total_patterns", 0),
                "total_logs": pattern_analysis.get("total_logs", 0),
                "transfer_ability": pattern_analysis.get("transfer_analysis", {}).get("transfer_ability", 0.0),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_reinforcement_system(self) -> Dict[str, Any]:
        """강화 시스템 테스트"""
        test_name = "강화 시스템 테스트"
        start_time = time.time()

        try:
            # 다양한 강화 시나리오 테스트
            reinforcement_scenarios = [
                {
                    "context": {"scenario": "high_success"},
                    "action": "excellent_performance",
                    "outcome": "outstanding_success",
                    "success": True,
                    "learning_score": 0.95,
                },
                {
                    "context": {"scenario": "moderate_success"},
                    "action": "good_performance",
                    "outcome": "success",
                    "success": True,
                    "learning_score": 0.7,
                },
                {
                    "context": {"scenario": "failure"},
                    "action": "poor_performance",
                    "outcome": "failure",
                    "success": False,
                    "learning_score": 0.2,
                },
            ]

            reinforcement_results = []
            for scenario in reinforcement_scenarios:
                result = await self.clarion_system.process_learning_log(scenario)
                reinforcement_results.append(result)

            # 강화 유형 분포 확인
            reinforcement_types = [result.reinforcement_type for result in reinforcement_results]
            positive_count = sum(1 for rt in reinforcement_types if rt == ReinforcementType.POSITIVE)
            negative_count = sum(1 for rt in reinforcement_types if rt == ReinforcementType.NEGATIVE)
            neutral_count = sum(1 for rt in reinforcement_types if rt == ReinforcementType.NEUTRAL)

            # 검증
            assert len(reinforcement_results) == 3, "강화 결과 수가 맞지 않음"
            assert positive_count > 0, "긍정적 강화가 없음"
            assert negative_count > 0, "부정적 강화가 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "positive_reinforcements": positive_count,
                "negative_reinforcements": negative_count,
                "neutral_reinforcements": neutral_count,
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_learning_phases(self) -> Dict[str, Any]:
        """학습 단계 테스트"""
        test_name = "학습 단계 테스트"
        start_time = time.time()

        try:
            # 다양한 학습 단계 시나리오
            phase_scenarios = [
                {
                    "context": {"phase": "acquisition"},
                    "action": "new_learning",
                    "outcome": "basic_understanding",
                    "success": True,
                    "learning_score": 0.2,
                },
                {
                    "context": {"phase": "consolidation"},
                    "action": "practice_and_review",
                    "outcome": "improved_skill",
                    "success": True,
                    "learning_score": 0.6,
                },
                {
                    "context": {"phase": "retrieval"},
                    "action": "apply_knowledge",
                    "outcome": "successful_application",
                    "success": True,
                    "learning_score": 0.8,
                },
                {
                    "context": {"phase": "transfer"},
                    "action": "adapt_to_new_situation",
                    "outcome": "successful_transfer",
                    "success": True,
                    "learning_score": 0.9,
                },
            ]

            phase_results = []
            for scenario in phase_scenarios:
                result = await self.clarion_system.process_learning_log(scenario)
                phase_results.append(result)

            # 학습 단계 분포 확인
            learning_phases = [result.learning_phase for result in phase_results]
            phase_counts = {}
            for phase in learning_phases:
                phase_counts[phase.value] = phase_counts.get(phase.value, 0) + 1

            # 검증
            assert len(phase_results) == 4, "학습 단계 결과 수가 맞지 않음"
            assert len(phase_counts) >= 2, "학습 단계 다양성이 부족함"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "phase_distribution": phase_counts,
                "total_phases": len(phase_results),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def test_integrated_cycle_with_clarion(self) -> Dict[str, Any]:
        """CLARION이 포함된 통합 사이클 테스트"""
        test_name = "CLARION이 포함된 통합 사이클 테스트"
        start_time = time.time()

        try:
            # 통합 사이클 실행을 위한 컨텍스트
            context = {
                "situation": "CLARION 기반 통합 테스트",
                "priority": "high",
                "complexity": "medium",
                "available_resources": ["time", "energy", "attention"],
                "emotion": {"type": "focused", "intensity": 0.8},
            }

            # 통합 사이클 실행
            result = await self.integrated_manager.run_integrated_cycle(context)

            # 검증
            assert "clarion_result" in result, "통합 결과에 clarion_result 없음"
            assert "overall_score" in result, "통합 결과에 overall_score 없음"
            assert "duration" in result, "통합 결과에 duration 없음"

            clarion_result = result["clarion_result"]
            assert "learning_type" in clarion_result, "CLARION 결과에 learning_type 없음"
            assert "reinforcement_type" in clarion_result, "CLARION 결과에 reinforcement_type 없음"
            assert "pattern_strength" in clarion_result, "CLARION 결과에 pattern_strength 없음"

            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": True,
                "duration": duration,
                "overall_score": result["overall_score"],
                "clarion_result_keys": list(clarion_result.keys()),
                "learning_type": clarion_result.get("learning_type", "unknown"),
                "pattern_strength": clarion_result.get("pattern_strength", 0.0),
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            duration = time.time() - start_time
            return {
                "test_name": test_name,
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": datetime.now().isoformat(),
            }

    async def generate_test_summary(self):
        """테스트 결과 요약 생성"""
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests

        total_duration = sum(result.get("duration", 0) for result in self.test_results)

        summary = {
            "test_summary": {
                "total_tests": total_tests,
                "successful_tests": successful_tests,
                "failed_tests": failed_tests,
                "success_rate": ((successful_tests / total_tests * 100) if total_tests > 0 else 0),
                "total_duration": total_duration,
                "timestamp": datetime.now().isoformat(),
            },
            "detailed_results": self.test_results,
        }

        # 결과 출력
        print("\n=== CLARION 학습 시스템 통합 테스트 결과 ===")
        print(f"총 테스트 수: {total_tests}")
        print(f"성공한 테스트: {successful_tests}")
        print(f"실패한 테스트: {failed_tests}")
        print(f"성공률: {summary['test_summary']['success_rate']:.1f}%")
        print(f"총 소요 시간: {total_duration:.3f}초")

        # 실패한 테스트들 출력
        if failed_tests > 0:
            print("\n실패한 테스트들:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result.get('error', 'Unknown error')}")

        # 결과를 파일로 저장
        with open("clarion_integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info("테스트 결과가 clarion_integration_test_results.json에 저장되었습니다.")
        return summary


async def main():
    """메인 테스트 실행"""
    tester = CLARIONIntegrationTest()
    await tester.run_comprehensive_test()


if __name__ == "__main__":
    asyncio.run(main())
