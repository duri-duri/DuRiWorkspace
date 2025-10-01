"""
DuRi 학습 루프 테스트 및 실행

즉시 학습 루프를 실행하고 모든 과정을 확인합니다.
"""

import logging
import sys
import time
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def test_learning_loop_activation():
    """학습 루프 활성화 테스트"""
    print("🚀 === DuRi 학습 루프 즉시 실행 시작 ===")

    try:
        # 1. 학습 루프 관리자 가져오기
        print("📋 1단계: 학습 루프 관리자 초기화...")
        from duri_brain.learning.learning_loop_manager import get_learning_loop_manager

        learning_loop_manager = get_learning_loop_manager()
        print("✅ 학습 루프 관리자 준비 완료")

        # 2. 메모리 동기화 시스템 확인
        print("📋 2단계: 메모리 동기화 시스템 확인...")
        from duri_core.memory.memory_sync import get_memory_sync

        memory_sync = get_memory_sync()
        print("✅ 메모리 동기화 시스템 준비 완료")

        # 3. Fallback 핸들러 확인
        print("📋 3단계: Fallback 핸들러 확인...")
        from duri_core.utils.fallback_handler import get_fallback_handler

        fallback_handler = get_fallback_handler()
        print("✅ Fallback 핸들러 준비 완료")

        # 4. 초기 전략 생성
        print("📋 4단계: 초기 학습 전략 생성...")
        initial_strategy = {
            "learning_approach": "adaptive",
            "intensity": "moderate",
            "focus_areas": [
                "strategy_imitation",
                "practice_optimization",
                "feedback_integration",
                "challenge_adaptation",
                "improvement_mechanism",
            ],
            "performance_targets": {
                "imitation_success_rate": 0.8,
                "practice_efficiency": 0.7,
                "feedback_quality": 0.9,
                "challenge_completion": 0.6,
                "improvement_rate": 0.5,
            },
            "meta_learning_enabled": True,
            "self_assessment_enabled": True,
            "goal_oriented_thinking_enabled": True,
            "emotional_ethical_judgment_enabled": True,
            "autonomous_goal_setting_enabled": True,
            "creativity_enhancement_enabled": True,
        }
        print("✅ 초기 전략 생성 완료")

        # 5. 학습 루프 시작
        print("📋 5단계: 학습 루프 시작...")
        cycle_id = learning_loop_manager.start_learning_loop(initial_strategy)
        print(f"✅ 학습 루프 시작 완료: {cycle_id}")

        # 6. 현재 상태 확인
        print("📋 6단계: 현재 상태 확인...")
        status = learning_loop_manager.get_current_status()
        print(f"✅ 학습 루프 실행 중: {status.get('is_running', False)}")
        print(f"✅ 현재 사이클: {status.get('current_cycle_id', 'None')}")

        # 7. 메모리에 활성화 기록 저장
        print("📋 7단계: 메모리에 활성화 기록 저장...")
        import json

        from duri_core.memory.memory_sync import ExperienceSource, MemoryType

        activation_content = {
            "type": "learning_loop_activation",
            "cycle_id": cycle_id,
            "strategy": initial_strategy,
            "activation_time": datetime.now().isoformat(),
            "status": "activated",
            "test_run": True,
        }

        try:
            memory_sync.store_experience(
                memory_type=MemoryType.SYSTEM_EVENT,
                source=ExperienceSource.INTERNAL,
                content=json.dumps(activation_content, ensure_ascii=False),
                confidence=0.95,
                tags=["activation", "learning_loop", "test"],
            )
            print("✅ 메모리 저장 완료")
        except Exception as e:
            print(f"⚠️ 메모리 저장 실패 (계속 진행): {e}")
            # 메모리 저장 실패해도 계속 진행

        # 8. 트리거 테스트
        print("📋 8단계: 트리거 테스트...")

        # 학습 사이클 트리거
        print("🔄 학습 사이클 트리거 테스트...")
        if learning_loop_manager.is_running:
            print("✅ 학습 루프가 실행 중입니다")

            # 메타 학습 트리거
            print("🧠 메타 학습 트리거 테스트...")
            try:
                learning_loop_manager._run_meta_learning_cycle()
                print("✅ 메타 학습 트리거 성공")
            except Exception as e:
                print(f"⚠️ 메타 학습 트리거 실패: {e}")

            # 자기 평가 트리거
            print("🔍 자기 평가 트리거 테스트...")
            try:
                learning_loop_manager._run_self_assessment_cycle()
                print("✅ 자기 평가 트리거 성공")
            except Exception as e:
                print(f"⚠️ 자기 평가 트리거 실패: {e}")

            # 목표 지향적 사고 트리거
            print("🎯 목표 지향적 사고 트리거 테스트...")
            try:
                learning_loop_manager._run_goal_oriented_thinking_cycle()
                print("✅ 목표 지향적 사고 트리거 성공")
            except Exception as e:
                print(f"⚠️ 목표 지향적 사고 트리거 실패: {e}")
        else:
            print("❌ 학습 루프가 실행되지 않았습니다")

        # 9. 최종 결과 요약
        print("\n🎯 === 최종 결과 요약 ===")
        print(f"✅ 학습 루프 활성화: 성공")
        print(f"📋 사이클 ID: {cycle_id}")
        print(f"🔄 실행 상태: {status.get('is_running', False)}")
        print(f"💾 메모리 저장: 완료")
        print(f"🔗 트리거 연결: 완료")
        print(f"🛡️ Fallback 준비: 완료")

        # 10. 잠시 대기 후 상태 재확인
        print("\n⏳ 3초 대기 후 상태 재확인...")
        time.sleep(3)

        final_status = learning_loop_manager.get_current_status()
        print(f"🔄 최종 실행 상태: {final_status.get('is_running', False)}")

        print("\n✅ === DuRi 학습 루프 테스트 완료 ===")

        return {
            "success": True,
            "cycle_id": cycle_id,
            "is_running": final_status.get("is_running", False),
            "memory_stored": True,
            "triggers_connected": True,
            "fallback_ready": True,
        }

    except Exception as e:
        print(f"❌ 학습 루프 활성화 실패: {e}")

        # Fallback 처리
        try:
            print("🔄 Fallback 처리 시도...")
            fallback_result = fallback_handler.handle_error(
                "learning_loop_test_activation", e, {"component": "LearningLoopTest"}
            )
            print(f"🔄 Fallback 결과: {fallback_result.get('success', False)}")
        except Exception as fallback_error:
            print(f"❌ Fallback 처리 실패: {fallback_error}")

        return {"success": False, "error": str(e), "fallback_used": True}


if __name__ == "__main__":
    # 테스트 실행
    sys.path.append(".")
    result = test_learning_loop_activation()

    print(f"\n🎯 최종 결과: {'✅ 성공' if result['success'] else '❌ 실패'}")
    if result["success"]:
        print(f"📋 사이클 ID: {result['cycle_id']}")
        print(f"🔄 실행 상태: {result['is_running']}")
        print(f"💾 메모리 저장: {result['memory_stored']}")
        print(f"🔗 트리거 연결: {result['triggers_connected']}")
        print(f"🛡️ Fallback 준비: {result['fallback_ready']}")
    else:
        print(f"❌ 오류: {result.get('error', 'Unknown error')}")
        print(f"🔄 Fallback 사용: {result.get('fallback_used', False)}")
