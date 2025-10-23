#!/usr/bin/env python3
"""
DuRiCore - 벡터 기반 메모리 저장소
의미 기반 메모리 + 유사도 검색 시스템
"""

import hashlib
import json
import logging
import math
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """메모리 엔트리"""

    id: str
    content: str
    semantic_vector: List[float]  # 의미 벡터
    emotion_vector: List[float]  # 감정 벡터
    context_vector: List[float]  # 맥락 벡터
    importance: float  # 중요도 (0.0 ~ 1.0)
    memory_type: str  # 메모리 타입
    created_at: datetime
    accessed_count: int  # 접근 횟수
    last_accessed: datetime
    tags: List[str]  # 태그
    associations: List[str]  # 연관 메모리 ID들


class VectorMemoryStore:
    """벡터 기반 메모리 저장소"""

    def __init__(self):
        self.memories: Dict[str, MemoryEntry] = {}
        self.semantic_index: Dict[str, List[float]] = {}
        self.emotion_index: Dict[str, List[float]] = {}
        self.context_index: Dict[str, List[float]] = {}

        # 벡터 차원
        self.semantic_dim = 128
        self.emotion_dim = 10
        self.context_dim = 64

        # 유사도 임계값
        self.similarity_threshold = 0.7

        logger.info("벡터 메모리 저장소 초기화 완료")

    def store_memory(
        self,
        content: str,
        emotion_data: Dict[str, Any],
        context_data: Dict[str, Any],
        importance: float = 0.5,
    ) -> str:
        """메모리 저장"""
        try:
            # 고유 ID 생성
            memory_id = self._generate_memory_id(content, emotion_data, context_data)

            # 벡터 생성
            semantic_vector = self._create_semantic_vector(content)
            emotion_vector = self._create_emotion_vector(emotion_data)
            context_vector = self._create_context_vector(context_data)

            # 태그 추출
            tags = self._extract_tags(content, emotion_data, context_data)

            # 메모리 엔트리 생성
            memory_entry = MemoryEntry(
                id=memory_id,
                content=content,
                semantic_vector=semantic_vector,
                emotion_vector=emotion_vector,
                context_vector=context_vector,
                importance=importance,
                memory_type=self._determine_memory_type(content, emotion_data),
                created_at=datetime.now(),
                accessed_count=0,
                last_accessed=datetime.now(),
                tags=tags,
                associations=[],
            )

            # 저장
            self.memories[memory_id] = memory_entry
            self.semantic_index[memory_id] = semantic_vector
            self.emotion_index[memory_id] = emotion_vector
            self.context_index[memory_id] = context_vector

            # 연관 메모리 찾기 및 연결
            self._find_and_link_associations(memory_id)

            logger.info(f"메모리 저장 완료: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"메모리 저장 오류: {e}")
            return ""

    def search_similar_memories(
        self,
        query: str,
        emotion_data: Optional[Dict[str, Any]] = None,
        context_data: Optional[Dict[str, Any]] = None,
        limit: int = 5,
    ) -> List[Tuple[str, float]]:
        """유사한 메모리 검색"""
        try:
            # 쿼리 벡터 생성
            query_semantic = self._create_semantic_vector(query)
            query_emotion = (
                self._create_emotion_vector(emotion_data)
                if emotion_data
                else [0.0] * self.emotion_dim
            )
            query_context = (
                self._create_context_vector(context_data)
                if context_data
                else [0.0] * self.context_dim
            )

            similarities = []

            for memory_id, memory in self.memories.items():
                # 각 차원별 유사도 계산
                semantic_sim = self._cosine_similarity(
                    query_semantic, memory.semantic_vector
                )
                emotion_sim = self._cosine_similarity(
                    query_emotion, memory.emotion_vector
                )
                context_sim = self._cosine_similarity(
                    query_context, memory.context_vector
                )

                # 가중 평균 유사도
                weighted_sim = (
                    semantic_sim * 0.5 + emotion_sim * 0.3 + context_sim * 0.2
                )

                # 중요도 보정
                adjusted_sim = weighted_sim * (0.5 + memory.importance * 0.5)

                if adjusted_sim >= self.similarity_threshold:
                    similarities.append((memory_id, adjusted_sim))

            # 유사도 순으로 정렬
            similarities.sort(key=lambda x: x[1], reverse=True)

            # 접근 횟수 업데이트
            for memory_id, _ in similarities[:limit]:
                if memory_id in self.memories:
                    self.memories[memory_id].accessed_count += 1
                    self.memories[memory_id].last_accessed = datetime.now()

            return similarities[:limit]

        except Exception as e:
            logger.error(f"메모리 검색 오류: {e}")
            return []

    def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """ID로 메모리 조회"""
        return self.memories.get(memory_id)

    def get_memories_by_tags(self, tags: List[str]) -> List[MemoryEntry]:
        """태그로 메모리 조회"""
        results = []
        for memory in self.memories.values():
            if any(tag in memory.tags for tag in tags):
                results.append(memory)
        return results

    def update_memory_importance(self, memory_id: str, new_importance: float):
        """메모리 중요도 업데이트"""
        if memory_id in self.memories:
            self.memories[memory_id].importance = max(0.0, min(1.0, new_importance))

    def delete_memory(self, memory_id: str) -> bool:
        """메모리 삭제"""
        if memory_id in self.memories:
            del self.memories[memory_id]
            del self.semantic_index[memory_id]
            del self.emotion_index[memory_id]
            del self.context_index[memory_id]
            return True
        return False

    def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 통계"""
        if not self.memories:
            return {"total_memories": 0}

        total_memories = len(self.memories)
        avg_importance = (
            sum(m.importance for m in self.memories.values()) / total_memories
        )
        avg_access_count = (
            sum(m.accessed_count for m in self.memories.values()) / total_memories
        )

        # 메모리 타입별 통계
        type_counts = {}
        for memory in self.memories.values():
            type_counts[memory.memory_type] = type_counts.get(memory.memory_type, 0) + 1

        return {
            "total_memories": total_memories,
            "average_importance": avg_importance,
            "average_access_count": avg_access_count,
            "memory_types": type_counts,
            "most_accessed": self._get_most_accessed_memories(5),
            "most_important": self._get_most_important_memories(5),
        }

    def _generate_memory_id(
        self, content: str, emotion_data: Dict[str, Any], context_data: Dict[str, Any]
    ) -> str:
        """메모리 ID 생성"""
        combined = f"{content}_{json.dumps(emotion_data, sort_keys=True)}_{json.dumps(context_data, sort_keys=True)}"
        return hashlib.md5(combined.encode()).hexdigest()[:16]

    def _create_semantic_vector(self, text: str) -> List[float]:
        """의미 벡터 생성 (간단한 해시 기반)"""
        # 실제로는 BERT나 Word2Vec 같은 임베딩 모델 사용
        vector = [0.0] * self.semantic_dim

        # 간단한 해시 기반 벡터 생성
        for i, char in enumerate(text):
            if i >= self.semantic_dim:
                break
            vector[i] = (ord(char) % 100) / 100.0

        # 정규화
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]

        return vector

    def _create_emotion_vector(self, emotion_data: Dict[str, Any]) -> List[float]:
        """감정 벡터 생성"""
        vector = [0.0] * self.emotion_dim

        if not emotion_data:
            return vector

        # 감정 카테고리별 매핑
        emotion_mapping = {
            "joy": 0,
            "sadness": 1,
            "anger": 2,
            "fear": 3,
            "surprise": 4,
            "disgust": 5,
            "love": 6,
            "contempt": 7,
            "anticipation": 8,
            "neutral": 9,
        }

        # 주요 감정 설정
        primary_emotion = emotion_data.get("primary_emotion", "neutral")
        if primary_emotion in emotion_mapping:
            idx = emotion_mapping[primary_emotion]
            intensity = emotion_data.get("intensity", 0.5)
            vector[idx] = intensity

        # 보조 감정들 설정
        secondary_emotions = emotion_data.get("secondary_emotions", [])
        for emotion in secondary_emotions:
            if emotion in emotion_mapping:
                idx = emotion_mapping[emotion]
                vector[idx] = max(vector[idx], 0.3)  # 보조 감정은 낮은 강도

        return vector

    def _create_context_vector(self, context_data: Dict[str, Any]) -> List[float]:
        """맥락 벡터 생성"""
        vector = [0.0] * self.context_dim

        if not context_data:
            return vector

        # 맥락 정보를 벡터로 변환
        context_keywords = [
            "일상",
            "업무",
            "관계",
            "건강",
            "취미",
            "학습",
            "여행",
            "음식",
            "음악",
            "영화",
            "책",
            "운동",
            "쇼핑",
            "게임",
            "예술",
            "기술",
        ]

        for i, keyword in enumerate(context_keywords):
            if i >= self.context_dim:
                break
            if keyword in str(context_data):
                vector[i] = 1.0

        return vector

    def _extract_tags(
        self, content: str, emotion_data: Dict[str, Any], context_data: Dict[str, Any]
    ) -> List[str]:
        """태그 추출"""
        tags = []

        # 감정 태그
        if emotion_data:
            primary = emotion_data.get("primary_emotion", "")
            if primary:
                tags.append(f"emotion:{primary}")

            intensity = emotion_data.get("intensity", 0.0)
            if intensity > 0.7:
                tags.append("high_intensity")
            elif intensity < 0.3:
                tags.append("low_intensity")

        # 맥락 태그
        if context_data:
            for key, value in context_data.items():
                if isinstance(value, str) and value:
                    tags.append(f"context:{key}:{value}")

        # 내용 기반 태그
        content_words = content.split()
        for word in content_words:
            if len(word) > 2:  # 2글자 이상만 태그로
                tags.append(f"word:{word}")

        return list(set(tags))  # 중복 제거

    def _determine_memory_type(self, content: str, emotion_data: Dict[str, Any]) -> str:
        """메모리 타입 결정"""
        if emotion_data and emotion_data.get("intensity", 0.0) > 0.8:
            return "emotional"
        elif len(content) > 100:
            return "detailed"
        elif emotion_data and emotion_data.get("sentiment_score", 0.0) > 0.5:
            return "positive"
        elif emotion_data and emotion_data.get("sentiment_score", 0.0) < -0.5:
            return "negative"
        else:
            return "neutral"

    def _find_and_link_associations(self, memory_id: str):
        """연관 메모리 찾기 및 연결"""
        if memory_id not in self.memories:
            return

        current_memory = self.memories[memory_id]
        associations = []

        for other_id, other_memory in self.memories.items():
            if other_id == memory_id:
                continue

            # 유사도 계산
            semantic_sim = self._cosine_similarity(
                current_memory.semantic_vector, other_memory.semantic_vector
            )
            emotion_sim = self._cosine_similarity(
                current_memory.emotion_vector, other_memory.emotion_vector
            )

            # 높은 유사도를 가진 메모리들을 연관으로 설정
            if semantic_sim > 0.8 or emotion_sim > 0.8:
                associations.append(other_id)

        # 연관 메모리 업데이트
        current_memory.associations = associations[:5]  # 최대 5개까지만

        # 상호 연관 설정
        for assoc_id in associations[:5]:
            if (
                assoc_id in self.memories
                and memory_id not in self.memories[assoc_id].associations
            ):
                self.memories[assoc_id].associations.append(memory_id)

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """코사인 유사도 계산"""
        if len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _get_most_accessed_memories(self, limit: int) -> List[Dict[str, Any]]:
        """가장 많이 접근된 메모리들"""
        sorted_memories = sorted(
            self.memories.values(), key=lambda x: x.accessed_count, reverse=True
        )
        return [
            {"id": m.id, "content": m.content[:50], "access_count": m.accessed_count}
            for m in sorted_memories[:limit]
        ]

    def _get_most_important_memories(self, limit: int) -> List[Dict[str, Any]]:
        """가장 중요한 메모리들"""
        sorted_memories = sorted(
            self.memories.values(), key=lambda x: x.importance, reverse=True
        )
        return [
            {"id": m.id, "content": m.content[:50], "importance": m.importance}
            for m in sorted_memories[:limit]
        ]

    def export_memories(self, filepath: str):
        """메모리 내보내기"""
        try:
            export_data = {
                "memories": {
                    mid: asdict(memory) for mid, memory in self.memories.items()
                },
                "semantic_index": self.semantic_index,
                "emotion_index": self.emotion_index,
                "context_index": self.context_index,
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"메모리 내보내기 완료: {filepath}")

        except Exception as e:
            logger.error(f"메모리 내보내기 오류: {e}")

    def import_memories(self, filepath: str):
        """메모리 가져오기"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            # 메모리 복원
            for mid, memory_data in import_data["memories"].items():
                # datetime 문자열을 datetime 객체로 변환
                memory_data["created_at"] = datetime.fromisoformat(
                    memory_data["created_at"]
                )
                memory_data["last_accessed"] = datetime.fromisoformat(
                    memory_data["last_accessed"]
                )

                self.memories[mid] = MemoryEntry(**memory_data)

            # 인덱스 복원
            self.semantic_index = import_data["semantic_index"]
            self.emotion_index = import_data["emotion_index"]
            self.context_index = import_data["context_index"]

            logger.info(f"메모리 가져오기 완료: {filepath}")

        except Exception as e:
            logger.error(f"메모리 가져오기 오류: {e}")
