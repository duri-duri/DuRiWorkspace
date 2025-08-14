#!/usr/bin/env python3
"""
DuRi 맥락 이해 시스템
대화 흐름, 주제 추적, 감정 추정, 사용자 목표 예측
"""

import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class ContextAnalyzer:
    """대화 맥락을 분석하고 이해하는 시스템"""
    
    def __init__(self):
        self.conversation_history = []
        self.topic_keywords = {
            "duri_evolution": ["진화", "개선", "학습", "발전", "업그레이드"],
            "system_architecture": ["시스템", "아키텍처", "구조", "모듈", "노드"],
            "implementation": ["구현", "코딩", "개발", "프로그래밍", "코드"],
            "testing": ["테스트", "검증", "확인", "실험"],
            "optimization": ["최적화", "효율", "성능", "개선"],
            "priorities": ["우선순위", "순서", "계획", "단계", "진행"]
        }
        
        self.emotion_indicators = {
            "focused": ["집중", "중요", "핵심", "본질", "우선"],
            "curious": ["궁금", "알고싶", "어떻게", "왜", "무엇"],
            "frustrated": ["어려워", "복잡", "문제", "오류", "실패"],
            "excited": ["좋아", "훌륭", "완벽", "성공", "진화"],
            "analytical": ["분석", "검토", "평가", "판단", "결론"]
        }
        
        self.intent_patterns = {
            "planning": ["계획", "순서", "단계", "우선순위", "진행"],
            "implementation": ["구현", "코딩", "개발", "작업", "시작"],
            "evaluation": ["평가", "검토", "분석", "확인", "테스트"],
            "learning": ["학습", "이해", "알기", "배우", "진화"],
            "problem_solving": ["문제", "해결", "개선", "수정", "고치"]
        }
    
    def analyze_conversation_context(self, conversation_history: List[Dict]) -> Dict[str, Any]:
        """
        대화 맥락을 종합적으로 분석
        
        Args:
            conversation_history: 대화 히스토리 리스트
            
        Returns:
            맥락 분석 결과
        """
        if not conversation_history:
            return self._get_default_context()
        
        # 최근 대화 추출 (최대 10개)
        recent_conversations = conversation_history[-10:]
        
        # 1. 주제 분석
        topic_analysis = self._analyze_topic(recent_conversations)
        
        # 2. 감정 분석
        emotion_analysis = self._analyze_emotion(recent_conversations)
        
        # 3. 의도 분석
        intent_analysis = self._analyze_intent(recent_conversations)
        
        # 4. 대화 흐름 분석
        flow_analysis = self._analyze_conversation_flow(recent_conversations)
        
        # 5. 신뢰도 계산
        confidence = self._calculate_confidence(topic_analysis, emotion_analysis, intent_analysis)
        
        return {
            "topic": topic_analysis["primary_topic"],
            "subtopics": topic_analysis["subtopics"],
            "emotion": emotion_analysis["primary_emotion"],
            "emotion_confidence": emotion_analysis["confidence"],
            "intent": intent_analysis["primary_intent"],
            "intent_confidence": intent_analysis["confidence"],
            "conversation_flow": flow_analysis,
            "confidence": confidence,
            "context_summary": self._generate_context_summary(topic_analysis, emotion_analysis, intent_analysis),
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_topic(self, conversations: List[Dict]) -> Dict[str, Any]:
        """주제 분석"""
        topic_scores = {}
        all_text = " ".join([conv.get("user_input", "") + " " + conv.get("duri_response", "") 
                            for conv in conversations])
        
        # 각 주제별 키워드 매칭
        for topic, keywords in self.topic_keywords.items():
            score = 0
            for keyword in keywords:
                score += len(re.findall(keyword, all_text, re.IGNORECASE))
            topic_scores[topic] = score
        
        # 가장 높은 점수의 주제 선택
        primary_topic = max(topic_scores.items(), key=lambda x: x[1])
        
        # 하위 주제들 (점수 > 0)
        subtopics = [topic for topic, score in topic_scores.items() if score > 0]
        
        return {
            "primary_topic": primary_topic[0] if primary_topic[1] > 0 else "general",
            "subtopics": subtopics,
            "topic_scores": topic_scores
        }
    
    def _analyze_emotion(self, conversations: List[Dict]) -> Dict[str, Any]:
        """감정 분석"""
        emotion_scores = {}
        all_text = " ".join([conv.get("user_input", "") + " " + conv.get("duri_response", "") 
                            for conv in conversations])
        
        # 각 감정별 지표 매칭
        for emotion, indicators in self.emotion_indicators.items():
            score = 0
            for indicator in indicators:
                score += len(re.findall(indicator, all_text, re.IGNORECASE))
            emotion_scores[emotion] = score
        
        # 가장 높은 점수의 감정 선택
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        
        # 감정 신뢰도 계산 (전체 텍스트 대비 감정 지표 비율)
        total_indicators = sum(emotion_scores.values())
        total_words = len(all_text.split())
        confidence = min(total_indicators / max(total_words, 1) * 10, 1.0)
        
        return {
            "primary_emotion": primary_emotion[0] if primary_emotion[1] > 0 else "neutral",
            "emotion_scores": emotion_scores,
            "confidence": confidence
        }
    
    def _analyze_intent(self, conversations: List[Dict]) -> Dict[str, Any]:
        """의도 분석"""
        intent_scores = {}
        all_text = " ".join([conv.get("user_input", "") + " " + conv.get("duri_response", "") 
                            for conv in conversations])
        
        # 각 의도별 패턴 매칭
        for intent, patterns in self.intent_patterns.items():
            score = 0
            for pattern in patterns:
                score += len(re.findall(pattern, all_text, re.IGNORECASE))
            intent_scores[intent] = score
        
        # 가장 높은 점수의 의도 선택
        primary_intent = max(intent_scores.items(), key=lambda x: x[1])
        
        # 의도 신뢰도 계산
        total_patterns = sum(intent_scores.values())
        total_words = len(all_text.split())
        confidence = min(total_patterns / max(total_words, 1) * 10, 1.0)
        
        return {
            "primary_intent": primary_intent[0] if primary_intent[1] > 0 else "general",
            "intent_scores": intent_scores,
            "confidence": confidence
        }
    
    def _analyze_conversation_flow(self, conversations: List[Dict]) -> Dict[str, Any]:
        """대화 흐름 분석"""
        if len(conversations) < 2:
            return {"flow_type": "single", "direction": "neutral"}
        
        # 대화 방향성 분석
        recent_inputs = [conv.get("user_input", "") for conv in conversations[-3:]]
        
        # 질문 패턴 분석
        question_count = sum(1 for text in recent_inputs if "?" in text or "어떻게" in text or "왜" in text)
        
        # 명령 패턴 분석
        command_count = sum(1 for text in recent_inputs if any(word in text for word in ["해줘", "해보자", "시작", "진행"]))
        
        # 설명 요청 패턴 분석
        explanation_count = sum(1 for text in recent_inputs if any(word in text for word in ["설명", "이해", "알기", "배우"]))
        
        # 흐름 타입 결정
        if question_count > command_count and question_count > explanation_count:
            flow_type = "questioning"
        elif command_count > question_count and command_count > explanation_count:
            flow_type = "directive"
        elif explanation_count > question_count and explanation_count > command_count:
            flow_type = "explanatory"
        else:
            flow_type = "mixed"
        
        return {
            "flow_type": flow_type,
            "question_ratio": question_count / len(recent_inputs),
            "command_ratio": command_count / len(recent_inputs),
            "explanation_ratio": explanation_count / len(recent_inputs)
        }
    
    def _calculate_confidence(self, topic_analysis: Dict, emotion_analysis: Dict, intent_analysis: Dict) -> float:
        """전체 맥락 분석 신뢰도 계산"""
        # 각 분석의 신뢰도 가중 평균
        topic_confidence = min(len(topic_analysis["subtopics"]) / 3, 1.0)
        emotion_confidence = emotion_analysis["confidence"]
        intent_confidence = intent_analysis["confidence"]
        
        # 가중 평균 (감정과 의도에 더 높은 가중치)
        confidence = (topic_confidence * 0.3 + emotion_confidence * 0.4 + intent_confidence * 0.3)
        
        return min(confidence, 1.0)
    
    def _generate_context_summary(self, topic_analysis: Dict, emotion_analysis: Dict, intent_analysis: Dict) -> str:
        """맥락 요약 생성"""
        topic = topic_analysis["primary_topic"]
        emotion = emotion_analysis["primary_emotion"]
        intent = intent_analysis["primary_intent"]
        
        summary_templates = {
            "duri_evolution": f"사용자는 DuRi의 {emotion}한 상태에서 {intent} 의도로 진화를 추구하고 있습니다.",
            "system_architecture": f"사용자는 {emotion}한 접근으로 시스템 구조에 대한 {intent}를 보여줍니다.",
            "implementation": f"사용자는 {emotion}한 집중력으로 실제 구현에 대한 {intent}를 표현합니다.",
            "testing": f"사용자는 {emotion}한 태도로 검증과 테스트에 대한 {intent}를 보여줍니다.",
            "optimization": f"사용자는 {emotion}한 관점에서 최적화에 대한 {intent}를 추구합니다.",
            "priorities": f"사용자는 {emotion}한 판단으로 우선순위에 대한 {intent}를 결정하려 합니다."
        }
        
        return summary_templates.get(topic, f"사용자는 {emotion}한 상태에서 {intent} 의도를 보여줍니다.")
    
    def _get_default_context(self) -> Dict[str, Any]:
        """기본 맥락 반환"""
        return {
            "topic": "general",
            "subtopics": [],
            "emotion": "neutral",
            "emotion_confidence": 0.5,
            "intent": "general",
            "intent_confidence": 0.5,
            "conversation_flow": {"flow_type": "single", "direction": "neutral"},
            "confidence": 0.5,
            "context_summary": "새로운 대화가 시작되었습니다.",
            "timestamp": datetime.now().isoformat()
        }
    
    def update_conversation_history(self, conversation: Dict[str, Any]):
        """대화 히스토리 업데이트"""
        self.conversation_history.append(conversation)
        
        # 히스토리 크기 제한 (최대 50개)
        if len(self.conversation_history) > 50:
            self.conversation_history = self.conversation_history[-50:]

# 전역 인스턴스 생성
context_analyzer = ContextAnalyzer() 