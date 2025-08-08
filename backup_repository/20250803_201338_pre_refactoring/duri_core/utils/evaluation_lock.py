"""
DuRi 평가 동시성 제어 시스템

평가 루틴 충돌 방지를 위한 동시성 제어와 상태 관리를 담당합니다.
"""

import logging
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class EvaluationStatus(Enum):
    """평가 상태"""
    IDLE = "idle"              # 대기 중
    EVALUATING = "evaluating"  # 평가 중
    ERROR = "error"            # 오류 상태
    LOCKED = "locked"          # 잠금 상태

@dataclass
class EvaluationState:
    """평가 상태 관리"""
    is_evaluating: bool = False
    current_evaluation_id: Optional[str] = None
    evaluation_start_time: Optional[datetime] = None
    last_save_time: Optional[datetime] = None
    error_count: int = 0
    last_error_time: Optional[datetime] = None
    
    def start_evaluation(self, evaluation_id: str):
        """평가 시작"""
        self.is_evaluating = True
        self.current_evaluation_id = evaluation_id
        self.evaluation_start_time = datetime.now()
        self.last_save_time = datetime.now()
    
    def end_evaluation(self):
        """평가 종료"""
        self.is_evaluating = False
        self.current_evaluation_id = None
        self.evaluation_start_time = None
    
    def record_error(self):
        """오류 기록"""
        self.error_count += 1
        self.last_error_time = datetime.now()
        self.is_evaluating = False
    
    def reset_errors(self):
        """오류 카운트 리셋"""
        self.error_count = 0
        self.last_error_time = None

class EvaluationLock:
    """평가 동시성 제어"""
    
    def __init__(self, timeout_seconds: int = 300):  # 5분 타임아웃
        """EvaluationLock 초기화"""
        self._lock = threading.RLock()
        self._evaluation_in_progress = False
        self._current_evaluation_id = None
        self._evaluation_start_time = None
        self._timeout_seconds = timeout_seconds
        
        # 데드락 방지를 위한 타임아웃 관리
        self._last_cleanup = datetime.now()
        self._cleanup_interval = timedelta(minutes=5)
        
        logger.info("EvaluationLock 초기화 완료")
    
    @contextmanager
    def evaluation_context(self, evaluation_id: str):
        """평가 컨텍스트 관리"""
        try:
            with self._lock:
                if self._evaluation_in_progress:
                    raise RuntimeError(f"평가가 이미 진행 중입니다: {self._current_evaluation_id}")
                
                # 타임아웃된 평가 정리
                self._cleanup_timeout_evaluations()
                
                self._evaluation_in_progress = True
                self._current_evaluation_id = evaluation_id
                self._evaluation_start_time = datetime.now()
                
                logger.debug(f"평가 시작: {evaluation_id}")
            
            yield
            
        except Exception as e:
            logger.error(f"평가 중 오류 발생: {e}")
            raise
        finally:
            with self._lock:
                self._evaluation_in_progress = False
                self._current_evaluation_id = None
                self._evaluation_start_time = None
                logger.debug(f"평가 종료: {evaluation_id}")
    
    def _cleanup_timeout_evaluations(self):
        """타임아웃된 평가를 정리합니다."""
        current_time = datetime.now()
        
        # 정리 주기 확인
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        # 타임아웃 확인
        if (self._evaluation_in_progress and self._evaluation_start_time and
            current_time - self._evaluation_start_time > timedelta(seconds=self._timeout_seconds)):
            
            logger.warning(f"평가 타임아웃 강제 종료: {self._current_evaluation_id}")
            self._evaluation_in_progress = False
            self._current_evaluation_id = None
            self._evaluation_start_time = None
        
        self._last_cleanup = current_time
    
    def is_evaluation_in_progress(self) -> bool:
        """평가 진행 중 여부를 확인합니다."""
        with self._lock:
            return self._evaluation_in_progress
    
    def get_current_evaluation_info(self) -> Optional[Dict[str, Any]]:
        """현재 평가 정보를 반환합니다."""
        with self._lock:
            if not self._evaluation_in_progress:
                return None
            
            return {
                'evaluation_id': self._current_evaluation_id,
                'start_time': self._evaluation_start_time,
                'duration_seconds': (datetime.now() - self._evaluation_start_time).total_seconds() if self._evaluation_start_time else 0
            }

class EvaluationStateManager:
    """평가 상태 관리자"""
    
    def __init__(self):
        """EvaluationStateManager 초기화"""
        self._lock = threading.RLock()
        self._states: Dict[str, EvaluationState] = {}
        
        logger.info("EvaluationStateManager 초기화 완료")
    
    def get_state(self, evaluation_type: str) -> EvaluationState:
        """평가 상태를 반환합니다."""
        with self._lock:
            if evaluation_type not in self._states:
                self._states[evaluation_type] = EvaluationState()
            return self._states[evaluation_type]
    
    def start_evaluation(self, evaluation_type: str, evaluation_id: str):
        """평가를 시작합니다."""
        with self._lock:
            state = self.get_state(evaluation_type)
            state.start_evaluation(evaluation_id)
            logger.debug(f"평가 시작: {evaluation_type} - {evaluation_id}")
    
    def end_evaluation(self, evaluation_type: str):
        """평가를 종료합니다."""
        with self._lock:
            state = self.get_state(evaluation_type)
            state.end_evaluation()
            logger.debug(f"평가 종료: {evaluation_type}")
    
    def record_error(self, evaluation_type: str):
        """오류를 기록합니다."""
        with self._lock:
            state = self.get_state(evaluation_type)
            state.record_error()
            logger.error(f"평가 오류 기록: {evaluation_type}")
    
    def get_all_states(self) -> Dict[str, EvaluationState]:
        """모든 평가 상태를 반환합니다."""
        with self._lock:
            return self._states.copy()
    
    def cleanup_old_states(self, max_age_hours: int = 24):
        """오래된 상태를 정리합니다."""
        with self._lock:
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            for eval_type, state in list(self._states.items()):
                if (state.evaluation_start_time and 
                    state.evaluation_start_time < cutoff_time and 
                    not state.is_evaluating):
                    del self._states[eval_type]
                    logger.debug(f"오래된 상태 정리: {eval_type}")

# 싱글톤 인스턴스들
_evaluation_lock = None
_evaluation_state_manager = None

def get_evaluation_lock() -> EvaluationLock:
    """EvaluationLock 싱글톤 인스턴스 반환"""
    global _evaluation_lock
    if _evaluation_lock is None:
        _evaluation_lock = EvaluationLock()
    return _evaluation_lock

def get_evaluation_state_manager() -> EvaluationStateManager:
    """EvaluationStateManager 싱글톤 인스턴스 반환"""
    global _evaluation_state_manager
    if _evaluation_state_manager is None:
        _evaluation_state_manager = EvaluationStateManager()
    return _evaluation_state_manager 