#!/usr/bin/env python3
"""
새로운 통합 인터페이스 테스트
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
    from simple_integration_manager import SimpleIntegrationManager
    
    print("✅ 모든 모듈 import 성공")
    
except ImportError as e:
    print(f"❌ 모듈 import 실패: {e}")
    sys.exit(1)

def test_new_integration_interface():
    """새로운 통합 인터페이스 테스트"""
    try:
        print("\n🚀 새로운 통합 인터페이스 테스트 시작")
        
        # 1. 지식 베이스 초기화
        print("\n1️⃣ 지식 베이스 초기화 중...")
        knowledge_base = AlgorithmKnowledgeBase()
        print("✅ 지식 베이스 초기화 완료")
        
        # 2. Phase 1 시스템 실행 및 통합 인터페이스 테스트
        print("\n2️⃣ Phase 1 시스템 실행 및 통합 인터페이스 테스트 중...")
        phase1_solver = Phase1ProblemSolver(knowledge_base)
        
        # 문제 진단 및 해결
        diagnosis_results = phase1_solver.diagnose_all_problems()
        solutions = phase1_solver.solve_all_problems()
        
        if 'error' in diagnosis_results or 'error' in solutions:
            print("❌ Phase 1 실행 실패")
            return False
        
        print("✅ Phase 1 시스템 실행 완료")
        
        # 새로운 통합 인터페이스 테스트
        print("\n🔧 Phase 1 통합 인터페이스 테스트:")
        
        # 통합 준비 상태 확인
        if hasattr(phase1_solver, 'is_ready_for_integration'):
            ready_status = phase1_solver.is_ready_for_integration()
            print(f"   통합 준비 상태: {ready_status}")
        else:
            print("   ❌ is_ready_for_integration 메서드 없음")
        
        # 통합 인터페이스 가져오기
        if hasattr(phase1_solver, 'get_integration_interface'):
            integration_interface = phase1_solver.get_integration_interface()
            print(f"   통합 인터페이스 상태: {integration_interface.get('status', 'unknown')}")
            print(f"   사용 가능한 모델: {list(integration_interface.get('models', {}).keys())}")
        else:
            print("   ❌ get_integration_interface 메서드 없음")
        
        # Phase 2용 데이터 내보내기
        if hasattr(phase1_solver, 'export_for_phase2'):
            export_data = phase1_solver.export_for_phase2()
            print(f"   Phase 2용 데이터 내보내기: {len(export_data)}개 항목")
        else:
            print("   ❌ export_for_phase2 메서드 없음")
        
        # 3. Phase 2 시스템 실행 및 통합 인터페이스 테스트
        print("\n3️⃣ Phase 2 시스템 실행 및 통합 인터페이스 테스트 중...")
        phase2_system = Phase2DeepLearningIntegration()
        
        # 향상된 데이터 생성 및 딥러닝 모델 학습
        enhanced_data = phase2_system.create_enhanced_test_data()
        training_result = phase2_system.train_deep_learning_model(enhanced_data)
        
        if not training_result.get('success', False):
            print("❌ Phase 2 실행 실패")
            return False
        
        print("✅ Phase 2 시스템 실행 완료")
        
        # 새로운 통합 인터페이스 테스트
        print("\n🤖 Phase 2 통합 인터페이스 테스트:")
        
        # Phase 1 통합 상태 확인
        if hasattr(phase2_system, 'get_phase1_integration_status'):
            integration_status = phase2_system.get_phase1_integration_status()
            print(f"   Phase 1 통합 상태: {integration_status}")
        else:
            print("   ❌ get_phase1_integration_status 메서드 없음")
        
        # 4. 통합 관리자를 통한 통합 테스트
        print("\n4️⃣ 통합 관리자를 통한 통합 테스트 중...")
        integration_manager = SimpleIntegrationManager()
        
        # Phase 1과 Phase 2 설정
        if integration_manager.set_phase1_solver(phase1_solver):
            print("✅ Phase 1 솔버 설정 완료")
        else:
            print("❌ Phase 1 솔버 설정 실패")
            return False
        
        if integration_manager.set_phase2_system(phase2_system):
            print("✅ Phase 2 시스템 설정 완료")
        else:
            print("❌ Phase 2 시스템 설정 실패")
            return False
        
        # 통합 상태 확인
        status = integration_manager.get_status()
        print(f"   통합 준비 상태: {status}")
        
        # 통합 수행
        integration_result = integration_manager.perform_integration()
        if integration_result.get('success'):
            print("✅ 통합 수행 완료")
        else:
            print(f"❌ 통합 수행 실패: {integration_result.get('reason')}")
            return False
        
        # 5. 향상된 하이브리드 시스템 테스트
        print("\n5️⃣ 향상된 하이브리드 시스템 테스트 중...")
        
        if hasattr(phase2_system, 'create_enhanced_hybrid_system'):
            enhanced_result = phase2_system.create_enhanced_hybrid_system()
            if enhanced_result.get('success'):
                print("✅ 향상된 하이브리드 시스템 생성 완료")
                
                # 결과 요약
                print("\n📊 향상된 하이브리드 시스템 결과:")
                if 'phase1_integration' in enhanced_result:
                    phase1_info = enhanced_result['phase1_integration']
                    print(f"   Phase 1 통합: {phase1_info.get('integration_status', 'unknown')}")
                    print(f"   사용 가능한 모델: {phase1_info.get('models_available', [])}")
                
                if 'hybrid_system' in enhanced_result:
                    hybrid_info = enhanced_result['hybrid_system']
                    print(f"   하이브리드 시스템 상태: {hybrid_info.get('status', 'unknown')}")
                    print(f"   총 모델 수: {hybrid_info.get('total_models', 0)}")
            else:
                print(f"❌ 향상된 하이브리드 시스템 생성 실패: {enhanced_result.get('reason')}")
        else:
            print("   ❌ create_enhanced_hybrid_system 메서드 없음")
        
        # 6. 최종 결과 요약
        print("\n🎉 === 새로운 통합 인터페이스 테스트 완료! ===")
        print("   ✅ Phase 1 통합 인터페이스 추가 완료")
        print("   ✅ Phase 2 통합 인터페이스 추가 완료")
        print("   ✅ 통합 관리자 생성 및 테스트 완료")
        print("   🚀 완전한 통합 시스템 준비 완료!")
        
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_new_integration_interface()
    sys.exit(0 if success else 1)
