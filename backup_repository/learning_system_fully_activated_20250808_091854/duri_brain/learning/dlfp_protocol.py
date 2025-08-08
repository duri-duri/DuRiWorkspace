"""
DuRi Learning Feedback Protocol (DLFP)

챗지피티가 제안한 안전한 학습 루프 트리거 시스템
"""

import time
import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DLFPProtocol:
    """DuRi Learning Feedback Protocol 구현"""
    
    def __init__(self):
        """DLFP 초기화"""
        self.max_retries = 3
        self.verification_delay = 4  # 4초 대기
        self.fallback_conditions = [
            "SYSTEM_EVENT", 
            "AttributeError", 
            "MemorySyncError", 
            "TriggerTimeout", 
            "EmptyStrategyList"
        ]
        
        logger.info("DLFP 프로토콜 초기화 완료")
    
    def trigger_new_learning_cycle_with_verification(self, reason: str = "자동 학습 검증") -> bool:
        """
        학습 루프를 안전하게 트리거하고 검증합니다.
        
        Args:
            reason: 학습 트리거 이유
            
        Returns:
            bool: 성공 여부
        """
        logger.info(f"🚀 DLFP 학습 루프 트리거 시작: {reason}")
        
        for attempt in range(1, self.max_retries + 1):
            print(f"\n🚀 [{attempt}] 학습 루프 트리거 시도 중...")
            
            # 1단계: 학습 유도
            success = self._trigger_learning_cycle(reason)
            if not success:
                print(f"❌ [{attempt}] 학습 루프 트리거 실패")
                continue
            
            # 2단계: 유예 시간 후 상태 판별
            print(f"⏳ [{attempt}] 학습 활성화 대기 중... ({self.verification_delay}초)")
            time.sleep(self.verification_delay)
            
            # 3단계: 상태 확인
            verification_result = self._verify_learning_state()
            if verification_result["success"]:
                print("✅ 학습 루프 정상 시작됨")
                logger.info(f"DLFP 학습 루프 성공: {verification_result}")
                return True
            else:
                print(f"❌ [{attempt}] 학습 실패, 원인: {verification_result['cause']}")
                
                # 4단계: 자동 수정 및 재시도
                self._auto_fix_and_retry(verification_result["cause"])
        
        print("❌ 최대 재시도 초과. 수동 개입 필요")
        logger.error("DLFP 최대 재시도 초과")
        return False
    
    def _trigger_learning_cycle(self, reason: str) -> bool:
        """학습 루프를 트리거합니다."""
        try:
            from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
            learning_loop_manager = get_learning_loop_manager()
            
            # 학습 루프 시작
            learning_loop_manager.start_learning_loop(reason=reason)
            print(f"✅ 학습 루프 트리거 완료: {reason}")
            return True
            
        except Exception as e:
            print(f"❌ 학습 루프 트리거 실패: {e}")
            logger.error(f"학습 루프 트리거 오류: {e}")
            return False
    
    def _verify_learning_state(self) -> Dict[str, Any]:
        """학습 상태를 검증합니다."""
        try:
            from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
            from duri_core.memory.memory_sync import get_memory_sync
            
            learning_loop_manager = get_learning_loop_manager()
            memory_sync = get_memory_sync()
            
            # 상태 확인
            is_active = learning_loop_manager.is_running
            current_cycle_id = learning_loop_manager.current_cycle_id
            last_update = memory_sync.get_last_update_time() if memory_sync else None
            
            print(f"🔍 상태 확인:")
            print(f"  - 학습 루프 활성: {is_active}")
            print(f"  - 현재 사이클 ID: {current_cycle_id}")
            print(f"  - 마지막 업데이트: {last_update}")
            
            # 판단 로직
            if not is_active or current_cycle_id is None:
                cause = self._analyze_failure_cause()
                return {
                    "success": False,
                    "cause": cause,
                    "details": {
                        "is_active": is_active,
                        "current_cycle_id": current_cycle_id,
                        "last_update": last_update
                    }
                }
            else:
                return {
                    "success": True,
                    "cause": None,
                    "details": {
                        "is_active": is_active,
                        "current_cycle_id": current_cycle_id,
                        "last_update": last_update
                    }
                }
                
        except Exception as e:
            print(f"❌ 상태 검증 실패: {e}")
            return {
                "success": False,
                "cause": f"검증 오류: {e}",
                "details": {"error": str(e)}
            }
    
    def _analyze_failure_cause(self) -> str:
        """실패 원인을 분석합니다."""
        try:
            from duri_core.utils.fallback_handler import get_fallback_handler
            fallback_handler = get_fallback_handler()
            
            if fallback_handler:
                cause = fallback_handler.get_last_failure_cause()
                return cause if cause else "알 수 없는 오류"
            else:
                return "Fallback 핸들러 없음"
                
        except Exception as e:
            return f"원인 분석 실패: {e}"
    
    def _auto_fix_and_retry(self, cause: str):
        """자동 수정 및 재시도를 수행합니다."""
        try:
            print(f"🔧 자동 수정 시도: {cause}")
            
            from duri_core.utils.fallback_handler import get_fallback_handler
            fallback_handler = get_fallback_handler()
            
            if fallback_handler:
                # 자동 수정 실행
                fix_result = fallback_handler.auto_fix()
                print(f"🔧 수정 결과: {fix_result}")
                
                # 잠시 대기 후 재시도 준비
                time.sleep(2)
            else:
                print("⚠️ Fallback 핸들러를 찾을 수 없음")
                
        except Exception as e:
            print(f"❌ 자동 수정 실패: {e}")
    
    def safe_learning_trigger(self, reason: str = "자동 학습 검증", max_retries: int = 3) -> bool:
        """
        안전한 학습 트리거 (챗지피티 제안 함수)
        
        Args:
            reason: 학습 이유
            max_retries: 최대 재시도 횟수
            
        Returns:
            bool: 성공 여부
        """
        self.max_retries = max_retries
        return self.trigger_new_learning_cycle_with_verification(reason)
    
    def get_dlfp_status(self) -> Dict[str, Any]:
        """DLFP 상태를 반환합니다."""
        return {
            "protocol_name": "DLFP (DuRi Learning Feedback Protocol)",
            "max_retries": self.max_retries,
            "verification_delay": self.verification_delay,
            "fallback_conditions": self.fallback_conditions,
            "status": "ready"
        }

