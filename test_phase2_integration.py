#!/usr/bin/env python3
"""
Phase 2 딥러닝 통합 시스템 테스트 스크립트
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
    from ml_integration.phase2_deep_learning_integration import Phase2DeepLearningIntegration
    
    print("✅ Phase 2 모듈 import 성공")
    
except ImportError as e:
    print(f"❌ Phase 2 모듈 import 실패: {e}")
    sys.exit(1)

def test_phase2_integration():
    """Phase 2 딥러닝 통합 시스템 테스트"""
    try:
        print("\n🚀 Phase 2 딥러닝 통합 시스템 테스트 시작")
        
        # 1. Phase 2 시스템 초기화
        print("\n1️⃣ Phase 2 시스템 초기화 중...")
        phase2_system = Phase2DeepLearningIntegration()
        print("✅ Phase 2 시스템 초기화 완료")
        
        # 2. 향상된 테스트 데이터 생성
        print("\n2️⃣ 향상된 테스트 데이터 생성 중...")
        enhanced_data = phase2_system.create_enhanced_test_data()
        
        if enhanced_data.empty:
            print("❌ 향상된 테스트 데이터 생성 실패")
            return False
        
        print(f"✅ 향상된 테스트 데이터 생성 완료: {enhanced_data.shape}")
        print(f"   특성 수: {len(enhanced_data.columns)}")
        print(f"   샘플 수: {len(enhanced_data)}")
        
        # 3. 딥러닝 모델 학습
        print("\n3️⃣ 딥러닝 모델 학습 중...")
        training_result = phase2_system.train_deep_learning_model(enhanced_data)
        
        if not training_result.get('success', False):
            print(f"❌ 딥러닝 모델 학습 실패: {training_result.get('reason', '알 수 없는 오류')}")
            return False
        
        print("✅ 딥러닝 모델 학습 완료")
        
        # 4. 학습 성능 출력
        performance = training_result.get('performance', {})
        print(f"   R² 점수: {performance.get('r2_score', 'N/A'):.3f}")
        print(f"   MSE: {performance.get('mse', 'N/A'):.6f}")
        print(f"   교차 검증 평균: {performance.get('cv_mean', 'N/A'):.3f}")
        print(f"   최적 에포크: {performance.get('best_epoch', 'N/A')}")
        
        # 5. 하이브리드 시스템 생성
        print("\n4️⃣ 하이브리드 시스템 생성 중...")
        hybrid_result = phase2_system.create_hybrid_system()
        
        if not hybrid_result.get('success', False):
            print(f"❌ 하이브리드 시스템 생성 실패: {hybrid_result.get('reason', '알 수 없는 오류')}")
            return False
        
        print("✅ 하이브리드 시스템 생성 완료")
        
        # 6. 성능 비교 결과 출력
        print("\n📊 성능 비교 결과:")
        performance_comparison = hybrid_result.get('performance_comparison', {})
        
        for model_name, metrics in performance_comparison.items():
            print(f"   {model_name.upper()}:")
            print(f"     R²: {metrics.get('r2', 'N/A'):.3f}")
            print(f"     MSE: {metrics.get('mse', 'N/A'):.6f}")
        
        # 7. 앙상블 개선 효과 출력
        print("\n🔧 앙상블 개선 효과:")
        ensemble_improvement = hybrid_result.get('ensemble_improvement', {})
        
        print(f"   최고 개별 모델: {ensemble_improvement.get('best_individual_model', 'N/A')}")
        print(f"   최고 개별 R²: {ensemble_improvement.get('best_individual_r2', 'N/A'):.3f}")
        print(f"   앙상블 R²: {ensemble_improvement.get('ensemble_r2', 'N/A'):.3f}")
        print(f"   개선도: {ensemble_improvement.get('improvement', 'N/A'):.3f}")
        print(f"   개선률: {ensemble_improvement.get('improvement_percentage', 'N/A'):.1f}%")
        
        # 8. 특성 중요도 출력
        print("\n🎯 특성 중요도 (Random Forest):")
        feature_importance = hybrid_result.get('feature_importance', {}).get('random_forest', {})
        
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:5]:  # 상위 5개
            print(f"   {feature}: {importance:.3f}")
        
        # 9. 시스템 요약 출력
        print("\n📋 시스템 요약:")
        system_summary = phase2_system.get_system_summary()
        
        print(f"   Phase 1 상태: {system_summary.get('phase1_status', 'N/A')}")
        print(f"   딥러닝 상태: {system_summary.get('deep_learning_status', 'N/A')}")
        print(f"   하이브리드 시스템 상태: {system_summary.get('hybrid_system_status', 'N/A')}")
        
        # 10. 모델 저장 테스트
        print("\n💾 모델 저장 테스트 중...")
        save_success = phase2_system.save_models("./models")
        
        if save_success:
            print("✅ 모델 저장 성공")
        else:
            print("❌ 모델 저장 실패")
        
        print("\n🎉 Phase 2 딥러닝 통합 시스템 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_phase2_integration()
    sys.exit(0 if success else 1)
