#!/usr/bin/env python3
"""
DuRi Memory System Day 4 - 학습 분석 및 교정 시스템 테스트
"""

import json
import requests
import time
from datetime import datetime

class TestLearningAnalysisSystem:
    def __init__(self):
        self.base_url = "http://localhost:8083"
        self.test_memories = []
    
    def test_learning_memories_save(self):
        """학습 분석을 위한 테스트 기억 저장"""
        print("\n📋 학습 분석 테스트 기억 저장...")
        
        # 성공 패턴 기억들 저장
        success_memories = [
            {
                "type": "test",
                "context": "Day 4 학습 분석 테스트",
                "content": "이것은 success와 good이 포함된 성공 패턴 기억입니다",
                "source": "user",
                "tags": ["day4", "success", "good", "learning"],
                "memory_level": "medium",
                "importance_score": 85
            },
            {
                "type": "test",
                "context": "Day 4 학습 분석 테스트",
                "content": "이것은 correct와 helpful이 포함된 또 다른 성공 기억입니다",
                "source": "cursor_ai",
                "tags": ["day4", "correct", "helpful", "learning"],
                "memory_level": "medium",
                "importance_score": 75
            }
        ]
        
        for i, memory in enumerate(success_memories):
            response = requests.post(f"{self.base_url}/memory/save", json=memory)
            if response.status_code == 200:
                result = response.json()
                memory_id = result["memory"]["id"]
                self.test_memories.append(memory_id)
                print(f"✅ 성공 패턴 기억 {i+1} 저장: ID={memory_id}")
            else:
                print(f"❌ 성공 패턴 기억 {i+1} 저장 실패: {response.status_code}")
                return False
        
        # 실패 패턴 기억들 저장
        failure_memories = [
            {
                "type": "test",
                "context": "Day 4 학습 분석 테스트",
                "content": "이것은 error와 fail이 포함된 실패 패턴 기억입니다",
                "source": "cursor_ai",
                "tags": ["day4", "error", "fail", "learning"],
                "memory_level": "medium",
                "importance_score": 45
            },
            {
                "type": "test",
                "context": "Day 4 학습 분석 테스트",
                "content": "이것은 wrong과 bad가 포함된 또 다른 실패 기억입니다",
                "source": "user",
                "tags": ["day4", "wrong", "bad", "learning"],
                "memory_level": "medium",
                "importance_score": 35
            }
        ]
        
        for i, memory in enumerate(failure_memories):
            response = requests.post(f"{self.base_url}/memory/save", json=memory)
            if response.status_code == 200:
                result = response.json()
                memory_id = result["memory"]["id"]
                self.test_memories.append(memory_id)
                print(f"✅ 실패 패턴 기억 {i+1} 저장: ID={memory_id}")
            else:
                print(f"❌ 실패 패턴 기억 {i+1} 저장 실패: {response.status_code}")
                return False
        
        return True
    
    def test_learning_pattern_analysis(self):
        """학습 패턴 분석 테스트"""
        print("\n📋 학습 패턴 분석 테스트...")
        
        if not self.test_memories:
            print("❌ 테스트 기억이 없습니다")
            return False
        
        # 첫 번째 기억의 학습 패턴 분석
        memory_id = self.test_memories[0]
        response = requests.get(f"{self.base_url}/memory/learn/{memory_id}")
        
        if response.status_code == 200:
            result = response.json()
            analysis = result["analysis"]
            print(f"✅ 학습 패턴 분석 성공: ID={memory_id}")
            print(f"   학습 패턴 존재: {analysis['learning_patterns']}")
            print(f"   유사한 기억 수: {analysis.get('similar_count', 0)}")
            print(f"   일관성 점수: {analysis.get('consistency_score', 0)}")
            print(f"   개선 제안 수: {len(analysis.get('improvement_suggestions', []))}")
        else:
            print(f"❌ 학습 패턴 분석 실패: {response.status_code}")
            return False
        
        return True
    
    def test_memory_comparison(self):
        """기억 비교 분석 테스트"""
        print("\n📋 기억 비교 분석 테스트...")
        
        if len(self.test_memories) < 2:
            print("❌ 비교할 기억이 부족합니다")
            return False
        
        # 첫 번째와 두 번째 기억 비교
        memory_id_1 = self.test_memories[0]
        memory_id_2 = self.test_memories[1]
        
        response = requests.get(f"{self.base_url}/memory/compare/{memory_id_1}/{memory_id_2}")
        
        if response.status_code == 200:
            result = response.json()
            comparison = result["comparison"]
            print(f"✅ 기억 비교 분석 성공: {memory_id_1} vs {memory_id_2}")
            print(f"   유사점 수: {len(comparison['similarities'])}")
            print(f"   차이점 수: {len(comparison['differences'])}")
            print(f"   학습 인사이트 수: {len(comparison['learning_insights'])}")
        else:
            print(f"❌ 기억 비교 분석 실패: {response.status_code}")
            return False
        
        return True
    
    def test_learning_report_generation(self):
        """학습 리포트 생성 테스트"""
        print("\n📋 학습 리포트 생성 테스트...")
        
        if not self.test_memories:
            print("❌ 테스트 기억이 없습니다")
            return False
        
        # 첫 번째 기억의 학습 리포트 생성
        memory_id = self.test_memories[0]
        response = requests.get(f"{self.base_url}/memory/report/{memory_id}")
        
        if response.status_code == 200:
            result = response.json()
            report = result["report"]
            print(f"✅ 학습 리포트 생성 성공: ID={memory_id}")
            print(f"   기억 레벨: {report['memory_info']['level']}")
            print(f"   유사한 기억 수: {report['similar_memories_count']}")
            print(f"   비교 분석 수: {len(report['comparisons'])}")
            print(f"   요약: {report['summary'][:100]}...")
            print(f"   권장사항 수: {len(report['recommendations'])}")
        else:
            print(f"❌ 학습 리포트 생성 실패: {response.status_code}")
            return False
        
        return True
    
    def test_learning_insights(self):
        """학습 인사이트 조회 테스트"""
        print("\n📋 학습 인사이트 조회 테스트...")
        
        # 중기 기억의 학습 인사이트 조회
        response = requests.get(f"{self.base_url}/memory/insights/medium")
        
        if response.status_code == 200:
            result = response.json()
            insights = result["insights"]
            print(f"✅ 학습 인사이트 조회 성공")
            print(f"   기억 레벨: {insights['memory_level']}")
            print(f"   총 기억 수: {insights['total_memories']}")
            print(f"   성공 패턴 수: {insights['success_count']}")
            print(f"   실패 패턴 수: {insights['failure_count']}")
            print(f"   학습 패턴: {insights['learning_patterns']}")
            print(f"   권장사항 수: {len(insights['recommendations'])}")
        else:
            print(f"❌ 학습 인사이트 조회 실패: {response.status_code}")
            return False
        
        return True
    
    def test_truth_promotion_from_learning(self):
        """학습 기반 Truth 승격 테스트"""
        print("\n📋 학습 기반 Truth 승격 테스트...")
        
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
    
    def test_level_distribution_after_learning(self):
        """학습 후 레벨별 분포 테스트"""
        print("\n📋 학습 후 레벨별 분포 테스트...")
        
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
        print("🧪 DuRi Memory System Day 4 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("학습 분석 기억 저장", self.test_learning_memories_save),
            ("학습 패턴 분석", self.test_learning_pattern_analysis),
            ("기억 비교 분석", self.test_memory_comparison),
            ("학습 리포트 생성", self.test_learning_report_generation),
            ("학습 인사이트 조회", self.test_learning_insights),
            ("학습 기반 Truth 승격", self.test_truth_promotion_from_learning),
            ("학습 후 레벨별 분포", self.test_level_distribution_after_learning)
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
            print("   Day 4 목표 달성: 학습 및 교정 시스템 구현 완료")
            print("\n🚀 Day 4 완료! Day 5로 진행할 준비가 되었습니다.")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False

if __name__ == "__main__":
    tester = TestLearningAnalysisSystem()
    success = tester.run_all_tests()
    if success:
        print("\n🎯 Day 4 성공! DuRi가 비교, 학습, 교정을 수행하는 지능적 AI로 진화했습니다.")
    else:
        print("\n🔧 Day 4 문제 해결이 필요합니다.") 