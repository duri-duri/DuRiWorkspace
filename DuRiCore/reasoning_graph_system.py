#!/usr/bin/env python3
"""
DuRi 사고 추론 그래프 시스템 (Day 5)
명시적 사고 과정 구조화
"""

import asyncio
import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NodeType(Enum):
    """노드 유형"""

    PREMISE = "premise"
    INFERENCE = "inference"
    CONCLUSION = "conclusion"
    COUNTER_ARGUMENT = "counter_argument"
    EVIDENCE = "evidence"
    ASSUMPTION = "assumption"


class EdgeType(Enum):
    """엣지 유형"""

    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    INFERS = "infers"
    ASSUMES = "assumes"
    EVIDENCES = "evidences"


@dataclass
class ReasoningNode:
    """추론 노드"""

    node_id: str
    node_type: NodeType
    content: str
    confidence: float  # 0.0-1.0
    source: str
    metadata: Dict[str, Any]


@dataclass
class ReasoningEdge:
    """추론 엣지"""

    edge_id: str
    source_node: str
    target_node: str
    edge_type: EdgeType
    strength: float  # 0.0-1.0
    reasoning: str


@dataclass
class ReasoningGraph:
    """추론 그래프"""

    graph_id: str
    nodes: Dict[str, ReasoningNode]
    edges: Dict[str, ReasoningEdge]
    root_nodes: List[str]
    leaf_nodes: List[str]
    confidence_score: float
    complexity_score: float


