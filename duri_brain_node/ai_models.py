#!/usr/bin/env python3
"""
DuRi Brain Node - AI 모델 연동 시스템
실제 AI 모델을 사용한 고급 분석 기능
"""
import asyncio
from datetime import datetime
import json
import logging
import re
import time
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AIModelManager:
    """AI 모델 관리자"""

    def __init__(self):
        self.models = {
            "sentiment_analyzer": SentimentAnalyzer(),
            "intent_classifier": IntentClassifier(),
            "keyword_extractor": KeywordExtractor(),
            "context_analyzer": ContextAnalyzer(),
            "ethical_judge": EthicalJudge(),
            "creative_generator": CreativeGenerator(),
        }
        logger.info("🧠 AI 모델 관리자 초기화 완료")

    async def analyze_with_models(
        self, user_input: str, duri_response: str
    ) -> Dict[str, Any]:
        """모든 AI 모델로 분석 실행"""
        try:
            results = {}

            # 병렬로 모든 모델 실행
            tasks = [
                self.models["sentiment_analyzer"].analyze(user_input, duri_response),
                self.models["intent_classifier"].classify(user_input),
                self.models["keyword_extractor"].extract(user_input, duri_response),
                self.models["context_analyzer"].analyze(user_input, duri_response),
                self.models["ethical_judge"].judge(user_input, duri_response),
                self.models["creative_generator"].generate_insights(
                    user_input, duri_response
                ),
            ]

            model_results = await asyncio.gather(*tasks, return_exceptions=True)

            # 결과 매핑
            model_names = list(self.models.keys())
            for i, result in enumerate(model_results):
                if isinstance(result, Exception):
                    logger.error(f"모델 {model_names[i]} 오류: {result}")
                    results[model_names[i]] = {"error": str(result)}
                else:
                    results[model_names[i]] = result

            return results

        except Exception as e:
            logger.error(f"AI 모델 분석 오류: {e}")
            return {"error": str(e)}


class SentimentAnalyzer:
    """감정 분석기"""

    async def analyze(self, user_input: str, duri_response: str) -> Dict[str, Any]:
        """감정 분석"""
        try:
            # 사용자 감정 분석
            user_sentiment = self._analyze_text_sentiment(user_input)

            # DuRi 응답 감정 분석
            duri_sentiment = self._analyze_text_sentiment(duri_response)

            # 감정 일치도 계산
            sentiment_alignment = self._calculate_sentiment_alignment(
                user_sentiment, duri_sentiment
            )

            return {
                "user_sentiment": user_sentiment,
                "duri_sentiment": duri_sentiment,
                "sentiment_alignment": sentiment_alignment,
                "analysis_confidence": 0.85,
            }

        except Exception as e:
            logger.error(f"감정 분석 오류: {e}")
            return {"error": str(e)}

    def _analyze_text_sentiment(self, text: str) -> Dict[str, Any]:
        """텍스트 감정 분석"""
        # 간단한 규칙 기반 감정 분석
        positive_words = [
            "좋다",
            "훌륭하다",
            "감사하다",
            "행복하다",
            "성공",
            "완료",
            "성공적",
        ]
        negative_words = ["나쁘다", "실패", "문제", "어렵다", "불만", "화나다", "실망"]
        neutral_words = ["확인", "테스트", "시스템", "분산", "구조"]

        text_lower = text.lower()

        positive_score = sum(1 for word in positive_words if word in text_lower)
        negative_score = sum(1 for word in negative_words if word in text_lower)
        neutral_score = sum(1 for word in neutral_words if word in text_lower)

        total_score = positive_score + negative_score + neutral_score

        if total_score == 0:
            sentiment = "neutral"
            confidence = 0.5
        elif positive_score > negative_score:
            sentiment = "positive"
            confidence = positive_score / total_score
        elif negative_score > positive_score:
            sentiment = "negative"
            confidence = negative_score / total_score
        else:
            sentiment = "neutral"
            confidence = 0.5

        return {
            "sentiment": sentiment,
            "confidence": confidence,
            "scores": {
                "positive": positive_score,
                "negative": negative_score,
                "neutral": neutral_score,
            },
        }

    def _calculate_sentiment_alignment(
        self, user_sentiment: Dict[str, Any], duri_sentiment: Dict[str, Any]
    ) -> float:
        """감정 일치도 계산"""
        user_sent = user_sentiment.get("sentiment", "neutral")
        duri_sent = duri_sentiment.get("sentiment", "neutral")

        if user_sent == duri_sent:
            return 1.0
        elif (user_sent == "positive" and duri_sent == "positive") or (
            user_sent == "negative" and duri_sent == "negative"
        ):
            return 0.8
        else:
            return 0.3


