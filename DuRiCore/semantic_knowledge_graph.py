#!/usr/bin/env python3
"""
DuRiCore Phase 6.2.6 - 시맨틱 지식 연결망 시스템
개념 노드 + 추론 엣지를 기반으로 한 knowledge graph 구조
"""

import asyncio
import json
import logging
import math
import random
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ConceptType(Enum):
    """개념 유형"""

    ENTITY = "entity"  # 실체 (사람, 물체, 장소)
    ACTION = "action"  # 행동 (동작, 활동)
    PROPERTY = "property"  # 속성 (특징, 성질)
    RELATION = "relation"  # 관계 (연결, 상호작용)
    ABSTRACT = "abstract"  # 추상 (개념, 아이디어)


class InferenceType(Enum):
    """추론 유형"""

    IS_A = "is_a"  # 상하 관계
    PART_OF = "part_of"  # 부분-전체 관계
    HAS_PROPERTY = "has_property"  # 속성 관계
    CAUSES = "causes"  # 인과 관계
    SIMILAR_TO = "similar_to"  # 유사 관계
    OPPOSITE_OF = "opposite_of"  # 반대 관계
    ASSOCIATED_WITH = "associated_with"  # 연관 관계


class ConfidenceLevel(Enum):
    """신뢰도 수준"""

    CERTAIN = "certain"  # 확실함 (1.0)
    LIKELY = "likely"  # 가능함 (0.8)
    POSSIBLE = "possible"  # 가능성 있음 (0.6)
    UNCERTAIN = "uncertain"  # 불확실함 (0.4)
    DOUBTFUL = "doubtful"  # 의심스러움 (0.2)


@dataclass
class ConceptNode:
    """개념 노드"""

    id: str
    name: str
    concept_type: ConceptType
    description: str
    properties: Dict[str, Any]
    confidence: float
    created_at: datetime
    last_updated: datetime
    frequency: int = 1
    centrality: float = 0.0
    semantic_vector: List[float] = None

    def __post_init__(self):
        if self.semantic_vector is None:
            self.semantic_vector = [random.random() for _ in range(100)]


@dataclass
class InferenceEdge:
    """추론 엣지"""

    id: str
    source_id: str
    target_id: str
    inference_type: InferenceType
    confidence: float
    evidence: List[str]
    created_at: datetime
    last_used: datetime
    strength: float = 1.0

    def __post_init__(self):
        if self.last_used is None:
            self.last_used = self.created_at


@dataclass
class SemanticPath:
    """시맨틱 경로"""

    path_id: str
    source_concept: str
    target_concept: str
    path_nodes: List[str]
    path_edges: List[str]
    total_confidence: float
    path_length: int
    inference_chain: List[InferenceType]


@dataclass
class KnowledgeGraphResult:
    """지식 그래프 결과"""

    concept_count: int
    edge_count: int
    average_confidence: float
    graph_density: float
    connected_components: int
    created_at: str
    success: bool = True


