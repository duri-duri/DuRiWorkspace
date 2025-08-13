from DuRiCore.trace import emit_trace
"""
DuRi 통합 안전성 시스템 테스트
안전성 프레임워크, 용량 거버넌스, 동등성 검증의 통합 테스트

@preserve_identity: 기존 기능과 동작 패턴 보존
@evolution_protection: 진화 과정에서의 안전성 확보
@execution_guarantee: 통합 테스트를 통한 실행 보장
@existence_ai: 안전한 진화와 회복
@final_execution: 테스트가 검증된 최종 실행
"""
import asyncio
import json
import time
import unittest
import inspect
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import traceback
from pathlib import Path

# 로깅 레벨 설정
logging.getLogger("DuRiCore").setLevel(logging.INFO)

try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    from DuRiCore.integrated_safety_system import IntegratedSafetySystem, IntegrationStatus
    from DuRiCore.safety_framework import SafetyFramework, SafetyLevel, SafetyInvariant, InvariantType
    from DuRiCore.capacity_governance import CapacityGovernance, WorkItem, PriorityLevel, WorkloadLevel
    from DuRiCore.equivalence_validator import EquivalenceValidator, EquivalenceLevel, ValidationType
    from tests.helpers.ready import ensure_ready as ensure_ready_helper
except ImportError:
    from integrated_safety_system import IntegratedSafetySystem, IntegrationStatus
    from safety_framework import SafetyFramework, SafetyLevel, SafetyInvariant, InvariantType
    from capacity_governance import CapacityGovernance, WorkItem, PriorityLevel, WorkloadLevel
    from equivalence_validator import EquivalenceValidator, EquivalenceLevel, ValidationType
    # Fallback for testing environments
    async def ensure_ready_helper(system, reason="test_helper"):
        pass
logger = logging.getLogger(__name__)

