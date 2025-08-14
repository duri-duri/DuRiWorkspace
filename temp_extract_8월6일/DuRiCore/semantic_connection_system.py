#!/usr/bin/env python3
"""
DuRi 의미 기반 노드 연결 시스템 - Phase 1-3 Week 3 Day 5
동적 추론 그래프의 의미 기반 노드 연결을 관리하는 시스템

기능:
1. 고급 의미적 유사도 계산
2. 의미 기반 연결 생성
3. 연결 최적화
4. 연결 검증
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
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

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

class SemanticSimilarityEngine:
    """고급 의미적 유사도 계산 엔진"""
    
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95
        )
        self.similarity_cache = {}
        self.max_cache_size = 1000
        self.similarity_methods = self._initialize_similarity_methods()
    
    def _initialize_similarity_methods(self) -> Dict[str, Dict[str, Any]]:
        """유사도 계산 방법 초기화"""
        return {
            "cosine_similarity": {
                "weight": 0.4,
                "description": "코사인 유사도"
            },
            "keyword_overlap": {
                "weight": 0.3,
                "description": "키워드 중복도"
            },
            "semantic_distance": {
                "weight": 0.2,
                "description": "의미적 거리"
            },
            "context_similarity": {
                "weight": 0.1,
                "description": "컨텍스트 유사도"
            }
        }
    
    async def calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """고급 의미적 유사도 계산"""
        # 캐시 확인
        cache_key = f"{hash(text1)}_{hash(text2)}"
        if cache_key in self.similarity_cache:
            return self.similarity_cache[cache_key]
        
        # 1. 코사인 유사도 계산
        cosine_sim = await self._calculate_cosine_similarity(text1, text2)
        
        # 2. 키워드 중복도 계산
        keyword_overlap = await self._calculate_keyword_overlap(text1, text2)
        
        # 3. 의미적 거리 계산
        semantic_distance = await self._calculate_semantic_distance(text1, text2)
        
        # 4. 컨텍스트 유사도 계산
        context_similarity = await self._calculate_context_similarity(text1, text2)
        
        # 종합 유사도 계산 (가중치 조정)
        overall_similarity = (
            cosine_sim * 0.3 +  # 0.4 -> 0.3
            keyword_overlap * 0.4 +  # 0.3 -> 0.4
            semantic_distance * 0.2 +  # 0.2 -> 0.2
            context_similarity * 0.1   # 0.1 -> 0.1
        )
        
        # 최소 유사도 보장
        overall_similarity = max(overall_similarity, keyword_overlap * 0.5)
        
        # 캐시에 저장
        if len(self.similarity_cache) < self.max_cache_size:
            self.similarity_cache[cache_key] = overall_similarity
        
        return overall_similarity
    
    async def _calculate_cosine_similarity(self, text1: str, text2: str) -> float:
        """코사인 유사도 계산"""
        try:
            # TF-IDF 벡터화
            texts = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            
            # 코사인 유사도 계산
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return float(similarity)
        except Exception as e:
            logger.warning(f"코사인 유사도 계산 실패: {e}")
            return 0.0
    
    async def _calculate_keyword_overlap(self, text1: str, text2: str) -> float:
        """키워드 중복도 계산"""
        # 키워드 추출 (한글과 영문 모두 지원)
        keywords1 = set(re.findall(r'[가-힣a-zA-Z]+', text1.lower()))
        keywords2 = set(re.findall(r'[가-힣a-zA-Z]+', text2.lower()))
        
        # 의미있는 키워드만 필터링 (길이가 2 이상인 단어)
        keywords1 = {word for word in keywords1 if len(word) >= 2}
        keywords2 = {word for word in keywords2 if len(word) >= 2}
        
        if not keywords1 or not keywords2:
            return 0.0
        
        # 중복 키워드 수
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        # Jaccard 유사도 계산
        jaccard_similarity = intersection / union if union > 0 else 0.0
        
        # 추가 가중치: 공통 키워드의 중요도
        common_keywords = keywords1.intersection(keywords2)
        if common_keywords:
            # 공통 키워드가 많을수록 높은 유사도
            keyword_bonus = min(0.4, len(common_keywords) * 0.15)
            jaccard_similarity += keyword_bonus
        
        # 최소 유사도 보장 (공통 키워드가 있으면)
        if common_keywords:
            jaccard_similarity = max(jaccard_similarity, 0.2)
        
        return min(1.0, jaccard_similarity)
    
    async def _calculate_semantic_distance(self, text1: str, text2: str) -> float:
        """의미적 거리 계산"""
        # 간단한 의미적 거리 계산 (1 - 유사도)
        keyword_overlap = await self._calculate_keyword_overlap(text1, text2)
        semantic_distance = 1.0 - keyword_overlap
        
        # 거리를 유사도로 변환 (거리가 가까울수록 유사도 높음)
        return max(0.0, 1.0 - semantic_distance)
    
    async def _calculate_context_similarity(self, text1: str, text2: str) -> float:
        """컨텍스트 유사도 계산"""
        # 문맥적 키워드 추출
        context_keywords1 = self._extract_context_keywords(text1)
        context_keywords2 = self._extract_context_keywords(text2)
        
        if not context_keywords1 or not context_keywords2:
            return 0.0
        
        # 컨텍스트 키워드 중복도
        intersection = len(context_keywords1.intersection(context_keywords2))
        union = len(context_keywords1.union(context_keywords2))
        
        return intersection / union if union > 0 else 0.0
    
    def _extract_context_keywords(self, text: str) -> Set[str]:
        """컨텍스트 키워드 추출"""
        # 의미있는 키워드만 추출 (길이가 3 이상인 단어)
        keywords = set()
        words = re.findall(r'\w+', text.lower())
        
        for word in words:
            if len(word) >= 3 and word not in ['the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use']:
                keywords.add(word)
        
        return keywords

class SemanticConnectionGenerator:
    """의미 기반 연결 생성 시스템"""
    
    def __init__(self):
        self.similarity_engine = SemanticSimilarityEngine()
        self.connection_rules = self._initialize_connection_rules()
        self.connection_cache = {}
        self.max_cache_size = 1000
    
    def _initialize_connection_rules(self) -> Dict[str, Dict[str, Any]]:
        """연결 규칙 초기화"""
        return {
            "high_similarity": {
                "threshold": 0.7,
                "edge_types": ["supports", "evidences", "infers"],
                "strength_range": (0.8, 1.0),
                "description": "높은 유사도 연결"
            },
            "medium_similarity": {
                "threshold": 0.4,
                "edge_types": ["supports", "infers", "assumes"],
                "strength_range": (0.5, 0.8),
                "description": "중간 유사도 연결"
            },
            "low_similarity": {
                "threshold": 0.2,
                "edge_types": ["challenges", "contradicts", "constrains"],
                "strength_range": (0.3, 0.6),
                "description": "낮은 유사도 연결"
            }
        }
    
    async def generate_semantic_connections(self, graph: 'DynamicReasoningGraph', 
                                          target_node: 'DynamicReasoningNode',
                                          max_connections: int = 5) -> List['DynamicReasoningEdge']:
        """의미 기반 연결 생성"""
        logger.info(f"의미 기반 연결 생성 시작: {target_node.node_id}")
        
        connections = []
        potential_connections = []
        
        # 모든 노드와의 유사도 계산
        for node_id, node in graph.nodes.items():
            if node_id != target_node.node_id:
                similarity = await self.similarity_engine.calculate_semantic_similarity(
                    target_node.content, node.content
                )
                
                if similarity > 0.05:  # 0.1 -> 0.05 (임계값 낮춤)
                    potential_connections.append((node, similarity))
        
        # 유사도 순으로 정렬
        potential_connections.sort(key=lambda x: x[1], reverse=True)
        
        # 연결 생성
        for node, similarity in potential_connections[:max_connections]:
            edge = await self._create_semantic_connection(target_node, node, similarity)
            if edge:
                connections.append(edge)
        
        logger.info(f"의미 기반 연결 생성 완료: {len(connections)}개 생성")
        return connections
    
    async def _create_semantic_connection(self, source_node: 'DynamicReasoningNode', 
                                        target_node: 'DynamicReasoningNode', 
                                        similarity: float) -> Optional['DynamicReasoningEdge']:
        """의미적 연결 생성"""
        # 연결 규칙 결정
        connection_rule = self._determine_connection_rule(similarity)
        if not connection_rule:
            return None
        
        # 엣지 유형 결정
        edge_type = self._determine_edge_type(source_node, target_node, similarity)
        if not edge_type:
            return None
        
        # 강도 계산
        strength_range = connection_rule["strength_range"]
        strength = random.uniform(*strength_range) * similarity
        
        # 추론 생성
        reasoning = self._generate_connection_reasoning(source_node, target_node, edge_type, similarity)
        
        # 엣지 생성
        edge_id = f"semantic_edge_{source_node.node_id}_{target_node.node_id}_{int(datetime.now().timestamp())}"
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
    
    def _determine_connection_rule(self, similarity: float) -> Optional[Dict[str, Any]]:
        """연결 규칙 결정"""
        for rule_name, rule in self.connection_rules.items():
            if similarity >= rule["threshold"]:
                return rule
        return None
    
    def _determine_edge_type(self, source_node: 'DynamicReasoningNode', 
                           target_node: 'DynamicReasoningNode', 
                           similarity: float) -> Optional[EdgeType]:
        """엣지 유형 결정"""
        # 노드 유형에 따른 기본 엣지 유형
        source_type = source_node.node_type.value
        target_type = target_node.node_type.value
        
        # 유사도 기반 엣지 유형 결정
        if similarity >= 0.5:
            # 높은 유사도: 지원 관계
            if source_type == "premise" and target_type in ["inference", "conclusion"]:
                return EdgeType.SUPPORTS
            elif source_type == "evidence" and target_type in ["inference", "conclusion"]:
                return EdgeType.EVIDENCES
            elif source_type == "inference" and target_type == "conclusion":
                return EdgeType.INFERS
            elif source_type == "premise" and target_type == "evidence":
                return EdgeType.SUPPORTS
            else:
                return EdgeType.SUPPORTS
        elif similarity >= 0.3:
            # 중간 유사도: 추론 관계
            if source_type == "premise" and target_type == "inference":
                return EdgeType.SUPPORTS
            elif source_type == "inference" and target_type == "conclusion":
                return EdgeType.INFERS
            elif source_type == "evidence" and target_type in ["inference", "conclusion"]:
                return EdgeType.EVIDENCES
            else:
                return EdgeType.INFERS
        elif similarity >= 0.2:
            # 낮은 유사도: 도전 관계
            if source_type == "counter_argument" and target_type in ["conclusion", "inference"]:
                return EdgeType.CHALLENGES
            elif source_type in ["premise", "evidence"] and target_type == "counter_argument":
                return EdgeType.CHALLENGES
            else:
                return EdgeType.CHALLENGES
        else:
            # 매우 낮은 유사도: 도전 관계
            return EdgeType.CHALLENGES
    
    def _generate_connection_reasoning(self, source_node: 'DynamicReasoningNode', 
                                     target_node: 'DynamicReasoningNode', 
                                     edge_type: EdgeType, 
                                     similarity: float) -> str:
        """연결 추론 생성"""
        reasoning_templates = {
            EdgeType.SUPPORTS: [
                "의미적 유사도 {similarity:.2f}로 {source}가 {target}를 지원함",
                "유사한 맥락으로 {source}가 {target}를 강화함",
                "의미적 연관성 {similarity:.2f}로 {source}가 {target}를 확증함"
            ],
            EdgeType.INFERS: [
                "의미적 유사도 {similarity:.2f}로 {source}에서 {target}를 추론함",
                "유사한 맥락으로 {source}가 {target}와 연결됨",
                "의미적 연관성 {similarity:.2f}로 {source}에서 {target}로 전개됨"
            ],
            EdgeType.EVIDENCES: [
                "의미적 유사도 {similarity:.2f}로 {source}가 {target}의 증거가 됨",
                "유사한 맥락으로 {source}가 {target}를 입증함",
                "의미적 연관성 {similarity:.2f}로 {source}가 {target}를 지지함"
            ],
            EdgeType.CHALLENGES: [
                "의미적 차이 {similarity:.2f}로 {source}가 {target}에 도전함",
                "다른 관점으로 {source}가 {target}에 의문을 제기함",
                "의미적 차이 {similarity:.2f}로 {source}가 {target}를 반박함"
            ]
        }
        
        templates = reasoning_templates.get(edge_type, [f"{edge_type.value}: {{source}} -> {{target}}"])
        template = random.choice(templates)
        
        return template.format(
            source=source_node.content[:20],
            target=target_node.content[:20],
            similarity=similarity
        )

class ConnectionOptimizer:
    """연결 최적화 시스템"""
    
    def __init__(self):
        self.optimization_strategies = self._initialize_optimization_strategies()
        self.optimization_cache = {}
        self.max_cache_size = 1000
    
    def _initialize_optimization_strategies(self) -> Dict[str, Dict[str, Any]]:
        """최적화 전략 초기화"""
        return {
            "strength_optimization": {
                "weight": 0.4,
                "description": "강도 최적화"
            },
            "similarity_optimization": {
                "weight": 0.3,
                "description": "유사도 최적화"
            },
            "connectivity_optimization": {
                "weight": 0.2,
                "description": "연결성 최적화"
            },
            "balance_optimization": {
                "weight": 0.1,
                "description": "균형 최적화"
            }
        }
    
    async def optimize_connections(self, graph: 'DynamicReasoningGraph') -> Dict[str, Any]:
        """연결 최적화"""
        logger.info(f"연결 최적화 시작: {len(graph.edges)}개 엣지")
        
        optimization_results = {
            "optimized_edges": [],
            "removed_edges": [],
            "new_edges": [],
            "optimization_metrics": {}
        }
        
        # 1. 강도 최적화
        strength_optimized = await self._optimize_edge_strengths(graph)
        optimization_results["optimized_edges"].extend(strength_optimized)
        
        # 2. 유사도 최적화
        similarity_optimized = await self._optimize_similarity_based_connections(graph)
        optimization_results["optimized_edges"].extend(similarity_optimized)
        
        # 3. 연결성 최적화
        connectivity_optimized = await self._optimize_connectivity(graph)
        optimization_results["optimized_edges"].extend(connectivity_optimized)
        
        # 4. 균형 최적화
        balance_optimized = await self._optimize_balance(graph)
        optimization_results["optimized_edges"].extend(balance_optimized)
        
        # 최적화 메트릭 계산
        optimization_results["optimization_metrics"] = await self._calculate_optimization_metrics(graph)
        
        logger.info(f"연결 최적화 완료: {len(optimization_results['optimized_edges'])}개 최적화됨")
        return optimization_results
    
    async def _optimize_edge_strengths(self, graph: 'DynamicReasoningGraph') -> List[str]:
        """엣지 강도 최적화"""
        optimized_edges = []
        
        for edge_id, edge in graph.edges.items():
            # 강도가 너무 낮거나 높은 엣지 조정
            if edge.strength < 0.3:
                # 너무 약한 엣지 강화
                edge.strength = min(0.8, edge.strength * 1.5)
                optimized_edges.append(edge_id)
            elif edge.strength > 0.9:
                # 너무 강한 엣지 조정
                edge.strength = max(0.7, edge.strength * 0.9)
                optimized_edges.append(edge_id)
        
        return optimized_edges
    
    async def _optimize_similarity_based_connections(self, graph: 'DynamicReasoningGraph') -> List[str]:
        """유사도 기반 연결 최적화"""
        optimized_edges = []
        
        for edge_id, edge in graph.edges.items():
            # 유사도와 강도의 불일치 조정
            if edge.semantic_similarity > 0.7 and edge.strength < 0.6:
                # 높은 유사도지만 낮은 강도인 경우 강화
                edge.strength = min(0.9, edge.strength * 1.3)
                optimized_edges.append(edge_id)
            elif edge.semantic_similarity < 0.3 and edge.strength > 0.7:
                # 낮은 유사도지만 높은 강도인 경우 조정
                edge.strength = max(0.4, edge.strength * 0.8)
                optimized_edges.append(edge_id)
        
        return optimized_edges
    
    async def _optimize_connectivity(self, graph: 'DynamicReasoningGraph') -> List[str]:
        """연결성 최적화"""
        optimized_edges = []
        
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
                        similarity = await self._calculate_simple_similarity(node.content, target_node.content)
                        if similarity > best_similarity:
                            best_similarity = similarity
                            best_target = target_id
                
                # 새로운 엣지 생성
                if best_target and best_similarity > 0.2:
                    new_edge_id = f"optimized_edge_{node_id}_{best_target}"
                    new_edge = DynamicReasoningEdge(
                        edge_id=new_edge_id,
                        source_node=node_id,
                        target_node=best_target,
                        edge_type=EdgeType.SUPPORTS,
                        strength=best_similarity,
                        reasoning=f"연결성 최적화를 통한 연결 (유사도: {best_similarity:.2f})",
                        semantic_similarity=best_similarity
                    )
                    graph.edges[new_edge_id] = new_edge
                    optimized_edges.append(new_edge_id)
        
        return optimized_edges
    
    async def _optimize_balance(self, graph: 'DynamicReasoningGraph') -> List[str]:
        """균형 최적화"""
        optimized_edges = []
        
        # 노드별 연결 수 계산
        node_connections = defaultdict(int)
        for edge in graph.edges.values():
            node_connections[edge.source_node] += 1
            node_connections[edge.target_node] += 1
        
        # 연결이 너무 많거나 적은 노드 조정
        avg_connections = sum(node_connections.values()) / len(node_connections) if node_connections else 0
        
        for node_id, connection_count in node_connections.items():
            if connection_count > avg_connections * 2:
                # 연결이 너무 많은 노드의 일부 연결 강도 감소
                for edge in graph.edges.values():
                    if edge.source_node == node_id or edge.target_node == node_id:
                        if edge.strength > 0.6:
                            edge.strength *= 0.9
                            optimized_edges.append(edge.edge_id)
        
        return optimized_edges
    
    async def _calculate_optimization_metrics(self, graph: 'DynamicReasoningGraph') -> Dict[str, float]:
        """최적화 메트릭 계산"""
        metrics = {}
        
        # 평균 강도
        edge_strengths = [edge.strength for edge in graph.edges.values()]
        metrics["avg_strength"] = sum(edge_strengths) / len(edge_strengths) if edge_strengths else 0.0
        
        # 평균 유사도
        edge_similarities = [edge.semantic_similarity for edge in graph.edges.values()]
        metrics["avg_similarity"] = sum(edge_similarities) / len(edge_similarities) if edge_similarities else 0.0
        
        # 연결성
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        metrics["connectivity"] = total_edges / (total_nodes * (total_nodes - 1) / 2) if total_nodes > 1 else 0.0
        
        # 강도 표준편차 (낮을수록 균형적)
        if edge_strengths:
            strength_std = np.std(edge_strengths)
            metrics["strength_balance"] = max(0.0, 1.0 - strength_std)
        else:
            metrics["strength_balance"] = 0.0
        
        return metrics
    
    async def _calculate_simple_similarity(self, text1: str, text2: str) -> float:
        """간단한 유사도 계산"""
        keywords1 = set(re.findall(r'\w+', text1.lower()))
        keywords2 = set(re.findall(r'\w+', text2.lower()))
        
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = len(keywords1.intersection(keywords2))
        union = len(keywords1.union(keywords2))
        
        return intersection / union if union > 0 else 0.0

class ConnectionValidator:
    """연결 검증 시스템"""
    
    def __init__(self):
        self.validation_criteria = self._initialize_validation_criteria()
    
    def _initialize_validation_criteria(self) -> Dict[str, Dict[str, Any]]:
        """검증 기준 초기화"""
        return {
            "connection_quality": {
                "weight": 0.3,
                "description": "연결 품질"
            },
            "semantic_coherence": {
                "weight": 0.3,
                "description": "의미적 일관성"
            },
            "structural_balance": {
                "weight": 0.2,
                "description": "구조적 균형"
            },
            "connection_efficiency": {
                "weight": 0.2,
                "description": "연결 효율성"
            }
        }
    
    async def validate_connections(self, graph: 'DynamicReasoningGraph') -> Dict[str, Any]:
        """연결 검증"""
        logger.info(f"연결 검증 시작: {len(graph.edges)}개 엣지")
        
        # 1. 연결 품질 평가
        connection_quality = await self._evaluate_connection_quality(graph)
        
        # 2. 의미적 일관성 평가
        semantic_coherence = await self._evaluate_semantic_coherence(graph)
        
        # 3. 구조적 균형 평가
        structural_balance = await self._evaluate_structural_balance(graph)
        
        # 4. 연결 효율성 평가
        connection_efficiency = await self._evaluate_connection_efficiency(graph)
        
        # 종합 검증 점수
        overall_score = (
            connection_quality * self.validation_criteria["connection_quality"]["weight"] +
            semantic_coherence * self.validation_criteria["semantic_coherence"]["weight"] +
            structural_balance * self.validation_criteria["structural_balance"]["weight"] +
            connection_efficiency * self.validation_criteria["connection_efficiency"]["weight"]
        )
        
        return {
            "overall_score": overall_score,
            "connection_quality": connection_quality,
            "semantic_coherence": semantic_coherence,
            "structural_balance": structural_balance,
            "connection_efficiency": connection_efficiency,
            "validation_details": {
                "total_edges": len(graph.edges),
                "avg_strength": sum(edge.strength for edge in graph.edges.values()) / len(graph.edges) if graph.edges else 0.0,
                "avg_similarity": sum(edge.semantic_similarity for edge in graph.edges.values()) / len(graph.edges) if graph.edges else 0.0,
                "connectivity": len(graph.edges) / (len(graph.nodes) * (len(graph.nodes) - 1) / 2) if len(graph.nodes) > 1 else 0.0
            }
        }
    
    async def _evaluate_connection_quality(self, graph: 'DynamicReasoningGraph') -> float:
        """연결 품질 평가"""
        if not graph.edges:
            return 0.0
        
        # 강도와 유사도의 일치도
        quality_scores = []
        for edge in graph.edges.values():
            # 강도와 유사도가 일치하는 정도
            strength_similarity_match = 1.0 - abs(edge.strength - edge.semantic_similarity)
            quality_scores.append(strength_similarity_match)
        
        return sum(quality_scores) / len(quality_scores)
    
    async def _evaluate_semantic_coherence(self, graph: 'DynamicReasoningGraph') -> float:
        """의미적 일관성 평가"""
        if not graph.edges:
            return 0.0
        
        # 평균 의미적 유사도
        similarities = [edge.semantic_similarity for edge in graph.edges.values()]
        return sum(similarities) / len(similarities)
    
    async def _evaluate_structural_balance(self, graph: 'DynamicReasoningGraph') -> float:
        """구조적 균형 평가"""
        if not graph.nodes:
            return 0.0
        
        # 노드별 연결 수의 표준편차 (낮을수록 균형적)
        node_connections = defaultdict(int)
        for edge in graph.edges.values():
            node_connections[edge.source_node] += 1
            node_connections[edge.target_node] += 1
        
        if not node_connections:
            return 0.0
        
        connection_counts = list(node_connections.values())
        connection_std = np.std(connection_counts)
        avg_connections = sum(connection_counts) / len(connection_counts)
        
        # 표준편차가 작을수록 균형적
        balance_score = max(0.0, 1.0 - (connection_std / avg_connections) if avg_connections > 0 else 0.0)
        return balance_score
    
    async def _evaluate_connection_efficiency(self, graph: 'DynamicReasoningGraph') -> float:
        """연결 효율성 평가"""
        if not graph.nodes:
            return 0.0
        
        # 연결성 비율 (실제 연결 / 가능한 최대 연결)
        total_nodes = len(graph.nodes)
        total_edges = len(graph.edges)
        max_possible_edges = total_nodes * (total_nodes - 1) / 2
        
        if max_possible_edges == 0:
            return 0.0
        
        connectivity_ratio = total_edges / max_possible_edges
        
        # 적절한 연결성 (너무 많거나 적으면 비효율적)
        optimal_connectivity = 0.3  # 30% 연결성이 최적
        efficiency = 1.0 - abs(connectivity_ratio - optimal_connectivity) / optimal_connectivity
        efficiency = max(0.0, efficiency)
        
        return efficiency

async def test_semantic_connection_system():
    """의미 기반 노드 연결 시스템 테스트"""
    print("=== 의미 기반 노드 연결 시스템 테스트 시작 (Phase 1-3 Week 3 Day 5) ===")
    
    # 테스트 그래프 생성
    graph = DynamicReasoningGraph(graph_id="test_graph")
    
    # 초기 노드들 생성
    initial_nodes = {
        "node1": DynamicReasoningNode("node1", NodeType.PREMISE, "윤리적 행동은 옳다", 0.8, "test"),
        "node2": DynamicReasoningNode("node2", NodeType.INFERENCE, "윤리적 행동 분석: 도덕적 의무", 0.7, "test"),
        "node3": DynamicReasoningNode("node3", NodeType.CONCLUSION, "윤리적 행동 필요: 최종 판단", 0.9, "test"),
        "node4": DynamicReasoningNode("node4", NodeType.EVIDENCE, "윤리적 행동의 증거: 사회적 이익", 0.8, "test"),
        "node5": DynamicReasoningNode("node5", NodeType.COUNTER_ARGUMENT, "윤리적 행동의 반론: 자유 제한", 0.6, "test")
    }
    
    graph.nodes = initial_nodes
    
    print(f"\n📊 초기 그래프 상태:")
    print(f"  • 노드 수: {len(graph.nodes)}")
    print(f"  • 엣지 수: {len(graph.edges)}")
    
    # 1. 의미적 유사도 계산 테스트
    similarity_engine = SemanticSimilarityEngine()
    
    print(f"\n🔍 의미적 유사도 계산 테스트:")
    test_pairs = [
        ("node1", "node2"),
        ("node1", "node3"),
        ("node2", "node3"),
        ("node4", "node5")
    ]
    
    for node1_id, node2_id in test_pairs:
        node1 = graph.nodes[node1_id]
        node2 = graph.nodes[node2_id]
        similarity = await similarity_engine.calculate_semantic_similarity(node1.content, node2.content)
        print(f"  • {node1_id} ↔ {node2_id}: {similarity:.3f}")
    
    # 2. 의미 기반 연결 생성 테스트
    connection_generator = SemanticConnectionGenerator()
    
    print(f"\n🔗 의미 기반 연결 생성 테스트:")
    for node_id, node in graph.nodes.items():
        connections = await connection_generator.generate_semantic_connections(graph, node, 3)
        
        if connections:
            print(f"  • {node_id} 연결 생성: {len(connections)}개")
            for connection in connections:
                graph.edges[connection.edge_id] = connection
                print(f"    - {connection.source_node} → {connection.target_node} ({connection.edge_type.value}, 강도: {connection.strength:.2f})")
    
    # 3. 연결 최적화 테스트
    optimizer = ConnectionOptimizer()
    
    print(f"\n⚙️ 연결 최적화 테스트:")
    optimization_results = await optimizer.optimize_connections(graph)
    
    print(f"  • 최적화된 엣지 수: {len(optimization_results['optimized_edges'])}")
    print(f"  • 최적화 메트릭:")
    for metric, value in optimization_results['optimization_metrics'].items():
        print(f"    - {metric}: {value:.3f}")
    
    # 4. 연결 검증 테스트
    validator = ConnectionValidator()
    
    print(f"\n📊 연결 검증 테스트:")
    validation_results = await validator.validate_connections(graph)
    
    print(f"  • 종합 검증 점수: {validation_results['overall_score']:.3f}")
    print(f"  • 연결 품질: {validation_results['connection_quality']:.3f}")
    print(f"  • 의미적 일관성: {validation_results['semantic_coherence']:.3f}")
    print(f"  • 구조적 균형: {validation_results['structural_balance']:.3f}")
    print(f"  • 연결 효율성: {validation_results['connection_efficiency']:.3f}")
    
    # 5. 최종 그래프 상태
    print(f"\n📊 최종 그래프 상태:")
    print(f"  • 노드 수: {len(graph.nodes)}")
    print(f"  • 엣지 수: {len(graph.edges)} (증가: {len(graph.edges) - 0})")
    
    # 엣지 유형별 분포
    edge_types = defaultdict(int)
    for edge in graph.edges.values():
        edge_types[edge.edge_type.value] += 1
    
    print(f"  • 엣지 유형별 분포:")
    for edge_type, count in edge_types.items():
        print(f"    - {edge_type}: {count}개")
    
    # 평균 강도와 유사도
    if graph.edges:
        avg_strength = sum(edge.strength for edge in graph.edges.values()) / len(graph.edges)
        avg_similarity = sum(edge.semantic_similarity for edge in graph.edges.values()) / len(graph.edges)
        print(f"  • 평균 강도: {avg_strength:.3f}")
        print(f"  • 평균 유사도: {avg_similarity:.3f}")
    
    print(f"\n{'='*70}")
    print("=== 의미 기반 노드 연결 시스템 테스트 완료 (Phase 1-3 Week 3 Day 5) ===")
    print("✅ Day 5 목표 달성: 의미 기반 노드 연결 시스템 구현")
    print("✅ 고급 의미적 유사도 계산 구현")
    print("✅ 의미 기반 연결 생성 구현")
    print("✅ 연결 최적화 구현")
    print("✅ 연결 검증 구현")

if __name__ == "__main__":
    asyncio.run(test_semantic_connection_system()) 