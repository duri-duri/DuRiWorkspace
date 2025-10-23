#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 통합 진화 시스템 테스트 (성능 최적화 통합 버전)

이 스크립트는 통합된 성능 최적화 시스템의 성능을 테스트합니다.
"""

import asyncio
import json
import logging
import time
from datetime import datetime

from integrated_evolution_system import DuRiIntegratedEvolutionSystem

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


async def test_integrated_performance_optimization():
    """통합 성능 최적화 시스템 테스트"""
    logger.info("🚀 DuRi 통합 진화 시스템 (성능 최적화 통합 버전) 테스트 시작")

    # 시스템 초기화
    system = DuRiIntegratedEvolutionSystem()

    try:
        # 1. 기본 성능 테스트
        logger.info("📊 1. 기본 성능 테스트 시작")
        test_input = {
            "task": "performance_test",
            "data": "test_data",
            "timestamp": datetime.now().isoformat(),
        }
        test_context = {"test_mode": True, "performance_optimization": True}

        start_time = time.time()
        result = await system.process_stimulus(test_input, test_context)
        execution_time = time.time() - start_time

        logger.info(f"✅ 기본 성능 테스트 완료: {execution_time:.3f}초")
        logger.info(f"   - 성공: {result.success}")
        logger.info(f"   - 개선점수: {result.overall_improvement_score:.3f}")

        # 2. 통합 성능 테스트
        logger.info("🧪 2. 통합 성능 테스트 시작")
        integrated_test_results = await system.test_integrated_performance()

        logger.info("✅ 통합 성능 테스트 완료")
        logger.info(
            f"   - 기본 성능: {integrated_test_results.get('basic_performance', {}).get('execution_time', 0):.3f}초"
        )
        logger.info(
            f"   - 병렬 처리: {integrated_test_results.get('parallel_processing', {}).get('execution_time', 0):.3f}초"
        )
        logger.info(
            f"   - 캐시 성능: {integrated_test_results.get('cache_performance', {}).get('cache_lookup_time', 0):.3f}초"
        )

        # 3. 시스템 성능 최적화
        logger.info("�� 3. 시스템 성능 최적화 시작")
        optimization_results = await system.optimize_system_performance()

        logger.info("✅ 시스템 성능 최적화 완료")
        if optimization_results:
            for key, value in optimization_results.items():
                logger.info(f"   - {key}: {value}")

        # 4. 진화 시스템 요약
        logger.info("📈 4. 진화 시스템 요약 생성")
        summary = await system.get_evolution_summary()

        logger.info("✅ 진화 시스템 요약 완료")
        logger.info(f"   - 총 세션: {summary.get('total_sessions', 0)}")
        logger.info(f"   - 성공률: {summary.get('success_rate', 0):.1f}%")
        logger.info(f"   - 평균 실행시간: {summary.get('average_execution_time', 0):.3f}초")
        logger.info(f"   - 성능 개선률: {summary.get('performance_improvement', 0):.1f}%")

        # 5. 캐시 통계
        cache_stats = system.get_cache_stats()
        logger.info("📊 캐시 통계:")
        logger.info(f"   - 캐시 크기: {cache_stats.get('cache_size', 0)}")
        logger.info(f"   - 캐시 히트율: {cache_stats.get('cache_hit_rate', 0):.1f}%")
        logger.info(f"   - 캐시 히트: {cache_stats.get('cache_hits', 0)}")
        logger.info(f"   - 캐시 미스: {cache_stats.get('cache_misses', 0)}")

        # 6. 통합 시스템 상태
        integrated_systems = summary.get("integrated_systems", {})
        logger.info("🔗 통합 시스템 상태:")
        logger.info(f"   - 향상된 병렬 처리: {'✅' if integrated_systems.get('enhanced_parallel_processor') else '❌'}")
        logger.info(f"   - 성능 최적화: {'✅' if integrated_systems.get('performance_optimizer') else '❌'}")
        logger.info(f"   - ACT-R 병렬 처리: {'✅' if integrated_systems.get('act_r_parallel_processor') else '❌'}")

        # 7. 성능 비교 분석
        baseline_time = summary.get("baseline_execution_time", 0.215)
        current_time = summary.get("average_execution_time", 0)
        target_time = summary.get("target_execution_time", 0.1)

        if baseline_time > 0 and current_time > 0:
            improvement_ratio = (baseline_time - current_time) / baseline_time * 100
            target_achievement = (
                (baseline_time - current_time) / (baseline_time - target_time) * 100
                if baseline_time > target_time
                else 100
            )

            logger.info("🎯 성능 비교 분석:")
            logger.info(f"   - 기준 시간: {baseline_time:.3f}초")
            logger.info(f"   - 현재 시간: {current_time:.3f}초")
            logger.info(f"   - 목표 시간: {target_time:.3f}초")
            logger.info(f"   - 개선률: {improvement_ratio:.1f}%")
            logger.info(f"   - 목표 달성률: {target_achievement:.1f}%")

        # 결과 저장
        test_results = {
            "test_timestamp": datetime.now().isoformat(),
            "basic_performance": {
                "execution_time": execution_time,
                "success": result.success,
                "improvement_score": result.overall_improvement_score,
            },
            "integrated_performance": integrated_test_results,
            "optimization_results": optimization_results,
            "system_summary": summary,
            "cache_stats": cache_stats,
            "performance_analysis": {
                "baseline_time": baseline_time,
                "current_time": current_time,
                "target_time": target_time,
                "improvement_ratio": (improvement_ratio if baseline_time > 0 and current_time > 0 else 0),
                "target_achievement": (target_achievement if baseline_time > 0 and current_time > 0 else 0),
            },
        }

        # 결과를 JSON 파일로 저장
        with open("integrated_performance_test_results.json", "w", encoding="utf-8") as f:
            json.dump(test_results, f, indent=2, ensure_ascii=False, default=str)

        logger.info("💾 테스트 결과가 'integrated_performance_test_results.json'에 저장되었습니다.")

        return test_results

    except Exception as e:
        logger.error(f"❌ 테스트 실패: {e}")
        return {"error": str(e)}
    finally:
        # 리소스 정리
        await system.cleanup()


async def main():
    """메인 함수"""
    logger.info("🚀 DuRi 통합 진화 시스템 (성능 최적화 통합 버전) 테스트 시작")

    # 테스트 실행
    results = await test_integrated_performance_optimization()

    if "error" in results:
        logger.error(f"❌ 테스트 실패: {results['error']}")
        return 1
    else:
        logger.info("✅ 모든 테스트 완료!")
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
