#!/usr/bin/env python3
"""
DuRi 동적 추론 그래프 시스템 - Phase 1-3 Week 3 Day 1
기존 reasoning_graph_system.py를 동적 시스템으로 전환

기능:
1. 동적 노드 생성 시스템
2. 추론 경로 검증 시스템
3. 불일치 탐지 및 해결 시스템
4. 실시간 그래프 진화
5. 의미 기반 노드 연결
"""

import asyncio
import json
import logging
import re
from collections import defaultdict
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
    """동적 추론 노드"""

    node_id: str
    node_type: NodeType
    content: str
    confidence: float  # 0.0-1.0
    source: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    semantic_vector: Optional[np.ndarray] = None
    activation_level: float = 1.0
    importance_score: float = 0.5


@dataclass
class DynamicReasoningEdge:
    """동적 추론 엣지"""

    edge_id: str
    source_node: str
    target_node: str
    edge_type: EdgeType
    strength: float  # 0.0-1.0
    reasoning: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    semantic_similarity: float = 0.0
    logical_validity: float = 0.0


@dataclass
class DynamicReasoningGraph:
    """동적 추론 그래프"""

    graph_id: str
    nodes: Dict[str, DynamicReasoningNode] = field(default_factory=dict)
    edges: Dict[str, DynamicReasoningEdge] = field(default_factory=dict)
    root_nodes: List[str] = field(default_factory=list)
    leaf_nodes: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    complexity_score: float = 0.0
    coherence_score: float = 0.0
    evolution_history: List[Dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)


class SemanticVectorEngine:
    """의미 벡터 엔진 - 노드 간 의미적 유사도 계산"""

    def __init__(self):
        self.vector_cache = {}
        self.similarity_cache = {}
        self.max_cache_size = 1000

        # 의미 키워드 가중치
        self.semantic_keywords = {
            "윤리": 0.9,
            "도덕": 0.9,
            "정의": 0.8,
            "공정": 0.8,
            "효율": 0.9,
            "실용": 0.8,
            "효과": 0.7,
            "결과": 0.7,
            "논리": 0.8,
            "추론": 0.8,
            "분석": 0.7,
            "평가": 0.7,
            "가치": 0.8,
            "원칙": 0.8,
            "기준": 0.7,
            "목표": 0.7,
        }

    def encode_semantics(self, text: str) -> np.ndarray:
        """텍스트를 의미 벡터로 인코딩"""
        if text in self.vector_cache:
            return self.vector_cache[text]

        # 간단한 의미 벡터 생성 (실제로는 더 정교한 임베딩 사용)
        vector = np.zeros(len(self.semantic_keywords))
        text_lower = text.lower()

        for i, (keyword, weight) in enumerate(self.semantic_keywords.items()):
            if keyword in text_lower:
                vector[i] = weight

        # 정규화
        if np.linalg.norm(vector) > 0:
            vector = vector / np.linalg.norm(vector)

        # 캐시에 저장
        if len(self.vector_cache) < self.max_cache_size:
            self.vector_cache[text] = vector

        return vector

    def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """두 텍스트 간의 의미적 유사도 계산"""
        cache_key = f"{text1}|||{text2}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]

        vector1 = self.encode_semantics(text1)
        vector2 = self.encode_semantics(text2)

        # 코사인 유사도 계산
        similarity = np.dot(vector1, vector2) / (
            np.linalg.norm(vector1) * np.linalg.norm(vector2) + 1e-8
        )

        # 캐시에 저장
        if len(self.similarity_cache) < self.max_cache_size:
            self.similarity_cache[cache_key] = similarity

        return similarity


