#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import logging
import traceback
from pathlib import Path

# DuRi 로깅 시스템 초기화
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    # 로컬 디렉토리에서 직접 import
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 테스트 대상 시스템들 import
try:
    from DuRiCore.integrated_safety_system import IntegratedSafetySystem, IntegrationStatus
    from DuRiCore.safety_framework import SafetyFramework, SafetyLevel, SafetyInvariant, InvariantType
    from DuRiCore.capacity_governance import CapacityGovernance, WorkItem, PriorityLevel, WorkloadLevel
    from DuRiCore.equivalence_validator import EquivalenceValidator, EquivalenceLevel, ValidationType
except ImportError:
    # 로컬 디렉토리에서 직접 import
    from integrated_safety_system import IntegratedSafetySystem, IntegrationStatus
    from safety_framework import SafetyFramework, SafetyLevel, SafetyInvariant, InvariantType
    from capacity_governance import CapacityGovernance, WorkItem, PriorityLevel, WorkloadLevel
    from equivalence_validator import EquivalenceValidator, EquivalenceLevel, ValidationType

logger = logging.getLogger(__name__)

class TestIntegratedSafetySystem(unittest.IsolatedAsyncioTestCase):
    """통합 안전성 시스템 테스트 클래스"""
    
    async def asyncSetUp(self):
        """비동기 설정"""
        self.integrated_system = IntegratedSafetySystem()
        self.test_start_time = datetime.now()
        
        logger.info("통합 안전성 시스템 테스트 설정 완료")
    
    async def asyncTearDown(self):
        """비동기 정리"""
        test_duration = datetime.now() - self.test_start_time
        logger.info(f"테스트 완료: {test_duration.total_seconds():.2f}초 소요")
    
    async def test_system_initialization(self):
        """시스템 초기화 테스트"""
        logger.info("시스템 초기화 테스트 시작")
        
        # 1. 기본 시스템들이 초기화되었는지 확인
        self.assertIsNotNone(self.integrated_system.safety_framework)
        self.assertIsNotNone(self.integrated_system.capacity_governance)
        self.assertIsNotNone(self.integrated_system.equivalence_validator)
        
        # 2. 초기 상태 확인
        self.assertEqual(self.integrated_system.integration_status, IntegrationStatus.INITIALIZING)
        
        # 3. 기본 체크포인트들이 등록되었는지 확인
        expected_checkpoints = [
            "system_initialization",
            "capacity_governance", 
            "equivalence_validation",
            "safety_framework",
            "integration_status"
        ]
        
        for checkpoint_id in expected_checkpoints:
            self.assertIn(checkpoint_id, self.integrated_system.safety_checkpoints)
        
        # 4. 메트릭 초기화 확인
        self.assertEqual(self.integrated_system.metrics.total_checkpoints, 0)
        self.assertEqual(self.integrated_system.metrics.integration_score, 1.0)
        
        logger.info("시스템 초기화 테스트 통과")
    
    async def test_integration_check(self):
        """통합 안전성 검사 테스트"""
        logger.info("통합 안전성 검사 테스트 시작")
        
        # 1. 통합 검사 실행
        checkpoint = await self.integrated_system.run_integration_check()
        
        # 2. 체크포인트 결과 확인
        self.assertIsNotNone(checkpoint)
        self.assertIsInstance(checkpoint.overall_status, bool)
        self.assertIsInstance(checkpoint.safety_framework_check, bool)
        self.assertIsInstance(checkpoint.capacity_governance_check, bool)
        self.assertIsInstance(checkpoint.equivalence_validation_check, bool)
        
        # 3. 메트릭 업데이트 확인
        self.assertEqual(self.integrated_system.metrics.total_checkpoints, 1)
        self.assertGreaterEqual(self.integrated_system.metrics.integration_score, 0.0)
        self.assertLessEqual(self.integrated_system.metrics.integration_score, 1.0)
        
        # 4. 통합 상태 업데이트 확인
        self.assertIn(self.integrated_system.integration_status, [
            IntegrationStatus.READY,
            IntegrationStatus.WARNING,
            IntegrationStatus.EMERGENCY_STOP
        ])
        
        logger.info("통합 안전성 검사 테스트 통과")
    
    async def test_work_item_management(self):
        """작업 항목 관리 테스트"""
        logger.info("작업 항목 관리 테스트 시작")
        
        # 1. 테스트 작업 항목 생성
        test_work_item = WorkItem(
            id="test_001",
            name="테스트 작업",
            description="통합 안전성 시스템 테스트용 작업",
            priority_level=PriorityLevel.MEDIUM,
            estimated_workload=5,
            risk_score=3,
            change_impact=4
        )
        
        # 2. 작업 항목 추가
        work_item_id = await self.integrated_system.add_work_item(test_work_item)
        self.assertIsNotNone(work_item_id)
        
        # 3. 작업 항목 시작
        start_success = await self.integrated_system.start_work_item(work_item_id)
        self.assertTrue(start_success)
        
        # 4. 작업 항목 완료
        complete_success = await self.integrated_system.complete_work_item(
            work_item_id, 
            actual_workload=4,
            loc_change=100,
            file_change=2
        )
        self.assertTrue(complete_success)
        
        logger.info("작업 항목 관리 테스트 통과")
    
    async def test_emergency_stop(self):
        """비상 정지 테스트"""
        logger.info("비상 정지 테스트 시작")
        
        # 1. 비상 정지 실행
        await self.integrated_system.emergency_stop()
        
        # 2. 통합 상태 확인
        self.assertEqual(self.integrated_system.integration_status, IntegrationStatus.EMERGENCY_STOP)
        
        # 3. 메트릭 업데이트 확인
        self.assertEqual(self.integrated_system.metrics.emergency_stops, 1)
        
        logger.info("비상 정지 테스트 통과")
    
    async def test_health_check(self):
        """상태 점검 테스트"""
        logger.info("상태 점검 테스트 시작")
        
        # 1. 상태 점검 실행
        health_status = await self.integrated_system.health_check()
        
        # 2. 기본 구조 확인
        self.assertIn("timestamp", health_status)
        self.assertIn("overall_health", health_status)
        self.assertIn("components", health_status)
        
        # 3. 컴포넌트 상태 확인
        expected_components = [
            "safety_framework",
            "capacity_governance", 
            "equivalence_validator"
        ]
        
        for component in expected_components:
            self.assertIn(component, health_status["components"])
            self.assertIn("status", health_status["components"][component])
        
        # 4. 전체 상태 확인
        self.assertIn(health_status["overall_health"], ["healthy", "warning", "unhealthy", "error"])
        
        logger.info("상태 점검 테스트 통과")
    
    async def test_integration_report(self):
        """통합 보고서 테스트"""
        logger.info("통합 보고서 테스트 시작")
        
        # 1. 통합 보고서 생성
        integration_report = await self.integrated_system.get_integration_report()
        
        # 2. 기본 구조 확인
        self.assertIn("integration_status", integration_report)
        self.assertIn("timestamp", integration_report)
        self.assertIn("uptime_seconds", integration_report)
        self.assertIn("integration_score", integration_report)
        
        # 3. 하위 시스템 보고서 확인
        self.assertIn("safety_framework", integration_report)
        self.assertIn("capacity_governance", integration_report)
        self.assertIn("equivalence_validator", integration_report)
        
        # 4. 체크포인트 정보 확인
        self.assertIn("checkpoints", integration_report)
        self.assertIn("metrics", integration_report)
        
        # 5. 메트릭 값 확인
        metrics = integration_report["metrics"]
        self.assertGreaterEqual(metrics["total_checkpoints"], 0)
        self.assertGreaterEqual(metrics["passed_checkpoints"], 0)
        self.assertGreaterEqual(metrics["failed_checkpoints"], 0)
        
        logger.info("통합 보고서 테스트 통과")
    
    async def test_capacity_governance_integration(self):
        """용량 거버넌스 통합 테스트"""
        logger.info("용량 거버넌스 통합 테스트 시작")
        
        # 1. 용량 한계 확인
        capacity_limits = self.integrated_system.capacity_governance.check_capacity_limits()
        self.assertIsInstance(capacity_limits, dict)
        
        # 2. 작업량 수준 확인
        workload_level = self.integrated_system.capacity_governance.get_workload_level()
        self.assertIsInstance(workload_level, WorkloadLevel)
        
        # 3. 용량 보고서 확인
        capacity_report = self.integrated_system.capacity_governance.get_capacity_report()
        self.assertIn("current_wip", capacity_report)
        self.assertIn("max_wip", capacity_report)
        self.assertIn("workload_level", capacity_report)
        
        logger.info("용량 거버넌스 통합 테스트 통과")
    
    async def test_equivalence_validator_integration(self):
        """동등성 검증 통합 테스트"""
        logger.info("동등성 검증 통합 테스트 시작")
        
        # 1. 기본 동등성 검증 실행
        async def test_basic_functionality():
            return {"result": "success", "data": "test_data"}
        
        async def test_emotional_response():
            return {"emotion": "positive", "confidence": 0.95}
        
        async def test_response_time():
            await asyncio.sleep(0.01)  # 10ms 지연
            return {"response_time": 0.01, "status": "fast"}
        
        # 2. 동등성 검증 실행
        execution_functions = {
            "func_basic_conversation": test_basic_functionality,
            "behavior_emotional_response": test_emotional_response,
            "perf_response_time": test_response_time
        }
        
        validation_results = await self.integrated_system.equivalence_validator.run_full_validation(execution_functions)
        
        # 3. 동등성 메트릭 확인
        equivalence_metrics = self.integrated_system.equivalence_validator.get_equivalence_report()
        self.assertIn("overall_equivalence_score", equivalence_metrics["overview"])
        self.assertIn("total_tests", equivalence_metrics["overview"])
        self.assertIn("passed_tests", equivalence_metrics["overview"])
        
        # 4. 동등성 점수 범위 확인
        score = equivalence_metrics["overview"]["overall_equivalence_score"]
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)
        
        logger.info(f"동등성 검증 통합 테스트 통과: 점수 {score:.3f}")
    
    async def test_safety_framework_integration(self):
        """안전성 프레임워크 통합 테스트"""
        logger.info("안전성 프레임워크 통합 테스트 시작")
        
        # 1. 안전성 검사 실행
        safety_check = await self.integrated_system.safety_framework.run_safety_check()
        
        # 2. 안전성 검사 결과 확인
        self.assertIsNotNone(safety_check)
        self.assertIn(safety_check.safety_level, SafetyLevel)
        
        # 3. 안전성 보고서 확인
        safety_report = await self.integrated_system.safety_framework.get_safety_report()
        self.assertIn("safety_score", safety_report["framework_status"])
        self.assertIn("total_checks", safety_report["metrics"])
        self.assertIn("passed_checks", safety_report["metrics"])
        
        # 4. 안전성 점수 범위 확인
        safety_score = safety_report["framework_status"]["safety_score"]
        self.assertGreaterEqual(safety_score, 0.0)
        self.assertLessEqual(safety_score, 1.0)
        
        logger.info("안전성 프레임워크 통합 테스트 통과")

