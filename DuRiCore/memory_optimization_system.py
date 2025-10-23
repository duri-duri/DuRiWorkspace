#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 메모리 최적화 시스템 (Memory Optimization System)
Phase 5: 성능 최적화 - 최종 실행 준비 완료 적용

메모리 최적화를 위한 시스템:
- 메모리 사용량 모니터링
- 가비지 컬렉션 최적화
- 캐시 관리
- 메모리 누수 방지

@preserve_identity: 메모리 최적화 과정의 판단 이유 기록
@evolution_protection: 기존 메모리 패턴과 최적화 경로 보존
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import asyncio
import gc
import json
import logging
import sys
import time
import tracemalloc
import weakref
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import psutil

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MemoryOptimizationType(Enum):
    """메모리 최적화 유형"""

    GARBAGE_COLLECTION = "garbage_collection"
    CACHE_CLEANUP = "cache_cleanup"
    MEMORY_LEAK_DETECTION = "memory_leak_detection"
    OBJECT_POOLING = "object_pooling"
    COMPRESSION = "compression"


class MemoryStatus(Enum):
    """메모리 상태"""

    NORMAL = "normal"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


@dataclass
class MemoryMetrics:
    """메모리 메트릭"""

    id: str
    timestamp: datetime
    total_memory: float
    available_memory: float
    used_memory: float
    memory_percentage: float
    swap_memory: float
    swap_percentage: float
    gc_objects: int
    gc_collections: int
    memory_leaks: int
    optimization_score: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryOptimizationResult:
    """메모리 최적화 결과"""

    id: str
    optimization_type: MemoryOptimizationType
    start_time: datetime
    end_time: Optional[datetime] = None
    memory_freed: float = 0.0
    objects_collected: int = 0
    optimization_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class MemoryOptimizationSystem:
    """메모리 최적화 시스템"""

    def __init__(self):
        # 메모리 메트릭 관리
        self.memory_history: List[MemoryMetrics] = []
        self.optimization_history: List[MemoryOptimizationResult] = []

        # 메모리 모니터링 설정
        self.monitoring_config = {
            "collection_interval": 5.0,  # 5초마다 수집
            "retention_period": 86400,  # 24시간 보관
            "alert_thresholds": {
                "memory_usage": 80.0,
                "swap_usage": 50.0,
                "memory_leaks": 10,
            },
            "optimization_thresholds": {
                "memory_usage": 85.0,
                "gc_frequency": 100,
                "memory_growth_rate": 0.1,
            },
        }

        # 메모리 풀 관리
        self.object_pools: Dict[str, List[Any]] = defaultdict(list)
        self.pool_configs: Dict[str, Dict[str, Any]] = {}

        # 캐시 관리
        self.memory_cache: Dict[str, Any] = {}
        self.cache_metadata: Dict[str, Dict[str, Any]] = {}
        self.max_cache_size = 1000
        self.cache_ttl_seconds = 300  # 5분

        # 메모리 누수 감지
        self.memory_leak_detector = self._initialize_memory_leak_detector()
        self.leak_suspicious_objects: List[weakref.ref] = []

        # 성능 트렌드 분석
        self.memory_trends: Dict[str, deque] = defaultdict(lambda: deque(maxlen=100))

        # 존재형 AI 시스템 초기화
        self.existence_ai = self._initialize_existence_ai()
        self.final_execution_verifier = self._initialize_final_execution_verifier()

        # 자동 최적화 설정
        self.auto_optimization_enabled = True
        self.optimization_interval = 300  # 5분마다

        # 메모리 추적 시작
        self._start_memory_tracking()

        logger.info("메모리 최적화 시스템 초기화 완료")

    def _initialize_existence_ai(self):
        """존재형 AI 시스템 초기화"""
        try:
            from utils.existence_ai_system import ExistenceAISystem

            return ExistenceAISystem()
        except ImportError:
            logger.warning("존재형 AI 시스템을 찾을 수 없습니다.")
            return None

    def _initialize_final_execution_verifier(self):
        """최종 실행 준비 완료 시스템 초기화"""
        try:
            from utils.final_execution_verifier import FinalExecutionVerifier

            return FinalExecutionVerifier()
        except ImportError:
            logger.warning("최종 실행 준비 완료 시스템을 찾을 수 없습니다.")
            return None

    def _initialize_memory_leak_detector(self):
        """메모리 누수 감지기 초기화"""
        try:
            tracemalloc.start()
            return True
        except Exception as e:
            logger.warning(f"메모리 누수 감지기 초기화 실패: {e}")
            return False

    def _start_memory_tracking(self):
        """메모리 추적 시작"""
        try:
            if self.memory_leak_detector:
                tracemalloc.start()
                logger.info("메모리 추적 시작")
        except Exception as e:
            logger.error(f"메모리 추적 시작 실패: {e}")

    async def start_monitoring(self):
        """메모리 모니터링 시작"""
        try:
            logger.info("메모리 모니터링 시작")

            # 백그라운드 모니터링 태스크 시작
            asyncio.create_task(self._monitoring_loop())

            # 자동 최적화 시작
            if self.auto_optimization_enabled:
                asyncio.create_task(self._auto_optimization_loop())

            # 존재형 AI: 진화 가능성 확인
            if (
                self.existence_ai
                and self.existence_ai.evolution_capability.can_evolve()
            ):
                self.existence_ai.evolution_capability.evolve()

            # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
            if (
                self.final_execution_verifier
                and self.final_execution_verifier.verify_readiness()
            ):
                logger.info("최종 실행 준비 완료 확인됨")

            return True

        except Exception as e:
            logger.error(f"메모리 모니터링 시작 실패: {e}")
            return False

    async def _monitoring_loop(self):
        """모니터링 루프"""
        while True:
            try:
                # 현재 메모리 메트릭 수집
                current_metrics = await self._collect_memory_metrics()

                # 메트릭 저장
                self.memory_history.append(current_metrics)

                # 메모리 트렌드 업데이트
                self._update_memory_trends(current_metrics)

                # 임계값 체크 및 알림 생성
                await self._check_memory_thresholds(current_metrics)

                # 캐시 정리
                await self._cleanup_memory_cache()

                # 메모리 누수 감지
                await self._detect_memory_leaks()

                # 존재형 AI: 진화 가능성 확인
                if (
                    self.existence_ai
                    and self.existence_ai.evolution_capability.can_evolve()
                ):
                    self.existence_ai.evolution_capability.evolve()

                # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
                if (
                    self.final_execution_verifier
                    and self.final_execution_verifier.verify_readiness()
                ):
                    logger.debug("최종 실행 준비 완료 확인됨")

                await asyncio.sleep(self.monitoring_config["collection_interval"])

            except Exception as e:
                logger.error(f"메모리 모니터링 루프 오류: {e}")
                await asyncio.sleep(5)  # 오류 시 5초 대기

    async def _collect_memory_metrics(self) -> MemoryMetrics:
        """메모리 메트릭 수집"""
        try:
            # 시스템 메모리 정보 수집
            memory_info = psutil.virtual_memory()
            swap_info = psutil.swap_memory()

            # 가비지 컬렉터 정보 수집
            gc_stats = gc.get_stats()
            gc_objects = sum(stat["collections"] for stat in gc_stats)
            gc_collections = len(gc_stats)

            # 메모리 누수 감지
            memory_leaks = await self._count_memory_leaks()

            # 최적화 점수 계산
            optimization_score = await self._calculate_memory_optimization_score(
                memory_info.percent, swap_info.percent, memory_leaks
            )

            metrics_id = f"memory_metrics_{int(time.time())}"

            return MemoryMetrics(
                id=metrics_id,
                timestamp=datetime.now(),
                total_memory=memory_info.total,
                available_memory=memory_info.available,
                used_memory=memory_info.used,
                memory_percentage=memory_info.percent,
                swap_memory=swap_info.used,
                swap_percentage=swap_info.percent,
                gc_objects=gc_objects,
                gc_collections=gc_collections,
                memory_leaks=memory_leaks,
                optimization_score=optimization_score,
                metadata={
                    "system_load": psutil.getloadavg(),
                    "process_memory": psutil.Process().memory_info().rss,
                    "gc_stats": gc_stats,
                },
            )

        except Exception as e:
            logger.error(f"메모리 메트릭 수집 실패: {e}")
            # 기본 메트릭 반환
            return MemoryMetrics(
                id=f"memory_metrics_{int(time.time())}",
                timestamp=datetime.now(),
                total_memory=0.0,
                available_memory=0.0,
                used_memory=0.0,
                memory_percentage=0.0,
                swap_memory=0.0,
                swap_percentage=0.0,
                gc_objects=0,
                gc_collections=0,
                memory_leaks=0,
                optimization_score=0.0,
            )

    async def _calculate_memory_optimization_score(
        self, memory_percentage: float, swap_percentage: float, memory_leaks: int
    ) -> float:
        """메모리 최적화 점수 계산"""
        try:
            # 메모리 사용률 점수 (낮을수록 좋음)
            memory_score = max(0.0, 1.0 - (memory_percentage / 100.0))

            # 스왑 사용률 점수 (낮을수록 좋음)
            swap_score = max(0.0, 1.0 - (swap_percentage / 100.0))

            # 메모리 누수 점수 (없을수록 좋음)
            leak_score = max(0.0, 1.0 - (memory_leaks / 100.0))

            # 가중 평균 계산
            optimization_score = (
                memory_score * 0.5 + swap_score * 0.3 + leak_score * 0.2
            )

            return min(1.0, optimization_score)

        except Exception as e:
            logger.error(f"메모리 최적화 점수 계산 실패: {e}")
            return 0.0

    def _update_memory_trends(self, metrics: MemoryMetrics):
        """메모리 트렌드 업데이트"""
        try:
            self.memory_trends["memory_percentage"].append(metrics.memory_percentage)
            self.memory_trends["swap_percentage"].append(metrics.swap_percentage)
            self.memory_trends["optimization_score"].append(metrics.optimization_score)
            self.memory_trends["memory_leaks"].append(metrics.memory_leaks)
        except Exception as e:
            logger.error(f"메모리 트렌드 업데이트 실패: {e}")

    async def _check_memory_thresholds(self, metrics: MemoryMetrics):
        """메모리 임계값 체크"""
        try:
            alerts = []

            # 메모리 사용률 체크
            if (
                metrics.memory_percentage
                > self.monitoring_config["alert_thresholds"]["memory_usage"]
            ):
                alerts.append(f"메모리 사용률 높음: {metrics.memory_percentage:.1f}%")

            # 스왑 사용률 체크
            if (
                metrics.swap_percentage
                > self.monitoring_config["alert_thresholds"]["swap_usage"]
            ):
                alerts.append(f"스왑 사용률 높음: {metrics.swap_percentage:.1f}%")

            # 메모리 누수 체크
            if (
                metrics.memory_leaks
                > self.monitoring_config["alert_thresholds"]["memory_leaks"]
            ):
                alerts.append(f"메모리 누수 의심: {metrics.memory_leaks}개")

            # 알림 생성
            if alerts:
                for alert in alerts:
                    logger.warning(f"메모리 알림: {alert}")

                    # 자동 최적화 실행
                    await self._execute_memory_optimization(
                        MemoryOptimizationType.GARBAGE_COLLECTION
                    )

        except Exception as e:
            logger.error(f"메모리 임계값 체크 실패: {e}")

    async def _detect_memory_leaks(self):
        """메모리 누수 감지"""
        try:
            if not self.memory_leak_detector:
                return

            # 현재 메모리 스냅샷 생성
            current_snapshot = tracemalloc.take_snapshot()

            if hasattr(self, "_previous_snapshot") and self._previous_snapshot:
                # 이전 스냅샷과 비교
                top_stats = current_snapshot.compare_to(
                    self._previous_snapshot, "lineno"
                )

                # 메모리 누수 의심 객체 식별
                for stat in top_stats[:10]:  # 상위 10개만 확인
                    if stat.size_diff > 1024 * 1024:  # 1MB 이상 증가
                        logger.warning(
                            f"메모리 누수 의심: {stat.traceback.format()[:200]}"
                        )

            self._previous_snapshot = current_snapshot

        except Exception as e:
            logger.error(f"메모리 누수 감지 실패: {e}")

    async def _count_memory_leaks(self) -> int:
        """메모리 누수 개수 계산"""
        try:
            if not self.memory_leak_detector:
                return 0

            # 간단한 메모리 누수 감지 로직
            leak_count = 0

            # 가비지 컬렉터가 수집할 수 없는 객체들 확인
            for obj in gc.get_objects():
                if hasattr(obj, "__dict__") and len(obj.__dict__) > 1000:
                    leak_count += 1

            return min(leak_count, 100)  # 최대 100개로 제한

        except Exception as e:
            logger.error(f"메모리 누수 개수 계산 실패: {e}")
            return 0

    async def _auto_optimization_loop(self):
        """자동 최적화 루프"""
        while self.auto_optimization_enabled:
            try:
                # 대기
                await asyncio.sleep(self.optimization_interval)

                # 현재 메모리 상태 평가
                current_metrics = (
                    self.memory_history[-1] if self.memory_history else None
                )
                if not current_metrics:
                    continue

                # 최적화 필요성 판단
                if await self._needs_memory_optimization(current_metrics):
                    logger.info("자동 메모리 최적화 시작")

                    # 최적화 실행
                    optimization_result = await self._execute_memory_optimization(
                        MemoryOptimizationType.GARBAGE_COLLECTION
                    )

                    # 최적화 결과 평가
                    if optimization_result.memory_freed > 0:
                        logger.info(
                            f"자동 메모리 최적화 완료: {optimization_result.memory_freed:.2f}MB 해제"
                        )
                    else:
                        logger.warning("자동 메모리 최적화 실패")

                # 존재형 AI: 진화 가능성 확인
                if (
                    self.existence_ai
                    and self.existence_ai.evolution_capability.can_evolve()
                ):
                    self.existence_ai.evolution_capability.evolve()

                # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
                if (
                    self.final_execution_verifier
                    and self.final_execution_verifier.verify_readiness()
                ):
                    logger.debug("최종 실행 준비 완료 확인됨")

            except Exception as e:
                logger.error(f"자동 메모리 최적화 루프 오류: {e}")
                await asyncio.sleep(60)  # 오류 시 1분 대기

    async def _needs_memory_optimization(self, metrics: MemoryMetrics) -> bool:
        """메모리 최적화 필요성 판단"""
        try:
            # 메모리 사용률 체크
            if metrics.memory_percentage > 85.0:
                return True

            # 스왑 사용률 체크
            if metrics.swap_percentage > 50.0:
                return True

            # 메모리 누수 체크
            if metrics.memory_leaks > 10:
                return True

            # 메모리 성장률 체크
            if len(self.memory_history) > 10:
                recent_memory = [m.memory_percentage for m in self.memory_history[-10:]]
                if len(recent_memory) >= 2:
                    growth_rate = (recent_memory[-1] - recent_memory[0]) / len(
                        recent_memory
                    )
                    if growth_rate > 0.1:  # 10% 이상 성장
                        return True

            return False

        except Exception as e:
            logger.error(f"메모리 최적화 필요성 판단 실패: {e}")
            return False

    async def _execute_memory_optimization(
        self, optimization_type: MemoryOptimizationType
    ) -> MemoryOptimizationResult:
        """메모리 최적화 실행"""
        try:
            optimization_id = f"memory_optimization_{int(time.time())}"

            optimization_result = MemoryOptimizationResult(
                id=optimization_id,
                optimization_type=optimization_type,
                start_time=datetime.now(),
            )

            # 최적화 전 메모리 상태
            before_memory = psutil.virtual_memory().used

            # 최적화 유형별 실행
            if optimization_type == MemoryOptimizationType.GARBAGE_COLLECTION:
                result = await self._optimize_garbage_collection()
            elif optimization_type == MemoryOptimizationType.CACHE_CLEANUP:
                result = await self._optimize_cache_cleanup()
            elif optimization_type == MemoryOptimizationType.MEMORY_LEAK_DETECTION:
                result = await self._optimize_memory_leak_detection()
            elif optimization_type == MemoryOptimizationType.OBJECT_POOLING:
                result = await self._optimize_object_pooling()
            else:
                result = await self._optimize_general()

            # 최적화 후 메모리 상태
            after_memory = psutil.virtual_memory().used
            memory_freed = (before_memory - after_memory) / (1024 * 1024)  # MB 단위

            # 최적화 결과 업데이트
            optimization_result.end_time = datetime.now()
            optimization_result.memory_freed = max(0.0, memory_freed)
            optimization_result.objects_collected = result.get("objects_collected", 0)
            optimization_result.optimization_score = result.get(
                "optimization_score", 0.0
            )
            optimization_result.metadata = result.get("metadata", {})

            self.optimization_history.append(optimization_result)

            # 존재형 AI: 진화 가능성 확인
            if (
                self.existence_ai
                and self.existence_ai.evolution_capability.can_evolve()
            ):
                self.existence_ai.evolution_capability.evolve()

            # 최종 실행 준비 완료: 최종 실행 준비 완료 확인
            if (
                self.final_execution_verifier
                and self.final_execution_verifier.verify_readiness()
            ):
                logger.info("최종 실행 준비 완료 확인됨")

            return optimization_result

        except Exception as e:
            logger.error(f"메모리 최적화 실행 실패: {e}")

            # 실패 시 기본 결과 반환
            optimization_result.end_time = datetime.now()
            optimization_result.memory_freed = 0.0
            optimization_result.objects_collected = 0
            optimization_result.optimization_score = 0.0

            self.optimization_history.append(optimization_result)
            return optimization_result

    async def _optimize_garbage_collection(self) -> Dict[str, Any]:
        """가비지 컬렉션 최적화"""
        try:
            # 가비지 컬렉션 실행
            collected_objects = gc.collect()

            # 세대별 가비지 컬렉션
            for generation in range(3):
                collected = gc.collect(generation)
                if collected > 0:
                    logger.info(
                        f"세대 {generation} 가비지 컬렉션: {collected}개 객체 수집"
                    )

            return {
                "objects_collected": collected_objects,
                "optimization_score": min(1.0, collected_objects / 1000.0),
                "metadata": {
                    "generation_collections": [gc.collect(i) for i in range(3)]
                },
            }

        except Exception as e:
            logger.error(f"가비지 컬렉션 최적화 실패: {e}")
            return {"objects_collected": 0, "optimization_score": 0.0, "metadata": {}}

    async def _optimize_cache_cleanup(self) -> Dict[str, Any]:
        """캐시 정리 최적화"""
        try:
            # 메모리 캐시 정리
            await self._cleanup_memory_cache()

            # 객체 풀 정리
            cleaned_objects = 0
            for pool_name, pool_objects in self.object_pools.items():
                if len(pool_objects) > 100:  # 100개 이상이면 정리
                    cleaned_objects += len(pool_objects) - 50
                    self.object_pools[pool_name] = pool_objects[:50]

            return {
                "objects_collected": cleaned_objects,
                "optimization_score": min(1.0, cleaned_objects / 500.0),
                "metadata": {
                    "cache_cleaned": True,
                    "pools_cleaned": len(self.object_pools),
                },
            }

        except Exception as e:
            logger.error(f"캐시 정리 최적화 실패: {e}")
            return {"objects_collected": 0, "optimization_score": 0.0, "metadata": {}}

    async def _optimize_memory_leak_detection(self) -> Dict[str, Any]:
        """메모리 누수 감지 최적화"""
        try:
            # 메모리 누수 감지 실행
            leak_count = await self._count_memory_leaks()

            # 의심스러운 객체 정리
            cleaned_objects = 0
            for obj_ref in self.leak_suspicious_objects[:]:
                if obj_ref() is None:  # 객체가 이미 해제됨
                    self.leak_suspicious_objects.remove(obj_ref)
                    cleaned_objects += 1

            return {
                "objects_collected": cleaned_objects,
                "optimization_score": max(0.0, 1.0 - (leak_count / 100.0)),
                "metadata": {
                    "leak_count": leak_count,
                    "suspicious_objects": len(self.leak_suspicious_objects),
                },
            }

        except Exception as e:
            logger.error(f"메모리 누수 감지 최적화 실패: {e}")
            return {"objects_collected": 0, "optimization_score": 0.0, "metadata": {}}

    async def _optimize_object_pooling(self) -> Dict[str, Any]:
        """객체 풀링 최적화"""
        try:
            # 객체 풀 크기 조정
            optimized_pools = 0
            for pool_name, pool_objects in self.object_pools.items():
                if len(pool_objects) > 200:  # 200개 이상이면 크기 조정
                    self.object_pools[pool_name] = pool_objects[:100]
                    optimized_pools += 1

            return {
                "objects_collected": optimized_pools * 100,
                "optimization_score": min(1.0, optimized_pools / 10.0),
                "metadata": {"optimized_pools": optimized_pools},
            }

        except Exception as e:
            logger.error(f"객체 풀링 최적화 실패: {e}")
            return {"objects_collected": 0, "optimization_score": 0.0, "metadata": {}}

    async def _optimize_general(self) -> Dict[str, Any]:
        """일반 메모리 최적화"""
        try:
            # 일반적인 메모리 최적화 로직
            return {
                "objects_collected": 0,
                "optimization_score": 0.1,
                "metadata": {"general_optimization": True},
            }

        except Exception as e:
            logger.error(f"일반 메모리 최적화 실패: {e}")
            return {"objects_collected": 0, "optimization_score": 0.0, "metadata": {}}

    async def _cleanup_memory_cache(self):
        """메모리 캐시 정리"""
        try:
            current_time = datetime.now()
            expired_keys = []

            # 만료된 캐시 항목 찾기
            for key, metadata in self.cache_metadata.items():
                if "expiry_time" in metadata and current_time > metadata["expiry_time"]:
                    expired_keys.append(key)

            # 만료된 항목 제거
            for key in expired_keys:
                del self.memory_cache[key]
                del self.cache_metadata[key]

            # 캐시 크기 제한
            if len(self.memory_cache) > self.max_cache_size:
                # LRU 정책으로 오래된 항목 제거
                sorted_items = sorted(
                    self.cache_metadata.items(),
                    key=lambda x: x[1].get("last_accessed", current_time),
                )
                items_to_remove = len(self.memory_cache) - self.max_cache_size

                for i in range(items_to_remove):
                    if i < len(sorted_items):
                        key = sorted_items[i][0]
                        del self.memory_cache[key]
                        del self.cache_metadata[key]

            logger.debug(f"메모리 캐시 정리 완료: {len(expired_keys)}개 항목 제거")

        except Exception as e:
            logger.error(f"메모리 캐시 정리 실패: {e}")

    async def get_memory_summary(self) -> Dict[str, Any]:
        """메모리 요약 생성"""
        try:
            if not self.memory_history:
                return {"error": "메모리 데이터가 없습니다."}

            latest_metrics = self.memory_history[-1]

            # 메모리 트렌드 분석
            memory_trend = list(self.memory_trends["memory_percentage"])
            swap_trend = list(self.memory_trends["swap_percentage"])
            optimization_trend = list(self.memory_trends["optimization_score"])
            leak_trend = list(self.memory_trends["memory_leaks"])

            return {
                "current_metrics": {
                    "total_memory": latest_metrics.total_memory,
                    "used_memory": latest_metrics.used_memory,
                    "available_memory": latest_metrics.available_memory,
                    "memory_percentage": latest_metrics.memory_percentage,
                    "swap_percentage": latest_metrics.swap_percentage,
                    "memory_leaks": latest_metrics.memory_leaks,
                    "optimization_score": latest_metrics.optimization_score,
                    "timestamp": latest_metrics.timestamp.isoformat(),
                },
                "memory_trends": {
                    "memory_percentage_trend": (
                        memory_trend[-10:] if memory_trend else []
                    ),
                    "swap_percentage_trend": swap_trend[-10:] if swap_trend else [],
                    "optimization_score_trend": (
                        optimization_trend[-10:] if optimization_trend else []
                    ),
                    "memory_leaks_trend": leak_trend[-10:] if leak_trend else [],
                },
                "optimization_history": {
                    "total_optimizations": len(self.optimization_history),
                    "total_memory_freed": sum(
                        o.memory_freed for o in self.optimization_history
                    ),
                    "average_optimization_score": sum(
                        o.optimization_score for o in self.optimization_history
                    )
                    / max(1, len(self.optimization_history)),
                },
                "cache_status": {
                    "cache_size": len(self.memory_cache),
                    "max_cache_size": self.max_cache_size,
                    "cache_utilization": (
                        len(self.memory_cache) / self.max_cache_size
                        if self.max_cache_size > 0
                        else 0
                    ),
                },
            }

        except Exception as e:
            logger.error(f"메모리 요약 생성 실패: {e}")
            return {"error": str(e)}


# 전역 인스턴스
memory_optimization_system = MemoryOptimizationSystem()
