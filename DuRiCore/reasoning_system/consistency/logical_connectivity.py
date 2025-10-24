#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 논리적 연결성 검증 모듈

추론 과정의 논리적 일관성을 검증하는 모듈입니다.
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LogicalConnectionType(Enum):
    """논리적 연결 유형"""

    CAUSAL = "causal"  # 인과적 연결
    TEMPORAL = "temporal"  # 시간적 연결
    SPATIAL = "spatial"  # 공간적 연결
    CONCEPTUAL = "conceptual"  # 개념적 연결
    FUNCTIONAL = "functional"  # 기능적 연결
    HIERARCHICAL = "hierarchical"  # 계층적 연결


@dataclass
class LogicalConnection:
    """논리적 연결"""

    connection_id: str
    source_element: str
    target_element: str
    connection_type: LogicalConnectionType
    strength: float
    confidence: float
    evidence: List[str] = field(default_factory=list)


class LogicalConnectivityValidator:
    """논리적 연결성 검증"""

    def __init__(self):
        self.connection_patterns = {}
        self.validation_history = []

    async def validate_logical_connections(self, reasoning_steps: List[Dict[str, Any]]) -> List[LogicalConnection]:
        """논리적 연결 검증"""
        connections = []

        if len(reasoning_steps) < 2:
            return connections

        for i in range(1, len(reasoning_steps)):
            prev_step = reasoning_steps[i - 1]
            current_step = reasoning_steps[i]

            connection = await self._validate_step_connection(prev_step, current_step)
            if connection:
                connections.append(connection)

        return connections

    async def _validate_step_connection(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> Optional[LogicalConnection]:
        """단계 간 연결 검증"""
        connection_id = f"connection_{int(time.time())}_{hash(str(prev_step))}_{hash(str(current_step))}"

        # 연결 유형 분석
        connection_type = await self._analyze_connection_type(prev_step, current_step)

        # 연결 강도 계산
        strength = await self._calculate_connection_strength(prev_step, current_step)

        # 연결 신뢰도 계산
        confidence = await self._calculate_connection_confidence(prev_step, current_step)

        # 연결 증거 수집
        evidence = await self._collect_connection_evidence(prev_step, current_step)

        if strength > 0.1:  # 최소 강도 임계값
            connection = LogicalConnection(
                connection_id=connection_id,
                source_element=str(prev_step.get("id", "unknown")),
                target_element=str(current_step.get("id", "unknown")),
                connection_type=connection_type,
                strength=strength,
                confidence=confidence,
                evidence=evidence,
            )
            return connection

        return None

    async def _analyze_connection_type(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> LogicalConnectionType:
        """연결 유형 분석"""
        # 기본적으로 개념적 연결로 설정
        return LogicalConnectionType.CONCEPTUAL

    async def _calculate_connection_strength(self, prev_step: Dict[str, Any], current_step: Dict[str, Any]) -> float:
        """연결 강도 계산"""
        # 유사도 기반 강도 계산
        similarity = await self._calculate_similarity(prev_step, current_step)
        return similarity

    async def _calculate_similarity(self, step1: Dict[str, Any], step2: Dict[str, Any]) -> float:
        """단계 간 유사도 계산"""
        # 간단한 유사도 계산 (실제로는 더 복잡한 알고리즘 사용)
        common_keys = set(step1.keys()) & set(step2.keys())
        if not common_keys:
            return 0.0

        similarities = []
        for key in common_keys:
            if isinstance(step1[key], (str, int, float)) and isinstance(step2[key], (str, int, float)):
                if step1[key] == step2[key]:
                    similarities.append(1.0)
                else:
                    similarities.append(0.0)

        return np.mean(similarities) if similarities else 0.0

    async def _calculate_connection_confidence(self, prev_step: Dict[str, Any], current_step: Dict[str, Any]) -> float:
        """연결 신뢰도 계산"""
        # 기본 신뢰도 계산
        base_confidence = 0.5

        # 단계의 완성도에 따른 조정
        prev_completeness = len(prev_step) / 10.0  # 최대 10개 키 가정
        current_completeness = len(current_step) / 10.0

        completeness_factor = (prev_completeness + current_completeness) / 2.0

        return min(1.0, base_confidence * completeness_factor)

    async def _collect_connection_evidence(self, prev_step: Dict[str, Any], current_step: Dict[str, Any]) -> List[str]:
        """연결 증거 수집"""
        evidence = []

        # 공통 키가 있는지 확인
        common_keys = set(prev_step.keys()) & set(current_step.keys())
        if common_keys:
            evidence.append(f"공통 키 발견: {', '.join(common_keys)}")

        # 시간적 순서 확인
        if "timestamp" in prev_step and "timestamp" in current_step:
            if prev_step["timestamp"] < current_step["timestamp"]:
                evidence.append("시간적 순서 일치")

        return evidence
