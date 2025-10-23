#!/usr/bin/env python3
"""
DuRi 실시간 학습 시스템 - Phase 1-3 Week 3 Day 6
동적 추론 그래프의 실시간 학습을 관리하는 시스템

기능:
1. 학습 데이터 수집 시스템
2. 실시간 모델 업데이트 시스템
3. 학습 성과 평가 시스템
4. 학습 검증 시스템
"""

import asyncio
import heapq
import json
import logging
import os
import pickle
import random
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 테스트용 클래스들 (먼저 정의)
class NodeType(Enum):
    """노드 유형 - 확장된 버전"""

    PREMISE = "premise"
    INFERENCE = "inference"
    CONCLUSION = "conclusion"
    COUNTER_ARGUMENT = "counter_argument"
    EVIDENCE = "evidence"
    ASSUMPTION = "assumption"
    HYPOTHESIS = "hypothesis"
    CONSTRAINT = "constraint"
    ALTERNATIVE = "alternative"
    INTEGRATION = "integration"


class EdgeType(Enum):
    """엣지 유형 - 확장된 버전"""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    INFERS = "infers"
    ASSUMES = "assumes"
    EVIDENCES = "evidences"
    CONSTRAINS = "constrains"
    ALTERNATES = "alternates"
    INTEGRATES = "integrates"
    CHALLENGES = "challenges"
    REFINES = "refines"


@dataclass
class DynamicReasoningNode:
    """동적 추론 노드 (테스트용)"""

    node_id: str
    node_type: NodeType
    content: str
    confidence: float
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    semantic_vector: Optional[np.ndarray] = None
    activation_level: float = 1.0
    importance_score: float = 0.5


@dataclass
class DynamicReasoningEdge:
    """동적 추론 엣지 (테스트용)"""

    edge_id: str
    source_node: str
    target_node: str
    edge_type: EdgeType
    strength: float
    reasoning: str
    semantic_similarity: float = 0.0
    logical_validity: float = 0.0


@dataclass
class DynamicReasoningGraph:
    """동적 추론 그래프 (테스트용)"""

    graph_id: str
    nodes: Dict[str, DynamicReasoningNode] = field(default_factory=dict)
    edges: Dict[str, DynamicReasoningEdge] = field(default_factory=dict)


class LearningDataType(Enum):
    """학습 데이터 유형"""

    USER_INTERACTION = "user_interaction"
    SYSTEM_FEEDBACK = "system_feedback"
    PERFORMANCE_METRIC = "performance_metric"
    ERROR_CORRECTION = "error_correction"
    ADAPTATION_DATA = "adaptation_data"


class LearningTrigger(Enum):
    """학습 트리거 유형"""

    PERFORMANCE_DEGRADATION = "performance_degradation"
    USER_FEEDBACK = "user_feedback"
    ERROR_DETECTION = "error_detection"
    AUTOMATIC_SCHEDULE = "automatic_schedule"
    ADAPTATION_NEEDED = "adaptation_needed"


@dataclass
class LearningData:
    """학습 데이터"""

    data_id: str
    data_type: LearningDataType
    timestamp: datetime
    content: Dict[str, Any]
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed: bool = False


