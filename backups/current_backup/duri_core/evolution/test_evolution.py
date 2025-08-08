#!/usr/bin/env python3
"""
DuRi Evolution System Test Script

Evolution 시스템의 기능을 테스트하고 데모를 제공합니다.
"""

import os
import sys
import time
from datetime import datetime

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evolution.evolution_controller import EvolutionController
from evolution.action_executor import ExecutionContext
from duri_common.logger import get_logger

logger = get_logger("duri_evolution.test")


def test_basic_evolution_cycle():
    """기본 진화 사이클 테스트"""
    print("\n=== 기본 진화 사이클 테스트 ===")
    
    # Evolution Controller 초기화
    controller = EvolutionController(data_dir="test_evolution_data")
    
    # 진화 세션 시작
    session_id = controller.start_evolution_session({
        'test_type': 'basic_cycle',
        'description': '기본 진화 사이클 테스트'
    })
    print(f"진화 세션 시작: {session_id}")
    
    # 다양한 감정-액션 조합 테스트
    test_cases = [
        ('happy', {'intensity': 0.7, 'confidence': 0.8, 'action': 'console'}),
        ('sad', {'intensity': 0.5, 'confidence': 0.6, 'action': 'reflect'}),
        ('angry', {'intensity': 0.9, 'confidence': 0.4, 'action': 'wait'}),
        ('grateful', {'intensity': 0.6, 'confidence': 0.9, 'action': 'act'}),
        ('frustration', {'intensity': 0.8, 'confidence': 0.3, 'action': 'observe'})
    ]
    
    for emotion, context in test_cases:
        print(f"\n--- {emotion} 감정으로 {context['action']} 액션 실행 ---")
        
        # 진화 사이클 실행
        execution_result, recorded_result, learning_insights = controller.execute_evolution_cycle(
            emotion, context
        )
        
        if execution_result:
            print(f"  실행 결과: 성공={execution_result.success}, 점수={execution_result.result_score:.2f}")
            print(f"  피드백: {execution_result.feedback_text}")
            print(f"  학습 인사이트: {len(learning_insights)}개 생성")
        
        time.sleep(0.5)  # 실행 간격
    
    # 세션 종료
    session = controller.end_evolution_session()
    if session:
        print(f"\n세션 종료: 총 {session.total_actions}개 액션, 성공 {session.successful_actions}개")
    
    return controller


def test_adaptive_evolution():
    """적응형 진화 테스트"""
    print("\n=== 적응형 진화 테스트 ===")
    
    controller = EvolutionController(data_dir="test_evolution_data")
    session_id = controller.start_evolution_session({
        'test_type': 'adaptive_evolution',
        'description': '적응형 진화 테스트'
    })
    
    # 동일한 감정으로 여러 번 실행하여 학습 효과 확인
    emotion = 'happy'
    base_context = {'intensity': 0.6, 'confidence': 0.7}
    
    for i in range(5):
        print(f"\n--- 반복 실행 {i+1}/5 ---")
        
        # 적응형 진화 사이클 실행
        execution_result, recorded_result, learning_insights, evolution_metadata = controller.execute_adaptive_evolution_cycle(
            emotion, base_context, learning_rate=0.15
        )
        
        if execution_result:
            print(f"  실행 결과: 성공={execution_result.success}, 점수={execution_result.result_score:.2f}")
            print(f"  진화 상태: {evolution_metadata.get('evolution_state', 'unknown')}")
            print(f"  학습 인사이트: {len(learning_insights)}개")
        
        time.sleep(0.3)
    
    session = controller.end_evolution_session()
    return controller


