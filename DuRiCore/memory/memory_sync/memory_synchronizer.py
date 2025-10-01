#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-5: 메모리 동기화 모듈

메모리 동기화 및 백업/복원 기능을 제공하는 모듈입니다.
- 메모리 동기화
- 메모리 백업/복원
- 메모리 충돌 해결
- 메모리 일관성 검증
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import logging
import sqlite3
import threading
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SyncStatus(Enum):
    """동기화 상태"""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CONFLICT = "conflict"


class SyncType(Enum):
    """동기화 타입"""

    FULL = "full"
    INCREMENTAL = "incremental"
    SELECTIVE = "selective"
    BACKUP = "backup"
    RESTORE = "restore"


@dataclass
class SyncOperation:
    """동기화 작업"""

    sync_id: str
    sync_type: SyncType
    source_id: str
    target_id: str
    status: SyncStatus
    started_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    items_synced: int = 0
    items_failed: int = 0
    conflicts_resolved: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConflict:
    """메모리 충돌"""

    conflict_id: str
    memory_id: str
    source_version: Dict[str, Any]
    target_version: Dict[str, Any]
    conflict_type: str
    detected_at: datetime = field(default_factory=datetime.now)
    resolved: bool = False
    resolution_strategy: Optional[str] = None


class MemorySynchronizer:
    """메모리 동기화기"""

    def __init__(self, db_path: str = "memory_sync.db"):
        """초기화"""
        self.db_path = db_path
        self.lock = threading.Lock()
        self.sync_operations: Dict[str, SyncOperation] = {}
        self.memory_conflicts: Dict[str, MemoryConflict] = {}
        self.sync_queue = asyncio.Queue()

        # 동기화 설정
        self.sync_config = {
            "sync_interval": timedelta(minutes=5),
            "max_retries": 3,
            "conflict_resolution_timeout": timedelta(minutes=10),
            "backup_retention_days": 30,
            "max_sync_items": 1000,
        }

        # 성능 메트릭
        self.performance_metrics = {
            "total_sync_operations": 0,
            "successful_syncs": 0,
            "failed_syncs": 0,
            "conflicts_detected": 0,
            "conflicts_resolved": 0,
            "average_sync_time": 0.0,
        }

        # 데이터베이스 초기화
        self._init_database()

        logger.info("메모리 동기화기 초기화 완료")

    def _init_database(self):
        """데이터베이스 초기화"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # 동기화 작업 테이블
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS sync_operations (
                        sync_id TEXT PRIMARY KEY,
                        sync_type TEXT NOT NULL,
                        source_id TEXT NOT NULL,
                        target_id TEXT NOT NULL,
                        status TEXT NOT NULL,
                        started_at TEXT NOT NULL,
                        completed_at TEXT,
                        items_synced INTEGER DEFAULT 0,
                        items_failed INTEGER DEFAULT 0,
                        conflicts_resolved INTEGER DEFAULT 0,
                        metadata TEXT
                    )
                """
                )

                # 메모리 충돌 테이블
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS memory_conflicts (
                        conflict_id TEXT PRIMARY KEY,
                        memory_id TEXT NOT NULL,
                        source_version TEXT NOT NULL,
                        target_version TEXT NOT NULL,
                        conflict_type TEXT NOT NULL,
                        detected_at TEXT NOT NULL,
                        resolved INTEGER DEFAULT 0,
                        resolution_strategy TEXT
                    )
                """
                )

                # 인덱스 생성
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sync_status ON sync_operations(status)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_sync_type ON sync_operations(sync_type)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS idx_conflict_resolved ON memory_conflicts(resolved)"
                )

                conn.commit()
                logger.info("동기화 데이터베이스 초기화 완료")

        except Exception as e:
            logger.error(f"데이터베이스 초기화 실패: {e}")
            raise

    async def start_sync_operation(
        self,
        sync_type: SyncType,
        source_id: str,
        target_id: str,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """동기화 작업 시작"""
        try:
            sync_id = f"sync_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            sync_operation = SyncOperation(
                sync_id=sync_id,
                sync_type=sync_type,
                source_id=source_id,
                target_id=target_id,
                status=SyncStatus.PENDING,
                metadata=metadata or {},
            )

            self.sync_operations[sync_id] = sync_operation

            # 동기화 큐에 추가
            await self.sync_queue.put(sync_operation)

            logger.info(f"동기화 작업 시작: {sync_id} ({sync_type.value})")
            return sync_id

        except Exception as e:
            logger.error(f"동기화 작업 시작 실패: {e}")
            return ""

    async def perform_sync(self, sync_operation: SyncOperation) -> bool:
        """동기화 수행"""
        try:
            sync_operation.status = SyncStatus.IN_PROGRESS
            start_time = time.time()

            # 동기화 타입에 따른 처리
            if sync_operation.sync_type == SyncType.FULL:
                success = await self._perform_full_sync(sync_operation)
            elif sync_operation.sync_type == SyncType.INCREMENTAL:
                success = await self._perform_incremental_sync(sync_operation)
            elif sync_operation.sync_type == SyncType.SELECTIVE:
                success = await self._perform_selective_sync(sync_operation)
            elif sync_operation.sync_type == SyncType.BACKUP:
                success = await self._perform_backup_sync(sync_operation)
            elif sync_operation.sync_type == SyncType.RESTORE:
                success = await self._perform_restore_sync(sync_operation)
            else:
                logger.error(f"알 수 없는 동기화 타입: {sync_operation.sync_type}")
                success = False

            # 동기화 완료 처리
            sync_operation.completed_at = datetime.now()
            sync_operation.status = (
                SyncStatus.COMPLETED if success else SyncStatus.FAILED
            )

            # 성능 메트릭 업데이트
            self.performance_metrics["total_sync_operations"] += 1
            if success:
                self.performance_metrics["successful_syncs"] += 1
            else:
                self.performance_metrics["failed_syncs"] += 1

            sync_time = time.time() - start_time
            self.performance_metrics["average_sync_time"] = (
                self.performance_metrics["average_sync_time"]
                * (self.performance_metrics["total_sync_operations"] - 1)
                + sync_time
            ) / self.performance_metrics["total_sync_operations"]

            logger.info(
                f"동기화 완료: {sync_operation.sync_id} ({'성공' if success else '실패'})"
            )
            return success

        except Exception as e:
            logger.error(f"동기화 수행 실패: {e}")
            sync_operation.status = SyncStatus.FAILED
            sync_operation.completed_at = datetime.now()
            return False

    async def _perform_full_sync(self, sync_operation: SyncOperation) -> bool:
        """전체 동기화 수행"""
        try:
            # 소스에서 모든 메모리 데이터 가져오기
            source_memories = await self._get_memories_from_source(
                sync_operation.source_id
            )

            # 타겟에 동기화
            synced_count = 0
            failed_count = 0

            for memory_data in source_memories:
                try:
                    success = await self._sync_memory_to_target(
                        sync_operation.target_id, memory_data
                    )
                    if success:
                        synced_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"메모리 동기화 실패: {e}")
                    failed_count += 1

            sync_operation.items_synced = synced_count
            sync_operation.items_failed = failed_count

            return failed_count == 0

        except Exception as e:
            logger.error(f"전체 동기화 실패: {e}")
            return False

    async def _perform_incremental_sync(self, sync_operation: SyncOperation) -> bool:
        """증분 동기화 수행"""
        try:
            # 마지막 동기화 이후 변경된 데이터만 가져오기
            last_sync_time = await self._get_last_sync_time(
                sync_operation.source_id, sync_operation.target_id
            )

            # 변경된 메모리 데이터 가져오기
            changed_memories = await self._get_changed_memories(
                sync_operation.source_id, last_sync_time
            )

            # 타겟에 동기화
            synced_count = 0
            failed_count = 0

            for memory_data in changed_memories:
                try:
                    success = await self._sync_memory_to_target(
                        sync_operation.target_id, memory_data
                    )
                    if success:
                        synced_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"메모리 동기화 실패: {e}")
                    failed_count += 1

            sync_operation.items_synced = synced_count
            sync_operation.items_failed = failed_count

            return failed_count == 0

        except Exception as e:
            logger.error(f"증분 동기화 실패: {e}")
            return False

    async def _perform_selective_sync(self, sync_operation: SyncOperation) -> bool:
        """선택적 동기화 수행"""
        try:
            # 메타데이터에서 선택 조건 가져오기
            selection_criteria = sync_operation.metadata.get("selection_criteria", {})

            # 조건에 맞는 메모리 데이터 가져오기
            selected_memories = await self._get_selected_memories(
                sync_operation.source_id, selection_criteria
            )

            # 타겟에 동기화
            synced_count = 0
            failed_count = 0

            for memory_data in selected_memories:
                try:
                    success = await self._sync_memory_to_target(
                        sync_operation.target_id, memory_data
                    )
                    if success:
                        synced_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"메모리 동기화 실패: {e}")
                    failed_count += 1

            sync_operation.items_synced = synced_count
            sync_operation.items_failed = failed_count

            return failed_count == 0

        except Exception as e:
            logger.error(f"선택적 동기화 실패: {e}")
            return False

    async def _perform_backup_sync(self, sync_operation: SyncOperation) -> bool:
        """백업 동기화 수행"""
        try:
            # 백업 파일 경로 생성
            backup_path = f"backup_{int(time.time())}_{uuid.uuid4().hex[:8]}.json"

            # 소스에서 모든 메모리 데이터 가져오기
            source_memories = await self._get_memories_from_source(
                sync_operation.source_id
            )

            # 백업 파일에 저장
            backup_data = {
                "backup_id": sync_operation.sync_id,
                "created_at": datetime.now().isoformat(),
                "source_id": sync_operation.source_id,
                "memories": source_memories,
            }

            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(backup_data, f, ensure_ascii=False, indent=2)

            sync_operation.metadata["backup_path"] = backup_path
            sync_operation.items_synced = len(source_memories)

            logger.info(f"백업 완료: {backup_path} ({len(source_memories)}개 메모리)")
            return True

        except Exception as e:
            logger.error(f"백업 동기화 실패: {e}")
            return False

    async def _perform_restore_sync(self, sync_operation: SyncOperation) -> bool:
        """복원 동기화 수행"""
        try:
            # 백업 파일 경로 가져오기
            backup_path = sync_operation.metadata.get("backup_path")
            if not backup_path:
                logger.error("백업 파일 경로가 없습니다.")
                return False

            # 백업 파일에서 데이터 읽기
            with open(backup_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)

            # 타겟에 복원
            restored_count = 0
            failed_count = 0

            for memory_data in backup_data.get("memories", []):
                try:
                    success = await self._sync_memory_to_target(
                        sync_operation.target_id, memory_data
                    )
                    if success:
                        restored_count += 1
                    else:
                        failed_count += 1
                except Exception as e:
                    logger.error(f"메모리 복원 실패: {e}")
                    failed_count += 1

            sync_operation.items_synced = restored_count
            sync_operation.items_failed = failed_count

            logger.info(f"복원 완료: {restored_count}개 메모리 복원")
            return failed_count == 0

        except Exception as e:
            logger.error(f"복원 동기화 실패: {e}")
            return False

    async def detect_conflicts(
        self,
        memory_id: str,
        source_version: Dict[str, Any],
        target_version: Dict[str, Any],
    ) -> Optional[MemoryConflict]:
        """메모리 충돌 감지"""
        try:
            # 버전 비교
            if source_version.get("version") != target_version.get("version"):
                conflict_id = f"conflict_{int(time.time())}_{uuid.uuid4().hex[:8]}"

                conflict = MemoryConflict(
                    conflict_id=conflict_id,
                    memory_id=memory_id,
                    source_version=source_version,
                    target_version=target_version,
                    conflict_type="version_mismatch",
                )

                self.memory_conflicts[conflict_id] = conflict
                self.performance_metrics["conflicts_detected"] += 1

                logger.info(f"메모리 충돌 감지: {conflict_id} (메모리: {memory_id})")
                return conflict

            return None

        except Exception as e:
            logger.error(f"메모리 충돌 감지 실패: {e}")
            return None

    async def resolve_conflict(
        self, conflict_id: str, resolution_strategy: str
    ) -> bool:
        """메모리 충돌 해결"""
        try:
            if conflict_id not in self.memory_conflicts:
                logger.warning(f"충돌을 찾을 수 없음: {conflict_id}")
                return False

            conflict = self.memory_conflicts[conflict_id]

            # 충돌 해결 전략 적용
            if resolution_strategy == "source_wins":
                # 소스 버전 우선
                resolved_version = conflict.source_version
            elif resolution_strategy == "target_wins":
                # 타겟 버전 우선
                resolved_version = conflict.target_version
            elif resolution_strategy == "merge":
                # 병합
                resolved_version = await self._merge_versions(
                    conflict.source_version, conflict.target_version
                )
            else:
                logger.error(f"알 수 없는 해결 전략: {resolution_strategy}")
                return False

            # 해결된 버전 적용
            success = await self._apply_resolved_version(
                conflict.memory_id, resolved_version
            )

            if success:
                conflict.resolved = True
                conflict.resolution_strategy = resolution_strategy
                self.performance_metrics["conflicts_resolved"] += 1

                logger.info(
                    f"메모리 충돌 해결 완료: {conflict_id} ({resolution_strategy})"
                )
                return True
            else:
                logger.error(f"메모리 충돌 해결 실패: {conflict_id}")
                return False

        except Exception as e:
            logger.error(f"메모리 충돌 해결 실패: {e}")
            return False

    async def _get_memories_from_source(self, source_id: str) -> List[Dict[str, Any]]:
        """소스에서 메모리 데이터 가져오기"""
        # 실제 구현에서는 소스 시스템에서 데이터를 가져와야 함
        return []

    async def _sync_memory_to_target(
        self, target_id: str, memory_data: Dict[str, Any]
    ) -> bool:
        """타겟에 메모리 동기화"""
        # 실제 구현에서는 타겟 시스템에 데이터를 저장해야 함
        return True

    async def _get_last_sync_time(self, source_id: str, target_id: str) -> datetime:
        """마지막 동기화 시간 가져오기"""
        # 실제 구현에서는 데이터베이스에서 마지막 동기화 시간을 조회해야 함
        return datetime.now() - timedelta(hours=1)

    async def _get_changed_memories(
        self, source_id: str, since_time: datetime
    ) -> List[Dict[str, Any]]:
        """변경된 메모리 데이터 가져오기"""
        # 실제 구현에서는 소스 시스템에서 변경된 데이터를 가져와야 함
        return []

    async def _get_selected_memories(
        self, source_id: str, criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """선택된 메모리 데이터 가져오기"""
        # 실제 구현에서는 소스 시스템에서 조건에 맞는 데이터를 가져와야 함
        return []

    async def _merge_versions(
        self, source_version: Dict[str, Any], target_version: Dict[str, Any]
    ) -> Dict[str, Any]:
        """버전 병합"""
        # 실제 구현에서는 두 버전을 병합하는 로직이 필요함
        merged_version = source_version.copy()
        merged_version.update(target_version)
        merged_version["version"] = (
            max(source_version.get("version", 0), target_version.get("version", 0)) + 1
        )
        return merged_version

    async def _apply_resolved_version(
        self, memory_id: str, resolved_version: Dict[str, Any]
    ) -> bool:
        """해결된 버전 적용"""
        # 실제 구현에서는 해결된 버전을 메모리 시스템에 적용해야 함
        return True

    async def get_sync_status(self, sync_id: str) -> Optional[SyncOperation]:
        """동기화 상태 조회"""
        try:
            return self.sync_operations.get(sync_id)

        except Exception as e:
            logger.error(f"동기화 상태 조회 실패: {e}")
            return None

    async def get_sync_statistics(self) -> Dict[str, Any]:
        """동기화 통계 조회"""
        try:
            stats = {
                "total_operations": len(self.sync_operations),
                "pending_operations": len(
                    [
                        op
                        for op in self.sync_operations.values()
                        if op.status == SyncStatus.PENDING
                    ]
                ),
                "in_progress_operations": len(
                    [
                        op
                        for op in self.sync_operations.values()
                        if op.status == SyncStatus.IN_PROGRESS
                    ]
                ),
                "completed_operations": len(
                    [
                        op
                        for op in self.sync_operations.values()
                        if op.status == SyncStatus.COMPLETED
                    ]
                ),
                "failed_operations": len(
                    [
                        op
                        for op in self.sync_operations.values()
                        if op.status == SyncStatus.FAILED
                    ]
                ),
                "total_conflicts": len(self.memory_conflicts),
                "resolved_conflicts": len(
                    [c for c in self.memory_conflicts.values() if c.resolved]
                ),
                "performance_metrics": self.performance_metrics.copy(),
            }

            return stats

        except Exception as e:
            logger.error(f"동기화 통계 조회 실패: {e}")
            return {}
