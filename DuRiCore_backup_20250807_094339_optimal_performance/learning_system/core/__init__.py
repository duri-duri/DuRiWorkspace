#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 Core 모듈

학습 시스템의 핵심 기능들을 제공하는 모듈입니다.
"""

from .learning_engine import LearningEngine, LearningSession, LearningProcess, LearningResult, LearningSessionStatus, LearningProcessType
from .knowledge_evolution import KnowledgeEvolutionSystem, KnowledgeItem, KnowledgeEvolution, EvolutionSession, EvolutionType, KnowledgeQuality
from .learning_optimization import LearningOptimizationSystem, OptimizationStrategy, OptimizationResult, OptimizationTarget, OptimizationType, OptimizationStatus, PerformanceMetrics

__all__ = [
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
    "PerformanceMetrics"
]
