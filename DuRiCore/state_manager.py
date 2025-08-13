from DuRiCore.trace import emit_trace
"""
DuRi 상태 매니저 (State Manager)
시스템의 전역 상태를 단일 소스로 관리하는 시스템

@preserve_identity: 기존 상태 관리 패턴 보존
@evolution_protection: 진화 과정에서의 상태 일관성 확보
@execution_guarantee: 상태 기반 실행 보장
@existence_ai: 안정적인 상태 관리로 진화와 회복
@final_execution: 상태가 보장된 최종 실행
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
from pathlib import Path
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SystemState(Enum):
    """시스템 상태"""
    INITIALIZING = 'initializing'
    READY = 'ready'
    RUNNING = 'running'
    WARNING = 'warning'
    ERROR = 'error'
    EMERGENCY_STOP = 'emergency_stop'
    SAFE_MODE = 'safe_mode'

class WorkloadLevel(Enum):
    """작업량 수준 (SSOT 정의)"""
    IDLE = 'idle'
    NORMAL = 'normal'
    HIGH = 'high'
    SATURATED = 'saturated'

@dataclass
class SystemMetrics:
    """시스템 메트릭 (SSOT 정의) - T3: 타입 고정"""
    workload_level: WorkloadLevel = WorkloadLevel.IDLE
    current_wip: int = 0
    safety_score: float = 1.0
    health_status: str = 'healthy'
    last_update: datetime = field(default_factory=datetime.now)

@dataclass
class StateTransition:
    """상태 전환"""
    from_state: SystemState
    to_state: SystemState
    timestamp: datetime
    reason: str
    metadata: Dict[str, Any] = field(default_factory=dict)

class StateManager:
    """DuRi 상태 매니저 (SSOT)"""

    def __init__(self):
        self.current_state = SystemState.INITIALIZING
        self.metrics = SystemMetrics()
        self.state_history: List[StateTransition] = []
        self.state_listeners: Dict[str, List[Callable]] = {}
        self.start_time = datetime.now()
        self.init_defaults()
        self._register_state_events()
        logger.info('DuRi 상태 매니저 초기화 완료')

    def init_defaults(self):
        """T8: 필수 메트릭 기본값 초기화"""
        try:
            self.metrics.current_wip = 0
            self.metrics.workload_level = WorkloadLevel.IDLE
            self.metrics.safety_score = 1.0
            self.metrics.health_status = 'healthy'
            self.metrics.last_update = datetime.now()
            self._equivalence_metrics = {'overall_equivalence_score': None, 'n_samples': 0, 'last_validation': None, 'validation_history': [], 'threshold': 0.8}
            logger.info('T8: 필수 메트릭 기본값 초기화 완료')
        except Exception as e:
            logger.error(f'T8: 메트릭 기본값 초기화 실패: {e}')
            self.metrics.current_wip = 0
            self.metrics.workload_level = WorkloadLevel.IDLE
            self.metrics.safety_score = 1.0

    def _register_state_events(self):
        """상태 변경 이벤트 등록"""
        self.state_listeners = {'state_change': [], 'metrics_update': [], 'emergency_stop': [], 'safe_mode_enter': [], 'safe_mode_exit': []}

    def add_state_listener(self, event_type: str, callback: Callable):
        """상태 변경 리스너 추가"""
        if event_type in self.state_listeners:
            self.state_listeners[event_type].append(callback)
            logger.debug(f'상태 리스너 추가: {event_type} -> {callback.__name__}')

    def remove_state_listener(self, event_type: str, callback: Callable):
        """상태 변경 리스너 제거"""
        if event_type in self.state_listeners:
            if callback in self.state_listeners[event_type]:
                self.state_listeners[event_type].remove(callback)
                logger.debug(f'상태 리스너 제거: {event_type} -> {callback.__name__}')

    def _notify_listeners(self, event_type: str, data: Any=None):
        """리스너들에게 이벤트 알림"""
        if event_type in self.state_listeners:
            for callback in self.state_listeners[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        asyncio.create_task(callback(data))
                    else:
                        callback(data)
                except Exception as e:
                    logger.error(f'상태 리스너 콜백 실행 실패: {e}')

    async def change_state(self, new_state: SystemState, reason: str='', metadata: Dict[str, Any]=None):
        """시스템 상태 변경"""
        if metadata is None:
            metadata = {}
        old_state = self.current_state
        self.current_state = new_state
        transition = StateTransition(from_state=old_state, to_state=new_state, timestamp=datetime.now(), reason=reason, metadata=metadata)
        self.state_history.append(transition)
        self._notify_listeners('state_change', {'old_state': old_state.value, 'new_state': new_state.value, 'reason': reason, 'metadata': metadata})
        logger.info(f'시스템 상태 변경: {old_state.value} → {new_state.value}, 이유: {reason}')
        if new_state == SystemState.EMERGENCY_STOP:
            self._notify_listeners('emergency_stop', transition)
        elif new_state == SystemState.SAFE_MODE:
            self._notify_listeners('safe_mode_enter', transition)
        elif old_state == SystemState.SAFE_MODE and new_state != SystemState.SAFE_MODE:
            self._notify_listeners('safe_mode_exit', transition)

    async def update_metrics(self, **kwargs):
        """메트릭 업데이트 (SSOT) - T3: 타입 검증 + KeyError 방지 + HF-3: async 일원화 + T8: read-before-validate 가드"""
        update_time = datetime.now()
        try:
            if not hasattr(self.metrics, 'current_wip') or self.metrics.current_wip is None:
                logger.warning('⚠️ T8: update_metrics 전 current_wip 누락 감지, 기본값 0으로 보정')
                self.metrics.current_wip = 0
            if not hasattr(self.metrics, 'workload_level') or self.metrics.workload_level is None:
                logger.warning('⚠️ T8: update_metrics 전 workload_level 누락 감지, 기본값 IDLE로 보정')
                self.metrics.workload_level = WorkloadLevel.IDLE
            if not hasattr(self.metrics, 'safety_score') or self.metrics.safety_score is None:
                logger.warning('⚠️ T8: update_metrics 전 safety_score 누락 감지, 기본값 1.0으로 보정')
                self.metrics.safety_score = 1.0
        except Exception as e:
            logger.error(f'❌ T8: update_metrics 전 메트릭 보정 실패: {e}')
            self.metrics.current_wip = 0
            self.metrics.workload_level = WorkloadLevel.IDLE
            self.metrics.safety_score = 1.0
        if 'workload_level' in kwargs:
            if isinstance(kwargs['workload_level'], str):
                try:
                    self.metrics.workload_level = WorkloadLevel(kwargs['workload_level'])
                    logger.debug(f"✅ T3: workload_level 업데이트: {kwargs['workload_level']}")
                except ValueError:
                    logger.warning(f"⚠️ T3: 잘못된 workload_level 값 {kwargs['workload_level']} → IDLE로 보정")
                    self.metrics.workload_level = WorkloadLevel.IDLE
            elif isinstance(kwargs['workload_level'], WorkloadLevel):
                self.metrics.workload_level = kwargs['workload_level']
                logger.debug(f"✅ T3: workload_level 업데이트: {kwargs['workload_level'].value}")
        if 'current_wip' in kwargs:
            wip_value = kwargs['current_wip']
            try:
                if isinstance(wip_value, (int, float)) and wip_value >= 0:
                    self.metrics.current_wip = int(wip_value)
                    logger.debug(f'✅ T3: current_wip 업데이트: {wip_value}')
                else:
                    logger.warning(f'⚠️ T3: 잘못된 current_wip 값 {wip_value} → 0으로 보정')
                    self.metrics.current_wip = 0
            except (ValueError, TypeError):
                logger.warning(f'⚠️ T3: current_wip 타입 오류 {wip_value} → 0으로 보정')
                self.metrics.current_wip = 0
        if 'safety_score' in kwargs:
            safety_value = kwargs['safety_score']
            try:
                if isinstance(safety_value, (int, float)) and 0 <= safety_value <= 1:
                    self.metrics.safety_score = float(safety_value)
                    logger.debug(f'✅ T3: safety_score 업데이트: {safety_value}')
                else:
                    logger.warning(f'⚠️ T3: 잘못된 safety_score 값 {safety_value} → 1.0으로 보정')
                    self.metrics.safety_score = 1.0
            except (ValueError, TypeError):
                logger.warning(f'⚠️ T3: safety_score 타입 오류 {safety_value} → 1.0으로 보정')
                self.metrics.safety_score = 1.0
        if 'health_status' in kwargs:
            try:
                self.metrics.health_status = str(kwargs['health_status'])
                logger.debug(f"✅ T3: health_status 업데이트: {kwargs['health_status']}")
            except Exception:
                logger.warning(f"⚠️ T3: health_status 타입 오류 → 'healthy'로 보정")
                self.metrics.health_status = 'healthy'
        self.metrics.last_update = update_time
        try:
            self._notify_listeners('metrics_update', {'metrics': self.get_metrics(), 'update_time': update_time.isoformat()})
            logger.info('✅ T3: 메트릭 업데이트 완료 (타입 검증 통과)')
        except Exception as e:
            logger.error(f'❌ T3: 메트릭 업데이트 이벤트 알림 실패: {e}')
        return True

    def get_metrics(self) -> Dict[str, Any]:
        """현재 메트릭 반환 (SSOT) - T8: 딕셔너리 기준 통일 + setdefault 가드"""
        metrics_dict = {}
        try:
            metrics_dict['workload_level'] = getattr(self.metrics, 'workload_level', WorkloadLevel.IDLE).value
            metrics_dict['current_wip'] = getattr(self.metrics, 'current_wip', 0)
            metrics_dict['safety_score'] = getattr(self.metrics, 'safety_score', 1.0)
            metrics_dict['health_status'] = getattr(self.metrics, 'health_status', 'healthy')
            metrics_dict['last_update'] = getattr(self.metrics, 'last_update', datetime.now()).isoformat()
        except Exception as e:
            logger.error(f'❌ T8: 기본 메트릭 구성 중 오류: {e}')
            metrics_dict.update({'workload_level': 'idle', 'current_wip': 0, 'safety_score': 1.0, 'health_status': 'healthy', 'last_update': datetime.now().isoformat()})
        try:
            if hasattr(self, '_equivalence_metrics') and self._equivalence_metrics:
                metrics_dict.update(self._equivalence_metrics)
            else:
                logger.debug('🔧 T8: 동등성 메트릭 기본값 설정')
                self._equivalence_metrics = {'overall_equivalence_score': None, 'n_samples': 0, 'last_validation': None, 'validation_history': [], 'threshold': 0.8}
                metrics_dict.update(self._equivalence_metrics)
        except Exception as e:
            logger.error(f'❌ T8: 동등성 메트릭 처리 중 오류: {e}')
            metrics_dict.update({'overall_equivalence_score': None, 'n_samples': 0, 'last_validation': None, 'validation_history': [], 'threshold': 0.8})
        return metrics_dict

    def get_state(self) -> Dict[str, Any]:
        """현재 상태 정보 반환"""
        return {'current_state': self.current_state.value, 'uptime_seconds': (datetime.now() - self.start_time).total_seconds(), 'state_history_count': len(self.state_history), 'metrics': self.get_metrics()}

    def get_state_history(self, limit: int=100) -> List[Dict[str, Any]]:
        """상태 전환 히스토리 반환"""
        recent_transitions = self.state_history[-limit:] if limit > 0 else self.state_history
        return [{'from_state': t.from_state.value, 'to_state': t.to_state.value, 'timestamp': t.timestamp.isoformat(), 'reason': t.reason, 'metadata': t.metadata} for t in recent_transitions]

    async def enter_safe_mode(self, reason: str='안전 모드 진입'):
        """안전 모드 진입"""
        await self.change_state(SystemState.SAFE_MODE, reason, {'mode': 'safe_mode'})
        logger.warning(f'안전 모드 진입: {reason}')

    async def exit_safe_mode(self, reason: str='안전 모드 해제'):
        """안전 모드 해제"""
        await self.change_state(SystemState.READY, reason, {'mode': 'normal'})
        logger.info(f'안전 모드 해제: {reason}')

    async def emergency_stop(self, reason: str='비상 정지'):
        """비상 정지"""
        await self.change_state(SystemState.EMERGENCY_STOP, reason, {'mode': 'emergency'})
        logger.critical(f'비상 정지: {reason}')

    async def trigger_emergency_stop(self, estop_data: Dict[str, Any]):
        """E-stop 트리거 실행 (T5: E-stop 히스테리시스 지원 + HF-4: SSOT 라우팅 고정)"""
        reason = estop_data.get('reason', 'E-stop 트리거')
        trigger = estop_data.get('trigger', 'unknown')
        severity = estop_data.get('severity', 1.0)
        routing_config = {'equivalence': 'hysteresis', 'performance': 'immediate', 'observability': 'gradual'}
        logger.critical(f'🚨 E-stop 트리거: {trigger} (심각도: {severity:.2f})')
        logger.critical(f'🚨 E-stop 사유: {reason}')
        logger.critical(f'🚨 HF-4: SSOT 라우팅 설정 - {routing_config}')
        await self.emergency_stop(reason)
        self._notify_listeners('emergency_stop', {'trigger': trigger, 'severity': severity, 'reason': reason, 'timestamp': datetime.now(), 'estop_data': estop_data, 'routing_config': routing_config})
        return {'status': 'emergency_stop_triggered', 'timestamp': datetime.now(), 'routing_config': routing_config}

    def publish_equivalence_metrics(self, equivalence_snapshot: Dict[str, Any]):
        """동등성 메트릭 퍼블리시 (SSOT 경로) - T7: 퍼블리셔 경로 단일화 확인 로그 추가"""
        try:
            overall_score = equivalence_snapshot.get('overall_equivalence_score')
            n_samples = equivalence_snapshot.get('n_samples', 0)
            logger.info(f'✅ T7: Equivalence → StateManager OK: overall_equivalence_score={overall_score}, n_samples={n_samples}')
            self.metrics.safety_score = overall_score if overall_score is not None else 1.0
            if not hasattr(self, '_equivalence_metrics'):
                self._equivalence_metrics = {}
            for (key, value) in equivalence_snapshot.items():
                if key not in self._equivalence_metrics:
                    self._equivalence_metrics[key] = value
                    logger.debug(f'🔧 T10: 새 키 추가 - {key}: {value}')
                else:
                    logger.debug(f'🔧 T10: 기존 키 보존 - {key}: {self._equivalence_metrics[key]}')
            self._notify_listeners('metrics_update', {'metrics': self.get_metrics(), 'equivalence_metrics': equivalence_snapshot, 'update_time': datetime.now().isoformat()})
            logger.info(f'✅ T7: 동등성 메트릭 퍼블리시 완료: overall_equivalence_score={overall_score}, n_samples={n_samples}')
        except Exception as e:
            logger.error(f'❌ T7: 동등성 메트릭 퍼블리시 실패: {e}')

    def get_equivalence_metrics(self) -> Dict[str, Any]:
        """동등성 메트릭 반환 (SSOT) - T8: 기본값 보장"""
        if hasattr(self, '_equivalence_metrics'):
            return self._equivalence_metrics.copy()
        else:
            return {'overall_equivalence_score': None, 'n_samples': 0, 'last_validation': None, 'validation_history': [], 'threshold': 0.8, 'source': 'StateManager'}
state_manager = StateManager()