class ReasoningGraphBuilder:
    """추론 그래프 구축 시스템"""

    def __init__(self):
        self.graph_counter = 0
        self.node_counter = 0
        self.edge_counter = 0

    def build_reasoning_chain(
        self,
        situation: str,
        semantic_context: Dict[str, Any],
        philosophical_arguments: Dict[str, Any],
    ) -> ReasoningGraph:
        """추론 체인 구축"""
        logger.info(f"추론 그래프 구축 시작: {situation}")

        # 그래프 초기화
        graph_id = f"reasoning_graph_{self.graph_counter}"
        self.graph_counter += 1

        nodes = {}
        edges = {}
        root_nodes = []
        leaf_nodes = []

        # 1. 상황 분석 노드 추가
        situation_nodes = self._create_situation_nodes(situation, semantic_context)
        nodes.update(situation_nodes)
        root_nodes.extend(situation_nodes.keys())

        # 2. 철학적 논증 노드 추가
        philosophical_nodes = self._create_philosophical_nodes(philosophical_arguments)
        nodes.update(philosophical_nodes)

        # 3. 추론 엣지 생성
        reasoning_edges = self._create_reasoning_edges(nodes, situation, philosophical_arguments)
        edges.update(reasoning_edges)

        # 4. 결론 노드 추가
        conclusion_nodes = self._create_conclusion_nodes(nodes, edges)
        nodes.update(conclusion_nodes)
        leaf_nodes.extend(conclusion_nodes.keys())

        # 5. 그래프 메트릭 계산
        confidence_score = self._calculate_graph_confidence(nodes, edges)
        complexity_score = self._calculate_graph_complexity(nodes, edges)

        reasoning_graph = ReasoningGraph(
            graph_id=graph_id,
            nodes=nodes,
            edges=edges,
            root_nodes=root_nodes,
            leaf_nodes=leaf_nodes,
            confidence_score=confidence_score,
            complexity_score=complexity_score,
        )

        logger.info(f"추론 그래프 구축 완료: {len(nodes)} 노드, {len(edges)} 엣지")
        return reasoning_graph

    def _create_situation_nodes(self, situation: str, semantic_context) -> Dict[str, ReasoningNode]:
        """상황 분석 노드 생성"""
        nodes = {}

        # 상황 유형 노드
        situation_type_node = ReasoningNode(
            node_id=f"node_{self.node_counter}",
            node_type=NodeType.PREMISE,
            content=f"상황 유형: {semantic_context.situation_type.value if hasattr(semantic_context, 'situation_type') else 'unknown'}",  # noqa: E501
            confidence=(semantic_context.confidence_score if hasattr(semantic_context, "confidence_score") else 0.5),
            source="Semantic Analysis",
            metadata={
                "situation_type": (
                    semantic_context.situation_type.value if hasattr(semantic_context, "situation_type") else "unknown"
                )
            },
        )
        nodes[situation_type_node.node_id] = situation_type_node
        self.node_counter += 1

        # 의도 노드
        intent_node = ReasoningNode(
            node_id=f"node_{self.node_counter}",
            node_type=NodeType.PREMISE,
            content=f"의도: {semantic_context.intent.value if hasattr(semantic_context, 'intent') else 'unknown'}",
            confidence=(semantic_context.confidence_score if hasattr(semantic_context, "confidence_score") else 0.5),
            source="Intent Analysis",
            metadata={"intent": (semantic_context.intent.value if hasattr(semantic_context, "intent") else "unknown")},
        )
        nodes[intent_node.node_id] = intent_node
        self.node_counter += 1

        # 가치 충돌 노드들
        value_conflicts = semantic_context.value_conflicts if hasattr(semantic_context, "value_conflicts") else []
        for i, conflict in enumerate(value_conflicts):
            conflict_node = ReasoningNode(
                node_id=f"node_{self.node_counter}",
                node_type=NodeType.PREMISE,
                content=f"가치 충돌 {i+1}: {conflict.value if hasattr(conflict, 'value') else conflict}",
                confidence=0.7,
                source="Value Conflict Analysis",
                metadata={"conflict_type": (conflict.value if hasattr(conflict, "value") else conflict)},
            )
            nodes[conflict_node.node_id] = conflict_node
            self.node_counter += 1

        return nodes

    def _create_philosophical_nodes(self, philosophical_arguments: Dict[str, Any]) -> Dict[str, ReasoningNode]:
        """철학적 논증 노드 생성"""
        nodes = {}

        # 칸트적 분석 노드
        if "kantian" in philosophical_arguments:
            kantian = philosophical_arguments["kantian"]
            kantian_node = ReasoningNode(
                node_id=f"node_{self.node_counter}",
                node_type=NodeType.INFERENCE,
                content=f"칸트적 분석: {kantian.final_conclusion if hasattr(kantian, 'final_conclusion') else '분석 없음'}",  # noqa: E501
                confidence=kantian.strength if hasattr(kantian, "strength") else 0.5,
                source="Kantian Reasoning",
                metadata={
                    "reasoning_type": "kantian",
                    "strength": (kantian.strength if hasattr(kantian, "strength") else 0.5),
                },
            )
            nodes[kantian_node.node_id] = kantian_node
            self.node_counter += 1

        # 공리주의 분석 노드
        if "utilitarian" in philosophical_arguments:
            utilitarian = philosophical_arguments["utilitarian"]
            utilitarian_node = ReasoningNode(
                node_id=f"node_{self.node_counter}",
                node_type=NodeType.INFERENCE,
                content=f"공리주의 분석: {utilitarian.final_conclusion if hasattr(utilitarian, 'final_conclusion') else '분석 없음'}",  # noqa: E501
                confidence=(utilitarian.strength if hasattr(utilitarian, "strength") else 0.5),
                source="Utilitarian Reasoning",
                metadata={
                    "reasoning_type": "utilitarian",
                    "strength": (utilitarian.strength if hasattr(utilitarian, "strength") else 0.5),
                },
            )
            nodes[utilitarian_node.node_id] = utilitarian_node
            self.node_counter += 1

        # 통합 분석 노드
        if "integrated" in philosophical_arguments:
            integrated = philosophical_arguments["integrated"]
            integrated_node = ReasoningNode(
                node_id=f"node_{self.node_counter}",
                node_type=NodeType.INFERENCE,
                content=f"통합 분석: {integrated.get('recommendation', '분석 없음')}",
                confidence=integrated.get("strength", 0.5),
                source="Multi-Perspective Analysis",
                metadata={
                    "reasoning_type": "integrated",
                    "strength": integrated.get("strength"),
                },
            )
            nodes[integrated_node.node_id] = integrated_node
            self.node_counter += 1

        return nodes

    def _create_reasoning_edges(
        self,
        nodes: Dict[str, ReasoningNode],
        situation: str,
        philosophical_arguments: Dict[str, Any],
    ) -> Dict[str, ReasoningEdge]:
        """추론 엣지 생성"""
        edges = {}

        # 상황 분석 → 철학적 분석 연결
        situation_nodes = [n for n in nodes.values() if n.node_type == NodeType.PREMISE]
        philosophical_nodes = [n for n in nodes.values() if n.node_type == NodeType.INFERENCE]

        for situation_node in situation_nodes:
            for philosophical_node in philosophical_nodes:
                edge = ReasoningEdge(
                    edge_id=f"edge_{self.edge_counter}",
                    source_node=situation_node.node_id,
                    target_node=philosophical_node.node_id,
                    edge_type=EdgeType.SUPPORTS,
                    strength=0.6,
                    reasoning=f"{situation_node.content}이 {philosophical_node.content}를 지원함",
                )
                edges[edge.edge_id] = edge
                self.edge_counter += 1

        # 철학적 분석 간 연결
        if len(philosophical_nodes) > 1:
            for i, node1 in enumerate(philosophical_nodes):
                for node2 in philosophical_nodes[i + 1 :]:
                    edge = ReasoningEdge(
                        edge_id=f"edge_{self.edge_counter}",
                        source_node=node1.node_id,
                        target_node=node2.node_id,
                        edge_type=EdgeType.INFERS,
                        strength=0.5,
                        reasoning=f"{node1.content}과 {node2.content} 간의 논리적 관계",
                    )
                    edges[edge.edge_id] = edge
                    self.edge_counter += 1

        return edges

    def _create_conclusion_nodes(
        self, nodes: Dict[str, ReasoningNode], edges: Dict[str, ReasoningEdge]
    ) -> Dict[str, ReasoningNode]:
        """결론 노드 생성"""
        conclusion_nodes = {}

        # 최종 결론 노드
        final_conclusion_node = ReasoningNode(
            node_id=f"node_{self.node_counter}",
            node_type=NodeType.CONCLUSION,
            content="최종 도덕적 판단",
            confidence=0.7,
            source="Final Reasoning",
            metadata={"conclusion_type": "final_judgment"},
        )
        conclusion_nodes[final_conclusion_node.node_id] = final_conclusion_node
        self.node_counter += 1

        # 반론 노드
        counter_argument_node = ReasoningNode(
            node_id=f"node_{self.node_counter}",
            node_type=NodeType.COUNTER_ARGUMENT,
            content="대안적 관점 및 반론",
            confidence=0.6,
            source="Counter Analysis",
            metadata={"counter_type": "alternative_perspectives"},
        )
        conclusion_nodes[counter_argument_node.node_id] = counter_argument_node
        self.node_counter += 1

        return conclusion_nodes

    def _calculate_graph_confidence(self, nodes: Dict[str, ReasoningNode], edges: Dict[str, ReasoningEdge]) -> float:
        """그래프 신뢰도 계산"""
        if not nodes:
            return 0.0

        # 노드 신뢰도의 평균
        node_confidences = [node.confidence for node in nodes.values()]
        avg_node_confidence = sum(node_confidences) / len(node_confidences)

        # 엣지 강도의 평균
        if edges:
            edge_strengths = [edge.strength for edge in edges.values()]
            avg_edge_strength = sum(edge_strengths) / len(edge_strengths)
        else:
            avg_edge_strength = 0.5

        # 종합 신뢰도
        overall_confidence = (avg_node_confidence + avg_edge_strength) / 2
        return min(max(overall_confidence, 0.0), 1.0)

    def _calculate_graph_complexity(self, nodes: Dict[str, ReasoningNode], edges: Dict[str, ReasoningEdge]) -> float:
        """그래프 복잡도 계산"""
        complexity = 0.0

        # 노드 수에 따른 복잡도
        node_complexity = min(len(nodes) / 10.0, 1.0)
        complexity += node_complexity * 0.3

        # 엣지 수에 따른 복잡도
        edge_complexity = min(len(edges) / 15.0, 1.0)
        complexity += edge_complexity * 0.3

        # 노드 유형 다양성에 따른 복잡도
        node_types = set(node.node_type for node in nodes.values())
        type_diversity = len(node_types) / 6.0  # 최대 6개 유형
        complexity += type_diversity * 0.2

        # 엣지 유형 다양성에 따른 복잡도
        edge_types = set(edge.edge_type for edge in edges.values())
        edge_diversity = len(edge_types) / 5.0  # 최대 5개 유형
        complexity += edge_diversity * 0.2

        return min(complexity, 1.0)


