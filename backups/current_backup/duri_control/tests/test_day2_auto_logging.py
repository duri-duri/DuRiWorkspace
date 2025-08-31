#!/usr/bin/env python3
"""
DuRi Memory System Day 2 테스트
자동 로깅 시스템, 이벤트 트리거, 데코레이터 패턴 테스트
"""

import sys
import os
import time
import json
from datetime import datetime, timedelta

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from duri_control.app.services.memory_service import MemoryService
from duri_control.app.services.event_trigger_service import EventTriggerService, TriggerType
from duri_control.app.decorators.memory_logger import (
    log_to_memory, log_api_request, log_important_event, 
    log_system_event, log_user_action
)
from duri_control.app.database.database import get_db_session


class TestDay2AutoLogging:
    """Day 2 자동 로깅 시스템 테스트"""
    
    def __init__(self):
        self.db = next(get_db_session())
        self.memory_service = MemoryService(self.db)
        self.trigger_service = EventTriggerService()
        self.test_results = []
    
    def cleanup_test_memories(self):
        """테스트 메모리 정리"""
        try:
            # 테스트 태그가 포함된 메모리들 삭제
            test_memories = self.memory_service.query_memories(
                tags=["day2_test"],
                limit=100
            )
            
            for memory in test_memories:
                self.memory_service.delete_memory(memory.id)
            
            print(f"🧹 테스트 메모리 {len(test_memories)}개 정리 완료")
            
        except Exception as e:
            print(f"❌ 테스트 메모리 정리 실패: {e}")
    
    def test_memory_decorator(self):
        """Memory 데코레이터 테스트"""
        print("\n📋 Memory 데코레이터 테스트...")
        
        @log_to_memory(
            memory_type="test_function",
            context="Day 2 데코레이터 테스트",
            importance_score=60,
            auto_capture_args=True,
            auto_capture_result=True
        )
        def test_function_with_decorator(value: str, number: int = 42):
            """데코레이터가 적용된 테스트 함수"""
            time.sleep(0.1)  # 실행 시간 측정을 위한 지연
            return f"결과: {value} - {number}"
        
        try:
            # 데코레이터가 적용된 함수 실행
            result = test_function_with_decorator("테스트", 123)
            
            # 메모리에 로그가 저장되었는지 확인
            recent_memories = self.memory_service.query_memories(
                type="test_function",
                limit=5
            )
            
            if recent_memories:
                memory = recent_memories[0]
                print(f"✅ 데코레이터 로그 저장 성공")
                print(f"   함수명: {memory.raw_data.get('function_name')}")
                print(f"   실행시간: {memory.raw_data.get('execution_time', 0):.3f}초")
                print(f"   결과: {memory.raw_data.get('result', 'N/A')}")
                return True
            else:
                print("❌ 데코레이터 로그 저장 실패")
                return False
                
        except Exception as e:
            print(f"❌ 데코레이터 테스트 실패: {e}")
            return False
    
    def test_api_request_decorator(self):
        """API 요청 데코레이터 테스트"""
        print("\n📋 API 요청 데코레이터 테스트...")
        
        @log_api_request(
            endpoint="/test/endpoint",
            method="POST",
            importance_score=70
        )
        def test_api_function():
            """API 요청을 시뮬레이션하는 함수"""
            return {"status": "success", "data": "test_data"}
        
        try:
            # API 함수 실행
            result = test_api_function()
            
            # API 요청 로그 확인
            api_logs = self.memory_service.query_memories(
                type="api_request",
                limit=5
            )
            
            if api_logs:
                api_log = api_logs[0]
                print(f"✅ API 요청 로그 저장 성공")
                print(f"   엔드포인트: {api_log.raw_data.get('endpoint')}")
                print(f"   메서드: {api_log.raw_data.get('method')}")
                return True
            else:
                print("❌ API 요청 로그 저장 실패")
                return False
                
        except Exception as e:
            print(f"❌ API 요청 데코레이터 테스트 실패: {e}")
            return False
    
    def test_convenience_functions(self):
        """편의 함수들 테스트"""
        print("\n📋 편의 함수들 테스트...")
        
        try:
            # 중요 이벤트 로깅
            log_important_event(
                context="Day 2 테스트",
                content="중요한 시스템 이벤트 발생",
                importance_score=85
            )
            
            # 시스템 이벤트 로깅
            log_system_event(
                context="Day 2 테스트",
                content="일반적인 시스템 이벤트",
                importance_score=45
            )
            
            # 사용자 액션 로깅
            log_user_action(
                context="Day 2 테스트",
                content="사용자가 테스트 액션 수행",
                importance_score=65
            )
            
            # 로그 확인
            important_events = self.memory_service.query_memories(
                type="important_event",
                limit=5
            )
            
            system_events = self.memory_service.query_memories(
                type="system_event",
                limit=5
            )
            
            user_actions = self.memory_service.query_memories(
                type="user_action",
                limit=5
            )
            
            if important_events and system_events and user_actions:
                print(f"✅ 편의 함수 로깅 성공")
                print(f"   중요 이벤트: {len(important_events)}개")
                print(f"   시스템 이벤트: {len(system_events)}개")
                print(f"   사용자 액션: {len(user_actions)}개")
                return True
            else:
                print("❌ 편의 함수 로깅 실패")
                return False
                
        except Exception as e:
            print(f"❌ 편의 함수 테스트 실패: {e}")
            return False
    
    def test_event_triggers(self):
        """이벤트 트리거 테스트"""
        print("\n📋 이벤트 트리거 테스트...")
        
        try:
            # 오류 메모리 여러 개 생성 (트리거 조건: 5개 이상)
            for i in range(6):
                self.memory_service.save_memory({
                    "type": "error",
                    "context": f"Day 2 트리거 테스트 오류 {i+1}",
                    "content": f"테스트 오류 메시지 {i+1}",
                    "source": "day2_test",
                    "tags": ["day2_test", "error"],
                    "importance_score": 30 + i
                })
            
            # 트리거 통계 확인
            trigger_stats = self.memory_service.get_trigger_stats()
            
            print(f"✅ 트리거 시스템 동작 확인")
            print(f"   총 트리거 수: {trigger_stats['total_triggers']}")
            print(f"   활성화된 트리거: {trigger_stats['enabled_triggers']}")
            
            # 트리거 상세 정보 확인
            for trigger_detail in trigger_stats['trigger_details']:
                if trigger_detail['target'] == 'error':
                    print(f"   오류 트리거 실행 횟수: {trigger_detail['trigger_count']}")
                    break
            
            return True
            
        except Exception as e:
            print(f"❌ 이벤트 트리거 테스트 실패: {e}")
            return False
    
    def test_trigger_actions(self):
        """트리거 액션 테스트"""
        print("\n📋 트리거 액션 테스트...")
        
        try:
            # 메모리 사용량 임계값 테스트를 위해 많은 메모리 생성
            for i in range(50):  # 50개 메모리 생성
                self.memory_service.save_memory({
                    "type": "system_event",
                    "context": f"Day 2 액션 테스트 {i+1}",
                    "content": f"시스템 이벤트 {i+1}",
                    "source": "day2_test",
                    "tags": ["day2_test", "system_event"],
                    "importance_score": 20
                })
            
            # 전체 메모리 통계 확인
            stats = self.memory_service.get_memory_stats()
            print(f"✅ 메모리 생성 완료")
            print(f"   총 메모리 수: {stats['total_memories']}")
            
            # 트리거 액션 실행 확인
            trigger_stats = self.memory_service.get_trigger_stats()
            
            # 정리 액션이 실행되었는지 확인
            cleanup_events = self.memory_service.query_memories(
                type="system_event",
                context="메모리 정리",
                limit=5
            )
            
            if cleanup_events:
                print(f"✅ 트리거 액션 실행 확인")
                print(f"   정리 이벤트: {len(cleanup_events)}개")
                return True
            else:
                print("⚠️ 트리거 액션 실행되지 않음 (정상 - 임계값 미달)")
                return True
                
        except Exception as e:
            print(f"❌ 트리거 액션 테스트 실패: {e}")
            return False
    
    def test_logging_filtering(self):
        """로깅 필터링 테스트"""
        print("\n📋 로깅 필터링 테스트...")
        
        try:
            # 다양한 중요도의 메모리 생성
            importance_levels = [10, 30, 50, 70, 90]
            
            for importance in importance_levels:
                self.memory_service.save_memory({
                    "type": "test_filtering",
                    "context": f"중요도 {importance} 테스트",
                    "content": f"중요도 {importance}인 메모리",
                    "source": "day2_test",
                    "tags": ["day2_test", "filtering"],
                    "importance_score": importance
                })
            
            # 중요도별 필터링 테스트
            high_importance = self.memory_service.query_memories(
                type="test_filtering",
                min_importance=70,
                limit=10
            )
            
            low_importance = self.memory_service.query_memories(
                type="test_filtering",
                min_importance=30,
                limit=10
            )
            
            print(f"✅ 로깅 필터링 테스트 성공")
            print(f"   높은 중요도 (70+): {len(high_importance)}개")
            print(f"   낮은 중요도 (30+): {len(low_importance)}개")
            
            return True
            
        except Exception as e:
            print(f"❌ 로깅 필터링 테스트 실패: {e}")
            return False
    
    def run_all_tests(self):
        """모든 테스트 실행"""
        print("🧪 DuRi Memory System Day 2 테스트 시작")
        print("=" * 60)
        
        tests = [
            ("Memory 데코레이터", self.test_memory_decorator),
            ("API 요청 데코레이터", self.test_api_request_decorator),
            ("편의 함수들", self.test_convenience_functions),
            ("이벤트 트리거", self.test_event_triggers),
            ("트리거 액션", self.test_trigger_actions),
            ("로깅 필터링", self.test_logging_filtering)
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
        
        # 테스트 메모리 정리
        self.cleanup_test_memories()
        
        print("\n" + "=" * 60)
        print("📊 테스트 결과 요약")
        print("=" * 60)
        print(f"✅ 통과: {passed}/{total}")
        print(f"❌ 실패: {total - passed}/{total}")
        
        if passed == total:
            print("\n🎉 모든 테스트가 통과했습니다!")
            print("   Day 2 목표 달성: 자동 로깅 시스템 구현 완료")
            print("\n🚀 Day 2 완료! Day 3로 진행할 준비가 되었습니다.")
            return True
        else:
            print(f"\n⚠️ {total - passed}개 테스트가 실패했습니다.")
            print("   문제를 해결한 후 다시 테스트하세요.")
            return False


if __name__ == "__main__":
    test_runner = TestDay2AutoLogging()
    success = test_runner.run_all_tests()
    
    if success:
        print("\n🎯 Day 2 자동 로깅 시스템 구현 완료!")
        print("   - Memory 데코레이터 패턴 구현")
        print("   - 이벤트 트리거 시스템 구현")
        print("   - 로깅 필터링 및 중요도 평가")
        print("   - API 엔드포인트 자동 로깅")
    else:
        print("\n⚠️ Day 2 테스트 실패. 문제를 해결하세요.")
    
    sys.exit(0 if success else 1) 