class SemanticKnowledgeGraph:
    """시맨틱 지식 연결망 시스템"""

    def __init__(self):
        """초기화"""
        self.concepts = {}  # concept_id -> ConceptNode
        self.edges = {}  # edge_id -> InferenceEdge
        self.adjacency_list = defaultdict(set)  # concept_id -> set of connected concept_ids
        self.reverse_adjacency = defaultdict(set)  # concept_id -> set of concepts that point to it

        # 시맨틱 분석기들
        self.concept_analyzer = ConceptAnalyzer(self)
        self.inference_engine = InferenceEngine(self)
        self.path_finder = PathFinder(self)
        self.semantic_optimizer = SemanticOptimizer(self)

        # 그래프 매개변수
        self.graph_parameters = {
            "max_concepts": 10000,
            "max_edges": 50000,
            "min_confidence": 0.3,
            "max_path_length": 5,
            "similarity_threshold": 0.7,
        }

        logger.info("시맨틱 지식 연결망 시스템 초기화 완료")

    async def add_concept(
        self,
        name: str,
        concept_type: ConceptType,
        description: str = "",
        properties: Dict[str, Any] = None,
        confidence: float = 0.8,
    ) -> str:
        """개념 노드 추가"""
        try:
            # 기존 개념 확인
            existing_concept = self._find_concept_by_name(name)
            if existing_concept:
                # 기존 개념 업데이트
                existing_concept.frequency += 1
                existing_concept.last_updated = datetime.now()
                existing_concept.confidence = max(existing_concept.confidence, confidence)
                if properties:
                    existing_concept.properties.update(properties)
                logger.info(f"기존 개념 업데이트: {name}")
                return existing_concept.id

            # 새 개념 생성
            concept_id = f"concept_{len(self.concepts) + 1}_{int(time.time())}"
            concept = ConceptNode(
                id=concept_id,
                name=name,
                concept_type=concept_type,
                description=description,
                properties=properties or {},
                confidence=confidence,
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )

            self.concepts[concept_id] = concept
            logger.info(f"새 개념 추가: {name} (ID: {concept_id})")
            return concept_id

        except Exception as e:
            logger.error(f"개념 추가 실패: {e}")
            return None

    async def add_inference(
        self,
        source_name: str,
        target_name: str,
        inference_type: InferenceType,
        confidence: float = 0.7,
        evidence: List[str] = None,
    ) -> str:
        """추론 엣지 추가"""
        try:
            # 소스와 타겟 개념 확인/생성
            source_id = await self._ensure_concept_exists(source_name)
            target_id = await self._ensure_concept_exists(target_name)

            if not source_id or not target_id:
                logger.error(f"개념을 찾을 수 없음: {source_name} 또는 {target_name}")
                return None

            # 기존 엣지 확인
            existing_edge = self._find_edge(source_id, target_id, inference_type)
            if existing_edge:
                # 기존 엣지 업데이트
                existing_edge.confidence = max(existing_edge.confidence, confidence)
                existing_edge.last_used = datetime.now()
                existing_edge.strength += 0.1
                if evidence:
                    existing_edge.evidence.extend(evidence)
                logger.info(f"기존 추론 업데이트: {source_name} -> {target_name}")
                return existing_edge.id

            # 새 엣지 생성
            edge_id = f"edge_{len(self.edges) + 1}_{int(time.time())}"
            edge = InferenceEdge(
                id=edge_id,
                source_id=source_id,
                target_id=target_id,
                inference_type=inference_type,
                confidence=confidence,
                evidence=evidence or [],
                created_at=datetime.now(),
            )

            self.edges[edge_id] = edge
            self.adjacency_list[source_id].add(target_id)
            self.reverse_adjacency[target_id].add(source_id)

            logger.info(f"새 추론 추가: {source_name} -> {target_name} ({inference_type.value})")
            return edge_id

        except Exception as e:
            logger.error(f"추론 추가 실패: {e}")
            return None

    async def find_semantic_path(
        self, source_name: str, target_name: str, max_length: int = 5
    ) -> Optional[SemanticPath]:
        """시맨틱 경로 찾기"""
        try:
            source_concept = self._find_concept_by_name(source_name)
            target_concept = self._find_concept_by_name(target_name)

            if not source_concept or not target_concept:
                logger.warning(f"개념을 찾을 수 없음: {source_name} 또는 {target_name}")
                return None

            path_result = await self.path_finder.find_path(
                source_concept.id, target_concept.id, max_length
            )

            return path_result

        except Exception as e:
            logger.error(f"시맨틱 경로 찾기 실패: {e}")
            return None

    async def infer_new_knowledge(
        self, concept_name: str, inference_type: InferenceType = None
    ) -> List[Dict[str, Any]]:
        """새로운 지식 추론"""
        try:
            concept = self._find_concept_by_name(concept_name)
            if not concept:
                logger.warning(f"개념을 찾을 수 없음: {concept_name}")
                return []

            inference_results = await self.inference_engine.infer_knowledge(
                concept.id, inference_type
            )

            return inference_results

        except Exception as e:
            logger.error(f"지식 추론 실패: {e}")
            return []

    async def analyze_semantic_similarity(self, concept1_name: str, concept2_name: str) -> float:
        """시맨틱 유사도 분석"""
        try:
            concept1 = self._find_concept_by_name(concept1_name)
            concept2 = self._find_concept_by_name(concept2_name)

            if not concept1 or not concept2:
                return 0.0

            similarity = self._calculate_semantic_similarity(concept1, concept2)
            return similarity

        except Exception as e:
            logger.error(f"시맨틱 유사도 분석 실패: {e}")
            return 0.0

    async def get_knowledge_graph_status(self) -> KnowledgeGraphResult:
        """지식 그래프 상태 반환"""
        try:
            concept_count = len(self.concepts)
            edge_count = len(self.edges)

            # 평균 신뢰도 계산
            total_confidence = sum(concept.confidence for concept in self.concepts.values())
            avg_confidence = total_confidence / concept_count if concept_count > 0 else 0.0

            # 그래프 밀도 계산
            max_edges = concept_count * (concept_count - 1) if concept_count > 1 else 0
            graph_density = edge_count / max_edges if max_edges > 0 else 0.0

            # 연결 요소 수 계산
            connected_components = await self._count_connected_components()

            return KnowledgeGraphResult(
                concept_count=concept_count,
                edge_count=edge_count,
                average_confidence=avg_confidence,
                graph_density=graph_density,
                connected_components=connected_components,
                created_at=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"지식 그래프 상태 계산 실패: {e}")
            return KnowledgeGraphResult(
                concept_count=0,
                edge_count=0,
                average_confidence=0.0,
                graph_density=0.0,
                connected_components=0,
                created_at=datetime.now().isoformat(),
                success=False,
            )

    def _find_concept_by_name(self, name: str) -> Optional[ConceptNode]:
        """이름으로 개념 찾기"""
        for concept in self.concepts.values():
            if concept.name.lower() == name.lower():
                return concept
        return None

    async def _ensure_concept_exists(self, name: str) -> str:
        """개념이 존재하는지 확인하고 없으면 생성"""
        concept = self._find_concept_by_name(name)
        if concept:
            return concept.id

        # 기본 개념 타입 추정
        concept_type = self._estimate_concept_type(name)
        concept_id = await self.add_concept(name, concept_type)
        return concept_id

    def _estimate_concept_type(self, name: str) -> ConceptType:
        """개념 타입 추정"""
        # 간단한 규칙 기반 추정
        action_words = ["run", "walk", "think", "create", "build", "learn", "teach"]
        property_words = ["big", "small", "fast", "slow", "hot", "cold", "good", "bad"]
        relation_words = ["between", "among", "with", "without", "through"]

        name_lower = name.lower()

        if any(word in name_lower for word in action_words):
            return ConceptType.ACTION
        elif any(word in name_lower for word in property_words):
            return ConceptType.PROPERTY
        elif any(word in name_lower for word in relation_words):
            return ConceptType.RELATION
        else:
            return ConceptType.ENTITY

    def _find_edge(
        self, source_id: str, target_id: str, inference_type: InferenceType
    ) -> Optional[InferenceEdge]:
        """엣지 찾기"""
        for edge in self.edges.values():
            if (
                edge.source_id == source_id
                and edge.target_id == target_id
                and edge.inference_type == inference_type
            ):
                return edge
        return None

    def _calculate_semantic_similarity(self, concept1: ConceptNode, concept2: ConceptNode) -> float:
        """시맨틱 유사도 계산"""
        # 벡터 유사도 계산
        vec1 = np.array(concept1.semantic_vector)
        vec2 = np.array(concept2.semantic_vector)

        cosine_similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

        # 개념 타입 일치도
        type_similarity = 1.0 if concept1.concept_type == concept2.concept_type else 0.5

        # 속성 유사도
        common_properties = set(concept1.properties.keys()) & set(concept2.properties.keys())
        property_similarity = len(common_properties) / max(
            len(concept1.properties), len(concept2.properties), 1
        )

        # 종합 유사도
        total_similarity = (
            cosine_similarity * 0.5 + type_similarity * 0.3 + property_similarity * 0.2
        )

        return max(0.0, min(1.0, total_similarity))

    async def _count_connected_components(self) -> int:
        """연결 요소 수 계산"""
        visited = set()
        components = 0

        for concept_id in self.concepts.keys():
            if concept_id not in visited:
                # DFS로 연결된 모든 노드 방문
                stack = [concept_id]
                while stack:
                    current = stack.pop()
                    if current not in visited:
                        visited.add(current)
                        # 인접한 노드들 추가
                        for neighbor in self.adjacency_list[current]:
                            if neighbor not in visited:
                                stack.append(neighbor)
                        for neighbor in self.reverse_adjacency[current]:
                            if neighbor not in visited:
                                stack.append(neighbor)
                components += 1

        return components


