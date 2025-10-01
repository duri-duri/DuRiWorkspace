#!/usr/bin/env python3
"""
DuRiCore - 비동기 LLM 인터페이스 최적화
Phase 4: 성능 최적화를 위한 aiohttp 기반 LLM 호출 시스템
"""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional, Union

import aiohttp

logger = logging.getLogger(__name__)


class LLMProvider(Enum):
    """LLM 제공자"""

    CHATGPT = "chatgpt"
    CLAUDE = "claude"
    GEMINI = "gemini"
    LOCAL = "local"


class QueryType(Enum):
    """쿼리 타입"""

    EMOTION_ANALYSIS = "emotion_analysis"
    LEARNING_QUERY = "learning_query"
    ETHICAL_JUDGMENT = "ethical_judgment"
    EVOLUTION_QUERY = "evolution_query"
    GENERAL = "general"


@dataclass
class LLMRequest:
    """LLM 요청"""

    id: str
    provider: LLMProvider
    query_type: QueryType
    prompt: str
    context: Dict[str, Any]
    timestamp: datetime
    priority: int = 1  # 1-5, 높을수록 우선순위 높음


@dataclass
class LLMResponse:
    """LLM 응답"""

    id: str
    request_id: str
    content: str
    provider: LLMProvider
    processing_time: float
    token_count: int
    confidence_score: float
    quality_score: float
    timestamp: datetime
    metadata: Dict[str, Any]


