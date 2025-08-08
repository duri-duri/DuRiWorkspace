#!/usr/bin/env python3
"""
DuRi Memory System - Day 4 Performance Monitoring Test
성능 모니터링 API 테스트
"""
import requests
import json
import time
from datetime import datetime

def test_performance_monitoring_apis():
    """성능 모니터링 API 테스트"""
    base_url = "http://localhost:8083"
    
    print("🔍 DuRi 성능 모니터링 API 테스트 시작")
    print("=" * 50)
    
    # 1. 기본 메트릭 테스트
    print("\n1️⃣ 기본 성능 메트릭 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/basic")
        if response.status_code == 200:
            data = response.json()
            print("✅ 기본 메트릭 조회 성공")
            print(f"   - CPU 사용률: {data['basic_metrics']['system']['cpu_percent']}%")
            print(f"   - 메모리 사용률: {data['basic_metrics']['system']['memory_percent']}%")
            print(f"   - 총 메모리 수: {data['basic_metrics']['application']['total_memories']}")
            print(f"   - 응답 시간: {data['basic_metrics']['application']['response_time_ms']:.2f}ms")
        else:
            print(f"❌ 기본 메트릭 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 기본 메트릭 테스트 오류: {e}")
    
    # 2. 시스템 메트릭 테스트
    print("\n2️⃣ 시스템 메트릭 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/system")
        if response.status_code == 200:
            data = response.json()
            print("✅ 시스템 메트릭 조회 성공")
            print(f"   - CPU: {data['system_metrics']['cpu_percent']}%")
            print(f"   - 메모리: {data['system_metrics']['memory_percent']}%")
            print(f"   - 디스크: {data['system_metrics']['disk_percent']}%")
            print(f"   - 사용 가능 메모리: {data['system_metrics']['memory_available_mb']:.1f}MB")
        else:
            print(f"❌ 시스템 메트릭 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 시스템 메트릭 테스트 오류: {e}")
    
    # 3. 애플리케이션 메트릭 테스트
    print("\n3️⃣ 애플리케이션 메트릭 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/application")
        if response.status_code == 200:
            data = response.json()
            print("✅ 애플리케이션 메트릭 조회 성공")
            print(f"   - 총 메모리: {data['application_metrics']['total_memories']}")
            print(f"   - 평균 중요도: {data['application_metrics']['avg_importance']:.2f}")
            print(f"   - 분석 큐 크기: {data['application_metrics']['analysis_queue_size']}")
            print(f"   - 응답 시간: {data['application_metrics']['response_time_ms']:.2f}ms")
        else:
            print(f"❌ 애플리케이션 메트릭 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 애플리케이션 메트릭 테스트 오류: {e}")
    
    # 4. 리소스 건강도 테스트
    print("\n4️⃣ 리소스 건강도 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/health/resources")
        if response.status_code == 200:
            data = response.json()
            print("✅ 리소스 건강도 조회 성공")
            print(f"   - 건강도 점수: {data['health_resources']['health_score']}/100")
            print(f"   - 상태: {data['health_resources']['status']}")
            print(f"   - CPU: {data['health_resources']['system_metrics']['cpu_percent']}%")
            print(f"   - 메모리: {data['health_resources']['system_metrics']['memory_percent']}%")
        else:
            print(f"❌ 리소스 건강도 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 리소스 건강도 테스트 오류: {e}")
    
    # 5. 성능 알림 테스트
    print("\n5️⃣ 성능 알림 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/alerts")
        if response.status_code == 200:
            data = response.json()
            print("✅ 성능 알림 조회 성공")
            print(f"   - 총 알림 수: {data['performance_alerts']['total_alerts']}")
            print(f"   - 위험 알림: {data['performance_alerts']['critical_count']}")
            print(f"   - 경고 알림: {data['performance_alerts']['warning_count']}")
        else:
            print(f"❌ 성능 알림 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 성능 알림 테스트 오류: {e}")
    
    # 6. 성능 요약 테스트
    print("\n6️⃣ 성능 요약 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/summary")
        if response.status_code == 200:
            data = response.json()
            print("✅ 성능 요약 조회 성공")
            summary = data['performance_summary']['summary']
            print(f"   - 평균 CPU: {summary['avg_cpu_percent']}%")
            print(f"   - 평균 메모리: {summary['avg_memory_percent']}%")
            print(f"   - 평균 응답시간: {summary['avg_response_time_ms']:.2f}ms")
            print(f"   - 메트릭 수: {data['performance_summary']['metrics_count']}")
        else:
            print(f"❌ 성능 요약 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 성능 요약 테스트 오류: {e}")
    
    # 7. 모니터링 상태 테스트
    print("\n7️⃣ 모니터링 상태 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/status")
        if response.status_code == 200:
            data = response.json()
            print("✅ 모니터링 상태 조회 성공")
            print(f"   - 모니터링 활성: {data['monitoring_status']['monitoring_active']}")
            print(f"   - 수집 간격: {data['monitoring_status']['collection_interval_seconds']}초")
            print(f"   - 히스토리 크기: {data['monitoring_status']['metrics_history_size']}")
            print(f"   - 서비스 상태: {data['monitoring_status']['service_status']}")
        else:
            print(f"❌ 모니터링 상태 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 모니터링 상태 테스트 오류: {e}")
    
    # 8. 메트릭 수집 트리거 테스트
    print("\n8️⃣ 메트릭 수집 트리거 테스트")
    try:
        response = requests.post(f"{base_url}/metrics/collect")
        if response.status_code == 200:
            data = response.json()
            print("✅ 메트릭 수집 트리거 성공")
            print(f"   - 메시지: {data['collection_triggered']['message']}")
            print(f"   - 타임스탬프: {data['collection_triggered']['timestamp']}")
        else:
            print(f"❌ 메트릭 수집 트리거 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메트릭 수집 트리거 테스트 오류: {e}")
    
    # 9. 메트릭 히스토리 테스트
    print("\n9️⃣ 메트릭 히스토리 테스트")
    try:
        response = requests.get(f"{base_url}/metrics/history?hours=1")
        if response.status_code == 200:
            data = response.json()
            print("✅ 메트릭 히스토리 조회 성공")
            print(f"   - 총 레코드: {data['metrics_history']['total_records']}")
            print(f"   - 시간 범위: {data['metrics_history']['time_range_hours']}시간")
        else:
            print(f"❌ 메트릭 히스토리 조회 실패: {response.status_code}")
    except Exception as e:
        print(f"❌ 메트릭 히스토리 테스트 오류: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 성능 모니터링 API 테스트 완료!")
    print(f"📅 테스트 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def test_performance_monitoring_integration():
    """성능 모니터링 통합 테스트"""
    print("\n🔗 성능 모니터링 통합 테스트")
    print("=" * 30)
    
    base_url = "http://localhost:8083"
    
    # 연속 메트릭 수집 테스트
    print("📊 연속 메트릭 수집 테스트 (3회)")
    for i in range(3):
        try:
            response = requests.get(f"{base_url}/metrics/basic")
            if response.status_code == 200:
                data = response.json()
                print(f"   {i+1}회 - CPU: {data['basic_metrics']['system']['cpu_percent']}%, "
                      f"메모리: {data['basic_metrics']['system']['memory_percent']}%")
            time.sleep(2)
        except Exception as e:
            print(f"   {i+1}회 - 오류: {e}")
    
    # 건강도 변화 모니터링
    print("\n🏥 건강도 변화 모니터링")
    try:
        response = requests.get(f"{base_url}/metrics/health/resources")
        if response.status_code == 200:
            data = response.json()
            health_score = data['health_resources']['health_score']
            status = data['health_resources']['status']
            
            if health_score >= 80:
                print(f"   ✅ 시스템 상태 양호 (점수: {health_score}/100, 상태: {status})")
            elif health_score >= 60:
                print(f"   ⚠️ 시스템 상태 주의 (점수: {health_score}/100, 상태: {status})")
            else:
                print(f"   ❌ 시스템 상태 위험 (점수: {health_score}/100, 상태: {status})")
    except Exception as e:
        print(f"   ❌ 건강도 모니터링 오류: {e}")
    
    print("\n✅ 통합 테스트 완료!")

if __name__ == "__main__":
    test_performance_monitoring_apis()
    test_performance_monitoring_integration() 