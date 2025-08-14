#!/usr/bin/env python3
"""
DuRi 실시간 그래프 진화 시스템 - Phase 1-3 Week 3 Day 4
동적 추론 그래프의 실시간 진화를 관리하는 시스템

기능:
1. 동적 노드 생성 시스템
2. 동적 엣지 생성 시스템
3. 그래프 진화 시스템
4. 진화 검증 시스템
"""

import asyncio
import json
import re
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import logging
from collections import defaultdict, deque
import heapq
import random

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

class EvolutionTrigger(Enum):
    """진화 트리거 유형"""
    SITUATION_CHANGE = "situation_change"
    NEW_EVIDENCE = "new_evidence"
    CONTRADICTION_DETECTED = "contradiction_detected"
    QUALITY_DEGRADATION = "quality_degradation"
    USER_INPUT = "user_input"
    AUTOMATIC_REFRESH = "automatic_refresh"

class EvolutionStrategy(Enum):
    """진화 전략"""
    CONSERVATIVE = "conservative"  # 보수적 진화
    MODERATE = "moderate"          # 중간 진화
    AGGRESSIVE = "aggressive"      # 적극적 진화
    ADAPTIVE = "adaptive"          # 적응적 진화

@dataclass
class EvolutionEvent:
    """진화 이벤트"""
    event_id: str
    trigger: EvolutionTrigger
    timestamp: datetime
    description: str
    affected_nodes: List[str] = field(default_factory=list)
    affected_edges: List[str] = field(default_factory=list)
    evolution_data: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvolutionResult:
    """진화 결과"""
    evolution_id: str
    strategy: EvolutionStrategy
    success: bool
    confidence: float
    description: str
    new_nodes: List[str] = field(default_factory=list)
    new_edges: List[str] = field(default_factory=list)
    modified_nodes: List[str] = field(default_factory=list)
    modified_edges: List[str] = field(default_factory=list)
    removed_nodes: List[str] = field(default_factory=list)
    removed_edges: List[str] = field(default_factory=list)
    evolution_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class DynamicNodeGenerator:
    """동적 노드 생성 시스템"""
    
    def __init__(self):
        self.node_templates = self._initialize_node_templates()
        self.generation_rules = self._initialize_generation_rules()
    
    def _initialize_node_templates(self) -> Dict[str, Dict[str, Any]]:
        """노드 템플릿 초기화"""
        return {
            "premise": {
                "confidence_range": (0.6, 0.9),
                "importance_range": (0.5, 0.8),
                "content_patterns": [
                    "상황: {context}",
                    "전제: {context}",
                    "가정: {context}",
                    "배경: {context}"
                ]
            },
            "inference": {
                "confidence_range": (0.5, 0.8),
                "importance_range": (0.6, 0.9),
                "content_patterns": [
                    "{reasoning_type} 분석: {content}",
                    "추론: {content}",
                    "분석: {content}",
                    "평가: {content}"
                ]
            },
            "evidence": {
                "confidence_range": (0.7, 0.95),
                "importance_range": (0.7, 0.9),
                "content_patterns": [
                    "증거: {content}",
                    "사실: {content}",
                    "데이터: {content}",
                    "관찰: {content}"
                ]
            },
            "conclusion": {
                "confidence_range": (0.6, 0.9),
                "importance_range": (0.8, 1.0),
                "content_patterns": [
                    "결론: {content}",
                    "판단: {content}",
                    "결정: {content}",
                    "의견: {content}"
                ]
            },
            "counter_argument": {
                "confidence_range": (0.4, 0.7),
                "importance_range": (0.5, 0.8),
                "content_patterns": [
                    "반론: {content}",
                    "이의: {content}",
                    "문제점: {content}",
                    "우려: {content}"
                ]
            }
        }
    
    def _initialize_generation_rules(self) -> Dict[str, Dict[str, Any]]:
        """생성 규칙 초기화"""
        return {
            "situation_change": {
                "node_types": ["premise", "inference"],
                "probability": 0.8,
                "max_nodes": 3
            },
            "new_evidence": {
                "node_types": ["evidence", "inference"],
                "probability": 0.9,
                "max_nodes": 2
            },
            "contradiction_detected": {
                "node_types": ["counter_argument", "inference"],
                "probability": 0.7,
                "max_nodes": 2
            },
            "quality_degradation": {
                "node_types": ["premise", "evidence", "inference"],
                "probability": 0.6,
                "max_nodes": 4
            }
        }
    
    async def generate_dynamic_nodes(self, graph: 'DynamicReasoningGraph', 
                                   trigger: EvolutionTrigger, 
                                   context: Dict[str, Any]) -> List['DynamicReasoningNode']:
        """동적 노드 생성"""
        logger.info(f"동적 노드 생성 시작: {trigger.value}")
        
        new_nodes = []
        rules = self.generation_rules.get(trigger.value, {})
        
        if not rules or random.random() > rules.get("probability", 0.5):
            return new_nodes
        
        max_nodes = rules.get("max_nodes", 2)
        node_types = rules.get("node_types", ["inference"])
        
        for _ in range(random.randint(1, max_nodes)):
            node_type = random.choice(node_types)
            new_node = await self._create_node(node_type, context, graph)
            if new_node:
                new_nodes.append(new_node)
        
        logger.info(f"동적 노드 생성 완료: {len(new_nodes)}개 생성")
        return new_nodes
    
    async def _create_node(self, node_type: str, context: Dict[str, Any], 
                          graph: 'DynamicReasoningGraph') -> Optional['DynamicReasoningNode']:
        """노드 생성"""
        template = self.node_templates.get(node_type)
        if not template:
            return None
        
        # 노드 ID 생성
        node_id = f"{node_type}_{len(graph.nodes) + 1}_{int(datetime.now().timestamp())}"
        
        # 내용 생성
        content = self._generate_content(node_type, context, template)
        
        # 신뢰도와 중요도 생성
        confidence = random.uniform(*template["confidence_range"])
        importance = random.uniform(*template["importance_range"])
        
        # NodeType 매핑 (소문자 -> 대문자)
        node_type_mapping = {
            "premise": NodeType.PREMISE,
            "inference": NodeType.INFERENCE,
            "conclusion": NodeType.CONCLUSION,
            "counter_argument": NodeType.COUNTER_ARGUMENT,
            "evidence": NodeType.EVIDENCE,
            "assumption": NodeType.ASSUMPTION,
            "hypothesis": NodeType.HYPOTHESIS,
            "constraint": NodeType.CONSTRAINT,
            "alternative": NodeType.ALTERNATIVE,
            "integration": NodeType.INTEGRATION
        }
        
        # 노드 생성
        node = DynamicReasoningNode(
            node_id=node_id,
            node_type=node_type_mapping.get(node_type, NodeType.INFERENCE),
            content=content,
            confidence=confidence,
            source="dynamic_generation",
            importance_score=importance
        )
        
        return node
    
    def _generate_content(self, node_type: str, context: Dict[str, Any], 
                         template: Dict[str, Any]) -> str:
        """내용 생성"""
        patterns = template.get("content_patterns", [f"{node_type}: {{content}}"])
        pattern = random.choice(patterns)
        
        # 컨텍스트에서 내용 추출
        content = context.get("content", f"동적으로 생성된 {node_type}")
        
        # 패턴에 맞게 내용 생성
        if "{context}" in pattern:
            context_content = context.get("context", content)
            return pattern.format(context=context_content)
        elif "{content}" in pattern:
            return pattern.format(content=content)
        elif "{reasoning_type}" in pattern:
            reasoning_types = ["논리적", "분석적", "체계적", "종합적"]
            reasoning_type = random.choice(reasoning_types)
            return pattern.format(reasoning_type=reasoning_type, content=content)
        else:
            return pattern

