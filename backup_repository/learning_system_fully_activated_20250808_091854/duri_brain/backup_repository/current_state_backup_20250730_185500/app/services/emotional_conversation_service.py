#!/usr/bin/env python3
"""
EmotionalConversationSystem - Phase 12.3
감정 지능 대화 시스템

목적:
- 가족 구성원의 감정 상태 정확한 인식
- 적절한 감정적 지원과 공감 제공
- 감정적 유대감 강화를 통한 가족 관계 증진
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmotionalState(Enum):
    """감정 상태"""
    HAPPY = "happy"
    EXCITED = "excited"
    CALM = "calm"
    SAD = "sad"
    ANGRY = "angry"
    ANXIOUS = "anxious"
    FRUSTRATED = "frustrated"
    CONFUSED = "confused"
    PROUD = "proud"
    GRATEFUL = "grateful"
    LONELY = "lonely"
    NEUTRAL = "neutral"

class EmotionalIntensity(Enum):
    """감정 강도"""
    VERY_LOW = "very_low"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"

class SupportType(Enum):
    """지원 유형"""
    VALIDATION = "validation"
    ENCOURAGEMENT = "encouragement"
    COMFORT = "comfort"
    GUIDANCE = "guidance"
    CELEBRATION = "celebration"
    PROBLEM_SOLVING = "problem_solving"
    LISTENING = "listening"

class ConversationTone(Enum):
    """대화 톤"""
    WARM = "warm"
    GENTLE = "gentle"
    ENTHUSIASTIC = "enthusiastic"
    CALMING = "calming"
    SUPPORTIVE = "supportive"
    PLAYFUL = "playful"
    SERIOUS = "serious"

@dataclass
class EmotionalAnalysis:
    """감정 분석"""
    primary_emotion: EmotionalState
    secondary_emotions: List[EmotionalState]
    intensity: EmotionalIntensity
    emotional_triggers: List[str]
    underlying_needs: List[str]
    support_requirements: List[SupportType]
    confidence_score: float

@dataclass
class EmotionalResponse:
    """감정적 응답"""
    response_type: SupportType
    conversation_tone: ConversationTone
    response_content: str
    emotional_validation: str
    practical_support: Optional[str]
    follow_up_questions: List[str]
    confidence_score: float

@dataclass
class EmotionalConversation:
    """감정적 대화"""
    id: str
    family_member: str
    initial_emotion: EmotionalState
    conversation_flow: List[Dict[str, Any]]
    emotional_progress: List[EmotionalState]
    support_provided: List[SupportType]
    resolution_achieved: bool
    emotional_bond_strengthened: bool
    timestamp: datetime

class EmotionalConversationSystem:
    """감정 지능 대화 시스템"""
    
    def __init__(self):
        self.emotional_conversations: List[EmotionalConversation] = []
        self.emotional_patterns: Dict[str, List[EmotionalState]] = {}
        self.support_effectiveness: Dict[SupportType, float] = {}
        
        logger.info("EmotionalConversationSystem 초기화 완료")
    
    def analyze_emotional_state(self, message: str, family_context: Dict[str, Any], 
                              speaker_info: Dict[str, Any]) -> EmotionalAnalysis:
        """감정 상태 분석"""
        # 감정 키워드 분석
        emotion_keywords = self._extract_emotion_keywords(message)
        primary_emotion = self._determine_primary_emotion(emotion_keywords, message)
        secondary_emotions = self._identify_secondary_emotions(emotion_keywords, primary_emotion)
        
        # 감정 강도 평가
        intensity = self._assess_emotional_intensity(message, emotion_keywords)
        
        # 감정 트리거 식별
        emotional_triggers = self._identify_emotional_triggers(message, family_context)
        
        # 근본적 욕구 파악
        underlying_needs = self._identify_underlying_needs(primary_emotion, message, family_context)
        
        # 지원 요구사항 결정
        support_requirements = self._determine_support_requirements(primary_emotion, intensity, underlying_needs)
        
        # 신뢰도 계산
        confidence_score = self._calculate_emotional_confidence(message, emotion_keywords, primary_emotion)
        
        analysis = EmotionalAnalysis(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            emotional_triggers=emotional_triggers,
            underlying_needs=underlying_needs,
            support_requirements=support_requirements,
            confidence_score=confidence_score
        )
        
        logger.info(f"감정 상태 분석 완료: {primary_emotion.value} ({intensity.value})")
        return analysis
    
    def _extract_emotion_keywords(self, message: str) -> List[str]:
        """감정 키워드 추출"""
        emotion_keywords = []
        message_lower = message.lower()
        
        # 긍정적 감정 키워드
        positive_keywords = ['기쁘', '행복', '즐거', '신나', '감사', '만족', '자랑', '희망', '사랑']
        # 부정적 감정 키워드
        negative_keywords = ['슬프', '화나', '짜증', '걱정', '불안', '실망', '혼란', '외로', '스트레스']
        # 중성적 감정 키워드
        neutral_keywords = ['그냥', '보통', '괜찮', '평범']
        
        for keyword in positive_keywords:
            if keyword in message_lower:
                emotion_keywords.append(keyword)
        
        for keyword in negative_keywords:
            if keyword in message_lower:
                emotion_keywords.append(keyword)
        
        for keyword in neutral_keywords:
            if keyword in message_lower:
                emotion_keywords.append(keyword)
        
        return emotion_keywords
    
    def _determine_primary_emotion(self, emotion_keywords: List[str], message: str) -> EmotionalState:
        """주요 감정 결정"""
        message_lower = message.lower()
        
        # 긍정적 감정
        if any(word in message_lower for word in ['기쁘', '행복', '즐거']):
            return EmotionalState.HAPPY
        elif any(word in message_lower for word in ['신나', '설렘', '흥미']):
            return EmotionalState.EXCITED
        elif any(word in message_lower for word in ['감사', '고마워']):
            return EmotionalState.GRATEFUL
        elif any(word in message_lower for word in ['자랑', '성취', '만족']):
            return EmotionalState.PROUD
        elif any(word in message_lower for word in ['차분', '평온', '안정']):
            return EmotionalState.CALM
        
        # 부정적 감정
        elif any(word in message_lower for word in ['슬프', '우울', '눈물']):
            return EmotionalState.SAD
        elif any(word in message_lower for word in ['화나', '짜증', '분노']):
            return EmotionalState.ANGRY
        elif any(word in message_lower for word in ['걱정', '불안', '두려움']):
            return EmotionalState.ANXIOUS
        elif any(word in message_lower for word in ['실망', '좌절', '힘들']):
            return EmotionalState.FRUSTRATED
        elif any(word in message_lower for word in ['혼란', '어려워', '모르겠']):
            return EmotionalState.CONFUSED
        elif any(word in message_lower for word in ['외로', '혼자']):
            return EmotionalState.LONELY
        
        else:
            return EmotionalState.NEUTRAL
    
    def _identify_secondary_emotions(self, emotion_keywords: List[str], primary_emotion: EmotionalState) -> List[EmotionalState]:
        """보조 감정 식별"""
        secondary_emotions = []
        
        # 주요 감정과 다른 감정들이 있는지 확인
        for keyword in emotion_keywords:
            if '감사' in keyword and primary_emotion != EmotionalState.GRATEFUL:
                secondary_emotions.append(EmotionalState.GRATEFUL)
            elif '자랑' in keyword and primary_emotion != EmotionalState.PROUD:
                secondary_emotions.append(EmotionalState.PROUD)
            elif '걱정' in keyword and primary_emotion != EmotionalState.ANXIOUS:
                secondary_emotions.append(EmotionalState.ANXIOUS)
        
        return list(set(secondary_emotions))  # 중복 제거
    
    def _assess_emotional_intensity(self, message: str, emotion_keywords: List[str]) -> EmotionalIntensity:
        """감정 강도 평가"""
        # 강조 표현 확인
        intensity_indicators = {
            'very_low': ['조금', '약간', '살짝'],
            'low': ['그냥', '보통'],
            'moderate': ['꽤', '나름'],
            'high': ['정말', '너무', '매우', '완전'],
            'very_high': ['정말 정말', '완전 완전', '너무너무', '미치도록']
        }
        
        message_lower = message.lower()
        
        for intensity, indicators in intensity_indicators.items():
            if any(indicator in message_lower for indicator in indicators):
                if intensity == 'very_low':
                    return EmotionalIntensity.VERY_LOW
                elif intensity == 'low':
                    return EmotionalIntensity.LOW
                elif intensity == 'moderate':
                    return EmotionalIntensity.MODERATE
                elif intensity == 'high':
                    return EmotionalIntensity.HIGH
                elif intensity == 'very_high':
                    return EmotionalIntensity.VERY_HIGH
        
        # 기본값
        return EmotionalIntensity.MODERATE
    
    def _identify_emotional_triggers(self, message: str, family_context: Dict[str, Any]) -> List[str]:
        """감정 트리거 식별"""
        triggers = []
        message_lower = message.lower()
        
        # 가족 관련 트리거
        if '가족' in message_lower or '엄마' in message_lower or '아빠' in message_lower:
            triggers.append("가족 관계")
        
        # 학교/학습 관련 트리거
        if any(word in message_lower for word in ['학교', '공부', '시험', '숙제']):
            triggers.append("학습/학교")
        
        # 친구 관련 트리거
        if any(word in message_lower for word in ['친구', '친구들', '같이']):
            triggers.append("친구 관계")
        
        # 성취/실패 관련 트리거
        if any(word in message_lower for word in ['성공', '실패', '잘했', '못했']):
            triggers.append("성취/실패")
        
        # 건강 관련 트리거
        if any(word in message_lower for word in ['아프', '병', '피곤', '힘들']):
            triggers.append("건강")
        
        return triggers
    
    def _identify_underlying_needs(self, primary_emotion: EmotionalState, message: str, family_context: Dict[str, Any]) -> List[str]:
        """근본적 욕구 파악"""
        needs = []
        
        if primary_emotion in [EmotionalState.SAD, EmotionalState.LONELY]:
            needs.extend(['사랑과 관심', '위로', '공감'])
        
        elif primary_emotion in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
            needs.extend(['이해', '공감', '해결책'])
        
        elif primary_emotion == EmotionalState.ANXIOUS:
            needs.extend(['안정감', '확신', '지지'])
        
        elif primary_emotion == EmotionalState.CONFUSED:
            needs.extend(['명확한 설명', '가이드', '지지'])
        
        elif primary_emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED, EmotionalState.PROUD]:
            needs.extend(['인정', '축하', '공유'])
        
        return needs
    
    def _determine_support_requirements(self, primary_emotion: EmotionalState, intensity: EmotionalIntensity, underlying_needs: List[str]) -> List[SupportType]:
        """지원 요구사항 결정"""
        support_types = []
        
        if primary_emotion in [EmotionalState.SAD, EmotionalState.LONELY]:
            support_types.extend([SupportType.VALIDATION, SupportType.COMFORT])
        
        elif primary_emotion in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
            support_types.extend([SupportType.VALIDATION, SupportType.PROBLEM_SOLVING])
        
        elif primary_emotion == EmotionalState.ANXIOUS:
            support_types.extend([SupportType.COMFORT, SupportType.GUIDANCE])
        
        elif primary_emotion == EmotionalState.CONFUSED:
            support_types.extend([SupportType.GUIDANCE, SupportType.LISTENING])
        
        elif primary_emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED, EmotionalState.PROUD]:
            support_types.extend([SupportType.CELEBRATION, SupportType.ENCOURAGEMENT])
        
        # 강도에 따른 추가 지원
        if intensity in [EmotionalIntensity.HIGH, EmotionalIntensity.VERY_HIGH]:
            support_types.append(SupportType.LISTENING)
        
        return list(set(support_types))  # 중복 제거
    
    def _calculate_emotional_confidence(self, message: str, emotion_keywords: List[str], primary_emotion: EmotionalState) -> float:
        """감정 분석 신뢰도 계산"""
        base_score = 0.7
        
        # 감정 키워드 수
        if len(emotion_keywords) >= 2:
            base_score += 0.2
        elif len(emotion_keywords) == 1:
            base_score += 0.1
        
        # 메시지 길이
        if len(message) > 50:
            base_score += 0.1
        
        # 감정의 명확성
        if primary_emotion != EmotionalState.NEUTRAL:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def generate_emotional_response(self, analysis: EmotionalAnalysis, family_context: Dict[str, Any]) -> EmotionalResponse:
        """감정적 응답 생성"""
        # 응답 유형 결정
        primary_support = analysis.support_requirements[0] if analysis.support_requirements else SupportType.LISTENING
        
        # 대화 톤 결정
        conversation_tone = self._determine_conversation_tone(analysis.primary_emotion, analysis.intensity)
        
        # 응답 내용 생성
        response_content = self._generate_response_content(analysis, primary_support, conversation_tone)
        
        # 감정적 검증
        emotional_validation = self._generate_emotional_validation(analysis)
        
        # 실용적 지원
        practical_support = self._generate_practical_support(analysis, family_context)
        
        # 후속 질문
        follow_up_questions = self._generate_follow_up_questions(analysis)
        
        # 신뢰도 계산
        confidence_score = self._calculate_response_confidence(analysis, response_content)
        
        response = EmotionalResponse(
            response_type=primary_support,
            conversation_tone=conversation_tone,
            response_content=response_content,
            emotional_validation=emotional_validation,
            practical_support=practical_support,
            follow_up_questions=follow_up_questions,
            confidence_score=confidence_score
        )
        
        logger.info(f"감정적 응답 생성 완료: {primary_support.value}")
        return response
    
    def _determine_conversation_tone(self, primary_emotion: EmotionalState, intensity: EmotionalIntensity) -> ConversationTone:
        """대화 톤 결정"""
        if primary_emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED, EmotionalState.PROUD]:
            return ConversationTone.ENTHUSIASTIC
        elif primary_emotion in [EmotionalState.SAD, EmotionalState.LONELY]:
            return ConversationTone.WARM
        elif primary_emotion in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
            return ConversationTone.CALMING
        elif primary_emotion == EmotionalState.ANXIOUS:
            return ConversationTone.SUPPORTIVE
        elif primary_emotion == EmotionalState.CONFUSED:
            return ConversationTone.GENTLE
        else:
            return ConversationTone.WARM
    
    def _generate_response_content(self, analysis: EmotionalAnalysis, support_type: SupportType, tone: ConversationTone) -> str:
        """응답 내용 생성"""
        if support_type == SupportType.VALIDATION:
            return f"그런 감정을 느끼는 게 당연해. {analysis.primary_emotion.value}한 마음이 이해돼."
        elif support_type == SupportType.ENCOURAGEMENT:
            return f"정말 잘하고 있어! 네가 얼마나 노력하는지 다 알고 있어."
        elif support_type == SupportType.COMFORT:
            return f"괜찮아, 내가 여기 있어. 함께 있어."
        elif support_type == SupportType.GUIDANCE:
            return f"함께 해결해보자. 어떤 방법이 있을까?"
        elif support_type == SupportType.CELEBRATION:
            return f"와! 정말 대단해! 축하해!"
        elif support_type == SupportType.PROBLEM_SOLVING:
            return f"어떤 부분이 가장 힘들었어? 함께 생각해보자."
        else:  # LISTENING
            return f"더 자세히 들려줘. 네 이야기에 집중하고 있어."
    
    def _generate_emotional_validation(self, analysis: EmotionalAnalysis) -> str:
        """감정적 검증 생성"""
        if analysis.primary_emotion in [EmotionalState.SAD, EmotionalState.LONELY]:
            return "그런 감정을 느끼는 것은 자연스러워. 네 마음이 아플 수 있어."
        elif analysis.primary_emotion in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
            return "화가 나는 게 당연해. 그런 상황이라면 누구라도 그럴 거야."
        elif analysis.primary_emotion == EmotionalState.ANXIOUS:
            return "걱정되는 마음이 이해돼. 불안한 감정은 자연스러워."
        elif analysis.primary_emotion == EmotionalState.CONFUSED:
            return "혼란스러운 게 당연해. 복잡한 일이잖아."
        elif analysis.primary_emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED, EmotionalState.PROUD]:
            return "정말 기쁜 일이구나! 그런 기분을 느끼는 게 좋아."
        else:
            return "네 감정이 이해돼."
    
    def _generate_practical_support(self, analysis: EmotionalAnalysis, family_context: Dict[str, Any]) -> Optional[str]:
        """실용적 지원 생성"""
        if analysis.primary_emotion == EmotionalState.ANXIOUS:
            return "깊은 숨을 몇 번 쉬어보자. 그리고 하나씩 차근차근 생각해보자."
        elif analysis.primary_emotion == EmotionalState.ANGRY:
            return "잠깐 심호흡을 해보자. 그리고 왜 화가 났는지 생각해보자."
        elif analysis.primary_emotion == EmotionalState.SAD:
            return "좋아하는 음식을 먹거나 좋아하는 일을 해보는 건 어때?"
        elif analysis.primary_emotion == EmotionalState.CONFUSED:
            return "하나씩 차근차근 정리해보자. 무엇부터 시작하고 싶어?"
        else:
            return None
    
    def _generate_follow_up_questions(self, analysis: EmotionalAnalysis) -> List[str]:
        """후속 질문 생성"""
        questions = []
        
        if analysis.primary_emotion in [EmotionalState.SAD, EmotionalState.LONELY]:
            questions.extend(["무엇이 가장 힘들었어?", "어떤 도움이 필요해?"])
        elif analysis.primary_emotion in [EmotionalState.ANGRY, EmotionalState.FRUSTRATED]:
            questions.extend(["왜 그렇게 생각했어?", "어떻게 하면 좋을까?"])
        elif analysis.primary_emotion == EmotionalState.ANXIOUS:
            questions.extend(["가장 걱정되는 건 뭐야?", "어떤 결과를 원해?"])
        elif analysis.primary_emotion == EmotionalState.CONFUSED:
            questions.extend(["어떤 부분이 가장 헷갈려?", "더 자세히 설명해줄 수 있어?"])
        elif analysis.primary_emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED, EmotionalState.PROUD]:
            questions.extend(["어떤 부분이 가장 기뻤어?", "다음에는 어떻게 할 거야?"])
        
        return questions
    
    def _calculate_response_confidence(self, analysis: EmotionalAnalysis, response_content: str) -> float:
        """응답 신뢰도 계산"""
        base_score = analysis.confidence_score
        
        # 응답 내용의 적절성
        if len(response_content) > 20:
            base_score += 0.1
        
        # 지원 유형의 적절성
        if analysis.support_requirements:
            base_score += 0.1
        
        return min(1.0, base_score)
    
    def conduct_emotional_conversation(self, family_member: str, initial_message: str, 
                                     family_context: Dict[str, Any]) -> EmotionalConversation:
        """감정적 대화 수행"""
        conversation_id = f"emotional_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 초기 감정 분석
        initial_analysis = self.analyze_emotional_state(initial_message, family_context, {'name': family_member})
        initial_emotion = initial_analysis.primary_emotion
        
        # 대화 흐름 시뮬레이션
        conversation_flow = []
        emotional_progress = [initial_emotion]
        support_provided = []
        
        # 첫 번째 응답
        first_response = self.generate_emotional_response(initial_analysis, family_context)
        conversation_flow.append({
            'speaker': family_member,
            'message': initial_message,
            'emotion': initial_emotion.value,
            'analysis': asdict(initial_analysis)
        })
        conversation_flow.append({
            'speaker': 'DuRi',
            'response': asdict(first_response),
            'support_type': first_response.response_type.value
        })
        support_provided.append(first_response.response_type)
        
        # 감정 변화 시뮬레이션
        if initial_emotion in [EmotionalState.SAD, EmotionalState.ANGRY, EmotionalState.ANXIOUS]:
            # 부정적 감정에서 긍정적 감정으로 변화
            emotional_progress.append(EmotionalState.CALM)
            support_provided.append(SupportType.COMFORT)
        elif initial_emotion in [EmotionalState.HAPPY, EmotionalState.EXCITED, EmotionalState.PROUD]:
            # 긍정적 감정 유지
            emotional_progress.append(EmotionalState.HAPPY)
            support_provided.append(SupportType.CELEBRATION)
        
        # 해결 달성 여부
        resolution_achieved = len(emotional_progress) > 1 and emotional_progress[-1] in [EmotionalState.CALM, EmotionalState.HAPPY]
        
        # 감정적 유대감 강화 여부
        emotional_bond_strengthened = len(support_provided) >= 2
        
        conversation = EmotionalConversation(
            id=conversation_id,
            family_member=family_member,
            initial_emotion=initial_emotion,
            conversation_flow=conversation_flow,
            emotional_progress=emotional_progress,
            support_provided=support_provided,
            resolution_achieved=resolution_achieved,
            emotional_bond_strengthened=emotional_bond_strengthened,
            timestamp=datetime.now()
        )
        
        self.emotional_conversations.append(conversation)
        logger.info(f"감정적 대화 완료: {family_member}와의 대화")
        
        return conversation
    
    def get_emotional_statistics(self) -> Dict[str, Any]:
        """감정적 대화 통계"""
        total_conversations = len(self.emotional_conversations)
        
        # 감정별 통계
        emotion_stats = {}
        for emotion in EmotionalState:
            emotion_conversations = [c for c in self.emotional_conversations if c.initial_emotion == emotion]
            emotion_stats[emotion.value] = len(emotion_conversations)
        
        # 지원 유형별 통계
        support_stats = {}
        for support_type in SupportType:
            support_count = sum(1 for conv in self.emotional_conversations 
                              for support in conv.support_provided if support == support_type)
            support_stats[support_type.value] = support_count
        
        # 해결률
        resolution_rate = sum(1 for conv in self.emotional_conversations if conv.resolution_achieved) / max(1, total_conversations)
        
        # 유대감 강화율
        bond_strengthening_rate = sum(1 for conv in self.emotional_conversations if conv.emotional_bond_strengthened) / max(1, total_conversations)
        
        statistics = {
            'total_conversations': total_conversations,
            'emotion_statistics': emotion_stats,
            'support_statistics': support_stats,
            'resolution_rate': resolution_rate,
            'bond_strengthening_rate': bond_strengthening_rate,
            'last_updated': datetime.now().isoformat()
        }
        
        logger.info("감정적 대화 통계 생성 완료")
        return statistics
    
    def export_emotional_data(self) -> Dict[str, Any]:
        """감정적 대화 데이터 내보내기"""
        return {
            'emotional_conversations': [asdict(c) for c in self.emotional_conversations],
            'emotional_patterns': self.emotional_patterns,
            'support_effectiveness': {k.value: v for k, v in self.support_effectiveness.items()},
            'export_date': datetime.now().isoformat()
        }

# 테스트 함수
def test_emotional_conversation_system():
    """감정 지능 대화 시스템 테스트"""
    print("🧠 EmotionalConversationSystem 테스트 시작...")
    
    emotional_system = EmotionalConversationSystem()
    
    # 1. 감정 상태 분석
    family_context = {
        'family_type': 'nuclear',
        'children_count': 2,
        'children_ages': [5, 8],
        'family_values': ['사랑', '소통', '성장', '창의성']
    }
    
    test_message = "오늘 학교에서 친구랑 싸웠어. 너무 화나고 슬퍼."
    speaker_info = {'name': '아이1', 'age': 8}
    
    analysis = emotional_system.analyze_emotional_state(test_message, family_context, speaker_info)
    
    print(f"✅ 감정 상태 분석: {analysis.primary_emotion.value}")
    print(f"   감정 강도: {analysis.intensity.value}")
    print(f"   근본적 욕구: {analysis.underlying_needs}")
    print(f"   신뢰도: {analysis.confidence_score:.2f}")
    
    # 2. 감정적 응답 생성
    response = emotional_system.generate_emotional_response(analysis, family_context)
    
    print(f"✅ 감정적 응답 생성: {response.response_type.value}")
    print(f"   대화 톤: {response.conversation_tone.value}")
    print(f"   응답 내용: {response.response_content}")
    print(f"   신뢰도: {response.confidence_score:.2f}")
    
    # 3. 감정적 대화 수행
    conversation = emotional_system.conduct_emotional_conversation('아이1', test_message, family_context)
    
    print(f"✅ 감정적 대화 수행: {conversation.family_member}")
    print(f"   초기 감정: {conversation.initial_emotion.value}")
    print(f"   해결 달성: {conversation.resolution_achieved}")
    print(f"   유대감 강화: {conversation.emotional_bond_strengthened}")
    
    # 4. 통계
    statistics = emotional_system.get_emotional_statistics()
    print(f"✅ 감정적 대화 통계: {statistics['total_conversations']}개 대화")
    print(f"   해결률: {statistics['resolution_rate']:.2f}")
    print(f"   유대감 강화율: {statistics['bond_strengthening_rate']:.2f}")
    print(f"   감정별 통계: {statistics['emotion_statistics']}")
    
    # 5. 데이터 내보내기
    export_data = emotional_system.export_emotional_data()
    print(f"✅ 감정적 대화 데이터 내보내기: {len(export_data['emotional_conversations'])}개 대화")
    
    print("🎉 EmotionalConversationSystem 테스트 완료!")

if __name__ == "__main__":
    test_emotional_conversation_system() 