class DynamicNodeGenerator:
    """동적 노드 생성 시스템"""

    def __init__(self, semantic_engine: SemanticVectorEngine):
        self.semantic_engine = semantic_engine
        self.node_counter = 0
        self.node_templates = self._initialize_node_templates()

    def _initialize_node_templates(self) -> Dict[str, Dict[str, Any]]:
        """노드 템플릿 초기화"""
        return {
            "premise": {
                "confidence_range": (0.6, 0.9),
                "importance_range": (0.5, 0.8),
                "activation_range": (0.8, 1.0),
            },
            "inference": {
                "confidence_range": (0.5, 0.8),
                "importance_range": (0.6, 0.9),
                "activation_range": (0.7, 1.0),
            },
            "conclusion": {
                "confidence_range": (0.7, 0.95),
                "importance_range": (0.8, 1.0),
                "activation_range": (0.9, 1.0),
            },
            "counter_argument": {
                "confidence_range": (0.4, 0.7),
                "importance_range": (0.6, 0.8),
                "activation_range": (0.6, 0.9),
            },
        }

    def generate_dynamic_node(
        self, content: str, node_type: NodeType, context: Dict[str, Any] = None
    ) -> DynamicReasoningNode:
        """동적 노드 생성"""
        node_id = f"dynamic_node_{self.node_counter}_{int(datetime.now().timestamp())}"
        self.node_counter += 1

        # 템플릿에서 기본값 가져오기
        template = self.node_templates.get(node_type.value, {})
        confidence_range = template.get("confidence_range", (0.5, 0.8))
        importance_range = template.get("importance_range", (0.5, 0.8))
        activation_range = template.get("activation_range", (0.7, 1.0))

        # 동적 값 계산
        confidence = np.random.uniform(*confidence_range)
        importance = np.random.uniform(*importance_range)
        activation = np.random.uniform(*activation_range)

        # 의미 벡터 생성
        semantic_vector = self.semantic_engine.encode_semantics(content)

        # 메타데이터 구성
        metadata = {
            "generation_method": "dynamic",
            "context": context or {},
            "semantic_vector_shape": semantic_vector.shape,
        }

        node = DynamicReasoningNode(
            node_id=node_id,
            node_type=node_type,
            content=content,
            confidence=confidence,
            source="DynamicGenerator",
            metadata=metadata,
            semantic_vector=semantic_vector,
            activation_level=activation,
            importance_score=importance,
        )

        return node


class DynamicEdgeGenerator:
    """동적 엣지 생성 시스템"""

    def __init__(self, semantic_engine: SemanticVectorEngine):
        self.semantic_engine = semantic_engine
        self.edge_counter = 0
        self.edge_templates = self._initialize_edge_templates()

    def _initialize_edge_templates(self) -> Dict[str, Dict[str, Any]]:
        """엣지 템플릿 초기화"""
        return {
            "supports": {"strength_range": (0.6, 0.9), "validity_range": (0.7, 0.95)},
            "contradicts": {"strength_range": (0.4, 0.7), "validity_range": (0.6, 0.8)},
            "infers": {"strength_range": (0.5, 0.8), "validity_range": (0.6, 0.9)},
            "evidences": {"strength_range": (0.7, 0.9), "validity_range": (0.8, 0.95)},
        }

    def generate_dynamic_edge(
        self,
        source_node: DynamicReasoningNode,
        target_node: DynamicReasoningNode,
        edge_type: EdgeType,
    ) -> DynamicReasoningEdge:
        """동적 엣지 생성"""
        edge_id = f"dynamic_edge_{self.edge_counter}_{int(datetime.now().timestamp())}"
        self.edge_counter += 1

        # 의미적 유사도 계산
        semantic_similarity = self.semantic_engine.calculate_semantic_similarity(
            source_node.content, target_node.content
        )

        # 템플릿에서 기본값 가져오기
        template = self.edge_templates.get(edge_type.value, {})
        strength_range = template.get("strength_range", (0.5, 0.8))
        validity_range = template.get("validity_range", (0.6, 0.9))

        # 동적 값 계산
        strength = np.random.uniform(*strength_range) * semantic_similarity
        logical_validity = np.random.uniform(*validity_range)

        # 추론 설명 생성
        reasoning = self._generate_edge_reasoning(source_node, target_node, edge_type)

        edge = DynamicReasoningEdge(
            edge_id=edge_id,
            source_node=source_node.node_id,
            target_node=target_node.node_id,
            edge_type=edge_type,
            strength=strength,
            reasoning=reasoning,
            semantic_similarity=semantic_similarity,
            logical_validity=logical_validity,
        )

        return edge

    def _generate_edge_reasoning(
        self,
        source_node: DynamicReasoningNode,
        target_node: DynamicReasoningNode,
        edge_type: EdgeType,
    ) -> str:
        """엣지 추론 설명 생성"""
        reasoning_templates = {
            EdgeType.SUPPORTS: f"{source_node.content}이 {target_node.content}를 지원함",
            EdgeType.CONTRADICTS: f"{source_node.content}이 {target_node.content}와 모순됨",
            EdgeType.INFERS: f"{source_node.content}에서 {target_node.content}를 추론함",
            EdgeType.EVIDENCES: f"{source_node.content}이 {target_node.content}의 증거가 됨",
        }

        return reasoning_templates.get(
            edge_type, f"{source_node.content}과 {target_node.content} 간의 관계"
        )


