from DuRiCore.trace import emit_trace
"""
DuRi SafetyController - Phase 1 완성
히스테리시스 + 락 + UTC + AsyncMock 기능을 포함한 안전성 제어 시스템

@preserve_identity: 기존 기능과 동작 패턴 보존
@evolution_protection: 진화 과정에서의 안전성 확보
@execution_guarantee: 통합된 안전성 보장
@existence_ai: 안전한 진화와 회복
@final_execution: 통합 안전성이 보장된 최종 실행
"""
import asyncio
import json
import time
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import traceback
from pathlib import Path
from collections import deque
import threading
from contextlib import asynccontextmanager
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

class SafetyTrigger(Enum):
    """안전성 트리거 유형"""
    PERFORMANCE_DEGRADATION = 'performance_degradation'
    MEMORY_LEAK = 'memory_leak'
    ERROR_SPIKE = 'error_spike'
    RESOURCE_EXHAUSTION = 'resource_exhaustion'
    BEHAVIOR_ANOMALY = 'behavior_anomaly'

class SafetyAction(Enum):
    """안전성 액션"""
    EMERGENCY_STOP = 'emergency_stop'
    GRADUAL_THROTTLE = 'gradual_throttle'
    WARNING = 'warning'
    MONITOR = 'monitor'
    NONE = 'none'

@dataclass
class SafetyEvent:
    """안전성 이벤트"""
    id: str
    trigger: SafetyTrigger
    level: SafetyLevel
    timestamp: datetime
    details: Dict[str, Any]
    action: SafetyAction
    resolved: bool = False
    resolution_time: Optional[datetime] = None

@dataclass
class HysteresisWindow:
    """히스테리시스 윈도우 - T10: 웜업 윈도우 포함"""
    window_size: int = 3
    time_window: float = 180.0
    warmup_window: float = 60.0
    violations: deque = field(default_factory=lambda : deque(maxlen=3))
    last_action_time: Optional[datetime] = None

    def add_violation(self, event: SafetyEvent):
        """위반 추가"""
        self.violations.append(event)

    def should_trigger_action(self) -> bool:
        """액션 트리거 여부 확인 - T10: 웜업 윈도우 적용"""
        if self.last_action_time:
            warmup_elapsed = (datetime.now(timezone.utc) - self.last_action_time).total_seconds()
            if warmup_elapsed < self.warmup_window:
                logger.debug(f'🔧 T10: 웜업 윈도우 내 액션 차단 (경과: {warmup_elapsed:.1f}s < {self.warmup_window}s)')
                return False
        if len(self.violations) < self.window_size:
            return False
        now = datetime.now(timezone.utc)
        recent_violations = [v for v in self.violations if (now - v.timestamp).total_seconds() <= self.time_window]
        return len(recent_violations) >= self.window_size

    def record_action(self):
        """액션 실행 기록 - T10: 웜업 윈도우 시작"""
        self.last_action_time = datetime.now(timezone.utc)
        logger.info(f'🔧 T10: 웜업 윈도우 시작 - {self.warmup_window}s 동안 액션 차단')

    def get_warmup_status(self) -> Dict[str, Any]:
        """웜업 상태 반환 - T10: 웜업 윈도우 정보"""
        if not self.last_action_time:
            return {'active': False, 'remaining': 0.0}
        elapsed = (datetime.now(timezone.utc) - self.last_action_time).total_seconds()
        remaining = max(0.0, self.warmup_window - elapsed)
        return {'active': remaining > 0.0, 'remaining': remaining, 'elapsed': elapsed, 'warmup_window': self.warmup_window}

@dataclass
class SafetyMetrics:
    """안전성 메트릭"""
    total_events: int = 0
    critical_events: int = 0
    high_events: int = 0
    medium_events: int = 0
    low_events: int = 0
    emergency_stops: int = 0
    gradual_throttles: int = 0
    warnings: int = 0
    error_events: int = 0
    performance_events: int = 0
    memory_events: int = 0
    resource_events: int = 0
    behavior_events: int = 0
    last_event_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    safety_score: float = 1.0

