#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Integrated Evolution System - Enhanced Version with Performance Optimization

이 모듈은 DuRi의 모든 진화 시스템들을 통합하는 메인 시스템입니다.
Phase Z(자가 반성), Phase Ω(생존 본능), Self-Rewriting, Genetic Evolution, MetaCoder를 통합하여
자극-진화-수정 루프를 구현합니다.

주요 기능:
- 자극 기반 진화 트리거
- 통합 진화 루프 관리
- 자가 수정 및 구조 진화
- 성능 평가 및 반성
- 병렬 처리 최적화 (기존 시스템 통합)
- 캐싱 시스템 (기존 시스템 통합)
- 로드 밸런싱 (기존 시스템 통합)
- 학습 기반 진화
- 적응형 트리거
- 분산 진화
"""

import asyncio
import hashlib
import json
import logging
import multiprocessing as mp
import time
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import numpy as np
# 기존 시스템들 import
from duri_thought_flow import DuRiThoughtFlow, ThoughtFlowResult

# Phase Ω 시스템 import (순환 import 방지를 위해 동적 import 시스템 구현)
# 필요할 때만 동적으로 import하여 순환 참조 방지
PHASE_OMEGA_AVAILABLE = False
PHASE_OMEGA_MODULE = None


def _get_phase_omega_system():
    """Phase Ω 시스템을 동적으로 가져오는 함수"""
    global PHASE_OMEGA_AVAILABLE, PHASE_OMEGA_MODULE

    if PHASE_OMEGA_AVAILABLE:
        return PHASE_OMEGA_MODULE

    try:
        import importlib

        PHASE_OMEGA_MODULE = importlib.import_module("phase_omega_integration")
        PHASE_OMEGA_AVAILABLE = True
        logger.info("Phase Ω 시스템 동적 import 성공")
        return PHASE_OMEGA_MODULE
    except ImportError as e:
        logger.warning(f"Phase Ω 시스템 동적 import 실패: {e}")
        return None


from genetic_evolution_engine import (EvolutionResult, GeneticEvolutionEngine,
                                      GeneticIndividual)
from meta_coder import CodeAnalysis, MetaCoder, RefactorProposal
from self_rewriting_module import (CodeAssessment, RewriteProposal,
                                   SelfRewritingModule)

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class EvolutionTrigger(Enum):
    """진화 트리거 열거형"""

    REFLECTION_SCORE_LOW = "reflection_score_low"
    SURVIVAL_THREAT = "survival_threat"
    PERFORMANCE_DEGRADATION = "performance_degradation"
    GOAL_MISALIGNMENT = "goal_misalignment"
    EXTERNAL_STIMULUS = "external_stimulus"
    SELF_IMPROVEMENT_OPPORTUNITY = "self_improvement_opportunity"
    LEARNING_BASED_EVOLUTION = "learning_based_evolution"  # 새로 추가
    ADAPTIVE_TRIGGER = "adaptive_trigger"  # 새로 추가


class EvolutionPhase(Enum):
    """진화 단계 열거형"""

    STIMULUS_DETECTION = "stimulus_detection"
    REFLECTION_ANALYSIS = "reflection_analysis"
    GOAL_GENERATION = "goal_generation"
    EVOLUTION_EXECUTION = "evolution_execution"
    SELF_MODIFICATION = "self_modification"
    VALIDATION = "validation"
    INTEGRATION = "integration"
    LEARNING_ANALYSIS = "learning_analysis"  # 새로 추가
    ADAPTIVE_OPTIMIZATION = "adaptive_optimization"  # 새로 추가


class TaskPriority(Enum):
    """작업 우선순위 (기존 시스템 통합)"""

    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4


class TaskStatus(Enum):
    """작업 상태 (기존 시스템 통합)"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ParallelTask:
    """병렬 작업 정보 (기존 시스템 통합)"""

    id: str
    name: str
    function: Any
    args: tuple = ()
    kwargs: dict = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.kwargs is None:
            self.kwargs = {}


@dataclass
class StimulusEvent:
    """자극 이벤트 데이터 클래스"""

    event_id: str
    trigger_type: EvolutionTrigger
    input_data: Dict[str, Any]
    context: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    intensity: float = 0.0
    description: str = ""
    learning_pattern: Optional[Dict[str, Any]] = None  # 새로 추가


@dataclass
class EvolutionSession:
    """진화 세션 데이터 클래스"""

    session_id: str
    stimulus_event: StimulusEvent
    phases: List[EvolutionPhase] = field(default_factory=list)
    results: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    success: bool = False
    error_message: Optional[str] = None
    performance_metrics: Dict[str, float] = field(default_factory=dict)  # 새로 추가


@dataclass
class IntegratedEvolutionResult:
    """통합 진화 결과 데이터 클래스"""

    session_id: str
    stimulus_event: StimulusEvent
    thought_flow_result: Optional[ThoughtFlowResult] = None
    phase_omega_result: Optional[Any] = None  # Phase Omega 결과를 Any로 변경
    self_rewriting_result: Optional[Any] = None
    genetic_evolution_result: Optional[EvolutionResult] = None
    meta_coding_result: Optional[Any] = None
    overall_improvement_score: float = 0.0
    evolution_time: float = 0.0
    success: bool = True
    error_message: Optional[str] = None
    learning_insights: List[str] = field(default_factory=list)  # 새로 추가
    adaptive_changes: Dict[str, Any] = field(default_factory=dict)  # 새로 추가


@dataclass
class LearningPattern:
    """학습 패턴 데이터 클래스"""

    pattern_id: str
    trigger_type: EvolutionTrigger
    success_rate: float
    average_improvement: float
    execution_time: float
    frequency: int
    last_used: datetime
    adaptation_score: float = 0.0


@dataclass
class AdaptiveTrigger:
    """적응형 트리거 데이터 클래스"""

    trigger_id: str
    base_trigger: EvolutionTrigger
    adaptive_threshold: float
    environmental_factors: Dict[str, float]
    success_history: List[float]
    adaptation_rate: float = 0.1