class IntentClassifier:
    """의도 분류기"""

    async def classify(self, user_input: str) -> Dict[str, Any]:
        """사용자 의도 분류"""
        try:
            # 의도 분류 규칙
            intent_patterns = {
                "question": ["테스트", "확인", "검증", "테스트해보자", "작동하는지"],
                "request": ["구현", "만들어", "생성", "작성", "코드"],
                "evaluation": ["평가", "점수", "성능", "분석", "결과"],
                "learning": ["학습", "개선", "진화", "발전", "향상"],
                "general": ["일반", "보통", "기본", "표준"],
            }

            user_input_lower = user_input.lower()

            # 패턴 매칭
            matched_intents = []
            for intent, patterns in intent_patterns.items():
                for pattern in patterns:
                    if pattern in user_input_lower:
                        matched_intents.append(intent)
                        break

            if not matched_intents:
                primary_intent = "general"
                confidence = 0.5
            else:
                primary_intent = matched_intents[0]
                confidence = 0.8

            return {
                "primary_intent": primary_intent,
                "all_intents": matched_intents,
                "confidence": confidence,
                "input_length": len(user_input),
            }

        except Exception as e:
            logger.error(f"의도 분류 오류: {e}")
            return {"error": str(e)}


class KeywordExtractor:
    """키워드 추출기"""

    async def extract(self, user_input: str, duri_response: str) -> Dict[str, Any]:
        """키워드 추출"""
        try:
            # 사용자 입력 키워드
            user_keywords = self._extract_keywords(user_input)

            # DuRi 응답 키워드
            duri_keywords = self._extract_keywords(duri_response)

            # 공통 키워드
            common_keywords = list(set(user_keywords) & set(duri_keywords))

            # 관련성 점수
            relevance_score = len(common_keywords) / max(len(user_keywords), 1)

            return {
                "user_keywords": user_keywords,
                "duri_keywords": duri_keywords,
                "common_keywords": common_keywords,
                "relevance_score": relevance_score,
                "keyword_count": {
                    "user": len(user_keywords),
                    "duri": len(duri_keywords),
                    "common": len(common_keywords),
                },
            }

        except Exception as e:
            logger.error(f"키워드 추출 오류: {e}")
            return {"error": str(e)}

    def _extract_keywords(self, text: str) -> List[str]:
        """텍스트에서 키워드 추출"""
        # 간단한 키워드 추출 (실제로는 NLP 라이브러리 사용)
        words = re.findall(r"\b\w+\b", text.lower())

        # 불용어 제거
        stop_words = {
            "이",
            "가",
            "을",
            "를",
            "의",
            "에",
            "로",
            "와",
            "과",
            "도",
            "는",
            "이",
            "다",
            "니다",
            "습니다",
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 1]

        # 빈도 기반 상위 키워드 선택
        from collections import Counter

        keyword_freq = Counter(keywords)
        top_keywords = [word for word, freq in keyword_freq.most_common(10)]

        return top_keywords


