"""
DuRi Memory System - Advanced Memory Management Service
고급 메모리 관리 시스템
"""
import logging
import json
import gzip
import pickle
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from collections import defaultdict

from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)

class MemoryLifecycleStage(Enum):
    """메모리 생명주기 단계"""
    CREATED = "created"
    EVOLVING = "evolving"
    STABLE = "stable"
    ARCHIVED = "archived"
    DELETED = "deleted"

class MemoryPriority(Enum):
    """메모리 우선순위"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"

@dataclass
class MemoryLifecycle:
    """메모리 생명주기 정보"""
    memory_id: int
    current_stage: MemoryLifecycleStage
    stage_history: List[Dict[str, Any]]
    priority: MemoryPriority
    evolution_score: float
    last_accessed: datetime
    access_count: int
    compression_ratio: float = 1.0
    backup_status: str = "none"

class AdvancedMemoryService:
    """고급 메모리 관리 서비스"""
    
    def __init__(self):
        self.lifecycle_cache: Dict[int, MemoryLifecycle] = {}
        self.performance_metrics: Dict[str, Any] = {}
        self._load_lifecycle_cache()
    
    def _load_lifecycle_cache(self):
        """생명주기 캐시 로드"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            memories = memory_service.query_memories(limit=1000)
            for memory in memories:
                lifecycle = self._create_lifecycle_from_memory(memory)
                self.lifecycle_cache[memory.id] = lifecycle
                
        except Exception as e:
            logger.error(f"생명주기 캐시 로드 실패: {e}")
    
    def _create_lifecycle_from_memory(self, memory) -> MemoryLifecycle:
        """메모리로부터 생명주기 객체 생성"""
        # 우선순위 결정
        priority = self._determine_priority(memory.importance_score)
        
        # 생명주기 단계 결정
        stage = self._determine_lifecycle_stage(memory)
        
        # 진화 점수 계산
        evolution_score = self._calculate_evolution_score(memory)
        
        return MemoryLifecycle(
            memory_id=memory.id,
            current_stage=stage,
            stage_history=[],
            priority=priority,
            evolution_score=evolution_score,
            last_accessed=memory.updated_at or memory.created_at,
            access_count=memory.promotion_count or 0
        )
    
    def _determine_priority(self, importance_score: float) -> MemoryPriority:
        """중요도 점수로 우선순위 결정"""
        if importance_score >= 90:
            return MemoryPriority.CRITICAL
        elif importance_score >= 70:
            return MemoryPriority.HIGH
        elif importance_score >= 50:
            return MemoryPriority.MEDIUM
        elif importance_score >= 30:
            return MemoryPriority.LOW
        else:
            return MemoryPriority.MINIMAL
    
    def _determine_lifecycle_stage(self, memory) -> MemoryLifecycleStage:
        """메모리 생명주기 단계 결정"""
        age_hours = (datetime.now() - memory.created_at.replace(tzinfo=None)).total_seconds() / 3600
        
        if age_hours < 1:
            return MemoryLifecycleStage.CREATED
        elif age_hours < 24:
            return MemoryLifecycleStage.EVOLVING
        elif age_hours < 168:  # 7일
            return MemoryLifecycleStage.STABLE
        else:
            return MemoryLifecycleStage.ARCHIVED
    
    def _calculate_evolution_score(self, memory) -> float:
        """진화 점수 계산"""
        base_score = memory.importance_score / 100.0
        age_factor = min(1.0, (datetime.now() - memory.created_at.replace(tzinfo=None)).total_seconds() / 86400)
        access_factor = min(1.0, (memory.promotion_count or 0) / 10.0)
        
        return (base_score * 0.5 + age_factor * 0.3 + access_factor * 0.2)
    
    def manage_memory_lifecycle(self, memory_id: int) -> Dict[str, Any]:
        """메모리 생명주기 관리"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            memory = memory_service.get_memory_by_id(memory_id)
            if not memory:
                return {"error": "Memory not found"}
            
            lifecycle = self.lifecycle_cache.get(memory_id)
            if not lifecycle:
                lifecycle = self._create_lifecycle_from_memory(memory)
                self.lifecycle_cache[memory_id] = lifecycle
            
            # 생명주기 업데이트
            old_stage = lifecycle.current_stage
            new_stage = self._determine_lifecycle_stage(memory)
            
            if old_stage != new_stage:
                lifecycle.stage_history.append({
                    "stage": old_stage.value,
                    "timestamp": datetime.now().isoformat(),
                    "reason": "automatic_transition"
                })
                lifecycle.current_stage = new_stage
                
                log_important_event(
                    f"메모리 생명주기 전환: {memory_id}",
                    f"{old_stage.value} → {new_stage.value}",
                    importance_score=60
                )
            
            # 우선순위 업데이트
            new_priority = self._determine_priority(memory.importance_score)
            if lifecycle.priority != new_priority:
                lifecycle.priority = new_priority
                
                log_important_event(
                    f"메모리 우선순위 변경: {memory_id}",
                    f"{lifecycle.priority.value} → {new_priority.value}",
                    importance_score=50
                )
            
            # 진화 점수 업데이트
            lifecycle.evolution_score = self._calculate_evolution_score(memory)
            lifecycle.last_accessed = memory.updated_at or memory.created_at
            lifecycle.access_count = memory.promotion_count or 0
            
            return {
                "memory_id": memory_id,
                "current_stage": lifecycle.current_stage.value,
                "priority": lifecycle.priority.value,
                "evolution_score": lifecycle.evolution_score,
                "stage_transition": old_stage != new_stage,
                "priority_changed": lifecycle.priority != new_priority
            }
            
        except Exception as e:
            logger.error(f"생명주기 관리 실패: {e}")
            return {"error": str(e)}
    
    def optimize_memory_storage(self, memory_id: int) -> Dict[str, Any]:
        """메모리 저장 최적화"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            memory = memory_service.get_memory_by_id(memory_id)
            if not memory:
                return {"error": "Memory not found"}
            
            # 압축 전 크기
            original_size = len(json.dumps(memory.raw_data or {}))
            
            # 압축 적용
            compressed_data = self._compress_memory_data(memory.raw_data or {})
            compressed_size = len(compressed_data)
            
            # 압축률 계산
            compression_ratio = compressed_size / original_size if original_size > 0 else 1.0
            
            lifecycle = self.lifecycle_cache.get(memory_id)
            if lifecycle:
                lifecycle.compression_ratio = compression_ratio
            
            # 압축된 데이터로 업데이트
            memory.raw_data = compressed_data
            db.commit()
            
            log_system_event(
                f"메모리 압축 완료: {memory_id}",
                f"압축률: {compression_ratio:.2f}",
                importance_score=40
            )
            
            return {
                "memory_id": memory_id,
                "original_size": original_size,
                "compressed_size": compressed_size,
                "compression_ratio": compression_ratio,
                "space_saved": original_size - compressed_size
            }
            
        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return {"error": str(e)}
    
    def _compress_memory_data(self, data: Dict[str, Any]) -> str:
        """메모리 데이터 압축"""
        try:
            # JSON 직렬화
            json_data = json.dumps(data, ensure_ascii=False)
            
            # gzip 압축
            compressed = gzip.compress(json_data.encode('utf-8'))
            
            # base64 인코딩
            import base64
            encoded = base64.b64encode(compressed).decode('utf-8')
            
            return encoded
            
        except Exception as e:
            logger.error(f"데이터 압축 실패: {e}")
            return json.dumps(data, ensure_ascii=False)
    
    def backup_memory_system(self) -> Dict[str, Any]:
        """메모리 시스템 백업"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            # 모든 메모리 조회
            memories = memory_service.query_memories(limit=10000)
            
            # 백업 데이터 구성
            backup_data = {
                "backup_timestamp": datetime.now().isoformat(),
                "total_memories": len(memories),
                "lifecycle_data": {},
                "performance_metrics": self.performance_metrics,
                "memories": []
            }
            
            # 메모리 데이터 수집
            for memory in memories:
                memory_data = {
                    "id": memory.id,
                    "type": memory.type,
                    "context": memory.context,
                    "content": memory.content,
                    "raw_data": memory.raw_data,
                    "source": memory.source,
                    "tags": memory.tags,
                    "importance_score": memory.importance_score,
                    "memory_level": memory.memory_level,
                    "expires_at": memory.expires_at.isoformat() if memory.expires_at else None,
                    "promotion_count": memory.promotion_count,
                    "created_at": memory.created_at.isoformat(),
                    "updated_at": memory.updated_at.isoformat()
                }
                backup_data["memories"].append(memory_data)
                
                # 생명주기 데이터 추가
                lifecycle = self.lifecycle_cache.get(memory.id)
                if lifecycle:
                    backup_data["lifecycle_data"][memory.id] = {
                        "current_stage": lifecycle.current_stage.value,
                        "priority": lifecycle.priority.value,
                        "evolution_score": lifecycle.evolution_score,
                        "last_accessed": lifecycle.last_accessed.isoformat(),
                        "access_count": lifecycle.access_count,
                        "compression_ratio": lifecycle.compression_ratio,
                        "backup_status": lifecycle.backup_status
                    }
            
            # 백업 파일 저장
            backup_filename = f"memory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = f"/app/backups/{backup_filename}"
            
            import os
            os.makedirs("/app/backups", exist_ok=True)
            
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)
            
            log_important_event(
                "메모리 시스템 백업 완료",
                f"백업 파일: {backup_filename}, 메모리 수: {len(memories)}",
                importance_score=80
            )
            
            return {
                "backup_filename": backup_filename,
                "total_memories": len(memories),
                "backup_size": os.path.getsize(backup_path),
                "lifecycle_entries": len(backup_data["lifecycle_data"])
            }
            
        except Exception as e:
            logger.error(f"백업 실패: {e}")
            return {"error": str(e)}
    
    def monitor_performance(self) -> Dict[str, Any]:
        """성능 모니터링"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            # 기본 통계
            stats = memory_service.get_memory_stats()
            
            # 생명주기 통계
            lifecycle_stats = self._calculate_lifecycle_stats()
            
            # 성능 메트릭 계산
            performance_metrics = {
                "total_memories": stats.get("total_memories", 0),
                "memory_distribution": stats.get("memory_levels", {}),
                "lifecycle_distribution": lifecycle_stats,
                "average_importance": self._calculate_average_importance(),
                "compression_efficiency": self._calculate_compression_efficiency(),
                "access_patterns": self._analyze_access_patterns(),
                "system_health": self._assess_system_health()
            }
            
            self.performance_metrics = performance_metrics
            
            return performance_metrics
            
        except Exception as e:
            logger.error(f"성능 모니터링 실패: {e}")
            return {"error": str(e)}
    
    def _calculate_lifecycle_stats(self) -> Dict[str, int]:
        """생명주기 통계 계산"""
        stats = defaultdict(int)
        for lifecycle in self.lifecycle_cache.values():
            stats[lifecycle.current_stage.value] += 1
            stats[f"priority_{lifecycle.priority.value}"] += 1
        return dict(stats)
    
    def _calculate_average_importance(self) -> float:
        """평균 중요도 계산"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            memories = memory_service.query_memories(limit=1000)
            if not memories:
                return 0.0
            
            total_importance = sum(m.importance_score for m in memories)
            return total_importance / len(memories)
            
        except Exception as e:
            logger.error(f"평균 중요도 계산 실패: {e}")
            return 0.0
    
    def _calculate_compression_efficiency(self) -> Dict[str, float]:
        """압축 효율성 계산"""
        compression_ratios = [lc.compression_ratio for lc in self.lifecycle_cache.values()]
        
        if not compression_ratios:
            return {"average_ratio": 1.0, "space_saved_percent": 0.0}
        
        avg_ratio = sum(compression_ratios) / len(compression_ratios)
        space_saved = (1.0 - avg_ratio) * 100
        
        return {
            "average_ratio": avg_ratio,
            "space_saved_percent": space_saved
        }
    
    def _analyze_access_patterns(self) -> Dict[str, Any]:
        """접근 패턴 분석"""
        access_counts = [lc.access_count for lc in self.lifecycle_cache.values()]
        
        if not access_counts:
            return {"average_access": 0, "high_access_count": 0}
        
        avg_access = sum(access_counts) / len(access_counts)
        high_access = sum(1 for count in access_counts if count > 5)
        
        return {
            "average_access": avg_access,
            "high_access_count": high_access,
            "total_access": sum(access_counts)
        }
    
    def _assess_system_health(self) -> Dict[str, Any]:
        """시스템 건강도 평가"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            total_memories = len(memory_service.query_memories(limit=10000))
            lifecycle_count = len(self.lifecycle_cache)
            
            health_score = min(100, (lifecycle_count / max(total_memories, 1)) * 100)
            
            return {
                "health_score": health_score,
                "cache_coverage": lifecycle_count / max(total_memories, 1),
                "system_status": "healthy" if health_score > 80 else "warning"
            }
            
        except Exception as e:
            logger.error(f"시스템 건강도 평가 실패: {e}")
            return {"health_score": 0, "system_status": "error"}

# 전역 인스턴스
advanced_memory_service = AdvancedMemoryService() 