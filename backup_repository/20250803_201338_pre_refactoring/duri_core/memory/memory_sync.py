"""
DuRi의 기억 동기화 시스템

이 모듈은 DuRi의 학습 경험을 저장하고 공유하는 시스템을 제공합니다.
Dream ↔ Reality 간 경험 통합과 강화학습 데이터 수집을 담당합니다.
"""

import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
import threading

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """기억 유형"""
    LEARNING_EXPERIENCE = "learning_experience"  # 학습 경험
    CREATIVITY_EXPERIENCE = "creativity_experience"  # 창의성 경험
    EVOLUTION_EXPERIENCE = "evolution_experience"  # 진화 경험
    DREAM_EXPERIENCE = "dream_experience"  # Dream 경험
    REALITY_EXPERIENCE = "reality_experience"  # Reality 경험


class ExperienceSource(Enum):
    """경험 출처"""
    DREAM = "dream"  # Dream 시스템
    REALITY = "reality"  # Reality 시스템
    HYBRID = "hybrid"  # 하이브리드 시스템
    EXTERNAL = "external"  # 외부 입력


@dataclass
class MemoryEntry:
    """기억 항목"""
    id: str
    type: MemoryType
    source: ExperienceSource
    content: Dict[str, Any]
    timestamp: datetime
    confidence: float  # 0.0 ~ 1.0
    tags: List[str]  # 검색용 태그들
    metadata: Dict[str, Any]  # 추가 메타데이터
    
    def get(self, key: str, default=None):
        """dict-like 인터페이스를 위한 get 메서드"""
        if isinstance(self.content, dict):
            return self.content.get(key, default)
        elif hasattr(self.content, 'get'):
            return self.content.get(key, default)
        else:
            # content가 dict가 아닌 경우, 전체 객체를 dict로 변환
            try:
                content_dict = asdict(self) if hasattr(self, '__dataclass_fields__') else vars(self)
                return content_dict.get(key, default)
            except:
                return default


