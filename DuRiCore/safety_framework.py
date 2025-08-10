#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 안전성 프레임워크 (Safety Framework)
안전성과 동등성을 보장하는 핵심 시스템

@preserve_identity: 기존 기능과 동작 패턴 보존
@evolution_protection: 진화 과정에서의 안전성 확보
@execution_guarantee: 실행 안전성 보장
@existence_ai: 안전한 진화와 회복
@final_execution: 안전한 최종 실행
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import traceback
import hashlib
import pickle
from pathlib import Path

# DuRi 로깅 시스템 초기화
try:
    from DuRiCore.bootstrap import bootstrap_logging
    bootstrap_logging()
except ImportError:
    # 로컬 디렉토리에서 직접 import
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

class SafetyLevel(Enum):
    """안전성 수준"""
    CRITICAL = "critical"      # 즉시 중단 필요
    HIGH = "high"              # 높은 주의 필요
    MEDIUM = "medium"          # 중간 주의 필요
    LOW = "low"                # 낮은 주의 필요
    SAFE = "safe"              # 안전함

class InvariantType(Enum):
    """불변 조건 유형"""
    FUNCTIONALITY = "functionality"    # 기능적 불변
    PERFORMANCE = "performance"        # 성능적 불변
    MEMORY = "memory"                 # 메모리 불변
    API_COMPATIBILITY = "api_compatibility"  # API 호환성
    DATA_INTEGRITY = "data_integrity" # 데이터 무결성

@dataclass
class SafetyInvariant:
    """안전성 불변 조건"""
    id: str
    name: str
    invariant_type: InvariantType
    description: str
    check_function: Callable
    critical: bool = False
    last_check: Optional[datetime] = None
    check_result: Optional[bool] = None
    violation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class SafetyCheck:
    """안전성 검사 결과"""
    id: str
    timestamp: datetime
    safety_level: SafetyLevel
    message: str
    details: Dict[str, Any]
    action_required: bool = False
    rollback_triggered: bool = False

@dataclass
class SafetyMetrics:
    """안전성 메트릭"""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    critical_violations: int = 0
    last_check_time: Optional[datetime] = None
    uptime_seconds: float = 0.0
    safety_score: float = 1.0

