#!/usr/bin/env python3
"""
ACT-R 병렬 처리 시스템 통합 테스트
DuRi Phase 6.1 - 성능 향상 검증
"""

import asyncio
import logging
import time

from duri_orchestrator import DuRiOrchestrator

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_act_r_integration():
    """ACT-R 병렬 처리 통합 테스트"""
    logger.info("🧪 ACT-R 병렬 처리 통합 테스트 시작")

    # DuRi Orchestrator 초기화
    orchestrator = DuRiOrchestrator()

    # ACT-R 병렬 처리 시스템 상태 확인
    if orchestrator.parallel_processor:
        logger.info("✅ ACT-R 병렬 처리 시스템 활성화됨")
    else:
        logger.warning("⚠️  ACT-R 병렬 처리 시스템 비활성화됨")

    # 성능 테스트
    logger.info("📊 성능 테스트 시작")

    # 기본 실행 루프 테스트
    start_time = time.time()

    # 5회 실행 루프 테스트
    for i in range(5):
        logger.info(f"🔄 실행 루프 {i+1}/5")

        # Judgment Phase
        await orchestrator._execute_judgment_phase()

        # Action Phase
        await orchestrator._execute_action_phase()

        # Feedback Phase
        await orchestrator._execute_feedback_phase()

        # 성능 모니터링
        await orchestrator._monitor_performance()

        # 잠시 대기
        await asyncio.sleep(0.1)

    total_time = time.time() - start_time

    # 결과 분석
    logger.info(f"📈 테스트 결과:")
    logger.info(f"   총 실행 시간: {total_time:.3f}초")
    logger.info(f"   평균 실행 시간: {total_time/5:.3f}초")

    # 성능 메트릭 확인
    performance_metrics = orchestrator.get_performance_metrics()
    logger.info(f"📊 성능 메트릭:")
    logger.info(
        f"   ACT-R 병렬 처리: {performance_metrics.get('act_r_parallel_processing', False)}"
    )
    logger.info(f"   병렬 효율성: {performance_metrics.get('parallel_efficiency', 0.0):.1f}%")
    logger.info(f"   성능 향상률: {performance_metrics.get('performance_improvement', 0.0):.1f}%")
    logger.info(f"   목표 향상률: {performance_metrics.get('target_improvement', 23.0):.1f}%")
    logger.info(f"   성공률: {performance_metrics.get('success_rate', 0.0):.1f}%")

    # 목표 달성 여부 확인
    target_improvement = performance_metrics.get("target_improvement", 23.0)
    current_improvement = performance_metrics.get("performance_improvement", 0.0)

    if current_improvement >= target_improvement:
        logger.info("🎉 목표 성능 향상 달성!")
    else:
        logger.info(
            f"📈 추가 최적화 필요 (현재: {current_improvement:.1f}%, 목표: {target_improvement:.1f}%)"
        )

    return {
        "total_time": total_time,
        "average_time": total_time / 5,
        "performance_metrics": performance_metrics,
        "target_achieved": current_improvement >= target_improvement,
    }


async def compare_sequential_vs_parallel():
    """순차 처리 vs 병렬 처리 비교"""
    logger.info("⚖️  순차 처리 vs 병렬 처리 비교 테스트")

    # 순차 처리 시뮬레이션
    async def sequential_simulation():
        start_time = time.time()

        # 순차적으로 작업 실행
        await asyncio.sleep(0.02)  # 판단
        await asyncio.sleep(0.03)  # 행동
        await asyncio.sleep(0.01)  # 피드백

        return time.time() - start_time

    # 병렬 처리 시뮬레이션
    async def parallel_simulation():
        start_time = time.time()

        # 병렬로 작업 실행
        await asyncio.gather(
            asyncio.sleep(0.02),  # 판단
            asyncio.sleep(0.03),  # 행동
            asyncio.sleep(0.01),  # 피드백
        )

        return time.time() - start_time

    # 테스트 실행
    sequential_time = await sequential_simulation()
    parallel_time = await parallel_simulation()

    # 결과 분석
    improvement = ((sequential_time - parallel_time) / sequential_time) * 100

    logger.info(f"📊 비교 결과:")
    logger.info(f"   순차 처리 시간: {sequential_time:.3f}초")
    logger.info(f"   병렬 처리 시간: {parallel_time:.3f}초")
    logger.info(f"   성능 향상률: {improvement:.1f}%")

    return {
        "sequential_time": sequential_time,
        "parallel_time": parallel_time,
        "improvement": improvement,
    }


async def main():
    """메인 테스트 함수"""
    logger.info("🚀 ACT-R 병렬 처리 시스템 통합 테스트 시작")

    # 1. 통합 테스트
    integration_result = await test_act_r_integration()

    # 2. 비교 테스트
    comparison_result = await compare_sequential_vs_parallel()

    # 최종 결과 요약
    logger.info("📋 최종 테스트 결과 요약:")
    logger.info(f"   통합 테스트 성공: {'✅' if integration_result['target_achieved'] else '❌'}")
    logger.info(f"   평균 실행 시간: {integration_result['average_time']:.3f}초")
    logger.info(
        f"   성능 향상률: {integration_result['performance_metrics']['performance_improvement']:.1f}%"
    )
    logger.info(f"   병렬 vs 순차 향상률: {comparison_result['improvement']:.1f}%")

    return {"integration": integration_result, "comparison": comparison_result}


if __name__ == "__main__":
    asyncio.run(main())
