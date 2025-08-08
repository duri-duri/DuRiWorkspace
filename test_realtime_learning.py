#!/usr/bin/env python3
"""
DuRi 실시간 학습 시스템 테스트
"""
import requests
import json
import time
from datetime import datetime

def test_realtime_learning_system():
    """실시간 학습 시스템 테스트"""
    base_url = "http://localhost:8088"
    print("🚀 DuRi 실시간 학습 시스템 테스트 시작...")
    
    # 1. 실시간 학습 시작
    print("\n1️⃣ 실시간 학습 시작")
    try:
        response = requests.post(f"{base_url}/realtime-learning/start")
        result = response.json()
        print(f"   결과: {result}")
        
        if result.get("status") == "success":
            print("   ✅ 실시간 학습 시작 성공")
        else:
            print("   ❌ 실시간 학습 시작 실패")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 2. 실시간 대화 추가 테스트
    print("\n2️⃣ 실시간 대화 추가 테스트")
    test_conversations = [
        {
            "user_input": "Python에서 리스트를 어떻게 만드나요?",
            "assistant_response": "Python에서 리스트는 대괄호 []를 사용하여 만들 수 있습니다. 예: my_list = [1, 2, 3]"
        },
        {
            "user_input": "함수는 어떻게 정의하나요?",
            "assistant_response": "def 키워드를 사용하여 함수를 정의합니다. 예: def my_function(): pass"
        },
        {
            "user_input": "클래스는 어떻게 만드나요?",
            "assistant_response": "class 키워드를 사용하여 클래스를 정의합니다. 예: class MyClass: pass"
        }
    ]
    
    for i, conversation in enumerate(test_conversations, 1):
        try:
            response = requests.post(f"{base_url}/realtime-learning/conversation", json=conversation)
            result = response.json()
            print(f"   대화 {i}: {result.get('status', 'unknown')}")
        except Exception as e:
            print(f"   대화 {i}: 오류 - {e}")
        
        time.sleep(1)  # 1초 대기
    
    # 3. 실시간 학습 상태 확인
    print("\n3️⃣ 실시간 학습 상태 확인")
    try:
        response = requests.get(f"{base_url}/realtime-learning/status")
        result = response.json()
        print(f"   결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get("status") == "success":
            realtime_data = result.get("realtime_learning", {})
            is_active = realtime_data.get("is_active", False)
            queue_size = realtime_data.get("queue_size", 0)
            
            print(f"   📊 활성 상태: {is_active}")
            print(f"   📊 큐 크기: {queue_size}")
        else:
            print("   ❌ 상태 확인 실패")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 4. 자동 학습 시스템과 연동 확인
    print("\n4️⃣ 자동 학습 시스템과 연동 확인")
    try:
        response = requests.get(f"{base_url}/autonomous-learning/status")
        result = response.json()
        
        if result.get("status") == "success":
            autonomous_data = result.get("autonomous_learning", {})
            learning_cycles = autonomous_data.get("total_learning_cycles", 0)
            problems_detected = autonomous_data.get("total_problems_detected", 0)
            
            print(f"   📊 학습 사이클: {learning_cycles}")
            print(f"   🚨 감지된 문제: {problems_detected}")
        else:
            print("   ❌ 자동 학습 상태 확인 실패")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 5. 실시간 학습 중지
    print("\n5️⃣ 실시간 학습 중지")
    try:
        response = requests.post(f"{base_url}/realtime-learning/stop")
        result = response.json()
        print(f"   결과: {result}")
        
        if result.get("status") == "success":
            print("   ✅ 실시간 학습 중지 성공")
        else:
            print("   ❌ 실시간 학습 중지 실패")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    print("\n🎉 DuRi 실시간 학습 시스템 테스트 완료!")

def test_realtime_learning_integration():
    """실시간 학습과 기존 시스템 통합 테스트"""
    base_url = "http://localhost:8088"
    print("\n🔄 실시간 학습과 기존 시스템 통합 테스트")
    
    # 1. 실시간 학습 시작
    print("\n1️⃣ 실시간 학습 시작")
    try:
        response = requests.post(f"{base_url}/realtime-learning/start")
        result = response.json()
        print(f"   결과: {result}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
        return
    
    # 2. 자동 학습 시작
    print("\n2️⃣ 자동 학습 시작")
    try:
        response = requests.post(f"{base_url}/autonomous-learning/start")
        result = response.json()
        print(f"   결과: {result}")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 3. 실시간 대화 시뮬레이션
    print("\n3️⃣ 실시간 대화 시뮬레이션")
    for i in range(5):
        conversation = {
            "user_input": f"테스트 질문 {i+1}: Python에서 무엇을 배울 수 있나요?",
            "assistant_response": f"Python에서는 웹 개발, 데이터 분석, AI, 자동화 등 다양한 것을 배울 수 있습니다. 테스트 응답 {i+1}입니다."
        }
        
        try:
            response = requests.post(f"{base_url}/realtime-learning/conversation", json=conversation)
            result = response.json()
            print(f"   대화 {i+1}: {result.get('status', 'unknown')}")
        except Exception as e:
            print(f"   대화 {i+1}: 오류 - {e}")
        
        time.sleep(2)  # 2초 대기
    
    # 4. 통합 상태 확인
    print("\n4️⃣ 통합 상태 확인")
    try:
        # 실시간 학습 상태
        response = requests.get(f"{base_url}/realtime-learning/status")
        realtime_result = response.json()
        
        # 자동 학습 상태
        response = requests.get(f"{base_url}/autonomous-learning/status")
        autonomous_result = response.json()
        
        if realtime_result.get("status") == "success" and autonomous_result.get("status") == "success":
            realtime_data = realtime_result.get("realtime_learning", {})
            autonomous_data = autonomous_result.get("autonomous_learning", {})
            
            print(f"   📊 실시간 학습 활성: {realtime_data.get('is_active', False)}")
            print(f"   📊 자동 학습 활성: {autonomous_data.get('is_running', False)}")
            print(f"   📊 학습 히스토리: {realtime_data.get('learning_history_count', 0)}")
        else:
            print("   ❌ 상태 확인 실패")
            
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    # 5. 시스템 중지
    print("\n5️⃣ 시스템 중지")
    try:
        requests.post(f"{base_url}/realtime-learning/stop")
        requests.post(f"{base_url}/autonomous-learning/stop")
        print("   ✅ 모든 시스템 중지 완료")
    except Exception as e:
        print(f"   ❌ 오류: {e}")
    
    print("\n✅ 실시간 학습 통합 테스트 완료!")

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 DuRi 실시간 학습 시스템 테스트")
    print("=" * 60)
    
    # 기본 테스트
    test_realtime_learning_system()
    
    # 통합 테스트
    test_realtime_learning_integration()
    
    print("\n" + "=" * 60)
    print("🎉 모든 테스트 완료!")
    print("=" * 60) 