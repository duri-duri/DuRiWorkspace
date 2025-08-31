#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 공통 데이터 구조

추론 시스템에서 사용하는 공통 데이터 구조들을 정의합니다.
"""

import json
import time
import logging
import re
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict, Counter
import hashlib
from enum import Enum

logger = logging.getLogger(__name__)

class ReasoningType(Enum):
    """추론 유형"""
    DEDUCTIVE = "deductive"  # 연역적 추론
    INDUCTIVE = "inductive"  # 귀납적 추론
    ABDUCTIVE = "abductive"  # 가설적 추론
    ANALOGICAL = "analogical"  # 유추적 추론
    CREATIVE = "creative"  # 창의적 추론
    INTUITIVE = "intuitive"  # 직관적 추론
    EMOTIONAL = "emotional"  # 감정적 추론
    INTEGRATED = "integrated"  # 통합적 추론

class ReasoningAdaptationLevel(Enum):
    """추론 적응 수준"""
    BASIC = "basic"  # 기본 적응
    INTERMEDIATE = "intermediate"  # 중급 적응
    ADVANCED = "advanced"  # 고급 적응
    EXPERT = "expert"  # 전문가 적응
    MASTER = "master"  # 마스터 적응

class ReasoningContext(Enum):
    """추론 컨텍스트"""
    PROBLEM_SOLVING = "problem_solving"  # 문제 해결
    DECISION_MAKING = "decision_making"  # 의사결정
    LEARNING = "learning"  # 학습
    CREATION = "creation"  # 창작
    ANALYSIS = "analysis"  # 분석
    SYNTHESIS = "synthesis"  # 종합
    EVALUATION = "evaluation"  # 평가
    PREDICTION = "prediction"  # 예측

@dataclass
class ReasoningSession:
    """추론 세션"""
    session_id: str
    reasoning_type: ReasoningType
    context: ReasoningContext
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Dict[str, Any] = field(default_factory=dict)
    reasoning_steps: List[Dict[str, Any]] = field(default_factory=list)
    intermediate_results: List[Dict[str, Any]] = field(default_factory=list)
    final_result: Optional[Dict[str, Any]] = None
    confidence_score: float = 0.0
    adaptation_score: float = 0.0
    efficiency_score: float = 0.0
    learning_feedback: List[str] = field(default_factory=list)

@dataclass
class ReasoningAdaptation:
    """추론 적응"""
    adaptation_id: str
    session_id: str
    original_approach: ReasoningType
    adapted_approach: ReasoningType
    adaptation_reason: str
    adaptation_effectiveness: float
    learning_gained: List[str]
    improvement_suggestions: List[str]

@dataclass
class ReasoningFeedback:
    """추론 피드백"""
    feedback_id: str
    session_id: str
    feedback_type: str
    feedback_content: str
    feedback_score: float
    learning_impact: float
    adaptation_suggestions: List[str]

@dataclass
class ReasoningEvolution:
    """추론 진화"""
    evolution_id: str
    evolution_type: str
    original_capabilities: Dict[str, Any]
    evolved_capabilities: Dict[str, Any]
    evolution_factors: List[str]
    improvement_score: float
    adaptation_enhancement: float