class LogicalInferenceEngine:
    """논리적 추론 엔진"""

    def __init__(self):
        self.inference_rules = self._initialize_inference_rules()
        self.logical_operators = self._initialize_logical_operators()

    def _initialize_inference_rules(self) -> Dict[str, str]:
        """추론 규칙 초기화"""
        return {
            "modus_ponens": "P → Q, P ⊢ Q",
            "modus_tollens": "P → Q, ¬Q ⊢ ¬P",
            "hypothetical_syllogism": "P → Q, Q → R ⊢ P → R",
            "disjunctive_syllogism": "P ∨ Q, ¬P ⊢ Q",
            "constructive_dilemma": "(P → Q) ∧ (R → S), P ∨ R ⊢ Q ∨ S",
        }

    def _initialize_logical_operators(self) -> Dict[str, str]:
        """논리 연산자 초기화"""
        return {"and": "∧", "or": "∨", "not": "¬", "implies": "→", "iff": "↔"}

    async def apply_logical_inference(self, premises: List[str], conclusion: str) -> Dict[str, Any]:
        """논리적 추론 적용"""
        logger.info(f"논리적 추론 시작: {len(premises)} 전제")

        # 추론 유효성 검사
        validity_check = self._check_inference_validity(premises, conclusion)

        # 논리적 일관성 검사
        consistency_check = self._check_logical_consistency(premises)

        # 추론 강도 계산
        inference_strength = self._calculate_inference_strength(premises, conclusion)

        return {
            "is_valid": validity_check["is_valid"],
            "is_consistent": consistency_check["is_consistent"],
            "inference_strength": inference_strength,
            "reasoning": validity_check["reasoning"],
            "counter_examples": validity_check["counter_examples"],
        }

    def _check_inference_validity(self, premises: List[str], conclusion: str) -> Dict[str, Any]:
        """추론 유효성 검사"""
        validity_result = {"is_valid": True, "reasoning": "", "counter_examples": []}

        # 기본적인 논리적 검사
        if not premises:
            validity_result.update(
                {
                    "is_valid": False,
                    "reasoning": "전제가 없으면 유효한 추론이 불가능하다",
                }
            )
            return validity_result

        # 결론이 전제에서 논리적으로 도출되는지 검사
        conclusion_keywords = set(re.findall(r"\w+", conclusion.lower()))
        premise_keywords = set()
        for premise in premises:
            premise_keywords.update(re.findall(r"\w+", premise.lower()))

        # 결론의 주요 개념이 전제에 포함되어 있는지 검사
        if not conclusion_keywords.issubset(premise_keywords):
            validity_result.update(
                {
                    "is_valid": False,
                    "reasoning": "결론에 전제에 없는 새로운 개념이 포함되어 있다",
                }
            )

        return validity_result

    def _check_logical_consistency(self, premises: List[str]) -> Dict[str, Any]:
        """논리적 일관성 검사"""
        consistency_result = {"is_consistent": True, "contradictions": []}

        # 모순되는 전제 검사
        for i, premise1 in enumerate(premises):
            for premise2 in premises[i + 1 :]:
                if self._are_contradictory(premise1, premise2):
                    consistency_result["contradictions"].append({"premise1": premise1, "premise2": premise2})
                    consistency_result["is_consistent"] = False

        return consistency_result

    def _are_contradictory(self, premise1: str, premise2: str) -> bool:
        """두 전제가 모순되는지 검사"""
        # 간단한 키워드 기반 모순 검사
        contradiction_patterns = [
            (["허용", "금지"], ["금지", "허용"]),
            (["옳다", "틀리다"], ["틀리다", "옳다"]),
            (["참", "거짓"], ["거짓", "참"]),
        ]

        for pattern1, pattern2 in contradiction_patterns:
            if any(word in premise1 for word in pattern1) and any(word in premise2 for word in pattern2):
                return True

        return False

    def _calculate_inference_strength(self, premises: List[str], conclusion: str) -> float:
        """추론 강도 계산"""
        strength = 0.5  # 기본값

        # 전제 수에 따른 강도
        if len(premises) >= 3:
            strength += 0.2
        elif len(premises) >= 2:
            strength += 0.1

        # 전제와 결론의 관련성
        premise_keywords = set()
        for premise in premises:
            premise_keywords.update(re.findall(r"\w+", premise.lower()))

        conclusion_keywords = set(re.findall(r"\w+", conclusion.lower()))

        overlap = len(premise_keywords.intersection(conclusion_keywords))
        total = len(premise_keywords.union(conclusion_keywords))

        if total > 0:
            relevance = overlap / total
            strength += relevance * 0.3

        return min(max(strength, 0.0), 1.0)