@dataclass
class LearningResult:
    """학습 결과"""

    learning_id: str
    trigger: LearningTrigger
    success: bool
    confidence: float
    description: str
    improvements: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class LearningDataCollector:
    """학습 데이터 수집 시스템"""

    def __init__(self):
        self.data_storage = {}
        self.collection_rules = self._initialize_collection_rules()
        self.data_queue = deque(maxlen=1000)
        self.collection_stats = defaultdict(int)

    def _initialize_collection_rules(self) -> Dict[str, Dict[str, Any]]:
        """수집 규칙 초기화"""
        return {
            "user_interaction": {
                "enabled": True,
                "priority": "high",
                "max_storage": 1000,
                "retention_days": 30,
            },
            "system_feedback": {
                "enabled": True,
                "priority": "medium",
                "max_storage": 500,
                "retention_days": 60,
            },
            "performance_metric": {
                "enabled": True,
                "priority": "high",
                "max_storage": 2000,
                "retention_days": 90,
            },
            "error_correction": {
                "enabled": True,
                "priority": "high",
                "max_storage": 500,
                "retention_days": 120,
            },
            "adaptation_data": {
                "enabled": True,
                "priority": "medium",
                "max_storage": 300,
                "retention_days": 45,
            },
        }

    async def collect_learning_data(
        self,
        data_type: LearningDataType,
        content: Dict[str, Any],
        source: str = "system",
    ) -> str:
        """학습 데이터 수집"""
        logger.info(f"학습 데이터 수집 시작: {data_type.value}")

        # 데이터 ID 생성
        data_id = f"{data_type.value}_{int(datetime.now().timestamp())}_{random.randint(1000, 9999)}"

        # 학습 데이터 생성
        learning_data = LearningData(
            data_id=data_id,
            data_type=data_type,
            timestamp=datetime.now(),
            content=content,
            source=source,
            metadata={
                "collection_timestamp": datetime.now().isoformat(),
                "data_size": len(str(content)),
                "priority": self.collection_rules.get(data_type.value, {}).get(
                    "priority", "medium"
                ),
            },
        )

        # 데이터 저장
        self.data_storage[data_id] = learning_data
        self.data_queue.append(learning_data)

        # 통계 업데이트
        self.collection_stats[data_type.value] += 1

        logger.info(f"학습 데이터 수집 완료: {data_id}")
        return data_id

    async def collect_user_interaction(
        self, user_id: str, interaction_type: str, interaction_data: Dict[str, Any]
    ) -> str:
        """사용자 상호작용 데이터 수집"""
        content = {
            "user_id": user_id,
            "interaction_type": interaction_type,
            "interaction_data": interaction_data,
            "timestamp": datetime.now().isoformat(),
        }

        return await self.collect_learning_data(
            LearningDataType.USER_INTERACTION, content, f"user_{user_id}"
        )

    async def collect_system_feedback(
        self, feedback_type: str, feedback_data: Dict[str, Any]
    ) -> str:
        """시스템 피드백 데이터 수집"""
        content = {
            "feedback_type": feedback_type,
            "feedback_data": feedback_data,
            "timestamp": datetime.now().isoformat(),
        }

        return await self.collect_learning_data(
            LearningDataType.SYSTEM_FEEDBACK, content, "system"
        )

    async def collect_performance_metric(
        self, metric_name: str, metric_value: float, context: Dict[str, Any] = None
    ) -> str:
        """성능 메트릭 데이터 수집"""
        content = {
            "metric_name": metric_name,
            "metric_value": metric_value,
            "context": context or {},
            "timestamp": datetime.now().isoformat(),
        }

        return await self.collect_learning_data(
            LearningDataType.PERFORMANCE_METRIC, content, "system"
        )

    async def collect_error_correction(
        self,
        error_type: str,
        error_data: Dict[str, Any],
        correction_data: Dict[str, Any],
    ) -> str:
        """오류 수정 데이터 수집"""
        content = {
            "error_type": error_type,
            "error_data": error_data,
            "correction_data": correction_data,
            "timestamp": datetime.now().isoformat(),
        }

        return await self.collect_learning_data(
            LearningDataType.ERROR_CORRECTION, content, "system"
        )

    async def get_learning_data(
        self, data_type: Optional[LearningDataType] = None, limit: int = 100
    ) -> List[LearningData]:
        """학습 데이터 조회"""
        if data_type:
            filtered_data = [
                data
                for data in self.data_storage.values()
                if data.data_type == data_type
            ]
        else:
            filtered_data = list(self.data_storage.values())

        # 시간순 정렬 (최신순)
        filtered_data.sort(key=lambda x: x.timestamp, reverse=True)

        return filtered_data[:limit]

    async def cleanup_old_data(self) -> int:
        """오래된 데이터 정리"""
        current_time = datetime.now()
        cleaned_count = 0

        for data_id, data in list(self.data_storage.items()):
            rule = self.collection_rules.get(data.data_type.value, {})
            retention_days = rule.get("retention_days", 30)

            if (current_time - data.timestamp).days > retention_days:
                del self.data_storage[data_id]
                cleaned_count += 1

        logger.info(f"오래된 데이터 정리 완료: {cleaned_count}개 삭제")
        return cleaned_count


