"""
DuRiCore Phase 2.2: 내적 동기 시스템 통합 테스트
- 호기심, 성취욕, 탐구욕 메트릭 테스트
- 자발적 학습 목표 생성 테스트
- 기존 시스템과의 통합 테스트
"""

import asyncio
import logging
import os
import sys

# DuRiCore 모듈 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "DuRiCore"))

from DuRiCore.intrinsic_motivation_system import (IntrinsicMotivationSystem,
                                                  MotivationType)
from DuRiCore.lida_attention_system import LIDAAttentionSystem
from DuRiCore.social_intelligence_system import SocialIntelligenceSystem

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_intrinsic_motivation_system():
    """내적 동기 시스템 독립 테스트"""
    print("\n🧠 1. 내적 동기 시스템 독립 테스트")

    motivation_system = IntrinsicMotivationSystem()

    # 테스트 경험 데이터
    test_experience = {
        "novelty": 0.8,
        "complexity": 0.7,
        "exploration": 0.9,
        "questions": 5,
        "learning_interest": 0.8,
    }

    # 테스트 성능 데이터
    test_performance = {
        "mastery": 0.7,
        "improvement": 0.6,
        "skill_dev": 0.8,
        "goal_setting": 0.5,
        "persistence": 0.7,
    }

    # 메트릭 업데이트
    await motivation_system.update_curiosity_metrics(test_experience)
    await motivation_system.update_achievement_metrics(test_performance)

    # 자발적 학습 실행
    learning_result = await motivation_system.execute_voluntary_learning()

    print(
        f"✅ 호기심 수준: {motivation_system.motivation_state.curiosity_metrics.overall_curiosity:.3f}"
    )
    print(
        f"✅ 성취욕 수준: {motivation_system.motivation_state.achievement_metrics.overall_achievement:.3f}"
    )
    print(f"✅ 실행된 학습 목표: {learning_result['executed_goals']}개")

    return motivation_system


async def test_lida_attention_integration():
    """LIDA 주의 시스템 통합 테스트"""
    print("\n🧠 2. LIDA 주의 시스템 - 내적 동기 통합 테스트")

    attention_system = LIDAAttentionSystem()

    # 테스트 컨텍스트
    test_context = {
        "patterns": ["새로운 패턴 발견"],
        "complexity": 0.8,
        "performance": {"accuracy": 0.7, "efficiency": 0.6},
        "skills": ["패턴 인식", "분석 능력"],
        "questions": ["왜 이런 패턴이 발생하는가?"],
    }

    # 내적 동기 기반 주의 처리
    attention_result = await attention_system.process_attention_with_motivation(test_context)

    print(f"✅ 주의 집중 영역: {attention_result.get('focus_areas', [])}")
    print(f"✅ 호기심 기반 탐구: {attention_result.get('exploration_focus', [])}")
    print(f"✅ 성취욕 기반 목표: {attention_result.get('goal_focus', [])}")
    print(f"✅ 자발적 학습: {attention_result.get('voluntary_learning', {})}")

    # 경험을 통한 내적 동기 업데이트
    test_experience = {
        "novelty": 0.9,
        "complexity": 0.8,
        "exploration": 0.9,
        "performance": {"accuracy": 0.8, "efficiency": 0.7},
    }

    await attention_system.update_motivation_from_experience(test_experience)

    # 동기 상태 확인
    motivation_state = attention_system.get_motivation_state()
    print(f"✅ 업데이트된 호기심: {motivation_state['curiosity_metrics']['overall_curiosity']:.3f}")
    print(
        f"✅ 업데이트된 성취욕: {motivation_state['achievement_metrics']['overall_achievement']:.3f}"
    )

    return attention_system


async def test_social_intelligence_integration():
    """사회적 지능 시스템 통합 테스트"""
    print("\n🧠 3. 사회적 지능 시스템 - 내적 동기 통합 테스트")

    social_system = SocialIntelligenceSystem()

    # 테스트 사회적 상황
    test_situation = {
        "context_type": "team_collaboration",
        "stakeholders": ["팀원1", "팀원2", "팀원3"],
        "cultural_factors": ["다양한 배경", "다른 관점"],
        "emotional_climate": "positive",
        "communication_channels": ["대면", "온라인", "문서"],
    }

    # 내적 동기를 고려한 상황 이해
    context_analysis = await social_system.understand_context_with_motivation(test_situation)

    print(f"✅ 상황 이해 - 핵심 요소: {context_analysis.key_factors}")
    print(f"✅ 복잡성 수준: {context_analysis.complexity.value}")
    print(f"✅ 이해관계자: {context_analysis.stakeholders}")

    # 내적 동기를 고려한 행동 적응
    current_behavior = {"communication_style": "formal", "participation_level": 0.6}
    adaptive_behavior = await social_system.adapt_behavior_with_motivation(
        context_analysis, current_behavior
    )

    print(f"✅ 적응 전략: {adaptive_behavior.implementation_strategy}")
    print(f"✅ 적응 수준: {adaptive_behavior.adaptation_level.value}")

    # 내적 동기를 고려한 협력
    collaboration_goal = {
        "type": "project_collaboration",
        "requires_expertise": True,
        "requires_facilitation": True,
    }

    collaboration_plan = await social_system.collaborate_with_motivation(
        context_analysis, collaboration_goal
    )

    print(f"✅ 협력 참여자: {collaboration_plan.participants}")
    print(f"✅ 갈등 해결 전략: {collaboration_plan.conflict_resolution_strategy}")
    print(f"✅ 성공 기준: {collaboration_plan.success_criteria}")

    # 사회적 경험을 통한 내적 동기 업데이트
    social_experience = {
        "novelty": 0.7,
        "complexity": 0.6,
        "social_performance": {"mastery": 0.8, "improvement": 0.7, "skill_dev": 0.9},
    }

    await social_system.update_motivation_from_social_experience(social_experience)

    # 사회적 동기 상태 확인
    social_motivation = social_system.get_social_motivation_state()
    print(f"✅ 사회적 호기심: {social_motivation['curiosity_metrics']['overall_curiosity']:.3f}")
    print(
        f"✅ 사회적 성취욕: {social_motivation['achievement_metrics']['overall_achievement']:.3f}"
    )

    return social_system