class DynamicEdgeGenerator:
    """동적 엣지 생성 시스템"""
    
    def __init__(self):
        self.edge_templates = self._initialize_edge_templates()
        self.connection_rules = self._initialize_connection_rules()
    
    def _initialize_edge_templates(self) -> Dict[str, Dict[str, Any]]:
        """엣지 템플릿 초기화"""
        return {
            "supports": {
                "strength_range": (0.6, 0.9),
                "reasoning_patterns": [
                    "지원: {source}가 {target}를 지원함",
                    "강화: {source}가 {target}를 강화함",
                    "확증: {source}가 {target}를 확증함"
                ]
            },
            "infers": {
                "strength_range": (0.5, 0.8),
                "reasoning_patterns": [
                    "추론: {source}에서 {target}를 추론함",
                    "연결: {source}가 {target}와 연결됨",
                    "전개: {source}에서 {target}로 전개됨"
                ]
            },
            "evidences": {
                "strength_range": (0.7, 0.95),
                "reasoning_patterns": [
                    "증거: {source}가 {target}의 증거가 됨",
                    "입증: {source}가 {target}를 입증함",
                    "지지: {source}가 {target}를 지지함"
                ]
            },
            "challenges": {
                "strength_range": (0.4, 0.7),
                "reasoning_patterns": [
                    "도전: {source}가 {target}에 도전함",
                    "의문: {source}가 {target}에 의문을 제기함",
                    "반박: {source}가 {target}를 반박함"
                ]
            }
        }
    
    def _initialize_connection_rules(self) -> Dict[str, Dict[str, Any]]:
        """연결 규칙 초기화"""
        return {
            "premise": {
                "can_connect_to": ["inference", "conclusion"],
                "preferred_edge_types": ["supports", "infers"],
                "max_connections": 3
            },
            "inference": {
                "can_connect_to": ["conclusion", "counter_argument", "evidence"],
                "preferred_edge_types": ["infers", "supports"],
                "max_connections": 4
            },
            "evidence": {
                "can_connect_to": ["inference", "conclusion", "premise"],
                "preferred_edge_types": ["evidences", "supports"],
                "max_connections": 3
            },
            "conclusion": {
                "can_connect_to": ["counter_argument", "inference"],
                "preferred_edge_types": ["challenges", "supports"],
                "max_connections": 2
            },
            "counter_argument": {
                "can_connect_to": ["conclusion", "inference"],
                "preferred_edge_types": ["challenges", "contradicts"],
                "max_connections": 2
            }
        }
    
    async def generate_dynamic_edges(self, graph: 'DynamicReasoningGraph', 
                                   new_nodes: List['DynamicReasoningNode']) -> List['DynamicReasoningEdge']:
        """동적 엣지 생성"""
        logger.info(f"동적 엣지 생성 시작: {len(new_nodes)}개 새 노드")
        
        new_edges = []
        
        for new_node in new_nodes:
            # 새 노드와 기존 노드 간의 연결 생성
            connections = await self._create_connections(new_node, graph)
            new_edges.extend(connections)
            
            # 새 노드들 간의 연결 생성
            for other_node in new_nodes:
                if new_node.node_id != other_node.node_id:
                    connection = await self._create_connection(new_node, other_node)
                    if connection:
                        new_edges.append(connection)
        
        logger.info(f"동적 엣지 생성 완료: {len(new_edges)}개 생성")
        return new_edges
    
    async def _create_connections(self, new_node: 'DynamicReasoningNode', 
                                graph: 'DynamicReasoningGraph') -> List['DynamicReasoningEdge']:
        """연결 생성"""
        connections = []
        rules = self.connection_rules.get(new_node.node_type.value, {})
        
        if not rules:
            return connections
        
        can_connect_to = rules.get("can_connect_to", [])
        max_connections = rules.get("max_connections", 2)
        
        # 연결 가능한 노드들 찾기
        potential_targets = []
        for node in graph.nodes.values():
            if node.node_type.value in can_connect_to:
                # 의미적 유사도 계산
                similarity = self._calculate_semantic_similarity(new_node.content, node.content)
                if similarity > 0.1:  # 최소 유사도 임계값
                    potential_targets.append((node, similarity))
        
        # 유사도 순으로 정렬
        potential_targets.sort(key=lambda x: x[1], reverse=True)
        
        # 연결 생성
        for target_node, similarity in potential_targets[:max_connections]:
            edge = await self._create_connection(new_node, target_node, similarity)
            if edge:
                connections.append(edge)
        
        return connections
    
    async def _create_connection(self, source_node: 'DynamicReasoningNode', 
                               target_node: 'DynamicReasoningNode', 
                               similarity: float = 0.0) -> Optional['DynamicReasoningEdge']:
        """연결 생성"""
        # 엣지 유형 결정
        edge_type = self._determine_edge_type(source_node, target_node)
        if not edge_type:
            return None
        
        # 엣지 템플릿 가져오기
        template = self.edge_templates.get(edge_type.value, {})
        strength_range = template.get("strength_range", (0.5, 0.8))
        
        # 강도 계산 (유사도 기반)
        base_strength = random.uniform(*strength_range)
        strength = min(1.0, base_strength + similarity * 0.3)
        
        # 추론 생성
        reasoning_patterns = template.get("reasoning_patterns", [f"{edge_type.value}: {{source}} -> {{target}}"])
        reasoning = random.choice(reasoning_patterns).format(
            source=source_node.content[:20],
            target=target_node.content[:20]
        )
        
        # 엣지 생성
        edge_id = f"edge_{source_node.node_id}_{target_node.node_id}_{int(datetime.now().timestamp())}"
        edge = DynamicReasoningEdge(
            edge_id=edge_id,
            source_node=source_node.node_id,
            target_node=target_node.node_id,
            edge_type=edge_type,
            strength=strength,
            reasoning=reasoning,
            semantic_similarity=similarity
        )
        
        return edge
    
    def _determine_edge_type(self, source_node: 'DynamicReasoningNode', 
                           target_node: 'DynamicReasoningNode') -> Optional[EdgeType]:
        """엣지 유형 결정"""
        source_type = source_node.node_type.value
        target_type = target_node.node_type.value
        
        # 노드 유형에 따른 엣지 유형 결정
        if source_type == "premise" and target_type in ["inference", "conclusion"]:
            return EdgeType.SUPPORTS
        elif source_type == "inference" and target_type == "conclusion":
            return EdgeType.INFERS
        elif source_type == "evidence" and target_type in ["inference", "conclusion"]:
            return EdgeType.EVIDENCES
        elif source_type == "counter_argument" and target_type in ["conclusion", "inference"]:
            return EdgeType.CHALLENGES
        elif source_type == "inference" and target_type == "counter_argument":
            return EdgeType.CHALLENGES
        else:
            # 기본 연결
            return EdgeType.SUPPORTS
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """의미적 유사도 계산"""
        keywords1 = set(re.findall(r'\w+', text1.lower()))
        keywords2 = set(re.findall(r'\w+', text2.lower()))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0

