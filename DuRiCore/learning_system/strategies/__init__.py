#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 Strategies 모듈

학습 전략들을 제공하는 모듈입니다.
"""

from .adaptive_learning import (AdaptationResult, AdaptationType,
                                AdaptiveLearningStrategy, LearningData,
                                LearningModel, LearningResult, LearningStatus,
                                LearningType)
from .cognitive_meta_learning import (CognitiveMetaLearningMetrics,
                                      CognitiveMetaLearningState,
                                      CognitiveMetaLearningStrategy,
                                      LearningEfficiency, LearningPattern,
                                      LearningStrategy, MetaLearningProcess,
                                      MetaLearningStage, MetaLearningType)
from .meta_cognition import (MetaCognitionInsight, MetaCognitionLevel,
                             MetaCognitionResult, MetaCognitionStrategy,
                             ReflectionType, SelfReflection, ThinkingProcess,
                             ThinkingQuality, ThinkingQualityAssessment)
from .self_directed_learning import (CuriosityTrigger, LearningActivity,
                                     LearningGoal, LearningOutcome,
                                     SelfDirectedLearningResult,
                                     SelfDirectedLearningStrategy,
                                     SelfDiscoveredProblem)

__all__ = [
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
    "LearningResult",
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
]
