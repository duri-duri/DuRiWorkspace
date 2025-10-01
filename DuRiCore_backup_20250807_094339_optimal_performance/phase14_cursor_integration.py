#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase 14: 커서 판단 루프에 통합

Phase 13에서 구현된 reasoning + learning 통합 시스템을
커서 판단 루프에 통합하여 실시간 응답 시스템 구축

주요 기능:
1. 커서 인터페이스 통합
2. 실시간 사용자 입력 처리
3. reasoning + learning 기반 응답 생성
4. 대화 컨텍스트 관리 및 상태 동기화
5. 커서 환경에서의 성능 최적화
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# Phase 13 시스템 import
try:
    from phase13_reasoning_learning_integration import (
        IntegrationContext,
        IntegrationPhase,
        IntegrationResult,
        IntegrationStatus,
        ReasoningLearningIntegrationSystem,
    )
except ImportError as e:
    logging.warning(f"Phase 13 시스템 import 실패: {e}")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CursorPhase(Enum):
    """커서 단계"""

    INITIALIZATION = "initialization"
    INPUT_PROCESSING = "input_processing"
    REASONING_LEARNING = "reasoning_learning"
    RESPONSE_GENERATION = "response_generation"
    CONTEXT_UPDATE = "context_update"
    COMPLETION = "completion"


class CursorStatus(Enum):
    """커서 상태"""

    IDLE = "idle"
    PROCESSING = "processing"
    RESPONDING = "responding"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class CursorContext:
    """커서 컨텍스트"""

    session_id: str
    user_id: str
    phase: CursorPhase
    status: CursorStatus
    start_time: datetime
    end_time: Optional[datetime] = None
    user_input: Optional[str] = None
    system_response: Optional[str] = None
    reasoning_result: Optional[Dict[str, Any]] = None
    learning_result: Optional[Dict[str, Any]] = None
    context_data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CursorResult:
    """커서 결과"""

    session_id: str
    success: bool
    response: str
    reasoning_quality: float
    learning_effectiveness: float
    response_time: float
    context_accuracy: float
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextManager:
    """컨텍스트 관리자"""

    def __init__(self):
        self.contexts: Dict[str, CursorContext] = {}
        self.max_contexts = 1000

    async def create_context(self, session_id: str, user_id: str) -> CursorContext:
        """새로운 컨텍스트 생성"""
        context = CursorContext(
            session_id=session_id,
            user_id=user_id,
            phase=CursorPhase.INITIALIZATION,
            status=CursorStatus.IDLE,
            start_time=datetime.now(),
        )
        self.contexts[session_id] = context
        return context

    async def get_context(self, session_id: str) -> Optional[CursorContext]:
        """컨텍스트 조회"""
        return self.contexts.get(session_id)

    async def update_context(self, session_id: str, **kwargs) -> bool:
        """컨텍스트 업데이트"""
        if session_id in self.contexts:
            context = self.contexts[session_id]
            for key, value in kwargs.items():
                if hasattr(context, key):
                    setattr(context, key, value)
            return True
        return False

    async def cleanup_old_contexts(self):
        """오래된 컨텍스트 정리"""
        current_time = datetime.now()
        expired_sessions = []

        for session_id, context in self.contexts.items():
            if (current_time - context.start_time).total_seconds() > 3600:  # 1시간
                expired_sessions.append(session_id)

        for session_id in expired_sessions:
            del self.contexts[session_id]