class GraphEvolutionEngine:
    """그래프 진화 엔진"""
    
    def __init__(self):
        self.node_generator = DynamicNodeGenerator()
        self.edge_generator = DynamicEdgeGenerator()
        self.evolution_strategies = self._initialize_evolution_strategies()
        self.evolution_history = []
    
    def _initialize_evolution_strategies(self) -> Dict[str, Dict[str, Any]]:
        """진화 전략 초기화"""
        return {
            "conservative": {
                "node_generation_probability": 0.6,  # 0.3 -> 0.6
                "edge_generation_probability": 0.7,  # 0.4 -> 0.7
                "max_new_nodes": 2,
                "max_new_edges": 3,
                "description": "보수적 진화"
            },
            "moderate": {
                "node_generation_probability": 0.8,  # 0.6 -> 0.8
                "edge_generation_probability": 0.9,  # 0.7 -> 0.9
                "max_new_nodes": 4,
                "max_new_edges": 6,
                "description": "중간 진화"
            },
            "aggressive": {
                "node_generation_probability": 0.9,  # 0.8 -> 0.9
                "edge_generation_probability": 0.95, # 0.9 -> 0.95
                "max_new_nodes": 6,
                "max_new_edges": 10,
                "description": "적극적 진화"
            },
            "adaptive": {
                "node_generation_probability": 0.7,  # 0.5 -> 0.7
                "edge_generation_probability": 0.8,  # 0.6 -> 0.8
                "max_new_nodes": 3,
                "max_new_edges": 5,
                "description": "적응적 진화"
            }
        }
    
    async def evolve_graph(self, graph: 'DynamicReasoningGraph', 
                          trigger: EvolutionTrigger, 
                          context: Dict[str, Any],
                          strategy: EvolutionStrategy = EvolutionStrategy.MODERATE) -> EvolutionResult:
        """그래프 진화"""
        logger.info(f"그래프 진화 시작: {trigger.value} -> {strategy.value}")
        
        evolution_id = f"evolution_{int(datetime.now().timestamp())}"
        strategy_config = self.evolution_strategies.get(strategy.value, self.evolution_strategies["moderate"])
        
        # 진화 이벤트 생성
        evolution_event = EvolutionEvent(
            event_id=f"event_{evolution_id}",
            trigger=trigger,
            timestamp=datetime.now(),
            description=f"그래프 진화: {trigger.value} -> {strategy.value}",
            evolution_data=context
        )
        
        new_nodes = []
        new_edges = []
        modified_nodes = []
        modified_edges = []
        
        try:
            # 1. 동적 노드 생성
            if random.random() < strategy_config["node_generation_probability"]:
                new_nodes = await self.node_generator.generate_dynamic_nodes(
                    graph, trigger, context
                )
                
                # 노드 수 제한
                max_nodes = strategy_config["max_new_nodes"]
                if len(new_nodes) > max_nodes:
                    new_nodes = new_nodes[:max_nodes]
                
                # 그래프에 노드 추가
                for node in new_nodes:
                    graph.nodes[node.node_id] = node
                    modified_nodes.append(node.node_id)
            
            # 2. 동적 엣지 생성
            if random.random() < strategy_config["edge_generation_probability"]:
                new_edges = await self.edge_generator.generate_dynamic_edges(
                    graph, new_nodes
                )
                
                # 엣지 수 제한
                max_edges = strategy_config["max_new_edges"]
                if len(new_edges) > max_edges:
                    new_edges = new_edges[:max_edges]
                
                # 그래프에 엣지 추가
                for edge in new_edges:
                    graph.edges[edge.edge_id] = edge
                    modified_edges.append(edge.edge_id)
            
            # 3. 진화 메트릭 계산
            evolution_metrics = await self._calculate_evolution_metrics(graph, new_nodes, new_edges)
            
            # 4. 진화 결과 생성
            evolution_result = EvolutionResult(
                evolution_id=evolution_id,
                strategy=strategy,
                success=True,
                confidence=evolution_metrics.get("overall_confidence", 0.7),
                description=f"그래프 진화 완료: {len(new_nodes)}개 노드, {len(new_edges)}개 엣지 생성",
                new_nodes=[node.node_id for node in new_nodes],
                new_edges=[edge.edge_id for edge in new_edges],
                modified_nodes=modified_nodes,
                modified_edges=modified_edges,
                evolution_metrics=evolution_metrics
            )
            
            # 진화 이력에 추가
            self.evolution_history.append({
                "event": evolution_event,
                "result": evolution_result,
                "timestamp": datetime.now()
            })
            
            logger.info(f"그래프 진화 완료: {len(new_nodes)}개 노드, {len(new_edges)}개 엣지 생성")
            return evolution_result
            
        except Exception as e:
            logger.error(f"그래프 진화 실패: {e}")
            return EvolutionResult(
                evolution_id=evolution_id,
                strategy=strategy,
                success=False,
                confidence=0.0,
                description=f"그래프 진화 실패: {str(e)}"
            )
    
    async def _calculate_evolution_metrics(self, graph: 'DynamicReasoningGraph', 
                                         new_nodes: List['DynamicReasoningNode'],
                                         new_edges: List['DynamicReasoningEdge']) -> Dict[str, float]:
        """진화 메트릭 계산"""
        metrics = {}
        
        # 전체 노드 수
        total_nodes = len(graph.nodes)
        metrics["total_nodes"] = total_nodes
        
        # 전체 엣지 수
        total_edges = len(graph.edges)
        metrics["total_edges"] = total_edges
        
        # 새 노드 비율
        new_node_ratio = len(new_nodes) / total_nodes if total_nodes > 0 else 0.0
        metrics["new_node_ratio"] = new_node_ratio
        
        # 새 엣지 비율
        new_edge_ratio = len(new_edges) / total_edges if total_edges > 0 else 0.0
        metrics["new_edge_ratio"] = new_edge_ratio
        
        # 평균 신뢰도
        node_confidences = [node.confidence for node in graph.nodes.values()]
        avg_confidence = sum(node_confidences) / len(node_confidences) if node_confidences else 0.0
        metrics["avg_confidence"] = avg_confidence
        
        # 평균 강도
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        avg_strength = sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0
        metrics["avg_strength"] = avg_strength
        
        # 연결성
        connectivity = total_edges / (total_nodes * (total_nodes - 1) / 2) if total_nodes > 1 else 0.0
        metrics["connectivity"] = connectivity
        
        # 종합 신뢰도
        overall_confidence = (avg_confidence + avg_strength) / 2.0
        metrics["overall_confidence"] = overall_confidence
        
        return metrics

