#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 학습 시스템 Integration 모듈

학습 통합 기능들을 제공하는 모듈입니다.
"""

from .learning_integration import LearningIntegrationSystem, IntegrationSession, IntegratedLearningResult, LearningStrategyResult, IntegrationType, IntegrationStatus
from .knowledge_integration import KnowledgeIntegrationSystem, IntegratedKnowledge, KnowledgeSource, IntegrationSession as KnowledgeIntegrationSession, IntegrationMethod, KnowledgeQuality

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
    "KnowledgeQuality"
]
