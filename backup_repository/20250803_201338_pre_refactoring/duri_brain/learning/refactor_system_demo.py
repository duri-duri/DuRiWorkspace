"""
DuRi 리팩터링 예측 시스템 데모

전체 리팩터링 예측 시스템을 테스트하고 데모를 실행합니다.
"""

import logging
import time
import sys
from datetime import datetime
from typing import Dict, Any

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_performance_history():
    """PerformanceHistory 테스트"""
    print("\n📊 === PerformanceHistory 테스트 ===")
    try:
        # 절대 import로 변경
        import sys
        sys.path.append('.')
        from duri_brain.learning.performance_history import get_performance_history
        
        history = get_performance_history()
        history.start_collection()
        
        print("✅ 성능 데이터 수집 시작")
        time.sleep(10)  # 10초간 데이터 수집
        
        summary = history.get_performance_summary()
        print(f"📈 성능 요약: {summary}")
        
        history.stop_collection()
        print("✅ PerformanceHistory 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ PerformanceHistory 테스트 실패: {e}")
        return False

def test_degradation_predictor():
    """DegradationPredictor 테스트"""
    print("\n🔮 === DegradationPredictor 테스트 ===")
    try:
        # 절대 import로 변경
        import sys
        sys.path.append('.')
        from duri_brain.learning.degradation_predictor import get_degradation_predictor
        
        predictor = get_degradation_predictor()
        predictor.start_prediction()
        
        print("✅ 성능 저하 예측 시작")
        time.sleep(15)  # 15초간 예측 실행
        
        summary = predictor.get_prediction_summary()
        print(f"📊 예측 요약: {summary}")
        
        predictor.stop_prediction()
        print("✅ DegradationPredictor 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ DegradationPredictor 테스트 실패: {e}")
        return False

def test_refactor_controller():
    """RefactorPredictiveController 테스트"""
    print("\n🔧 === RefactorPredictiveController 테스트 ===")
    try:
        # 절대 import로 변경
        import sys
        sys.path.append('.')
        from duri_brain.learning.refactor_predictive_controller import get_refactor_controller
        
        controller = get_refactor_controller()
        controller.start_controller()
        
        print("✅ 리팩터링 컨트롤러 시작")
        time.sleep(10)  # 10초간 컨트롤러 실행
        
        summary = controller.get_task_summary()
        print(f"📋 작업 요약: {summary}")
        
        controller.stop_controller()
        print("✅ RefactorPredictiveController 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ RefactorPredictiveController 테스트 실패: {e}")
        return False

def test_integration():
    """통합 시스템 테스트"""
    print("\n🔗 === 리팩터링 예측 시스템 통합 테스트 ===")
    try:
        # 절대 import로 변경
        import sys
        sys.path.append('.')
        from duri_brain.learning.refactor_integration import integrate_refactor_system_with_learning
        
        manager = integrate_refactor_system_with_learning()
        
        print("✅ 리팩터링 예측 시스템 통합 완료")
        time.sleep(20)  # 20초간 통합 시스템 실행
        
        summary = manager.get_refactor_summary()
        print(f"📊 통합 요약: {summary}")
        
        # 자동 리팩터링 활성화 테스트
        print("\n🔄 자동 리팩터링 활성화 테스트")
        manager.enable_auto_refactor()
        time.sleep(5)
        
        # 자동 리팩터링 비활성화
        manager.disable_auto_refactor()
        
        print("✅ 통합 시스템 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 통합 시스템 테스트 실패: {e}")
        return False