class EvolutionValidator:
    """진화 검증 시스템"""
    
    def __init__(self):
        self.validation_criteria = self._initialize_validation_criteria()
    
    def _initialize_validation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """검증 기준 초기화"""
        return {
            "evolution_success": {
                "weight": 0.3,
                "description": "진화 성공률"
            },
            "quality_improvement": {
                "weight": 0.3,
                "description": "품질 향상도"
            },
            "system_stability": {
                "weight": 0.2,
                "description": "시스템 안정성"
            },
            "evolution_efficiency": {
                "weight": 0.2,
                "description": "진화 효율성"
            }
        }
    
    async def validate_evolution(self, graph: 'DynamicReasoningGraph', 
                               evolution_result: EvolutionResult) -> Dict[str, Any]:
        """진화 검증"""
        logger.info(f"진화 검증 시작: {evolution_result.evolution_id}")
        
        # 1. 진화 성공률 평가
        evolution_success = self._evaluate_evolution_success(evolution_result)
        
        # 2. 품질 향상도 평가
        quality_improvement = await self._evaluate_quality_improvement(graph, evolution_result)
        
        # 3. 시스템 안정성 평가
        system_stability = await self._evaluate_system_stability(graph)
        
        # 4. 진화 효율성 평가
        evolution_efficiency = self._evaluate_evolution_efficiency(evolution_result)
        
        # 종합 검증 점수
        overall_score = (
            evolution_success * self.validation_criteria["evolution_success"]["weight"] +
            quality_improvement * self.validation_criteria["quality_improvement"]["weight"] +
            system_stability * self.validation_criteria["system_stability"]["weight"] +
            evolution_efficiency * self.validation_criteria["evolution_efficiency"]["weight"]
        )
        
        return {
            "overall_score": overall_score,
            "evolution_success": evolution_success,
            "quality_improvement": quality_improvement,
            "system_stability": system_stability,
            "evolution_efficiency": evolution_efficiency,
            "validation_details": {
                "new_nodes_count": len(evolution_result.new_nodes),
                "new_edges_count": len(evolution_result.new_edges),
                "modified_nodes_count": len(evolution_result.modified_nodes),
                "modified_edges_count": len(evolution_result.modified_edges),
                "evolution_metrics": evolution_result.evolution_metrics
            }
        }
    
    def _evaluate_evolution_success(self, evolution_result: EvolutionResult) -> float:
        """진화 성공률 평가"""
        if not evolution_result.success:
            return 0.0
        
        # 새 노드와 엣지 생성 성공도
        node_success = min(1.0, len(evolution_result.new_nodes) / 2.0)  # 최소 2개 노드 기준
        edge_success = min(1.0, len(evolution_result.new_edges) / 3.0)  # 최소 3개 엣지 기준
        
        return (node_success + edge_success) / 2.0
    
    async def _evaluate_quality_improvement(self, graph: 'DynamicReasoningGraph', 
                                          evolution_result: EvolutionResult) -> float:
        """품질 향상도 평가"""
        # 진화 메트릭 기반 품질 평가
        metrics = evolution_result.evolution_metrics
        
        # 신뢰도 향상
        confidence_improvement = metrics.get("avg_confidence", 0.0)
        
        # 연결성 향상
        connectivity_improvement = metrics.get("connectivity", 0.0)
        
        # 새 노드/엣지 비율 (적절한 수준)
        new_node_ratio = metrics.get("new_node_ratio", 0.0)
        new_edge_ratio = metrics.get("new_edge_ratio", 0.0)
        
        # 적절한 진화 수준 (너무 많거나 적으면 안됨)
        evolution_balance = 1.0 - abs(new_node_ratio - 0.1) - abs(new_edge_ratio - 0.15)
        evolution_balance = max(0.0, evolution_balance)
        
        # 종합 품질 점수
        quality_score = (
            confidence_improvement * 0.4 +
            connectivity_improvement * 0.3 +
            evolution_balance * 0.3
        )
        
        return quality_score
    
    async def _evaluate_system_stability(self, graph: 'DynamicReasoningGraph') -> float:
        """시스템 안정성 평가"""
        # 노드 신뢰도의 표준편차 (낮을수록 안정적)
        node_confidences = [node.confidence for node in graph.nodes.values()]
        if len(node_confidences) < 2:
            return 0.5
        
        confidence_std = np.std(node_confidences)
        stability_score = max(0.0, 1.0 - confidence_std)
        
        # 엣지 강도의 표준편차
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        if len(edge_strengths) < 2:
            return stability_score
        
        strength_std = np.std(edge_strengths)
        strength_stability = max(0.0, 1.0 - strength_std)
        
        return (stability_score + strength_stability) / 2.0
    
    def _evaluate_evolution_efficiency(self, evolution_result: EvolutionResult) -> float:
        """진화 효율성 평가"""
        # 진화 비용 대비 효과
        total_changes = (
            len(evolution_result.new_nodes) +
            len(evolution_result.new_edges) +
            len(evolution_result.modified_nodes) +
            len(evolution_result.modified_edges)
        )
        
        if total_changes == 0:
            return 0.0
        
        # 변화 대비 효과 (새 노드/엣지 비율)
        effective_changes = len(evolution_result.new_nodes) + len(evolution_result.new_edges)
        efficiency = effective_changes / total_changes if total_changes > 0 else 0.0
        
        return efficiency