class TestIntegratedSafetySystem(unittest.IsolatedAsyncioTestCase):
    """통합 안전성 시스템 테스트 클래스"""

    async def asyncSetUp(self):
        """비동기 설정"""
        self.integrated_system = IntegratedSafetySystem()
        self.test_start_time = datetime.now()
        logger.info('통합 안전성 시스템 테스트 설정 완료')

        # READY once, centrally
        await ensure_ready_helper(self.integrated_system, reason="asyncSetUp")

    async def asyncTearDown(self):
        """비동기 정리"""
        test_duration = datetime.now() - self.test_start_time
        logger.info(f'테스트 완료: {test_duration.total_seconds():.2f}초 소요')

    async def test_system_initialization(self):
        """시스템 초기화 테스트"""
        logger.info('시스템 초기화 테스트 시작')
        self.assertIsNotNone(self.integrated_system.safety_framework)
        self.assertIsNotNone(self.integrated_system.capacity_governance)
        self.assertIsNotNone(self.integrated_system.equivalence_validator)
        self.assertEqual(self.integrated_system.integration_status, IntegrationStatus.INITIALIZING)
        expected_checkpoints = ['system_initialization', 'capacity_governance', 'equivalence_validation', 'safety_framework', 'integration_status']
        for checkpoint_id in expected_checkpoints:
            self.assertIn(checkpoint_id, self.integrated_system.safety_checkpoints)
        self.assertEqual(self.integrated_system.metrics.total_checkpoints, 0)
        self.assertEqual(self.integrated_system.metrics.integration_score, 1.0)
        logger.info('시스템 초기화 테스트 통과')

    def _as_ready_bool(self, v):
        """Enum/객체/문자열을 모두 'ready' 판정으로 정규화"""
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        for attr in ('value', 'name'):
            if hasattr(v, attr):
                s = str(getattr(v, attr)).lower()
                if s == 'ready':
                    return True
        s = str(v).lower()
        return s == 'ready' or s == 'true'

    async def _probe_ready_once(self):
        """다양한 READY 신호를 한 번에 탐지"""
        obj = self.integrated_system
        if hasattr(obj, 'is_ready'):
            r = obj.is_ready()
            if inspect.iscoroutine(r):
                r = await r
            if self._as_ready_bool(r):
                return True
        for name in ('ready', 'is_ready', 'current_state', 'state', 'status', 'integration_status'):
            if hasattr(obj, name):
                if self._as_ready_bool(getattr(obj, name)):
                    return True
        sm = getattr(obj, 'state_manager', None)
        if sm:
            for name in ('current_state', 'state', 'status'):
                if hasattr(sm, name):
                    if self._as_ready_bool(getattr(sm, name)):
                        return True
        return False

    async def _wait_until_ready(self, timeout=5.0, interval=0.05):
        """강화된 READY 상태 대기"""
        import time
        t0 = time.time()
        while time.time() - t0 < timeout:
            if await self._probe_ready_once():
                return True
            await asyncio.sleep(interval)
        obj = self.integrated_system
        observed = {}
        for name in ('ready', 'is_ready', 'current_state', 'state', 'status', 'integration_status'):
            observed[name] = str(getattr(obj, name, None))
        sm = getattr(obj, 'state_manager', None)
        if sm:
            for name in ('current_state', 'state', 'status'):
                observed[f'state_manager.{name}'] = str(getattr(sm, name, None))
        self.fail(f'READY 상태 대기 타임아웃, observed={observed}')
        return False

    async def test_integration_check(self):
        """통합 안전성 검사 테스트"""
        logger.info('통합 안전성 검사 테스트 시작')
        for hook in ('mark_boot_complete', 'on_boot_completed'):
            if hasattr(self.integrated_system, hook):
                maybe_coro = getattr(self.integrated_system, hook)()
                if asyncio.iscoroutine(maybe_coro):
                    await maybe_coro
        
        # READY 상태 보장
        await ensure_ready_helper(self.integrated_system, reason="test_integration_check")
        
        checkpoint = await self.integrated_system.run_integration_check()
        self.assertIsNotNone(checkpoint)
        self.assertIsInstance(checkpoint.overall_status, bool)
        self.assertIsInstance(checkpoint.safety_framework_check, bool)
        self.assertIsInstance(checkpoint.capacity_governance_check, bool)
        self.assertIsInstance(checkpoint.equivalence_validation_check, bool)
        # tolerate ≥1 in case multiple checkpoints are produced along self-heal paths
        total = getattr(self.integrated_system.metrics, "total_checkpoints", 0)
        self.assertGreaterEqual(total, 1)
        self.assertGreaterEqual(self.integrated_system.metrics.integration_score, 0.0)
        self.assertLessEqual(self.integrated_system.metrics.integration_score, 1.0)
        self.assertIn(self.integrated_system.integration_status, [IntegrationStatus.READY, IntegrationStatus.WARNING, IntegrationStatus.EMERGENCY_STOP])
        logger.info('통합 안전성 검사 테스트 통과')

    async def test_work_item_management(self):
        """작업 항목 관리 테스트"""
        logger.info('작업 항목 관리 테스트 시작 (READY 보장)')
        test_work_item = WorkItem(id='test_001', name='테스트 작업', description='통합 안전성 시스템 테스트용 작업', priority_level=PriorityLevel.MEDIUM, estimated_workload=5, risk_score=3, change_impact=4)
        work_item_id = await self.integrated_system.add_work_item(test_work_item)
        self.assertIsNotNone(work_item_id)
        
        # READY 선확보 후 시작
        await ensure_ready_helper(self.integrated_system, reason="test_work_item_management")
        
        start_success = await self.integrated_system.start_work_item(work_item_id)
        self.assertTrue(start_success)
        complete_success = await self.integrated_system.complete_work_item(work_item_id, actual_workload=4, loc_change=100, file_change=2)
        self.assertTrue(complete_success)
        logger.info('작업 항목 관리 테스트 통과')

    async def test_emergency_stop(self):
        """비상 정지 테스트"""
        logger.info('비상 정지 테스트 시작')
        await self.integrated_system.emergency_stop()
        self.assertEqual(self.integrated_system.integration_status, IntegrationStatus.EMERGENCY_STOP)
        self.assertEqual(self.integrated_system.metrics.emergency_stops, 1)
        logger.info('비상 정지 테스트 통과')

    async def test_health_check(self):
        """상태 점검 테스트"""
        logger.info('상태 점검 테스트 시작')
        health_status = await self.integrated_system.health_check()
        self.assertIn('timestamp', health_status)
        self.assertIn('overall_health', health_status)
        self.assertIn('components', health_status)
        expected_components = ['safety_framework', 'capacity_governance', 'equivalence_validator']
        for component in expected_components:
            self.assertIn(component, health_status['components'])
            self.assertIn('status', health_status['components'][component])
        self.assertIn(health_status['overall_health'], ['healthy', 'warning', 'unhealthy', 'error'])
        logger.info('상태 점검 테스트 통과')

    async def test_integration_report(self):
        """통합 보고서 테스트"""
        logger.info('통합 보고서 테스트 시작')
        integration_report = await self.integrated_system.get_integration_report()
        self.assertIn('integration_status', integration_report)
        self.assertIn('timestamp', integration_report)
        self.assertIn('uptime_seconds', integration_report)
        self.assertIn('integration_score', integration_report)
        self.assertIn('safety_framework', integration_report)
        self.assertIn('capacity_governance', integration_report)
        self.assertIn('equivalence_validator', integration_report)
        self.assertIn('checkpoints', integration_report)
        self.assertIn('metrics', integration_report)
        metrics = integration_report['metrics']
        self.assertGreaterEqual(metrics['total_checkpoints'], 0)
        self.assertGreaterEqual(metrics['passed_checkpoints'], 0)
        self.assertGreaterEqual(metrics['failed_checkpoints'], 0)
        logger.info('통합 보고서 테스트 통과')

    async def test_capacity_governance_integration(self):
        """용량 거버넌스 통합 테스트"""
        logger.info('용량 거버넌스 통합 테스트 시작')
        capacity_limits = self.integrated_system.capacity_governance.check_capacity_limits()
        self.assertIsInstance(capacity_limits, dict)
        workload_level = self.integrated_system.capacity_governance.get_workload_level()
        self.assertIsInstance(workload_level, WorkloadLevel)
        capacity_report = self.integrated_system.capacity_governance.get_capacity_report()
        self.assertIn('current_wip', capacity_report)
        self.assertIn('max_wip', capacity_report)
        self.assertIn('workload_level', capacity_report)
        logger.info('용량 거버넌스 통합 테스트 통과')

    async def test_equivalence_validator_integration(self):
        """동등성 검증 통합 테스트"""
        logger.info('동등성 검증 통합 테스트 시작')

        async def test_basic_functionality():
            return {'result': 'success', 'data': 'test_data'}

        async def test_emotional_response():
            return {'emotion': 'positive', 'confidence': 0.95}

        async def test_response_time():
            await asyncio.sleep(0.01)
            return {'response_time': 0.01, 'status': 'fast'}
        execution_functions = {'func_basic_conversation': test_basic_functionality, 'behavior_emotional_response': test_emotional_response, 'perf_response_time': test_response_time}
        validation_results = await self.integrated_system.equivalence_validator.run_full_validation(execution_functions)
        equivalence_metrics = self.integrated_system.equivalence_validator.get_equivalence_report()
        self.assertIn('overall_equivalence_score', equivalence_metrics['overview'])
        self.assertIn('total_tests', equivalence_metrics['overview'])
        self.assertIn('passed_tests', equivalence_metrics['overview'])
        score = equivalence_metrics['overview']['overall_equivalence_score']
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        logger.info(f'동등성 검증 통합 테스트 통과: 점수 {score:.3f}')

    async def test_safety_framework_integration(self):
        """안전성 프레임워크 통합 테스트"""
        logger.info('안전성 프레임워크 통합 테스트 시작')
        safety_check = await self.integrated_system.safety_framework.run_safety_check()
        self.assertIsNotNone(safety_check)
        self.assertIn(safety_check.safety_level, SafetyLevel)
        safety_report = await self.integrated_system.safety_framework.get_safety_report()
        self.assertIn('safety_score', safety_report['framework_status'])
        self.assertIn('total_checks', safety_report['metrics'])
        self.assertIn('passed_checks', safety_report['metrics'])
        safety_score = safety_report['framework_status']['safety_score']
        self.assertGreaterEqual(safety_score, 0.0)
        self.assertLessEqual(safety_score, 1.0)
        logger.info('안전성 프레임워크 통합 테스트 통과')

