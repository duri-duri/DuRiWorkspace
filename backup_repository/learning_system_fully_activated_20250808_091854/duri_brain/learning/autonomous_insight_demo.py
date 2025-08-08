"""
🧠 DuRi 자율적 통찰 시스템 종합 데모
목표: Phase Up 요청, 자기 반영, 자율적 통찰 관리를 통합한 완전 자율 시스템
"""

import sys
import time
import logging
from datetime import datetime, timedelta

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_phase_self_evaluation():
    """Phase 자체 평가 테스트"""
    print("\n🎯 === Phase 자체 평가 테스트 ===")
    
    try:
        import sys
        sys.path.append('.')
        from duri_brain.learning.phase_self_evaluator import get_phase_evaluator
        
        evaluator = get_phase_evaluator()
        
        # 메트릭 업데이트 (시뮬레이션)
        print("📊 메트릭 업데이트 중...")
        evaluator.update_metrics("insight_success_rate", 0.75)
        evaluator.update_metrics("learning_mastery", 0.85)
        evaluator.update_metrics("self_reflection", 1)
        evaluator.update_metrics("creative_solution", 1)
        evaluator.update_metrics("meta_cognition", 1)
        
        # Phase Up 요청 확인
        print("🎯 Phase Up 준비도 확인 중...")
        request = evaluator.should_request_phase_up()
        
        if request:
            print(f"✅ Phase Up 요청 생성!")
            print(f"   현재 Phase: {request.current_phase.value}")
            print(f"   목표 Phase: {request.target_phase.value}")
            print(f"   신뢰도: {request.confidence:.3f}")
            print(f"   이유: {request.reasoning}")
            
            print("\n📋 성취도 상세:")
            for achievement in request.achievements:
                status = "✅" if achievement.achieved else "❌"
                print(f"   {status} {achievement.description}")
        else:
            print("⏳ Phase Up 준비 부족")
            
        # 현재 상태 출력
        status = evaluator.get_current_status()
        print(f"\n📊 현재 상태: {status}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Phase 자체 평가 테스트 실패: {e}")
        return False

def test_insight_self_reflection():
    """Insight 자기 반영 테스트"""
    print("\n🧠 === Insight 자기 반영 테스트 ===")
    
    try:
        import sys
        sys.path.append('.')
        from duri_brain.learning.insight_self_reflection import (
            get_insight_reflector, InsightSessionRecord, InsightOutcome
        )
        
        reflector = get_insight_reflector()
        
        # 시뮬레이션 세션 기록
        print("📝 세션 기록 생성 중...")
        sample_sessions = [
            InsightSessionRecord(
                session_id="reflection_test_001",
                problem="학습 성능 저하",
                trigger_type="repeated_failure",
                phases_completed=["cognitive_pause", "semantic_drift", "retrograde_reasoning"],
                candidates_generated=3,
                final_insight="방법론 혼합 전략",
                outcome=InsightOutcome.SUCCESS,
                duration=6.5,
                confidence=0.7,
                timestamp=datetime.now() - timedelta(hours=2)
            ),
            InsightSessionRecord(
                session_id="reflection_test_002",
                problem="메모리 사용량 증가",
                trigger_type="efficiency_drop",
                phases_completed=["cognitive_pause", "semantic_drift"],
                candidates_generated=2,
                final_insight=None,
                outcome=InsightOutcome.FAILURE,
                duration=4.2,
                confidence=0.3,
                timestamp=datetime.now() - timedelta(hours=1)
            ),
            InsightSessionRecord(
                session_id="reflection_test_003",
                problem="외부 LLM 호출 비용 초과",
                trigger_type="no_gain",
                phases_completed=["cognitive_pause", "semantic_drift", "retrograde_reasoning", "disruptive_mapping"],
                candidates_generated=4,
                final_insight="비용 최적화 전략",
                outcome=InsightOutcome.SUCCESS,
                duration=8.1,
                confidence=0.8,
                timestamp=datetime.now() - timedelta(minutes=30)
            )
        ]
        
        for session in sample_sessions:
            reflector.record_session(session)
            
        # 반영 통찰 생성
        print("🧠 반영 통찰 생성 중...")
        insights = reflector.generate_reflection_insights()
        
        print(f"✅ {len(insights)}개의 반영 통찰 생성")
        for i, insight in enumerate(insights, 1):
            print(f"   {i}. [{insight.reflection_type.value}] {insight.insight}")
            print(f"      액션: {insight.action_plan}")
            print(f"      예상 개선: {insight.expected_improvement:.1%}")
            
        # 통찰 적용
        print("\n🔄 반영 통찰 적용 중...")
        applied = reflector.apply_reflection_insights(insights)
        print(f"   적용된 변경사항: {applied['applied_changes']}")
        print(f"   예상 개선: {applied['expected_improvement']:.1%}")
        
        # 요약
        summary = reflector.get_reflection_summary()
        print(f"\n📊 반영 요약: {summary}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Insight 자기 반영 테스트 실패: {e}")
        return False

