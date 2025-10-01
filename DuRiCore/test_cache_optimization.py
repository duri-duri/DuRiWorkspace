#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 통합 진화 시스템 - 캐시 히트율 향상 테스트

이 스크립트는 캐시 히트율 향상을 위한 최적화 기능을 테스트합니다.
"""

import asyncio
from datetime import datetime
import json
import logging
import time

from integrated_evolution_system import DuRiIntegratedEvolutionSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_cache_optimization():
    """캐시 히트율 향상 테스트"""
    logger.info("🧪 캐시 히트율 향상 테스트 시작")

    # 시스템 초기화
    system = DuRiIntegratedEvolutionSystem()

    try:
        # 1. 기본 캐시 테스트
        logger.info("📊 1. 기본 캐시 테스트 시작")

        test_inputs = [
            {"task": "test1", "data": "data1"},  # 타임스탬프 제거
            {"task": "test2", "data": "data2"},  # 타임스탬프 제거
            {"task": "test3", "data": "data3"},  # 타임스탬프 제거
            {"task": "test1", "data": "data1"},  # 중복 (캐시 히트 예상)
            {"task": "test2", "data": "data2"},  # 중복 (캐시 히트 예상)
        ]

        test_context = {"test_mode": True, "performance_optimization": True}

        cache_results = []
        for i, test_input in enumerate(test_inputs):
            start_time = time.time()
            result = await system.process_stimulus(test_input, test_context)
            execution_time = time.time() - start_time

            # 캐시 히트 여부 확인
            cache_key = system._generate_cache_key(test_input, test_context)
            cached_result = system._get_from_cache(cache_key)
            cache_hit = cached_result is not None

            cache_results.append(
                {
                    "test_id": i + 1,
                    "input": test_input,
                    "execution_time": execution_time,
                    "success": result.success,
                    "cache_hit": cache_hit,
                    "cache_key": cache_key,
                }
            )

            logger.info(
                f"   테스트 {i+1}: {execution_time:.3f}초, 성공: {result.success}, 캐시히트: {cache_hit}"
            )

        # 2. 캐시 전략 개선 테스트
        logger.info("🔧 2. 캐시 전략 개선 테스트 시작")

        # 캐시 전략 개선 실행
        system._improve_cache_strategy()

        # 캐시 통계 확인
        cache_stats = system.get_cache_stats()
        logger.info(f"   캐시 크기: {cache_stats.get('cache_size', 0)}")
        logger.info(f"   캐시 히트율: {cache_stats.get('cache_hit_rate', 0):.1%}")
        logger.info(f"   캐시 히트: {cache_stats.get('cache_hits', 0)}")
        logger.info(f"   캐시 미스: {cache_stats.get('cache_misses', 0)}")

        # 3. 캐시 키 최적화 테스트
        logger.info("🔑 3. 캐시 키 최적화 테스트 시작")

        test_cases = [
            {
                "name": "기본 테스트",
                "input": {"task": "basic", "data": "test_data"},
                "context": {"mode": "test"},
            },
            {
                "name": "복잡한 데이터",
                "input": {
                    "task": "complex",
                    "data": "test_data",
                    "extra": "additional_info",
                    "nested": {"key": "value"},
                },
                "context": {"mode": "test", "performance": True},
            },
            {
                "name": "중요도 기반",
                "input": {
                    "task": "important",
                    "data": "test_data",
                    "id": "123",
                    "timestamp": "2025-08-06",
                },
                "context": {"goal": "optimization", "mode": "test"},
            },
        ]

        optimization_results = []
        for test_case in test_cases:
            start_time = time.time()
            cache_key = system._optimize_cache_key(
                test_case["input"], test_case["context"]
            )
            optimization_time = time.time() - start_time

            optimization_results.append(
                {
                    "name": test_case["name"],
                    "cache_key": cache_key,
                    "optimization_time": optimization_time,
                    "key_length": len(cache_key),
                }
            )

            logger.info(
                f"   {test_case['name']}: {optimization_time:.3f}초, 키 길이: {len(cache_key)}"
            )

        # 4. 캐시 크기 조정 테스트
        logger.info("📏 4. 캐시 크기 조정 테스트 시작")

        # 현재 캐시 크기 확인
        current_size = len(system.cache)
        current_max_size = system.cache_max_size

        # 캐시 크기 조정 실행
        system._adjust_cache_size()

        new_max_size = system.cache_max_size
        logger.info(f"   현재 캐시 크기: {current_size}")
        logger.info(f"   캐시 최대 크기: {current_max_size} -> {new_max_size}")

        # 5. 캐시 정리 테스트
        logger.info("🧹 5. 캐시 정리 테스트 시작")

        # 캐시 정리 실행
        system._improve_cache_cleanup()

        cleaned_size = len(system.cache)
        logger.info(f"   정리 후 캐시 크기: {cleaned_size}")

        # 6. 성능 비교 분석
        logger.info("📈 6. 성능 비교 분석")

        # 캐시 히트율 계산
        total_requests = cache_stats.get("cache_hits", 0) + cache_stats.get(
            "cache_misses", 0
        )
        hit_rate = cache_stats.get("cache_hit_rate", 0.0)

        logger.info(f"   총 요청 수: {total_requests}")
        logger.info(f"   캐시 히트율: {hit_rate:.1%}")

        # 성능 개선 효과 분석
        if hit_rate > 0.5:
            logger.info("   ✅ 캐시 히트율이 50% 이상으로 양호합니다!")
        elif hit_rate > 0.2:
            logger.info("   ⚠️ 캐시 히트율이 20% 이상이지만 개선 여지가 있습니다.")
        else:
            logger.info("   ❌ 캐시 히트율이 낮습니다. 추가 최적화가 필요합니다.")

        # 결과 저장
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "cache_results": cache_results,
            "cache_stats": cache_stats,
            "optimization_results": optimization_results,
            "cache_size_adjustment": {
                "previous_size": current_max_size,
                "new_size": new_max_size,
                "current_items": current_size,
                "cleaned_items": cleaned_size,
            },
            "performance_analysis": {
                "total_requests": total_requests,
                "hit_rate": hit_rate,
                "improvement_needed": hit_rate < 0.5,
            },
        }

        # 결과를 JSON 파일로 저장
        with open("cache_optimization_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)

        logger.info(
            "💾 테스트 결과가 'cache_optimization_test_results.json'에 저장되었습니다."
        )

        return test_results

    except Exception as e:
        logger.error(f"❌ 캐시 최적화 테스트 실패: {e}")
        return {"error": str(e)}
    finally:
        # 리소스 정리
        await system.cleanup()


async def main():
    """메인 함수"""
    logger.info("🚀 DuRi 통합 진화 시스템 - 캐시 히트율 향상 테스트 시작")

    # 테스트 실행
    results = await test_cache_optimization()

    if "error" in results:
        logger.error(f"❌ 테스트 실패: {results['error']}")
        return 1
    else:
        logger.info("✅ 모든 테스트 완료!")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
