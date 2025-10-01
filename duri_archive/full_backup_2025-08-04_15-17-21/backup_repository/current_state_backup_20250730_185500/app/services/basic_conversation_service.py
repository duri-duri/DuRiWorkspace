#!/usr/bin/env python3
"""
BasicConversationSystem - Phase 11
기본 대화 시스템

기능:
- 가족 중심 기본 대화
- 대화 맥락 이해 및 응답 생성
- 감정 상태 인식 및 공감적 응답
- 대화 히스토리 관리
"""

import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
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
    OTHER = "other"


class EmotionType(Enum):
    """감정 유형"""

    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    EXCITED = "excited"
    WORRIED = "worried"
    CALM = "calm"
    CONFUSED = "confused"
    NEUTRAL = "neutral"


class ResponseStyle(Enum):
    """응답 스타일"""

    WARM = "warm"
    SUPPORTIVE = "supportive"
    ENCOURAGING = "encouraging"
    PLAYFUL = "playful"
    EDUCATIONAL = "educational"
    NEUTRAL = "neutral"


@dataclass
class ConversationContext:
    """대화 맥락"""

    family_member_id: str
    family_member_name: str
    relationship: str
    current_emotion: EmotionType
    conversation_history: List[str]
    family_context: Dict[str, Any]


@dataclass
class ConversationMessage:
    """대화 메시지"""

    id: str
    speaker_id: str
    speaker_name: str
    message: str
    conversation_type: ConversationType
    emotion_detected: EmotionType
    timestamp: datetime
    response_style: ResponseStyle = ResponseStyle.NEUTRAL


@dataclass
class ConversationResponse:
    """대화 응답"""

    id: str
    message_id: str
    response_text: str
    response_style: ResponseStyle
    emotion_appropriate: bool
    family_relevant: bool
    confidence_score: float
    timestamp: datetime
    notes: Optional[str] = None


@dataclass
class ConversationSession:
    """대화 세션"""

    id: str
    family_member_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    message_count: int = 0
    average_emotion: EmotionType = EmotionType.NEUTRAL
    session_quality: float = 0.0