class AsyncMock:
    """비동기 모의 객체 - 테스트 및 개발용"""

    def __init__(self, return_value: Any=None, side_effect: Any=None):
        self.return_value = return_value
        self.side_effect = side_effect
        self.call_count = 0
        self.call_args = []
        self.call_kwargs = []

    async def __call__(self, *args, **kwargs):
        """비동기 호출 모의"""
        self.call_count += 1
        self.call_args.append(args)
        self.call_kwargs.append(kwargs)
        if self.side_effect is not None:
            if callable(self.side_effect):
                if asyncio.iscoroutinefunction(self.side_effect):
                    return await self.side_effect(*args, **kwargs)
                else:
                    return self.side_effect(*args, **kwargs)
            else:
                return self.side_effect
        return self.return_value

    def reset_mock(self):
        """모의 객체 초기화"""
        self.call_count = 0
        self.call_args.clear()
        self.call_kwargs.clear()

    def assert_called_with(self, *args, **kwargs):
        """호출 인자 검증"""
        if not self.call_args:
            raise AssertionError('모의 객체가 호출되지 않았습니다')
        last_call_args = self.call_args[-1]
        last_call_kwargs = self.call_kwargs[-1]
        if args != last_call_args or kwargs != last_call_kwargs:
            raise AssertionError(f'예상: args={args}, kwargs={kwargs}, 실제: args={last_call_args}, kwargs={last_call_kwargs}')