class ConceptAnalyzer:
    """개념 분석기"""

    def __init__(self, parent):
        self.parent = parent

    async def analyze_concept_properties(self, concept: ConceptNode) -> Dict[str, Any]:
        """개념 속성 분석"""
        try:
            analysis = {
                "centrality": self._calculate_centrality(concept.id),
                "connectivity": self._calculate_connectivity(concept.id),
                "semantic_richness": self._calculate_semantic_richness(concept),
                "temporal_activity": self._calculate_temporal_activity(concept),
            }
            return analysis
        except Exception as e:
            logger.error(f"개념 속성 분석 실패: {e}")
            return {}

    def _calculate_centrality(self, concept_id: str) -> float:
        """중앙성 계산"""
        if concept_id not in self.parent.adjacency_list:
            return 0.0

        in_degree = len(self.parent.reverse_adjacency.get(concept_id, set()))
        out_degree = len(self.parent.adjacency_list.get(concept_id, set()))

        return (in_degree + out_degree) / max(len(self.parent.concepts), 1)

    def _calculate_connectivity(self, concept_id: str) -> float:
        """연결성 계산"""
        neighbors = set()
        if concept_id in self.parent.adjacency_list:
            neighbors.update(self.parent.adjacency_list[concept_id])
        if concept_id in self.parent.reverse_adjacency:
            neighbors.update(self.parent.reverse_adjacency[concept_id])

        return len(neighbors) / max(len(self.parent.concepts), 1)

    def _calculate_semantic_richness(self, concept: ConceptNode) -> float:
        """시맨틱 풍부성 계산"""
        richness_factors = [
            len(concept.description) / 100.0,  # 설명 길이
            len(concept.properties) / 10.0,  # 속성 수
            concept.frequency / 10.0,  # 빈도
            len(concept.semantic_vector) / 100.0,  # 벡터 차원
        ]

        return min(1.0, sum(richness_factors) / len(richness_factors))

    def _calculate_temporal_activity(self, concept: ConceptNode) -> float:
        """시간적 활동성 계산"""
        time_diff = datetime.now() - concept.last_updated
        days_since_update = time_diff.total_seconds() / (24 * 3600)

        # 최근 업데이트일수록 높은 활동성
        activity = max(0.0, 1.0 - (days_since_update / 30.0))
        return activity


