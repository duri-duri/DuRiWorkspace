#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 지식 통합 시스템 (Knowledge Integration System)

다양한 소스의 지식을 통합하고 체계화하는 시스템입니다.
- 지식 소스 통합
- 지식 체계화
- 지식 품질 평가
- 지식 접근성 최적화
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IntegrationMethod(Enum):
    """통합 방법"""

    HIERARCHICAL = "hierarchical"  # 계층적 통합
    NETWORK = "network"  # 네트워크 통합
    SEMANTIC = "semantic"  # 시맨틱 통합
    HYBRID = "hybrid"  # 하이브리드 통합


class KnowledgeQuality(Enum):
    """지식 품질"""

    POOR = "poor"  # 낮음 (0.0-0.3)
    FAIR = "fair"  # 보통 (0.3-0.6)
    GOOD = "good"  # 좋음 (0.6-0.8)
    EXCELLENT = "excellent"  # 우수 (0.8-1.0)


@dataclass
class KnowledgeSource:
    """지식 소스"""

    source_id: str
    source_type: str
    content: Dict[str, Any]
    quality_score: float  # 0.0-1.0
    reliability: float  # 0.0-1.0
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class IntegratedKnowledge:
    """통합된 지식"""

    knowledge_id: str
    source_ids: List[str]
    integrated_content: Dict[str, Any]
    integration_method: IntegrationMethod
    coherence_score: float  # 0.0-1.0
    completeness_score: float  # 0.0-1.0
    accessibility_score: float  # 0.0-1.0
    quality: KnowledgeQuality
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class IntegrationSession:
    """통합 세션"""

    session_id: str
    integration_method: IntegrationMethod
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    sources_processed: int = 0
    knowledge_integrated: int = 0
    quality_improvements: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeIntegrationSystem:
    """지식 통합 시스템"""

    def __init__(self):
        """초기화"""
        self.knowledge_sources: Dict[str, KnowledgeSource] = {}
        self.integrated_knowledge: List[IntegratedKnowledge] = []
        self.integration_sessions: List[IntegrationSession] = []

        # 성능 메트릭
        self.performance_metrics = {
            "total_sources": 0,
            "total_integrations": 0,
            "average_coherence": 0.0,
            "average_completeness": 0.0,
            "average_accessibility": 0.0,
        }

        logger.info("지식 통합 시스템 초기화 완료")

    async def add_knowledge_source(
        self,
        source_type: str,
        content: Dict[str, Any],
        quality_score: float = 0.5,
        reliability: float = 0.5,
    ) -> str:
        """지식 소스 추가"""
        source_id = f"source_{int(time.time())}_{source_type}"

        knowledge_source = KnowledgeSource(
            source_id=source_id,
            source_type=source_type,
            content=content,
            quality_score=quality_score,
            reliability=reliability,
        )

        self.knowledge_sources[source_id] = knowledge_source
        self.performance_metrics["total_sources"] += 1

        logger.info(f"지식 소스 추가: {source_id} ({source_type})")
        return source_id

    async def integrate_knowledge(
        self,
        source_ids: List[str],
        integration_method: IntegrationMethod = IntegrationMethod.HIERARCHICAL,
    ) -> str:
        """지식 통합"""
        session_id = f"integration_session_{int(time.time())}_{integration_method.value}"
        start_time = datetime.now()

        try:
            # 통합 세션 생성
            session = IntegrationSession(
                session_id=session_id,
                integration_method=integration_method,
                start_time=start_time,
            )

            # 소스 수집
            sources = []
            for source_id in source_ids:
                if source_id in self.knowledge_sources:
                    sources.append(self.knowledge_sources[source_id])
                    session.sources_processed += 1

            if not sources:
                logger.error("통합할 소스가 없습니다")
                return ""

            # 지식 통합 실행
            integrated_content = await self._create_integrated_knowledge(sources, integration_method)

            # 품질 평가
            coherence_score = await self._calculate_coherence_score(integrated_content)
            completeness_score = await self._calculate_completeness_score(integrated_content, sources)
            accessibility_score = await self._calculate_accessibility_score(integrated_content)

            # 통합된 지식 생성
            knowledge_id = f"knowledge_{int(time.time())}_{integration_method.value}"
            quality = self._assess_knowledge_quality(coherence_score, completeness_score, accessibility_score)

            integrated_knowledge = IntegratedKnowledge(
                knowledge_id=knowledge_id,
                source_ids=source_ids,
                integrated_content=integrated_content,
                integration_method=integration_method,
                coherence_score=coherence_score,
                completeness_score=completeness_score,
                accessibility_score=accessibility_score,
                quality=quality,
            )

            # 세션 완료
            end_time = datetime.now()
            session.end_time = end_time
            session.duration = (end_time - start_time).total_seconds()
            session.knowledge_integrated = 1

            # 결과 저장
            self.integrated_knowledge.append(integrated_knowledge)
            self.integration_sessions.append(session)

            # 성능 메트릭 업데이트
            await self._update_performance_metrics(integrated_knowledge)

            logger.info(f"지식 통합 완료: {knowledge_id} (일관성: {coherence_score:.2f})")
            return knowledge_id

        except Exception as e:
            logger.error(f"지식 통합 실패: {e}")
            return ""

    async def _create_integrated_knowledge(
        self, sources: List[KnowledgeSource], integration_method: IntegrationMethod
    ) -> Dict[str, Any]:
        """통합된 지식 생성"""
        if integration_method == IntegrationMethod.HIERARCHICAL:
            return await self._hierarchical_integration(sources)
        elif integration_method == IntegrationMethod.NETWORK:
            return await self._network_integration(sources)
        elif integration_method == IntegrationMethod.SEMANTIC:
            return await self._semantic_integration(sources)
        elif integration_method == IntegrationMethod.HYBRID:
            return await self._hybrid_integration(sources)
        else:
            return await self._default_integration(sources)

    async def _hierarchical_integration(self, sources: List[KnowledgeSource]) -> Dict[str, Any]:
        """계층적 통합"""
        integrated_content = {"hierarchy": {}, "relationships": {}, "metadata": {}}

        # 계층 구조 생성
        for source in sources:
            source_type = source.source_type
            if source_type not in integrated_content["hierarchy"]:
                integrated_content["hierarchy"][source_type] = []

            integrated_content["hierarchy"][source_type].append(
                {
                    "source_id": source.source_id,
                    "content": source.content,
                    "quality_score": source.quality_score,
                    "reliability": source.reliability,
                }
            )

        return integrated_content

    async def _network_integration(self, sources: List[KnowledgeSource]) -> Dict[str, Any]:
        """네트워크 통합"""
        integrated_content = {"nodes": [], "edges": [], "network_structure": {}}

        # 노드 생성
        for source in sources:
            node = {
                "node_id": source.source_id,
                "node_type": source.source_type,
                "content": source.content,
                "quality_score": source.quality_score,
            }
            integrated_content["nodes"].append(node)

        # 엣지 생성 (간단한 연결)
        for i, source1 in enumerate(sources):
            for j, source2 in enumerate(sources[i + 1 :], i + 1):
                edge = {
                    "from_node": source1.source_id,
                    "to_node": source2.source_id,
                    "relationship_type": "related",
                }
                integrated_content["edges"].append(edge)

        return integrated_content

    async def _semantic_integration(self, sources: List[KnowledgeSource]) -> Dict[str, Any]:
        """시맨틱 통합"""
        integrated_content = {
            "semantic_entities": [],
            "semantic_relationships": [],
            "semantic_context": {},
        }

        # 시맨틱 엔티티 생성
        for source in sources:
            entity = {
                "entity_id": source.source_id,
                "entity_type": source.source_type,
                "semantic_content": source.content,
                "semantic_score": source.quality_score,
            }
            integrated_content["semantic_entities"].append(entity)

        return integrated_content

    async def _hybrid_integration(self, sources: List[KnowledgeSource]) -> Dict[str, Any]:
        """하이브리드 통합"""
        # 계층적 통합과 네트워크 통합의 조합
        hierarchical_content = await self._hierarchical_integration(sources)
        network_content = await self._network_integration(sources)

        integrated_content = {
            "hierarchical_structure": hierarchical_content,
            "network_structure": network_content,
            "hybrid_relationships": {},
        }

        return integrated_content

    async def _default_integration(self, sources: List[KnowledgeSource]) -> Dict[str, Any]:
        """기본 통합"""
        integrated_content = {"sources": [], "combined_content": {}, "metadata": {}}

        for source in sources:
            integrated_content["sources"].append(
                {
                    "source_id": source.source_id,
                    "source_type": source.source_type,
                    "content": source.content,
                }
            )

        return integrated_content

    async def _calculate_coherence_score(self, integrated_content: Dict[str, Any]) -> float:
        """일관성 점수 계산"""
        # 기본 일관성 점수 계산
        coherence_score = 0.7  # 기본값

        # 내용의 복잡성에 따른 조정
        if "hierarchy" in integrated_content:
            hierarchy_complexity = len(integrated_content["hierarchy"])
            coherence_score = min(coherence_score + hierarchy_complexity * 0.1, 1.0)

        if "nodes" in integrated_content:
            network_complexity = len(integrated_content["nodes"])
            coherence_score = min(coherence_score + network_complexity * 0.05, 1.0)

        return coherence_score

    async def _calculate_completeness_score(
        self, integrated_content: Dict[str, Any], sources: List[KnowledgeSource]
    ) -> float:
        """완전성 점수 계산"""
        if not sources:
            return 0.0

        # 소스별 완전성 평가
        completeness_scores = []
        for source in sources:
            source_completeness = source.quality_score * source.reliability
            completeness_scores.append(source_completeness)

        # 평균 완전성 점수
        average_completeness = sum(completeness_scores) / len(completeness_scores)

        # 통합 내용의 풍부성에 따른 보정
        content_richness = len(str(integrated_content)) / 1000.0  # 간단한 풍부성 측정
        adjusted_completeness = min(average_completeness + content_richness * 0.1, 1.0)

        return adjusted_completeness

    async def _calculate_accessibility_score(self, integrated_content: Dict[str, Any]) -> float:
        """접근성 점수 계산"""
        # 기본 접근성 점수
        accessibility_score = 0.8

        # 구조의 복잡성에 따른 조정
        structure_complexity = 0.0

        if "hierarchy" in integrated_content:
            structure_complexity += len(integrated_content["hierarchy"]) * 0.1

        if "nodes" in integrated_content:
            structure_complexity += len(integrated_content["nodes"]) * 0.05

        # 복잡성이 높을수록 접근성 감소
        accessibility_score = max(accessibility_score - structure_complexity, 0.0)

        return accessibility_score

    def _assess_knowledge_quality(
        self,
        coherence_score: float,
        completeness_score: float,
        accessibility_score: float,
    ) -> KnowledgeQuality:
        """지식 품질 평가"""
        # 종합 품질 점수 계산
        overall_quality = (coherence_score + completeness_score + accessibility_score) / 3.0

        if overall_quality >= 0.8:
            return KnowledgeQuality.EXCELLENT
        elif overall_quality >= 0.6:
            return KnowledgeQuality.GOOD
        elif overall_quality >= 0.3:
            return KnowledgeQuality.FAIR
        else:
            return KnowledgeQuality.POOR

    async def _update_performance_metrics(self, integrated_knowledge: IntegratedKnowledge):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_integrations"] += 1

        # 평균 점수 업데이트
        all_coherence_scores = [k.coherence_score for k in self.integrated_knowledge]
        all_completeness_scores = [k.completeness_score for k in self.integrated_knowledge]
        all_accessibility_scores = [k.accessibility_score for k in self.integrated_knowledge]

        if all_coherence_scores:
            self.performance_metrics["average_coherence"] = sum(all_coherence_scores) / len(all_coherence_scores)

        if all_completeness_scores:
            self.performance_metrics["average_completeness"] = sum(all_completeness_scores) / len(
                all_completeness_scores
            )

        if all_accessibility_scores:
            self.performance_metrics["average_accessibility"] = sum(all_accessibility_scores) / len(
                all_accessibility_scores
            )

    async def get_integrated_knowledge(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """통합된 지식 조회"""
        for knowledge in self.integrated_knowledge:
            if knowledge.knowledge_id == knowledge_id:
                return {
                    "knowledge_id": knowledge.knowledge_id,
                    "source_ids": knowledge.source_ids,
                    "integration_method": knowledge.integration_method.value,
                    "coherence_score": knowledge.coherence_score,
                    "completeness_score": knowledge.completeness_score,
                    "accessibility_score": knowledge.accessibility_score,
                    "quality": knowledge.quality.value,
                    "created_at": knowledge.created_at.isoformat(),
                }
        return None

    async def get_integration_report(self) -> Dict[str, Any]:
        """통합 리포트 생성"""
        if not self.integrated_knowledge:
            return {"error": "통합된 지식이 없습니다"}

        # 최근 통합 분석
        recent_integrations = self.integrated_knowledge[-10:]  # 최근 10개

        avg_coherence = sum(k.coherence_score for k in recent_integrations) / len(recent_integrations)
        avg_completeness = sum(k.completeness_score for k in recent_integrations) / len(recent_integrations)
        avg_accessibility = sum(k.accessibility_score for k in recent_integrations) / len(recent_integrations)

        # 통합 방법별 통계
        method_stats = defaultdict(lambda: {"count": 0, "avg_quality": 0.0})
        for knowledge in recent_integrations:
            method = knowledge.integration_method.value
            method_stats[method]["count"] += 1
            method_stats[method]["avg_quality"] += (
                knowledge.coherence_score + knowledge.completeness_score + knowledge.accessibility_score
            ) / 3.0

        for method in method_stats:
            if method_stats[method]["count"] > 0:
                method_stats[method]["avg_quality"] /= method_stats[method]["count"]

        return {
            "performance_summary": {
                "average_coherence": avg_coherence,
                "average_completeness": avg_completeness,
                "average_accessibility": avg_accessibility,
                "total_integrations": len(self.integrated_knowledge),
            },
            "method_statistics": dict(method_stats),
            "recent_integrations": [
                {
                    "knowledge_id": k.knowledge_id,
                    "integration_method": k.integration_method.value,
                    "coherence_score": k.coherence_score,
                    "completeness_score": k.completeness_score,
                    "accessibility_score": k.accessibility_score,
                    "quality": k.quality.value,
                }
                for k in recent_integrations
            ],
        }
