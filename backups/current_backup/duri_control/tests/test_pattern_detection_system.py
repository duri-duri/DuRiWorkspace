#!/usr/bin/env python3
"""
DuRi Memory System Day 3 - 패턴 감지 및 승격 시스템 테스트
"""

import json
import requests
import time
from datetime import datetime

class TestPatternDetectionSystem:
    def __init__(self):
        self.base_url = "http://localhost:8083"
        self.test_memories = []
    
    def test_pattern_detection_save(self):
        """패턴 감지를 위한 테스트 기억 저장"""
        print("\n📋 패턴 감지 테스트 기억 저장...")
        
        # 반복 패턴을 위한 유사한 기억들 저장
        for i in range(3):
            memory = {
                "type": "test",
                "context": "Day 3 반복 패턴 테스트",
                "content": f"이것은 반복 패턴 테스트 {i+1}번째 기억입니다",
                "source": "cursor_ai",
                "tags": ["day3", "pattern", "test"],
                "memory_level": "short",
                "importance_score": 60
            }
            
            response = requests.post(f"{self.base_url}/memory/save", json=memory)
            if response.status_code == 200:
                result = response.json()
                memory_id = result["memory"]["id"]
                self.test_memories.append(memory_id)
                print(f"✅ 반복 패턴 기억 {i+1} 저장: ID={memory_id}")
            else:
                print(f"❌ 반복 패턴 기억 {i+1} 저장 실패: {response.status_code}")
                return False
        
        # 감정 강도가 높은 기억 저장
        emotional_memory = {
            "type": "test",
            "context": "Day 3 감정 강도 테스트",
            "content": "이것은 error와 frustration이 포함된 강한 감정의 기억입니다",
            "source": "user",
            "tags": ["day3", "error", "frustration", "test"],
            "memory_level": "short",
            "importance_score": 85
        }
        
        response = requests.post(f"{self.base_url}/memory/save", json=emotional_memory)
        if response.status_code == 200:
            result = response.json()
            memory_id = result["memory"]["id"]
            self.test_memories.append(memory_id)
            print(f"✅ 감정 강도 기억 저장: ID={memory_id}")
        else:
            print(f"❌ 감정 강도 기억 저장 실패: {response.status_code}")
            return False
        
        # 사용자 피드백 기억 저장
        feedback_memory = {
            "type": "test",
            "context": "Day 3 사용자 피드백 테스트",
            "content": "이것은 good과 helpful이 포함된 사용자 피드백입니다",
            "source": "user",
            "tags": ["day3", "feedback", "good", "test"],
            "memory_level": "short",
            "importance_score": 70
        }
        
        response = requests.post(f"{self.base_url}/memory/save", json=feedback_memory)
        if response.status_code == 200:
            result = response.json()
            memory_id = result["memory"]["id"]
            self.test_memories.append(memory_id)
            print(f"✅ 사용자 피드백 기억 저장: ID={memory_id}")
        else:
            print(f"❌ 사용자 피드백 기억 저장 실패: {response.status_code}")
            return False
        
        return True
    
    def test_pattern_analysis(self):
        """패턴 분석 테스트"""
        print("\n📋 패턴 분석 테스트...")
        
        if not self.test_memories:
            print("❌ 테스트 기억이 없습니다")
            return False
        
        # 첫 번째 기억의 패턴 분석
        memory_id = self.test_memories[0]
        response = requests.get(f"{self.base_url}/memory/analyze/{memory_id}")
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["analysis"]
            print(f"✅ 패턴 분석 성공: ID={memory_id}")
            print(f"   현재 레벨: {analysis['current_level']}")
            print(f"   반복 패턴: {analysis['repetition_patterns']['pattern_found']}")
            print(f"   감정 강도: {analysis['emotional_intensity']['intensity_level']}")
            print(f"   사용자 피드백: {analysis['user_feedback']['feedback_pattern']}")
        else:
            print(f"❌ 패턴 분석 실패: {response.status_code}")
            return False
        
        return True
    
    def test_manual_promotion(self):
        """수동 승격 테스트"""
        print("\n📋 수동 승격 테스트...")
        
        if not self.test_memories:
            print("❌ 테스트 기억이 없습니다")
            return False
        
        # 첫 번째 기억을 중기로 승격 시도
        memory_id = self.test_memories[0]
        response = requests.post(f"{self.base_url}/memory/promote/{memory_id}/medium")
        
        if response.status_code == 200:
            result = response.json()
            if result["success"]:
                print(f"✅ 중기 기억 승격 성공: ID={memory_id}")
                print(f"   승격 점수: {result['promotion_score']}")
                print(f"   승격 이유: {result['promotion_reasons']}")
            else:
                print(f"⚠️ 중기 기억 승격 조건 미충족: {result['message']}")
                print(f"   현재 점수: {result['promotion_score']}")
        else:
            print(f"❌ 중기 기억 승격 실패: {response.status_code}")
            return False
        
        return True
    
    def test_auto_promotion(self):
        """자동 승격 테스트"""
        print("\n📋 자동 승격 테스트...")
        
        response = requests.post(f"{self.base_url}/memory/promote/auto")
        
        if response.status_code == 200:
            result = response.json()
            auto_results = result["results"]
            print(f"✅ 자동 승격 완료")
            print(f"   처리된 기억 수: {auto_results['total_processed']}")
            print(f"   단기→중기 승격: {len(auto_results['short_to_medium'])}개")
            print(f"   중기→Truth 승격: {len(auto_results['medium_to_truth'])}개")
        else:
            print(f"❌ 자동 승격 실패: {response.status_code}")
            return False
        
        return True
    
    def test_truth_promotion(self):
        """Truth 승격 테스트"""
        print("\n📋 Truth 승격 테스트...")
        
        # 중기 기억 조회
        response = requests.get(f"{self.base_url}/memory/level/medium")
        if response.status_code == 200:
            result = response.json()
            medium_memories = result["memories"]
            
            if medium_memories:
                # 첫 번째 중기 기억을 Truth로 승격 시도
                memory_id = medium_memories[0]["id"]
                response = requests.post(f"{self.base_url}/memory/promote/{memory_id}/truth")
                
                if response.status_code == 200:
                    result = response.json()
                    if result["success"]:
                        print(f"✅ Truth 승격 성공: ID={memory_id}")
                        print(f"   승격 점수: {result['promotion_score']}")
                        print(f"   승격 이유: {result['promotion_reasons']}")
                    else:
                        print(f"⚠️ Truth 승격 조건 미충족: {result['message']}")
                        print(f"   현재 점수: {result['promotion_score']}")
                else:
                    print(f"❌ Truth 승격 실패: {response.status_code}")
                    return False
            else:
                print("⚠️ 중기 기억이 없어 Truth 승격 테스트를 건너뜁니다")
        else:
            print(f"❌ 중기 기억 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def test_level_distribution(self):
        """레벨별 분포 테스트"""
        print("\n📋 레벨별 분포 테스트...")
        
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
        print("🧪 DuRi Memory System Day 3 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("패턴 감지 기억 저장", self.test_pattern_detection_save),
            ("패턴 분석", self.test_pattern_analysis),
            ("수동 승격", self.test_manual_promotion),
            ("자동 승격", self.test_auto_promotion),
            ("Truth 승격", self.test_truth_promotion),
            ("레벨별 분포", self.test_level_distribution)
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
            print("   Day 3 목표 달성: 패턴 감지 및 승격 알고리즘 구현 완료")
            print("\n🚀 Day 3 완료! Day 4로 진행할 준비가 되었습니다.")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False

if __name__ == "__main__":
    tester = TestPatternDetectionSystem()
    success = tester.run_all_tests()
    if success:
        print("\n🎯 Day 3 성공! DuRi가 학습하고 성장하는 AI로 진화했습니다.")
    else:
        print("\n🔧 Day 3 문제 해결이 필요합니다.") 