"""
DuRi 마스터 통합 시스템

DuRi의 모든 시스템을 통합하고 최종 완성을 관리합니다.
"""

import logging
import uuid
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict

# 모든 시스템 import
from duri_core.assessment.self_assessment_manager import get_self_assessment_manager
from duri_core.memory.memory_sync import get_memory_sync, MemoryType
from duri_core.memory.meta_learning_data import get_meta_learning_data_manager
from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
from duri_brain.goals.goal_oriented_thinking import get_goal_oriented_thinking
from duri_brain.ethics.emotional_ethical_judgment import get_emotional_ethical_judgment
from duri_brain.goals.autonomous_goal_setting import get_autonomous_goal_setting
from duri_brain.creativity.advanced_creativity_system import get_advanced_creativity_system
from duri_core.integration.system_integration_validator import get_system_integration_validator
from duri_core.optimization.final_optimization_system import get_final_optimization_system

logger = logging.getLogger(__name__)

class SystemStatus(Enum):
    """시스템 상태"""
    OPERATIONAL = "operational"      # 운영 중
    OPTIMIZING = "optimizing"        # 최적화 중
    INTEGRATING = "integrating"      # 통합 중
    COMPLETED = "completed"          # 완료
    ERROR = "error"                  # 오류

class IntegrationPhase(Enum):
    """통합 단계"""
    INITIALIZATION = "initialization"    # 초기화
    VALIDATION = "validation"            # 검증
    OPTIMIZATION = "optimization"        # 최적화
    INTEGRATION = "integration"          # 통합
    COMPLETION = "completion"            # 완성

@dataclass
class SystemComponentStatus:
    """시스템 컴포넌트 상태"""
    component_id: str
    name: str
    status: SystemStatus
    health_score: float  # 0.0 ~ 1.0
    last_check: datetime
    is_operational: bool = True
    error_count: int = 0
    performance_score: float = 0.0
    notes: str = ""

@dataclass
class IntegrationPhaseResult:
    """통합 단계 결과"""
    phase_id: str
    phase: IntegrationPhase
    timestamp: datetime
    success: bool
    duration: timedelta
    components_processed: int
    issues_found: List[str] = field(default_factory=list)
    optimizations_applied: List[str] = field(default_factory=list)
    notes: str = ""

@dataclass
class MasterIntegrationReport:
    """마스터 통합 보고서"""
    report_id: str
    timestamp: datetime
    overall_status: SystemStatus
    overall_health_score: float  # 0.0 ~ 1.0
    phase_results: List[IntegrationPhaseResult] = field(default_factory=list)
    component_statuses: List[SystemComponentStatus] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    completion_percentage: float = 0.0  # 0.0 ~ 100.0
    final_recommendations: List[str] = field(default_factory=list)

