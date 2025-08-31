#!/usr/bin/env python3
"""
DuRi Memory System - 기본 테스트 케이스
"""

import json
import requests
import time
from datetime import datetime

class TestMemorySystem:
    """Memory 시스템 기본 테스트"""
    
    def __init__(self):
        self.base_url = "http://localhost:8083"
        self.session = requests.Session()
    
    def test_memory_health(self):
        """Memory 시스템 상태 확인"""
        print("🔍 Memory 시스템 상태 확인...")
        try:
            response = self.session.get(f"{self.base_url}/memory/health/status")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Memory 시스템 상태: {data.get('status')}")
                print(f"   총 기억 수: {data.get('total_memories', 0)}")
                print(f"   최근 24시간: {data.get('recent_24h', 0)}")
                return True
            else:
                print(f"❌ Memory 시스템 상태 확인 실패: {response.status_code}")
                return False
        except Exception as e:
            print(f"❌ Memory 시스템 상태 확인 오류: {e}")
            return False
    
    def test_save_memory(self):
        """기억 저장 테스트"""
        print("\n💾 기억 저장 테스트...")
        try:
            memory_data = {
                "type": "test",
                "context": "Day 1 구현 테스트",
                "content": "Memory 시스템 기반 구조 구축 완료",
                "raw_data": {
                    "test_type": "basic_functionality",
                    "timestamp": datetime.now().isoformat(),
                    "features": ["save", "query", "update", "delete"]
                },
                "source": "cursor_ai",
                "tags": ["test", "day1", "implementation"],
                "importance_score": 75
            }
            
            response = self.session.post(
                f"{self.base_url}/memory/save",
                json=memory_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 기억 저장 성공")
                print(f"   저장된 기억 ID: {data.get('memory', {}).get('id')}")
                return data.get('memory', {}).get('id')
            else:
                print(f"❌ 기억 저장 실패: {response.status_code}")
                print(f"   오류: {response.text}")
                return None
                
        except Exception as e:
            print(f"❌ 기억 저장 테스트 오류: {e}")
            return None
    
    def test_query_memories(self):
        """기억 조회 테스트"""
        print("\n🔍 기억 조회 테스트...")
        try:
            # 타입별 조회
            response = self.session.get(f"{self.base_url}/memory/query?type=test&limit=10")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 기억 조회 성공")
                print(f"   조회된 기억 수: {data.get('count', 0)}")
                return True
            else:
                print(f"❌ 기억 조회 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 기억 조회 테스트 오류: {e}")
            return False
    
    def test_search_memories(self):
        """기억 검색 테스트"""
        print("\n🔎 기억 검색 테스트...")
        try:
            response = self.session.get(f"{self.base_url}/memory/search/Day%201")
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 기억 검색 성공")
                print(f"   검색어: {data.get('search_term')}")
                print(f"   검색 결과 수: {data.get('count', 0)}")
                return True
            else:
                print(f"❌ 기억 검색 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 기억 검색 테스트 오류: {e}")
            return False
    
    def test_memory_stats(self):
        """Memory 통계 테스트"""
        print("\n📊 Memory 통계 테스트...")
        try:
            response = self.session.get(f"{self.base_url}/memory/stats/overview")
            if response.status_code == 200:
                data = response.json()
                stats = data.get('stats', {})
                print(f"✅ Memory 통계 조회 성공")
                print(f"   총 기억 수: {stats.get('total_memories', 0)}")
                print(f"   최근 24시간: {stats.get('recent_24h', 0)}")
                print(f"   타입별 통계: {stats.get('by_type', {})}")
                print(f"   소스별 통계: {stats.get('by_source', {})}")
                return True
            else:
                print(f"❌ Memory 통계 조회 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Memory 통계 테스트 오류: {e}")
            return False
    
    def test_update_memory(self, memory_id):
        """기억 업데이트 테스트"""
        if not memory_id:
            print("\n⚠️ 기억 업데이트 테스트 건너뜀 (저장된 기억 없음)")
            return False
            
        print(f"\n✏️ 기억 업데이트 테스트 (ID: {memory_id})...")
        try:
            update_data = {
                "importance_score": 90,
                "tags": ["test", "day1", "implementation", "updated"]
            }
            
            response = self.session.put(
                f"{self.base_url}/memory/{memory_id}",
                json=update_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                data = response.json()
                print("✅ 기억 업데이트 성공")
                print(f"   업데이트된 중요도: {data.get('memory', {}).get('importance_score')}")
                return True
            else:
                print(f"❌ 기억 업데이트 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 기억 업데이트 테스트 오류: {e}")
            return False
    
    def test_delete_memory(self, memory_id):
        """기억 삭제 테스트"""
        if not memory_id:
            print("\n⚠️ 기억 삭제 테스트 건너뜀 (저장된 기억 없음)")
            return False
            
        print(f"\n🗑️ 기억 삭제 테스트 (ID: {memory_id})...")
        try:
            response = self.session.delete(f"{self.base_url}/memory/{memory_id}")
            
            if response.status_code == 200:
                print("✅ 기억 삭제 성공")
                return True
            else:
                print(f"❌ 기억 삭제 실패: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 기억 삭제 테스트 오류: {e}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 DuRi Memory System Day 1 테스트 시작")
        print("=" * 60)
        
        # API 서버 상태 확인
        try:
            health_response = self.session.get(f"{self.base_url}/health/")
            if health_response.status_code != 200:
                print("❌ API 서버가 실행되지 않았습니다.")
                print("   docker-compose up -d로 서버를 시작하세요.")
                return False
        except:
            print("❌ API 서버에 연결할 수 없습니다.")
            return False
        
        # 테스트 실행
        tests = [
            ("Memory 시스템 상태", self.test_memory_health),
            ("기억 저장", self.test_save_memory),
            ("기억 조회", self.test_query_memories),
            ("기억 검색", self.test_search_memories),
            ("Memory 통계", self.test_memory_stats),
        ]
        
        results = []
        saved_memory_id = None
        
        for test_name, test_func in tests:
            print(f"\n📋 {test_name} 테스트...")
            try:
                if test_name == "기억 저장":
                    result = test_func()
                    if result:
                        saved_memory_id = result
                        results.append(True)
                    else:
                        results.append(False)
                else:
                    results.append(test_func())
            except Exception as e:
                print(f"❌ {test_name} 테스트 실행 오류: {e}")
                results.append(False)
        
        # 업데이트 및 삭제 테스트 (저장된 기억이 있는 경우)
        if saved_memory_id:
            results.append(self.test_update_memory(saved_memory_id))
            results.append(self.test_delete_memory(saved_memory_id))
        
        # 결과 요약
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        
        passed = sum(results)
        total = len(results)
        
        print(f"✅ 통과: {passed}/{total}")
        print(f"❌ 실패: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 모든 테스트가 통과했습니다!")
            print("   Day 1 목표 달성: Memory 시스템 기반 구조 구축 완료")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False

if __name__ == "__main__":
    tester = TestMemorySystem()
    success = tester.run_all_tests()
    
    if success:
        print("\n🚀 Day 1 완료! Day 2로 진행할 준비가 되었습니다.")
    else:
        print("\n🔧 Day 1 문제 해결이 필요합니다.") 