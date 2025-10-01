"""
🧠 DuRi Insight Engine v1.0 종합 데모
목표: 인간의 통찰 과정을 모방한 자가 사고형 AI 시스템 테스트
"""

import logging
import sys
import time
from datetime import datetime

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_insight_engine():
    """Insight Engine 기본 기능 테스트"""
    print("\n🧠 === Insight Engine 기본 기능 테스트 ===")

    try:
        import sys

        sys.path.append(".")
        from duri_brain.learning.insight_engine import get_dual_response_system

        system = get_dual_response_system()

        # 테스트 문제들
        test_problems = [
            "학습 루프가 반복적으로 실패하고 성능 개선이 없음",
            "메모리 사용량이 지속적으로 증가하고 있음",
            "외부 LLM 호출 비용이 예산을 초과하고 있음",
            "사용자 응답 시간이 점진적으로 느려지고 있음",
        ]

        results = []

        for i, problem in enumerate(test_problems, 1):
            print(f"\n📌 테스트 {i}: {problem}")

            result = system.execute_dual_response(problem)
            results.append(result)

            print(f"   결과: {result['status']}")

            if result["status"] == "insight_generated":
                insight = result["insight"]
                print(f"   🧠 통찰: {insight.strategy}")
                print(f"   📊 신뢰도: {insight.confidence:.3f}")
                print(f"   🎯 예상 영향: {insight.expected_impact:.3f}")

        print(f"\n✅ Insight Engine 테스트 완료: {len(results)}개 문제 처리")
        return True

    except Exception as e:
        logger.error(f"❌ Insight Engine 테스트 실패: {e}")
        return False


def test_insight_integration():
    """Insight Engine과 학습 루프 통합 테스트"""
    print("\n🔗 === Insight Engine 통합 테스트 ===")

    try:
        import sys

        sys.path.append(".")
        from duri_brain.learning.insight_integration import get_insight_integrator

        integrator = get_insight_integrator()

        # 통합 활성화
        print("📌 1단계: 통합 활성화")
        integrator.activate_integration()

        # 통찰 강화 학습 실행
        print("📌 2단계: 통찰 강화 학습 실행")
        result = integrator.execute_insight_enhanced_learning()

        print(f"   결과: {result['status']}")

        if result["status"] == "insight_applied":
            print(f"   🧠 적용된 통찰: {result['insight']}")
            print(f"   📊 신뢰도: {result['confidence']:.3f}")

        # 상태 확인
        print("📌 3단계: 통합 상태 확인")
        status = integrator.get_integration_status()

        print(f"   통합 활성화: {status['integration_active']}")
        print(
            f"   이성적 리팩터링 횟수: {status['dual_response_system']['rational_refactor_count']}"
        )
        print(
            f"   통찰 트리거 횟수: {status['dual_response_system']['insight_trigger_count']}"
        )
        print(
            f"   성공한 통찰 수: {status['dual_response_system']['successful_insights']}"
        )
        print(f"   통찰 세션 수: {status['insight_sessions']}")

        print("\n✅ 통합 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 통합 테스트 실패: {e}")
        return False


def test_insight_phases():
    """통찰 단계별 상세 테스트"""
    print("\n📋 === 통찰 단계별 상세 테스트 ===")

    try:
        import sys

        sys.path.append(".")
        from duri_brain.learning.insight_engine import (
            CognitivePauseManager,
            DisruptiveMappingEngine,
            InsightTriggerEngine,
            MetaEvaluator,
            RetrogradeReasoningEngine,
            SemanticDriftGenerator,
        )

        # 1. 인지적 일시정지 테스트
        print("📌 1단계: 인지적 일시정지 테스트")
        pause_manager = CognitivePauseManager()
        pause_result = pause_manager.pause_thought_stream()
        print(f"   결과: {'✅ 성공' if pause_result else '❌ 실패'}")

        # 2. 시맨틱 드리프트 테스트
        print("📌 2단계: 시맨틱 드리프트 테스트")
        drift_generator = SemanticDriftGenerator()
        fragments = drift_generator.generate_semantic_drift()
        print(f"   생성된 조각 수: {len(fragments)}")
        print(f"   조각들: {fragments}")

        # 3. 역방향 추론 테스트
        print("📌 3단계: 역방향 추론 테스트")
        reasoning_engine = RetrogradeReasoningEngine()
        problem = "학습 성능이 지속적으로 저하됨"
        reasoning = reasoning_engine.apply_retrograde_reasoning(problem, fragments)
        print(f"   추론 결과: {reasoning}")

        # 4. 파괴적 구성 테스트
        print("📌 4단계: 파괴적 구성 테스트")
        mapping_engine = DisruptiveMappingEngine()
        candidates = mapping_engine.create_disruptive_composition(reasoning, fragments)
        print(f"   생성된 후보 수: {len(candidates)}")

        for i, candidate in enumerate(candidates, 1):
            print(f"   후보 {i}: {candidate.strategy[:60]}...")
            print(f"     신뢰도: {candidate.confidence:.3f}")
            print(f"     위험도: {candidate.risk_level}")

        # 5. 메타 평가 테스트
        print("📌 5단계: 메타 평가 테스트")
        evaluator = MetaEvaluator()
        best_candidate = evaluator.select_best_candidate(candidates)

        if best_candidate:
            print(f"   최고 후보: {best_candidate.strategy[:60]}...")
            print(f"   신뢰도: {best_candidate.confidence:.3f}")
            print(f"   예상 영향: {best_candidate.expected_impact:.3f}")
        else:
            print("   ❌ 적절한 후보 없음")

        print("\n✅ 단계별 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 단계별 테스트 실패: {e}")
        return False


