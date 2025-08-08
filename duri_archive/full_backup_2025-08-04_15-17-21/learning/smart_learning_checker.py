"""
DuRi 스마트 학습 체커

챗지피티가 제안한 학습 루프 트리거 후 스마트 체크 및 자동 유예시간 최적화 시스템
"""

import time
import logging
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LearningLatencyData:
    """학습 지연시간 데이터"""
    cycle_id: str
    activation_time: datetime
    success_time: datetime
    latency_seconds: float
    success: bool

@dataclass
class LearningStuckDiagnostic:
    """학습 루프 정체 진단 데이터"""
    timestamp: datetime
    loop_flags: Dict[str, bool]
    last_trigger_time: Optional[datetime]
    trigger_steps: List[str]
    scheduler_blocking: bool
    fallback_triggered: bool
    activation_result: Optional[Dict[str, Any]]
    stuck_reason: str

class SmartLearningChecker:
    """스마트 학습 체커"""
    
    def __init__(self):
        """SmartLearningChecker 초기화"""
        self.default_max_wait = 30  # 기본 타임아웃을 30초로 변경
        self.latency_history: List[LearningLatencyData] = []
        self.adaptive_wait_enabled = True
        self.min_wait_time = 3
        self.max_wait_time = 60  # 최대 대기시간을 60초로 증가
        self.diagnostic_history: List[LearningStuckDiagnostic] = []
        
        logger.info("스마트 학습 체커 초기화 완료")
    
    def trigger_learning_with_smart_check(self, max_wait: Optional[int] = None) -> bool:
        """
        학습 루프를 트리거하고 스마트 체크를 수행합니다.
        
        Args:
            max_wait: 최대 대기 시간 (None이면 적응형 시간 사용)
            
        Returns:
            bool: 성공 여부
        """
        if max_wait is None:
            max_wait = self._get_adaptive_wait_time()
        
        logger.info(f"🚀 스마트 학습 체크 시작 (max_wait: {max_wait}초)")
        
        # 학습 루프 트리거
        activation_start = datetime.now()
        result = self._trigger_learning_loop()
        print(f"🚀 학습 루프 트리거 결과: {result}")
        
        if not result:
            print("❌ 학습 루프 트리거 실패")
            # 실패 시 진단 실행
            self._trace_learning_stuck_reason("트리거 실패")
            return False
        
        # 스마트 체크 수행 (타임아웃 보호)
        success = self._smart_check_activation_with_timeout(max_wait, activation_start)
        
        # 지연시간 데이터 기록
        self._record_latency_data(activation_start, success)
        
        return success
    
    def _trigger_learning_loop(self) -> bool:
        """학습 루프를 트리거합니다."""
        try:
            from duri_brain.learning.learning_loop_activator import activate_learning_loop
            result = activate_learning_loop()
            return result.success
        except Exception as e:
            logger.error(f"학습 루프 트리거 실패: {e}")
            return False
    
    def _smart_check_activation_with_timeout(self, max_wait: int, activation_start: datetime) -> bool:
        """타임아웃 보호가 포함된 활성화 상태를 스마트하게 체크합니다."""
        try:
            from duri_brain.learning.learning_loop_activator import get_learning_loop_activator
            activator = get_learning_loop_activator()
            
            wait = 0
            while wait < max_wait:
                status = activator.get_activation_status()
                if status.get("is_activated", False):
                    success_time = datetime.now()
                    latency = (success_time - activation_start).total_seconds()
                    print(f"✅ {wait}초 후 학습 루프 활성화 확인됨 (지연시간: {latency:.2f}초)")
                    return True
                
                time.sleep(1)
                wait += 1
                
                # 10초마다 진행상황 로그
                if wait % 10 == 0:
                    print(f"⏳ 활성화 대기 중... ({wait}/{max_wait}초)")
            
            # 타임아웃 발생 시 진단 실행
            print(f"❌ {max_wait}초 후 학습 루프 비활성 상태 → 진단 실행")
            self._trace_learning_stuck_reason("타임아웃")
            self._auto_fix_learning_loop()
            return False
            
        except Exception as e:
            logger.error(f"스마트 체크 실패: {e}")
            self._trace_learning_stuck_reason(f"스마트 체크 오류: {e}")
            return False
    
    def _auto_fix_learning_loop(self):
        """학습 루프 자동 수정을 수행합니다."""
        try:
            print("🔧 자동 수정 루프 시작...")
            
            # Fallback handler 실행
            from duri_core.utils.fallback_handler import get_fallback_handler
            fallback_handler = get_fallback_handler()
            
            if fallback_handler:
                fix_result = fallback_handler.auto_fix()
                print(f"🔧 자동 수정 결과: {fix_result}")
            else:
                print("⚠️ Fallback handler를 찾을 수 없음")
                
        except Exception as e:
            print(f"❌ 자동 수정 실패: {e}")
    
    def _trace_learning_stuck_reason(self, stuck_reason: str):
        """학습 루프 정체 원인을 추적하고 진단합니다."""
        print(f"\n🔍 === 학습 루프 정체 진단 시작: {stuck_reason} ===")
        
        try:
            # 1. 루프 플래그 상태 확인
            loop_flags = self._check_loop_flags()
            print(f"📋 루프 플래그 상태:")
            for flag, value in loop_flags.items():
                print(f"   - {flag}: {value}")
            
            # 2. 마지막 트리거 시간 및 단계별 진입 로그
            trigger_info = self._check_trigger_info()
            print(f"📋 트리거 정보:")
            print(f"   - 마지막 트리거 시간: {trigger_info.get('last_trigger_time', 'Unknown')}")
            print(f"   - 트리거 단계: {', '.join(trigger_info.get('trigger_steps', []))}")
            
            # 3. 스케줄러 블로킹 여부
            scheduler_status = self._check_scheduler_status()
            print(f"📋 스케줄러 상태:")
            print(f"   - 스케줄러 블로킹: {scheduler_status.get('blocking', False)}")
            print(f"   - 스케줄러 스레드 활성: {scheduler_status.get('thread_alive', False)}")
            
            # 4. Fallback 트리거 여부
            fallback_status = self._check_fallback_status()
            print(f"📋 Fallback 상태:")
            print(f"   - Fallback 트리거됨: {fallback_status.get('triggered', False)}")
            print(f"   - 마지막 오류: {fallback_status.get('last_error', 'None')}")
            
            # 5. 활성화 결과 확인
            activation_result = self._check_activation_result()
            print(f"📋 활성화 결과:")
            print(f"   - 성공 여부: {activation_result.get('success', False)}")
            print(f"   - 오류 메시지: {activation_result.get('error', 'None')}")
            
            # 진단 데이터 저장
            diagnostic = LearningStuckDiagnostic(
                timestamp=datetime.now(),
                loop_flags=loop_flags,
                last_trigger_time=trigger_info.get('last_trigger_time'),
                trigger_steps=trigger_info.get('trigger_steps', []),
                scheduler_blocking=scheduler_status.get('blocking', False),
                fallback_triggered=fallback_status.get('triggered', False),
                activation_result=activation_result,
                stuck_reason=stuck_reason
            )
            
            self.diagnostic_history.append(diagnostic)
            
            # 최근 5개 진단만 유지
            if len(self.diagnostic_history) > 5:
                self.diagnostic_history = self.diagnostic_history[-5:]
            
            print(f"\n✅ 진단 완료 - 정체 원인: {stuck_reason}")
            
        except Exception as e:
            print(f"❌ 진단 중 오류 발생: {e}")
    
    def _check_loop_flags(self) -> Dict[str, bool]:
        """루프 플래그 상태를 확인합니다."""
        try:
            from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
            from duri_brain.learning.learning_loop_activator import get_learning_loop_activator
            
            learning_loop_manager = get_learning_loop_manager()
            activator = get_learning_loop_activator()
            
            return {
                "is_running": learning_loop_manager.is_running if learning_loop_manager else False,
                "is_activated": activator.is_activated if activator else False,
                "loop_thread_alive": learning_loop_manager.loop_thread.is_alive() if learning_loop_manager and learning_loop_manager.loop_thread else False,
                "scheduler_thread_alive": activator.scheduler_thread.is_alive() if activator and activator.scheduler_thread else False
            }
        except Exception as e:
            logger.error(f"루프 플래그 확인 실패: {e}")
            return {"error": str(e)}
    
    def _check_trigger_info(self) -> Dict[str, Any]:
        """트리거 정보를 확인합니다."""
        try:
            from duri_brain.learning.learning_loop_activator import get_learning_loop_activator
            
            activator = get_learning_loop_activator()
            
            return {
                "last_trigger_time": getattr(activator, 'last_trigger_time', None) if activator else None,
                "trigger_steps": getattr(activator, 'trigger_steps', []) if activator else []
            }
        except Exception as e:
            logger.error(f"트리거 정보 확인 실패: {e}")
            return {"error": str(e)}
    
    def _check_scheduler_status(self) -> Dict[str, Any]:
        """스케줄러 상태를 확인합니다."""
        try:
            from duri_brain.learning.learning_loop_activator import get_learning_loop_activator
            
            activator = get_learning_loop_activator()
            
            if not activator or not activator.scheduler_thread:
                return {"blocking": False, "thread_alive": False}
            
            return {
                "blocking": not activator.scheduler_thread.is_alive(),
                "thread_alive": activator.scheduler_thread.is_alive()
            }
        except Exception as e:
            logger.error(f"스케줄러 상태 확인 실패: {e}")
            return {"error": str(e)}
    
    def _check_fallback_status(self) -> Dict[str, Any]:
        """Fallback 상태를 확인합니다."""
        try:
            from duri_core.utils.fallback_handler import get_fallback_handler
            
            fallback_handler = get_fallback_handler()
            
            if not fallback_handler:
                return {"triggered": False, "last_error": "Fallback handler not found"}
            
            return {
                "triggered": getattr(fallback_handler, 'last_triggered', False),
                "last_error": getattr(fallback_handler, 'last_error', None)
            }
        except Exception as e:
            logger.error(f"Fallback 상태 확인 실패: {e}")
            return {"error": str(e)}
    
    def _check_activation_result(self) -> Dict[str, Any]:
        """활성화 결과를 확인합니다."""
        try:
            from duri_brain.learning.learning_loop_activator import get_learning_loop_activator
            
            activator = get_learning_loop_activator()
            
            if not activator:
                return {"success": False, "error": "Activator not found"}
            
            return {
                "success": activator.is_activated,
                "error": getattr(activator, 'last_error', None)
            }
        except Exception as e:
            logger.error(f"활성화 결과 확인 실패: {e}")
            return {"error": str(e)}
    
    def _record_latency_data(self, activation_start: datetime, success: bool):
        """지연시간 데이터를 기록합니다."""
        try:
            from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
            learning_loop_manager = get_learning_loop_manager()
            
            cycle_id = learning_loop_manager.current_cycle_id if learning_loop_manager else "unknown"
            success_time = datetime.now()
            latency = (success_time - activation_start).total_seconds()
            
            latency_data = LearningLatencyData(
                cycle_id=cycle_id,
                activation_time=activation_start,
                success_time=success_time,
                latency_seconds=latency,
                success=success
            )
            
            self.latency_history.append(latency_data)
            
            # 최근 10개 데이터만 유지
            if len(self.latency_history) > 10:
                self.latency_history = self.latency_history[-10:]
            
            logger.info(f"지연시간 데이터 기록: {latency:.2f}초, 성공: {success}")
            
        except Exception as e:
            logger.error(f"지연시간 데이터 기록 실패: {e}")
    
    def _get_adaptive_wait_time(self) -> int:
        """적응형 대기 시간을 계산합니다."""
        if not self.adaptive_wait_enabled or not self.latency_history:
            return self.default_max_wait
        
        # 성공한 학습의 평균 지연시간 계산
        successful_latencies = [
            data.latency_seconds 
            for data in self.latency_history 
            if data.success
        ]
        
        if not successful_latencies:
            return self.default_max_wait
        
        avg_latency = sum(successful_latencies) / len(successful_latencies)
        
        # 평균 지연시간 + 2초 여유시간
        adaptive_wait = int(avg_latency + 2)
        
        # 최소/최대 범위 내로 제한
        adaptive_wait = max(self.min_wait_time, min(self.max_wait_time, adaptive_wait))
        
        logger.info(f"적응형 대기 시간 계산: 평균 {avg_latency:.2f}초 → {adaptive_wait}초")
        
        return adaptive_wait
    
    def set_adaptive_waiting_time(self, based_on: str = "last_successful_cycle_latency"):
        """적응형 대기 시간 설정을 업데이트합니다."""
        if based_on == "last_successful_cycle_latency":
            self.adaptive_wait_enabled = True
            logger.info("적응형 대기 시간 활성화: 최근 성공 사이클 지연시간 기반")
        else:
            self.adaptive_wait_enabled = False
            logger.info("적응형 대기 시간 비활성화")
    
    def get_latency_statistics(self) -> Dict[str, Any]:
        """지연시간 통계를 반환합니다."""
        if not self.latency_history:
            return {"message": "데이터 없음"}
        
        successful_latencies = [data.latency_seconds for data in self.latency_history if data.success]
        failed_count = len([data for data in self.latency_history if not data.success])
        
        stats = {
            "total_attempts": len(self.latency_history),
            "successful_attempts": len(successful_latencies),
            "failed_attempts": failed_count,
            "success_rate": len(successful_latencies) / len(self.latency_history) if self.latency_history else 0,
            "avg_latency": sum(successful_latencies) / len(successful_latencies) if successful_latencies else 0,
            "min_latency": min(successful_latencies) if successful_latencies else 0,
            "max_latency": max(successful_latencies) if successful_latencies else 0,
            "adaptive_wait_enabled": self.adaptive_wait_enabled,
            "current_adaptive_wait": self._get_adaptive_wait_time()
        }
        
        return stats
    
    def get_status(self) -> Dict[str, Any]:
        """스마트 체커 상태를 반환합니다."""
        return {
            "adaptive_wait_enabled": self.adaptive_wait_enabled,
            "default_max_wait": self.default_max_wait,
            "min_wait_time": self.min_wait_time,
            "max_wait_time": self.max_wait_time,
            "latency_history_count": len(self.latency_history),
            "current_adaptive_wait": self._get_adaptive_wait_time()
        }

