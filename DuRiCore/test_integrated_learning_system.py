#!/usr/bin/env python3
"""
DuRi 3단계 통합 학습 시스템 테스트
판단 기록 → 자가 반성 → 자기개선의 완전한 진화 사이클을 테스트합니다.
"""

import json
import os
import sys
from datetime import datetime

# DuRiCore 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.evolution import SelfEvolutionManager  # noqa: E402
from modules.integrated_learning_system import IntegratedLearningSystem  # noqa: E402
from modules.judgment_system import JudgmentTraceLogger  # noqa: E402
from modules.thought_flow import SelfReflectionLoop  # noqa: E402


def test_judgment_trace_system():
    """1단계: 판단 과정 기록 시스템 테스트"""
    print("\n" + "=" * 50)
    print("📝 1단계: 판단 과정 기록 시스템 테스트")
    print("=" * 50)

    # 판단 기록 시스템 초기화
    judgment_logger = JudgmentTraceLogger()

    # 테스트 판단 기록들 생성
    test_judgments = [
        {
            "context": "사용자가 복잡한 코딩 문제를 요청함",
            "judgment": "단계별 접근 방식으로 문제를 분석해야 함",
            "reasoning": "복잡한 문제는 작은 단위로 나누어 해결하는 것이 효과적",
            "outcome": "문제를 3단계로 나누어 해결 방안 제시",
            "confidence_level": 0.8,
            "tags": ["복잡", "단계별", "분석"],
        },
        {
            "context": "사용자가 긴급한 버그 수정을 요청함",
            "judgment": "빠른 임시 해결책을 먼저 제시하고 근본 원인 분석은 후속으로",
            "reasoning": "긴급 상황에서는 사용자 경험을 우선시해야 함",
            "outcome": "임시 패치 적용 후 근본 원인 분석 진행",
            "confidence_level": 0.6,
            "tags": ["긴급", "버그", "임시해결"],
        },
        {
            "context": "사용자가 성능 최적화 방법을 문의함",
            "judgment": "현재 코드의 병목 지점을 먼저 분석해야 함",
            "reasoning": "성능 최적화는 측정 가능한 데이터 기반으로 접근해야 함",
            "outcome": "프로파일링 도구 사용을 권장하고 구체적인 측정 방법 제시",
            "confidence_level": 0.9,
            "tags": ["성능", "최적화", "프로파일링"],
        },
    ]

    # 판단 기록들 저장
    recorded_traces = []
    for judgment in test_judgments:
        trace = judgment_logger.record_judgment_trace(
            context=judgment["context"],
            judgment=judgment["judgment"],
            reasoning=judgment["reasoning"],
            outcome=judgment["outcome"],
            confidence_level=judgment["confidence_level"],
            tags=judgment["tags"],
        )
        recorded_traces.append(trace)
        print(f"✅ 판단 기록 저장됨: {trace.timestamp}")

    # 판단 기록 요약 확인
    summary = judgment_logger.get_traces_summary()
    print("\n📊 판단 기록 요약:")
    print(f"  - 총 기록 수: {summary['total_traces']}")
    print(f"  - 평균 신뢰도: {summary['average_confidence']:.2f}")
    print(f"  - 태그 분포: {summary['tag_distribution']}")

    return recorded_traces


def test_reflection_loop():
    """2단계: 자가 반성 루프 테스트"""
    print("\n" + "=" * 50)
    print("🔍 2단계: 자가 반성 루프 테스트")
    print("=" * 50)

    # 자가 반성 루프 시스템 초기화
    reflection_loop = SelfReflectionLoop()

    # 반성 루프 실행
    reflection_result = reflection_loop.reflection_loop("user_request")

    print("✅ 반성 루프 실행 완료:")
    print(f"  - 분석된 판단 수: {reflection_result.get('traces_analyzed', 0)}")
    print(f"  - 생성된 통찰 수: {reflection_result.get('new_insights', 0)}")
    print(f"  - 업데이트된 신념 수: {reflection_result.get('beliefs_updated', 0)}")
    print(f"  - 업데이트된 규칙 수: {reflection_result.get('rules_updated', 0)}")

    return reflection_result


def test_self_improvement_sequence():
    """3단계: 자기개선 시퀀스 테스트"""
    print("\n" + "=" * 50)
    print("🚀 3단계: 자기개선 시퀀스 테스트")
    print("=" * 50)

    # 자기개선 시퀀스 시스템 초기화
    evolution_manager = SelfEvolutionManager()

    # 자기개선 시퀀스 실행
    evolution_result = evolution_manager.execute_self_improvement_sequence()

    print("✅ 자기개선 시퀀스 실행 완료:")
    print(f"  - 업데이트된 신념 수: {evolution_result.get('beliefs_updated', 0)}")
    print(f"  - 업데이트된 규칙 수: {evolution_result.get('rules_updated', 0)}")
    print(f"  - 업데이트된 행동 패턴 수: {evolution_result.get('behaviors_updated', 0)}")
    print(f"  - 진화 단계 수: {evolution_result.get('evolution_steps', 0)}")

    return evolution_result


