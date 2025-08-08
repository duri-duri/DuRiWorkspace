#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 Strategies 모듈

학습 전략들을 제공하는 모듈입니다.
"""

from .self_directed_learning import SelfDirectedLearningStrategy, LearningGoal, LearningActivity, LearningOutcome, SelfDirectedLearningResult, CuriosityTrigger, SelfDiscoveredProblem
from .adaptive_learning import AdaptiveLearningStrategy, LearningData, LearningModel, LearningResult, AdaptationResult, LearningType, AdaptationType, LearningStatus
from .meta_cognition import MetaCognitionStrategy, ThinkingProcess, SelfReflection, ThinkingQualityAssessment, MetaCognitionInsight, MetaCognitionResult, MetaCognitionLevel, ThinkingQuality, ReflectionType
from .cognitive_meta_learning import CognitiveMetaLearningStrategy, LearningPattern, LearningStrategy, MetaLearningProcess, CognitiveMetaLearningMetrics, CognitiveMetaLearningState, MetaLearningType, LearningEfficiency, MetaLearningStage

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
    "MetaLearningStage"
]
