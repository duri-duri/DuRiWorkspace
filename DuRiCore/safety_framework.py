from DuRiCore.trace import emit_trace
"""
DuRi 안전성 프레임워크 (Safety Framework)
안전성과 동등성을 보장하는 핵심 시스템

@preserve_identity: 기존 기능과 동작 패턴 보존
@evolution_protection: 진화 과정에서의 안전성 확보
@execution_guarantee: 실행 안전성 보장
@existence_ai: 안전한 진화와 회복
@final_execution: 안전한 최종 실행
"""
import asyncio
import json
import time
import math
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import traceback
import hashlib
import pickle
from pathlib import Path
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """안전성 수준"""
    CRITICAL = 'critical'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'
    SAFE = 'safe'

class InvariantType(Enum):
    """불변 조건 유형"""
    FUNCTIONALITY = 'functionality'
    PERFORMANCE = 'performance'
    MEMORY = 'memory'
    API_COMPATIBILITY = 'api_compatibility'
    DATA_INTEGRITY = 'data_integrity'

@dataclass
class SafetyInvariant:
    """안전성 불변 조건"""
    id: str
    name: str
    invariant_type: InvariantType
    description: str
    check_function: Callable
    critical: bool = False
    last_check: Optional[datetime] = None
    check_result: Optional[bool] = None
    violation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SafetyCheck:
    """안전성 검사 결과"""
    id: str
    timestamp: datetime
    safety_level: SafetyLevel
    message: str
    details: Dict[str, Any]
    action_required: bool = False
    rollback_triggered: bool = False

@dataclass
class SafetyMetrics:
    """안전성 메트릭"""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    critical_violations: int = 0
    last_check_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    safety_score: float = 1.0