class InferenceEngine:
    """추론 엔진"""

    def __init__(self, parent):
        self.parent = parent

    async def infer_knowledge(
        self, concept_id: str, inference_type: InferenceType = None
    ) -> List[Dict[str, Any]]:
        """지식 추론"""
        try:
            inferences = []

            # 직접 연결된 개념들에서 추론
            direct_inferences = await self._infer_from_direct_connections(
                concept_id, inference_type
            )
            inferences.extend(direct_inferences)

            # 간접 연결을 통한 추론
            indirect_inferences = await self._infer_from_indirect_connections(
                concept_id, inference_type
            )
            inferences.extend(indirect_inferences)

            # 패턴 기반 추론
            pattern_inferences = await self._infer_from_patterns(concept_id, inference_type)
            inferences.extend(pattern_inferences)

            return inferences

        except Exception as e:
            logger.error(f"지식 추론 실패: {e}")
            return []

    async def _infer_from_direct_connections(
        self, concept_id: str, inference_type: InferenceType = None
    ) -> List[Dict[str, Any]]:
        """직접 연결에서 추론"""
        inferences = []

        # 나가는 엣지들
        for target_id in self.parent.adjacency_list.get(concept_id, set()):
            edge = self._find_edge_by_concepts(concept_id, target_id)
            if edge and (inference_type is None or edge.inference_type == inference_type):
                target_concept = self.parent.concepts.get(target_id)
                if target_concept:
                    inferences.append(
                        {
                            "type": "direct_outgoing",
                            "inference_type": edge.inference_type.value,
                            "target_concept": target_concept.name,
                            "confidence": edge.confidence,
                            "evidence": edge.evidence,
                        }
                    )

        # 들어오는 엣지들
        for source_id in self.parent.reverse_adjacency.get(concept_id, set()):
            edge = self._find_edge_by_concepts(source_id, concept_id)
            if edge and (inference_type is None or edge.inference_type == inference_type):
                source_concept = self.parent.concepts.get(source_id)
                if source_concept:
                    inferences.append(
                        {
                            "type": "direct_incoming",
                            "inference_type": edge.inference_type.value,
                            "source_concept": source_concept.name,
                            "confidence": edge.confidence,
                            "evidence": edge.evidence,
                        }
                    )

        return inferences

    async def _infer_from_indirect_connections(
        self, concept_id: str, inference_type: InferenceType = None
    ) -> List[Dict[str, Any]]:
        """간접 연결에서 추론"""
        inferences = []

        # 2단계 연결 탐색
        visited = {concept_id}
        queue = deque([(concept_id, 0)])

        while queue:
            current_id, distance = queue.popleft()

            if distance >= 2:  # 2단계까지만
                continue

            # 인접 노드들 탐색
            for neighbor_id in self.parent.adjacency_list.get(current_id, set()):
                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    queue.append((neighbor_id, distance + 1))

                    if distance == 1:  # 2단계 연결
                        edge = self._find_edge_by_concepts(current_id, neighbor_id)
                        if edge and (
                            inference_type is None or edge.inference_type == inference_type
                        ):
                            neighbor_concept = self.parent.concepts.get(neighbor_id)
                            if neighbor_concept:
                                inferences.append(
                                    {
                                        "type": "indirect",
                                        "inference_type": edge.inference_type.value,
                                        "target_concept": neighbor_concept.name,
                                        "confidence": edge.confidence * 0.8,  # 신뢰도 감소
                                        "distance": distance + 1,
                                    }
                                )

        return inferences

    async def _infer_from_patterns(
        self, concept_id: str, inference_type: InferenceType = None
    ) -> List[Dict[str, Any]]:
        """패턴 기반 추론"""
        inferences = []

        # 유사한 개념들 찾기
        current_concept = self.parent.concepts.get(concept_id)
        if not current_concept:
            return inferences

        similar_concepts = []
        for other_id, other_concept in self.parent.concepts.items():
            if other_id != concept_id:
                similarity = self.parent._calculate_semantic_similarity(
                    current_concept, other_concept
                )
                if similarity > self.parent.graph_parameters["similarity_threshold"]:
                    similar_concepts.append((other_concept, similarity))

        # 유사한 개념들의 연결 패턴 분석
        for similar_concept, similarity in similar_concepts:
            for edge in self.parent.edges.values():
                if edge.source_id == similar_concept.id and (
                    inference_type is None or edge.inference_type == inference_type
                ):
                    target_concept = self.parent.concepts.get(edge.target_id)
                    if target_concept:
                        inferences.append(
                            {
                                "type": "pattern_based",
                                "inference_type": edge.inference_type.value,
                                "target_concept": target_concept.name,
                                "confidence": edge.confidence * similarity * 0.7,
                                "similarity": similarity,
                                "pattern_source": similar_concept.name,
                            }
                        )

        return inferences

    def _find_edge_by_concepts(self, source_id: str, target_id: str) -> Optional[InferenceEdge]:
        """두 개념 간의 엣지 찾기"""
        for edge in self.parent.edges.values():
            if edge.source_id == source_id and edge.target_id == target_id:
                return edge
        return None


