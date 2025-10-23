#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 학습 모듈 개별 테스트 스크립트
챗지피티의 분석에 따라 각 모듈을 개별적으로 테스트합니다.
"""

import asyncio
import logging
import os
import sys

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_unified_learning_system():
    """통합 학습 시스템 테스트"""
    print("\n🧪 통합 학습 시스템 테스트")
    print("-" * 40)

    try:
        from DuRiCore.unified_learning_system import EvolutionType, LearningType, UnifiedLearningSystem

        # 시스템 초기화
        learning_system = UnifiedLearningSystem()
        print("✅ 시스템 초기화 성공")

        # 학습 세션 시작
        session = await learning_system.start_learning_session(
            learning_type=LearningType.CONTINUOUS, context={"test": True}
        )
        print(f"✅ 학습 세션 시작 성공: {session.id}")

        # 진화 세션 시작
        evolution_session = await learning_system.start_evolution_session(
            evolution_type=EvolutionType.INCREMENTAL, context={"test": True}
        )
        print(f"✅ 진화 세션 시작 성공: {evolution_session.id}")

        return True

    except Exception as e:
        print(f"❌ 통합 학습 시스템 테스트 실패: {e}")
        return False


async def test_autonomous_learning_system():
    """자율 학습 시스템 테스트"""
    print("\n🧪 자율 학습 시스템 테스트")
    print("-" * 40)

    try:
        from duri_modules.autonomous.continuous_learner import AutonomousLearner
        from duri_modules.autonomous.duri_autonomous_core import DuRiAutonomousCore

        # 자율 학습 시작
        autonomous_learner = AutonomousLearner()
        autonomous_core = DuRiAutonomousCore()

        print("✅ 시스템 초기화 성공")

        # 자율 학습 시작
        learner_started = autonomous_learner.start_autonomous_learning()
        print(f"✅ 자율 학습 시작: {learner_started}")

        # 자율 코어 시작
        core_started = await autonomous_core.start_autonomous_learning()
        print(f"✅ 자율 코어 시작: {core_started}")

        return learner_started and core_started

    except Exception as e:
        print(f"❌ 자율 학습 시스템 테스트 실패: {e}")
        return False


async def test_learning_loop_manager():
    """학습 루프 매니저 테스트"""
    print("\n🧪 학습 루프 매니저 테스트")
    print("-" * 40)

    try:
        from duri_brain.learning.learning_loop_manager import get_learning_loop_manager

        # 학습 루프 매니저 가져오기
        learning_loop_manager = get_learning_loop_manager()
        print("✅ 학습 루프 매니저 초기화 성공")

        # 초기 전략 설정
        initial_strategy = {
            "learning_type": "continuous",
            "intensity": "moderate",
            "focus_areas": ["general", "problem_solving", "creativity"],
            "meta_learning_enabled": True,
            "self_assessment_enabled": True,
        }

        # 학습 루프 시작
        cycle_id = learning_loop_manager.start_learning_loop(initial_strategy)
        print(f"✅ 학습 루프 시작 성공: {cycle_id}")

        # 상태 확인
        status = learning_loop_manager.get_current_status()
        print(f"✅ 상태 확인 성공: {status.get('is_running', False)}")

        return True

    except Exception as e:
        print(f"❌ 학습 루프 매니저 테스트 실패: {e}")
        return False


async def test_realtime_learner():
    """실시간 학습 시스템 테스트"""
    print("\n🧪 실시간 학습 시스템 테스트")
    print("-" * 40)

    try:
        from duri_modules.autonomous.continuous_learner import AutonomousLearner
        from duri_modules.autonomous.realtime_learner import RealtimeLearner

        autonomous_learner = AutonomousLearner()
        realtime_learner = RealtimeLearner(autonomous_learner)

        print("✅ 시스템 초기화 성공")

        # 실시간 학습 시작
        realtime_started = realtime_learner.start_realtime_learning()
        print(f"✅ 실시간 학습 시작: {realtime_started}")

        # 상태 확인
        status = realtime_learner.get_realtime_status()
        print(f"✅ 상태 확인 성공: {status}")

        return realtime_started

    except Exception as e:
        print(f"❌ 실시간 학습 시스템 테스트 실패: {e}")
        return False


async def test_memory_sync():
    """메모리 동기화 시스템 테스트"""
    print("\n🧪 메모리 동기화 시스템 테스트")
    print("-" * 40)

    try:
        from duri_core.memory.memory_sync import ExperienceSource, MemoryType, get_memory_sync

        # 메모리 동기화 시스템 가져오기
        memory_sync = get_memory_sync()
        print("✅ 메모리 동기화 시스템 초기화 성공")

        # 테스트 데이터 저장
        test_content = {"test": "data", "timestamp": "2025-08-08"}
        memory_id = memory_sync.store_experience(
            memory_type=MemoryType.LEARNING_EXPERIENCE,
            source=ExperienceSource.EXTERNAL,
            content=test_content,
            confidence=0.8,
            tags=["test", "learning"],
        )
        print(f"✅ 테스트 데이터 저장 성공: {memory_id}")

        # 데이터 조회
        experiences = memory_sync.retrieve_experiences(memory_type=MemoryType.LEARNING_EXPERIENCE, limit=1)
        print(f"✅ 데이터 조회 성공: {len(experiences)}개")

        return True

    except Exception as e:
        print(f"❌ 메모리 동기화 시스템 테스트 실패: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRi 학습 모듈 개별 테스트 시작")
    print("=" * 60)

    test_results = {}

    # 1. 메모리 동기화 시스템 테스트 (가장 먼저)
    test_results["memory_sync"] = await test_memory_sync()

    # 2. 통합 학습 시스템 테스트
    test_results["unified_learning"] = await test_unified_learning_system()

    # 3. 자율 학습 시스템 테스트
    test_results["autonomous_learning"] = await test_autonomous_learning_system()

    # 4. 학습 루프 매니저 테스트
    test_results["learning_loop_manager"] = await test_learning_loop_manager()

    # 5. 실시간 학습 시스템 테스트
    test_results["realtime_learner"] = await test_realtime_learner()

    # 결과 요약
    print("\n📊 테스트 결과 요약")
    print("=" * 60)

    successful_tests = sum(1 for result in test_results.values() if result)
    total_tests = len(test_results)

    for test_name, result in test_results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"  {test_name}: {status}")

    print(f"\n🎯 전체 성공률: {successful_tests}/{total_tests}")

    if successful_tests == total_tests:
        print("\n🎉 모든 모듈이 정상 작동합니다!")
        print("이제 전체 학습 시스템을 활성화할 수 있습니다.")
    elif successful_tests > 0:
        print(f"\n⚠️ 일부 모듈만 정상 작동합니다. ({successful_tests}/{total_tests})")
        print("문제가 있는 모듈을 수정해야 합니다.")
    else:
        print("\n🚨 모든 모듈에 문제가 있습니다.")
        print("기본적인 의존성 문제를 해결해야 합니다.")


if __name__ == "__main__":
    asyncio.run(main())