class SafetyFramework:
    """DuRi 안전성 프레임워크"""
    
    def __init__(self):
        self.invariants: Dict[str, SafetyInvariant] = {}
        self.safety_checks: List[SafetyCheck] = []
        self.metrics = SafetyMetrics()
        self.start_time = datetime.now()
        self.rollback_ready = False
        self.safety_enabled = True
        
        # 기본 안전성 불변 조건 등록
        self._register_default_invariants()
        
        logger.info("DuRi 안전성 프레임워크 초기화 완료")
    
    def _register_default_invariants(self):
        """기본 안전성 불변 조건 등록"""
        
        # 기능적 불변 조건
        self.register_invariant(
            SafetyInvariant(
                id="func_core_functionality",
                name="핵심 기능 유지",
                invariant_type=InvariantType.FUNCTIONALITY,
                description="핵심 기능이 정상적으로 작동하는지 확인",
                check_function=self._check_core_functionality,
                critical=True
            )
        )
        
        # 성능적 불변 조건
        self.register_invariant(
            SafetyInvariant(
                id="perf_response_time",
                name="응답 시간 유지",
                invariant_type=InvariantType.PERFORMANCE,
                description="응답 시간이 허용 범위 내에 있는지 확인",
                check_function=self._check_response_time,
                critical=False
            )
        )
        
        # 메모리 불변 조건
        self.register_invariant(
            SafetyInvariant(
                id="mem_usage_limit",
                name="메모리 사용량 제한",
                invariant_type=InvariantType.MEMORY,
                description="메모리 사용량이 허용 범위 내에 있는지 확인",
                check_function=self._check_memory_usage,
                critical=True
            )
        )
        
        # API 호환성 불변 조건
        self.register_invariant(
            SafetyInvariant(
                id="api_compatibility",
                name="API 호환성 유지",
                invariant_type=InvariantType.API_COMPATIBILITY,
                description="기존 API 호환성이 유지되는지 확인",
                check_function=self._check_api_compatibility,
                critical=True
            )
        )
    
    def register_invariant(self, invariant: SafetyInvariant):
        """안전성 불변 조건 등록"""
        self.invariants[invariant.id] = invariant
        logger.info(f"안전성 불변 조건 등록: {invariant.name} ({invariant.id})")
    
    def unregister_invariant(self, invariant_id: str):
        """안전성 불변 조건 제거"""
        if invariant_id in self.invariants:
            del self.invariants[invariant_id]
            logger.info(f"안전성 불변 조건 제거: {invariant_id}")
    
    async def run_safety_check(self) -> SafetyCheck:
        """전체 안전성 검사 실행"""
        if not self.safety_enabled:
            return SafetyCheck(
                id="safety_disabled",
                timestamp=datetime.now(),
                safety_level=SafetyLevel.SAFE,
                message="안전성 검사가 비활성화됨",
                details={},
                action_required=False
            )
        
        start_time = time.time()
        check_id = f"safety_check_{int(time.time())}"
        
        logger.info("안전성 검사 시작")
        
        # 모든 불변 조건 검사
        invariant_results = {}
        critical_violations = []
        
        for invariant_id, invariant in self.invariants.items():
            try:
                result = await self._check_invariant(invariant)
                invariant_results[invariant_id] = result
                
                if not result and invariant.critical:
                    critical_violations.append(invariant_id)
                    
            except Exception as e:
                logger.error(f"불변 조건 검사 실패: {invariant_id}, 오류: {e}")
                invariant_results[invariant_id] = False
                if invariant.critical:
                    critical_violations.append(invariant_id)
        
        # 안전성 수준 결정
        if critical_violations:
            safety_level = SafetyLevel.CRITICAL
            action_required = True
            message = f"중요한 안전성 위반 발생: {', '.join(critical_violations)}"
        elif any(not result for result in invariant_results.values()):
            safety_level = SafetyLevel.HIGH
            action_required = True
            message = "안전성 위반 발생"
        else:
            safety_level = SafetyLevel.SAFE
            action_required = False
            message = "모든 안전성 검사 통과"
        
        # 메트릭 업데이트
        self._update_metrics(invariant_results)
        
        # 안전성 검사 결과 생성
        safety_check = SafetyCheck(
            id=check_id,
            timestamp=datetime.now(),
            safety_level=safety_level,
            message=message,
            details={
                "invariant_results": invariant_results,
                "critical_violations": critical_violations,
                "check_duration": time.time() - start_time
            },
            action_required=action_required
        )
        
        self.safety_checks.append(safety_check)
        
        # 중요 위반 시 롤백 준비
        if safety_level == SafetyLevel.CRITICAL:
            await self._prepare_rollback()
        
        logger.info(f"안전성 검사 완료: {safety_level.value}, 위반: {len(critical_violations)}")
        
        return safety_check
    
    async def _check_invariant(self, invariant: SafetyInvariant) -> bool:
        """개별 불변 조건 검사"""
        try:
            if asyncio.iscoroutinefunction(invariant.check_function):
                result = await invariant.check_function()
            else:
                result = invariant.check_function()
            
            # 메타데이터 업데이트
            invariant.last_check = datetime.now()
            invariant.check_result = result
            
            if not result:
                invariant.violation_count += 1
                logger.warning(f"불변 조건 위반: {invariant.name} ({invariant.id})")
            else:
                logger.debug(f"불변 조건 통과: {invariant.name} ({invariant.id})")
            
            return result
            
        except Exception as e:
            logger.error(f"불변 조건 검사 중 오류: {invariant.name}, 오류: {e}")
            invariant.last_check = datetime.now()
            invariant.check_result = False
            invariant.violation_count += 1
            return False
    
    def _update_metrics(self, invariant_results: Dict[str, bool]):
        """안전성 메트릭 업데이트"""
        self.metrics.total_checks += 1
        self.metrics.last_check_time = datetime.now()
        
        passed = sum(1 for result in invariant_results.values() if result)
        failed = len(invariant_results) - passed
        
        self.metrics.passed_checks += passed
        self.metrics.failed_checks += failed
        
        # 안전성 점수 계산 (0.0 ~ 1.0)
        if self.metrics.total_checks > 0:
            self.metrics.safety_score = self.metrics.passed_checks / self.metrics.total_checks
        
        # 업타임 계산
        self.metrics.uptime_seconds = (datetime.now() - self.start_time).total_seconds()
    
    async def _prepare_rollback(self):
        """롤백 준비"""
        if not self.rollback_ready:
            logger.warning("롤백 준비 시작")
            # 롤백 로직 구현 예정
            self.rollback_ready = True
    
    async def get_safety_report(self) -> Dict[str, Any]:
        """안전성 보고서 생성"""
        return {
            "framework_status": {
                "enabled": self.safety_enabled,
                "uptime_seconds": self.metrics.uptime_seconds,
                "safety_score": self.metrics.safety_score
            },
            "metrics": {
                "total_checks": self.metrics.total_checks,
                "passed_checks": self.metrics.passed_checks,
                "failed_checks": self.metrics.failed_checks,
                "last_check_time": self.metrics.last_check_time.isoformat() if self.metrics.last_check_time else None
            },
            "invariants": {
                inv_id: {
                    "name": inv.name,
                    "type": inv.invariant_type.value,
                    "critical": inv.critical,
                    "last_check": inv.last_check.isoformat() if inv.last_check else None,
                    "check_result": inv.check_result,
                    "violation_count": inv.violation_count
                }
                for inv_id, inv in self.invariants.items()
            },
            "recent_checks": [
                {
                    "id": check.id,
                    "timestamp": check.timestamp.isoformat(),
                    "safety_level": check.safety_level.value,
                    "message": check.message,
                    "action_required": check.action_required
                }
                for check in self.safety_checks[-10:]  # 최근 10개
            ]
        }
    
    # 기본 불변 조건 검사 함수들
    
    async def _check_core_functionality(self) -> bool:
        """핵심 기능 정상 작동 확인"""
        try:
            # 기본적인 시스템 상태 확인
            return True  # 실제 구현에서는 더 구체적인 검사 필요
        except Exception as e:
            logger.error(f"핵심 기능 검사 실패: {e}")
            return False
    
    async def _check_response_time(self) -> bool:
        """응답 시간 확인"""
        try:
            # 응답 시간 측정 및 허용 범위 확인
            return True  # 실제 구현에서는 실제 응답 시간 측정 필요
        except Exception as e:
            logger.error(f"응답 시간 검사 실패: {e}")
            return False
    
    async def _check_memory_usage(self) -> bool:
        """메모리 사용량 확인"""
        try:
            # 메모리 사용량 측정 및 제한 확인
            return True  # 실제 구현에서는 실제 메모리 사용량 측정 필요
        except Exception as e:
            logger.error(f"메모리 사용량 검사 실패: {e}")
            return False
    
    async def _check_api_compatibility(self) -> bool:
        """API 호환성 확인"""
        try:
            # API 호환성 검사
            return True  # 실제 구현에서는 실제 API 호환성 검사 필요
        except Exception as e:
            logger.error(f"API 호환성 검사 실패: {e}")
            return False
    
    def enable_safety(self):
        """안전성 검사 활성화"""
        self.safety_enabled = True
        logger.info("안전성 검사 활성화")
    
    def disable_safety(self):
        """안전성 검사 비활성화"""
        self.safety_enabled = False
        logger.warning("안전성 검사 비활성화 - 주의 필요!")
    
    async def emergency_stop(self):
        """긴급 정지"""
        logger.critical("긴급 정지 실행!")
        self.safety_enabled = False
        # 추가적인 긴급 정지 로직 구현 예정
    
    def set_safety_level(self, level: SafetyLevel):
        """안전성 수준 설정 (SSOT 경로)"""
        try:
            # 안전성 수준 업데이트
            if isinstance(level, SafetyLevel):
                self.current_safety_level = level
                logger.info(f"안전성 수준 설정: {level.value}")
                
                # 안전성 수준 변경 이벤트 알림
                self._notify_safety_level_change(level)
                
                return True
            else:
                logger.warning(f"잘못된 안전성 수준: {level}")
                return False
                
        except Exception as e:
            logger.error(f"안전성 수준 설정 실패: {e}")
            return False
    
    def _notify_safety_level_change(self, new_level: SafetyLevel):
        """안전성 수준 변경 알림"""
        try:
            # 안전성 수준 변경 이벤트 발생
            logger.debug(f"안전성 수준 변경 알림: {new_level.value}")
            
            # 여기에 리스너 알림 로직 추가 가능
            # self._notify_listeners("safety_level_change", {"level": new_level.value})
            
        except Exception as e:
            logger.error(f"안전성 수준 변경 알림 실패: {e}")
    
    @property
    def current_safety_level(self) -> SafetyLevel:
        """현재 안전성 수준 반환"""
        return getattr(self, '_current_safety_level', SafetyLevel.SAFE)
    
    @current_safety_level.setter
    def current_safety_level(self, level: SafetyLevel):
        """현재 안전성 수준 설정"""
        self._current_safety_level = level

# 전역 인스턴스
safety_framework = SafetyFramework()
