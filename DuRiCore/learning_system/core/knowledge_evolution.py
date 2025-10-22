#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-3: 지식 진화 시스템 (Knowledge Evolution System)

지식의 진화와 발전을 관리하는 시스템입니다.
- 지식 진화 프로세스
- 지식 통합 및 갱신
- 지식 품질 평가
- 지식 진화 추적
"""

import asyncio
import json
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EvolutionType(Enum):
    """진화 유형"""

    INCREMENTAL = "incremental"  # 점진적 진화
    REVOLUTIONARY = "revolutionary"  # 혁신적 진화
    INTEGRATIVE = "integrative"  # 통합적 진화
    ADAPTIVE = "adaptive"  # 적응적 진화


class KnowledgeQuality(Enum):
    """지식 품질"""

    POOR = "poor"  # 낮음 (0.0-0.3)
    FAIR = "fair"  # 보통 (0.3-0.6)
    GOOD = "good"  # 좋음 (0.6-0.8)
    EXCELLENT = "excellent"  # 우수 (0.8-1.0)


@dataclass
class KnowledgeItem:
    """지식 항목"""

    knowledge_id: str
    content: str
    domain: str
    confidence: float  # 0.0-1.0
    quality: KnowledgeQuality
    source: str
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeEvolution:
    """지식 진화"""

    evolution_id: str
    original_knowledge_id: str
    evolved_knowledge_id: str
    evolution_type: EvolutionType
    evolution_factors: List[str] = field(default_factory=list)
    confidence_change: float = 0.0
    quality_improvement: float = 0.0
    relevance_score: float = 0.0
    integration_level: float = 0.0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class EvolutionSession:
    """진화 세션"""

    session_id: str
    evolution_type: EvolutionType
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[timedelta] = None
    knowledge_items_processed: int = 0
    evolutions_created: int = 0
    quality_improvements: List[float] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)


class KnowledgeEvolutionSystem:
    """지식 진화 시스템"""

    def __init__(self):
        """초기화"""
        self.knowledge_items: Dict[str, KnowledgeItem] = {}
        self.evolutions: List[KnowledgeEvolution] = []
        self.evolution_sessions: List[EvolutionSession] = []

        # 성능 메트릭
        self.performance_metrics = {
            "total_knowledge_items": 0,
            "total_evolutions": 0,
            "average_quality_improvement": 0.0,
            "evolution_success_rate": 0.0,
            "knowledge_integration_rate": 0.0,
        }

        logger.info("지식 진화 시스템 초기화 완료")

    async def add_knowledge_item(
        self,
        content: str,
        domain: str,
        confidence: float = 0.5,
        quality: KnowledgeQuality = KnowledgeQuality.FAIR,
        source: str = "unknown",
    ) -> str:
        """지식 항목 추가"""
        knowledge_id = f"knowledge_{int(time.time())}_{domain}"

        knowledge_item = KnowledgeItem(
            knowledge_id=knowledge_id,
            content=content,
            domain=domain,
            confidence=confidence,
            quality=quality,
            source=source,
        )

        self.knowledge_items[knowledge_id] = knowledge_item
        self.performance_metrics["total_knowledge_items"] += 1

        logger.info(f"지식 항목 추가: {knowledge_id} ({domain})")
        return knowledge_id

    async def evolve_knowledge(
        self,
        knowledge_id: str,
        new_information: Dict[str, Any],
        evolution_type: EvolutionType = EvolutionType.INCREMENTAL,
    ) -> Optional[str]:
        """지식 진화"""
        if knowledge_id not in self.knowledge_items:
            logger.error(f"지식 항목을 찾을 수 없음: {knowledge_id}")
            return None

        original_knowledge = self.knowledge_items[knowledge_id]

        # 진화된 지식 생성
        evolved_content = await self._generate_evolved_content(original_knowledge, new_information)
        evolved_confidence = await self._calculate_evolved_confidence(
            original_knowledge, new_information
        )
        evolved_quality = await self._assess_evolved_quality(original_knowledge, evolved_content)

        # 새로운 지식 항목 생성
        evolved_knowledge_id = f"knowledge_{int(time.time())}_{original_knowledge.domain}_evolved"
        evolved_knowledge = KnowledgeItem(
            knowledge_id=evolved_knowledge_id,
            content=evolved_content,
            domain=original_knowledge.domain,
            confidence=evolved_confidence,
            quality=evolved_quality,
            source=f"evolution_from_{knowledge_id}",
            version=original_knowledge.version + 1,
        )

        self.knowledge_items[evolved_knowledge_id] = evolved_knowledge

        # 진화 기록 생성
        evolution_id = f"evolution_{int(time.time())}_{knowledge_id}"
        evolution = KnowledgeEvolution(
            evolution_id=evolution_id,
            original_knowledge_id=knowledge_id,
            evolved_knowledge_id=evolved_knowledge_id,
            evolution_type=evolution_type,
            evolution_factors=await self._identify_evolution_factors(
                original_knowledge, new_information
            ),
            confidence_change=evolved_confidence - original_knowledge.confidence,
            quality_improvement=await self._calculate_quality_improvement(
                original_knowledge, evolved_knowledge
            ),
            relevance_score=await self._calculate_relevance_score(
                evolved_knowledge, new_information
            ),
            integration_level=await self._calculate_integration_level(
                original_knowledge, evolved_knowledge
            ),
        )

        self.evolutions.append(evolution)
        self.performance_metrics["total_evolutions"] += 1

        logger.info(f"지식 진화 완료: {knowledge_id} -> {evolved_knowledge_id}")
        return evolved_knowledge_id

    async def _generate_evolved_content(
        self, original_knowledge: KnowledgeItem, new_information: Dict[str, Any]
    ) -> str:
        """진화된 내용 생성"""
        # 기본 진화 로직
        evolved_content = original_knowledge.content

        # 새로운 정보 통합
        if "content" in new_information:
            evolved_content += f"\n\n추가 정보: {new_information['content']}"

        # 메타데이터 업데이트
        if "metadata" in new_information:
            evolved_content += (
                f"\n\n메타데이터: {json.dumps(new_information['metadata'], ensure_ascii=False)}"
            )

        return evolved_content

    async def _calculate_evolved_confidence(
        self, original_knowledge: KnowledgeItem, new_information: Dict[str, Any]
    ) -> float:
        """진화된 신뢰도 계산"""
        base_confidence = original_knowledge.confidence

        # 새로운 정보의 신뢰도 반영
        if "confidence" in new_information:
            new_confidence = new_information["confidence"]
            # 가중 평균 계산
            evolved_confidence = (base_confidence * 0.7) + (new_confidence * 0.3)
        else:
            evolved_confidence = base_confidence

        return min(evolved_confidence, 1.0)

    async def _assess_evolved_quality(
        self, original_knowledge: KnowledgeItem, evolved_content: str
    ) -> KnowledgeQuality:
        """진화된 품질 평가"""
        # 기본 품질 평가 로직
        content_length = len(evolved_content)
        content_complexity = len(evolved_content.split())

        # 품질 점수 계산
        quality_score = min((content_length / 1000.0 + content_complexity / 100.0) / 2.0, 1.0)

        if quality_score >= 0.8:
            return KnowledgeQuality.EXCELLENT
        elif quality_score >= 0.6:
            return KnowledgeQuality.GOOD
        elif quality_score >= 0.3:
            return KnowledgeQuality.FAIR
        else:
            return KnowledgeQuality.POOR

    async def _identify_evolution_factors(
        self, original_knowledge: KnowledgeItem, new_information: Dict[str, Any]
    ) -> List[str]:
        """진화 요인 식별"""
        factors = []

        # 내용 확장
        if "content" in new_information and new_information["content"]:
            factors.append("content_expansion")

        # 신뢰도 변화
        if "confidence" in new_information:
            factors.append("confidence_adjustment")

        # 메타데이터 추가
        if "metadata" in new_information:
            factors.append("metadata_enrichment")

        # 도메인 관련성
        if "domain" in new_information:
            factors.append("domain_integration")

        return factors

    async def _calculate_quality_improvement(
        self, original_knowledge: KnowledgeItem, evolved_knowledge: KnowledgeItem
    ) -> float:
        """품질 개선도 계산"""
        original_quality = self._convert_quality_to_float(original_knowledge.quality)
        evolved_quality = self._convert_quality_to_float(evolved_knowledge.quality)

        return max(evolved_quality - original_quality, 0.0)

    async def _calculate_relevance_score(
        self, evolved_knowledge: KnowledgeItem, new_information: Dict[str, Any]
    ) -> float:
        """관련성 점수 계산"""
        # 기본 관련성 점수
        relevance_score = 0.5

        # 내용 관련성
        if "content" in new_information:
            content_similarity = await self._calculate_content_similarity(
                evolved_knowledge.content, new_information["content"]
            )
            relevance_score = (relevance_score + content_similarity) / 2.0

        # 도메인 관련성
        if "domain" in new_information:
            if new_information["domain"] == evolved_knowledge.domain:
                relevance_score += 0.2

        return min(relevance_score, 1.0)

    async def _calculate_integration_level(
        self, original_knowledge: KnowledgeItem, evolved_knowledge: KnowledgeItem
    ) -> float:
        """통합 수준 계산"""
        # 기본 통합 수준
        integration_level = 0.5

        # 내용 길이 증가
        content_ratio = len(evolved_knowledge.content) / max(len(original_knowledge.content), 1)
        integration_level = min(integration_level + (content_ratio - 1.0) * 0.3, 1.0)

        # 신뢰도 변화
        confidence_change = abs(evolved_knowledge.confidence - original_knowledge.confidence)
        integration_level = min(integration_level + confidence_change * 0.2, 1.0)

        return integration_level

    async def _calculate_content_similarity(self, content1: str, content2: str) -> float:
        """내용 유사도 계산"""
        # 간단한 유사도 계산 (단어 기반)
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        return len(intersection) / len(union) if union else 0.0

    def _convert_quality_to_float(self, quality: KnowledgeQuality) -> float:
        """품질을 float로 변환"""
        quality_map = {
            KnowledgeQuality.POOR: 0.25,
            KnowledgeQuality.FAIR: 0.5,
            KnowledgeQuality.GOOD: 0.75,
            KnowledgeQuality.EXCELLENT: 1.0,
        }
        return quality_map.get(quality, 0.5)

    async def start_evolution_session(self, evolution_type: EvolutionType) -> str:
        """진화 세션 시작"""
        session_id = f"evolution_session_{int(time.time())}_{evolution_type.value}"

        session = EvolutionSession(
            session_id=session_id,
            evolution_type=evolution_type,
            start_time=datetime.now(),
        )

        self.evolution_sessions.append(session)

        logger.info(f"진화 세션 시작: {session_id} ({evolution_type.value})")
        return session_id

    async def complete_evolution_session(self, session_id: str) -> bool:
        """진화 세션 완료"""
        session = None
        for s in self.evolution_sessions:
            if s.session_id == session_id:
                session = s
                break

        if not session:
            logger.error(f"세션을 찾을 수 없음: {session_id}")
            return False

        session.end_time = datetime.now()
        session.duration = session.end_time - session.start_time

        # 세션 메트릭 계산
        await self._calculate_session_metrics(session)

        logger.info(f"진화 세션 완료: {session_id} (지속시간: {session.duration})")
        return True

    async def _calculate_session_metrics(self, session: EvolutionSession):
        """세션 메트릭 계산"""
        if session.quality_improvements:
            session.average_quality_improvement = sum(session.quality_improvements) / len(
                session.quality_improvements
            )

            # 전체 평균 품질 개선도 업데이트
            all_improvements = []
            for s in self.evolution_sessions:
                all_improvements.extend(s.quality_improvements)

            if all_improvements:
                self.performance_metrics["average_quality_improvement"] = sum(
                    all_improvements
                ) / len(all_improvements)

    async def get_knowledge_item(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """지식 항목 조회"""
        if knowledge_id in self.knowledge_items:
            item = self.knowledge_items[knowledge_id]
            return {
                "knowledge_id": item.knowledge_id,
                "content": item.content,
                "domain": item.domain,
                "confidence": item.confidence,
                "quality": item.quality.value,
                "source": item.source,
                "version": item.version,
                "created_at": item.created_at.isoformat(),
                "updated_at": item.updated_at.isoformat(),
            }
        return None

    async def get_evolution_history(self, knowledge_id: str) -> List[Dict[str, Any]]:
        """진화 이력 조회"""
        evolutions = []
        for evolution in self.evolutions:
            if evolution.original_knowledge_id == knowledge_id:
                evolutions.append(
                    {
                        "evolution_id": evolution.evolution_id,
                        "evolved_knowledge_id": evolution.evolved_knowledge_id,
                        "evolution_type": evolution.evolution_type.value,
                        "confidence_change": evolution.confidence_change,
                        "quality_improvement": evolution.quality_improvement,
                        "created_at": evolution.created_at.isoformat(),
                    }
                )
        return evolutions

    async def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        return {
            "performance_metrics": self.performance_metrics,
            "total_knowledge_items": len(self.knowledge_items),
            "total_evolutions": len(self.evolutions),
            "active_evolution_sessions": len(
                [s for s in self.evolution_sessions if not s.end_time]
            ),
            "recent_evolutions": [
                {
                    "evolution_id": e.evolution_id,
                    "evolution_type": e.evolution_type.value,
                    "quality_improvement": e.quality_improvement,
                    "created_at": e.created_at.isoformat(),
                }
                for e in self.evolutions[-5:]  # 최근 5개 진화
            ],
        }