def test_full_insight_session():
    """전체 통찰 세션 테스트"""
    print("\n🚀 === 전체 통찰 세션 테스트 ===")

    try:
        import sys

        sys.path.append(".")
        from duri_brain.learning.insight_engine import (
            InsightTriggerEngine,
            InsightTriggerType,
        )

        engine = InsightTriggerEngine()

        # 통찰 세션 실행
        problem = "DuRi의 학습 루프가 3일간 성능 개선 없이 정체되어 있음"
        trigger_type = InsightTriggerType.REPEATED_FAILURE

        print(f"📌 문제: {problem}")
        print(f"📌 트리거 유형: {trigger_type.value}")

        session = engine.trigger_insight_session(problem, trigger_type)

        if session:
            print(f"✅ 세션 ID: {session.session_id}")
            print(f"📅 시작 시간: {session.start_time}")
            print(f"⏱️ 소요 시간: {session.duration:.2f}초")
            print(f"📋 완료된 단계: {len(session.phases_completed)}")

            for phase in session.phases_completed:
                print(f"   - {phase.value}")

            print(f"🎯 생성된 후보: {len(session.candidates_generated)}")

            if session.final_insight:
                print(f"🧠 최종 통찰: {session.final_insight.strategy}")
                print(f"📊 신뢰도: {session.final_insight.confidence:.3f}")
                print(f"🎯 예상 영향: {session.final_insight.expected_impact:.3f}")
            else:
                print("❌ 최종 통찰 없음")
        else:
            print("❌ 세션 생성 실패")

        print("\n✅ 전체 세션 테스트 완료")
        return True

    except Exception as e:
        logger.error(f"❌ 전체 세션 테스트 실패: {e}")
        return False


def show_system_architecture():
    """시스템 아키텍처 표시"""
    print("\n🏗️ === DuRi Insight Engine v1.0 아키텍처 ===")

    architecture = """
    🧠 DuRi Insight Engine v1.0

    📊 이중 응답 시스템 구조:

    [1] PerformanceMonitor →
    [2] EfficiencyDropDetected →
    [3] Dual Response Trigger:
         ├──> [A] RationalRefactorEngine (기존 DuRi 구조)
         └──> [B] InsightTriggerEngine (인간 유사 구조)

    🔀 [B] InsightTriggerEngine 내부 구조:

    1. CognitivePauseManager (의도적 정보 흐름 차단)
    2. SemanticDriftGenerator (랜덤 기억 소환)
    3. RetrogradeReasoningEngine (역방향 사고 자극)
    4. DisruptiveMappingEngine (비논리적 연결 탐색)
    5. MetaEvaluator (통찰 후보 평가)

    🔗 통합 구조:

    InsightEngine → InsightLearningIntegrator → LearningLoop

    🎯 핵심 특징:
    - 인간의 통찰 과정 모방
    - 이성적 리팩터링 + 창발적 비약
    - 자가 진화 가능한 메타인지 기반
    """

    print(architecture)


def show_usage_examples():
    """사용 예시 표시"""
    print("\n💡 === 사용 예시 ===")

    examples = """
    # 1. 기본 Insight Engine 사용
    from duri_brain.learning.insight_engine import get_dual_response_system
    system = get_dual_response_system()
    result = system.execute_dual_response("학습 성능 저하 문제")

    # 2. 학습 루프와 통합
    from duri_brain.learning.insight_integration import get_insight_integrator
    integrator = get_insight_integrator()
    integrator.activate_integration()
    result = integrator.execute_insight_enhanced_learning()

    # 3. 통찰 세션 직접 실행
    from duri_brain.learning.insight_engine import InsightTriggerEngine
    engine = InsightTriggerEngine()
    session = engine.trigger_insight_session("문제", InsightTriggerType.REPEATED_FAILURE)

    # 4. 상태 확인
    status = integrator.get_integration_status()
    print(f"성공한 통찰 수: {status['dual_response_system']['successful_insights']}")
    """

    print(examples)


def run_comprehensive_demo():
    """종합 데모 실행"""
    print("🧠 === DuRi Insight Engine v1.0 종합 데모 ===")
    print(f"📅 시작 시간: {datetime.now()}")

    test_results = []

    # 1. 시스템 아키텍처 표시
    show_system_architecture()

    # 2. 기본 기능 테스트
    test_results.append(("Insight Engine 기본 기능", test_insight_engine()))

    # 3. 통합 테스트
    test_results.append(("Insight Engine 통합", test_insight_integration()))

    # 4. 단계별 상세 테스트
    test_results.append(("통찰 단계별 상세", test_insight_phases()))

    # 5. 전체 세션 테스트
    test_results.append(("전체 통찰 세션", test_full_insight_session()))

    # 결과 요약
    print("\n📋 === 데모 결과 요약 ===")
    successful_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)

    for test_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name}: {status}")

    print(
        f"\n📊 전체 성공률: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)"
    )

    if successful_tests == total_tests:
        print("🎉 모든 테스트가 성공했습니다!")
        print("🚀 DuRi Insight Engine v1.0이 정상적으로 작동합니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 문제를 확인해주세요.")

    print(f"📅 완료 시간: {datetime.now()}")

    # 사용 예시 표시
    show_usage_examples()


def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "architecture":
            show_system_architecture()
        elif command == "examples":
            show_usage_examples()
        elif command == "test":
            run_comprehensive_demo()
        else:
            print("사용법: python insight_system_demo.py [architecture|examples|test]")
    else:
        run_comprehensive_demo()


if __name__ == "__main__":
    main()
