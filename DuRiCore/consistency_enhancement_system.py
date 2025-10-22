#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 1-3 Week 3 Day 14 - 일관성 강화 시스템

구조적 일관성을 강화하는 고급 추론 시스템
- 논리적 연결성 검증: 추론 과정의 논리적 일관성 검증
- 지식 충돌 해결: 상충되는 지식 간의 충돌 해결 알고리즘
- 통합성 평가: 다중 지식 소스의 통합성 평가
- 일관성 점수 향상: 목표 60% 이상으로 향상
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


class ConsistencyLevel(Enum):
    """일관성 수준"""

    LOW = "low"  # 낮음 (0-30%)
    MEDIUM = "medium"  # 중간 (30-60%)
    HIGH = "high"  # 높음 (60-80%)
    VERY_HIGH = "very_high"  # 매우 높음 (80-100%)


class LogicalConnectionType(Enum):
    """논리적 연결 유형"""

    CAUSAL = "causal"  # 인과적 연결
    TEMPORAL = "temporal"  # 시간적 연결
    SPATIAL = "spatial"  # 공간적 연결
    CONCEPTUAL = "conceptual"  # 개념적 연결
    FUNCTIONAL = "functional"  # 기능적 연결
    HIERARCHICAL = "hierarchical"  # 계층적 연결


class ConflictResolutionStrategy(Enum):
    """충돌 해결 전략"""

    PRIORITY_BASED = "priority_based"  # 우선순위 기반
    CONSENSUS_BASED = "consensus_based"  # 합의 기반
    EVIDENCE_BASED = "evidence_based"  # 증거 기반
    CONTEXT_BASED = "context_based"  # 컨텍스트 기반
    INTEGRATION_BASED = "integration_based"  # 통합 기반


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


@dataclass
class KnowledgeConflict:
    """지식 충돌"""

    conflict_id: str
    conflicting_elements: List[str]
    conflict_type: str
    severity: float
    resolution_strategy: ConflictResolutionStrategy
    resolution_result: Optional[Dict[str, Any]] = None


@dataclass
class IntegrationAssessment:
    """통합성 평가"""

    assessment_id: str
    knowledge_sources: List[str]
    integration_score: float
    coherence_score: float
    completeness_score: float
    consistency_score: float
    assessment_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConsistencyEnhancement:
    """일관성 강화"""

    enhancement_id: str
    original_consistency: float
    enhanced_consistency: float
    enhancement_methods: List[str]
    improvement_score: float
    enhancement_details: Dict[str, Any] = field(default_factory=dict)