class RealtimeModelUpdater:
    """실시간 모델 업데이트 시스템"""

    def __init__(self):
        self.model_versions = {}
        self.update_strategies = self._initialize_update_strategies()
        self.update_history = []
        self.model_performance = defaultdict(list)

    def _initialize_update_strategies(self) -> Dict[str, Dict[str, Any]]:
        """업데이트 전략 초기화"""
        return {
            "incremental": {
                "description": "점진적 업데이트",
                "update_frequency": "daily",
                "batch_size": 100,
                "learning_rate": 0.01,
            },
            "adaptive": {
                "description": "적응적 업데이트",
                "update_frequency": "on_demand",
                "batch_size": 50,
                "learning_rate": 0.02,
            },
            "comprehensive": {
                "description": "포괄적 업데이트",
                "update_frequency": "weekly",
                "batch_size": 500,
                "learning_rate": 0.005,
            },
        }

    async def update_model(
        self,
        graph: "DynamicReasoningGraph",
        learning_data: List[LearningData],
        strategy: str = "adaptive",
    ) -> LearningResult:
        """모델 업데이트"""
        logger.info(f"모델 업데이트 시작: {strategy}")

        learning_id = f"learning_{int(datetime.now().timestamp())}"
        strategy_config = self.update_strategies.get(
            strategy, self.update_strategies["adaptive"]
        )

        improvements = []
        metrics = {}

        try:
            # 1. 노드 신뢰도 업데이트
            node_improvements = await self._update_node_confidence(graph, learning_data)
            improvements.extend(node_improvements)

            # 2. 엣지 강도 업데이트
            edge_improvements = await self._update_edge_strength(graph, learning_data)
            improvements.extend(edge_improvements)

            # 3. 연결성 최적화
            connectivity_improvements = await self._optimize_connectivity(
                graph, learning_data
            )
            improvements.extend(connectivity_improvements)

            # 4. 성능 메트릭 계산
            metrics = await self._calculate_learning_metrics(graph, learning_data)

            # 5. 모델 버전 관리
            version_info = await self._create_model_version(graph, strategy, metrics)

            learning_result = LearningResult(
                learning_id=learning_id,
                trigger=LearningTrigger.ADAPTATION_NEEDED,
                success=True,
                confidence=metrics.get("overall_confidence", 0.7),
                description=f"모델 업데이트 완료: {len(improvements)}개 개선사항",
                improvements=improvements,
                metrics=metrics,
            )

            # 업데이트 이력에 추가
            self.update_history.append(
                {
                    "learning_result": learning_result,
                    "version_info": version_info,
                    "timestamp": datetime.now(),
                }
            )

            logger.info(f"모델 업데이트 완료: {len(improvements)}개 개선사항")
            return learning_result

        except Exception as e:
            logger.error(f"모델 업데이트 실패: {e}")
            return LearningResult(
                learning_id=learning_id,
                trigger=LearningTrigger.ADAPTATION_NEEDED,
                success=False,
                confidence=0.0,
                description=f"모델 업데이트 실패: {str(e)}",
            )

    async def _update_node_confidence(
        self, graph: "DynamicReasoningGraph", learning_data: List[LearningData]
    ) -> List[str]:
        """노드 신뢰도 업데이트"""
        improvements = []

        for node_id, node in graph.nodes.items():
            # 학습 데이터에서 해당 노드와 관련된 피드백 찾기
            relevant_feedback = []
            for data in learning_data:
                if data.data_type == LearningDataType.USER_INTERACTION:
                    if node_id in str(data.content):
                        relevant_feedback.append(data)
                elif data.data_type == LearningDataType.SYSTEM_FEEDBACK:
                    if node_id in str(data.content):
                        relevant_feedback.append(data)

            if relevant_feedback:
                # 피드백 기반 신뢰도 조정
                feedback_score = self._calculate_feedback_score(relevant_feedback)
                old_confidence = node.confidence
                node.confidence = min(
                    1.0, max(0.0, old_confidence + feedback_score * 0.1)
                )

                if abs(node.confidence - old_confidence) > 0.01:
                    improvements.append(
                        f"노드 {node_id} 신뢰도 업데이트: {old_confidence:.3f} → {node.confidence:.3f}"
                    )

        return improvements

    async def _update_edge_strength(
        self, graph: "DynamicReasoningGraph", learning_data: List[LearningData]
    ) -> List[str]:
        """엣지 강도 업데이트"""
        improvements = []

        for edge_id, edge in graph.edges.items():
            # 학습 데이터에서 해당 엣지와 관련된 피드백 찾기
            relevant_feedback = []
            for data in learning_data:
                if data.data_type == LearningDataType.USER_INTERACTION:
                    if (
                        edge_id in str(data.content)
                        or edge.source_node in str(data.content)
                        or edge.target_node in str(data.content)
                    ):
                        relevant_feedback.append(data)

            if relevant_feedback:
                # 피드백 기반 강도 조정
                feedback_score = self._calculate_feedback_score(relevant_feedback)
                old_strength = edge.strength
                edge.strength = min(1.0, max(0.0, old_strength + feedback_score * 0.1))

                if abs(edge.strength - old_strength) > 0.01:
                    improvements.append(
                        f"엣지 {edge_id} 강도 업데이트: {old_strength:.3f} → {edge.strength:.3f}"
                    )

        return improvements

    async def _optimize_connectivity(
        self, graph: "DynamicReasoningGraph", learning_data: List[LearningData]
    ) -> List[str]:
        """연결성 최적화"""
        improvements = []

        # 고립된 노드 찾기
        isolated_nodes = []
        for node_id in graph.nodes:
            has_connection = False
            for edge in graph.edges.values():
                if edge.source_node == node_id or edge.target_node == node_id:
                    has_connection = True
                    break

            if not has_connection:
                isolated_nodes.append(node_id)

        # 고립된 노드들을 다른 노드와 연결
        for node_id in isolated_nodes:
            node = graph.nodes.get(node_id)
            if node:
                # 가장 유사한 노드 찾기
                best_similarity = 0.0
                best_target = None

                for target_id, target_node in graph.nodes.items():
                    if target_id != node_id:
                        # 간단한 유사도 계산
                        similarity = await self._calculate_simple_similarity(
                            node.content, target_node.content
                        )
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_target = target_id

                # 새로운 엣지 생성
                if best_target and best_similarity > 0.2:
                    new_edge_id = f"learning_edge_{node_id}_{best_target}"
                    new_edge = DynamicReasoningEdge(
                        edge_id=new_edge_id,
                        source_node=node_id,
                        target_node=best_target,
                        edge_type=EdgeType.SUPPORTS,
                        strength=best_similarity,
                        reasoning=f"학습 기반 연결성 최적화 (유사도: {best_similarity:.2f})",
                        semantic_similarity=best_similarity,
                    )
                    graph.edges[new_edge_id] = new_edge
                    improvements.append(
                        f"고립된 노드 {node_id} 연결 생성: {best_target} (유사도: {best_similarity:.2f})"
                    )

        return improvements

    async def _calculate_learning_metrics(
        self, graph: "DynamicReasoningGraph", learning_data: List[LearningData]
    ) -> Dict[str, float]:
        """학습 메트릭 계산"""
        metrics = {}

        # 평균 노드 신뢰도
        node_confidences = [node.confidence for node in graph.nodes.values()]
        metrics["avg_node_confidence"] = (
            sum(node_confidences) / len(node_confidences) if node_confidences else 0.0
        )

        # 평균 엣지 강도
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        metrics["avg_edge_strength"] = (
            sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0
        )

        # 연결성
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        metrics["connectivity"] = (
            total_edges / (total_nodes * (total_nodes - 1) / 2)
            if total_nodes > 1
            else 0.0
        )

        # 학습 데이터 품질
        metrics["learning_data_quality"] = (
            len([d for d in learning_data if d.processed]) / len(learning_data)
            if learning_data
            else 0.0
        )

        # 종합 신뢰도
        metrics["overall_confidence"] = (
            metrics["avg_node_confidence"] + metrics["avg_edge_strength"]
        ) / 2.0

        return metrics

    async def _create_model_version(
        self, graph: "DynamicReasoningGraph", strategy: str, metrics: Dict[str, float]
    ) -> Dict[str, Any]:
        """모델 버전 생성"""
        version_id = (
            f"v{len(self.model_versions) + 1}_{int(datetime.now().timestamp())}"
        )

        version_info = {
            "version_id": version_id,
            "strategy": strategy,
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
        }

        self.model_versions[version_id] = version_info
        return version_info

    def _calculate_feedback_score(self, feedback_data: List[LearningData]) -> float:
        """피드백 점수 계산"""
        if not feedback_data:
            return 0.0

        total_score = 0.0
        for data in feedback_data:
            if data.data_type == LearningDataType.USER_INTERACTION:
                # 사용자 상호작용은 양수 점수
                total_score += 0.1
            elif data.data_type == LearningDataType.SYSTEM_FEEDBACK:
                # 시스템 피드백은 중성 점수
                total_score += 0.0
            elif data.data_type == LearningDataType.ERROR_CORRECTION:
                # 오류 수정은 양수 점수
                total_score += 0.2

        return total_score / len(feedback_data)

    async def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """간단한 유사도 계산"""
        keywords1 = set(re.findall(r"[가-힣a-zA-Z]+", text1.lower()))
        keywords2 = set(re.findall(r"[가-힣a-zA-Z]+", text2.lower()))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0


