#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 패키지

학습 시스템의 모든 모듈을 통합하는 패키지입니다.
"""

from .core.knowledge_evolution import (EvolutionSession, EvolutionType,
                                       KnowledgeEvolution,
                                       KnowledgeEvolutionSystem, KnowledgeItem,
                                       KnowledgeQuality)
# Core 모듈
from .core.learning_engine import (LearningEngine, LearningProcess,
                                   LearningProcessType, LearningResult,
                                   LearningSession, LearningSessionStatus)
from .core.learning_optimization import (LearningOptimizationSystem,
                                         OptimizationResult,
                                         OptimizationStatus,
                                         OptimizationStrategy,
                                         OptimizationTarget, OptimizationType,
                                         PerformanceMetrics)
from .integration.knowledge_integration import (IntegratedKnowledge,
                                                IntegrationMethod)
from .integration.knowledge_integration import \
    IntegrationSession as KnowledgeIntegrationSession
from .integration.knowledge_integration import KnowledgeIntegrationSystem
from .integration.knowledge_integration import \
    KnowledgeQuality as IntegrationKnowledgeQuality
from .integration.knowledge_integration import KnowledgeSource
# Integration 모듈
from .integration.learning_integration import (IntegratedLearningResult,
                                               IntegrationSession,
                                               IntegrationStatus,
                                               IntegrationType,
                                               LearningIntegrationSystem,
                                               LearningStrategyResult)
# Monitoring 모듈
from .monitoring.learning_monitor import (LearningEvent, LearningMetrics,
                                          LearningMonitoringSystem,
                                          LearningPattern, LearningPhase,
                                          MonitoringSession, MonitoringStatus)
from .monitoring.learning_monitoring import LearningIssue, LearningIssueType
from .monitoring.learning_monitoring import \
    LearningMonitoringSystem as AdvancedLearningMonitoringSystem
from .monitoring.learning_monitoring import (LearningPrediction,
                                             MonitoringLevel,
                                             OptimizationRecommendation)
from .strategies.adaptive_learning import (AdaptationResult, AdaptationType,
                                           AdaptiveLearningStrategy,
                                           LearningData, LearningModel)
from .strategies.adaptive_learning import \
    LearningResult as AdaptiveLearningResult
from .strategies.adaptive_learning import LearningStatus, LearningType
from .strategies.cognitive_meta_learning import (CognitiveMetaLearningMetrics,
                                                 CognitiveMetaLearningState,
                                                 CognitiveMetaLearningStrategy,
                                                 LearningEfficiency,
                                                 LearningPattern,
                                                 LearningStrategy,
                                                 MetaLearningProcess,
                                                 MetaLearningStage,
                                                 MetaLearningType)
from .strategies.meta_cognition import (MetaCognitionInsight,
                                        MetaCognitionLevel,
                                        MetaCognitionResult,
                                        MetaCognitionStrategy, ReflectionType,
                                        SelfReflection, ThinkingProcess,
                                        ThinkingQuality,
                                        ThinkingQualityAssessment)
# Strategies 모듈
from .strategies.self_directed_learning import (CuriosityTrigger,
                                                LearningActivity, LearningGoal,
                                                LearningOutcome,
                                                SelfDirectedLearningResult,
                                                SelfDirectedLearningStrategy,
                                                SelfDiscoveredProblem)

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
    "LearningIssueType",
]