def test_experience_learning():
    """경험 학습 테스트"""
    print("\n=== 경험 학습 테스트 ===")
    
    controller = EvolutionController(data_dir="test_evolution_data")
    
    # 다양한 시나리오로 경험 축적
    scenarios = [
        # 성공 시나리오들
        ('happy', {'intensity': 0.8, 'confidence': 0.9, 'action': 'console'}),
        ('happy', {'intensity': 0.7, 'confidence': 0.8, 'action': 'console'}),
        ('happy', {'intensity': 0.6, 'confidence': 0.7, 'action': 'console'}),
        
        # 실패 시나리오들
        ('angry', {'intensity': 0.9, 'confidence': 0.3, 'action': 'console'}),
        ('angry', {'intensity': 0.8, 'confidence': 0.4, 'action': 'console'}),
        
        # 성공 시나리오들
        ('angry', {'intensity': 0.7, 'confidence': 0.6, 'action': 'wait'}),
        ('angry', {'intensity': 0.6, 'confidence': 0.7, 'action': 'wait'}),
    ]
    
    session_id = controller.start_evolution_session({
        'test_type': 'experience_learning',
        'description': '경험 학습 테스트'
    })
    
    for i, (emotion, context) in enumerate(scenarios):
        print(f"\n--- 시나리오 {i+1}: {emotion} -> {context['action']} ---")
        
        execution_result, recorded_result, learning_insights = controller.execute_evolution_cycle(
            emotion, context
        )
        
        if execution_result:
            print(f"  결과: 성공={execution_result.success}, 점수={execution_result.result_score:.2f}")
            print(f"  인사이트: {len(learning_insights)}개")
    
    session = controller.end_evolution_session()
    
    # 경험 데이터 분석
    print("\n--- 경험 데이터 분석 ---")
    patterns = controller.experience_manager.get_experience_patterns()
    insights = controller.experience_manager.get_learning_insights()
    
    print(f"경험 패턴: {len(patterns)}개")
    for pattern in patterns[:3]:  # 상위 3개만 표시
        print(f"  {pattern.emotion} -> {pattern.action}: 성공률 {pattern.success_rate:.1%}, 신뢰도 {pattern.confidence_level:.1%}")
    
    print(f"학습 인사이트: {len(insights)}개")
    for insight in insights[:3]:  # 상위 3개만 표시
        print(f"  {insight.insight_type}: {insight.description}")
    
    return controller


def test_recommendation_system():
    """추천 시스템 테스트"""
    print("\n=== 추천 시스템 테스트 ===")
    
    controller = EvolutionController(data_dir="test_evolution_data")
    
    # 추천 테스트
    test_emotions = ['happy', 'sad', 'angry', 'grateful']
    
    for emotion in test_emotions:
        print(f"\n--- {emotion} 감정에 대한 추천 ---")
        
        context = {'intensity': 0.6, 'confidence': 0.7}
        recommendation = controller.experience_manager.get_recommended_action(
            emotion, context, confidence_threshold=0.5
        )
        
        if recommendation:
            action, confidence = recommendation
            print(f"  추천 액션: {action} (신뢰도: {confidence:.2f})")
        else:
            print(f"  추천 없음 (충분한 경험 데이터 없음)")


def test_statistics_and_insights():
    """통계 및 인사이트 테스트"""
    print("\n=== 통계 및 인사이트 테스트 ===")
    
    controller = EvolutionController(data_dir="test_evolution_data")
    
    # 종합 통계
    stats = controller.get_comprehensive_statistics()
    print("\n--- 종합 통계 ---")
    print(f"진화 메트릭: {stats.get('evolution_metrics', {})}")
    print(f"현재 세션: {stats.get('current_session', {})}")
    print(f"진화 상태: {stats.get('evolution_state', 'unknown')}")
    
    # 진화 인사이트
    insights = controller.get_evolution_insights(limit=5)
    print(f"\n--- 진화 인사이트 ({len(insights)}개) ---")
    for insight in insights:
        print(f"  {insight['title']}: {insight['description']}")


def cleanup_test_data():
    """테스트 데이터 정리"""
    print("\n=== 테스트 데이터 정리 ===")
    
    controller = EvolutionController(data_dir="test_evolution_data")
    
    # 데이터 내보내기 (선택사항)
    export_success = controller.export_evolution_data(".")
    if export_success:
        print("테스트 데이터 내보내기 완료")
    
    # 데이터 초기화
    reset_success = controller.reset_evolution_data(confirm=True)
    if reset_success:
        print("테스트 데이터 초기화 완료")


def main():
    """메인 테스트 함수"""
    print("DuRi Evolution System Test")
    print("=" * 50)
    
    try:
        # 1. 기본 진화 사이클 테스트
        controller1 = test_basic_evolution_cycle()
        
        # 2. 적응형 진화 테스트
        controller2 = test_adaptive_evolution()
        
        # 3. 경험 학습 테스트
        controller3 = test_experience_learning()
        
        # 4. 추천 시스템 테스트
        test_recommendation_system()
        
        # 5. 통계 및 인사이트 테스트
        test_statistics_and_insights()
        
        print("\n" + "=" * 50)
        print("모든 테스트 완료!")
        
        # 6. 데이터 정리 (선택사항)
        response = input("\n테스트 데이터를 정리하시겠습니까? (y/N): ")
        if response.lower() == 'y':
            cleanup_test_data()
        
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {e}")
        print(f"테스트 실패: {e}")


if __name__ == "__main__":
    main() 