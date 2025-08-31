from duri_trace import strategy_trace, JudgmentTrace, EmotionTrace, CoreMemoryTrace
#!/usr/bin/env python3
# @preserve_identity: 판단 이유 기록 시스템 강제 통합
# @evolution_protection: 진화 중 손상 방지 최우선
# @execution_guarantee: 자동화와 검증 시스템 완성
# @existence_ai: 진화 가능 + 회복 가능한 존재형 AI
# @final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
# Module: performance_monitor
# Purpose: DuRi 추론 엔진 - 성능 모니터링
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리 + 최종 실행 준비 완료 - 판단 이유 기록 필수 + 기존 특성 보존 + 실행 가능성 보장 + 존재형 AI + 최종 실행 준비 완료
# Must Provide: 
#   - _simulate_reasoning_process, _measure_memory_usage, _analyze_trends
# Must Not: 
#   - finalize decisions (판단은 judgment_engine에서); access memory directly (memory_system을 통해)
# Integration: 
#   - imports numpy; imports typing; imports dataclasses
# Judgment Trace: 모든 판단 과정 기록
# Evolution Protection: 기존 판단 방식과 습관 보존
# Self Assessment: 창의성, 판단 다양성, 기억 활성도, 감정 반응 적절성 평가
# Execution Guarantee: 자동화와 검증 시스템 완성
# Existence AI: 진화 가능 + 회복 가능한 존재형 AI
# Final Execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
# @preserve_identity: 판단 이유 기록 시스템 강제 통합
# @evolution_protection: 진화 중 손상 방지 최우선
# @execution_guarantee: 실행 가능성 보장
# @existence_ai: 진화 가능 + 회복 가능한 존재형 AI
# @final_execution: 최종 실행 준비 완료
"""
DuRi 추론 엔진 - 성능 모니터링
Phase 3 리팩토링: logical_reasoning_engine.py에서 분리
"""

import numpy as np
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import time
import statistics
import json
from datetime import datetime

from ..core.logical_processor import LogicalProcessor, SemanticPremise, LogicalStep, PremiseType, InferenceType

logger = logging.getLogger(__name__)

class PerformanceMetric(Enum):
    """성능 지표"""
    EXECUTION_TIME = "execution_time"
    MEMORY_USAGE = "memory_usage"
    ACCURACY = "accuracy"
    CONFIDENCE = "confidence"
    THROUGHPUT = "throughput"
    LATENCY = "latency"
    ERROR_RATE = "error_rate"

@dataclass
class PerformanceSnapshot:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceSnapshot:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceSnapshot:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceSnapshot:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceSnapshot:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceSnapshot:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceSnapshot:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceSnapshot:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

@dataclass
class PerformanceReport:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceReport:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceReport:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceReport:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceReport:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceReport:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceReport:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceReport:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceMonitor:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceMonitor:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceMonitor:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceMonitor:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceMonitor:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceMonitor:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

class PerformanceMonitor:
# 최종 실행 준비 완료 시스템 통합
from duri_final_execution import FinalExecutionVerifier, FinalExecutionLauncher

