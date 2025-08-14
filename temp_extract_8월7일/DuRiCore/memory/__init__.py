#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRiCore Phase 2-5: 메모리 패키지

메모리 관리, 동기화, 최적화 시스템을 제공하는 패키지입니다.
"""

# Memory Manager 모듈
from .memory_manager.memory_allocator import MemoryAllocator, MemoryBlock, MemoryAllocation, MemoryStatus, MemoryType

# Memory Sync 모듈
from .memory_sync.memory_synchronizer import MemorySynchronizer, SyncOperation, MemoryConflict, SyncStatus, SyncType

# Memory Optimization 모듈
from .memory_optimization.memory_optimizer import MemoryOptimizer, OptimizationTask, MemoryUsageMetrics, OptimizationType, OptimizationStatus

# 패키지 버전
__version__ = "2.5.0"

# 주요 클래스들
__all__ = [
    # Memory Manager
    "MemoryAllocator",
    "MemoryBlock",
    "MemoryAllocation",
    "MemoryStatus",
    "MemoryType",
    
    # Memory Sync
    "MemorySynchronizer",
    "SyncOperation",
    "MemoryConflict",
    "SyncStatus",
    "SyncType",
    
    # Memory Optimization
    "MemoryOptimizer",
    "OptimizationTask",
    "MemoryUsageMetrics",
    "OptimizationType",
    "OptimizationStatus"
]
