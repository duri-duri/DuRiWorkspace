#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 성능 최적화 시스템 테스트
Phase 5: 성능 최적화 - 최종 실행 준비 완료 적용

통합 성능 최적화 시스템의 테스트를 위한 스크립트입니다.
"""

import asyncio
from datetime import datetime
import json
import logging
import time
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_unified_performance_optimizer():
    """통합 성능 최적화 시스템 테스트"""
    try:
        logger.info("=== 통합 성능 최적화 시스템 테스트 시작 ===")

        # 통합 성능 최적화 시스템 임포트
        from unified_performance_optimizer import unified_performance_optimizer

        # 성능 모니터링 시작
        await unified_performance_optimizer.start_monitoring()

        # 잠시 대기하여 메트릭 수집
        await asyncio.sleep(5)

        # 성능 요약 생성
        performance_summary = (
            await unified_performance_optimizer.get_performance_summary()
        )

        logger.info("성능 요약:")
        logger.info(json.dumps(performance_summary, indent=2, ensure_ascii=False))

        return performance_summary

    except Exception as e:
        logger.error(f"통합 성능 최적화 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_async_optimization_system():
    """비동기 최적화 시스템 테스트"""
    try:
        logger.info("=== 비동기 최적화 시스템 테스트 시작 ===")

        # 비동기 최적화 시스템 임포트
        from async_optimization_system import (
            OptimizationStrategy,
            TaskPriority,
            async_optimization_system,
        )

        # 테스트 작업 생성
        async def test_task_1():
            await asyncio.sleep(1)
            return "작업 1 완료"

        async def test_task_2():
            await asyncio.sleep(0.5)
            return "작업 2 완료"

        async def test_task_3():
            await asyncio.sleep(2)
            return "작업 3 완료"

        # 작업 제출
        task_id_1 = await async_optimization_system.submit_task(
            "테스트 작업 1", test_task_1(), TaskPriority.HIGH
        )
        task_id_2 = await async_optimization_system.submit_task(
            "테스트 작업 2", test_task_2(), TaskPriority.NORMAL
        )
        task_id_3 = await async_optimization_system.submit_task(
            "테스트 작업 3", test_task_3(), TaskPriority.LOW
        )

        # 작업 실행
        results = await async_optimization_system.execute_tasks(
            OptimizationStrategy.PARALLEL
        )

        logger.info("비동기 최적화 결과:")
        logger.info(json.dumps(results, indent=2, ensure_ascii=False))

        # 최적화 요약 생성
        optimization_summary = (
            await async_optimization_system.get_optimization_summary()
        )

        logger.info("최적화 요약:")
        logger.info(json.dumps(optimization_summary, indent=2, ensure_ascii=False))

        return results

    except Exception as e:
        logger.error(f"비동기 최적화 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_memory_optimization_system():
    """메모리 최적화 시스템 테스트"""
    try:
        logger.info("=== 메모리 최적화 시스템 테스트 시작 ===")

        # 메모리 최적화 시스템 임포트
        from memory_optimization_system import (
            MemoryOptimizationType,
            memory_optimization_system,
        )

        # 메모리 모니터링 시작
        await memory_optimization_system.start_monitoring()

        # 잠시 대기하여 메트릭 수집
        await asyncio.sleep(5)

        # 메모리 최적화 실행
        optimization_result = (
            await memory_optimization_system._execute_memory_optimization(
                MemoryOptimizationType.GARBAGE_COLLECTION
            )
        )

        logger.info("메모리 최적화 결과:")
        logger.info(f"해제된 메모리: {optimization_result.memory_freed:.2f}MB")
        logger.info(f"수집된 객체: {optimization_result.objects_collected}개")
        logger.info(f"최적화 점수: {optimization_result.optimization_score:.2f}")

        # 메모리 요약 생성
        memory_summary = await memory_optimization_system.get_memory_summary()

        logger.info("메모리 요약:")
        logger.info(json.dumps(memory_summary, indent=2, ensure_ascii=False))

        return memory_summary

    except Exception as e:
        logger.error(f"메모리 최적화 시스템 테스트 실패: {e}")
        return {"error": str(e)}


async def test_integrated_performance_optimization():
    """통합 성능 최적화 테스트"""
    try:
        logger.info("=== 통합 성능 최적화 테스트 시작 ===")

        # 모든 최적화 시스템 테스트
        results = {}

        # 1. 통합 성능 최적화 시스템 테스트
        logger.info("1. 통합 성능 최적화 시스템 테스트 중...")
        results["unified_performance"] = await test_unified_performance_optimizer()

        # 2. 비동기 최적화 시스템 테스트
        logger.info("2. 비동기 최적화 시스템 테스트 중...")
        results["async_optimization"] = await test_async_optimization_system()

        # 3. 메모리 최적화 시스템 테스트
        logger.info("3. 메모리 최적화 시스템 테스트 중...")
        results["memory_optimization"] = await test_memory_optimization_system()

        # 통합 결과 생성
        integrated_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_results": results,
            "overall_status": (
                "completed"
                if all("error" not in result for result in results.values())
                else "partial_failure"
            ),
        }

        logger.info("=== 통합 성능 최적화 테스트 완료 ===")
        logger.info("통합 결과:")
        logger.info(json.dumps(integrated_results, indent=2, ensure_ascii=False))

        return integrated_results

    except Exception as e:
        logger.error(f"통합 성능 최적화 테스트 실패: {e}")
        return {"error": str(e)}


async def main():
    """메인 함수"""
    try:
        logger.info("DuRi 성능 최적화 시스템 테스트 시작")

        # 통합 성능 최적화 테스트 실행
        results = await test_integrated_performance_optimization()

        # 결과 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_performance_optimization_{timestamp}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        logger.info(f"테스트 결과가 {filename}에 저장되었습니다.")

        return results

    except Exception as e:
        logger.error(f"메인 함수 실행 실패: {e}")
        return {"error": str(e)}


if __name__ == "__main__":
    # asyncio.run(main())
    # 테스트 실행을 위한 간단한 실행
    asyncio.run(test_integrated_performance_optimization())
