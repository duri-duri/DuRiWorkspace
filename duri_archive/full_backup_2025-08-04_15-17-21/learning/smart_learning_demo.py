"""
DuRi 스마트 학습 체커 데모

챗지피티가 제안한 스마트 학습 체커의 실제 동작을 테스트합니다.
"""

import sys
import time
from datetime import datetime

# 프로젝트 루트를 Python 경로에 추가
sys.path.append('.')

def test_smart_learning_checker():
    """스마트 학습 체커를 테스트합니다."""
    print("🧠 === DuRi 스마트 학습 체커 데모 시작 ===")
    
    try:
        from duri_brain.learning.smart_learning_checker import (
            trigger_learning_with_smart_check,
            set_adaptive_waiting_time,
            get_latency_statistics,
            get_smart_checker_status,
            trace_learning_stuck_reason,
            get_diagnostic_history
        )
        
        # 1. 초기 상태 확인
        print("\n📋 1단계: 스마트 체커 초기 상태 확인")
        status = get_smart_checker_status()
        print(f"   - 적응형 대기 시간: {status.get('adaptive_wait_enabled', False)}")
        print(f"   - 기본 최대 대기: {status.get('default_max_wait', 0)}초")
        print(f"   - 최소/최대 대기: {status.get('min_wait_time', 0)}~{status.get('max_wait_time', 0)}초")
        
        # 2. 적응형 대기 시간 설정
        print("\n📋 2단계: 적응형 대기 시간 설정")
        set_adaptive_waiting_time("last_successful_cycle_latency")
        print("   ✅ 적응형 대기 시간 활성화 완료")
        
        # 3. 스마트 학습 체크 테스트 (30초 타임아웃)
        print("\n📋 3단계: 스마트 학습 체크 테스트 (30초 타임아웃)")
        print("   🚀 학습 루프 트리거 및 활성화 체크 시작...")
        
        start_time = time.time()
        success = trigger_learning_with_smart_check(max_wait=30)
        elapsed_time = time.time() - start_time
        
        print(f"   ⏱️  실행 시간: {elapsed_time:.2f}초")
        print(f"   🎯 결과: {'✅ 성공' if success else '❌ 실패'}")
        
        # 4. 결과 분석
        print("\n📋 4단계: 결과 분석")
        
        # 지연시간 통계
        stats = get_latency_statistics()
        print(f"   📊 지연시간 통계:")
        print(f"      - 총 시도: {stats.get('total_attempts', 0)}회")
        print(f"      - 성공: {stats.get('successful_attempts', 0)}회")
        print(f"      - 실패: {stats.get('failed_attempts', 0)}회")
        print(f"      - 성공률: {stats.get('success_rate', 0):.1%}")
        if stats.get('avg_latency', 0) > 0:
            print(f"      - 평균 지연시간: {stats.get('avg_latency', 0):.2f}초")
        
        # 진단 히스토리
        diagnostic_history = get_diagnostic_history()
        if diagnostic_history:
            print(f"   🔍 진단 기록: {len(diagnostic_history)}개")
            for i, diagnostic in enumerate(diagnostic_history[-3:], 1):
                print(f"      {i}. {diagnostic.timestamp.strftime('%H:%M:%S')}: {diagnostic.stuck_reason}")
        
        # 5. 수동 진단 테스트 (실패한 경우)
        if not success:
            print("\n📋 5단계: 수동 진단 실행")
            print("   🔍 학습 루프 정체 원인 수동 진단...")
            trace_learning_stuck_reason("데모 테스트 실패")
        
        print("\n✅ === 스마트 학습 체커 데모 완료 ===")
        return success
        
    except Exception as e:
        print(f"❌ 스마트 학습 체커 데모 실패: {e}")
        return False

def compare_with_chatgpt_proposal():
    """챗지피티 제안과 비교합니다."""
    print("\n📋 === 챗지피티 제안과 비교 ===")
    
    chatgpt_proposal = """
    ChatGPT 제안:
    1. trigger_new_learning_cycle_with_verification()
    2. 일정 시간 대기 (3-5초)
    3. 상태 확인 (is_active, current_cycle_id)
    4. 실패 시 원인 분석 및 재시도
    5. 최대 3회 재시도
    """
    
    our_implementation = """
    우리 구현:
    1. trigger_learning_with_smart_check()
    2. 적응형 대기 시간 (3-60초)
    3. 실시간 상태 체크 (1초 간격)
    4. 타임아웃 시 자동 진단 (trace_learning_stuck_reason)
    5. 진단 히스토리 관리
    6. Fallback handler 연동
    """
    
    print("✅ 구현된 기능:")
    print("   - 적응형 대기 시간 (ChatGPT 제안보다 고급)")
    print("   - 실시간 상태 체크 (ChatGPT 제안보다 정밀)")
    print("   - 자동 진단 시스템 (ChatGPT 제안에 없음)")
    print("   - 진단 히스토리 관리 (ChatGPT 제안에 없음)")
    print("   - Fallback handler 연동 (ChatGPT 제안에 없음)")
    
    print("\n🎯 개선점:")
    print("   - ChatGPT 제안보다 더 강력한 타임아웃 보호")
    print("   - 더 상세한 진단 정보 제공")
    print("   - 자동 복구 메커니즘 포함")

if __name__ == "__main__":
    # 메인 테스트 실행
    success = test_smart_learning_checker()
    
    # 챗지피티 제안과 비교
    compare_with_chatgpt_proposal()
    
    print(f"\n🎯 최종 결과: {'✅ 성공' if success else '❌ 실패'}")
    print("💡 실패한 경우 trace_learning_stuck_reason() 함수가 자동으로 실행되어 원인을 진단합니다.") 