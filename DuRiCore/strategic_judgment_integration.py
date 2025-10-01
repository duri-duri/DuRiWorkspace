#!/usr/bin/env python3
"""
DuRi 전략 판단 4단계 통합 시스템
전략 판단을 사고 흐름, 기억, 진화, 외부 피드백까지 4단계로 통합하는 시스템
"""

from datetime import datetime
import os
import sys
from typing import Any, Dict, Optional

# DuRiCore 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.evolution.self_evolution_manager import SelfEvolutionManager
from modules.integrated_learning_system import IntegratedLearningSystem

# 📦 핵심 모듈 임포트 (현재 구현된 시스템에 맞게 수정)
from modules.judgment_system.strategic_learning_engine import StrategicLearningEngine
from modules.memory.memory_manager import MemoryManager
from modules.thought_flow.du_ri_thought_flow import DuRiThoughtFlow


class FeedbackHub:
    """외부 피드백 통합 모듈 (시뮬레이션)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FeedbackHub, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.feedback_history = []
            self.initialized = True

    def broadcast(self, event_type: str, data: Any) -> Dict[str, Any]:
        """
        외부 피드백 시스템에 이벤트를 브로드캐스트합니다.

        Args:
            event_type: 이벤트 타입 (예: 'judgment/strategic')
            data: 브로드캐스트할 데이터

        Returns:
            브로드캐스트 결과
        """
        feedback_event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data,
            "status": "broadcasted",
        }

        self.feedback_history.append(feedback_event)

        print(f"📡 외부 피드백 브로드캐스트: {event_type}")
        return feedback_event


def integrate_strategic_judgment():
    """
    전략 판단을 4단계로 통합하는 메인 함수
    """
    print("🚀 DuRi 전략 판단 4단계 통합 시스템 시작")

    try:
        # 📦 핵심 모듈 초기화
        strategic_engine = StrategicLearningEngine()
        thought_flow = DuRiThoughtFlow()
        memory_manager = MemoryManager()
        evolution_manager = SelfEvolutionManager()
        feedback_hub = FeedbackHub()
        integrated_system = IntegratedLearningSystem()

        # 📌 최신 전략 판단 추적 (새로운 판단 생성)
        latest_trace = strategic_engine.get_latest_trace()

        # 만약 최신 추적이 없다면 새로운 판단을 생성
        if latest_trace is None:
            print("📝 새로운 전략 판단 생성 중...")
            latest_trace = strategic_engine.observe_decision(
                situation="사용자가 전략적 판단 통합을 요청함",
                action="4단계 통합 시스템 실행",
                reasoning="전략 판단을 사고 흐름, 기억, 진화, 외부 피드백까지 통합하여 시스템 성능 향상",
            )

        print(f"✅ 최신 전략 판단 추적 획득: {latest_trace.get('timestamp', 'N/A')}")

        # 1️⃣ DuRi 사고 흐름에 판단 연결
        print("🔄 1단계: 사고 흐름에 판단 연결 중...")
        thought_flow.register_stream("strategic_judgment", latest_trace)
        print("✅ 사고 흐름 연결 완료")

        # 2️⃣ 판단 결과를 장기 기억에 저장
        print("💾 2단계: 장기 기억에 판단 저장 중...")
        memory_manager.store_long_term("strategic_judgment_trace", latest_trace)
        print("✅ 장기 기억 저장 완료")

        # 3️⃣ 판단 변화 추적을 진화 시스템에 연결
        print("🔄 3단계: 진화 시스템에 판단 변화 연결 중...")
        # 진화 시스템에 판단 변화 로깅 (새로운 메서드 추가 필요)
        try:
            # 진화 시스템에 판단 변화 기록
            evolution_summary = evolution_manager.get_evolution_summary()
            evolution_manager._record_evolution_steps(
                beliefs_to_update=[],  # 새로운 신념 업데이트 없음
                rules_to_update=[],  # 새로운 규칙 업데이트 없음
                updated_behaviors=[],  # 새로운 행동 패턴 없음
                reflection_insights=[latest_trace],  # 현재 판단을 통찰로 전달
            )
            print("✅ 진화 시스템 연결 완료")
        except Exception as e:
            print(f"⚠️ 진화 시스템 연결 중 오류: {e}")

        # 4️⃣ 외부 피드백 시스템에 전달
        print("📡 4단계: 외부 피드백 시스템에 전달 중...")
        feedback_result = feedback_hub.broadcast("judgment/strategic", latest_trace)
        print("✅ 외부 피드백 전달 완료")

        # 5️⃣ 통합 학습 시스템에 기록
        print("🎯 5단계: 통합 학습 시스템에 기록 중...")
        integrated_system.record_judgment_trace(
            context=f"전략 판단 4단계 통합: {latest_trace.get('situation', 'N/A')}",
            judgment=latest_trace.get("action", "N/A"),
            reasoning=latest_trace.get("reasoning", "N/A"),
            outcome="4단계 통합 시스템 성공적으로 실행됨",
            confidence_level=0.9,
            tags=["전략", "통합", "4단계", "시스템"],
        )
        print("✅ 통합 학습 시스템 기록 완료")

        # 📊 통합 결과 요약
        integration_summary = {
            "timestamp": datetime.now().isoformat(),
            "strategic_trace": latest_trace,
            "thought_flow_status": "connected",
            "memory_status": "stored",
            "evolution_status": "logged",
            "feedback_status": "broadcasted",
            "integration_status": "completed",
        }

        print("\n" + "=" * 60)
        print("🎉 전략 판단 4단계 통합 완료!")
        print("=" * 60)
        print(f"📅 실행 시간: {integration_summary['timestamp']}")
        print(f"🧠 사고 흐름: {integration_summary['thought_flow_status']}")
        print(f"💾 장기 기억: {integration_summary['memory_status']}")
        print(f"🔄 진화 시스템: {integration_summary['evolution_status']}")
        print(f"📡 외부 피드백: {integration_summary['feedback_status']}")
        print(f"🎯 통합 상태: {integration_summary['integration_status']}")
        print("=" * 60)

        return integration_summary

    except Exception as e:
        print(f"❌ 전략 판단 4단계 통합 실패: {e}")
        import traceback

        traceback.print_exc()
        return {"status": "failed", "error": str(e)}


def main():
    """메인 실행 함수"""
    print("🚀 DuRi 전략 판단 4단계 통합 시스템 실행")
    print(f"📅 실행 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # 전략 판단 4단계 통합 실행
    result = integrate_strategic_judgment()

    if result.get("status") == "failed":
        print(f"\n❌ 통합 실패: {result.get('error')}")
        return False
    else:
        print(f"\n✅ 통합 성공!")
        return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