# 전역 함수로 실행 가능하도록
def safe_learning_trigger(reason: str = "자동 학습 검증", max_retries: int = 3) -> bool:
    """안전한 학습 트리거 (전역 함수)"""
    dlfp = DLFPProtocol()
    return dlfp.safe_learning_trigger(reason, max_retries)

def trigger_new_learning_cycle_with_verification(reason: str = "자동 학습 검증") -> bool:
    """검증이 포함된 학습 루프 트리거 (전역 함수)"""
    dlfp = DLFPProtocol()
    return dlfp.trigger_new_learning_cycle_with_verification(reason)

def get_dlfp_status() -> Dict[str, Any]:
    """DLFP 상태 반환 (전역 함수)"""
    dlfp = DLFPProtocol()
    return dlfp.get_dlfp_status()

if __name__ == "__main__":
    # DLFP 테스트 실행
    import sys
    sys.path.append('.')
    
    print("🧠 === DLFP 프로토콜 테스트 시작 ===")
    
    # DLFP 상태 확인
    status = get_dlfp_status()
    print(f"📋 DLFP 상태: {status}")
    
    # 안전한 학습 트리거 테스트
    print("\n🚀 안전한 학습 트리거 테스트...")
    success = safe_learning_trigger("DLFP 테스트", max_retries=2)
    
    print(f"\n🎯 테스트 결과: {'✅ 성공' if success else '❌ 실패'}")
    print("✅ === DLFP 프로토콜 테스트 완료 ===") 