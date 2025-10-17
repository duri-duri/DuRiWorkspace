#!/usr/bin/env python3
"""
합성 트래픽 상시 주입: 무해화 (쓰기 금지, 다운스트림 호출 차단)
"""

import requests
import time
import random
import json
import os
from datetime import datetime

# 합성 트래픽 설정
SYNTHETIC_CONFIG = {
    "interval_seconds": 60,  # 1분 주기
    "endpoints": [
        {"url": "http://localhost:8083/health", "method": "GET", "weight": 1.0}  # 읽기 전용
    ],
    "headers": {
        "X-DuRi-Shadow": "1",
        "X-DuRi-Synthetic": "1",  # 합성 트래픽 식별
        "Content-Type": "application/json"
    }
}

# 환경 변수로 스테이지/프로드 분리
SYNTHETIC_BASE_URL = os.getenv("SYNTHETIC_BASE_URL", "http://localhost:8083")

def generate_synthetic_request():
    """합성 요청 생성 (읽기 전용)"""
    # 가중치 기반 엔드포인트 선택
    endpoints = SYNTHETIC_CONFIG["endpoints"]
    weights = [ep["weight"] for ep in endpoints]
    selected_endpoint = random.choices(endpoints, weights=weights)[0]
    
    # 읽기 전용 요청만 생성
    data = None
    
    return selected_endpoint, data

def send_synthetic_request():
    """합성 요청 전송 (무해화)"""
    try:
        endpoint, data = generate_synthetic_request()
        
        # 요청 전송 (읽기 전용)
        if endpoint["method"] == "GET":
            response = requests.get(
                f"{SYNTHETIC_BASE_URL}{endpoint['url'].replace('http://localhost:8083', '')}",
                headers=SYNTHETIC_CONFIG["headers"],
                timeout=10
            )
        else:
            # POST 요청은 차단 (쓰기 방지)
            print("🚫 합성 POST 요청 차단 (쓰기 방지)")
            return False
        
        # 결과 로깅
        status = "✅" if response.status_code == 200 else "❌"
        print(f"{status} 합성 트래픽: {endpoint['method']} {endpoint['url']} → {response.status_code}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"❌ 합성 트래픽 실패: {e}")
        return False

def run_synthetic_traffic():
    """합성 트래픽 실행 (무해화)"""
    print("🚀 합성 트래픽 시작 (무해화)")
    
    success_count = 0
    total_count = 0
    
    while True:
        try:
            success = send_synthetic_request()
            total_count += 1
            if success:
                success_count += 1
            
            # 성공률 로깅 (10회마다)
            if total_count % 10 == 0:
                success_rate = success_count / total_count
                print(f"📊 합성 트래픽 성공률: {success_rate:.1%} ({success_count}/{total_count})")
            
            time.sleep(SYNTHETIC_CONFIG["interval_seconds"])
            
        except KeyboardInterrupt:
            print("🛑 합성 트래픽 중지")
            break
        except Exception as e:
            print(f"❌ 합성 트래픽 오류: {e}")
            time.sleep(10)  # 오류 시 10초 대기

if __name__ == "__main__":
    run_synthetic_traffic()
