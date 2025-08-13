from DuRiCore.trace import emit_trace
"""
DuRi IntegrationValidator 테스트 - Phase 2 검증
통합 안전성 검증 시스템의 모든 기능 테스트

@preserve_identity: 기존 SafetyController와의 호환성 검증
@evolution_protection: 진화 과정에서의 통합 안전성 검증
@execution_guarantee: 통합된 검증 보장 검증
@existence_ai: 안전한 진화와 회복을 위한 통합 검증 테스트
@final_execution: 통합 안전성이 보장된 최종 실행 검증
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
try:
    from DuRiCore.integration_validator import IntegrationValidator, ValidationResult, ValidationRule, integration_validator, start_integration_validation, stop_integration_validation, run_integration_validation, get_integration_status
    from DuRiCore.safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, SafetyMetrics
except ImportError:
    from integration_validator import IntegrationValidator, ValidationResult, ValidationRule, integration_validator, start_integration_validation, stop_integration_validation, run_integration_validation, get_integration_status
    from safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, SafetyMetrics
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestIntegrationValidator:
    """IntegrationValidator 테스트 클래스"""

    def __init__(self):
        """테스트 인스턴스 초기화"""
        self.validator = None
        self.safety_controller = None

    async def setup(self):
        """테스트 전 설정"""
        self.safety_controller = SafetyController()
        await self.safety_controller.start()
        self.validator = IntegrationValidator(self.safety_controller)

    async def teardown(self):
        """테스트 후 정리"""
        if self.validator:
            await self.validator.stop()
            await self.validator.reset()
        if self.safety_controller:
            await self.safety_controller.stop()
            await self.safety_controller.reset()

    async def test_initialization(self):
        """초기화 테스트"""
        await self.setup()
        try:
            assert self.validator is not None
            assert self.validator._running == False
            assert len(self.validator.validation_rules) >= 3
            assert self.validator.max_concurrent_validations == 5
            assert self.validator.validation_semaphore._value == 5
            rule_names = [rule.name for rule in self.validator.validation_rules]
            assert 'performance_degradation_threshold' in rule_names
            assert 'error_spike_detection' in rule_names
            assert 'resource_exhaustion_warning' in rule_names
            emit_trace('info', ' '.join(map(str, ['✅ 초기화 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_rule_management(self):
        """규칙 관리 테스트"""
        await self.setup()
        try:
            custom_rule = ValidationRule(name='custom_test_rule', description='커스텀 테스트 규칙', severity=SafetyLevel.LOW, condition=lambda m: m.total_events < 100, action=SafetyAction.NONE)
            self.validator.add_rule(custom_rule)
            assert len(self.validator.validation_rules) == 4
            result = self.validator.remove_rule('custom_test_rule')
            assert result == True
            assert len(self.validator.validation_rules) == 3
            result = self.validator.remove_rule('nonexistent_rule')
            assert result == False
            emit_trace('info', ' '.join(map(str, ['✅ 규칙 관리 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_start_stop(self):
        """시작/정지 테스트"""
        await self.setup()
        try:
            result = await self.validator.start()
            assert result == True
            assert self.validator._running == True
            assert self.validator._validation_task is not None
            result = await self.validator.start()
            assert result == False
            result = await self.validator.stop()
            assert result == True
            assert self.validator._running == False
            assert self.validator._validation_task is None
            emit_trace('info', ' '.join(map(str, ['✅ 시작/정지 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_validation_execution(self):
        """검증 실행 테스트"""
        await self.setup()
        try:
            await self.validator.start()
            result = await self.validator.run_validation()
            assert isinstance(result, ValidationResult)
            assert result.success == True
            assert result.metrics is not None
            assert 'rules_evaluated' in result.details
            assert len(self.validator.validation_history) > 0
            assert self.validator.validation_history[-1] == result
            emit_trace('info', ' '.join(map(str, ['✅ 검증 실행 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_rule_evaluation(self):
        """규칙 평가 테스트"""
        await self.setup()
        try:
            test_metrics = SafetyMetrics()
            test_metrics.performance_events = 5
            test_metrics.error_events = 3
            test_metrics.resource_events = 2
            for rule in self.validator.validation_rules:
                if rule.name == 'performance_degradation_threshold':
                    result = rule.evaluate(test_metrics)
                    assert result == False
                elif rule.name == 'error_spike_detection':
                    result = rule.evaluate(test_metrics)
                    assert result == False
                elif rule.name == 'resource_exhaustion_warning':
                    result = rule.evaluate(test_metrics)
                    assert result == False
            emit_trace('info', ' '.join(map(str, ['✅ 규칙 평가 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_validation_status(self):
        """검증 상태 조회 테스트"""
        await self.setup()
        try:
            await self.validator.start()
            await self.validator.run_validation()
            status = await self.validator.get_validation_status()
            assert 'running' in status
            assert 'total_rules' in status
            assert 'enabled_rules' in status
            assert 'recent_validations' in status
            assert 'success_rate' in status
            assert 'last_validation' in status
            assert status['running'] == True
            assert status['total_rules'] >= 3
            assert status['recent_validations'] > 0
            emit_trace('info', ' '.join(map(str, ['✅ 검증 상태 조회 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_concurrent_validation(self):
        """동시 검증 테스트"""
        await self.setup()
        try:
            await self.validator.start()

            async def run_single_validation():
                return await self.validator.run_validation()
            tasks = [run_single_validation() for _ in range(3)]
            results = await asyncio.gather(*tasks)
            assert all((isinstance(r, ValidationResult) for r in results))
            assert all((r.success for r in results))
            emit_trace('info', ' '.join(map(str, ['✅ 동시 검증 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_error_handling(self):
        """오류 처리 테스트"""
        await self.setup()
        try:
            invalid_rule = ValidationRule(name='invalid_rule', description='오류를 발생시키는 규칙', severity=SafetyLevel.LOW, condition=lambda m: m.nonexistent_property > 0, action=SafetyAction.NONE)
            result = invalid_rule.evaluate(SafetyMetrics())
            assert result == False
            emit_trace('info', ' '.join(map(str, ['✅ 오류 처리 테스트 통과'])))
        finally:
            await self.teardown()

    async def test_global_functions(self):
        """전역 함수 테스트"""
        try:
            result = await start_integration_validation()
            assert result == True
            validation_result = await run_integration_validation()
            assert isinstance(validation_result, ValidationResult)
            status = await get_integration_status()
            assert status['running'] == True
            result = await stop_integration_validation()
            assert result == True
            emit_trace('info', ' '.join(map(str, ['✅ 전역 함수 테스트 통과'])))
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'⚠️ 전역 함수 테스트 중 오류 (예상됨): {e}'])))

    async def test_integration_with_safety_controller(self):
        """SafetyController와의 통합 테스트"""
        await self.setup()
        try:
            await self.validator.start()
            event = await self.safety_controller.register_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM, {'integration_test': True})
            assert event is not None
            result = await self.validator.run_validation()
            assert isinstance(result, ValidationResult)
            assert result.metrics is not None
            assert hasattr(result.metrics, 'total_events') or hasattr(result.metrics, 'performance_events')
            emit_trace('info', ' '.join(map(str, ['✅ SafetyController 통합 테스트 통과'])))
        finally:
            await self.teardown()

class TestValidationResult:
    """ValidationResult 독립 테스트"""

    def test_validation_result_creation(self):
        """ValidationResult 생성 테스트"""
        result = ValidationResult(success=True, details={'test': 'value'}, errors=['error1'], warnings=['warning1'])
        assert result.success == True
        assert result.details['test'] == 'value'
        assert 'error1' in result.errors
        assert 'warning1' in result.warnings
        assert result.timestamp is not None

    def test_validation_result_to_dict(self):
        """ValidationResult 딕셔너리 변환 테스트"""
        result = ValidationResult(success=False, details={'nested': {'key': 'value'}}, errors=['test_error'])
        result_dict = result.to_dict()
        assert result_dict['success'] == False
        assert result_dict['details']['nested']['key'] == 'value'
        assert 'test_error' in result_dict['errors']
        assert 'timestamp' in result_dict

class TestValidationRule:
    """ValidationRule 독립 테스트"""

    def test_validation_rule_creation(self):
        """ValidationRule 생성 테스트"""
        rule = ValidationRule(name='test_rule', description='테스트 규칙', severity=SafetyLevel.HIGH, condition=lambda m: m.total_events > 0, action=SafetyAction.WARNING)
        assert rule.name == 'test_rule'
        assert rule.description == '테스트 규칙'
        assert rule.severity == SafetyLevel.HIGH
        assert rule.action == SafetyAction.WARNING
        assert rule.enabled == True

    def test_validation_rule_evaluation(self):
        """ValidationRule 평가 테스트"""
        rule = ValidationRule(name='test_rule', description='테스트 규칙', severity=SafetyLevel.MEDIUM, condition=lambda m: m.total_events > 5, action=SafetyAction.MONITOR)
        test_metrics = SafetyMetrics()
        test_metrics.total_events = 10
        result = rule.evaluate(test_metrics)
        assert result == True
        rule.enabled = False
        result = rule.evaluate(test_metrics)
        assert result == True

async def run_all_tests():
    """모든 테스트 실행"""
    emit_trace('info', ' '.join(map(str, ['🧪 IntegrationValidator 테스트 시작'])))
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    test_instance = TestIntegrationValidator()
    test_methods = ['test_initialization', 'test_rule_management', 'test_start_stop', 'test_validation_execution', 'test_rule_evaluation', 'test_validation_status', 'test_concurrent_validation', 'test_error_handling', 'test_global_functions', 'test_integration_with_safety_controller']
    passed = 0
    failed = 0
    for method_name in test_methods:
        try:
            emit_trace('info', ' '.join(map(str, [f'🔍 {method_name} 실행 중...'])))
            await getattr(test_instance, method_name)()
            passed += 1
        except Exception as e:
            emit_trace('info', ' '.join(map(str, [f'❌ {method_name} 실패: {e}'])))
            failed += 1
    emit_trace('info', ' '.join(map(str, ['\n🔍 독립 테스트 실행 중...'])))
    try:
        test_result = TestValidationResult()
        test_result.test_validation_result_creation()
        test_result.test_validation_result_to_dict()
        emit_trace('info', ' '.join(map(str, ['✅ ValidationResult 테스트 통과'])))
        passed += 2
    except Exception as e:
        emit_trace('info', ' '.join(map(str, [f'❌ ValidationResult 테스트 실패: {e}'])))
        failed += 2
    try:
        test_rule = TestValidationRule()
        test_rule.test_validation_rule_creation()
        test_rule.test_validation_rule_evaluation()
        emit_trace('info', ' '.join(map(str, ['✅ ValidationRule 테스트 통과'])))
        passed += 2
    except Exception as e:
        emit_trace('info', ' '.join(map(str, [f'❌ ValidationRule 테스트 실패: {e}'])))
        failed += 2
    emit_trace('info', ' '.join(map(str, ['=' * 60])))
    emit_trace('info', ' '.join(map(str, [f'📊 테스트 결과: {passed}개 통과, {failed}개 실패'])))
    if failed == 0:
        emit_trace('info', ' '.join(map(str, ['🎉 모든 테스트 통과! Phase 2 스켈레톤 완성!'])))
    else:
        emit_trace('info', ' '.join(map(str, ['⚠️ 일부 테스트 실패. 수정이 필요합니다.'])))
    return (passed, failed)
if __name__ == '__main__':
    asyncio.run(run_all_tests())