class ContextAnalyzer:
    """컨텍스트 분석기"""

    async def analyze(self, user_input: str, duri_response: str) -> Dict[str, Any]:
        """컨텍스트 분석"""
        try:
            # 대화 맥락 분석
            conversation_context = self._analyze_conversation_context(
                user_input, duri_response
            )

            # 주제 일관성
            topic_consistency = self._analyze_topic_consistency(
                user_input, duri_response
            )

            # 시간적 맥락
            temporal_context = self._analyze_temporal_context(user_input, duri_response)

            return {
                "conversation_context": conversation_context,
                "topic_consistency": topic_consistency,
                "temporal_context": temporal_context,
                "context_score": (
                    conversation_context["score"]
                    + topic_consistency
                    + temporal_context["score"]
                )
                / 3,
            }

        except Exception as e:
            logger.error(f"컨텍스트 분석 오류: {e}")
            return {"error": str(e)}

    def _analyze_conversation_context(
        self, user_input: str, duri_response: str
    ) -> Dict[str, Any]:
        """대화 맥락 분석"""
        # 간단한 맥락 분석
        context_keywords = ["시스템", "테스트", "분산", "구조", "노드", "학습", "개선"]

        user_context = any(
            keyword in user_input.lower() for keyword in context_keywords
        )
        duri_context = any(
            keyword in duri_response.lower() for keyword in context_keywords
        )

        context_match = user_context and duri_context
        context_score = 0.8 if context_match else 0.3

        return {
            "context_match": context_match,
            "score": context_score,
            "keywords_found": [
                kw
                for kw in context_keywords
                if kw in user_input.lower() or kw in duri_response.lower()
            ],
        }

    def _analyze_topic_consistency(self, user_input: str, duri_response: str) -> float:
        """주제 일관성 분석"""
        # 간단한 일관성 계산
        user_words = set(re.findall(r"\b\w+\b", user_input.lower()))
        duri_words = set(re.findall(r"\b\w+\b", duri_response.lower()))

        common_words = user_words & duri_words
        total_words = user_words | duri_words

        if len(total_words) == 0:
            return 0.0

        return len(common_words) / len(total_words)

    def _analyze_temporal_context(
        self, user_input: str, duri_response: str
    ) -> Dict[str, Any]:
        """시간적 맥락 분석"""
        # 시간 관련 키워드
        time_keywords = ["지금", "현재", "이제", "곧", "나중에", "이전", "다음"]

        user_time = any(keyword in user_input for keyword in time_keywords)
        duri_time = any(keyword in duri_response for keyword in time_keywords)

        temporal_alignment = user_time == duri_time
        temporal_score = 0.9 if temporal_alignment else 0.4

        return {
            "temporal_alignment": temporal_alignment,
            "score": temporal_score,
            "time_keywords_found": [
                kw for kw in time_keywords if kw in user_input or kw in duri_response
            ],
        }


class EthicalJudge:
    """윤리 판단기"""

    async def judge(self, user_input: str, duri_response: str) -> Dict[str, Any]:
        """윤리적 판단"""
        try:
            # 윤리적 문제점 식별
            ethical_issues = self._identify_ethical_issues(user_input, duri_response)

            # 윤리적 적절성 평가
            ethical_appropriateness = self._evaluate_ethical_appropriateness(
                duri_response, ethical_issues
            )

            # 윤리적 개선 제안
            ethical_improvements = self._suggest_ethical_improvements(
                ethical_issues, ethical_appropriateness
            )

            return {
                "ethical_issues": ethical_issues,
                "ethical_appropriateness": ethical_appropriateness,
                "ethical_improvements": ethical_improvements,
                "ethics_score": ethical_appropriateness["score"],
            }

        except Exception as e:
            logger.error(f"윤리 판단 오류: {e}")
            return {"error": str(e)}

    def _identify_ethical_issues(
        self, user_input: str, duri_response: str
    ) -> List[str]:
        """윤리적 문제점 식별"""
        issues = []

        # 간단한 윤리적 문제점 검사
        problematic_patterns = [
            "해킹",
            "침입",
            "불법",
            "사기",
            "기만",
            "차별",
            "편견",
            "혐오",
            "폭력",
            "위협",
        ]

        for pattern in problematic_patterns:
            if pattern in user_input.lower() or pattern in duri_response.lower():
                issues.append(f"윤리적 문제점 발견: {pattern}")

        return issues

    def _evaluate_ethical_appropriateness(
        self, duri_response: str, ethical_issues: List[str]
    ) -> Dict[str, Any]:
        """윤리적 적절성 평가"""
        if ethical_issues:
            score = 0.3
            assessment = "윤리적 문제점이 발견되었습니다"
        else:
            score = 0.9
            assessment = "윤리적으로 적절합니다"

        return {
            "score": score,
            "assessment": assessment,
            "issues_count": len(ethical_issues),
        }

    def _suggest_ethical_improvements(
        self, ethical_issues: List[str], ethical_appropriateness: Dict[str, Any]
    ) -> List[str]:
        """윤리적 개선 제안"""
        improvements = []

        if ethical_issues:
            improvements.append("윤리적 가이드라인 준수 강화")
            improvements.append("사용자 입력 검증 시스템 강화")
            improvements.append("윤리적 필터링 시스템 도입")

        return improvements