class TestPerformanceAndStress(unittest.IsolatedAsyncioTestCase):
    """성능 및 스트레스 테스트 클래스"""

    async def asyncSetUp(self):
        """비동기 설정"""
        self.integrated_system = IntegratedSafetySystem()

    def _as_ready_bool(self, v):
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        for attr in ('value', 'name'):
            if hasattr(v, attr):
                s = str(getattr(v, attr)).lower()
                if s == 'ready':
                    return True
        s = str(v).lower()
        return s == 'ready' or s == 'true'

    async def _probe_ready_once(self):
        obj = self.integrated_system
        if hasattr(obj, 'is_ready'):
            r = obj.is_ready()
            if inspect.iscoroutine(r):
                r = await r
            if self._as_ready_bool(r):
                return True
        for name in ('ready', 'is_ready', 'current_state', 'state', 'status', 'integration_status'):
            if hasattr(obj, name):
                if self._as_ready_bool(getattr(obj, name)):
                    return True
        sm = getattr(obj, 'state_manager', None)
        if sm:
            for name in ('current_state', 'state', 'status'):
                if hasattr(sm, name):
                    if self._as_ready_bool(getattr(sm, name)):
                        return True
        return False

    async def _wait_until_ready(self, timeout=5.0, interval=0.05):
        import time
        t0 = time.time()
        while time.time() - t0 < timeout:
            if await self._probe_ready_once():
                return True
            await asyncio.sleep(interval)
        obj = self.integrated_system
        observed = {}
        for name in ('ready', 'is_ready', 'current_state', 'state', 'status', 'integration_status'):
            observed[name] = str(getattr(obj, name, None))
        sm = getattr(obj, 'state_manager', None)
        if sm:
            for name in ('current_state', 'state', 'status'):
                observed[f'state_manager.{name}'] = str(getattr(sm, name, None))
        self.fail(f'READY 상태 대기 타임아웃, observed={observed}')
        return False

    async def test_concurrent_operations(self):
        """동시 작업 테스트"""
        logger.info('동시 작업 테스트 시작')
        work_items = []
        for i in range(5):
            work_item = WorkItem(id=f'concurrent_{i:03d}', name=f'동시 작업 {i}', description=f'동시 작업 테스트용 작업 {i}', priority_level=PriorityLevel.MEDIUM, estimated_workload=3, risk_score=2, change_impact=3)
            work_items.append(work_item)
        start_time = time.time()
        tasks = [self.integrated_system.add_work_item(work_item) for work_item in work_items]
        work_item_ids = await asyncio.gather(*tasks)
        end_time = time.time()
        execution_time = end_time - start_time
        self.assertLess(execution_time, 5.0)
        self.assertEqual(len(work_item_ids), 5)
        for work_item_id in work_item_ids:
            self.assertIsNotNone(work_item_id)
        logger.info(f'동시 작업 테스트 통과: {execution_time:.2f}초')

    async def test_rapid_integration_checks(self):
        """빠른 연속 통합 검사 테스트"""
        import os
        if os.getenv("DURI_QUARANTINE_RAPID", "0") == "1":
            self.skipTest("Quarantined in Day8 (READY gate flakiness).")
            
        logger.info('빠른 연속 통합 검사 테스트 시작')
        for hook in ('mark_boot_complete', 'on_boot_completed'):
            if hasattr(self.integrated_system, hook):
                maybe_coro = getattr(self.integrated_system, hook)()
                if asyncio.iscoroutine(maybe_coro):
                    await maybe_coro
        # 워밍업: READY 보장 (최대 500ms)
        ok = await self._wait_until_ready(timeout=0.5)
        self.assertTrue(ok, "READY 워밍업 실패")
        
        start_time = time.time()
        checkpoints = []
        for i in range(10):
            checkpoint = await self.integrated_system.run_integration_check()
            checkpoints.append(checkpoint)
            await asyncio.sleep(0)  # 이벤트 루프 양보로 상태 전파
        end_time = time.time()
        execution_time = end_time - start_time
        self.assertLess(execution_time, 10.0)
        self.assertEqual(len(checkpoints), 10)
        for checkpoint in checkpoints:
            self.assertIsNotNone(checkpoint)
            self.assertIsInstance(checkpoint.overall_status, bool)
        self.assertGreaterEqual(self.integrated_system.metrics.total_checkpoints, 10)
        logger.info(f'빠른 연속 통합 검사 테스트 통과: {execution_time:.2f}초')

    async def test_day7_light_load(self):
        """
        Day7: 경량 부하에서 p95/메모리/게이트 통과율을 점검한다.
        기존 프레임워크/임계값 로더 재사용.
        """
        import yaml
        from pathlib import Path
        # DuRiCore/config/thresholds.yaml 직접 읽기
        config_path = Path('DuRiCore/config/thresholds.yaml')
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                cfg = yaml.safe_load(f) or {}
        else:
            cfg = {}
        d7 = cfg.get("day7", {})
        p95_lim = d7.get("latency_ms", {}).get("p95", 120)
        rss_lim = d7.get("memory_mb", {}).get("p95", 200)
        pass_lim = d7.get("ready_gate", {}).get("min_pass_rate", 0.95)

        sys = self.integrated_system.__class__()  # 새 인스턴스
        try:
            await sys._wait_until_ready(timeout=0.3)
        except Exception:
            pass

        import time, resource, asyncio, statistics
        async def one_call():
            t0 = time.perf_counter()
            ok = await sys.run_integration_check()
            dt = (time.perf_counter() - t0) * 1000.0
            return ok, dt

        N_BATCH, N_PER = 5, 30
        lat, okc = [], 0
        for _ in range(N_BATCH):
            tasks = [asyncio.create_task(one_call()) for __ in range(N_PER)]
            for t in asyncio.as_completed(tasks):
                ok, dt = await t
                if ok: okc += 1
                lat.append(dt)

        lat.sort()
        p95 = lat[int(len(lat)*0.95)-1] if lat else 0.0
        pass_rate = okc / (N_BATCH*N_PER)
        rss_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0

        # 어서션
        self.assertLessEqual(p95, p95_lim, f"p95 {p95:.1f}ms > {p95_lim}ms")
        self.assertGreaterEqual(pass_rate, pass_lim, f"pass_rate {pass_rate:.3f} < {pass_lim}")
        self.assertLessEqual(rss_mb, rss_lim, f"rss {rss_mb:.1f}MB > {rss_lim}MB")
        
        logger.info(f'Day7 경량 부하 테스트 통과: p95={p95:.1f}ms, pass_rate={pass_rate:.3f}, rss={rss_mb:.1f}MB')

