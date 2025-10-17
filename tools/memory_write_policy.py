#!/usr/bin/env python3
"""
메모리 "쓰기 정책"의 뼈대
- 지금부터 로그가 쌓이니 "무엇을 저장/버릴지" 기준이 필요
- episodic(세션) vs semantic(지식) 분리 + 주기적 압축 잡
"""

import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, asdict

class MemoryType(Enum):
    EPISODIC = "episodic"  # 세션/대화 로그
    SEMANTIC = "semantic"  # 지식/팩트
    PROCEDURAL = "procedural"  # 절차/스킬
    EMOTIONAL = "emotional"  # 감정/경험

class MemoryPriority(Enum):
    CRITICAL = "critical"  # 필수 보존
    HIGH = "high"  # 중요
    MEDIUM = "medium"  # 일반
    LOW = "low"  # 임시
    TRASH = "trash"  # 삭제 대상

@dataclass
class MemoryEntry:
    id: str
    content: str
    memory_type: MemoryType
    priority: MemoryPriority
    created_at: datetime
    last_accessed: datetime
    access_count: int
    importance_score: float
    tags: List[str]
    metadata: Dict[str, Any]
    compressed: bool = False
    retention_days: int = 30

@dataclass
class CompressionRule:
    memory_type: MemoryType
    age_days: int
    access_threshold: int
    importance_threshold: float
    compression_ratio: float