class TestPerformanceAndStress(unittest.IsolatedAsyncioTestCase):
    """성능 및 스트레스 테스트 클래스"""
    
    async def asyncSetUp(self):
        """비동기 설정"""
        self.integrated_system = IntegratedSafetySystem()
    
    async def test_concurrent_operations(self):
        """동시 작업 테스트"""
        logger.info("동시 작업 테스트 시작")
        
        # 1. 여러 작업 항목을 동시에 생성
        work_items = []
        for i in range(5):
            work_item = WorkItem(
                id=f"concurrent_{i:03d}",
                name=f"동시 작업 {i}",
                description=f"동시 작업 테스트용 작업 {i}",
                priority_level=PriorityLevel.MEDIUM,
                estimated_workload=3,
                risk_score=2,
                change_impact=3
            )
            work_items.append(work_item)
        
        # 2. 동시에 작업 항목 추가
        start_time = time.time()
        tasks = [
            self.integrated_system.add_work_item(work_item)
            for work_item in work_items
        ]
        
        work_item_ids = await asyncio.gather(*tasks)
        end_time = time.time()
        
        # 3. 성능 확인
        execution_time = end_time - start_time
        self.assertLess(execution_time, 5.0)  # 5초 이내 완료
        
        # 4. 모든 작업 항목이 성공적으로 추가되었는지 확인
        self.assertEqual(len(work_item_ids), 5)
        for work_item_id in work_item_ids:
            self.assertIsNotNone(work_item_id)
        
        logger.info(f"동시 작업 테스트 통과: {execution_time:.2f}초")
    
    async def test_rapid_integration_checks(self):
        """빠른 연속 통합 검사 테스트"""
        logger.info("빠른 연속 통합 검사 테스트 시작")
        
        # 1. 연속으로 통합 검사 실행
        start_time = time.time()
        checkpoints = []
        
        for i in range(10):
            checkpoint = await self.integrated_system.run_integration_check()
            checkpoints.append(checkpoint)
        
        end_time = time.time()
        
        # 2. 성능 확인
        execution_time = end_time - start_time
        self.assertLess(execution_time, 10.0)  # 10초 이내 완료
        
        # 3. 모든 검사가 완료되었는지 확인
        self.assertEqual(len(checkpoints), 10)
        for checkpoint in checkpoints:
            self.assertIsNotNone(checkpoint)
            self.assertIsInstance(checkpoint.overall_status, bool)
        
        # 4. 메트릭 업데이트 확인
        self.assertEqual(self.integrated_system.metrics.total_checkpoints, 10)
        
        logger.info(f"빠른 연속 통합 검사 테스트 통과: {execution_time:.2f}초")

