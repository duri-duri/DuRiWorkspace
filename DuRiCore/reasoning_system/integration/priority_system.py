#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 우선순위 시스템 모듈

지식 통합의 우선순위를 결정하는 모듈입니다.
"""

import asyncio
import hashlib
import json
import logging
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationPriority(Enum):
    """통합 우선순위"""

    LOW = "low"  # 낮음
    MEDIUM = "medium"  # 중간
    HIGH = "high"  # 높음
    CRITICAL = "critical"  # 중요


@dataclass
class IntegrationPriorityItem:
    """통합 우선순위 항목"""

    priority_id: str
    element_id: str
    priority_level: IntegrationPriority
    priority_score: float
    priority_factors: List[str] = field(default_factory=list)
    assigned_time: datetime = field(default_factory=datetime.now)


class IntegrationPrioritySystem:
    """통합 우선순위 시스템"""

    def __init__(self):
        self.priority_history = []
        self.priority_weights = {}

    async def determine_integration_priorities(
        self, knowledge_elements: List[Dict[str, Any]]
    ) -> List[IntegrationPriorityItem]:
        """통합 우선순위 결정"""
        priority_items = []

        for element in knowledge_elements:
            priority_item = await self._calculate_element_priority(element)
            priority_items.append(priority_item)

        # 우선순위 점수에 따라 정렬
        priority_items.sort(key=lambda x: x.priority_score, reverse=True)

        return priority_items

    async def _calculate_element_priority(
        self, element: Dict[str, Any]
    ) -> IntegrationPriorityItem:
        """요소 우선순위 계산"""
        priority_id = f"priority_{int(time.time())}_{hash(str(element))}"
        element_id = str(element.get("id", "unknown"))

        # 우선순위 점수 계산
        priority_score = await self._calculate_priority_score(element)

        # 우선순위 수준 결정
        priority_level = await self._determine_priority_level(priority_score)

        # 우선순위 요인 분석
        priority_factors = await self._analyze_priority_factors(element)

        priority_item = IntegrationPriorityItem(
            priority_id=priority_id,
            element_id=element_id,
            priority_level=priority_level,
            priority_score=priority_score,
            priority_factors=priority_factors,
        )

        return priority_item

    async def _calculate_priority_score(self, element: Dict[str, Any]) -> float:
        """우선순위 점수 계산"""
        score = 0.0

        # 요소의 완성도
        completeness = len(element) / 10.0  # 최대 10개 키 가정
        score += completeness * 0.3

        # 요소의 중요도
        importance = element.get("importance", 0.5)
        score += importance * 0.4

        # 요소의 신뢰도
        confidence = element.get("confidence", 0.5)
        score += confidence * 0.3

        return min(1.0, score)

    async def _determine_priority_level(
        self, priority_score: float
    ) -> IntegrationPriority:
        """우선순위 수준 결정"""
        if priority_score >= 0.8:
            return IntegrationPriority.CRITICAL
        elif priority_score >= 0.6:
            return IntegrationPriority.HIGH
        elif priority_score >= 0.4:
            return IntegrationPriority.MEDIUM
        else:
            return IntegrationPriority.LOW

    async def _analyze_priority_factors(self, element: Dict[str, Any]) -> List[str]:
        """우선순위 요인 분석"""
        factors = []

        # 완성도 요인
        if len(element) >= 8:
            factors.append("높은 완성도")
        elif len(element) >= 5:
            factors.append("중간 완성도")
        else:
            factors.append("낮은 완성도")

        # 중요도 요인
        importance = element.get("importance", 0.5)
        if importance >= 0.8:
            factors.append("매우 중요")
        elif importance >= 0.6:
            factors.append("중요")
        else:
            factors.append("일반")

        # 신뢰도 요인
        confidence = element.get("confidence", 0.5)
        if confidence >= 0.8:
            factors.append("높은 신뢰도")
        elif confidence >= 0.6:
            factors.append("중간 신뢰도")
        else:
            factors.append("낮은 신뢰도")

        return factors
