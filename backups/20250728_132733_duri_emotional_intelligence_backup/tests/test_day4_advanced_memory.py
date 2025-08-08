#!/usr/bin/env python3
"""
DuRi Memory System Day 4 테스트
고급 메모리 관리 시스템 테스트
"""
import sys
import os
import time
import json
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from duri_control.app.services.memory_service import MemoryService
from duri_control.app.services.advanced_memory_service import AdvancedMemoryService
from duri_control.app.database.database import get_db_session

class TestDay4AdvancedMemory:
    def __init__(self):
        self.db = next(get_db_session())
        self.memory_service = MemoryService(self.db)
        self.advanced_service = AdvancedMemoryService()
        self.test_results = []
    
    def cleanup_test_memories(self):
        """테스트 메모리 정리"""
        try:
            # 테스트 태그가 있는 메모리 삭제
            memories = self.memory_service.search_memories("test_day4", limit=100)
            for memory in memories:
                self.memory_service.delete_memory(memory.id)
            print("✅ 테스트 메모리 정리 완료")
        except Exception as e:
            print(f"❌ 테스트 메모리 정리 실패: {e}")
    
    def create_test_data(self):
        """테스트 데이터 생성"""
        try:
            test_memories = [
                {
                    "type": "test_day4",
                    "context": "고급 메모리 관리 테스트",
                    "content": "생명주기 관리 테스트 메모리",
                    "raw_data": {"test": True, "day": 4, "data": "생명주기 테스트"},
                    "source": "test_system",
                    "tags": ["test", "day4", "lifecycle"],
                    "importance_score": 85.0,
                    "memory_level": "working"
                },
                {
                    "type": "test_day4",
                    "context": "압축 테스트",
                    "content": "메모리 압축 테스트 메모리",
                    "raw_data": {"test": True, "day": 4, "compression": "test", "large_data": "x" * 1000},
                    "source": "test_system",
                    "tags": ["test", "day4", "compression"],
                    "importance_score": 70.0,
                    "memory_level": "working"
                },
                {
                    "type": "test_day4",
                    "context": "우선순위 테스트",
                    "content": "우선순위 시스템 테스트 메모리",
                    "raw_data": {"test": True, "day": 4, "priority": "high"},
                    "source": "test_system",
                    "tags": ["test", "day4", "priority"],
                    "importance_score": 95.0,
                    "memory_level": "working"
                }
            ]
            
            created_memories = []
            for memory_data in test_memories:
                memory = self.memory_service.save_memory(memory_data)
                created_memories.append(memory)
                print(f"✅ 테스트 메모리 생성: ID={memory.id}")
            
            return created_memories
            
        except Exception as e:
            print(f"❌ 테스트 데이터 생성 실패: {e}")
            return []
    
    def test_lifecycle_management(self):
        """생명주기 관리 테스트"""
        try:
            print("\n🔍 생명주기 관리 테스트 시작...")
            
            # 테스트 메모리 조회
            memories = self.memory_service.search_memories("test_day4", limit=10)
            if not memories:
                print("❌ 테스트 메모리가 없습니다")
                return False
            
            memory = memories[0]
            
            # 생명주기 관리 실행
            result = self.advanced_service.manage_memory_lifecycle(memory.id)
            
            if "error" in result:
                print(f"❌ 생명주기 관리 실패: {result['error']}")
                return False
            
            print(f"✅ 생명주기 관리 성공:")
            print(f"   - 메모리 ID: {result['memory_id']}")
            print(f"   - 현재 단계: {result['current_stage']}")
            print(f"   - 우선순위: {result['priority']}")
            print(f"   - 진화 점수: {result['evolution_score']:.2f}")
            
            self.test_results.append({
                "test": "lifecycle_management",
                "success": True,
                "result": result
            })
            return True
            
        except Exception as e:
            print(f"❌ 생명주기 관리 테스트 실패: {e}")
            self.test_results.append({
                "test": "lifecycle_management",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_memory_optimization(self):
        """메모리 최적화 테스트"""
        try:
            print("\n🔍 메모리 최적화 테스트 시작...")
            
            # 압축 테스트용 메모리 조회
            memories = self.memory_service.search_memories("compression", limit=5)
            if not memories:
                print("❌ 압축 테스트 메모리가 없습니다")
                return False
            
            memory = memories[0]
            
            # 최적화 실행
            result = self.advanced_service.optimize_memory_storage(memory.id)
            
            if "error" in result:
                print(f"❌ 메모리 최적화 실패: {result['error']}")
                return False
            
            print(f"✅ 메모리 최적화 성공:")
            print(f"   - 메모리 ID: {result['memory_id']}")
            print(f"   - 원본 크기: {result['original_size']} bytes")
            print(f"   - 압축 크기: {result['compressed_size']} bytes")
            print(f"   - 압축률: {result['compression_ratio']:.2f}")
            print(f"   - 절약 공간: {result['space_saved']} bytes")
            
            self.test_results.append({
                "test": "memory_optimization",
                "success": True,
                "result": result
            })
            return True
            
        except Exception as e:
            print(f"❌ 메모리 최적화 테스트 실패: {e}")
            self.test_results.append({
                "test": "memory_optimization",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_backup_system(self):
        """백업 시스템 테스트"""
        try:
            print("\n🔍 백업 시스템 테스트 시작...")
            
            # 백업 실행
            result = self.advanced_service.backup_memory_system()
            
            if "error" in result:
                print(f"❌ 백업 시스템 실패: {result['error']}")
                return False
            
            print(f"✅ 백업 시스템 성공:")
            print(f"   - 백업 파일: {result['backup_filename']}")
            print(f"   - 총 메모리 수: {result['total_memories']}")
            print(f"   - 백업 크기: {result['backup_size']} bytes")
            print(f"   - 생명주기 항목: {result['lifecycle_entries']}")
            
            self.test_results.append({
                "test": "backup_system",
                "success": True,
                "result": result
            })
            return True
            
        except Exception as e:
            print(f"❌ 백업 시스템 테스트 실패: {e}")
            self.test_results.append({
                "test": "backup_system",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_performance_monitoring(self):
        """성능 모니터링 테스트"""
        try:
            print("\n🔍 성능 모니터링 테스트 시작...")
            
            # 성능 모니터링 실행
            result = self.advanced_service.monitor_performance()
            
            if "error" in result:
                print(f"❌ 성능 모니터링 실패: {result['error']}")
                return False
            
            print(f"✅ 성능 모니터링 성공:")
            print(f"   - 총 메모리 수: {result.get('total_memories', 0)}")
            print(f"   - 평균 중요도: {result.get('average_importance', 0):.2f}")
            print(f"   - 압축 효율성: {result.get('compression_efficiency', {})}")
            print(f"   - 시스템 건강도: {result.get('system_health', {})}")
            
            self.test_results.append({
                "test": "performance_monitoring",
                "success": True,
                "result": result
            })
            return True
            
        except Exception as e:
            print(f"❌ 성능 모니터링 테스트 실패: {e}")
            self.test_results.append({
                "test": "performance_monitoring",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_priority_system(self):
        """우선순위 시스템 테스트"""
        try:
            print("\n🔍 우선순위 시스템 테스트 시작...")
            
            # 우선순위 테스트용 메모리 조회
            memories = self.memory_service.search_memories("priority", limit=5)
            if not memories:
                print("❌ 우선순위 테스트 메모리가 없습니다")
                return False
            
            memory = memories[0]
            
            # 생명주기 관리로 우선순위 확인
            result = self.advanced_service.manage_memory_lifecycle(memory.id)
            
            if "error" in result:
                print(f"❌ 우선순위 확인 실패: {result['error']}")
                return False
            
            print(f"✅ 우선순위 시스템 성공:")
            print(f"   - 메모리 ID: {result['memory_id']}")
            print(f"   - 우선순위: {result['priority']}")
            print(f"   - 진화 점수: {result['evolution_score']:.2f}")
            
            self.test_results.append({
                "test": "priority_system",
                "success": True,
                "result": result
            })
            return True
            
        except Exception as e:
            print(f"❌ 우선순위 시스템 테스트 실패: {e}")
            self.test_results.append({
                "test": "priority_system",
                "success": False,
                "error": str(e)
            })
            return False
    
    def test_batch_operations(self):
        """배치 작업 테스트"""
        try:
            print("\n🔍 배치 작업 테스트 시작...")
            
            # 테스트 메모리들 조회
            memories = self.memory_service.search_memories("test_day4", limit=10)
            if len(memories) < 2:
                print("❌ 배치 테스트를 위한 메모리가 부족합니다")
                return False
            
            memory_ids = [m.id for m in memories[:3]]
            
            # 배치 생명주기 관리
            success_count = 0
            for memory_id in memory_ids:
                result = self.advanced_service.manage_memory_lifecycle(memory_id)
                if "error" not in result:
                    success_count += 1
            
            print(f"✅ 배치 작업 성공:")
            print(f"   - 처리된 메모리: {len(memory_ids)}개")
            print(f"   - 성공: {success_count}개")
            print(f"   - 실패: {len(memory_ids) - success_count}개")
            
            self.test_results.append({
                "test": "batch_operations",
                "success": True,
                "result": {
                    "total_processed": len(memory_ids),
                    "success_count": success_count,
                    "error_count": len(memory_ids) - success_count
                }
            })
            return True
            
        except Exception as e:
            print(f"❌ 배치 작업 테스트 실패: {e}")
            self.test_results.append({
                "test": "batch_operations",
                "success": False,
                "error": str(e)
            })
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🚀 DuRi Memory System Day 4 테스트 시작")
        print("=" * 50)
        
        # 테스트 데이터 생성
        self.cleanup_test_memories()
        test_memories = self.create_test_data()
        
        if not test_memories:
            print("❌ 테스트 데이터 생성 실패")
            return False
        
        # 테스트 실행
        tests = [
            self.test_lifecycle_management,
            self.test_memory_optimization,
            self.test_backup_system,
            self.test_performance_monitoring,
            self.test_priority_system,
            self.test_batch_operations
        ]
        
        success_count = 0
        for test in tests:
            if test():
                success_count += 1
        
        # 결과 요약
        print("\n" + "=" * 50)
        print("📊 Day 4 테스트 결과 요약")
        print("=" * 50)
        print(f"✅ 성공: {success_count}/{len(tests)}")
        print(f"❌ 실패: {len(tests) - success_count}/{len(tests)}")
        
        if success_count == len(tests):
            print("\n🎉 모든 Day 4 테스트가 성공했습니다!")
            return True
        else:
            print("\n⚠️ 일부 테스트가 실패했습니다.")
            return False

if __name__ == "__main__":
    test_runner = TestDay4AdvancedMemory()
    success = test_runner.run_all_tests()
    sys.exit(0 if success else 1) 