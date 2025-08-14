from DuRiCore.trace import emit_trace
"""
DuRi 통합 안전성 검증 스모크 테스트 - Phase 2 검증
SafetyController와 IntegrationValidator의 실제 연결 흐름 검증

@preserve_identity: 기존 SafetyController와의 호환성 실시간 검증
@evolution_protection: 진화 과정에서의 통합 안전성 실시간 검증
@execution_guarantee: 통합된 검증 보장 실시간 검증
@existence_ai: 안전한 진화와 회복을 위한 통합 검증 실시간 검증
@final_execution: 통합 안전성이 보장된 최종 실행 실시간 검증
"""
import asyncio
import json
import time
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional
import logging
try:
    from DuRiCore.safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, safety_controller, register_safety_event, get_safety_metrics, get_safety_health
    from DuRiCore.integration_validator import IntegrationValidator, ValidationResult, ValidationRule, integration_validator, start_integration_validation, stop_integration_validation, run_integration_validation, get_integration_status
except ImportError:
    from safety_controller import SafetyController, SafetyLevel, SafetyTrigger, SafetyAction, SafetyEvent, safety_controller, register_safety_event, get_safety_metrics, get_safety_health
    from integration_validator import IntegrationValidator, ValidationResult, ValidationRule, integration_validator, start_integration_validation, stop_integration_validation, run_integration_validation, get_integration_status
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SmokeValidationFlow:
    """통합 안전성 검증 스모크 테스트"""

    def __init__(self):
        """스모크 테스트 초기화"""
        self.safety_controller = None
        self.integration_validator = None
        self.test_results = []
        logger.info('🚬 통합 안전성 검증 스모크 테스트 초기화')

    async def setup(self):
        """테스트 환경 설정"""
        logger.info('🔧 테스트 환경 설정 시작')
        self.safety_controller = SafetyController()
        await self.safety_controller.start()
        self.integration_validator = IntegrationValidator(self.safety_controller)
        await self.integration_validator.start()
        logger.info('✅ 테스트 환경 설정 완료')

    async def teardown(self):
        """테스트 환경 정리"""
        logger.info('🧹 테스트 환경 정리 시작')
        if self.integration_validator:
            await self.integration_validator.stop()
            await self.integration_validator.reset()
        if self.safety_controller:
            await self.safety_controller.stop()
            await self.safety_controller.reset()
        logger.info('✅ 테스트 환경 정리 완료')

    async def test_basic_integration(self):
        """기본 통합 테스트"""
        logger.info('🔍 기본 통합 테스트 시작')
        try:
            assert self.safety_controller._running == True
            assert self.integration_validator._running == True
            metrics = await self.safety_controller.get_metrics()
            assert metrics.total_events == 0
            status = await self.integration_validator.get_validation_status()
            assert status['running'] == True
            assert status['total_rules'] >= 3
            logger.info('✅ 기본 통합 테스트 통과')
            return True
        except Exception as e:
            logger.error(f'❌ 기본 통합 테스트 실패: {e}')
            return False

    async def test_event_flow(self):
        """이벤트 흐름 테스트"""
        logger.info('🔔 이벤트 흐름 테스트 시작')
        try:
            event1 = await self.safety_controller.register_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.MEDIUM, {'smoke_test': True, 'step': 1})
            assert event1 is not None
            event2 = await self.safety_controller.register_event(SafetyTrigger.ERROR_SPIKE, SafetyLevel.HIGH, {'smoke_test': True, 'step': 2})
            assert event2 is not None
            metrics = await self.safety_controller.get_metrics()
            assert metrics.total_events == 2
            assert metrics.high_events == 1
            assert metrics.medium_events == 1
            validation_result = await self.integration_validator.run_validation()
            assert isinstance(validation_result, ValidationResult)
            updated_metrics = await self.safety_controller.get_metrics()
            assert updated_metrics.total_events >= 2
            logger.info('✅ 이벤트 흐름 테스트 통과')
            return True
        except Exception as e:
            logger.error(f'❌ 이벤트 흐름 테스트 실패: {e}')
            return False

    async def test_validation_rules(self):
        """검증 규칙 테스트"""
        logger.info('📋 검증 규칙 테스트 시작')
        try:
            custom_rule = ValidationRule(name='smoke_test_rule', description='스모크 테스트용 커스텀 규칙', severity=SafetyLevel.CRITICAL, condition=lambda m: m.total_events > 1, action=SafetyAction.EMERGENCY_STOP)
            self.integration_validator.add_rule(custom_rule)
            assert len(self.integration_validator.validation_rules) == 4
            test_metrics = await self.safety_controller.get_metrics()
            rule_result = custom_rule.evaluate(test_metrics)
            assert rule_result == False
            validation_result = await self.integration_validator.run_validation()
            assert validation_result.success == False
            self.integration_validator.remove_rule('smoke_test_rule')
            assert len(self.integration_validator.validation_rules) == 3
            logger.info('✅ 검증 규칙 테스트 통과')
            return True
        except Exception as e:
            logger.error(f'❌ 검증 규칙 테스트 실패: {e}')
            return False

    async def test_concurrent_operations(self):
        """동시 작업 테스트"""
        logger.info('⚡ 동시 작업 테스트 시작')
        try:

            async def register_event(trigger: SafetyTrigger, level: SafetyLevel, details: Dict):
                return await self.safety_controller.register_event(trigger, level, details)
            tasks = [register_event(SafetyTrigger.MEMORY_LEAK, SafetyLevel.LOW, {'concurrent': True, 'id': 1}), register_event(SafetyTrigger.BEHAVIOR_ANOMALY, SafetyLevel.MEDIUM, {'concurrent': True, 'id': 2}), register_event(SafetyTrigger.RESOURCE_EXHAUSTION, SafetyLevel.HIGH, {'concurrent': True, 'id': 3})]
            results = await asyncio.gather(*tasks)
            assert all((result is not None for result in results))

            async def run_validation():
                return await self.integration_validator.run_validation()
            validation_tasks = [run_validation() for _ in range(3)]
            validation_results = await asyncio.gather(*validation_tasks)
            assert all((isinstance(r, ValidationResult) for r in validation_results))
            final_metrics = await self.safety_controller.get_metrics()
            assert final_metrics.total_events >= 6
            logger.info('✅ 동시 작업 테스트 통과')
            return True
        except Exception as e:
            logger.error(f'❌ 동시 작업 테스트 실패: {e}')
            return False

    async def test_global_functions(self):
        """전역 함수 테스트"""
        logger.info('🌐 전역 함수 테스트 시작')
        try:
            global_event = await register_safety_event(SafetyTrigger.PERFORMANCE_DEGRADATION, SafetyLevel.LOW, {'global_test': True})
            assert global_event is not None
            global_metrics = await get_safety_metrics()
            assert global_metrics.total_events > 0
            global_health = await get_safety_health()
            assert 'status' in global_health
            global_status = await get_integration_status()
            assert 'running' in global_status
            logger.info('✅ 전역 함수 테스트 통과')
            return True
        except Exception as e:
            logger.error(f'❌ 전역 함수 테스트 실패: {e}')
            return False

    async def test_error_recovery(self):
        """오류 복구 테스트"""
        logger.info('🔄 오류 복구 테스트 시작')
        try:
            result = await self.safety_controller.resolve_event('invalid_event_id')
            assert result == False
            await self.integration_validator.stop()
            await self.integration_validator.start()
            assert self.integration_validator._running == True
            validation_result = await self.integration_validator.run_validation()
            assert isinstance(validation_result, ValidationResult)
            logger.info('✅ 오류 복구 테스트 통과')
            return True
        except Exception as e:
            logger.error(f'❌ 오류 복구 테스트 실패: {e}')
            return False

    async def run_all_tests(self):
        """모든 스모크 테스트 실행"""
        logger.info('🚬 통합 안전성 검증 스모크 테스트 시작')
        emit_trace('info', ' '.join(map(str, ['=' * 80])))
        try:
            await self.setup()
            tests = [('기본 통합', self.test_basic_integration), ('이벤트 흐름', self.test_event_flow), ('검증 규칙', self.test_validation_rules), ('동시 작업', self.test_concurrent_operations), ('전역 함수', self.test_global_functions), ('오류 복구', self.test_error_recovery)]
            passed = 0
            failed = 0
            for (test_name, test_func) in tests:
                emit_trace('info', ' '.join(map(str, [f'🔍 {test_name} 테스트 실행 중...'])))
                try:
                    result = await test_func()
                    if result:
                        emit_trace('info', ' '.join(map(str, [f'✅ {test_name} 테스트 통과'])))
                        passed += 1
                    else:
                        emit_trace('info', ' '.join(map(str, [f'❌ {test_name} 테스트 실패'])))
                        failed += 1
                except Exception as e:
                    emit_trace('info', ' '.join(map(str, [f'❌ {test_name} 테스트 오류: {e}'])))
                    failed += 1
                await asyncio.sleep(1)
            emit_trace('info', ' '.join(map(str, ['=' * 80])))
            emit_trace('info', ' '.join(map(str, [f'📊 스모크 테스트 결과: {passed}개 통과, {failed}개 실패'])))
            if failed == 0:
                emit_trace('info', ' '.join(map(str, ['🎉 모든 스모크 테스트 통과! Phase 1+2 완벽 통합!'])))
                emit_trace('info', ' '.join(map(str, ['🚀 SafetyController + IntegrationValidator 연결 성공!'])))
            else:
                emit_trace('info', ' '.join(map(str, ['⚠️ 일부 스모크 테스트 실패. 통합 검증이 필요합니다.'])))
            return (passed, failed)
        finally:
            await self.teardown()

async def main():
    """메인 실행 함수"""
    smoke_test = SmokeValidationFlow()
    await smoke_test.run_all_tests()
if __name__ == '__main__':
    asyncio.run(main())