class AsyncLLMInterface:
    """비동기 LLM 인터페이스"""

    def __init__(self, max_concurrent_requests: int = 10):
        self.max_concurrent_requests = max_concurrent_requests
        self.semaphore = asyncio.Semaphore(max_concurrent_requests)
        self.session: Optional[aiohttp.ClientSession] = None
        self.request_queue: asyncio.Queue = asyncio.Queue()
        self.response_cache: Dict[str, LLMResponse] = {}
        self.provider_configs: Dict[LLMProvider, Dict[str, Any]] = {}
        self.request_history: List[LLMRequest] = []
        self.response_history: List[LLMResponse] = []

        # 성능 통계
        self.stats = {
            "total_requests": 0,
            "total_responses": 0,
            "cache_hits": 0,
            "average_response_time": 0.0,
            "error_count": 0,
        }

        self._initialize_providers()
        logger.info("비동기 LLM 인터페이스 초기화 완료")

    def _initialize_providers(self):
        """LLM 제공자 설정 초기화"""
        # ChatGPT 설정
        self.provider_configs[LLMProvider.CHATGPT] = {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "model": "gpt-4",
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 30,
            "retry_count": 3,
        }

        # Claude 설정
        self.provider_configs[LLMProvider.CLAUDE] = {
            "api_url": "https://api.anthropic.com/v1/messages",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 30,
            "retry_count": 3,
        }

        # Gemini 설정
        self.provider_configs[LLMProvider.GEMINI] = {
            "api_url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
            "api_key": os.getenv("GOOGLE_API_KEY"),
            "model": "gemini-pro",
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 30,
            "retry_count": 3,
        }

        # 로컬 모델 설정 (시뮬레이션)
        self.provider_configs[LLMProvider.LOCAL] = {
            "api_url": "http://localhost:8000/generate",
            "api_key": None,
            "model": "local-simulation",
            "max_tokens": 1000,
            "temperature": 0.7,
            "timeout": 5,
            "retry_count": 1,
        }

    async def start(self):
        """인터페이스 시작"""
        self.session = aiohttp.ClientSession()
        logger.info("LLM 인터페이스 세션 시작")

    async def stop(self):
        """인터페이스 종료"""
        if self.session:
            await self.session.close()
        logger.info("LLM 인터페이스 세션 종료")

    async def ask_llm(
        self,
        prompt: str,
        query_type: QueryType,
        context: Dict[str, Any] = None,
        provider: LLMProvider = LLMProvider.CHATGPT,
        priority: int = 1,
    ) -> LLMResponse:
        """LLM에 질문 (비동기)"""
        try:
            # 캐시 확인
            cache_key = self._generate_cache_key(prompt, query_type, context, provider)
            if cache_key in self.response_cache:
                self.stats["cache_hits"] += 1
                logger.info(f"캐시 히트: {cache_key}")
                return self.response_cache[cache_key]

            # 요청 생성
            request_id = f"req_{int(time.time() * 1000)}_{hashlib.md5(prompt.encode()).hexdigest()[:8]}"

            llm_request = LLMRequest(
                id=request_id,
                provider=provider,
                query_type=query_type,
                prompt=prompt,
                context=context or {},
                timestamp=datetime.now(),
                priority=priority,
            )

            self.request_history.append(llm_request)
            self.stats["total_requests"] += 1

            # 세마포어로 동시 요청 제한
            async with self.semaphore:
                start_time = time.time()

                # 실제 LLM 호출
                response = await self._call_llm_provider(llm_request)

                processing_time = time.time() - start_time
                response.processing_time = processing_time

                # 응답 품질 평가
                response.quality_score = self._evaluate_response_quality(
                    response.content, query_type
                )
                response.confidence_score = self._calculate_confidence_score(
                    response.content, query_type
                )

                # 캐시에 저장
                self.response_cache[cache_key] = response

                # 통계 업데이트
                self._update_stats(processing_time)

                self.response_history.append(response)
                self.stats["total_responses"] += 1

                logger.info(
                    f"LLM 응답 완료: {request_id} (처리시간: {processing_time:.2f}s)"
                )
                return response

        except Exception as e:
            self.stats["error_count"] += 1
            logger.error(f"LLM 요청 오류: {e}")
            raise

    async def _call_llm_provider(self, request: LLMRequest) -> LLMResponse:
        """LLM 제공자 호출"""
        config = self.provider_configs[request.provider]

        if request.provider == LLMProvider.CHATGPT:
            return await self._call_chatgpt(request, config)
        elif request.provider == LLMProvider.CLAUDE:
            return await self._call_claude(request, config)
        elif request.provider == LLMProvider.GEMINI:
            return await self._call_gemini(request, config)
        elif request.provider == LLMProvider.LOCAL:
            return await self._call_local_simulation(request, config)
        else:
            raise ValueError(f"지원하지 않는 LLM 제공자: {request.provider}")

    async def _call_chatgpt(
        self, request: LLMRequest, config: Dict[str, Any]
    ) -> LLMResponse:
        """ChatGPT API 호출"""
        headers = {
            "Authorization": f'Bearer {config["api_key"]}',
            "Content-Type": "application/json",
        }

        payload = {
            "model": config["model"],
            "messages": [
                {
                    "role": "system",
                    "content": self._create_system_prompt(request.query_type),
                },
                {"role": "user", "content": request.prompt},
            ],
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
        }

        async with self.session.post(
            config["api_url"],
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=config["timeout"]),
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data["choices"][0]["message"]["content"]
                token_count = data["usage"]["total_tokens"]

                return LLMResponse(
                    id=f"resp_{request.id}",
                    request_id=request.id,
                    content=content,
                    provider=request.provider,
                    processing_time=0.0,  # 나중에 설정
                    token_count=token_count,
                    confidence_score=0.0,  # 나중에 계산
                    quality_score=0.0,  # 나중에 계산
                    timestamp=datetime.now(),
                    metadata={"usage": data["usage"]},
                )
            else:
                raise Exception(f"ChatGPT API 오류: {response.status}")

    async def _call_claude(
        self, request: LLMRequest, config: Dict[str, Any]
    ) -> LLMResponse:
        """Claude API 호출"""
        headers = {
            "x-api-key": config["api_key"],
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        payload = {
            "model": config["model"],
            "max_tokens": config["max_tokens"],
            "temperature": config["temperature"],
            "messages": [{"role": "user", "content": request.prompt}],
        }

        async with self.session.post(
            config["api_url"],
            headers=headers,
            json=payload,
            timeout=aiohttp.ClientTimeout(total=config["timeout"]),
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data["content"][0]["text"]

                return LLMResponse(
                    id=f"resp_{request.id}",
                    request_id=request.id,
                    content=content,
                    provider=request.provider,
                    processing_time=0.0,
                    token_count=0,  # Claude는 토큰 수를 제공하지 않음
                    confidence_score=0.0,
                    quality_score=0.0,
                    timestamp=datetime.now(),
                    metadata={
                        "input_tokens": data.get("usage", {}).get("input_tokens", 0)
                    },
                )
            else:
                raise Exception(f"Claude API 오류: {response.status}")

    async def _call_gemini(
        self, request: LLMRequest, config: Dict[str, Any]
    ) -> LLMResponse:
        """Gemini API 호출"""
        url = f"{config['api_url']}?key={config['api_key']}"

        payload = {
            "contents": [{"parts": [{"text": request.prompt}]}],
            "generationConfig": {
                "maxOutputTokens": config["max_tokens"],
                "temperature": config["temperature"],
            },
        }

        async with self.session.post(
            url, json=payload, timeout=aiohttp.ClientTimeout(total=config["timeout"])
        ) as response:
            if response.status == 200:
                data = await response.json()
                content = data["candidates"][0]["content"]["parts"][0]["text"]

                return LLMResponse(
                    id=f"resp_{request.id}",
                    request_id=request.id,
                    content=content,
                    provider=request.provider,
                    processing_time=0.0,
                    token_count=0,
                    confidence_score=0.0,
                    quality_score=0.0,
                    timestamp=datetime.now(),
                    metadata={"usageMetadata": data.get("usageMetadata", {})},
                )
            else:
                raise Exception(f"Gemini API 오류: {response.status}")

    async def _call_local_simulation(
        self, request: LLMRequest, config: Dict[str, Any]
    ) -> LLMResponse:
        """로컬 시뮬레이션 (테스트용)"""
        # 실제 API 호출 대신 시뮬레이션
        await asyncio.sleep(0.1)  # 네트워크 지연 시뮬레이션

        # 쿼리 타입별 시뮬레이션 응답
        simulation_responses = {
            QueryType.EMOTION_ANALYSIS: "이 상황에서 감정 상태는 평온함과 약간의 기대감이 섞여 있습니다.",
            QueryType.LEARNING_QUERY: "이 경험을 통해 새로운 패턴을 학습했습니다. 향후 유사한 상황에 적용할 수 있습니다.",
            QueryType.ETHICAL_JUDGMENT: "이 행동은 윤리적으로 적절하며, 타인에게 해를 끼치지 않습니다.",
            QueryType.EVOLUTION_QUERY: "이 경험을 통해 자기 진화의 새로운 단계로 나아갈 수 있습니다.",
            QueryType.GENERAL: "일반적인 질문에 대한 응답입니다.",
        }

        content = simulation_responses.get(request.query_type, "시뮬레이션 응답입니다.")

        return LLMResponse(
            id=f"resp_{request.id}",
            request_id=request.id,
            content=content,
            provider=request.provider,
            processing_time=0.0,
            token_count=len(content.split()),
            confidence_score=0.8,
            quality_score=0.7,
            timestamp=datetime.now(),
            metadata={"simulation": True},
        )

    def _create_system_prompt(self, query_type: QueryType) -> str:
        """시스템 프롬프트 생성"""
        prompts = {
            QueryType.EMOTION_ANALYSIS: "당신은 감정 분석 전문가입니다. 주어진 상황의 감정 상태를 정확히 분석해주세요.",
            QueryType.LEARNING_QUERY: "당신은 학습 시스템입니다. 새로운 지식과 경험을 체계적으로 학습하고 정리해주세요.",
            QueryType.ETHICAL_JUDGMENT: "당신은 윤리 판단 시스템입니다. 주어진 상황의 윤리적 측면을 분석해주세요.",
            QueryType.EVOLUTION_QUERY: "당신은 자기 진화 시스템입니다. 개인의 성장과 발전을 도모하는 조언을 해주세요.",
            QueryType.GENERAL: "당신은 도움이 되는 AI 어시스턴트입니다.",
        }
        return prompts.get(query_type, "당신은 도움이 되는 AI 어시스턴트입니다.")

    def _generate_cache_key(
        self,
        prompt: str,
        query_type: QueryType,
        context: Dict[str, Any],
        provider: LLMProvider,
    ) -> str:
        """캐시 키 생성"""
        content = f"{prompt}_{query_type.value}_{provider.value}_{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()

    def _evaluate_response_quality(self, content: str, query_type: QueryType) -> float:
        """응답 품질 평가"""
        # 간단한 품질 평가 (실제로는 더 정교한 평가 필요)
        if len(content) < 10:
            return 0.3
        elif len(content) < 50:
            return 0.6
        else:
            return 0.8

    def _calculate_confidence_score(self, content: str, query_type: QueryType) -> float:
        """신뢰도 점수 계산"""
        # 간단한 신뢰도 계산 (실제로는 더 정교한 계산 필요)
        if "확실" in content or "분명" in content:
            return 0.9
        elif "아마" in content or "어쩌면" in content:
            return 0.6
        else:
            return 0.7

    def _update_stats(self, processing_time: float):
        """통계 업데이트"""
        if self.stats["total_responses"] > 0:
            current_avg = self.stats["average_response_time"]
            new_count = self.stats["total_responses"]
            self.stats["average_response_time"] = (
                current_avg * (new_count - 1) + processing_time
            ) / new_count

    def get_performance_stats(self) -> Dict[str, Any]:
        """성능 통계 반환"""
        return {
            **self.stats,
            "cache_hit_rate": self.stats["cache_hits"]
            / max(self.stats["total_requests"], 1),
            "error_rate": self.stats["error_count"]
            / max(self.stats["total_requests"], 1),
            "active_requests": self.semaphore._value,
            "queue_size": (
                self.request_queue.qsize()
                if hasattr(self.request_queue, "qsize")
                else 0
            ),
        }

    def clear_cache(self):
        """캐시 클리어"""
        self.response_cache.clear()
        logger.info("LLM 응답 캐시 클리어 완료")

    async def batch_request(self, requests: List[LLMRequest]) -> List[LLMResponse]:
        """배치 요청 처리"""
        tasks = [
            self.ask_llm(
                req.prompt, req.query_type, req.context, req.provider, req.priority
            )
            for req in requests
        ]

        return await asyncio.gather(*tasks, return_exceptions=True)