class MemoryWritePolicy:
    """메모리 쓰기 정책"""
    
    def __init__(self):
        self.memory_entries: Dict[str, MemoryEntry] = {}
        self.compression_rules: List[CompressionRule] = []
        self.retention_policies: Dict[MemoryType, int] = {
            MemoryType.EPISODIC: 7,  # 7일
            MemoryType.SEMANTIC: 365,  # 1년
            MemoryType.PROCEDURAL: 180,  # 6개월
            MemoryType.EMOTIONAL: 30  # 30일
        }
        
        # 압축 규칙 설정
        self._setup_compression_rules()
        
        # 중요도 계산 가중치
        self.importance_weights = {
            "access_frequency": 0.3,
            "recency": 0.2,
            "content_length": 0.1,
            "user_feedback": 0.2,
            "system_usage": 0.2
        }
    
    def _setup_compression_rules(self):
        """압축 규칙 설정"""
        self.compression_rules = [
            CompressionRule(
                memory_type=MemoryType.EPISODIC,
                age_days=3,
                access_threshold=5,
                importance_threshold=0.5,
                compression_ratio=0.3
            ),
            CompressionRule(
                memory_type=MemoryType.SEMANTIC,
                age_days=30,
                access_threshold=10,
                importance_threshold=0.7,
                compression_ratio=0.5
            ),
            CompressionRule(
                memory_type=MemoryType.PROCEDURAL,
                age_days=14,
                access_threshold=3,
                importance_threshold=0.6,
                compression_ratio=0.4
            ),
            CompressionRule(
                memory_type=MemoryType.EMOTIONAL,
                age_days=7,
                access_threshold=2,
                importance_threshold=0.4,
                compression_ratio=0.2
            )
        ]
    
    def should_store(self, content: str, memory_type: MemoryType, context: Dict[str, Any]) -> Tuple[bool, MemoryPriority]:
        """저장 여부 결정"""
        # 1. 내용 품질 검사
        if not self._is_content_quality_good(content):
            return False, MemoryPriority.TRASH
        
        # 2. 중복성 검사
        if self._is_duplicate_content(content):
            return False, MemoryPriority.TRASH
        
        # 3. 중요도 계산
        importance_score = self._calculate_importance(content, memory_type, context)
        
        # 4. 우선순위 결정
        priority = self._determine_priority(importance_score, memory_type)
        
        # 5. 저장 여부 결정
        should_store = priority != MemoryPriority.TRASH
        
        return should_store, priority
    
    def _is_content_quality_good(self, content: str) -> bool:
        """내용 품질 검사"""
        # 최소 길이
        if len(content.strip()) < 10:
            return False
        
        # 의미 있는 내용 (단순 반복 제외)
        words = content.split()
        if len(set(words)) < len(words) * 0.3:  # 30% 이상 중복
            return False
        
        # 금지된 패턴
        forbidden_patterns = [
            "error", "exception", "traceback",
            "undefined", "null", "none"
        ]
        
        content_lower = content.lower()
        for pattern in forbidden_patterns:
            if pattern in content_lower:
                return False
        
        return True
    
    def _is_duplicate_content(self, content: str) -> bool:
        """중복 내용 검사"""
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        for entry in self.memory_entries.values():
            entry_hash = hashlib.md5(entry.content.encode()).hexdigest()
            if content_hash == entry_hash:
                return True
        
        return False
    
    def _calculate_importance(self, content: str, memory_type: MemoryType, context: Dict[str, Any]) -> float:
        """중요도 계산"""
        score = 0.0
        
        # 1. 접근 빈도 (시뮬레이션)
        access_frequency = context.get("access_frequency", 1)
        score += min(1.0, access_frequency / 10) * self.importance_weights["access_frequency"]
        
        # 2. 최근성
        recency = context.get("recency", 1.0)
        score += recency * self.importance_weights["recency"]
        
        # 3. 내용 길이
        content_length = min(1.0, len(content) / 1000)
        score += content_length * self.importance_weights["content_length"]
        
        # 4. 사용자 피드백
        user_feedback = context.get("user_feedback", 0.5)
        score += user_feedback * self.importance_weights["user_feedback"]
        
        # 5. 시스템 사용
        system_usage = context.get("system_usage", 0.5)
        score += system_usage * self.importance_weights["system_usage"]
        
        return min(1.0, score)
    
    def _determine_priority(self, importance_score: float, memory_type: MemoryType) -> MemoryPriority:
        """우선순위 결정"""
        if importance_score >= 0.9:
            return MemoryPriority.CRITICAL
        elif importance_score >= 0.7:
            return MemoryPriority.HIGH
        elif importance_score >= 0.5:
            return MemoryPriority.MEDIUM
        elif importance_score >= 0.3:
            return MemoryPriority.LOW
        else:
            return MemoryPriority.TRASH
    
    def store_memory(self, content: str, memory_type: MemoryType, context: Dict[str, Any]) -> Optional[str]:
        """메모리 저장"""
        should_store, priority = self.should_store(content, memory_type, context)
        
        if not should_store:
            return None
        
        # 메모리 엔트리 생성
        memory_id = self._generate_memory_id(content, memory_type)
        importance_score = self._calculate_importance(content, memory_type, context)
        
        entry = MemoryEntry(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            priority=priority,
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            importance_score=importance_score,
            tags=context.get("tags", []),
            metadata=context.get("metadata", {}),
            retention_days=self.retention_policies[memory_type]
        )
        
        self.memory_entries[memory_id] = entry
        return memory_id
    
    def _generate_memory_id(self, content: str, memory_type: MemoryType) -> str:
        """메모리 ID 생성"""
        timestamp = int(time.time())
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        return f"{memory_type.value}_{timestamp}_{content_hash}"
    
    def compress_memories(self) -> Dict[str, Any]:
        """메모리 압축"""
        compressed_count = 0
        deleted_count = 0
        
        for rule in self.compression_rules:
            entries_to_compress = []
            entries_to_delete = []
            
            for entry in self.memory_entries.values():
                if entry.memory_type != rule.memory_type:
                    continue
                
                age_days = (datetime.now() - entry.created_at).days
                
                # 압축 조건 확인
                if (age_days >= rule.age_days and 
                    entry.access_count >= rule.access_threshold and
                    entry.importance_score >= rule.importance_threshold and
                    not entry.compressed):
                    entries_to_compress.append(entry)
                
                # 삭제 조건 확인
                elif (age_days >= entry.retention_days and
                      entry.priority == MemoryPriority.LOW):
                    entries_to_delete.append(entry)
            
            # 압축 실행
            for entry in entries_to_compress:
                self._compress_entry(entry, rule.compression_ratio)
                compressed_count += 1
            
            # 삭제 실행
            for entry in entries_to_delete:
                del self.memory_entries[entry.id]
                deleted_count += 1
        
        return {
            "compressed_count": compressed_count,
            "deleted_count": deleted_count,
            "total_memories": len(self.memory_entries)
        }
    
    def _compress_entry(self, entry: MemoryEntry, compression_ratio: float):
        """메모리 엔트리 압축"""
        # 간단한 압축: 중요 키워드만 추출
        words = entry.content.split()
        important_words = [word for word in words if len(word) > 3][:int(len(words) * compression_ratio)]
        
        entry.content = " ".join(important_words)
        entry.compressed = True
        entry.metadata["compression_ratio"] = compression_ratio
        entry.metadata["compressed_at"] = datetime.now().isoformat()
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """메모리 통계"""
        stats = {
            "total_memories": len(self.memory_entries),
            "by_type": {},
            "by_priority": {},
            "compressed_count": 0,
            "avg_importance": 0.0
        }
        
        total_importance = 0.0
        
        for entry in self.memory_entries.values():
            # 타입별 통계
            type_key = entry.memory_type.value
            stats["by_type"][type_key] = stats["by_type"].get(type_key, 0) + 1
            
            # 우선순위별 통계
            priority_key = entry.priority.value
            stats["by_priority"][priority_key] = stats["by_priority"].get(priority_key, 0) + 1
            
            # 압축 통계
            if entry.compressed:
                stats["compressed_count"] += 1
            
            # 중요도 평균
            total_importance += entry.importance_score
        
        if self.memory_entries:
            stats["avg_importance"] = total_importance / len(self.memory_entries)
        
        return stats
    
    def cleanup_expired_memories(self) -> int:
        """만료된 메모리 정리"""
        now = datetime.now()
        expired_entries = []
        
        for entry in self.memory_entries.values():
            if (now - entry.created_at).days >= entry.retention_days:
                expired_entries.append(entry)
        
        for entry in expired_entries:
            del self.memory_entries[entry.id]
        
        return len(expired_entries)

# 전역 인스턴스
memory_write_policy = MemoryWritePolicy()
