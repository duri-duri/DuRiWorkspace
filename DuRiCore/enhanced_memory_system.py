#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 2 - 고도화된 기억 시스템
기억 분류, 연관성 분석, 우선순위 시스템 구현
"""

import asyncio
import hashlib
import json
import logging
import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# Phase 6.2.6 시맨틱 지식 연결망 통합
from semantic_knowledge_graph import ConceptType, InferenceType, SemanticKnowledgeGraph

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """기억 타입 열거형"""

    EXPERIENCE = "experience"  # 경험 기억
    KNOWLEDGE = "knowledge"  # 지식 기억
    PATTERN = "pattern"  # 패턴 기억
    EMOTION = "emotion"  # 감정 기억
    WORKING = "working"  # 작업 기억 (Phase 6.2.2 추가)


class AssociationType(Enum):
    """연관성 타입 열거형"""

    SEMANTIC = "semantic"  # 의미적 연관성
    TEMPORAL = "temporal"  # 시간적 연관성
    EMOTIONAL = "emotional"  # 감정적 연관성
    CONTEXTUAL = "contextual"  # 맥락적 연관성
    OPERATIONAL = "operational"  # 연산적 연관성 (Phase 6.2.2 추가)


@dataclass
class MemoryEntry:
    """고도화된 메모리 엔트리"""

    id: str
    content: str
    memory_type: MemoryType
    importance: float
    created_at: datetime
    accessed_count: int
    last_accessed: datetime
    associations: List[str]
    vector_data: List[float]
    metadata: Dict[str, Any]

    # 새로운 필드들
    classification_confidence: float
    priority_score: float
    retention_score: float
    association_strength: Dict[str, float]
    tags: List[str]
    context_info: Dict[str, Any]


@dataclass
class AssociationLink:
    """연관성 링크"""

    source_id: str
    target_id: str
    association_type: AssociationType
    strength: float
    created_at: datetime
    metadata: Dict[str, Any]


@dataclass
class WorkingMemoryBuffer:
    """작업 기억 버퍼 (Phase 6.2.2 추가)"""

    id: str
    content: str
    operation_type: str  # 'addition', 'subtraction', 'comparison', 'integration'
    operands: List[str]  # 연산에 사용된 메모리 ID들
    result: str
    confidence: float
    created_at: datetime
    expires_at: datetime  # 작업 기억은 일시적
    access_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.expires_at is None:
            # 기본적으로 30분 후 만료
            self.expires_at = self.created_at + timedelta(minutes=30)


@dataclass
class MemoryOperation:
    """메모리 연산 정보 (Phase 6.2.2 추가)"""

    operation_id: str
    operation_type: str
    input_memories: List[str]
    output_memory: str
    operation_result: str
    confidence: float
    execution_time: float
    created_at: datetime


class EnhancedMemorySystem:
    """고도화된 기억 시스템"""

    def __init__(self):
        self.memories: Dict[str, MemoryEntry] = {}
        self.associations: Dict[str, AssociationLink] = {}
        self.memory_type_index: Dict[MemoryType, List[str]] = defaultdict(list)
        self.priority_queue: List[str] = []

        # Phase 6.2.2 - Working Memory 연산 버퍼 추가
        self.working_memory_buffers: Dict[str, WorkingMemoryBuffer] = {}
        self.memory_operations: Dict[str, MemoryOperation] = {}
        self.operation_history: List[MemoryOperation] = []

        # 분류 시스템 설정
        self.classification_threshold = 0.8
        self.association_threshold = 0.6

        # 우선순위 시스템 설정
        self.importance_weight = 0.4
        self.access_weight = 0.3
        self.recency_weight = 0.3

        # Phase 6.2.2 - Working Memory 설정
        self.working_memory_capacity = 7  # Miller's Law (7±2)
        self.working_memory_ttl = 1800  # 30분 (초 단위)
        self.operation_confidence_threshold = 0.7

        # Phase 6.2.6 - 시맨틱 지식 연결망 설정
        self.semantic_graph = SemanticKnowledgeGraph()

        # 벡터 차원
        self.vector_dim = 128

        logger.info("고도화된 기억 시스템 초기화 완료 (Phase 6.2.2, 6.2.6 포함)")

    async def process_input(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """입력 데이터 처리 (통합 루프용)"""
        try:
            content = input_data.get("content", "")
            context = input_data.get("context", {})
            importance = input_data.get("importance", 0.5)

            # 메모리 저장
            memory_id = await self.store_memory(content, context, importance)

            # 관련 메모리 검색
            related_memories = await self.get_related_memories(memory_id, limit=5)

            # 메모리 통계
            statistics = await self.get_memory_statistics()

            return {
                "success": True,
                "memory_id": memory_id,
                "related_memories": related_memories,
                "statistics": statistics,
                "data": {
                    "content": content,
                    "context": context,
                    "importance": importance,
                    "memory_id": memory_id,
                },
            }

        except Exception as e:
            logger.error(f"입력 데이터 처리 실패: {e}")
            return {"success": False, "error": str(e), "data": {}}

    async def store_memory(self, content: str, context: Dict[str, Any], importance: float = 0.5) -> str:
        """메모리 저장 (고도화된 버전)"""
        try:
            # 고유 ID 생성
            memory_id = self._generate_memory_id(content, context)

            # 기억 타입 분류
            memory_type, confidence = await self._classify_memory_type(content, context)

            # 벡터 데이터 생성
            vector_data = await self._create_enhanced_vector(content, context)

            # 태그 추출
            tags = await self._extract_enhanced_tags(content, context)

            # 우선순위 점수 계산
            priority_score = self._calculate_priority_score(importance, 0, datetime.now())

            # 보존 점수 계산
            retention_score = self._calculate_retention_score(content, memory_type, importance)

            # 메모리 엔트리 생성
            memory_entry = MemoryEntry(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                created_at=datetime.now(),
                accessed_count=0,
                last_accessed=datetime.now(),
                associations=[],
                vector_data=vector_data,
                metadata=context,
                classification_confidence=confidence,
                priority_score=priority_score,
                retention_score=retention_score,
                association_strength={},
                tags=tags,
                context_info=context,
            )

            # 저장
            self.memories[memory_id] = memory_entry
            self.memory_type_index[memory_type].append(memory_id)

            # 우선순위 큐 업데이트
            self._update_priority_queue(memory_id, priority_score)

            # 연관성 분석 및 연결
            await self._analyze_and_link_associations(memory_id)

            logger.info(f"고도화된 메모리 저장 완료: {memory_id} (타입: {memory_type.value})")
            return memory_id

        except Exception as e:
            logger.error(f"메모리 저장 오류: {e}")
            return ""

    async def search_memories(
        self, query: str, memory_type: Optional[MemoryType] = None, limit: int = 10
    ) -> List[Tuple[MemoryEntry, float]]:
        """고도화된 메모리 검색"""
        try:
            results = []
            query_vector = await self._create_enhanced_vector(query, {})

            # 검색 대상 결정
            search_ids = self._get_search_targets(memory_type)

            for memory_id in search_ids:
                if memory_id in self.memories:
                    memory = self.memories[memory_id]
                    similarity = self._cosine_similarity(query_vector, memory.vector_data)

                    if similarity > 0.3:  # 임계값
                        results.append((memory, similarity))

            # 유사도 순으로 정렬
            results.sort(key=lambda x: x[1], reverse=True)

            # 접근 횟수 업데이트
            for memory, _ in results[:limit]:
                memory.accessed_count += 1
                memory.last_accessed = datetime.now()
                self._update_priority_queue(memory.id, memory.priority_score)

            return results[:limit]

        except Exception as e:
            logger.error(f"메모리 검색 오류: {e}")
            return []

    async def get_related_memories(
        self,
        memory_id: str,
        association_type: Optional[AssociationType] = None,
        limit: int = 5,
    ) -> List[Tuple[MemoryEntry, float]]:
        """연관 메모리 검색"""
        try:
            if memory_id not in self.memories:
                return []

            related_memories = []
            memory = self.memories[memory_id]  # noqa: F841

            # 연관성 링크 검색
            for link_id, link in self.associations.items():
                if (link.source_id == memory_id or link.target_id == memory_id) and (
                    association_type is None or link.association_type == association_type
                ):
                    related_id = link.target_id if link.source_id == memory_id else link.source_id
                    if related_id in self.memories:
                        related_memory = self.memories[related_id]
                        related_memories.append((related_memory, link.strength))

            # 강도 순으로 정렬
            related_memories.sort(key=lambda x: x[1], reverse=True)

            return related_memories[:limit]

        except Exception as e:
            logger.error(f"연관 메모리 검색 오류: {e}")
            return []

    async def update_memory_importance(self, memory_id: str, new_importance: float):
        """메모리 중요도 업데이트"""
        try:
            if memory_id in self.memories:
                memory = self.memories[memory_id]
                memory.importance = new_importance
                memory.priority_score = self._calculate_priority_score(
                    new_importance, memory.accessed_count, memory.last_accessed
                )
                self._update_priority_queue(memory_id, memory.priority_score)

                logger.info(f"메모리 중요도 업데이트: {memory_id} -> {new_importance}")

        except Exception as e:
            logger.error(f"중요도 업데이트 오류: {e}")

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 통계 정보"""
        try:
            stats = {
                "total_memories": len(self.memories),
                "memory_types": {},
                "priority_distribution": {},
                "association_stats": {},
                "access_patterns": {},
            }

            # 타입별 통계
            for memory_type in MemoryType:
                type_memories = [m for m in self.memories.values() if m.memory_type == memory_type]
                stats["memory_types"][memory_type.value] = {
                    "count": len(type_memories),
                    "avg_importance": (np.mean([m.importance for m in type_memories]) if type_memories else 0),
                    "avg_priority": (np.mean([m.priority_score for m in type_memories]) if type_memories else 0),
                }

            # 우선순위 분포
            priorities = [m.priority_score for m in self.memories.values()]
            stats["priority_distribution"] = {
                "min": min(priorities) if priorities else 0,
                "max": max(priorities) if priorities else 0,
                "mean": np.mean(priorities) if priorities else 0,
                "std": np.std(priorities) if priorities else 0,
            }

            # 연관성 통계
            association_types = [link.association_type for link in self.associations.values()]
            type_counts = Counter(association_types)
            stats["association_stats"] = {
                "total_links": len(self.associations),
                "type_distribution": {t.value: count for t, count in type_counts.items()},
            }

            # 접근 패턴
            access_counts = [m.accessed_count for m in self.memories.values()]
            stats["access_patterns"] = {
                "total_accesses": sum(access_counts),
                "avg_accesses": np.mean(access_counts) if access_counts else 0,
                "most_accessed": max(access_counts) if access_counts else 0,
            }

            return stats

        except Exception as e:
            logger.error(f"통계 생성 오류: {e}")
            return {}

    async def cleanup_low_priority_memories(self, threshold: float = 0.3):
        """낮은 우선순위 메모리 정리"""
        try:
            to_delete = []

            for memory_id, memory in self.memories.items():
                if memory.priority_score < threshold and memory.accessed_count < 3:
                    to_delete.append(memory_id)

            for memory_id in to_delete:
                await self._delete_memory(memory_id)

            logger.info(f"낮은 우선순위 메모리 정리 완료: {len(to_delete)}개 삭제")
            return len(to_delete)

        except Exception as e:
            logger.error(f"메모리 정리 오류: {e}")
            return 0

    # 내부 메서드들
    def _generate_memory_id(self, content: str, context: Dict[str, Any]) -> str:
        """고유 메모리 ID 생성"""
        data = f"{content}{json.dumps(context, sort_keys=True)}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]

    async def _classify_memory_type(self, content: str, context: Dict[str, Any]) -> Tuple[MemoryType, float]:
        """기억 타입 분류"""
        try:
            # 키워드 기반 분류
            keywords = {
                MemoryType.EXPERIENCE: ["경험", "발생", "일어났다", "했다", "했다"],
                MemoryType.KNOWLEDGE: ["알다", "이해", "학습", "정보", "지식"],
                MemoryType.PATTERN: ["패턴", "반복", "규칙", "습관", "경향"],
                MemoryType.EMOTION: ["감정", "기분", "느낌", "행복", "슬픔", "화남"],
            }

            scores = {}
            for memory_type, type_keywords in keywords.items():
                score = sum(1 for keyword in type_keywords if keyword in content)
                scores[memory_type] = score

            # 컨텍스트 정보 반영
            if "emotion" in context:
                scores[MemoryType.EMOTION] += 2

            if "learning" in context:
                scores[MemoryType.KNOWLEDGE] += 2

            # 최고 점수 선택
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type] / 3.0, 1.0)  # 최대 1.0

            return best_type, confidence

        except Exception as e:
            logger.error(f"메모리 타입 분류 오류: {e}")
            return MemoryType.EXPERIENCE, 0.5

    async def _create_enhanced_vector(self, content: str, context: Dict[str, Any]) -> List[float]:
        """고도화된 벡터 생성"""
        try:
            # 간단한 해시 기반 벡터 생성 (실제로는 임베딩 모델 사용)
            vector = []
            for i in range(self.vector_dim):
                # 내용과 컨텍스트를 조합한 해시
                data = f"{content}{json.dumps(context)}{i}"
                hash_val = int(hashlib.md5(data.encode()).hexdigest(), 16)
                vector.append((hash_val % 1000) / 1000.0)  # 0-1 범위로 정규화

            return vector

        except Exception as e:
            logger.error(f"벡터 생성 오류: {e}")
            return [0.0] * self.vector_dim

    async def _extract_enhanced_tags(self, content: str, context: Dict[str, Any]) -> List[str]:
        """고도화된 태그 추출"""
        try:
            tags = []

            # 기본 태그
            if "emotion" in context:
                tags.append("감정")
            if "learning" in context:
                tags.append("학습")
            if "important" in context:
                tags.append("중요")

            # 내용 기반 태그
            content_words = content.split()
            if len(content_words) > 3:
                tags.extend(content_words[:3])

            return list(set(tags))  # 중복 제거

        except Exception as e:
            logger.error(f"태그 추출 오류: {e}")
            return []

    def _calculate_priority_score(self, importance: float, access_count: int, last_accessed: datetime) -> float:
        """우선순위 점수 계산"""
        try:
            # 시간 가중치 (최근일수록 높음)
            time_diff = datetime.now() - last_accessed
            time_weight = max(0, 1 - (time_diff.total_seconds() / (24 * 3600)))  # 24시간 기준

            # 접근 빈도 가중치
            access_weight = min(1.0, access_count / 10.0)  # 최대 10회 기준

            # 종합 점수
            priority_score = (
                self.importance_weight * importance
                + self.access_weight * access_weight
                + self.recency_weight * time_weight
            )

            return min(1.0, priority_score)

        except Exception as e:
            logger.error(f"우선순위 계산 오류: {e}")
            return importance

    def _calculate_retention_score(self, content: str, memory_type: MemoryType, importance: float) -> float:
        """보존 점수 계산"""
        try:
            # 기본 점수
            base_score = importance

            # 타입별 가중치
            type_weights = {
                MemoryType.EXPERIENCE: 0.8,
                MemoryType.KNOWLEDGE: 0.9,
                MemoryType.PATTERN: 0.7,
                MemoryType.EMOTION: 0.6,
            }

            type_weight = type_weights.get(memory_type, 0.7)

            # 내용 길이 가중치
            length_weight = min(1.0, len(content) / 100.0)

            retention_score = base_score * type_weight * (0.7 + 0.3 * length_weight)

            return min(1.0, retention_score)

        except Exception as e:
            logger.error(f"보존 점수 계산 오류: {e}")
            return importance

    def _update_priority_queue(self, memory_id: str, priority_score: float):
        """우선순위 큐 업데이트"""
        try:
            # 기존 항목 제거
            if memory_id in self.priority_queue:
                self.priority_queue.remove(memory_id)

            # 새 위치에 삽입
            insert_index = 0
            for i, existing_id in enumerate(self.priority_queue):
                if existing_id in self.memories:
                    existing_priority = self.memories[existing_id].priority_score
                    if priority_score > existing_priority:
                        insert_index = i
                        break
                    insert_index = i + 1
                else:
                    insert_index = i

            self.priority_queue.insert(insert_index, memory_id)

        except Exception as e:
            logger.error(f"우선순위 큐 업데이트 오류: {e}")

    def _get_search_targets(self, memory_type: Optional[MemoryType]) -> List[str]:
        """검색 대상 결정"""
        if memory_type:
            return self.memory_type_index.get(memory_type, [])
        else:
            return list(self.memories.keys())

    async def _analyze_and_link_associations(self, memory_id: str):
        """연관성 분석 및 연결"""
        try:
            if memory_id not in self.memories:
                return

            new_memory = self.memories[memory_id]

            for existing_id, existing_memory in self.memories.items():
                if existing_id == memory_id:
                    continue

                # 의미적 연관성
                semantic_similarity = self._cosine_similarity(new_memory.vector_data, existing_memory.vector_data)

                if semantic_similarity > self.association_threshold:
                    await self._create_association_link(
                        memory_id,
                        existing_id,
                        AssociationType.SEMANTIC,
                        semantic_similarity,
                    )

                # 시간적 연관성
                time_diff = abs((new_memory.created_at - existing_memory.created_at).total_seconds())
                if time_diff < 3600:  # 1시간 이내
                    temporal_strength = max(0, 1 - (time_diff / 3600))
                    if temporal_strength > self.association_threshold:
                        await self._create_association_link(
                            memory_id,
                            existing_id,
                            AssociationType.TEMPORAL,
                            temporal_strength,
                        )

                # 감정적 연관성 (감정 메모리인 경우)
                if new_memory.memory_type == MemoryType.EMOTION and existing_memory.memory_type == MemoryType.EMOTION:
                    emotion_similarity = self._cosine_similarity(new_memory.vector_data, existing_memory.vector_data)
                    if emotion_similarity > self.association_threshold:
                        await self._create_association_link(
                            memory_id,
                            existing_id,
                            AssociationType.EMOTIONAL,
                            emotion_similarity,
                        )

        except Exception as e:
            logger.error(f"연관성 분석 오류: {e}")

    async def _create_association_link(
        self,
        source_id: str,
        target_id: str,
        association_type: AssociationType,
        strength: float,
    ):
        """연관성 링크 생성"""
        try:
            link_id = f"{source_id}_{target_id}_{association_type.value}"

            link = AssociationLink(
                source_id=source_id,
                target_id=target_id,
                association_type=association_type,
                strength=strength,
                created_at=datetime.now(),
                metadata={},
            )

            self.associations[link_id] = link

            # 메모리에 연관 정보 추가
            if source_id in self.memories:
                self.memories[source_id].associations.append(target_id)
                self.memories[source_id].association_strength[target_id] = strength

            if target_id in self.memories:
                self.memories[target_id].associations.append(source_id)
                self.memories[target_id].association_strength[source_id] = strength

        except Exception as e:
            logger.error(f"연관성 링크 생성 오류: {e}")

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        try:
            if len(vec1) != len(vec2):
                return 0.0

            dot_product = sum(a * b for a, b in zip(vec1, vec2))  # noqa: B905
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(a * a for a in vec2))

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)

        except Exception as e:
            logger.error(f"유사도 계산 오류: {e}")
            return 0.0

    async def _delete_memory(self, memory_id: str):
        """메모리 삭제"""
        try:
            if memory_id in self.memories:
                # 연관성 링크 제거
                links_to_remove = []
                for link_id, link in self.associations.items():
                    if link.source_id == memory_id or link.target_id == memory_id:
                        links_to_remove.append(link_id)

                for link_id in links_to_remove:
                    del self.associations[link_id]

                # 타입 인덱스에서 제거
                memory = self.memories[memory_id]
                if memory.memory_type in self.memory_type_index:
                    if memory_id in self.memory_type_index[memory.memory_type]:
                        self.memory_type_index[memory.memory_type].remove(memory_id)

                # 우선순위 큐에서 제거
                if memory_id in self.priority_queue:
                    self.priority_queue.remove(memory_id)

                # 메모리 삭제
                del self.memories[memory_id]

                logger.info(f"메모리 삭제 완료: {memory_id}")

        except Exception as e:
            logger.error(f"메모리 삭제 오류: {e}")

    # Phase 6.2.2 - Working Memory 연산 기능들

    async def perform_memory_operation(self, operation_type: str, memory_ids: List[str]) -> Dict[str, Any]:
        """메모리 연산 수행"""
        try:
            start_time = time.time()  # noqa: F821

            # 입력 메모리 검증
            input_memories = []
            for memory_id in memory_ids:
                if memory_id in self.memories:
                    input_memories.append(self.memories[memory_id])
                else:
                    return {"success": False, "error": f"Memory {memory_id} not found"}

            if len(input_memories) < 2:
                return {
                    "success": False,
                    "error": "At least 2 memories required for operation",
                }

            # 연산 수행
            operation_result = await self._execute_memory_operation(operation_type, input_memories)

            # 결과를 작업 기억 버퍼에 저장
            buffer_id = await self._store_in_working_memory(operation_type, memory_ids, operation_result)

            # 연산 기록
            execution_time = time.time() - start_time  # noqa: F821
            operation_record = MemoryOperation(
                operation_id=f"op_{int(time.time() * 1000)}",  # noqa: F821
                operation_type=operation_type,
                input_memories=memory_ids,
                output_memory=buffer_id,
                operation_result=operation_result["result"],
                confidence=operation_result["confidence"],
                execution_time=execution_time,
                created_at=datetime.now(),
            )

            self.memory_operations[operation_record.operation_id] = operation_record
            self.operation_history.append(operation_record)

            logger.info(f"🧠 메모리 연산 완료: {operation_type} (신뢰도: {operation_result['confidence']:.3f})")

            return {
                "success": True,
                "operation_id": operation_record.operation_id,
                "buffer_id": buffer_id,
                "result": operation_result["result"],
                "confidence": operation_result["confidence"],
                "execution_time": execution_time,
            }

        except Exception as e:
            logger.error(f"메모리 연산 실패: {e}")
            return {"success": False, "error": str(e)}

    async def _execute_memory_operation(self, operation_type: str, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """메모리 연산 실행"""
        if operation_type == "addition":
            return await self._add_memories(memories)
        elif operation_type == "subtraction":
            return await self._subtract_memories(memories)
        elif operation_type == "comparison":
            return await self._compare_memories(memories)
        elif operation_type == "integration":
            return await self._integrate_memories(memories)
        else:
            return {"result": "Unknown operation", "confidence": 0.0}

    async def _add_memories(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """메모리 추가 연산"""
        # 의미적 유사성을 기반으로 메모리 통합
        combined_content = " ".join([m.content for m in memories])
        combined_tags = list(set([tag for m in memories for tag in m.tags]))  # noqa: F841

        # 신뢰도 계산 (평균 + 유사성 보너스)
        avg_confidence = sum(m.classification_confidence for m in memories) / len(memories)
        similarity_bonus = self._calculate_memory_similarity(memories) * 0.1

        confidence = min(1.0, avg_confidence + similarity_bonus)

        return {"result": f"통합된 정보: {combined_content}", "confidence": confidence}

    async def _subtract_memories(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """메모리 차감 연산"""
        if len(memories) < 2:
            return {
                "result": "Insufficient memories for subtraction",
                "confidence": 0.0,
            }

        # 첫 번째 메모리에서 나머지 메모리들의 공통 요소 제거
        base_memory = memories[0]
        other_memories = memories[1:]

        # 공통 태그 찾기
        common_tags = set(base_memory.tags)
        for memory in other_memories:
            common_tags = common_tags.intersection(set(memory.tags))

        # 차감된 결과
        remaining_tags = set(base_memory.tags) - common_tags  # noqa: F841
        result_content = f"차감된 정보: {base_memory.content} (제외: {', '.join(common_tags)})"

        confidence = base_memory.classification_confidence * 0.8

        return {"result": result_content, "confidence": confidence}

    async def _compare_memories(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """메모리 비교 연산"""
        if len(memories) < 2:
            return {"result": "Insufficient memories for comparison", "confidence": 0.0}

        # 메모리 간 유사성 분석
        similarities = []
        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                similarity = self._cosine_similarity(memories[i].vector_data, memories[j].vector_data)
                similarities.append(similarity)

        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0

        # 비교 결과 생성
        if avg_similarity > 0.7:
            comparison_result = "높은 유사성"
        elif avg_similarity > 0.4:
            comparison_result = "중간 유사성"
        else:
            comparison_result = "낮은 유사성"

        result_content = f"비교 결과: {comparison_result} (평균 유사도: {avg_similarity:.3f})"

        return {"result": result_content, "confidence": avg_similarity}

    async def _integrate_memories(self, memories: List[MemoryEntry]) -> Dict[str, Any]:
        """메모리 통합 연산"""
        # 메모리들을 의미적으로 통합
        integrated_content = "통합된 지식: "
        integrated_parts = []

        for memory in memories:
            integrated_parts.append(f"{memory.content}")

        integrated_content += " + ".join(integrated_parts)

        # 통합 신뢰도 계산
        avg_confidence = sum(m.classification_confidence for m in memories) / len(memories)
        integration_bonus = 0.1  # 통합 자체의 가치

        confidence = min(1.0, avg_confidence + integration_bonus)

        return {"result": integrated_content, "confidence": confidence}

    async def _store_in_working_memory(
        self,
        operation_type: str,
        memory_ids: List[str],
        operation_result: Dict[str, Any],
    ) -> str:
        """작업 기억 버퍼에 저장"""
        buffer_id = f"wm_{int(time.time() * 1000)}"  # noqa: F821

        # 작업 기억 용량 확인
        if len(self.working_memory_buffers) >= self.working_memory_capacity:
            # 가장 오래된 버퍼 제거
            oldest_buffer = min(self.working_memory_buffers.values(), key=lambda x: x.created_at)
            del self.working_memory_buffers[oldest_buffer.id]

        # 새 버퍼 생성
        buffer = WorkingMemoryBuffer(
            id=buffer_id,
            content=operation_result["result"],
            operation_type=operation_type,
            operands=memory_ids,
            result=operation_result["result"],
            confidence=operation_result["confidence"],
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(seconds=self.working_memory_ttl),
        )

        self.working_memory_buffers[buffer_id] = buffer

        logger.info(f"💾 작업 기억 버퍼 저장: {buffer_id}")
        return buffer_id

    def _calculate_memory_similarity(self, memories: List[MemoryEntry]) -> float:
        """메모리 간 유사성 계산"""
        if len(memories) < 2:
            return 0.0

        similarities = []
        for i in range(len(memories)):
            for j in range(i + 1, len(memories)):
                similarity = self._cosine_similarity(memories[i].vector_data, memories[j].vector_data)
                similarities.append(similarity)

        return sum(similarities) / len(similarities) if similarities else 0.0

    async def get_working_memory_status(self) -> Dict[str, Any]:
        """작업 기억 상태 조회"""
        # 만료된 버퍼 정리
        current_time = datetime.now()
        expired_buffers = [
            buffer_id for buffer_id, buffer in self.working_memory_buffers.items() if current_time > buffer.expires_at
        ]

        for buffer_id in expired_buffers:
            del self.working_memory_buffers[buffer_id]

        return {
            "total_buffers": len(self.working_memory_buffers),
            "capacity": self.working_memory_capacity,
            "utilization": len(self.working_memory_buffers) / self.working_memory_capacity,
            "buffers": [
                {
                    "id": buffer.id,
                    "content": buffer.content,
                    "operation_type": buffer.operation_type,
                    "confidence": buffer.confidence,
                    "expires_at": buffer.expires_at.isoformat(),
                    "access_count": buffer.access_count,
                }
                for buffer in self.working_memory_buffers.values()
            ],
            "operation_history_count": len(self.operation_history),
        }

    async def access_working_memory(self, buffer_id: str) -> Dict[str, Any]:
        """작업 기억 버퍼 접근"""
        if buffer_id not in self.working_memory_buffers:
            return {"success": False, "error": "Buffer not found"}

        buffer = self.working_memory_buffers[buffer_id]

        # 만료 확인
        if datetime.now() > buffer.expires_at:
            del self.working_memory_buffers[buffer_id]
            return {"success": False, "error": "Buffer expired"}

        # 접근 횟수 증가
        buffer.access_count += 1

        return {
            "success": True,
            "buffer": {
                "id": buffer.id,
                "content": buffer.content,
                "operation_type": buffer.operation_type,
                "confidence": buffer.confidence,
                "access_count": buffer.access_count,
            },
        }

    # Phase 6.2.6 - 시맨틱 지식 연결망 기능들

    async def add_semantic_concept(
        self,
        name: str,
        concept_type: ConceptType,
        description: str = "",
        properties: Dict[str, Any] = None,
        confidence: float = 0.8,
    ) -> str:
        """시맨틱 개념 추가"""
        try:
            concept_id = await self.semantic_graph.add_concept(name, concept_type, description, properties, confidence)
            logger.info(f"시맨틱 개념 추가: {name}")
            return concept_id
        except Exception as e:
            logger.error(f"시맨틱 개념 추가 실패: {e}")
            return None

    async def add_semantic_inference(
        self,
        source_name: str,
        target_name: str,
        inference_type: InferenceType,
        confidence: float = 0.7,
        evidence: List[str] = None,
    ) -> str:
        """시맨틱 추론 추가"""
        try:
            edge_id = await self.semantic_graph.add_inference(
                source_name, target_name, inference_type, confidence, evidence
            )
            logger.info(f"시맨틱 추론 추가: {source_name} -> {target_name}")
            return edge_id
        except Exception as e:
            logger.error(f"시맨틱 추론 추가 실패: {e}")
            return None

    async def find_semantic_path(
        self, source_name: str, target_name: str, max_length: int = 5
    ) -> Optional[Dict[str, Any]]:
        """시맨틱 경로 찾기"""
        try:
            path = await self.semantic_graph.find_semantic_path(source_name, target_name, max_length)
            if path:
                return {
                    "success": True,
                    "path": {
                        "source": path.source_concept,
                        "target": path.target_concept,
                        "path_length": path.path_length,
                        "total_confidence": path.total_confidence,
                        "inference_chain": [inference.value for inference in path.inference_chain],
                    },
                }
            else:
                return {"success": False, "error": "경로를 찾을 수 없음"}
        except Exception as e:
            logger.error(f"시맨틱 경로 찾기 실패: {e}")
            return {"success": False, "error": str(e)}

    async def infer_semantic_knowledge(
        self, concept_name: str, inference_type: InferenceType = None
    ) -> List[Dict[str, Any]]:
        """시맨틱 지식 추론"""
        try:
            inferences = await self.semantic_graph.infer_new_knowledge(concept_name, inference_type)
            logger.info(f"시맨틱 지식 추론 완료: {concept_name} -> {len(inferences)}개 추론")
            return inferences
        except Exception as e:
            logger.error(f"시맨틱 지식 추론 실패: {e}")
            return []

    async def analyze_semantic_similarity(self, concept1_name: str, concept2_name: str) -> float:
        """시맨틱 유사도 분석"""
        try:
            similarity = await self.semantic_graph.analyze_semantic_similarity(concept1_name, concept2_name)
            logger.info(f"시맨틱 유사도 분석: {concept1_name} vs {concept2_name} = {similarity:.3f}")
            return similarity
        except Exception as e:
            logger.error(f"시맨틱 유사도 분석 실패: {e}")
            return 0.0

    async def get_semantic_graph_status(self) -> Dict[str, Any]:
        """시맨틱 그래프 상태 반환"""
        try:
            status = await self.semantic_graph.get_knowledge_graph_status()
            return {
                "success": status.success,
                "concept_count": status.concept_count,
                "edge_count": status.edge_count,
                "average_confidence": status.average_confidence,
                "graph_density": status.graph_density,
                "connected_components": status.connected_components,
                "created_at": status.created_at,
            }
        except Exception as e:
            logger.error(f"시맨틱 그래프 상태 조회 실패: {e}")
            return {"success": False, "error": str(e)}

    async def optimize_semantic_graph(self) -> Dict[str, Any]:
        """시맨틱 그래프 최적화"""
        try:
            optimization_results = await self.semantic_graph.semantic_optimizer.optimize_graph()
            logger.info(f"시맨틱 그래프 최적화 완료: {optimization_results}")
            return optimization_results
        except Exception as e:
            logger.error(f"시맨틱 그래프 최적화 실패: {e}")
            return {}


# 테스트 함수
async def test_enhanced_memory_system():
    """고도화된 기억 시스템 테스트"""
    print("=== DuRiCore Phase 5 Day 2 - 고도화된 기억 시스템 테스트 ===")

    # 시스템 초기화
    memory_system = EnhancedMemorySystem()

    # 테스트 데이터
    test_memories = [
        {
            "content": "오늘 새로운 머신러닝 알고리즘을 학습했다. 매우 흥미로웠다.",
            "context": {"type": "learning", "emotion": "excited", "importance": "high"},
            "importance": 0.9,
        },
        {
            "content": "친구와 함께 영화를 봤다. 정말 재미있었다.",
            "context": {
                "type": "experience",
                "emotion": "happy",
                "importance": "medium",
            },
            "importance": 0.7,
        },
        {
            "content": "코딩할 때 항상 같은 패턴을 사용하는 것을 발견했다.",
            "context": {
                "type": "pattern",
                "emotion": "neutral",
                "importance": "medium",
            },
            "importance": 0.6,
        },
        {
            "content": "시험 결과가 나왔는데 실망스럽다.",
            "context": {
                "type": "emotion",
                "emotion": "disappointed",
                "importance": "high",
            },
            "importance": 0.8,
        },
    ]

    # 메모리 저장 테스트
    print("\n1. 메모리 저장 테스트")
    memory_ids = []
    for i, test_memory in enumerate(test_memories):
        memory_id = await memory_system.store_memory(
            test_memory["content"], test_memory["context"], test_memory["importance"]
        )
        memory_ids.append(memory_id)
        print(f"메모리 {i+1} 저장: {memory_id}")

    # 메모리 검색 테스트
    print("\n2. 메모리 검색 테스트")
    search_results = await memory_system.search_memories("학습", limit=3)
    print(f"'학습' 관련 메모리 검색 결과: {len(search_results)}개")
    for memory, similarity in search_results:
        print(f"  - {memory.content[:50]}... (유사도: {similarity:.3f})")

    # 연관 메모리 검색 테스트
    print("\n3. 연관 메모리 검색 테스트")
    if memory_ids:
        related_memories = await memory_system.get_related_memories(memory_ids[0], limit=3)
        print(f"첫 번째 메모리의 연관 메모리: {len(related_memories)}개")
        for memory, strength in related_memories:
            print(f"  - {memory.content[:50]}... (강도: {strength:.3f})")

    # 통계 정보 테스트
    print("\n4. 통계 정보 테스트")
    stats = await memory_system.get_memory_statistics()
    print(f"총 메모리 수: {stats.get('total_memories', 0)}")
    print(f"타입별 분포: {stats.get('memory_types', {})}")

    # 우선순위 업데이트 테스트
    print("\n5. 우선순위 업데이트 테스트")
    if memory_ids:
        await memory_system.update_memory_importance(memory_ids[0], 0.95)
        updated_memory = memory_system.memories.get(memory_ids[0])
        if updated_memory:
            print(f"우선순위 업데이트: {updated_memory.priority_score:.3f}")

    # Phase 6.2.2 - Working Memory 연산 테스트
    print("\n6. Working Memory 연산 테스트")
    if len(memory_ids) >= 2:
        # 메모리 추가 연산
        add_result = await memory_system.perform_memory_operation("addition", memory_ids[:2])
        print(f"메모리 추가 연산: {add_result.get('success', False)}")
        if add_result.get("success"):
            print(f"  결과: {add_result.get('result', '')[:50]}...")
            print(f"  신뢰도: {add_result.get('confidence', 0):.3f}")

        # 메모리 비교 연산
        compare_result = await memory_system.perform_memory_operation("comparison", memory_ids[:2])
        print(f"메모리 비교 연산: {compare_result.get('success', False)}")
        if compare_result.get("success"):
            print(f"  결과: {compare_result.get('result', '')[:50]}...")
            print(f"  신뢰도: {compare_result.get('confidence', 0):.3f}")

        # 메모리 통합 연산
        integrate_result = await memory_system.perform_memory_operation("integration", memory_ids)
        print(f"메모리 통합 연산: {integrate_result.get('success', False)}")
        if integrate_result.get("success"):
            print(f"  결과: {integrate_result.get('result', '')[:50]}...")
            print(f"  신뢰도: {integrate_result.get('confidence', 0):.3f}")

    # Working Memory 상태 조회
    print("\n7. Working Memory 상태 조회")
    wm_status = await memory_system.get_working_memory_status()
    print(f"작업 기억 버퍼 수: {wm_status.get('total_buffers', 0)}")
    print(f"용량: {wm_status.get('capacity', 0)}")
    print(f"사용률: {wm_status.get('utilization', 0):.1%}")
    print(f"연산 히스토리 수: {wm_status.get('operation_history_count', 0)}")

    # Working Memory 버퍼 접근 테스트
    print("\n8. Working Memory 버퍼 접근 테스트")
    if wm_status.get("buffers"):
        buffer_id = wm_status["buffers"][0]["id"]
        access_result = await memory_system.access_working_memory(buffer_id)
        print(f"버퍼 접근: {access_result.get('success', False)}")
        if access_result.get("success"):
            buffer_info = access_result.get("buffer", {})
            print(f"  내용: {buffer_info.get('content', '')[:50]}...")
            print(f"  연산 유형: {buffer_info.get('operation_type', '')}")
            print(f"  접근 횟수: {buffer_info.get('access_count', 0)}")

    print("\n=== Phase 6.2.2 Working Memory 연산 테스트 완료 ===")


if __name__ == "__main__":
    asyncio.run(test_enhanced_memory_system())
