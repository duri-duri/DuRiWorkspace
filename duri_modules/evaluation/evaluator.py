#!/usr/bin/env python3
"""
ChatGPT 6차원 평가 시스템 모듈
"""

import re
from datetime import datetime
from typing import Any, Dict, List


class ChatGPTEvaluator:
    """ChatGPT의 6차원 답변 평가 시스템"""

    EVALUATION_CRITERIA = {
        "correctness": "정확성 - 기술적 정확도와 사실성",
        "relevance": "관련성 - 질문과의 연관성",
        "depth": "깊이 - 상세한 설명과 분석",
        "structure": "구조 - 논리적 구성과 흐름",
        "clarity": "명확성 - 이해하기 쉬운 설명",
        "actionability": "실행가능성 - 실용적 적용 가능성",
    }

    def evaluate_response(
        self, duri_response: str, user_question: str
    ) -> Dict[str, Any]:
        """DuRi 응답을 6차원으로 평가"""

        print(f"🤖 ChatGPT 평가 시작: {len(duri_response)}자 응답")

        # 6차원 점수 계산
        scores = self._calculate_6d_scores(duri_response, user_question)

        # 개선 제안 생성
        suggestions = self._identify_improvements(duri_response)

        # 중요 이슈 식별
        critical_issues = self._find_critical_issues(duri_response)

        # 전체 평가 생성
        overall_assessment = self._generate_overall_assessment(duri_response)

        # 총점 계산
        total_score = sum(scores.values()) / len(scores)

        evaluation_result = {
            "scores": scores,
            "suggestions": suggestions,
            "critical_issues": critical_issues,
            "overall_assessment": overall_assessment,
            "timestamp": datetime.now().isoformat(),
            "total_score": total_score,
        }

        print(f"🤖 ChatGPT 평가 완료: 총점 {total_score:.3f}")
        print(f"   📊 세부 점수: {scores}")
        print(f"   💡 개선 제안: {suggestions}")

        return evaluation_result

    def _calculate_6d_scores(self, response: str, question: str) -> Dict[str, float]:
        """6차원 점수 계산"""
        scores = {}

        # 정확성 (기술적 정확도)
        technical_accuracy = self._assess_technical_accuracy(response)
        scores["correctness"] = technical_accuracy

        # 관련성 (질문과의 연관성)
        relevance_score = self._assess_relevance(response, question)
        scores["relevance"] = relevance_score

        # 깊이 (상세한 설명)
        depth_score = self._assess_depth(response)
        scores["depth"] = depth_score

        # 구조 (논리적 구성)
        structure_score = self._assess_structure(response)
        scores["structure"] = structure_score

        # 명확성 (이해하기 쉬움)
        clarity_score = self._assess_clarity(response)
        scores["clarity"] = clarity_score

        # 실행가능성 (실용적 적용)
        actionability_score = self._assess_actionability(response)
        scores["actionability"] = actionability_score

        return scores

    def _assess_technical_accuracy(self, response: str) -> float:
        """기술적 정확도 평가"""
        # 기술적 키워드 포함 여부
        tech_keywords = [
            "API",
            "HTTP",
            "JSON",
            "async",
            "await",
            "FastAPI",
            "Flask",
            "Python",
        ]
        keyword_count = sum(
            1 for keyword in tech_keywords if keyword.lower() in response.lower()
        )
        return min(keyword_count / len(tech_keywords), 1.0)

    def _assess_relevance(self, response: str, question: str) -> float:
        """질문과의 관련성 평가"""
        # 질문 키워드가 응답에 포함되는지 확인
        question_words = set(re.findall(r"\w+", question.lower()))
        response_words = set(re.findall(r"\w+", response.lower()))

        if not question_words:
            return 0.0

        overlap = len(question_words.intersection(response_words))
        return min(overlap / len(question_words), 1.0)

    def _assess_depth(self, response: str) -> float:
        """상세한 설명 평가"""
        # 응답 길이와 복잡성
        word_count = len(response.split())
        if word_count < 10:
            return 0.0
        elif word_count < 50:
            return 0.3
        elif word_count < 100:
            return 0.6
        else:
            return 1.0

    def _assess_structure(self, response: str) -> float:
        """논리적 구조 평가"""
        # 구조적 요소 확인
        structure_indicators = [
            "1.",
            "2.",
            "3.",
            "첫째",
            "둘째",
            "셋째",
            "단계",
            "단계별",
        ]
        indicator_count = sum(
            1 for indicator in structure_indicators if indicator in response
        )
        return min(indicator_count / 3, 1.0)

    def _assess_clarity(self, response: str) -> float:
        """명확성 평가"""
        # 명확한 설명 요소
        clarity_indicators = ["예를 들어", "즉", "다시 말해", "구체적으로", "예시"]
        indicator_count = sum(
            1 for indicator in clarity_indicators if indicator in response
        )
        return min(indicator_count / 2, 1.0)

    def _assess_actionability(self, response: str) -> float:
        """실행가능성 평가"""
        # 실용적 요소
        action_indicators = ["코드", "예제", "실제", "구현", "사용법", "방법"]
        indicator_count = sum(
            1 for indicator in action_indicators if indicator in response
        )
        return min(indicator_count / 3, 1.0)

    def _identify_improvements(self, response: str) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        if len(response.split()) < 20:
            suggestions.append("더 상세한 설명이 필요합니다")

        if "코드" not in response and "예제" not in response:
            suggestions.append("실제 코드 예제를 추가해보세요")

        if "이유" not in response and "왜" not in response:
            suggestions.append("이유와 근거를 더 명확히 설명해보세요")

        if not any(indicator in response for indicator in ["1.", "2.", "단계"]):
            suggestions.append("단계별로 구조화된 설명을 추가해보세요")

        return suggestions

    def _find_critical_issues(self, response: str) -> List[str]:
        """중요 이슈 식별"""
        issues = []

        if len(response.split()) < 10:
            issues.append("답변이 너무 짧습니다")

        if "모르겠습니다" in response or "알 수 없습니다" in response:
            issues.append("불확실한 답변입니다")

        if len(response) > 1000:
            issues.append("답변이 너무 길어서 핵심을 놓칠 수 있습니다")

        return issues

    def _generate_overall_assessment(self, response: str) -> str:
        """전체 평가 생성"""
        word_count = len(response.split())

        if word_count < 10:
            return "답변이 너무 간단합니다. 더 구체적인 정보가 필요합니다."
        elif word_count < 50:
            return "기본적인 답변입니다. 더 상세한 설명이 필요합니다."
        elif word_count < 100:
            return "적절한 수준의 답변입니다. 일부 개선 여지가 있습니다."
        else:
            return "상세하고 포괄적인 답변입니다. 매우 좋습니다."


# 모듈 인스턴스 생성
chatgpt_evaluator = ChatGPTEvaluator()