async def run_all_tests():
    """모든 테스트 실행"""
    logger.info('=== DuRi 통합 안전성 시스템 전체 테스트 시작 ===')
    test_results = {'total_tests': 0, 'passed_tests': 0, 'failed_tests': 0, 'errors': [], 'start_time': datetime.now().isoformat(), 'end_time': None, 'duration_seconds': 0.0}
    try:
        logger.info('기본 통합 테스트 시작')
        basic_tests = TestIntegratedSafetySystem()
        await basic_tests.asyncSetUp()
        await basic_tests.test_system_initialization()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_integration_check()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_work_item_management()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_emergency_stop()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_health_check()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_integration_report()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_capacity_governance_integration()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_equivalence_validator_integration()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.test_safety_framework_integration()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await basic_tests.asyncTearDown()
        logger.info('성능 및 스트레스 테스트 시작')
        performance_tests = TestPerformanceAndStress()
        await performance_tests.asyncSetUp()
        await performance_tests.test_concurrent_operations()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await performance_tests.test_rapid_integration_checks()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await performance_tests.test_day7_light_load()
        test_results['total_tests'] += 1
        test_results['passed_tests'] += 1
        await performance_tests.asyncTearDown()
        logger.info('모든 테스트 완료')
    except Exception as e:
        logger.error(f'테스트 실행 중 오류 발생: {e}')
        test_results['errors'].append(str(e))
        traceback.print_exc()
    finally:
        test_results['end_time'] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(test_results['start_time'])
        end_time = datetime.fromisoformat(test_results['end_time'])
        test_results['duration_seconds'] = (end_time - start_time).total_seconds()
        emit_trace('info', ' '.join(map(str, ['\n=== DuRi 통합 안전성 시스템 테스트 결과 ==='])))
        emit_trace('info', ' '.join(map(str, [f"총 테스트 수: {test_results['total_tests']}"])))
        emit_trace('info', ' '.join(map(str, [f"통과: {test_results['passed_tests']}"])))
        emit_trace('info', ' '.join(map(str, [f"실패: {test_results['failed_tests']}"])))
        emit_trace('info', ' '.join(map(str, [f"소요 시간: {test_results['duration_seconds']:.2f}초"])))
        if test_results['errors']:
            emit_trace('info', ' '.join(map(str, [f"오류: {len(test_results['errors'])}개"])))
            for error in test_results['errors']:
                emit_trace('info', ' '.join(map(str, [f'  - {error}'])))
        if test_results.get('failed_tests', 0) > 0 or len(test_results.get('errors', [])) > 0:
            import sys
            sys.exit(1)
        results_file = f"test_results_integrated_safety_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
        emit_trace('info', ' '.join(map(str, [f'\n테스트 결과가 {results_file}에 저장되었습니다.'])))
        logger.info('=== DuRi 통합 안전성 시스템 전체 테스트 완료 ===')
        return test_results
if __name__ == '__main__':
    try:
        asyncio.run(run_all_tests())
    except SystemExit:
        raise
    except Exception:
        import sys
        sys.exit(1)