class PathFinder:
    """경로 찾기"""

    def __init__(self, parent):
        self.parent = parent

    async def find_path(
        self, source_id: str, target_id: str, max_length: int = 5
    ) -> Optional[SemanticPath]:
        """경로 찾기"""
        try:
            # BFS로 최단 경로 찾기
            queue = deque([(source_id, [source_id], [])])
            visited = {source_id}

            while queue:
                current_id, path_nodes, path_edges = queue.popleft()

                if current_id == target_id:
                    # 경로 찾음
                    return await self._create_semantic_path(path_nodes, path_edges)

                if len(path_nodes) >= max_length:
                    continue

                # 인접 노드들 탐색
                for neighbor_id in self.parent.adjacency_list.get(current_id, set()):
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)

                        # 엣지 찾기
                        edge = self._find_edge_by_concepts(current_id, neighbor_id)
                        new_path_edges = path_edges + [edge.id] if edge else path_edges

                        queue.append((neighbor_id, path_nodes + [neighbor_id], new_path_edges))

            return None  # 경로를 찾지 못함

        except Exception as e:
            logger.error(f"경로 찾기 실패: {e}")
            return None

    async def _create_semantic_path(
        self, path_nodes: List[str], path_edges: List[str]
    ) -> SemanticPath:
        """시맨틱 경로 생성"""
        try:
            path_id = f"path_{int(time.time())}"
            source_concept = self.parent.concepts.get(path_nodes[0])
            target_concept = self.parent.concepts.get(path_nodes[-1])

            # 추론 체인 생성
            inference_chain = []
            total_confidence = 1.0

            for edge_id in path_edges:
                edge = self.parent.edges.get(edge_id)
                if edge:
                    inference_chain.append(edge.inference_type)
                    total_confidence *= edge.confidence

            return SemanticPath(
                path_id=path_id,
                source_concept=source_concept.name if source_concept else "",
                target_concept=target_concept.name if target_concept else "",
                path_nodes=path_nodes,
                path_edges=path_edges,
                total_confidence=total_confidence,
                path_length=len(path_nodes) - 1,
                inference_chain=inference_chain,
            )

        except Exception as e:
            logger.error(f"시맨틱 경로 생성 실패: {e}")
            return None

    def _find_edge_by_concepts(self, source_id: str, target_id: str) -> Optional[InferenceEdge]:
        """두 개념 간의 엣지 찾기"""
        for edge in self.parent.edges.values():
            if edge.source_id == source_id and edge.target_id == target_id:
                return edge
        return None


