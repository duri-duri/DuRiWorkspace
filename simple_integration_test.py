#!/usr/bin/env python3
"""
Phase 1 + Phase 2 간단 통합 테스트
"""

import sys
import os
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 경로 설정
sys.path.append(os.path.join(os.path.dirname(__file__), 'temp_extract_8월7일', 'DuRiCore', 'modules'))

try:
    from ml_integration.phase1_problem_solver import Phase1ProblemSolver
    from ml_integration.phase2_deep_learning_integration import Phase2DeepLearningIntegration
    from algorithm_knowledge.algorithm_knowledge_base import AlgorithmKnowledgeBase
    
    print("✅ 모든 모듈 import 성공")
    
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    sys.exit(1)

def test_integration():
    """Phase 1 + Phase 2 통합 테스트"""
    try:
        print("\n🚀 Phase 1 + Phase 2 통합 테스트 시작")
        
        # 1. 지식 베이스 초기화
        print("\n1️⃣ 지식 베이스 초기화 중...")
        knowledge_base = AlgorithmKnowledgeBase()
        print("✅ 지식 베이스 초기화 완료")
        
        # 2. Phase 1 시스템 실행
        print("\n2️⃣ Phase 1 시스템 실행 중...")
        phase1_solver = Phase1ProblemSolver(knowledge_base)
        
        # 문제 진단
        diagnosis_results = phase1_solver.diagnose_all_problems()
        if 'error' in diagnosis_results:
            print(f"❌ Phase 1 진단 실패: {diagnosis_results['error']}")
            return False
        
        # 문제 해결
        solutions = phase1_solver.solve_all_problems()
        if 'error' in solutions:
            print(f"❌ Phase 1 해결 실패: {solutions['error']}")
            return False
        
        print("✅ Phase 1 시스템 실행 완료")
        
        # 3. Phase 2 시스템 실행
        print("\n3️⃣ Phase 2 시스템 실행 중...")
        phase2_system = Phase2DeepLearningIntegration()
        
        # 향상된 데이터 생성
        enhanced_data = phase2_system.create_enhanced_test_data()
        if enhanced_data.empty:
            print("❌ 향상된 데이터 생성 실패")
            return False
        
        # 딥러닝 모델 학습
        training_result = phase2_system.train_deep_learning_model(enhanced_data)
        if not training_result.get('success', False):
            print(f"❌ 딥러닝 모델 학습 실패: {training_result.get('reason', '알 수 없는 오류')}")
            return False
        
        print("✅ Phase 2 시스템 실행 완료")
        
        # 4. 통합 시스템 성능 비교
        print("\n4️⃣ 통합 시스템 성능 비교 중...")
        hybrid_result = phase2_system.create_hybrid_system()
        
        if not hybrid_result.get('success', False):
            print(f"❌ 하이브리드 시스템 생성 실패: {hybrid_result.get('reason', '알 수 없는 오류')}")
            return False
        
        print("✅ 통합 시스템 성능 비교 완료")
        
        # 5. 결과 요약
        print("\n📊 === 통합 시스템 결과 요약 ===")
        
        # Phase 1 결과
        print("\n🔧 Phase 1 결과:")
        if 'overall_summary' in diagnosis_results:
            summary = diagnosis_results['overall_summary']
            print(f"   전체 상태: {summary.get('overall_status', 'unknown')}")
            print(f"   총 문제 수: {summary.get('total_problems', 0)}")
        
        # Phase 2 결과
        print("\n🤖 Phase 2 결과:")
        performance = training_result.get('performance', {})
        print(f"   딥러닝 R²: {performance.get('r2_score', 'N/A'):.3f}")
        print(f"   딥러닝 MSE: {performance.get('mse', 'N/A'):.6f}")
        
        # 통합 결과
        print("\n🔄 통합 시스템 결과:")
        performance_comparison = hybrid_result.get('performance_comparison', {})
        
        for model_name, metrics in performance_comparison.items():
            print(f"   {model_name.upper()}: R²={metrics.get('r2', 'N/A'):.3f}, MSE={metrics.get('mse', 'N/A'):.6f}")
        
        # 앙상블 효과
        ensemble_improvement = hybrid_result.get('ensemble_improvement', {})
        print(f"   앙상블 개선률: {ensemble_improvement.get('improvement_percentage', 'N/A'):.1f}%")
        
        # 6. 전체 시스템 상태
        print("\n📋 전체 시스템 상태:")
        phase1_status = "✅ 완료" if solutions else "❌ 실패"
        phase2_status = "✅ 완료" if training_result.get('success') else "❌ 실패"
        integration_status = "✅ 완료" if hybrid_result.get('success') else "❌ 실패"
        
        print(f"   Phase 1: {phase1_status}")
        print(f"   Phase 2: {phase2_status}")
        print(f"   통합 시스템: {integration_status}")
        
        # 7. 성공 여부 판단
        overall_success = (
            solutions and 
            training_result.get('success') and 
            hybrid_result.get('success')
        )
        
        if overall_success:
            print("\n🎉 === Phase 1 + Phase 2 통합 성공! ===")
            print("   ✅ 전통적 ML 시스템 완성")
            print("   ✅ 딥러닝 시스템 완성")
            print("   ✅ 하이브리드 통합 시스템 완성")
            print("   🚀 전체 시스템 준비 완료!")
        else:
            print("\n❌ === 통합 시스템 일부 실패 ===")
        
        return overall_success
        
    except Exception as e:
        print(f"❌ 통합 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_integration()
    sys.exit(0 if success else 1)