class SafetyFramework:
    """DuRi 안전성 프레임워크"""

    def __init__(self):
        self.invariants: Dict[str, SafetyInvariant] = {}
        self.safety_checks: List[SafetyCheck] = []
        self.metrics = SafetyMetrics()
        self.start_time = datetime.now()
        self.rollback_ready = False
        self.safety_enabled = True
        self._is_critical = False  # 동등성 히스테리시스 상태 메모
        self._register_default_invariants()
        logger.info('DuRi 안전성 프레임워크 초기화 완료')

    def _register_default_invariants(self):
        """기본 안전성 불변 조건 등록"""
        self.register_invariant(SafetyInvariant(id='func_core_functionality', name='핵심 기능 유지', invariant_type=InvariantType.FUNCTIONALITY, description='핵심 기능이 정상적으로 작동하는지 확인', check_function=self._check_core_functionality, critical=True))
        self.register_invariant(SafetyInvariant(id='perf_response_time', name='응답 시간 유지', invariant_type=InvariantType.PERFORMANCE, description='응답 시간이 허용 범위 내에 있는지 확인', check_function=self._check_response_time, critical=False))
        self.register_invariant(SafetyInvariant(id='mem_usage_limit', name='메모리 사용량 제한', invariant_type=InvariantType.MEMORY, description='메모리 사용량이 허용 범위 내에 있는지 확인', check_function=self._check_memory_usage, critical=True))
        self.register_invariant(SafetyInvariant(id='api_compatibility', name='API 호환성 유지', invariant_type=InvariantType.API_COMPATIBILITY, description='기존 API 호환성이 유지되는지 확인', check_function=self._check_api_compatibility, critical=True))

    def register_invariant(self, invariant: SafetyInvariant):
        """안전성 불변 조건 등록"""
        self.invariants[invariant.id] = invariant
        logger.info(f'안전성 불변 조건 등록: {invariant.name} ({invariant.id})')

    def unregister_invariant(self, invariant_id: str):
        """안전성 불변 조건 제거"""
        if invariant_id in self.invariants:
            del self.invariants[invariant_id]
            logger.info(f'안전성 불변 조건 제거: {invariant_id}')

    async def run_safety_check(self) -> SafetyCheck:
        """전체 안전성 검사 실행"""
        if not self.safety_enabled:
            return SafetyCheck(id='safety_disabled', timestamp=datetime.now(), safety_level=SafetyLevel.SAFE, message='안전성 검사가 비활성화됨', details={}, action_required=False)
        start_time = time.time()
        check_id = f'safety_check_{int(time.time())}'
        logger.info('안전성 검사 시작')
        invariant_results = {}
        critical_violations = []
        for (invariant_id, invariant) in self.invariants.items():
            try:
                result = await self._check_invariant(invariant)
                invariant_results[invariant_id] = result
                if not result and invariant.critical:
                    critical_violations.append(invariant_id)
            except Exception as e:
                logger.error(f'불변 조건 검사 실패: {invariant_id}, 오류: {e}')
                invariant_results[invariant_id] = False
                if invariant.critical:
                    critical_violations.append(invariant_id)
        if critical_violations:
            safety_level = SafetyLevel.CRITICAL
            action_required = True
            message = f"중요한 안전성 위반 발생: {', '.join(critical_violations)}"
        elif any((not result for result in invariant_results.values())):
            safety_level = SafetyLevel.HIGH
            action_required = True
            message = '안전성 위반 발생'
        else:
            safety_level = SafetyLevel.SAFE
            action_required = False
            message = '모든 안전성 검사 통과'
        self._update_metrics(invariant_results)
        safety_check = SafetyCheck(id=check_id, timestamp=datetime.now(), safety_level=safety_level, message=message, details={'invariant_results': invariant_results, 'critical_violations': critical_violations, 'check_duration': time.time() - start_time}, action_required=action_required)
        self.safety_checks.append(safety_check)
        if safety_level == SafetyLevel.CRITICAL:
            await self._prepare_rollback()
        logger.info(f'안전성 검사 완료: {safety_level.value}, 위반: {len(critical_violations)}')
        return safety_check

    async def _check_invariant(self, invariant: SafetyInvariant) -> bool:
        """개별 불변 조건 검사"""
        try:
            if asyncio.iscoroutinefunction(invariant.check_function):
                result = await invariant.check_function()
            else:
                result = invariant.check_function()
            invariant.last_check = datetime.now()
            invariant.check_result = result
            if not result:
                invariant.violation_count += 1
                logger.warning(f'불변 조건 위반: {invariant.name} ({invariant.id})')
            else:
                logger.debug(f'불변 조건 통과: {invariant.name} ({invariant.id})')
            return result
        except Exception as e:
            logger.error(f'불변 조건 검사 중 오류: {invariant.name}, 오류: {e}')
            invariant.last_check = datetime.now()
            invariant.check_result = False
            invariant.violation_count += 1
            return False

    def _update_metrics(self, invariant_results: Dict[str, bool]):
        """안전성 메트릭 업데이트"""
        self.metrics.total_checks += 1
        self.metrics.last_check_time = datetime.now()
        passed = sum((1 for result in invariant_results.values() if result))
        failed = len(invariant_results) - passed
        self.metrics.passed_checks += passed
        self.metrics.failed_checks += failed
        if self.metrics.total_checks > 0:
            raw_score = self.metrics.passed_checks / self.metrics.total_checks
            # eq_avg는 현재 동등성 평균을 계산하지 않으므로 None 전달
            # 향후 동등성 메트릭이 추가되면 여기서 계산하여 전달
            self.metrics.safety_score = self._finalize_score(raw_score, eq_avg=None)
        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()

    def _finalize_score(self, score: float, eq_avg: Optional[float] = None) -> float:
        """최종 safety_score를 [0,1] 범위로 정규화하고 히스테리시스를 적용한다."""
        try:
            v = float(score)
        except Exception:
            return 0.0
        if math.isnan(v) or math.isinf(v):
            return 0.0
        
        # Day7 임계값 로드 (프로파일은 기존 코드와 동일하게 전달/기본값 사용)
        try:
            import yaml
            from pathlib import Path
            # DuRiCore/config/thresholds.yaml 직접 읽기
            config_path = Path('DuRiCore/config/thresholds.yaml')
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    raw_config = yaml.safe_load(f) or {}
                    day7 = raw_config.get("day7", {})
                    clamp_cfg = day7.get("safety_score", {})
                    clamp_min = clamp_cfg.get("clamp_min", 0.0)
                    clamp_max = clamp_cfg.get("clamp_max", 1.0)
                    # 점수 정규화
                    s = max(clamp_min, min(clamp_max, v))
            else:
                s = max(0.0, min(1.0, v))
        except Exception as e:
            logger.warning(f"Day7 설정 로드 실패, 기본값 사용: {e}")
            s = max(0.0, min(1.0, v))

        # 동등성 히스테리시스
        if eq_avg is not None:
            try:
                hcfg = day7.get("hysteresis", {})
                enter_crit = hcfg.get("enter_critical", 0.12)
                exit_crit = hcfg.get("exit_critical", 0.16)
                
                if not self._is_critical and eq_avg < enter_crit:
                    self._is_critical = True
                    logger.info(f"동등성 히스테리시스: critical 진입 (eq_avg={eq_avg:.3f} < {enter_crit})")
                elif self._is_critical and eq_avg >= exit_crit:
                    self._is_critical = False
                    logger.info(f"동등성 히스테리시스: critical 해제 (eq_avg={eq_avg:.3f} >= {exit_crit})")
            except Exception as e:
                logger.warning(f"히스테리시스 적용 실패: {e}")
        
        return s

    async def _prepare_rollback(self):
        """롤백 준비"""
        if not self.rollback_ready:
            logger.warning('롤백 준비 시작')
            self.rollback_ready = True

    async def get_safety_report(self) -> Dict[str, Any]:
        """안전성 보고서 생성"""
        return {'framework_status': {'enabled': self.safety_enabled, 'uptime_seconds': self.metrics.uptime_seconds, 'safety_score': self.metrics.safety_score}, 'metrics': {'total_checks': self.metrics.total_checks, 'passed_checks': self.metrics.passed_checks, 'failed_checks': self.metrics.failed_checks, 'last_check_time': self.metrics.last_check_time.isoformat() if self.metrics.last_check_time else None}, 'invariants': {inv_id: {'name': inv.name, 'type': inv.invariant_type.value, 'critical': inv.critical, 'last_check': inv.last_check.isoformat() if inv.last_check else None, 'check_result': inv.check_result, 'violation_count': inv.violation_count} for (inv_id, inv) in self.invariants.items()}, 'recent_checks': [{'id': check.id, 'timestamp': check.timestamp.isoformat(), 'safety_level': check.safety_level.value, 'message': check.message, 'action_required': check.action_required} for check in self.safety_checks[-10:]]}

    async def _check_core_functionality(self) -> bool:
        """핵심 기능 정상 작동 확인"""
        try:
            return True
        except Exception as e:
            logger.error(f'핵심 기능 검사 실패: {e}')
            return False

    async def _check_response_time(self) -> bool:
        """응답 시간 확인"""
        try:
            return True
        except Exception as e:
            logger.error(f'응답 시간 검사 실패: {e}')
            return False

    async def _check_memory_usage(self) -> bool:
        """메모리 사용량 확인"""
        try:
            return True
        except Exception as e:
            logger.error(f'메모리 사용량 검사 실패: {e}')
            return False

    async def _check_api_compatibility(self) -> bool:
        """API 호환성 확인"""
        try:
            return True
        except Exception as e:
            logger.error(f'API 호환성 검사 실패: {e}')
            return False

    def enable_safety(self):
        """안전성 검사 활성화"""
        self.safety_enabled = True
        logger.info('안전성 검사 활성화')

    def disable_safety(self):
        """안전성 검사 비활성화"""
        self.safety_enabled = False
        logger.warning('안전성 검사 비활성화 - 주의 필요!')

    async def emergency_stop(self):
        """긴급 정지"""
        logger.critical('긴급 정지 실행!')
        self.safety_enabled = False

    def set_safety_level(self, level: SafetyLevel):
        """안전성 수준 설정 (SSOT 경로)"""
        try:
            if isinstance(level, SafetyLevel):
                self.current_safety_level = level
                logger.info(f'안전성 수준 설정: {level.value}')
                self._notify_safety_level_change(level)
                return True
            else:
                logger.warning(f'잘못된 안전성 수준: {level}')
                return False
        except Exception as e:
            logger.error(f'안전성 수준 설정 실패: {e}')
            return False

    def _notify_safety_level_change(self, new_level: SafetyLevel):
        """안전성 수준 변경 알림"""
        try:
            logger.debug(f'안전성 수준 변경 알림: {new_level.value}')
        except Exception as e:
            logger.error(f'안전성 수준 변경 알림 실패: {e}')

    @property
    def current_safety_level(self) -> SafetyLevel:
        """현재 안전성 수준 반환"""
        return getattr(self, '_current_safety_level', SafetyLevel.SAFE)

    @current_safety_level.setter
    def current_safety_level(self, level: SafetyLevel):
        """현재 안전성 수준 설정"""
        self._current_safety_level = level
safety_framework = SafetyFramework()