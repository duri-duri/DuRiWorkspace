#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 일관성 강화 모듈

구조적 일관성을 강화하는 고급 추론 시스템 모듈입니다.
"""

from .integration_evaluator import IntegrationAssessment, IntegrationEvaluator
from .knowledge_conflict import (ConflictResolutionStrategy, KnowledgeConflict,
                                 KnowledgeConflictResolver)
from .logical_connectivity import (LogicalConnection, LogicalConnectionType,
                                   LogicalConnectivityValidator)

__all__ = [
    "LogicalConnectivityValidator",
    "LogicalConnection",
    "LogicalConnectionType",
    "KnowledgeConflictResolver",
    "KnowledgeConflict",
    "ConflictResolutionStrategy",
    "IntegrationEvaluator",
    "IntegrationAssessment",
]
