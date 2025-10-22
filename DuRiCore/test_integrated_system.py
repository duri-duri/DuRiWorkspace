#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 통합 테스트 시스템 테스트
Phase 6: 통합 테스트 및 검증 - 최종 실행 준비 완료 적용

통합 테스트 시스템의 테스트를 위한 스크립트입니다.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_integrated_test_system():
    """통합 테스트 시스템 테스트"""
    try:
        logger.info("=== 통합 테스트 시스템 테스트 시작 ===")

        # 통합 테스트 시스템 임포트
        from integrated_test_system import (TestPriority, TestSuite, TestType,
                                            integrated_test_system)

        # 테스트 스위트 등록
        test_suites = [
            TestSuite(
                id="unified_systems_suite",
                name="통합 시스템 테스트 스위트",
                description="통합 시스템들의 기능 테스트",
                tests=[
                    "unified_performance_test",
                    "unified_conversation_test",
                    "unified_learning_test",
                    "unified_judgment_test",
                ],
                priority=TestPriority.HIGH,
                dependencies=[
                    "unified_performance_optimizer",
                    "unified_conversation_service",
                    "unified_learning_system",
                    "unified_judgment_system",
                ],
            ),
            TestSuite(
                id="optimization_systems_suite",
                name="최적화 시스템 테스트 스위트",
                description="성능 최적화 시스템들의 테스트",
                tests=[
                    "async_optimization_test",
                    "memory_optimization_test",
                    "performance_optimization_test",
                ],
                priority=TestPriority.HIGH,
                dependencies=[
                    "async_optimization_system",
                    "memory_optimization_system",
                ],
            ),
            TestSuite(
                id="integration_systems_suite",
                name="시스템 통합 테스트 스위트",
                description="전체 시스템 통합 테스트",
                tests=["integration_system_test"],
                priority=TestPriority.CRITICAL,
                dependencies=[],
            ),
        ]

        # 테스트 스위트 등록
        for suite in test_suites:
            await integrated_test_system.register_test_suite(suite)

        # 통합 테스트 실행
        logger.info("통합 테스트 실행 중...")
        report = await integrated_test_system.run_integration_tests()

        logger.info("통합 테스트 결과:")
        logger.info(
            json.dumps(
                {
                    "id": report.id,
                    "timestamp": report.timestamp.isoformat(),
                    "total_tests": report.total_tests,
                    "passed_tests": report.passed_tests,
                    "failed_tests": report.failed_tests,
                    "skipped_tests": report.skipped_tests,
                    "overall_score": report.overall_score,
                    "recommendations": report.recommendations,
                },
                indent=2,
                ensure_ascii=False,
            )
        )

        # 테스트 요약 생성
        summary = await integrated_test_system.get_test_summary()

        logger.info("테스트 요약:")
        logger.info(json.dumps(summary, indent=2, ensure_ascii=False))

        # JSON 직렬화 가능한 형태로 변환
        return {
            "id": report.id,
            "timestamp": report.timestamp.isoformat(),
            "total_tests": report.total_tests,
            "passed_tests": report.passed_tests,
            "failed_tests": report.failed_tests,
            "skipped_tests": report.skipped_tests,
            "overall_score": report.overall_score,
            "recommendations": report.recommendations,
        }

    except Exception as e:
        logger.error(f"통합 테스트 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_individual_systems():
    """개별 시스템 테스트"""
    try:
        logger.info("=== 개별 시스템 테스트 시작 ===")

        results = {}

        # 1. 통합 성능 최적화 시스템 테스트
        try:
            from unified_performance_optimizer import \
                unified_performance_optimizer

            performance_summary = await unified_performance_optimizer.get_performance_summary()
            results["unified_performance"] = {
                "status": "success",
                "efficiency_score": performance_summary.get("current_metrics", {}).get(
                    "efficiency_score", 0.0
                ),
            }
            logger.info(
                f"통합 성능 최적화 시스템: 효율성 점수 {results['unified_performance']['efficiency_score']:.2f}"
            )
        except Exception as e:
            results["unified_performance"] = {"status": "error", "error": str(e)}
            logger.error(f"통합 성능 최적화 시스템 테스트 실패: {e}")

        # 2. 비동기 최적화 시스템 테스트
        try:
            from async_optimization_system import async_optimization_system

            async_summary = await async_optimization_system.get_optimization_summary()
            results["async_optimization"] = {
                "status": "success",
                "optimization_score": async_summary.get("current_metrics", {}).get(
                    "optimization_score", 0.0
                ),
            }
            logger.info(
                f"비동기 최적화 시스템: 최적화 점수 {results['async_optimization']['optimization_score']:.2f}"
            )
        except Exception as e:
            results["async_optimization"] = {"status": "error", "error": str(e)}
            logger.error(f"비동기 최적화 시스템 테스트 실패: {e}")

        # 3. 메모리 최적화 시스템 테스트
        try:
            from memory_optimization_system import memory_optimization_system

            memory_summary = await memory_optimization_system.get_memory_summary()
            results["memory_optimization"] = {
                "status": "success",
                "optimization_score": memory_summary.get("current_metrics", {}).get(
                    "optimization_score", 0.0
                ),
            }
            logger.info(
                f"메모리 최적화 시스템: 최적화 점수 {results['memory_optimization']['optimization_score']:.2f}"
            )
        except Exception as e:
            results["memory_optimization"] = {"status": "error", "error": str(e)}
            logger.error(f"메모리 최적화 시스템 테스트 실패: {e}")

        # 4. 통합 대화 서비스 테스트
        try:
            from unified_conversation_service import \
                unified_conversation_service

            results["unified_conversation"] = {
                "status": "success",
                "service": "unified_conversation_service",
            }
            logger.info("통합 대화 서비스: 정상")
        except Exception as e:
            results["unified_conversation"] = {"status": "error", "error": str(e)}
            logger.error(f"통합 대화 서비스 테스트 실패: {e}")

        # 5. 통합 학습 시스템 테스트
        try:
            from unified_learning_system import unified_learning_system

            results["unified_learning"] = {
                "status": "success",
                "service": "unified_learning_system",
            }
            logger.info("통합 학습 시스템: 정상")
        except Exception as e:
            results["unified_learning"] = {"status": "error", "error": str(e)}
            logger.error(f"통합 학습 시스템 테스트 실패: {e}")

        # 6. 통합 판단 시스템 테스트
        try:
            from unified_judgment_system import unified_judgment_system

            results["unified_judgment"] = {
                "status": "success",
                "service": "unified_judgment_system",
            }
            logger.info("통합 판단 시스템: 정상")
        except Exception as e:
            results["unified_judgment"] = {"status": "error", "error": str(e)}
            logger.error(f"통합 판단 시스템 테스트 실패: {e}")

        return results

    except Exception as e:
        logger.error(f"개별 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_system_integration():
    """시스템 통합 테스트"""
    try:
        logger.info("=== 시스템 통합 테스트 시작 ===")

        # 시스템 간 연동 테스트
        integration_results = {}

        # 1. 성능 최적화 시스템과 메모리 최적화 시스템 연동 테스트
        try:
            from memory_optimization_system import memory_optimization_system
            from unified_performance_optimizer import \
                unified_performance_optimizer

            # 성능 모니터링 시작
            await unified_performance_optimizer.start_monitoring()
            await memory_optimization_system.start_monitoring()

            # 잠시 대기
            await asyncio.sleep(2)

            # 성능 요약 확인
            performance_summary = await unified_performance_optimizer.get_performance_summary()
            memory_summary = await memory_optimization_system.get_memory_summary()

            integration_results["performance_memory_integration"] = {
                "status": "success",
                "performance_score": performance_summary.get("current_metrics", {}).get(
                    "efficiency_score", 0.0
                ),
                "memory_score": memory_summary.get("current_metrics", {}).get(
                    "optimization_score", 0.0
                ),
            }

            logger.info(
                f"성능-메모리 통합: 성능 점수 {integration_results['performance_memory_integration']['performance_score']:.2f}, 메모리 점수 {integration_results['performance_memory_integration']['memory_score']:.2f}"
            )

        except Exception as e:
            integration_results["performance_memory_integration"] = {
                "status": "error",
                "error": str(e),
            }
            logger.error(f"성능-메모리 통합 테스트 실패: {e}")

        # 2. 비동기 최적화 시스템과 통합 시스템 연동 테스트
        try:
            from async_optimization_system import async_optimization_system
            from unified_conversation_service import \
                unified_conversation_service

            # 비동기 작업 제출 테스트
            async def test_task():
                await asyncio.sleep(0.1)
                return "통합 테스트 완료"

            task_id = await async_optimization_system.submit_task("통합 테스트 작업", test_task())
            results = await async_optimization_system.execute_tasks()

            integration_results["async_integration"] = {
                "status": "success",
                "completed_tasks": results.get("completed", 0),
                "failed_tasks": results.get("failed", 0),
            }

            logger.info(
                f"비동기 통합: 완료된 작업 {integration_results['async_integration']['completed_tasks']}개, 실패한 작업 {integration_results['async_integration']['failed_tasks']}개"
            )

        except Exception as e:
            integration_results["async_integration"] = {
                "status": "error",
                "error": str(e),
            }
            logger.error(f"비동기 통합 테스트 실패: {e}")

        return integration_results

    except Exception as e:
        logger.error(f"시스템 통합 테스트 실패: {e}")
        return {"error": str(e)}


async def main():
    """메인 함수"""
    try:
        logger.info("DuRi 통합 테스트 시스템 테스트 시작")

        # 1. 개별 시스템 테스트
        individual_results = await test_individual_systems()

        # 2. 시스템 통합 테스트
        integration_results = await test_system_integration()

        # 3. 통합 테스트 시스템 테스트
        integrated_test_results = await test_integrated_test_system()

        # 전체 결과 생성
        overall_results = {
            "test_timestamp": datetime.now().isoformat(),
            "individual_systems": individual_results,
            "system_integration": integration_results,
            "integrated_test_system": integrated_test_results,
            "overall_status": "completed",
        }

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_integrated_system_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(overall_results, f, indent=2, ensure_ascii=False)

        logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")

        logger.info("=== 통합 테스트 시스템 테스트 완료 ===")

        return overall_results

    except Exception as e:
        logger.error(f"메인 함수 실행 실패: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    asyncio.run(main())
