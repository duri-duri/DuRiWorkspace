#!/usr/bin/env python3
"""
DuRi 추론 경로 검증 시스템 - Phase 1-3 Week 3 Day 2
동적 추론 그래프의 추론 경로를 검증하고 최적화하는 시스템

기능:
1. 추론 경로 검증 시스템
2. 경로 최적화 시스템
3. 경로 다양성 시스템
4. 경로 평가 시스템
"""

import asyncio
import heapq
import json
import logging
import re
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


@dataclass
class ReasoningPath:
    """추론 경로"""

    path_id: str
    nodes: List[str]  # 노드 ID 리스트
    edges: List[str]  # 엣지 ID 리스트
    confidence: float = 0.0
    validity: float = 0.0
    completeness: float = 0.0
    coherence: float = 0.0
    strength: float = 0.0
    reasoning_steps: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class PathValidationResult:
    """경로 검증 결과"""

    is_valid: bool
    validity_score: float
    completeness_score: float
    coherence_score: float
    strength_score: float
    issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class ReasoningPathValidator:
    """추론 경로 검증 시스템"""

    def __init__(self):
        self.validation_rules = self._initialize_validation_rules()
        self.path_cache = {}
        self.max_cache_size = 1000

    def _initialize_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """검증 규칙 초기화"""
        return {
            "logical_consistency": {"weight": 0.3, "description": "논리적 일관성 검증"},
            "completeness": {"weight": 0.25, "description": "경로 완전성 검증"},
            "coherence": {"weight": 0.25, "description": "의미적 일관성 검증"},
            "strength": {"weight": 0.2, "description": "경로 강도 검증"},
        }

    async def validate_reasoning_path(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> PathValidationResult:
        """추론 경로 검증"""
        logger.info(f"추론 경로 검증 시작: {path.path_id}")

        # 캐시 확인
        cache_key = f"{path.path_id}_{len(path.nodes)}_{len(path.edges)}"
        if cache_key in self.path_cache:
            return self.path_cache[cache_key]

        # 1. 논리적 일관성 검증
        logical_consistency = await self._validate_logical_consistency(path, graph)

        # 2. 완전성 검증
        completeness = await self._validate_completeness(path, graph)

        # 3. 일관성 검증
        coherence = await self._validate_coherence(path, graph)

        # 4. 강도 검증
        strength = await self._validate_strength(path, graph)

        # 종합 검증 결과
        overall_validity = (
            logical_consistency * self.validation_rules["logical_consistency"]["weight"]
            + completeness * self.validation_rules["completeness"]["weight"]
            + coherence * self.validation_rules["coherence"]["weight"]
            + strength * self.validation_rules["strength"]["weight"]
        )

        # 이슈 및 권장사항 생성
        issues = self._generate_issues(
            path, logical_consistency, completeness, coherence, strength
        )
        recommendations = self._generate_recommendations(issues)

        result = PathValidationResult(
            is_valid=overall_validity > 0.7,
            validity_score=overall_validity,
            completeness_score=completeness,
            coherence_score=coherence,
            strength_score=strength,
            issues=issues,
            recommendations=recommendations,
        )

        # 캐시에 저장
        if len(self.path_cache) < self.max_cache_size:
            self.path_cache[cache_key] = result

        return result

    async def _validate_logical_consistency(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """논리적 일관성 검증"""
        if len(path.nodes) < 2:
            return 0.0

        consistency_scores = []

        # 연속된 노드 간의 논리적 연결 검증
        for i in range(len(path.nodes) - 1):
            node1_id = path.nodes[i]
            node2_id = path.nodes[i + 1]

            # 두 노드 간의 엣지 찾기
            edge_found = False
            edge_validity = 0.0

            for edge in graph.edges.values():
                if (edge.source_node == node1_id and edge.target_node == node2_id) or (
                    edge.source_node == node2_id and edge.target_node == node1_id
                ):
                    edge_found = True
                    edge_validity = edge.logical_validity
                    break

            if edge_found:
                consistency_scores.append(edge_validity)
            else:
                # 직접 연결이 없는 경우 의미적 유사도 기반 검증
                node1 = graph.nodes.get(node1_id)
                node2 = graph.nodes.get(node2_id)

                if node1 and node2:
                    # 간단한 의미적 유사도 계산
                    similarity = self._calculate_simple_similarity(
                        node1.content, node2.content
                    )
                    consistency_scores.append(
                        similarity * 0.5
                    )  # 직접 연결이 없으므로 가중치 감소
                else:
                    consistency_scores.append(0.0)

        return (
            sum(consistency_scores) / len(consistency_scores)
            if consistency_scores
            else 0.0
        )

    async def _validate_completeness(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """완전성 검증"""
        if not path.nodes:
            return 0.0

        # 필수 노드 유형 확인
        required_node_types = {
            NodeType.PREMISE,
            NodeType.INFERENCE,
            NodeType.CONCLUSION,
        }
        path_node_types = set()

        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                path_node_types.add(node.node_type)

        # 필수 노드 유형 포함도
        completeness_score = len(
            path_node_types.intersection(required_node_types)
        ) / len(required_node_types)

        # 경로 길이 적절성 (너무 짧거나 긴 경로는 완전성이 낮음)
        optimal_length = 5  # 최적 경로 길이
        length_score = 1.0 - abs(len(path.nodes) - optimal_length) / optimal_length
        length_score = max(0.0, length_score)

        # 종합 완전성 점수
        overall_completeness = completeness_score * 0.7 + length_score * 0.3
        return overall_completeness

    async def _validate_coherence(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """일관성 검증"""
        if len(path.nodes) < 2:
            return 0.0

        coherence_scores = []

        # 노드 간 의미적 일관성 검증
        for i in range(len(path.nodes) - 1):
            node1 = graph.nodes.get(path.nodes[i])
            node2 = graph.nodes.get(path.nodes[i + 1])

            if node1 and node2:
                # 의미적 유사도 계산
                similarity = self._calculate_simple_similarity(
                    node1.content, node2.content
                )
                coherence_scores.append(similarity)

        # 엣지의 의미적 일관성 검증
        for edge_id in path.edges:
            edge = graph.edges.get(edge_id)
            if edge:
                coherence_scores.append(edge.semantic_similarity)

        return (
            sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
        )

    async def _validate_strength(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """강도 검증"""
        if not path.nodes:
            return 0.0

        # 노드 신뢰도의 평균
        node_confidences = []
        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                node_confidences.append(node.confidence)

        avg_node_confidence = (
            sum(node_confidences) / len(node_confidences) if node_confidences else 0.0
        )

        # 엣지 강도의 평균
        edge_strengths = []
        for edge_id in path.edges:
            edge = graph.edges.get(edge_id)
            if edge:
                edge_strengths.append(edge.strength)

        avg_edge_strength = (
            sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0
        )

        # 종합 강도 (노드 60%, 엣지 40%)
        overall_strength = avg_node_confidence * 0.6 + avg_edge_strength * 0.4
        return overall_strength

    def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """간단한 의미적 유사도 계산"""
        # 키워드 기반 유사도 계산
        keywords1 = set(re.findall(r"\w+", text1.lower()))
        keywords2 = set(re.findall(r"\w+", text2.lower()))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

    def _generate_issues(
        self,
        path: ReasoningPath,
        logical_consistency: float,
        completeness: float,
        coherence: float,
        strength: float,
    ) -> List[str]:
        """이슈 생성"""
        issues = []

        if logical_consistency < 0.7:
            issues.append("논리적 일관성이 낮습니다")

        if completeness < 0.6:
            issues.append("경로 완전성이 부족합니다")

        if coherence < 0.6:
            issues.append("의미적 일관성이 낮습니다")

        if strength < 0.6:
            issues.append("경로 강도가 약합니다")

        if len(path.nodes) < 3:
            issues.append("경로가 너무 짧습니다")

        if len(path.nodes) > 10:
            issues.append("경로가 너무 깁니다")

        return issues

    def _generate_recommendations(self, issues: List[str]) -> List[str]:
        """권장사항 생성"""
        recommendations = []

        for issue in issues:
            if "논리적 일관성" in issue:
                recommendations.append("노드 간 논리적 연결을 강화하세요")
            elif "완전성" in issue:
                recommendations.append("필수 노드 유형을 추가하세요")
            elif "의미적 일관성" in issue:
                recommendations.append("의미적으로 관련된 노드들을 연결하세요")
            elif "강도" in issue:
                recommendations.append("신뢰도가 높은 노드와 강한 엣지를 사용하세요")
            elif "너무 짧습니다" in issue:
                recommendations.append("추가적인 추론 단계를 포함하세요")
            elif "너무 깁니다" in issue:
                recommendations.append("불필요한 노드를 제거하여 경로를 단순화하세요")

        return recommendations


class ReasoningPathOptimizer:
    """추론 경로 최적화 시스템"""

    def __init__(self):
        self.optimization_algorithms = self._initialize_optimization_algorithms()

    def _initialize_optimization_algorithms(self) -> Dict[str, str]:
        """최적화 알고리즘 초기화"""
        return {
            "dijkstra": "최단 경로 알고리즘",
            "bellman_ford": "음수 가중치 지원 알고리즘",
            "a_star": "휴리스틱 기반 최적화 알고리즘",
            "genetic": "유전 알고리즘 기반 최적화",
        }

    def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """간단한 의미적 유사도 계산"""
        # 키워드 기반 유사도 계산
        keywords1 = set(re.findall(r"\w+", text1.lower()))
        keywords2 = set(re.findall(r"\w+", text2.lower()))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

    async def find_optimal_paths(
        self,
        graph: "DynamicReasoningGraph",
        start_nodes: List[str],
        end_nodes: List[str],
        max_paths: int = 5,
    ) -> List[ReasoningPath]:
        """최적 경로 탐색"""
        logger.info(
            f"최적 경로 탐색 시작: {len(start_nodes)} 시작점, {len(end_nodes)} 종료점"
        )

        optimal_paths = []

        for start_node in start_nodes:
            for end_node in end_nodes:
                if start_node != end_node:
                    # A* 알고리즘을 사용한 최적 경로 탐색
                    path = await self._find_path_a_star(graph, start_node, end_node)
                    if path:
                        optimal_paths.append(path)

        # 경로 품질에 따라 정렬
        optimal_paths.sort(key=lambda p: p.confidence, reverse=True)

        return optimal_paths[:max_paths]

    async def _find_path_a_star(
        self, graph: "DynamicReasoningGraph", start_node: str, end_node: str
    ) -> Optional[ReasoningPath]:
        """A* 알고리즘을 사용한 경로 탐색"""
        if start_node not in graph.nodes or end_node not in graph.nodes:
            return None

        # 우선순위 큐 (f_score, node_id, path)
        open_set = [(0, start_node, [start_node], [])]
        closed_set = set()

        while open_set:
            f_score, current_node, current_path, current_edges = heapq.heappop(open_set)

            if current_node == end_node:
                # 경로 생성
                path = ReasoningPath(
                    path_id=f"optimal_path_{len(current_path)}_{int(datetime.now().timestamp())}",
                    nodes=current_path,
                    edges=current_edges,
                )

                # 경로 메트릭 계산
                await self._calculate_path_metrics(path, graph)
                return path

            if current_node in closed_set:
                continue

            closed_set.add(current_node)

            # 인접 노드 탐색
            for edge in graph.edges.values():
                if edge.source_node == current_node:
                    neighbor = edge.target_node
                    if neighbor not in closed_set:
                        new_path = current_path + [neighbor]
                        new_edges = current_edges + [edge.edge_id]

                        # f_score 계산 (g_score + h_score)
                        g_score = len(new_path)  # 경로 길이
                        h_score = self._calculate_heuristic(neighbor, end_node, graph)
                        f_score = g_score + h_score

                        heapq.heappush(
                            open_set, (f_score, neighbor, new_path, new_edges)
                        )

                elif edge.target_node == current_node:
                    neighbor = edge.source_node
                    if neighbor not in closed_set:
                        new_path = current_path + [neighbor]
                        new_edges = current_edges + [edge.edge_id]

                        g_score = len(new_path)
                        h_score = self._calculate_heuristic(neighbor, end_node, graph)
                        f_score = g_score + h_score

                        heapq.heappush(
                            open_set, (f_score, neighbor, new_path, new_edges)
                        )

        return None

    def _calculate_heuristic(
        self, current_node: str, end_node: str, graph: "DynamicReasoningGraph"
    ) -> float:
        """휴리스틱 함수 계산"""
        current = graph.nodes.get(current_node)
        end = graph.nodes.get(end_node)

        if not current or not end:
            return float("inf")

        # 간단한 휴리스틱: 노드 유형 기반 거리
        type_distance = {
            NodeType.PREMISE: 0,
            NodeType.INFERENCE: 1,
            NodeType.CONCLUSION: 2,
            NodeType.COUNTER_ARGUMENT: 1,
            NodeType.EVIDENCE: 1,
            NodeType.ASSUMPTION: 1,
            NodeType.HYPOTHESIS: 1,
            NodeType.CONSTRAINT: 1,
            NodeType.ALTERNATIVE: 1,
            NodeType.INTEGRATION: 2,
        }

        current_type_score = type_distance.get(current.node_type, 1)
        end_type_score = type_distance.get(end.node_type, 1)

        return abs(current_type_score - end_type_score)

    async def _calculate_path_metrics(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ):
        """경로 메트릭 계산"""
        if not path.nodes:
            return

        # 신뢰도 계산
        node_confidences = []
        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                node_confidences.append(node.confidence)

        path.confidence = (
            sum(node_confidences) / len(node_confidences) if node_confidences else 0.0
        )

        # 강도 계산
        edge_strengths = []
        for edge_id in path.edges:
            edge = graph.edges.get(edge_id)
            if edge:
                edge_strengths.append(edge.strength)

        path.strength = (
            sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0
        )

        # 일관성 계산
        coherence_scores = []
        for i in range(len(path.nodes) - 1):
            node1 = graph.nodes.get(path.nodes[i])
            node2 = graph.nodes.get(path.nodes[i + 1])

            if node1 and node2:
                similarity = self._calculate_simple_similarity(
                    node1.content, node2.content
                )
                coherence_scores.append(similarity)

        path.coherence = (
            sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0.0
        )

        # 완전성 계산
        required_types = {NodeType.PREMISE, NodeType.INFERENCE, NodeType.CONCLUSION}
        path_types = set()

        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                path_types.add(node.node_type)

        path.completeness = len(path_types.intersection(required_types)) / len(
            required_types
        )

        # 유효성 계산
        path.validity = (
            path.confidence + path.strength + path.coherence + path.completeness
        ) / 4.0


class ReasoningPathDiversityGenerator:
    """추론 경로 다양성 생성 시스템"""

    def __init__(self):
        self.diversity_strategies = self._initialize_diversity_strategies()

    def _initialize_diversity_strategies(self) -> Dict[str, str]:
        """다양성 전략 초기화"""
        return {
            "alternative_perspectives": "대안적 관점 기반 경로",
            "different_reasoning_types": "다양한 추론 유형 기반 경로",
            "varying_complexity": "다양한 복잡도 기반 경로",
            "semantic_variations": "의미적 변형 기반 경로",
        }

    async def generate_diverse_paths(
        self,
        graph: "DynamicReasoningGraph",
        base_path: ReasoningPath,
        num_variations: int = 3,
    ) -> List[ReasoningPath]:
        """다양한 경로 생성"""
        logger.info(f"다양한 경로 생성 시작: {num_variations}개 변형")

        diverse_paths = []

        # 1. 대안적 관점 기반 경로
        alternative_paths = await self._generate_alternative_perspective_paths(
            graph, base_path
        )
        diverse_paths.extend(alternative_paths[: num_variations // 3])

        # 2. 다양한 추론 유형 기반 경로
        reasoning_type_paths = await self._generate_different_reasoning_type_paths(
            graph, base_path
        )
        diverse_paths.extend(reasoning_type_paths[: num_variations // 3])

        # 3. 다양한 복잡도 기반 경로
        complexity_paths = await self._generate_varying_complexity_paths(
            graph, base_path
        )
        diverse_paths.extend(complexity_paths[: num_variations // 3])

        return diverse_paths[:num_variations]

    async def _generate_alternative_perspective_paths(
        self, graph: "DynamicReasoningGraph", base_path: ReasoningPath
    ) -> List[ReasoningPath]:
        """대안적 관점 기반 경로 생성"""
        alternative_paths = []

        # 반론 노드들을 포함하는 경로 생성
        counter_argument_nodes = [
            n for n in graph.nodes.values() if n.node_type == NodeType.COUNTER_ARGUMENT
        ]

        for counter_node in counter_argument_nodes:
            if counter_node.node_id not in base_path.nodes:
                # 기존 경로에 반론 노드 추가
                new_nodes = base_path.nodes + [counter_node.node_id]
                new_path = ReasoningPath(
                    path_id=f"alternative_path_{len(new_nodes)}_{int(datetime.now().timestamp())}",
                    nodes=new_nodes,
                    edges=base_path.edges.copy(),
                )
                alternative_paths.append(new_path)

        return alternative_paths

    async def _generate_different_reasoning_type_paths(
        self, graph: "DynamicReasoningGraph", base_path: ReasoningPath
    ) -> List[ReasoningPath]:
        """다양한 추론 유형 기반 경로 생성"""
        reasoning_type_paths = []

        # 다양한 추론 유형의 노드들 찾기
        inference_nodes = [
            n for n in graph.nodes.values() if n.node_type == NodeType.INFERENCE
        ]
        evidence_nodes = [
            n for n in graph.nodes.values() if n.node_type == NodeType.EVIDENCE
        ]

        # 추론 노드 기반 경로
        for inference_node in inference_nodes:
            if inference_node.node_id not in base_path.nodes:
                new_nodes = base_path.nodes + [inference_node.node_id]
                new_path = ReasoningPath(
                    path_id=f"reasoning_type_path_{len(new_nodes)}_{int(datetime.now().timestamp())}",
                    nodes=new_nodes,
                    edges=base_path.edges.copy(),
                )
                reasoning_type_paths.append(new_path)

        return reasoning_type_paths

    async def _generate_varying_complexity_paths(
        self, graph: "DynamicReasoningGraph", base_path: ReasoningPath
    ) -> List[ReasoningPath]:
        """다양한 복잡도 기반 경로 생성"""
        complexity_paths = []

        # 단순화된 경로 (중요도가 높은 노드만 포함)
        important_nodes = [n for n in graph.nodes.values() if n.importance_score > 0.7]
        important_node_ids = [n.node_id for n in important_nodes]

        simplified_nodes = [n for n in base_path.nodes if n in important_node_ids]
        if len(simplified_nodes) >= 3:
            simplified_path = ReasoningPath(
                path_id=f"simplified_path_{len(simplified_nodes)}_{int(datetime.now().timestamp())}",
                nodes=simplified_nodes,
                edges=[],  # 단순화된 경로는 엣지 제거
            )
            complexity_paths.append(simplified_path)

        # 복잡화된 경로 (더 많은 노드 포함)
        all_node_ids = list(graph.nodes.keys())
        complex_nodes = (
            base_path.nodes + [n for n in all_node_ids if n not in base_path.nodes][:3]
        )

        complex_path = ReasoningPath(
            path_id=f"complex_path_{len(complex_nodes)}_{int(datetime.now().timestamp())}",
            nodes=complex_nodes,
            edges=base_path.edges.copy(),
        )
        complexity_paths.append(complex_path)

        return complexity_paths


class ReasoningPathEvaluator:
    """추론 경로 평가 시스템"""

    def __init__(self):
        self.evaluation_criteria = self._initialize_evaluation_criteria()

    def _initialize_evaluation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """평가 기준 초기화"""
        return {
            "quality": {"weight": 0.3, "description": "경로 품질 평가"},
            "efficiency": {"weight": 0.25, "description": "경로 효율성 평가"},
            "robustness": {"weight": 0.25, "description": "경로 견고성 평가"},
            "novelty": {"weight": 0.2, "description": "경로 신규성 평가"},
        }

    async def evaluate_paths(
        self, paths: List[ReasoningPath], graph: "DynamicReasoningGraph"
    ) -> Dict[str, Any]:
        """경로들 평가"""
        logger.info(f"경로 평가 시작: {len(paths)}개 경로")

        evaluation_results = []

        for path in paths:
            # 1. 품질 평가
            quality_score = await self._evaluate_quality(path, graph)

            # 2. 효율성 평가
            efficiency_score = await self._evaluate_efficiency(path, graph)

            # 3. 견고성 평가
            robustness_score = await self._evaluate_robustness(path, graph)

            # 4. 신규성 평가
            novelty_score = await self._evaluate_novelty(path, graph)

            # 종합 점수 계산
            overall_score = (
                quality_score * self.evaluation_criteria["quality"]["weight"]
                + efficiency_score * self.evaluation_criteria["efficiency"]["weight"]
                + robustness_score * self.evaluation_criteria["robustness"]["weight"]
                + novelty_score * self.evaluation_criteria["novelty"]["weight"]
            )

            evaluation_results.append(
                {
                    "path_id": path.path_id,
                    "overall_score": overall_score,
                    "quality_score": quality_score,
                    "efficiency_score": efficiency_score,
                    "robustness_score": robustness_score,
                    "novelty_score": novelty_score,
                    "path": path,
                }
            )

        # 점수에 따라 정렬
        evaluation_results.sort(key=lambda x: x["overall_score"], reverse=True)

        return {
            "evaluation_results": evaluation_results,
            "best_path": evaluation_results[0] if evaluation_results else None,
            "average_score": (
                sum(r["overall_score"] for r in evaluation_results)
                / len(evaluation_results)
                if evaluation_results
                else 0.0
            ),
        }

    async def _evaluate_quality(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """품질 평가"""
        if not path.nodes:
            return 0.0

        # 노드 품질 (신뢰도 기반)
        node_qualities = []
        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                node_qualities.append(node.confidence)

        avg_node_quality = (
            sum(node_qualities) / len(node_qualities) if node_qualities else 0.0
        )

        # 엣지 품질 (강도 기반)
        edge_qualities = []
        for edge_id in path.edges:
            edge = graph.edges.get(edge_id)
            if edge:
                edge_qualities.append(edge.strength)

        avg_edge_quality = (
            sum(edge_qualities) / len(edge_qualities) if edge_qualities else 0.0
        )

        # 종합 품질
        overall_quality = avg_node_quality * 0.6 + avg_edge_quality * 0.4
        return overall_quality

    async def _evaluate_efficiency(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """효율성 평가"""
        if len(path.nodes) < 2:
            return 0.0

        # 경로 길이 효율성 (너무 길거나 짧으면 효율성 낮음)
        optimal_length = 5
        length_efficiency = 1.0 - abs(len(path.nodes) - optimal_length) / optimal_length
        length_efficiency = max(0.0, length_efficiency)

        # 노드 간 연결 효율성
        connection_efficiency = len(path.edges) / max(len(path.nodes) - 1, 1)

        # 종합 효율성
        overall_efficiency = length_efficiency * 0.6 + connection_efficiency * 0.4
        return overall_efficiency

    async def _evaluate_robustness(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """견고성 평가"""
        if not path.nodes:
            return 0.0

        # 노드 다양성 (다양한 유형의 노드가 포함되면 견고성 높음)
        node_types = set()
        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                node_types.add(node.node_type)

        type_diversity = len(node_types) / 10.0  # 최대 10개 유형

        # 노드 중요도 (중요한 노드가 많으면 견고성 높음)
        importance_scores = []
        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                importance_scores.append(node.importance_score)

        avg_importance = (
            sum(importance_scores) / len(importance_scores)
            if importance_scores
            else 0.0
        )

        # 종합 견고성
        overall_robustness = type_diversity * 0.5 + avg_importance * 0.5
        return overall_robustness

    async def _evaluate_novelty(
        self, path: ReasoningPath, graph: "DynamicReasoningGraph"
    ) -> float:
        """신규성 평가"""
        if not path.nodes:
            return 0.0

        # 새로운 노드 유형 포함도
        novel_node_types = {
            NodeType.HYPOTHESIS,
            NodeType.ALTERNATIVE,
            NodeType.INTEGRATION,
        }
        path_node_types = set()

        for node_id in path.nodes:
            node = graph.nodes.get(node_id)
            if node:
                path_node_types.add(node.node_type)

        novelty_score = len(path_node_types.intersection(novel_node_types)) / len(
            novel_node_types
        )

        # 경로 길이 신규성 (표준과 다른 길이)
        standard_length = 5
        length_novelty = abs(len(path.nodes) - standard_length) / standard_length
        length_novelty = min(length_novelty, 1.0)

        # 종합 신규성
        overall_novelty = novelty_score * 0.7 + length_novelty * 0.3
        return overall_novelty


async def test_reasoning_path_validator():
    """추론 경로 검증 시스템 테스트"""
    print("=== 추론 경로 검증 시스템 테스트 시작 (Phase 1-3 Week 3 Day 2) ===")

    # 테스트 그래프 생성
    graph = DynamicReasoningGraph(graph_id="test_graph")

    # 테스트 노드들 생성
    nodes = {
        "node1": DynamicReasoningNode(
            "node1", NodeType.PREMISE, "상황: 윤리적 딜레마", 0.8, "test"
        ),
        "node2": DynamicReasoningNode(
            "node2", NodeType.INFERENCE, "칸트적 분석", 0.7, "test"
        ),
        "node3": DynamicReasoningNode(
            "node3", NodeType.INFERENCE, "공리주의 분석", 0.6, "test"
        ),
        "node4": DynamicReasoningNode(
            "node4", NodeType.CONCLUSION, "최종 판단", 0.9, "test"
        ),
        "node5": DynamicReasoningNode(
            "node5", NodeType.COUNTER_ARGUMENT, "반론", 0.5, "test"
        ),
    }

    graph.nodes = nodes

    # 테스트 엣지들 생성
    edges = {
        "edge1": DynamicReasoningEdge(
            "edge1", "node1", "node2", EdgeType.SUPPORTS, 0.8, "지원"
        ),
        "edge2": DynamicReasoningEdge(
            "edge2", "node1", "node3", EdgeType.SUPPORTS, 0.7, "지원"
        ),
        "edge3": DynamicReasoningEdge(
            "edge3", "node2", "node4", EdgeType.INFERS, 0.9, "추론"
        ),
        "edge4": DynamicReasoningEdge(
            "edge4", "node3", "node4", EdgeType.INFERS, 0.8, "추론"
        ),
        "edge5": DynamicReasoningEdge(
            "edge5", "node5", "node4", EdgeType.CHALLENGES, 0.6, "도전"
        ),
    }

    graph.edges = edges

    # 테스트 경로 생성
    test_path = ReasoningPath(
        path_id="test_path_1",
        nodes=["node1", "node2", "node4"],
        edges=["edge1", "edge3"],
    )

    # 1. 경로 검증 테스트
    validator = ReasoningPathValidator()
    validation_result = await validator.validate_reasoning_path(test_path, graph)

    print(f"\n🔍 경로 검증 결과:")
    print(f"  • 유효성: {validation_result.is_valid}")
    print(f"  • 유효성 점수: {validation_result.validity_score:.2f}")
    print(f"  • 완전성 점수: {validation_result.completeness_score:.2f}")
    print(f"  • 일관성 점수: {validation_result.coherence_score:.2f}")
    print(f"  • 강도 점수: {validation_result.strength_score:.2f}")
    print(f"  • 이슈: {validation_result.issues}")
    print(f"  • 권장사항: {validation_result.recommendations}")

    # 2. 경로 최적화 테스트
    optimizer = ReasoningPathOptimizer()
    optimal_paths = await optimizer.find_optimal_paths(graph, ["node1"], ["node4"], 3)

    print(f"\n🎯 최적 경로 탐색 결과:")
    print(f"  • 발견된 최적 경로 수: {len(optimal_paths)}")
    for i, path in enumerate(optimal_paths):
        print(
            f"  • 경로 {i+1}: {path.path_id} (신뢰도: {path.confidence:.2f}, 강도: {path.strength:.2f})"
        )

    # 3. 경로 다양성 생성 테스트
    diversity_generator = ReasoningPathDiversityGenerator()
    diverse_paths = await diversity_generator.generate_diverse_paths(
        graph, test_path, 3
    )

    print(f"\n🌈 다양한 경로 생성 결과:")
    print(f"  • 생성된 다양한 경로 수: {len(diverse_paths)}")
    for i, path in enumerate(diverse_paths):
        print(f"  • 변형 경로 {i+1}: {path.path_id} (노드 수: {len(path.nodes)})")

    # 4. 경로 평가 테스트
    evaluator = ReasoningPathEvaluator()
    all_paths = [test_path] + optimal_paths + diverse_paths
    evaluation_results = await evaluator.evaluate_paths(all_paths, graph)

    print(f"\n📊 경로 평가 결과:")
    print(f"  • 평가된 경로 수: {len(evaluation_results['evaluation_results'])}")
    print(f"  • 평균 점수: {evaluation_results['average_score']:.2f}")
    if evaluation_results["best_path"]:
        print(
            f"  • 최고 점수 경로: {evaluation_results['best_path']['path_id']} (점수: {evaluation_results['best_path']['overall_score']:.2f})"
        )

    print(f"\n{'='*70}")
    print("=== 추론 경로 검증 시스템 테스트 완료 (Phase 1-3 Week 3 Day 2) ===")
    print("✅ Day 2 목표 달성: 추론 경로 검증 시스템 구현")
    print("✅ 경로 검증 시스템 구현")
    print("✅ 경로 최적화 시스템 구현")
    print("✅ 경로 다양성 생성 시스템 구현")
    print("✅ 경로 평가 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_reasoning_path_validator())
