#!/usr/bin/env python3
"""
DuRiCore 테스트 스크립트
새로운 감정 엔진, 자기 진화 엔진, 메인 루프 테스트
"""

import asyncio
import os
import sys
from datetime import datetime

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "DuRiCore"))

from DuRiCore.DuRiCore.core.main_loop import InputData, MainLoop
from DuRiCore.DuRiCore.modules.emotion_engine import EmotionEngine
from DuRiCore.DuRiCore.modules.self_evolution import SelfEvolutionEngine


async def test_emotion_engine():
    """감정 엔진 테스트"""
    print("🧠 감정 엔진 테스트 시작...")

    emotion_engine = EmotionEngine()

    # 테스트 케이스들
    test_cases = [
        {
            "text": "오늘 정말 기분이 좋아요! 새로운 프로젝트가 성공했어요.",
            "context": {"type": "work", "user_mood": "positive"},
        },
        {
            "text": "너무 화가 나요. 계속 실패만 하고 있어요.",
            "context": {"type": "personal", "user_mood": "negative"},
        },
        {
            "text": "조금 걱정이 되네요. 내일 중요한 회의가 있어요.",
            "context": {"type": "work", "user_mood": "concerned"},
        },
        {
            "text": "그냥 평범한 하루였어요.",
            "context": {"type": "general", "user_mood": "neutral"},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"입력: {test_case['text']}")
        print(f"맥락: {test_case['context']}")

        # 감정 분석 실행
        analysis = emotion_engine.analyze_complex_emotion(test_case)

        print(f"주요 감정: {analysis.primary_emotion}")
        print(f"보조 감정: {analysis.secondary_emotions}")
        print(f"강도: {analysis.intensity:.2f}")
        print(f"신뢰도: {analysis.confidence:.2f}")
        print(f"맥락 적합성: {analysis.context_fit:.2f}")
        print(f"감정-이성 균형: {analysis.emotion_reason_balance['balance_type']}")
        print(f"공감적 반응: {analysis.empathetic_response}")

    print("\n✅ 감정 엔진 테스트 완료!")


async def test_self_evolution_engine():
    """자기 진화 엔진 테스트"""
    print("\n🔄 자기 진화 엔진 테스트 시작...")

    evolution_engine = SelfEvolutionEngine()

    # 자기 진화 분석 실행
    evolution_result = evolution_engine.analyze_and_evolve()

    print(f"진화 점수: {evolution_result.evolution_score:.2f}")
    print(f"개선 영역 수: {len(evolution_result.improvement_areas)}")
    print(f"진화 방향 수: {len(evolution_result.evolution_directions)}")
    print(f"개선 액션 수: {len(evolution_result.improvement_actions)}")

    # 개선 영역 출력
    if evolution_result.improvement_areas:
        print("\n개선 영역:")
        for area in evolution_result.improvement_areas:
            print(
                f"  - {area['system']}: {area['current_score']:.1f}점 → {area['target_score']}점"
            )

    # 진화 방향 출력
    if evolution_result.evolution_directions:
        print("\n진화 방향:")
        for direction in evolution_result.evolution_directions:
            print(f"  - {direction['system']}: {direction['direction']}")

    print("\n✅ 자기 진화 엔진 테스트 완료!")


async def test_main_loop():
    """메인 루프 테스트"""
    print("\n🔄 메인 루프 테스트 시작...")

    main_loop = MainLoop()

    # 테스트 입력들
    test_inputs = [
        InputData(
            text="안녕하세요! 오늘 기분이 정말 좋아요.",
            context={"type": "social", "user_mood": "positive"},
        ),
        InputData(
            text="프로젝트가 실패해서 너무 속상해요.",
            context={"type": "work", "user_mood": "negative"},
        ),
        InputData(
            text="내일 중요한 발표가 있어서 긴장돼요.",
            context={"type": "work", "user_mood": "anxious"},
        ),
    ]

    for i, input_data in enumerate(test_inputs, 1):
        print(f"\n--- 메인 루프 테스트 {i} ---")
        print(f"입력: {input_data.text}")

        # 메인 루프 실행
        result = await main_loop.process_input(input_data)

        print(f"감정: {result['emotional_analysis'].primary_emotion}")
        print(f"판단: {result['judgment'].decision}")
        print(f"실행 성공: {result['execution'].success}")
        print(f"인사이트 수: {len(result['reflection'].insights)}")
        print(f"사이클 시간: {result['cycle_time']:.3f}초")

    # 시스템 상태 출력
    status = main_loop.get_system_status()
    print(f"\n시스템 상태:")
    print(f"  - 총 사이클: {status['performance_stats']['total_cycles']}")
    print(f"  - 메모리 수: {status['memory_count']}")
    print(f"  - 현재 감정: {status['current_state']['emotional_state']}")

    # 메모리 요약 출력
    memory_summary = main_loop.get_memory_summary(limit=3)
    print(f"\n최근 메모리:")
    for memory in memory_summary:
        print(f"  - {memory['input']} → {memory['emotion']} → {memory['decision']}")

    print("\n✅ 메인 루프 테스트 완료!")


async def test_integration():
    """통합 테스트"""
    print("\n🔗 통합 테스트 시작...")

    # 메인 루프 생성
    main_loop = MainLoop()

    # 복잡한 시나리오 테스트
    complex_input = InputData(
        text="오늘 팀 회의에서 내 아이디어가 거절당했어요. 처음에는 화가 났지만, 지금은 그들의 의견도 이해가 돼요.",
        context={
            "type": "work",
            "user_mood": "mixed",
            "complexity": "high",
            "emotional_intensity": "medium",
        },
    )

    print(f"복잡한 입력: {complex_input.text}")
    print(f"맥락: {complex_input.context}")

    # 메인 루프 실행
    result = await main_loop.process_input(complex_input)

    print(f"\n결과 분석:")
    print(
        f"  - 감정: {result['emotional_analysis'].primary_emotion} (강도: {result['emotional_analysis'].intensity:.2f})"
    )
    print(f"  - 판단: {result['judgment'].decision}")
    print(f"  - 신뢰도: {result['judgment'].confidence:.2f}")
    print(f"  - 실행 성공: {result['execution'].success}")
    print(f"  - 인사이트: {len(result['reflection'].insights)}개")
    print(f"  - 교훈: {len(result['reflection'].lessons_learned)}개")
    print(f"  - 개선 제안: {len(result['reflection'].improvement_suggestions)}개")

    # 성능 통계
    print(f"\n성능 통계:")
    stats = result["performance_stats"]
    print(f"  - 총 사이클: {stats['total_cycles']}")
    print(f"  - 평균 사이클 시간: {stats.get('average_cycle_time', 0):.3f}초")
    print(f"  - 마지막 사이클 시간: {stats['last_cycle_time']:.3f}초")

    print("\n✅ 통합 테스트 완료!")


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRiCore 테스트 시작!")
    print("=" * 50)

    try:
        # 1. 감정 엔진 테스트
        await test_emotion_engine()

        # 2. 자기 진화 엔진 테스트
        await test_self_evolution_engine()

        # 3. 메인 루프 테스트
        await test_main_loop()

        # 4. 통합 테스트
        await test_integration()

        print("\n" + "=" * 50)
        print("🎉 모든 테스트 완료!")
        print("DuRiCore가 성공적으로 작동하고 있습니다.")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