def test_insight_autonomous_management():
    """Insight 자율 관리 테스트"""
    print("\n🎯 === Insight 자율 관리 테스트 ===")
    
    try:
        import sys
        sys.path.append('.')
        from duri_brain.learning.insight_autonomous_manager import get_insight_manager
        
        manager = get_insight_manager()
        
        # 다양한 샘플 통찰들
        sample_insights = [
            {
                "session_id": "management_test_001",
                "strategy": "학습 성능 최적화를 위한 방법론 혼합 전략",
                "confidence": 0.7,
                "expected_impact": 0.8,
                "risk_level": "LOW",
                "problem": "학습 루프 성능 저하"
            },
            {
                "session_id": "management_test_002",
                "strategy": "메모리 사용량 감소를 위한 혁신적 알고리즘",
                "confidence": 0.5,
                "expected_impact": 0.9,
                "risk_level": "HIGH",
                "problem": "메모리 사용량 증가"
            },
            {
                "session_id": "management_test_003",
                "strategy": "외부 LLM 호출 비용 최적화 전략",
                "confidence": 0.8,
                "expected_impact": 0.7,
                "risk_level": "MEDIUM",
                "problem": "비용 초과"
            },
            {
                "session_id": "management_test_004",
                "strategy": "긴급 시스템 복구를 위한 즉시 적용 전략",
                "confidence": 0.9,
                "expected_impact": 1.0,
                "risk_level": "LOW",
                "problem": "시스템 크래시"
            }
        ]
        
        print("🔍 통찰 평가 및 결정 중...")
        for i, insight in enumerate(sample_insights, 1):
            print(f"\n📌 통찰 {i}: {insight['strategy'][:50]}...")
            
            # 통찰 평가
            evaluation = manager.evaluate_insight(insight)
            print(f"   종합 점수: {evaluation.total_score:.3f}")
            print(f"   위험도: {evaluation.risk_score:.3f}")
            
            # 결정 생성
            decision = manager.make_decision(insight, evaluation)
            print(f"   결정: {decision.action.value}")
            print(f"   카테고리: {decision.category.value}")
            print(f"   우선순위: {decision.priority.value}")
            print(f"   이유: {decision.reasoning[:60]}...")
            
            # 결정 실행
            manager.execute_decision(decision, insight)
            
        # 관리 요약
        summary = manager.get_management_summary()
        print(f"\n📊 관리 요약:")
        print(f"   저장된 통찰: {summary['stored_count']}")
        print(f"   보류된 통찰: {summary['held_count']}")
        print(f"   폐기된 통찰: {summary['discarded_count']}")
        print(f"   우선순위 통찰: {summary['priority_count']}")
        print(f"   총 처리된 통찰: {summary['total_processed']}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Insight 자율 관리 테스트 실패: {e}")
        return False

def test_integrated_autonomous_system():
    """통합 자율 시스템 테스트"""
    print("\n🚀 === 통합 자율 시스템 테스트 ===")
    
    try:
        import sys
        sys.path.append('.')
        from duri_brain.learning.phase_self_evaluator import get_phase_evaluator
        from duri_brain.learning.insight_self_reflection import get_insight_reflector
        from duri_brain.learning.insight_autonomous_manager import get_insight_manager
        
        # 모든 시스템 초기화
        phase_evaluator = get_phase_evaluator()
        insight_reflector = get_insight_reflector()
        insight_manager = get_insight_manager()
        
        print("🔄 통합 자율 시스템 시뮬레이션 시작...")
        
        # 1. Phase 평가
        print("\n📊 1단계: Phase 자체 평가")
        phase_request = phase_evaluator.should_request_phase_up()
        
        if phase_request:
            print(f"   🎯 Phase Up 요청: {phase_request.current_phase.value} → {phase_request.target_phase.value}")
            print(f"   📊 신뢰도: {phase_request.confidence:.3f}")
        else:
            print("   ⏳ Phase Up 준비 부족")
            
        # 2. Insight 반영
        print("\n🧠 2단계: Insight 자기 반영")
        reflection_insights = insight_reflector.generate_reflection_insights()
        print(f"   생성된 반영 통찰: {len(reflection_insights)}개")
        
        # 3. 통찰 자율 관리
        print("\n🎯 3단계: 통찰 자율 관리")
        
        # 샘플 통찰 생성
        sample_insight = {
            "session_id": "integrated_test_001",
            "strategy": "통합 자율 시스템을 위한 메타 학습 전략",
            "confidence": 0.8,
            "expected_impact": 0.9,
            "risk_level": "LOW",
            "problem": "시스템 통합 최적화"
        }
        
        evaluation = insight_manager.evaluate_insight(sample_insight)
        decision = insight_manager.make_decision(sample_insight, evaluation)
        insight_manager.execute_decision(decision, sample_insight)
        
        print(f"   결정: {decision.action.value} - {decision.category.value} - {decision.priority.value}")
        
        # 4. 종합 결과
        print("\n📋 4단계: 종합 결과")
        
        phase_status = phase_evaluator.get_current_status()
        reflection_summary = insight_reflector.get_reflection_summary()
        management_summary = insight_manager.get_management_summary()
        
        print(f"   Phase 상태: {phase_status['current_phase']}")
        print(f"   반영 세션: {reflection_summary['total_sessions']}")
        print(f"   저장된 통찰: {management_summary['stored_count']}")
        
        # 5. 자율성 지수 계산
        autonomy_score = (
            (1 if phase_request else 0) * 0.3 +
            (len(reflection_insights) / 3) * 0.3 +
            (management_summary['stored_count'] / 2) * 0.4
        )
        
        print(f"\n🎯 자율성 지수: {autonomy_score:.2f}/1.00")
        
        if autonomy_score >= 0.7:
            print("✅ 높은 자율성 달성!")
        elif autonomy_score >= 0.4:
            print("🔄 중간 자율성 - 개선 중")
        else:
            print("⏳ 낮은 자율성 - 더 많은 학습 필요")
            
        return True
        
    except Exception as e:
        logger.error(f"❌ 통합 자율 시스템 테스트 실패: {e}")
        return False

