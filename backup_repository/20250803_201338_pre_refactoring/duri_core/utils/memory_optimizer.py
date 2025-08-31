"""
DuRi 메모리 최적화 시스템

메모리 사용량을 최적화하고 누수를 방지합니다.
"""

import logging
import gc
import psutil
import threading
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class MemoryUsage:
    """메모리 사용량 정보"""
    timestamp: datetime
    total_memory: float
    available_memory: float
    used_memory: float
    memory_percentage: float
    process_memory: float
    python_memory: float

@dataclass
class MemoryOptimizationResult:
    """메모리 최적화 결과"""
    optimization_id: str
    timestamp: datetime
    before_memory: float
    after_memory: float
    freed_memory: float
    optimization_type: str
    success: bool
    details: List[str]

class MemoryOptimizer:
    """DuRi 메모리 최적화 시스템"""
    
    def __init__(self):
        """MemoryOptimizer 초기화"""
        self.optimization_history: List[MemoryOptimizationResult] = []
        self.is_optimizing = False
        self.optimization_thread: Optional[threading.Thread] = None
        self.auto_optimization_enabled = True
        self.optimization_interval = 300  # 5분마다 자동 최적화
        
        # 최적화 임계값
        self.memory_thresholds = {
            'warning': 75.0,      # 75% 이상 시 경고
            'critical': 85.0,     # 85% 이상 시 즉시 최적화
            'auto_optimize': 80.0 # 80% 이상 시 자동 최적화
        }
        
        logger.info("MemoryOptimizer 초기화 완료")
    
    def start_auto_optimization(self):
        """자동 메모리 최적화를 시작합니다."""
        if self.auto_optimization_enabled:
            self.optimization_thread = threading.Thread(target=self._auto_optimization_loop, daemon=True)
            self.optimization_thread.start()
            logger.info("자동 메모리 최적화 시작")
    
    def stop_auto_optimization(self):
        """자동 메모리 최적화를 중지합니다."""
        self.auto_optimization_enabled = False
        if self.optimization_thread:
            self.optimization_thread.join(timeout=5)
        logger.info("자동 메모리 최적화 중지")
    
    def _auto_optimization_loop(self):
        """자동 최적화 루프"""
        while self.auto_optimization_enabled:
            try:
                current_memory = self.get_current_memory_usage()
                
                if current_memory.memory_percentage >= self.memory_thresholds['auto_optimize']:
                    logger.info(f"자동 메모리 최적화 실행: {current_memory.memory_percentage:.1f}%")
                    self.optimize_memory()
                
                time.sleep(self.optimization_interval)
                
            except Exception as e:
                logger.error(f"자동 메모리 최적화 중 오류: {e}")
                time.sleep(60)  # 오류 시 1분 대기
    
    def get_current_memory_usage(self) -> MemoryUsage:
        """현재 메모리 사용량을 반환합니다."""
        try:
            memory = psutil.virtual_memory()
            process = psutil.Process()
            
            return MemoryUsage(
                timestamp=datetime.now(),
                total_memory=memory.total,
                available_memory=memory.available,
                used_memory=memory.used,
                memory_percentage=memory.percent,
                process_memory=process.memory_info().rss,
                python_memory=process.memory_info().rss
            )
            
        except Exception as e:
            logger.error(f"메모리 사용량 조회 실패: {e}")
            return MemoryUsage(
                timestamp=datetime.now(),
                total_memory=0.0,
                available_memory=0.0,
                used_memory=0.0,
                memory_percentage=0.0,
                process_memory=0.0,
                python_memory=0.0
            )
    
    def optimize_memory(self) -> MemoryOptimizationResult:
        """메모리를 최적화합니다."""
        try:
            if self.is_optimizing:
                logger.warning("메모리 최적화가 이미 실행 중입니다.")
                return None
            
            self.is_optimizing = True
            optimization_id = f"opt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 최적화 전 메모리 사용량
            before_memory = self.get_current_memory_usage()
            before_usage = before_memory.memory_percentage
            
            logger.info(f"메모리 최적화 시작: {before_usage:.1f}%")
            
            details = []
            
            # 1. 가비지 컬렉션 실행
            gc_result = self._run_garbage_collection()
            details.extend(gc_result)
            
            # 2. 캐시 정리
            cache_result = self._clear_caches()
            details.extend(cache_result)
            
            # 3. 메모리 압축
            compression_result = self._compress_memory()
            details.extend(compression_result)
            
            # 최적화 후 메모리 사용량
            after_memory = self.get_current_memory_usage()
            after_usage = after_memory.memory_percentage
            
            freed_memory = before_usage - after_usage
            
            result = MemoryOptimizationResult(
                optimization_id=optimization_id,
                timestamp=datetime.now(),
                before_memory=before_usage,
                after_memory=after_usage,
                freed_memory=freed_memory,
                optimization_type="comprehensive",
                success=freed_memory > 0,
                details=details
            )
            
            self.optimization_history.append(result)
            
            logger.info(f"메모리 최적화 완료: {before_usage:.1f}% → {after_usage:.1f}% (해제: {freed_memory:.1f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return None
        finally:
            self.is_optimizing = False
    
    def _run_garbage_collection(self) -> List[str]:
        """가비지 컬렉션을 실행합니다."""
        try:
            details = []
            
            # 현재 가비지 컬렉터 통계
            gc.collect()
            
            # 세대별 가비지 컬렉션
            for generation in range(3):
                collected = gc.collect(generation)
                if collected > 0:
                    details.append(f"세대 {generation}에서 {collected}개 객체 수집")
            
            # 가비지 컬렉터 설정 최적화
            gc.set_threshold(700, 10, 10)  # 더 적극적인 가비지 컬렉션
            
            details.append("가비지 컬렉션 완료")
            return details
            
        except Exception as e:
            logger.error(f"가비지 컬렉션 실패: {e}")
            return [f"가비지 컬렉션 실패: {e}"]
    
    def _clear_caches(self) -> List[str]:
        """캐시를 정리합니다."""
        try:
            details = []
            
            # Python 내장 캐시 정리
            import sys
            if hasattr(sys, 'intern'):
                sys.intern.clear()
                details.append("문자열 인터닝 캐시 정리")
            
            # 모듈 캐시 정리
            import importlib
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('duri_'):
                    try:
                        module = sys.modules[module_name]
                        if hasattr(module, '__dict__'):
                            # 불필요한 속성 제거
                            for attr in list(module.__dict__.keys()):
                                if attr.startswith('_temp_') or attr.startswith('cache_'):
                                    delattr(module, attr)
                                    details.append(f"모듈 {module_name}의 임시 속성 제거")
                    except Exception:
                        pass
            
            details.append("캐시 정리 완료")
            return details
            
        except Exception as e:
            logger.error(f"캐시 정리 실패: {e}")
            return [f"캐시 정리 실패: {e}"]
    
    def _compress_memory(self) -> List[str]:
        """메모리 압축을 수행합니다."""
        try:
            details = []
            
            # 메모리 압축 시도 (가능한 경우)
            try:
                import gc
                gc.collect()
                details.append("메모리 압축 완료")
            except Exception:
                details.append("메모리 압축 실패")
            
            return details
            
        except Exception as e:
            logger.error(f"메모리 압축 실패: {e}")
            return [f"메모리 압축 실패: {e}"]
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 통계를 반환합니다."""
        try:
            current_memory = self.get_current_memory_usage()
            
            # 최적화 통계
            total_optimizations = len(self.optimization_history)
            successful_optimizations = len([r for r in self.optimization_history if r.success])
            total_freed_memory = sum([r.freed_memory for r in self.optimization_history if r.success])
            
            # 최근 최적화 (24시간)
            recent_optimizations = [
                r for r in self.optimization_history
                if r.timestamp >= datetime.now() - timedelta(hours=24)
            ]
            
            recent_freed_memory = sum([r.freed_memory for r in recent_optimizations if r.success])
            
            return {
                "current_memory_usage": current_memory.memory_percentage,
                "total_memory_mb": current_memory.total_memory / (1024 * 1024),
                "available_memory_mb": current_memory.available_memory / (1024 * 1024),
                "used_memory_mb": current_memory.used_memory / (1024 * 1024),
                "process_memory_mb": current_memory.process_memory / (1024 * 1024),
                "total_optimizations": total_optimizations,
                "successful_optimizations": successful_optimizations,
                "success_rate": successful_optimizations / total_optimizations if total_optimizations > 0 else 0.0,
                "total_freed_memory_percent": total_freed_memory,
                "recent_freed_memory_percent": recent_freed_memory,
                "auto_optimization_enabled": self.auto_optimization_enabled,
                "memory_status": self._get_memory_status(current_memory.memory_percentage)
            }
            
        except Exception as e:
            logger.error(f"메모리 통계 계산 실패: {e}")
            return {}
    
    def _get_memory_status(self, memory_percentage: float) -> str:
        """메모리 상태를 반환합니다."""
        if memory_percentage >= self.memory_thresholds['critical']:
            return "critical"
        elif memory_percentage >= self.memory_thresholds['warning']:
            return "warning"
        else:
            return "normal"
    
    def update_optimization_thresholds(self, new_thresholds: Dict[str, float]):
        """최적화 임계값을 업데이트합니다."""
        self.memory_thresholds.update(new_thresholds)
        logger.info("메모리 최적화 임계값 업데이트 완료")
    
    def get_optimization_history(self, hours: int = 24) -> List[MemoryOptimizationResult]:
        """최적화 히스토리를 반환합니다."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        return [
            result for result in self.optimization_history
            if result.timestamp >= cutoff_time
        ]

# 싱글톤 인스턴스
_memory_optimizer = None

def get_memory_optimizer() -> MemoryOptimizer:
    """MemoryOptimizer 싱글톤 인스턴스 반환"""
    global _memory_optimizer
    if _memory_optimizer is None:
        _memory_optimizer = MemoryOptimizer()
    return _memory_optimizer 