class ResponseGenerator:
    """응답 생성기"""

    def __init__(self):
        self.response_templates = {
            "success": "✅ {message}",
            "error": "❌ {message}",
            "processing": "🔄 {message}",
            "info": "ℹ️ {message}",
        }

    async def generate_response(
        self,
        reasoning_result: Dict[str, Any],
        learning_result: Dict[str, Any],
        context: CursorContext,
    ) -> str:
        """응답 생성"""
        try:
            # reasoning 결과 분석
            reasoning_quality = reasoning_result.get("quality", 0.0)
            reasoning_insights = reasoning_result.get("insights", [])

            # learning 결과 분석
            learning_effectiveness = learning_result.get("effectiveness", 0.0)
            learning_improvements = learning_result.get("improvements", [])

            # 응답 구성
            response_parts = []

            # 주요 인사이트 추가
            if reasoning_insights:
                response_parts.append(
                    f"💡 **주요 인사이트**: {', '.join(reasoning_insights[:3])}"
                )

            # 개선사항 추가
            if learning_improvements:
                response_parts.append(
                    f"🚀 **개선사항**: {', '.join(learning_improvements[:2])}"
                )

            # 품질 지표 추가
            response_parts.append(
                f"📊 **품질 지표**: Reasoning {reasoning_quality:.1%}, Learning {learning_effectiveness:.1%}"
            )

            # 최종 응답 생성
            response = "\n\n".join(response_parts) if response_parts else "✅ 처리 완료"

            return response

        except Exception as e:
            logger.error(f"응답 생성 중 오류: {e}")
            return f"❌ 응답 생성 중 오류가 발생했습니다: {str(e)}"


class CursorIntegrationSystem:
    """커서 통합 시스템"""

    def __init__(self):
        self.reasoning_learning_system = ReasoningLearningIntegrationSystem()
        self.context_manager = ContextManager()
        self.response_generator = ResponseGenerator()

        self.cursor_config = {
            "enable_real_time_processing": True,
            "enable_context_management": True,
            "enable_response_generation": True,
            "max_response_time": 5.0,  # 5초
            "context_cleanup_interval": 3600,  # 1시간
        }

        # 성능 메트릭
        self.performance_metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "average_response_time": 0.0,
            "error_count": 0,
        }

    async def initialize(self):
        """시스템 초기화"""
        try:
            # Phase 13 시스템 초기화
            await self.reasoning_learning_system.initialize_systems()

            # 컨텍스트 관리자 초기화
            await self.context_manager.cleanup_old_contexts()

            logger.info("커서 통합 시스템 초기화 완료")
            return True

        except Exception as e:
            logger.error(f"커서 통합 시스템 초기화 실패: {e}")
            return False

    async def process_user_input(
        self, user_input: str, session_id: str, user_id: str = "default"
    ) -> CursorResult:
        """사용자 입력 처리"""
        start_time = time.time()

        try:
            # 1. 컨텍스트 생성/조회
            context = await self.context_manager.get_context(session_id)
            if not context:
                context = await self.context_manager.create_context(session_id, user_id)

            # 2. 컨텍스트 업데이트
            await self.context_manager.update_context(
                session_id,
                phase=CursorPhase.INPUT_PROCESSING,
                status=CursorStatus.PROCESSING,
                user_input=user_input,
            )

            # 3. reasoning + learning 통합 실행
            integration_result = await self._execute_reasoning_learning(
                user_input, context
            )

            # 4. 응답 생성
            response = await self.response_generator.generate_response(
                integration_result.get("reasoning_result", {}),
                integration_result.get("learning_result", {}),
                context,
            )

            # 5. 컨텍스트 업데이트
            await self.context_manager.update_context(
                session_id,
                phase=CursorPhase.COMPLETION,
                status=CursorStatus.COMPLETED,
                system_response=response,
                reasoning_result=integration_result.get("reasoning_result"),
                learning_result=integration_result.get("learning_result"),
                end_time=datetime.now(),
            )

            # 6. 성능 메트릭 업데이트
            response_time = time.time() - start_time
            self._update_performance_metrics(True, response_time)

            return CursorResult(
                session_id=session_id,
                success=True,
                response=response,
                reasoning_quality=integration_result.get("reasoning_quality", 0.0),
                learning_effectiveness=integration_result.get(
                    "learning_effectiveness", 0.0
                ),
                response_time=response_time,
                context_accuracy=0.85,  # 기본값
                metadata=integration_result.get("metadata", {}),
            )

        except Exception as e:
            logger.error(f"사용자 입력 처리 중 오류: {e}")

            # 성능 메트릭 업데이트
            response_time = time.time() - start_time
            self._update_performance_metrics(False, response_time)

            return CursorResult(
                session_id=session_id,
                success=False,
                response=f"❌ 처리 중 오류가 발생했습니다: {str(e)}",
                reasoning_quality=0.0,
                learning_effectiveness=0.0,
                response_time=response_time,
                context_accuracy=0.0,
                error_message=str(e),
            )

    async def _execute_reasoning_learning(
        self, user_input: str, context: CursorContext
    ) -> Dict[str, Any]:
        """reasoning + learning 통합 실행"""
        try:
            # Phase 13 시스템을 사용하여 통합 실행
            input_data = {
                "user_input": user_input,
                "session_id": context.session_id,
                "user_id": context.user_id,
                "timestamp": datetime.now().isoformat(),
            }

            integration_result = (
                await self.reasoning_learning_system.execute_integration_flow(
                    input_data=input_data, context=context.context_data
                )
            )

            return {
                "reasoning_result": integration_result.reasoning_result,
                "learning_result": integration_result.learning_result,
                "reasoning_quality": integration_result.reasoning_quality,
                "learning_effectiveness": integration_result.learning_effectiveness,
                "integration_score": integration_result.integration_score,
                "metadata": integration_result.metadata,
            }

        except Exception as e:
            logger.error(f"reasoning + learning 통합 실행 중 오류: {e}")
            return {
                "reasoning_result": {},
                "learning_result": {},
                "reasoning_quality": 0.0,
                "learning_effectiveness": 0.0,
                "integration_score": 0.0,
                "metadata": {"error": str(e)},
            }

    def _update_performance_metrics(self, success: bool, response_time: float):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_requests"] += 1

        if success:
            self.performance_metrics["successful_requests"] += 1
        else:
            self.performance_metrics["error_count"] += 1

        # 평균 응답 시간 업데이트
        total_requests = self.performance_metrics["total_requests"]
        current_avg = self.performance_metrics["average_response_time"]
        self.performance_metrics["average_response_time"] = (
            current_avg * (total_requests - 1) + response_time
        ) / total_requests

    async def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics.copy()

    async def get_context(self, session_id: str) -> Optional[CursorContext]:
        """컨텍스트 조회"""
        return await self.context_manager.get_context(session_id)

    async def cleanup_contexts(self):
        """컨텍스트 정리"""
        await self.context_manager.cleanup_old_contexts()


