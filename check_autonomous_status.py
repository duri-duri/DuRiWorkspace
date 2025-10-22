#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 자율 학습 시스템 상태 확인 스크립트
"""

import asyncio
import logging
import sys
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def check_autonomous_status():
    """DuRi의 자율 학습 시스템 상태를 확인합니다."""
    try:
        print("=" * 50)
        print("🤖 DuRi 자율 학습 시스템 상태 확인")
        print("=" * 50)

        # 자율 학습 시스템 import 시도
        try:
            sys.path.append(".")
            from duri_modules.autonomous.continuous_learner import \
                AutonomousLearner
            from duri_modules.autonomous.duri_autonomous_core import \
                DuRiAutonomousCore

            # 자율 학습 시스템 초기화
            autonomous_learner = AutonomousLearner()
            autonomous_core = DuRiAutonomousCore()

            print(f"🎯 자율 학습 시스템 상태:")
            print(f"  - AutonomousLearner 실행 중: {autonomous_learner.is_running}")
            print(f"  - DuRiAutonomousCore 활성화: {autonomous_core.is_active}")

            if autonomous_learner.is_running:
                status = autonomous_learner.get_status()
                print(f"  - 세션 ID: {status.get('session_id', 'N/A')}")
                print(f"  - 총 학습 사이클: {status.get('total_learning_cycles', 0)}")
                print(f"  - 감지된 문제: {status.get('total_problems_detected', 0)}")
                print(f"  - 자동 결정: {status.get('total_decisions_made', 0)}")

        except ImportError as e:
            print(f"⚠️ 자율 학습 모듈을 찾을 수 없습니다: {e}")

        # 실시간 학습 시스템 확인
        try:
            from duri_modules.autonomous.realtime_learner import \
                RealtimeLearner

            # 실시간 학습 시스템 상태 확인 (새로운 인스턴스 생성)
            realtime_learner = RealtimeLearner(None)  # None으로 초기화
            print(f"\n⚡ 실시간 학습 시스템:")
            print(f"  - 활성화 상태: {realtime_learner.is_active}")

        except ImportError as e:
            print(f"⚠️ 실시간 학습 모듈을 찾을 수 없습니다: {e}")

        # 학습 루프 매니저 확인
        try:
            from duri_brain.learning.learning_loop_manager import \
                LearningLoopManager

            # 학습 루프 매니저 상태 확인
            learning_loop_manager = LearningLoopManager()
            current_status = learning_loop_manager.get_current_status()

            print(f"\n🔄 학습 루프 매니저:")
            print(f"  - 상태: {current_status.get('status', 'unknown')}")
            print(f"  - 실행 중: {learning_loop_manager.is_running}")
            print(f"  - 현재 사이클: {learning_loop_manager.current_cycle}")

        except ImportError as e:
            print(f"⚠️ 학습 루프 매니저를 찾을 수 없습니다: {e}")

        # 통합 학습 시스템 확인
        try:
            from DuRiCore.unified_learning_system import UnifiedLearningSystem

            unified_system = UnifiedLearningSystem()
            print(f"\n🎓 통합 학습 시스템:")
            print(f"  - 총 학습 세션: {len(unified_system.learning_sessions)}")
            print(f"  - 총 진화 세션: {len(unified_system.evolution_sessions)}")

            # 활성 세션 확인
            active_learning = [
                s for s in unified_system.learning_sessions if s.status.value == "in_progress"
            ]
            active_evolution = [
                s for s in unified_system.evolution_sessions if s.status.value == "in_progress"
            ]

            print(f"  - 활성 학습 세션: {len(active_learning)}")
            print(f"  - 활성 진화 세션: {len(active_evolution)}")

        except ImportError as e:
            print(f"⚠️ 통합 학습 시스템을 찾을 수 없습니다: {e}")

        # 전체 상태 요약
        print(f"\n📊 전체 학습 상태 요약:")

        # 각 시스템의 활성 상태를 확인
        systems_status = []

        try:
            if "autonomous_learner" in locals() and autonomous_learner.is_running:
                systems_status.append("자율 학습 시스템")
        except:
            pass

        try:
            if "realtime_learner" in locals() and realtime_learner.is_active:
                systems_status.append("실시간 학습 시스템")
        except:
            pass

        try:
            if "learning_loop_manager" in locals() and learning_loop_manager.is_running:
                systems_status.append("학습 루프 매니저")
        except:
            pass

        try:
            if "unified_system" in locals() and (
                len(active_learning) > 0 or len(active_evolution) > 0
            ):
                systems_status.append("통합 학습 시스템")
        except:
            pass

        if systems_status:
            print(f"  ✅ 활성화된 시스템: {', '.join(systems_status)}")
            print(f"  🎓 현재 학습 상태: 학습 중")
        else:
            print(f"  😴 활성화된 시스템: 없음")
            print(f"  🎓 현재 학습 상태: 대기 중")

        print("\n" + "=" * 50)

    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        logger.error(f"자율 학습 상태 확인 중 오류: {e}")


if __name__ == "__main__":
    asyncio.run(check_autonomous_status())