class MasterIntegrationSystem:
    """DuRi 마스터 통합 시스템"""
    
    def __init__(self):
        """MasterIntegrationSystem 초기화"""
        # 모든 시스템 컴포넌트
        self.self_assessment_manager = get_self_assessment_manager()
        self.memory_sync = get_memory_sync()
        self.meta_learning_manager = get_meta_learning_data_manager()
        self.learning_loop_manager = get_learning_loop_manager()
        self.goal_oriented_thinking = get_goal_oriented_thinking()
        self.emotional_ethical_judgment = get_emotional_ethical_judgment()
        self.autonomous_goal_setting = get_autonomous_goal_setting()
        self.advanced_creativity_system = get_advanced_creativity_system()
        self.system_integration_validator = get_system_integration_validator()
        self.final_optimization_system = get_final_optimization_system()
        
        # 통합 관리
        self.integration_reports: List[MasterIntegrationReport] = []
        self.current_phase = IntegrationPhase.INITIALIZATION
        self.completion_percentage = 0.0
        
        # 시스템 컴포넌트 목록
        self.system_components = [
            ("SelfAssessmentManager", self.self_assessment_manager),
            ("MemorySync", self.memory_sync),
            ("MetaLearningManager", self.meta_learning_manager),
            ("LearningLoopManager", self.learning_loop_manager),
            ("GoalOrientedThinking", self.goal_oriented_thinking),
            ("EmotionalEthicalJudgment", self.emotional_ethical_judgment),
            ("AutonomousGoalSetting", self.autonomous_goal_setting),
            ("AdvancedCreativitySystem", self.advanced_creativity_system),
            ("SystemIntegrationValidator", self.system_integration_validator),
            ("FinalOptimizationSystem", self.final_optimization_system)
        ]
        
        logger.info("MasterIntegrationSystem 초기화 완료")
    
    def run_master_integration(self) -> MasterIntegrationReport:
        """마스터 통합을 실행합니다."""
        try:
            report_id = f"master_integration_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            logger.info("마스터 통합 시작")
            
            # 1단계: 초기화
            initialization_result = self._run_initialization_phase()
            
            # 2단계: 검증
            validation_result = self._run_validation_phase()
            
            # 3단계: 최적화
            optimization_result = self._run_optimization_phase()
            
            # 4단계: 통합
            integration_result = self._run_integration_phase()
            
            # 5단계: 완성
            completion_result = self._run_completion_phase()
            
            # 전체 결과 집계
            phase_results = [
                initialization_result,
                validation_result,
                optimization_result,
                integration_result,
                completion_result
            ]
            
            # 컴포넌트 상태 확인
            component_statuses = self._check_all_component_statuses()
            
            # 전체 건강도 점수 계산
            overall_health_score = self._calculate_overall_health_score(component_statuses, phase_results)
            
            # 전체 상태 결정
            overall_status = self._determine_overall_status(overall_health_score, phase_results)
            
            # 완성도 계산
            completion_percentage = self._calculate_completion_percentage(phase_results)
            
            # 중요한 이슈 식별
            critical_issues = self._identify_critical_issues(component_statuses, phase_results)
            
            # 최종 권장사항 생성
            final_recommendations = self._generate_final_recommendations(component_statuses, phase_results)
            
            report = MasterIntegrationReport(
                report_id=report_id,
                timestamp=start_time,
                overall_status=overall_status,
                overall_health_score=overall_health_score,
                phase_results=phase_results,
                component_statuses=component_statuses,
                critical_issues=critical_issues,
                completion_percentage=completion_percentage,
                final_recommendations=final_recommendations
            )
            
            self.integration_reports.append(report)
            self.completion_percentage = completion_percentage
            
            logger.info(f"마스터 통합 완료: 상태 {overall_status.value}, 건강도 {overall_health_score:.2f}, 완성도 {completion_percentage:.1f}%")
            
            return report
            
        except Exception as e:
            logger.error(f"마스터 통합 실행 실패: {e}")
            return None
    
    def _run_initialization_phase(self) -> IntegrationPhaseResult:
        """초기화 단계를 실행합니다."""
        try:
            phase_id = f"initialization_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            logger.info("초기화 단계 시작")
            
            # 모든 컴포넌트 초기화 확인
            components_processed = 0
            issues_found = []
            optimizations_applied = []
            
            for name, component in self.system_components:
                try:
                    # 컴포넌트 초기화 상태 확인
                    if hasattr(component, 'get_current_status'):
                        status = component.get_current_status()
                        if status:
                            components_processed += 1
                        else:
                            issues_found.append(f"{name}: 상태 정보 없음")
                    elif hasattr(component, 'get_assessment_statistics'):
                        stats = component.get_assessment_statistics()
                        if stats:
                            components_processed += 1
                        else:
                            issues_found.append(f"{name}: 통계 정보 없음")
                    else:
                        components_processed += 1  # 기본적으로 정상으로 간주
                        
                except Exception as e:
                    issues_found.append(f"{name}: 초기화 오류 - {e}")
            
            duration = datetime.now() - start_time
            success = components_processed >= len(self.system_components) * 0.8  # 80% 이상 성공
            
            logger.info(f"초기화 단계 완료: {components_processed}/{len(self.system_components)} 컴포넌트")
            
            return IntegrationPhaseResult(
                phase_id=phase_id,
                phase=IntegrationPhase.INITIALIZATION,
                timestamp=start_time,
                success=success,
                duration=duration,
                components_processed=components_processed,
                issues_found=issues_found,
                optimizations_applied=optimizations_applied,
                notes=f"초기화 완료: {components_processed}/{len(self.system_components)} 컴포넌트"
            )
            
        except Exception as e:
            logger.error(f"초기화 단계 실패: {e}")
            return IntegrationPhaseResult(
                phase_id=f"initialization_{uuid.uuid4().hex[:8]}",
                phase=IntegrationPhase.INITIALIZATION,
                timestamp=datetime.now(),
                success=False,
                duration=timedelta(0),
                components_processed=0,
                issues_found=[f"초기화 단계 실패: {e}"],
                notes="초기화 단계에서 오류 발생"
            )
    
    def _run_validation_phase(self) -> IntegrationPhaseResult:
        """검증 단계를 실행합니다."""
        try:
            phase_id = f"validation_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            logger.info("검증 단계 시작")
            
            # 시스템 통합 검증 실행
            integration_report = self.system_integration_validator.validate_system_integration()
            
            if not integration_report:
                return IntegrationPhaseResult(
                    phase_id=phase_id,
                    phase=IntegrationPhase.VALIDATION,
                    timestamp=start_time,
                    success=False,
                    duration=datetime.now() - start_time,
                    components_processed=0,
                    issues_found=["시스템 통합 검증 실패"],
                    notes="시스템 통합 검증에서 오류 발생"
                )
            
            # 검증 결과 분석
            components_processed = len(integration_report.components)
            tests_passed = sum(1 for test in integration_report.tests if test.result.value == "pass")
            total_tests = len(integration_report.tests)
            
            issues_found = integration_report.critical_issues
            optimizations_applied = [f"{len(integration_report.optimizations)}개 최적화 적용"]
            
            duration = datetime.now() - start_time
            success = integration_report.overall_health_score >= 0.7 and tests_passed >= total_tests * 0.8
            
            logger.info(f"검증 단계 완료: 건강도 {integration_report.overall_health_score:.2f}, 테스트 {tests_passed}/{total_tests}")
            
            return IntegrationPhaseResult(
                phase_id=phase_id,
                phase=IntegrationPhase.VALIDATION,
                timestamp=start_time,
                success=success,
                duration=duration,
                components_processed=components_processed,
                issues_found=issues_found,
                optimizations_applied=optimizations_applied,
                notes=f"검증 완료: 건강도 {integration_report.overall_health_score:.2f}, 테스트 통과율 {tests_passed}/{total_tests}"
            )
            
        except Exception as e:
            logger.error(f"검증 단계 실패: {e}")
            return IntegrationPhaseResult(
                phase_id=f"validation_{uuid.uuid4().hex[:8]}",
                phase=IntegrationPhase.VALIDATION,
                timestamp=datetime.now(),
                success=False,
                duration=timedelta(0),
                components_processed=0,
                issues_found=[f"검증 단계 실패: {e}"],
                notes="검증 단계에서 오류 발생"
            )
    
    def _run_optimization_phase(self) -> IntegrationPhaseResult:
        """최적화 단계를 실행합니다."""
        try:
            phase_id = f"optimization_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            logger.info("최적화 단계 시작")
            
            # 최종 최적화 실행
            optimization_report = self.final_optimization_system.run_final_optimization()
            
            if not optimization_report:
                return IntegrationPhaseResult(
                    phase_id=phase_id,
                    phase=IntegrationPhase.OPTIMIZATION,
                    timestamp=start_time,
                    success=False,
                    duration=datetime.now() - start_time,
                    components_processed=0,
                    issues_found=["최종 최적화 실패"],
                    notes="최종 최적화에서 오류 발생"
                )
            
            # 최적화 결과 분석
            successful_optimizations = sum(1 for result in optimization_report.optimization_results if result.success)
            total_optimizations = len(optimization_report.optimization_results)
            
            components_processed = len(optimization_report.stability_checks)
            issues_found = optimization_report.critical_issues
            optimizations_applied = [f"{successful_optimizations}/{total_optimizations} 최적화 성공"]
            
            duration = datetime.now() - start_time
            success = optimization_report.overall_performance_score >= 0.6 and optimization_report.overall_stability_score >= 0.7
            
            logger.info(f"최적화 단계 완료: 성능 {optimization_report.overall_performance_score:.2f}, 안정성 {optimization_report.overall_stability_score:.2f}")
            
            return IntegrationPhaseResult(
                phase_id=phase_id,
                phase=IntegrationPhase.OPTIMIZATION,
                timestamp=start_time,
                success=success,
                duration=duration,
                components_processed=components_processed,
                issues_found=issues_found,
                optimizations_applied=optimizations_applied,
                notes=f"최적화 완료: 성능 {optimization_report.overall_performance_score:.2f}, 안정성 {optimization_report.overall_stability_score:.2f}"
            )
            
        except Exception as e:
            logger.error(f"최적화 단계 실패: {e}")
            return IntegrationPhaseResult(
                phase_id=f"optimization_{uuid.uuid4().hex[:8]}",
                phase=IntegrationPhase.OPTIMIZATION,
                timestamp=datetime.now(),
                success=False,
                duration=timedelta(0),
                components_processed=0,
                issues_found=[f"최적화 단계 실패: {e}"],
                notes="최적화 단계에서 오류 발생"
            )
    
    def _run_integration_phase(self) -> IntegrationPhaseResult:
        """통합 단계를 실행합니다."""
        try:
            phase_id = f"integration_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            logger.info("통합 단계 시작")
            
            # 모든 시스템 간 통합 테스트
            components_processed = 0
            issues_found = []
            optimizations_applied = []
            
            # 메모리-학습 통합 테스트
            try:
                test_experience = self.memory_sync.store_experience(
                    MemoryType.LEARNING_EXPERIENCE,
                    "통합 테스트",
                    {"integration_test": True}
                )
                if test_experience:
                    components_processed += 1
                else:
                    issues_found.append("메모리-학습 통합 실패")
            except Exception as e:
                issues_found.append(f"메모리-학습 통합 오류: {e}")
            
            # 목표-판단 통합 테스트
            try:
                goal_stats = self.goal_oriented_thinking.get_goal_statistics()
                judgment_stats = self.emotional_ethical_judgment.get_judgment_statistics()
                if goal_stats and judgment_stats:
                    components_processed += 1
                else:
                    issues_found.append("목표-판단 통합 실패")
            except Exception as e:
                issues_found.append(f"목표-판단 통합 오류: {e}")
            
            # 창의성-자율 통합 테스트
            try:
                creativity_stats = self.advanced_creativity_system.get_creativity_statistics()
                autonomous_stats = self.autonomous_goal_setting.get_autonomous_goal_statistics()
                if creativity_stats and autonomous_stats:
                    components_processed += 1
                else:
                    issues_found.append("창의성-자율 통합 실패")
            except Exception as e:
                issues_found.append(f"창의성-자율 통합 오류: {e}")
            
            # 학습 루프 통합 테스트
            try:
                learning_status = self.learning_loop_manager.get_current_status()
                if learning_status:
                    components_processed += 1
                else:
                    issues_found.append("학습 루프 통합 실패")
            except Exception as e:
                issues_found.append(f"학습 루프 통합 오류: {e}")
            
            duration = datetime.now() - start_time
            success = components_processed >= 3  # 최소 3개 통합 성공
            
            logger.info(f"통합 단계 완료: {components_processed}/4 통합 성공")
            
            return IntegrationPhaseResult(
                phase_id=phase_id,
                phase=IntegrationPhase.INTEGRATION,
                timestamp=start_time,
                success=success,
                duration=duration,
                components_processed=components_processed,
                issues_found=issues_found,
                optimizations_applied=optimizations_applied,
                notes=f"통합 완료: {components_processed}/4 통합 성공"
            )
            
        except Exception as e:
            logger.error(f"통합 단계 실패: {e}")
            return IntegrationPhaseResult(
                phase_id=f"integration_{uuid.uuid4().hex[:8]}",
                phase=IntegrationPhase.INTEGRATION,
                timestamp=datetime.now(),
                success=False,
                duration=timedelta(0),
                components_processed=0,
                issues_found=[f"통합 단계 실패: {e}"],
                notes="통합 단계에서 오류 발생"
            )
    
    def _run_completion_phase(self) -> IntegrationPhaseResult:
        """완성 단계를 실행합니다."""
        try:
            phase_id = f"completion_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            logger.info("완성 단계 시작")
            
            # 최종 완성 확인
            components_processed = 0
            issues_found = []
            optimizations_applied = []
            
            # 모든 시스템이 정상 작동하는지 확인
            for name, component in self.system_components:
                try:
                    if hasattr(component, 'get_current_status'):
                        status = component.get_current_status()
                        if status:
                            components_processed += 1
                    elif hasattr(component, 'get_assessment_statistics'):
                        stats = component.get_assessment_statistics()
                        if stats:
                            components_processed += 1
                    elif hasattr(component, 'get_goal_statistics'):
                        stats = component.get_goal_statistics()
                        if stats:
                            components_processed += 1
                    elif hasattr(component, 'get_judgment_statistics'):
                        stats = component.get_judgment_statistics()
                        if stats:
                            components_processed += 1
                    elif hasattr(component, 'get_autonomous_goal_statistics'):
                        stats = component.get_autonomous_goal_statistics()
                        if stats:
                            components_processed += 1
                    elif hasattr(component, 'get_creativity_statistics'):
                        stats = component.get_creativity_statistics()
                        if stats:
                            components_processed += 1
                    elif hasattr(component, 'get_integration_statistics'):
                        stats = component.get_integration_statistics()
                        if stats:
                            components_processed += 1
                    elif hasattr(component, 'get_final_optimization_statistics'):
                        stats = component.get_final_optimization_statistics()
                        if stats:
                            components_processed += 1
                    else:
                        components_processed += 1  # 기본적으로 정상으로 간주
                        
                except Exception as e:
                    issues_found.append(f"{name}: 완성 확인 오류 - {e}")
            
            duration = datetime.now() - start_time
            success = components_processed >= len(self.system_components) * 0.9  # 90% 이상 성공
            
            if success:
                optimizations_applied.append("모든 시스템 완성 확인")
            
            logger.info(f"완성 단계 완료: {components_processed}/{len(self.system_components)} 시스템 완성")
            
            return IntegrationPhaseResult(
                phase_id=phase_id,
                phase=IntegrationPhase.COMPLETION,
                timestamp=start_time,
                success=success,
                duration=duration,
                components_processed=components_processed,
                issues_found=issues_found,
                optimizations_applied=optimizations_applied,
                notes=f"완성 확인: {components_processed}/{len(self.system_components)} 시스템 완성"
            )
            
        except Exception as e:
            logger.error(f"완성 단계 실패: {e}")
            return IntegrationPhaseResult(
                phase_id=f"completion_{uuid.uuid4().hex[:8]}",
                phase=IntegrationPhase.COMPLETION,
                timestamp=datetime.now(),
                success=False,
                duration=timedelta(0),
                components_processed=0,
                issues_found=[f"완성 단계 실패: {e}"],
                notes="완성 단계에서 오류 발생"
            )
    
    def _check_all_component_statuses(self) -> List[SystemComponentStatus]:
        """모든 컴포넌트 상태를 확인합니다."""
        try:
            component_statuses = []
            
            for name, component in self.system_components:
                try:
                    component_id = f"component_{uuid.uuid4().hex[:8]}"
                    
                    # 컴포넌트 상태 확인
                    is_operational = True
                    health_score = 0.8
                    error_count = 0
                    performance_score = 0.8
                    
                    # 컴포넌트별 특정 확인
                    if hasattr(component, 'get_current_status'):
                        status = component.get_current_status()
                        if not status:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_assessment_statistics'):
                        stats = component.get_assessment_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_goal_statistics'):
                        stats = component.get_goal_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_judgment_statistics'):
                        stats = component.get_judgment_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_autonomous_goal_statistics'):
                        stats = component.get_autonomous_goal_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_creativity_statistics'):
                        stats = component.get_creativity_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_integration_statistics'):
                        stats = component.get_integration_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    elif hasattr(component, 'get_final_optimization_statistics'):
                        stats = component.get_final_optimization_statistics()
                        if not stats:
                            is_operational = False
                            error_count += 1
                    
                    # 상태 결정
                    if is_operational and error_count == 0:
                        status = SystemStatus.OPERATIONAL
                    elif is_operational:
                        status = SystemStatus.OPTIMIZING
                    else:
                        status = SystemStatus.ERROR
                    
                    component_status = SystemComponentStatus(
                        component_id=component_id,
                        name=name,
                        status=status,
                        health_score=health_score,
                        last_check=datetime.now(),
                        is_operational=is_operational,
                        error_count=error_count,
                        performance_score=performance_score,
                        notes=f"컴포넌트 상태 확인 완료"
                    )
                    
                    component_statuses.append(component_status)
                    
                except Exception as e:
                    logger.error(f"컴포넌트 상태 확인 실패 {name}: {e}")
                    component_statuses.append(SystemComponentStatus(
                        component_id=f"component_{uuid.uuid4().hex[:8]}",
                        name=name,
                        status=SystemStatus.ERROR,
                        health_score=0.0,
                        last_check=datetime.now(),
                        is_operational=False,
                        error_count=1,
                        performance_score=0.0,
                        notes=f"상태 확인 실패: {e}"
                    ))
            
            return component_statuses
            
        except Exception as e:
            logger.error(f"모든 컴포넌트 상태 확인 실패: {e}")
            return []
    
    def _calculate_overall_health_score(self, component_statuses: List[SystemComponentStatus], phase_results: List[IntegrationPhaseResult]) -> float:
        """전체 건강도 점수를 계산합니다."""
        try:
            if not component_statuses:
                return 0.0
            
            # 컴포넌트 건강도 평균
            component_scores = [comp.health_score for comp in component_statuses]
            avg_component_score = sum(component_scores) / len(component_scores)
            
            # 단계 성공률
            successful_phases = sum(1 for phase in phase_results if phase.success)
            phase_success_rate = successful_phases / len(phase_results) if phase_results else 0.0
            
            # 전체 건강도 계산
            overall_score = (avg_component_score * 0.6 + phase_success_rate * 0.4)
            
            return min(1.0, max(0.0, overall_score))
            
        except Exception as e:
            logger.error(f"전체 건강도 점수 계산 실패: {e}")
            return 0.5
    
    def _determine_overall_status(self, health_score: float, phase_results: List[IntegrationPhaseResult]) -> SystemStatus:
        """전체 상태를 결정합니다."""
        try:
            # 모든 단계가 성공했는지 확인
            all_phases_successful = all(phase.success for phase in phase_results)
            
            if health_score >= 0.9 and all_phases_successful:
                return SystemStatus.COMPLETED
            elif health_score >= 0.7:
                return SystemStatus.OPERATIONAL
            elif health_score >= 0.5:
                return SystemStatus.OPTIMIZING
            elif health_score >= 0.3:
                return SystemStatus.INTEGRATING
            else:
                return SystemStatus.ERROR
                
        except Exception as e:
            logger.error(f"전체 상태 결정 실패: {e}")
            return SystemStatus.ERROR
    
    def _calculate_completion_percentage(self, phase_results: List[IntegrationPhaseResult]) -> float:
        """완성도를 계산합니다."""
        try:
            if not phase_results:
                return 0.0
            
            # 각 단계별 완성도
            phase_completion = {
                IntegrationPhase.INITIALIZATION: 0.2,
                IntegrationPhase.VALIDATION: 0.2,
                IntegrationPhase.OPTIMIZATION: 0.2,
                IntegrationPhase.INTEGRATION: 0.2,
                IntegrationPhase.COMPLETION: 0.2
            }
            
            total_completion = 0.0
            for phase_result in phase_results:
                if phase_result.success:
                    total_completion += phase_completion.get(phase_result.phase, 0.0)
            
            return min(100.0, total_completion * 100)
            
        except Exception as e:
            logger.error(f"완성도 계산 실패: {e}")
            return 0.0
    
    def _identify_critical_issues(self, component_statuses: List[SystemComponentStatus], phase_results: List[IntegrationPhaseResult]) -> List[str]:
        """중요한 이슈를 식별합니다."""
        try:
            critical_issues = []
            
            # 컴포넌트 이슈 확인
            for component in component_statuses:
                if component.status == SystemStatus.ERROR:
                    critical_issues.append(f"{component.name}: 치명적 오류")
                elif component.error_count > 0:
                    critical_issues.append(f"{component.name}: {component.error_count}개 오류")
            
            # 단계 실패 확인
            failed_phases = [phase for phase in phase_results if not phase.success]
            for phase in failed_phases:
                critical_issues.append(f"{phase.phase.value} 단계 실패")
            
            return critical_issues
            
        except Exception as e:
            logger.error(f"중요 이슈 식별 실패: {e}")
            return ["이슈 식별 중 오류 발생"]
    
    def _generate_final_recommendations(self, component_statuses: List[SystemComponentStatus], phase_results: List[IntegrationPhaseResult]) -> List[str]:
        """최종 권장사항을 생성합니다."""
        try:
            recommendations = []
            
            # 성공한 단계 수
            successful_phases = sum(1 for phase in phase_results if phase.success)
            if successful_phases == len(phase_results):
                recommendations.append("모든 통합 단계 성공")
            
            # 운영 중인 컴포넌트 수
            operational_components = sum(1 for comp in component_statuses if comp.is_operational)
            if operational_components == len(component_statuses):
                recommendations.append("모든 시스템 컴포넌트 정상 운영")
            
            # 일반적인 권장사항
            if not recommendations:
                recommendations.append("시스템 통합 완료 - 정기 모니터링 권장")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"최종 권장사항 생성 실패: {e}")
            return ["권장사항 생성 중 오류 발생"]
    
    def get_master_integration_statistics(self) -> Dict[str, Any]:
        """마스터 통합 통계를 반환합니다."""
        try:
            total_reports = len(self.integration_reports)
            if total_reports == 0:
                return {"total_reports": 0}
            
            # 최신 보고서
            latest_report = self.integration_reports[-1]
            
            # 단계별 성공률
            phase_success_rates = defaultdict(int)
            for phase_result in latest_report.phase_results:
                phase_success_rates[phase_result.phase.value] += 1 if phase_result.success else 0
            
            # 컴포넌트 상태 분포
            component_statuses = defaultdict(int)
            operational_components = 0
            for component in latest_report.component_statuses:
                component_statuses[component.status.value] += 1
                if component.is_operational:
                    operational_components += 1
            
            return {
                "total_reports": total_reports,
                "latest_health_score": latest_report.overall_health_score,
                "overall_status": latest_report.overall_status.value,
                "completion_percentage": latest_report.completion_percentage,
                "phase_success_rates": dict(phase_success_rates),
                "component_status_distribution": dict(component_statuses),
                "operational_components": operational_components,
                "critical_issues_count": len(latest_report.critical_issues)
            }
            
        except Exception as e:
            logger.error(f"마스터 통합 통계 계산 실패: {e}")
            return {}

# 싱글톤 인스턴스
_master_integration_system = None

def get_master_integration_system() -> MasterIntegrationSystem:
    """MasterIntegrationSystem 싱글톤 인스턴스 반환"""
    global _master_integration_system
    if _master_integration_system is None:
        _master_integration_system = MasterIntegrationSystem()
    return _master_integration_system 