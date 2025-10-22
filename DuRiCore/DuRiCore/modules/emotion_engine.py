#!/usr/bin/env python3
"""
DuRiCore - 감정 엔진
LLM 기반 감정 분석 및 공감 능력 구현
"""

import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class EmotionalAnalysis:
    """감정 분석 결과"""

    primary_emotion: str
    secondary_emotions: List[str]
    intensity: float
    confidence: float
    context_fit: float
    emotion_reason_balance: Dict[str, Any]
    empathetic_response: str
    analysis_timestamp: datetime


class LLMInterface:
    """LLM 인터페이스 - 실제 AI 모델과 연결"""

    def __init__(self):
        # TODO: 실제 LLM API 연결 (OpenAI, Claude 등)
        self.model_name = "gpt-4"  # 또는 "claude-3-sonnet"
        self.api_key = None  # 환경변수에서 로드

    def analyze_emotion(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """LLM 기반 감정 분석"""
        # TODO: 실제 LLM 호출
        # 임시로 기존 로직 사용
        return self._fallback_emotion_analysis(text, context)

    def _fallback_emotion_analysis(self, text: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """LLM 연결 전 임시 감정 분석"""
        # 기존 emotional_intelligence_service.py 로직 활용
        emotion_dimensions = [
            "joy",
            "anger",
            "fear",
            "trust",
            "surprise",
            "sadness",
            "anticipation",
            "disgust",
        ]

        # 간단한 키워드 기반 분석
        emotion_scores = {dim: 0.0 for dim in emotion_dimensions}

        # 기본 감정 매핑
        emotion_keywords = {
            "joy": ["행복", "기쁨", "즐거움", "웃음", "좋아"],
            "anger": ["화나", "분노", "짜증", "열받", "화"],
            "fear": ["무서워", "두려워", "겁나", "불안", "걱정"],
            "trust": ["믿어", "신뢰", "안전", "믿음"],
            "surprise": ["놀라", "깜짝", "어?", "뭐?"],
            "sadness": ["슬퍼", "우울", "속상", "아픔", "눈물"],
            "anticipation": ["기대", "설렘", "기다려", "궁금"],
            "disgust": ["역겨워", "싫어", "징그러워", "혐오"],
        }

        # 텍스트에서 감정 키워드 검색
        for emotion, keywords in emotion_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    emotion_scores[emotion] += 0.3

        # 주요 감정 결정
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]
        intensity = min(1.0, max(emotion_scores.values()))

        return {
            "primary_emotion": primary_emotion,
            "secondary_emotions": [
                k for k, v in emotion_scores.items() if v > 0.1 and k != primary_emotion
            ],
            "intensity": intensity,
            "emotion_scores": emotion_scores,
            "confidence": 0.7,  # 임시 값
        }


class EmotionEngine:
    """감정 엔진 - LLM 기반 감정 분석 및 공감 능력"""

    def __init__(self):
        self.emotion_dimensions = [
            "joy",
            "anger",
            "fear",
            "trust",
            "surprise",
            "sadness",
            "anticipation",
            "disgust",
        ]
        self.emotion_weights = {
            "joy": 0.8,
            "anger": -0.6,
            "fear": -0.7,
            "trust": 0.9,
            "surprise": 0.3,
            "sadness": -0.8,
            "anticipation": 0.6,
            "disgust": -0.5,
        }
        self.llm_interface = LLMInterface()

    def analyze_complex_emotion(self, input_data: Dict[str, Any]) -> EmotionalAnalysis:
        """LLM 기반 복합 감정 분석"""
        try:
            # 입력 데이터 추출
            text = input_data.get("text", "")
            context = input_data.get("context", {})

            # 1. LLM 기반 감정 분석
            llm_analysis = self.llm_interface.analyze_emotion(text, context)

            # 2. 복합 감정 분석
            complex_analysis = self._analyze_emotion_combination(
                llm_analysis["primary_emotion"],
                llm_analysis["secondary_emotions"],
                llm_analysis["intensity"],
            )

            # 3. 맥락 기반 감정 해석
            contextual_emotion = self._analyze_contextual_emotion(complex_analysis, context)

            # 4. 감정-이성 균형 계산
            emotion_reason_balance = self._calculate_emotion_reason_balance(
                contextual_emotion, context
            )

            # 5. 공감적 반응 생성
            empathetic_response = self._generate_empathetic_response(
                contextual_emotion, emotion_reason_balance
            )

            # 6. 분석 결과 생성
            return EmotionalAnalysis(
                primary_emotion=llm_analysis["primary_emotion"],
                secondary_emotions=llm_analysis["secondary_emotions"],
                intensity=llm_analysis["intensity"],
                confidence=llm_analysis["confidence"],
                context_fit=contextual_emotion.get("context_fit", 0.5),
                emotion_reason_balance=emotion_reason_balance,
                empathetic_response=empathetic_response,
                analysis_timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"복합 감정 분석 실패: {e}")
            # 기본 응답 반환
            return EmotionalAnalysis(
                primary_emotion="neutral",
                secondary_emotions=[],
                intensity=0.0,
                confidence=0.0,
                context_fit=0.0,
                emotion_reason_balance={
                    "balance_type": "neutral",
                    "recommendation": "관찰 필요",
                },
                empathetic_response="감정을 더 자세히 이해하고 싶어요.",
                analysis_timestamp=datetime.now(),
            )

    def _analyze_emotion_combination(
        self, primary: str, secondary: List[str], intensity: float
    ) -> Dict[str, Any]:
        """감정 조합 분석"""
        try:
            # 감정 벡터 생성
            emotion_vector = {dim: 0.0 for dim in self.emotion_dimensions}

            # 주요 감정 설정
            if primary in self.emotion_dimensions:
                emotion_vector[primary] = intensity

            # 보조 감정들 추가
            for sec_emotion in secondary:
                if sec_emotion in self.emotion_dimensions:
                    emotion_vector[sec_emotion] = min(intensity * 0.7, 1.0)

            # 감정 충돌 분석
            conflicts = self._detect_emotion_conflicts(emotion_vector)

            # 감정 안정성 계산
            stability = self._calculate_emotion_stability(emotion_vector)

            # 복합 감정 타입 결정
            complex_type = self._determine_complex_emotion_type(emotion_vector)

            return {
                "emotion_vector": emotion_vector,
                "conflicts": conflicts,
                "stability": stability,
                "complex_type": complex_type,
                "intensity": intensity,
            }

        except Exception as e:
            logger.error(f"감정 조합 분석 실패: {e}")
            return {"error": str(e)}

    def _detect_emotion_conflicts(self, emotion_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """감정 충돌 탐지"""
        conflicts = []

        # 상반되는 감정들
        opposing_pairs = [
            ("joy", "sadness"),
            ("trust", "fear"),
            ("anger", "joy"),
            ("anticipation", "disgust"),
        ]

        for emotion1, emotion2 in opposing_pairs:
            if emotion_vector[emotion1] > 0.3 and emotion_vector[emotion2] > 0.3:
                conflicts.append(
                    {
                        "conflict_type": "opposing_emotions",
                        "emotions": [emotion1, emotion2],
                        "intensity": (emotion_vector[emotion1] + emotion_vector[emotion2]) / 2,
                    }
                )

        return conflicts

    def _calculate_emotion_stability(self, emotion_vector: Dict[str, float]) -> float:
        """감정 안정성 계산"""
        try:
            # 활성화된 감정 수
            active_emotions = sum(1 for v in emotion_vector.values() if v > 0.1)

            # 감정 강도 분산
            intensities = [v for v in emotion_vector.values() if v > 0.1]
            if not intensities:
                return 1.0

            variance = np.var(intensities)

            # 안정성 점수 계산 (감정 수가 적고, 강도가 균등할수록 안정적)
            stability = max(0.0, 1.0 - (active_emotions - 1) * 0.2 - variance * 0.5)

            return min(1.0, stability)

        except Exception as e:
            logger.error(f"감정 안정성 계산 실패: {e}")
            return 0.5

    def _determine_complex_emotion_type(self, emotion_vector: Dict[str, float]) -> str:
        """복합 감정 타입 결정"""
        active_emotions = [(k, v) for k, v in emotion_vector.items() if v > 0.1]

        if len(active_emotions) == 0:
            return "neutral"
        elif len(active_emotions) == 1:
            return "simple"
        elif len(active_emotions) == 2:
            return "dual"
        else:
            return "complex"

    def _analyze_contextual_emotion(
        self, complex_analysis: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """맥락 기반 감정 해석"""
        try:
            emotion_vector = complex_analysis.get("emotion_vector", {})
            context_type = context.get("type", "general")

            interpretation = {
                "context_type": context_type,
                "emotion_vector": emotion_vector,
                "context_fit": 0.5,  # 기본값
                "recommendations": [],
            }

            # 맥락별 해석
            if context_type == "work":
                interpretation.update(self._interpret_work_emotion(emotion_vector, context))
            elif context_type == "social":
                interpretation.update(self._interpret_social_emotion(emotion_vector, context))
            elif context_type == "personal":
                interpretation.update(self._interpret_personal_emotion(emotion_vector, context))

            # 맥락 적합성 평가
            context_fit = self._evaluate_context_fit(emotion_vector, context)
            interpretation["context_fit"] = context_fit

            # 권장사항 생성
            recommendations = self._generate_context_recommendations(interpretation, context_fit)
            interpretation["recommendations"] = recommendations

            return interpretation

        except Exception as e:
            logger.error(f"맥락 기반 감정 해석 실패: {e}")
            return {"error": str(e)}

    def _interpret_work_emotion(
        self, emotion_vector: Dict[str, float], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """업무 맥락 감정 해석"""
        return {
            "work_impact": "neutral",
            "productivity_effect": 0.5,
            "stress_level": emotion_vector.get("fear", 0.0) + emotion_vector.get("anger", 0.0),
        }

    def _interpret_social_emotion(
        self, emotion_vector: Dict[str, float], social_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """사회적 맥락 감정 해석"""
        return {
            "social_comfort": 1.0
            - (emotion_vector.get("fear", 0.0) + emotion_vector.get("anger", 0.0)),
            "empathy_level": emotion_vector.get("trust", 0.0) + emotion_vector.get("joy", 0.0),
        }

    def _interpret_personal_emotion(
        self, emotion_vector: Dict[str, float], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개인적 맥락 감정 해석"""
        return {
            "personal_wellbeing": emotion_vector.get("joy", 0.0)
            - emotion_vector.get("sadness", 0.0),
            "self_awareness": 0.7,  # 기본값
        }

    def _evaluate_context_fit(
        self, emotion_vector: Dict[str, float], context: Dict[str, Any]
    ) -> float:
        """맥락 적합성 평가"""
        try:
            context_type = context.get("type", "general")

            # 맥락별 적합성 기준
            fit_criteria = {
                "work": ["trust", "anticipation"],  # 업무에 적합한 감정
                "social": ["joy", "trust"],  # 사회적 상호작용에 적합한 감정
                "personal": ["joy", "anticipation"],  # 개인적 상황에 적합한 감정
            }

            if context_type not in fit_criteria:
                return 0.5

            positive_emotions = fit_criteria[context_type]
            negative_emotions = ["anger", "fear", "sadness", "disgust"]

            # 긍정적 감정 점수
            positive_score = sum(emotion_vector.get(emotion, 0.0) for emotion in positive_emotions)

            # 부정적 감정 점수
            negative_score = sum(emotion_vector.get(emotion, 0.0) for emotion in negative_emotions)

            # 적합성 계산
            fit_score = max(0.0, positive_score - negative_score)

            return min(1.0, fit_score)

        except Exception as e:
            logger.error(f"맥락 적합성 평가 실패: {e}")
            return 0.5

    def _generate_context_recommendations(
        self, interpretation: Dict[str, Any], context_fit: float
    ) -> List[str]:
        """맥락별 권장사항 생성"""
        recommendations = []

        if context_fit < 0.3:
            recommendations.append(
                "현재 감정 상태가 맥락에 적합하지 않습니다. 잠시 휴식을 취하는 것을 고려해보세요."
            )
        elif context_fit < 0.6:
            recommendations.append("감정 상태를 조절하여 더 나은 적응을 시도해보세요.")
        else:
            recommendations.append("현재 감정 상태가 맥락에 잘 적합합니다.")

        return recommendations

    def _calculate_emotion_reason_balance(
        self, contextual_emotion: Dict[str, Any], context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정-이성 균형 계산"""
        try:
            emotion_vector = contextual_emotion.get("emotion_vector", {})

            # 감정 강도 계산
            emotion_intensity = sum(emotion_vector.values())

            # 이성 강도 (감정의 반대)
            reason_intensity = max(0.0, 1.0 - emotion_intensity)

            # 균형 타입 결정
            if emotion_intensity > 0.7:
                balance_type = "emotion_dominant"
            elif reason_intensity > 0.7:
                balance_type = "reason_dominant"
            else:
                balance_type = "balanced"

            # 권장사항 생성
            recommendation = self._get_balance_recommendation(balance_type)

            return {
                "emotion_intensity": emotion_intensity,
                "reason_intensity": reason_intensity,
                "balance_type": balance_type,
                "recommendation": recommendation,
                "balance_score": abs(emotion_intensity - reason_intensity),
            }

        except Exception as e:
            logger.error(f"감정-이성 균형 계산 실패: {e}")
            return {
                "emotion_intensity": 0.5,
                "reason_intensity": 0.5,
                "balance_type": "balanced",
                "recommendation": "균형을 유지하세요.",
                "balance_score": 0.0,
            }

    def _get_balance_recommendation(self, balance_type: str) -> str:
        """균형 타입별 권장사항"""
        recommendations = {
            "emotion_dominant": "감정이 강합니다. 잠시 차분히 생각해보는 것이 좋겠어요.",
            "reason_dominant": "이성이 우세합니다. 감정도 함께 고려해보세요.",
            "balanced": "감정과 이성이 균형을 이루고 있습니다.",
        }
        return recommendations.get(balance_type, "균형을 유지하세요.")

    def _generate_empathetic_response(
        self, contextual_emotion: Dict[str, Any], balance: Dict[str, Any]
    ) -> str:
        """공감적 반응 생성"""
        try:
            interpretation = contextual_emotion
            balance_type = balance.get("balance_type", "balanced")

            # 공감 수준 계산
            empathy_level = self._calculate_empathy_level(interpretation, balance_type)

            # 공감적 반응 생성
            response = self._create_empathetic_response(interpretation, empathy_level, balance_type)

            return response

        except Exception as e:
            logger.error(f"공감적 반응 생성 실패: {e}")
            return "당신의 감정을 이해하고 있어요."

    def _calculate_empathy_level(self, interpretation: Dict[str, Any], balance_type: str) -> float:
        """공감 수준 계산"""
        try:
            context_fit = interpretation.get("context_fit", 0.5)

            # 기본 공감 수준
            base_empathy = 0.7

            # 맥락 적합성에 따른 조정
            context_adjustment = (context_fit - 0.5) * 0.3

            # 균형 타입에 따른 조정
            balance_adjustment = {
                "emotion_dominant": 0.2,
                "reason_dominant": -0.1,
                "balanced": 0.0,
            }.get(balance_type, 0.0)

            empathy_level = base_empathy + context_adjustment + balance_adjustment

            return max(0.0, min(1.0, empathy_level))

        except Exception as e:
            logger.error(f"공감 수준 계산 실패: {e}")
            return 0.7

    def _create_empathetic_response(
        self, interpretation: Dict[str, Any], empathy_level: float, balance_type: str
    ) -> str:
        """공감적 반응 생성"""
        try:
            context_type = interpretation.get("context_type", "general")

            # 기본 공감 표현
            base_responses = {
                "work": "업무 상황에서 그런 감정을 느끼시는군요.",
                "social": "사람들과의 관계에서 그런 마음이 드시는군요.",
                "personal": "개인적으로 그런 감정을 경험하고 계시는군요.",
                "general": "그런 감정을 느끼고 계시는군요.",
            }

            base_response = base_responses.get(context_type, base_responses["general"])

            # 공감 수준에 따른 조정
            if empathy_level > 0.8:
                response = f"정말 {base_response} 완전히 이해해요."
            elif empathy_level > 0.6:
                response = f"{base_response} 이해가 돼요."
            else:
                response = f"{base_response} 더 자세히 들려주세요."

            # 균형 타입에 따른 추가 조언
            if balance_type == "emotion_dominant":
                response += " 잠시 차분히 생각해보는 것도 좋을 것 같아요."
            elif balance_type == "reason_dominant":
                response += " 감정도 함께 고려해보세요."

            return response

        except Exception as e:
            logger.error(f"공감적 반응 생성 실패: {e}")
            return "당신의 감정을 이해하고 있어요."

    def get_emotional_intelligence_stats(self) -> Dict[str, Any]:
        """감정 지능 통계"""
        return {
            "total_analyses": 0,  # TODO: 실제 통계 구현
            "average_confidence": 0.7,
            "most_common_emotion": "neutral",
            "stability_trend": "stable",
            "last_analysis": datetime.now().isoformat(),
        }