class SafetyController:
    """안전성 제어 시스템 - Phase 1 완성"""

    def __init__(self, config: Optional[Dict[str, Any]]=None):
        self.config = config or {}
        self.enabled = self.config.get('enabled', True)
        self.auto_resolve = self.config.get('auto_resolve', False)
        self.hysteresis_windows: Dict[SafetyTrigger, HysteresisWindow] = {}
        for trigger in SafetyTrigger:
            self.hysteresis_windows[trigger] = HysteresisWindow(window_size=self.config.get(f'{trigger.value}_window_size', 3), time_window=self.config.get(f'{trigger.value}_time_window', 180.0), warmup_window=self.config.get(f'{trigger.value}_warmup_window', 60.0))
        self._lock = threading.RLock()
        self._async_lock = asyncio.Lock()
        self._running = False
        self._events: List[SafetyEvent] = []
        self._metrics = SafetyMetrics()
        self._start_time = datetime.now(timezone.utc)
        self._callbacks: Dict[SafetyAction, List[Callable]] = {action: [] for action in SafetyAction}
        self._mocks: Dict[str, AsyncMock] = {}
        logger.info('🔒 SafetyController 초기화 완료')

    @asynccontextmanager
    async def safety_context(self):
        """안전성 컨텍스트 매니저"""
        try:
            await self._async_lock.acquire()
            logger.debug('🔒 안전성 컨텍스트 진입')
            yield self
        finally:
            self._async_lock.release()
            logger.debug('🔒 안전성 컨텍스트 해제')

    async def start(self):
        """안전성 제어 시스템 시작"""
        async with self.safety_context():
            if self._running:
                logger.warning('⚠️ SafetyController가 이미 실행 중입니다')
                return False
            self._running = True
            self._start_time = datetime.now(timezone.utc)
            logger.info('🚀 SafetyController 시작됨')
            return True

    async def stop(self):
        """안전성 제어 시스템 정지"""
        async with self.safety_context():
            if not self._running:
                logger.warning('⚠️ SafetyController가 이미 정지되어 있습니다')
                return False
            self._running = False
            uptime = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            self._metrics.uptime_seconds = uptime
            logger.info(f'🛑 SafetyController 정지됨 (가동시간: {uptime:.1f}초)')
            return True

    async def register_event(self, trigger: SafetyTrigger, level: SafetyLevel, details: Dict[str, Any]) -> SafetyEvent:
        """안전성 이벤트 등록"""
        async with self.safety_context():
            if not self._running:
                logger.warning('⚠️ SafetyController가 실행되지 않았습니다')
                return None
            timestamp = datetime.now(timezone.utc)
            event = SafetyEvent(id=f'evt_{int(timestamp.timestamp() * 1000)}', trigger=trigger, level=level, timestamp=timestamp, details=details, action=SafetyAction.NONE)
            hysteresis = self.hysteresis_windows[trigger]
            hysteresis.add_violation(event)
            action = await self._determine_action(trigger, level, hysteresis)
            event.action = action
            self._events.append(event)
            await self._update_metrics(event)
            await self._execute_callbacks(action, event)
            logger.info(f'🔔 안전성 이벤트 등록: {trigger.value} - {level.value} -> {action.value}')
            return event

    async def _determine_action(self, trigger: SafetyTrigger, level: SafetyLevel, hysteresis: HysteresisWindow) -> SafetyAction:
        """액션 결정 로직"""
        if hysteresis.should_trigger_action():
            if level == SafetyLevel.CRITICAL:
                return SafetyAction.EMERGENCY_STOP
            elif level == SafetyLevel.HIGH:
                return SafetyAction.GRADUAL_THROTTLE
            elif level == SafetyLevel.MEDIUM:
                return SafetyAction.WARNING
            else:
                return SafetyAction.MONITOR
        if level == SafetyLevel.CRITICAL:
            return SafetyAction.EMERGENCY_STOP
        elif level == SafetyLevel.HIGH:
            return SafetyAction.WARNING
        elif level == SafetyLevel.MEDIUM:
            return SafetyAction.MONITOR
        else:
            return SafetyAction.NONE

    async def _update_metrics(self, event: SafetyEvent):
        """메트릭 업데이트"""
        self._metrics.total_events += 1
        self._metrics.last_event_time = event.timestamp
        if event.level == SafetyLevel.CRITICAL:
            self._metrics.critical_events += 1
        elif event.level == SafetyLevel.HIGH:
            self._metrics.high_events += 1
        elif event.level == SafetyLevel.MEDIUM:
            self._metrics.medium_events += 1
        elif event.level == SafetyLevel.LOW:
            self._metrics.low_events += 1
        if event.action == SafetyAction.EMERGENCY_STOP:
            self._metrics.emergency_stops += 1
        elif event.action == SafetyAction.GRADUAL_THROTTLE:
            self._metrics.gradual_throttles += 1
        elif event.action == SafetyAction.WARNING:
            self._metrics.warnings += 1
        if event.trigger == SafetyTrigger.ERROR_SPIKE:
            self._metrics.error_events += 1
        elif event.trigger == SafetyTrigger.PERFORMANCE_DEGRADATION:
            self._metrics.performance_events += 1
        elif event.trigger == SafetyTrigger.MEMORY_LEAK:
            self._metrics.memory_events += 1
        elif event.trigger == SafetyTrigger.RESOURCE_EXHAUSTION:
            self._metrics.resource_events += 1
        elif event.trigger == SafetyTrigger.BEHAVIOR_ANOMALY:
            self._metrics.behavior_events += 1
        await self._calculate_safety_score()

    async def _calculate_safety_score(self):
        """안전성 점수 계산"""
        if self._metrics.total_events == 0:
            self._metrics.safety_score = 1.0
            return
        critical_weight = 1.0
        high_weight = 0.7
        medium_weight = 0.4
        low_weight = 0.1
        total_weighted = self._metrics.critical_events * critical_weight + self._metrics.high_events * high_weight + self._metrics.medium_events * medium_weight + self._metrics.low_events * low_weight
        max_possible_weight = self._metrics.total_events * critical_weight
        self._metrics.safety_score = max(0.0, 1.0 - total_weighted / max_possible_weight)

    async def register_callback(self, action: SafetyAction, callback: Callable):
        """콜백 함수 등록"""
        async with self.safety_context():
            if action not in self._callbacks:
                self._callbacks[action] = []
            self._callbacks[action].append(callback)
            logger.debug(f'📞 콜백 등록: {action.value}')

    async def _execute_callbacks(self, action: SafetyAction, event: SafetyEvent):
        """콜백 함수 실행"""
        if action not in self._callbacks:
            return
        for callback in self._callbacks[action]:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                logger.error(f'❌ 콜백 실행 오류: {e}')
                traceback.print_exc()

    async def resolve_event(self, event_id: str, resolution_details: Dict[str, Any]=None):
        """이벤트 해결"""
        async with self.safety_context():
            for event in self._events:
                if event.id == event_id and (not event.resolved):
                    event.resolved = True
                    event.resolution_time = datetime.now(timezone.utc)
                    if resolution_details:
                        event.details.update(resolution_details)
                    logger.info(f'✅ 이벤트 해결: {event_id}')
                    return True
            logger.warning(f'⚠️ 이벤트를 찾을 수 없습니다: {event_id}')
            return False

    async def get_events(self, resolved: Optional[bool]=None, trigger: Optional[SafetyTrigger]=None, level: Optional[SafetyLevel]=None) -> List[SafetyEvent]:
        """이벤트 조회"""
        async with self.safety_context():
            events = self._events
            if resolved is not None:
                events = [e for e in events if e.resolved == resolved]
            if trigger is not None:
                events = [e for e in events if e.trigger == trigger]
            if level is not None:
                events = [e for e in events if e.level == level]
            return events

    async def get_metrics(self) -> SafetyMetrics:
        """메트릭 조회"""
        async with self.safety_context():
            if self._running:
                self._metrics.uptime_seconds = (datetime.now(timezone.utc) - self._start_time).total_seconds()
            return self._metrics

    async def get_hysteresis_status(self) -> Dict[str, Any]:
        """히스테리시스 상태 조회"""
        async with self.safety_context():
            status = {}
            for (trigger, hysteresis) in self.hysteresis_windows.items():
                status[trigger.value] = {'window_size': hysteresis.window_size, 'time_window': hysteresis.time_window, 'warmup_window': hysteresis.warmup_window, 'violation_count': len(hysteresis.violations), 'should_trigger': hysteresis.should_trigger_action(), 'warmup_status': hysteresis.get_warmup_status()}
            return status

    def add_mock(self, name: str, mock: AsyncMock):
        """모의 객체 추가 (테스트용)"""
        self._mocks[name] = mock
        logger.debug(f'🎭 모의 객체 추가: {name}')

    def get_mock(self, name: str) -> Optional[AsyncMock]:
        """모의 객체 조회 (테스트용)"""
        return self._mocks.get(name)

    async def health_check(self) -> Dict[str, Any]:
        """건강 상태 확인"""
        async with self.safety_context():
            return {'status': 'healthy' if self._running else 'stopped', 'running': self._running, 'enabled': self.enabled, 'uptime_seconds': self._metrics.uptime_seconds, 'total_events': self._metrics.total_events, 'safety_score': self._metrics.safety_score, 'hysteresis_windows': len(self.hysteresis_windows), 'registered_callbacks': sum((len(callbacks) for callbacks in self._callbacks.values())), 'mocks': len(self._mocks)}

    async def reset(self):
        """시스템 초기화"""
        async with self.safety_context():
            self._events.clear()
            self._metrics = SafetyMetrics()
            self._start_time = datetime.now(timezone.utc)
            for hysteresis in self.hysteresis_windows.values():
                hysteresis.violations.clear()
                hysteresis.last_action_time = None
            for mock in self._mocks.values():
                mock.reset_mock()
            logger.info('🔄 SafetyController 초기화 완료')
safety_controller = SafetyController()

async def register_safety_event(trigger: SafetyTrigger, level: SafetyLevel, details: Dict[str, Any]) -> SafetyEvent:
    """전역 안전성 이벤트 등록"""
    return await safety_controller.register_event(trigger, level, details)

async def get_safety_metrics() -> SafetyMetrics:
    """전역 안전성 메트릭 조회"""
    return await safety_controller.get_metrics()

async def get_safety_health() -> Dict[str, Any]:
    """전역 안전성 건강 상태 조회"""
    return await safety_controller.health_check()