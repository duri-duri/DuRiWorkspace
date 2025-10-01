#!/usr/bin/env python3
"""
DuRiCore Phase 5 Day 2 - 기억 연관 시스템
의미적, 시간적, 감정적 연관성 분석 및 강화 시스템
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import json
import logging
import math
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)


class AssociationType(Enum):
    """연관성 타입 열거형"""

    SEMANTIC = "semantic"  # 의미적 연관성
    TEMPORAL = "temporal"  # 시간적 연관성
    EMOTIONAL = "emotional"  # 감정적 연관성
    CONTEXTUAL = "contextual"  # 맥락적 연관성
    THEMATIC = "thematic"  # 주제적 연관성


class AssociationStrength(Enum):
    """연관성 강도 열거형"""

    WEAK = "weak"  # 약한 연관성 (0.0-0.3)
    MODERATE = "moderate"  # 중간 연관성 (0.3-0.7)
    STRONG = "strong"  # 강한 연관성 (0.7-1.0)


@dataclass
class AssociationLink:
    """연관성 링크"""

    source_id: str
    target_id: str
    association_type: AssociationType
    strength: float
    confidence: float
    created_at: datetime
    metadata: Dict[str, Any]
    evidence: List[str]


@dataclass
class AssociationAnalysis:
    """연관성 분석 결과"""

    memory_id: str
    associations: List[AssociationLink]
    total_associations: int
    strength_distribution: Dict[AssociationStrength, int]
    type_distribution: Dict[AssociationType, int]
    strongest_associations: List[AssociationLink]
    weakest_associations: List[AssociationLink]


class MemoryAssociationSystem:
    """기억 연관 시스템"""

    def __init__(self):
        self.associations: Dict[str, AssociationLink] = {}
        self.memory_graph: Dict[str, Set[str]] = defaultdict(set)
        self.association_cache: Dict[str, List[AssociationLink]] = {}

        # 연관성 임계값
        self.semantic_threshold = 0.6
        self.temporal_threshold = 0.5
        self.emotional_threshold = 0.7
        self.contextual_threshold = 0.5

        # 시간 윈도우 설정
        self.temporal_window_hours = 24
        self.emotional_window_hours = 48

        # 벡터 차원
        self.vector_dim = 128

        logger.info("기억 연관 시스템 초기화 완료")

    async def analyze_associations(
        self,
        memory_id: str,
        memory_content: str,
        memory_vector: List[float],
        memory_context: Dict[str, Any],
        all_memories: Dict[str, Any],
    ) -> List[AssociationLink]:
        """연관성 분석 및 생성"""
        try:
            associations = []

            # 1. 의미적 연관성 분석
            semantic_associations = await self._analyze_semantic_associations(
                memory_id, memory_content, memory_vector, all_memories
            )
            associations.extend(semantic_associations)

            # 2. 시간적 연관성 분석
            temporal_associations = await self._analyze_temporal_associations(
                memory_id, memory_context, all_memories
            )
            associations.extend(temporal_associations)

            # 3. 감정적 연관성 분석
            emotional_associations = await self._analyze_emotional_associations(
                memory_id, memory_content, memory_context, all_memories
            )
            associations.extend(emotional_associations)

            # 4. 맥락적 연관성 분석
            contextual_associations = await self._analyze_contextual_associations(
                memory_id, memory_context, all_memories
            )
            associations.extend(contextual_associations)

            # 5. 주제적 연관성 분석
            thematic_associations = await self._analyze_thematic_associations(
                memory_id, memory_content, all_memories
            )
            associations.extend(thematic_associations)

            # 연관성 저장 및 그래프 업데이트
            await self._store_associations(associations)

            logger.info(
                f"연관성 분석 완료: {memory_id} -> {len(associations)}개 연관성"
            )
            return associations

        except Exception as e:
            logger.error(f"연관성 분석 오류: {e}")
            return []

    async def find_related_memories(
        self,
        memory_id: str,
        association_type: Optional[AssociationType] = None,
        min_strength: float = 0.3,
        limit: int = 10,
    ) -> List[Tuple[str, float]]:
        """연관 메모리 검색"""
        try:
            related_memories = []

            # 캐시 확인
            cache_key = (
                f"{memory_id}_{association_type.value if association_type else 'all'}"
            )
            if cache_key in self.association_cache:
                cached_associations = self.association_cache[cache_key]
                for link in cached_associations:
                    if link.strength >= min_strength:
                        target_id = (
                            link.target_id
                            if link.source_id == memory_id
                            else link.source_id
                        )
                        related_memories.append((target_id, link.strength))

                # 강도 순으로 정렬
                related_memories.sort(key=lambda x: x[1], reverse=True)
                return related_memories[:limit]

            # 그래프에서 직접 검색
            if memory_id in self.memory_graph:
                for related_id in self.memory_graph[memory_id]:
                    link_key = self._get_link_key(memory_id, related_id)
                    if link_key in self.associations:
                        link = self.associations[link_key]

                        if (
                            association_type is None
                            or link.association_type == association_type
                        ) and link.strength >= min_strength:
                            related_memories.append((related_id, link.strength))

            # 강도 순으로 정렬
            related_memories.sort(key=lambda x: x[1], reverse=True)

            # 캐시 저장
            self.association_cache[cache_key] = [
                self.associations[self._get_link_key(memory_id, related_id)]
                for related_id, _ in related_memories[:limit]
                if self._get_link_key(memory_id, related_id) in self.associations
            ]

            return related_memories[:limit]

        except Exception as e:
            logger.error(f"연관 메모리 검색 오류: {e}")
            return []

    async def get_association_analysis(self, memory_id: str) -> AssociationAnalysis:
        """연관성 분석 결과 조회"""
        try:
            associations = []

            # 메모리와 관련된 모든 연관성 링크 수집
            for link in self.associations.values():
                if link.source_id == memory_id or link.target_id == memory_id:
                    associations.append(link)

            # 통계 계산
            total_associations = len(associations)

            # 강도 분포
            strength_distribution = Counter()
            for link in associations:
                strength = self._get_strength_category(link.strength)
                strength_distribution[strength] += 1

            # 타입 분포
            type_distribution = Counter()
            for link in associations:
                type_distribution[link.association_type] += 1

            # 가장 강한/약한 연관성
            strongest_associations = sorted(
                associations, key=lambda x: x.strength, reverse=True
            )[:5]
            weakest_associations = sorted(associations, key=lambda x: x.strength)[:5]

            return AssociationAnalysis(
                memory_id=memory_id,
                associations=associations,
                total_associations=total_associations,
                strength_distribution=dict(strength_distribution),
                type_distribution=dict(type_distribution),
                strongest_associations=strongest_associations,
                weakest_associations=weakest_associations,
            )

        except Exception as e:
            logger.error(f"연관성 분석 조회 오류: {e}")
            return AssociationAnalysis(
                memory_id=memory_id,
                associations=[],
                total_associations=0,
                strength_distribution={},
                type_distribution={},
                strongest_associations=[],
                weakest_associations=[],
            )

    async def strengthen_association(
        self,
        source_id: str,
        target_id: str,
        association_type: AssociationType,
        additional_evidence: List[str],
    ) -> bool:
        """연관성 강화"""
        try:
            link_key = self._get_link_key(source_id, target_id)

            if link_key in self.associations:
                link = self.associations[link_key]

                # 기존 증거에 추가
                link.evidence.extend(additional_evidence)

                # 강도 재계산
                new_strength = self._recalculate_strength(link, additional_evidence)
                link.strength = min(
                    1.0, link.strength + (new_strength - link.strength) * 0.3
                )

                # 신뢰도 업데이트
                link.confidence = min(1.0, link.confidence + 0.1)

                logger.info(
                    f"연관성 강화 완료: {source_id} -> {target_id} (새 강도: {link.strength:.3f})"
                )
                return True

            return False

        except Exception as e:
            logger.error(f"연관성 강화 오류: {e}")
            return False

    async def remove_weak_associations(self, min_strength: float = 0.2) -> int:
        """약한 연관성 제거"""
        try:
            to_remove = []

            for link_key, link in self.associations.items():
                if link.strength < min_strength:
                    to_remove.append(link_key)

            for link_key in to_remove:
                link = self.associations[link_key]

                # 그래프에서 제거
                if link.source_id in self.memory_graph:
                    self.memory_graph[link.source_id].discard(link.target_id)
                if link.target_id in self.memory_graph:
                    self.memory_graph[link.target_id].discard(link.source_id)

                # 연관성 제거
                del self.associations[link_key]

            # 캐시 클리어
            self.association_cache.clear()

            logger.info(f"약한 연관성 제거 완료: {len(to_remove)}개")
            return len(to_remove)

        except Exception as e:
            logger.error(f"약한 연관성 제거 오류: {e}")
            return 0

    # 내부 메서드들
    async def _analyze_semantic_associations(
        self,
        memory_id: str,
        memory_content: str,
        memory_vector: List[float],
        all_memories: Dict[str, Any],
    ) -> List[AssociationLink]:
        """의미적 연관성 분석"""
        try:
            associations = []

            for other_id, other_memory in all_memories.items():
                if other_id == memory_id:
                    continue

                # 벡터 유사도 계산
                if hasattr(other_memory, "vector_data"):
                    similarity = self._cosine_similarity(
                        memory_vector, other_memory.vector_data
                    )

                    if similarity > self.semantic_threshold:
                        evidence = [
                            f"벡터 유사도: {similarity:.3f}",
                            f"내용 유사성: 높음",
                        ]

                        association = AssociationLink(
                            source_id=memory_id,
                            target_id=other_id,
                            association_type=AssociationType.SEMANTIC,
                            strength=similarity,
                            confidence=0.8,
                            created_at=datetime.now(),
                            metadata={"similarity": similarity},
                            evidence=evidence,
                        )

                        associations.append(association)

            return associations

        except Exception as e:
            logger.error(f"의미적 연관성 분석 오류: {e}")
            return []

    async def _analyze_temporal_associations(
        self,
        memory_id: str,
        memory_context: Dict[str, Any],
        all_memories: Dict[str, Any],
    ) -> List[AssociationLink]:
        """시간적 연관성 분석"""
        try:
            associations = []
            current_time = datetime.now()

            for other_id, other_memory in all_memories.items():
                if other_id == memory_id:
                    continue

                # 시간 차이 계산
                if hasattr(other_memory, "created_at"):
                    time_diff = abs(
                        (current_time - other_memory.created_at).total_seconds()
                    )

                    if time_diff < self.temporal_window_hours * 3600:  # 시간 윈도우 내
                        # 시간적 강도 계산 (가까울수록 강함)
                        temporal_strength = max(
                            0, 1 - (time_diff / (self.temporal_window_hours * 3600))
                        )

                        if temporal_strength > self.temporal_threshold:
                            evidence = [
                                f"시간 차이: {time_diff/3600:.1f}시간",
                                f"시간적 근접성: 높음",
                            ]

                            association = AssociationLink(
                                source_id=memory_id,
                                target_id=other_id,
                                association_type=AssociationType.TEMPORAL,
                                strength=temporal_strength,
                                confidence=0.7,
                                created_at=datetime.now(),
                                metadata={"time_diff_hours": time_diff / 3600},
                                evidence=evidence,
                            )

                            associations.append(association)

            return associations

        except Exception as e:
            logger.error(f"시간적 연관성 분석 오류: {e}")
            return []

    async def _analyze_emotional_associations(
        self,
        memory_id: str,
        memory_content: str,
        memory_context: Dict[str, Any],
        all_memories: Dict[str, Any],
    ) -> List[AssociationLink]:
        """감정적 연관성 분석"""
        try:
            associations = []

            # 현재 메모리의 감정 분석
            current_emotion = self._extract_emotion(memory_content, memory_context)

            for other_id, other_memory in all_memories.items():
                if other_id == memory_id:
                    continue

                # 다른 메모리의 감정 분석
                if hasattr(other_memory, "content"):
                    other_emotion = self._extract_emotion(
                        other_memory.content, getattr(other_memory, "context_info", {})
                    )

                    # 감정 유사도 계산
                    emotion_similarity = self._calculate_emotion_similarity(
                        current_emotion, other_emotion
                    )

                    if emotion_similarity > self.emotional_threshold:
                        evidence = [
                            f"감정 유사도: {emotion_similarity:.3f}",
                            f"현재 감정: {current_emotion}",
                            f"대상 감정: {other_emotion}",
                        ]

                        association = AssociationLink(
                            source_id=memory_id,
                            target_id=other_id,
                            association_type=AssociationType.EMOTIONAL,
                            strength=emotion_similarity,
                            confidence=0.8,
                            created_at=datetime.now(),
                            metadata={
                                "current_emotion": current_emotion,
                                "other_emotion": other_emotion,
                            },
                            evidence=evidence,
                        )

                        associations.append(association)

            return associations

        except Exception as e:
            logger.error(f"감정적 연관성 분석 오류: {e}")
            return []

    async def _analyze_contextual_associations(
        self,
        memory_id: str,
        memory_context: Dict[str, Any],
        all_memories: Dict[str, Any],
    ) -> List[AssociationLink]:
        """맥락적 연관성 분석"""
        try:
            associations = []

            for other_id, other_memory in all_memories.items():
                if other_id == memory_id:
                    continue

                # 컨텍스트 유사도 계산
                if hasattr(other_memory, "context_info"):
                    context_similarity = self._calculate_context_similarity(
                        memory_context, other_memory.context_info
                    )

                    if context_similarity > self.contextual_threshold:
                        evidence = [
                            f"맥락 유사도: {context_similarity:.3f}",
                            f"공통 컨텍스트 요소 발견",
                        ]

                        association = AssociationLink(
                            source_id=memory_id,
                            target_id=other_id,
                            association_type=AssociationType.CONTEXTUAL,
                            strength=context_similarity,
                            confidence=0.7,
                            created_at=datetime.now(),
                            metadata={"context_similarity": context_similarity},
                            evidence=evidence,
                        )

                        associations.append(association)

            return associations

        except Exception as e:
            logger.error(f"맥락적 연관성 분석 오류: {e}")
            return []

    async def _analyze_thematic_associations(
        self, memory_id: str, memory_content: str, all_memories: Dict[str, Any]
    ) -> List[AssociationLink]:
        """주제적 연관성 분석"""
        try:
            associations = []

            # 현재 메모리의 주제 추출
            current_themes = self._extract_themes(memory_content)

            for other_id, other_memory in all_memories.items():
                if other_id == memory_id:
                    continue

                # 다른 메모리의 주제 추출
                if hasattr(other_memory, "content"):
                    other_themes = self._extract_themes(other_memory.content)

                    # 주제 유사도 계산
                    theme_similarity = self._calculate_theme_similarity(
                        current_themes, other_themes
                    )

                    if theme_similarity > 0.5:  # 주제 임계값
                        evidence = [
                            f"주제 유사도: {theme_similarity:.3f}",
                            f"공통 주제: {list(set(current_themes) & set(other_themes))}",
                        ]

                        association = AssociationLink(
                            source_id=memory_id,
                            target_id=other_id,
                            association_type=AssociationType.THEMATIC,
                            strength=theme_similarity,
                            confidence=0.6,
                            created_at=datetime.now(),
                            metadata={
                                "current_themes": current_themes,
                                "other_themes": other_themes,
                            },
                            evidence=evidence,
                        )

                        associations.append(association)

            return associations

        except Exception as e:
            logger.error(f"주제적 연관성 분석 오류: {e}")
            return []

    async def _store_associations(self, associations: List[AssociationLink]):
        """연관성 저장"""
        try:
            for association in associations:
                link_key = self._get_link_key(
                    association.source_id, association.target_id
                )
                self.associations[link_key] = association

                # 그래프 업데이트
                self.memory_graph[association.source_id].add(association.target_id)
                self.memory_graph[association.target_id].add(association.source_id)

            # 캐시 클리어
            self.association_cache.clear()

        except Exception as e:
            logger.error(f"연관성 저장 오류: {e}")

    def _get_link_key(self, source_id: str, target_id: str) -> str:
        """연관성 링크 키 생성"""
        return f"{min(source_id, target_id)}_{max(source_id, target_id)}"

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        try:
            if len(vec1) != len(vec2):
                return 0.0

            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = math.sqrt(sum(a * a for a in vec1))
            norm2 = math.sqrt(sum(a * a for a in vec2))

            if norm1 == 0 or norm2 == 0:
                return 0.0

            return dot_product / (norm1 * norm2)

        except Exception as e:
            logger.error(f"유사도 계산 오류: {e}")
            return 0.0

    def _extract_emotion(self, content: str, context: Dict[str, Any]) -> str:
        """감정 추출"""
        try:
            # 감정 키워드 사전
            emotion_keywords = {
                "positive": [
                    "행복",
                    "기쁨",
                    "즐거움",
                    "신기",
                    "재미",
                    "좋다",
                    "만족",
                    "감동",
                ],
                "negative": [
                    "슬픔",
                    "화남",
                    "짜증",
                    "우울",
                    "실망",
                    "걱정",
                    "불안",
                    "스트레스",
                ],
                "neutral": ["보통", "그냥", "평범", "무덤덤", "차분", "평온"],
            }

            # 컨텍스트에서 감정 확인
            if "emotion" in context:
                return context["emotion"]

            # 내용에서 감정 키워드 검색
            for emotion_type, keywords in emotion_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        return emotion_type

            return "neutral"

        except Exception as e:
            logger.error(f"감정 추출 오류: {e}")
            return "neutral"

    def _calculate_emotion_similarity(self, emotion1: str, emotion2: str) -> float:
        """감정 유사도 계산"""
        try:
            if emotion1 == emotion2:
                return 1.0
            elif (emotion1 == "positive" and emotion2 == "negative") or (
                emotion1 == "negative" and emotion2 == "positive"
            ):
                return 0.0
            else:
                return 0.5  # neutral과의 유사도

        except Exception as e:
            logger.error(f"감정 유사도 계산 오류: {e}")
            return 0.0

    def _calculate_context_similarity(
        self, context1: Dict[str, Any], context2: Dict[str, Any]
    ) -> float:
        """컨텍스트 유사도 계산"""
        try:
            if not context1 or not context2:
                return 0.0

            # 공통 키 개수
            common_keys = set(context1.keys()) & set(context2.keys())
            if not common_keys:
                return 0.0

            # 공통 키의 값 유사도
            similar_values = 0
            for key in common_keys:
                if context1[key] == context2[key]:
                    similar_values += 1

            return similar_values / len(common_keys)

        except Exception as e:
            logger.error(f"컨텍스트 유사도 계산 오류: {e}")
            return 0.0

    def _extract_themes(self, content: str) -> List[str]:
        """주제 추출"""
        try:
            # 간단한 키워드 기반 주제 추출
            themes = []

            theme_keywords = {
                "학습": ["학습", "공부", "배우", "이해", "알다", "깨달"],
                "경험": ["경험", "발생", "일어나", "하다", "만나", "가다", "오다"],
                "감정": [
                    "감정",
                    "기분",
                    "느낌",
                    "행복",
                    "슬픔",
                    "화남",
                    "기쁨",
                    "우울",
                ],
                "패턴": ["패턴", "반복", "규칙", "습관", "경향", "항상", "늘"],
                "일상": ["일상", "하루", "매일", "평범", "보통"],
                "일": ["일", "업무", "회사", "직장", "프로젝트"],
                "여가": ["여가", "취미", "영화", "게임", "운동", "여행"],
            }

            for theme, keywords in theme_keywords.items():
                for keyword in keywords:
                    if keyword in content:
                        themes.append(theme)
                        break

            return list(set(themes))  # 중복 제거

        except Exception as e:
            logger.error(f"주제 추출 오류: {e}")
            return []

    def _calculate_theme_similarity(
        self, themes1: List[str], themes2: List[str]
    ) -> float:
        """주제 유사도 계산"""
        try:
            if not themes1 or not themes2:
                return 0.0

            # Jaccard 유사도
            intersection = set(themes1) & set(themes2)
            union = set(themes1) | set(themes2)

            if not union:
                return 0.0

            return len(intersection) / len(union)

        except Exception as e:
            logger.error(f"주제 유사도 계산 오류: {e}")
            return 0.0

    def _get_strength_category(self, strength: float) -> AssociationStrength:
        """강도 카테고리 결정"""
        if strength < 0.3:
            return AssociationStrength.WEAK
        elif strength < 0.7:
            return AssociationStrength.MODERATE
        else:
            return AssociationStrength.STRONG

    def _recalculate_strength(
        self, link: AssociationLink, additional_evidence: List[str]
    ) -> float:
        """강도 재계산"""
        try:
            # 기본 강도
            base_strength = link.strength

            # 증거 개수에 따른 보너스
            evidence_bonus = min(0.2, len(additional_evidence) * 0.05)

            # 신뢰도에 따른 보너스
            confidence_bonus = link.confidence * 0.1

            new_strength = base_strength + evidence_bonus + confidence_bonus

            return min(1.0, new_strength)

        except Exception as e:
            logger.error(f"강도 재계산 오류: {e}")
            return link.strength


# 테스트 함수
async def test_memory_association():
    """기억 연관 시스템 테스트"""
    print("=== DuRiCore Phase 5 Day 2 - 기억 연관 시스템 테스트 ===")

    # 시스템 초기화
    association_system = MemoryAssociationSystem()

    # 테스트 메모리 데이터
    test_memories = {
        "mem1": {
            "content": "오늘 새로운 머신러닝 알고리즘을 학습했다. 매우 흥미로웠다.",
            "vector_data": [0.1 + i * 0.01 for i in range(128)],
            "context_info": {
                "type": "learning",
                "emotion": "excited",
                "importance": "high",
            },
            "created_at": datetime.now(),
        },
        "mem2": {
            "content": "친구와 함께 영화를 봤다. 정말 재미있었다.",
            "vector_data": [0.2 + i * 0.01 for i in range(128)],
            "context_info": {
                "type": "experience",
                "emotion": "happy",
                "importance": "medium",
            },
            "created_at": datetime.now() - timedelta(hours=2),
        },
        "mem3": {
            "content": "코딩할 때 항상 같은 패턴을 사용하는 것을 발견했다.",
            "vector_data": [0.3 + i * 0.01 for i in range(128)],
            "context_info": {
                "type": "pattern",
                "emotion": "neutral",
                "importance": "medium",
            },
            "created_at": datetime.now() - timedelta(hours=1),
        },
        "mem4": {
            "content": "시험 결과가 나왔는데 실망스럽다.",
            "vector_data": [0.4 + i * 0.01 for i in range(128)],
            "context_info": {
                "type": "emotion",
                "emotion": "disappointed",
                "importance": "high",
            },
            "created_at": datetime.now() - timedelta(hours=3),
        },
    }

    # 연관성 분석 테스트
    print("\n1. 연관성 분석 테스트")
    for memory_id, memory_data in test_memories.items():
        # 테스트 데이터를 객체 형태로 변환
        class MockMemory:
            def __init__(self, data):
                self.content = data["content"]
                self.vector_data = data["vector_data"]
                self.context_info = data["context_info"]
                self.created_at = data["created_at"]

        # 모든 메모리를 MockMemory 객체로 변환
        mock_memories = {k: MockMemory(v) for k, v in test_memories.items()}

        associations = await association_system.analyze_associations(
            memory_id,
            memory_data["content"],
            memory_data["vector_data"],
            memory_data["context_info"],
            mock_memories,
        )
        print(f"메모리 {memory_id}: {len(associations)}개 연관성 발견")

    # 연관 메모리 검색 테스트
    print("\n2. 연관 메모리 검색 테스트")
    for memory_id in test_memories.keys():
        related_memories = await association_system.find_related_memories(
            memory_id, limit=3
        )
        print(f"메모리 {memory_id}의 연관 메모리: {len(related_memories)}개")
        for related_id, strength in related_memories:
            print(f"  - {related_id} (강도: {strength:.3f})")

    # 연관성 분석 결과 테스트
    print("\n3. 연관성 분석 결과 테스트")
    for memory_id in test_memories.keys():
        analysis = await association_system.get_association_analysis(memory_id)
        print(f"메모리 {memory_id} 분석:")
        print(f"  총 연관성: {analysis.total_associations}개")
        print(f"  타입 분포: {analysis.type_distribution}")
        print(f"  강도 분포: {analysis.strength_distribution}")

    # 연관성 강화 테스트
    print("\n4. 연관성 강화 테스트")
    if len(test_memories) >= 2:
        memory_ids = list(test_memories.keys())
        success = await association_system.strengthen_association(
            memory_ids[0], memory_ids[1], AssociationType.SEMANTIC, ["추가 증거"]
        )
        print(f"연관성 강화 결과: {'성공' if success else '실패'}")

    print("\n=== 테스트 완료 ===")


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_memory_association())
