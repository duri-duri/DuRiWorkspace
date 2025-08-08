"""
DuRi Fallback 처리 시스템

오류 발생 시 시스템이 멈추지 않고 기능 제한 모드로 작동하도록 합니다.
"""

import logging
import traceback
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class FallbackMode(Enum):
    """Fallback 모드"""
    NORMAL = "normal"              # 정상 모드
    LIMITED = "limited"            # 제한 모드
    EMERGENCY = "emergency"        # 비상 모드
    DISABLED = "disabled"          # 비활성화 모드

@dataclass
class FallbackInfo:
    """Fallback 정보"""
    module_name: str
    error_type: str
    error_message: str
    fallback_mode: FallbackMode
    timestamp: datetime
    recovery_attempts: int = 0
    is_recovered: bool = False

class FallbackHandler:
    """DuRi Fallback 처리 시스템"""
    
    def __init__(self):
        """FallbackHandler 초기화"""
        self.fallback_history: List[FallbackInfo] = []
        self.current_mode = FallbackMode.NORMAL
        self.recovery_callbacks: Dict[str, Callable] = {}
        self.limited_mode_handlers: Dict[str, Callable] = {}
        
        logger.info("FallbackHandler 초기화 완료")
    
    def register_recovery_callback(self, module_name: str, callback: Callable):
        """복구 콜백을 등록합니다."""
        self.recovery_callbacks[module_name] = callback
        logger.info(f"복구 콜백 등록: {module_name}")
    
    def register_limited_mode_handler(self, module_name: str, handler: Callable):
        """제한 모드 핸들러를 등록합니다."""
        self.limited_mode_handlers[module_name] = handler
        logger.info(f"제한 모드 핸들러 등록: {module_name}")
    
    def handle_error(self, module_name: str, error: Exception, 
                    fallback_mode: FallbackMode = FallbackMode.LIMITED) -> FallbackInfo:
        """
        오류를 처리하고 fallback 모드로 전환합니다.
        
        Args:
            module_name: 오류가 발생한 모듈 이름
            error: 발생한 오류
            fallback_mode: 전환할 fallback 모드
            
        Returns:
            FallbackInfo: fallback 정보
        """
        try:
            # 오류 정보 수집
            error_type = type(error).__name__
            error_message = str(error)
            
            # Fallback 정보 생성
            fallback_info = FallbackInfo(
                module_name=module_name,
                error_type=error_type,
                error_message=error_message,
                fallback_mode=fallback_mode,
                timestamp=datetime.now()
            )
            
            # Fallback 모드 전환
            self._switch_to_fallback_mode(fallback_mode, module_name)
            
            # 오류 로깅
            logger.warning(f"모듈 {module_name}에서 오류 발생: {error_type} - {error_message}")
            logger.info(f"Fallback 모드로 전환: {fallback_mode.value}")
            
            # 제한 기능 안내
            self._show_limited_functionality_guide(module_name, fallback_mode)
            
            # Fallback 로그 저장
            self._save_fallback_log(fallback_info)
            
            # 히스토리에 추가
            self.fallback_history.append(fallback_info)
            
            return fallback_info
            
        except Exception as e:
            logger.error(f"Fallback 처리 중 오류 발생: {e}")
            return FallbackInfo(
                module_name=module_name,
                error_type="FallbackError",
                error_message=str(e),
                fallback_mode=FallbackMode.EMERGENCY,
                timestamp=datetime.now()
            )
    
    def _switch_to_fallback_mode(self, mode: FallbackMode, module_name: str):
        """Fallback 모드로 전환합니다."""
        self.current_mode = mode
        
        if mode == FallbackMode.LIMITED:
            logger.info(f"제한 모드 활성화: {module_name}")
        elif mode == FallbackMode.EMERGENCY:
            logger.warning(f"비상 모드 활성화: {module_name}")
        elif mode == FallbackMode.DISABLED:
            logger.error(f"모듈 비활성화: {module_name}")
    
    def _show_limited_functionality_guide(self, module_name: str, mode: FallbackMode):
        """제한 기능 안내를 표시합니다."""
        guides = {
            "duri_brain.dream.dream_engine": {
                FallbackMode.LIMITED: "Dream Engine이 제한 모드로 작동합니다. 기본 창의성 기능만 사용 가능합니다.",
                FallbackMode.EMERGENCY: "Dream Engine이 비상 모드로 작동합니다. 창의성 기능이 비활성화되었습니다.",
                FallbackMode.DISABLED: "Dream Engine이 비활성화되었습니다. 창의성 기능을 사용할 수 없습니다."
            },
            "duri_brain.eval.core_eval": {
                FallbackMode.LIMITED: "Core_Eval이 제한 모드로 작동합니다. 기본 평가 기능만 사용 가능합니다.",
                FallbackMode.EMERGENCY: "Core_Eval이 비상 모드로 작동합니다. 고급 평가 기능이 비활성화되었습니다.",
                FallbackMode.DISABLED: "Core_Eval이 비활성화되었습니다. 평가 기능을 사용할 수 없습니다."
            },
            "duri_brain.learning.learning_loop_manager": {
                FallbackMode.LIMITED: "Learning Loop Manager가 제한 모드로 작동합니다. 기본 학습 기능만 사용 가능합니다.",
                FallbackMode.EMERGENCY: "Learning Loop Manager가 비상 모드로 작동합니다. 고급 학습 기능이 비활성화되었습니다.",
                FallbackMode.DISABLED: "Learning Loop Manager가 비활성화되었습니다. 학습 기능을 사용할 수 없습니다."
            },
            "duri_core.philosophy.core_belief": {
                FallbackMode.LIMITED: "CoreBelief가 제한 모드로 작동합니다. 기본 철학 기능만 사용 가능합니다.",
                FallbackMode.EMERGENCY: "CoreBelief가 비상 모드로 작동합니다. 고급 철학 기능이 비활성화되었습니다.",
                FallbackMode.DISABLED: "CoreBelief가 비활성화되었습니다. 철학 기능을 사용할 수 없습니다."
            }
        }
        
        # mode가 Enum인지 확인하고 안전하게 value 접근
        mode_value = mode.value if hasattr(mode, 'value') else str(mode)
        guide = guides.get(module_name, {}).get(mode, f"모듈 {module_name}이 {mode_value} 모드로 작동합니다.")
        print(f"⚠️  {guide}")
        logger.info(f"제한 기능 안내: {guide}")
    
    def attempt_recovery(self, module_name: str) -> bool:
        """모듈 복구를 시도합니다."""
        try:
            if module_name in self.recovery_callbacks:
                logger.info(f"모듈 복구 시도: {module_name}")
                success = self.recovery_callbacks[module_name]()
                
                if success:
                    self.current_mode = FallbackMode.NORMAL
                    logger.info(f"모듈 복구 성공: {module_name}")
                    return True
                else:
                    logger.warning(f"모듈 복구 실패: {module_name}")
                    return False
            else:
                logger.warning(f"복구 콜백이 등록되지 않음: {module_name}")
                return False
                
        except Exception as e:
            logger.error(f"복구 시도 중 오류 발생: {e}")
            return False
    
    def get_limited_functionality(self, module_name: str, *args, **kwargs) -> Any:
        """제한된 기능을 제공합니다."""
        try:
            if module_name in self.limited_mode_handlers:
                return self.limited_mode_handlers[module_name](*args, **kwargs)
            else:
                # 기본 제한 기능
                return self._default_limited_functionality(module_name, *args, **kwargs)
        except Exception as e:
            logger.error(f"제한 기능 제공 중 오류: {e}")
            return None
    
    def _save_fallback_log(self, fallback_info: FallbackInfo):
        """Fallback 로그를 저장합니다."""
        try:
            import json
            from pathlib import Path
            
            # 로그 디렉토리 생성
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # 로그 파일 경로
            log_file = log_dir / "fallback_log.jsonl"
            
            # 로그 엔트리 생성
            log_entry = {
                "timestamp": fallback_info.timestamp.isoformat(),
                "module_name": fallback_info.module_name,
                "error_type": fallback_info.error_type,
                "error_message": fallback_info.error_message,
                "fallback_mode": fallback_info.fallback_mode.value if hasattr(fallback_info.fallback_mode, 'value') else str(fallback_info.fallback_mode),
                "recovery_attempts": fallback_info.recovery_attempts,
                "is_recovered": fallback_info.is_recovered
            }
            
            # JSONL 형식으로 저장
            with open(log_file, 'a', encoding='utf-8') as f:
                json.dump(log_entry, f, ensure_ascii=False)
                f.write('\n')
            
            logger.debug(f"Fallback 로그 저장 완료: {fallback_info.module_name}")
            
        except Exception as e:
            logger.error(f"Fallback 로그 저장 실패: {e}")
    
    def _default_limited_functionality(self, module_name: str, *args, **kwargs) -> Any:
        """기본 제한 기능을 제공합니다."""
        if "dream" in module_name:
            return {"status": "limited", "message": "Dream 기능이 제한 모드로 작동합니다."}
        elif "eval" in module_name:
            return {"status": "limited", "message": "평가 기능이 제한 모드로 작동합니다."}
        elif "learning" in module_name:
            return {"status": "limited", "message": "학습 기능이 제한 모드로 작동합니다."}
        else:
            return {"status": "limited", "message": f"모듈 {module_name}이 제한 모드로 작동합니다."}
    
    def get_fallback_statistics(self) -> Dict[str, Any]:
        """Fallback 통계를 반환합니다."""
        total_fallbacks = len(self.fallback_history)
        recent_fallbacks = [f for f in self.fallback_history 
                          if (datetime.now() - f.timestamp).hours < 24]
        
        mode_counts = {}
        for fallback in self.fallback_history:
            # fallback_mode가 Enum인지 확인하고 안전하게 value 접근
            mode = fallback.fallback_mode.value if hasattr(fallback.fallback_mode, 'value') else str(fallback.fallback_mode)
            mode_counts[mode] = mode_counts.get(mode, 0) + 1
        
        return {
            "total_fallbacks": total_fallbacks,
            "recent_fallbacks_24h": len(recent_fallbacks),
            "current_mode": self.current_mode.value if hasattr(self.current_mode, 'value') else str(self.current_mode),
            "mode_distribution": mode_counts,
            "recovery_attempts": sum(f.recovery_attempts for f in self.fallback_history),
            "successful_recoveries": len([f for f in self.fallback_history if f.is_recovered])
        }
    
    def is_in_fallback_mode(self) -> bool:
        """현재 fallback 모드인지 확인합니다."""
        return self.current_mode != FallbackMode.NORMAL

# 싱글톤 인스턴스
_fallback_handler = None

def get_fallback_handler() -> FallbackHandler:
    """FallbackHandler 싱글톤 인스턴스 반환"""
    global _fallback_handler
    if _fallback_handler is None:
        _fallback_handler = FallbackHandler()
    return _fallback_handler 