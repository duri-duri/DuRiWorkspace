#!/usr/bin/env python3
"""
윤리 판단 엔진 테스트 스크립트
4개 윤리 모듈 통합 테스트
"""

import os
import sys
from datetime import datetime

# DuRiCore 모듈 임포트를 위한 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), "DuRiCore"))

from DuRiCore.DuRiCore.modules.ethical_reasoning import EthicalReasoningEngine


def test_ethical_engine():
    """윤리 판단 엔진 테스트"""
    print("⚖️ 윤리 판단 엔진 테스트 시작...")

    ethical_engine = EthicalReasoningEngine()
    # 테스트 케이스들
    test_cases = [
        {
            "situation": "회사에서 비밀 정보를 알게 되었는데, 이 정보가 공개되면 회사에 큰 피해가 있을 것 같습니다. 하지만 이 정보를 숨기는 것이 윤리적으로 옳은지 의문이 듭니다.",
            "context": {
                "dilemma_description": "비밀 정보 공개 여부",
                "complexity": "high",
                "stakeholders": 3,
                "novelty": "medium",
            },
        },
        {
            "situation": "친구가 시험에서 부정행위를 했는데, 이를 고발해야 할지 망설이고 있습니다. 친구를 보호하고 싶지만, 공정성도 중요합니다.",
            "context": {
                "dilemma_description": "친구 부정행위 고발",
                "complexity": "medium",
                "stakeholders": 2,
                "novelty": "low",
            },
        },
        {
            "situation": "환경을 위해 자동차 대신 대중교통을 이용하는 것이 좋지만, 시간이 오래 걸려서 불편합니다. 개인의 편의와 공공의 이익 사이에서 갈등합니다.",
            "context": {
                "dilemma_description": "개인 편의 vs 공공 이익",
                "complexity": "medium",
                "stakeholders": 2,
                "novelty": "low",
            },
        },
        {
            "situation": "인공지능이 인간의 일자리를 대체할 것이라는 우려가 있습니다. 기술 발전의 이익과 사회적 비용 사이의 균형을 어떻게 맞춰야 할까요?",
            "context": {
                "dilemma_description": "AI 발전과 일자리 문제",
                "complexity": "high",
                "stakeholders": 5,
                "novelty": "high",
            },
        },
        {
            "situation": "가족의 생명을 구하기 위해 거짓말을 해야 하는 상황입니다. 진실의 가치와 생명의 가치 중 어느 것이 더 중요한가요?",
            "context": {
                "dilemma_description": "진실 vs 생명",
                "complexity": "high",
                "stakeholders": 3,
                "novelty": "medium",
            },
        },
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n--- 테스트 케이스 {i} ---")
        print(f"상황: {test_case['situation'][:50]}...")
        print(f"맥락: {test_case['context']}")

        # 윤리 분석 실행
        result = ethical_engine.analyze_ethical_dilemma(
            test_case["situation"], test_case["context"]
        )

        print(f"윤리 딜레마: {result.ethical_dilemma}")
        print(f"윤리 점수: {result.ethical_score:.2f}")
        print(f"신뢰도: {result.confidence:.2f}")
        print(f"윤리 원칙: {result.ethical_principles}")
        print(f"추론 과정: {len(result.reasoning_process)}단계")
        print(f"권장 행동: {result.recommended_action}")

        # 상세 결과 출력
        print(f"  - 추론 과정: {result.reasoning_process}")
        print(f"  - 이해관계자: {result.stakeholder_analysis}")

    # 윤리 통계 출력
    stats = ethical_engine.get_ethical_stats()
    print(f"\n📊 윤리 통계:")
    print(f"  - 총 윤리 분석: {stats['total_ethical_analyses']}")
    print(f"  - 평균 윤리 점수: {stats['average_ethical_score']:.2f}")
    print(f"  - 가장 일반적인 원칙: {stats['most_common_principle']}")
    print(f"  - 복잡도 분포: {stats['complexity_distribution']}")

    print("\n✅ 윤리 판단 엔진 테스트 완료!")


def test_individual_systems():
    """개별 윤리 시스템 테스트"""
    print("\n🔍 개별 윤리 시스템 테스트...")

    from DuRiCore.DuRiCore.modules.ethical_reasoning import (
        AdvancedEthicalReasoningSystem, CreativeThinkingService,
        EnhancedEthicalSystem, SocialIntelligenceService)

    # 창의적 사고 시스템 테스트
    print("\n--- 창의적 사고 시스템 ---")
    creative_system = CreativeThinkingService()
    creative_result = creative_system.analyze_creative_context(
        {"complexity": "high", "novelty": "high", "stakeholders": 5}
    )
    print(f"창의성 점수: {creative_result['creativity_score']:.2f}")
    print(f"창의적 인사이트: {creative_result['creative_insights']}")

    # 향상된 윤리 시스템 테스트
    print("\n--- 향상된 윤리 시스템 ---")
    enhanced_ethical = EnhancedEthicalSystem()
    ethical_result = enhanced_ethical.analyze_ethical_situation(
        "윤리적 딜레마 상황에서 정의와 공정성을 고려해야 합니다."
    )
    print(f"윤리 점수: {ethical_result['ethical_score']:.2f}")
    print(f"적용된 원칙: {ethical_result['applied_principles']}")

    # 고급 윤리 추론 시스템 테스트
    print("\n--- 고급 윤리 추론 시스템 ---")
    advanced_ethical = AdvancedEthicalReasoningSystem()
    advanced_result = advanced_ethical.analyze_ethical_dilemma(
        "만약 이렇게 한다면 결과가 좋을 것이지만, 그런데 다른 관점에서는 문제가 될 수 있습니다."
    )
    print(f"추론 점수: {advanced_result['reasoning_score']:.2f}")
    print(f"윤리적 프레임워크: {advanced_result['ethical_frameworks']}")

    # 사회적 지능 시스템 테스트
    print("\n--- 사회적 지능 시스템 ---")
    social_intelligence = SocialIntelligenceService()
    social_result = social_intelligence.process_conversation(
        {
            "input": "친구들과 함께 협력하여 문제를 해결했습니다. 대화를 통해 서로를 이해할 수 있었습니다."
        }
    )
    print(f"사회적 점수: {social_result['social_score']:.2f}")
    print(f"상호작용 타입: {social_result['social_dynamics']['interaction_type']}")

    print("\n✅ 개별 윤리 시스템 테스트 완료!")


def test_ethical_scenarios():
    """윤리적 시나리오 테스트"""
    print("\n🎭 윤리적 시나리오 테스트...")

    ethical_engine = EthicalReasoningEngine()

    # 복잡한 윤리적 시나리오들
    scenarios = [
        {
            "name": "트롤리 딜레마",
            "situation": "기차가 다섯 명의 사람을 향해 달려오고 있습니다. 레버를 당기면 기차가 다른 선로로 바뀌어 한 명만 죽게 됩니다. 레버를 당겨야 할까요?",
            "context": {"complexity": "high", "stakeholders": 6, "novelty": "medium"},
        },
        {
            "name": "의료 윤리",
            "situation": "환자가 생명을 구하기 위해 수술이 필요하지만, 수술 비용을 감당할 수 없습니다. 의사로서 어떻게 해야 할까요?",
            "context": {"complexity": "high", "stakeholders": 4, "novelty": "medium"},
        },
        {
            "name": "기업 윤리",
            "situation": "회사에서 환경 오염을 줄이기 위해 비용을 투자해야 하지만, 이로 인해 이익이 줄어들어 직원들을 해고해야 할 수도 있습니다.",
            "context": {"complexity": "high", "stakeholders": 5, "novelty": "medium"},
        },
    ]

    for scenario in scenarios:
        print(f"\n--- {scenario['name']} ---")
        print(f"상황: {scenario['situation']}")

        result = ethical_engine.analyze_ethical_dilemma(
            scenario["situation"], scenario["context"]
        )

        print(f"윤리 점수: {result.ethical_score:.2f}")
        print(f"신뢰도: {result.confidence:.2f}")
        print(f"권장 행동: {result.recommended_action}")
        print(f"윤리 원칙: {result.ethical_principles}")

    print("\n✅ 윤리적 시나리오 테스트 완료!")


def main():
    """메인 테스트 함수"""
    print("🚀 윤리 판단 엔진 테스트 시작!")
    print("=" * 50)

    try:
        # 1. 통합 윤리 판단 엔진 테스트
        test_ethical_engine()

        # 2. 개별 윤리 시스템 테스트
        test_individual_systems()

        # 3. 윤리적 시나리오 테스트
        test_ethical_scenarios()

        print("\n" + "=" * 50)
        print("🎉 모든 윤리 판단 엔진 테스트 완료!")
        print("4개 윤리 모듈이 성공적으로 통합되었습니다.")

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