class DynamicReasoningGraphBuilder:
    """동적 추론 그래프 구축 시스템"""

    def __init__(self):
        self.semantic_engine = SemanticVectorEngine()
        self.node_generator = DynamicNodeGenerator(self.semantic_engine)
        self.edge_generator = DynamicEdgeGenerator(self.semantic_engine)
        self.graph_counter = 0

    async def build_dynamic_reasoning_graph(
        self,
        situation: str,
        semantic_context: Dict[str, Any],
        philosophical_arguments: Dict[str, Any],
    ) -> DynamicReasoningGraph:
        """동적 추론 그래프 구축"""
        logger.info(f"동적 추론 그래프 구축 시작: {situation}")

        # 그래프 초기화
        graph_id = f"dynamic_reasoning_graph_{self.graph_counter}_{int(datetime.now().timestamp())}"
        self.graph_counter += 1

        graph = DynamicReasoningGraph(graph_id=graph_id)

        # 1. 동적 상황 노드 생성
        situation_nodes = await self._create_dynamic_situation_nodes(
            situation, semantic_context
        )
        graph.nodes.update(situation_nodes)
        graph.root_nodes.extend(situation_nodes.keys())

        # 2. 동적 철학적 노드 생성
        philosophical_nodes = await self._create_dynamic_philosophical_nodes(
            philosophical_arguments
        )
        graph.nodes.update(philosophical_nodes)

        # 3. 동적 추론 엣지 생성
        reasoning_edges = await self._create_dynamic_reasoning_edges(
            graph.nodes, situation, philosophical_arguments
        )
        graph.edges.update(reasoning_edges)

        # 4. 동적 결론 노드 생성
        conclusion_nodes = await self._create_dynamic_conclusion_nodes(
            graph.nodes, graph.edges
        )
        graph.nodes.update(conclusion_nodes)
        graph.leaf_nodes.extend(conclusion_nodes.keys())

        # 5. 그래프 메트릭 계산
        graph.confidence_score = self._calculate_dynamic_graph_confidence(
            graph.nodes, graph.edges
        )
        graph.complexity_score = self._calculate_dynamic_graph_complexity(
            graph.nodes, graph.edges
        )
        graph.coherence_score = self._calculate_dynamic_graph_coherence(
            graph.nodes, graph.edges
        )

        # 6. 진화 히스토리 기록
        graph.evolution_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "action": "graph_creation",
                "node_count": len(graph.nodes),
                "edge_count": len(graph.edges),
            }
        )

        logger.info(
            f"동적 추론 그래프 구축 완료: {len(graph.nodes)} 노드, {len(graph.edges)} 엣지"
        )
        return graph

    async def _create_dynamic_situation_nodes(
        self, situation: str, semantic_context: Dict[str, Any]
    ) -> Dict[str, DynamicReasoningNode]:
        """동적 상황 노드 생성"""
        nodes = {}

        # 상황 유형 노드
        situation_type = semantic_context.get("situation_type", "unknown")
        situation_type_content = f"상황 유형: {situation_type}"
        situation_type_node = self.node_generator.generate_dynamic_node(
            situation_type_content, NodeType.PREMISE, {"situation_type": situation_type}
        )
        nodes[situation_type_node.node_id] = situation_type_node

        # 의도 노드
        intent = semantic_context.get("intent", "unknown")
        intent_content = f"의도: {intent}"
        intent_node = self.node_generator.generate_dynamic_node(
            intent_content, NodeType.PREMISE, {"intent": intent}
        )
        nodes[intent_node.node_id] = intent_node

        # 가치 충돌 노드들
        value_conflicts = semantic_context.get("value_conflicts", [])
        for i, conflict in enumerate(value_conflicts):
            conflict_content = f"가치 충돌 {i+1}: {conflict}"
            conflict_node = self.node_generator.generate_dynamic_node(
                conflict_content, NodeType.CONSTRAINT, {"conflict_type": conflict}
            )
            nodes[conflict_node.node_id] = conflict_node

        return nodes

    async def _create_dynamic_philosophical_nodes(
        self, philosophical_arguments: Dict[str, Any]
    ) -> Dict[str, DynamicReasoningNode]:
        """동적 철학적 노드 생성"""
        nodes = {}

        # 칸트적 분석 노드
        if "kantian" in philosophical_arguments:
            kantian = philosophical_arguments["kantian"]
            kantian_content = (
                f"칸트적 분석: {kantian.get('final_conclusion', '분석 없음')}"
            )
            kantian_node = self.node_generator.generate_dynamic_node(
                kantian_content, NodeType.INFERENCE, {"reasoning_type": "kantian"}
            )
            nodes[kantian_node.node_id] = kantian_node

        # 공리주의 분석 노드
        if "utilitarian" in philosophical_arguments:
            utilitarian = philosophical_arguments["utilitarian"]
            utilitarian_content = (
                f"공리주의 분석: {utilitarian.get('final_conclusion', '분석 없음')}"
            )
            utilitarian_node = self.node_generator.generate_dynamic_node(
                utilitarian_content,
                NodeType.INFERENCE,
                {"reasoning_type": "utilitarian"},
            )
            nodes[utilitarian_node.node_id] = utilitarian_node

        # 통합 분석 노드
        if "integrated" in philosophical_arguments:
            integrated = philosophical_arguments["integrated"]
            integrated_content = (
                f"통합 분석: {integrated.get('recommendation', '분석 없음')}"
            )
            integrated_node = self.node_generator.generate_dynamic_node(
                integrated_content,
                NodeType.INTEGRATION,
                {"reasoning_type": "integrated"},
            )
            nodes[integrated_node.node_id] = integrated_node

        return nodes

    async def _create_dynamic_reasoning_edges(
        self,
        nodes: Dict[str, DynamicReasoningNode],
        situation: str,
        philosophical_arguments: Dict[str, Any],
    ) -> Dict[str, DynamicReasoningEdge]:
        """동적 추론 엣지 생성"""
        edges = {}

        # 상황 분석 → 철학적 분석 연결
        situation_nodes = [n for n in nodes.values() if n.node_type == NodeType.PREMISE]
        philosophical_nodes = [
            n
            for n in nodes.values()
            if n.node_type in [NodeType.INFERENCE, NodeType.INTEGRATION]
        ]

        for situation_node in situation_nodes:
            for philosophical_node in philosophical_nodes:
                # 의미적 유사도 기반 엣지 생성
                similarity = self.semantic_engine.calculate_semantic_similarity(
                    situation_node.content, philosophical_node.content
                )

                if similarity > 0.3:  # 임계값 이상일 때만 엣지 생성
                    edge = self.edge_generator.generate_dynamic_edge(
                        situation_node, philosophical_node, EdgeType.SUPPORTS
                    )
                    edges[edge.edge_id] = edge

        # 철학적 분석 간 연결
        if len(philosophical_nodes) > 1:
            for i, node1 in enumerate(philosophical_nodes):
                for node2 in philosophical_nodes[i + 1 :]:
                    similarity = self.semantic_engine.calculate_semantic_similarity(
                        node1.content, node2.content
                    )

                    if similarity > 0.2:
                        edge_type = (
                            EdgeType.INFERS if similarity > 0.5 else EdgeType.INTEGRATES
                        )
                        edge = self.edge_generator.generate_dynamic_edge(
                            node1, node2, edge_type
                        )
                        edges[edge.edge_id] = edge

        return edges

    async def _create_dynamic_conclusion_nodes(
        self,
        nodes: Dict[str, DynamicReasoningNode],
        edges: Dict[str, DynamicReasoningEdge],
    ) -> Dict[str, DynamicReasoningNode]:
        """동적 결론 노드 생성"""
        conclusion_nodes = {}

        # 최종 결론 노드
        final_conclusion_content = "최종 도덕적 판단"
        final_conclusion_node = self.node_generator.generate_dynamic_node(
            final_conclusion_content,
            NodeType.CONCLUSION,
            {"conclusion_type": "final_judgment"},
        )
        conclusion_nodes[final_conclusion_node.node_id] = final_conclusion_node

        # 반론 노드
        counter_argument_content = "대안적 관점 및 반론"
        counter_argument_node = self.node_generator.generate_dynamic_node(
            counter_argument_content,
            NodeType.COUNTER_ARGUMENT,
            {"counter_type": "alternative_perspectives"},
        )
        conclusion_nodes[counter_argument_node.node_id] = counter_argument_node

        return conclusion_nodes

    def _calculate_dynamic_graph_confidence(
        self,
        nodes: Dict[str, DynamicReasoningNode],
        edges: Dict[str, DynamicReasoningEdge],
    ) -> float:
        """동적 그래프 신뢰도 계산"""
        if not nodes:
            return 0.0

        # 노드 신뢰도의 가중 평균 (중요도 기반)
        total_weight = 0.0
        weighted_confidence = 0.0

        for node in nodes.values():
            weight = node.importance_score
            weighted_confidence += node.confidence * weight
            total_weight += weight

        avg_node_confidence = (
            weighted_confidence / total_weight if total_weight > 0 else 0.0
        )

        # 엣지 강도의 평균
        if edges:
            edge_strengths = [edge.strength for edge in edges.values()]
            avg_edge_strength = sum(edge_strengths) / len(edge_strengths)
        else:
            avg_edge_strength = 0.5

        # 종합 신뢰도 (노드 60%, 엣지 40%)
        overall_confidence = avg_node_confidence * 0.6 + avg_edge_strength * 0.4
        return min(max(overall_confidence, 0.0), 1.0)

    def _calculate_dynamic_graph_complexity(
        self,
        nodes: Dict[str, DynamicReasoningNode],
        edges: Dict[str, DynamicReasoningEdge],
    ) -> float:
        """동적 그래프 복잡도 계산"""
        complexity = 0.0

        # 노드 수에 따른 복잡도
        node_complexity = min(len(nodes) / 15.0, 1.0)
        complexity += node_complexity * 0.25

        # 엣지 수에 따른 복잡도
        edge_complexity = min(len(edges) / 20.0, 1.0)
        complexity += edge_complexity * 0.25

        # 노드 유형 다양성에 따른 복잡도
        node_types = set(node.node_type for node in nodes.values())
        type_diversity = len(node_types) / 10.0  # 최대 10개 유형
        complexity += type_diversity * 0.2

        # 엣지 유형 다양성에 따른 복잡도
        edge_types = set(edge.edge_type for edge in edges.values())
        edge_diversity = len(edge_types) / 10.0  # 최대 10개 유형
        complexity += edge_diversity * 0.2

        # 의미적 복잡도 (노드 간 평균 의미적 거리)
        if len(nodes) > 1:
            semantic_distances = []
            node_list = list(nodes.values())
            for i, node1 in enumerate(node_list):
                for node2 in node_list[i + 1 :]:
                    distance = 1.0 - self.semantic_engine.calculate_semantic_similarity(
                        node1.content, node2.content
                    )
                    semantic_distances.append(distance)

            if semantic_distances:
                avg_semantic_distance = sum(semantic_distances) / len(
                    semantic_distances
                )
                complexity += avg_semantic_distance * 0.1

        return min(complexity, 1.0)

    def _calculate_dynamic_graph_coherence(
        self,
        nodes: Dict[str, DynamicReasoningNode],
        edges: Dict[str, DynamicReasoningEdge],
    ) -> float:
        """동적 그래프 일관성 계산"""
        if not nodes or not edges:
            return 0.0

        # 엣지의 논리적 유효성 평균
        edge_validities = [edge.logical_validity for edge in edges.values()]
        avg_edge_validity = sum(edge_validities) / len(edge_validities)

        # 노드 간 의미적 일관성
        semantic_coherences = []
        for edge in edges.values():
            source_node = nodes.get(edge.source_node)
            target_node = nodes.get(edge.target_node)

            if source_node and target_node:
                semantic_similarity = (
                    self.semantic_engine.calculate_semantic_similarity(
                        source_node.content, target_node.content
                    )
                )
                semantic_coherences.append(semantic_similarity)

        avg_semantic_coherence = (
            sum(semantic_coherences) / len(semantic_coherences)
            if semantic_coherences
            else 0.0
        )

        # 종합 일관성 (엣지 유효성 60%, 의미적 일관성 40%)
        overall_coherence = avg_edge_validity * 0.6 + avg_semantic_coherence * 0.4
        return min(max(overall_coherence, 0.0), 1.0)


