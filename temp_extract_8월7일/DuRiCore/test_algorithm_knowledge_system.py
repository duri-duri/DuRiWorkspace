"""
알고리즘 지식 시스템 테스트
"""

import sys
import os
import logging
from datetime import datetime

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.algorithm_knowledge.integrated_algorithm_system import IntegratedAlgorithmSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_basic_functionality():
    """기본 기능 테스트"""
    print("🧪 기본 기능 테스트 시작")
    
    # 시스템 초기화
    system = IntegratedAlgorithmSystem()
    
    # 1. 기본 알고리즘 확인
    print("\n1️⃣ 기본 알고리즘 확인")
    algorithms = system.search_algorithms("")
    print(f"   총 {len(algorithms)}개의 기본 알고리즘이 있습니다:")
    for alg in algorithms:
        print(f"   - {alg.name} ({alg.category}): 성공률 {alg.success_rate:.1%}")
    
    # 2. 문제 해결 테스트
    print("\n2️⃣ 문제 해결 테스트")
    problem = "복잡한 코딩 문제를 효율적으로 해결하고 싶습니다"
    recommendation = system.solve_problem(problem, "학습", "complex")
    
    if recommendation:
        print(f"   추천 알고리즘: {recommendation.algorithm.name}")
        print(f"   신뢰도: {recommendation.confidence_score:.1%}")
        print(f"   추천 이유: {recommendation.reasoning}")
        print(f"   위험도: {recommendation.risk_level}")
    else:
        print("   적합한 알고리즘을 찾지 못했습니다")
    
    # 3. 새로운 알고리즘 추가
    print("\n3️⃣ 새로운 알고리즘 추가")
    new_alg_id = system.add_new_algorithm(
        name="반복 학습 최적화",
        description="학습 내용을 효율적으로 기억하고 복습하는 알고리즘",
        category="learning",
        input_patterns=["학습", "기억", "복습", "최적화"],
        process_steps=[
            "1. 학습 내용 요약 및 핵심 포인트 추출",
            "2. 기억 곡선 기반 복습 주기 설정",
            "3. 간격 반복을 통한 장기 기억 강화",
            "4. 학습 효과 측정 및 피드백"
        ],
        output_patterns=["최적화된 학습 계획", "기억 강화", "학습 효율성 향상"],
        applicable_domains=["교육", "학습", "자기계발"]
    )
    
    if new_alg_id:
        print(f"   새로운 알고리즘 추가 완료: {new_alg_id}")
    else:
        print("   알고리즘 추가 실패")
    
    # 4. 새로운 문제 패턴 추가
    print("\n4️⃣ 새로운 문제 패턴 추가")
    new_pattern_id = system.add_problem_pattern(
        name="학습 효율성 최적화",
        description="학습 시간을 최소화하면서 최대한의 효과를 얻고 싶은 상황",
        pattern_type="learning_optimization",
        key_features=["학습", "효율성", "시간", "최적화", "성과"],
        complexity_level="medium",
        domain="교육",
        applicable_algorithms=[new_alg_id] if new_alg_id else []
    )
    
    if new_pattern_id:
        print(f"   새로운 문제 패턴 추가 완료: {new_pattern_id}")
    else:
        print("   문제 패턴 추가 실패")
    
    return system