class SemanticOptimizer:
    """시맨틱 최적화기"""

    def __init__(self, parent):
        self.parent = parent

    async def optimize_graph(self) -> Dict[str, Any]:
        """그래프 최적화"""
        try:
            optimization_results = {
                "removed_concepts": 0,
                "removed_edges": 0,
                "merged_concepts": 0,
                "confidence_improvements": 0,
            }

            # 낮은 신뢰도의 개념 제거
            low_confidence_concepts = [
                concept_id
                for concept_id, concept in self.parent.concepts.items()
                if concept.confidence < self.parent.graph_parameters["min_confidence"]
            ]

            for concept_id in low_confidence_concepts:
                await self._remove_concept(concept_id)
                optimization_results["removed_concepts"] += 1

            # 낮은 신뢰도의 엣지 제거
            low_confidence_edges = [
                edge_id
                for edge_id, edge in self.parent.edges.items()
                if edge.confidence < self.parent.graph_parameters["min_confidence"]
            ]

            for edge_id in low_confidence_edges:
                await self._remove_edge(edge_id)
                optimization_results["removed_edges"] += 1

            # 유사한 개념 병합
            merged_count = await self._merge_similar_concepts()
            optimization_results["merged_concepts"] = merged_count

            logger.info(f"그래프 최적화 완료: {optimization_results}")
            return optimization_results

        except Exception as e:
            logger.error(f"그래프 최적화 실패: {e}")
            return {}

    async def _remove_concept(self, concept_id: str):
        """개념 제거"""
        if concept_id in self.parent.concepts:
            del self.parent.concepts[concept_id]

            # 관련 엣지들 제거
            edges_to_remove = []
            for edge_id, edge in self.parent.edges.items():
                if edge.source_id == concept_id or edge.target_id == concept_id:
                    edges_to_remove.append(edge_id)

            for edge_id in edges_to_remove:
                await self._remove_edge(edge_id)

    async def _remove_edge(self, edge_id: str):
        """엣지 제거"""
        if edge_id in self.parent.edges:
            edge = self.parent.edges[edge_id]

            # 인접 리스트에서 제거
            if edge.source_id in self.parent.adjacency_list:
                self.parent.adjacency_list[edge.source_id].discard(edge.target_id)

            if edge.target_id in self.parent.reverse_adjacency:
                self.parent.reverse_adjacency[edge.target_id].discard(edge.source_id)

            del self.parent.edges[edge_id]

    async def _merge_similar_concepts(self) -> int:
        """유사한 개념 병합"""
        merged_count = 0
        processed = set()

        for concept_id1, concept1 in self.parent.concepts.items():
            if concept_id1 in processed:
                continue

            for concept_id2, concept2 in self.parent.concepts.items():
                if (
                    concept_id2 in processed
                    or concept_id1 == concept_id2
                    or concept_id2 in processed
                ):
                    continue

                similarity = self.parent._calculate_semantic_similarity(concept1, concept2)
                if similarity > self.parent.graph_parameters["similarity_threshold"]:
                    # 개념 병합
                    await self._merge_concepts(concept_id1, concept_id2)
                    processed.add(concept_id2)
                    merged_count += 1

        return merged_count

    async def _merge_concepts(self, primary_id: str, secondary_id: str):
        """두 개념 병합"""
        primary = self.parent.concepts[primary_id]
        secondary = self.parent.concepts[secondary_id]

        # 주 개념에 부 개념의 정보 병합
        primary.frequency += secondary.frequency
        primary.confidence = max(primary.confidence, secondary.confidence)
        primary.properties.update(secondary.properties)

        # 엣지들 업데이트
        for edge in self.parent.edges.values():
            if edge.source_id == secondary_id:
                edge.source_id = primary_id
            if edge.target_id == secondary_id:
                edge.target_id = primary_id

        # 부 개념 제거
        del self.parent.concepts[secondary_id]


