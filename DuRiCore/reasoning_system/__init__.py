#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 패키지

추론 시스템을 모듈화한 패키지입니다.
"""

# 기존 모듈들 (하위 호환성 유지)
# Adaptive 모듈
from .adaptive.dynamic_reasoning_engine import DynamicReasoningEngine
from .adaptive.evolutionary_improvement import EvolutionaryImprovementMechanism
from .adaptive.feedback_loop import FeedbackLoopSystem
from .adaptive.learning_integration import LearningIntegrationInterface
from .consistency.integration_evaluator import (IntegrationAssessment,
                                                IntegrationEvaluator)
from .consistency.knowledge_conflict import (ConflictResolutionStrategy,
                                             KnowledgeConflict,
                                             KnowledgeConflictResolver)
# Consistency 모듈
from .consistency.logical_connectivity import (LogicalConnection,
                                               LogicalConnectionType,
                                               LogicalConnectivityValidator)
# Data structures
from .data_structures import *
# Efficiency 모듈
from .efficiency.dynamic_resource_allocator import (DynamicResourceAllocator,
                                                    ResourceAllocation,
                                                    ResourceType)
from .efficiency.learning_strategy_optimizer import (LearningOptimization,
                                                     LearningStrategy,
                                                     LearningStrategyOptimizer)
from .efficiency.optimization_strategy import \
    OptimizationResult as EfficiencyOptimizationResult
from .efficiency.optimization_strategy import \
    OptimizationStrategy as EfficiencyOptimizationStrategy
from .efficiency.performance_monitor import (PerformanceMetrics,
                                             PerformanceMonitor)
# Integration 모듈
from .integration.conflict_detection import (ConflictDetectionSystem,
                                             ConflictType, IntegrationConflict)
from .integration.priority_system import (IntegrationPriority,
                                          IntegrationPriorityItem,
                                          IntegrationPrioritySystem)
from .integration.resolution_algorithm import (ResolutionAlgorithm,
                                               ResolutionMethod)
from .integration.success_monitoring import (IntegrationMonitor,
                                             IntegrationSuccess,
                                             SuccessMonitoringSystem)
from .reasoning_engine.decision_maker import (DecisionContext,
                                              DecisionCriteria, DecisionMaker,
                                              DecisionOption, DecisionResult,
                                              DecisionType)
# Reasoning Engine 모듈
from .reasoning_engine.inference_engine import (InferenceContext,
                                                InferenceEngine,
                                                InferenceResult, InferenceType)
from .reasoning_engine.logic_processor import (LogicalChain, LogicalRule,
                                               LogicAnalysis, LogicProcessor,
                                               LogicType)
# Reasoning Optimization 모듈
from .reasoning_optimization.reasoning_optimizer import (OptimizationAnalysis,
                                                         OptimizationResult,
                                                         OptimizationStrategy,
                                                         OptimizationTarget,
                                                         OptimizationType,
                                                         ReasoningOptimizer)
from .reasoning_strategies.abductive_reasoning import (AbductiveAnalysis,
                                                       AbductiveExplanation,
                                                       AbductiveHypothesis,
                                                       AbductiveObservation,
                                                       AbductiveReasoning,
                                                       AbductiveType)
# Reasoning Strategies 모듈
from .reasoning_strategies.deductive_reasoning import (DeductiveAnalysis,
                                                       DeductiveConclusion,
                                                       DeductivePremise,
                                                       DeductiveReasoning,
                                                       DeductiveRule,
                                                       DeductiveRuleType)
from .reasoning_strategies.inductive_reasoning import (InductiveAnalysis,
                                                       InductiveGeneralization,
                                                       InductiveObservation,
                                                       InductivePattern,
                                                       InductiveReasoning,
                                                       InductiveType)

__all__ = [
    # Reasoning Engine
    "InferenceEngine",
    "InferenceType",
    "InferenceContext",
    "InferenceResult",
    "LogicProcessor",
    "LogicType",
    "LogicalRule",
    "LogicalChain",
    "LogicAnalysis",
    "DecisionMaker",
    "DecisionType",
    "DecisionCriteria",
    "DecisionOption",
    "DecisionResult",
    "DecisionContext",
    # Reasoning Strategies
    "DeductiveReasoning",
    "DeductiveRuleType",
    "DeductivePremise",
    "DeductiveConclusion",
    "DeductiveRule",
    "DeductiveAnalysis",
    "InductiveReasoning",
    "InductiveType",
    "InductiveObservation",
    "InductivePattern",
    "InductiveGeneralization",
    "InductiveAnalysis",
    "AbductiveReasoning",
    "AbductiveType",
    "AbductiveObservation",
    "AbductiveHypothesis",
    "AbductiveExplanation",
    "AbductiveAnalysis",
    # Reasoning Optimization
    "ReasoningOptimizer",
    "OptimizationType",
    "OptimizationTarget",
    "OptimizationStrategy",
    "OptimizationResult",
    "OptimizationAnalysis",
    # 기존 모듈들 (하위 호환성)
    # Adaptive
    "DynamicReasoningEngine",
    "LearningIntegrationInterface",
    "FeedbackLoopSystem",
    "EvolutionaryImprovementMechanism",
    # Consistency
    "LogicalConnectivityValidator",
    "LogicalConnection",
    "LogicalConnectionType",
    "KnowledgeConflictResolver",
    "KnowledgeConflict",
    "ConflictResolutionStrategy",
    "IntegrationEvaluator",
    "IntegrationAssessment",
    # Integration
    "ConflictDetectionSystem",
    "IntegrationConflict",
    "ConflictType",
    "ResolutionAlgorithm",
    "ResolutionMethod",
    "IntegrationPrioritySystem",
    "IntegrationPriorityItem",
    "IntegrationPriority",
    "SuccessMonitoringSystem",
    "IntegrationSuccess",
    "IntegrationMonitor",
    # Efficiency
    "DynamicResourceAllocator",
    "ResourceAllocation",
    "ResourceType",
    "LearningStrategyOptimizer",
    "LearningOptimization",
    "LearningStrategy",
    "PerformanceMonitor",
    "PerformanceMetrics",
    "EfficiencyOptimizationStrategy",
    "EfficiencyOptimizationResult",
]
