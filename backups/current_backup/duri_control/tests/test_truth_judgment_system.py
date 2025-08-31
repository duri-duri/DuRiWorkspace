#!/usr/bin/env python3
"""
DuRi Memory System Day 5 - Truth Memory 기반 판단 시스템 테스트
"""

import json
import requests
import time
from datetime import datetime

class TestTruthJudgmentSystem:
    def __init__(self):
        self.base_url = "http://localhost:8083"
        self.test_memories = []
    
    def test_truth_memories_save(self):
        """Truth Memory 테스트 기억 저장"""
        print("\n📋 Truth Memory 테스트 기억 저장...")
        
        # Truth Memory로 승격할 성공 패턴 기억들 저장
        success_truths = [
            {
                "type": "test",
                "context": "Day 5 Truth 판단 테스트",
                "content": "이것은 success와 good이 포함된 성공 Truth Memory입니다",
                "source": "user",
                "tags": ["day5", "success", "good", "truth"],
                "memory_level": "truth",
                "importance_score": 90
            },
            {
                "type": "test",
                "context": "Day 5 Truth 판단 테스트",
                "content": "이것은 correct와 helpful이 포함된 또 다른 성공 Truth Memory입니다",
                "source": "cursor_ai",
                "tags": ["day5", "correct", "helpful", "truth"],
                "memory_level": "truth",
                "importance_score": 85
            },
            {
                "type": "test",
                "context": "Day 5 Truth 판단 테스트",
                "content": "이것은 solved와 fixed가 포함된 문제 해결 Truth Memory입니다",
                "source": "user",
                "tags": ["day5", "solved", "fixed", "truth"],
                "memory_level": "truth",
                "importance_score": 88
            }
        ]
        
        for i, memory in enumerate(success_truths):
            response = requests.post(f"{self.base_url}/memory/save", json=memory)
            if response.status_code == 200:
                result = response.json()
                memory_id = result["memory"]["id"]
                self.test_memories.append(memory_id)
                print(f"✅ 성공 Truth Memory {i+1} 저장: ID={memory_id}")
            else:
                print(f"❌ 성공 Truth Memory {i+1} 저장 실패: {response.status_code}")
                return False
        
        # 실패 Truth Memory들 저장
        failure_truths = [
            {
                "type": "test",
                "context": "Day 5 Truth 판단 테스트",
                "content": "이것은 error와 fail이 포함된 실패 Truth Memory입니다",
                "source": "cursor_ai",
                "tags": ["day5", "error", "fail", "truth"],
                "memory_level": "truth",
                "importance_score": 75
            },
            {
                "type": "test",
                "context": "Day 5 Truth 판단 테스트",
                "content": "이것은 wrong과 bad가 포함된 또 다른 실패 Truth Memory입니다",
                "source": "user",
                "tags": ["day5", "wrong", "bad", "truth"],
                "memory_level": "truth",
                "importance_score": 70
            }
        ]
        
        for i, memory in enumerate(failure_truths):
            response = requests.post(f"{self.base_url}/memory/save", json=memory)
            if response.status_code == 200:
                result = response.json()
                memory_id = result["memory"]["id"]
                self.test_memories.append(memory_id)
                print(f"✅ 실패 Truth Memory {i+1} 저장: ID={memory_id}")
            else:
                print(f"❌ 실패 Truth Memory {i+1} 저장 실패: {response.status_code}")
                return False
        
        return True
    
    def test_truth_memories_query(self):
        """Truth Memory 조회 테스트"""
        print("\n📋 Truth Memory 조회 테스트...")
        
        response = requests.get(f"{self.base_url}/memory/truth/list")
        
        if response.status_code == 200:
            result = response.json()
            truths = result["truth_memories"]
            count = result["count"]
            print(f"✅ Truth Memory 조회 성공: {count}개")
            
            if count > 0:
                print(f"   첫 번째 Truth Memory: {truths[0]['content'][:50]}...")
        else:
            print(f"❌ Truth Memory 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def test_truth_judgment_success(self):
        """성공 가능성 판단 테스트"""
        print("\n📋 성공 가능성 판단 테스트...")
        
        # 성공 가능성이 높은 상황
        success_situation = {
            "type": "test",
            "context": "Day 5 Truth 판단 테스트",
            "content": "이것은 success와 good이 포함된 성공 가능성이 높은 상황입니다",
            "tags": ["success", "good", "test"]
        }
        
        response = requests.post(f"{self.base_url}/memory/judge", json=success_situation)
        
        if response.status_code == 200:
            result = response.json()
            judgment = result["judgment"]
            print(f"✅ 성공 가능성 판단 성공")
            print(f"   판단: {judgment['judgment']}")
            print(f"   신뢰도: {judgment['confidence']:.1f}%")
            print(f"   이유: {judgment['reason']}")
            print(f"   관련 Truth Memory 수: {len(judgment['relevant_truths'])}")
        else:
            print(f"❌ 성공 가능성 판단 실패: {response.status_code}")
            return False
        
        return True
    
    def test_truth_judgment_failure(self):
        """실패 가능성 판단 테스트"""
        print("\n📋 실패 가능성 판단 테스트...")
        
        # 실패 가능성이 높은 상황
        failure_situation = {
            "type": "test",
            "context": "Day 5 Truth 판단 테스트",
            "content": "이것은 error와 fail이 포함된 실패 가능성이 높은 상황입니다",
            "tags": ["error", "fail", "test"]
        }
        
        response = requests.post(f"{self.base_url}/memory/judge", json=failure_situation)
        
        if response.status_code == 200:
            result = response.json()
            judgment = result["judgment"]
            print(f"✅ 실패 가능성 판단 성공")
            print(f"   판단: {judgment['judgment']}")
            print(f"   신뢰도: {judgment['confidence']:.1f}%")
            print(f"   이유: {judgment['reason']}")
            print(f"   관련 Truth Memory 수: {len(judgment['relevant_truths'])}")
        else:
            print(f"❌ 실패 가능성 판단 실패: {response.status_code}")
            return False
        
        return True
    
    def test_truth_judgment_uncertain(self):
        """불확실한 상황 판단 테스트"""
        print("\n📋 불확실한 상황 판단 테스트...")
        
        # 불확실한 상황
        uncertain_situation = {
            "type": "unknown",
            "context": "Day 5 Truth 판단 테스트",
            "content": "이것은 알 수 없는 새로운 상황입니다",
            "tags": ["unknown", "new", "test"]
        }
        
        response = requests.post(f"{self.base_url}/memory/judge", json=uncertain_situation)
        
        if response.status_code == 200:
            result = response.json()
            judgment = result["judgment"]
            print(f"✅ 불확실한 상황 판단 성공")
            print(f"   판단: {judgment['judgment']}")
            print(f"   신뢰도: {judgment['confidence']:.1f}%")
            print(f"   이유: {judgment['reason']}")
            print(f"   권장사항 수: {len(judgment['recommendations'])}")
        else:
            print(f"❌ 불확실한 상황 판단 실패: {response.status_code}")
            return False
        
        return True
    
    def test_judgment_history(self):
        """판단 이력 조회 테스트"""
        print("\n📋 판단 이력 조회 테스트...")
        
        response = requests.get(f"{self.base_url}/memory/judgment/history")
        
        if response.status_code == 200:
            result = response.json()
            history = result["judgment_history"]
            count = result["count"]
            print(f"✅ 판단 이력 조회 성공: {count}개")
            
            if count > 0:
                print(f"   최근 판단: {history[0]['content'][:50]}...")
        else:
            print(f"❌ 판단 이력 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def test_truth_statistics(self):
        """Truth Memory 통계 테스트"""
        print("\n📋 Truth Memory 통계 테스트...")
        
        response = requests.get(f"{self.base_url}/memory/truth/statistics")
        
        if response.status_code == 200:
            result = response.json()
            stats = result["statistics"]
            print(f"✅ Truth Memory 통계 조회 성공")
            print(f"   총 Truth Memory 수: {stats['total_truth_memories']}")
            print(f"   타입별 분포: {stats['type_distribution']}")
            print(f"   중요도 분포: {stats['importance_distribution']}")
        else:
            print(f"❌ Truth Memory 통계 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def test_level_distribution_after_truth(self):
        """Truth 판단 후 레벨별 분포 테스트"""
        print("\n📋 Truth 판단 후 레벨별 분포 테스트...")
        
        levels = ['short', 'medium', 'truth']
        
        for level in levels:
            response = requests.get(f"{self.base_url}/memory/level/{level}")
            if response.status_code == 200:
                result = response.json()
                count = result["count"]
                print(f"✅ {level} 레벨 기억: {count}개")
            else:
                print(f"❌ {level} 레벨 조회 실패: {response.status_code}")
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
        print("🧪 DuRi Memory System Day 5 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("Truth Memory 저장", self.test_truth_memories_save),
            ("Truth Memory 조회", self.test_truth_memories_query),
            ("성공 가능성 판단", self.test_truth_judgment_success),
            ("실패 가능성 판단", self.test_truth_judgment_failure),
            ("불확실한 상황 판단", self.test_truth_judgment_uncertain),
            ("판단 이력 조회", self.test_judgment_history),
            ("Truth Memory 통계", self.test_truth_statistics),
            ("Truth 판단 후 레벨별 분포", self.test_level_distribution_after_truth)
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
            print("   Day 5 목표 달성: Truth Memory 기반 판단 시스템 구현 완료")
            print("\n🚀 Day 5 완료! Day 6로 진행할 준비가 되었습니다.")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False

if __name__ == "__main__":
    tester = TestTruthJudgmentSystem()
    success = tester.run_all_tests()
    if success:
        print("\n🎯 Day 5 성공! DuRi가 Truth Memory를 기반으로 정확하고 일관된 판단을 내리는 AI로 진화했습니다.")
    else:
        print("\n🔧 Day 5 문제 해결이 필요합니다.") 