def run_comprehensive_demo():
    """종합 데모 실행"""
    print("🚀 === DuRi 리팩터링 예측 시스템 종합 데모 ===")
    print(f"📅 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 테스트 결과 저장
    test_results = {}
    
    # 1. PerformanceHistory 테스트
    test_results['performance_history'] = test_performance_history()
    
    # 2. DegradationPredictor 테스트
    test_results['degradation_predictor'] = test_degradation_predictor()
    
    # 3. RefactorPredictiveController 테스트
    test_results['refactor_controller'] = test_refactor_controller()
    
    # 4. 통합 시스템 테스트
    test_results['integration'] = test_integration()
    
    # 결과 요약
    print("\n📋 === 데모 결과 요약 ===")
    success_count = sum(test_results.values())
    total_count = len(test_results)
    
    for test_name, success in test_results.items():
        status = "✅ 성공" if success else "❌ 실패"
        print(f"   {test_name}: {status}")
    
    print(f"\n📊 전체 성공률: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
    
    print(f"📅 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return test_results

def show_system_architecture():
    """시스템 아키텍처 설명"""
    print("\n🏗️ === DuRi 리팩터링 예측 시스템 아키텍처 ===")
    print("""
    📊 PerformanceHistory
    ├── 성능 데이터 수집 (30초마다)
    ├── SQLite 데이터베이스 저장
    ├── 성능 경향 분석 (24시간마다)
    └── 성능 요약 생성
    
    🔮 DegradationPredictor
    ├── 선형 회귀 기반 예측
    ├── 성능 저하 수준 판단
    ├── 리팩터링 권장사항 생성
    └── 예측 신뢰도 계산
    
    🔧 RefactorPredictiveController
    ├── 리팩터링 작업 관리
    ├── 백업 생성 및 롤백
    ├── 성능 측정 (이전/이후)
    └── 작업 우선순위 관리
    
    🔗 RefactorIntegrationManager
    ├── learning_loop와 통합
    ├── 자동/수동 모드 전환
    ├── 성능 경고 시 예측 트리거
    └── 긴급 리팩터링 실행
    """)

def show_usage_examples():
    """사용 예시"""
    print("\n💡 === 사용 예시 ===")
    print("""
    # 1. 시스템 통합
    from duri_brain.learning.refactor_integration import integrate_refactor_system_with_learning
    manager = integrate_refactor_system_with_learning()
    
    # 2. 자동 리팩터링 활성화
    manager.enable_auto_refactor()
    
    # 3. 시스템 상태 확인
    summary = manager.get_refactor_summary()
    print(summary)
    
    # 4. 수동 리팩터링 (기본값)
    manager.disable_auto_refactor()
    
    # 5. 개별 컴포넌트 사용
    from duri_brain.learning.performance_history import get_performance_history
    history = get_performance_history()
    perf_summary = history.get_performance_summary()
    
    from duri_brain.learning.degradation_predictor import get_degradation_predictor
    predictor = get_degradation_predictor()
    pred_summary = predictor.get_prediction_summary()
    
    from duri_brain.learning.refactor_predictive_controller import get_refactor_controller
    controller = get_refactor_controller()
    task_summary = controller.get_task_summary()
    """)

def main():
    """메인 함수"""
    print("🧠 === DuRi 리팩터링 예측 시스템 ===")
    print("목표: 성능 저하가 발생하기 전, DuRi가 스스로 구조적 리팩터링을 판단하고 실행")
    
    # 시스템 아키텍처 설명
    show_system_architecture()
    
    # 사용 예시
    show_usage_examples()
    
    # 사용자 선택
    print("\n🎯 실행할 작업을 선택하세요:")
    print("1. 종합 데모 실행 (모든 테스트)")
    print("2. 개별 컴포넌트 테스트")
    print("3. 시스템 아키텍처만 보기")
    print("4. 종료")
    
    try:
        choice = input("\n선택 (1-4): ").strip()
        
        if choice == "1":
            run_comprehensive_demo()
        elif choice == "2":
            print("\n개별 컴포넌트 테스트:")
            print("1. PerformanceHistory")
            print("2. DegradationPredictor")
            print("3. RefactorPredictiveController")
            print("4. 통합 시스템")
            
            sub_choice = input("선택 (1-4): ").strip()
            
            if sub_choice == "1":
                test_performance_history()
            elif sub_choice == "2":
                test_degradation_predictor()
            elif sub_choice == "3":
                test_refactor_controller()
            elif sub_choice == "4":
                test_integration()
            else:
                print("❌ 잘못된 선택입니다.")
        elif choice == "3":
            show_system_architecture()
        elif choice == "4":
            print("👋 종료합니다.")
        else:
            print("❌ 잘못된 선택입니다.")
            
    except KeyboardInterrupt:
        print("\n👋 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    main() 