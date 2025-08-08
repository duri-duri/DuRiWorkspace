#!/usr/bin/env python3
"""
DuRi Memory System - Day 5 Realtime Sync Test
실시간 동기화 시스템 테스트
"""
import requests
import json
import time
import asyncio
import websockets
from datetime import datetime

def test_realtime_sync_apis():
    """실시간 동기화 API 테스트"""
    base_url = "http://localhost:8083"
    
    print("🔍 DuRi 실시간 동기화 API 테스트 시작")
    print("=" * 50)
    
    # 1. 동기화 상태 테스트
    print("\n1️⃣ 실시간 동기화 상태 테스트")
    try:
        response = requests.get(f"{base_url}/sync/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ 동기화 상태 조회 성공")
            print(f"   - 동기화 활성: {data['sync_status']['sync_enabled']}")
            print(f"   - 활성 연결 수: {data['sync_status']['active_connections']['total_connections']}")
            print(f"   - 이벤트 큐 크기: {data['sync_status']['event_queue_size']}")
        else:
            print(f"❌ 동기화 상태 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 동기화 상태 테스트 오류: {e}")
    
    # 2. 활성 연결 목록 테스트
    print("\n2️⃣ 활성 연결 목록 테스트")
    try:
        response = requests.get(f"{base_url}/sync/connections")
        if response.status_code == 200:
            data = response.json()
            print("✅ 활성 연결 목록 조회 성공")
            print(f"   - 총 연결 수: {data['active_connections']['total_connections']}")
            print(f"   - 연결 목록: {len(data['active_connections']['connections'])}개")
        else:
            print(f"❌ 활성 연결 목록 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 활성 연결 목록 테스트 오류: {e}")
    
    # 3. 연결 테스트
    print("\n3️⃣ 연결 테스트")
    try:
        response = requests.post(f"{base_url}/sync/test/connection")
        if response.status_code == 200:
            data = response.json()
            print("✅ 연결 테스트 성공")
            print(f"   - 테스트 ID: {data['test_result']['test_id']}")
            print(f"   - 활성 연결 수: {data['test_result']['active_connections']}")
        else:
            print(f"❌ 연결 테스트 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 연결 테스트 오류: {e}")
    
    # 4. 메모리 생성 알림 테스트
    print("\n4️⃣ 메모리 생성 알림 테스트")
    try:
        memory_data = {
            "id": 999,
            "type": "test_memory",
            "content": "테스트 메모리 생성",
            "importance_score": 85,
            "memory_level": "short"
        }
        response = requests.post(f"{base_url}/sync/notify/memory-created", json=memory_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 메모리 생성 알림 성공")
            print(f"   - 메모리 ID: {data['notification_result']['memory_id']}")
        else:
            print(f"❌ 메모리 생성 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메모리 생성 알림 테스트 오류: {e}")
    
    # 5. 메모리 업데이트 알림 테스트
    print("\n5️⃣ 메모리 업데이트 알림 테스트")
    try:
        memory_data = {
            "id": 999,
            "type": "test_memory",
            "content": "업데이트된 테스트 메모리",
            "importance_score": 90,
            "memory_level": "medium"
        }
        response = requests.post(f"{base_url}/sync/notify/memory-updated", json=memory_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 메모리 업데이트 알림 성공")
            print(f"   - 메모리 ID: {data['notification_result']['memory_id']}")
        else:
            print(f"❌ 메모리 업데이트 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메모리 업데이트 알림 테스트 오류: {e}")
    
    # 6. 메모리 삭제 알림 테스트
    print("\n6️⃣ 메모리 삭제 알림 테스트")
    try:
        response = requests.post(f"{base_url}/sync/notify/memory-deleted", params={"memory_id": 999})
        if response.status_code == 200:
            data = response.json()
            print("✅ 메모리 삭제 알림 성공")
            print(f"   - 메모리 ID: {data['notification_result']['memory_id']}")
        else:
            print(f"❌ 메모리 삭제 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메모리 삭제 알림 테스트 오류: {e}")
    
    # 7. 분석 완료 알림 테스트
    print("\n7️⃣ 분석 완료 알림 테스트")
    try:
        analysis_data = {
            "type": "pattern_analysis",
            "result": "새로운 패턴이 발견되었습니다",
            "confidence": 0.95,
            "patterns_found": 3
        }
        response = requests.post(f"{base_url}/sync/notify/analysis-completed", json=analysis_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 분석 완료 알림 성공")
            print(f"   - 분석 타입: {data['notification_result']['analysis_type']}")
        else:
            print(f"❌ 분석 완료 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 분석 완료 알림 테스트 오류: {e}")
    
    # 8. 시스템 알림 테스트
    print("\n8️⃣ 시스템 알림 테스트")
    try:
        alert_data = {
            "type": "performance_warning",
            "message": "시스템 성능이 저하되고 있습니다",
            "severity": "warning",
            "metric": "cpu_usage",
            "value": 85.5
        }
        response = requests.post(f"{base_url}/sync/notify/system-alert", json=alert_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 시스템 알림 성공")
            print(f"   - 알림 타입: {data['notification_result']['alert_type']}")
        else:
            print(f"❌ 시스템 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 시스템 알림 테스트 오류: {e}")
    
    # 9. 건강도 업데이트 알림 테스트
    print("\n9️⃣ 건강도 업데이트 알림 테스트")
    try:
        health_data = {
            "health_score": 95,
            "status": "healthy",
            "cpu_percent": 15.2,
            "memory_percent": 45.8,
            "disk_percent": 25.3
        }
        response = requests.post(f"{base_url}/sync/notify/health-update", json=health_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 건강도 업데이트 알림 성공")
            print(f"   - 건강도 점수: {data['notification_result']['health_score']}")
        else:
            print(f"❌ 건강도 업데이트 알림 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 건강도 업데이트 알림 테스트 오류: {e}")
    
    # 10. 이벤트 히스토리 테스트
    print("\n🔟 이벤트 히스토리 테스트")
    try:
        response = requests.get(f"{base_url}/sync/events?limit=20")
        if response.status_code == 200:
            data = response.json()
            print("✅ 이벤트 히스토리 조회 성공")
            print(f"   - 총 이벤트 수: {data['event_history']['total_events']}")
            print(f"   - 조회 제한: {data['event_history']['limit']}")
            
            # 최근 이벤트들 출력
            recent_events = data['event_history']['events'][-5:]
            print("   - 최근 5개 이벤트:")
            for i, event in enumerate(recent_events, 1):
                print(f"     {i}. {event['event_type']} - {event['timestamp']}")
        else:
            print(f"❌ 이벤트 히스토리 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 이벤트 히스토리 테스트 오류: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 실시간 동기화 API 테스트 완료!")
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_broadcast_apis():
    """브로드캐스트 API 테스트"""
    print("\n📡 브로드캐스트 API 테스트")
    print("=" * 30)
    
    base_url = "http://localhost:8083"
    
    # 1. 메모리 이벤트 브로드캐스트 테스트
    print("\n1️⃣ 메모리 이벤트 브로드캐스트 테스트")
    try:
        event_data = {
            "id": 1001,
            "type": "broadcast_test",
            "content": "브로드캐스트 테스트 메모리",
            "importance_score": 88,
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(f"{base_url}/sync/broadcast/memory", 
                               params={"event_type": "memory_created"},
                               json=event_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 메모리 이벤트 브로드캐스트 성공")
            print(f"   - 이벤트 타입: {data['broadcast_result']['event_type']}")
        else:
            print(f"❌ 메모리 이벤트 브로드캐스트 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메모리 이벤트 브로드캐스트 테스트 오류: {e}")
    
    # 2. 시스템 이벤트 브로드캐스트 테스트
    print("\n2️⃣ 시스템 이벤트 브로드캐스트 테스트")
    try:
        system_data = {
            "type": "system_maintenance",
            "message": "시스템 점검이 시작됩니다",
            "duration_minutes": 30,
            "affected_services": ["memory_service", "analysis_service"],
            "timestamp": datetime.now().isoformat()
        }
        response = requests.post(f"{base_url}/sync/broadcast/system",
                               params={"event_type": "system_alert"},
                               json=system_data)
        if response.status_code == 200:
            data = response.json()
            print("✅ 시스템 이벤트 브로드캐스트 성공")
            print(f"   - 이벤트 타입: {data['broadcast_result']['event_type']}")
        else:
            print(f"❌ 시스템 이벤트 브로드캐스트 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 시스템 이벤트 브로드캐스트 테스트 오류: {e}")
    
    print("\n✅ 브로드캐스트 API 테스트 완료!")

def test_sync_integration():
    """동기화 통합 테스트"""
    print("\n🔗 동기화 통합 테스트")
    print("=" * 30)
    
    base_url = "http://localhost:8083"
    
    # 연속 이벤트 생성 테스트
    print("📊 연속 이벤트 생성 테스트 (5회)")
    for i in range(5):
        try:
            # 메모리 생성 알림
            memory_data = {
                "id": 2000 + i,
                "type": f"integration_test_{i}",
                "content": f"통합 테스트 메모리 {i+1}",
                "importance_score": 70 + i * 5,
                "memory_level": "short"
            }
            response = requests.post(f"{base_url}/sync/notify/memory-created", json=memory_data)
            
            if response.status_code == 200:
                print(f"   {i+1}회 - 메모리 생성 알림 성공 (ID: {memory_data['id']})")
            else:
                print(f"   {i+1}회 - 메모리 생성 알림 실패")
            
            time.sleep(1)
            
        except Exception as e:
            print(f"   {i+1}회 - 오류: {e}")
    
    # 최종 이벤트 히스토리 확인
    print("\n📋 최종 이벤트 히스토리 확인")
    try:
        response = requests.get(f"{base_url}/sync/events?limit=50")
        if response.status_code == 200:
            data = response.json()
            total_events = data['event_history']['total_events']
            print(f"   - 총 이벤트 수: {total_events}")
            
            # 이벤트 타입별 통계
            event_types = {}
            for event in data['event_history']['events']:
                event_type = event['event_type']
                event_types[event_type] = event_types.get(event_type, 0) + 1
            
            print("   - 이벤트 타입별 통계:")
            for event_type, count in event_types.items():
                print(f"     * {event_type}: {count}개")
        else:
            print(f"   - 이벤트 히스토리 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"   - 이벤트 히스토리 확인 오류: {e}")
    
    print("\n✅ 동기화 통합 테스트 완료!")

if __name__ == "__main__":
    test_realtime_sync_apis()
    test_broadcast_apis()
    test_sync_integration() 