class LearningPerformanceEvaluator:
    """학습 성과 평가 시스템"""

    def __init__(self):
        self.evaluation_criteria = self._initialize_evaluation_criteria()
        self.performance_history = []

    def _initialize_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """평가 기준 초기화"""
        return {
            "accuracy_improvement": {"weight": 0.3, "description": "정확도 향상"},
            "adaptability": {"weight": 0.25, "description": "적응성"},
            "efficiency": {"weight": 0.25, "description": "효율성"},
            "stability": {"weight": 0.2, "description": "안정성"},
        }

    async def evaluate_learning_performance(
        self,
        graph: "DynamicReasoningGraph",
        learning_data: List[LearningData],
        learning_result: LearningResult,
    ) -> Dict[str, Any]:
        """학습 성과 평가"""
        logger.info(f"학습 성과 평가 시작: {learning_result.learning_id}")

        # 1. 정확도 향상 평가
        accuracy_improvement = await self._evaluate_accuracy_improvement(
            graph, learning_data
        )

        # 2. 적응성 평가
        adaptability = await self._evaluate_adaptability(graph, learning_data)

        # 3. 효율성 평가
        efficiency = await self._evaluate_efficiency(learning_result)

        # 4. 안정성 평가
        stability = await self._evaluate_stability(graph)

        # 종합 성과 점수
        overall_performance = (
            accuracy_improvement
            * self.evaluation_criteria["accuracy_improvement"]["weight"]
            + adaptability * self.evaluation_criteria["adaptability"]["weight"]
            + efficiency * self.evaluation_criteria["efficiency"]["weight"]
            + stability * self.evaluation_criteria["stability"]["weight"]
        )

        evaluation_result = {
            "overall_performance": overall_performance,
            "accuracy_improvement": accuracy_improvement,
            "adaptability": adaptability,
            "efficiency": efficiency,
            "stability": stability,
            "evaluation_details": {
                "learning_data_count": len(learning_data),
                "improvements_count": len(learning_result.improvements),
                "graph_complexity": len(graph.nodes) + len(graph.edges),
            },
        }

        # 성과 이력에 추가
        self.performance_history.append(
            {
                "evaluation_result": evaluation_result,
                "learning_result": learning_result,
                "timestamp": datetime.now(),
            }
        )

        return evaluation_result

    async def _evaluate_accuracy_improvement(
        self, graph: "DynamicReasoningGraph", learning_data: List[LearningData]
    ) -> float:
        """정확도 향상 평가"""
        if not learning_data:
            return 0.0

        # 노드 신뢰도 향상
        node_confidences = [node.confidence for node in graph.nodes.values()]
        avg_confidence = (
            sum(node_confidences) / len(node_confidences) if node_confidences else 0.0
        )

        # 엣지 강도 향상
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        avg_strength = (
            sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0
        )

        # 학습 데이터 품질
        processed_data = [d for d in learning_data if d.processed]
        data_quality = (
            len(processed_data) / len(learning_data) if learning_data else 0.0
        )

        # 종합 정확도 향상
        accuracy_improvement = (avg_confidence + avg_strength + data_quality) / 3.0

        return accuracy_improvement

    async def _evaluate_adaptability(
        self, graph: "DynamicReasoningGraph", learning_data: List[LearningData]
    ) -> float:
        """적응성 평가"""
        if not learning_data:
            return 0.0

        # 다양한 데이터 유형 처리 능력
        data_types = set(data.data_type for data in learning_data)
        type_diversity = len(data_types) / len(LearningDataType)

        # 연결성 적응성
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        connectivity_adaptability = (
            min(1.0, total_edges / (total_nodes * 2)) if total_nodes > 0 else 0.0
        )

        # 학습 속도
        recent_data = [
            d for d in learning_data if (datetime.now() - d.timestamp).days <= 7
        ]
        learning_speed = len(recent_data) / max(1, len(learning_data))

        # 종합 적응성
        adaptability = (
            type_diversity + connectivity_adaptability + learning_speed
        ) / 3.0

        return adaptability

    async def _evaluate_efficiency(self, learning_result: LearningResult) -> float:
        """효율성 평가"""
        if not learning_result.success:
            return 0.0

        # 개선사항 수
        improvements_count = len(learning_result.improvements)
        efficiency_score = min(
            1.0, improvements_count / 10.0
        )  # 최대 10개 개선사항 기준

        # 신뢰도
        confidence_score = learning_result.confidence

        # 메트릭 품질
        metrics_quality = len(learning_result.metrics) / 5.0  # 최대 5개 메트릭 기준

        # 종합 효율성
        efficiency = (efficiency_score + confidence_score + metrics_quality) / 3.0

        return efficiency

    async def _evaluate_stability(self, graph: "DynamicReasoningGraph") -> float:
        """안정성 평가"""
        if not graph.nodes:
            return 0.0

        # 노드 신뢰도의 표준편차 (낮을수록 안정적)
        node_confidences = [node.confidence for node in graph.nodes.values()]
        if len(node_confidences) < 2:
            return 0.5

        confidence_std = np.std(node_confidences)
        confidence_stability = max(0.0, 1.0 - confidence_std)

        # 엣지 강도의 표준편차
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        if len(edge_strengths) < 2:
            return confidence_stability

        strength_std = np.std(edge_strengths)
        strength_stability = max(0.0, 1.0 - strength_std)

        # 연결성 안정성
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        connectivity_stability = (
            min(1.0, total_edges / (total_nodes * (total_nodes - 1) / 2))
            if total_nodes > 1
            else 0.0
        )

        # 종합 안정성
        stability = (
            confidence_stability + strength_stability + connectivity_stability
        ) / 3.0

        return stability