# 테스트 함수
async def test_semantic_knowledge_graph():
    """시맨틱 지식 연결망 테스트"""
    graph = SemanticKnowledgeGraph()

    # 테스트 개념들 추가
    await graph.add_concept("사람", ConceptType.ENTITY, "인간 개체")
    await graph.add_concept("동물", ConceptType.ENTITY, "동물 개체")
    await graph.add_concept("포유류", ConceptType.ENTITY, "포유류 동물")
    await graph.add_concept("이동", ConceptType.ACTION, "움직이는 행동")
    await graph.add_concept("생각", ConceptType.ACTION, "머리로 생각하는 행동")

    # 테스트 추론들 추가
    await graph.add_inference("사람", "동물", InferenceType.IS_A, 0.9)
    await graph.add_inference("동물", "포유류", InferenceType.IS_A, 0.8)
    await graph.add_inference("사람", "이동", InferenceType.CAN_DO, 0.95)
    await graph.add_inference("사람", "생각", InferenceType.CAN_DO, 0.9)

    # 시맨틱 경로 찾기
    path = await graph.find_semantic_path("사람", "포유류")

    # 지식 그래프 상태 확인
    status = await graph.get_knowledge_graph_status()

    # 결과 출력
    print("=== 시맨틱 지식 연결망 테스트 결과 ===")
    print(f"개념 수: {status.concept_count}")
    print(f"엣지 수: {status.edge_count}")
    print(f"평균 신뢰도: {status.average_confidence:.3f}")
    print(f"그래프 밀도: {status.graph_density:.3f}")
    if path:
        print(f"경로 찾음: {path.source_concept} -> {path.target_concept}")
        print(f"경로 길이: {path.path_length}")
        print(f"총 신뢰도: {path.total_confidence:.3f}")


if __name__ == "__main__":
    asyncio.run(test_semantic_knowledge_graph())
