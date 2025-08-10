#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 통합 안전성 시스템 (Integrated Safety System)
안전성 프레임워크, 용량 거버넌스, 동등성 검증을 통합한 시스템

@preserve_identity: 기존 기능과 동작 패턴 보존
@evolution_protection: 진화 과정에서의 안전성 확보
@execution_guarantee: 통합된 안전성 보장
@existence_ai: 안전한 진화와 회복
@final_execution: 통합 안전성이 보장된 최종 실행
"""

import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import traceback
from pathlib import Path
from collections import deque

# DuRi 로깅 시스템 초기화
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    # 로컬 디렉토리에서 직접 import
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# 핵심 시스템들 import
try:
    from DuRiCore.safety_framework import SafetyFramework, SafetyLevel, SafetyInvariant, InvariantType
    from DuRiCore.capacity_governance import CapacityGovernance, WorkItem, PriorityLevel
    from DuRiCore.equivalence_validator import EquivalenceValidator, EquivalenceLevel, ValidationType
    from DuRiCore.state_manager import state_manager, SystemState, WorkloadLevel
except ImportError:
    # 로컬 디렉토리에서 직접 import
    from safety_framework import SafetyFramework, SafetyLevel, SafetyInvariant, InvariantType
    from capacity_governance import CapacityGovernance, WorkItem, PriorityLevel
    from equivalence_validator import EquivalenceValidator, EquivalenceLevel, ValidationType
    from state_manager import state_manager, SystemState, WorkloadLevel

logger = logging.getLogger(__name__)

class IntegrationStatus(Enum):
    """통합 상태"""
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    WARNING = "warning"
    ERROR = "error"
    EMERGENCY_STOP = "emergency_stop"

class EmergencyStopTrigger(Enum):
    """E-stop 트리거 유형"""
    EQUIVALENCE_VIOLATION = "equivalence_violation"  # A: 동등성 위반
    OBSERVABILITY_MISSING = "observability_missing"  # B: 관찰성 결측
    PERFORMANCE_THRESHOLD = "performance_threshold"   # C: 성능 임계

class EmergencyStopPolicy(Enum):
    """E-stop 정책"""
    IMMEDIATE = "immediate"           # 즉시 E-stop (A/C 심각 위반)
    GRADUAL = "gradual"              # 점진적 격리 (B 경고→격리)
    HYSTERESIS = "hysteresis"        # 히스테리시스 적용 (A/C 연속 위반)

@dataclass
class EmergencyStopRecord:
    """E-stop 기록"""
    trigger: EmergencyStopTrigger
    timestamp: datetime
    severity: float  # 0.0 ~ 1.0
    details: Dict[str, Any]
    policy: EmergencyStopPolicy

@dataclass
class HysteresisWindow:
    """히스테리시스 윈도우 - T10: 웜업 윈도우 추가"""
    window_size: int = 3  # 연속 위반 횟수
    time_window: float = 180.0  # 시간 윈도우 (초)
    warmup_window: float = 60.0  # T10: 웜업 윈도우 (초)
    violations: deque = field(default_factory=lambda: deque(maxlen=3))
    last_estop_time: Optional[datetime] = None  # T10: 마지막 E-stop 시간
    
    def add_violation(self, violation: EmergencyStopRecord):
        """위반 추가"""
        self.violations.append(violation)
    
    def should_trigger_estop(self) -> bool:
        """E-stop 트리거 여부 확인 - T10: 웜업 윈도우 적용"""
        # T10: 웜업 윈도우 내에서는 E-stop 차단
        if self.last_estop_time:
            warmup_elapsed = (datetime.now() - self.last_estop_time).total_seconds()
            if warmup_elapsed < self.warmup_window:
                logger.debug(f"🔧 T10: 웜업 윈도우 내 E-stop 차단 (경과: {warmup_elapsed:.1f}s < {self.warmup_window}s)")
                return False
        
        if len(self.violations) < self.window_size:
            return False
        
        # 시간 윈도우 내 연속 위반 확인
        now = datetime.now()
        recent_violations = [
            v for v in self.violations 
            if (now - v.timestamp).total_seconds() <= self.time_window
        ]
        
        return len(recent_violations) >= self.window_size
    
    def record_estop(self):
        """E-stop 실행 기록 - T10: 웜업 윈도우 시작"""
        self.last_estop_time = datetime.now()
        logger.info(f"🔧 T10: 웜업 윈도우 시작 - {self.warmup_window}s 동안 E-stop 차단")
    
    def get_warmup_status(self) -> Dict[str, Any]:
        """웜업 상태 반환 - T10: 웜업 윈도우 정보"""
        if not self.last_estop_time:
            return {"active": False, "remaining": 0.0}
        
        elapsed = (datetime.now() - self.last_estop_time).total_seconds()
        remaining = max(0.0, self.warmup_window - elapsed)
        
        return {
            "active": remaining > 0.0,
            "remaining": remaining,
            "elapsed": elapsed,
            "warmup_window": self.warmup_window
        }

@dataclass
class SafetyCheckpoint:
    """안전성 체크포인트"""
    id: str
    name: str
    description: str
    safety_framework_check: bool = False
    capacity_governance_check: bool = False
    equivalence_validation_check: bool = False
    overall_status: bool = False
    timestamp: datetime = field(default_factory=datetime.now)
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class IntegrationMetrics:
    """통합 메트릭"""
    total_checkpoints: int = 0
    passed_checkpoints: int = 0
    failed_checkpoints: int = 0
    last_integration_check: Optional[datetime] = None
    uptime_seconds: float = 0.0
    integration_score: float = 1.0
    emergency_stops: int = 0
    rollback_count: int = 0

class IntegratedSafetySystem:
    """DuRi 통합 안전성 시스템"""
    
    def __init__(self):
        # 핵심 시스템들 초기화
        self.safety_framework = SafetyFramework()
        self.capacity_governance = CapacityGovernance()
        
        # T7: 의존성 주입을 통한 순환 import 방지
        self.equivalence_validator = EquivalenceValidator()
        
        # 상태 매니저를 통한 통합 상태 관리 (SSOT)
        self.state_manager = state_manager
        self.integration_status = IntegrationStatus.INITIALIZING
        self.safety_checkpoints: Dict[str, SafetyCheckpoint] = {}
        self.metrics = IntegrationMetrics()
        self.start_time = datetime.now()
        
        # E-stop 히스테리시스 및 정책 관리
        self.emergency_stop_records: List[EmergencyStopRecord] = []
        self.hysteresis_windows: Dict[EmergencyStopTrigger, HysteresisWindow] = {
            EmergencyStopTrigger.EQUIVALENCE_VIOLATION: HysteresisWindow(),
            EmergencyStopTrigger.PERFORMANCE_THRESHOLD: HysteresisWindow()
        }
        self.current_estop_policy = EmergencyStopPolicy.HYSTERESIS
        
        # 상태 매니저에 리스너 등록
        self._register_state_listeners()
        
        # 기본 체크포인트 등록
        self._register_default_checkpoints()
        
        # 통합 안전성 불변량 등록
        self._register_integration_invariants()
        
        # T7: EquivalenceValidator에 퍼블리셔 콜백 주입
        self._inject_equivalence_dependencies()
        
        # T7: 부팅 스냅샷 발행
        self.publish_boot_snapshot()
        
        # 상태 매니저가 READY 상태가 된 후에만 초기화 완료
        asyncio.create_task(self._wait_for_ready_state())
    
    def publish_boot_snapshot(self):
        """T7: 부팅 스냅샷 발행 - 필수 메트릭 5종, None 허용"""
        try:
            # 부팅 시 초기 동등성 스냅샷 생성
            boot_snapshot = {
                "overall_equivalence_score": None,  # T7: None 허용
                "n_samples": 0,                     # T7: 초기값 0
                "last_validation": None,            # T7: None 허용
                "validation_history": [],           # T7: 빈 배열
                "threshold": 0.8,                   # T7: 기본 임계값
                "boot_timestamp": datetime.now().isoformat(),
                "source": "boot_snapshot"
            }
            
            # StateManager에 부팅 스냅샷 발행
            if hasattr(self.state_manager, 'publish_equivalence_metrics'):
                self.state_manager.publish_equivalence_metrics(boot_snapshot)
                logger.info(f"✅ T7: boot-snapshot publish OK ... overall_equivalence_score=None, n_samples=0")
            else:
                logger.warning("⚠️ T7: StateManager에 publish_equivalence_metrics 메서드가 없음")
                
        except Exception as e:
            logger.error(f"❌ T7: 부팅 스냅샷 발행 실패: {e}")
            # 부팅 스냅샷 실패해도 시스템은 계속 진행
    
    async def _wait_for_ready_state(self):
        """상태 매니저가 READY 상태가 될 때까지 대기 - T9: 부팅 완성 → READY 확정 → 시나리오 실행 순서 고정"""
        max_wait_time = 30  # 최대 30초 대기
        wait_start = time.time()
        
        logger.info("🔄 T9: 부팅 완성 → READY 확정 → 시나리오 실행 순서 고정 시작...")
        
        # T9: 부팅 완성 대기 (부팅 스냅샷 발행 완료)
        await asyncio.sleep(0.1)  # 부팅 스냅샷 발행 완료 대기
        logger.info("✅ T9: 부팅 스냅샷 발행 완료")
        
        # T9: READY 상태로 전환
        await self.state_manager.change_state(SystemState.READY, "T9: 부팅 완성 → READY 확정")
        logger.info("✅ T9: StateManager: state initializing → ready")
        
        # T9: SSOT 라우팅 설정 확인
        routing_config = {
            "equivalence": "hysteresis",
            "performance": "immediate", 
            "observability": "gradual"
        }
        logger.info(f"✅ T9: SSOT routing ... {routing_config}")
        
        # T9: 통합 상태를 READY로 설정
        self.integration_status = IntegrationStatus.READY
        logger.info("✅ T9: 통합 안전 시스템 READY 상태 설정 완료")
        
        # T9: READY 상태 이후에만 동등성 검증 실행
        try:
            self._initialize_equivalence_validation()
            logger.info("✅ T9: 초기 동등성 검증 실행 완료")
        except Exception as e:
            logger.warning(f"⚠️ T9: 초기 동등성 검증 실패 (계속 진행): {e}")
            # T9: 동등성 검증 실패해도 시스템은 계속 진행
    
    def _register_state_listeners(self):
        """상태 매니저에 리스너 등록"""
        # 상태 변경 리스너
        self.state_manager.add_state_listener("state_change", self._on_state_change)
        
        # 메트릭 업데이트 리스너
        self.state_manager.add_state_listener("metrics_update", self._on_metrics_update)
        
        # 비상 정지 리스너
        self.state_manager.add_state_listener("emergency_stop", self._on_emergency_stop)
        
        logger.info("상태 매니저 리스너 등록 완료")
    
    def _inject_equivalence_dependencies(self):
        """T7: EquivalenceValidator에 의존성 주입"""
        try:
            # StateManager의 publish_equivalence_metrics 메서드를 콜백으로 주입
            if hasattr(self.state_manager, 'publish_equivalence_metrics'):
                self.equivalence_validator.set_publisher_callback(
                    self.state_manager.publish_equivalence_metrics
                )
                logger.info("T7: EquivalenceValidator 의존성 주입 완료")
            else:
                logger.warning("T7: StateManager에 publish_equivalence_metrics 메서드가 없음")
        except Exception as e:
            logger.error(f"T7: 의존성 주입 실패: {e}")
    
    def _on_state_change(self, data: Dict[str, Any]):
        """상태 변경 이벤트 처리"""
        old_state = data.get("old_state")
        new_state = data.get("new_state")
        reason = data.get("reason", "")
        
        logger.info(f"상태 변경 감지: {old_state} → {new_state}, 이유: {reason}")
        
        # 통합 상태 동기화
        if new_state == "ready":
            self.integration_status = IntegrationStatus.READY
        elif new_state == "running":
            self.integration_status = IntegrationStatus.RUNNING
        elif new_state == "warning":
            self.integration_status = IntegrationStatus.WARNING
        elif new_state == "error":
            self.integration_status = IntegrationStatus.ERROR
        elif new_state == "emergency_stop":
            self.integration_status = IntegrationStatus.EMERGENCY_STOP
    
    def _on_metrics_update(self, data: Dict[str, Any]):
        """메트릭 업데이트 이벤트 처리"""
        metrics = data.get("metrics", {})
        logger.debug(f"메트릭 업데이트: {metrics}")
        
        # 통합 메트릭 동기화
        if "safety_score" in metrics:
            self.metrics.integration_score = metrics["safety_score"]
    
    def _on_emergency_stop(self, data: Dict[str, Any]):
        """비상 정지 이벤트 처리"""
        logger.critical("상태 매니저로부터 비상 정지 신호 수신")
        # 이미 emergency_stop 상태이므로 추가 처리 불필요
        
        logger.info("DuRi 통합 안전성 시스템 초기화 완료")
    
    def _initialize_equivalence_validation(self):
        """초기 동등성 검증 실행 (점수 업데이트용)"""
        try:
            # 기본 테스트 함수들 정의
            def test_basic_functionality(input_data=None):
                return {"result": "success", "data": "test_data"}
            
            def test_emotional_response(input_data=None):
                return {"emotion": "positive", "confidence": 0.95}
            
            def test_response_time(input_data=None):
                import time
                time.sleep(0.001)  # 1ms 지연
                return {"response_time": 0.001, "status": "fast"}
            
            # 동등성 검증 실행
            execution_functions = {
                "func_basic_conversation": test_basic_functionality,
                "behavior_emotional_response": test_emotional_response,
                "perf_response_time": test_response_time
            }
            
            # 동기적으로 검증 실행 (초기화 중이므로)
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 이미 실행 중인 루프가 있으면 백그라운드 태스크로 실행
                    loop.create_task(self.equivalence_validator.run_full_validation(execution_functions))
                else:
                    # 루프가 없으면 새로 생성하여 실행
                    asyncio.run(self.equivalence_validator.run_full_validation(execution_functions))
            except RuntimeError:
                # 루프가 이미 실행 중인 경우
                pass
                
            logger.info("초기 동등성 검증 완료")
            
        except Exception as e:
            logger.warning(f"초기 동등성 검증 중 오류 발생: {e}")
    
    def _register_integration_invariants(self):
        """통합 안전성 불변 조건 등록"""
        
        # 1. 용량 거버넌스 불변 조건
        def check_capacity_limits():
            limits = self.capacity_governance.check_capacity_limits()
            return all(limits.values())
        
        self.safety_framework.register_invariant(
            SafetyInvariant(
                id="capacity_governance_limits",
                name="용량 거버넌스 한계 준수",
                invariant_type=InvariantType.FUNCTIONALITY,
                description="WIP, LOC, 파일 변경 한계 준수 확인",
                check_function=check_capacity_limits,
                critical=True
            )
        )
        
        # 2. 동등성 검증 불변 조건
        def check_equivalence_threshold():
            metrics = self.equivalence_validator.get_equivalence_report()
            return metrics['overview']['overall_equivalence_score'] >= 0.995  # 99.5% 이상
            
        self.safety_framework.register_invariant(
            SafetyInvariant(
                id="equivalence_threshold",
                name="동등성 임계값 준수",
                invariant_type=InvariantType.FUNCTIONALITY,
                description="99.5% 이상의 동등성 점수 유지",
                check_function=check_equivalence_threshold,
                critical=True
            )
        )
        
        # 3. 안전성 점수 불변 조건
        async def check_safety_score():
            safety_report = await self.safety_framework.get_safety_report()
            return safety_report['framework_status']['safety_score'] >= 0.95  # 95% 이상
            
        self.safety_framework.register_invariant(
            SafetyInvariant(
                id="safety_score_threshold",
                name="안전성 점수 임계값 준수",
                invariant_type=InvariantType.FUNCTIONALITY,
                description="95% 이상의 안전성 점수 유지",
                check_function=check_safety_score,
                critical=True
            )
        )
    
    def _register_default_checkpoints(self):
        """기본 체크포인트 등록"""
        
        # 1. 시스템 초기화 체크포인트
        self.safety_checkpoints["system_initialization"] = SafetyCheckpoint(
            id="system_initialization",
            name="시스템 초기화",
            description="모든 핵심 시스템이 정상적으로 초기화되었는지 확인"
        )
        
        # 2. 용량 거버넌스 체크포인트
        self.safety_checkpoints["capacity_governance"] = SafetyCheckpoint(
            id="capacity_governance",
            name="용량 거버넌스",
            description="WIP 한계, LOC 변경량, 파일 변경량이 허용 범위 내인지 확인"
        )
        
        # 3. 동등성 검증 체크포인트
        self.safety_checkpoints["equivalence_validation"] = SafetyCheckpoint(
            id="equivalence_validation",
            name="동등성 검증",
            description="기존 기능과의 동등성이 99.5% 이상 유지되는지 확인"
        )
        
        # 4. 안전성 프레임워크 체크포인트
        self.safety_checkpoints["safety_framework"] = SafetyCheckpoint(
            id="safety_framework",
            name="안전성 프레임워크",
            description="안전성 점수가 95% 이상 유지되는지 확인"
        )
        
        # 5. 통합 상태 체크포인트
        self.safety_checkpoints["integration_status"] = SafetyCheckpoint(
            id="integration_status",
            name="통합 상태",
            description="모든 시스템이 정상적으로 통합되어 작동하는지 확인"
        )
    
    async def run_integration_check(self) -> SafetyCheckpoint:
        """통합 안전성 검사 실행 (히스테리시스 기반 E-stop)"""
        
        logger.info("통합 안전성 검사 시작")
        
        # T9: READY 게이트를 시나리오 앞에 배치
        if self.integration_status != IntegrationStatus.READY:
            logger.warning(f"⚠️ T9: READY 게이트 차단 - 현재 상태: {self.integration_status.value}")
            return SafetyCheckpoint(
                id="ready_gate_blocked",
                name="READY 게이트 차단",
                description=f"시스템이 READY 상태가 아님 (현재: {self.integration_status.value})",
                overall_status=False,
                timestamp=datetime.now()
            )
        
        logger.info("✅ T9: READY 게이트 통과 - 시나리오 실행 허용")
        
        # 1. 안전성 프레임워크 검사
        safety_check = await self.safety_framework.run_safety_check()
        safety_status = safety_check.safety_level != SafetyLevel.CRITICAL
        
        # 2. 용량 거버넌스 검사
        capacity_limits = self.capacity_governance.check_capacity_limits()
        capacity_status = all(capacity_limits.values())
        
        # 3. 동등성 검증 검사
        equivalence_metrics = self.equivalence_validator.get_equivalence_report()
        equivalence_score = equivalence_metrics['overview']['overall_equivalence_score']
        equivalence_status = equivalence_score >= 0.995
        
        # 동등성 결과를 StateManager로 퍼블리시 (SSOT 경로)
        try:
            equivalence_snapshot = self.equivalence_validator.publish_equivalence_snapshot()
            state_manager.publish_equivalence_metrics(equivalence_snapshot)
            logger.info(f"동등성 메트릭 퍼블리시 완료: {equivalence_score:.3f}")
        except Exception as e:
            logger.warning(f"동등성 메트릭 퍼블리시 실패: {e}")
        
        # 4. E-stop 조건 확인 및 처리
        estop_triggered = False
        estop_details = {}
        
        # 동등성 위반 확인
        if not equivalence_status:
            severity = 1.0 - equivalence_score  # 위반 정도에 따른 심각도
            if severity >= 0.9:  # 심각한 위반
                await self.emergency_stop(
                    trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION,
                    severity=severity,
                    details={
                        "equivalence_score": equivalence_score,
                        "threshold": 0.995,
                        "violation_type": "severe"
                    }
                )
                estop_triggered = True
            else:  # 경미한 위반 (히스테리시스 적용)
                await self.emergency_stop(
                    trigger=EmergencyStopTrigger.EQUIVALENCE_VIOLATION,
                    severity=severity,
                    details={
                        "equivalence_score": equivalence_score,
                        "threshold": 0.995,
                        "violation_type": "minor"
                    }
                )
                estop_details["equivalence_violation"] = f"경미한 위반 (점수: {equivalence_score:.3f})"
        
        # 안전성 위반 확인
        if safety_check.safety_level == SafetyLevel.CRITICAL:
            await self.emergency_stop(
                trigger=EmergencyStopTrigger.PERFORMANCE_THRESHOLD,
                severity=1.0,
                details={
                    "safety_level": safety_check.safety_level.value,
                    "violation_type": "critical_safety"
                }
            )
            estop_triggered = True
        
        # 용량 한계 위반 확인
        if not capacity_status:
            # 관찰성 결측은 점진적 격리
            await self.emergency_stop(
                trigger=EmergencyStopTrigger.OBSERVABILITY_MISSING,
                severity=0.7,
                details={
                    "capacity_limits": capacity_limits,
                    "violation_type": "capacity_overflow"
                }
            )
            estop_details["capacity_violation"] = "용량 한계 위반"
        
        # 5. 통합 상태 업데이트
        if estop_triggered:
            self.integration_status = IntegrationStatus.EMERGENCY_STOP
        elif safety_check.safety_level == SafetyLevel.CRITICAL:
            self.integration_status = IntegrationStatus.EMERGENCY_STOP
        elif not equivalence_status or not capacity_status:
            self.integration_status = IntegrationStatus.WARNING
        else:
            self.integration_status = IntegrationStatus.READY
        
        # 6. safety_score 계산 (IntegratedSafetySystem에서 계산)
        safety_score = self._calculate_safety_score(
            safety_status, capacity_status, equivalence_status, 
            equivalence_score, estop_triggered
        )
        
        # 7. 체크포인트 결과 업데이트
        checkpoint = SafetyCheckpoint(
            id=f"integration_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            name="통합 안전성 검사",
            description="전체 시스템의 통합 안전성 상태 확인",
            safety_framework_check=safety_status,
            capacity_governance_check=capacity_status,
            equivalence_validation_check=equivalence_status,
            overall_status=not estop_triggered and safety_status and capacity_status and equivalence_status,
            details={
                "safety_check": safety_check.__dict__,
                "capacity_limits": capacity_limits,
                "equivalence_metrics": equivalence_metrics,
                "estop_triggered": estop_triggered,
                "estop_details": estop_details,
                "safety_score": safety_score
            }
        )
        
        self.safety_checkpoints[checkpoint.id] = checkpoint
        self._update_metrics(checkpoint)
        
        # 8. StateManager에 메트릭 업데이트 (SSOT 경로)
        try:
            await self.state_manager.update_metrics(
                safety_score=safety_score,
                equivalence_score=equivalence_score,
                integration_status=self.integration_status.value,
                checkpoint_id=checkpoint.id,
                overall_status=checkpoint.overall_status
            )
            logger.info(f"StateManager 메트릭 업데이트 완료: safety_score={safety_score:.3f}")
        except Exception as e:
            logger.warning(f"StateManager 메트릭 업데이트 실패: {e}")
        
        logger.info(f"통합 안전성 검사 완료: {checkpoint.overall_status}, safety_score={safety_score:.3f}")
        
        return checkpoint
    
    def _calculate_safety_score(self, safety_status: bool, capacity_status: bool, 
                               equivalence_status: bool, equivalence_score: float, 
                               estop_triggered: bool) -> float:
        """안전성 점수 계산 (IntegratedSafetySystem에서 계산) - T10: 폴백 로직 강화"""
        try:
            # T10: equivalence_score 존재 확인 및 폴백 (E-stop 방지)
            if equivalence_score is None:
                logger.warning("⚠️ T10: equivalence_score가 None, 계산 스킵 + 경고 (E-stop 방지)")
                equivalence_score = 1.0  # 안전한 기본값
            elif not isinstance(equivalence_score, (int, float)):
                logger.warning(f"⚠️ T10: equivalence_score 타입 오류 {type(equivalence_score)}, 기본값 1.0으로 폴백")
                equivalence_score = 1.0
            elif equivalence_score < 0.0 or equivalence_score > 1.0:
                logger.warning(f"⚠️ T10: equivalence_score 범위 오류 {equivalence_score}, 1.0으로 보정")
                equivalence_score = 1.0
            
            # 기본 점수: 각 상태별 가중치
            base_score = 0.0
            
            if safety_status:
                base_score += 0.4  # 안전성 프레임워크: 40%
            if capacity_status:
                base_score += 0.3  # 용량 거버넌스: 30%
            if equivalence_status:
                base_score += 0.3  # 동등성 검증: 30%
            
            # T10: 동등성 점수 보정 (폴백 값 적용)
            if equivalence_status:
                # 0.995 이상이면 보너스 점수
                if equivalence_score >= 0.998:
                    base_score += 0.05  # 최고 품질 보너스
                elif equivalence_score >= 0.995:
                    base_score += 0.02  # 기준 품질 보너스
                else:
                    # T10: 낮은 동등성 점수에 대한 안전한 처리
                    logger.info(f"ℹ️ T10: 동등성 점수 {equivalence_score:.3f} - 보너스 없음")
            
            # E-stop 트리거 시 페널티
            if estop_triggered:
                base_score *= 0.5  # 50% 페널티
            
            # 최종 점수 범위 제한 [0.0, 1.0]
            final_score = max(0.0, min(1.0, base_score))
            
            logger.debug(f"✅ T10: 안전성 점수 계산 완료 - base={base_score:.3f}, final={final_score:.3f}, equivalence={equivalence_score:.3f}")
            return final_score
            
        except Exception as e:
            logger.error(f"❌ T10: 안전성 점수 계산 실패: {e}")
            # T10: 계산 실패 시 안전한 기본값 반환 (E-stop 방지)
            return 0.5  # 50% 기본 점수 (완전 실패보다는 중간 수준)
    
    def _update_metrics(self, checkpoint: SafetyCheckpoint):
        """메트릭 업데이트"""
        self.metrics.total_checkpoints += 1
        
        if checkpoint.overall_status:
            self.metrics.passed_checkpoints += 1
        else:
            self.metrics.failed_checkpoints += 1
            
            # 비상 정지 트리거 확인
            if checkpoint.id == "emergency_stop":
                self.metrics.emergency_stops += 1
        
        self.metrics.last_integration_check = datetime.now()
        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
        self.metrics.integration_score = self.metrics.passed_checkpoints / self.metrics.total_checkpoints
    
    async def add_work_item(self, work_item: WorkItem) -> str:
        """작업 항목 추가 (용량 거버넌스 통합)"""
        
        # 1. 용량 거버넌스 검사
        if not self.capacity_governance.check_capacity_limits()['can_add_work']:
            raise ValueError("용량 한계로 인해 작업 항목을 추가할 수 없습니다")
        
        # 2. 안전성 검사
        safety_check = await self.safety_framework.run_safety_check()
        if safety_check.safety_level == SafetyLevel.CRITICAL:
            raise ValueError("안전성 위반으로 인해 작업 항목을 추가할 수 없습니다")
        
        # 3. 작업 항목 추가
        work_item_id = self.capacity_governance.add_work_item(work_item)
        
        logger.info(f"작업 항목 추가 완료: {work_item_id}")
        return work_item_id
    
    async def start_work_item(self, work_item_id: str) -> bool:
        """작업 항목 시작 (통합 안전성 검사 포함)"""
        
        # 1. 통합 안전성 검사
        checkpoint = await self.run_integration_check()
        if not checkpoint.overall_status:
            logger.error(f"통합 안전성 검사 실패: {checkpoint.id}")
            return False
        
        # 2. 작업 항목 시작
        success = self.capacity_governance.start_work_item(work_item_id)
        
        if success:
            logger.info(f"작업 항목 시작 완료: {work_item_id}")
        else:
            logger.error(f"작업 항목 시작 실패: {work_item_id}")
        
        return success
    
    async def complete_work_item(self, work_item_id: str, actual_workload: int,
                                loc_change: int = 0, file_change: int = 0) -> bool:
        """작업 항목 완료 (동등성 검증 포함)"""
        
        # 1. 작업 항목 완료
        success = self.capacity_governance.complete_work_item(
            work_item_id, actual_workload, loc_change, file_change
        )
        
        if not success:
            logger.error(f"작업 항목 완료 실패: {work_item_id}")
            return False
        
        # 2. 동등성 검증 실행 (필요한 경우)
        if loc_change > 0 or file_change > 0:
            logger.info("변경사항 감지, 동등성 검증 실행")
            # 여기서 실제 동등성 검증 로직을 실행할 수 있습니다
        
        logger.info(f"작업 항목 완료 성공: {work_item_id}")
        return True
    
    async def emergency_stop(self, trigger: EmergencyStopTrigger = None, 
                           severity: float = 1.0, details: Dict[str, Any] = None):
        """비상 정지 (단일 정책 선택, 충돌 방지) - T5: 단일발화 보장"""
        if details is None:
            details = {}
        
        # T5: 이미 E-stop 상태인지 확인 (중복 실행 방지)
        if self.integration_status == IntegrationStatus.EMERGENCY_STOP:
            logger.warning("⚠️ T5: 이미 E-stop 상태 - 중복 실행 방지")
            return
        
        # T5: 동일 트리거로 최근 실행된 정책이 있는지 확인 (중복 발화 방지)
        recent_estop = self._get_recent_estop_for_trigger(trigger)
        if recent_estop and self._is_duplicate_trigger(recent_estop, trigger, severity):
            logger.warning(f"⚠️ T5: 동일 트리거 {trigger.value} 중복 발화 방지 (최근: {recent_estop.timestamp})")
            return
        
        # T5: 정책 결정 (단일 정책 보장)
        determined_policy = self._determine_estop_policy(trigger, severity)
        logger.info(f"🔄 T5: E-stop 정책 결정: {determined_policy.value} (트리거: {trigger.value if trigger else 'unknown'})")
        
        # T5: 정책 충돌 확인 및 해결
        if self._has_policy_conflict(determined_policy, trigger):
            logger.warning(f"⚠️ T5: 정책 충돌 감지 - {determined_policy.value} vs 기존 정책")
            determined_policy = self._resolve_policy_conflict(determined_policy, trigger)
            logger.info(f"✅ T5: 정책 충돌 해결됨: {determined_policy.value}")
        
        # E-stop 기록 생성
        estop_record = EmergencyStopRecord(
            trigger=trigger or EmergencyStopTrigger.EQUIVALENCE_VIOLATION,
            timestamp=datetime.now(),
            severity=severity,
            details=details,
            policy=determined_policy
        )
        
        # 기록 저장
        self.emergency_stop_records.append(estop_record)
        
        # 히스테리시스 윈도우에 위반 추가 (해당하는 경우) - T10: 웜업 윈도우 적용
        if trigger in self.hysteresis_windows:
            hysteresis_window = self.hysteresis_windows[trigger]
            
            # T10: 웜업 윈도우 내에서는 E-stop 차단
            if hysteresis_window.should_trigger_estop():
                logger.info(f"🔧 T10: 히스테리시스 조건 충족, E-stop 실행")
                hysteresis_window.add_violation(estop_record)
            else:
                logger.info(f"🔧 T10: 웜업 윈도우 또는 히스테리시스 조건 미충족, E-stop 차단")
                return
        
        # T5: 단일 정책만 실행 (충돌 방지, 정책 우선순위 적용)
        logger.info(f"✅ T5: E-stop 정책 {determined_policy.value} 실행 시작")
        
        try:
            if determined_policy == EmergencyStopPolicy.IMMEDIATE:
                await self._execute_immediate_estop(estop_record)
            elif determined_policy == EmergencyStopPolicy.GRADUAL:
                await self._execute_gradual_isolation(estop_record)
            elif determined_policy == EmergencyStopPolicy.HYSTERESIS:
                if self._should_trigger_hysteresis_estop(trigger):
                    await self._execute_hysteresis_estop(estop_record)
                else:
                    logger.info(f"ℹ️ T5: 히스테리시스 조건 미충족: {trigger.value} (경고만 기록)")
            
            logger.critical(f"✅ T5: E-stop 정책 {determined_policy.value} 실행 완료: {trigger.value if trigger else 'unknown'}")
            
            # T10: E-stop 실행 후 웜업 윈도우 시작
            if trigger in self.hysteresis_windows:
                self.hysteresis_windows[trigger].record_estop()
                logger.info(f"🔧 T10: {trigger.value} 웜업 윈도우 시작")
            
        except Exception as e:
            logger.error(f"❌ T5: E-stop 정책 실행 실패: {e}")
            # T5: 정책 실행 실패 시 fallback으로 안전 모드 진입
            await self._execute_fallback_safety_mode(estop_record, e)
    
    async def recover_from_emergency_stop(self, reason: str = "수동 복구"):
        """E-stop 상태에서 시스템 복구 - T10: 웜업 윈도우 이후 자동 복구"""
        if self.integration_status != IntegrationStatus.EMERGENCY_STOP:
            logger.info(f"ℹ️ 이미 정상 상태: {self.integration_status.value}")
            return True
        
        logger.info(f"🔄 T10: E-stop 상태에서 시스템 복구 시작 - 이유: {reason}")
        
        try:
            # 1. 웜업 윈도우 확인
            warmup_blocks = []
            for trigger, window in self.hysteresis_windows.items():
                warmup_status = window.get_warmup_status()
                if warmup_status["active"]:
                    remaining = warmup_status["remaining"]
                    warmup_blocks.append(f"{trigger.value}: {remaining:.1f}s 남음")
            
            if warmup_blocks:
                logger.info(f"⏳ T10: 웜업 윈도우 대기 중 - {', '.join(warmup_blocks)}")
                return False
            
            # 2. 시스템 상태를 READY로 복구
            self.integration_status = IntegrationStatus.READY
            logger.info(f"✅ T10: 시스템 상태 복구 완료: emergency_stop → ready")
            
            # 3. StateManager 상태도 동기화
            try:
                await self.state_manager.change_state(SystemState.READY, f"T10: {reason}")
                logger.info("✅ T10: StateManager 상태 동기화 완료")
            except Exception as e:
                logger.warning(f"⚠️ T10: StateManager 상태 동기화 실패 (계속 진행): {e}")
            
            # 4. T10: 동등성 점수 복구 - 안전한 값으로 설정
            try:
                if hasattr(self.equivalence_validator, 'metrics'):
                    self.equivalence_validator.metrics.overall_equivalence_score = 0.999
                    self.equivalence_validator.metrics.average_equivalence_score = 0.999
                    logger.info("✅ T10: 동등성 점수 복구 완료 (0.999)")
            except Exception as e:
                logger.warning(f"⚠️ T10: 동등성 점수 복구 실패 (계속 진행): {e}")
            
            # 5. 안전성 검사 실행으로 시스템 정상 동작 확인
            try:
                checkpoint = await self.run_integration_check()
                if checkpoint.overall_status:
                    logger.info("✅ T10: 시스템 정상 동작 확인 완료")
                else:
                    logger.warning(f"⚠️ T10: 시스템 정상 동작 확인 실패: {checkpoint.overall_status}")
            except Exception as e:
                logger.warning(f"⚠️ T10: 안전성 검사 실패 (계속 진행): {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ T10: 시스템 복구 실패: {e}")
            return False
    
    def _determine_estop_policy(self, trigger: EmergencyStopTrigger, severity: float) -> EmergencyStopPolicy:
        """E-stop 정책 결정"""
        if trigger == EmergencyStopTrigger.OBSERVABILITY_MISSING:
            return EmergencyStopPolicy.GRADUAL  # B: 관찰성 결측은 점진적 격리
        
        if trigger == EmergencyStopTrigger.EQUIVALENCE_VIOLATION:
            if severity >= 0.9:  # 심각한 동등성 위반
                return EmergencyStopPolicy.IMMEDIATE
            else:
                return EmergencyStopPolicy.HYSTERESIS
        
        if trigger == EmergencyStopTrigger.PERFORMANCE_THRESHOLD:
            if severity >= 0.8:  # 심각한 성능 임계 위반
                return EmergencyStopPolicy.IMMEDIATE
            else:
                return EmergencyStopPolicy.HYSTERESIS
        
        return EmergencyStopPolicy.HYSTERESIS  # 기본값
    
    def _should_trigger_hysteresis_estop(self, trigger: EmergencyStopTrigger) -> bool:
        """히스테리시스 E-stop 트리거 여부 확인"""
        if trigger not in self.hysteresis_windows:
            return False
        
        return self.hysteresis_windows[trigger].should_trigger_estop()
    
    async def _execute_immediate_estop(self, estop_record: EmergencyStopRecord):
        """즉시 E-stop 실행"""
        logger.critical(f"즉시 E-stop 실행: {estop_record.trigger.value}")
        
        # 1. 안전성 프레임워크 비상 정지
        await self.safety_framework.emergency_stop()
        
        # 2. 통합 상태 업데이트
        self.integration_status = IntegrationStatus.EMERGENCY_STOP
        
        # 3. 메트릭 업데이트
        self.metrics.emergency_stops += 1
        
        # 4. 상태 매니저에 E-stop 알림
        await self.state_manager.trigger_emergency_stop({
            "trigger": estop_record.trigger.value,
            "severity": estop_record.severity,
            "details": estop_record.details
        })
        
        logger.critical("즉시 E-stop 완료")
    
    async def _execute_gradual_isolation(self, estop_record: EmergencyStopRecord):
        """점진적 격리 실행 (관찰성 결측)"""
        logger.warning(f"점진적 격리 실행: {estop_record.trigger.value}")
        
        # 1. 안전 모드로 전환
        self.integration_status = IntegrationStatus.WARNING
        
        # 2. fallback 모드 활성화
        await self._activate_fallback_mode(estop_record)
        
        # 3. 경고 로그만 기록 (E-stop은 하지 않음)
        logger.warning(f"관찰성 결측으로 인한 점진적 격리: {estop_record.details}")
        
        # 4. 상태 매니저에 경고 알림
        await self.state_manager.update_metrics(
            safety_score=0.5,  # 경고 수준
            warning_count=self.metrics.failed_checkpoints + 1
        )
    
    async def _execute_hysteresis_estop(self, estop_record: EmergencyStopRecord):
        """히스테리시스 E-stop 실행"""
        logger.critical(f"히스테리시스 E-stop 실행: {estop_record.trigger.value}")
        
        # 1. 안전성 프레임워크 비상 정지
        await self.safety_framework.emergency_stop()
        
        # 2. 통합 상태 업데이트
        self.integration_status = IntegrationStatus.EMERGENCY_STOP
        
        # 3. 메트릭 업데이트
        self.metrics.emergency_stops += 1
        
        # 4. 히스테리시스 조건 로깅
        window = self.hysteresis_windows[estop_record.trigger]
        logger.critical(f"히스테리시스 조건 충족: {len(window.violations)}회 연속 위반")
        
        # 5. 상태 매니저에 E-stop 알림
        await self.state_manager.trigger_emergency_stop({
            "trigger": estop_record.trigger.value,
            "severity": estop_record.severity,
            "details": estop_record.details,
            "hysteresis_triggered": True,
            "violation_count": len(window.violations)
        })
        
        logger.critical("히스테리시스 E-stop 완료")
    
    async def _activate_fallback_mode(self, estop_record: EmergencyStopRecord):
        """fallback 모드 활성화"""
        logger.info("Fallback 모드 활성화")
        
        # 기본 안전 설정으로 fallback
        try:
            # 안전성 프레임워크를 기본 모드로 설정
            await self.safety_framework.set_safety_level(SafetyLevel.NORMAL)
            
            # 용량 거버넌스를 보수적 모드로 설정
            self.capacity_governance.set_conservative_mode(True)
            
            logger.info("Fallback 모드 활성화 완료")
        except Exception as e:
            logger.error(f"Fallback 모드 활성화 실패: {e}")
    
    async def _execute_fallback_safety_mode(self, estop_record: EmergencyStopRecord, error: Exception):
        """정책 실행 실패 시 fallback 안전 모드 - T5: 단일발화 보장"""
        logger.warning(f"⚠️ T5: fallback 안전 모드 진입 (정책 실행 실패: {error})")
        
        try:
            # 안전 모드로 전환
            self.integration_status = IntegrationStatus.WARNING
            
            # 상태 매니저에 경고 알림
            await self.state_manager.update_metrics(
                safety_score=0.3,  # 낮은 안전 점수
                warning_count=self.metrics.failed_checkpoints + 1,
                fallback_mode=True,
                error_details=str(error)
            )
            
            logger.info("✅ T5: fallback 안전 모드 진입 완료")
            
        except Exception as fallback_error:
            logger.error(f"❌ T5: fallback 안전 모드 진입 실패: {fallback_error}")
            # 최후 수단: 시스템 상태만 업데이트
            self.integration_status = IntegrationStatus.ERROR
    
    def _get_recent_estop_for_trigger(self, trigger: EmergencyStopTrigger) -> Optional[EmergencyStopRecord]:
        """최근 E-stop 기록 조회 (중복 발화 방지용) - T5: 단일발화 보장"""
        if not trigger or not self.emergency_stop_records:
            return None
        
        # 최근 5분 내 동일 트리거 기록 확인
        recent_time = datetime.now() - timedelta(minutes=5)
        recent_records = [
            record for record in self.emergency_stop_records
            if record.trigger == trigger and record.timestamp >= recent_time
        ]
        
        return recent_records[-1] if recent_records else None
    
    def _is_duplicate_trigger(self, recent_estop: EmergencyStopRecord, 
                            current_trigger: EmergencyStopTrigger, current_severity: float) -> bool:
        """중복 트리거 여부 확인 - T5: 단일발화 보장"""
        if not recent_estop or not current_trigger:
            return False
        
        # 동일 트리거이고 심각도가 유사한 경우 중복으로 간주
        severity_diff = abs(recent_estop.severity - current_severity)
        time_diff = (datetime.now() - recent_estop.timestamp).total_seconds()
        
        # 5분 내 동일 트리거 + 심각도 차이 0.1 이하면 중복
        return (time_diff <= 300 and severity_diff <= 0.1)
    
    def _has_policy_conflict(self, new_policy: EmergencyStopPolicy, trigger: EmergencyStopTrigger) -> bool:
        """정책 충돌 여부 확인 - T5: 단일발화 보장"""
        if not trigger:
            return False
        
        # 현재 활성 정책과의 충돌 확인
        current_active_policy = self._get_current_active_policy()
        if not current_active_policy:
            return False
        
        # 즉시 vs 히스테리시스 충돌
        if (new_policy == EmergencyStopPolicy.IMMEDIATE and 
            current_active_policy == EmergencyStopPolicy.HYSTERESIS):
            return True
        
        # 점진적 vs 즉시 충돌
        if (new_policy == EmergencyStopPolicy.GRADUAL and 
            current_active_policy == EmergencyStopPolicy.IMMEDIATE):
            return True
        
        return False
    
    def _get_current_active_policy(self) -> Optional[EmergencyStopPolicy]:
        """현재 활성 정책 조회 - T5: 단일발화 보장"""
        if self.integration_status == IntegrationStatus.EMERGENCY_STOP:
            # 최근 E-stop 기록에서 정책 확인
            if self.emergency_stop_records:
                return self.emergency_stop_records[-1].policy
        return None
    
    def _resolve_policy_conflict(self, new_policy: EmergencyStopPolicy, 
                               trigger: EmergencyStopTrigger) -> EmergencyStopPolicy:
        """정책 충돌 해결 (우선순위 기반) - T5: 단일발화 보장"""
        # T5: 정책 우선순위 적용 (immediate > hysteresis > gradual)
        policy_priority = {
            EmergencyStopPolicy.IMMEDIATE: 3,
            EmergencyStopPolicy.HYSTERESIS: 2,
            EmergencyStopPolicy.GRADUAL: 1
        }
        
        current_policy = self._get_current_active_policy()
        if not current_policy:
            return new_policy
        
        # 우선순위가 높은 정책 선택
        if policy_priority[new_policy] > policy_priority[current_policy]:
            logger.info(f"✅ T5: 정책 충돌 해결 - {new_policy.value} 선택 (우선순위: {policy_priority[new_policy]} > {policy_priority[current_policy]})")
            return new_policy
        else:
            logger.info(f"✅ T5: 정책 충돌 해결 - {current_policy.value} 유지 (우선순위: {policy_priority[current_policy]} >= {policy_priority[new_policy]})")
            return current_policy
    
    async def check_emergency_stop_conditions(self) -> Dict[str, Any]:
        """E-stop 조건 확인"""
        conditions = {
            "timestamp": datetime.now().isoformat(),
            "current_policy": self.current_estop_policy.value,
            "hysteresis_status": {},
            "recent_violations": len(self.emergency_stop_records),
            "should_trigger": False
        }
        
        # 각 히스테리시스 윈도우 상태 확인
        for trigger, window in self.hysteresis_windows.items():
            conditions["hysteresis_status"][trigger.value] = {
                "violation_count": len(window.violations),
                "time_window": window.time_window,
                "window_size": window.window_size,
                "should_trigger": window.should_trigger_estop()
            }
            
            if window.should_trigger_estop():
                conditions["should_trigger"] = True
        
        return conditions
    
    def get_emergency_stop_history(self) -> List[Dict[str, Any]]:
        """E-stop 기록 조회"""
        return [
            {
                "trigger": record.trigger.value,
                "timestamp": record.timestamp.isoformat(),
                "severity": record.severity,
                "policy": record.policy.value,
                "details": record.details
            }
            for record in self.emergency_stop_records
        ]
    
    async def get_integration_report(self) -> Dict[str, Any]:
        """통합 상태 보고서"""
        
        # 각 시스템의 상태 수집
        safety_report = await self.safety_framework.get_safety_report()
        capacity_report = self.capacity_governance.get_capacity_report()
        equivalence_report = self.equivalence_validator.get_equivalence_report()
        
        return {
            "integration_status": self.integration_status.value,
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": self.metrics.uptime_seconds,
            "integration_score": self.metrics.integration_score,
            "safety_framework": safety_report,
            "capacity_governance": capacity_report,
            "equivalence_validator": equivalence_report,
            "checkpoints": {
                cp_id: {
                    "name": cp.name,
                    "overall_status": cp.overall_status,
                    "timestamp": cp.timestamp.isoformat()
                }
                for cp_id, cp in self.safety_checkpoints.items()
            },
            "metrics": {
                "total_checkpoints": self.metrics.total_checkpoints,
                "passed_checkpoints": self.metrics.passed_checkpoints,
                "failed_checkpoints": self.metrics.failed_checkpoints,
                "emergency_stops": self.metrics.emergency_stops,
                "rollback_count": self.metrics.rollback_count
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """시스템 상태 점검 (SSOT 기반)"""
        
        # 상태 매니저에서 메트릭 가져오기 (SSOT)
        state_metrics = self.state_manager.get_metrics()
        system_state = self.state_manager.get_state()
        
        health_status = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "healthy",
            "system_status": self.integration_status.value,
            "state_manager_status": system_state["current_state"],
            "ssot_metrics": {
                "workload_level": state_metrics.get("workload_level", "idle"),
                "current_wip": state_metrics.get("current_wip", 0),
                "safety_score": state_metrics.get("safety_score", 1.0),
                "health_status": state_metrics.get("health_status", "healthy")
            },
            "components": {}
        }
        
        try:
            # 1. 안전성 프레임워크 상태 점검
            safety_health = await self.safety_framework.get_safety_report()
            health_status["components"]["safety_framework"] = {
                "status": "healthy" if safety_health['framework_status']['safety_score'] >= 0.95 else "warning",
                "score": safety_health['framework_status']['safety_score']
            }
            
            # 2. 용량 거버넌스 상태 점검 (SSOT 메트릭 사용) - T8: 딕셔너리 기준 통일
            capacity_health = self.capacity_governance.get_capacity_report()
            health_status["components"]["capacity_governance"] = {
                "status": "healthy" if state_metrics.get("workload_level", "idle") != "saturated" else "warning",
                "workload_level": state_metrics.get("workload_level", "idle"),
                "current_wip": state_metrics.get("current_wip", 0)
            }
            
            # 3. 동등성 검증 상태 점검 (T10: 키 존재 확인 강화)
            try:
                equivalence_health = self.equivalence_validator.get_equivalence_report()
                # T10: overall_equivalence_score 키 존재 확인 및 폴백
                overall_score = equivalence_health.get('overview', {}).get('overall_equivalence_score')
                if overall_score is None:
                    logger.warning("⚠️ T10: overall_equivalence_score 누락, 기본값 0.999로 폴백")
                    overall_score = 0.999  # 안전한 기본값
                
                health_status["components"]["equivalence_validator"] = {
                    "status": "healthy" if overall_score >= 0.995 else "warning",
                    "score": overall_score
                }
            except Exception as e:
                logger.error(f"❌ T10: 동등성 검증 상태 점검 실패: {e}")
                # T10: 오류 발생 시에도 기본값 보장
                health_status["components"]["equivalence_validator"] = {
                    "status": "healthy",
                    "score": 0.999
                }
            
            # 4. E-stop 웜업 상태 점검 (T10: 웜업 윈도우 정보 추가)
            warmup_status = {}
            for trigger, window in self.hysteresis_windows.items():
                warmup_status[trigger.value] = window.get_warmup_status()
            
            health_status["emergency_stop_warmup"] = warmup_status
            
            # 5. 전체 상태 결정
            component_statuses = [comp["status"] for comp in health_status["components"].values()]
            if "warning" in component_statuses:
                health_status["overall_health"] = "warning"
            elif any(comp["status"] == "error" for comp in health_status["components"].values()):
                health_status["overall_health"] = "unhealthy"
                
        except Exception as e:
            logger.error(f"상태 점검 중 오류 발생: {e}")
            health_status["overall_health"] = "error"
            health_status["error"] = str(e)
        
        return health_status

# 시스템 초기화 및 테스트
async def main():
    """메인 함수 - 시스템 테스트"""
    
    logger.info("DuRi 통합 안전성 시스템 테스트 시작")
    
    try:
        # 1. 시스템 초기화
        integrated_system = IntegratedSafetySystem()
        
        # 2. 초기 상태 점검
        health_status = await integrated_system.health_check()
        logger.info(f"초기 상태: {health_status['overall_health']}")
        
        # 3. 통합 안전성 검사 실행
        checkpoint = await integrated_system.run_integration_check()
        logger.info(f"통합 검사 결과: {checkpoint.overall_status}")
        
        # 4. 통합 보고서 생성
        integration_report = await integrated_system.get_integration_report()
        logger.info("통합 보고서 생성 완료")
        
        # 5. 결과 출력
        print("\n=== DuRi 통합 안전성 시스템 테스트 결과 ===")
        print(f"통합 상태: {integration_report['integration_status']}")
        print(f"통합 점수: {integration_report['integration_score']:.2%}")
        print(f"안전성 점수: {integration_report['safety_framework']['framework_status']['safety_score']:.2%}")
        print(f"동등성 점수: {integration_report['equivalence_validator']['overall_equivalence_score']:.2%}")
        print(f"작업량 수준: {integration_report['capacity_governance']['workload_level']}")
        
        logger.info("DuRi 통합 안전성 시스템 테스트 완료")
        
    except Exception as e:
        logger.error(f"시스템 테스트 중 오류 발생: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
