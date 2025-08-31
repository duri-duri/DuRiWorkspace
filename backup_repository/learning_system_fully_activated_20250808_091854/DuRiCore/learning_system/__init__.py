#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 패키지

학습 시스템의 모든 모듈을 통합하는 패키지입니다.
"""

# Core 모듈
from .core.learning_engine import LearningEngine, LearningSession, LearningProcess, LearningResult, LearningSessionStatus, LearningProcessType
from .core.knowledge_evolution import KnowledgeEvolutionSystem, KnowledgeItem, KnowledgeEvolution, EvolutionSession, EvolutionType, KnowledgeQuality
from .core.learning_optimization import LearningOptimizationSystem, OptimizationStrategy, OptimizationResult, OptimizationTarget, OptimizationType, OptimizationStatus, PerformanceMetrics

# Strategies 모듈
from .strategies.self_directed_learning import SelfDirectedLearningStrategy, LearningGoal, LearningActivity, LearningOutcome, SelfDirectedLearningResult, CuriosityTrigger, SelfDiscoveredProblem
from .strategies.adaptive_learning import AdaptiveLearningStrategy, LearningData, LearningModel, LearningResult as AdaptiveLearningResult, AdaptationResult, LearningType, AdaptationType, LearningStatus
from .strategies.meta_cognition import MetaCognitionStrategy, ThinkingProcess, SelfReflection, ThinkingQualityAssessment, MetaCognitionInsight, MetaCognitionResult, MetaCognitionLevel, ThinkingQuality, ReflectionType
from .strategies.cognitive_meta_learning import CognitiveMetaLearningStrategy, LearningPattern, LearningStrategy, MetaLearningProcess, CognitiveMetaLearningMetrics, CognitiveMetaLearningState, MetaLearningType, LearningEfficiency, MetaLearningStage

# Integration 모듈
from .integration.learning_integration import LearningIntegrationSystem, IntegrationSession, IntegratedLearningResult, LearningStrategyResult, IntegrationType, IntegrationStatus
from .integration.knowledge_integration import KnowledgeIntegrationSystem, IntegratedKnowledge, KnowledgeSource, IntegrationSession as KnowledgeIntegrationSession, IntegrationMethod, KnowledgeQuality as IntegrationKnowledgeQuality

# Monitoring 모듈
from .monitoring.learning_monitor import LearningMonitoringSystem, MonitoringSession, LearningEvent, LearningMetrics, LearningPattern, MonitoringStatus, LearningPhase
from .monitoring.learning_monitoring import LearningMonitoringSystem as AdvancedLearningMonitoringSystem, LearningIssue, LearningPrediction, OptimizationRecommendation, MonitoringLevel, LearningIssueType

# 패키지 버전
__version__ = "2.3.0"

# 주요 클래스들
__all__ = [
    # Core
    "LearningEngine",
    "LearningSession", 
    "LearningProcess",
    "LearningResult",
    "LearningSessionStatus",
    "LearningProcessType",
    "KnowledgeEvolutionSystem",
    "KnowledgeItem",
    "KnowledgeEvolution",
    "EvolutionSession",
    "EvolutionType",
    "KnowledgeQuality",
    "LearningOptimizationSystem",
    "OptimizationStrategy",
    "OptimizationResult",
    "OptimizationTarget",
    "OptimizationType",
    "OptimizationStatus",
    "PerformanceMetrics",
    
    # Strategies
    "SelfDirectedLearningStrategy",
    "LearningGoal",
    "LearningActivity",
    "LearningOutcome",
    "SelfDirectedLearningResult",
    "CuriosityTrigger",
    "SelfDiscoveredProblem",
    "AdaptiveLearningStrategy",
    "LearningData",
    "LearningModel",
    "AdaptiveLearningResult",
    "AdaptationResult",
    "LearningType",
    "AdaptationType",
    "LearningStatus",
    "MetaCognitionStrategy",
    "ThinkingProcess",
    "SelfReflection",
    "ThinkingQualityAssessment",
    "MetaCognitionInsight",
    "MetaCognitionResult",
    "MetaCognitionLevel",
    "ThinkingQuality",
    "ReflectionType",
    "CognitiveMetaLearningStrategy",
    "LearningPattern",
    "LearningStrategy",
    "MetaLearningProcess",
    "CognitiveMetaLearningMetrics",
    "CognitiveMetaLearningState",
    "MetaLearningType",
    "LearningEfficiency",
    "MetaLearningStage",
    
    # Integration
    "LearningIntegrationSystem",
    "IntegrationSession",
    "IntegratedLearningResult",
    "LearningStrategyResult",
    "IntegrationType",
    "IntegrationStatus",
    "KnowledgeIntegrationSystem",
    "IntegratedKnowledge",
    "KnowledgeSource",
    "KnowledgeIntegrationSession",
    "IntegrationMethod",
    "IntegrationKnowledgeQuality",
    
    # Monitoring
    "LearningMonitoringSystem",
    "MonitoringSession",
    "LearningEvent",
    "LearningMetrics",
    "LearningPattern",
    "MonitoringStatus",
    "LearningPhase",
    "AdvancedLearningMonitoringSystem",
    "LearningIssue",
    "LearningPrediction",
    "OptimizationRecommendation",
    "MonitoringLevel",
    "LearningIssueType"
]