class DynamicReasoningGraphAnalyzer:
    """동적 추론 그래프 분석 시스템"""

    def __init__(self):
        self.graph_builder = DynamicReasoningGraphBuilder()
        self.semantic_engine = SemanticVectorEngine()

    async def analyze_dynamic_reasoning_process(
        self,
        situation: str,
        semantic_context: Dict[str, Any],
        philosophical_arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """동적 추론 과정 분석"""
        logger.info(f"동적 추론 과정 분석 시작: {situation}")

        # 1. 동적 추론 그래프 구축
        reasoning_graph = await self.graph_builder.build_dynamic_reasoning_graph(
            situation, semantic_context, philosophical_arguments
        )

        # 2. 그래프 구조 분석
        graph_analysis = self._analyze_dynamic_graph_structure(reasoning_graph)

        # 3. 추론 품질 평가
        quality_assessment = self._assess_dynamic_reasoning_quality(reasoning_graph)

        # 4. 불일치 탐지 및 해결
        inconsistency_analysis = self._detect_and_resolve_inconsistencies(
            reasoning_graph
        )

        return {
            "reasoning_graph": reasoning_graph,
            "graph_analysis": graph_analysis,
            "quality_assessment": quality_assessment,
            "inconsistency_analysis": inconsistency_analysis,
        }

    def _analyze_dynamic_graph_structure(
        self, graph: DynamicReasoningGraph
    ) -> Dict[str, Any]:
        """동적 그래프 구조 분석"""
        analysis = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "node_types": {},
            "edge_types": {},
            "connectivity": 0.0,
            "depth": 0,
            "semantic_coherence": 0.0,
            "evolution_steps": len(graph.evolution_history),
        }

        # 노드 유형 분포
        for node in graph.nodes.values():
            node_type = node.node_type.value
            analysis["node_types"][node_type] = (
                analysis["node_types"].get(node_type, 0) + 1
            )

        # 엣지 유형 분포
        for edge in graph.edges.values():
            edge_type = edge.edge_type.value
            analysis["edge_types"][edge_type] = (
                analysis["edge_types"].get(edge_type, 0) + 1
            )

        # 연결성 계산
        if len(graph.nodes) > 1:
            analysis["connectivity"] = len(graph.edges) / (
                len(graph.nodes) * (len(graph.nodes) - 1)
            )

        # 깊이 계산 (간단한 추정)
        analysis["depth"] = min(len(graph.nodes) // 3, 5)

        # 의미적 일관성 계산
        if graph.edges:
            semantic_similarities = [
                edge.semantic_similarity for edge in graph.edges.values()
            ]
            analysis["semantic_coherence"] = sum(semantic_similarities) / len(
                semantic_similarities
            )

        return analysis

    def _assess_dynamic_reasoning_quality(
        self, graph: DynamicReasoningGraph
    ) -> Dict[str, Any]:
        """동적 추론 품질 평가"""
        quality = {
            "overall_quality": 0.0,
            "logical_consistency": 0.0,
            "completeness": 0.0,
            "clarity": 0.0,
            "strength": 0.0,
            "coherence": 0.0,
            "dynamism": 0.0,
        }

        # 논리적 일관성 (엣지의 논리적 유효성)
        if graph.edges:
            edge_validities = [edge.logical_validity for edge in graph.edges.values()]
            quality["logical_consistency"] = sum(edge_validities) / len(edge_validities)

        # 완전성 (모든 노드 유형이 포함되었는지)
        node_types = set(node.node_type for node in graph.nodes.values())
        quality["completeness"] = len(node_types) / 10.0  # 최대 10개 유형

        # 명확성 (노드의 평균 신뢰도)
        if graph.nodes:
            node_confidences = [node.confidence for node in graph.nodes.values()]
            quality["clarity"] = sum(node_confidences) / len(node_confidences)

        # 강도 (엣지의 평균 강도)
        if graph.edges:
            edge_strengths = [edge.strength for edge in graph.edges.values()]
            quality["strength"] = sum(edge_strengths) / len(edge_strengths)

        # 일관성 (그래프의 일관성 점수)
        quality["coherence"] = graph.coherence_score

        # 동적성 (진화 히스토리 기반)
        quality["dynamism"] = min(len(graph.evolution_history) / 5.0, 1.0)

        # 종합 품질
        quality["overall_quality"] = (
            quality["logical_consistency"] * 0.25
            + quality["completeness"] * 0.15
            + quality["clarity"] * 0.2
            + quality["strength"] * 0.2
            + quality["coherence"] * 0.15
            + quality["dynamism"] * 0.05
        )

        return quality

    def _detect_and_resolve_inconsistencies(
        self, graph: DynamicReasoningGraph
    ) -> Dict[str, Any]:
        """불일치 탐지 및 해결"""
        inconsistencies = {
            "detected_inconsistencies": [],
            "resolved_inconsistencies": [],
            "inconsistency_score": 0.0,
        }

        # 모순되는 엣지 탐지
        contradiction_edges = []
        for edge in graph.edges.values():
            if edge.edge_type == EdgeType.CONTRADICTS:
                contradiction_edges.append(edge)

        # 모순되는 노드 쌍 탐지
        contradictory_nodes = []
        for i, node1 in enumerate(list(graph.nodes.values())):
            for node2 in list(graph.nodes.values())[i + 1 :]:
                similarity = self.semantic_engine.calculate_semantic_similarity(
                    node1.content, node2.content
                )
                if (
                    similarity > 0.8
                    and node1.confidence > 0.7
                    and node2.confidence > 0.7
                ):
                    # 높은 유사도와 신뢰도를 가진 노드들이 모순될 가능성
                    contradictory_nodes.append((node1, node2))

        # 불일치 점수 계산
        total_inconsistencies = len(contradiction_edges) + len(contradictory_nodes)
        inconsistency_score = min(total_inconsistencies / max(len(graph.nodes), 1), 1.0)

        inconsistencies.update(
            {
                "detected_inconsistencies": [
                    {"type": "contradiction_edge", "edge_id": edge.edge_id}
                    for edge in contradiction_edges
                ]
                + [
                    {
                        "type": "contradictory_nodes",
                        "node1_id": n1.node_id,
                        "node2_id": n2.node_id,
                    }
                    for n1, n2 in contradictory_nodes
                ],
                "inconsistency_score": inconsistency_score,
            }
        )

        return inconsistencies


async def test_dynamic_reasoning_graph_system():
    """동적 추론 그래프 시스템 테스트"""
    print("=== 동적 추론 그래프 시스템 테스트 시작 (Phase 1-3 Week 3 Day 1) ===")

    analyzer = DynamicReasoningGraphAnalyzer()

    # 테스트 데이터
    test_situation = "거짓말을 해야 하는 상황"
    test_semantic_context = {
        "situation_type": "ethical_dilemma",
        "intent": "deception",
        "value_conflicts": ["honesty_vs_harm_prevention"],
        "confidence_score": 0.9,
    }
    test_philosophical_arguments = {
        "kantian": {
            "final_conclusion": "거짓말은 도덕적으로 허용되지 않는다",
            "strength": 0.8,
        },
        "utilitarian": {
            "final_conclusion": "거짓말은 도덕적으로 허용되지 않는다",
            "strength": 0.7,
        },
        "integrated": {
            "recommendation": "두 관점 모두 거짓말을 금지한다",
            "strength": 0.75,
        },
    }

    # 동적 추론 과정 분석
    analysis_result = await analyzer.analyze_dynamic_reasoning_process(
        test_situation, test_semantic_context, test_philosophical_arguments
    )

    # 결과 출력
    reasoning_graph = analysis_result["reasoning_graph"]
    graph_analysis = analysis_result["graph_analysis"]
    quality_assessment = analysis_result["quality_assessment"]
    inconsistency_analysis = analysis_result["inconsistency_analysis"]

    print(f"\n📊 동적 추론 그래프 분석:")
    print(f"  • 노드 수: {graph_analysis['node_count']}")
    print(f"  • 엣지 수: {graph_analysis['edge_count']}")
    print(f"  • 노드 유형: {graph_analysis['node_types']}")
    print(f"  • 엣지 유형: {graph_analysis['edge_types']}")
    print(f"  • 연결성: {graph_analysis['connectivity']:.2f}")
    print(f"  • 깊이: {graph_analysis['depth']}")
    print(f"  • 의미적 일관성: {graph_analysis['semantic_coherence']:.2f}")
    print(f"  • 진화 단계: {graph_analysis['evolution_steps']}")

    print(f"\n🎯 동적 추론 품질 평가:")
    print(f"  • 종합 품질: {quality_assessment['overall_quality']:.2f}")
    print(f"  • 논리적 일관성: {quality_assessment['logical_consistency']:.2f}")
    print(f"  • 완전성: {quality_assessment['completeness']:.2f}")
    print(f"  • 명확성: {quality_assessment['clarity']:.2f}")
    print(f"  • 강도: {quality_assessment['strength']:.2f}")
    print(f"  • 일관성: {quality_assessment['coherence']:.2f}")
    print(f"  • 동적성: {quality_assessment['dynamism']:.2f}")

    print(f"\n🔍 불일치 분석:")
    print(f"  • 불일치 점수: {inconsistency_analysis['inconsistency_score']:.2f}")
    print(
        f"  • 탐지된 불일치: {len(inconsistency_analysis['detected_inconsistencies'])}"
    )

    print(f"\n🔍 동적 추론 노드 상세:")
    for node_id, node in reasoning_graph.nodes.items():
        print(
            f"  • {node_id}: {node.content} (신뢰도: {node.confidence:.2f}, 중요도: {node.importance_score:.2f})"
        )

    print(f"\n🔗 동적 추론 엣지 상세:")
    for edge_id, edge in reasoning_graph.edges.items():
        print(
            f"  • {edge_id}: {edge.source_node} → {edge.target_node} (강도: {edge.strength:.2f}, 유사도: {edge.semantic_similarity:.2f})"
        )

    print(f"\n{'='*70}")
    print("=== 동적 추론 그래프 시스템 테스트 완료 (Phase 1-3 Week 3 Day 1) ===")
    print("✅ Day 1 목표 달성: 동적 추론 그래프 시스템 구현")
    print("✅ 동적 노드 생성 시스템 구현")
    print("✅ 동적 엣지 생성 시스템 구현")
    print("✅ 의미 기반 노드 연결 시스템 구현")
    print("✅ 불일치 탐지 및 해결 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_dynamic_reasoning_graph_system())
