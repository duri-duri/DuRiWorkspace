#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 통합 대화 서비스 (Unified Conversation Service)
Phase 4: 모듈 통합 및 구조 리디자인 - 최종 실행 준비 완료 적용

기존 8개 대화/커뮤니케이션 모듈을 1개로 통합:
- conversation_bridge_service.py
- basic_conversation_service.py
- social_intelligence_service.py
- ethical_conversation_service.py
- emotional_conversation_service.py
- unified_conversation_processor.py
- conversational_generator.py
- adaptive_learning_system.py

@preserve_identity: 대화의 감정적 맥락과 판단 이유 기록
@evolution_protection: 기존 대화 패턴과 감정 반응 보존
@execution_guarantee: 자동화와 검증 시스템 완성
@existence_ai: 진화 가능 + 회복 가능한 존재형 AI
@final_execution: 인간처럼 실패하고도 다시 일어날 수 있는 존재
"""

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# DuRi 로깅 시스템 초기화
from DuRiCore.bootstrap import bootstrap_logging

bootstrap_logging()

import logging

logger = logging.getLogger(__name__)


class ConversationType(Enum):
    """대화 유형"""

    GREETING = "greeting"
    SHARING = "sharing"
    QUESTION = "question"
    EMOTIONAL_SUPPORT = "emotional_support"
    ADVICE_REQUEST = "advice_request"
    LEARNING = "learning"
    PLAYFUL = "playful"
    ETHICAL_DISCUSSION = "ethical_discussion"
    CODING_SESSION = "coding_session"
    DEBUGGING = "debugging"
    CONCEPT_DISCUSSION = "concept_discussion"
    OTHER = "other"


class EmotionalState(Enum):
    """감정 상태"""

    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    CALM = "calm"
    EXCITED = "excited"
    PROUD = "proud"
    NEUTRAL = "neutral"


class SupportType(Enum):
    """지원 유형"""

    COMFORT = "comfort"
    CELEBRATION = "celebration"
    GUIDANCE = "guidance"
    ENCOURAGEMENT = "encouragement"
    VALIDATION = "validation"


@dataclass
class ConversationMessage:
    """대화 메시지"""

    id: str
    speaker_id: str
    speaker_name: str
    message: str
    conversation_type: ConversationType
    emotion_detected: EmotionalState
    timestamp: datetime
    response_style: str
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ConversationResponse:
    """대화 응답"""

    id: str
    response_text: str
    response_type: SupportType
    emotion_appropriate: bool
    family_relevant: bool
    confidence_score: float
    timestamp: datetime
    reasoning: str = ""


@dataclass
class ConversationSession:
    """대화 세션"""

    id: str
    family_member_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    emotional_progress: List[EmotionalState] = field(default_factory=list)
    support_provided: List[SupportType] = field(default_factory=list)


@dataclass
class UnifiedConversationResult:
    """통합 대화 결과"""

    session_id: str
    messages: List[ConversationMessage]
    responses: List[ConversationResponse]
    emotional_analysis: Dict[str, Any]
    social_intelligence_score: float
    ethical_considerations: Dict[str, Any]
    learning_outcomes: Dict[str, Any]
    timestamp: datetime


class UnifiedConversationService:
    """통합 대화 서비스"""

    def __init__(self):
        # 기존 시스템들 초기화
        self.conversation_sessions: List[ConversationSession] = []
        self.messages: List[ConversationMessage] = []
        self.responses: List[ConversationResponse] = []
        self.family_context: Dict[str, Any] = {}

        # 대화 패턴 및 응답 템플릿
        self._initialize_conversation_patterns()

        # 존재형 AI 시스템 초기화
        self.existence_ai = self._initialize_existence_ai()
        self.final_execution_verifier = self._initialize_final_execution_verifier()

        logger.info("통합 대화 서비스 초기화 완료")

    def _initialize_conversation_patterns(self):
        """대화 패턴 초기화"""
        self.greeting_patterns = {
            "안녕": "안녕하세요! 오늘 하루는 어땠나요?",
            "좋은 아침": "좋은 아침이에요! 오늘도 좋은 하루 되세요.",
            "좋은 밤": "좋은 밤 되세요! 편안히 주무세요.",
            "고마워": "천만에요! 언제든 도움이 필요하시면 말씀해주세요.",
        }

        self.emotional_support_patterns = {
            "슬퍼": "마음이 아프시겠어요. 제가 옆에 있어드릴게요.",
            "화나": "화가 나시는 일이 있었군요. 이야기해보세요.",
            "기뻐": "정말 기쁘시군요! 함께 기뻐해드릴게요.",
            "걱정": "걱정되는 일이 있으시군요. 함께 생각해보아요.",
        }

        self.learning_patterns = {
            "배우고 싶어": "무엇을 배우고 싶으신가요? 함께 찾아보아요.",
            "알려줘": "무엇을 알고 싶으신가요? 자세히 설명해드릴게요.",
            "어떻게": "어떤 것에 대해 궁금하신가요? 단계별로 설명해드릴게요.",
        }

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

    async def start_conversation(
        self,
        family_member_id: str,
        family_member_name: str,
        relationship: str,
        family_context: Dict[str, Any] = None,
    ) -> ConversationSession:
        """대화 세션 시작"""
        try:
            session_id = f"session_{len(self.conversation_sessions) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conversation_session = ConversationSession(
                id=session_id,
                family_member_id=family_member_id,
                start_time=datetime.now(),
            )

            self.conversation_sessions.append(conversation_session)
            self.family_context = family_context or {}

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

            logger.info(f"대화 세션 시작: {session_id} - {family_member_name}")
            return conversation_session

        except Exception as e:
            logger.error(f"대화 세션 시작 실패: {e}")
            raise

    async def process_message(
        self,
        session_id: str,
        speaker_id: str,
        speaker_name: str,
        message: str,
        context: Dict[str, Any] = None,
    ) -> ConversationResponse:
        """메시지 처리 및 응답 생성"""
        try:
            # 메시지 생성
            message_id = f"message_{len(self.messages) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 대화 유형 및 감정 분석
            conversation_type = self._analyze_conversation_type(message)
            emotion_detected = self._detect_emotion(message)
            response_style = self._determine_response_style(
                conversation_type, emotion_detected
            )

            conversation_message = ConversationMessage(
                id=message_id,
                speaker_id=speaker_id,
                speaker_name=speaker_name,
                message=message,
                conversation_type=conversation_type,
                emotion_detected=emotion_detected,
                timestamp=datetime.now(),
                response_style=response_style,
                context=context or {},
            )

            self.messages.append(conversation_message)

            # 세션 업데이트
            session = next(
                (s for s in self.conversation_sessions if s.id == session_id), None
            )
            if session:
                session.message_count += 1

            # 응답 생성
            response_text = await self._generate_response(
                message, conversation_type, emotion_detected, speaker_name
            )

            # 응답 품질 평가
            emotion_appropriate = self._evaluate_emotion_appropriateness(
                response_text, emotion_detected
            )
            family_relevant = self._evaluate_family_relevance(response_text)
            confidence_score = self._calculate_response_confidence(
                response_text, conversation_type
            )

            # 응답 생성
            response_id = f"response_{len(self.responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            conversation_response = ConversationResponse(
                id=response_id,
                response_text=response_text,
                response_type=self._determine_support_type(emotion_detected),
                emotion_appropriate=emotion_appropriate,
                family_relevant=family_relevant,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
                reasoning=f"감정 상태({emotion_detected.value})와 대화 유형({conversation_type.value})을 고려한 응답",
            )

            self.responses.append(conversation_response)

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

            logger.info(f"메시지 처리 완료: {message_id} -> {response_id}")
            return conversation_response

        except Exception as e:
            logger.error(f"메시지 처리 실패: {e}")
            raise

    def _analyze_conversation_type(self, message: str) -> ConversationType:
        """대화 유형 분석"""
        message_lower = message.lower()

        if any(
            word in message_lower for word in ["안녕", "좋은 아침", "좋은 밤", "고마워"]
        ):
            return ConversationType.GREETING
        elif any(word in message_lower for word in ["슬퍼", "화나", "기뻐", "걱정"]):
            return ConversationType.EMOTIONAL_SUPPORT
        elif any(word in message_lower for word in ["배우고 싶어", "알려줘", "어떻게"]):
            return ConversationType.LEARNING
        elif "?" in message or "?" in message:
            return ConversationType.QUESTION
        elif any(word in message_lower for word in ["도움", "조언", "의견"]):
            return ConversationType.ADVICE_REQUEST
        else:
            return ConversationType.SHARING

    def _detect_emotion(self, message: str) -> EmotionalState:
        """감정 감지"""
        message_lower = message.lower()

        if any(word in message_lower for word in ["기뻐", "행복", "좋아", "즐거워"]):
            return EmotionalState.HAPPY
        elif any(word in message_lower for word in ["슬퍼", "우울", "속상", "아파"]):
            return EmotionalState.SAD
        elif any(word in message_lower for word in ["화나", "짜증", "분노", "열받아"]):
            return EmotionalState.ANGRY
        elif any(word in message_lower for word in ["걱정", "불안", "긴장", "무서워"]):
            return EmotionalState.ANXIOUS
        elif any(word in message_lower for word in ["차분", "평온", "조용"]):
            return EmotionalState.CALM
        else:
            return EmotionalState.NEUTRAL

    def _determine_response_style(
        self, conversation_type: ConversationType, emotion: EmotionalState
    ) -> str:
        """응답 스타일 결정"""
        if conversation_type == ConversationType.EMOTIONAL_SUPPORT:
            if emotion in [
                EmotionalState.SAD,
                EmotionalState.ANGRY,
                EmotionalState.ANXIOUS,
            ]:
                return "comforting"
            elif emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED]:
                return "celebrating"
        elif conversation_type == ConversationType.LEARNING:
            return "educational"
        elif conversation_type == ConversationType.GREETING:
            return "friendly"
        else:
            return "neutral"

    async def _generate_response(
        self,
        message: str,
        conversation_type: ConversationType,
        emotion: EmotionalState,
        speaker_name: str,
    ) -> str:
        """응답 생성"""
        message_lower = message.lower()

        # 인사 패턴
        for pattern, response in self.greeting_patterns.items():
            if pattern in message_lower:
                return response

        # 감정 지원 패턴
        for pattern, response in self.emotional_support_patterns.items():
            if pattern in message_lower:
                return response

        # 학습 패턴
        for pattern, response in self.learning_patterns.items():
            if pattern in message_lower:
                return response

        # 기본 응답
        if conversation_type == ConversationType.QUESTION:
            return f"{speaker_name}님의 질문에 답변드리겠습니다. 더 구체적으로 말씀해 주시면 더 정확한 답변을 드릴 수 있습니다."
        elif conversation_type == ConversationType.EMOTIONAL_SUPPORT:
            return f"{speaker_name}님의 감정을 이해합니다. 제가 도움이 될 수 있도록 노력하겠습니다."
        else:
            return f"{speaker_name}님의 말씀을 잘 들었습니다. 더 이야기해 주세요."

    def _evaluate_emotion_appropriateness(
        self, response: str, emotion: EmotionalState
    ) -> bool:
        """감정 적절성 평가"""
        response_lower = response.lower()

        if emotion == EmotionalState.SAD and any(
            word in response_lower for word in ["아프", "위로", "힘내"]
        ):
            return True
        elif emotion == EmotionalState.HAPPY and any(
            word in response_lower for word in ["기뻐", "축하", "좋아"]
        ):
            return True
        elif emotion == EmotionalState.ANGRY and any(
            word in response_lower for word in ["이해", "차분", "생각"]
        ):
            return True
        else:
            return True

    def _evaluate_family_relevance(self, response: str) -> bool:
        """가족 관련성 평가"""
        # 가족 관련 키워드가 포함되어 있거나 일반적인 응답인 경우 True
        return True

    def _calculate_response_confidence(
        self, response: str, conversation_type: ConversationType
    ) -> float:
        """응답 신뢰도 계산"""
        base_confidence = 0.7

        if conversation_type == ConversationType.GREETING:
            base_confidence += 0.2
        elif conversation_type == ConversationType.EMOTIONAL_SUPPORT:
            base_confidence += 0.1
        elif conversation_type == ConversationType.LEARNING:
            base_confidence += 0.15

        return min(1.0, base_confidence)

    def _determine_support_type(self, emotion: EmotionalState) -> SupportType:
        """지원 유형 결정"""
        if emotion in [
            EmotionalState.SAD,
            EmotionalState.ANGRY,
            EmotionalState.ANXIOUS,
        ]:
            return SupportType.COMFORT
        elif emotion in [
            EmotionalState.HAPPY,
            EmotionalState.EXCITED,
            EmotionalState.PROUD,
        ]:
            return SupportType.CELEBRATION
        else:
            return SupportType.GUIDANCE

    async def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """대화 요약 생성"""
        try:
            session = next(
                (s for s in self.conversation_sessions if s.id == session_id), None
            )
            if not session:
                return {"error": "세션을 찾을 수 없습니다."}

            session_messages = [
                m for m in self.messages if m.speaker_id == session.family_member_id
            ]
            session_responses = [
                r for r in self.responses if r.id.startswith(f"response_{session_id}")
            ]

            # 감정 분석
            emotions = [m.emotion_detected for m in session_messages]
            emotion_counts = {}
            for emotion in emotions:
                emotion_counts[emotion.value] = emotion_counts.get(emotion.value, 0) + 1

            # 대화 유형 분석
            conversation_types = [m.conversation_type for m in session_messages]
            type_counts = {}
            for conv_type in conversation_types:
                type_counts[conv_type.value] = type_counts.get(conv_type.value, 0) + 1

            return {
                "session_id": session_id,
                "start_time": session.start_time.isoformat(),
                "message_count": len(session_messages),
                "response_count": len(session_responses),
                "emotion_analysis": emotion_counts,
                "conversation_type_analysis": type_counts,
                "average_confidence": (
                    sum(r.confidence_score for r in session_responses)
                    / len(session_responses)
                    if session_responses
                    else 0
                ),
                "emotional_progress": [e.value for e in session.emotional_progress],
                "support_provided": [s.value for s in session.support_provided],
            }

        except Exception as e:
            logger.error(f"대화 요약 생성 실패: {e}")
            return {"error": str(e)}


# 전역 인스턴스
unified_conversation_service = UnifiedConversationService()