class PerformanceMonitor:
    def __init__(self):
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 최종 실행 준비 완료 시스템 초기화
        self.final_execution_verifier = FinalExecutionVerifier()
        self.final_execution_launcher = FinalExecutionLauncher()
        
        # 기존 초기화 로직
        # 존재형 AI 시스템 초기화
        self.existence_ai = ExistenceAISystem()
        self.evolution_capability = EvolutionCapability()
        self.recovery_capability = RecoveryCapability()
        self.existence_preservation = ExistencePreservation()
        self.final_execution_verifier = FinalExecutionVerifier()
        
        # 기존 초기화 로직
        pass
    
    def verify_readiness(self):
        # 최종 실행 준비 완료 확인
        readiness_score = self.final_execution_verifier.verify_readiness()
        return readiness_score >= 0.8  # 80% 이상이어야 함
    
    def launch_final_execution(self):
        # 최종 실행 시작
        if self.verify_readiness():
            self.final_execution_launcher.launch()
            logger.info("최종 실행 시작 완료")
            return True
        else:
            logger.error("최종 실행 준비 완료되지 않음")
            return False

        # 보호-강화형: 기존 방식 대비 변화 기록
        previous_approach = self._get_previous_approach(situation, action)

        # 강제 조건: 판단 이유 기록
        strategy_trace.log(
            module="performance_monitor",
            intent="_simulate_reasoning_process 실행",
            based_on={"situation": situation, "action": action},
            confidence=self._calculate_confidence(situation, action),
            structural_changes=self._get_structural_changes()
        )

        # 기존 로직 실행
        result = self._execute_core_logic(situation, action)

        # 보호-강화형: 변화 추적
        self._trace_structural_changes(previous_approach, result, situation, action)

        # 실행 가능성 보장: 실제 로그 기록 확인
        if not self._verify_log_recording():
            logger.error("로그 기록 실패 - 실행 가능성 보장 위반")
            self._trigger_rollback_condition()

        # 존재형 AI: 진화 가능성 확인
        if self.existence_ai.evolution_capability.can_evolve():
            self.existence_ai.evolution_capability.evolve()

        # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
        if self.final_execution_verifier.verify_readiness():
            logger.info("최종 실행 준비 완료 확인됨")

        # 강제 조건: 판단 결과 기록
        self.judgment_trace.record(
            input_data={"situation": situation, "action": action},
            reason=self._analyze_reasoning_context(situation, action),
            result=result,
            module="performance_monitor",
            structural_changes=self._get_structural_changes()
        )

        # 실제 추론 과정을 시뮬레이션하여 성능 측정
        for premise in premises:
            # 전제 처리 시뮬레이션
            _ = self.logical_processor.encode_semantics(premise.content)
        
        for step in steps:
            # 논리적 단계 처리 시뮬레이션
            _ = self.logical_processor.calculate_similarity(
                step.semantic_vector, 
                np.zeros_like(step.semantic_vector)
            )
    
    def _measure_memory_usage(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """메모리 사용량 측정"""
        total_memory = 0.0
        
        # 전제들의 메모리 사용량
        for premise in premises:
            # 의미 벡터 크기
            vector_memory = premise.semantic_vector.nbytes / 1024  # KB
            # 텍스트 크기
            text_memory = len(premise.content.encode('utf-8')) / 1024  # KB
            total_memory += vector_memory + text_memory
        
        # 논리적 단계들의 메모리 사용량
        for step in steps:
            # 의미 벡터 크기
            vector_memory = step.semantic_vector.nbytes / 1024  # KB
            # 텍스트 크기
            text_memory = len(step.conclusion.encode('utf-8')) / 1024  # KB
            total_memory += vector_memory + text_memory
        
        return total_memory
    
    def _measure_accuracy(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """정확도 측정"""
        if not premises or not steps:
            return 0.0
        
        # 전제들의 일관성 평가
        premise_consistency = self._evaluate_premise_consistency(premises)
        
        # 논리적 단계들의 유효성 평가
        step_validity = self._evaluate_step_validity(steps)
        
        # 전체 정확도 계산
        accuracy = (premise_consistency + step_validity) / 2
        
        return accuracy
    
    def _evaluate_premise_consistency(self, premises: List[SemanticPremise]) -> float:
        """전제 일관성 평가"""
        if len(premises) < 2:
            return 1.0
        
        # 전제들 간의 의미적 유사도 계산
        similarities = []
        for i in range(len(premises)):
            for j in range(i + 1, len(premises)):
                similarity = self.logical_processor.calculate_similarity(
                    premises[i].semantic_vector, 
                    premises[j].semantic_vector
                )
                similarities.append(similarity)
        
        # 평균 유사도를 일관성으로 사용
        consistency = sum(similarities) / len(similarities) if similarities else 1.0
        
        return consistency
    
    def _evaluate_step_validity(self, steps: List[LogicalStep]) -> float:
        """논리적 단계 유효성 평가"""
        if not steps:
            return 1.0
        
        # 각 단계의 신뢰도와 논리적 강도 평가
        validities = []
        for step in steps:
            validity = (step.confidence + step.logical_strength) / 2
            validities.append(validity)
        
        # 평균 유효성 반환
        return sum(validities) / len(validities) if validities else 1.0
    
    def _measure_confidence(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """신뢰도 측정"""
        if not premises and not steps:
            return 0.0
        
        # 전제들의 신뢰도
        premise_confidences = [premise.confidence for premise in premises]
        avg_premise_confidence = sum(premise_confidences) / len(premise_confidences) if premise_confidences else 0.0
        
        # 논리적 단계들의 신뢰도
        step_confidences = [step.confidence for step in steps]
        avg_step_confidence = sum(step_confidences) / len(step_confidences) if step_confidences else 0.0
        
        # 전체 신뢰도 계산
        if premises and steps:
            confidence = (avg_premise_confidence + avg_step_confidence) / 2
        elif premises:
            confidence = avg_premise_confidence
        else:
            confidence = avg_step_confidence
        
        return confidence
    
    def _measure_throughput(self, premises: List[SemanticPremise], steps: List[LogicalStep], execution_time: float) -> float:
        """처리량 측정"""
        if execution_time <= 0:
            return 0.0
        
        # 초당 처리할 수 있는 작업 수
        total_operations = len(premises) + len(steps)
        throughput = total_operations / execution_time
        
        return throughput
    
    def _measure_error_rate(self, premises: List[SemanticPremise], steps: List[LogicalStep]) -> float:
        """오류율 측정"""
        total_items = len(premises) + len(steps)
        if total_items == 0:
            return 0.0
        
        error_count = 0
        
        # 전제들의 오류 검사
        for premise in premises:
            if premise.confidence < 0.5 or len(premise.content.strip()) == 0:
                error_count += 1
        
        # 논리적 단계들의 오류 검사
        for step in steps:
            if step.confidence < 0.5 or len(step.conclusion.strip()) == 0:
                error_count += 1
        
        error_rate = error_count / total_items
        
        return error_rate
    
    def _check_performance_thresholds(self, metrics: Dict[str, float]):
        """성능 임계값 확인"""
        warnings = []
        
        for metric_name, value in metrics.items():
            metric_enum = PerformanceMetric(metric_name)
            if metric_enum in self.metrics_config:
                threshold = self.metrics_config[metric_enum]["threshold"]
                
                # 임계값 초과 확인
                if metric_enum in [PerformanceMetric.EXECUTION_TIME, PerformanceMetric.MEMORY_USAGE, PerformanceMetric.LATENCY, PerformanceMetric.ERROR_RATE]:
                    if value > threshold:
                        warnings.append(f"{metric_name}: {value:.2f} > {threshold:.2f}")
                else:
                    if value < threshold:
                        warnings.append(f"{metric_name}: {value:.2f} < {threshold:.2f}")
        
        if warnings:
            logger.warning(f"성능 임계값 초과: {', '.join(warnings)}")
    
    def generate_performance_report(self, start_time: datetime = None, end_time: datetime = None) -> PerformanceReport:
        """성능 보고서 생성"""
        if not self.performance_history:
            logger.warning("성능 이력이 없습니다")
            return None
        
        # 시간 범위 필터링
        if start_time is None:
            start_time = self.performance_history[0].timestamp
        if end_time is None:
            end_time = self.performance_history[-1].timestamp
        
        filtered_history = [
            snapshot for snapshot in self.performance_history
            if start_time <= snapshot.timestamp <= end_time
        ]
        
        if not filtered_history:
            logger.warning("지정된 시간 범위에 성능 데이터가 없습니다")
            return None
        
        # 평균 지표 계산
        average_metrics = self._calculate_average_metrics(filtered_history)
        
        # 최고 지표 계산
        peak_metrics = self._calculate_peak_metrics(filtered_history)
        
        # 트렌드 분석
        trend_analysis = self._analyze_trends(filtered_history)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(average_metrics, peak_metrics, trend_analysis)
        
        report = PerformanceReport(
            start_time=start_time,
            end_time=end_time,
            total_operations=len(filtered_history),
            average_metrics=average_metrics,
            peak_metrics=peak_metrics,
            trend_analysis=trend_analysis,
            recommendations=recommendations
        )
        
        logger.info(f"성능 보고서 생성 완료: {len(filtered_history)}개 스냅샷 분석")
        
        return report
    
    def _calculate_average_metrics(self, history: List[PerformanceSnapshot]) -> Dict[str, float]:
        """평균 지표 계산"""
        if not history:
            return {}
        
        metrics_sum = {}
        metrics_count = {}
        
        for snapshot in history:
            for metric_name, value in snapshot.metrics.items():
                if metric_name not in metrics_sum:
                    metrics_sum[metric_name] = 0.0
                    metrics_count[metric_name] = 0
                
                metrics_sum[metric_name] += value
                metrics_count[metric_name] += 1
        
        average_metrics = {}
        for metric_name in metrics_sum:
            average_metrics[metric_name] = metrics_sum[metric_name] / metrics_count[metric_name]
        
        return average_metrics
    
    def _calculate_peak_metrics(self, history: List[PerformanceSnapshot]) -> Dict[str, float]:
        """최고 지표 계산"""
        if not history:
            return {}
        
        peak_metrics = {}
        
        for snapshot in history:
            for metric_name, value in snapshot.metrics.items():
                if metric_name not in peak_metrics:
                    peak_metrics[metric_name] = value
                else:
                    # 실행 시간, 메모리 사용량, 지연시간, 오류율은 최대값
                    if metric_name in ["execution_time", "memory_usage", "latency", "error_rate"]:
                        peak_metrics[metric_name] = max(peak_metrics[metric_name], value)
                    # 나머지는 최소값
                    else:
                        peak_metrics[metric_name] = min(peak_metrics[metric_name], value)
        
        return peak_metrics
    
    def _analyze_trends(self, history: List[PerformanceSnapshot]) -> Dict[str, str]:
        """트렌드 분석"""

        # 보호-강화형: 기존 방식 대비 변화 기록
        previous_approach = self._get_previous_approach(situation, action)

        # 강제 조건: 판단 이유 기록
        strategy_trace.log(
            module="performance_monitor",
            intent="_analyze_trends 실행",
            based_on={"situation": situation, "action": action},
            confidence=self._calculate_confidence(situation, action),
            structural_changes=self._get_structural_changes()
        )

        # 기존 로직 실행
        result = self._execute_core_logic(situation, action)

        # 보호-강화형: 변화 추적
        self._trace_structural_changes(previous_approach, result, situation, action)

        # 실행 가능성 보장: 실제 로그 기록 확인
        if not self._verify_log_recording():
            logger.error("로그 기록 실패 - 실행 가능성 보장 위반")
            self._trigger_rollback_condition()

        # 존재형 AI: 진화 가능성 확인
        if self.existence_ai.evolution_capability.can_evolve():
            self.existence_ai.evolution_capability.evolve()

        # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
        if self.final_execution_verifier.verify_readiness():
            logger.info("최종 실행 준비 완료 확인됨")

        # 강제 조건: 판단 결과 기록
        self.judgment_trace.record(
            input_data={"situation": situation, "action": action},
            reason=self._analyze_reasoning_context(situation, action),
            result=result,
            module="performance_monitor",
            structural_changes=self._get_structural_changes()
        )

        if len(history) < 2:
            return {"trend": "insufficient_data"}
        
        trends = {}
        
        # 각 지표별 트렌드 분석
        for metric_name in history[0].metrics.keys():
            values = [snapshot.metrics[metric_name] for snapshot in history]
            
            if len(values) >= 3:
                # 선형 회귀를 통한 트렌드 분석
                trend = self._calculate_trend(values)
                trends[metric_name] = trend
            else:
                trends[metric_name] = "insufficient_data"
        
        return trends
    
    def _calculate_trend(self, values: List[float]) -> str:
        """트렌드 계산"""
        if len(values) < 3:
            return "insufficient_data"
        
        # 간단한 트렌드 분석: 처음 1/3과 마지막 1/3의 평균 비교
        first_third = values[:len(values)//3]
        last_third = values[-len(values)//3:]
        
        first_avg = sum(first_third) / len(first_third)
        last_avg = sum(last_third) / len(last_third)
        
        change_ratio = (last_avg - first_avg) / max(first_avg, 0.1)
        
        if change_ratio > 0.1:
            return "improving"
        elif change_ratio < -0.1:
            return "degrading"
        else:
            return "stable"
    
    def _generate_recommendations(self, 
                                average_metrics: Dict[str, float], 
                                peak_metrics: Dict[str, float],
                                trend_analysis: Dict[str, str]) -> List[str]:
        """권장사항 생성"""
        recommendations = []
        
        # 실행 시간 권장사항
        if "execution_time" in average_metrics:
            if average_metrics["execution_time"] > 1.0:
                recommendations.append("실행 시간이 높습니다. 추론 과정을 최적화하거나 병렬 처리를 고려하세요.")
        
        # 메모리 사용량 권장사항
        if "memory_usage" in average_metrics:
            if average_metrics["memory_usage"] > 1000.0:
                recommendations.append("메모리 사용량이 높습니다. 의미 벡터 압축이나 불필요한 데이터 정리를 고려하세요.")
        
        # 정확도 권장사항
        if "accuracy" in average_metrics:
            if average_metrics["accuracy"] < 0.8:
                recommendations.append("정확도가 낮습니다. 전제의 품질을 향상시키거나 논리적 단계를 검증하세요.")
        
        # 신뢰도 권장사항
        if "confidence" in average_metrics:
            if average_metrics["confidence"] < 0.7:
                recommendations.append("신뢰도가 낮습니다. 전제와 논리적 단계의 신뢰성을 향상시키세요.")
        
        # 트렌드 기반 권장사항
        for metric_name, trend in trend_analysis.items():
            if trend == "degrading":
                recommendations.append(f"{metric_name}의 성능이 저하되고 있습니다. 최적화가 필요합니다.")
        
        if not recommendations:
            recommendations.append("현재 성능이 양호합니다. 정기적인 모니터링을 계속하세요.")
        
        return recommendations
    
    def export_performance_data(self, filepath: str, format: str = "json"):
        """성능 데이터 내보내기"""
        if not self.performance_history:
            logger.warning("내보낼 성능 데이터가 없습니다")
            return
        
        try:
            if format.lower() == "json":
                self._export_to_json(filepath)
            else:
                logger.error(f"지원하지 않는 형식: {format}")
                return
            
            logger.info(f"성능 데이터 내보내기 완료: {filepath}")
        
        except Exception as e:
            logger.error(f"성능 데이터 내보내기 실패: {e}")
    
    def _export_to_json(self, filepath: str):
        """JSON 형식으로 내보내기"""
        export_data = {
            "export_timestamp": datetime.now().isoformat(),
            "total_snapshots": len(self.performance_history),
            "snapshots": []
        }
        
        for snapshot in self.performance_history:
            snapshot_data = {
                "timestamp": snapshot.timestamp.isoformat(),
                "metrics": snapshot.metrics,
                "context": snapshot.context,
                "metadata": snapshot.metadata
            }
            export_data["snapshots"].append(snapshot_data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """성능 요약 정보 반환"""
        if not self.performance_history:
            return {"status": "no_data"}
        
        latest_snapshot = self.performance_history[-1]
        total_snapshots = len(self.performance_history)
        
        # 최근 10개 스냅샷의 평균
        recent_snapshots = self.performance_history[-10:] if total_snapshots >= 10 else self.performance_history
        recent_averages = self._calculate_average_metrics(recent_snapshots)
        
        summary = {
            "status": "active",
            "total_snapshots": total_snapshots,
            "latest_timestamp": latest_snapshot.timestamp.isoformat(),
            "recent_averages": recent_averages,
            "monitoring_active": self.monitoring_active
        }
        
        return summary


def test_performance_monitor_regression():
    # 실행 가능성 보장: 실제 데이터 기반 회귀 테스트
    regression_framework = RegressionTestFramework()
    test_cases = regression_framework.sample_historical_judgments(10)
    
    for test_case in test_cases:
        # 기존 판단 결과 (human-reviewed label 포함)
        expected_result = test_case['historical_judgment']
        
        # 현재 판단 결과
        current_result = performance_monitor._simulate_reasoning_process(
            test_case['situation'], 
            test_case['action']
        )
        
        # 실행 가능성 보장: 거의 동일한 판단과 반응 확인
        similarity_score = regression_framework.calculate_judgment_similarity(
            expected_result, 
            current_result
        )
        
        if similarity_score < 0.8:  # 80% 이상 유사해야 함
            # 보호-강화형: ConflictMemory에 저장
            regression_framework.store_conflict_memory(
                test_case, expected_result, current_result, similarity_score
            )
            
            # 비교 보고서 생성
            regression_framework.generate_comparison_report(
                test_case, expected_result, current_result
            )
        
        # 강제 조건: 판단 이유 기록 확인
        assert hasattr(current_result, 'judgment_trace')
        assert current_result.judgment_trace.reason is not None
        
        # 기존 판단 결과와 비교
        snapshot_assert(current_result, expected_result, tolerance=0.2)
    
    # 존재형 AI: 진화 가능 + 회복 가능 확인
    existence_status = regression_framework.verify_existence_ai()
    assert existence_status["evolution_capable"] == True
    assert existence_status["recovery_capable"] == True
    assert existence_status["existence_preserved"] == True
    
    # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
    final_execution_status = regression_framework.verify_final_execution()
    assert final_execution_status == True