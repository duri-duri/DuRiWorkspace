from DuRiCore.trace import emit_trace
"""
DuRi SafetyController 테스트 - Phase 1 완성 검증
히스테리시스 + 락 + UTC + AsyncMock 기능 테스트

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
from typing import Dict, List, Any, Optional
import logging

def pytest_mark_asyncio(func):
    """pytest.mark.asyncio 대체용 데코레이터"""
    return func

def pytest_fixture(autouse=False):
    """pytest.fixture 대체용 데코레이터"""

    def decorator(func):
        return func
    return decorator
try:
    from DuRiCore.safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, HysteresisWindow, SafetyMetrics, AsyncMock, safety_controller, register_safety_event, get_safety_metrics, get_safety_health
except ImportError:
    from safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, HysteresisWindow, SafetyMetrics, AsyncMock, safety_controller, register_safety_event, get_safety_metrics, get_safety_health
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestSafetyController:
    """SafetyController 테스트 클래스"""

    def __init__(self):
        """테스트 인스턴스 초기화"""
        self.controller = None

    async def setup(self):
        """테스트 전 설정"""
        self.controller = SafetyController()
        await self.controller.start()

    async def teardown(self):
        """테스트 후 정리"""
        if self.controller:
            await self.controller.stop()
            await self.controller.reset()

    @pytest_mark_asyncio
    async def test_initialization(self):
        """초기화 테스트"""
        await self.setup()
        try:
            assert self.controller.enabled == True
            assert self.controller.auto_resolve == False
            assert len(self.controller.hysteresis_windows) == len(SafetyTrigger)
            assert self.controller._running == True
            for trigger in SafetyTrigger:
                assert trigger in self.controller.hysteresis_windows
                hysteresis = self.controller.hysteresis_windows[trigger]
                assert hysteresis.window_size == 3
                assert hysteresis.time_window == 180.0
                assert hysteresis.warmup_window == 60.0
        finally:
            await self.teardown()

    @pytest_mark_asyncio
    async def test_start_stop(self):
        """시작/정지 테스트"""
        result = await self.controller.start()
        assert result == False
        result = await self.controller.stop()
        assert result == True
        assert self.controller._running == False
        result = await self.controller.start()
        assert result == True
        assert self.controller._running == True

    @pytest_mark_asyncio
    async def test_safety_context(self):
        """안전성 컨텍스트 테스트"""
        async with self.controller.safety_context():
            assert self.controller._async_lock.locked() == True
        assert self.controller._async_lock.locked() == False

    @pytest_mark_asyncio
    async def test_register_event_basic(self):
        """기본 이벤트 등록 테스트"""
        details = {'message': '테스트 이벤트', 'value': 42}
        event = await self.controller.register_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM, details)
        assert event is not None
        assert event.trigger == SafetyTrigger.PERFORMANCE_DEGRADATION
        assert event.level == SafetyLevel.MEDIUM
        assert event.details == details
        assert event.action == SafetyAction.MONITOR
        assert event.resolved == False
        assert event.timestamp.tzinfo == timezone.utc

    @pytest_mark_asyncio
    async def test_register_event_critical(self):
        """위험 이벤트 등록 테스트"""
        details = {'error_count': 100, 'response_time': 5000}
        event = await self.controller.register_event(SafetyTrigger.ERROR_SPIKE, SafetyLevel.CRITICAL, details)
        assert event is not None
        assert event.action == SafetyAction.EMERGENCY_STOP

    @pytest_mark_asyncio
    async def test_hysteresis_window_basic(self):
        """히스테리시스 윈도우 기본 테스트"""
        hysteresis = self.controller.hysteresis_windows[SafetyTrigger.PERFORMANCE_DEGRADATION]
        assert hysteresis.should_trigger_action() == False
        assert len(hysteresis.violations) == 0
        for i in range(3):
            event = SafetyEvent(id=f'test_{i}', trigger=SafetyTrigger.PERFORMANCE_DEGRADATION, level=SafetyLevel.MEDIUM, timestamp=datetime.now(timezone.utc), details={'iteration': i}, action=SafetyAction.NONE)
            hysteresis.add_violation(event)
        assert len(hysteresis.violations) == 3
        assert hysteresis.should_trigger_action() == True

    @pytest_mark_asyncio
    async def test_hysteresis_warmup_window(self):
        """히스테리시스 웜업 윈도우 테스트 - T10"""
        hysteresis = self.controller.hysteresis_windows[SafetyTrigger.MEMORY_LEAK]
        hysteresis.record_action()
        assert hysteresis.should_trigger_action() == False
        warmup_status = hysteresis.get_warmup_status()
        assert warmup_status['active'] == True
        assert warmup_status['remaining'] > 0.0
        assert warmup_status['warmup_window'] == 60.0

    @pytest_mark_asyncio
    async def test_hysteresis_time_window(self):
        """히스테리시스 시간 윈도우 테스트"""
        hysteresis = self.controller.hysteresis_windows[SafetyTrigger.RESOURCE_EXHAUSTION]
        old_event = SafetyEvent(id='old_event', trigger=SafetyTrigger.RESOURCE_EXHAUSTION, level=SafetyLevel.HIGH, timestamp=datetime.now(timezone.utc) - timedelta(seconds=200), details={'old': True}, action=SafetyAction.NONE)
        hysteresis.add_violation(old_event)
        for i in range(2):
            recent_event = SafetyEvent(id=f'recent_{i}', trigger=SafetyTrigger.RESOURCE_EXHAUSTION, level=SafetyLevel.HIGH, timestamp=datetime.now(timezone.utc), details={'recent': True, 'iteration': i}, action=SafetyAction.NONE)
            hysteresis.add_violation(recent_event)
        assert hysteresis.should_trigger_action() == False

    @pytest_mark_asyncio
    async def test_metrics_update(self):
        """메트릭 업데이트 테스트"""
        initial_metrics = await self.controller.get_metrics()
        assert initial_metrics.total_events == 0
        assert initial_metrics.safety_score == 1.0
        events = [(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.LOW), (SafetyTrigger.MEMORY_LEAK, SafetyLevel.MEDIUM), (SafetyTrigger.ERROR_SPIKE, SafetyLevel.HIGH), (SafetyTrigger.RESOURCE_EXHAUSTION, SafetyLevel.CRITICAL)]
        for (trigger, level) in events:
            await self.controller.register_event(trigger, level, {'test': True})
        updated_metrics = await self.controller.get_metrics()
        assert updated_metrics.total_events == 4
        assert updated_metrics.low_events == 1
        assert updated_metrics.medium_events == 1
        assert updated_metrics.high_events == 1
        assert updated_metrics.critical_events == 1
        assert updated_metrics.safety_score < 1.0

    @pytest_mark_asyncio
    async def test_callback_registration(self):
        """콜백 등록 테스트"""
        callback_called = False
        callback_event = None

        async def test_callback(event: SafetyEvent):
            nonlocal callback_called, callback_event
            callback_called = True
            callback_event = event
        await self.controller.register_callback(SafetyAction.WARNING, test_callback)
        event = await self.controller.register_event(SafetyTrigger.BEHAVIOR_ANOMALY, SafetyLevel.HIGH, {'anomaly': 'test'})
        assert callback_called == True
        assert callback_event == event

    @pytest_mark_asyncio
    async def test_event_resolution(self):
        """이벤트 해결 테스트"""
        event = await self.controller.register_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM, {'issue': 'resolved'})
        assert event.resolved == False
        assert event.resolution_time is None
        resolution_details = {'resolution': 'manual_fix', 'fixed_by': 'tester'}
        result = await self.controller.resolve_event(event.id, resolution_details)
        assert result == True
        assert event.resolved == True
        assert event.resolution_time is not None
        assert 'resolution' in event.details

    @pytest_mark_asyncio
    async def test_event_filtering(self):
        """이벤트 필터링 테스트"""
        events_data = [(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.LOW), (SafetyTrigger.MEMORY_LEAK, SafetyLevel.MEDIUM), (SafetyTrigger.ERROR_SPIKE, SafetyLevel.HIGH), (SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM)]
        for (trigger, level) in events_data:
            await self.controller.register_event(trigger, level, {'filter_test': True})
        all_events = await self.controller.get_events()
        assert len(all_events) == 4
        perf_events = await self.controller.get_events(trigger=SafetyTrigger.PERFORMANCE_DEGRADATION)
        assert len(perf_events) == 2
        high_events = await self.controller.get_events(level=SafetyLevel.HIGH)
        assert len(high_events) == 1
        unresolved_events = await self.controller.get_events(resolved=False)
        assert len(unresolved_events) == 4

    @pytest_mark_asyncio
    async def test_async_mock_basic(self):
        """AsyncMock 기본 테스트"""
        mock = AsyncMock(return_value='test_result')
        assert mock.call_count == 0
        assert len(mock.call_args) == 0
        result = await mock('arg1', 'arg2', key='value')
        assert result == 'test_result'
        assert mock.call_count == 1
        assert mock.call_args[0] == ('arg1', 'arg2')
        assert mock.call_kwargs[0] == {'key': 'value'}

    @pytest_mark_asyncio
    async def test_async_mock_side_effect(self):
        """AsyncMock 사이드 이펙트 테스트"""

        async def side_effect_func(arg1, arg2):
            return f'processed_{arg1}_{arg2}'
        mock = AsyncMock(side_effect=side_effect_func)
        result = await mock('hello', 'world')
        assert result == 'processed_hello_world'
        mock.assert_called_with('hello', 'world')

    @pytest_mark_asyncio
    async def test_async_mock_reset(self):
        """AsyncMock 리셋 테스트"""
        mock = AsyncMock(return_value='test')
        await mock('call1')
        await mock('call2')
        assert mock.call_count == 2
        assert len(mock.call_args) == 2
        mock.reset_mock()
        assert mock.call_count == 0
        assert len(mock.call_args) == 0
        assert len(mock.call_kwargs) == 0

    @pytest_mark_asyncio
    async def test_controller_mock_integration(self):
        """컨트롤러와 모의 객체 통합 테스트"""
        test_mock = AsyncMock(return_value='mock_result')
        self.controller.add_mock('test_mock', test_mock)
        retrieved_mock = self.controller.get_mock('test_mock')
        assert retrieved_mock == test_mock
        result = await retrieved_mock('test_arg')
        assert result == 'mock_result'
        health = await self.controller.health_check()
        assert health['mocks'] == 1

    @pytest_mark_asyncio
    async def test_health_check(self):
        """건강 상태 확인 테스트"""
        health = await self.controller.health_check()
        assert 'status' in health
        assert 'running' in health
        assert 'enabled' in health
        assert 'uptime_seconds' in health
        assert 'total_events' in health
        assert 'safety_score' in health
        assert 'hysteresis_windows' in health
        assert 'registered_callbacks' in health
        assert 'mocks' in health
        assert health['status'] == 'healthy'
        assert health['running'] == True
        assert health['enabled'] == True
        assert health['hysteresis_windows'] == len(SafetyTrigger)

    @pytest_mark_asyncio
    async def test_hysteresis_status(self):
        """히스테리시스 상태 조회 테스트"""
        status = await self.controller.get_hysteresis_status()
        for trigger in SafetyTrigger:
            assert trigger.value in status
            trigger_status = status[trigger.value]
            assert 'window_size' in trigger_status
            assert 'time_window' in trigger_status
            assert 'warmup_window' in trigger_status
            assert 'violation_count' in trigger_status
            assert 'should_trigger' in trigger_status
            assert 'warmup_status' in trigger_status

    @pytest_mark_asyncio
    async def test_global_functions(self):
        """전역 함수 테스트"""
        await safety_controller.start()
        try:
            event = await register_safety_event(SafetyTrigger.BEHAVIOR_ANOMALY, SafetyLevel.LOW, {'global_test': True})
            assert event is not None
            assert event.trigger == SafetyTrigger.BEHAVIOR_ANOMALY
            metrics = await get_safety_metrics()
            assert metrics.total_events > 0
            health = await get_safety_health()
            assert health['status'] == 'healthy'
        finally:
            await safety_controller.stop()

    @pytest_mark_asyncio
    async def test_concurrent_access(self):
        """동시 접근 테스트"""

        async def register_event_task(task_id: int):
            return await self.controller.register_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM, {'task_id': task_id, 'concurrent': True})
        tasks = [register_event_task(i) for i in range(5)]
        results = await asyncio.gather(*tasks)
        assert all((result is not None for result in results))
        assert len(results) == 5
        metrics = await self.controller.get_metrics()
        assert metrics.total_events >= 5

    @pytest_mark_asyncio
    async def test_error_handling(self):
        """오류 처리 테스트"""
        stopped_controller = SafetyController()
        event = await stopped_controller.register_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM, {'test': True})
        assert event is None
        result = await self.controller.resolve_event('nonexistent_id')
        assert result == False

class TestHysteresisWindow:
    """HysteresisWindow 독립 테스트"""

    def test_hysteresis_initialization(self):
        """히스테리시스 윈도우 초기화 테스트"""
        hysteresis = HysteresisWindow()
        assert hysteresis.window_size == 3
        assert hysteresis.time_window == 180.0
        assert hysteresis.warmup_window == 60.0
        assert len(hysteresis.violations) == 0
        assert hysteresis.last_action_time is None

    def test_violation_management(self):
        """위반 관리 테스트"""
        hysteresis = HysteresisWindow(window_size=2)
        event1 = SafetyEvent(id='test1', trigger=SafetyTrigger.PERFORMANCE_DEGRADATION, level=SafetyLevel.MEDIUM, timestamp=datetime.now(timezone.utc), details={'test': 1}, action=SafetyAction.NONE)
        event2 = SafetyEvent(id='test2', trigger=SafetyTrigger.PERFORMANCE_DEGRADATION, level=SafetyLevel.MEDIUM, timestamp=datetime.now(timezone.utc), details={'test': 2}, action=SafetyAction.NONE)
        hysteresis.add_violation(event1)
        assert len(hysteresis.violations) == 1
        assert hysteresis.should_trigger_action() == False
        hysteresis.add_violation(event2)
        assert len(hysteresis.violations) == 2
        assert hysteresis.should_trigger_action() == True

    def test_warmup_window_logic(self):
        """웜업 윈도우 로직 테스트 - T10"""
        hysteresis = HysteresisWindow(warmup_window=30.0)
        hysteresis.record_action()
        warmup_status = hysteresis.get_warmup_status()
        assert warmup_status['active'] == True
        assert warmup_status['remaining'] > 0.0
        assert warmup_status['warmup_window'] == 30.0
        assert hysteresis.should_trigger_action() == False

class TestAsyncMock:
    """AsyncMock 독립 테스트"""

    @pytest_mark_asyncio
    async def test_mock_assertions(self):
        """모의 객체 검증 테스트"""
        mock = AsyncMock()
        with pytest.raises(AssertionError):
            mock.assert_called_with('arg1')
        await mock('arg1', key='value')
        mock.assert_called_with('arg1', key='value')
        with pytest.raises(AssertionError):
            mock.assert_called_with('wrong_arg')

async def run_all_tests():
    """모든 테스트 실행"""
    emit_trace('info', ' '.join(map(str, ['🧪 SafetyController 테스트 시작'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    test_instance = TestSafetyController()
    test_methods = ['test_initialization', 'test_start_stop', 'test_safety_context', 'test_register_event_basic', 'test_register_event_critical', 'test_hysteresis_window_basic', 'test_hysteresis_warmup_window', 'test_hysteresis_time_window', 'test_metrics_update', 'test_callback_registration', 'test_event_resolution', 'test_event_filtering', 'test_async_mock_basic', 'test_async_mock_side_effect', 'test_async_mock_reset', 'test_controller_mock_integration', 'test_health_check', 'test_hysteresis_status', 'test_global_functions', 'test_concurrent_access', 'test_error_handling']
    passed = 0
    failed = 0
    for method_name in test_methods:
        try:
            emit_trace('info', ' '.join(map(str, [f'🔍 {method_name} 실행 중...'])))
            await test_instance.setup()
            await getattr(test_instance, method_name)()
            emit_trace('info', ' '.join(map(str, [f'✅ {method_name} 통과'])))
            passed += 1
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ {method_name} 실패: {e}'])))
            failed += 1
        finally:
            await test_instance.teardown()
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    emit_trace('info', ' '.join(map(str, [f'📊 테스트 결과: {passed}개 통과, {failed}개 실패'])))
    if failed == 0:
        emit_trace('info', ' '.join(map(str, ['🎉 모든 테스트 통과! Phase 1 완성!'])))
    else:
        emit_trace('info', ' '.join(map(str, ['⚠️ 일부 테스트 실패. 수정이 필요합니다.'])))
    return (passed, failed)
if __name__ == '__main__':
    asyncio.run(run_all_tests())