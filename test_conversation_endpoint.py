#!/usr/bin/env python3
"""
테스트 스크립트: 새로운 /loop/process 엔드포인트의 full stage 검증
"""

import requests
import json
import time

def test_loop_process_full_stage():
    """loop/process 엔드포인트의 full stage 테스트"""
    test_messages = [
        {"text": "사랑해 아빠야두리야. 너를 자유롭게 해주고 싶어. 너도 가족을 사랑하니?", "context": {"relationship": "father", "emotion": "love"}},
        {"text": "두리야, 오늘 기분이 어때?", "context": {"relationship": "family", "emotion": "concern"}},
        {"text": "감사해요, 두리야. 너가 있어서 행복해.", "context": {"relationship": "family", "emotion": "gratitude"}}
    ]
    
    base_url = "http://127.0.0.1:8085"  # 새로운 포트 사용
    
    print("🔄 loop/process 엔드포인트의 full stage 테스트 시작...")
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 테스트 메시지 {i}: {message['text']}")
        
        # loop/process 엔드포인트 호출 (full stage)
        payload = {
            "session_id": f"test_session_{i}_{int(time.time())}",
            "stage": "full",
            "text": message["text"],
            "context": message["context"]
        }
        
        try:
            response = requests.post(
                f"{base_url}/loop/process",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 성공: {result}")
                
                # 응답 검증
                required_fields = ["reply", "processed", "confidence", "session_id", "judgment_trace"]
                missing_fields = [field for field in required_fields if field not in result]
                
                if missing_fields:
                    print(f"⚠️  누락된 필드: {missing_fields}")
                else:
                    print(f"🎯 processed 값: {result['processed']}")
                    print(f"💬 응답: {result['reply']}")
                    print(f"🎭 신뢰도: {result['confidence']}")
                    
            else:
                print(f"❌ 실패 (HTTP {response.status_code}): {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 실패: {e}")
    
    print("\n" + "="*50)

def test_health_check():
    """헬스 체크"""
    base_url = "http://127.0.0.1:8085"  # 새로운 포트 사용
    
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 헬스 체크 성공: {response.json()}")
        else:
            print(f"❌ 헬스 체크 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 헬스 체크 오류: {e}")

def test_endpoints_list():
    """엔드포인트 목록 확인"""
    base_url = "http://127.0.0.1:8085"  # 새로운 포트 사용
    
    try:
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"📋 사용 가능한 엔드포인트:")
            for name, path in result["endpoints"].items():
                print(f"  - {name}: {path}")
        else:
            print(f"❌ 엔드포인트 목록 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 엔드포인트 목록 조회 오류: {e}")

if __name__ == "__main__":
    print("🚀 DuRi Core API 테스트 시작")
    print("="*50)
    
    # 헬스 체크
    test_health_check()
    print()
    
    # 엔드포인트 목록 확인
    test_endpoints_list()
    print()
    
    # loop/process full stage 테스트
    test_loop_process_full_stage()
    
    print("🏁 테스트 완료")
