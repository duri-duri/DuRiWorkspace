#!/usr/bin/env python3
"""
DuRiCore Phase 6.3 - 고급 인지 시스템 통합 테스트
고급 인지 시스템의 기능과 통합 시스템과의 연동을 테스트
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

# 테스트 대상 시스템들
from advanced_cognitive_system import AdvancedCognitiveSystem
from integrated_system_manager import IntegratedSystemManager

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class AdvancedCognitiveIntegrationTest:
    """고급 인지 시스템 통합 테스트 클래스"""

    def __init__(self):
        """초기화"""
        self.advanced_cognitive_system = AdvancedCognitiveSystem()
        self.integrated_manager = IntegratedSystemManager()
        self.test_results = []

    async def run_all_tests(self) -> Dict[str, Any]:
        """모든 테스트 실행"""
        logger.info("=== 고급 인지 시스템 통합 테스트 시작 ===")
        start_time = time.time()

        # 테스트 시나리오들
        test_scenarios = [
            (
                "고급 인지 기본 기능 테스트",
                self.test_advanced_cognitive_basic_functionality,
            ),
            ("추상화 엔진 테스트", self.test_abstraction_engine),
            ("메타인지 분석기 테스트", self.test_metacognitive_analyzer),
            ("인지 통합기 테스트", self.test_cognitive_integrator),
            ("고급 최적화기 테스트", self.test_advanced_optimizer),
            ("인지 시스템 통합 테스트", self.test_cognitive_system_integration),
            ("통합 시스템 매니저 테스트", self.test_integrated_system_manager),
        ]

        # 각 테스트 실행
        for test_name, test_func in test_scenarios:
            try:
                logger.info(f"테스트 실행: {test_name}")
                test_start = time.time()
                success = await test_func()
                test_duration = time.time() - test_start

                test_result = {
                    "test_name": test_name,
                    "success": success,
                    "duration": test_duration,
                    "timestamp": datetime.now().isoformat(),
                }
                self.test_results.append(test_result)

                logger.info(f"테스트 완료: {test_name} - 성공: {success}")

            except Exception as e:
                logger.error(f"테스트 실패: {test_name} - {e}")
                test_result = {
                    "test_name": test_name,
                    "success": False,
                    "error": str(e),
                    "duration": 0,
                    "timestamp": datetime.now().isoformat(),
                }
                self.test_results.append(test_result)

        # 전체 결과 계산
        total_duration = time.time() - start_time
        successful_tests = sum(1 for result in self.test_results if result["success"])
        total_tests = len(self.test_results)
        success_rate = (successful_tests / total_tests) * 100 if total_tests > 0 else 0

        # 결과 요약
        summary = {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "failed_tests": total_tests - successful_tests,
            "success_rate": success_rate,
            "total_duration": total_duration,
            "test_results": self.test_results,
            "timestamp": datetime.now().isoformat(),
        }

        # 결과 출력
        print("\n=== 고급 인지 시스템 통합 테스트 결과 ===")
        print(f"총 테스트 수: {total_tests}")
        print(f"성공한 테스트: {successful_tests}")
        print(f"실패한 테스트: {total_tests - successful_tests}")
        print(f"성공률: {success_rate:.1f}%")
        print(f"총 소요 시간: {total_duration:.3f}초")

        if failed_tests := [r for r in self.test_results if not r["success"]]:
            print("\n실패한 테스트들:")
            for result in failed_tests:
                print(f"  - {result['test_name']}: {result.get('error', '알 수 없는 오류')}")

        # 결과를 파일로 저장
        with open("advanced_cognitive_integration_test_results.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)

        logger.info("테스트 결과가 advanced_cognitive_integration_test_results.json에 저장되었습니다.")
        return summary

    async def test_advanced_cognitive_basic_functionality(self) -> bool:
        """고급 인지 기본 기능 테스트"""
        try:
            # 테스트 컨텍스트
            test_context = {
                "situation": "복잡한 문제 해결 상황",
                "priority": "high",
                "complexity": "high",
                "emotion": {"type": "focused", "intensity": 0.8},
            }

            # 고급 인지 처리
            result = await self.advanced_cognitive_system.process_advanced_cognition(test_context)

            # 기본 결과 확인
            if not result.success:
                return False

            if not hasattr(result, "cognitive_insights") or not hasattr(result, "overall_cognitive_score"):
                return False

            return True

        except Exception as e:
            logger.error(f"고급 인지 기본 기능 테스트 실패: {e}")
            return False

    async def test_abstraction_engine(self) -> bool:
        """추상화 엔진 테스트"""
        try:
            # 테스트 컨텍스트
            test_context = {
                "situation": "패턴 분석 상황",
                "priority": "medium",
                "complexity": "medium",
            }

            # 추상화 생성
            abstractions = await self.advanced_cognitive_system.generate_abstractions(test_context)

            # 추상화 결과 확인
            if not isinstance(abstractions, list):
                return False

            # 추상화의 기본 속성 확인
            for abstraction in abstractions:
                if not hasattr(abstraction, "concept_id") or not hasattr(abstraction, "abstraction_type"):
                    return False

            return True

        except Exception as e:
            logger.error(f"추상화 엔진 테스트 실패: {e}")
            return False

    async def test_metacognitive_analyzer(self) -> bool:
        """메타인지 분석기 테스트"""
        try:
            # 테스트 컨텍스트
            test_context = {
                "situation": "자기 성찰 상황",
                "priority": "medium",
                "complexity": "low",
                "emotion": {"type": "reflective", "intensity": 0.6},
            }

            # 메타인지 분석
            metacognitive_processes = await self.advanced_cognitive_system.analyze_metacognition(test_context)

            # 메타인지 결과 확인
            if not isinstance(metacognitive_processes, list):
                return False

            # 메타인지 과정의 기본 속성 확인
            for process in metacognitive_processes:
                if not hasattr(process, "process_id") or not hasattr(process, "metacognitive_type"):
                    return False

            return True

        except Exception as e:
            logger.error(f"메타인지 분석기 테스트 실패: {e}")
            return False

    async def test_cognitive_integrator(self) -> bool:
        """인지 통합기 테스트"""
        try:
            # 테스트 컨텍스트
            test_context = {
                "situation": "통합 사고 상황",
                "priority": "high",
                "complexity": "high",
            }

            # 인지 시스템 통합
            integration_result = await self.advanced_cognitive_system.integrate_cognitive_systems(test_context)

            # 통합 결과 확인
            if not isinstance(integration_result, dict):
                return False

            # 필수 필드 확인
            required_fields = [
                "creative_thinking",
                "strategic_planning",
                "integration_score",
            ]
            for field in required_fields:
                if field not in integration_result:
                    return False

            return True

        except Exception as e:
            logger.error(f"인지 통합기 테스트 실패: {e}")
            return False

    async def test_advanced_optimizer(self) -> bool:
        """고급 최적화기 테스트"""
        try:
            # 테스트 컨텍스트
            test_context = {
                "situation": "성능 최적화 상황",
                "priority": "high",
                "complexity": "medium",
            }

            # 인지 성능 최적화
            optimization_result = await self.advanced_cognitive_system.optimize_cognitive_performance(test_context)

            # 최적화 결과 확인
            if not isinstance(optimization_result, dict):
                return False

            # 최적화 영역 확인
            optimization_areas = [
                "abstraction_optimization",
                "metacognitive_optimization",
                "overall_improvement",
            ]
            for area in optimization_areas:
                if area not in optimization_result:
                    return False

            return True

        except Exception as e:
            logger.error(f"고급 최적화기 테스트 실패: {e}")
            return False

    async def test_cognitive_system_integration(self) -> bool:
        """인지 시스템 통합 테스트"""
        try:
            # 테스트 컨텍스트
            test_context = {
                "situation": "복합 인지 처리 상황",
                "priority": "high",
                "complexity": "high",
                "emotion": {"type": "analytical", "intensity": 0.9},
                "available_resources": ["time", "energy", "knowledge", "creativity"],
            }

            # 고급 인지 처리
            result = await self.advanced_cognitive_system.process_advanced_cognition(test_context)

            # 결과 검증
            if not result.success:
                return False

            # 각 구성 요소 확인
            if not isinstance(result.cognitive_insights, list):
                return False

            if not isinstance(result.metacognitive_processes, list):
                return False

            if not isinstance(result.abstract_concepts, list):
                return False

            if not isinstance(result.overall_cognitive_score, (int, float)):
                return False

            return True

        except Exception as e:
            logger.error(f"인지 시스템 통합 테스트 실패: {e}")
            return False

    async def test_integrated_system_manager(self) -> bool:
        """통합 시스템 매니저 테스트"""
        try:
            # 통합 시스템 매니저의 고급 인지 기능 테스트

            # 통합 사이클 실행
            test_context = {
                "situation": "고급 인지 통합 테스트 상황",
                "priority": "high",
                "complexity": "high",
                "emotion": {"type": "focused", "intensity": 0.8},
                "available_resources": ["time", "energy", "attention", "creativity"],
            }

            result = await self.integrated_manager.run_integrated_cycle(test_context)

            # 결과에 고급 인지 관련 정보가 포함되어 있는지 확인
            if "cognitive_result" not in result:
                return False

            cognitive_result = result["cognitive_result"]

            # 고급 인지 결과의 기본 필드들 확인
            required_fields = [
                "cognitive_insights_count",
                "overall_cognitive_score",
                "success",
            ]
            for field in required_fields:
                if field not in cognitive_result:
                    return False

            # 성공 여부 확인
            if not cognitive_result.get("success", False):
                return False

            # 시스템 상태 확인
            status = await self.integrated_manager.get_system_status()

            if "advanced_cognitive" not in status.get("systems", {}):
                return False

            if status["systems"]["advanced_cognitive"] != "active":
                return False

            return True

        except Exception as e:
            logger.error(f"통합 시스템 매니저 테스트 실패: {e}")
            return False


async def main():
    """메인 테스트 함수"""
    logger.info("고급 인지 시스템 통합 테스트 시작")

    # 테스트 실행
    test_runner = AdvancedCognitiveIntegrationTest()
    results = await test_runner.run_all_tests()

    # 결과 출력
    print("\n=== 최종 테스트 결과 ===")
    print(f"성공률: {results['success_rate']:.1f}%")
    print(f"총 소요 시간: {results['total_duration']:.3f}초")

    if results["success_rate"] >= 80:
        print("✅ 고급 인지 시스템 통합 테스트 성공!")
    else:
        print("❌ 고급 인지 시스템 통합 테스트 실패")


if __name__ == "__main__":
    asyncio.run(main())