# 테스트 함수
async def test_cursor_integration():
    """커서 통합 시스템 테스트"""
    print("🧪 커서 통합 시스템 테스트 시작")

    # 시스템 초기화
    cursor_system = CursorIntegrationSystem()
    success = await cursor_system.initialize()

    if not success:
        print("❌ 시스템 초기화 실패")
        return

    print("✅ 시스템 초기화 성공")

    # 테스트 입력 처리
    test_inputs = [
        "안녕하세요! 오늘 날씨는 어떤가요?",
        "Python으로 웹 애플리케이션을 만들고 싶어요.",
        "머신러닝 모델의 성능을 개선하는 방법을 알려주세요.",
    ]

    for i, test_input in enumerate(test_inputs, 1):
        print(f"\n📝 테스트 {i}: {test_input}")

        result = await cursor_system.process_user_input(
            user_input=test_input, session_id=f"test_session_{i}", user_id="test_user"
        )

        if result.success:
            print(f"✅ 성공 - 응답 시간: {result.response_time:.3f}초")
            print(
                f"📊 품질 지표: Reasoning {result.reasoning_quality:.1%}, Learning {result.learning_effectiveness:.1%}"
            )
            print(f"💬 응답: {result.response[:200]}...")
        else:
            print(f"❌ 실패: {result.error_message}")

    # 성능 메트릭 출력
    metrics = await cursor_system.get_performance_metrics()
    print(f"\n📊 성능 메트릭:")
    print(f"   총 요청: {metrics['total_requests']}")
    print(
        f"   성공률: {metrics['successful_requests']/metrics['total_requests']*100:.1f}%"
    )
    print(f"   평균 응답 시간: {metrics['average_response_time']:.3f}초")
    print(f"   오류 수: {metrics['error_count']}")

    print("\n🎯 커서 통합 시스템 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(test_cursor_integration())
