"""
DuRi 모듈 실패 시 회복 전략 설계 (FallbackRecoveryModule)

DuRi의 개별 모듈이 실패했을 때 자동 복구 및 대체 전략을 실행하는 시스템입니다.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import traceback

logger = logging.getLogger(__name__)

class RecoveryStrategy(Enum):
    """회복 전략"""
    RETRY = "retry"                   # 재시도
    FALLBACK = "fallback"             # 대체 모듈 사용
    DEGRADED = "degraded"             # 기능 축소
    RESTART = "restart"               # 모듈 재시작
    IGNORE = "ignore"                 # 무시하고 계속
    CRITICAL = "critical"             # 치명적 오류

class ModuleStatus(Enum):
    """모듈 상태"""
    OPERATIONAL = "operational"       # 정상 운영
    DEGRADED = "degraded"            # 기능 축소
    FAILED = "failed"                # 실패
    RECOVERING = "recovering"        # 복구 중
    CRITICAL = "critical"            # 치명적 오류

class RecoveryPriority(Enum):
    """회복 우선순위"""
    LOW = "low"                      # 낮음
    MEDIUM = "medium"                # 보통
    HIGH = "high"                    # 높음
    CRITICAL = "critical"            # 치명적

@dataclass
class ModuleHealth:
    """모듈 건강도"""
    module_id: str
    module_name: str
    status: ModuleStatus
    health_score: float  # 0.0 ~ 1.0
    last_check: datetime
    error_count: int = 0
    recovery_attempts: int = 0
    last_error: Optional[str] = None
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.RETRY
    notes: str = ""

@dataclass
class RecoveryAction:
    """회복 액션"""
    action_id: str
    module_id: str
    strategy: RecoveryStrategy
    priority: RecoveryPriority
    timestamp: datetime
    success: bool = False
    execution_time: timedelta = field(default_factory=lambda: timedelta(0))
    error_message: Optional[str] = None
    fallback_module: Optional[str] = None
    notes: str = ""

@dataclass
class RecoveryPlan:
    """회복 계획"""
    plan_id: str
    module_id: str
    trigger_time: datetime
    strategies: List[RecoveryStrategy] = field(default_factory=list)
    max_attempts: int = 3
    timeout_seconds: int = 30
    fallback_modules: List[str] = field(default_factory=list)
    priority: RecoveryPriority = RecoveryPriority.MEDIUM
    is_active: bool = True

@dataclass
class RecoveryReport:
    """회복 보고서"""
    report_id: str
    timestamp: datetime
    module_health_status: Dict[str, ModuleHealth] = field(default_factory=dict)
    recovery_actions: List[RecoveryAction] = field(default_factory=list)
    active_plans: List[RecoveryPlan] = field(default_factory=list)
    overall_success_rate: float = 0.0
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)

class FallbackRecoveryModule:
    """DuRi 모듈 실패 시 회복 전략 설계 시스템"""
    
    def __init__(self):
        """FallbackRecoveryModule 초기화"""
        # 모듈 건강도 관리
        self.module_health: Dict[str, ModuleHealth] = {}
        self.recovery_actions: List[RecoveryAction] = []
        self.recovery_plans: Dict[str, RecoveryPlan] = {}
        
        # 회복 설정
        self.recovery_config = {
            'max_retry_attempts': 3,
            'retry_delay_seconds': 5,
            'health_check_interval': 30,
            'critical_timeout_seconds': 60,
            'enable_automatic_recovery': True,
            'enable_fallback_modules': True
        }
        
        # 대체 모듈 매핑
        self.fallback_module_mapping = {
            'SelfAssessmentManager': ['BasicAssessmentManager'],
            'MemorySync': ['SimpleMemoryManager'],
            'LearningLoopManager': ['BasicLearningManager'],
            'GoalOrientedThinking': ['SimpleGoalManager'],
            'EmotionalEthicalJudgment': ['BasicJudgmentManager'],
            'AutonomousGoalSetting': ['SimpleGoalSetting'],
            'AdvancedCreativitySystem': ['BasicCreativityManager']
        }
        
        # 회복 전략 우선순위
        self.strategy_priority = {
            RecoveryStrategy.RETRY: RecoveryPriority.MEDIUM,
            RecoveryStrategy.FALLBACK: RecoveryPriority.HIGH,
            RecoveryStrategy.DEGRADED: RecoveryPriority.LOW,
            RecoveryStrategy.RESTART: RecoveryPriority.HIGH,
            RecoveryStrategy.IGNORE: RecoveryPriority.LOW,
            RecoveryStrategy.CRITICAL: RecoveryPriority.CRITICAL
        }
        
        logger.info("FallbackRecoveryModule 초기화 완료")
    
    def register_module(self, module_id: str, module_name: str, 
                       initial_health_score: float = 1.0) -> bool:
        """모듈을 등록합니다."""
        try:
            module_health = ModuleHealth(
                module_id=module_id,
                module_name=module_name,
                status=ModuleStatus.OPERATIONAL,
                health_score=initial_health_score,
                last_check=datetime.now()
            )
            
            self.module_health[module_id] = module_health
            
            # 기본 회복 계획 생성
            recovery_plan = RecoveryPlan(
                plan_id=f"plan_{uuid.uuid4().hex[:8]}",
                module_id=module_id,
                trigger_time=datetime.now(),
                strategies=[RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK, RecoveryStrategy.DEGRADED],
                max_attempts=self.recovery_config['max_retry_attempts'],
                timeout_seconds=self.recovery_config['critical_timeout_seconds'],
                fallback_modules=self.fallback_module_mapping.get(module_name, []),
                priority=RecoveryPriority.MEDIUM
            )
            
            self.recovery_plans[module_id] = recovery_plan
            
            logger.info(f"모듈 등록 완료: {module_id} ({module_name})")
            return True
            
        except Exception as e:
            logger.error(f"모듈 등록 실패: {e}")
            return False
    
    def report_module_failure(self, module_id: str, error_message: str, 
                            error_type: str = "unknown") -> bool:
        """모듈 실패를 보고합니다."""
        try:
            if module_id not in self.module_health:
                logger.error(f"등록되지 않은 모듈: {module_id}")
                return False
            
            module_health = self.module_health[module_id]
            module_health.error_count += 1
            module_health.last_error = error_message
            module_health.last_check = datetime.now()
            
            # 건강도 점수 감소
            health_decrease = 0.2 * module_health.error_count
            module_health.health_score = max(0.0, module_health.health_score - health_decrease)
            
            # 상태 결정
            if module_health.health_score >= 0.7:
                module_health.status = ModuleStatus.OPERATIONAL
            elif module_health.health_score >= 0.4:
                module_health.status = ModuleStatus.DEGRADED
            elif module_health.health_score >= 0.1:
                module_health.status = ModuleStatus.FAILED
            else:
                module_health.status = ModuleStatus.CRITICAL
            
            # 회복 전략 결정
            recovery_strategy = self._determine_recovery_strategy(module_health)
            module_health.recovery_strategy = recovery_strategy
            
            # 회복 액션 실행
            recovery_action = self._execute_recovery_action(module_id, recovery_strategy, error_message)
            
            if recovery_action:
                self.recovery_actions.append(recovery_action)
                
                if recovery_action.success:
                    logger.info(f"모듈 회복 성공: {module_id} ({recovery_strategy.value})")
                else:
                    logger.warning(f"모듈 회복 실패: {module_id} ({recovery_strategy.value})")
            
            return True
            
        except Exception as e:
            logger.error(f"모듈 실패 보고 실패: {e}")
            return False
    
    def _determine_recovery_strategy(self, module_health: ModuleHealth) -> RecoveryStrategy:
        """회복 전략을 결정합니다."""
        try:
            if module_health.error_count == 1:
                return RecoveryStrategy.RETRY
            elif module_health.error_count == 2:
                return RecoveryStrategy.FALLBACK
            elif module_health.error_count == 3:
                return RecoveryStrategy.DEGRADED
            elif module_health.error_count >= 4:
                return RecoveryStrategy.CRITICAL
            else:
                return RecoveryStrategy.IGNORE
                
        except Exception as e:
            logger.error(f"회복 전략 결정 실패: {e}")
            return RecoveryStrategy.IGNORE
    
    def _execute_recovery_action(self, module_id: str, strategy: RecoveryStrategy, 
                               error_message: str) -> Optional[RecoveryAction]:
        """회복 액션을 실행합니다."""
        try:
            action_id = f"action_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            module_health = self.module_health[module_id]
            module_health.recovery_attempts += 1
            
            success = False
            fallback_module = None
            notes = ""
            
            if strategy == RecoveryStrategy.RETRY:
                success = self._retry_module(module_id)
                notes = "모듈 재시도"
                
            elif strategy == RecoveryStrategy.FALLBACK:
                fallback_module = self._activate_fallback_module(module_id)
                success = fallback_module is not None
                notes = f"대체 모듈 활성화: {fallback_module}"
                
            elif strategy == RecoveryStrategy.DEGRADED:
                success = self._degrade_module_functionality(module_id)
                notes = "기능 축소 모드 활성화"
                
            elif strategy == RecoveryStrategy.RESTART:
                success = self._restart_module(module_id)
                notes = "모듈 재시작"
                
            elif strategy == RecoveryStrategy.IGNORE:
                success = True
                notes = "오류 무시하고 계속"
                
            elif strategy == RecoveryStrategy.CRITICAL:
                success = self._handle_critical_failure(module_id)
                notes = "치명적 오류 처리"
            
            execution_time = datetime.now() - start_time
            
            recovery_action = RecoveryAction(
                action_id=action_id,
                module_id=module_id,
                strategy=strategy,
                priority=self.strategy_priority.get(strategy, RecoveryPriority.MEDIUM),
                timestamp=start_time,
                success=success,
                execution_time=execution_time,
                error_message=error_message,
                fallback_module=fallback_module,
                notes=notes
            )
            
            return recovery_action
            
        except Exception as e:
            logger.error(f"회복 액션 실행 실패: {e}")
            return None
    
    def _retry_module(self, module_id: str) -> bool:
        """모듈을 재시도합니다."""
        try:
            # 재시도 로직 (시뮬레이션)
            time.sleep(0.1)  # 짧은 지연
            
            # 성공 확률 계산 (오류 횟수에 따라 감소)
            module_health = self.module_health[module_id]
            success_probability = max(0.1, 1.0 - (module_health.error_count * 0.3))
            
            import random
            success = random.random() < success_probability
            
            if success:
                module_health.health_score = min(1.0, module_health.health_score + 0.1)
                module_health.status = ModuleStatus.OPERATIONAL
            
            return success
            
        except Exception as e:
            logger.error(f"모듈 재시도 실패: {e}")
            return False
    
    def _activate_fallback_module(self, module_id: str) -> Optional[str]:
        """대체 모듈을 활성화합니다."""
        try:
            module_health = self.module_health[module_id]
            fallback_modules = self.fallback_module_mapping.get(module_health.module_name, [])
            
            if fallback_modules:
                # 첫 번째 대체 모듈 선택
                fallback_module = fallback_modules[0]
                
                # 대체 모듈 활성화 (시뮬레이션)
                logger.info(f"대체 모듈 활성화: {module_health.module_name} → {fallback_module}")
                
                return fallback_module
            else:
                logger.warning(f"대체 모듈 없음: {module_health.module_name}")
                return None
                
        except Exception as e:
            logger.error(f"대체 모듈 활성화 실패: {e}")
            return None
    
    def _degrade_module_functionality(self, module_id: str) -> bool:
        """모듈 기능을 축소합니다."""
        try:
            module_health = self.module_health[module_id]
            
            # 기능 축소 모드 활성화
            module_health.status = ModuleStatus.DEGRADED
            module_health.health_score = max(0.3, module_health.health_score)
            
            logger.info(f"모듈 기능 축소: {module_health.module_name}")
            return True
            
        except Exception as e:
            logger.error(f"모듈 기능 축소 실패: {e}")
            return False
    
    def _restart_module(self, module_id: str) -> bool:
        """모듈을 재시작합니다."""
        try:
            module_health = self.module_health[module_id]
            
            # 재시작 로직 (시뮬레이션)
            time.sleep(0.2)  # 재시작 시간
            
            # 재시작 후 상태 초기화
            module_health.health_score = 0.8  # 부분적 복구
            module_health.status = ModuleStatus.OPERATIONAL
            module_health.error_count = 0
            module_health.recovery_attempts = 0
            module_health.last_error = None
            
            logger.info(f"모듈 재시작 완료: {module_health.module_name}")
            return True
            
        except Exception as e:
            logger.error(f"모듈 재시작 실패: {e}")
            return False
    
    def _handle_critical_failure(self, module_id: str) -> bool:
        """치명적 오류를 처리합니다."""
        try:
            module_health = self.module_health[module_id]
            
            # 치명적 오류 상태로 설정
            module_health.status = ModuleStatus.CRITICAL
            module_health.health_score = 0.0
            
            # 긴급 복구 시도
            emergency_success = self._emergency_recovery(module_id)
            
            if emergency_success:
                module_health.status = ModuleStatus.DEGRADED
                module_health.health_score = 0.2
            
            logger.critical(f"치명적 오류 처리: {module_health.module_name}")
            return emergency_success
            
        except Exception as e:
            logger.error(f"치명적 오류 처리 실패: {e}")
            return False
    
    def _emergency_recovery(self, module_id: str) -> bool:
        """긴급 복구를 시도합니다."""
        try:
            # 모든 회복 전략을 순차적으로 시도
            strategies = [
                RecoveryStrategy.RESTART,
                RecoveryStrategy.FALLBACK,
                RecoveryStrategy.DEGRADED
            ]
            
            for strategy in strategies:
                action = self._execute_recovery_action(module_id, strategy, "긴급 복구")
                if action and action.success:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"긴급 복구 실패: {e}")
            return False
    
    def get_module_health(self, module_id: str) -> Optional[ModuleHealth]:
        """모듈 건강도를 반환합니다."""
        return self.module_health.get(module_id)
    
    def get_all_module_health(self) -> Dict[str, ModuleHealth]:
        """모든 모듈 건강도를 반환합니다."""
        return self.module_health.copy()
    
    def generate_recovery_report(self) -> RecoveryReport:
        """회복 보고서를 생성합니다."""
        try:
            report_id = f"recovery_report_{uuid.uuid4().hex[:8]}"
            timestamp = datetime.now()
            
            # 전체 성공률 계산
            total_actions = len(self.recovery_actions)
            successful_actions = sum(1 for action in self.recovery_actions if action.success)
            overall_success_rate = successful_actions / total_actions if total_actions > 0 else 0.0
            
            # 중요한 이슈 식별
            critical_issues = []
            for module_health in self.module_health.values():
                if module_health.status == ModuleStatus.CRITICAL:
                    critical_issues.append(f"{module_health.module_name}: 치명적 오류")
                elif module_health.status == ModuleStatus.FAILED:
                    critical_issues.append(f"{module_health.module_name}: 실패 상태")
            
            # 권장사항 생성
            recommendations = []
            if overall_success_rate < 0.7:
                recommendations.append("회복 전략 개선 필요")
            if critical_issues:
                recommendations.append("치명적 오류 즉시 해결 필요")
            else:
                recommendations.append("시스템 상태 양호")
            
            report = RecoveryReport(
                report_id=report_id,
                timestamp=timestamp,
                module_health_status=self.module_health.copy(),
                recovery_actions=self.recovery_actions.copy(),
                active_plans=list(self.recovery_plans.values()),
                overall_success_rate=overall_success_rate,
                critical_issues=critical_issues,
                recommendations=recommendations
            )
            
            return report
            
        except Exception as e:
            logger.error(f"회복 보고서 생성 실패: {e}")
            return None
    
    def get_recovery_statistics(self) -> Dict[str, Any]:
        """회복 통계를 반환합니다."""
        try:
            total_modules = len(self.module_health)
            operational_modules = sum(1 for health in self.module_health.values() 
                                   if health.status == ModuleStatus.OPERATIONAL)
            failed_modules = sum(1 for health in self.module_health.values() 
                               if health.status == ModuleStatus.FAILED)
            critical_modules = sum(1 for health in self.module_health.values() 
                                 if health.status == ModuleStatus.CRITICAL)
            
            total_actions = len(self.recovery_actions)
            successful_actions = sum(1 for action in self.recovery_actions if action.success)
            
            return {
                'total_modules': total_modules,
                'operational_modules': operational_modules,
                'failed_modules': failed_modules,
                'critical_modules': critical_modules,
                'total_recovery_actions': total_actions,
                'successful_recovery_actions': successful_actions,
                'recovery_success_rate': successful_actions / total_actions if total_actions > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"회복 통계 계산 실패: {e}")
            return {}

# 싱글톤 인스턴스
_fallback_recovery_module = None

def get_fallback_recovery_module() -> FallbackRecoveryModule:
    """FallbackRecoveryModule 싱글톤 인스턴스 반환"""
    global _fallback_recovery_module
    if _fallback_recovery_module is None:
        _fallback_recovery_module = FallbackRecoveryModule()
    return _fallback_recovery_module 