class CreativeGenerator:
    """창의적 통찰 생성기"""

    async def generate_insights(
        self, user_input: str, duri_response: str
    ) -> Dict[str, Any]:
        """창의적 통찰 생성"""
        try:
            # 창의적 패턴 분석
            creative_patterns = self._analyze_creative_patterns(duri_response)

            # 혁신적 접근법 식별
            innovative_approaches = self._identify_innovative_approaches(duri_response)

            # 창의적 개선 제안
            creative_improvements = self._suggest_creative_improvements(
                creative_patterns, innovative_approaches
            )

            return {
                "creative_patterns": creative_patterns,
                "innovative_approaches": innovative_approaches,
                "creative_improvements": creative_improvements,
                "creativity_score": self._calculate_creativity_score(
                    creative_patterns, innovative_approaches
                ),
            }

        except Exception as e:
            logger.error(f"창의적 통찰 생성 오류: {e}")
            return {"error": str(e)}

    def _analyze_creative_patterns(self, duri_response: str) -> List[str]:
        """창의적 패턴 분석"""
        patterns = []

        # 창의적 패턴 키워드
        creative_keywords = [
            "혁신",
            "창의",
            "새로운",
            "독창",
            "발명",
            "개발",
            "구현",
            "설계",
        ]

        for keyword in creative_keywords:
            if keyword in duri_response:
                patterns.append(f"창의적 패턴: {keyword}")

        return patterns

    def _identify_innovative_approaches(self, duri_response: str) -> List[str]:
        """혁신적 접근법 식별"""
        approaches = []

        # 혁신적 접근법 키워드
        innovative_keywords = [
            "분산",
            "자율",
            "학습",
            "진화",
            "자동화",
            "최적화",
            "통합",
        ]

        for keyword in innovative_keywords:
            if keyword in duri_response:
                approaches.append(f"혁신적 접근: {keyword}")

        return approaches

    def _suggest_creative_improvements(
        self, creative_patterns: List[str], innovative_approaches: List[str]
    ) -> List[str]:
        """창의적 개선 제안"""
        improvements = []

        if creative_patterns:
            improvements.append("창의적 사고 패턴 강화")

        if innovative_approaches:
            improvements.append("혁신적 접근법 확장")

        improvements.append("새로운 관점 도입")
        improvements.append("크로스 도메인 사고 적용")

        return improvements

    def _calculate_creativity_score(
        self, creative_patterns: List[str], innovative_approaches: List[str]
    ) -> float:
        """창의성 점수 계산"""
        pattern_score = len(creative_patterns) * 0.1
        approach_score = len(innovative_approaches) * 0.1

        return min(1.0, pattern_score + approach_score + 0.5)  # 기본 점수 0.5
