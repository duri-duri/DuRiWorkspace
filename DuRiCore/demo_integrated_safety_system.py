from DuRiCore.trace import emit_trace
"""
DuRi 통합 안전성 시스템 데모 (T6: 회귀세트 편입)
안전성 프레임워크, 용량 거버넌스, 동등성 검증의 통합 시연
히스테리시스 기반 E-stop 시스템 테스트 포함

@preserve_identity: 기존 기능과 동작 패턴 보존
@evolution_protection: 진화 과정에서의 안전성 확보
@execution_guarantee: 데모를 통한 실행 보장
@existence_ai: 안전한 진화와 회복
@final_execution: 데모가 검증된 최종 실행
@t6_regression: 회귀 테스트 세트 편입
"""
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
import traceback
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
from integrated_safety_system import IntegratedSafetySystem, IntegrationStatus, EmergencyStopTrigger, EmergencyStopPolicy
from capacity_governance import WorkItem, PriorityLevel
logger = logging.getLogger(__name__)

class SafetySystemDemo:
    """안전성 시스템 데모 클래스 (T6: 회귀세트 편입)"""

    def __init__(self):
        self.integrated_system = None
        self.demo_start_time = datetime.now()
        self.demo_results = {'scenarios': [], 'total_scenarios': 0, 'successful_scenarios': 0, 'failed_scenarios': 0, 'start_time': self.demo_start_time.isoformat(), 'end_time': None, 'duration_seconds': 0.0, 't6_regression_tests': [], 'hysteresis_tests': [], 'estop_policy_tests': []}
        try:
            from DuRiCore.state_manager import state_manager
            self.state_manager = state_manager
            self.state_manager.add_state_listener('state_change', self._on_state_change)
            self.collectors_started = False
        except ImportError:
            self.state_manager = None
            self.collectors_started = True

    async def initialize_system(self):
        """시스템 초기화 (T6: 개선된 초기화)"""
        logger.info('=== DuRi 통합 안전성 시스템 초기화 (T6) ===')
        try:
            self.integrated_system = IntegratedSafetySystem()
            logger.info('✅ 통합 안전성 시스템 생성 완료')
            try:
                await self.integrated_system._wait_for_ready_state()
                logger.info('✅ T9: 시스템 READY 상태 대기 완료')
            except Exception as e:
                logger.warning(f'⚠️ T9: READY 상태 대기 실패 (계속 진행): {e}')
            try:
                health_status = await self.integrated_system.health_check()
                logger.info(f"✅ 초기 상태: {health_status['overall_health']}")
            except Exception as e:
                logger.warning(f'⚠️ 초기 상태 점검 실패 (계속 진행): {e}')
                health_status = {'overall_health': 'unknown'}
            emit_trace('info', ' '.join(map(str, [f'\n🔧 시스템 상태: {self.integrated_system.integration_status.value}'])))
            emit_trace('info', ' '.join(map(str, [f'📊 통합 점수: {self.integrated_system.metrics.integration_score:.2%}'])))
            try:
                estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
                emit_trace('info', ' '.join(map(str, [f"🛑 E-stop 정책: {estop_conditions.get('current_policy', 'unknown')}"])))
                logger.info(f"✅ E-stop 조건 확인: {estop_conditions.get('should_trigger', False)}")
            except Exception as e:
                logger.warning(f'⚠️ E-stop 조건 확인 실패 (계속 진행): {e}')
            return True
        except Exception as e:
            logger.error(f'❌ 시스템 초기화 실패: {e}')
            import traceback
            traceback.print_exc()
            return False

    def _on_state_change(self, data: Dict[str, Any]):
        """상태 변경 이벤트 핸들러 (state.ready 대기)"""
        try:
            if data.get('to_state') == 'ready' and (not self.collectors_started):
                logger.info('🎯 StateManager가 READY 상태 - 수집기 시작 준비 완료')
                self.collectors_started = True
                asyncio.create_task(self._start_collectors())
        except Exception as e:
            logger.warning(f'상태 변경 이벤트 처리 실패: {e}')

    async def _start_collectors(self):
        """수집기 시작 (StateManager READY 이후)"""
        try:
            logger.info('🚀 수집기 시작 중...')
            if hasattr(self.integrated_system, 'equivalence_validator'):
                logger.info('✅ 동등성 검증기 초기화 완료')
            if hasattr(self.integrated_system, 'safety_framework'):
                logger.info('✅ 안전성 프레임워크 초기화 완료')
            if hasattr(self.integrated_system, 'capacity_governance'):
                logger.info('✅ 용량 거버넌스 초기화 완료')
            logger.info('🎉 모든 수집기 시작 완료 - 시스템 준비됨')
        except Exception as e:
            logger.error(f'❌ 수집기 시작 실패: {e}')
            self.collectors_started = False

    async def demo_scenario_1_basic_operations(self):
        """시나리오 1: 기본 작업 관리"""
        logger.info('=== 시나리오 1: 기본 작업 관리 ===')
        scenario_result = {'name': '기본 작업 관리', 'description': '작업 항목 추가, 시작, 완료의 기본 워크플로우', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            work_item = WorkItem(id='demo_001', name='데모 작업 1', description='기본 작업 관리 시나리오 테스트', priority_level=PriorityLevel.MEDIUM, estimated_workload=4, risk_score=2, change_impact=3)
            work_item_id = await self.integrated_system.add_work_item(work_item)
            logger.info(f'✅ 작업 항목 추가 완료: {work_item_id}')
            start_success = await self.integrated_system.start_work_item(work_item_id)
            if start_success:
                logger.info('✅ 작업 항목 시작 완료')
            else:
                logger.error('❌ 작업 항목 시작 실패')
                raise Exception('작업 항목 시작 실패')
            complete_success = await self.integrated_system.complete_work_item(work_item_id, actual_workload=3, loc_change=50, file_change=1)
            if complete_success:
                logger.info('✅ 작업 항목 완료 성공')
            else:
                logger.error('❌ 작업 항목 완료 실패')
                raise Exception('작업 항목 완료 실패')
            scenario_result['success'] = True
            scenario_result['details'] = {'work_item_id': work_item_id, 'start_success': start_success, 'complete_success': complete_success}
            logger.info('✅ 시나리오 1 완료')
        except Exception as e:
            logger.error(f'❌ 시나리오 1 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_2_capacity_governance(self):
        """시나리오 2: 용량 거버넌스 테스트"""
        logger.info('=== 시나리오 2: 용량 거버넌스 테스트 ===')
        scenario_result = {'name': '용량 거버넌스 테스트', 'description': 'WIP 한계, LOC 변경량, 파일 변경량 제한 테스트', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            capacity_report = self.integrated_system.capacity_governance.get_capacity_report()
            logger.info(f"📊 현재 WIP: {capacity_report['current_status']['current_wip']}/{capacity_report['current_status']['wip_limit']}")
            logger.info(f"📊 작업량 수준: {capacity_report['current_status']['workload_level']}")
            work_items = []
            for i in range(3):
                work_item = WorkItem(id=f'capacity_demo_{i:03d}', name=f'용량 테스트 작업 {i}', description=f'용량 거버넌스 테스트용 작업 {i}', priority_level=PriorityLevel.LOW, estimated_workload=2, risk_score=1, change_impact=2)
                work_items.append(work_item)
            added_count = 0
            for work_item in work_items:
                try:
                    work_item_id = await self.integrated_system.add_work_item(work_item)
                    logger.info(f'✅ 작업 항목 추가 성공: {work_item_id}')
                    added_count += 1
                except Exception as e:
                    logger.info(f'⚠️ 작업 항목 추가 제한됨: {e}')
                    break
            capacity_limits = self.integrated_system.capacity_governance.check_capacity_limits()
            logger.info(f'📊 용량 한계 상태: {capacity_limits}')
            scenario_result['success'] = True
            scenario_result['details'] = {'initial_capacity': capacity_report, 'added_work_items': added_count, 'capacity_limits': capacity_limits}
            logger.info('✅ 시나리오 2 완료')
        except Exception as e:
            logger.error(f'❌ 시나리오 2 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_3_safety_monitoring(self):
        """시나리오 3: 안전성 모니터링"""
        logger.info('=== 시나리오 3: 안전성 모니터링 ===')
        scenario_result = {'name': '안전성 모니터링', 'description': '실시간 안전성 상태 모니터링 및 체크포인트', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            checkpoints = []
            for i in range(5):
                logger.info(f'🔍 안전성 검사 {i + 1}/5 실행 중...')
                checkpoint = await self.integrated_system.run_integration_check()
                checkpoints.append(checkpoint)
                emit_trace('info', ' '.join(map(str, [f"  📊 검사 {i + 1}: {('✅' if checkpoint.overall_status else '❌')}"])))
                emit_trace('info', ' '.join(map(str, [f"     안전성: {('✅' if checkpoint.safety_framework_check else '❌')}"])))
                emit_trace('info', ' '.join(map(str, [f"     용량: {('✅' if checkpoint.capacity_governance_check else '❌')}"])))
                emit_trace('info', ' '.join(map(str, [f"     동등성: {('✅' if checkpoint.equivalence_validation_check else '❌')}"])))
                await asyncio.sleep(0.5)
            health_status = await self.integrated_system.health_check()
            logger.info(f"📊 전체 상태: {health_status['overall_health']}")
            integration_report = await self.integrated_system.get_integration_report()
            scenario_result['success'] = True
            scenario_result['details'] = {'checkpoints_count': len(checkpoints), 'health_status': health_status['overall_health'], 'integration_score': integration_report['integration_score'], 'safety_score': integration_report['safety_framework']['framework_status']['safety_score'], 'equivalence_score': integration_report['equivalence_validator']['overview']['overall_equivalence_score']}
            logger.info('✅ 시나리오 3 완료')
        except Exception as e:
            logger.error(f'❌ 시나리오 3 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_4_emergency_response(self):
        """시나리오 4: 비상 대응 (T6: 개선된 E-stop)"""
        logger.info('=== 시나리오 4: 비상 대응 (T6) ===')
        scenario_result = {'name': '비상 대응 (T6)', 'description': '히스테리시스 기반 비상 정지 및 복구 시나리오', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            logger.info('🛑 히스테리시스 E-stop 테스트 중...')
            await self.integrated_system.emergency_stop(trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION, severity=0.3, details={'test_type': 'hysteresis_test', 'violation_level': 'minor'})
            estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
            logger.info(f"🛑 E-stop 조건: {estop_conditions['should_trigger']}")
            health_status = await self.integrated_system.health_check()
            logger.info(f"📊 E-stop 후 상태: {health_status['overall_health']}")
            scenario_result['success'] = True
            scenario_result['details'] = {'estop_conditions': estop_conditions, 'health_status': health_status['overall_health'], 'emergency_stops_count': self.integrated_system.metrics.emergency_stops, 'hysteresis_status': estop_conditions['hysteresis_status']}
            logger.info('✅ 시나리오 4 완료 (T6)')
        except Exception as e:
            logger.error(f'❌ 시나리오 4 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_5_hysteresis_test(self):
        """시나리오 5: 히스테리시스 테스트 (T6)"""
        logger.info('=== 시나리오 5: 히스테리시스 테스트 (T6) ===')
        scenario_result = {'name': '히스테리시스 테스트 (T6)', 'description': '연속 위반에 따른 히스테리시스 E-stop 트리거 테스트', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            logger.info('🔄 연속 위반 시뮬레이션 중...')
            violations = []
            for i in range(3):
                violation = await self.integrated_system.emergency_stop(trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION, severity=0.4 + i * 0.1, details={'test_type': 'hysteresis_sequence', 'violation_number': i + 1, 'total_violations': 3})
                violations.append(violation)
                await asyncio.sleep(0.1)
            estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
            hysteresis_triggered = estop_conditions['should_trigger']
            scenario_result['success'] = True
            scenario_result['details'] = {'violations_count': len(violations), 'hysteresis_triggered': hysteresis_triggered, 'estop_conditions': estop_conditions, 'hysteresis_windows': estop_conditions['hysteresis_status']}
            self.demo_results['hysteresis_tests'].append({'test_name': '연속 위반 히스테리시스', 'violations_count': len(violations), 'triggered': hysteresis_triggered, 'timestamp': datetime.now().isoformat()})
            logger.info(f'✅ 시나리오 5 완료 (T6): 히스테리시스 트리거 = {hysteresis_triggered}')
        except Exception as e:
            logger.error(f'❌ 시나리오 5 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_6_estop_policy_test(self):
        """시나리오 6: E-stop 정책 테스트 (T6)"""
        logger.info('=== 시나리오 6: E-stop 정책 테스트 (T6) ===')
        scenario_result = {'name': 'E-stop 정책 테스트 (T6)', 'description': '다양한 E-stop 정책 (즉시/점진적/히스테리시스) 테스트', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            logger.info('🚨 즉시 E-stop 테스트 중...')
            await self.integrated_system.emergency_stop(trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION, severity=0.95, details={'test_type': 'immediate_estop', 'violation_level': 'severe'})
            logger.info('⚠️ 점진적 격리 테스트 중...')
            await self.integrated_system.emergency_stop(trigger=EmergencyStopTrigger.OBSERVABILITY_MISSING, severity=0.6, details={'test_type': 'gradual_isolation', 'missing_type': 'observability'})
            estop_history = self.integrated_system.get_emergency_stop_history()
            policy_results = {}
            for record in estop_history[-3:]:
                policy_results[record['trigger']] = {'policy': record['policy'], 'severity': record['severity']}
            scenario_result['success'] = True
            scenario_result['details'] = {'estop_history': estop_history, 'policy_results': policy_results, 'total_estops': len(estop_history)}
            self.demo_results['estop_policy_tests'].append({'test_name': '다양한 E-stop 정책', 'policies_tested': list(policy_results.keys()), 'total_estops': len(estop_history), 'timestamp': datetime.now().isoformat()})
            logger.info('✅ 시나리오 6 완료 (T6)')
        except Exception as e:
            logger.error(f'❌ 시나리오 6 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_7_regression_test(self):
        """시나리오 7: 회귀 테스트 (T6)"""
        logger.info('=== 시나리오 7: 회귀 테스트 (T6) ===')
        scenario_result = {'name': '회귀 테스트 (T6)', 'description': '기존 기능의 회귀 방지 및 안정성 검증', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            if self.integrated_system.integration_status.value == 'emergency_stop':
                logger.info('🔄 T10: E-stop 상태에서 시스템 복구 시도...')
                recovery_success = await self.integrated_system.recover_from_emergency_stop('시나리오 7 회귀 테스트')
                if not recovery_success:
                    logger.warning('⚠️ T10: 시스템 복구 실패 - 웜업 윈도우 대기 중')
                    await asyncio.sleep(2.0)
                    recovery_success = await self.integrated_system.recover_from_emergency_stop('시나리오 7 회귀 테스트 재시도')
                if recovery_success:
                    logger.info('✅ T10: 시스템 복구 완료 - 회귀 테스트 진행')
                else:
                    logger.error('❌ T10: 시스템 복구 실패 - 회귀 테스트 중단')
                    scenario_result['details']['error'] = '시스템 복구 실패'
                    return
            logger.info('⏳ READY 상태 확인 중...')
            max_wait_time = 5.0
            wait_start = time.time()
            while self.integrated_system.integration_status != IntegrationStatus.READY:
                if time.time() - wait_start > max_wait_time:
                    logger.warning('⚠️ READY 상태 대기 시간 초과, 계속 진행')
                    break
                await asyncio.sleep(0.1)
            logger.info('🔄 기본 기능 회귀 테스트 중...')
            checkpoint = await self.integrated_system.run_integration_check()
            state_status = self.integrated_system.state_manager.current_state
            capacity_status = self.integrated_system.capacity_governance.check_capacity_limits()
            logger.info(f'🔍 용량 거버넌스 상태: {capacity_status}')
            equivalence_status = self.integrated_system.equivalence_validator.get_equivalence_report()
            integration_ok = checkpoint.overall_status
            state_ok = state_status.value.lower() == 'ready'
            capacity_ok = all(capacity_status.values())
            equivalence_ok = equivalence_status['overview'].get('overall_equivalence_score', 0) >= 0.995
            logger.info(f'🔍 회귀 테스트 상세 결과:')
            logger.info(f'  - 통합 검사: {integration_ok}')
            logger.info(f'  - 상태 매니저: {state_ok} ({state_status.value})')
            logger.info(f'  - 용량 거버넌스: {capacity_ok} ({capacity_status})')
            logger.info(f"  - 동등성 검증: {equivalence_ok} ({equivalence_status['overview'].get('overall_equivalence_score', 0)})")
            regression_passed = all([integration_ok, state_ok, capacity_ok, equivalence_ok])
            scenario_result['success'] = regression_passed
            scenario_result['details'] = {'integration_check': checkpoint.overall_status, 'state_manager': state_status.value, 'capacity_governance': all(capacity_status.values()), 'equivalence_validation': equivalence_status['overview'].get('overall_equivalence_score', 0) >= 0.995, 'regression_passed': regression_passed}
            self.demo_results['t6_regression_tests'].append({'test_name': '기본 기능 회귀', 'passed': regression_passed, 'components_tested': ['integration', 'state_manager', 'capacity', 'equivalence'], 'timestamp': datetime.now().isoformat()})
            logger.info(f"✅ 시나리오 7 완료 (T6): 회귀 테스트 {('통과' if regression_passed else '실패')}")
        except Exception as e:
            logger.error(f'❌ 시나리오 7 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def demo_scenario_8_integration_validation(self):
        """시나리오 8: 통합 검증 (T6)"""
        logger.info('=== 시나리오 8: 통합 검증 (T6) ===')
        scenario_result = {'name': '통합 검증 (T6)', 'description': '전체 시스템의 통합 상태 및 성능 검증', 'success': False, 'details': {}, 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
        try:
            if self.integrated_system.integration_status.value == 'emergency_stop':
                logger.info('🔄 T10: E-stop 상태에서 시스템 복구 시도...')
                recovery_success = await self.integrated_system.recover_from_emergency_stop('시나리오 8 통합 검증')
                if not recovery_success:
                    logger.warning('⚠️ T10: 시스템 복구 실패 - 웜업 윈도우 대기 중')
                    await asyncio.sleep(2.0)
                    recovery_success = await self.integrated_system.recover_from_emergency_stop('시나리오 8 통합 검증 재시도')
                if recovery_success:
                    logger.info('✅ T10: 시스템 복구 완료 - 통합 검증 진행')
                else:
                    logger.error('❌ T10: 시스템 복구 실패 - 통합 검증 중단')
                    scenario_result['details']['error'] = '시스템 복구 실패'
                    return
            logger.info('⏳ READY 상태 확인 중...')
            max_wait_time = 5.0
            wait_start = time.time()
            while self.integrated_system.integration_status != IntegrationStatus.READY:
                if time.time() - wait_start > max_wait_time:
                    logger.warning('⚠️ READY 상태 대기 시간 초과, 계속 진행')
                    break
                await asyncio.sleep(0.1)
            logger.info('🔍 전체 시스템 상태 점검 중...')
            health_status = await self.integrated_system.health_check()
            estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
            integration_report = await self.integrated_system.get_integration_report()
            performance_metrics = {'uptime': self.integrated_system.metrics.uptime_seconds, 'integration_score': self.integrated_system.metrics.integration_score, 'checkpoints_passed': self.integrated_system.metrics.passed_checkpoints, 'emergency_stops': self.integrated_system.metrics.emergency_stops}
            validation_criteria = {'health_ok': health_status['overall_health'] == 'healthy', 'no_estop': not estop_conditions['should_trigger'], 'integration_score_ok': self.integrated_system.metrics.integration_score > 0.95, 'system_ready': self.integrated_system.integration_status == IntegrationStatus.READY}
            integration_passed = all(validation_criteria.values())
            scenario_result['success'] = integration_passed
            scenario_result['details'] = {'health_status': health_status, 'estop_conditions': estop_conditions, 'performance_metrics': performance_metrics, 'validation_criteria': validation_criteria, 'integration_passed': integration_passed}
            self.demo_results['t6_regression_tests'].append({'test_name': '통합 검증', 'passed': integration_passed, 'criteria_met': sum(validation_criteria.values()), 'total_criteria': len(validation_criteria), 'timestamp': datetime.now().isoformat()})
            logger.info(f"✅ 시나리오 8 완료 (T6): 통합 검증 {('통과' if integration_passed else '실패')}")
        except Exception as e:
            logger.error(f'❌ 시나리오 8 실패: {e}')
            scenario_result['details']['error'] = str(e)
        finally:
            scenario_result['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result['start_time'])
            end_time = datetime.fromisoformat(scenario_result['end_time'])
            scenario_result['duration_seconds'] = (end_time - start_time).total_seconds()
            self.demo_results['scenarios'].append(scenario_result)
            self.demo_results['total_scenarios'] += 1
            if scenario_result['success']:
                self.demo_results['successful_scenarios'] += 1
            else:
                self.demo_results['failed_scenarios'] += 1

    async def run_demo(self):
        """전체 데모 실행 - T9: READY 게이트를 시나리오 앞에 배치"""
        logger.info('🚀 DuRi 통합 안전성 시스템 데모 시작')
        try:
            if not await self.initialize_system():
                logger.error('❌ 시스템 초기화 실패로 데모를 중단합니다')
                return False
            logger.info('⏳ T9: READY 게이트 대기 중...')
            ready_wait_start = time.time()
            if self.state_manager:
                max_wait_time = 10.0
                while self.state_manager.current_state.value != 'ready':
                    if time.time() - ready_wait_start > max_wait_time:
                        logger.warning('⚠️ T9: READY 상태 대기 시간 초과, 계속 진행')
                        break
                    await asyncio.sleep(0.1)
                ready_wait_duration = time.time() - ready_wait_start
                logger.info(f'✅ T9: READY 게이트 통과 완료 (대기 시간: {ready_wait_duration:.2f}초)')
            else:
                logger.info('ℹ️ T9: StateManager 없음, READY 게이트 건너뜀')
            logger.info('🎯 T9: READY 게이트 완료, 시나리오 실행 시작')
            await self.demo_scenario_1_basic_operations()
            await self.demo_scenario_2_capacity_governance()
            await self.demo_scenario_3_safety_monitoring()
            await self.demo_scenario_4_emergency_response()
            await self.demo_scenario_5_hysteresis_test()
            await self.demo_scenario_6_estop_policy_test()
            await self.demo_scenario_7_regression_test()
            await self.demo_scenario_8_integration_validation()
            self.demo_results['end_time'] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(self.demo_results['start_time'])
            end_time = datetime.fromisoformat(self.demo_results['end_time'])
            self.demo_results['duration_seconds'] = (end_time - start_time).total_seconds()
            self._print_demo_results()
            self._save_demo_results()
            logger.info('🎉 DuRi 통합 안전성 시스템 데모 완료')
            return True
        except Exception as e:
            logger.error(f'❌ 데모 실행 중 오류 발생: {e}')
            traceback.print_exc()
            return False

    def _print_demo_results(self):
        """데모 결과 출력"""
        emit_trace('info', ' '.join(map(str, ['\n' + '=' * 60])))
        emit_trace('info', ' '.join(map(str, ['🎯 DuRi 통합 안전성 시스템 데모 결과'])))
        emit_trace('info', ' '.join(map(str, ['=' * 60])))
        emit_trace('info', ' '.join(map(str, [f'\n📊 전체 요약:'])))
        emit_trace('info', ' '.join(map(str, [f"   총 시나리오: {self.demo_results['total_scenarios']}"])))
        emit_trace('info', ' '.join(map(str, [f"   성공: {self.demo_results['successful_scenarios']}"])))
        emit_trace('info', ' '.join(map(str, [f"   실패: {self.demo_results['failed_scenarios']}"])))
        emit_trace('info', ' '.join(map(str, [f"   소요 시간: {self.demo_results['duration_seconds']:.2f}초"])))
        emit_trace('info', ' '.join(map(str, [f'\n📋 시나리오별 결과:'])))
        for (i, scenario) in enumerate(self.demo_results['scenarios'], 1):
            status_icon = '✅' if scenario['success'] else '❌'
            emit_trace('info', ' '.join(map(str, [f"   {i}. {status_icon} {scenario['name']}"])))
            emit_trace('info', ' '.join(map(str, [f"      소요 시간: {scenario['duration_seconds']:.2f}초"])))
            if not scenario['success'] and 'error' in scenario['details']:
                emit_trace('info', ' '.join(map(str, [f"      오류: {scenario['details']['error']}"])))
        emit_trace('info', ' '.join(map(str, [f"\n🏆 성공률: {self.demo_results['successful_scenarios'] / self.demo_results['total_scenarios'] * 100:.1f}%"])))

    def _save_demo_results(self):
        """데모 결과를 JSON 파일로 저장"""
        try:
            results_file = f"demo_results_integrated_safety_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.demo_results, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f'📁 데모 결과가 {results_file}에 저장되었습니다')
        except Exception as e:
            logger.error(f'❌ 데모 결과 저장 실패: {e}')

async def main():
    """메인 함수"""
    emit_trace('info', ' '.join(map(str, ['🚀 DuRi 통합 안전성 시스템 데모를 시작합니다...'])))
    emit_trace('info', ' '.join(map(str, ['이 데모는 다음 기능들을 시연합니다:'])))
    emit_trace('info', ' '.join(map(str, ['  • 안전성 프레임워크'])))
    emit_trace('info', ' '.join(map(str, ['  • 용량 거버넌스 시스템'])))
    emit_trace('info', ' '.join(map(str, ['  • 동등성 검증 시스템'])))
    emit_trace('info', ' '.join(map(str, ['  • 통합 안전성 관리'])))
    emit_trace('info', ' '.join(map(str, [])))
    demo = SafetySystemDemo()
    success = await demo.run_demo()
    if success:
        emit_trace('info', ' '.join(map(str, ['\n🎉 데모가 성공적으로 완료되었습니다!'])))
    else:
        emit_trace('info', ' '.join(map(str, ['\n❌ 데모 실행 중 문제가 발생했습니다.'])))
    return success
if __name__ == '__main__':
    asyncio.run(main())