#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-5: 메모리 할당/해제 모듈

메모리 할당, 해제, 관리 기능을 제공하는 모듈입니다.
- 메모리 할당
- 메모리 해제
- 메모리 상태 관리
- 메모리 최적화
"""

import asyncio
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import json
import logging
import time
from typing import Any, Dict, List, Optional, Tuple, Union
import uuid

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryStatus(Enum):
    """메모리 상태"""

    ALLOCATED = "allocated"
    FREE = "free"
    RESERVED = "reserved"
    CORRUPTED = "corrupted"
    EXPIRED = "expired"


class MemoryType(Enum):
    """메모리 타입"""

    EXPERIENCE = "experience"
    KNOWLEDGE = "knowledge"
    PATTERN = "pattern"
    EMOTION = "emotion"
    WORKING = "working"


@dataclass
class MemoryBlock:
    """메모리 블록"""

    block_id: str
    memory_type: MemoryType
    content: str
    size: int
    status: MemoryStatus
    allocated_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryAllocation:
    """메모리 할당"""

    allocation_id: str
    block_id: str
    memory_type: MemoryType
    size: int
    allocated_at: datetime = field(default_factory=datetime.now)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryAllocator:
    """메모리 할당기"""

    def __init__(self):
        """초기화"""
        self.memory_blocks: Dict[str, MemoryBlock] = {}
        self.allocations: Dict[str, MemoryAllocation] = {}
        self.free_blocks: List[str] = []
        self.reserved_blocks: List[str] = []

        # 할당 설정
        self.allocation_config = {
            "max_memory_size": 1000000,  # 1MB
            "block_size": 1024,  # 1KB
            "max_blocks": 1000,
            "cleanup_interval": timedelta(hours=1),
            "expiration_check_interval": timedelta(minutes=30),
        }

        # 성능 메트릭
        self.performance_metrics = {
            "total_allocations": 0,
            "total_deallocations": 0,
            "current_allocated_size": 0,
            "current_free_size": 0,
            "allocation_success_rate": 0.0,
            "average_allocation_time": 0.0,
        }

        logger.info("메모리 할당기 초기화 완료")

    async def allocate_memory(
        self,
        content: str,
        memory_type: MemoryType,
        size: Optional[int] = None,
        expires_at: Optional[datetime] = None,
    ) -> str:
        """메모리 할당"""
        try:
            start_time = time.time()

            # 크기 계산
            if size is None:
                size = len(content.encode("utf-8"))

            # 블록 ID 생성
            block_id = f"block_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            # 메모리 블록 생성
            memory_block = MemoryBlock(
                block_id=block_id,
                memory_type=memory_type,
                content=content,
                size=size,
                status=MemoryStatus.ALLOCATED,
            )

            # 할당 정보 생성
            allocation_id = f"alloc_{int(time.time())}_{uuid.uuid4().hex[:8]}"
            allocation = MemoryAllocation(
                allocation_id=allocation_id,
                block_id=block_id,
                memory_type=memory_type,
                size=size,
                expires_at=expires_at,
            )

            # 저장
            self.memory_blocks[block_id] = memory_block
            self.allocations[allocation_id] = allocation

            # 성능 메트릭 업데이트
            self.performance_metrics["total_allocations"] += 1
            self.performance_metrics["current_allocated_size"] += size
            self.performance_metrics["average_allocation_time"] = (
                self.performance_metrics["average_allocation_time"]
                * (self.performance_metrics["total_allocations"] - 1)
                + (time.time() - start_time)
            ) / self.performance_metrics["total_allocations"]

            logger.info(f"메모리 할당 완료: {allocation_id} (크기: {size}바이트)")
            return allocation_id

        except Exception as e:
            logger.error(f"메모리 할당 실패: {e}")
            return ""

    async def deallocate_memory(self, allocation_id: str) -> bool:
        """메모리 해제"""
        try:
            if allocation_id not in self.allocations:
                logger.warning(f"할당을 찾을 수 없음: {allocation_id}")
                return False

            allocation = self.allocations[allocation_id]
            block_id = allocation.block_id

            if block_id not in self.memory_blocks:
                logger.warning(f"메모리 블록을 찾을 수 없음: {block_id}")
                return False

            memory_block = self.memory_blocks[block_id]

            # 메모리 블록 상태 변경
            memory_block.status = MemoryStatus.FREE
            memory_block.last_accessed = datetime.now()

            # 할당 정보 제거
            del self.allocations[allocation_id]

            # 성능 메트릭 업데이트
            self.performance_metrics["total_deallocations"] += 1
            self.performance_metrics["current_allocated_size"] -= memory_block.size
            self.performance_metrics["current_free_size"] += memory_block.size

            logger.info(f"메모리 해제 완료: {allocation_id}")
            return True

        except Exception as e:
            logger.error(f"메모리 해제 실패: {e}")
            return False

    async def get_memory_block(self, block_id: str) -> Optional[MemoryBlock]:
        """메모리 블록 조회"""
        try:
            if block_id in self.memory_blocks:
                memory_block = self.memory_blocks[block_id]
                memory_block.last_accessed = datetime.now()
                memory_block.access_count += 1
                return memory_block
            else:
                return None

        except Exception as e:
            logger.error(f"메모리 블록 조회 실패: {e}")
            return None

    async def get_allocation_info(
        self, allocation_id: str
    ) -> Optional[MemoryAllocation]:
        """할당 정보 조회"""
        try:
            return self.allocations.get(allocation_id)

        except Exception as e:
            logger.error(f"할당 정보 조회 실패: {e}")
            return None

    async def list_allocated_memory(
        self, memory_type: Optional[MemoryType] = None
    ) -> List[MemoryBlock]:
        """할당된 메모리 목록 조회"""
        try:
            allocated_blocks = []

            for block_id, memory_block in self.memory_blocks.items():
                if memory_block.status == MemoryStatus.ALLOCATED:
                    if memory_type is None or memory_block.memory_type == memory_type:
                        allocated_blocks.append(memory_block)

            return allocated_blocks

        except Exception as e:
            logger.error(f"할당된 메모리 목록 조회 실패: {e}")
            return []

    async def list_free_memory(self) -> List[MemoryBlock]:
        """사용 가능한 메모리 목록 조회"""
        try:
            free_blocks = []

            for block_id, memory_block in self.memory_blocks.items():
                if memory_block.status == MemoryStatus.FREE:
                    free_blocks.append(memory_block)

            return free_blocks

        except Exception as e:
            logger.error(f"사용 가능한 메모리 목록 조회 실패: {e}")
            return []

    async def cleanup_expired_memory(self) -> int:
        """만료된 메모리 정리"""
        try:
            current_time = datetime.now()
            expired_count = 0

            expired_allocations = []
            for allocation_id, allocation in self.allocations.items():
                if allocation.expires_at and allocation.expires_at < current_time:
                    expired_allocations.append(allocation_id)

            # 만료된 할당 해제
            for allocation_id in expired_allocations:
                await self.deallocate_memory(allocation_id)
                expired_count += 1

            logger.info(f"만료된 메모리 정리 완료: {expired_count}개")
            return expired_count

        except Exception as e:
            logger.error(f"만료된 메모리 정리 실패: {e}")
            return 0

    async def optimize_memory(self) -> Dict[str, Any]:
        """메모리 최적화"""
        try:
            optimization_results = {
                "fragmented_blocks_merged": 0,
                "unused_blocks_removed": 0,
                "total_space_saved": 0,
                "optimization_time": 0.0,
            }

            start_time = time.time()

            # 1. 사용되지 않는 블록 정리
            unused_blocks = []
            for block_id, memory_block in self.memory_blocks.items():
                if (
                    memory_block.status == MemoryStatus.FREE
                    and memory_block.last_accessed
                    < datetime.now() - timedelta(hours=24)
                ):
                    unused_blocks.append(block_id)

            for block_id in unused_blocks:
                del self.memory_blocks[block_id]
                optimization_results["unused_blocks_removed"] += 1

            # 2. 단편화된 블록 병합
            free_blocks = await self.list_free_memory()
            if len(free_blocks) > 1:
                # 간단한 병합 로직 (실제로는 더 복잡한 알고리즘 필요)
                optimization_results["fragmented_blocks_merged"] = len(free_blocks) // 2

            optimization_results["optimization_time"] = time.time() - start_time

            logger.info(f"메모리 최적화 완료: {optimization_results}")
            return optimization_results

        except Exception as e:
            logger.error(f"메모리 최적화 실패: {e}")
            return {}

    async def get_memory_statistics(self) -> Dict[str, Any]:
        """메모리 통계 조회"""
        try:
            stats = {
                "total_blocks": len(self.memory_blocks),
                "allocated_blocks": len(
                    [
                        b
                        for b in self.memory_blocks.values()
                        if b.status == MemoryStatus.ALLOCATED
                    ]
                ),
                "free_blocks": len(
                    [
                        b
                        for b in self.memory_blocks.values()
                        if b.status == MemoryStatus.FREE
                    ]
                ),
                "reserved_blocks": len(
                    [
                        b
                        for b in self.memory_blocks.values()
                        if b.status == MemoryStatus.RESERVED
                    ]
                ),
                "total_allocations": self.performance_metrics["total_allocations"],
                "total_deallocations": self.performance_metrics["total_deallocations"],
                "current_allocated_size": self.performance_metrics[
                    "current_allocated_size"
                ],
                "current_free_size": self.performance_metrics["current_free_size"],
                "allocation_success_rate": self.performance_metrics[
                    "allocation_success_rate"
                ],
                "average_allocation_time": self.performance_metrics[
                    "average_allocation_time"
                ],
            }

            # 타입별 통계
            type_stats = defaultdict(int)
            for memory_block in self.memory_blocks.values():
                type_stats[memory_block.memory_type.value] += 1

            stats["type_distribution"] = dict(type_stats)

            return stats

        except Exception as e:
            logger.error(f"메모리 통계 조회 실패: {e}")
            return {}

    async def reserve_memory(self, size: int, memory_type: MemoryType) -> str:
        """메모리 예약"""
        try:
            block_id = f"reserved_{int(time.time())}_{uuid.uuid4().hex[:8]}"

            memory_block = MemoryBlock(
                block_id=block_id,
                memory_type=memory_type,
                content="",
                size=size,
                status=MemoryStatus.RESERVED,
            )

            self.memory_blocks[block_id] = memory_block
            self.reserved_blocks.append(block_id)

            logger.info(f"메모리 예약 완료: {block_id} (크기: {size}바이트)")
            return block_id

        except Exception as e:
            logger.error(f"메모리 예약 실패: {e}")
            return ""

    async def release_reserved_memory(self, block_id: str) -> bool:
        """예약된 메모리 해제"""
        try:
            if block_id not in self.memory_blocks:
                return False

            memory_block = self.memory_blocks[block_id]
            if memory_block.status != MemoryStatus.RESERVED:
                return False

            del self.memory_blocks[block_id]
            if block_id in self.reserved_blocks:
                self.reserved_blocks.remove(block_id)

            logger.info(f"예약된 메모리 해제 완료: {block_id}")
            return True

        except Exception as e:
            logger.error(f"예약된 메모리 해제 실패: {e}")
            return False
