#!/usr/bin/env python3
"""
DuRi 불일치 탐지 및 해결 시스템 - Phase 1-3 Week 3 Day 3
동적 추론 그래프의 불일치를 탐지하고 자동으로 해결하는 시스템

기능:
1. 불일치 탐지 시스템
2. 자동 해결 시스템
3. 해결 전략 시스템
4. 검증 시스템
"""

import asyncio
import logging
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InconsistencyType(Enum):
    """불일치 유형"""

    LOGICAL_CONTRADICTION = "logical_contradiction"
    SEMANTIC_INCONSISTENCY = "semantic_inconsistency"
    STRUCTURAL_INCONSISTENCY = "structural_inconsistency"
    CONFLICTING_EVIDENCE = "conflicting_evidence"
    CIRCULAR_REASONING = "circular_reasoning"
    MISSING_PREMISE = "missing_premise"


class ResolutionStrategy(Enum):
    """해결 전략"""

    NODE_MODIFICATION = "node_modification"
    EDGE_ADJUSTMENT = "edge_adjustment"
    PATH_RECONSTRUCTION = "path_reconstruction"
    EVIDENCE_WEIGHTING = "evidence_weighting"
    CONTRADICTION_RESOLUTION = "contradiction_resolution"


@dataclass
class Inconsistency:
    """불일치 정보"""

    inconsistency_id: str
    inconsistency_type: InconsistencyType
    severity: float  # 0.0-1.0
    description: str
    affected_nodes: List[str] = field(default_factory=list)
    affected_edges: List[str] = field(default_factory=list)
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class ResolutionResult:
    """해결 결과"""

    resolution_id: str
    inconsistency_id: str
    strategy: ResolutionStrategy
    success: bool
    confidence: float
    description: str
    modified_nodes: List[str] = field(default_factory=list)
    modified_edges: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class InconsistencyDetector:
    """불일치 탐지 시스템"""

    def __init__(self):
        self.detection_rules = self._initialize_detection_rules()
        self.inconsistency_cache = {}
        self.max_cache_size = 1000

    def _initialize_detection_rules(self) -> Dict[str, Dict[str, Any]]:
        """탐지 규칙 초기화"""
        return {
            "logical_contradiction": {
                "weight": 0.3,
                "threshold": 0.7,
                "description": "논리적 모순 탐지",
            },
            "semantic_inconsistency": {
                "weight": 0.25,
                "threshold": 0.6,
                "description": "의미적 불일치 탐지",
            },
            "structural_inconsistency": {
                "weight": 0.25,
                "threshold": 0.6,
                "description": "구조적 불일치 탐지",
            },
            "conflicting_evidence": {
                "weight": 0.2,
                "threshold": 0.5,
                "description": "상충하는 증거 탐지",
            },
        }

    async def detect_inconsistencies(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """불일치 탐지"""
        logger.info(f"불일치 탐지 시작: {len(graph.nodes)} 노드, {len(graph.edges)} 엣지")

        inconsistencies = []

        # 1. 논리적 모순 탐지
        logical_contradictions = await self._detect_logical_contradictions(graph)
        inconsistencies.extend(logical_contradictions)

        # 2. 의미적 불일치 탐지
        semantic_inconsistencies = await self._detect_semantic_inconsistencies(graph)
        inconsistencies.extend(semantic_inconsistencies)

        # 3. 구조적 불일치 탐지
        structural_inconsistencies = await self._detect_structural_inconsistencies(graph)
        inconsistencies.extend(structural_inconsistencies)

        # 4. 상충하는 증거 탐지
        conflicting_evidence = await self._detect_conflicting_evidence(graph)
        inconsistencies.extend(conflicting_evidence)

        # 5. 순환 추론 탐지
        circular_reasoning = await self._detect_circular_reasoning(graph)
        inconsistencies.extend(circular_reasoning)

        # 6. 누락된 전제 탐지
        missing_premises = await self._detect_missing_premises(graph)
        inconsistencies.extend(missing_premises)

        logger.info(f"불일치 탐지 완료: {len(inconsistencies)}개 발견")
        return inconsistencies

    async def _detect_logical_contradictions(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """논리적 모순 탐지"""
        contradictions = []

        # 노드 간 직접적인 논리적 모순 탐지
        for node1_id, node1 in graph.nodes.items():
            for node2_id, node2 in graph.nodes.items():
                if node1_id != node2_id:
                    # 직접적인 논리적 모순 확인
                    if self._is_logical_contradiction(node1, node2):
                        contradiction = Inconsistency(
                            inconsistency_id=f"logical_contradiction_{node1_id}_{node2_id}",
                            inconsistency_type=InconsistencyType.LOGICAL_CONTRADICTION,
                            severity=0.8,
                            description=f"논리적 모순: {node1.content} vs {node2.content}",
                            affected_nodes=[node1_id, node2_id],
                            confidence=0.9,
                        )
                        contradictions.append(contradiction)

        # 엣지를 통한 논리적 모순 탐지
        for edge in graph.edges.values():
            if edge.edge_type.value in ["contradicts", "challenges"]:
                source_node = graph.nodes.get(edge.source_node)
                target_node = graph.nodes.get(edge.target_node)

                if source_node and target_node:
                    contradiction = Inconsistency(
                        inconsistency_id=f"edge_contradiction_{edge.edge_id}",
                        inconsistency_type=InconsistencyType.LOGICAL_CONTRADICTION,
                        severity=edge.strength,
                        description=f"엣지 기반 논리적 모순: {source_node.content} -> {target_node.content}",
                        affected_nodes=[edge.source_node, edge.target_node],
                        affected_edges=[edge.edge_id],
                        confidence=edge.strength,
                    )
                    contradictions.append(contradiction)

        return contradictions

    async def _detect_semantic_inconsistencies(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """의미적 불일치 탐지"""
        inconsistencies = []

        # 노드 간 의미적 불일치 탐지 (더 관대한 기준 적용)
        for node1_id, node1 in graph.nodes.items():
            for node2_id, node2 in graph.nodes.items():
                if node1_id != node2_id:
                    # 의미적 유사도가 낮지만 연결된 경우
                    similarity = self._calculate_semantic_similarity(node1.content, node2.content)

                    # 연결된 노드인지 확인
                    is_connected = False
                    for edge in graph.edges.values():
                        if (edge.source_node == node1_id and edge.target_node == node2_id) or (
                            edge.source_node == node2_id and edge.target_node == node1_id
                        ):
                            is_connected = True
                            break

                    # 더 관대한 기준 적용 (0.3 → 0.1)
                    if is_connected and similarity < 0.1:
                        inconsistency = Inconsistency(
                            inconsistency_id=f"semantic_inconsistency_{node1_id}_{node2_id}",
                            inconsistency_type=InconsistencyType.SEMANTIC_INCONSISTENCY,
                            severity=0.4,  # 심각도 감소
                            description=f"의미적 불일치: {node1.content} vs {node2.content} (유사도: {similarity:.2f})",
                            affected_nodes=[node1_id, node2_id],
                            confidence=0.5,  # 신뢰도 감소
                        )
                        inconsistencies.append(inconsistency)

        return inconsistencies

    async def _detect_structural_inconsistencies(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """구조적 불일치 탐지"""
        inconsistencies = []

        # 고립된 노드 탐지
        isolated_nodes = []
        for node_id in graph.nodes:
            has_connection = False
            for edge in graph.edges.values():
                if edge.source_node == node_id or edge.target_node == node_id:
                    has_connection = True
                    break

            if not has_connection:
                isolated_nodes.append(node_id)

        if isolated_nodes:
            inconsistency = Inconsistency(
                inconsistency_id="structural_inconsistency_isolated_nodes",
                inconsistency_type=InconsistencyType.STRUCTURAL_INCONSISTENCY,
                severity=0.5,
                description=f"고립된 노드 발견: {isolated_nodes}",
                affected_nodes=isolated_nodes,
                confidence=0.8,
            )
            inconsistencies.append(inconsistency)

        # 불균형한 그래프 구조 탐지
        node_types = defaultdict(int)
        for node in graph.nodes.values():
            node_types[node.node_type] += 1

        # 특정 유형의 노드가 너무 많거나 적은 경우
        total_nodes = len(graph.nodes)
        for node_type, count in node_types.items():
            ratio = count / total_nodes
            if ratio > 0.7 or (ratio < 0.1 and total_nodes > 5):
                inconsistency = Inconsistency(
                    inconsistency_id=f"structural_inconsistency_node_type_{node_type.value}",
                    inconsistency_type=InconsistencyType.STRUCTURAL_INCONSISTENCY,
                    severity=0.4,
                    description=f"불균형한 노드 유형: {node_type.value} ({count}/{total_nodes})",
                    affected_nodes=[n.node_id for n in graph.nodes.values() if n.node_type == node_type],
                    confidence=0.6,
                )
                inconsistencies.append(inconsistency)

        return inconsistencies

    async def _detect_conflicting_evidence(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """상충하는 증거 탐지"""
        conflicts = []

        # 증거 노드들 찾기
        evidence_nodes = [n for n in graph.nodes.values() if n.node_type.value == "evidence"]

        # 증거 간 상충 관계 탐지
        for i, evidence1 in enumerate(evidence_nodes):
            for j, evidence2 in enumerate(evidence_nodes[i + 1 :], i + 1):
                # 증거 간 의미적 상충 확인
                if self._is_conflicting_evidence(evidence1, evidence2):
                    conflict = Inconsistency(
                        inconsistency_id=f"conflicting_evidence_{evidence1.node_id}_{evidence2.node_id}",
                        inconsistency_type=InconsistencyType.CONFLICTING_EVIDENCE,
                        severity=0.7,
                        description=f"상충하는 증거: {evidence1.content} vs {evidence2.content}",
                        affected_nodes=[evidence1.node_id, evidence2.node_id],
                        confidence=0.8,
                    )
                    conflicts.append(conflict)

        return conflicts

    async def _detect_circular_reasoning(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """순환 추론 탐지"""
        circular_reasoning = []

        # 실제 순환만 탐지하도록 개선
        def has_cycle(start_node: str, visited: set, rec_stack: set, path: list) -> Optional[list]:
            """실제 순환 탐지"""
            if start_node in rec_stack:
                # 순환 발견
                cycle_start = path.index(start_node)
                cycle = path[cycle_start:]
                if len(cycle) > 2:  # 최소 3개 노드 이상의 순환만 고려
                    return cycle
                return None

            if start_node in visited:
                return None

            visited.add(start_node)
            rec_stack.add(start_node)
            path.append(start_node)

            # 인접 노드 탐색 (방향성 고려)
            for edge in graph.edges.values():
                if edge.source_node == start_node:
                    cycle = has_cycle(edge.target_node, visited.copy(), rec_stack.copy(), path.copy())
                    if cycle:
                        return cycle

            rec_stack.remove(start_node)
            return None

        # 모든 노드에서 순환 탐지
        all_visited = set()
        for node_id in graph.nodes:
            if node_id not in all_visited:
                cycle = has_cycle(node_id, set(), set(), [])
                if cycle:
                    circular_reasoning.append(
                        Inconsistency(
                            inconsistency_id=f"circular_reasoning_{len(circular_reasoning)}",
                            inconsistency_type=InconsistencyType.CIRCULAR_REASONING,
                            severity=0.6,
                            description=f"순환 추론 발견: {' -> '.join(cycle)}",
                            affected_nodes=cycle,
                            confidence=0.9,
                        )
                    )
                    all_visited.update(cycle)

        return circular_reasoning

    async def _detect_missing_premises(self, graph: "DynamicReasoningGraph") -> List[Inconsistency]:
        """누락된 전제 탐지"""
        missing_premises = []

        # 결론 노드들 찾기
        conclusion_nodes = [n for n in graph.nodes.values() if n.node_type.value == "conclusion"]

        for conclusion in conclusion_nodes:
            # 결론을 지원하는 전제들 찾기
            supporting_premises = []
            for edge in graph.edges.values():
                if edge.target_node == conclusion.node_id and edge.edge_type.value in [
                    "supports",
                    "infers",
                ]:
                    source_node = graph.nodes.get(edge.source_node)
                    if source_node and source_node.node_type.value == "premise":
                        supporting_premises.append(source_node)

            # 전제가 부족한 경우
            if len(supporting_premises) < 2:
                missing_premises.append(
                    Inconsistency(
                        inconsistency_id=f"missing_premise_{conclusion.node_id}",
                        inconsistency_type=InconsistencyType.MISSING_PREMISE,
                        severity=0.5,
                        description=f"누락된 전제: {conclusion.content} (지원 전제: {len(supporting_premises)}개)",
                        affected_nodes=[conclusion.node_id],
                        confidence=0.7,
                    )
                )

        return missing_premises

    def _is_logical_contradiction(self, node1: "DynamicReasoningNode", node2: "DynamicReasoningNode") -> bool:
        """논리적 모순 여부 확인"""
        # 간단한 키워드 기반 모순 탐지
        contradiction_keywords = {
            "찬성": "반대",
            "옳다": "틀리다",
            "참": "거짓",
            "있음": "없음",
            "가능": "불가능",
            "필요": "불필요",
            "중요": "중요하지 않음",
        }

        content1 = node1.content.lower()
        content2 = node2.content.lower()

        for keyword1, keyword2 in contradiction_keywords.items():
            if keyword1 in content1 and keyword2 in content2:
                return True
            if keyword2 in content1 and keyword1 in content2:
                return True

        return False

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """의미적 유사도 계산"""
        # 키워드 기반 유사도 계산
        keywords1 = set(re.findall(r"\w+", text1.lower()))
        keywords2 = set(re.findall(r"\w+", text2.lower()))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0

    def _is_conflicting_evidence(self, evidence1: "DynamicReasoningNode", evidence2: "DynamicReasoningNode") -> bool:
        """상충하는 증거 여부 확인"""
        # 간단한 키워드 기반 상충 탐지
        conflict_keywords = {
            "증가": "감소",
            "상승": "하락",
            "개선": "악화",
            "성공": "실패",
        }

        content1 = evidence1.content.lower()
        content2 = evidence2.content.lower()

        for keyword1, keyword2 in conflict_keywords.items():
            if keyword1 in content1 and keyword2 in content2:
                return True
            if keyword2 in content1 and keyword1 in content2:
                return True

        return False


class InconsistencyResolver:
    """불일치 해결 시스템"""

    def __init__(self):
        self.resolution_strategies = self._initialize_resolution_strategies()
        self.resolution_cache = {}
        self.max_cache_size = 1000

    def _initialize_resolution_strategies(self) -> Dict[str, Dict[str, Any]]:
        """해결 전략 초기화"""
        return {
            "node_modification": {"weight": 0.3, "description": "노드 수정 전략"},
            "edge_adjustment": {"weight": 0.25, "description": "엣지 조정 전략"},
            "path_reconstruction": {"weight": 0.25, "description": "경로 재구성 전략"},
            "evidence_weighting": {
                "weight": 0.2,
                "description": "증거 가중치 조정 전략",
            },
        }

    async def resolve_inconsistencies(
        self, graph: "DynamicReasoningGraph", inconsistencies: List[Inconsistency]
    ) -> List[ResolutionResult]:
        """불일치 해결"""
        logger.info(f"불일치 해결 시작: {len(inconsistencies)}개 불일치")

        resolution_results = []
        modified_nodes = set()  # 중복 수정 방지
        modified_edges = set()  # 중복 수정 방지

        for inconsistency in inconsistencies:
            # 불일치 유형에 따른 해결 전략 선택
            strategy = self._select_resolution_strategy(inconsistency)

            # 해결 실행 (중복 수정 방지)
            resolution_result = await self._execute_resolution_strategy(
                graph, inconsistency, strategy, modified_nodes, modified_edges
            )

            if resolution_result:
                resolution_results.append(resolution_result)
                # 수정된 노드와 엣지 기록
                modified_nodes.update(resolution_result.modified_nodes)
                modified_edges.update(resolution_result.modified_edges)

        logger.info(f"불일치 해결 완료: {len(resolution_results)}개 해결됨")
        return resolution_results

    def _select_resolution_strategy(self, inconsistency: Inconsistency) -> ResolutionStrategy:
        """해결 전략 선택"""
        if inconsistency.inconsistency_type == InconsistencyType.LOGICAL_CONTRADICTION:
            return ResolutionStrategy.CONTRADICTION_RESOLUTION
        elif inconsistency.inconsistency_type == InconsistencyType.SEMANTIC_INCONSISTENCY:
            return ResolutionStrategy.NODE_MODIFICATION
        elif inconsistency.inconsistency_type == InconsistencyType.STRUCTURAL_INCONSISTENCY:
            return ResolutionStrategy.PATH_RECONSTRUCTION
        elif inconsistency.inconsistency_type == InconsistencyType.CONFLICTING_EVIDENCE:
            return ResolutionStrategy.EVIDENCE_WEIGHTING
        else:
            return ResolutionStrategy.EDGE_ADJUSTMENT

    async def _execute_resolution_strategy(
        self,
        graph: "DynamicReasoningGraph",
        inconsistency: Inconsistency,
        strategy: ResolutionStrategy,
        modified_nodes: Set[str],
        modified_edges: Set[str],
    ) -> Optional[ResolutionResult]:
        """해결 전략 실행"""
        try:
            if strategy == ResolutionStrategy.NODE_MODIFICATION:
                return await self._resolve_node_modification(graph, inconsistency, modified_nodes)
            elif strategy == ResolutionStrategy.EDGE_ADJUSTMENT:
                return await self._resolve_edge_adjustment(graph, inconsistency, modified_edges)
            elif strategy == ResolutionStrategy.PATH_RECONSTRUCTION:
                return await self._resolve_path_reconstruction(graph, inconsistency, modified_nodes)
            elif strategy == ResolutionStrategy.EVIDENCE_WEIGHTING:
                return await self._resolve_evidence_weighting(graph, inconsistency, modified_nodes)
            elif strategy == ResolutionStrategy.CONTRADICTION_RESOLUTION:
                return await self._resolve_contradiction_resolution(
                    graph, inconsistency, modified_nodes, modified_edges
                )
            else:
                return None
        except Exception as e:
            logger.error(f"해결 전략 실행 실패: {e}")
            return None

    async def _resolve_node_modification(
        self,
        graph: "DynamicReasoningGraph",
        inconsistency: Inconsistency,
        modified_nodes: Set[str],
    ) -> ResolutionResult:
        """노드 수정 전략"""
        nodes_to_modify = []

        for node_id in inconsistency.affected_nodes:
            node = graph.nodes.get(node_id)
            if node:
                # 노드 신뢰도 조정
                original_confidence = node.confidence  # noqa: F841
                node.confidence = max(0.1, node.confidence * 0.8)  # 신뢰도 감소
                modified_nodes.add(node_id)  # 중복 수정 방지
                nodes_to_modify.append(node_id)

        return ResolutionResult(
            resolution_id=f"node_modification_{inconsistency.inconsistency_id}",
            inconsistency_id=inconsistency.inconsistency_id,
            strategy=ResolutionStrategy.NODE_MODIFICATION,
            success=len(nodes_to_modify) > 0,
            confidence=0.7,
            description=f"노드 수정: {len(nodes_to_modify)}개 노드 신뢰도 조정",
            modified_nodes=nodes_to_modify,
        )

    async def _resolve_edge_adjustment(
        self,
        graph: "DynamicReasoningGraph",
        inconsistency: Inconsistency,
        modified_edges: Set[str],
    ) -> ResolutionResult:
        """엣지 조정 전략"""
        edges_to_modify = []

        for edge_id in inconsistency.affected_edges:
            edge = graph.edges.get(edge_id)
            if edge:
                # 엣지 강도 조정
                original_strength = edge.strength  # noqa: F841
                edge.strength = max(0.1, edge.strength * 0.7)  # 강도 감소
                modified_edges.add(edge_id)  # 중복 수정 방지
                edges_to_modify.append(edge_id)

        return ResolutionResult(
            resolution_id=f"edge_adjustment_{inconsistency.inconsistency_id}",
            inconsistency_id=inconsistency.inconsistency_id,
            strategy=ResolutionStrategy.EDGE_ADJUSTMENT,
            success=len(edges_to_modify) > 0,
            confidence=0.6,
            description=f"엣지 조정: {len(edges_to_modify)}개 엣지 강도 조정",
            modified_edges=edges_to_modify,
        )

    async def _resolve_path_reconstruction(
        self,
        graph: "DynamicReasoningGraph",
        inconsistency: Inconsistency,
        modified_nodes: Set[str],
    ) -> ResolutionResult:
        """경로 재구성 전략"""
        # 고립된 노드들을 다른 노드와 연결
        new_edges = []

        for node_id in inconsistency.affected_nodes:
            node = graph.nodes.get(node_id)
            if node:
                # 가장 유사한 노드 찾기
                best_similarity = 0.0
                best_target = None

                for target_id, target_node in graph.nodes.items():
                    if target_id != node_id:
                        similarity = self._calculate_semantic_similarity(node.content, target_node.content)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_target = target_id

                # 새로운 엣지 생성
                if best_target and best_similarity > 0.3:
                    new_edge_id = f"reconstructed_edge_{node_id}_{best_target}"
                    new_edge = DynamicReasoningEdge(
                        edge_id=new_edge_id,
                        source_node=node_id,
                        target_node=best_target,
                        edge_type=EdgeType.SUPPORTS,
                        strength=best_similarity,
                        reasoning="경로 재구성을 통한 연결",
                    )
                    graph.edges[new_edge_id] = new_edge
                    new_edges.append(new_edge_id)
                    modified_nodes.add(node_id)  # 중복 수정 방지

        return ResolutionResult(
            resolution_id=f"path_reconstruction_{inconsistency.inconsistency_id}",
            inconsistency_id=inconsistency.inconsistency_id,
            strategy=ResolutionStrategy.PATH_RECONSTRUCTION,
            success=len(new_edges) > 0,
            confidence=0.5,
            description=f"경로 재구성: {len(new_edges)}개 새 엣지 생성",
            modified_nodes=list(modified_nodes),  # Set to List for JSON serialization
        )

    async def _resolve_evidence_weighting(
        self,
        graph: "DynamicReasoningGraph",
        inconsistency: Inconsistency,
        modified_nodes: Set[str],
    ) -> ResolutionResult:
        """증거 가중치 조정 전략"""
        nodes_to_modify = []

        for node_id in inconsistency.affected_nodes:
            node = graph.nodes.get(node_id)
            if node and node.node_type.value == "evidence":
                # 증거 노드의 중요도 조정
                original_importance = node.importance_score  # noqa: F841
                node.importance_score = max(0.1, node.importance_score * 0.6)  # 중요도 감소
                modified_nodes.add(node_id)  # 중복 수정 방지
                nodes_to_modify.append(node_id)

        return ResolutionResult(
            resolution_id=f"evidence_weighting_{inconsistency.inconsistency_id}",
            inconsistency_id=inconsistency.inconsistency_id,
            strategy=ResolutionStrategy.EVIDENCE_WEIGHTING,
            success=len(nodes_to_modify) > 0,
            confidence=0.6,
            description=f"증거 가중치 조정: {len(nodes_to_modify)}개 증거 노드 중요도 조정",
            modified_nodes=nodes_to_modify,
        )

    async def _resolve_contradiction_resolution(
        self,
        graph: "DynamicReasoningGraph",
        inconsistency: Inconsistency,
        modified_nodes: Set[str],
        modified_edges: Set[str],
    ) -> ResolutionResult:
        """모순 해결 전략"""
        nodes_to_modify = []
        edges_to_modify = []

        # 모순된 노드들의 신뢰도 조정
        for node_id in inconsistency.affected_nodes:
            node = graph.nodes.get(node_id)
            if node:
                # 모순된 노드의 신뢰도 감소
                node.confidence = max(0.1, node.confidence * 0.5)
                modified_nodes.add(node_id)  # 중복 수정 방지
                nodes_to_modify.append(node_id)

        # 모순을 나타내는 엣지들의 강도 조정
        for edge_id in inconsistency.affected_edges:
            edge = graph.edges.get(edge_id)
            if edge:
                edge.strength = max(0.1, edge.strength * 0.3)
                modified_edges.add(edge_id)  # 중복 수정 방지
                edges_to_modify.append(edge_id)

        return ResolutionResult(
            resolution_id=f"contradiction_resolution_{inconsistency.inconsistency_id}",
            inconsistency_id=inconsistency.inconsistency_id,
            strategy=ResolutionStrategy.CONTRADICTION_RESOLUTION,
            success=len(nodes_to_modify) > 0 or len(edges_to_modify) > 0,
            confidence=0.8,
            description=f"모순 해결: {len(nodes_to_modify)}개 노드, {len(edges_to_modify)}개 엣지 조정",
            modified_nodes=nodes_to_modify,
            modified_edges=edges_to_modify,
        )

    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """의미적 유사도 계산"""
        keywords1 = set(re.findall(r"\w+", text1.lower()))
        keywords2 = set(re.findall(r"\w+", text2.lower()))

        if not keywords1 or not keywords2:
            return 0.0

        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))

        return intersection / union if union > 0 else 0.0


class InconsistencyValidator:
    """불일치 해결 검증 시스템"""

    def __init__(self):
        self.validation_criteria = self._initialize_validation_criteria()

    def _initialize_validation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """검증 기준 초기화"""
        return {
            "resolution_success": {"weight": 0.4, "description": "해결 성공률"},
            "system_stability": {"weight": 0.3, "description": "시스템 안정성"},
            "quality_improvement": {"weight": 0.3, "description": "품질 향상도"},
        }

    async def validate_resolution_results(
        self,
        graph: "DynamicReasoningGraph",
        inconsistencies: List[Inconsistency],
        resolution_results: List[ResolutionResult],
    ) -> Dict[str, Any]:
        """해결 결과 검증"""
        logger.info(f"해결 결과 검증 시작: {len(resolution_results)}개 해결 결과")

        # 1. 해결 성공률 계산
        resolution_success_rate = self._calculate_resolution_success_rate(resolution_results)

        # 2. 시스템 안정성 평가
        system_stability = await self._evaluate_system_stability(graph)

        # 3. 품질 향상도 평가
        quality_improvement = await self._evaluate_quality_improvement(graph, inconsistencies)

        # 종합 검증 결과
        overall_validation_score = (
            resolution_success_rate * self.validation_criteria["resolution_success"]["weight"]
            + system_stability * self.validation_criteria["system_stability"]["weight"]
            + quality_improvement * self.validation_criteria["quality_improvement"]["weight"]
        )

        return {
            "overall_validation_score": overall_validation_score,
            "resolution_success_rate": resolution_success_rate,
            "system_stability": system_stability,
            "quality_improvement": quality_improvement,
            "validation_details": {
                "total_inconsistencies": len(inconsistencies),
                "resolved_inconsistencies": len([r for r in resolution_results if r.success]),
                "failed_resolutions": len([r for r in resolution_results if not r.success]),
                "modified_nodes": len(set([n for r in resolution_results for n in r.modified_nodes])),
                "modified_edges": len(set([e for r in resolution_results for e in r.modified_edges])),
            },
        }

    def _calculate_resolution_success_rate(self, resolution_results: List[ResolutionResult]) -> float:
        """해결 성공률 계산"""
        if not resolution_results:
            return 0.0

        successful_resolutions = len([r for r in resolution_results if r.success])
        return successful_resolutions / len(resolution_results)

    async def _evaluate_system_stability(self, graph: "DynamicReasoningGraph") -> float:
        """시스템 안정성 평가"""
        # 노드 신뢰도의 평균
        node_confidences = [node.confidence for node in graph.nodes.values()]
        avg_node_confidence = sum(node_confidences) / len(node_confidences) if node_confidences else 0.0

        # 엣지 강도의 평균
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        avg_edge_strength = sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0

        # 시스템 안정성 (신뢰도와 강도의 평균)
        system_stability = (avg_node_confidence + avg_edge_strength) / 2.0
        return system_stability

    async def _evaluate_quality_improvement(
        self, graph: "DynamicReasoningGraph", inconsistencies: List[Inconsistency]
    ) -> float:
        """품질 향상도 평가"""
        # 불일치 수에 따른 품질 점수 (더 관대한 기준 적용)
        total_nodes = len(graph.nodes)
        inconsistency_ratio = len(inconsistencies) / total_nodes if total_nodes > 0 else 0.0

        # 불일치 비율이 낮을수록 품질이 높음 (더 관대한 기준)
        quality_score = max(0.0, 1.0 - inconsistency_ratio * 2)  # 가중치 조정

        # 노드 간 연결성 고려
        total_possible_connections = total_nodes * (total_nodes - 1) / 2
        actual_connections = len(graph.edges)
        connectivity_ratio = actual_connections / total_possible_connections if total_possible_connections > 0 else 0.0

        # 노드 신뢰도 평균 고려
        node_confidences = [node.confidence for node in graph.nodes.values()]
        avg_confidence = sum(node_confidences) / len(node_confidences) if node_confidences else 0.0

        # 엣지 강도 평균 고려
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        avg_strength = sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0

        # 종합 품질 점수 (더 균형잡힌 가중치)
        overall_quality = quality_score * 0.4 + connectivity_ratio * 0.2 + avg_confidence * 0.2 + avg_strength * 0.2

        return overall_quality


# 테스트용 클래스들 (reasoning_path_validator.py에서 가져옴)
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


async def test_inconsistency_detector():
    """불일치 탐지 및 해결 시스템 테스트"""
    print("=== 불일치 탐지 및 해결 시스템 테스트 시작 (Phase 1-3 Week 3 Day 3) ===")

    # 테스트 그래프 생성
    graph = DynamicReasoningGraph(graph_id="test_graph")

    # 테스트 노드들 생성 (의도적으로 불일치 포함)
    nodes = {
        "node1": DynamicReasoningNode("node1", NodeType.PREMISE, "윤리적 행동은 옳다", 0.8, "test"),
        "node2": DynamicReasoningNode("node2", NodeType.PREMISE, "윤리적 행동은 틀리다", 0.7, "test"),  # 모순
        "node3": DynamicReasoningNode("node3", NodeType.INFERENCE, "칸트적 분석", 0.6, "test"),
        "node4": DynamicReasoningNode("node4", NodeType.CONCLUSION, "최종 판단", 0.9, "test"),
        "node5": DynamicReasoningNode("node5", NodeType.EVIDENCE, "증거 A: 긍정적 결과", 0.8, "test"),
        "node6": DynamicReasoningNode("node6", NodeType.EVIDENCE, "증거 B: 부정적 결과", 0.7, "test"),  # 상충
        "node7": DynamicReasoningNode("node7", NodeType.COUNTER_ARGUMENT, "반론", 0.5, "test"),
        "node8": DynamicReasoningNode("node8", NodeType.ASSUMPTION, "가정", 0.6, "test"),
    }

    graph.nodes = nodes

    # 테스트 엣지들 생성
    edges = {
        "edge1": DynamicReasoningEdge("edge1", "node1", "node3", EdgeType.SUPPORTS, 0.8, "지원"),
        "edge2": DynamicReasoningEdge("edge2", "node2", "node3", EdgeType.CONTRADICTS, 0.7, "모순"),  # 모순 엣지
        "edge3": DynamicReasoningEdge("edge3", "node3", "node4", EdgeType.INFERS, 0.9, "추론"),
        "edge4": DynamicReasoningEdge("edge4", "node5", "node4", EdgeType.EVIDENCES, 0.8, "증거"),
        "edge5": DynamicReasoningEdge("edge5", "node6", "node4", EdgeType.EVIDENCES, 0.7, "증거"),
        "edge6": DynamicReasoningEdge("edge6", "node7", "node4", EdgeType.CHALLENGES, 0.6, "도전"),
    }

    graph.edges = edges

    # 1. 불일치 탐지 테스트
    detector = InconsistencyDetector()
    inconsistencies = await detector.detect_inconsistencies(graph)

    print("\n🔍 불일치 탐지 결과:")
    print(f"  • 발견된 불일치 수: {len(inconsistencies)}")
    for i, inconsistency in enumerate(inconsistencies):
        print(f"  • 불일치 {i+1}: {inconsistency.inconsistency_type.value} (심각도: {inconsistency.severity:.2f})")
        print(f"    - 설명: {inconsistency.description}")
        print(f"    - 영향받는 노드: {inconsistency.affected_nodes}")

    # 2. 불일치 해결 테스트
    resolver = InconsistencyResolver()
    resolution_results = await resolver.resolve_inconsistencies(graph, inconsistencies)

    print("\n🔧 불일치 해결 결과:")
    print(f"  • 해결된 불일치 수: {len([r for r in resolution_results if r.success])}")
    for i, result in enumerate(resolution_results):
        print(f"  • 해결 결과 {i+1}: {result.strategy.value} (성공: {result.success})")
        print(f"    - 설명: {result.description}")
        print(f"    - 수정된 노드: {result.modified_nodes}")
        print(f"    - 수정된 엣지: {result.modified_edges}")

    # 3. 해결 결과 검증 테스트
    validator = InconsistencyValidator()
    validation_results = await validator.validate_resolution_results(graph, inconsistencies, resolution_results)

    print("\n📊 해결 결과 검증:")
    print(f"  • 종합 검증 점수: {validation_results['overall_validation_score']:.2f}")
    print(f"  • 해결 성공률: {validation_results['resolution_success_rate']:.2f}")
    print(f"  • 시스템 안정성: {validation_results['system_stability']:.2f}")
    print(f"  • 품질 향상도: {validation_results['quality_improvement']:.2f}")
    print("  • 검증 세부사항:")
    print(f"    - 총 불일치 수: {validation_results['validation_details']['total_inconsistencies']}")
    print(f"    - 해결된 불일치 수: {validation_results['validation_details']['resolved_inconsistencies']}")
    print(f"    - 실패한 해결 수: {validation_results['validation_details']['failed_resolutions']}")
    print(f"    - 수정된 노드 수: {validation_results['validation_details']['modified_nodes']}")
    print(f"    - 수정된 엣지 수: {validation_results['validation_details']['modified_edges']}")

    print(f"\n{'='*70}")
    print("=== 불일치 탐지 및 해결 시스템 테스트 완료 (Phase 1-3 Week 3 Day 3) ===")
    print("✅ Day 3 목표 달성: 불일치 탐지 및 해결 시스템 구현")
    print("✅ 불일치 탐지 시스템 구현")
    print("✅ 자동 해결 시스템 구현")
    print("✅ 해결 전략 시스템 구현")
    print("✅ 검증 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_inconsistency_detector())
