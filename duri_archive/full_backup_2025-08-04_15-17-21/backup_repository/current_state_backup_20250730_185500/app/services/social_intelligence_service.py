"""
Day 10: 사회적 지능 시스템
DuRi가 인간과 자연스럽게 소통하고 협력하는 능력 구현
"""

import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session

# from ..models.memory import MemoryEntry
# from ..utils.retry_decorator import retry_on_db_error

logger = logging.getLogger(__name__)


class SocialIntelligenceService:
    """사회적 지능 서비스 - DuRi가 인간과 상호작용하는 능력"""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.conversation_context = {}
        self.social_norms = {
            "politeness": 0.8,
            "empathy": 0.9,
            "cooperation": 0.85,
            "adaptability": 0.75,
        }
        self.emotion_weights = {
            "joy": 0.8,
            "sadness": -0.6,
            "anger": -0.7,
            "fear": -0.5,
            "trust": 0.9,
            "surprise": 0.3,
            "anticipation": 0.6,
            "disgust": -0.4,
        }

    def process_conversation(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """대화 처리 및 응답 생성"""
        try:
            # 1. 사용자 입력 분석
            input_analysis = self._analyze_user_input(user_input)

            # 2. 맥락 이해
            context_understanding = self._understand_context(input_analysis)

            # 3. 감정 상태 분석
            emotional_state = self._analyze_emotional_state(input_analysis)

            # 4. 적절한 응답 생성
            response = self._generate_appropriate_response(
                input_analysis, context_understanding, emotional_state
            )

            # 5. 협력 기회 탐지
            collaboration_opportunity = self._detect_collaboration_opportunity(
                input_analysis, context_understanding
            )

            # 6. 대화 맥락 업데이트
            self._update_conversation_context(user_input, response)

            return {
                "response": response,
                "context_understanding": context_understanding,
                "emotional_state": emotional_state,
                "collaboration_opportunity": collaboration_opportunity,
                "social_intelligence_score": self._calculate_social_intelligence_score(
                    input_analysis, context_understanding, response
                ),
            }

        except Exception as e:
            logger.error(f"대화 처리 실패: {e}")
            return {"error": str(e)}

    def _analyze_user_input(self, user_input: Dict[str, Any]) -> Dict[str, Any]:
        """사용자 입력 분석"""
        try:
            text = user_input.get("text", "")
            user_id = user_input.get("user_id", "unknown")
            timestamp = user_input.get("timestamp", datetime.now())

            # 1. 의도 분석
            intent = self._detect_intent(text)

            # 2. 감정 분석
            emotions = self._detect_emotions(text)

            # 3. 중요도 분석
            importance = self._analyze_importance(text, intent, emotions)

            # 4. 긴급성 분석
            urgency = self._analyze_urgency(text, intent, emotions)

            # 5. 협력 필요성 분석
            collaboration_needed = self._analyze_collaboration_need(text, intent)

            return {
                "text": text,
                "user_id": user_id,
                "timestamp": timestamp,
                "intent": intent,
                "emotions": emotions,
                "importance": importance,
                "urgency": urgency,
                "collaboration_needed": collaboration_needed,
                "analysis_confidence": self._calculate_analysis_confidence(
                    intent, emotions
                ),
            }

        except Exception as e:
            logger.error(f"사용자 입력 분석 실패: {e}")
            return {}

    def _detect_intent(self, text: str) -> Dict[str, Any]:
        """의도 감지"""
        try:
            intent_patterns = {
                "question": [
                    r"\?",
                    r"어떻게",
                    r"무엇",
                    r"언제",
                    r"어디",
                    r"왜",
                    r"어떤",
                ],
                "request": [r"도와주세요", r"부탁", r"해주세요", r"필요해"],
                "greeting": [r"안녕", r"반가워", r"좋은", r"하루"],
                "complaint": [r"문제", r"불만", r"어려워", r"힘들어", r"짜증"],
                "appreciation": [r"감사", r"고마워", r"좋아", r"훌륭해"],
                "collaboration": [r"함께", r"협력", r"도움", r"같이", r"협업"],
            }

            detected_intents = []
            for intent_type, patterns in intent_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, text, re.IGNORECASE):
                        detected_intents.append(intent_type)
                        break

            # 주요 의도 결정
            primary_intent = detected_intents[0] if detected_intents else "general"

            return {
                "primary_intent": primary_intent,
                "all_intents": detected_intents,
                "confidence": len(detected_intents) / len(intent_patterns),
            }

        except Exception as e:
            logger.error(f"의도 감지 실패: {e}")
            return {"primary_intent": "unknown", "all_intents": [], "confidence": 0.0}

    def _detect_emotions(self, text: str) -> Dict[str, float]:
        """감정 감지"""
        try:
            emotion_keywords = {
                "joy": ["기쁘", "행복", "좋아", "즐거", "신나"],
                "sadness": ["슬프", "우울", "속상", "힘들", "지치"],
                "anger": ["화나", "짜증", "분노", "열받", "빡치"],
                "fear": ["무서", "겁나", "걱정", "불안", "두려"],
                "trust": ["믿어", "신뢰", "안전", "확실"],
                "surprise": ["놀라", "깜짝", "어이", "헐"],
                "anticipation": ["기대", "설렘", "궁금", "궁금해"],
                "disgust": ["역겨", "싫어", "짜증", "불쾌"],
            }

            emotions = {}
            for emotion, keywords in emotion_keywords.items():
                count = sum(1 for keyword in keywords if keyword in text)
                if count > 0:
                    emotions[emotion] = min(1.0, count / len(keywords))

            return emotions

        except Exception as e:
            logger.error(f"감정 감지 실패: {e}")
            return {}

    def _analyze_importance(
        self, text: str, intent: Dict[str, Any], emotions: Dict[str, float]
    ) -> float:
        """중요도 분석"""
        try:
            # 의도 기반 중요도
            intent_importance = {
                "question": 0.7,
                "request": 0.8,
                "greeting": 0.3,
                "complaint": 0.9,
                "appreciation": 0.6,
                "collaboration": 0.85,
                "general": 0.5,
            }

            # 감정 기반 중요도
            emotion_importance = sum(
                self.emotion_weights.get(emotion, 0) * intensity
                for emotion, intensity in emotions.items()
            )

            # 텍스트 길이 기반 중요도
            length_importance = min(1.0, len(text) / 100.0)

            # 종합 중요도 계산
            importance = (
                intent_importance.get(intent.get("primary_intent", "general"), 0.5)
                * 0.4
                + emotion_importance * 0.3
                + length_importance * 0.3
            )

            return max(0.0, min(1.0, importance))

        except Exception as e:
            logger.error(f"중요도 분석 실패: {e}")
            return 0.5

    def _analyze_urgency(
        self, text: str, intent: Dict[str, Any], emotions: Dict[str, float]
    ) -> float:
        """긴급성 분석"""
        try:
            urgency_keywords = ["급해", "바로", "즉시", "당장", "빨리", "시급", "긴급"]
            urgency_count = sum(1 for keyword in urgency_keywords if keyword in text)

            # 의도 기반 긴급성
            intent_urgency = {
                "complaint": 0.8,
                "request": 0.6,
                "question": 0.4,
                "greeting": 0.1,
                "appreciation": 0.2,
                "collaboration": 0.5,
            }

            # 감정 기반 긴급성 (부정적 감정이 높을수록 긴급)
            negative_emotions = ["sadness", "anger", "fear", "disgust"]
            emotion_urgency = sum(
                emotions.get(emotion, 0) for emotion in negative_emotions
            )

            urgency = (
                min(1.0, urgency_count / 3.0) * 0.4
                + intent_urgency.get(intent.get("primary_intent", "general"), 0.3) * 0.3
                + emotion_urgency * 0.3
            )

            return max(0.0, min(1.0, urgency))

        except Exception as e:
            logger.error(f"긴급성 분석 실패: {e}")
            return 0.3

    def _analyze_collaboration_need(
        self, text: str, intent: Dict[str, Any]
    ) -> Dict[str, Any]:
        """협력 필요성 분석"""
        try:
            collaboration_keywords = [
                "함께",
                "협력",
                "도움",
                "같이",
                "협업",
                "팀",
                "함께해",
            ]
            collaboration_count = sum(
                1 for keyword in collaboration_keywords if keyword in text
            )

            # 의도 기반 협력 필요성
            intent_collaboration = {
                "collaboration": 0.9,
                "request": 0.7,
                "question": 0.4,
                "complaint": 0.6,
                "greeting": 0.1,
                "appreciation": 0.3,
            }

            collaboration_score = (
                min(1.0, collaboration_count / 3.0) * 0.6
                + intent_collaboration.get(intent.get("primary_intent", "general"), 0.3)
                * 0.4
            )

            return {
                "needed": bool(collaboration_score > 0.5),
                "score": float(collaboration_score),
                "type": (
                    "active"
                    if collaboration_score > 0.7
                    else "passive" if collaboration_score > 0.4 else "none"
                ),
            }

        except Exception as e:
            logger.error(f"협력 필요성 분석 실패: {e}")
            return {"needed": False, "score": 0.0, "type": "none"}

    def _calculate_analysis_confidence(
        self, intent: Dict[str, Any], emotions: Dict[str, float]
    ) -> float:
        """분석 신뢰도 계산"""
        try:
            intent_confidence = intent.get("confidence", 0.0)
            emotion_confidence = len(emotions) / 8.0  # 8가지 기본 감정 대비

            confidence = intent_confidence * 0.6 + emotion_confidence * 0.4
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.error(f"분석 신뢰도 계산 실패: {e}")
            return 0.5

    def _understand_context(self, input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """맥락 이해"""
        try:
            # 1. 대화 맥락 분석
            conversation_context = self._analyze_conversation_context(input_analysis)

            # 2. 사회적 맥락 분석
            social_context = self._analyze_social_context(input_analysis)

            # 3. 상황별 적절성 분석
            situational_appropriateness = self._analyze_situational_appropriateness(
                input_analysis, conversation_context, social_context
            )

            # 4. 응답 우선순위 결정
            response_priority = self._determine_response_priority(
                input_analysis, conversation_context, social_context
            )

            return {
                "conversation_context": conversation_context,
                "social_context": social_context,
                "situational_appropriateness": situational_appropriateness,
                "response_priority": response_priority,
                "context_confidence": self._calculate_context_confidence(
                    conversation_context, social_context
                ),
            }

        except Exception as e:
            logger.error(f"맥락 이해 실패: {e}")
            return {}

    def _analyze_conversation_context(
        self, input_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """대화 맥락 분석"""
        try:
            # 대화 히스토리 분석 (실제로는 DB에서 조회)
            conversation_history = {
                "turn_count": 3,  # 예시 데이터
                "topic_consistency": 0.8,
                "user_engagement": 0.7,
                "conversation_flow": "smooth",
            }

            # 현재 대화 상태
            current_state = {
                "user_emotion": input_analysis.get("emotions", {}),
                "user_intent": input_analysis.get("intent", {}),
                "conversation_stage": "middle",  # beginning, middle, end
                "topic": "general",
            }

            return {
                "history": conversation_history,
                "current_state": current_state,
                "continuity": 0.8,
            }

        except Exception as e:
            logger.error(f"대화 맥락 분석 실패: {e}")
            return {}

    def _analyze_social_context(self, input_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """사회적 맥락 분석"""
        try:
            # 사회적 규범 준수도
            social_norms_compliance = {
                "politeness": self.social_norms["politeness"],
                "empathy": self.social_norms["empathy"],
                "cooperation": self.social_norms["cooperation"],
                "adaptability": self.social_norms["adaptability"],
            }

            # 상황별 적절성
            situational_appropriateness = {
                "formal": 0.7,
                "casual": 0.8,
                "professional": 0.9,
                "personal": 0.6,
            }

            # 사용자 관계 분석
            user_relationship = {
                "familiarity": 0.6,  # 친밀도
                "trust_level": 0.7,  # 신뢰도
                "interaction_frequency": 0.5,  # 상호작용 빈도
            }

            return {
                "social_norms": social_norms_compliance,
                "situational_appropriateness": situational_appropriateness,
                "user_relationship": user_relationship,
                "overall_social_score": np.mean(list(social_norms_compliance.values())),
            }

        except Exception as e:
            logger.error(f"사회적 맥락 분석 실패: {e}")
            return {}

    def _analyze_situational_appropriateness(
        self,
        input_analysis: Dict[str, Any],
        conversation_context: Dict[str, Any],
        social_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """상황별 적절성 분석"""
        try:
            intent = input_analysis.get("intent", {})
            emotions = input_analysis.get("emotions", {})

            # 의도별 적절한 응답 스타일
            appropriate_styles = {
                "question": "informative",
                "request": "helpful",
                "greeting": "friendly",
                "complaint": "empathetic",
                "appreciation": "grateful",
                "collaboration": "cooperative",
            }

            # 감정별 적절한 톤
            emotion_appropriate_tones = {
                "joy": "positive",
                "sadness": "supportive",
                "anger": "calming",
                "fear": "reassuring",
                "trust": "confident",
                "surprise": "excited",
                "anticipation": "encouraging",
                "disgust": "neutral",
            }

            primary_intent = intent.get("primary_intent", "general")
            primary_emotion = (
                max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
            )

            return {
                "style": appropriate_styles.get(primary_intent, "general"),
                "tone": emotion_appropriate_tones.get(primary_emotion, "neutral"),
                "formality_level": "medium",
                "response_length": "appropriate",
            }

        except Exception as e:
            logger.error(f"상황별 적절성 분석 실패: {e}")
            return {}

    def _determine_response_priority(
        self,
        input_analysis: Dict[str, Any],
        conversation_context: Dict[str, Any],
        social_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """응답 우선순위 결정"""
        try:
            importance = input_analysis.get("importance", 0.5)
            urgency = input_analysis.get("urgency", 0.3)
            collaboration_needed = input_analysis.get("collaboration_needed", {})

            # 우선순위 계산
            priority_score = (
                importance * 0.4
                + urgency * 0.4
                + (collaboration_needed.get("score", 0) * 0.2)
            )

            # 우선순위 레벨 결정
            if priority_score > 0.8:
                priority_level = "high"
            elif priority_score > 0.5:
                priority_level = "medium"
            else:
                priority_level = "low"

            return {
                "score": float(priority_score),
                "level": priority_level,
                "response_time": "immediate" if priority_score > 0.8 else "normal",
                "attention_required": bool(priority_score > 0.7),
            }

        except Exception as e:
            logger.error(f"응답 우선순위 결정 실패: {e}")
            return {}

    def _calculate_context_confidence(
        self, conversation_context: Dict[str, Any], social_context: Dict[str, Any]
    ) -> float:
        """맥락 이해 신뢰도 계산"""
        try:
            conv_confidence = conversation_context.get("continuity", 0.5)
            social_confidence = social_context.get("overall_social_score", 0.5)

            confidence = conv_confidence * 0.6 + social_confidence * 0.4
            return max(0.0, min(1.0, confidence))

        except Exception as e:
            logger.error(f"맥락 이해 신뢰도 계산 실패: {e}")
            return 0.5

    def _analyze_emotional_state(
        self, input_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정 상태 분석"""
        try:
            emotions = input_analysis.get("emotions", {})

            if not emotions:
                return {
                    "primary_emotion": "neutral",
                    "emotion_intensity": 0.0,
                    "emotional_state": "stable",
                    "response_approach": "neutral",
                }

            # 주요 감정 결정
            primary_emotion = max(emotions.items(), key=lambda x: x[1])[0]
            emotion_intensity = emotions[primary_emotion]

            # 감정 상태 분류
            if emotion_intensity > 0.7:
                emotional_state = "intense"
            elif emotion_intensity > 0.4:
                emotional_state = "moderate"
            else:
                emotional_state = "mild"

            # 응답 접근법 결정
            response_approaches = {
                "joy": "encouraging",
                "sadness": "supportive",
                "anger": "calming",
                "fear": "reassuring",
                "trust": "confident",
                "surprise": "excited",
                "anticipation": "encouraging",
                "disgust": "neutral",
            }

            return {
                "primary_emotion": primary_emotion,
                "emotion_intensity": float(emotion_intensity),
                "emotional_state": emotional_state,
                "response_approach": response_approaches.get(
                    primary_emotion, "neutral"
                ),
                "all_emotions": emotions,
            }

        except Exception as e:
            logger.error(f"감정 상태 분석 실패: {e}")
            return {}

    def _generate_appropriate_response(
        self,
        input_analysis: Dict[str, Any],
        context_understanding: Dict[str, Any],
        emotional_state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """적절한 응답 생성"""
        try:
            intent = input_analysis.get("intent", {})
            primary_intent = intent.get("primary_intent", "general")
            emotional_state_info = emotional_state.get("emotional_state", "stable")
            response_approach = emotional_state.get("response_approach", "neutral")

            # 의도별 응답 템플릿
            response_templates = {
                "question": {
                    "content": "질문에 대한 명확하고 도움이 되는 답변을 제공합니다.",
                    "tone": "helpful",
                    "style": "informative",
                },
                "request": {
                    "content": "요청사항을 이해하고 적극적으로 도움을 제공합니다.",
                    "tone": "helpful",
                    "style": "cooperative",
                },
                "greeting": {
                    "content": "친근하고 따뜻한 인사로 응답합니다.",
                    "tone": "friendly",
                    "style": "casual",
                },
                "complaint": {
                    "content": "불만사항을 공감하고 해결책을 제시합니다.",
                    "tone": "empathetic",
                    "style": "supportive",
                },
                "appreciation": {
                    "content": "감사함을 표현하고 상호작용을 강화합니다.",
                    "tone": "grateful",
                    "style": "positive",
                },
                "collaboration": {
                    "content": "협력 의지를 표현하고 구체적인 협업 방안을 제시합니다.",
                    "tone": "enthusiastic",
                    "style": "cooperative",
                },
            }

            template = response_templates.get(
                primary_intent,
                {
                    "content": "적절한 응답을 제공합니다.",
                    "tone": "neutral",
                    "style": "general",
                },
            )

            # 감정 상태에 따른 응답 조정
            if emotional_state_info == "intense":
                template["tone"] = (
                    "calming" if primary_intent == "complaint" else "enthusiastic"
                )

            return {
                "content": template["content"],
                "tone": template["tone"],
                "style": template["style"],
                "approach": response_approach,
                "confidence": float(input_analysis.get("analysis_confidence", 0.5)),
            }

        except Exception as e:
            logger.error(f"적절한 응답 생성 실패: {e}")
            return {}

    def _detect_collaboration_opportunity(
        self, input_analysis: Dict[str, Any], context_understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """협력 기회 탐지"""
        try:
            collaboration_needed = input_analysis.get("collaboration_needed", {})
            intent = input_analysis.get("intent", {})

            # 협력 기회 판단
            if collaboration_needed.get("needed", False):
                opportunity_type = "explicit"
                confidence = 0.9
            elif intent.get("primary_intent") in ["request", "question"]:
                opportunity_type = "implicit"
                confidence = 0.6
            else:
                opportunity_type = "none"
                confidence = 0.1

            # 협력 방식 제안
            collaboration_methods = {
                "explicit": ["직접 협력", "함께 작업", "팀워크"],
                "implicit": ["간접 지원", "정보 제공", "가이드"],
                "none": [],
            }

            return {
                "detected": bool(opportunity_type != "none"),
                "type": opportunity_type,
                "confidence": float(confidence),
                "suggested_methods": collaboration_methods.get(opportunity_type, []),
                "priority": "high" if opportunity_type == "explicit" else "medium",
            }

        except Exception as e:
            logger.error(f"협력 기회 탐지 실패: {e}")
            return {}

    def _update_conversation_context(
        self, user_input: Dict[str, Any], response: Dict[str, Any]
    ):
        """대화 맥락 업데이트"""
        try:
            user_id = user_input.get("user_id", "unknown")

            if user_id not in self.conversation_context:
                self.conversation_context[user_id] = {
                    "conversation_history": [],
                    "user_preferences": {},
                    "interaction_patterns": {},
                }

            # 대화 히스토리 업데이트
            self.conversation_context[user_id]["conversation_history"].append(
                {
                    "user_input": user_input,
                    "response": response,
                    "timestamp": datetime.now(),
                }
            )

            # 최근 10개 대화만 유지
            if len(self.conversation_context[user_id]["conversation_history"]) > 10:
                self.conversation_context[user_id]["conversation_history"] = (
                    self.conversation_context[user_id]["conversation_history"][-10:]
                )

        except Exception as e:
            logger.error(f"대화 맥락 업데이트 실패: {e}")

    def _calculate_social_intelligence_score(
        self,
        input_analysis: Dict[str, Any],
        context_understanding: Dict[str, Any],
        response: Dict[str, Any],
    ) -> float:
        """사회적 지능 점수 계산"""
        try:
            # 분석 정확도
            analysis_accuracy = input_analysis.get("analysis_confidence", 0.5)

            # 맥락 이해도
            context_accuracy = context_understanding.get("context_confidence", 0.5)

            # 응답 적절성
            response_appropriateness = response.get("confidence", 0.5)

            # 사회적 규범 준수도
            social_norms_compliance = np.mean(list(self.social_norms.values()))

            # 종합 점수 계산
            score = (
                analysis_accuracy * 0.3
                + context_accuracy * 0.3
                + response_appropriateness * 0.2
                + social_norms_compliance * 0.2
            )

            return float(max(0.0, min(100.0, score * 100)))

        except Exception as e:
            logger.error(f"사회적 지능 점수 계산 실패: {e}")
            return 50.0

    def get_social_intelligence_stats(self) -> Dict[str, Any]:
        """사회적 지능 통계 조회"""
        try:
            # 대화 통계
            conversation_stats = {
                "total_conversations": len(self.conversation_context),
                "active_users": len(
                    [
                        k
                        for k, v in self.conversation_context.items()
                        if len(v.get("conversation_history", [])) > 0
                    ]
                ),
                "average_conversation_length": 3.5,  # 예시 데이터
            }

            # 사회적 지능 점수
            social_intelligence_scores = {
                "politeness": self.social_norms["politeness"] * 100,
                "empathy": self.social_norms["empathy"] * 100,
                "cooperation": self.social_norms["cooperation"] * 100,
                "adaptability": self.social_norms["adaptability"] * 100,
            }

            return {
                "conversation_stats": conversation_stats,
                "social_intelligence_scores": social_intelligence_scores,
                "overall_social_score": np.mean(
                    list(social_intelligence_scores.values())
                ),
            }

        except Exception as e:
            logger.error(f"사회적 지능 통계 조회 실패: {e}")
            return {}
