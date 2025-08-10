#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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

# DuRi 로깅 시스템 초기화
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    # 로컬 디렉토리에서 직접 import
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 통합 안전성 시스템 import
from integrated_safety_system import (
    IntegratedSafetySystem, IntegrationStatus, 
    EmergencyStopTrigger, EmergencyStopPolicy
)
from capacity_governance import WorkItem, PriorityLevel

logger = logging.getLogger(__name__)

class SafetySystemDemo:
    """안전성 시스템 데모 클래스 (T6: 회귀세트 편입)"""
    
    def __init__(self):
        self.integrated_system = None
        self.demo_start_time = datetime.now()
        self.demo_results = {
            "scenarios": [],
            "total_scenarios": 0,
            "successful_scenarios": 0,
            "failed_scenarios": 0,
            "start_time": self.demo_start_time.isoformat(),
            "end_time": None,
            "duration_seconds": 0.0,
            "t6_regression_tests": [],  # T6: 회귀 테스트 결과
            "hysteresis_tests": [],     # T6: 히스테리시스 테스트 결과
            "estop_policy_tests": []    # T6: E-stop 정책 테스트 결과
        }
        
        # 상태 리스너 등록 (state.ready 이벤트 대기)
        try:
            from DuRiCore.state_manager import state_manager
            self.state_manager = state_manager
            self.state_manager.add_state_listener("state_change", self._on_state_change)
            self.collectors_started = False  # 수집기 시작 상태 추적
        except ImportError:
            self.state_manager = None
            self.collectors_started = True  # StateManager 없으면 즉시 시작
    
    async def initialize_system(self):
        """시스템 초기화 (T6: 개선된 초기화)"""
        logger.info("=== DuRi 통합 안전성 시스템 초기화 (T6) ===")
        
        try:
            # 1. 통합 안전성 시스템 생성
            self.integrated_system = IntegratedSafetySystem()
            logger.info("✅ 통합 안전성 시스템 생성 완료")
            
            # 2. 시스템이 READY 상태가 될 때까지 대기 (T9: READY 게이트 해제)
            try:
                await self.integrated_system._wait_for_ready_state()
                logger.info("✅ T9: 시스템 READY 상태 대기 완료")
            except Exception as e:
                logger.warning(f"⚠️ T9: READY 상태 대기 실패 (계속 진행): {e}")
            
            # 3. 초기 상태 점검 (단순화된 버전)
            try:
                health_status = await self.integrated_system.health_check()
                logger.info(f"✅ 초기 상태: {health_status['overall_health']}")
            except Exception as e:
                logger.warning(f"⚠️ 초기 상태 점검 실패 (계속 진행): {e}")
                health_status = {"overall_health": "unknown"}
            
            # 3. 시스템 상태 출력 (기본 정보만)
            print(f"\n🔧 시스템 상태: {self.integrated_system.integration_status.value}")
            print(f"📊 통합 점수: {self.integrated_system.metrics.integration_score:.2%}")
            
            # 4. E-stop 조건 확인 (선택적)
            try:
                estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
                print(f"🛑 E-stop 정책: {estop_conditions.get('current_policy', 'unknown')}")
                logger.info(f"✅ E-stop 조건 확인: {estop_conditions.get('should_trigger', False)}")
            except Exception as e:
                logger.warning(f"⚠️ E-stop 조건 확인 실패 (계속 진행): {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 시스템 초기화 실패: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _on_state_change(self, data: Dict[str, Any]):
        """상태 변경 이벤트 핸들러 (state.ready 대기)"""
        try:
            if data.get("to_state") == "ready" and not self.collectors_started:
                logger.info("🎯 StateManager가 READY 상태 - 수집기 시작 준비 완료")
                self.collectors_started = True
                
                # 수집기 시작 로직 실행
                asyncio.create_task(self._start_collectors())
                
        except Exception as e:
            logger.warning(f"상태 변경 이벤트 처리 실패: {e}")
    
    async def _start_collectors(self):
        """수집기 시작 (StateManager READY 이후)"""
        try:
            logger.info("🚀 수집기 시작 중...")
            
            # 1. 동등성 검증 초기화
            if hasattr(self.integrated_system, 'equivalence_validator'):
                logger.info("✅ 동등성 검증기 초기화 완료")
            
            # 2. 안전성 프레임워크 초기화
            if hasattr(self.integrated_system, 'safety_framework'):
                logger.info("✅ 안전성 프레임워크 초기화 완료")
            
            # 3. 용량 거버넌스 초기화
            if hasattr(self.integrated_system, 'capacity_governance'):
                logger.info("✅ 용량 거버넌스 초기화 완료")
            
            logger.info("🎉 모든 수집기 시작 완료 - 시스템 준비됨")
            
        except Exception as e:
            logger.error(f"❌ 수집기 시작 실패: {e}")
            self.collectors_started = False
    
    async def demo_scenario_1_basic_operations(self):
        """시나리오 1: 기본 작업 관리"""
        logger.info("=== 시나리오 1: 기본 작업 관리 ===")
        
        scenario_result = {
            "name": "기본 작업 관리",
            "description": "작업 항목 추가, 시작, 완료의 기본 워크플로우",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. 작업 항목 생성
            work_item = WorkItem(
                id="demo_001",
                name="데모 작업 1",
                description="기본 작업 관리 시나리오 테스트",
                priority_level=PriorityLevel.MEDIUM,
                estimated_workload=4,
                risk_score=2,
                change_impact=3
            )
            
            # 2. 작업 항목 추가
            work_item_id = await self.integrated_system.add_work_item(work_item)
            logger.info(f"✅ 작업 항목 추가 완료: {work_item_id}")
            
            # 3. 작업 항목 시작
            start_success = await self.integrated_system.start_work_item(work_item_id)
            if start_success:
                logger.info("✅ 작업 항목 시작 완료")
            else:
                logger.error("❌ 작업 항목 시작 실패")
                raise Exception("작업 항목 시작 실패")
            
            # 4. 작업 항목 완료
            complete_success = await self.integrated_system.complete_work_item(
                work_item_id, 
                actual_workload=3,
                loc_change=50,
                file_change=1
            )
            if complete_success:
                logger.info("✅ 작업 항목 완료 성공")
            else:
                logger.error("❌ 작업 항목 완료 실패")
                raise Exception("작업 항목 완료 실패")
            
            # 5. 결과 확인
            scenario_result["success"] = True
            scenario_result["details"] = {
                "work_item_id": work_item_id,
                "start_success": start_success,
                "complete_success": complete_success
            }
            
            logger.info("✅ 시나리오 1 완료")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 1 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_2_capacity_governance(self):
        """시나리오 2: 용량 거버넌스 테스트"""
        logger.info("=== 시나리오 2: 용량 거버넌스 테스트 ===")
        
        scenario_result = {
            "name": "용량 거버넌스 테스트",
            "description": "WIP 한계, LOC 변경량, 파일 변경량 제한 테스트",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. 현재 용량 상태 확인
            capacity_report = self.integrated_system.capacity_governance.get_capacity_report()
            logger.info(f"📊 현재 WIP: {capacity_report['current_status']['current_wip']}/{capacity_report['current_status']['wip_limit']}")
            logger.info(f"📊 작업량 수준: {capacity_report['current_status']['workload_level']}")
            
            # 2. 여러 작업 항목 추가 시도
            work_items = []
            for i in range(3):
                work_item = WorkItem(
                    id=f"capacity_demo_{i:03d}",
                    name=f"용량 테스트 작업 {i}",
                    description=f"용량 거버넌스 테스트용 작업 {i}",
                    priority_level=PriorityLevel.LOW,
                    estimated_workload=2,
                    risk_score=1,
                    change_impact=2
                )
                work_items.append(work_item)
            
            # 3. 작업 항목들을 순차적으로 추가
            added_count = 0
            for work_item in work_items:
                try:
                    work_item_id = await self.integrated_system.add_work_item(work_item)
                    logger.info(f"✅ 작업 항목 추가 성공: {work_item_id}")
                    added_count += 1
                except Exception as e:
                    logger.info(f"⚠️ 작업 항목 추가 제한됨: {e}")
                    break
            
            # 4. 용량 한계 확인
            capacity_limits = self.integrated_system.capacity_governance.check_capacity_limits()
            logger.info(f"📊 용량 한계 상태: {capacity_limits}")
            
            # 5. 결과 확인
            scenario_result["success"] = True
            scenario_result["details"] = {
                "initial_capacity": capacity_report,
                "added_work_items": added_count,
                "capacity_limits": capacity_limits
            }
            
            logger.info("✅ 시나리오 2 완료")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 2 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_3_safety_monitoring(self):
        """시나리오 3: 안전성 모니터링"""
        logger.info("=== 시나리오 3: 안전성 모니터링 ===")
        
        scenario_result = {
            "name": "안전성 모니터링",
            "description": "실시간 안전성 상태 모니터링 및 체크포인트",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. 연속 안전성 검사 실행
            checkpoints = []
            for i in range(5):
                logger.info(f"🔍 안전성 검사 {i+1}/5 실행 중...")
                checkpoint = await self.integrated_system.run_integration_check()
                checkpoints.append(checkpoint)
                
                # 검사 결과 출력
                print(f"  📊 검사 {i+1}: {'✅' if checkpoint.overall_status else '❌'}")
                print(f"     안전성: {'✅' if checkpoint.safety_framework_check else '❌'}")
                print(f"     용량: {'✅' if checkpoint.capacity_governance_check else '❌'}")
                print(f"     동등성: {'✅' if checkpoint.equivalence_validation_check else '❌'}")
                
                await asyncio.sleep(0.5)  # 짧은 대기
            
            # 2. 상태 점검 실행
            health_status = await self.integrated_system.health_check()
            logger.info(f"📊 전체 상태: {health_status['overall_health']}")
            
            # 3. 통합 보고서 생성
            integration_report = await self.integrated_system.get_integration_report()
            
            # 4. 결과 확인
            scenario_result["success"] = True
            scenario_result["details"] = {
                "checkpoints_count": len(checkpoints),
                "health_status": health_status["overall_health"],
                "integration_score": integration_report["integration_score"],
                "safety_score": integration_report["safety_framework"]["framework_status"]["safety_score"],
                "equivalence_score": integration_report["equivalence_validator"]["overview"]["overall_equivalence_score"]
            }
            
            logger.info("✅ 시나리오 3 완료")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 3 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_4_emergency_response(self):
        """시나리오 4: 비상 대응 (T6: 개선된 E-stop)"""
        logger.info("=== 시나리오 4: 비상 대응 (T6) ===")
        
        scenario_result = {
            "name": "비상 대응 (T6)",
            "description": "히스테리시스 기반 비상 정지 및 복구 시나리오",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. 히스테리시스 E-stop 테스트
            logger.info("🛑 히스테리시스 E-stop 테스트 중...")
            
            # 경미한 동등성 위반 (히스테리시스 적용)
            await self.integrated_system.emergency_stop(
                trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION,
                severity=0.3,  # 경미한 위반
                details={"test_type": "hysteresis_test", "violation_level": "minor"}
            )
            
            # 2. E-stop 조건 확인
            estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
            logger.info(f"🛑 E-stop 조건: {estop_conditions['should_trigger']}")
            
            # 3. 시스템 상태 점검
            health_status = await self.integrated_system.health_check()
            logger.info(f"📊 E-stop 후 상태: {health_status['overall_health']}")
            
            # 4. 결과 확인
            scenario_result["success"] = True
            scenario_result["details"] = {
                "estop_conditions": estop_conditions,
                "health_status": health_status["overall_health"],
                "emergency_stops_count": self.integrated_system.metrics.emergency_stops,
                "hysteresis_status": estop_conditions["hysteresis_status"]
            }
            
            logger.info("✅ 시나리오 4 완료 (T6)")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 4 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_5_hysteresis_test(self):
        """시나리오 5: 히스테리시스 테스트 (T6)"""
        logger.info("=== 시나리오 5: 히스테리시스 테스트 (T6) ===")
        
        scenario_result = {
            "name": "히스테리시스 테스트 (T6)",
            "description": "연속 위반에 따른 히스테리시스 E-stop 트리거 테스트",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. 연속 위반 시뮬레이션
            logger.info("🔄 연속 위반 시뮬레이션 중...")
            
            violations = []
            for i in range(3):  # 3회 연속 위반
                violation = await self.integrated_system.emergency_stop(
                    trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION,
                    severity=0.4 + (i * 0.1),  # 점진적 심각도 증가
                    details={
                        "test_type": "hysteresis_sequence",
                        "violation_number": i + 1,
                        "total_violations": 3
                    }
                )
                violations.append(violation)
                await asyncio.sleep(0.1)  # 짧은 간격
            
            # 2. 히스테리시스 트리거 확인
            estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
            hysteresis_triggered = estop_conditions["should_trigger"]
            
            # 3. 결과 확인
            scenario_result["success"] = True
            scenario_result["details"] = {
                "violations_count": len(violations),
                "hysteresis_triggered": hysteresis_triggered,
                "estop_conditions": estop_conditions,
                "hysteresis_windows": estop_conditions["hysteresis_status"]
            }
            
            # T6: 히스테리시스 테스트 결과 저장
            self.demo_results["hysteresis_tests"].append({
                "test_name": "연속 위반 히스테리시스",
                "violations_count": len(violations),
                "triggered": hysteresis_triggered,
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ 시나리오 5 완료 (T6): 히스테리시스 트리거 = {hysteresis_triggered}")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 5 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_6_estop_policy_test(self):
        """시나리오 6: E-stop 정책 테스트 (T6)"""
        logger.info("=== 시나리오 6: E-stop 정책 테스트 (T6) ===")
        
        scenario_result = {
            "name": "E-stop 정책 테스트 (T6)",
            "description": "다양한 E-stop 정책 (즉시/점진적/히스테리시스) 테스트",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. 즉시 E-stop 테스트 (심각한 위반)
            logger.info("🚨 즉시 E-stop 테스트 중...")
            await self.integrated_system.emergency_stop(
                trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION,
                severity=0.95,  # 심각한 위반
                details={"test_type": "immediate_estop", "violation_level": "severe"}
            )
            
            # 2. 점진적 격리 테스트 (관찰성 결측)
            logger.info("⚠️ 점진적 격리 테스트 중...")
            await self.integrated_system.emergency_stop(
                trigger=EmergencyStopTrigger.OBSERVABILITY_MISSING,
                severity=0.6,  # 중간 수준
                details={"test_type": "gradual_isolation", "missing_type": "observability"}
            )
            
            # 3. 정책별 결과 확인
            estop_history = self.integrated_system.get_emergency_stop_history()
            policy_results = {}
            
            for record in estop_history[-3:]:  # 최근 3개 기록
                policy_results[record["trigger"]] = {
                    "policy": record["policy"],
                    "severity": record["severity"]
                }
            
            # 4. 결과 확인
            scenario_result["success"] = True
            scenario_result["details"] = {
                "estop_history": estop_history,
                "policy_results": policy_results,
                "total_estops": len(estop_history)
            }
            
            # T6: E-stop 정책 테스트 결과 저장
            self.demo_results["estop_policy_tests"].append({
                "test_name": "다양한 E-stop 정책",
                "policies_tested": list(policy_results.keys()),
                "total_estops": len(estop_history),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info("✅ 시나리오 6 완료 (T6)")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 6 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_7_regression_test(self):
        """시나리오 7: 회귀 테스트 (T6)"""
        logger.info("=== 시나리오 7: 회귀 테스트 (T6) ===")
        
        scenario_result = {
            "name": "회귀 테스트 (T6)",
            "description": "기존 기능의 회귀 방지 및 안정성 검증",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. E-stop 상태에서 시스템 복구 (T10: 웜업 윈도우 이후 자동 복구)
            if self.integrated_system.integration_status.value == "emergency_stop":
                logger.info("🔄 T10: E-stop 상태에서 시스템 복구 시도...")
                recovery_success = await self.integrated_system.recover_from_emergency_stop("시나리오 7 회귀 테스트")
                if not recovery_success:
                    logger.warning("⚠️ T10: 시스템 복구 실패 - 웜업 윈도우 대기 중")
                    # 웜업 윈도우 대기 후 재시도
                    await asyncio.sleep(2.0)
                    recovery_success = await self.integrated_system.recover_from_emergency_stop("시나리오 7 회귀 테스트 재시도")
                
                if recovery_success:
                    logger.info("✅ T10: 시스템 복구 완료 - 회귀 테스트 진행")
                else:
                    logger.error("❌ T10: 시스템 복구 실패 - 회귀 테스트 중단")
                    scenario_result["details"]["error"] = "시스템 복구 실패"
                    return
            
            # 2. READY 상태 확인 및 대기
            logger.info("⏳ READY 상태 확인 중...")
            max_wait_time = 5.0  # 최대 5초 대기
            wait_start = time.time()
            while self.integrated_system.integration_status != IntegrationStatus.READY:
                if time.time() - wait_start > max_wait_time:
                    logger.warning("⚠️ READY 상태 대기 시간 초과, 계속 진행")
                    break
                await asyncio.sleep(0.1)
            
            # 3. 기본 기능 회귀 테스트
            logger.info("🔄 기본 기능 회귀 테스트 중...")
            
            # 통합 안전성 검사
            checkpoint = await self.integrated_system.run_integration_check()
            
            # 상태 매니저 상태 확인
            state_status = self.integrated_system.state_manager.current_state
            
            # 용량 거버넌스 상태 확인
            capacity_status = self.integrated_system.capacity_governance.check_capacity_limits()
            logger.info(f"🔍 용량 거버넌스 상태: {capacity_status}")
            
            # 2. 동등성 검증 회귀 테스트
            equivalence_status = self.integrated_system.equivalence_validator.get_equivalence_report()
            
            # 3. 결과 확인 및 상세 로깅
            integration_ok = checkpoint.overall_status
            state_ok = state_status.value.lower() == "ready"  # 대소문자 구분 없이 비교
            capacity_ok = all(capacity_status.values())
            equivalence_ok = equivalence_status['overview'].get('overall_equivalence_score', 0) >= 0.995
            
            logger.info(f"🔍 회귀 테스트 상세 결과:")
            logger.info(f"  - 통합 검사: {integration_ok}")
            logger.info(f"  - 상태 매니저: {state_ok} ({state_status.value})")
            logger.info(f"  - 용량 거버넌스: {capacity_ok} ({capacity_status})")
            logger.info(f"  - 동등성 검증: {equivalence_ok} ({equivalence_status['overview'].get('overall_equivalence_score', 0)})")
            
            regression_passed = all([integration_ok, state_ok, capacity_ok, equivalence_ok])
            
            scenario_result["success"] = regression_passed
            scenario_result["details"] = {
                "integration_check": checkpoint.overall_status,
                "state_manager": state_status.value,
                "capacity_governance": all(capacity_status.values()),
                "equivalence_validation": equivalence_status['overview'].get('overall_equivalence_score', 0) >= 0.995,
                "regression_passed": regression_passed
            }
            
            # T6: 회귀 테스트 결과 저장
            self.demo_results["t6_regression_tests"].append({
                "test_name": "기본 기능 회귀",
                "passed": regression_passed,
                "components_tested": ["integration", "state_manager", "capacity", "equivalence"],
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ 시나리오 7 완료 (T6): 회귀 테스트 {'통과' if regression_passed else '실패'}")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 7 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def demo_scenario_8_integration_validation(self):
        """시나리오 8: 통합 검증 (T6)"""
        logger.info("=== 시나리오 8: 통합 검증 (T6) ===")
        
        scenario_result = {
            "name": "통합 검증 (T6)",
            "description": "전체 시스템의 통합 상태 및 성능 검증",
            "success": False,
            "details": {},
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "duration_seconds": 0.0
        }
        
        try:
            # 1. E-stop 상태에서 시스템 복구 (T10: 웜업 윈도우 이후 자동 복구)
            if self.integrated_system.integration_status.value == "emergency_stop":
                logger.info("🔄 T10: E-stop 상태에서 시스템 복구 시도...")
                recovery_success = await self.integrated_system.recover_from_emergency_stop("시나리오 8 통합 검증")
                if not recovery_success:
                    logger.warning("⚠️ T10: 시스템 복구 실패 - 웜업 윈도우 대기 중")
                    # 웜업 윈도우 대기 후 재시도
                    await asyncio.sleep(2.0)
                    recovery_success = await self.integrated_system.recover_from_emergency_stop("시나리오 8 통합 검증 재시도")
                
                if recovery_success:
                    logger.info("✅ T10: 시스템 복구 완료 - 통합 검증 진행")
                else:
                    logger.error("❌ T10: 시스템 복구 실패 - 통합 검증 중단")
                    scenario_result["details"]["error"] = "시스템 복구 실패"
                    return
            
            # 2. READY 상태 확인 및 대기
            logger.info("⏳ READY 상태 확인 중...")
            max_wait_time = 5.0  # 최대 5초 대기
            wait_start = time.time()
            while self.integrated_system.integration_status != IntegrationStatus.READY:
                if time.time() - wait_start > max_wait_time:
                    logger.warning("⚠️ READY 상태 대기 시간 초과, 계속 진행")
                    break
                await asyncio.sleep(0.1)
            
            # 3. 전체 시스템 상태 점검
            logger.info("🔍 전체 시스템 상태 점검 중...")
            
            health_status = await self.integrated_system.health_check()
            estop_conditions = await self.integrated_system.check_emergency_stop_conditions()
            integration_report = await self.integrated_system.get_integration_report()
            
            # 2. 성능 메트릭 확인
            performance_metrics = {
                "uptime": self.integrated_system.metrics.uptime_seconds,
                "integration_score": self.integrated_system.metrics.integration_score,
                "checkpoints_passed": self.integrated_system.metrics.passed_checkpoints,
                "emergency_stops": self.integrated_system.metrics.emergency_stops
            }
            
            # 3. 통합 검증 기준 확인
            validation_criteria = {
                "health_ok": health_status["overall_health"] == "healthy",
                "no_estop": not estop_conditions["should_trigger"],
                "integration_score_ok": self.integrated_system.metrics.integration_score > 0.95,
                "system_ready": self.integrated_system.integration_status == IntegrationStatus.READY
            }
            
            # 4. 결과 확인
            integration_passed = all(validation_criteria.values())
            
            scenario_result["success"] = integration_passed
            scenario_result["details"] = {
                "health_status": health_status,
                "estop_conditions": estop_conditions,
                "performance_metrics": performance_metrics,
                "validation_criteria": validation_criteria,
                "integration_passed": integration_passed
            }
            
            # T6: 통합 검증 결과 저장
            self.demo_results["t6_regression_tests"].append({
                "test_name": "통합 검증",
                "passed": integration_passed,
                "criteria_met": sum(validation_criteria.values()),
                "total_criteria": len(validation_criteria),
                "timestamp": datetime.now().isoformat()
            })
            
            logger.info(f"✅ 시나리오 8 완료 (T6): 통합 검증 {'통과' if integration_passed else '실패'}")
            
        except Exception as e:
            logger.error(f"❌ 시나리오 8 실패: {e}")
            scenario_result["details"]["error"] = str(e)
        
        finally:
            scenario_result["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(scenario_result["start_time"])
            end_time = datetime.fromisoformat(scenario_result["end_time"])
            scenario_result["duration_seconds"] = (end_time - start_time).total_seconds()
            
            self.demo_results["scenarios"].append(scenario_result)
            self.demo_results["total_scenarios"] += 1
            
            if scenario_result["success"]:
                self.demo_results["successful_scenarios"] += 1
            else:
                self.demo_results["failed_scenarios"] += 1
    
    async def run_demo(self):
        """전체 데모 실행 - T9: READY 게이트를 시나리오 앞에 배치"""
        logger.info("🚀 DuRi 통합 안전성 시스템 데모 시작")
        
        try:
            # 1. 시스템 초기화
            if not await self.initialize_system():
                logger.error("❌ 시스템 초기화 실패로 데모를 중단합니다")
                return False
            
            # T9: READY 게이트를 시나리오 시작 전에 배치 (타이밍 경쟁 제거)
            logger.info("⏳ T9: READY 게이트 대기 중...")
            ready_wait_start = time.time()
            
            # StateManager가 READY 상태가 될 때까지 대기
            if self.state_manager:
                max_wait_time = 10.0  # 최대 10초 대기
                while self.state_manager.current_state.value != "ready":
                    if time.time() - ready_wait_start > max_wait_time:
                        logger.warning("⚠️ T9: READY 상태 대기 시간 초과, 계속 진행")
                        break
                    await asyncio.sleep(0.1)
                
                ready_wait_duration = time.time() - ready_wait_start
                logger.info(f"✅ T9: READY 게이트 통과 완료 (대기 시간: {ready_wait_duration:.2f}초)")
            else:
                logger.info("ℹ️ T9: StateManager 없음, READY 게이트 건너뜀")
            
            # 2. 데모 시나리오 실행 (T9: READY 게이트 이후)
            logger.info("🎯 T9: READY 게이트 완료, 시나리오 실행 시작")
            await self.demo_scenario_1_basic_operations()
            await self.demo_scenario_2_capacity_governance()
            await self.demo_scenario_3_safety_monitoring()
            await self.demo_scenario_4_emergency_response()
            await self.demo_scenario_5_hysteresis_test()
            await self.demo_scenario_6_estop_policy_test()
            await self.demo_scenario_7_regression_test()
            await self.demo_scenario_8_integration_validation()
            
            # 3. 데모 결과 정리
            self.demo_results["end_time"] = datetime.now().isoformat()
            start_time = datetime.fromisoformat(self.demo_results["start_time"])
            end_time = datetime.fromisoformat(self.demo_results["end_time"])
            self.demo_results["duration_seconds"] = (end_time - start_time).total_seconds()
            
            # 4. 결과 출력
            self._print_demo_results()
            
            # 5. 결과를 JSON 파일로 저장
            self._save_demo_results()
            
            logger.info("🎉 DuRi 통합 안전성 시스템 데모 완료")
            return True
            
        except Exception as e:
            logger.error(f"❌ 데모 실행 중 오류 발생: {e}")
            traceback.print_exc()
            return False
    
    def _print_demo_results(self):
        """데모 결과 출력"""
        print("\n" + "="*60)
        print("🎯 DuRi 통합 안전성 시스템 데모 결과")
        print("="*60)
        
        print(f"\n📊 전체 요약:")
        print(f"   총 시나리오: {self.demo_results['total_scenarios']}")
        print(f"   성공: {self.demo_results['successful_scenarios']}")
        print(f"   실패: {self.demo_results['failed_scenarios']}")
        print(f"   소요 시간: {self.demo_results['duration_seconds']:.2f}초")
        
        print(f"\n📋 시나리오별 결과:")
        for i, scenario in enumerate(self.demo_results["scenarios"], 1):
            status_icon = "✅" if scenario["success"] else "❌"
            print(f"   {i}. {status_icon} {scenario['name']}")
            print(f"      소요 시간: {scenario['duration_seconds']:.2f}초")
            if not scenario["success"] and "error" in scenario["details"]:
                print(f"      오류: {scenario['details']['error']}")
        
        print(f"\n🏆 성공률: {(self.demo_results['successful_scenarios'] / self.demo_results['total_scenarios'] * 100):.1f}%")
    
    def _save_demo_results(self):
        """데모 결과를 JSON 파일로 저장"""
        try:
            results_file = f"demo_results_integrated_safety_system_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(self.demo_results, f, ensure_ascii=False, indent=2, default=str)
            
            logger.info(f"📁 데모 결과가 {results_file}에 저장되었습니다")
            
        except Exception as e:
            logger.error(f"❌ 데모 결과 저장 실패: {e}")

async def main():
    """메인 함수"""
    
    print("🚀 DuRi 통합 안전성 시스템 데모를 시작합니다...")
    print("이 데모는 다음 기능들을 시연합니다:")
    print("  • 안전성 프레임워크")
    print("  • 용량 거버넌스 시스템")
    print("  • 동등성 검증 시스템")
    print("  • 통합 안전성 관리")
    print()
    
    # 데모 실행
    demo = SafetySystemDemo()
    success = await demo.run_demo()
    
    if success:
        print("\n🎉 데모가 성공적으로 완료되었습니다!")
    else:
        print("\n❌ 데모 실행 중 문제가 발생했습니다.")
    
    return success

if __name__ == "__main__":
    # 데모 실행
    asyncio.run(main())
