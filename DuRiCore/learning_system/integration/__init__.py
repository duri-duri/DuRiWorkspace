#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 Integration 모듈

학습 통합 기능들을 제공하는 모듈입니다.
"""

from .knowledge_integration import (
    IntegratedKnowledge,
    IntegrationMethod,
    KnowledgeIntegrationSystem,
    KnowledgeQuality,
    KnowledgeSource,
)
from .knowledge_integration import IntegrationSession as KnowledgeIntegrationSession
from .learning_integration import (
    IntegratedLearningResult,
    IntegrationSession,
    IntegrationStatus,
    IntegrationType,
    LearningIntegrationSystem,
    LearningStrategyResult,
)

__all__ = [
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
    "KnowledgeQuality",
]