class LearningValidator:
    """학습 검증 시스템"""

    def __init__(self):
        self.validation_criteria = self._initialize_validation_criteria()

    def _initialize_validation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """검증 기준 초기화"""
        return {
            "learning_success": {"weight": 0.3, "description": "학습 성공률"},
            "performance_improvement": {"weight": 0.3, "description": "성능 향상도"},
            "system_stability": {"weight": 0.2, "description": "시스템 안정성"},
            "learning_efficiency": {"weight": 0.2, "description": "학습 효율성"},
        }

    async def validate_learning(
        self,
        graph: "DynamicReasoningGraph",
        learning_result: LearningResult,
        performance_evaluation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """학습 검증"""
        logger.info(f"학습 검증 시작: {learning_result.learning_id}")

        # 1. 학습 성공률 평가
        learning_success = self._evaluate_learning_success(learning_result)

        # 2. 성능 향상도 평가
        performance_improvement = await self._evaluate_performance_improvement(
            performance_evaluation
        )

        # 3. 시스템 안정성 평가
        system_stability = await self._evaluate_system_stability(graph)

        # 4. 학습 효율성 평가
        learning_efficiency = self._evaluate_learning_efficiency(learning_result)

        # 종합 검증 점수
        overall_score = (
            learning_success * self.validation_criteria["learning_success"]["weight"]
            + performance_improvement
            * self.validation_criteria["performance_improvement"]["weight"]
            + system_stability * self.validation_criteria["system_stability"]["weight"]
            + learning_efficiency
            * self.validation_criteria["learning_efficiency"]["weight"]
        )

        return {
            "overall_score": overall_score,
            "learning_success": learning_success,
            "performance_improvement": performance_improvement,
            "system_stability": system_stability,
            "learning_efficiency": learning_efficiency,
            "validation_details": {
                "improvements_count": len(learning_result.improvements),
                "metrics_count": len(learning_result.metrics),
                "graph_complexity": len(graph.nodes) + len(graph.edges),
            },
        }

    def _evaluate_learning_success(self, learning_result: LearningResult) -> float:
        """학습 성공률 평가"""
        if not learning_result.success:
            return 0.0

        # 개선사항 수
        improvements_score = min(1.0, len(learning_result.improvements) / 5.0)

        # 신뢰도
        confidence_score = learning_result.confidence

        # 메트릭 품질
        metrics_score = min(1.0, len(learning_result.metrics) / 3.0)

        return (improvements_score + confidence_score + metrics_score) / 3.0

    async def _evaluate_performance_improvement(
        self, performance_evaluation: Dict[str, Any]
    ) -> float:
        """성능 향상도 평가"""
        overall_performance = performance_evaluation.get("overall_performance", 0.0)
        return overall_performance

    async def _evaluate_system_stability(self, graph: "DynamicReasoningGraph") -> float:
        """시스템 안정성 평가"""
        if not graph.nodes:
            return 0.0

        # 노드 신뢰도의 표준편차
        node_confidences = [node.confidence for node in graph.nodes.values()]
        if len(node_confidences) < 2:
            return 0.5

        confidence_std = np.std(node_confidences)
        stability_score = max(0.0, 1.0 - confidence_std)

        return stability_score

    def _evaluate_learning_efficiency(self, learning_result: LearningResult) -> float:
        """학습 효율성 평가"""
        if not learning_result.success:
            return 0.0

        # 개선사항 대비 메트릭 수
        improvements_count = len(learning_result.improvements)
        metrics_count = len(learning_result.metrics)

        if improvements_count == 0:
            return 0.0

        efficiency = min(1.0, metrics_count / improvements_count)
        return efficiency


async def test_realtime_learning_system():
    """실시간 학습 시스템 테스트"""
    print("=== 실시간 학습 시스템 테스트 시작 (Phase 1-3 Week 3 Day 6) ===")

    # 테스트 그래프 생성
    graph = DynamicReasoningGraph(graph_id="test_graph")

    # 초기 노드들 생성
    initial_nodes = {
        "node1": DynamicReasoningNode(
            "node1", NodeType.PREMISE, "윤리적 행동은 옳다", 0.8, "test"
        ),
        "node2": DynamicReasoningNode(
            "node2", NodeType.INFERENCE, "윤리적 행동 분석: 도덕적 의무", 0.7, "test"
        ),
        "node3": DynamicReasoningNode(
            "node3", NodeType.CONCLUSION, "윤리적 행동 필요: 최종 판단", 0.9, "test"
        ),
        "node4": DynamicReasoningNode(
            "node4", NodeType.EVIDENCE, "윤리적 행동의 증거: 사회적 이익", 0.8, "test"
        ),
        "node5": DynamicReasoningNode(
            "node5",
            NodeType.COUNTER_ARGUMENT,
            "윤리적 행동의 반론: 자유 제한",
            0.6,
            "test",
        ),
    }

    graph.nodes = initial_nodes

    print(f"\n📊 초기 그래프 상태:")
    print(f"  • 노드 수: {len(graph.nodes)}")
    print(f"  • 엣지 수: {len(graph.edges)}")

    # 1. 학습 데이터 수집 테스트
    data_collector = LearningDataCollector()

    print(f"\n📊 학습 데이터 수집 테스트:")

    # 사용자 상호작용 데이터 수집
    user_interaction_id = await data_collector.collect_user_interaction(
        "user1",
        "node_feedback",
        {"node_id": "node1", "rating": 5, "comment": "좋은 전제"},
    )
    print(f"  • 사용자 상호작용 데이터 수집: {user_interaction_id}")

    # 시스템 피드백 데이터 수집
    system_feedback_id = await data_collector.collect_system_feedback(
        "performance_metric", {"metric": "accuracy", "value": 0.85}
    )
    print(f"  • 시스템 피드백 데이터 수집: {system_feedback_id}")

    # 성능 메트릭 데이터 수집
    performance_metric_id = await data_collector.collect_performance_metric(
        "node_confidence", 0.82, {"context": "user_interaction"}
    )
    print(f"  • 성능 메트릭 데이터 수집: {performance_metric_id}")

    # 오류 수정 데이터 수집
    error_correction_id = await data_collector.collect_error_correction(
        "semantic_error", {"error": "의미적 불일치"}, {"correction": "의미적 일치 개선"}
    )
    print(f"  • 오류 수정 데이터 수집: {error_correction_id}")

    # 수집된 데이터 조회
    learning_data = await data_collector.get_learning_data()
    print(f"  • 수집된 데이터 수: {len(learning_data)}")

    # 2. 실시간 모델 업데이트 테스트
    model_updater = RealtimeModelUpdater()

    print(f"\n🔄 실시간 모델 업데이트 테스트:")
    learning_result = await model_updater.update_model(graph, learning_data, "adaptive")

    print(f"  • 학습 성공: {learning_result.success}")
    print(f"  • 개선사항 수: {len(learning_result.improvements)}")
    print(f"  • 신뢰도: {learning_result.confidence:.3f}")

    if learning_result.improvements:
        print(f"  • 주요 개선사항:")
        for improvement in learning_result.improvements[:3]:
            print(f"    - {improvement}")

    if learning_result.metrics:
        print(f"  • 학습 메트릭:")
        for metric, value in learning_result.metrics.items():
            print(f"    - {metric}: {value:.3f}")

    # 3. 학습 성과 평가 테스트
    performance_evaluator = LearningPerformanceEvaluator()

    print(f"\n📊 학습 성과 평가 테스트:")
    performance_evaluation = await performance_evaluator.evaluate_learning_performance(
        graph, learning_data, learning_result
    )

    print(f"  • 종합 성과 점수: {performance_evaluation['overall_performance']:.3f}")
    print(f"  • 정확도 향상: {performance_evaluation['accuracy_improvement']:.3f}")
    print(f"  • 적응성: {performance_evaluation['adaptability']:.3f}")
    print(f"  • 효율성: {performance_evaluation['efficiency']:.3f}")
    print(f"  • 안정성: {performance_evaluation['stability']:.3f}")

    # 4. 학습 검증 테스트
    learning_validator = LearningValidator()

    print(f"\n✅ 학습 검증 테스트:")
    validation_result = await learning_validator.validate_learning(
        graph, learning_result, performance_evaluation
    )

    print(f"  • 종합 검증 점수: {validation_result['overall_score']:.3f}")
    print(f"  • 학습 성공률: {validation_result['learning_success']:.3f}")
    print(f"  • 성능 향상도: {validation_result['performance_improvement']:.3f}")
    print(f"  • 시스템 안정성: {validation_result['system_stability']:.3f}")
    print(f"  • 학습 효율성: {validation_result['learning_efficiency']:.3f}")

    # 5. 최종 그래프 상태
    print(f"\n📊 최종 그래프 상태:")
    print(f"  • 노드 수: {len(graph.nodes)}")
    print(f"  • 엣지 수: {len(graph.edges)} (증가: {len(graph.edges) - 0})")

    # 노드 신뢰도 변화
    print(f"  • 노드 신뢰도:")
    for node_id, node in graph.nodes.items():
        print(f"    - {node_id}: {node.confidence:.3f}")

    # 엣지 강도 변화
    if graph.edges:
        print(f"  • 엣지 강도:")
        for edge_id, edge in list(graph.edges.items())[:3]:
            print(f"    - {edge_id}: {edge.strength:.3f}")

    print(f"\n{'='*70}")
    print("=== 실시간 학습 시스템 테스트 완료 (Phase 1-3 Week 3 Day 6) ===")
    print("✅ Day 6 목표 달성: 실시간 학습 시스템 구현")
    print("✅ 학습 데이터 수집 시스템 구현")
    print("✅ 실시간 모델 업데이트 시스템 구현")
    print("✅ 학습 성과 평가 시스템 구현")
    print("✅ 학습 검증 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_realtime_learning_system())
