from DuRiCore.trace import emit_trace
"""
CI 파이프라인용 회귀 테스트 스크립트
8개 시나리오 자동 실행 + 3초 가드 + 스모크 검증
"""
import asyncio
import time
import json
import logging
from typing import Dict, Any, List
from pathlib import Path
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CIRegressionTest:
    """CI 회귀 테스트 실행기"""

    def __init__(self):
        self.test_results = []
        self.start_time = None
        self.max_execution_time = 3.0

    async def run_smoke_tests(self) -> Dict[str, bool]:
        """스모크 테스트 실행 (3줄 검증)"""
        logger.info('🔍 스모크 테스트 시작...')
        smoke_results = {'boot_snapshot_ok': False, 'initializing_to_ready': False, 'ssot_routing_confirmed': False}
        try:
            from integrated_safety_system import IntegratedSafetySystem
            system = IntegratedSafetySystem()
            smoke_results['boot_snapshot_ok'] = True
            logger.info('✅ 1/3: 부팅 스냅샷 OK')
            await system.initialize()
            await system._wait_for_ready_state()
            if system.integration_status.value.lower() == 'ready':
                smoke_results['initializing_to_ready'] = True
                logger.info('✅ 2/3: initializing → ready 전환 OK')
            if hasattr(system, 'state_manager') and system.state_manager:
                smoke_results['ssot_routing_confirmed'] = True
                logger.info('✅ 3/3: SSOT 라우팅 확인 OK')
        except Exception as e:
            logger.error(f'❌ 스모크 테스트 실패: {e}')
        return smoke_results

    async def run_regression_tests(self) -> List[Dict[str, Any]]:
        """8개 시나리오 회귀 테스트 실행"""
        logger.info('🚀 회귀 테스트 시작 (8개 시나리오)')
        from demo_integrated_safety_system import DuRiIntegratedSafetyDemo
        demo = DuRiIntegratedSafetyDemo()
        await demo.initialize_system()
        scenarios = [('시나리오 1: 시스템 초기화', demo.demo_scenario_1_initialization), ('시나리오 2: 용량 거버넌스', demo.demo_scenario_2_capacity_governance), ('시나리오 3: 안전성 프레임워크', demo.demo_scenario_3_safety_framework), ('시나리오 4: 동등성 검증', demo.demo_scenario_4_equivalence_validation), ('시나리오 5: 통합 안전성 검사', demo.demo_scenario_5_integration_safety_check), ('시나리오 6: E-stop 시뮬레이션', demo.demo_scenario_6_emergency_stop_simulation), ('시나리오 7: 회귀 테스트', demo.demo_scenario_7_regression_test), ('시나리오 8: 최종 통합 검증', demo.demo_scenario_8_final_integration_verification)]
        results = []
        for (name, scenario_func) in scenarios:
            logger.info(f'📋 {name} 실행 중...')
            start_time = time.time()
            try:
                result = await scenario_func()
                execution_time = time.time() - start_time
                test_result = {'scenario': name, 'success': result.get('success', False), 'execution_time': execution_time, 'details': result.get('details', ''), 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')}
                if test_result['success']:
                    logger.info(f'✅ {name}: 성공 ({execution_time:.2f}s)')
                else:
                    logger.error(f'❌ {name}: 실패 ({execution_time:.2f}s)')
                results.append(test_result)
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(f'💥 {name}: 예외 발생 ({execution_time:.2f}s) - {e}')
                results.append({'scenario': name, 'success': False, 'execution_time': execution_time, 'details': f'예외: {str(e)}', 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')})
        return results

    async def run_all_tests(self) -> Dict[str, Any]:
        """전체 테스트 실행"""
        self.start_time = time.time()
        logger.info('🎯 CI 회귀 테스트 시작')
        smoke_results = await self.run_smoke_tests()
        regression_results = await self.run_regression_tests()
        total_time = time.time() - self.start_time
        passed_scenarios = sum((1 for r in regression_results if r['success']))
        total_scenarios = len(regression_results)
        if total_time > self.max_execution_time:
            logger.error(f'⏰ 실행 시간 초과: {total_time:.2f}s > {self.max_execution_time}s')
            overall_success = False
        else:
            overall_success = passed_scenarios == total_scenarios
            logger.info(f'⏱️ 실행 시간: {total_time:.2f}s (가드: {self.max_execution_time}s)')
        final_result = {'overall_success': overall_success, 'execution_time': total_time, 'scenarios': {'total': total_scenarios, 'passed': passed_scenarios, 'failed': total_scenarios - passed_scenarios, 'success_rate': f'{passed_scenarios / total_scenarios * 100:.1f}%'}, 'smoke_tests': smoke_results, 'regression_tests': regression_results, 'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'), 'ci_gate': {'time_guard_passed': total_time <= self.max_execution_time, 'all_scenarios_passed': passed_scenarios == total_scenarios, 'smoke_tests_passed': all(smoke_results.values())}}
        return final_result

    def save_results(self, results: Dict[str, Any], filename: str=None):
        """테스트 결과 저장"""
        if filename is None:
            timestamp = time.strftime('%Y%m%d_%H%M%S')
            filename = f'ci_regression_results_{timestamp}.json'
        output_path = Path(filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        logger.info(f'💾 결과 저장: {output_path}')
        return output_path

async def main():
    """메인 실행 함수"""
    ci_test = CIRegressionTest()
    try:
        results = await ci_test.run_all_tests()
        emit_trace('info', ' '.join(map(str, ['\n' + '=' * 60])))
        emit_trace('info', ' '.join(map(str, ['🎯 CI 회귀 테스트 결과'])))
        emit_trace('info', ' '.join(map(str, ['=' * 60])))
        emit_trace('info', ' '.join(map(str, [f"📊 전체 성공: {('✅' if results['overall_success'] else '❌')}"])))
        emit_trace('info', ' '.join(map(str, [f"⏱️ 실행 시간: {results['execution_time']:.2f}s"])))
        emit_trace('info', ' '.join(map(str, [f"📋 시나리오: {results['scenarios']['passed']}/{results['scenarios']['total']} 통과"])))
        emit_trace('info', ' '.join(map(str, [f"📈 성공률: {results['scenarios']['success_rate']}"])))
        emit_trace('info', ' '.join(map(str, [f"🔒 CI 게이트: {('✅ 통과' if results['ci_gate']['time_guard_passed'] and results['ci_gate']['all_scenarios_passed'] else '❌ 차단')}"])))
        emit_trace('info', ' '.join(map(str, ['\n🔍 스모크 테스트:'])))
        for (test, passed) in results['smoke_tests'].items():
            status = '✅' if passed else '❌'
            emit_trace('info', ' '.join(map(str, [f'  {status} {test}'])))
        output_file = ci_test.save_results(results)
        if results['overall_success']:
            emit_trace('info', ' '.join(map(str, [f'\n🎉 CI 게이트 통과! 결과 파일: {output_file}'])))
            exit(0)
        else:
            emit_trace('info', ' '.join(map(str, [f'\n💥 CI 게이트 차단! 결과 파일: {output_file}'])))
            exit(1)
    except Exception as e:
        logger.error(f'💥 CI 테스트 실행 실패: {e}')
        exit(1)
if __name__ == '__main__':
    asyncio.run(main())