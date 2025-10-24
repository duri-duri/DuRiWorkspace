#!/usr/bin/env python3
"""
DuRiCore - 메모리 매니저 최적화
Phase 4: Vector DB + JSON 저장 연동 메모리 구조
"""

import asyncio
import gzip
import hashlib
import json
import logging
import pickle
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class MemoryEntry:
    """메모리 엔트리"""

    id: str
    content: str
    memory_type: str
    importance: float
    created_at: datetime
    accessed_count: int
    last_accessed: datetime
    tags: List[str]
    associations: List[str]
    metadata: Dict[str, Any]
    vector_data: Optional[List[float]] = None


@dataclass
class MemoryQuery:
    """메모리 쿼리"""

    query: str
    memory_type: Optional[str] = None
    tags: Optional[List[str]] = None
    min_importance: float = 0.0
    limit: int = 10
    include_vectors: bool = False


class MemoryManager:
    """메모리 매니저"""

    def __init__(self, storage_path: str = "memory_data"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(exist_ok=True)

        # 메모리 저장소
        self.memories: Dict[str, MemoryEntry] = {}
        self.memory_index: Dict[str, List[str]] = {}  # 태그별 인덱스
        self.type_index: Dict[str, List[str]] = {}  # 타입별 인덱스

        # 성능 통계
        self.stats = {
            "total_memories": 0,
            "total_queries": 0,
            "cache_hits": 0,
            "average_query_time": 0.0,
            "storage_size": 0,
        }

        # 캐시
        self.query_cache: Dict[str, List[MemoryEntry]] = {}
        self.cache_ttl = 3600  # 1시간

        # 백그라운드 작업
        self.auto_save_task: Optional[asyncio.Task] = None
        self.cleanup_task: Optional[asyncio.Task] = None

        logger.info("메모리 매니저 초기화 완료")

    async def start(self):
        """메모리 매니저 시작"""
        # 기존 데이터 로드
        await self.load_memories()

        # 백그라운드 작업 시작
        self.auto_save_task = asyncio.create_task(self._auto_save_loop())
        self.cleanup_task = asyncio.create_task(self._cleanup_loop())

        logger.info("메모리 매니저 시작 완료")

    async def stop(self):
        """메모리 매니저 종료"""
        # 백그라운드 작업 중지
        if self.auto_save_task:
            self.auto_save_task.cancel()
        if self.cleanup_task:
            self.cleanup_task.cancel()

        # 최종 저장
        await self.save_memories()

        logger.info("메모리 매니저 종료 완료")

    async def store_memory(
        self,
        content: str,
        memory_type: str,
        importance: float = 0.5,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """메모리 저장"""
        try:
            start_time = time.time()

            # 고유 ID 생성
            memory_id = self._generate_memory_id(content, memory_type)

            # 메모리 엔트리 생성
            memory_entry = MemoryEntry(
                id=memory_id,
                content=content,
                memory_type=memory_type,
                importance=importance,
                created_at=datetime.now(),
                accessed_count=0,
                last_accessed=datetime.now(),
                tags=tags or [],
                associations=[],
                metadata=metadata or {},
                vector_data=None,  # 벡터 데이터는 별도 처리
            )

            # 저장
            self.memories[memory_id] = memory_entry

            # 인덱스 업데이트
            self._update_indexes(memory_id, memory_entry)

            # 통계 업데이트
            self.stats["total_memories"] += 1
            self._update_stats(time.time() - start_time)

            logger.info(f"메모리 저장 완료: {memory_id}")
            return memory_id

        except Exception as e:
            logger.error(f"메모리 저장 오류: {e}")
            raise

    async def search_memories(self, query: MemoryQuery) -> List[MemoryEntry]:
        """메모리 검색"""
        try:
            start_time = time.time()

            # 캐시 확인
            cache_key = self._generate_query_cache_key(query)
            if cache_key in self.query_cache:
                self.stats["cache_hits"] += 1
                logger.info(f"쿼리 캐시 히트: {cache_key}")
                return self.query_cache[cache_key]

            # 검색 실행
            results = []

            for memory_id, memory in self.memories.items():
                # 타입 필터
                if query.memory_type and memory.memory_type != query.memory_type:
                    continue

                # 중요도 필터
                if memory.importance < query.min_importance:
                    continue

                # 태그 필터
                if query.tags and not any(tag in memory.tags for tag in query.tags):
                    continue

                # 내용 검색 (간단한 키워드 매칭)
                if query.query.lower() in memory.content.lower():
                    results.append(memory)

            # 중요도와 접근 횟수로 정렬
            results.sort(key=lambda x: (x.importance, x.accessed_count), reverse=True)

            # 제한
            results = results[: query.limit]

            # 벡터 데이터 제거 (필요한 경우만)
            if not query.include_vectors:
                for result in results:
                    result.vector_data = None

            # 캐시에 저장
            self.query_cache[cache_key] = results

            # 통계 업데이트
            self.stats["total_queries"] += 1
            self._update_stats(time.time() - start_time)

            logger.info(f"메모리 검색 완료: {len(results)}개 결과")
            return results

        except Exception as e:
            logger.error(f"메모리 검색 오류: {e}")
            raise

    async def get_memory_by_id(self, memory_id: str) -> Optional[MemoryEntry]:
        """ID로 메모리 조회"""
        memory = self.memories.get(memory_id)
        if memory:
            memory.accessed_count += 1
            memory.last_accessed = datetime.now()
        return memory

    async def update_memory(self, memory_id: str, updates: Dict[str, Any]) -> bool:
        """메모리 업데이트"""
        try:
            if memory_id not in self.memories:
                return False

            memory = self.memories[memory_id]

            # 업데이트 가능한 필드들
            if "content" in updates:
                memory.content = updates["content"]
            if "importance" in updates:
                memory.importance = updates["importance"]
            if "tags" in updates:
                memory.tags = updates["tags"]
            if "metadata" in updates:
                memory.metadata.update(updates["metadata"])

            memory.last_accessed = datetime.now()

            # 인덱스 재구성
            self._rebuild_indexes()

            logger.info(f"메모리 업데이트 완료: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"메모리 업데이트 오류: {e}")
            return False

    async def delete_memory(self, memory_id: str) -> bool:
        """메모리 삭제"""
        try:
            if memory_id not in self.memories:
                return False

            # 메모리 삭제
            del self.memories[memory_id]

            # 인덱스 재구성
            self._rebuild_indexes()

            # 통계 업데이트
            self.stats["total_memories"] -= 1

            logger.info(f"메모리 삭제 완료: {memory_id}")
            return True

        except Exception as e:
            logger.error(f"메모리 삭제 오류: {e}")
            return False

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 통계"""
        type_counts = {}
        tag_counts = {}

        for memory in self.memories.values():
            # 타입별 카운트
            type_counts[memory.memory_type] = type_counts.get(memory.memory_type, 0) + 1

            # 태그별 카운트
            for tag in memory.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1

        return {
            **self.stats,
            "type_distribution": type_counts,
            "tag_distribution": tag_counts,
            "average_importance": (
                sum(m.importance for m in self.memories.values()) / len(self.memories) if self.memories else 0
            ),
            "most_accessed": sorted(self.memories.values(), key=lambda x: x.accessed_count, reverse=True)[:5],
        }

    async def save_memories(self):
        """메모리 저장"""
        try:
            # JSON 저장
            json_data = {
                "memories": {k: asdict(v) for k, v in self.memories.items()},
                "stats": self.stats,
                "timestamp": datetime.now().isoformat(),
            }

            json_file = self.storage_path / "memories.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2, default=str)

            # 압축 저장 (백업용)
            compressed_file = self.storage_path / "memories.pkl.gz"
            with gzip.open(compressed_file, "wb") as f:
                pickle.dump(self.memories, f)

            # 저장 크기 업데이트
            self.stats["storage_size"] = json_file.stat().st_size

            logger.info("메모리 저장 완료")

        except Exception as e:
            logger.error(f"메모리 저장 오류: {e}")
            raise

    async def load_memories(self):
        """메모리 로드"""
        try:
            json_file = self.storage_path / "memories.json"

            if json_file.exists():
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                # 메모리 로드
                for memory_id, memory_data in data["memories"].items():
                    # datetime 변환
                    memory_data["created_at"] = datetime.fromisoformat(memory_data["created_at"])
                    memory_data["last_accessed"] = datetime.fromisoformat(memory_data["last_accessed"])

                    memory_entry = MemoryEntry(**memory_data)
                    self.memories[memory_id] = memory_entry

                # 통계 로드
                if "stats" in data:
                    self.stats.update(data["stats"])

                # 인덱스 재구성
                self._rebuild_indexes()

                logger.info(f"메모리 로드 완료: {len(self.memories)}개")
            else:
                logger.info("저장된 메모리가 없습니다.")

        except Exception as e:
            logger.error(f"메모리 로드 오류: {e}")
            raise

    def _generate_memory_id(self, content: str, memory_type: str) -> str:
        """메모리 ID 생성"""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        timestamp = int(time.time() * 1000)
        return f"{memory_type}_{content_hash}_{timestamp}"

    def _generate_query_cache_key(self, query: MemoryQuery) -> str:
        """쿼리 캐시 키 생성"""
        query_data = {
            "query": query.query,
            "memory_type": query.memory_type,
            "tags": query.tags,
            "min_importance": query.min_importance,
            "limit": query.limit,
            "include_vectors": query.include_vectors,
        }
        return hashlib.md5(json.dumps(query_data, sort_keys=True).encode()).hexdigest()

    def _update_indexes(self, memory_id: str, memory: MemoryEntry):
        """인덱스 업데이트"""
        # 태그 인덱스
        for tag in memory.tags:
            if tag not in self.memory_index:
                self.memory_index[tag] = []
            if memory_id not in self.memory_index[tag]:
                self.memory_index[tag].append(memory_id)

        # 타입 인덱스
        if memory.memory_type not in self.type_index:
            self.type_index[memory.memory_type] = []
        if memory_id not in self.type_index[memory.memory_type]:
            self.type_index[memory.memory_type].append(memory_id)

    def _rebuild_indexes(self):
        """인덱스 재구성"""
        self.memory_index.clear()
        self.type_index.clear()

        for memory_id, memory in self.memories.items():
            self._update_indexes(memory_id, memory)

    def _update_stats(self, processing_time: float):
        """통계 업데이트"""
        if self.stats["total_queries"] > 0:
            current_avg = self.stats["average_query_time"]
            new_count = self.stats["total_queries"]
            self.stats["average_query_time"] = (current_avg * (new_count - 1) + processing_time) / new_count

    async def _auto_save_loop(self):
        """자동 저장 루프"""
        while True:
            try:
                await asyncio.sleep(300)  # 5분마다
                await self.save_memories()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"자동 저장 오류: {e}")

    async def _cleanup_loop(self):
        """정리 루프"""
        while True:
            try:
                await asyncio.sleep(600)  # 10분마다

                # 오래된 캐시 정리
                current_time = time.time()
                expired_keys = []

                for key in self.query_cache.keys():
                    # 간단한 TTL 체크 (실제로는 더 정교한 구현 필요)
                    if current_time % self.cache_ttl == 0:
                        expired_keys.append(key)

                for key in expired_keys:
                    del self.query_cache[key]

                if expired_keys:
                    logger.info(f"캐시 정리 완료: {len(expired_keys)}개")

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"정리 루프 오류: {e}")

    def clear_cache(self):
        """캐시 클리어"""
        self.query_cache.clear()
        logger.info("메모리 쿼리 캐시 클리어 완료")

    async def export_memories(self, filepath: str):
        """메모리 내보내기"""
        try:
            export_data = {
                "memories": {k: asdict(v) for k, v in self.memories.items()},
                "statistics": await self.get_memory_statistics(),
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)

            logger.info(f"메모리 내보내기 완료: {filepath}")

        except Exception as e:
            logger.error(f"메모리 내보내기 오류: {e}")
            raise

    async def import_memories(self, filepath: str):
        """메모리 가져오기"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                import_data = json.load(f)

            # 기존 메모리 백업
            backup_memories = self.memories.copy()

            # 새 메모리 로드
            for memory_id, memory_data in import_data["memories"].items():
                memory_data["created_at"] = datetime.fromisoformat(memory_data["created_at"])
                memory_data["last_accessed"] = datetime.fromisoformat(memory_data["last_accessed"])

                memory_entry = MemoryEntry(**memory_data)
                self.memories[memory_id] = memory_entry

            # 인덱스 재구성
            self._rebuild_indexes()

            logger.info(f"메모리 가져오기 완료: {len(import_data['memories'])}개")

        except Exception as e:
            logger.error(f"메모리 가져오기 오류: {e}")
            # 백업 복원
            self.memories = backup_memories
            self._rebuild_indexes()
            raise