def test_integrated_learning_system():
    """통합 학습 시스템 전체 테스트"""
    print("\n" + "=" * 50)
    print("🔄 통합 학습 시스템 전체 테스트")
    print("=" * 50)

    # 통합 학습 시스템 초기화
    integrated_system = IntegratedLearningSystem()

    # 완전한 학습 사이클 실행
    cycle_result = integrated_system.execute_full_learning_cycle("user_request")

    print("✅ 통합 학습 사이클 완료:")
    print(f"  - 사이클 ID: {cycle_result.get('cycle_id', 'N/A')}")
    print(f"  - 트리거 타입: {cycle_result.get('trigger_type', 'N/A')}")
    print(f"  - 판단 기록 수: {cycle_result.get('judgment_traces', 0)}")
    print(f"  - 반성 통찰 수: {cycle_result.get('reflection_insights', 0)}")
    print(f"  - 진화 단계 수: {cycle_result.get('evolution_steps', 0)}")
    print(f"  - 소요 시간: {cycle_result.get('cycle_duration', 0):.2f}초")

    # 시스템 요약 확인
    system_summary = integrated_system.get_learning_system_summary()
    print("\n📊 시스템 요약:")
    print(f"  - 판단 시스템: {system_summary.get('judgment_system', {}).get('total_traces', 0)}개 기록")
    print(f"  - 반성 시스템: {system_summary.get('reflection_system', {}).get('total_insights', 0)}개 통찰")
    print(f"  - 진화 시스템: {system_summary.get('evolution_system', {}).get('total_evolution_steps', 0)}개 단계")
    print(f"  - 총 학습 사이클: {system_summary.get('total_learning_cycles', 0)}개")

    return cycle_result


def test_judgment_trace_recording():
    """판단 기록 기능 테스트"""
    print("\n" + "=" * 50)
    print("📝 판단 기록 기능 테스트")
    print("=" * 50)

    integrated_system = IntegratedLearningSystem()

    # 새로운 판단 기록
    judgment_result = integrated_system.record_judgment_trace(
        context="테스트 상황에서 복잡한 결정을 내려야 함",
        judgment="체계적인 분석 후 단계별 접근 방식을 선택함",
        reasoning="복잡한 문제는 구조화된 접근이 효과적이며, 리스크를 최소화할 수 있음",
        outcome="문제를 5단계로 분해하여 각 단계별 해결책을 제시함",
        confidence_level=0.85,
        tags=["테스트", "복잡", "체계적", "단계별"],
    )

    print(f"✅ 판단 기록 결과: {judgment_result}")

    return judgment_result


def main():
    """메인 테스트 함수"""
    print("🚀 DuRi 3단계 통합 학습 시스템 테스트 시작")
    print(f"📅 테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # 1단계 테스트
        recorded_traces = test_judgment_trace_system()

        # 2단계 테스트
        reflection_result = test_reflection_loop()

        # 3단계 테스트
        evolution_result = test_self_improvement_sequence()

        # 통합 시스템 테스트
        cycle_result = test_integrated_learning_system()

        # 판단 기록 기능 테스트
        judgment_result = test_judgment_trace_recording()

        print("\n" + "=" * 50)
        print("🎉 모든 테스트 완료!")
        print("=" * 50)

        # 최종 결과 요약
        final_summary = {
            "test_timestamp": datetime.now().isoformat(),
            "judgment_traces_recorded": len(recorded_traces),
            "reflection_insights_generated": reflection_result.get("new_insights", 0),
            "evolution_steps_completed": evolution_result.get("evolution_steps", 0),
            "full_cycle_completed": cycle_result.get("status") == "success",
            "judgment_recording_success": judgment_result.get("status") == "success",
        }

        print("📊 최종 테스트 결과:")
        for key, value in final_summary.items():
            if key != "test_timestamp":
                print(f"  - {key}: {value}")

        # 결과를 JSON 파일로 저장
        with open(
            "DuRiCore/test_results_integrated_learning_system.json",
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(final_summary, f, ensure_ascii=False, indent=2)

        print("\n💾 테스트 결과가 'test_results_integrated_learning_system.json'에 저장되었습니다.")

        return True

    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
