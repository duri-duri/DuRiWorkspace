#!/usr/bin/env python3
"""
학습 엔진 테스트 스크립트
12개 학습 모듈 통합 테스트
"""

import os
import sys
from datetime import datetime

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "DuRiCore"))

from DuRiCore.DuRiCore.modules.learning_engine import LearningEngine


def test_learning_engine():
    """학습 엔진 테스트"""
    print("📚 학습 엔진 테스트 시작...")

    learning_engine = LearningEngine()

    # 테스트 케이스들
    test_cases = [
        {
            "content": "인공지능에 대한 깊이 있는 텍스트를 읽었습니다. 머신러닝과 딥러닝의 차이점을 이해하게 되었고, 실제 응용 사례들도 배웠습니다.",
            "learning_type": "text",
            "context": {"complexity": "high", "domain": "technology"},
        },
        {
            "content": "00:01:30 안녕하세요 여러분\n00:01:35 오늘은 인공지능에 대해 알아보겠습니다\n00:01:40 먼저 머신러닝의 기본 개념부터 시작하겠습니다",
            "learning_type": "video",
            "context": {"media_type": "subtitle", "duration": "5:00"},
        },
        {
            "content": "가족과 함께 영화를 보면서 아이의 반응을 관찰했습니다. 아이가 어떤 장면에서 웃고, 어떤 장면에서 집중하는지 알 수 있었습니다.",
            "learning_type": "family",
            "context": {
                "family_members": ["parent", "child"],
                "activity": "movie_watching",
            },
        },
        {
            "content": "오늘 학습한 내용을 다시 생각해보니, 내가 어떤 부분을 잘 이해했고 어떤 부분이 어려웠는지 알 수 있었습니다. 다음에는 더 효율적으로 학습할 수 있을 것 같습니다.",
            "learning_type": "metacognitive",
            "context": {"reflection_level": "high", "self_awareness": "medium"},
        },
        {
            "content": "스스로 학습 계획을 세우고 목표를 설정했습니다. 독립적으로 공부하면서 새로운 지식을 습득할 수 있었습니다.",
            "learning_type": "autonomous",
            "context": {"autonomy_level": "high", "self_direction": "strong"},
        },
        {
            "content": "친구들과 함께 프로젝트를 진행하면서 서로의 아이디어를 공유하고 협력했습니다. 대화를 통해 새로운 관점을 배울 수 있었습니다.",
            "learning_type": "social",
            "context": {"group_size": 5, "interaction_type": "collaborative"},
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"콘텐츠: {test_case['content'][:50]}...")
        print(f"학습 타입: {test_case['learning_type']}")
        print(f"맥락: {test_case['context']}")

        # 학습 처리 실행
        result = learning_engine.process_learning(
            test_case["content"], test_case["learning_type"], test_case["context"]
        )

        print(f"콘텐츠 타입: {result.content_type}")
        print(f"학습 점수: {result.learning_score:.2f}")
        print(f"인사이트: {len(result.insights)}개")
        print(f"향상된 스킬: {len(result.skills_improved)}개")
        print(f"다음 단계: {len(result.next_steps)}개")

        # 상세 결과 출력
        print(f"  - 인사이트: {result.insights}")
        print(f"  - 향상된 스킬: {result.skills_improved}")
        print(f"  - 다음 단계: {result.next_steps}")

    # 학습 통계 출력
    stats = learning_engine.get_learning_stats()
    print(f"\n📊 학습 통계:")
    print(f"  - 총 학습 세션: {stats['total_learning_sessions']}")
    print(f"  - 평균 학습 점수: {stats['average_learning_score']:.2f}")
    print(f"  - 가장 일반적인 콘텐츠 타입: {stats['most_common_content_type']}")
    print(f"  - 향상된 스킬: {stats['skills_improved']}")

    print("\n✅ 학습 엔진 테스트 완료!")


def test_individual_systems():
    """개별 학습 시스템 테스트"""
    print("\n🔍 개별 학습 시스템 테스트...")

    from DuRiCore.DuRiCore.modules.learning_engine import (
        AutonomousLearningController, FamilyLearningSystem,
        MetacognitiveLearningSystem, SocialLearningSystem,
        SubtitleLearningSystem, TextLearningSystem)

    # 텍스트 학습 시스템 테스트
    print("\n--- 텍스트 학습 시스템 ---")
    text_system = TextLearningSystem()
    text_result = text_system.process(
        "인공지능과 머신러닝에 대한 깊이 있는 텍스트를 읽었습니다. 다양한 개념과 실제 응용 사례를 배웠습니다.",
        {"domain": "technology", "complexity": "high"},
    )
    print(f"학습 점수: {text_result['learning_score']:.2f}")
    print(f"핵심 개념: {text_result['knowledge_gained']['key_concepts']}")

    # 자막 학습 시스템 테스트
    print("\n--- 자막 학습 시스템 ---")
    subtitle_system = SubtitleLearningSystem()
    subtitle_result = subtitle_system.process(
        "00:01:30 안녕하세요\n00:01:35 오늘은 AI에 대해 알아보겠습니다\n00:01:40 먼저 기본 개념부터 시작하겠습니다",
        {"media_type": "subtitle"},
    )
    print(f"학습 점수: {subtitle_result['learning_score']:.2f}")
    print(f"자막 수: {subtitle_result['knowledge_gained']['subtitle_count']}")

    # 메타인지 학습 시스템 테스트
    print("\n--- 메타인지 학습 시스템 ---")
    metacognitive_system = MetacognitiveLearningSystem()
    metacognitive_result = metacognitive_system.process(
        "오늘 학습한 내용을 다시 생각해보니, 내가 어떤 부분을 잘 이해했고 어떤 부분이 어려웠는지 알 수 있었습니다.",
        {"reflection_level": "high"},
    )
    print(f"학습 점수: {metacognitive_result['learning_score']:.2f}")
    print(
        f"반성 수준: {metacognitive_result['knowledge_gained']['reflection_level']:.2f}"
    )

    # 가족 학습 시스템 테스트
    print("\n--- 가족 학습 시스템 ---")
    family_system = FamilyLearningSystem()
    family_result = family_system.process(
        "가족과 함께 영화를 보면서 아이의 반응을 관찰했습니다. 아이가 어떤 장면에서 웃고, 어떤 장면에서 집중하는지 알 수 있었습니다.",
        {"family_members": ["parent", "child"]},
    )
    print(f"학습 점수: {family_result['learning_score']:.2f}")
    print(
        f"가족 관계 이해: {family_result['knowledge_gained']['family_relationship']:.2f}"
    )

    # 자율 학습 시스템 테스트
    print("\n--- 자율 학습 시스템 ---")
    autonomous_system = AutonomousLearningController()
    autonomous_result = autonomous_system.process(
        "스스로 학습 계획을 세우고 목표를 설정했습니다. 독립적으로 공부하면서 새로운 지식을 습득할 수 있었습니다.",
        {"autonomy_level": "high"},
    )
    print(f"학습 점수: {autonomous_result['learning_score']:.2f}")
    print(f"자율성 수준: {autonomous_result['knowledge_gained']['autonomy_level']:.2f}")

    # 사회적 학습 시스템 테스트
    print("\n--- 사회적 학습 시스템 ---")
    social_system = SocialLearningSystem()
    social_result = social_system.process(
        "친구들과 함께 프로젝트를 진행하면서 서로의 아이디어를 공유하고 협력했습니다. 대화를 통해 새로운 관점을 배울 수 있었습니다.",
        {"group_size": 5, "interaction_type": "collaborative"},
    )
    print(f"학습 점수: {social_result['learning_score']:.2f}")
    print(
        f"사회적 상호작용: {social_result['knowledge_gained']['social_interaction']:.2f}"
    )

    print("\n✅ 개별 학습 시스템 테스트 완료!")


def main():
    """메인 테스트 함수"""
    print("🚀 학습 엔진 테스트 시작!")
    print("=" * 50)

    try:
        # 1. 통합 학습 엔진 테스트
        test_learning_engine()

        # 2. 개별 학습 시스템 테스트
        test_individual_systems()

        print("\n" + "=" * 50)
        print("🎉 모든 학습 엔진 테스트 완료!")
        print("12개 학습 모듈이 성공적으로 통합되었습니다.")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