class MemorySync:
    """
    DuRi의 기억 동기화 시스템
    
    학습 경험을 저장하고, Dream ↔ Reality 간 경험을 공유하며,
    강화학습 데이터를 수집합니다.
    """
    
    def __init__(self, db_path: str = "duri_memory.db"):
        """MemorySync 초기화"""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.memory_cache: Dict[str, MemoryEntry] = {}
        
        # 데이터베이스 초기화
        self._init_database()
        logger.info("MemorySync 시스템 초기화 완료")
    
    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 기억 테이블 생성
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS memories (
                        id TEXT PRIMARY KEY,
                        type TEXT NOT NULL,
                        source TEXT NOT NULL,
                        content TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        confidence REAL NOT NULL,
                        tags TEXT NOT NULL,
                        metadata TEXT NOT NULL
                    )
                ''')
                
                # 인덱스 생성
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_type ON memories(type)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON memories(source)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON memories(timestamp)')
                
                conn.commit()
                logger.info("메모리 데이터베이스 초기화 완료")
                
        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise
    
    def store_experience(self, memory_type: MemoryType, source: ExperienceSource,
                        content: Dict[str, Any], confidence: float = 0.5,
                        tags: List[str] = None, metadata: Dict[str, Any] = None) -> str:
        """
        경험을 저장
        
        Args:
            memory_type: 기억 유형
            source: 경험 출처
            content: 경험 내용
            confidence: 신뢰도
            tags: 태그들
            metadata: 메타데이터
            
        Returns:
            str: 저장된 기억의 ID
        """
        try:
            # enum 객체가 아닌 경우 처리
            memory_type_value = memory_type.value if hasattr(memory_type, 'value') else str(memory_type)
            source_value = source.value if hasattr(source, 'value') else str(source)
            
            memory_id = f"{memory_type_value}_{source_value}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
            
            # MemoryEntry 생성 시에도 enum 객체 처리
            memory_type_enum = memory_type if isinstance(memory_type, MemoryType) else MemoryType(memory_type_value)
            source_enum = source if isinstance(source, ExperienceSource) else ExperienceSource(source_value)
            
            memory_entry = MemoryEntry(
                id=memory_id,
                type=memory_type_enum,
                source=source_enum,
                content=content,
                timestamp=datetime.now(),
                confidence=confidence,
                tags=tags or [],
                metadata=metadata or {}
            )
            
            # 데이터베이스에 저장
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        INSERT INTO memories (id, type, source, content, timestamp, confidence, tags, metadata)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        memory_id,
                        memory_type_value,
                        source_value,
                        json.dumps(content, ensure_ascii=False),
                        memory_entry.timestamp.isoformat(),
                        confidence,
                        json.dumps(tags or [], ensure_ascii=False),
                        json.dumps(metadata or {}, ensure_ascii=False)
                    ))
                    conn.commit()
                
                # 캐시에 저장
                self.memory_cache[memory_id] = memory_entry
            
            logger.info(f"경험 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"경험 저장 실패: {e}")
            raise
    
    def retrieve_experiences(self, memory_type: MemoryType = None, 
                           source: ExperienceSource = None,
                           tags: List[str] = None,
                           limit: int = 100) -> List[MemoryEntry]:
        """
        경험을 조회
        
        Args:
            memory_type: 기억 유형 필터
            source: 경험 출처 필터
            tags: 태그 필터
            limit: 조회 제한 수
            
        Returns:
            List[MemoryEntry]: 조회된 기억들
        """
        try:
            query = "SELECT * FROM memories WHERE 1=1"
            params = []
            
            if memory_type:
                query += " AND type = ?"
                params.append(memory_type.value)
            
            if source:
                query += " AND source = ?"
                params.append(source.value)
            
            if tags:
                # 태그 검색 (JSON 배열에서 포함 여부 확인)
                tag_conditions = []
                for tag in tags:
                    tag_conditions.append("tags LIKE ?")
                    params.append(f'%"{tag}"%')
                query += f" AND ({' OR '.join(tag_conditions)})"
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
            
            memories = []
            for row in rows:
                memory_entry = MemoryEntry(
                    id=row[0],
                    type=MemoryType(row[1]),
                    source=ExperienceSource(row[2]),
                    content=json.loads(row[3]),
                    timestamp=datetime.fromisoformat(row[4]),
                    confidence=row[5],
                    tags=json.loads(row[6]),
                    metadata=json.loads(row[7])
                )
                memories.append(memory_entry)
            
            return memories
            
        except Exception as e:
            logger.error(f"경험 조회 실패: {e}")
            return []
    
    def sync_dream_reality_experiences(self) -> Dict[str, Any]:
        """
        Dream ↔ Reality 경험 동기화
        
        Returns:
            Dict[str, Any]: 동기화 결과
        """
        try:
            # Dream 경험 조회
            dream_experiences = self.retrieve_experiences(
                source=ExperienceSource.DREAM,
                limit=50
            )
            
            # Reality 경험 조회
            reality_experiences = self.retrieve_experiences(
                source=ExperienceSource.REALITY,
                limit=50
            )
            
            # 경험 비교 및 통합
            sync_results = {
                "dream_count": len(dream_experiences),
                "reality_count": len(reality_experiences),
                "shared_patterns": [],
                "conflicts": [],
                "synergies": []
            }
            
            # 공통 패턴 찾기
            dream_tags = set()
            for exp in dream_experiences:
                dream_tags.update(exp.tags)
            
            reality_tags = set()
            for exp in reality_experiences:
                reality_tags.update(exp.tags)
            
            shared_tags = dream_tags.intersection(reality_tags)
            sync_results["shared_patterns"] = list(shared_tags)
            
            # 성능 비교
            dream_performance = self._calculate_average_performance(dream_experiences)
            reality_performance = self._calculate_average_performance(reality_experiences)
            
            if dream_performance > reality_performance:
                sync_results["synergies"].append({
                    "type": "dream_superior",
                    "dream_performance": dream_performance,
                    "reality_performance": reality_performance
                })
            elif reality_performance > dream_performance:
                sync_results["synergies"].append({
                    "type": "reality_superior",
                    "dream_performance": dream_performance,
                    "reality_performance": reality_performance
                })
            
            logger.info(f"Dream ↔ Reality 동기화 완료: {len(shared_tags)}개 공통 패턴")
            return sync_results
            
        except Exception as e:
            logger.error(f"Dream ↔ Reality 동기화 실패: {e}")
            return {"error": str(e)}
    
    def collect_rl_data(self, memory_type: MemoryType = None) -> Dict[str, Any]:
        """
        강화학습 데이터 수집
        
        Args:
            memory_type: 특정 기억 유형만 수집
            
        Returns:
            Dict[str, Any]: 강화학습 데이터
        """
        try:
            # 최근 경험들 조회
            experiences = self.retrieve_experiences(
                memory_type=memory_type,
                limit=1000
            )
            
            rl_data = {
                "states": [],
                "actions": [],
                "rewards": [],
                "next_states": [],
                "dones": []
            }
            
            for exp in experiences:
                content = exp.content
                
                # 상태 추출
                if "state" in content:
                    rl_data["states"].append(content["state"])
                
                # 행동 추출
                if "action" in content:
                    rl_data["actions"].append(content["action"])
                
                # 보상 추출
                if "reward" in content:
                    rl_data["rewards"].append(content["reward"])
                
                # 다음 상태 추출
                if "next_state" in content:
                    rl_data["next_states"].append(content["next_state"])
                
                # 종료 여부 추출
                if "done" in content:
                    rl_data["dones"].append(content["done"])
            
            # 통계 정보 추가
            rl_data["statistics"] = {
                "total_experiences": len(experiences),
                "avg_confidence": sum(exp.confidence for exp in experiences) / len(experiences) if experiences else 0,
                "memory_types": {exp.type.value: len([e for e in experiences if e.type == exp.type]) for exp in experiences},
                "sources": {exp.source.value: len([e for e in experiences if e.source == exp.source]) for exp in experiences}
            }
            
            logger.info(f"강화학습 데이터 수집 완료: {len(experiences)}개 경험")
            return rl_data
            
        except Exception as e:
            logger.error(f"강화학습 데이터 수집 실패: {e}")
            return {"error": str(e)}
    
    def _calculate_average_performance(self, experiences: List[MemoryEntry]) -> float:
        """평균 성능 계산"""
        if not experiences:
            return 0.0
        
        total_performance = 0.0
        count = 0
        
        for exp in experiences:
            if "performance" in exp.content:
                total_performance += exp.content["performance"]
                count += 1
        
        return total_performance / count if count > 0 else 0.0
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """기억 시스템 요약 정보"""
        try:
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 총 기억 수
                    cursor.execute("SELECT COUNT(*) FROM memories")
                    total_memories = cursor.fetchone()[0]
                    
                    # 유형별 기억 수
                    cursor.execute("SELECT type, COUNT(*) FROM memories GROUP BY type")
                    memories_by_type = dict(cursor.fetchall())
                    
                    # 출처별 기억 수
                    cursor.execute("SELECT source, COUNT(*) FROM memories GROUP BY source")
                    memories_by_source = dict(cursor.fetchall())
                    
                    # 평균 신뢰도
                    cursor.execute("SELECT AVG(confidence) FROM memories")
                    avg_confidence = cursor.fetchone()[0] or 0.0
                    
                    # 최근 기억 시간
                    cursor.execute("SELECT MAX(timestamp) FROM memories")
                    last_memory_time = cursor.fetchone()[0]
            
            return {
                "total_memories": total_memories,
                "memories_by_type": memories_by_type,
                "memories_by_source": memories_by_source,
                "average_confidence": avg_confidence,
                "last_memory_time": last_memory_time
            }
            
        except Exception as e:
            logger.error(f"기억 요약 조회 실패: {e}")
            return {"error": str(e)}
    
    def clear_old_memories(self, days: int = 30) -> int:
        """
        오래된 기억 삭제
        
        Args:
            days: 삭제할 기억의 일수
            
        Returns:
            int: 삭제된 기억 수
        """
        try:
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            with self.lock:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM memories WHERE timestamp < ?", (cutoff_date.isoformat(),))
                    deleted_count = cursor.rowcount
                    conn.commit()
            
            logger.info(f"오래된 기억 삭제 완료: {deleted_count}개")
            return deleted_count
            
        except Exception as e:
            logger.error(f"오래된 기억 삭제 실패: {e}")
            return 0


# 싱글톤 인스턴스
_memory_sync_instance = None

def get_memory_sync() -> MemorySync:
    """MemorySync 싱글톤 인스턴스 반환"""
    global _memory_sync_instance
    if _memory_sync_instance is None:
        _memory_sync_instance = MemorySync()
    return _memory_sync_instance 