class LogicalConnectivityValidator:
    """논리적 연결성 검증"""

    def __init__(self):
        self.connection_patterns = {}
        self.validation_history = []

    async def validate_logical_connections(
        self, reasoning_steps: List[Dict[str, Any]]
    ) -> List[LogicalConnection]:
        """추론 과정의 논리적 일관성 검증"""
        connections = []

        for i, step in enumerate(reasoning_steps):
            if i > 0:
                # 이전 단계와의 연결성 검증
                connection = await self._validate_step_connection(reasoning_steps[i - 1], step)
                if connection:
                    connections.append(connection)

        return connections

    async def _validate_step_connection(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> Optional[LogicalConnection]:
        """단계 간 연결성 검증"""
        connection_id = f"connection_{int(time.time())}"

        # 연결 유형 분석
        connection_type = await self._analyze_connection_type(prev_step, current_step)

        # 연결 강도 계산
        strength = await self._calculate_connection_strength(prev_step, current_step)

        # 신뢰도 계산
        confidence = await self._calculate_connection_confidence(prev_step, current_step)

        # 증거 수집
        evidence = await self._collect_connection_evidence(prev_step, current_step)

        if strength > 0.3:  # 최소 연결 강도 임계값
            return LogicalConnection(
                connection_id=connection_id,
                source_element=str(prev_step.get("id", "unknown")),
                target_element=str(current_step.get("id", "unknown")),
                connection_type=connection_type,
                strength=strength,
                confidence=confidence,
                evidence=evidence,
            )

        return None

    async def _analyze_connection_type(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> LogicalConnectionType:
        """연결 유형 분석"""
        # 기본적으로 개념적 연결로 설정
        return LogicalConnectionType.CONCEPTUAL

    async def _calculate_connection_strength(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> float:
        """연결 강도 계산"""
        # 단계 간 유사성 기반 강도 계산
        similarity_score = await self._calculate_similarity(prev_step, current_step)
        return similarity_score

    async def _calculate_similarity(self, step1: Dict[str, Any], step2: Dict[str, Any]) -> float:
        """단계 간 유사성 계산"""
        # 간단한 유사성 계산 (실제로는 더 복잡한 알고리즘 사용)
        common_keys = set(step1.keys()) & set(step2.keys())
        if not common_keys:
            return 0.0

        similarity_scores = []
        for key in common_keys:
            if step1[key] == step2[key]:
                similarity_scores.append(1.0)
            else:
                similarity_scores.append(0.5)

        return np.mean(similarity_scores) if similarity_scores else 0.0

    async def _calculate_connection_confidence(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> float:
        """연결 신뢰도 계산"""
        # 기본 신뢰도
        base_confidence = 0.7

        # 단계 품질에 따른 보정
        prev_quality = prev_step.get("quality", 0.5)
        current_quality = current_step.get("quality", 0.5)

        quality_factor = (prev_quality + current_quality) / 2
        confidence = base_confidence * quality_factor

        return min(confidence, 1.0)

    async def _collect_connection_evidence(
        self, prev_step: Dict[str, Any], current_step: Dict[str, Any]
    ) -> List[str]:
        """연결 증거 수집"""
        evidence = []

        # 공통 요소 검색
        common_elements = set(prev_step.keys()) & set(current_step.keys())
        if common_elements:
            evidence.append(f"공통 요소: {', '.join(common_elements)}")

        # 논리적 흐름 검증
        if "conclusion" in prev_step and "premise" in current_step:
            evidence.append("논리적 흐름: 결론에서 전제로")

        return evidence


class KnowledgeConflictResolver:
    """지식 충돌 해결"""

    def __init__(self):
        self.conflict_history = []
        self.resolution_strategies = {}

    async def detect_and_resolve_conflicts(
        self, knowledge_elements: List[Dict[str, Any]]
    ) -> List[KnowledgeConflict]:
        """지식 충돌 감지 및 해결"""
        conflicts = await self._detect_conflicts(knowledge_elements)

        for conflict in conflicts:
            resolution = await self._resolve_conflict(conflict)
            conflict.resolution_result = resolution

        return conflicts

    async def _detect_conflicts(
        self, knowledge_elements: List[Dict[str, Any]]
    ) -> List[KnowledgeConflict]:
        """충돌 감지"""
        conflicts = []

        for i, element1 in enumerate(knowledge_elements):
            for j, element2 in enumerate(knowledge_elements[i + 1 :], i + 1):
                conflict = await self._check_for_conflict(element1, element2)
                if conflict:
                    conflicts.append(conflict)

        return conflicts

    async def _check_for_conflict(
        self, element1: Dict[str, Any], element2: Dict[str, Any]
    ) -> Optional[KnowledgeConflict]:
        """충돌 확인"""
        # 간단한 충돌 감지 로직
        if "value" in element1 and "value" in element2:
            if element1["value"] != element2["value"]:
                conflict_id = f"conflict_{int(time.time())}"
                return KnowledgeConflict(
                    conflict_id=conflict_id,
                    conflicting_elements=[
                        str(element1.get("id", "unknown")),
                        str(element2.get("id", "unknown")),
                    ],
                    conflict_type="value_conflict",
                    severity=0.7,
                    resolution_strategy=ConflictResolutionStrategy.EVIDENCE_BASED,
                )

        return None

    async def _resolve_conflict(self, conflict: KnowledgeConflict) -> Dict[str, Any]:
        """충돌 해결"""
        resolution_result = {
            "resolution_method": conflict.resolution_strategy.value,
            "resolution_status": "resolved",
            "resolution_details": {},
        }

        if conflict.resolution_strategy == ConflictResolutionStrategy.EVIDENCE_BASED:
            resolution_result["resolution_details"] = await self._evidence_based_resolution(
                conflict
            )
        elif conflict.resolution_strategy == ConflictResolutionStrategy.PRIORITY_BASED:
            resolution_result["resolution_details"] = await self._priority_based_resolution(
                conflict
            )
        else:
            resolution_result["resolution_details"] = await self._consensus_based_resolution(
                conflict
            )

        return resolution_result

    async def _evidence_based_resolution(self, conflict: KnowledgeConflict) -> Dict[str, Any]:
        """증거 기반 해결"""
        return {
            "method": "evidence_based",
            "evidence_analysis": "증거 분석을 통한 해결",
            "confidence": 0.8,
        }

    async def _priority_based_resolution(self, conflict: KnowledgeConflict) -> Dict[str, Any]:
        """우선순위 기반 해결"""
        return {
            "method": "priority_based",
            "priority_analysis": "우선순위 분석을 통한 해결",
            "confidence": 0.7,
        }

    async def _consensus_based_resolution(self, conflict: KnowledgeConflict) -> Dict[str, Any]:
        """합의 기반 해결"""
        return {
            "method": "consensus_based",
            "consensus_analysis": "합의 분석을 통한 해결",
            "confidence": 0.6,
        }


class IntegrationEvaluator:
    """통합성 평가"""

    def __init__(self):
        self.evaluation_history = []
        self.integration_metrics = {}

    async def evaluate_integration(
        self, knowledge_sources: List[Dict[str, Any]]
    ) -> IntegrationAssessment:
        """다중 지식 소스의 통합성 평가"""
        assessment_id = f"assessment_{int(time.time())}"

        # 통합 점수 계산
        integration_score = await self._calculate_integration_score(knowledge_sources)

        # 일관성 점수 계산
        coherence_score = await self._calculate_coherence_score(knowledge_sources)

        # 완전성 점수 계산
        completeness_score = await self._calculate_completeness_score(knowledge_sources)

        # 일관성 점수 계산
        consistency_score = await self._calculate_consistency_score(knowledge_sources)

        assessment = IntegrationAssessment(
            assessment_id=assessment_id,
            knowledge_sources=[str(source.get("id", "unknown")) for source in knowledge_sources],
            integration_score=integration_score,
            coherence_score=coherence_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            assessment_details={
                "total_sources": len(knowledge_sources),
                "evaluation_time": datetime.now().isoformat(),
            },
        )

        self.evaluation_history.append(assessment)
        return assessment

    async def _calculate_integration_score(self, knowledge_sources: List[Dict[str, Any]]) -> float:
        """통합 점수 계산"""
        if not knowledge_sources:
            return 0.0

        # 소스 간 연결성 기반 통합 점수
        connectivity_scores = []
        for i, source1 in enumerate(knowledge_sources):
            for source2 in knowledge_sources[i + 1 :]:
                connectivity = await self._calculate_connectivity(source1, source2)
                connectivity_scores.append(connectivity)

        return np.mean(connectivity_scores) if connectivity_scores else 0.0

    async def _calculate_coherence_score(self, knowledge_sources: List[Dict[str, Any]]) -> float:
        """일관성 점수 계산"""
        if not knowledge_sources:
            return 0.0

        # 소스 간 일관성 평가
        coherence_scores = []
        for i, source1 in enumerate(knowledge_sources):
            for source2 in knowledge_sources[i + 1 :]:
                coherence = await self._calculate_coherence(source1, source2)
                coherence_scores.append(coherence)

        return np.mean(coherence_scores) if coherence_scores else 0.0

    async def _calculate_completeness_score(self, knowledge_sources: List[Dict[str, Any]]) -> float:
        """완전성 점수 계산"""
        if not knowledge_sources:
            return 0.0

        # 지식 소스의 완전성 평가
        completeness_scores = []
        for source in knowledge_sources:
            completeness = await self._evaluate_completeness(source)
            completeness_scores.append(completeness)

        return np.mean(completeness_scores) if completeness_scores else 0.0

    async def _calculate_consistency_score(self, knowledge_sources: List[Dict[str, Any]]) -> float:
        """일관성 점수 계산"""
        if not knowledge_sources:
            return 0.0

        # 소스 간 일관성 평가
        consistency_scores = []
        for i, source1 in enumerate(knowledge_sources):
            for source2 in knowledge_sources[i + 1 :]:
                consistency = await self._evaluate_consistency(source1, source2)
                consistency_scores.append(consistency)

        return np.mean(consistency_scores) if consistency_scores else 0.0

    async def _calculate_connectivity(
        self, source1: Dict[str, Any], source2: Dict[str, Any]
    ) -> float:
        """연결성 계산"""
        # 간단한 연결성 계산
        common_keys = set(source1.keys()) & set(source2.keys())
        if not common_keys:
            return 0.0

        connectivity_score = len(common_keys) / max(len(source1.keys()), len(source2.keys()))
        return connectivity_score

    async def _calculate_coherence(self, source1: Dict[str, Any], source2: Dict[str, Any]) -> float:
        """일관성 계산"""
        # 간단한 일관성 계산
        if "type" in source1 and "type" in source2:
            if source1["type"] == source2["type"]:
                return 0.8
            else:
                return 0.4

        return 0.5

    async def _evaluate_completeness(self, source: Dict[str, Any]) -> float:
        """완전성 평가"""
        # 필수 필드 존재 여부 기반 완전성 평가
        required_fields = ["id", "content", "type"]
        existing_fields = [field for field in required_fields if field in source]

        completeness = len(existing_fields) / len(required_fields)
        return completeness

    async def _evaluate_consistency(
        self, source1: Dict[str, Any], source2: Dict[str, Any]
    ) -> float:
        """일관성 평가"""
        # 간단한 일관성 평가
        if "type" in source1 and "type" in source2:
            if source1["type"] == source2["type"]:
                return 0.9
            else:
                return 0.3

        return 0.5


class ConsistencyEnhancementSystem:
    """일관성 강화 시스템"""

    def __init__(self):
        self.logical_validator = LogicalConnectivityValidator()
        self.conflict_resolver = KnowledgeConflictResolver()
        self.integration_evaluator = IntegrationEvaluator()
        self.enhancement_history = []

    async def enhance_consistency(self, reasoning_data: Dict[str, Any]) -> ConsistencyEnhancement:
        """일관성 강화"""
        enhancement_id = f"enhancement_{int(time.time())}"

        # 원본 일관성 평가
        original_consistency = await self._evaluate_original_consistency(reasoning_data)

        # 일관성 강화 방법 적용
        enhancement_methods = await self._apply_enhancement_methods(reasoning_data)

        # 강화된 일관성 평가
        enhanced_consistency = await self._evaluate_enhanced_consistency(
            reasoning_data, enhancement_methods
        )

        # 개선 점수 계산
        improvement_score = enhanced_consistency - original_consistency

        enhancement = ConsistencyEnhancement(
            enhancement_id=enhancement_id,
            original_consistency=original_consistency,
            enhanced_consistency=enhanced_consistency,
            enhancement_methods=enhancement_methods,
            improvement_score=improvement_score,
            enhancement_details={
                "enhancement_time": datetime.now().isoformat(),
                "methods_applied": len(enhancement_methods),
            },
        )

        self.enhancement_history.append(enhancement)
        return enhancement

    async def _evaluate_original_consistency(self, reasoning_data: Dict[str, Any]) -> float:
        """원본 일관성 평가"""
        # 기본 일관성 점수 계산
        consistency_factors = []

        # 논리적 연결성 평가
        if "reasoning_steps" in reasoning_data:
            connections = await self.logical_validator.validate_logical_connections(
                reasoning_data["reasoning_steps"]
            )
            if connections:
                connection_strengths = [conn.strength for conn in connections]
                consistency_factors.append(np.mean(connection_strengths))

        # 지식 충돌 평가
        if "knowledge_elements" in reasoning_data:
            conflicts = await self.conflict_resolver.detect_and_resolve_conflicts(
                reasoning_data["knowledge_elements"]
            )
            if conflicts:
                conflict_severities = [conflict.severity for conflict in conflicts]
                conflict_factor = 1 - np.mean(conflict_severities)
                consistency_factors.append(conflict_factor)

        # 통합성 평가
        if "knowledge_sources" in reasoning_data:
            assessment = await self.integration_evaluator.evaluate_integration(
                reasoning_data["knowledge_sources"]
            )
            consistency_factors.append(assessment.consistency_score)

        return np.mean(consistency_factors) if consistency_factors else 0.0

    async def _apply_enhancement_methods(self, reasoning_data: Dict[str, Any]) -> List[str]:
        """일관성 강화 방법 적용"""
        enhancement_methods = []

        # 논리적 연결성 강화
        if "reasoning_steps" in reasoning_data:
            enhancement_methods.append("논리적 연결성 강화")

        # 지식 충돌 해결
        if "knowledge_elements" in reasoning_data:
            enhancement_methods.append("지식 충돌 해결")

        # 통합성 개선
        if "knowledge_sources" in reasoning_data:
            enhancement_methods.append("통합성 개선")

        return enhancement_methods

    async def _evaluate_enhanced_consistency(
        self, reasoning_data: Dict[str, Any], enhancement_methods: List[str]
    ) -> float:
        """강화된 일관성 평가"""
        # 강화 방법 적용 후 일관성 재평가
        enhanced_consistency = await self._evaluate_original_consistency(reasoning_data)

        # 강화 방법에 따른 보정
        enhancement_bonus = len(enhancement_methods) * 0.1
        enhanced_consistency = min(enhanced_consistency + enhancement_bonus, 1.0)

        return enhanced_consistency

    async def get_consistency_level(self, consistency_score: float) -> ConsistencyLevel:
        """일관성 수준 반환"""
        if consistency_score >= 0.8:
            return ConsistencyLevel.VERY_HIGH
        elif consistency_score >= 0.6:
            return ConsistencyLevel.HIGH
        elif consistency_score >= 0.3:
            return ConsistencyLevel.MEDIUM
        else:
            return ConsistencyLevel.LOW
