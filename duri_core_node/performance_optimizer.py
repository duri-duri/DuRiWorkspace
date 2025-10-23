#!/usr/bin/env python3
"""
DuRi Core Node - 성능 최적화 시스템
병렬 처리, 캐싱, 로드 밸런싱 기능
"""
import asyncio
import hashlib
import json
import logging
import time
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import aiohttp

logger = logging.getLogger(__name__)


class PerformanceOptimizer:
    """성능 최적화 관리자"""

    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5분 캐시
        self.request_history = defaultdict(list)
        self.performance_metrics = {
            "total_requests": 0,
            "cache_hits": 0,
            "cache_misses": 0,
            "average_response_time": 0.0,
            "parallel_requests": 0,
            "error_count": 0,
        }
        self.executor = ThreadPoolExecutor(max_workers=10)
        logger.info("⚡ 성능 최적화 시스템 초기화 완료")

    async def optimize_request(
        self, user_input: str, duri_response: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """요청 최적화 처리"""
        try:
            start_time = time.time()

            # 1. 캐시 확인
            cache_key = self._generate_cache_key(user_input, duri_response, metadata)
            cached_result = self._get_from_cache(cache_key)

            if cached_result:
                self.performance_metrics["cache_hits"] += 1
                logger.info(f"⚡ 캐시 히트: {cache_key[:20]}...")
                return cached_result

            self.performance_metrics["cache_misses"] += 1

            # 2. 병렬 처리 실행
            result = await self._parallel_processing(
                user_input, duri_response, metadata
            )

            # 3. 결과 캐싱
            self._cache_result(cache_key, result)

            # 4. 성능 메트릭 업데이트
            processing_time = time.time() - start_time
            self._update_performance_metrics(processing_time)

            return result

        except Exception as e:
            logger.error(f"❌ 성능 최적화 오류: {e}")
            self.performance_metrics["error_count"] += 1
            raise

    def _generate_cache_key(
        self, user_input: str, duri_response: str, metadata: Dict[str, Any]
    ) -> str:
        """캐시 키 생성"""
        content = f"{user_input}:{duri_response}:{json.dumps(metadata, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """캐시에서 결과 조회"""
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item["timestamp"] < self.cache_ttl:
                return cached_item["data"]
            else:
                # 만료된 캐시 삭제
                del self.cache[cache_key]
        return None

    def _cache_result(self, cache_key: str, result: Dict[str, Any]):
        """결과 캐싱"""
        self.cache[cache_key] = {"data": result, "timestamp": time.time()}

        # 캐시 크기 제한 (최대 1000개)
        if len(self.cache) > 1000:
            # 가장 오래된 항목 삭제
            oldest_key = min(
                self.cache.keys(), key=lambda k: self.cache[k]["timestamp"]
            )
            del self.cache[oldest_key]

    async def _parallel_processing(
        self, user_input: str, duri_response: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """병렬 처리 실행"""
        try:
            # Brain과 Evolution 노드에 동시 요청
            brain_task = asyncio.create_task(
                self._call_brain_node(user_input, duri_response, metadata)
            )
            evolution_task = asyncio.create_task(
                self._call_evolution_node(user_input, duri_response, metadata)
            )

            # 병렬로 결과 수집
            brain_result, evolution_result = await asyncio.gather(
                brain_task, evolution_task, return_exceptions=True
            )

            # 오류 처리
            if isinstance(brain_result, Exception):
                logger.error(f"Brain 노드 오류: {brain_result}")
                brain_result = {"error": str(brain_result)}

            if isinstance(evolution_result, Exception):
                logger.error(f"Evolution 노드 오류: {evolution_result}")
                evolution_result = {"error": str(evolution_result)}

            # 결과 통합
            integrated_result = self._integrate_results(brain_result, evolution_result)

            return integrated_result

        except Exception as e:
            logger.error(f"병렬 처리 오류: {e}")
            raise

    async def _call_brain_node(
        self, user_input: str, duri_response: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Brain 노드 호출 (비동기)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8091/analyze",
                    json={
                        "user_input": user_input,
                        "duri_response": duri_response,
                        "metadata": metadata,
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Brain node error: {response.status}"}

        except Exception as e:
            logger.error(f"Brain 노드 호출 오류: {e}")
            return {"error": str(e)}

    async def _call_evolution_node(
        self, user_input: str, duri_response: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Evolution 노드 호출 (비동기)"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "http://localhost:8092/learn",
                    json={
                        "user_input": user_input,
                        "duri_response": duri_response,
                        "metadata": metadata,
                    },
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return {"error": f"Evolution node error: {response.status}"}

        except Exception as e:
            logger.error(f"Evolution 노드 호출 오류: {e}")
            return {"error": str(e)}

    def _integrate_results(
        self, brain_result: Dict[str, Any], evolution_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """결과 통합 (최적화된 버전)"""
        try:
            # 통합 점수 계산 (가중 평균)
            brain_score = brain_result.get("analysis_score", 0.0)
            evolution_score = evolution_result.get("learning_score", 0.0)

            # 가중치 적용 (Brain: 0.6, Evolution: 0.4)
            integrated_score = (brain_score * 0.6) + (evolution_score * 0.4)

            return {
                "status": "success",
                "conversation_id": f"optimized_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "integrated_score": integrated_score,
                "brain_analysis": brain_result,
                "evolution_learning": evolution_result,
                "optimization": {
                    "cache_used": False,  # 병렬 처리에서는 캐시 미사용
                    "parallel_processing": True,
                    "performance_metrics": self.get_performance_metrics(),
                },
                "timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"결과 통합 오류: {e}")
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    def _update_performance_metrics(self, processing_time: float):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_requests"] += 1
        self.performance_metrics["parallel_requests"] += 1

        # 평균 응답 시간 업데이트
        current_avg = self.performance_metrics["average_response_time"]
        total_requests = self.performance_metrics["total_requests"]
        new_avg = (
            (current_avg * (total_requests - 1)) + processing_time
        ) / total_requests
        self.performance_metrics["average_response_time"] = new_avg

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        cache_hit_rate = 0.0
        if self.performance_metrics["total_requests"] > 0:
            cache_hit_rate = (
                self.performance_metrics["cache_hits"]
                / self.performance_metrics["total_requests"]
            )

        return {
            **self.performance_metrics,
            "cache_hit_rate": cache_hit_rate,
            "cache_size": len(self.cache),
            "timestamp": datetime.now().isoformat(),
        }

    def clear_cache(self):
        """캐시 클리어"""
        self.cache.clear()
        logger.info("🗑️ 캐시 클리어 완료")

    def get_cache_stats(self) -> Dict[str, Any]:
        """캐시 통계"""
        return {
            "cache_size": len(self.cache),
            "cache_ttl": self.cache_ttl,
            "cache_keys": list(self.cache.keys())[:10],  # 상위 10개만
            "timestamp": datetime.now().isoformat(),
        }


class LoadBalancer:
    """로드 밸런서"""

    def __init__(self):
        self.node_health = {
            "brain": {"healthy": True, "last_check": None, "response_time": 0.0},
            "evolution": {"healthy": True, "last_check": None, "response_time": 0.0},
        }
        self.request_count = {"brain": 0, "evolution": 0}
        logger.info("⚖️ 로드 밸런서 초기화 완료")

    async def check_node_health(self):
        """노드 상태 확인"""
        try:
            # Brain 노드 상태 확인
            brain_start = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "http://localhost:8091/health", timeout=2
                    ) as response:
                        self.node_health["brain"]["healthy"] = response.status == 200
                        self.node_health["brain"]["response_time"] = (
                            time.time() - brain_start
                        )
                        self.node_health["brain"][
                            "last_check"
                        ] = datetime.now().isoformat()
            except:
                self.node_health["brain"]["healthy"] = False

            # Evolution 노드 상태 확인
            evolution_start = time.time()
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "http://localhost:8092/health", timeout=2
                    ) as response:
                        self.node_health["evolution"]["healthy"] = (
                            response.status == 200
                        )
                        self.node_health["evolution"]["response_time"] = (
                            time.time() - evolution_start
                        )
                        self.node_health["evolution"][
                            "last_check"
                        ] = datetime.now().isoformat()
            except:
                self.node_health["evolution"]["healthy"] = False

        except Exception as e:
            logger.error(f"노드 상태 확인 오류: {e}")

    def get_optimal_node(self, operation_type: str) -> str:
        """최적 노드 선택"""
        if operation_type == "analysis":
            # 분석 작업은 Brain 노드
            return "brain" if self.node_health["brain"]["healthy"] else "evolution"
        elif operation_type == "learning":
            # 학습 작업은 Evolution 노드
            return "evolution" if self.node_health["evolution"]["healthy"] else "brain"
        else:
            # 기본적으로 응답 시간이 빠른 노드 선택
            if (
                self.node_health["brain"]["response_time"]
                <= self.node_health["evolution"]["response_time"]
            ):
                return "brain"
            else:
                return "evolution"

    def get_load_balancing_stats(self) -> Dict[str, Any]:
        """로드 밸런싱 통계"""
        return {
            "node_health": self.node_health,
            "request_count": self.request_count,
            "timestamp": datetime.now().isoformat(),
        }