# 전역 함수로 실행 가능하도록
def trigger_learning_with_smart_check(max_wait: Optional[int] = None) -> bool:
    """스마트 체크가 포함된 학습 트리거 (전역 함수)"""
    checker = SmartLearningChecker()
    return checker.trigger_learning_with_smart_check(max_wait)

def trace_learning_stuck_reason(stuck_reason: str = "수동 진단"):
    """학습 루프 정체 원인을 추적합니다 (전역 함수)"""
    checker = SmartLearningChecker()
    checker._trace_learning_stuck_reason(stuck_reason)

def set_adaptive_waiting_time(based_on: str = "last_successful_cycle_latency"):
    """적응형 대기 시간 설정 (전역 함수)"""
    checker = SmartLearningChecker()
    checker.set_adaptive_waiting_time(based_on)

def get_latency_statistics() -> Dict[str, Any]:
    """지연시간 통계 반환 (전역 함수)"""
    checker = SmartLearningChecker()
    return checker.get_latency_statistics()

def get_smart_checker_status() -> Dict[str, Any]:
    """스마트 체커 상태 반환 (전역 함수)"""
    checker = SmartLearningChecker()
    return checker.get_status()

def get_diagnostic_history() -> List[LearningStuckDiagnostic]:
    """진단 히스토리를 반환합니다 (전역 함수)"""
    checker = SmartLearningChecker()
    return checker.diagnostic_history