async def test_graph_evolution_system():
    """실시간 그래프 진화 시스템 테스트"""
    print("=== 실시간 그래프 진화 시스템 테스트 시작 (Phase 1-3 Week 3 Day 4) ===")
    
    # 테스트 그래프 생성
    graph = DynamicReasoningGraph(graph_id="test_graph")
    
    # 초기 노드들 생성
    initial_nodes = {
        "node1": DynamicReasoningNode("node1", NodeType.PREMISE, "윤리적 행동은 옳다", 0.8, "test"),
        "node2": DynamicReasoningNode("node2", NodeType.INFERENCE, "칸트적 분석", 0.7, "test"),
        "node3": DynamicReasoningNode("node3", NodeType.CONCLUSION, "최종 판단", 0.9, "test")
    }
    
    graph.nodes = initial_nodes
    
    # 초기 엣지들 생성
    initial_edges = {
        "edge1": DynamicReasoningEdge("edge1", "node1", "node2", EdgeType.SUPPORTS, 0.8, "지원"),
        "edge2": DynamicReasoningEdge("edge2", "node2", "node3", EdgeType.INFERS, 0.9, "추론")
    }
    
    graph.edges = initial_edges
    
    print(f"\n📊 초기 그래프 상태:")
    print(f"  • 노드 수: {len(graph.nodes)}")
    print(f"  • 엣지 수: {len(graph.edges)}")
    
    # 1. 그래프 진화 엔진 테스트
    evolution_engine = GraphEvolutionEngine()
    
    # 다양한 진화 시나리오 테스트
    evolution_scenarios = [
        (EvolutionTrigger.SITUATION_CHANGE, {"context": "새로운 윤리적 상황 발생", "content": "상황 변화"}),
        (EvolutionTrigger.NEW_EVIDENCE, {"context": "새로운 증거 발견", "content": "증거 추가"}),
        (EvolutionTrigger.CONTRADICTION_DETECTED, {"context": "논리적 모순 발견", "content": "모순 해결"}),
        (EvolutionTrigger.QUALITY_DEGRADATION, {"context": "품질 저하 감지", "content": "품질 개선"})
    ]
    
    evolution_results = []
    
    for trigger, context in evolution_scenarios:
        print(f"\n🔄 진화 시나리오: {trigger.value}")
        
        # 진화 실행
        evolution_result = await evolution_engine.evolve_graph(
            graph, trigger, context, EvolutionStrategy.MODERATE
        )
        
        evolution_results.append(evolution_result)
        
        print(f"  • 진화 성공: {evolution_result.success}")
        print(f"  • 새 노드 수: {len(evolution_result.new_nodes)}")
        print(f"  • 새 엣지 수: {len(evolution_result.new_edges)}")
        print(f"  • 수정된 노드 수: {len(evolution_result.modified_nodes)}")
        print(f"  • 수정된 엣지 수: {len(evolution_result.modified_edges)}")
        
        if evolution_result.evolution_metrics:
            metrics = evolution_result.evolution_metrics
            print(f"  • 진화 메트릭:")
            print(f"    - 전체 노드 수: {metrics.get('total_nodes', 0)}")
            print(f"    - 전체 엣지 수: {metrics.get('total_edges', 0)}")
            print(f"    - 평균 신뢰도: {metrics.get('avg_confidence', 0.0):.2f}")
            print(f"    - 평균 강도: {metrics.get('avg_strength', 0.0):.2f}")
            print(f"    - 연결성: {metrics.get('connectivity', 0.0):.2f}")
    
    # 2. 진화 검증 테스트
    validator = EvolutionValidator()
    
    print(f"\n📊 진화 검증 결과:")
    for i, evolution_result in enumerate(evolution_results):
        if evolution_result.success:
            validation_result = await validator.validate_evolution(graph, evolution_result)
            
            print(f"  • 진화 {i+1} 검증:")
            print(f"    - 종합 점수: {validation_result['overall_score']:.2f}")
            print(f"    - 진화 성공률: {validation_result['evolution_success']:.2f}")
            print(f"    - 품질 향상도: {validation_result['quality_improvement']:.2f}")
            print(f"    - 시스템 안정성: {validation_result['system_stability']:.2f}")
            print(f"    - 진화 효율성: {validation_result['evolution_efficiency']:.2f}")
    
    # 3. 최종 그래프 상태
    print(f"\n📊 최종 그래프 상태:")
    print(f"  • 노드 수: {len(graph.nodes)} (증가: {len(graph.nodes) - len(initial_nodes)})")
    print(f"  • 엣지 수: {len(graph.edges)} (증가: {len(graph.edges) - len(initial_edges)})")
    
    # 노드 유형별 분포
    node_types = defaultdict(int)
    for node in graph.nodes.values():
        node_types[node.node_type.value] += 1
    
    print(f"  • 노드 유형별 분포:")
    for node_type, count in node_types.items():
        print(f"    - {node_type}: {count}개")
    
    print(f"\n{'='*70}")
    print("=== 실시간 그래프 진화 시스템 테스트 완료 (Phase 1-3 Week 3 Day 4) ===")
    print("✅ Day 4 목표 달성: 실시간 그래프 진화 시스템 구현")
    print("✅ 동적 노드 생성 시스템 구현")
    print("✅ 동적 엣지 생성 시스템 구현")
    print("✅ 그래프 진화 시스템 구현")
    print("✅ 진화 검증 시스템 구현")

if __name__ == "__main__":
    asyncio.run(test_graph_evolution_system()) 