# 메인 테스트 실행 함수
async def run_all_tests():
    """모든 테스트 실행"""
    
    logger.info("=== DuRi 통합 안전성 시스템 전체 테스트 시작 ===")
    
    # 테스트 결과 수집
    test_results = {
        "total_tests": 0,
        "passed_tests": 0,
        "failed_tests": 0,
        "errors": [],
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "duration_seconds": 0.0
    }
    
    try:
        # 1. 기본 통합 테스트
        logger.info("기본 통합 테스트 시작")
        basic_tests = TestIntegratedSafetySystem()
        
        # 시스템 초기화 테스트
        await basic_tests.asyncSetUp()
        await basic_tests.test_system_initialization()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 통합 안전성 검사 테스트
        await basic_tests.test_integration_check()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 작업 항목 관리 테스트
        await basic_tests.test_work_item_management()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 비상 정지 테스트
        await basic_tests.test_emergency_stop()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 상태 점검 테스트
        await basic_tests.test_health_check()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 통합 보고서 테스트
        await basic_tests.test_integration_report()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 용량 거버넌스 통합 테스트
        await basic_tests.test_capacity_governance_integration()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 동등성 검증 통합 테스트
        await basic_tests.test_equivalence_validator_integration()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 안전성 프레임워크 통합 테스트
        await basic_tests.test_safety_framework_integration()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        await basic_tests.asyncTearDown()
        
        # 2. 성능 및 스트레스 테스트
        logger.info("성능 및 스트레스 테스트 시작")
        performance_tests = TestPerformanceAndStress()
        
        # 동시 작업 테스트
        await performance_tests.asyncSetUp()
        await performance_tests.test_concurrent_operations()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # 빠른 연속 통합 검사 테스트
        await performance_tests.test_rapid_integration_checks()
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        await performance_tests.asyncTearDown()
        
        logger.info("모든 테스트 완료")
        
    except Exception as e:
        logger.error(f"테스트 실행 중 오류 발생: {e}")
        test_results["errors"].append(str(e))
        traceback.print_exc()
    
    finally:
        # 테스트 결과 정리
        test_results["end_time"] = datetime.now().isoformat()
        start_time = datetime.fromisoformat(test_results["start_time"])
        end_time = datetime.fromisoformat(test_results["end_time"])
        test_results["duration_seconds"] = (end_time - start_time).total_seconds()
        
        # 결과 출력
        print("\n=== DuRi 통합 안전성 시스템 테스트 결과 ===")
        print(f"총 테스트 수: {test_results['total_tests']}")
        print(f"통과: {test_results['passed_tests']}")
        print(f"실패: {test_results['failed_tests']}")
        print(f"소요 시간: {test_results['duration_seconds']:.2f}초")
        
        if test_results["errors"]:
            print(f"오류: {len(test_results['errors'])}개")
            for error in test_results["errors"]:
                print(f"  - {error}")
        
        # 결과를 JSON 파일로 저장
        results_file = f"test_results_integrated_safety_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(test_results, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"\n테스트 결과가 {results_file}에 저장되었습니다.")
        
        logger.info("=== DuRi 통합 안전성 시스템 전체 테스트 완료 ===")
        
        return test_results

if __name__ == "__main__":
    # 테스트 실행
    asyncio.run(run_all_tests())
