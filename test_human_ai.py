#!/usr/bin/env python3
import requests
import json
import time

def test_human_ai_modules():
    base_url = "http://localhost:8088"
    
    print("🧠 DuRi 인간형 AI 모듈 테스트 시작...")
    
    # 테스트용 대화 히스토리
    conversation_history = [
        {
            "user_input": "DuRi 시스템을 개선하고 싶어",
            "duri_response": "좋은 아이디어입니다! 어떤 부분을 개선하고 싶으신가요?"
        },
        {
            "user_input": "자기학습 능력을 강화하고 싶어",
            "duri_response": "자기학습 능력은 매우 중요합니다. 현재 학습 루프를 분석해보겠습니다."
        },
        {
            "user_input": "뭐부터 시작할까?",
            "duri_response": "우선 현재 상태를 파악하고 단계별로 접근하는 것이 좋겠습니다."
        }
    ]
    
    # 1. 맥락 분석 테스트
    print("\n1️⃣ 맥락 분석 테스트...")
    try:
        data = {
            "conversation_history": conversation_history
        }
        response = requests.post(f"{base_url}/context-analyze", json=data)
        print(f"✅ 맥락 분석 성공: {response.status_code}")
        result = response.json()
        print(f"📊 주제: {result['context_analysis']['topic']}")
        print(f"📊 감정: {result['context_analysis']['emotion']}")
        print(f"📊 의도: {result['context_analysis']['intent']}")
        print(f"📊 신뢰도: {result['context_analysis']['confidence']:.3f}")
    except Exception as e:
        print(f"❌ 맥락 분석 실패: {e}")
    
    # 2. 직관적 판단 테스트
    print("\n2️⃣ 직관적 판단 테스트...")
    try:
        data = {
            "user_input": "뭐부터 시작할까?",
            "context": {
                "emotion": "focused",
                "intent": "planning",
                "confidence": 0.8
            }
        }
        response = requests.post(f"{base_url}/intuitive-judgment", json=data)
        print(f"✅ 직관적 판단 성공: {response.status_code}")
        result = response.json()
        if result['intuitive_judgment']:
            print(f"📊 직관 타입: {result['intuitive_judgment']['intuitive_type']}")
            print(f"📊 응답: {result['intuitive_judgment']['response']}")
            print(f"📊 신뢰도: {result['intuitive_judgment']['confidence']:.3f}")
        else:
            print("📊 직관적 판단이 트리거되지 않았습니다.")
    except Exception as e:
        print(f"❌ 직관적 판단 실패: {e}")
    
    # 3. 감정 분석 테스트
    print("\n3️⃣ 감정 분석 테스트...")
    try:
        data = {
            "text": "정말 좋은 아이디어야! 바로 시작해보자!",
            "context": {
                "emotion": "excited",
                "intent": "implementation",
                "confidence": 0.9
            }
        }
        response = requests.post(f"{base_url}/emotion-analyze", json=data)
        print(f"✅ 감정 분석 성공: {response.status_code}")
        result = response.json()
        print(f"📊 주요 감정: {result['emotion_analysis']['primary_emotion']}")
        print(f"📊 감정 강도: {result['emotion_analysis']['intensity']:.3f}")
        print(f"📊 신뢰도: {result['emotion_analysis']['confidence']:.3f}")
        print(f"📊 적응 톤: {result['adaptive_response']['tone']}")
    except Exception as e:
        print(f"❌ 감정 분석 실패: {e}")
    
    # 4. 통합 인간형 AI 응답 테스트
    print("\n4️⃣ 통합 인간형 AI 응답 테스트...")
    try:
        data = {
            "user_input": "DuRi가 진화할 수 있을까?",
            "conversation_history": conversation_history
        }
        response = requests.post(f"{base_url}/human-ai-response", json=data)
        print(f"✅ 통합 응답 성공: {response.status_code}")
        result = response.json()
        
        integrated = result['integrated_response']
        print(f"📊 응답 텍스트: {integrated['response_text']}")
        print(f"📊 톤: {integrated['tone']}")
        print(f"📊 스타일: {integrated['style']}")
        print(f"📊 감정: {integrated['emotion']}")
        print(f"📊 강도: {integrated['intensity']:.3f}")
        
        # 인간형 지표
        indicators = integrated['human_like_indicators']
        print(f"📊 맥락 인식: {indicators['context_aware']}")
        print(f"📊 감정 적응: {indicators['emotion_adaptive']}")
        print(f"📊 직관 트리거: {indicators['intuitive_triggered']}")
        print(f"📊 자연스러운 흐름: {indicators['natural_flow']}")
        
    except Exception as e:
        print(f"❌ 통합 응답 실패: {e}")
    
    print("\n🎉 인간형 AI 모듈 테스트 완료!")

if __name__ == "__main__":
    test_human_ai_modules() 