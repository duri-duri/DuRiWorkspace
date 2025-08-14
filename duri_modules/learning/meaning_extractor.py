#!/usr/bin/env python3
"""
DuRi 의미 분해기 (Meaning Extractor)
대화와 행동을 구조화된 의미로 변환
"""
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class MeaningExtractor:
    def __init__(self):
        self.intent_patterns = {
            "질문": [r"어떻게", r"무엇", r"왜", r"언제", r"어디", r"가능한가", r"가능하니"],
            "요청": [r"해줘", r"만들어", r"구현해", r"시작해", r"중지해"],
            "평가": [r"어떠니", r"어떤가", r"좋니", r"나쁘니", r"성공했니"],
            "확인": [r"맞니", r"정확한가", r"확실한가", r"진짜로"],
            "개선": [r"개선", r"향상", r"발전", r"진화", r"학습"]
        }
        
        self.topic_patterns = {
            "자율학습": [r"자율", r"학습", r"자동", r"진화", r"개선"],
            "시스템": [r"시스템", r"구조", r"아키텍처", r"모듈"],
            "성능": [r"성능", r"속도", r"효율", r"최적화"],
            "오류": [r"오류", r"에러", r"문제", r"실패", r"버그"],
            "기능": [r"기능", r"특징", r"역할", r"작동"]
        }
        
        self.difficulty_indicators = {
            "하": [r"간단", r"쉬운", r"기본", r"초보"],
            "중": [r"보통", r"일반", r"평균", r"적당"],
            "상": [r"복잡", r"어려운", r"고급", r"전문", r"심화"]
        }
        
    def extract_meaning(self, user_input: str, duri_response: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """대화의 의미를 추출"""
        try:
            # 기본 정보
            meaning = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "duri_response": duri_response,
                "input_length": len(user_input),
                "response_length": len(duri_response)
            }
            
            # 1. 사용자 의도 분석
            intent = self._analyze_intent(user_input)
            meaning["intent"] = intent
            
            # 2. 주제 분석
            topic = self._analyze_topic(user_input)
            meaning["topic"] = topic
            
            # 3. 난이도 분석
            difficulty = self._analyze_difficulty(user_input)
            meaning["difficulty"] = difficulty
            
            # 4. 응답 품질 분석
            response_quality = self._analyze_response_quality(duri_response, user_input)
            meaning["response_quality"] = response_quality
            
            # 5. 성공 여부 판단
            success = self._judge_success(user_input, duri_response, intent)
            meaning["is_success"] = success
            
            # 6. 교훈 추출
            lesson = self._extract_lesson(user_input, duri_response, success)
            meaning["lesson"] = lesson
            
            # 7. 개선점 식별
            improvements = self._identify_improvements(duri_response, user_input)
            meaning["improvements"] = improvements
            
            # 8. 다음 행동 제안
            next_actions = self._suggest_next_actions(meaning)
            meaning["next_actions"] = next_actions
            
            logger.info(f"의미 추출 완료: {intent} -> {topic} (난이도: {difficulty}, 성공: {success})")
            
            return meaning
            
        except Exception as e:
            logger.error(f"의미 추출 오류: {e}")
            return self._create_fallback_meaning(user_input, duri_response)
    
    def _analyze_intent(self, user_input: str) -> str:
        """사용자 의도 분석"""
        user_input_lower = user_input.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return intent
        
        # 기본값
        if "?" in user_input or "?" in user_input:
            return "질문"
        elif any(word in user_input_lower for word in ["해줘", "해주세요", "요청"]):
            return "요청"
        else:
            return "확인"
    
    def _analyze_topic(self, user_input: str) -> str:
        """주제 분석"""
        user_input_lower = user_input.lower()
        
        for topic, patterns in self.topic_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return topic
        
        return "일반"
    
    def _analyze_difficulty(self, user_input: str) -> str:
        """난이도 분석"""
        user_input_lower = user_input.lower()
        
        for difficulty, patterns in self.difficulty_indicators.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    return difficulty
        
        # 길이와 복잡성 기반 추정
        if len(user_input) < 20:
            return "하"
        elif len(user_input) < 50:
            return "중"
        else:
            return "상"
    
    def _analyze_response_quality(self, response: str, user_input: str) -> str:
        """응답 품질 분석"""
        # 1. 길이 적절성
        if len(response) < 20:
            return "하"
        elif len(response) < 100:
            return "중"
        else:
            return "상"
        
        # 2. 관련성 (키워드 매칭)
        input_words = set(user_input.lower().split())
        response_words = set(response.lower().split())
        
        if input_words:
            relevance = len(input_words.intersection(response_words)) / len(input_words)
            if relevance > 0.5:
                return "상"
            elif relevance > 0.2:
                return "중"
            else:
                return "하"
    
    def _judge_success(self, user_input: str, duri_response: str, intent: str) -> bool:
        """성공 여부 판단"""
        # 기본 판단 기준
        if len(duri_response) < 10:
            return False
        
        # 의도별 성공 기준
        if intent == "질문":
            # 질문에 대한 구체적인 답변이 있는가?
            return len(duri_response) > 30 and "?" not in duri_response
        
        elif intent == "요청":
            # 요청에 대한 실행 가능한 답변이 있는가?
            action_words = ["다음과 같이", "이렇게", "실행", "구현", "생성"]
            return any(word in duri_response for word in action_words)
        
        elif intent == "평가":
            # 평가에 대한 명확한 판단이 있는가?
            judgment_words = ["좋습니다", "나쁩니다", "성공", "실패", "가능", "불가능"]
            return any(word in duri_response for word in judgment_words)
        
        else:
            # 기본: 응답이 있고 의미가 있는가?
            return len(duri_response) > 20
    
    def _extract_lesson(self, user_input: str, duri_response: str, success: bool) -> str:
        """교훈 추출"""
        if success:
            # 성공한 경우: 무엇이 효과적이었는가?
            if "자율학습" in user_input.lower():
                return "사용자의 자율학습 관련 질문에 대해 구체적인 분석과 개선 방안을 제시하는 것이 효과적"
            elif "가능" in user_input.lower():
                return "기술적 가능성과 현재 구현 수준을 구분하여 명확히 설명하는 것이 중요"
            else:
                return "사용자의 의도를 정확히 파악하고 구체적인 답변을 제공하는 것이 효과적"
        else:
            # 실패한 경우: 무엇을 개선해야 하는가?
            if len(duri_response) < 20:
                return "응답이 너무 짧음 - 더 상세한 설명 필요"
            elif "?" in duri_response:
                return "질문으로 답하는 대신 구체적인 답변 제공 필요"
            else:
                return "사용자 의도에 맞는 더 정확한 답변 필요"
    
    def _identify_improvements(self, response: str, user_input: str) -> List[str]:
        """개선점 식별"""
        improvements = []
        
        # 응답 길이 체크
        if len(response) < 30:
            improvements.append("더 상세한 설명 추가")
        
        # 구체성 체크
        if "예시" not in response and "예제" not in response:
            improvements.append("구체적인 예시나 코드 추가")
        
        # 구조성 체크
        if not any(marker in response for marker in ["1.", "2.", "3.", "•", "-"]):
            improvements.append("단계별 구조화된 설명 추가")
        
        # 실행 가능성 체크
        if "요청" in user_input.lower() and "실행" not in response:
            improvements.append("실행 가능한 단계나 명령어 제공")
        
        return improvements
    
    def _suggest_next_actions(self, meaning: Dict[str, Any]) -> List[str]:
        """다음 행동 제안"""
        actions = []
        
        if not meaning["is_success"]:
            actions.append("동일한 질문에 대해 더 나은 답변 준비")
            actions.append("유사한 질문 패턴 학습")
        
        if meaning["difficulty"] == "상":
            actions.append("복잡한 질문에 대한 단계별 접근법 개발")
        
        if "자율학습" in meaning["topic"]:
            actions.append("자율학습 관련 지식 베이스 확장")
        
        return actions
    
    def _create_fallback_meaning(self, user_input: str, duri_response: str) -> Dict[str, Any]:
        """오류 시 기본 의미 생성"""
        return {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "duri_response": duri_response,
            "intent": "확인",
            "topic": "일반",
            "difficulty": "중",
            "response_quality": "중",
            "is_success": len(duri_response) > 20,
            "lesson": "의미 분석 중 오류 발생",
            "improvements": ["의미 분석 시스템 개선 필요"],
            "next_actions": ["오류 로그 확인 및 시스템 점검"]
        }
    
    def batch_extract(self, conversations: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """여러 대화의 의미를 일괄 추출"""
        meanings = []
        
        for conversation in conversations:
            meaning = self.extract_meaning(
                conversation.get("user_input", ""),
                conversation.get("duri_response", "")
            )
            meanings.append(meaning)
        
        return meanings
    
    def get_learning_summary(self, meanings: List[Dict[str, Any]]) -> Dict[str, Any]:
        """학습 요약 생성"""
        if not meanings:
            return {"error": "분석할 대화가 없습니다"}
        
        total_conversations = len(meanings)
        successful_conversations = sum(1 for m in meanings if m.get("is_success", False))
        success_rate = successful_conversations / total_conversations if total_conversations > 0 else 0
        
        # 주제별 분포
        topics = {}
        for meaning in meanings:
            topic = meaning.get("topic", "일반")
            topics[topic] = topics.get(topic, 0) + 1
        
        # 난이도별 분포
        difficulties = {}
        for meaning in meanings:
            difficulty = meaning.get("difficulty", "중")
            difficulties[difficulty] = difficulties.get(difficulty, 0) + 1
        
        # 주요 교훈 수집
        lessons = [m.get("lesson", "") for m in meanings if m.get("lesson")]
        
        return {
            "total_conversations": total_conversations,
            "success_rate": success_rate,
            "topics_distribution": topics,
            "difficulties_distribution": difficulties,
            "key_lessons": lessons[:5],  # 상위 5개 교훈
            "analysis_timestamp": datetime.now().isoformat()
        }

# 전역 인스턴스
meaning_extractor = MeaningExtractor() 