if __name__ == "__main__":
    # 스마트 체커 테스트 실행
    import sys
    sys.path.append('.')
    
    print("🧠 === 스마트 학습 체커 테스트 시작 ===")
    
    # 스마트 체커 상태 확인
    status = get_smart_checker_status()
    print(f"📋 스마트 체커 상태: {status}")
    
    # 적응형 대기 시간 설정
    set_adaptive_waiting_time("last_successful_cycle_latency")
    print("✅ 적응형 대기 시간 활성화")
    
    # 스마트 체크 테스트 (30초 타임아웃)
    print("\n🚀 스마트 학습 체크 테스트 (30초 타임아웃)...")
    success = trigger_learning_with_smart_check(max_wait=30)
    
    # 결과 분석
    print(f"\n🎯 테스트 결과: {'✅ 성공' if success else '❌ 실패'}")
    
    # 지연시간 통계 확인
    stats = get_latency_statistics()
    print(f"\n📊 지연시간 통계: {stats}")
    
    # 진단 히스토리 확인
    diagnostic_history = get_diagnostic_history()
    if diagnostic_history:
        print(f"\n🔍 최근 진단 기록: {len(diagnostic_history)}개")
        for i, diagnostic in enumerate(diagnostic_history[-3:], 1):
            print(f"   {i}. {diagnostic.timestamp}: {diagnostic.stuck_reason}")
    
    print("✅ === 스마트 학습 체커 테스트 완료 ===") 