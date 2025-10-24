#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 동적 리소스 할당 모듈

처리량과 품질에 따른 동적 리소스 할당 모듈입니다.
"""

import logging
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ResourceType(Enum):
    """리소스 유형"""

    CPU = "cpu"  # CPU 리소스
    MEMORY = "memory"  # 메모리 리소스
    STORAGE = "storage"  # 저장소 리소스
    NETWORK = "network"  # 네트워크 리소스
    TIME = "time"  # 시간 리소스


class OptimizationStrategy(Enum):
    """최적화 전략"""

    PERFORMANCE_FIRST = "performance_first"  # 성능 우선
    QUALITY_FIRST = "quality_first"  # 품질 우선
    BALANCED = "balanced"  # 균형
    ADAPTIVE = "adaptive"  # 적응적


@dataclass
class ResourceAllocation:
    """리소스 할당"""

    allocation_id: str
    resource_type: ResourceType
    allocated_amount: float
    max_available: float
    utilization_rate: float
    allocation_time: datetime
    priority: int = 0


class DynamicResourceAllocator:
    """동적 리소스 할당"""

    def __init__(self):
        self.allocation_history = []
        self.resource_limits = {}
        self.current_allocations = {}

    async def allocate_resources(
        self, requirements: Dict[str, Any], strategy: OptimizationStrategy
    ) -> List[ResourceAllocation]:
        """리소스 할당"""
        allocations = []

        for resource_type in ResourceType:
            if resource_type.value in requirements:
                allocation = await self._allocate_resource(resource_type, requirements, strategy)
                if allocation:
                    allocations.append(allocation)

        return allocations

    async def _allocate_resource(
        self,
        resource_type: ResourceType,
        requirements: Dict[str, Any],
        strategy: OptimizationStrategy,
    ) -> Optional[ResourceAllocation]:
        """개별 리소스 할당"""
        required_amount = requirements.get(resource_type.value, 0.0)
        max_available = await self._get_max_available(resource_type)

        if max_available <= 0:
            return None

        allocated_amount = await self._calculate_allocation(required_amount, max_available, strategy)
        utilization_rate = allocated_amount / max_available if max_available > 0 else 0.0
        priority = await self._determine_priority(resource_type, strategy)

        allocation = ResourceAllocation(
            allocation_id=f"allocation_{int(time.time())}_{resource_type.value}",
            resource_type=resource_type,
            allocated_amount=allocated_amount,
            max_available=max_available,
            utilization_rate=utilization_rate,
            allocation_time=datetime.now(),
            priority=priority,
        )

        self.allocation_history.append(allocation)
        return allocation

    async def _get_max_available(self, resource_type: ResourceType) -> float:
        """최대 사용 가능한 리소스량"""
        # 기본 리소스 한계 설정
        default_limits = {
            ResourceType.CPU: 100.0,
            ResourceType.MEMORY: 8192.0,  # MB
            ResourceType.STORAGE: 1000000.0,  # MB
            ResourceType.NETWORK: 1000.0,  # Mbps
            ResourceType.TIME: 3600.0,  # seconds
        }

        return default_limits.get(resource_type, 100.0)

    async def _calculate_allocation(
        self, required: float, max_available: float, strategy: OptimizationStrategy
    ) -> float:
        """할당량 계산"""
        if strategy == OptimizationStrategy.PERFORMANCE_FIRST:
            # 성능 우선: 요구량의 120%까지 할당
            return min(required * 1.2, max_available)
        elif strategy == OptimizationStrategy.QUALITY_FIRST:
            # 품질 우선: 요구량의 150%까지 할당
            return min(required * 1.5, max_available)
        elif strategy == OptimizationStrategy.BALANCED:
            # 균형: 요구량의 110%까지 할당
            return min(required * 1.1, max_available)
        else:  # ADAPTIVE
            # 적응적: 요구량과 가용량의 중간값
            return min(required, max_available * 0.8)

    async def _determine_priority(self, resource_type: ResourceType, strategy: OptimizationStrategy) -> int:
        """우선순위 결정"""
        base_priorities = {
            ResourceType.CPU: 3,
            ResourceType.MEMORY: 2,
            ResourceType.STORAGE: 1,
            ResourceType.NETWORK: 2,
            ResourceType.TIME: 4,
        }

        base_priority = base_priorities.get(resource_type, 1)

        # 전략에 따른 우선순위 조정
        if strategy == OptimizationStrategy.PERFORMANCE_FIRST:
            return base_priority + 1
        elif strategy == OptimizationStrategy.QUALITY_FIRST:
            return base_priority
        else:
            return base_priority
