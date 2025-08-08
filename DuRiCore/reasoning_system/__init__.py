#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 패키지

추론 시스템을 모듈화한 패키지입니다.
"""

# Reasoning Engine 모듈
from .reasoning_engine.inference_engine import InferenceEngine, InferenceType, InferenceContext, InferenceResult
from .reasoning_engine.logic_processor import LogicProcessor, LogicType, LogicalRule, LogicalChain, LogicAnalysis
from .reasoning_engine.decision_maker import DecisionMaker, DecisionType, DecisionCriteria, DecisionOption, DecisionResult, DecisionContext

# Reasoning Strategies 모듈
from .reasoning_strategies.deductive_reasoning import DeductiveReasoning, DeductiveRuleType, DeductivePremise, DeductiveConclusion, DeductiveRule, DeductiveAnalysis
from .reasoning_strategies.inductive_reasoning import InductiveReasoning, InductiveType, InductiveObservation, InductivePattern, InductiveGeneralization, InductiveAnalysis
from .reasoning_strategies.abductive_reasoning import AbductiveReasoning, AbductiveType, AbductiveObservation, AbductiveHypothesis, AbductiveExplanation, AbductiveAnalysis

# Reasoning Optimization 모듈
from .reasoning_optimization.reasoning_optimizer import ReasoningOptimizer, OptimizationType, OptimizationTarget, OptimizationStrategy, OptimizationResult, OptimizationAnalysis

# 기존 모듈들 (하위 호환성 유지)
# Adaptive 모듈
from .adaptive.dynamic_reasoning_engine import DynamicReasoningEngine
from .adaptive.learning_integration import LearningIntegrationInterface
from .adaptive.feedback_loop import FeedbackLoopSystem
from .adaptive.evolutionary_improvement import EvolutionaryImprovementMechanism

# Consistency 모듈
from .consistency.logical_connectivity import LogicalConnectivityValidator, LogicalConnection, LogicalConnectionType
from .consistency.knowledge_conflict import KnowledgeConflictResolver, KnowledgeConflict, ConflictResolutionStrategy
from .consistency.integration_evaluator import IntegrationEvaluator, IntegrationAssessment

# Integration 모듈
from .integration.conflict_detection import ConflictDetectionSystem, IntegrationConflict, ConflictType
from .integration.resolution_algorithm import ResolutionAlgorithm, ResolutionMethod
from .integration.priority_system import IntegrationPrioritySystem, IntegrationPriorityItem, IntegrationPriority
from .integration.success_monitoring import SuccessMonitoringSystem, IntegrationSuccess, IntegrationMonitor

# Efficiency 모듈
from .efficiency.dynamic_resource_allocator import DynamicResourceAllocator, ResourceAllocation, ResourceType
from .efficiency.learning_strategy_optimizer import LearningStrategyOptimizer, LearningOptimization, LearningStrategy
from .efficiency.performance_monitor import PerformanceMonitor, PerformanceMetrics
from .efficiency.optimization_strategy import OptimizationStrategy as EfficiencyOptimizationStrategy, OptimizationResult as EfficiencyOptimizationResult

# Data structures
from .data_structures import *

__all__ = [
    # Reasoning Engine
    'InferenceEngine',
    'InferenceType',
    'InferenceContext',
    'InferenceResult',
    'LogicProcessor',
    'LogicType',
    'LogicalRule',
    'LogicalChain',
    'LogicAnalysis',
    'DecisionMaker',
    'DecisionType',
    'DecisionCriteria',
    'DecisionOption',
    'DecisionResult',
    'DecisionContext',
    
    # Reasoning Strategies
    'DeductiveReasoning',
    'DeductiveRuleType',
    'DeductivePremise',
    'DeductiveConclusion',
    'DeductiveRule',
    'DeductiveAnalysis',
    'InductiveReasoning',
    'InductiveType',
    'InductiveObservation',
    'InductivePattern',
    'InductiveGeneralization',
    'InductiveAnalysis',
    'AbductiveReasoning',
    'AbductiveType',
    'AbductiveObservation',
    'AbductiveHypothesis',
    'AbductiveExplanation',
    'AbductiveAnalysis',
    
    # Reasoning Optimization
    'ReasoningOptimizer',
    'OptimizationType',
    'OptimizationTarget',
    'OptimizationStrategy',
    'OptimizationResult',
    'OptimizationAnalysis',
    
    # 기존 모듈들 (하위 호환성)
    # Adaptive
    'DynamicReasoningEngine',
    'LearningIntegrationInterface',
    'FeedbackLoopSystem',
    'EvolutionaryImprovementMechanism',
    
    # Consistency
    'LogicalConnectivityValidator',
    'LogicalConnection',
    'LogicalConnectionType',
    'KnowledgeConflictResolver',
    'KnowledgeConflict',
    'ConflictResolutionStrategy',
    'IntegrationEvaluator',
    'IntegrationAssessment',
    
    # Integration
    'ConflictDetectionSystem',
    'IntegrationConflict',
    'ConflictType',
    'ResolutionAlgorithm',
    'ResolutionMethod',
    'IntegrationPrioritySystem',
    'IntegrationPriorityItem',
    'IntegrationPriority',
    'SuccessMonitoringSystem',
    'IntegrationSuccess',
    'IntegrationMonitor',
    
    # Efficiency
    'DynamicResourceAllocator',
    'ResourceAllocation',
    'ResourceType',
    'LearningStrategyOptimizer',
    'LearningOptimization',
    'LearningStrategy',
    'PerformanceMonitor',
    'PerformanceMetrics',
    'EfficiencyOptimizationStrategy',
    'EfficiencyOptimizationResult'
]