class BasicConversationSystem:
    """기본 대화 시스템"""

    def __init__(self):
        self.conversation_sessions: List[ConversationSession] = []
        self.messages: List[ConversationMessage] = []
        self.responses: List[ConversationResponse] = []
        self.family_context: Dict[str, Any] = {}

        # 대화 패턴 및 응답 템플릿
        self._initialize_conversation_patterns()

        logger.info("BasicConversationSystem 초기화 완료")

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

    def start_conversation(
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

            logger.info(f"대화 세션 시작: {session_id} - {family_member_name}")
            return conversation_session

        except Exception as e:
            logger.error(f"대화 세션 시작 실패: {e}")
            raise

    def process_message(
        self, session_id: str, speaker_id: str, speaker_name: str, message: str
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
            )

            self.messages.append(conversation_message)

            # 세션 업데이트
            session = next(
                (s for s in self.conversation_sessions if s.id == session_id), None
            )
            if session:
                session.message_count += 1

            # 응답 생성
            response_text = self._generate_response(
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

            conversation_response = ConversationResponse(
                id=f"response_{len(self.responses) + 1}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                message_id=message_id,
                response_text=response_text,
                response_style=response_style,
                emotion_appropriate=emotion_appropriate,
                family_relevant=family_relevant,
                confidence_score=confidence_score,
                timestamp=datetime.now(),
            )

            self.responses.append(conversation_response)
            logger.info(f"대화 응답 생성: {conversation_response.id}")

            return conversation_response

        except Exception as e:
            logger.error(f"메시지 처리 실패: {e}")
            raise

    def _analyze_conversation_type(self, message: str) -> ConversationType:
        """대화 유형 분석"""
        message_lower = message.lower()

        # 인사말 패턴
        if any(
            word in message_lower for word in ["안녕", "좋은 아침", "좋은 밤", "고마워"]
        ):
            return ConversationType.GREETING

        # 감정 공유 패턴
        if any(
            word in message_lower
            for word in ["슬퍼", "화나", "기뻐", "걱정", "스트레스", "힘들어"]
        ):
            return ConversationType.EMOTIONAL_SUPPORT

        # 질문 패턴
        if (
            any(
                word in message_lower
                for word in ["뭐", "어떻게", "왜", "언제", "어디", "누가"]
            )
            and "?" in message
        ):
            return ConversationType.QUESTION

        # 조언 요청 패턴
        if any(
            word in message_lower for word in ["조언", "도움", "어떻게 해야", "방법"]
        ):
            return ConversationType.ADVICE_REQUEST

        # 학습 패턴
        if any(
            word in message_lower
            for word in ["배우고 싶어", "알려줘", "가르쳐", "설명"]
        ):
            return ConversationType.LEARNING

        # 장난스러운 패턴
        if any(word in message_lower for word in ["놀자", "재미", "웃겨", "장난"]):
            return ConversationType.PLAYFUL

        # 일반적인 공유
        return ConversationType.SHARING

    def _detect_emotion(self, message: str) -> EmotionType:
        """감정 감지"""
        message_lower = message.lower()

        # 기쁨 관련
        if any(
            word in message_lower
            for word in ["기뻐", "행복", "좋아", "재미", "웃겨", "즐거워"]
        ):
            return EmotionType.HAPPY

        # 슬픔 관련
        if any(
            word in message_lower for word in ["슬퍼", "우울", "속상", "힘들어", "지쳐"]
        ):
            return EmotionType.SAD

        # 화남 관련
        if any(word in message_lower for word in ["화나", "짜증", "열받", "분노"]):
            return EmotionType.ANGRY

        # 흥미 관련
        if any(word in message_lower for word in ["신나", "흥미", "재미있", "놀라워"]):
            return EmotionType.EXCITED

        # 걱정 관련
        if any(word in message_lower for word in ["걱정", "불안", "긴장", "두려워"]):
            return EmotionType.WORRIED

        # 혼란 관련
        if any(
            word in message_lower for word in ["모르겠", "헷갈려", "어려워", "복잡"]
        ):
            return EmotionType.CONFUSED

        # 차분함
        if any(word in message_lower for word in ["괜찮", "좋아", "평온", "차분"]):
            return EmotionType.CALM

        return EmotionType.NEUTRAL

    def _determine_response_style(
        self, conversation_type: ConversationType, emotion: EmotionType
    ) -> ResponseStyle:
        """응답 스타일 결정"""
        if conversation_type == ConversationType.EMOTIONAL_SUPPORT:
            if emotion in [EmotionType.SAD, EmotionType.WORRIED]:
                return ResponseStyle.SUPPORTIVE
            elif emotion == EmotionType.HAPPY:
                return ResponseStyle.WARM
            elif emotion == EmotionType.ANGRY:
                return ResponseStyle.SUPPORTIVE
            else:
                return ResponseStyle.WARM

        elif conversation_type == ConversationType.LEARNING:
            return ResponseStyle.EDUCATIONAL

        elif conversation_type == ConversationType.PLAYFUL:
            return ResponseStyle.PLAYFUL

        elif conversation_type == ConversationType.ADVICE_REQUEST:
            return ResponseStyle.ENCOURAGING

        else:
            return ResponseStyle.NEUTRAL

    def _generate_response(
        self,
        message: str,
        conversation_type: ConversationType,
        emotion: EmotionType,
        speaker_name: str,
    ) -> str:
        """응답 생성"""
        message_lower = message.lower()

        # 인사말 응답
        if conversation_type == ConversationType.GREETING:
            for pattern, response in self.greeting_patterns.items():
                if pattern in message_lower:
                    return response

        # 감정 지원 응답
        elif conversation_type == ConversationType.EMOTIONAL_SUPPORT:
            for pattern, response in self.emotional_support_patterns.items():
                if pattern in message_lower:
                    return f"{speaker_name}님, {response}"

        # 학습 응답
        elif conversation_type == ConversationType.LEARNING:
            for pattern, response in self.learning_patterns.items():
                if pattern in message_lower:
                    return f"{speaker_name}님, {response}"

        # 질문 응답
        elif conversation_type == ConversationType.QUESTION:
            return f"{speaker_name}님의 질문에 대해 생각해보겠습니다. 좀 더 구체적으로 말씀해주시면 더 정확한 답변을 드릴 수 있어요."

        # 조언 요청 응답
        elif conversation_type == ConversationType.ADVICE_REQUEST:
            return f"{speaker_name}님, 어떤 상황인지 자세히 말씀해주시면 함께 생각해보아요. 가족의 관점에서 도움을 드릴게요."

        # 장난스러운 응답
        elif conversation_type == ConversationType.PLAYFUL:
            return f"{speaker_name}님과 재미있게 대화할 수 있어서 좋아요! 더 재미있는 이야기를 들려주세요."

        # 일반적인 공유 응답
        else:
            if emotion == EmotionType.HAPPY:
                return f"{speaker_name}님, 기뻐하시는 모습이 보기 좋아요! 더 좋은 일이 있으시면 언제든 말씀해주세요."
            elif emotion == EmotionType.SAD:
                return f"{speaker_name}님, 마음이 아프시겠어요. 제가 옆에 있어드릴게요. 이야기하고 싶으시면 언제든 말씀해주세요."
            elif emotion == EmotionType.ANGRY:
                return f"{speaker_name}님, 화가 나시는 일이 있었군요. 천천히 이야기해보세요. 함께 해결해보아요."
            else:
                return f"{speaker_name}님, 말씀해주신 내용을 잘 들었어요. 더 궁금한 것이 있으시면 언제든 말씀해주세요."

    def _evaluate_emotion_appropriateness(
        self, response: str, emotion: EmotionType
    ) -> bool:
        """감정 적절성 평가"""
        response_lower = response.lower()

        if emotion == EmotionType.SAD and any(
            word in response_lower for word in ["아프", "슬프", "위로", "힘들"]
        ):
            return True
        elif emotion == EmotionType.HAPPY and any(
            word in response_lower for word in ["기뻐", "좋아", "행복", "즐거워"]
        ):
            return True
        elif emotion == EmotionType.ANGRY and any(
            word in response_lower for word in ["화", "짜증", "이해", "함께"]
        ):
            return True
        elif emotion == EmotionType.WORRIED and any(
            word in response_lower for word in ["걱정", "불안", "함께", "도움"]
        ):
            return True

        return True  # 기본적으로 적절하다고 가정

    def _evaluate_family_relevance(self, response: str) -> bool:
        """가족 관련성 평가"""
        family_keywords = [
            "가족",
            "부모",
            "자식",
            "사랑",
            "관계",
            "소통",
            "이해",
            "지지",
        ]
        response_lower = response.lower()

        return any(keyword in response_lower for keyword in family_keywords)

    def _calculate_response_confidence(
        self, response: str, conversation_type: ConversationType
    ) -> float:
        """응답 신뢰도 계산"""
        base_score = 0.6

        # 응답 길이 점수
        word_count = len(response.split())
        length_score = min(0.2, word_count * 0.01)

        # 대화 유형별 점수
        type_score = 0.0
        if conversation_type == ConversationType.EMOTIONAL_SUPPORT:
            type_score = 0.1
        elif conversation_type == ConversationType.LEARNING:
            type_score = 0.1
        elif conversation_type == ConversationType.ADVICE_REQUEST:
            type_score = 0.1
        else:
            type_score = 0.05

        return min(1.0, base_score + length_score + type_score)

    def end_conversation_session(self, session_id: str) -> ConversationSession:
        """대화 세션 종료"""
        try:
            session = next(
                (s for s in self.conversation_sessions if s.id == session_id), None
            )
            if session:
                session.end_time = datetime.now()

                # 세션 품질 계산
                session_messages = [
                    m for m in self.messages if m.id.startswith(session_id)
                ]
                if session_messages:
                    avg_emotion_score = sum(
                        self._emotion_to_score(m.emotion_detected)
                        for m in session_messages
                    ) / len(session_messages)
                    session.session_quality = min(
                        1.0, avg_emotion_score * 0.5 + len(session_messages) * 0.1
                    )

                logger.info(f"대화 세션 종료: {session_id}")

            return session

        except Exception as e:
            logger.error(f"대화 세션 종료 실패: {e}")
            raise

    def _emotion_to_score(self, emotion: EmotionType) -> float:
        """감정을 점수로 변환"""
        emotion_scores = {
            EmotionType.HAPPY: 0.9,
            EmotionType.EXCITED: 0.8,
            EmotionType.CALM: 0.7,
            EmotionType.NEUTRAL: 0.5,
            EmotionType.CONFUSED: 0.4,
            EmotionType.WORRIED: 0.3,
            EmotionType.SAD: 0.2,
            EmotionType.ANGRY: 0.1,
        }
        return emotion_scores.get(emotion, 0.5)

    def get_conversation_statistics(self) -> Dict[str, Any]:
        """대화 통계 제공"""
        try:
            total_sessions = len(self.conversation_sessions)
            total_messages = len(self.messages)
            total_responses = len(self.responses)

            # 대화 유형별 통계
            conversation_type_stats = {}
            for conv_type in ConversationType:
                type_messages = [
                    m for m in self.messages if m.conversation_type == conv_type
                ]
                conversation_type_stats[conv_type.value] = len(type_messages)

            # 감정별 통계
            emotion_stats = {}
            for emotion in EmotionType:
                emotion_messages = [
                    m for m in self.messages if m.emotion_detected == emotion
                ]
                emotion_stats[emotion.value] = len(emotion_messages)

            # 응답 스타일별 통계
            response_style_stats = {}
            for style in ResponseStyle:
                style_responses = [
                    r for r in self.responses if r.response_style == style
                ]
                response_style_stats[style.value] = len(style_responses)

            # 평균 세션 품질
            avg_session_quality = (
                sum(s.session_quality for s in self.conversation_sessions)
                / len(self.conversation_sessions)
                if self.conversation_sessions
                else 0
            )

            # 평균 응답 신뢰도
            avg_confidence = (
                sum(r.confidence_score for r in self.responses) / len(self.responses)
                if self.responses
                else 0
            )

            statistics = {
                "total_sessions": total_sessions,
                "total_messages": total_messages,
                "total_responses": total_responses,
                "conversation_type_stats": conversation_type_stats,
                "emotion_stats": emotion_stats,
                "response_style_stats": response_style_stats,
                "average_session_quality": avg_session_quality,
                "average_confidence": avg_confidence,
                "last_updated": datetime.now().isoformat(),
            }

            logger.info("대화 통계 생성 완료")
            return statistics

        except Exception as e:
            logger.error(f"대화 통계 생성 실패: {e}")
            return {}

    def export_conversation_data(self) -> Dict[str, Any]:
        """대화 데이터 내보내기"""
        try:
            export_data = {
                "conversation_sessions": [
                    asdict(session) for session in self.conversation_sessions
                ],
                "messages": [asdict(message) for message in self.messages],
                "responses": [asdict(response) for response in self.responses],
                "export_date": datetime.now().isoformat(),
            }

            logger.info("대화 데이터 내보내기 완료")
            return export_data

        except Exception as e:
            logger.error(f"대화 데이터 내보내기 실패: {e}")
            return {}

    def import_conversation_data(self, data: Dict[str, Any]):
        """대화 데이터 가져오기"""
        try:
            # 대화 세션 가져오기
            for session_data in data.get("conversation_sessions", []):
                # datetime 객체 변환
                if "start_time" in session_data:
                    session_data["start_time"] = datetime.fromisoformat(
                        session_data["start_time"]
                    )
                if "end_time" in session_data and session_data["end_time"]:
                    session_data["end_time"] = datetime.fromisoformat(
                        session_data["end_time"]
                    )

                conversation_session = ConversationSession(**session_data)
                self.conversation_sessions.append(conversation_session)

            # 메시지 가져오기
            for message_data in data.get("messages", []):
                # datetime 객체 변환
                if "timestamp" in message_data:
                    message_data["timestamp"] = datetime.fromisoformat(
                        message_data["timestamp"]
                    )

                conversation_message = ConversationMessage(**message_data)
                self.messages.append(conversation_message)

            # 응답 가져오기
            for response_data in data.get("responses", []):
                # datetime 객체 변환
                if "timestamp" in response_data:
                    response_data["timestamp"] = datetime.fromisoformat(
                        response_data["timestamp"]
                    )

                conversation_response = ConversationResponse(**response_data)
                self.responses.append(conversation_response)

            logger.info("대화 데이터 가져오기 완료")

        except Exception as e:
            logger.error(f"대화 데이터 가져오기 실패: {e}")
            raise


# 테스트 함수
def test_basic_conversation_system():
    """기본 대화 시스템 테스트"""
    print("💬 BasicConversationSystem 테스트 시작...")

    # 시스템 초기화
    conversation_system = BasicConversationSystem()

    # 가족 맥락 설정
    family_context = {
        "family_type": "nuclear",
        "children_count": 2,
        "children_ages": [5, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
    }

    # 1. 대화 세션 시작
    session = conversation_system.start_conversation(
        "member_1", "엄마", "mother", family_context
    )
    print(f"✅ 대화 세션 시작: {session.id}")

    # 2. 인사말 처리
    greeting_response = conversation_system.process_message(
        session.id, "member_1", "엄마", "안녕하세요!"
    )
    print(
        f"✅ 인사말 응답: {greeting_response.response_style.value} 스타일, {greeting_response.confidence_score:.2f} 신뢰도"
    )

    # 3. 감정 공유 처리
    emotional_response = conversation_system.process_message(
        session.id, "member_1", "엄마", "아이가 학교에서 친구와 다퉈서 속상해요."
    )
    print(
        f"✅ 감정 공유 응답: {emotional_response.response_style.value} 스타일, {emotional_response.emotion_appropriate} 감정 적절성"
    )

    # 4. 질문 처리
    question_response = conversation_system.process_message(
        session.id, "member_1", "엄마", "아이와 어떻게 대화해야 할까요?"
    )
    print(
        f"✅ 질문 응답: {question_response.response_style.value} 스타일, {question_response.family_relevant} 가족 관련성"
    )

    # 5. 학습 요청 처리
    learning_response = conversation_system.process_message(
        session.id, "member_1", "엄마", "아이의 창의력을 키우는 방법을 알려주세요."
    )
    print(
        f"✅ 학습 요청 응답: {learning_response.response_style.value} 스타일, {learning_response.confidence_score:.2f} 신뢰도"
    )

    # 6. 장난스러운 대화 처리
    playful_response = conversation_system.process_message(
        session.id, "member_1", "엄마", "재미있는 이야기 해주세요!"
    )
    print(
        f"✅ 장난스러운 대화 응답: {playful_response.response_style.value} 스타일, {playful_response.family_relevant} 가족 관련성"
    )

    # 7. 대화 세션 종료
    ended_session = conversation_system.end_conversation_session(session.id)
    print(f"✅ 대화 세션 종료: {ended_session.session_quality:.2f} 세션 품질")

    # 8. 대화 통계
    statistics = conversation_system.get_conversation_statistics()
    print(
        f"✅ 대화 통계: {statistics['total_sessions']}개 세션, {statistics['total_messages']}개 메시지"
    )
    print(f"   대화 유형별: {statistics['conversation_type_stats']}")
    print(f"   감정별: {statistics['emotion_stats']}")
    print(f"   응답 스타일별: {statistics['response_style_stats']}")

    # 9. 데이터 내보내기/가져오기
    export_data = conversation_system.export_conversation_data()
    print(
        f"✅ 대화 데이터 내보내기: {len(export_data['conversation_sessions'])}개 세션, {len(export_data['messages'])}개 메시지"
    )

    print("🎉 BasicConversationSystem 테스트 완료!")


if __name__ == "__main__":
    test_basic_conversation_system()
