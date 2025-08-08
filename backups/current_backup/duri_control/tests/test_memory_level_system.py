#!/usr/bin/env python3
"""
DuRi Memory System Day 2 - 기억 레벨 시스템 테스트
"""

import json
import requests
import time
from datetime import datetime

class TestMemoryLevelSystem:
    def __init__(self):
        self.base_url = "http://localhost:8083"
        self.test_memories = []
    
    def test_memory_level_save(self):
        """기억 레벨 저장 테스트"""
        print("\n📋 기억 레벨 저장 테스트...")
        
        # 단기 기억 저장 테스트
        short_memory = {
            "type": "test",
            "context": "Day 2 단기 기억 테스트",
            "content": "이것은 단기 기억으로 저장될 테스트입니다",
            "source": "cursor_ai",
            "tags": ["day2", "short", "test"],
            "memory_level": "short"
        }
        
        response = requests.post(f"{self.base_url}/memory/save", json=short_memory)
        if response.status_code == 200:
            result = response.json()
            memory_id = result["memory"]["id"]
            self.test_memories.append(memory_id)
            print(f"✅ 단기 기억 저장 성공: ID={memory_id}")
            print(f"   레벨: {result['memory']['memory_level']}")
            print(f"   만료시간: {result['memory']['expires_at']}")
        else:
            print(f"❌ 단기 기억 저장 실패: {response.status_code}")
            return False
        
        # 중기 기억 저장 테스트
        medium_memory = {
            "type": "test",
            "context": "Day 2 중기 기억 테스트",
            "content": "이것은 중기 기억으로 저장될 테스트입니다",
            "source": "cursor_ai",
            "tags": ["day2", "medium", "test"],
            "memory_level": "medium",
            "importance_score": 75
        }
        
        response = requests.post(f"{self.base_url}/memory/save", json=medium_memory)
        if response.status_code == 200:
            result = response.json()
            memory_id = result["memory"]["id"]
            self.test_memories.append(memory_id)
            print(f"✅ 중기 기억 저장 성공: ID={memory_id}")
            print(f"   레벨: {result['memory']['memory_level']}")
            print(f"   만료시간: {result['memory']['expires_at']}")
        else:
            print(f"❌ 중기 기억 저장 실패: {response.status_code}")
            return False
        
        return True
    
    def test_memory_level_query(self):
        """레벨별 기억 조회 테스트"""
        print("\n📋 레벨별 기억 조회 테스트...")
        
        # 단기 기억 조회
        response = requests.get(f"{self.base_url}/memory/level/short")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 단기 기억 조회 성공: {result['count']}개")
        else:
            print(f"❌ 단기 기억 조회 실패: {response.status_code}")
            return False
        
        # 중기 기억 조회
        response = requests.get(f"{self.base_url}/memory/level/medium")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 중기 기억 조회 성공: {result['count']}개")
        else:
            print(f"❌ 중기 기억 조회 실패: {response.status_code}")
            return False
        
        # 장기 기억 조회 (비어있을 것)
        response = requests.get(f"{self.base_url}/memory/level/truth")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 장기 기억 조회 성공: {result['count']}개")
        else:
            print(f"❌ 장기 기억 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def test_memory_level_filter(self):
        """레벨 필터링 테스트"""
        print("\n📋 레벨 필터링 테스트...")
        
        # 단기 기억만 조회
        response = requests.get(f"{self.base_url}/memory/query?memory_level=short")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 단기 기억 필터링 성공: {result['count']}개")
        else:
            print(f"❌ 단기 기억 필터링 실패: {response.status_code}")
            return False
        
        # 중기 기억만 조회
        response = requests.get(f"{self.base_url}/memory/query?memory_level=medium")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 중기 기억 필터링 성공: {result['count']}개")
        else:
            print(f"❌ 중기 기억 필터링 실패: {response.status_code}")
            return False
        
        return True
    
    def test_cleanup_function(self):
        """만료 기억 정리 테스트"""
        print("\n📋 만료 기억 정리 테스트...")
        
        response = requests.post(f"{self.base_url}/memory/cleanup/expired")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 만료 기억 정리 성공: {result['deleted_count']}개 삭제")
        else:
            print(f"❌ 만료 기억 정리 실패: {response.status_code}")
            return False
        
        return True
    
    def test_memory_stats_with_levels(self):
        """레벨별 통계 테스트"""
        print("\n📋 레벨별 통계 테스트...")
        
        response = requests.get(f"{self.base_url}/memory/stats/overview")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 통계 조회 성공")
            print(f"   총 기억 수: {result.get('total_memories', 0)}")
            print(f"   최근 24시간: {result.get('recent_24h', 0)}")
        else:
            print(f"❌ 통계 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def cleanup_test_memories(self):
        """테스트 기억 정리"""
        print("\n🗑️ 테스트 기억 정리...")
        
        for memory_id in self.test_memories:
            response = requests.delete(f"{self.base_url}/memory/{memory_id}")
            if response.status_code == 200:
                print(f"✅ 기억 삭제 성공: ID={memory_id}")
            else:
                print(f"❌ 기억 삭제 실패: ID={memory_id}")
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 DuRi Memory System Day 2 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("기억 레벨 저장", self.test_memory_level_save),
            ("레벨별 기억 조회", self.test_memory_level_query),
            ("레벨 필터링", self.test_memory_level_filter),
            ("만료 기억 정리", self.test_cleanup_function),
            ("레벨별 통계", self.test_memory_stats_with_levels)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} 통과")
                else:
                    print(f"❌ {test_name} 실패")
            except Exception as e:
                print(f"❌ {test_name} 오류: {e}")
        
        # 테스트 기억 정리
        self.cleanup_test_memories()
        
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"✅ 통과: {passed}/{total}")
        print(f"❌ 실패: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 모든 테스트가 통과했습니다!")
            print("   Day 2 목표 달성: 기억 레벨 시스템 구현 완료")
            print("\n🚀 Day 2 완료! Day 3로 진행할 준비가 되었습니다.")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False

if __name__ == "__main__":
    tester = TestMemoryLevelSystem()
    success = tester.run_all_tests()
    if success:
        print("\n🎯 Day 2 성공! 기억의 철학적 구조가 구현되었습니다.")
    else:
        print("\n🔧 Day 2 문제 해결이 필요합니다.") 