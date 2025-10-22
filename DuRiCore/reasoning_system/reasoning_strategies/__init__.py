#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 추론 전략 패키지

다양한 추론 전략들을 포함합니다.
"""

from .abductive_reasoning import (AbductiveAnalysis, AbductiveExplanation,
                                  AbductiveHypothesis, AbductiveObservation,
                                  AbductiveReasoning, AbductiveType)
from .deductive_reasoning import (DeductiveAnalysis, DeductiveConclusion,
                                  DeductivePremise, DeductiveReasoning,
                                  DeductiveRule, DeductiveRuleType)
from .inductive_reasoning import (InductiveAnalysis, InductiveGeneralization,
                                  InductiveObservation, InductivePattern,
                                  InductiveReasoning, InductiveType)

__all__ = [
    # Deductive Reasoning
    "DeductiveReasoning",
    "DeductiveRuleType",
    "DeductivePremise",
    "DeductiveConclusion",
    "DeductiveRule",
    "DeductiveAnalysis",
    # Inductive Reasoning
    "InductiveReasoning",
    "InductiveType",
    "InductiveObservation",
    "InductivePattern",
    "InductiveGeneralization",
    "InductiveAnalysis",
    # Abductive Reasoning
    "AbductiveReasoning",
    "AbductiveType",
    "AbductiveObservation",
    "AbductiveHypothesis",
    "AbductiveExplanation",
    "AbductiveAnalysis",
]
