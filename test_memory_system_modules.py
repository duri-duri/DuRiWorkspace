#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-5: 메모리 시스템 모듈 테스트

메모리 시스템의 모든 모듈을 테스트합니다.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_memory_allocator():
    """메모리 할당기 테스트"""
    logger.info("🔍 메모리 할당기 테스트 시작")

    try:
        # 메모리 할당기 import 테스트
        from DuRiCore.memory.memory_manager import (
            MemoryAllocation,
            MemoryAllocator,
            MemoryBlock,
            MemoryStatus,
            MemoryType,
        )

        # MemoryAllocator 인스턴스 생성 테스트
        memory_allocator = MemoryAllocator()
        logger.info(f"✅ MemoryAllocator 생성 성공: {type(memory_allocator)}")

        logger.info("✅ 메모리 할당기 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 메모리 할당기 테스트 실패: {e}")
        return False


def test_memory_synchronizer():
    """메모리 동기화기 테스트"""
    logger.info("🔍 메모리 동기화기 테스트 시작")

    try:
        # 메모리 동기화기 import 테스트
        from DuRiCore.memory.memory_sync import (
            MemoryConflict,
            MemorySynchronizer,
            SyncOperation,
            SyncStatus,
            SyncType,
        )

        # MemorySynchronizer 인스턴스 생성 테스트
        memory_synchronizer = MemorySynchronizer()
        logger.info(f"✅ MemorySynchronizer 생성 성공: {type(memory_synchronizer)}")

        logger.info("✅ 메모리 동기화기 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 메모리 동기화기 테스트 실패: {e}")
        return False


def test_memory_optimizer():
    """메모리 최적화기 테스트"""
    logger.info("🔍 메모리 최적화기 테스트 시작")

    try:
        # 메모리 최적화기 import 테스트
        from DuRiCore.memory.memory_optimization import (
            MemoryOptimizer,
            MemoryUsageMetrics,
            OptimizationStatus,
            OptimizationTask,
            OptimizationType,
        )

        # MemoryOptimizer 인스턴스 생성 테스트
        memory_optimizer = MemoryOptimizer()
        logger.info(f"✅ MemoryOptimizer 생성 성공: {type(memory_optimizer)}")

        logger.info("✅ 메모리 최적화기 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 메모리 최적화기 테스트 실패: {e}")
        return False


async def test_async_functionality():
    """비동기 기능 테스트"""
    logger.info("🔍 비동기 기능 테스트 시작")

    try:
        from DuRiCore.memory.memory_manager import MemoryAllocator, MemoryType
        from DuRiCore.memory.memory_optimization import (
            MemoryOptimizer,
            OptimizationType,
        )
        from DuRiCore.memory.memory_sync import MemorySynchronizer, SyncStatus, SyncType

        # 1. 메모리 할당 테스트
        memory_allocator = MemoryAllocator()

        # 메모리 할당
        allocation_id = await memory_allocator.allocate_memory(
            "테스트 메모리 내용", MemoryType.EXPERIENCE, size=1024
        )
        logger.info(f"✅ 메모리 할당: {allocation_id}")

        # 메모리 블록 조회
        memory_block = await memory_allocator.get_memory_block(
            allocation_id.replace("alloc_", "block_")
        )
        if memory_block:
            logger.info(f"✅ 메모리 블록 조회: {memory_block.block_id}")

        # 메모리 통계 조회
        stats = await memory_allocator.get_memory_statistics()
        logger.info(f"✅ 메모리 통계 조회: {len(stats)}개 항목")

        # 2. 메모리 동기화 테스트
        memory_synchronizer = MemorySynchronizer()

        # 동기화 작업 시작
        sync_id = await memory_synchronizer.start_sync_operation(
            SyncType.FULL, "source_system", "target_system"
        )
        logger.info(f"✅ 동기화 작업 시작: {sync_id}")

        # 동기화 상태 조회
        sync_status = await memory_synchronizer.get_sync_status(sync_id)
        if sync_status:
            logger.info(f"✅ 동기화 상태 조회: {sync_status.status.value}")

        # 동기화 통계 조회
        sync_stats = await memory_synchronizer.get_sync_statistics()
        logger.info(f"✅ 동기화 통계 조회: {len(sync_stats)}개 항목")

        # 3. 메모리 최적화 테스트
        memory_optimizer = MemoryOptimizer()

        # 최적화 작업 시작
        optimization_id = await memory_optimizer.start_optimization(
            OptimizationType.CLEANUP
        )
        logger.info(f"✅ 최적화 작업 시작: {optimization_id}")

        # 최적화 상태 조회
        optimization_status = await memory_optimizer.get_optimization_status(
            optimization_id
        )
        if optimization_status:
            logger.info(f"✅ 최적화 상태 조회: {optimization_status.status.value}")

        # 최적화 통계 조회
        optimization_stats = await memory_optimizer.get_optimization_statistics()
        logger.info(f"✅ 최적화 통계 조회: {len(optimization_stats)}개 항목")

        # 메모리 사용량 분석
        usage_metrics = await memory_optimizer.analyze_memory_usage()
        logger.info(f"✅ 메모리 사용량 분석: {usage_metrics.total_size}바이트")

        logger.info("✅ 비동기 기능 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 비동기 기능 테스트 실패: {e}")
        return False


def test_package_import():
    """패키지 전체 import 테스트"""
    logger.info("🔍 패키지 전체 import 테스트 시작")

    try:
        # 전체 패키지 import 테스트
        from DuRiCore.memory import (
            MemoryAllocator,
            MemoryOptimizer,
            MemorySynchronizer,
            MemoryType,
            OptimizationType,
            SyncType,
        )

        logger.info("✅ 패키지 전체 import 성공")
        return True

    except Exception as e:
        logger.error(f"❌ 패키지 전체 import 실패: {e}")
        return False


def main():
    """메인 테스트 함수"""
    logger.info("🚀 DuRiCore Phase 2-5 메모리 시스템 모듈 테스트 시작")

    test_results = []

    # 1. 메모리 할당기 테스트
    test_results.append(("메모리 할당기", test_memory_allocator()))

    # 2. 메모리 동기화기 테스트
    test_results.append(("메모리 동기화기", test_memory_synchronizer()))

    # 3. 메모리 최적화기 테스트
    test_results.append(("메모리 최적화기", test_memory_optimizer()))

    # 4. 패키지 전체 import 테스트
    test_results.append(("패키지 전체 import", test_package_import()))

    # 5. 비동기 기능 테스트
    async_result = asyncio.run(test_async_functionality())
    test_results.append(("비동기 기능", async_result))

    # 결과 요약
    logger.info("\n" + "=" * 50)
    logger.info("📊 테스트 결과 요약")
    logger.info("=" * 50)

    passed_tests = 0
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{test_name}: {status}")
        if result:
            passed_tests += 1

    logger.info(f"\n총 테스트: {total_tests}개")
    logger.info(f"통과: {passed_tests}개")
    logger.info(f"실패: {total_tests - passed_tests}개")
    logger.info(f"성공률: {(passed_tests/total_tests)*100:.1f}%")

    if passed_tests == total_tests:
        logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return 0
    else:
        logger.error("⚠️ 일부 테스트가 실패했습니다.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