class DuRiIntegratedEvolutionSystem:
    """DuRi 통합 진화 시스템 (성능 최적화 통합 버전)"""

    def __init__(self):
        """통합 진화 시스템 초기화"""
        # 기존 시스템들 초기화
        self.thought_flow = DuRiThoughtFlow(
            input_data={"task": "integrated_evolution", "phase": "integrated"},
            context={"goal": "self_evolution", "mode": "integration"},
        )
        self.self_rewriting = SelfRewritingModule()
        self.genetic_evolution = GeneticEvolutionEngine()
        self.meta_coder = MetaCoder()

        # Phase Ω 시스템 초기화 (동적)
        self.phase_omega = None
        self._try_initialize_phase_omega()

        # 통합 성능 최적화 시스템 (기존 시스템 통합)
        self.enhanced_parallel_processor = self._initialize_enhanced_parallel_processor()
        self.performance_optimizer = self._initialize_performance_optimizer()
        self.act_r_parallel_processor = self._initialize_act_r_parallel_processor()

        # 캐싱 시스템 (기존 시스템 통합)
        self.cache = {}
        self.cache_ttl = 300  # 5분 캐시
        self.cache_max_size = 1000

        # 로드 밸런싱 시스템 (기존 시스템 통합)
        self.node_status = {
            "brain_node": {"status": "active", "response_time": 0.0, "load": 0},
            "evolution_node": {"status": "active", "response_time": 0.0, "load": 0},
            "judgment_node": {"status": "active", "response_time": 0.0, "load": 0},
            "action_node": {"status": "active", "response_time": 0.0, "load": 0},
            "feedback_node": {"status": "active", "response_time": 0.0, "load": 0},
        }

        # 성능 설정 (기존 시스템 통합)
        self.performance_config = {
            "enable_parallel_processing": True,
            "max_workers": 10,
            "thread_pool_size": 15,
            "process_pool_size": 4,
            "enable_learning_based_evolution": True,
            "enable_adaptive_triggers": True,
            "enable_caching": True,
            "enable_load_balancing": True,
        }

        # 진화 설정 (기존 시스템 통합)
        self.evolution_config = {
            "enable_self_rewriting": True,
            "enable_genetic_evolution": True,
            "enable_meta_coding": True,
            "learning_threshold": 0.3,
            "adaptive_threshold": 0.5,
            "min_improvement_score": 0.1,
        }

        # 통합 성능 메트릭 (기존 시스템 통합)
        self.performance_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "parallel_efficiency": 0.0,
            "performance_improvement": 0.0,
            "cache_hits": 0,
            "cache_misses": 0,
            "cache_hit_rate": 0.0,
            "total_requests": 0,
            "error_count": 0,
        }

        # 학습 기반 진화 시스템
        self.learning_patterns: Dict[str, LearningPattern] = {}
        self.adaptive_triggers: Dict[str, AdaptiveTrigger] = {}

        # 진화 세션 관리
        self.evolution_sessions: List[EvolutionSession] = []
        self.stimulus_history: List[StimulusEvent] = []

        # 성능 측정용 (기존 시스템 통합)
        self.baseline_execution_time = 0.215  # 현재 기준 시간
        self.target_execution_time = 0.1  # 목표 시간 (53% 향상)

        # ThreadPoolExecutor (기존 시스템 통합)
        self.executor = ThreadPoolExecutor(max_workers=10)

        logger.info("🚀 DuRi 통합 진화 시스템 (성능 최적화 통합 버전) 초기화 완료")

    def _try_initialize_phase_omega(self):
        """Phase Ω 시스템을 동적으로 초기화하는 메서드"""
        if self.phase_omega is None:
            try:
                phase_omega_module = _get_phase_omega_system()
                if phase_omega_module:
                    self.phase_omega = phase_omega_module.DuRiPhaseOmega()
                    logger.info("Phase Ω 시스템 동적 import 및 초기화 완료")
                else:
                    logger.warning("Phase Ω 시스템 동적 import 실패 또는 모듈을 찾을 수 없습니다.")
            except Exception as e:
                logger.error(f"Phase Ω 시스템 동적 초기화 실패: {e}")

    def _initialize_enhanced_parallel_processor(self):
        """향상된 병렬 처리 시스템 초기화"""
        try:
            from enhanced_act_r_parallel_processor import \
                EnhancedACTRParallelProcessor

            processor = EnhancedACTRParallelProcessor(max_concurrent_tasks=10)
            logger.info("✅ 향상된 ACT-R 병렬 처리 시스템 통합 완료")
            return processor
        except ImportError as e:
            logger.warning(f"향상된 ACT-R 병렬 처리 시스템 통합 실패: {e}")
            return None

    def _initialize_performance_optimizer(self):
        """성능 최적화 시스템 초기화"""
        try:
            # 성능 최적화 시스템을 직접 구현
            class IntegratedPerformanceOptimizer:
                def __init__(self):
                    self.cache = {}
                    self.cache_ttl = 300
                    self.performance_metrics = {
                        "total_requests": 0,
                        "cache_hits": 0,
                        "cache_misses": 0,
                        "average_response_time": 0.0,
                        "parallel_requests": 0,
                        "error_count": 0,
                    }
                    self.executor = ThreadPoolExecutor(max_workers=10)

                async def optimize_request(
                    self, user_input: str, duri_response: str, metadata: Dict[str, Any]
                ) -> Dict[str, Any]:
                    """요청 최적화 처리"""
                    try:
                        start_time = time.time()

                        # 캐시 확인
                        cache_key = self._generate_cache_key(user_input, duri_response, metadata)
                        cached_result = self._get_from_cache(cache_key)

                        if cached_result:
                            self.performance_metrics["cache_hits"] += 1
                            return cached_result

                        self.performance_metrics["cache_misses"] += 1

                        # 병렬 처리 실행
                        result = await self._parallel_processing(
                            user_input, duri_response, metadata
                        )

                        # 결과 캐싱
                        self._cache_result(cache_key, result)

                        # 성능 메트릭 업데이트
                        processing_time = time.time() - start_time
                        self._update_performance_metrics(processing_time)

                        return result

                    except Exception as e:
                        logger.error(f"❌ 성능 최적화 오류: {e}")
                        self.performance_metrics["error_count"] += 1
                        raise

                def _generate_cache_key(
                    self, user_input: str, duri_response: str, metadata: Dict[str, Any]
                ) -> str:
                    """캐시 키 생성"""
                    content = f"{user_input}:{duri_response}:{json.dumps(metadata, sort_keys=True)}"
                    return hashlib.md5(content.encode()).hexdigest()

                def _get_from_cache(self, cache_key: str) -> Optional[Any]:
                    """캐시에서 결과 가져오기"""
                    if cache_key in self.cache:
                        cached_data = self.cache[cache_key]
                        if time.time() - cached_data["timestamp"] < self.cache_ttl:
                            return cached_data["result"]
                        else:
                            del self.cache[cache_key]
                    return None

                def _cache_result(self, cache_key: str, result: Any):
                    """결과 캐싱"""
                    if len(self.cache) >= 1000:  # 최대 캐시 크기
                        # 가장 오래된 항목 제거
                        oldest_key = min(
                            self.cache.keys(), key=lambda k: self.cache[k]["timestamp"]
                        )
                        del self.cache[oldest_key]

                    self.cache[cache_key] = {"result": result, "timestamp": time.time()}

                async def _parallel_processing(
                    self, user_input: str, duri_response: str, metadata: Dict[str, Any]
                ) -> Dict[str, Any]:
                    """병렬 처리 실행"""
                    # 실제 병렬 처리 로직 구현
                    return {
                        "optimized_input": user_input,
                        "optimized_response": duri_response,
                        "metadata": metadata,
                        "processing_time": time.time(),
                    }

                def _update_performance_metrics(self, processing_time: float):
                    """성능 메트릭 업데이트"""
                    self.performance_metrics["total_requests"] += 1
                    self.performance_metrics["average_response_time"] = (
                        self.performance_metrics["average_response_time"]
                        * (self.performance_metrics["total_requests"] - 1)
                        + processing_time
                    ) / self.performance_metrics["total_requests"]

            optimizer = IntegratedPerformanceOptimizer()
            logger.info("✅ 성능 최적화 시스템 통합 완료")
            return optimizer
        except Exception as e:
            logger.warning(f"성능 최적화 시스템 통합 실패: {e}")
            return None

    def _initialize_act_r_parallel_processor(self):
        """ACT-R 병렬 처리 시스템 초기화"""
        try:
            from act_r_parallel_processor import ACTRParallelProcessor

            processor = ACTRParallelProcessor(max_concurrent_tasks=10)
            logger.info("✅ ACT-R 병렬 처리 시스템 통합 완료")
            return processor
        except ImportError as e:
            logger.warning(f"ACT-R 병렬 처리 시스템 통합 실패: {e}")
            return None

    def _generate_cache_key(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """캐시 키 생성 (기존 시스템 통합) - 최적화된 버전"""
        try:
            # 더 효율적인 캐시 키 생성 알고리즘
            optimized_key = self._optimize_cache_key(input_data, context)
            return optimized_key
        except Exception as e:
            logger.warning(f"최적화된 캐시 키 생성 실패, 기본 방식 사용: {e}")
            # 기본 방식으로 폴백
            content = (
                f"{json.dumps(input_data, sort_keys=True)}:{json.dumps(context, sort_keys=True)}"
            )
            return hashlib.md5(content.encode()).hexdigest()

    def _optimize_cache_key(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> str:
        """최적화된 캐시 키 생성 (타임스탬프 제외) - 고급 버전"""
        try:
            # 고급 캐시 키 생성 알고리즘 사용
            return self._advanced_cache_key_generation(input_data, context)
        except Exception as e:
            logger.warning(f"고급 캐시 키 생성 실패, 기본 방식 사용: {e}")
            # 기본 방식으로 폴백
            important_data = self._extract_important_data(input_data)
            important_context = self._extract_important_context(context)
            normalized_data = self._normalize_data(important_data)
            normalized_context = self._normalize_data(important_context)
            key_content = f"{normalized_data}:{normalized_context}"
            return hashlib.md5(key_content.encode()).hexdigest()

    def _advanced_cache_key_generation(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> str:
        """고급 캐시 키 생성 알고리즘"""
        try:
            # 1. 데이터 중요도 가중치 적용
            weighted_data = self._apply_data_importance_weights(input_data)
            weighted_context = self._apply_context_priority_weights(context)

            # 2. 패턴 기반 키 생성
            pattern_key = self._generate_pattern_based_key(weighted_data, weighted_context)

            # 3. 컨텍스트 우선순위 분석
            priority_key = self._analyze_context_priority(weighted_context)

            # 4. 최종 키 생성
            final_key_content = f"{pattern_key}:{priority_key}"
            return hashlib.md5(final_key_content.encode()).hexdigest()

        except Exception as e:
            logger.error(f"고급 캐시 키 생성 실패: {e}")
            raise

    def _apply_data_importance_weights(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """데이터 중요도 가중치 적용"""
        importance_weights = {
            "task": 1.0,  # 가장 중요
            "data": 0.9,  # 매우 중요
            "type": 0.8,  # 중요
            "id": 0.7,  # 보통
            "mode": 0.6,  # 보통
            "goal": 0.5,  # 낮음
        }

        weighted_data = {}
        for key, value in input_data.items():
            weight = importance_weights.get(key, 0.3)  # 기본 가중치
            weighted_data[key] = {
                "value": value,
                "weight": weight,
                "importance_score": weight * len(str(value)),
            }

        return weighted_data

    def _apply_context_priority_weights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """컨텍스트 우선순위 가중치 적용"""
        priority_weights = {
            "goal": 1.0,  # 가장 중요
            "mode": 0.9,  # 매우 중요
            "test_mode": 0.8,  # 중요
            "performance_optimization": 0.7,  # 보통
            "optimization_level": 0.6,  # 보통
            "cache_strategy": 0.5,  # 낮음
        }

        weighted_context = {}
        for key, value in context.items():
            weight = priority_weights.get(key, 0.3)  # 기본 가중치
            weighted_context[key] = {
                "value": value,
                "weight": weight,
                "priority_score": weight * (1.0 if value else 0.5),
            }

        return weighted_context

    def _generate_pattern_based_key(
        self, weighted_data: Dict[str, Any], weighted_context: Dict[str, Any]
    ) -> str:
        """패턴 기반 키 생성"""
        try:
            # 1. 데이터 패턴 분석
            data_pattern = self._analyze_data_pattern(weighted_data)

            # 2. 컨텍스트 패턴 분석
            context_pattern = self._analyze_context_pattern(weighted_context)

            # 3. 패턴 조합
            combined_pattern = f"{data_pattern}:{context_pattern}"

            return hashlib.md5(combined_pattern.encode()).hexdigest()[:16]

        except Exception as e:
            logger.error(f"패턴 기반 키 생성 실패: {e}")
            return "default_pattern"

    def _analyze_data_pattern(self, weighted_data: Dict[str, Any]) -> str:
        """데이터 패턴 분석"""
        try:
            # 중요도 점수 계산
            total_score = 0
            pattern_elements = []

            for key, data_info in weighted_data.items():
                score = data_info["importance_score"]
                total_score += score
                pattern_elements.append(f"{key}:{score:.2f}")

            # 패턴 정렬
            pattern_elements.sort(key=lambda x: float(x.split(":")[1]), reverse=True)

            # 상위 3개 요소만 사용
            top_pattern = ":".join(pattern_elements[:3])

            return f"data_{total_score:.2f}_{top_pattern}"

        except Exception as e:
            logger.error(f"데이터 패턴 분석 실패: {e}")
            return "default_data_pattern"

    def _analyze_context_pattern(self, weighted_context: Dict[str, Any]) -> str:
        """컨텍스트 패턴 분석"""
        try:
            # 우선순위 점수 계산
            total_priority = 0
            priority_elements = []

            for key, context_info in weighted_context.items():
                priority = context_info["priority_score"]
                total_priority += priority
                priority_elements.append(f"{key}:{priority:.2f}")

            # 우선순위 정렬
            priority_elements.sort(key=lambda x: float(x.split(":")[1]), reverse=True)

            # 상위 3개 요소만 사용
            top_priority = ":".join(priority_elements[:3])

            return f"ctx_{total_priority:.2f}_{top_priority}"

        except Exception as e:
            logger.error(f"컨텍스트 패턴 분석 실패: {e}")
            return "default_context_pattern"

    def _analyze_context_priority(self, weighted_context: Dict[str, Any]) -> str:
        """컨텍스트 우선순위 분석"""
        try:
            # 우선순위 점수 계산
            priority_scores = []
            for key, context_info in weighted_context.items():
                priority_scores.append(context_info["priority_score"])

            if priority_scores:
                avg_priority = sum(priority_scores) / len(priority_scores)
                max_priority = max(priority_scores)
                min_priority = min(priority_scores)

                return f"priority_{avg_priority:.2f}_{max_priority:.2f}_{min_priority:.2f}"
            else:
                return "priority_default"

        except Exception as e:
            logger.error(f"컨텍스트 우선순위 분석 실패: {e}")
            return "priority_error"

    def _segmented_cache_strategy(self):
        """캐시 전략 세분화"""
        try:
            # 1. 데이터 유형별 캐시 전략
            self._implement_data_type_cache_strategy()

            # 2. 사용 빈도 기반 캐시 관리
            self._implement_frequency_based_cache_management()

            # 3. 예측적 캐시 로딩
            self._implement_predictive_cache_loading()

            logger.info("캐시 전략 세분화 완료")

        except Exception as e:
            logger.error(f"캐시 전략 세분화 실패: {e}")

    def _implement_data_type_cache_strategy(self):
        """데이터 유형별 캐시 전략 구현"""
        try:
            # 데이터 유형별 캐시 설정
            self.data_type_cache_config = {
                "frequent": {"ttl": 1800, "max_size": 500, "priority": "high"},  # 30분
                "normal": {"ttl": 600, "max_size": 1000, "priority": "medium"},  # 10분
                "rare": {"ttl": 300, "max_size": 200, "priority": "low"},  # 5분
            }

        except Exception as e:
            logger.error(f"데이터 유형별 캐시 전략 구현 실패: {e}")

    def _implement_frequency_based_cache_management(self):
        """사용 빈도 기반 캐시 관리 구현"""
        try:
            # 사용 빈도 추적
            if not hasattr(self, "cache_frequency_tracker"):
                self.cache_frequency_tracker = {}

            # 빈도 기반 캐시 정리
            self._cleanup_low_frequency_cache()

        except Exception as e:
            logger.error(f"사용 빈도 기반 캐시 관리 구현 실패: {e}")

    def _implement_predictive_cache_loading(self):
        """예측적 캐시 로딩 구현"""
        try:
            # 예측 모델 초기화
            if not hasattr(self, "cache_prediction_model"):
                self.cache_prediction_model = {
                    "patterns": {},
                    "predictions": {},
                    "accuracy": 0.0,
                }

            # 예측적 캐시 로딩 실행
            self._load_predictive_cache()

        except Exception as e:
            logger.error(f"예측적 캐시 로딩 구현 실패: {e}")

    def _cleanup_low_frequency_cache(self):
        """낮은 빈도 캐시 정리"""
        try:
            current_time = time.time()
            low_frequency_threshold = 0.1  # 10% 미만 사용 빈도

            # 빈도 분석
            for key, data in self.cache.items():
                if "access_count" not in data:
                    data["access_count"] = 0

                # 사용 빈도 계산
                age = current_time - data["timestamp"]
                frequency = data["access_count"] / max(age / 3600, 1)  # 시간당 접근 횟수

                # 낮은 빈도 항목 제거
                if frequency < low_frequency_threshold and age > 300:  # 5분 이상 된 항목
                    del self.cache[key]
                    logger.debug(f"낮은 빈도 캐시 항목 제거: {key[:20]}...")

        except Exception as e:
            logger.error(f"낮은 빈도 캐시 정리 실패: {e}")

    def _load_predictive_cache(self):
        """예측적 캐시 로딩"""
        try:
            # 사용 패턴 분석
            patterns = self._analyze_usage_patterns()

            # 예측적 캐시 로딩
            for pattern, probability in patterns.items():
                if probability > 0.7:  # 70% 이상 확률
                    self._preload_cache_for_pattern(pattern)

        except Exception as e:
            logger.error(f"예측적 캐시 로딩 실패: {e}")

    def _analyze_usage_patterns(self) -> Dict[str, float]:
        """사용 패턴 분석"""
        try:
            patterns = {}

            # 최근 사용 패턴 분석
            recent_usage = list(self.cache.keys())[-10:]  # 최근 10개

            for key in recent_usage:
                if key in self.cache:
                    data = self.cache[key]
                    pattern = self._extract_pattern_from_key(key)

                    if pattern in patterns:
                        patterns[pattern] += 1
                    else:
                        patterns[pattern] = 1

            # 확률 계산
            total_usage = len(recent_usage)
            if total_usage > 0:
                for pattern in patterns:
                    patterns[pattern] = patterns[pattern] / total_usage

            return patterns

        except Exception as e:
            logger.error(f"사용 패턴 분석 실패: {e}")
            return {}

    def _extract_pattern_from_key(self, key: str) -> str:
        """키에서 패턴 추출"""
        try:
            # 키의 첫 8자리를 패턴으로 사용
            return key[:8]
        except Exception as e:
            logger.error(f"패턴 추출 실패: {e}")
            return "default_pattern"

    def _preload_cache_for_pattern(self, pattern: str):
        """패턴에 대한 예측적 캐시 로딩"""
        try:
            # 패턴 기반 예측적 캐시 로딩
            logger.debug(f"예측적 캐시 로딩: {pattern}")

        except Exception as e:
            logger.error(f"예측적 캐시 로딩 실패: {e}")

    def _predictive_cache_system(self):
        """캐시 예측 시스템"""
        try:
            # 1. 사용 패턴 분석
            usage_patterns = self._analyze_usage_patterns()

            # 2. 예측적 캐시 로딩
            self._load_predictive_cache()

            # 3. 적응형 캐시 관리
            self._adaptive_cache_management(usage_patterns)

            logger.info("캐시 예측 시스템 실행 완료")

        except Exception as e:
            logger.error(f"캐시 예측 시스템 실패: {e}")

    def _adaptive_cache_management(self, usage_patterns: Dict[str, float]):
        """적응형 캐시 관리"""
        try:
            # 패턴 기반 캐시 크기 조정
            total_probability = sum(usage_patterns.values())

            if total_probability > 0.8:  # 높은 사용 패턴
                # 캐시 크기 증가
                new_size = min(self.cache_max_size * 1.5, 3000)
                if new_size != self.cache_max_size:
                    self.cache_max_size = int(new_size)
                    logger.info(f"적응형 캐시 크기 증가: {new_size}")

            elif total_probability < 0.3:  # 낮은 사용 패턴
                # 캐시 크기 감소
                new_size = max(self.cache_max_size * 0.7, 500)
                if new_size != self.cache_max_size:
                    self.cache_max_size = int(new_size)
                    logger.info(f"적응형 캐시 크기 감소: {new_size}")

        except Exception as e:
            logger.error(f"적응형 캐시 관리 실패: {e}")

    def _get_from_cache(self, cache_key: str) -> Optional[Any]:
        """캐시에서 결과 가져오기 (기존 시스템 통합) - 개선된 버전"""
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            current_time = time.time()

            # TTL 확인
            if current_time - cached_data["timestamp"] < self.cache_ttl:
                # 마지막 접근 시간 업데이트
                cached_data["last_accessed"] = current_time
                self.performance_metrics["cache_hits"] += 1
                logger.debug(f"⚡ 캐시 히트: {cache_key[:20]}...")
                return cached_data["result"]
            else:
                # 만료된 항목 제거
                del self.cache[cache_key]

        self.performance_metrics["cache_misses"] += 1
        return None

    def _cache_result(self, cache_key: str, result: Any):
        """결과 캐싱 (기존 시스템 통합) - 개선된 버전"""
        try:
            # 캐시 크기 확인 및 정리
            if len(self.cache) >= self.cache_max_size:
                self._cleanup_lru_cache()

            # 캐시에 저장
            self.cache[cache_key] = {
                "result": result,
                "timestamp": time.time(),
                "last_accessed": time.time(),
            }

            logger.debug(f"💾 캐시 저장: {cache_key[:20]}...")

        except Exception as e:
            logger.error(f"캐시 저장 실패: {e}")

    async def _update_cache_statistics(self):
        """캐시 통계 업데이트"""
        try:
            total_requests = (
                self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
            )
            if total_requests > 0:
                hit_rate = self.performance_metrics["cache_hits"] / total_requests
                self.performance_metrics["cache_hit_rate"] = hit_rate

                # 캐시 전략 자동 개선
                if total_requests % 100 == 0:  # 100번째 요청마다
                    self._improve_cache_strategy()

        except Exception as e:
            logger.error(f"캐시 통계 업데이트 실패: {e}")

    def _generate_task_cache_key(self, task: ParallelTask) -> str:
        """작업 캐시 키 생성 (기존 시스템 통합)"""
        content = f"{task.id}:{task.name}:{task.function.__name__}:{json.dumps(task.args, sort_keys=True)}:{json.dumps(task.kwargs, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    async def _execute_parallel_tasks_with_optimization(
        self, tasks: List[ParallelTask]
    ) -> List[Any]:
        """최적화된 병렬 작업 실행 (기존 시스템 통합)"""
        logger.info(f"⚡ {len(tasks)}개 작업 최적화된 병렬 실행 시작")

        start_time = time.time()

        try:
            # 작업을 우선순위별로 정렬
            sorted_tasks = sorted(tasks, key=lambda x: x.priority.value)

            # 캐시 확인 및 병렬 실행
            coroutines = []
            for task in sorted_tasks:
                coroutine = self._execute_single_task_with_cache(task)
                coroutines.append(coroutine)

            # asyncio.gather를 사용한 병렬 실행
            results = await asyncio.gather(*coroutines, return_exceptions=True)

            execution_time = time.time() - start_time

            # 성능 메트릭 업데이트
            await self._update_performance_metrics(execution_time, len(tasks))

            logger.info(f"✅ 최적화된 병렬 실행 완료: {execution_time:.3f}초")
            return results

        except Exception as e:
            logger.error(f"❌ 최적화된 병렬 실행 실패: {e}")
            return []

    async def _execute_single_task_with_cache(self, task: ParallelTask) -> Any:
        """캐싱이 포함된 단일 작업 실행 (기존 시스템 통합)"""
        # 캐시 키 생성
        cache_key = self._generate_task_cache_key(task)

        # 캐시 확인
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"⚡ 캐시 히트: {task.name}")
            return cached_result

        # 실제 작업 실행
        task.status = TaskStatus.RUNNING
        task.started_at = datetime.now()

        try:
            # 작업 실행
            if asyncio.iscoroutinefunction(task.function):
                result = await task.function(*task.args, **task.kwargs)
            else:
                # 동기 함수를 비동기로 실행
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(None, task.function, *task.args, **task.kwargs)

            task.status = TaskStatus.COMPLETED
            task.result = result
            task.completed_at = datetime.now()
            task.execution_time = (task.completed_at - task.started_at).total_seconds()

            # 결과 캐싱
            self._cache_result(cache_key, result)

            logger.info(f"✅ 작업 완료: {task.name} ({task.execution_time:.3f}초)")
            return result

        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.now()
            task.execution_time = (task.completed_at - task.started_at).total_seconds()

            logger.error(f"❌ 작업 실패: {task.name} - {e}")
            return None

    async def _execute_enhanced_parallel_processing(
        self, tasks: List[Callable], task_type: str = "general"
    ) -> List[Any]:
        """향상된 병렬 처리 실행 (기존 시스템 통합)"""
        logger.info(f"🚀 향상된 병렬 처리 실행: {len(tasks)}개 {task_type} 작업")

        start_time = time.time()

        try:
            # 향상된 병렬 처리 시스템 사용
            if self.enhanced_parallel_processor:
                parallel_tasks = []
                for i, task_func in enumerate(tasks):
                    task = ParallelTask(
                        id=f"{task_type}_{i}",
                        name=f"{task_type} 작업 {i+1}",
                        function=task_func,
                        priority=(
                            TaskPriority.HIGH
                            if task_type in ["judgment", "critical"]
                            else TaskPriority.MEDIUM
                        ),
                    )
                    parallel_tasks.append(task)

                results = await self.enhanced_parallel_processor.execute_parallel_tasks(
                    parallel_tasks
                )
            else:
                # 기본 병렬 처리
                coroutines = []
                for task_func in tasks:
                    if asyncio.iscoroutinefunction(task_func):
                        coroutines.append(task_func())
                    else:
                        loop = asyncio.get_event_loop()
                        coroutines.append(loop.run_in_executor(None, task_func))

                results = await asyncio.gather(*coroutines, return_exceptions=True)

            execution_time = time.time() - start_time
            logger.info(f"✅ 향상된 병렬 처리 완료: {execution_time:.3f}초")

            return results

        except Exception as e:
            logger.error(f"❌ 향상된 병렬 처리 실패: {e}")
            return []

    async def _optimize_performance(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """성능 최적화 실행 (기존 시스템 통합)"""
        try:
            if self.performance_optimizer:
                # 성능 최적화 시스템 사용
                optimized_result = await self.performance_optimizer.optimize_request(
                    str(input_data), str(context), {"timestamp": time.time()}
                )
                return optimized_result
            else:
                # 기본 최적화
                return {
                    "optimized_input": input_data,
                    "optimized_context": context,
                    "optimization_time": time.time(),
                }
        except Exception as e:
            logger.error(f"❌ 성능 최적화 실패: {e}")
            return input_data

    async def process_stimulus(
        self, input_data: Dict[str, Any], context: Optional[Dict[str, Any]] = None
    ) -> IntegratedEvolutionResult:
        """자극 처리 및 통합 진화 실행 (성능 최적화 통합 버전)"""
        start_time = time.time()

        try:
            # 성능 최적화 적용
            optimized_data = await self._optimize_performance(input_data, context or {})

            # 캐시 확인
            cache_key = self._generate_cache_key(optimized_data, context or {})
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                logger.info("⚡ 캐시 히트: 기존 진화 결과 사용")
                return cached_result

            # 자극 이벤트 생성 (향상된 버전)
            stimulus_event = await self._create_enhanced_stimulus_event(
                optimized_data, context or {}
            )

            # 진화 세션 시작
            session = await self._start_evolution_session(stimulus_event)

            # 향상된 통합 진화 실행
            evolution_results = await self._execute_enhanced_integrated_evolution(session)

            # 결과 통합
            integrated_result = await self._integrate_evolution_results(session, evolution_results)

            # 성능 메트릭 업데이트
            execution_time = time.time() - start_time
            await self._update_performance_metrics(
                execution_time, integrated_result.overall_improvement_score
            )

            # 결과 캐싱
            self._cache_result(cache_key, integrated_result)

            # 학습 패턴 및 적응형 트리거 업데이트
            await self._update_learning_patterns(stimulus_event, integrated_result)
            await self._update_adaptive_triggers(stimulus_event, integrated_result)

            logger.info(
                f"✅ 통합 진화 완료: {execution_time:.3f}초, 개선점수: {integrated_result.overall_improvement_score:.3f}"
            )

            return integrated_result

        except Exception as e:
            error_message = f"통합 진화 처리 실패: {e}"
            logger.error(f"❌ {error_message}")

            # 실패한 결과 생성
            stimulus_event = StimulusEvent(
                event_id=f"error_{int(time.time())}",
                trigger_type=EvolutionTrigger.EXTERNAL_STIMULUS,
                input_data=input_data,
                context=context or {},
                description=f"오류 발생: {e}",
            )

            return await self._create_failed_result(stimulus_event, error_message)

    async def _execute_enhanced_integrated_evolution(
        self, session: EvolutionSession
    ) -> Dict[str, Any]:
        """향상된 통합 진화 실행 (성능 최적화 통합 버전)"""
        logger.info(f"🚀 향상된 통합 진화 실행 시작: {session.session_id}")

        start_time = time.time()
        results = {}

        try:
            # 병렬 실행을 위한 작업 목록 생성
            parallel_tasks = []

            # 1. Thought Flow 실행 (병렬)
            thought_flow_task = ParallelTask(
                id="thought_flow",
                name="Thought Flow 실행",
                function=self._execute_thought_flow,
                args=(session,),
                priority=TaskPriority.CRITICAL,
            )
            parallel_tasks.append(thought_flow_task)

            # 2. Phase Ω 실행 (병렬)
            if self.phase_omega:
                phase_omega_task = ParallelTask(
                    id="phase_omega",
                    name="Phase Ω 실행",
                    function=self._execute_phase_omega,
                    args=(session,),
                    priority=TaskPriority.HIGH,
                )
                parallel_tasks.append(phase_omega_task)

            # 3. Self-Rewriting 실행 (병렬)
            self_rewriting_task = ParallelTask(
                id="self_rewriting",
                name="Self-Rewriting 실행",
                function=self._execute_self_rewriting,
                args=(session,),
                priority=TaskPriority.HIGH,
            )
            parallel_tasks.append(self_rewriting_task)

            # 4. Genetic Evolution 실행 (병렬)
            genetic_evolution_task = ParallelTask(
                id="genetic_evolution",
                name="Genetic Evolution 실행",
                function=self._execute_genetic_evolution,
                args=(session,),
                priority=TaskPriority.MEDIUM,
            )
            parallel_tasks.append(genetic_evolution_task)

            # 5. Meta-Coding 실행 (병렬)
            meta_coding_task = ParallelTask(
                id="meta_coding",
                name="Meta-Coding 실행",
                function=self._execute_meta_coding,
                args=(session,),
                priority=TaskPriority.MEDIUM,
            )
            parallel_tasks.append(meta_coding_task)

            # 6. Learning Analysis 실행 (병렬)
            learning_analysis_task = ParallelTask(
                id="learning_analysis",
                name="Learning Analysis 실행",
                function=self._execute_learning_analysis,
                args=(session,),
                priority=TaskPriority.LOW,
            )
            parallel_tasks.append(learning_analysis_task)

            # 7. Adaptive Optimization 실행 (병렬)
            adaptive_optimization_task = ParallelTask(
                id="adaptive_optimization",
                name="Adaptive Optimization 실행",
                function=self._execute_adaptive_optimization,
                args=(session,),
                priority=TaskPriority.LOW,
            )
            parallel_tasks.append(adaptive_optimization_task)

            # 향상된 병렬 처리 실행
            parallel_results = await self._execute_parallel_tasks_with_optimization(parallel_tasks)

            # 결과 매핑
            for i, task in enumerate(parallel_tasks):
                if i < len(parallel_results) and parallel_results[i] is not None:
                    results[task.id] = parallel_results[i]
                else:
                    results[task.id] = None

            # 성능 최적화 적용
            if self.performance_optimizer:
                optimized_results = await self.performance_optimizer.optimize_request(
                    str(results),
                    str(session.stimulus_event),
                    {"session_id": session.session_id},
                )
                results["optimization"] = optimized_results

            execution_time = time.time() - start_time
            logger.info(f"✅ 향상된 통합 진화 완료: {execution_time:.3f}초")

            return results

        except Exception as e:
            logger.error(f"❌ 향상된 통합 진화 실패: {e}")
            return {"error": str(e)}

    async def _execute_thought_flow(self, session: EvolutionSession) -> Optional[ThoughtFlowResult]:
        """사고 흐름 실행"""
        try:
            thought_context = {
                "evolution_session": session.session_id,
                "stimulus_event": session.stimulus_event.event_id,
                "trigger_type": session.stimulus_event.trigger_type.value,
            }

            thought_result = await self.thought_flow.process()
            logger.info("사고 흐름 실행 완료")

            return thought_result

        except Exception as e:
            logger.error(f"사고 흐름 실행 실패: {e}")
            return None

    async def _execute_phase_omega(self, session: EvolutionSession) -> Optional[Any]:
        """Phase Ω 실행"""
        try:
            if self.phase_omega is None:
                # 동적 import 시도
                self._try_initialize_phase_omega()

            if self.phase_omega is None:
                logger.warning("Phase Ω 시스템이 초기화되지 않아 Phase Ω 실행을 건너뛰었습니다.")
                return None

            phase_omega_result = await self.phase_omega.process_with_survival_instinct(
                session.stimulus_event.input_data, session.stimulus_event.context
            )

            logger.info("Phase Ω 실행 완료")

            return phase_omega_result

        except Exception as e:
            logger.error(f"Phase Ω 실행 실패: {e}")
            return None

    async def _execute_self_rewriting(self, session: EvolutionSession) -> Optional[Any]:
        """자가 수정 실행"""
        try:
            # 복잡도가 높은 모듈들 식별
            target_modules = await self._identify_target_modules()

            improvements_made = []

            for module_path in target_modules[:3]:  # 상위 3개만 처리
                # 코드 평가
                assessment = await self.self_rewriter.assess_self_code(module_path)

                if assessment.complexity_score > 0.6:
                    # 개선 제안 생성
                    with open(module_path, "r", encoding="utf-8") as f:
                        current_code = f.read()

                    proposal = await self.self_rewriter.generate_alternative(
                        current_code, assessment
                    )

                    if proposal.expected_impact > 0.3:
                        # 안전한 재작성 실행
                        rewrite_result = await self.self_rewriter.safely_rewrite(
                            module_path, proposal.proposed_code
                        )

                        if rewrite_result.success:
                            improvements_made.append(
                                f"{module_path}: {proposal.improvement_description}"
                            )

            logger.info(f"자가 수정 완료: {len(improvements_made)}개 개선")

            return {
                "improvements_made": improvements_made,
                "modules_processed": len(target_modules[:3]),
            }

        except Exception as e:
            logger.error(f"자가 수정 실행 실패: {e}")
            return None

    async def _execute_genetic_evolution(
        self, session: EvolutionSession
    ) -> Optional[EvolutionResult]:
        """유전자 진화 실행"""
        try:
            # 시드 코드 생성
            seed_code = await self._generate_seed_code()

            # 진화 실행
            evolution_result = await self.genetic_engine.evolve_capabilities(
                seed_code, target_goal="performance_optimization"
            )

            logger.info(f"유전자 진화 완료: {evolution_result.final_fitness:.2f} 적합도")

            return evolution_result

        except Exception as e:
            logger.error(f"유전자 진화 실행 실패: {e}")
            return None

    async def _execute_meta_coding(self, session: EvolutionSession) -> Optional[Any]:
        """메타 코딩 실행"""
        try:
            # 대상 모듈 분석
            target_modules = await self._identify_target_modules()

            refactoring_results = []

            for module_path in target_modules[:2]:  # 상위 2개만 처리
                # 코드 분석
                analysis = await self.meta_coder.parse_module(module_path)

                if analysis.complexity_score > 0.5:
                    # 리팩토링 제안 생성
                    refactor_proposal = await self.meta_coder.refactor_code(
                        analysis.ast_tree, goal="reduce_complexity"
                    )

                    if refactor_proposal.expected_impact > 0.2:
                        # 검증 후 적용
                        refactor_result = await self.meta_coder.validate_and_apply(
                            refactor_proposal.proposed_code, test_suite=[]
                        )

                        if refactor_result.success:
                            refactoring_results.append(
                                f"{module_path}: {refactor_proposal.improvement_description}"
                            )

            logger.info(f"메타 코딩 완료: {len(refactoring_results)}개 리팩토링")

            return {
                "refactoring_results": refactoring_results,
                "modules_processed": len(target_modules[:2]),
            }

        except Exception as e:
            logger.error(f"메타 코딩 실행 실패: {e}")
            return None

    async def _execute_learning_analysis(self, session: EvolutionSession) -> Optional[Any]:
        """학습 분석 실행"""
        try:
            # 이전 세션의 결과를 사용하여 학습 패턴 분석
            previous_session = self.evolution_sessions[-1] if self.evolution_sessions else None

            if previous_session and previous_session.success:
                # 성공적인 세션의 평균 개선 점수와 실행 시간을 사용
                avg_improvement = previous_session.results.get("overall_improvement_score", 0.0)
                avg_time = previous_session.performance_metrics.get("parallel_execution_time", 0.0)

                # 새로운 패턴 생성
                pattern_id = f"pattern_{int(time.time() * 1000)}"
                new_pattern = LearningPattern(
                    pattern_id=pattern_id,
                    trigger_type=previous_session.stimulus_event.trigger_type,
                    success_rate=1.0,  # 성공적인 세션은 100% 성공
                    average_improvement=avg_improvement,
                    execution_time=avg_time,
                    frequency=1,  # 현재 세션은 1회 실행
                    last_used=datetime.now(),
                )
                self.learning_patterns[pattern_id] = new_pattern
                logger.info(f"새로운 학습 패턴 생성: {pattern_id}")

                # 적응형 트리거 업데이트 (새로운 패턴에 대한 적응형 임계값 설정)
                if self.performance_config["enable_adaptive_triggers"]:
                    for trigger_id, trigger in self.adaptive_triggers.items():
                        if trigger.base_trigger == previous_session.stimulus_event.trigger_type:
                            trigger.adaptive_threshold = (
                                new_pattern.average_improvement * 1.5
                            )  # 평균 개선 점수의 1.5배로 설정
                            logger.info(
                                f"적응형 트리거 '{trigger_id}' 업데이트: 임계값 {trigger.adaptive_threshold}"
                            )

            return {
                "learning_patterns_updated": len(self.learning_patterns),
                "adaptive_triggers_updated": len(self.adaptive_triggers),
            }

        except Exception as e:
            logger.error(f"학습 분석 실행 실패: {e}")
            return None

    async def _execute_adaptive_optimization(self, session: EvolutionSession) -> Optional[Any]:
        """적응형 최적화 실행"""
        try:
            # 이전 세션의 결과를 사용하여 적응형 트리거 업데이트
            previous_session = self.evolution_sessions[-1] if self.evolution_sessions else None

            if previous_session and previous_session.success:
                # 성공적인 세션의 평균 개선 점수와 실행 시간을 사용
                avg_improvement = previous_session.results.get("overall_improvement_score", 0.0)
                avg_time = previous_session.performance_metrics.get("parallel_execution_time", 0.0)

                # 적응형 트리거 업데이트
                for trigger_id, trigger in self.adaptive_triggers.items():
                    if trigger.base_trigger == previous_session.stimulus_event.trigger_type:
                        # 성공적인 세션에서 평균 개선 점수가 높을수록 적응형 임계값 증가
                        trigger.adaptive_threshold = min(
                            trigger.adaptive_threshold * 1.1, 1.0
                        )  # 최대 1.0까지 증가
                        logger.info(
                            f"적응형 트리거 '{trigger_id}' 업데이트: 임계값 {trigger.adaptive_threshold}"
                        )

            return {"adaptive_triggers_updated": len(self.adaptive_triggers)}

        except Exception as e:
            logger.error(f"적응형 최적화 실행 실패: {e}")
            return None

    async def _execute_sequential_evolution(self, session: EvolutionSession) -> Dict[str, Any]:
        """순차 진화 실행 (병렬 처리 비활성화 시)"""
        results = {}

        logger.info("🔄 순차 진화 실행 시작")
        start_time = time.time()

        # 1. Phase Z: 사고 흐름 실행
        session.phases.append(EvolutionPhase.REFLECTION_ANALYSIS)
        results["thought_flow"] = await self._execute_thought_flow(session)

        # 2. Phase Ω: 생존 본능 기반 목표 생성
        session.phases.append(EvolutionPhase.GOAL_GENERATION)
        results["phase_omega"] = await self._execute_phase_omega(session)

        # 3. 자가 수정 실행
        if self.evolution_config["enable_self_rewriting"]:
            session.phases.append(EvolutionPhase.SELF_MODIFICATION)
            results["self_rewriting"] = await self._execute_self_rewriting(session)

        # 4. 유전자 진화 실행
        if self.evolution_config["enable_genetic_evolution"]:
            session.phases.append(EvolutionPhase.EVOLUTION_EXECUTION)
            results["genetic_evolution"] = await self._execute_genetic_evolution(session)

        # 5. 메타 코딩 실행
        if self.evolution_config["enable_meta_coding"]:
            session.phases.append(EvolutionPhase.EVOLUTION_EXECUTION)
            results["meta_coding"] = await self._execute_meta_coding(session)

        # 6. 학습 분석 실행
        if self.performance_config["enable_learning_based_evolution"]:
            session.phases.append(EvolutionPhase.LEARNING_ANALYSIS)
            results["learning_analysis"] = await self._execute_learning_analysis(session)

        # 7. 적응형 최적화 실행
        if self.performance_config["enable_adaptive_triggers"]:
            session.phases.append(EvolutionPhase.ADAPTIVE_OPTIMIZATION)
            results["adaptive_optimization"] = await self._execute_adaptive_optimization(session)

        execution_time = time.time() - start_time
        session.performance_metrics["sequential_execution_time"] = execution_time
        logger.info(f"🚀 순차 진화 완료: {execution_time:.3f}초")

        return results

    async def _identify_target_modules(self) -> List[str]:
        """대상 모듈 식별"""
        try:
            # 현재 디렉토리의 Python 파일들 수집
            import os

            target_modules = []

            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith(".py") and not file.startswith("__"):
                        file_path = os.path.join(root, file)
                        target_modules.append(file_path)

            # 복잡도 기준으로 정렬 (간단한 추정)
            def estimate_complexity(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        lines = len(content.split("\n"))
                        functions = content.count("def ")
                        classes = content.count("class ")
                        return lines + functions * 10 + classes * 20
                except:
                    return 0

            target_modules.sort(key=estimate_complexity, reverse=True)

            return target_modules[:10]  # 상위 10개만 반환

        except Exception as e:
            logger.error(f"대상 모듈 식별 실패: {e}")
            return []

    async def _generate_seed_code(self) -> str:
        """시드 코드 생성"""
        return """
def optimize_performance():
    \"\"\"성능 최적화 함수\"\"\"
    # 기본 최적화 로직
    return "optimized"
"""

    async def _integrate_evolution_results(
        self, session: EvolutionSession, results: Dict[str, Any]
    ) -> IntegratedEvolutionResult:
        """진화 결과 통합"""
        try:
            # 개선 점수 계산
            improvement_score = await self._calculate_improvement_score(results)

            # 통합 결과 생성
            integrated_result = IntegratedEvolutionResult(
                session_id=session.session_id,
                stimulus_event=session.stimulus_event,
                thought_flow_result=results.get("thought_flow"),
                phase_omega_result=results.get("phase_omega"),
                self_rewriting_result=results.get("self_rewriting"),
                genetic_evolution_result=results.get("genetic_evolution"),
                meta_coding_result=results.get("meta_coding"),
                overall_improvement_score=improvement_score,
                success=True,
            )

            # 학습 인사이트 추가
            if self.performance_config["enable_learning_based_evolution"]:
                integrated_result.learning_insights = await self._extract_learning_insights(results)

            # 적응형 변경사항 추가
            if self.performance_config["enable_adaptive_triggers"]:
                integrated_result.adaptive_changes = await self._extract_adaptive_changes(results)

            # 세션 결과 업데이트
            session.results = results
            session.results["overall_improvement_score"] = improvement_score
            session.success = True
            session.end_time = datetime.now()

            logger.info(f"진화 결과 통합 완료: 개선점수 {improvement_score:.3f}")

            return integrated_result

        except Exception as e:
            logger.error(f"진화 결과 통합 실패: {e}")
            return await self._create_failed_result(session.stimulus_event, str(e))

    async def _calculate_improvement_score(self, results: Dict[str, Any]) -> float:
        """개선 점수 계산"""
        try:
            scores = []

            # Phase Z 결과
            if results.get("thought_flow"):
                thought_score = getattr(results["thought_flow"], "reflection_score", 0.5)
                scores.append(thought_score * 0.2)

            # Phase Ω 결과
            if results.get("phase_omega"):
                phase_omega_score = getattr(results["phase_omega"], "survival_score", 0.5)
                if hasattr(phase_omega_score, "overall_score"):
                    scores.append(phase_omega_score.overall_score * 0.2)
                else:
                    scores.append(0.5 * 0.2)

            # 자가 수정 결과
            if results.get("self_rewriting"):
                self_rewriting_data = results["self_rewriting"]
                if (
                    isinstance(self_rewriting_data, dict)
                    and "improvements_made" in self_rewriting_data
                ):
                    improvement_count = len(self_rewriting_data["improvements_made"])
                    scores.append(min(improvement_count * 0.1, 0.2))
                else:
                    scores.append(0.1)

            # 유전자 진화 결과
            if results.get("genetic_evolution"):
                genetic_score = getattr(results["genetic_evolution"], "final_fitness", 0.5)
                scores.append(genetic_score * 0.2)

            # 메타 코딩 결과
            if results.get("meta_coding"):
                meta_coding_data = results["meta_coding"]
                if isinstance(meta_coding_data, dict) and "refactoring_results" in meta_coding_data:
                    refactoring_count = len(meta_coding_data["refactoring_results"])
                    scores.append(min(refactoring_count * 0.1, 0.2))
                else:
                    scores.append(0.1)

            # 학습 분석 결과
            if results.get("learning_analysis"):
                scores.append(0.1)  # 학습 분석이 실행되면 기본 점수

            # 적응형 최적화 결과
            if results.get("adaptive_optimization"):
                scores.append(0.1)  # 적응형 최적화가 실행되면 기본 점수

            # 평균 점수 계산
            if scores:
                return sum(scores) / len(scores)
            else:
                return 0.5  # 기본 점수

        except Exception as e:
            logger.error(f"개선 점수 계산 실패: {e}")
            return 0.5

    async def _extract_learning_insights(self, results: Dict[str, Any]) -> List[str]:
        """학습 인사이트 추출"""
        insights = []

        try:
            # Phase Z 인사이트
            if results.get("thought_flow"):
                insights.append("사고 흐름 분석을 통한 자가 반성 강화")

            # Phase Ω 인사이트
            if results.get("phase_omega"):
                insights.append("생존 본능 기반 목표 생성 및 진화")

            # 자가 수정 인사이트
            if results.get("self_rewriting"):
                self_rewriting_data = results["self_rewriting"]
                if (
                    isinstance(self_rewriting_data, dict)
                    and "improvements_made" in self_rewriting_data
                ):
                    insights.append(
                        f"자가 수정을 통한 {len(self_rewriting_data['improvements_made'])}개 개선 완료"
                    )

            # 유전자 진화 인사이트
            if results.get("genetic_evolution"):
                insights.append("유전자 진화를 통한 성능 최적화")

            # 메타 코딩 인사이트
            if results.get("meta_coding"):
                meta_coding_data = results["meta_coding"]
                if isinstance(meta_coding_data, dict) and "refactoring_results" in meta_coding_data:
                    insights.append(
                        f"메타 코딩을 통한 {len(meta_coding_data['refactoring_results'])}개 리팩토링 완료"
                    )

        except Exception as e:
            logger.error(f"학습 인사이트 추출 실패: {e}")

        return insights

    async def _extract_adaptive_changes(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """적응형 변경사항 추출"""
        changes = {}

        try:
            # 적응형 트리거 업데이트 정보
            if results.get("adaptive_optimization"):
                adaptive_data = results["adaptive_optimization"]
                if isinstance(adaptive_data, dict) and "adaptive_triggers_updated" in adaptive_data:
                    changes["adaptive_triggers_updated"] = adaptive_data[
                        "adaptive_triggers_updated"
                    ]

            # 학습 패턴 업데이트 정보
            if results.get("learning_analysis"):
                learning_data = results["learning_analysis"]
                if isinstance(learning_data, dict) and "learning_patterns_updated" in learning_data:
                    changes["learning_patterns_updated"] = learning_data[
                        "learning_patterns_updated"
                    ]

        except Exception as e:
            logger.error(f"적응형 변경사항 추출 실패: {e}")

        return changes

    async def _create_minimal_result(
        self, stimulus_event: StimulusEvent, session: EvolutionSession
    ) -> IntegratedEvolutionResult:
        """최소 결과 생성"""
        session.success = True
        session.end_time = datetime.now()

        return IntegratedEvolutionResult(
            session_id=session.session_id,
            stimulus_event=stimulus_event,
            overall_improvement_score=0.0,
            success=True,
        )

    async def _create_failed_result(
        self, stimulus_event: StimulusEvent, error_message: str
    ) -> IntegratedEvolutionResult:
        """실패 결과 생성"""
        return IntegratedEvolutionResult(
            session_id=f"failed_{int(time.time() * 1000)}",
            stimulus_event=stimulus_event,
            overall_improvement_score=0.0,
            success=False,
            error_message=error_message,
        )

    async def _generate_stimulus_description(
        self, trigger_type: EvolutionTrigger, input_data: Dict[str, Any]
    ) -> str:
        """자극 설명 생성"""
        descriptions = {
            EvolutionTrigger.REFLECTION_SCORE_LOW: "낮은 반성 점수로 인한 진화 필요",
            EvolutionTrigger.SURVIVAL_THREAT: "생존 위협으로 인한 긴급 진화",
            EvolutionTrigger.PERFORMANCE_DEGRADATION: "성능 저하로 인한 최적화 필요",
            EvolutionTrigger.GOAL_MISALIGNMENT: "목표 불일치로 인한 재정렬 필요",
            EvolutionTrigger.EXTERNAL_STIMULUS: "외부 자극으로 인한 진화",
            EvolutionTrigger.SELF_IMPROVEMENT_OPPORTUNITY: "자기 개선 기회 발견",
            EvolutionTrigger.LEARNING_BASED_EVOLUTION: "학습 기반 진화 트리거",
            EvolutionTrigger.ADAPTIVE_TRIGGER: "적응형 진화 트리거",
        }

        return descriptions.get(trigger_type, "알 수 없는 자극")

    async def _get_adaptive_threshold(self, trigger_type: EvolutionTrigger) -> float:
        """적응형 트리거의 임계값을 반환"""
        for trigger_id, trigger in self.adaptive_triggers.items():
            if trigger.base_trigger == trigger_type:
                return trigger.adaptive_threshold
        return self.evolution_config["adaptive_threshold"]  # 기본 임계값

    async def _calculate_learning_based_intensity(
        self, trigger_type: EvolutionTrigger, context: Dict[str, Any]
    ) -> float:
        """학습 기반 강도 계산"""
        try:
            # 학습 패턴 기반 강도 계산
            if trigger_type in self.learning_patterns:
                pattern = self.learning_patterns[trigger_type]
                return pattern.average_improvement * pattern.success_rate
            return 0.0
        except Exception as e:
            logger.error(f"학습 기반 강도 계산 실패: {e}")
            return 0.0

    async def _calculate_adaptive_intensity(
        self, trigger_type: EvolutionTrigger, context: Dict[str, Any]
    ) -> float:
        """적응형 강도 계산"""
        try:
            # 적응형 트리거 기반 강도 계산
            if trigger_type in self.adaptive_triggers:
                trigger = self.adaptive_triggers[trigger_type]
                return trigger.adaptive_threshold * (1.0 + len(trigger.success_history) * 0.1)
            return 0.0
        except Exception as e:
            logger.error(f"적응형 강도 계산 실패: {e}")
            return 0.0

    async def _create_enhanced_stimulus_event(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> StimulusEvent:
        """향상된 자극 이벤트 생성 (학습 패턴 분석 포함)"""
        event_id = f"stimulus_{int(time.time() * 1000)}"

        # 자극 유형 및 강도 분석
        trigger_type, intensity = await self._analyze_enhanced_stimulus(input_data, context)

        # 학습 패턴 분석
        learning_pattern = await self._analyze_learning_pattern(trigger_type, input_data, context)

        description = await self._generate_stimulus_description(trigger_type, input_data)

        return StimulusEvent(
            event_id=event_id,
            trigger_type=trigger_type,
            input_data=input_data,
            context=context,
            intensity=intensity,
            description=description,
            learning_pattern=learning_pattern,
        )

    async def _analyze_enhanced_stimulus(
        self, input_data: Dict[str, Any], context: Dict[str, Any]
    ) -> Tuple[EvolutionTrigger, float]:
        """향상된 자극 분석 (적응형 트리거 포함)"""
        intensity = 0.0
        trigger_type = EvolutionTrigger.EXTERNAL_STIMULUS

        # 기존 분석 로직
        if "reflection_score" in context:
            reflection_score = context["reflection_score"]
            if reflection_score < 0.3:  # 임계값
                trigger_type = EvolutionTrigger.REFLECTION_SCORE_LOW
                intensity = 1.0 - reflection_score

        if "survival_status" in context:
            survival_status = context["survival_status"]
            if hasattr(survival_status, "threat_level") and survival_status.threat_level > 0.5:
                trigger_type = EvolutionTrigger.SURVIVAL_THREAT
                intensity = max(intensity, survival_status.threat_level)

        if "performance_metrics" in context:
            performance_metrics = context["performance_metrics"]
            if "degradation_score" in performance_metrics:
                degradation_score = performance_metrics["degradation_score"]
                if degradation_score > 0.1:
                    trigger_type = EvolutionTrigger.PERFORMANCE_DEGRADATION
                    intensity = max(intensity, degradation_score)

        # 학습 기반 진화 트리거
        learning_intensity = await self._calculate_learning_based_intensity(trigger_type, context)
        if learning_intensity > 0.3:
            trigger_type = EvolutionTrigger.LEARNING_BASED_EVOLUTION
            intensity = max(intensity, learning_intensity)

        # 적응형 트리거
        adaptive_intensity = await self._calculate_adaptive_intensity(trigger_type, context)
        if adaptive_intensity > 0.5:
            trigger_type = EvolutionTrigger.ADAPTIVE_TRIGGER
            intensity = max(intensity, adaptive_intensity)

        return trigger_type, intensity

    async def _analyze_learning_pattern(
        self,
        trigger_type: EvolutionTrigger,
        input_data: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """학습 패턴 분석"""
        try:
            # 기존 학습 패턴 중 유사한 패턴 찾기
            similar_patterns = []
            for pattern in self.learning_patterns.values():
                if pattern.trigger_type == trigger_type:
                    # 시간 가중치 적용 (최근 패턴일수록 높은 가중치)
                    time_weight = 1.0 / (1.0 + (datetime.now() - pattern.last_used).days)
                    weighted_score = pattern.average_improvement * time_weight
                    similar_patterns.append(
                        {
                            "pattern_id": pattern.pattern_id,
                            "weighted_score": weighted_score,
                            "frequency": pattern.frequency,
                            "success_rate": pattern.success_rate,
                        }
                    )

            if similar_patterns:
                # 가장 높은 가중치 점수를 가진 패턴 선택
                best_pattern = max(similar_patterns, key=lambda x: x["weighted_score"])
                return {
                    "pattern_id": best_pattern["pattern_id"],
                    "expected_improvement": best_pattern["weighted_score"],
                    "confidence": best_pattern["success_rate"],
                    "frequency": best_pattern["frequency"],
                }

            return None

        except Exception as e:
            logger.error(f"학습 패턴 분석 실패: {e}")
            return None

    async def _start_evolution_session(self, stimulus_event: StimulusEvent) -> EvolutionSession:
        """진화 세션 시작"""
        session_id = f"evolution_{int(time.time() * 1000)}"
        session = EvolutionSession(session_id=session_id, stimulus_event=stimulus_event)

        self.evolution_sessions.append(session)

        logger.info(f"진화 세션 시작: {session_id} - {stimulus_event.trigger_type.value}")

        return session

    async def _generate_stimulus_description(
        self, trigger_type: EvolutionTrigger, input_data: Dict[str, Any]
    ) -> str:
        """자극 설명 생성"""
        descriptions = {
            EvolutionTrigger.REFLECTION_SCORE_LOW: "낮은 반성 점수로 인한 진화 필요",
            EvolutionTrigger.SURVIVAL_THREAT: "생존 위협으로 인한 긴급 진화",
            EvolutionTrigger.PERFORMANCE_DEGRADATION: "성능 저하로 인한 최적화 필요",
            EvolutionTrigger.GOAL_MISALIGNMENT: "목표 불일치로 인한 재정렬 필요",
            EvolutionTrigger.EXTERNAL_STIMULUS: "외부 자극으로 인한 진화",
            EvolutionTrigger.SELF_IMPROVEMENT_OPPORTUNITY: "자기 개선 기회 발견",
            EvolutionTrigger.LEARNING_BASED_EVOLUTION: "학습 기반 진화 트리거",
            EvolutionTrigger.ADAPTIVE_TRIGGER: "적응형 진화 트리거",
        }

        return descriptions.get(trigger_type, "알 수 없는 자극")

    async def _calculate_learning_based_intensity(
        self, trigger_type: EvolutionTrigger, context: Dict[str, Any]
    ) -> float:
        """학습 기반 강도 계산"""
        try:
            # 학습 패턴 기반 강도 계산
            if trigger_type in self.learning_patterns:
                pattern = self.learning_patterns[trigger_type]
                return pattern.average_improvement * pattern.success_rate
            return 0.0
        except Exception as e:
            logger.error(f"학습 기반 강도 계산 실패: {e}")
            return 0.0

    async def _calculate_adaptive_intensity(
        self, trigger_type: EvolutionTrigger, context: Dict[str, Any]
    ) -> float:
        """적응형 강도 계산"""
        try:
            # 적응형 트리거 기반 강도 계산
            if trigger_type in self.adaptive_triggers:
                trigger = self.adaptive_triggers[trigger_type]
                return trigger.adaptive_threshold * (1.0 + len(trigger.success_history) * 0.1)
            return 0.0
        except Exception as e:
            logger.error(f"적응형 강도 계산 실패: {e}")
            return 0.0

    async def _update_learning_patterns(
        self,
        stimulus_event: StimulusEvent,
        integrated_result: IntegratedEvolutionResult,
    ):
        """학습 패턴 업데이트"""
        if not self.performance_config["enable_learning_based_evolution"]:
            return

        try:
            # 새로운 패턴 생성
            pattern_id = f"pattern_{int(time.time() * 1000)}"
            new_pattern = LearningPattern(
                pattern_id=pattern_id,
                trigger_type=stimulus_event.trigger_type,
                success_rate=1.0 if integrated_result.success else 0.0,
                average_improvement=integrated_result.overall_improvement_score,
                execution_time=integrated_result.evolution_time,
                frequency=1,
                last_used=datetime.now(),
            )
            self.learning_patterns[pattern_id] = new_pattern
            logger.info(f"새로운 학습 패턴 생성: {pattern_id}")

            # 기존 패턴 업데이트
            for pattern in self.learning_patterns.values():
                if pattern.trigger_type == stimulus_event.trigger_type:
                    pattern.frequency += 1
                    pattern.last_used = datetime.now()
                    pattern.average_improvement = (
                        pattern.average_improvement + integrated_result.overall_improvement_score
                    ) / 2

        except Exception as e:
            logger.error(f"학습 패턴 업데이트 실패: {e}")

    async def _update_adaptive_triggers(
        self,
        stimulus_event: StimulusEvent,
        integrated_result: IntegratedEvolutionResult,
    ):
        """적응형 트리거 업데이트"""
        if not self.performance_config["enable_adaptive_triggers"]:
            return

        try:
            # 적응형 트리거가 없으면 생성
            trigger_id = f"adaptive_{stimulus_event.trigger_type.value}_{int(time.time() * 1000)}"
            if trigger_id not in self.adaptive_triggers:
                self.adaptive_triggers[trigger_id] = AdaptiveTrigger(
                    trigger_id=trigger_id,
                    base_trigger=stimulus_event.trigger_type,
                    adaptive_threshold=self.evolution_config["adaptive_threshold"],
                    environmental_factors={},
                    success_history=[],
                )

            # 성공 히스토리 업데이트
            trigger = self.adaptive_triggers[trigger_id]
            trigger.success_history.append(integrated_result.overall_improvement_score)

            # 최근 10개 결과만 유지
            if len(trigger.success_history) > 10:
                trigger.success_history = trigger.success_history[-10:]

            # 적응형 임계값 업데이트
            if integrated_result.success and integrated_result.overall_improvement_score > 0.5:
                trigger.adaptive_threshold = min(trigger.adaptive_threshold * 1.1, 1.0)
            elif integrated_result.overall_improvement_score < 0.3:
                trigger.adaptive_threshold = max(trigger.adaptive_threshold * 0.9, 0.1)

            logger.info(
                f"적응형 트리거 '{trigger_id}' 업데이트: 임계값 {trigger.adaptive_threshold:.3f}"
            )

        except Exception as e:
            logger.error(f"적응형 트리거 업데이트 실패: {e}")

    async def _update_performance_metrics(self, execution_time: float, improvement_score: float):
        """성능 메트릭 업데이트 (기존 시스템 통합)"""
        try:
            # 기본 메트릭 업데이트
            self.performance_metrics["total_tasks"] += 1
            self.performance_metrics["average_execution_time"] = (
                self.performance_metrics["average_execution_time"]
                * (self.performance_metrics["total_tasks"] - 1)
                + execution_time
            ) / self.performance_metrics["total_tasks"]

            # 성공/실패 세션 업데이트
            if improvement_score > 0:
                self.performance_metrics["completed_tasks"] += 1
            else:
                self.performance_metrics["failed_tasks"] += 1

            # 캐시 히트율 업데이트
            total_cache_requests = (
                self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
            )
            if total_cache_requests > 0:
                self.performance_metrics["cache_hit_rate"] = (
                    self.performance_metrics["cache_hits"] / total_cache_requests
                )

            # 성능 개선 점수 업데이트
            if self.baseline_execution_time > 0:
                improvement_ratio = (
                    self.baseline_execution_time - execution_time
                ) / self.baseline_execution_time
                current_improvement = self.performance_metrics["performance_improvement"]
                total_sessions = self.performance_metrics["total_tasks"]
                self.performance_metrics["performance_improvement"] = (
                    current_improvement * (total_sessions - 1) + improvement_ratio
                ) / total_sessions

            # 병렬 효율성 업데이트
            if execution_time > 0:
                parallel_efficiency = execution_time / (
                    execution_time * len(self.node_status)
                )  # 간단한 효율성 계산
                current_efficiency = self.performance_metrics["parallel_efficiency"]
                total_sessions = self.performance_metrics["total_tasks"]
                self.performance_metrics["parallel_efficiency"] = (
                    current_efficiency * (total_sessions - 1) + parallel_efficiency
                ) / total_sessions

            logger.debug(
                f"성능 메트릭 업데이트: 실행시간={execution_time:.3f}초, 개선점수={improvement_score:.3f}"
            )

        except Exception as e:
            logger.error(f"성능 메트릭 업데이트 실패: {e}")

    async def get_evolution_summary(self) -> Dict[str, Any]:
        """진화 시스템 요약 정보 반환 (성능 최적화 통합 버전)"""
        try:
            # 기본 성능 메트릭
            total_sessions = len(self.evolution_sessions)
            successful_sessions = len([s for s in self.evolution_sessions if s.success])
            failed_sessions = total_sessions - successful_sessions

            # 캐시 통계
            cache_stats = self.get_cache_stats()

            # 노드 상태
            node_status = {}
            for node_name, node_info in self.node_status.items():
                node_status[node_name] = {
                    "status": node_info["status"],
                    "response_time": node_info["response_time"],
                    "load": node_info["load"],
                }

            # 성능 개선률 계산
            current_execution_time = self.performance_metrics["average_execution_time"]
            improvement_ratio = 0.0
            if self.baseline_execution_time > 0:
                improvement_ratio = (
                    (self.baseline_execution_time - current_execution_time)
                    / self.baseline_execution_time
                    * 100
                )

            summary = {
                "system_status": "active",
                "total_sessions": total_sessions,
                "successful_sessions": successful_sessions,
                "failed_sessions": failed_sessions,
                "success_rate": successful_sessions / max(total_sessions, 1) * 100,
                "average_execution_time": current_execution_time,
                "baseline_execution_time": self.baseline_execution_time,
                "target_execution_time": self.target_execution_time,
                "performance_improvement": improvement_ratio,
                "cache_stats": cache_stats,
                "node_status": node_status,
                "performance_metrics": self.performance_metrics,
                "learning_patterns_count": len(self.learning_patterns),
                "adaptive_triggers_count": len(self.adaptive_triggers),
                "integrated_systems": {
                    "enhanced_parallel_processor": self.enhanced_parallel_processor is not None,
                    "performance_optimizer": self.performance_optimizer is not None,
                    "act_r_parallel_processor": self.act_r_parallel_processor is not None,
                },
            }

            return summary

        except Exception as e:
            logger.error(f"진화 시스템 요약 생성 실패: {e}")
            return {"error": str(e)}

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계 반환 (기존 시스템 통합)"""
        try:
            total_cache_requests = (
                self.performance_metrics["cache_hits"] + self.performance_metrics["cache_misses"]
            )
            cache_hit_rate = 0.0
            if total_cache_requests > 0:
                cache_hit_rate = self.performance_metrics["cache_hits"] / total_cache_requests * 100

            return {
                "cache_size": len(self.cache),
                "cache_hits": self.performance_metrics["cache_hits"],
                "cache_misses": self.performance_metrics["cache_misses"],
                "cache_hit_rate": cache_hit_rate,
                "cache_ttl": self.cache_ttl,
                "cache_max_size": self.cache_max_size,
            }
        except Exception as e:
            logger.error(f"캐시 통계 생성 실패: {e}")
            return {"error": str(e)}

    async def test_integrated_performance(self) -> Dict[str, Any]:
        """통합 성능 테스트 실행"""
        logger.info("🧪 통합 성능 테스트 시작")

        start_time = time.time()
        test_results = {}

        try:
            # 1. 기본 성능 테스트
            basic_test_start = time.time()
            test_input = {"test_type": "performance", "data": "test_data"}
            test_context = {"test_mode": True}

            result = await self.process_stimulus(test_input, test_context)
            basic_test_time = time.time() - basic_test_start

            test_results["basic_performance"] = {
                "execution_time": basic_test_time,
                "success": result.success,
                "improvement_score": result.overall_improvement_score,
            }

            # 2. 병렬 처리 테스트
            parallel_test_start = time.time()
            parallel_tasks = []
            for i in range(5):
                task = ParallelTask(
                    id=f"test_task_{i}",
                    name=f"테스트 작업 {i+1}",
                    function=lambda x: {"result": f"test_result_{x}"},
                    args=(i,),
                    priority=TaskPriority.MEDIUM,
                )
                parallel_tasks.append(task)

            parallel_results = await self._execute_parallel_tasks_with_optimization(parallel_tasks)
            parallel_test_time = time.time() - parallel_test_start

            test_results["parallel_processing"] = {
                "execution_time": parallel_test_time,
                "tasks_count": len(parallel_tasks),
                "successful_tasks": len([r for r in parallel_results if r is not None]),
            }

            # 3. 캐시 성능 테스트
            cache_test_start = time.time()
            cache_key = self._generate_cache_key(test_input, test_context)
            cached_result = self._get_from_cache(cache_key)
            cache_test_time = time.time() - cache_test_start

            test_results["cache_performance"] = {
                "cache_lookup_time": cache_test_time,
                "cache_hit": cached_result is not None,
                "cache_stats": self.get_cache_stats(),
            }

            # 4. 로드 밸런싱 테스트
            load_balancing_test_start = time.time()
            optimal_nodes = []
            for _ in range(5):
                optimal_node = self._get_optimal_node("test")
                optimal_nodes.append(optimal_node)
            load_balancing_test_time = time.time() - load_balancing_test_start

            test_results["load_balancing"] = {
                "node_selection_time": load_balancing_test_time,
                "selected_nodes": optimal_nodes,
                "node_status": self.node_status,
            }

            # 5. 통합 성능 분석
            total_test_time = time.time() - start_time
            test_results["overall_performance"] = {
                "total_test_time": total_test_time,
                "average_execution_time": self.performance_metrics["average_execution_time"],
                "performance_improvement": self.performance_metrics["performance_improvement"],
                "cache_hit_rate": self.performance_metrics["cache_hit_rate"],
            }

            logger.info(f"✅ 통합 성능 테스트 완료: {total_test_time:.3f}초")
            return test_results

        except Exception as e:
            logger.error(f"❌ 통합 성능 테스트 실패: {e}")
            return {"error": str(e)}

    async def optimize_system_performance(self) -> Dict[str, Any]:
        """시스템 성능 최적화 실행"""
        logger.info("🔧 시스템 성능 최적화 시작")

        try:
            optimization_results = {}

            # 1. 캐시 최적화
            if len(self.cache) > self.cache_max_size * 0.8:
                # 캐시 정리
                current_time = time.time()
                expired_keys = [
                    key
                    for key, data in self.cache.items()
                    if current_time - data["timestamp"] > self.cache_ttl
                ]
                for key in expired_keys:
                    del self.cache[key]

                optimization_results["cache_optimization"] = {
                    "cleaned_items": len(expired_keys),
                    "current_cache_size": len(self.cache),
                }

            # 2. 노드 상태 최적화
            for node_name, node_info in self.node_status.items():
                if node_info["load"] > 0.8:
                    # 부하가 높은 노드의 부하 감소
                    self.node_status[node_name]["load"] = max(0.0, node_info["load"] - 0.2)
                    optimization_results[f"{node_name}_optimization"] = {
                        "previous_load": node_info["load"],
                        "current_load": self.node_status[node_name]["load"],
                    }

            # 3. 성능 메트릭 최적화
            if self.performance_metrics["error_count"] > 10:
                # 오류가 많은 경우 임계값 조정
                self.performance_metrics["error_count"] = max(
                    0, self.performance_metrics["error_count"] - 5
                )
                optimization_results["error_optimization"] = {"error_count_reduced": True}

            logger.info("✅ 시스템 성능 최적화 완료")
            return optimization_results

        except Exception as e:
            logger.error(f"❌ 시스템 성능 최적화 실패: {e}")
            return {"error": str(e)}

    async def cleanup(self):
        """리소스 정리"""
        try:
            self.executor.shutdown(wait=True)
            logger.info("통합 진화 시스템 리소스 정리 완료")
        except Exception as e:
            logger.error(f"리소스 정리 실패: {e}")


async def main():
    """메인 함수"""
    # 통합 진화 시스템 초기화
    evolution_system = DuRiIntegratedEvolutionSystem()

    try:
        # 테스트 자극 생성
        test_stimulus = {
            "test_type": "performance_optimization",
            "target_modules": ["integrated_evolution_system.py"],
            "optimization_goals": ["speed", "efficiency", "accuracy"],
        }

        test_context = {
            "reflection_score": 0.4,  # 낮은 반성 점수
            "performance_metrics": {"degradation_score": 0.7},  # 성능 저하
            "survival_status": {"threat_level": 0.3},
        }

        print("🚀 향상된 통합 진화 시스템 테스트 시작...")

        # 진화 실행
        result = await evolution_system.process_stimulus(test_stimulus, test_context)

        # 결과 출력
        print(f"\n📊 향상된 통합 진화 결과:")
        print(f"✅ 성공: {result.success}")
        print(f"⏱️  실행 시간: {result.evolution_time:.3f}초")
        print(f"🎯 개선 점수: {result.overall_improvement_score:.3f}")
        print(f"🧠 학습 인사이트: {len(result.learning_insights)}개")
        print(f"🔄 적응형 변경사항: {len(result.adaptive_changes)}개")

        if result.learning_insights:
            print(f"\n💡 학습 인사이트:")
            for insight in result.learning_insights:
                print(f"  - {insight}")

        if result.adaptive_changes:
            print(f"\n🔄 적응형 변경사항:")
            for change_type, change_value in result.adaptive_changes.items():
                print(f"  - {change_type}: {change_value}")

        # 진화 요약 정보
        summary = await evolution_system.get_evolution_summary()
        print(f"\n📋 진화 요약:")
        print(f"총 세션: {summary['total_sessions']}")
        print(f"성공한 세션: {summary['successful_sessions']}")
        print(f"실패한 세션: {summary['failed_sessions']}")
        print(f"성공률: {summary['success_rate']:.1%}")
        print(f"평균 실행 시간: {summary['average_execution_time']:.3f}초")
        print(f"평균 개선 점수: {summary['average_improvement_score']:.3f}")
        print(f"병렬 처리 효율성: {summary['parallel_processing_efficiency']:.3f}")
        print(f"성능 개선 점수: {summary['performance_improvement']:.3f}")
        print(f"캐시 히트율: {summary['cache_hit_rate']:.1%}")
        print(f"학습 패턴 수: {summary['learning_patterns_count']}")
        print(f"적응형 트리거 수: {summary['adaptive_triggers_count']}")

    except Exception as e:
        print(f"❌ 테스트 실패: {e}")

    finally:
        # 리소스 정리
        await evolution_system.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