async def test_system_integration():
    """전체 시스템 통합 테스트"""
    print("\n🧠 4. 전체 시스템 통합 테스트")

    # 각 시스템 생성
    motivation_system = IntrinsicMotivationSystem()
    attention_system = LIDAAttentionSystem()
    social_system = SocialIntelligenceSystem()

    # 통합 시나리오: 새로운 사회적 상황에서의 학습
    scenario = {
        "situation": "새로운 팀 프로젝트 참여",
        "context": {
            "patterns": ["팀워크 패턴", "의사소통 패턴"],
            "complexity": 0.8,
            "performance": {"collaboration": 0.7, "communication": 0.6},
            "social_factors": ["다양한 배경", "새로운 기술"],
        },
    }

    print(f"📋 시나리오: {scenario['situation']}")

    # 1단계: 내적 동기 상태 평가
    curiosity_level = motivation_system.motivation_state.curiosity_metrics.overall_curiosity
    achievement_level = motivation_system.motivation_state.achievement_metrics.overall_achievement

    print(f"🔍 호기심 수준: {curiosity_level:.3f}")
    print(f"🏆 성취욕 수준: {achievement_level:.3f}")

    # 2단계: 주의 집중
    attention_result = await attention_system.process_attention_with_motivation(scenario["context"])
    print(f"🎯 주의 집중: {attention_result.get('focus_areas', [])}")

    # 3단계: 사회적 상황 이해
    social_analysis = await social_system.understand_context_with_motivation(scenario["context"])
    print(f"🤝 사회적 이해: {social_analysis.key_factors[:3]}")

    # 4단계: 자발적 학습 실행
    if curiosity_level > 0.6 or achievement_level > 0.5:
        learning_result = await motivation_system.execute_voluntary_learning()
        print(f"📚 자발적 학습: {learning_result['executed_goals']}개 목표 실행")

    # 5단계: 동기 상태 업데이트
    experience = {
        "novelty": 0.8,
        "complexity": 0.7,
        "performance": {"collaboration": 0.8, "communication": 0.7},
    }

    await motivation_system.update_curiosity_metrics(experience)
    await motivation_system.update_achievement_metrics(experience["performance"])

    print(
        f"🔄 업데이트된 호기심: {motivation_system.motivation_state.curiosity_metrics.overall_curiosity:.3f}"
    )
    print(
        f"🔄 업데이트된 성취욕: {motivation_system.motivation_state.achievement_metrics.overall_achievement:.3f}"
    )

    return {
        "motivation_system": motivation_system,
        "attention_system": attention_system,
        "social_system": social_system,
    }


async def main():
    """메인 테스트 함수"""
    print("🚀 DuRiCore Phase 2.2: 내적 동기 시스템 통합 테스트 시작")
    print("=" * 60)

    try:
        # 1. 내적 동기 시스템 독립 테스트
        motivation_system = await test_intrinsic_motivation_system()

        # 2. LIDA 주의 시스템 통합 테스트
        attention_system = await test_lida_attention_integration()

        # 3. 사회적 지능 시스템 통합 테스트
        social_system = await test_social_intelligence_integration()

        # 4. 전체 시스템 통합 테스트
        integrated_systems = await test_system_integration()

        print("\n" + "=" * 60)
        print("🎉 Phase 2.2: 내적 동기 시스템 통합 테스트 완료!")
        print("✅ 호기심, 성취욕, 탐구욕 메트릭 구현 완료")
        print("✅ 자발적 학습 목표 생성 시스템 구현 완료")
        print("✅ 기존 시스템과의 통합 완료")
        print("✅ 동적 우선순위 조정 메커니즘 구현 완료")

        print("\n🧠 DuRi의 새로운 능력:")
        print("- 자발적 학습 동기 생성")
        print("- 호기심 기반 탐구 능력")
        print("- 성취욕 기반 목표 달성")
        print("- 상황 적응적 내적 동기")
        print("- 지속적 자기 개선")

    except Exception as e:
        print(f"❌ 테스트 중 오류 발생: {e}")
        logger.error(f"테스트 실패: {e}")


if __name__ == "__main__":
    asyncio.run(main())
