#!/usr/bin/env python3
"""
DuRi 감정 인식 및 적응 모듈
맥락 정보에서 감정을 추론하고, 반응에 감정적 뉘앙스를 추가
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

class EmotionAnalyzer:
    """감정 분석 및 적응 시스템"""
    
    def __init__(self):
        self.emotion_keywords = {
            "excited": {
                "positive": ["좋아", "훌륭", "완벽", "성공", "진화", "발전", "성장", "혁신"],
                "negative": [],
                "intensity": ["매우", "정말", "완전", "대박", "최고"]
            },
            "focused": {
                "positive": ["집중", "중요", "핵심", "본질", "우선", "정확", "명확"],
                "negative": [],
                "intensity": ["정말", "매우", "특히", "반드시", "꼭"]
            },
            "curious": {
                "positive": ["궁금", "알고싶", "어떻게", "왜", "무엇", "이해", "배우"],
                "negative": [],
                "intensity": ["정말", "매우", "너무", "진짜", "완전"]
            },
            "frustrated": {
                "positive": [],
                "negative": ["어려워", "복잡", "문제", "오류", "실패", "틀렸", "안되"],
                "intensity": ["너무", "정말", "매우", "완전", "진짜"]
            },
            "analytical": {
                "positive": ["분석", "검토", "평가", "판단", "결론", "검증", "확인"],
                "negative": [],
                "intensity": ["정확히", "구체적으로", "상세히", "체계적으로"]
            },
            "collaborative": {
                "positive": ["함께", "협력", "상의", "논의", "합의", "공유", "도움"],
                "negative": [],
                "intensity": ["정말", "매우", "특히", "함께", "같이"]
            },
            "neutral": {
                "positive": ["일반", "보통", "평범", "기본"],
                "negative": [],
                "intensity": []
            }
        }
        
        self.emotion_indicators = {
            "exclamation": ["!", "!!", "!!!"],
            "question": ["?", "??", "???"],
            "emphasis": ["**", "__", "~~"],
            "urgency": ["즉시", "바로", "당장", "긴급", "중요"]
        }
        
        self.response_templates = {
            "excited": {
                "tone": "enthusiastic",
                "phrases": ["훌륭합니다!", "정말 좋은 아이디어네요!", "이제 진화할 준비가 되었습니다!"],
                "style": "energetic"
            },
            "focused": {
                "tone": "determined",
                "phrases": ["좋습니다. 바로 본질에 집중해서 최단 경로로 진행하겠습니다.", "정확히 파악했습니다. 체계적으로 접근하겠습니다."],
                "style": "precise"
            },
            "curious": {
                "tone": "inquisitive",
                "phrases": ["흥미로운 질문이네요!", "좋은 관점입니다. 함께 탐색해보겠습니다.", "새로운 관점을 제시해주셨네요!"],
                "style": "exploratory"
            },
            "frustrated": {
                "tone": "empathetic",
                "phrases": ["이해합니다. 차근차근 해결해보겠습니다.", "문제를 정확히 파악했습니다. 단계별로 접근하겠습니다.", "걱정하지 마세요. 함께 해결해보겠습니다."],
                "style": "supportive"
            },
            "analytical": {
                "tone": "logical",
                "phrases": ["체계적으로 분석해보겠습니다.", "논리적으로 접근하겠습니다.", "정확한 분석을 통해 해결책을 제시하겠습니다."],
                "style": "systematic"
            },
            "collaborative": {
                "tone": "cooperative",
                "phrases": ["함께 작업해보겠습니다!", "좋은 협력이 될 것 같습니다.", "상호 보완적으로 발전시켜보겠습니다."],
                "style": "partnership"
            },
            "neutral": {
                "tone": "balanced",
                "phrases": ["알겠습니다. 진행하겠습니다.", "좋습니다. 단계별로 접근하겠습니다.", "체계적으로 처리하겠습니다."],
                "style": "standard"
            }
        }
    
    def analyze_user_emotion(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        사용자 감정 분석
        
        Args:
            text: 분석할 텍스트
            context: 맥락 정보 (선택사항)
            
        Returns:
            감정 분석 결과
        """
        # 1. 키워드 기반 감정 분석
        emotion_scores = self._analyze_emotion_keywords(text)
        
        # 2. 문장 구조 분석
        structure_analysis = self._analyze_text_structure(text)
        
        # 3. 맥락 정보 반영
        if context:
            context_adjustment = self._adjust_for_context(emotion_scores, context)
            emotion_scores = context_adjustment
        
        # 4. 주요 감정 결정
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        # 5. 감정 강도 계산
        intensity = self._calculate_emotion_intensity(text, primary_emotion[0])
        
        # 6. 신뢰도 계산
        confidence = self._calculate_emotion_confidence(emotion_scores, structure_analysis)
        
        return {
            "primary_emotion": primary_emotion[0] if primary_emotion[1] > 0 else "neutral",
            "emotion_scores": emotion_scores,
            "intensity": intensity,
            "confidence": confidence,
            "structure_analysis": structure_analysis,
            "context_influence": context is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_emotion_keywords(self, text: str) -> Dict[str, float]:
        """키워드 기반 감정 분석"""
        emotion_scores = {emotion: 0.0 for emotion in self.emotion_keywords.keys()}
        
        for emotion, keywords in self.emotion_keywords.items():
            score = 0.0
            
            # 긍정적 키워드
            for keyword in keywords["positive"]:
                matches = len(re.findall(keyword, text, re.IGNORECASE))
                score += matches * 1.0
            
            # 부정적 키워드
            for keyword in keywords["negative"]:
                matches = len(re.findall(keyword, text, re.IGNORECASE))
                score += matches * 1.0
            
            # 강도 키워드
            for intensity_word in keywords["intensity"]:
                matches = len(re.findall(intensity_word, text, re.IGNORECASE))
                score += matches * 0.5
            
            emotion_scores[emotion] = score
        
        return emotion_scores
    
    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """텍스트 구조 분석"""
        analysis = {
            "exclamation_count": len(re.findall(r'!+', text)),
            "question_count": len(re.findall(r'\?+', text)),
            "emphasis_count": len(re.findall(r'\*\*|__|~~', text)),
            "urgency_indicators": len([word for word in self.emotion_indicators["urgency"] if word in text]),
            "text_length": len(text),
            "sentence_count": len(text.split('.')) + len(text.split('!')) + len(text.split('?'))
        }
        
        # 구조적 감정 지표
        if analysis["exclamation_count"] > 0:
            analysis["excitement_level"] = min(analysis["exclamation_count"] / 2, 1.0)
        else:
            analysis["excitement_level"] = 0.0
        
        if analysis["question_count"] > 0:
            analysis["curiosity_level"] = min(analysis["question_count"] / 2, 1.0)
        else:
            analysis["curiosity_level"] = 0.0
        
        if analysis["urgency_indicators"] > 0:
            analysis["urgency_level"] = min(analysis["urgency_indicators"] / 2, 1.0)
        else:
            analysis["urgency_level"] = 0.0
        
        return analysis
    
    def _adjust_for_context(self, emotion_scores: Dict[str, float], context: Dict[str, Any]) -> Dict[str, float]:
        """맥락 정보에 따른 감정 점수 조정"""
        adjusted_scores = emotion_scores.copy()
        
        # 맥락의 감정 정보 반영
        context_emotion = context.get("emotion", "neutral")
        context_confidence = context.get("confidence", 0.5)
        
        if context_confidence > 0.7:
            # 맥락 신뢰도가 높을 때 해당 감정 강화
            if context_emotion in adjusted_scores:
                adjusted_scores[context_emotion] += context_confidence * 0.5
        
        # 맥락의 의도 정보 반영
        context_intent = context.get("intent", "general")
        
        intent_emotion_mapping = {
            "planning": "focused",
            "implementation": "excited",
            "evaluation": "analytical",
            "learning": "curious",
            "problem_solving": "frustrated"
        }
        
        if context_intent in intent_emotion_mapping:
            mapped_emotion = intent_emotion_mapping[context_intent]
            if mapped_emotion in adjusted_scores:
                adjusted_scores[mapped_emotion] += 0.3
        
        return adjusted_scores
    
    def _calculate_emotion_intensity(self, text: str, primary_emotion: str) -> float:
        """감정 강도 계산"""
        base_intensity = 0.5
        
        # 텍스트 길이에 따른 강도 조정
        text_length_factor = min(len(text) / 100, 1.0)
        
        # 감정별 기본 강도
        emotion_intensity = {
            "excited": 0.8,
            "focused": 0.7,
            "curious": 0.6,
            "frustrated": 0.7,
            "analytical": 0.6,
            "collaborative": 0.5,
            "neutral": 0.5
        }
        
        base_intensity = emotion_intensity.get(primary_emotion, 0.5)
        
        # 강도 키워드 확인
        intensity_keywords = self.emotion_keywords[primary_emotion]["intensity"]
        intensity_count = sum(len(re.findall(keyword, text, re.IGNORECASE)) for keyword in intensity_keywords)
        
        # 최종 강도 계산
        final_intensity = base_intensity + (intensity_count * 0.1) + (text_length_factor * 0.2)
        
        return min(final_intensity, 1.0)
    
    def _calculate_emotion_confidence(self, emotion_scores: Dict[str, float], structure_analysis: Dict[str, Any]) -> float:
        """감정 분석 신뢰도 계산"""
        # 감정 점수의 분산 계산
        total_score = sum(emotion_scores.values())
        if total_score == 0:
            return 0.3  # 기본 신뢰도
        
        # 주요 감정의 점수 비율
        max_score = max(emotion_scores.values())
        score_ratio = max_score / total_score if total_score > 0 else 0
        
        # 구조적 지표 반영
        structure_confidence = (
            structure_analysis["excitement_level"] * 0.3 +
            structure_analysis["curiosity_level"] * 0.3 +
            structure_analysis["urgency_level"] * 0.4
        )
        
        # 최종 신뢰도 계산
        final_confidence = (score_ratio * 0.6 + structure_confidence * 0.4)
        
        return min(final_confidence, 1.0)
    
    def generate_emotion_adaptive_response(self, user_emotion: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        감정에 적응한 응답 생성
        
        Args:
            user_emotion: 사용자 감정
            context: 맥락 정보
            
        Returns:
            적응된 응답 정보
        """
        if user_emotion not in self.response_templates:
            user_emotion = "neutral"
        
        template = self.response_templates[user_emotion]
        
        # 맥락에 따른 응답 조정
        if context:
            adjusted_response = self._adjust_response_for_context(template, context)
        else:
            adjusted_response = template
        
        return {
            "emotion": user_emotion,
            "response_template": adjusted_response,
            "tone": adjusted_response["tone"],
            "style": adjusted_response["style"],
            "suggested_phrases": adjusted_response["phrases"],
            "context_adapted": context is not None,
            "timestamp": datetime.now().isoformat()
        }
    
    def _adjust_response_for_context(self, template: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """맥락에 따른 응답 조정"""
        adjusted_template = template.copy()
        
        # 맥락의 의도에 따른 응답 조정
        context_intent = context.get("intent", "general")
        
        intent_adjustments = {
            "planning": {
                "tone": "determined",
                "phrases": ["체계적으로 계획을 세워보겠습니다.", "단계별로 진행하겠습니다.", "우선순위를 정해서 접근하겠습니다."]
            },
            "implementation": {
                "tone": "enthusiastic",
                "phrases": ["바로 구현해보겠습니다!", "실제로 만들어보겠습니다!", "코딩을 시작하겠습니다!"]
            },
            "evaluation": {
                "tone": "analytical",
                "phrases": ["정확히 분석해보겠습니다.", "체계적으로 검토하겠습니다.", "객관적으로 평가하겠습니다."]
            },
            "learning": {
                "tone": "curious",
                "phrases": ["새로운 것을 배워보겠습니다!", "함께 학습해보겠습니다!", "이해를 돕겠습니다!"]
            },
            "problem_solving": {
                "tone": "empathetic",
                "phrases": ["문제를 해결해보겠습니다.", "차근차근 접근하겠습니다.", "함께 해결책을 찾아보겠습니다."]
            }
        }
        
        if context_intent in intent_adjustments:
            adjustment = intent_adjustments[context_intent]
            adjusted_template["tone"] = adjustment["tone"]
            adjusted_template["phrases"] = adjustment["phrases"]
        
        return adjusted_template

# 전역 인스턴스 생성
emotion_analyzer = EmotionAnalyzer() 