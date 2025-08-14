#!/usr/bin/env python3
"""
Phase 1 문제 해결 시스템 테스트 스크립트
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
    from algorithm_knowledge.algorithm_knowledge_base import AlgorithmKnowledgeBase
    from ml_integration.phase1_problem_solver import Phase1ProblemSolver
    
    print("✅ 모듈 import 성공")
    
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    sys.exit(1)

def test_phase1_solver():
    """Phase 1 문제 해결 시스템 테스트"""
    try:
        print("\n🚀 Phase 1 문제 해결 시스템 테스트 시작")
        
        # 1. 지식 베이스 초기화
        print("\n1️⃣ 지식 베이스 초기화 중...")
        knowledge_base = AlgorithmKnowledgeBase()
        print("✅ 지식 베이스 초기화 완료")
        
        # 2. 문제 해결 시스템 초기화
        print("\n2️⃣ 문제 해결 시스템 초기화 중...")
        problem_solver = Phase1ProblemSolver(knowledge_base)
        print("✅ 문제 해결 시스템 초기화 완료")
        
        # 3. 문제 진단 실행
        print("\n3️⃣ 문제 진단 실행 중...")
        diagnosis_results = problem_solver.diagnose_all_problems()
        
        if 'error' in diagnosis_results:
            print(f"❌ 문제 진단 실패: {diagnosis_results['error']}")
            return False
        
        print("✅ 문제 진단 완료")
        
        # 4. 진단 결과 출력
        print("\n📊 진단 결과:")
        if 'overall_summary' in diagnosis_results:
            summary = diagnosis_results['overall_summary']
            print(f"   전체 상태: {summary.get('overall_status', 'unknown')}")
            print(f"   총 문제 수: {summary.get('total_problems', 0)}")
            print(f"   심각한 문제: {summary.get('critical_problems', 0)}")
            print(f"   높은 우선순위: {summary.get('high_priority_problems', 0)}")
        
        # 5. 문제 해결 실행
        print("\n4️⃣ 문제 해결 실행 중...")
        solutions = problem_solver.solve_all_problems()
        
        if 'error' in solutions:
            print(f"❌ 문제 해결 실패: {solutions['error']}")
            return False
        
        print("✅ 문제 해결 완료")
        
        # 6. 해결 결과 출력
        print("\n🔧 해결 결과:")
        if 'validation_results' in solutions:
            validation = solutions['validation_results']
            if validation.get('validation_passed', False):
                print("   ✅ 검증 통과")
                print(f"   전체 개선도: {validation.get('overall_improvement', 0):.1f}%")
            else:
                print("   ❌ 검증 실패")
                if 'performance' in validation.get('validation_results', {}):
                    print(f"   성능 문제: {validation['validation_results']['performance']}")
        
        # 7. 개선된 모델 정보
        print("\n🤖 개선된 모델:")
        improved_models = problem_solver.get_improved_models()
        for model_name, model_info in improved_models.items():
            if 'improvement' in model_info:
                improvement = model_info['improvement']
                print(f"   {model_name}:")
                print(f"     원래 R²: {improvement.get('original_r2', 'N/A')}")
                print(f"     개선된 R²: {improvement.get('improved_r2', 'N/A'):.3f}")
                print(f"     개선률: {improvement.get('improvement_percentage', 0):.1f}%")
        
        print("\n🎉 Phase 1 문제 해결 시스템 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase1_solver()
    sys.exit(0 if success else 1)