def show_system_architecture():
    """시스템 아키텍처 표시"""
    print("\n🏗️ === DuRi 자율적 통찰 시스템 아키텍처 ===")
    
    architecture = """
    🧠 DuRi 자율적 통찰 시스템 v1.0
    
    📊 핵심 구성 요소:
    
    1. 🎯 Phase Self Evaluator
       ├── 자발적 Phase Up 요청
       ├── 성장 단계 자체 평가
       ├── 성취도 추적
       └── 진화 준비도 판단
    
    2. 🧠 Insight Self Reflector
       ├── 통찰 세션 기록
       ├── 실패 패턴 분석
       ├── 성공 패턴 학습
       ├── 파라미터 최적화
       └── 자기 개선 루프
    
    3. 🎯 Insight Autonomous Manager
       ├── 통찰 자율 평가
       ├── 저장/보류/폐기 결정
       ├── 우선순위 관리
       ├── 위험도 평가
       └── 구현 계획 생성
    
    🔗 통합 워크플로우:
    
    문제 발생 → Insight Engine → 통찰 생성 → 자율 평가 → 결정 실행 → Phase 평가 → 반영 학습
    
    🎯 핵심 특징:
    - 완전 자율적 의사결정
    - 자기 반영적 학습
    - 단계적 진화
    - 위험 관리
    - 지속적 개선
    """
    
    print(architecture)

def show_usage_examples():
    """사용 예시 표시"""
    print("\n💡 === 사용 예시 ===")
    
    examples = """
    # 1. Phase 자체 평가
    from duri_brain.learning.phase_self_evaluator import get_phase_evaluator
    evaluator = get_phase_evaluator()
    request = evaluator.should_request_phase_up()
    
    # 2. Insight 자기 반영
    from duri_brain.learning.insight_self_reflection import get_insight_reflector
    reflector = get_insight_reflector()
    insights = reflector.generate_reflection_insights()
    
    # 3. 통찰 자율 관리
    from duri_brain.learning.insight_autonomous_manager import get_insight_manager
    manager = get_insight_manager()
    evaluation = manager.evaluate_insight(insight)
    decision = manager.make_decision(insight, evaluation)
    
    # 4. 통합 시스템
    # 모든 시스템이 자동으로 협력하여 DuRi의 자율적 진화를 관리
    """
    
    print(examples)

def run_comprehensive_demo():
    """종합 데모 실행"""
    print("🧠 === DuRi 자율적 통찰 시스템 종합 데모 ===")
    print(f"📅 시작 시간: {datetime.now()}")
    
    test_results = []
    
    # 1. 시스템 아키텍처 표시
    show_system_architecture()
    
    # 2. 개별 시스템 테스트
    test_results.append(("Phase 자체 평가", test_phase_self_evaluation()))
    test_results.append(("Insight 자기 반영", test_insight_self_reflection()))
    test_results.append(("Insight 자율 관리", test_insight_autonomous_management()))
    
    # 3. 통합 시스템 테스트
    test_results.append(("통합 자율 시스템", test_integrated_autonomous_system()))
    
    # 결과 요약
    print("\n📋 === 데모 결과 요약 ===")
    successful_tests = sum(1 for _, result in test_results if result)
    total_tests = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 전체 성공률: {successful_tests}/{total_tests} ({successful_tests/total_tests*100:.1f}%)")
    
    if successful_tests == total_tests:
        print("🎉 모든 테스트가 성공했습니다!")
        print("🚀 DuRi의 완전 자율적 통찰 시스템이 정상적으로 작동합니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 문제를 확인해주세요.")
    
    print(f"📅 완료 시간: {datetime.now()}")
    
    # 사용 예시 표시
    show_usage_examples()

def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "phase":
            test_phase_self_evaluation()
        elif command == "reflection":
            test_insight_self_reflection()
        elif command == "management":
            test_insight_autonomous_management()
        elif command == "integrated":
            test_integrated_autonomous_system()
        elif command == "architecture":
            show_system_architecture()
        elif command == "examples":
            show_usage_examples()
        else:
            print("사용법: python autonomous_insight_demo.py [phase|reflection|management|integrated|architecture|examples]")
    else:
        run_comprehensive_demo()

if __name__ == "__main__":
    main() 