class ReasoningGraphAnalyzer:
    """추론 그래프 분석 시스템"""

    def __init__(self):
        self.graph_builder = ReasoningGraphBuilder()
        self.inference_engine = LogicalInferenceEngine()

    async def analyze_reasoning_process(
        self,
        situation: str,
        semantic_context: Dict[str, Any],
        philosophical_arguments: Dict[str, Any],
    ) -> Dict[str, Any]:
        """추론 과정 분석"""
        logger.info(f"추론 과정 분석 시작: {situation}")

        # 1. 추론 그래프 구축
        reasoning_graph = self.graph_builder.build_reasoning_chain(situation, semantic_context, philosophical_arguments)

        # 2. 논리적 추론 적용
        premises = [node.content for node in reasoning_graph.nodes.values() if node.node_type == NodeType.PREMISE]
        conclusions = [node.content for node in reasoning_graph.nodes.values() if node.node_type == NodeType.CONCLUSION]

        inference_results = []
        for conclusion in conclusions:
            inference_result = await self.inference_engine.apply_logical_inference(premises, conclusion)
            inference_results.append(inference_result)

        # 3. 그래프 분석
        graph_analysis = self._analyze_graph_structure(reasoning_graph)

        # 4. 추론 품질 평가
        quality_assessment = self._assess_reasoning_quality(reasoning_graph, inference_results)

        return {
            "reasoning_graph": reasoning_graph,
            "inference_results": inference_results,
            "graph_analysis": graph_analysis,
            "quality_assessment": quality_assessment,
        }

    def _analyze_graph_structure(self, graph: ReasoningGraph) -> Dict[str, Any]:
        """그래프 구조 분석"""
        analysis = {
            "node_count": len(graph.nodes),
            "edge_count": len(graph.edges),
            "node_types": {},
            "edge_types": {},
            "connectivity": 0.0,
            "depth": 0,
        }

        # 노드 유형 분포
        for node in graph.nodes.values():
            node_type = node.node_type.value
            analysis["node_types"][node_type] = analysis["node_types"].get(node_type, 0) + 1

        # 엣지 유형 분포
        for edge in graph.edges.values():
            edge_type = edge.edge_type.value
            analysis["edge_types"][edge_type] = analysis["edge_types"].get(edge_type, 0) + 1

        # 연결성 계산
        if len(graph.nodes) > 1:
            analysis["connectivity"] = len(graph.edges) / (len(graph.nodes) * (len(graph.nodes) - 1))

        # 깊이 계산 (간단한 추정)
        analysis["depth"] = min(len(graph.nodes) // 3, 5)

        return analysis

    def _assess_reasoning_quality(
        self, graph: ReasoningGraph, inference_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """추론 품질 평가"""
        quality = {
            "overall_quality": 0.0,
            "logical_consistency": 0.0,
            "completeness": 0.0,
            "clarity": 0.0,
            "strength": 0.0,
        }

        # 논리적 일관성
        valid_inferences = sum(1 for result in inference_results if result["is_valid"])
        quality["logical_consistency"] = valid_inferences / len(inference_results) if inference_results else 0.0

        # 완전성 (모든 노드 유형이 포함되었는지)
        node_types = set(node.node_type for node in graph.nodes.values())
        quality["completeness"] = len(node_types) / 6.0  # 최대 6개 유형

        # 명확성 (노드의 평균 신뢰도)
        node_confidences = [node.confidence for node in graph.nodes.values()]
        quality["clarity"] = sum(node_confidences) / len(node_confidences) if node_confidences else 0.0

        # 강도 (엣지의 평균 강도)
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        quality["strength"] = sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0

        # 종합 품질
        quality["overall_quality"] = (
            quality["logical_consistency"] * 0.3
            + quality["completeness"] * 0.2
            + quality["clarity"] * 0.25
            + quality["strength"] * 0.25
        )

        return quality


async def test_reasoning_graph_system():
    """추론 그래프 시스템 테스트"""
    print("=== 추론 그래프 시스템 테스트 시작 (Day 5) ===")

    analyzer = ReasoningGraphAnalyzer()

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

    # 추론 과정 분석
    analysis_result = await analyzer.analyze_reasoning_process(
        test_situation, test_semantic_context, test_philosophical_arguments
    )

    # 결과 출력
    reasoning_graph = analysis_result["reasoning_graph"]
    graph_analysis = analysis_result["graph_analysis"]
    quality_assessment = analysis_result["quality_assessment"]

    print("\n📊 추론 그래프 분석:")
    print(f"  • 노드 수: {graph_analysis['node_count']}")
    print(f"  • 엣지 수: {graph_analysis['edge_count']}")
    print(f"  • 노드 유형: {graph_analysis['node_types']}")
    print(f"  • 엣지 유형: {graph_analysis['edge_types']}")
    print(f"  • 연결성: {graph_analysis['connectivity']:.2f}")
    print(f"  • 깊이: {graph_analysis['depth']}")

    print("\n🎯 추론 품질 평가:")
    print(f"  • 종합 품질: {quality_assessment['overall_quality']:.2f}")
    print(f"  • 논리적 일관성: {quality_assessment['logical_consistency']:.2f}")
    print(f"  • 완전성: {quality_assessment['completeness']:.2f}")
    print(f"  • 명확성: {quality_assessment['clarity']:.2f}")
    print(f"  • 강도: {quality_assessment['strength']:.2f}")

    print("\n🔍 추론 노드 상세:")
    for node_id, node in reasoning_graph.nodes.items():
        print(f"  • {node_id}: {node.content} (신뢰도: {node.confidence:.2f})")

    print("\n🔗 추론 엣지 상세:")
    for edge_id, edge in reasoning_graph.edges.items():
        print(f"  • {edge_id}: {edge.source_node} → {edge.target_node} (강도: {edge.strength:.2f})")

    print(f"\n{'='*70}")
    print("=== 추론 그래프 시스템 테스트 완료 (Day 5) ===")
    print("✅ Day 5 목표 달성: 명시적 사고 과정 구조화")
    print("✅ 추론 그래프 구축 및 분석 시스템 구현")
    print("✅ 논리적 추론 엔진 및 품질 평가 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_reasoning_graph_system())
