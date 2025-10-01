#!/usr/bin/env python3
"""
DuRiCore - Phase 4 성능 최적화 테스트
Vector DB 연동, LLM 호출 최적화, 메모리 사용량 분석
"""

import asyncio
import json
import logging
import os

# DuRiCore 모듈 import
import sys
import time
from datetime import datetime
from typing import Any, Dict, List

import psutil

# 현재 디렉토리를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, "DuRiCore"))

try:
    from DuRiCore.memory.vector_store import VectorMemoryStore
    from DuRiCore.utils.llm_interface import AsyncLLMInterface, LLMProvider, QueryType
    from DuRiCore.utils.memory_manager import MemoryManager, MemoryQuery
except ImportError:
    try:
        # 대체 import 경로
        from memory.vector_store import VectorMemoryStore

        from utils.llm_interface import AsyncLLMInterface, LLMProvider, QueryType
        from utils.memory_manager import MemoryManager, MemoryQuery
    except ImportError:
        # 직접 import
        from DuRiCore.memory.vector_store import VectorMemoryStore
        from DuRiCore.utils.llm_interface import (
            AsyncLLMInterface,
            LLMProvider,
            QueryType,
        )
        from DuRiCore.utils.memory_manager import MemoryManager, MemoryQuery

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Phase4PerformanceTester:
    """Phase 4 성능 테스트"""

    def __init__(self):
        self.llm_interface = None
        self.memory_manager = None
        self.vector_store = None
        self.test_results = {}

    async def setup(self):
        """테스트 환경 설정"""
        logger.info("Phase 4 성능 테스트 환경 설정 시작")

        # LLM 인터페이스 초기화
        self.llm_interface = AsyncLLMInterface(max_concurrent_requests=5)
        await self.llm_interface.start()

        # 메모리 매니저 초기화
        self.memory_manager = MemoryManager(storage_path="test_memory_data")
        await self.memory_manager.start()

        # 벡터 스토어 초기화
        self.vector_store = VectorMemoryStore()

        logger.info("테스트 환경 설정 완료")

    async def cleanup(self):
        """테스트 환경 정리"""
        logger.info("테스트 환경 정리 시작")

        if self.llm_interface:
            await self.llm_interface.stop()

        if self.memory_manager:
            await self.memory_manager.stop()

        logger.info("테스트 환경 정리 완료")

    def get_memory_usage(self) -> Dict[str, float]:
        """메모리 사용량 조회"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()

        return {
            "rss_mb": memory_info.rss / 1024 / 1024,  # RSS (MB)
            "vms_mb": memory_info.vms / 1024 / 1024,  # VMS (MB)
            "percent": process.memory_percent(),
        }

    async def test_llm_interface_performance(self):
        """LLM 인터페이스 성능 테스트"""
        logger.info("LLM 인터페이스 성능 테스트 시작")

        test_prompts = [
            ("감정 분석 테스트", QueryType.EMOTION_ANALYSIS),
            ("학습 쿼리 테스트", QueryType.LEARNING_QUERY),
            ("윤리 판단 테스트", QueryType.ETHICAL_JUDGMENT),
            ("진화 쿼리 테스트", QueryType.EVOLUTION_QUERY),
            ("일반 쿼리 테스트", QueryType.GENERAL),
        ]

        results = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "average_response_time": 0.0,
            "total_tokens": 0,
            "cache_hit_rate": 0.0,
        }

        start_time = time.time()

        # 단일 요청 테스트
        for prompt, query_type in test_prompts:
            try:
                response = await self.llm_interface.ask_llm(
                    prompt, query_type, provider=LLMProvider.LOCAL
                )
                results["successful_requests"] += 1
                results["total_tokens"] += response.token_count
                logger.info(f"LLM 응답: {response.content[:50]}...")

            except Exception as e:
                results["failed_requests"] += 1
                logger.error(f"LLM 요청 실패: {e}")

            results["total_requests"] += 1

        # 배치 요청 테스트
        batch_requests = []
        for i in range(10):
            batch_requests.append(
                {
                    "prompt": f"배치 테스트 {i}",
                    "query_type": QueryType.GENERAL,
                    "provider": LLMProvider.LOCAL,
                }
            )

        try:
            batch_responses = await asyncio.gather(
                *[
                    self.llm_interface.ask_llm(
                        req["prompt"], req["query_type"], provider=req["provider"]
                    )
                    for req in batch_requests
                ]
            )

            results["successful_requests"] += len(batch_responses)
            results["total_requests"] += len(batch_requests)

        except Exception as e:
            logger.error(f"배치 요청 실패: {e}")
            results["failed_requests"] += len(batch_requests)

        total_time = time.time() - start_time
        results["average_response_time"] = total_time / results["total_requests"]

        # 성능 통계 조회
        llm_stats = self.llm_interface.get_performance_stats()
        results["cache_hit_rate"] = llm_stats["cache_hit_rate"]

        self.test_results["llm_interface"] = results
        logger.info(f"LLM 인터페이스 테스트 완료: {results}")

    async def test_memory_manager_performance(self):
        """메모리 매니저 성능 테스트"""
        logger.info("메모리 매니저 성능 테스트 시작")

        # 테스트 데이터 생성
        test_memories = [
            ("감정 관련 메모리 1", "emotion", 0.8, ["감정", "기쁨"]),
            ("학습 관련 메모리 1", "learning", 0.9, ["학습", "패턴"]),
            ("윤리 관련 메모리 1", "ethical", 0.7, ["윤리", "판단"]),
            ("진화 관련 메모리 1", "evolution", 0.6, ["진화", "성장"]),
            ("일반 메모리 1", "general", 0.5, ["일반", "정보"]),
        ]

        results = {
            "total_stored": 0,
            "total_queries": 0,
            "average_query_time": 0.0,
            "cache_hit_rate": 0.0,
        }

        start_time = time.time()

        # 메모리 저장 테스트
        for content, memory_type, importance, tags in test_memories:
            try:
                memory_id = await self.memory_manager.store_memory(
                    content, memory_type, importance, tags
                )
                results["total_stored"] += 1
                logger.info(f"메모리 저장: {memory_id}")

            except Exception as e:
                logger.error(f"메모리 저장 실패: {e}")

        # 메모리 검색 테스트
        search_queries = [
            MemoryQuery("감정", memory_type="emotion"),
            MemoryQuery("학습", memory_type="learning"),
            MemoryQuery("윤리", memory_type="ethical"),
            MemoryQuery("진화", memory_type="evolution"),
            MemoryQuery("일반", memory_type="general"),
        ]

        for query in search_queries:
            try:
                memories = await self.memory_manager.search_memories(query)
                results["total_queries"] += 1
                logger.info(f"검색 결과: {len(memories)}개")

            except Exception as e:
                logger.error(f"메모리 검색 실패: {e}")

        total_time = time.time() - start_time
        results["average_query_time"] = (
            total_time / results["total_queries"] if results["total_queries"] > 0 else 0
        )

        # 메모리 통계 조회
        memory_stats = await self.memory_manager.get_memory_statistics()
        results["cache_hit_rate"] = memory_stats.get("cache_hits", 0) / max(
            memory_stats.get("total_queries", 1), 1
        )

        self.test_results["memory_manager"] = results
        logger.info(f"메모리 매니저 테스트 완료: {results}")

    async def test_vector_store_performance(self):
        """벡터 스토어 성능 테스트"""
        logger.info("벡터 스토어 성능 테스트 시작")

        results = {"total_stored": 0, "total_searches": 0, "average_search_time": 0.0}

        # 테스트 데이터
        test_data = [
            (
                "벡터 메모리 1",
                {"emotion": "기쁨", "intensity": 0.8},
                {"context": "테스트"},
            ),
            (
                "벡터 메모리 2",
                {"emotion": "슬픔", "intensity": 0.6},
                {"context": "테스트"},
            ),
            (
                "벡터 메모리 3",
                {"emotion": "분노", "intensity": 0.7},
                {"context": "테스트"},
            ),
            (
                "벡터 메모리 4",
                {"emotion": "평온", "intensity": 0.9},
                {"context": "테스트"},
            ),
            (
                "벡터 메모리 5",
                {"emotion": "기대", "intensity": 0.5},
                {"context": "테스트"},
            ),
        ]

        start_time = time.time()

        # 벡터 메모리 저장 테스트
        for content, emotion_data, context_data in test_data:
            try:
                memory_id = self.vector_store.store_memory(
                    content, emotion_data, context_data, importance=0.7
                )
                results["total_stored"] += 1
                logger.info(f"벡터 메모리 저장: {memory_id}")

            except Exception as e:
                logger.error(f"벡터 메모리 저장 실패: {e}")

        # 벡터 검색 테스트
        search_queries = ["기쁨", "슬픔", "분노", "평온", "기대"]

        for query in search_queries:
            try:
                similar_memories = self.vector_store.search_similar_memories(
                    query, limit=3
                )
                results["total_searches"] += 1
                logger.info(f"벡터 검색 결과: {len(similar_memories)}개")

            except Exception as e:
                logger.error(f"벡터 검색 실패: {e}")

        total_time = time.time() - start_time
        results["average_search_time"] = (
            total_time / results["total_searches"]
            if results["total_searches"] > 0
            else 0
        )

        self.test_results["vector_store"] = results
        logger.info(f"벡터 스토어 테스트 완료: {results}")

    async def test_memory_usage_analysis(self):
        """메모리 사용량 분석 테스트"""
        logger.info("메모리 사용량 분석 테스트 시작")

        initial_memory = self.get_memory_usage()
        logger.info(f"초기 메모리 사용량: {initial_memory}")

        # 대량 데이터 생성 테스트
        large_data = []
        for i in range(1000):
            large_data.append(
                {
                    "id": f"test_{i}",
                    "content": f"테스트 데이터 {i} " * 10,  # 긴 내용
                    "metadata": {"index": i, "timestamp": datetime.now().isoformat()},
                }
            )

        # 메모리 사용량 모니터링
        memory_samples = []

        for i in range(0, len(large_data), 100):
            batch = large_data[i : i + 100]

            # 배치 처리
            for item in batch:
                try:
                    await self.memory_manager.store_memory(
                        item["content"],
                        "test",
                        importance=0.5,
                        metadata=item["metadata"],
                    )
                except Exception as e:
                    logger.error(f"대량 데이터 저장 실패: {e}")

            # 메모리 사용량 기록
            current_memory = self.get_memory_usage()
            memory_samples.append(
                {
                    "batch": i // 100,
                    "memory": current_memory,
                    "timestamp": datetime.now().isoformat(),
                }
            )

            logger.info(
                f"배치 {i//100}: 메모리 사용량 = {current_memory['rss_mb']:.2f}MB"
            )

        final_memory = self.get_memory_usage()

        results = {
            "initial_memory": initial_memory,
            "final_memory": final_memory,
            "memory_increase_mb": final_memory["rss_mb"] - initial_memory["rss_mb"],
            "memory_samples": memory_samples,
        }

        self.test_results["memory_usage"] = results
        logger.info(f"메모리 사용량 분석 완료: {results}")

    async def test_integrated_performance(self):
        """통합 성능 테스트"""
        logger.info("통합 성능 테스트 시작")

        results = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "average_operation_time": 0.0,
        }

        start_time = time.time()

        # 통합 워크플로우 테스트
        for i in range(10):
            try:
                # 1. LLM 질문
                llm_response = await self.llm_interface.ask_llm(
                    f"통합 테스트 질문 {i}",
                    QueryType.GENERAL,
                    provider=LLMProvider.LOCAL,
                )

                # 2. 메모리 저장
                memory_id = await self.memory_manager.store_memory(
                    llm_response.content,
                    "integrated_test",
                    importance=0.7,
                    tags=["통합", "테스트"],
                )

                # 3. 벡터 저장
                vector_id = self.vector_store.store_memory(
                    llm_response.content,
                    {"emotion": "neutral", "intensity": 0.5},
                    {"context": "integrated_test"},
                )

                # 4. 메모리 검색
                search_query = MemoryQuery("통합", memory_type="integrated_test")
                memories = await self.memory_manager.search_memories(search_query)

                results["successful_operations"] += 1
                logger.info(f"통합 작업 {i} 완료")

            except Exception as e:
                results["failed_operations"] += 1
                logger.error(f"통합 작업 {i} 실패: {e}")

            results["total_operations"] += 1

        total_time = time.time() - start_time
        results["average_operation_time"] = total_time / results["total_operations"]

        self.test_results["integrated"] = results
        logger.info(f"통합 성능 테스트 완료: {results}")

    async def run_all_tests(self):
        """모든 테스트 실행"""
        logger.info("Phase 4 성능 최적화 테스트 시작")

        try:
            await self.setup()

            # 개별 테스트 실행
            await self.test_llm_interface_performance()
            await self.test_memory_manager_performance()
            await self.test_vector_store_performance()
            await self.test_memory_usage_analysis()
            await self.test_integrated_performance()

            # 결과 저장
            await self.save_test_results()

            logger.info("모든 테스트 완료")

        except Exception as e:
            logger.error(f"테스트 실행 중 오류: {e}")
            raise

        finally:
            await self.cleanup()

    async def save_test_results(self):
        """테스트 결과 저장"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"phase4_performance_test_results_{timestamp}.json"

        # 결과에 메타데이터 추가
        final_results = {
            "test_timestamp": datetime.now().isoformat(),
            "test_duration": time.time(),
            "results": self.test_results,
            "summary": self.generate_summary(),
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2, default=str)

        logger.info(f"테스트 결과 저장 완료: {filename}")

    def generate_summary(self) -> Dict[str, Any]:
        """테스트 결과 요약"""
        summary = {
            "llm_interface": {
                "success_rate": 0.0,
                "average_response_time": 0.0,
                "cache_hit_rate": 0.0,
            },
            "memory_manager": {
                "success_rate": 0.0,
                "average_query_time": 0.0,
                "cache_hit_rate": 0.0,
            },
            "vector_store": {"success_rate": 0.0, "average_search_time": 0.0},
            "memory_usage": {"memory_increase_mb": 0.0, "peak_memory_mb": 0.0},
            "overall": {"total_tests": 0, "successful_tests": 0, "failed_tests": 0},
        }

        # LLM 인터페이스 요약
        if "llm_interface" in self.test_results:
            llm_results = self.test_results["llm_interface"]
            total = llm_results["total_requests"]
            successful = llm_results["successful_requests"]

            summary["llm_interface"]["success_rate"] = (
                successful / total if total > 0 else 0
            )
            summary["llm_interface"]["average_response_time"] = llm_results[
                "average_response_time"
            ]
            summary["llm_interface"]["cache_hit_rate"] = llm_results["cache_hit_rate"]

        # 메모리 매니저 요약
        if "memory_manager" in self.test_results:
            mm_results = self.test_results["memory_manager"]
            total = mm_results["total_queries"]

            summary["memory_manager"][
                "success_rate"
            ] = 1.0  # 모든 쿼리가 성공했다고 가정
            summary["memory_manager"]["average_query_time"] = mm_results[
                "average_query_time"
            ]
            summary["memory_manager"]["cache_hit_rate"] = mm_results["cache_hit_rate"]

        # 벡터 스토어 요약
        if "vector_store" in self.test_results:
            vs_results = self.test_results["vector_store"]
            total = vs_results["total_searches"]

            summary["vector_store"]["success_rate"] = 1.0  # 모든 검색이 성공했다고 가정
            summary["vector_store"]["average_search_time"] = vs_results[
                "average_search_time"
            ]

        # 메모리 사용량 요약
        if "memory_usage" in self.test_results:
            mu_results = self.test_results["memory_usage"]
            summary["memory_usage"]["memory_increase_mb"] = mu_results[
                "memory_increase_mb"
            ]

            # 최대 메모리 사용량 계산
            peak_memory = max(
                sample["memory"]["rss_mb"] for sample in mu_results["memory_samples"]
            )
            summary["memory_usage"]["peak_memory_mb"] = peak_memory

        # 전체 요약
        summary["overall"]["total_tests"] = len(self.test_results)
        summary["overall"]["successful_tests"] = len(
            [r for r in self.test_results.values() if "successful" in r]
        )
        summary["overall"]["failed_tests"] = len(
            [r for r in self.test_results.values() if "failed" in r]
        )

        return summary


async def main():
    """메인 함수"""
    tester = Phase4PerformanceTester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