def test_learning_and_evolution():
    """학습 및 진화 테스트"""
    print("\n🧪 학습 및 진화 테스트 시작")
    
    system = IntegratedAlgorithmSystem()
    
    # 1. 경험 학습 테스트
    print("\n1️⃣ 경험 학습 테스트")
    
    # 성공적인 학습 경험
    success_result = system.learn_from_experience(
        algorithm_id="alg_001",  # 단계별 문제 해결
        problem_context="복잡한 수학 문제를 단계별로 해결함",
        success=True,
        efficiency_score=0.9,
        execution_time=3.5,
        feedback="단계별 접근이 매우 효과적이었음"
    )
    print(f"   성공 학습 결과: {'성공' if success_result else '실패'}")
    
    # 실패한 학습 경험
    failure_result = system.learn_from_experience(
        algorithm_id="alg_002",  # 패턴 기반 학습
        problem_context="새로운 프로그래밍 언어 학습 시도",
        success=False,
        efficiency_score=0.3,
        execution_time=8.0,
        feedback="기존 지식과 연결이 어려웠음"
    )
    print(f"   실패 학습 결과: {'성공' if failure_result else '실패'}")
    
    # 2. 시스템 통계 확인
    print("\n2️⃣ 시스템 통계 확인")
    stats = system.get_system_statistics()
    
    print(f"   시스템 상태: {stats.get('system_status', 'unknown')}")
    print(f"   총 알고리즘: {stats.get('total_components', {}).get('algorithms', 0)}개")
    print(f"   총 문제 패턴: {stats.get('total_components', {}).get('problem_patterns', 0)}개")
    print(f"   학습 세션: {stats.get('total_components', {}).get('learning_sessions', 0)}개")
    print(f"   개선사항: {stats.get('total_components', {}).get('improvements', 0)}개")
    print(f"   새로운 알고리즘: {stats.get('total_components', {}).get('new_algorithms', 0)}개")
    
    # 3. 성능 지표 확인
    print("\n3️⃣ 성능 지표 확인")
    performance = stats.get('performance_metrics', {})
    print(f"   평균 성공률: {performance.get('average_success_rate', 0):.1%}")
    print(f"   평균 효율성: {performance.get('average_efficiency', 0):.1%}")
    print(f"   진화율: {performance.get('evolution_rate', 0):.1%}")
    print(f"   선택 신뢰도: {performance.get('selection_confidence', 0):.1%}")
    
    return system

def test_advanced_features():
    """고급 기능 테스트"""
    print("\n🧪 고급 기능 테스트 시작")
    
    system = IntegratedAlgorithmSystem()
    
    # 1. 알고리즘 검색 테스트
    print("\n1️⃣ 알고리즘 검색 테스트")
    
    # 카테고리별 검색
    problem_solving_algs = system.search_algorithms("", "problem_solving")
    print(f"   문제 해결 알고리즘: {len(problem_solving_algs)}개")
    
    learning_algs = system.search_algorithms("", "learning")
    print(f"   학습 알고리즘: {len(learning_algs)}개")
    
    # 키워드 검색
    pattern_algs = system.search_algorithms("패턴")
    print(f"   '패턴' 관련 알고리즘: {len(pattern_algs)}개")
    
    # 2. 관련 알고리즘 찾기
    print("\n2️⃣ 관련 알고리즘 찾기")
    if problem_solving_algs:
        related = system.get_related_algorithms(problem_solving_algs[0].algorithm_id)
        print(f"   '{problem_solving_algs[0].name}'과 관련된 알고리즘: {len(related)}개")
    
    # 3. 시스템 유지보수
    print("\n3️⃣ 시스템 유지보수")
    maintenance_result = system.perform_maintenance()
    print(f"   유지보수 결과: {'성공' if maintenance_result else '실패'}")
    
    # 4. 시스템 상태 저장/로드
    print("\n4️⃣ 시스템 상태 저장/로드")
    save_result = system.save_system_state("test_algorithm_system")
    print(f"   저장 결과: {'성공' if save_result else '실패'}")
    
    # 새로운 시스템 인스턴스로 로드 테스트
    new_system = IntegratedAlgorithmSystem()
    load_result = new_system.load_system_state("test_algorithm_system")
    print(f"   로드 결과: {'성공' if load_result else '실패'}")
    
    # 로드된 데이터 확인
    if load_result:
        loaded_stats = new_system.get_system_statistics()
        print(f"   로드된 알고리즘: {loaded_stats.get('total_components', {}).get('algorithms', 0)}개")
    
    return system

def test_integration_with_existing_system():
    """기존 시스템과의 통합 테스트"""
    print("\n🧪 기존 시스템과의 통합 테스트 시작")
    
    # 기존 통합 학습 시스템과의 연동 시뮬레이션
    print("\n1️⃣ 기존 시스템과의 연동 시뮬레이션")
    
    # 알고리즘 지식 시스템 초기화
    algorithm_system = IntegratedAlgorithmSystem()
    
    # 기존 학습 시스템의 판단 기록을 알고리즘으로 변환하는 시뮬레이션
    print("   기존 판단 기록을 알고리즘으로 변환 중...")
    
    # 예시: 기존 시스템의 판단 기록
    existing_judgments = [
        {
            "context": "복잡한 코딩 문제 해결",
            "judgment": "단계별 접근 방식 선택",
            "reasoning": "복잡한 문제는 구조화된 접근이 효과적",
            "outcome": "5단계로 분해하여 해결책 제시",
            "success": True
        },
        {
            "context": "새로운 기술 학습",
            "judgment": "패턴 기반 학습 방법 선택",
            "reasoning": "기존 지식과 연결하여 효율적 학습",
            "outcome": "유사한 패턴을 찾아 빠르게 습득",
            "success": True
        }
    ]
    
    # 판단 기록을 알고리즘으로 변환
    for judgment in existing_judgments:
        if judgment["success"]:
            # 성공한 판단을 알고리즘으로 저장
            algorithm_id = algorithm_system.add_new_algorithm(
                name=f"판단 기반 알고리즘 - {judgment['judgment'][:20]}...",
                description=f"컨텍스트: {judgment['context']}\n판단: {judgment['judgment']}\n근거: {judgment['reasoning']}",
                category="decision_making",
                input_patterns=[judgment["context"], judgment["judgment"]],
                process_steps=[
                    "1. 상황 분석",
                    "2. 판단 기준 설정",
                    "3. 최적 방법 선택",
                    "4. 실행 및 검증"
                ],
                output_patterns=[judgment["outcome"]],
                applicable_domains=["일반", "문제해결"]
            )
            
            if algorithm_id:
                print(f"   판단 기록을 알고리즘으로 변환 완료: {algorithm_id}")
    
    # 2. 통합 시스템 통계
    print("\n2️⃣ 통합 시스템 통계")
    final_stats = algorithm_system.get_system_statistics()
    
    print(f"   최종 알고리즘 수: {final_stats.get('total_components', {}).get('algorithms', 0)}개")
    print(f"   최종 문제 패턴 수: {final_stats.get('total_components', {}).get('problem_patterns', 0)}개")
    print(f"   시스템 상태: {final_stats.get('system_status', 'unknown')}")
    
    # 3. 향후 ML/DL 통합을 위한 준비 상태
    print("\n3️⃣ ML/DL 통합 준비 상태")
    print("   ✅ 알고리즘 지식 베이스 구조 완성")
    print("   ✅ 지능형 선택 엔진 구현")
    print("   ✅ 학습 및 진화 시스템 구축")
    print("   ✅ 기존 시스템과의 연동 구조 준비")
    print("   🔄 다음 단계: 머신러닝/딥러닝 모델 통합")
    
    return algorithm_system

def main():
    """메인 테스트 실행"""
    print("🚀 DuRi 알고리즘 지식 시스템 테스트 시작")
    print("=" * 60)
    
    try:
        # 1. 기본 기능 테스트
        system1 = test_basic_functionality()
        
        # 2. 학습 및 진화 테스트
        system2 = test_learning_and_evolution()
        
        # 3. 고급 기능 테스트
        system3 = test_advanced_features()
        
        # 4. 기존 시스템과의 통합 테스트
        system4 = test_integration_with_existing_system()
        
        print("\n" + "=" * 60)
        print("🎉 모든 테스트 완료!")
        print("\n📊 최종 시스템 요약:")
        
        final_stats = system4.get_system_statistics()
        print(f"   - 총 알고리즘: {final_stats.get('total_components', {}).get('algorithms', 0)}개")
        print(f"   - 총 문제 패턴: {final_stats.get('total_components', {}).get('problem_patterns', 0)}개")
        print(f"   - 시스템 상태: {final_stats.get('system_status', 'unknown')}")
        print(f"   - 평균 성공률: {final_stats.get('performance_metrics', {}).get('average_success_rate', 0):.1%}")
        
        print("\n🔮 다음 단계:")
        print("   1. 머신러닝 모델을 통한 알고리즘 성능 예측")
        print("   2. 딥러닝을 통한 문제 패턴 자동 인식")
        print("   3. 강화학습을 통한 알고리즘 자동 최적화")
        print("   4. NLP를 통한 자연어 기반 알고리즘 생성")
        
    except Exception as e:
        print(f"\n❌ 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
