#!/usr/bin/env python3
"""
DuRi 자기성찰 시스템 모듈
"""

from datetime import datetime
from typing import Any, Dict, List


class DuRiSelfReflector:
    """DuRi의 2차 성찰 시스템 - ChatGPT 평가에 대한 자기 분석"""

    def __init__(self):
        self.reflection_history = []
        self.improvement_suggestions = []

    def reflect_on_chatgpt_feedback(
        self,
        chatgpt_evaluation: Dict[str, Any],
        original_response: str,
        user_question: str,
    ) -> Dict[str, Any]:
        """ChatGPT 평가에 대한 DuRi의 자기성찰"""

        print(f"🤔 DuRi 자기성찰 시작")

        reflection = {
            "timestamp": datetime.now().isoformat(),
            "chatgpt_evaluation": chatgpt_evaluation,
            "original_response": original_response,
            "user_question": user_question,
            "accepted_criticisms": [],
            "disagreements": [],
            "improvement_proposal": {},
            "discussion_request": "",
            "self_assessment": {},
        }

        # 수용한 비판 분석
        reflection["accepted_criticisms"] = self._analyze_accepted_points(
            chatgpt_evaluation
        )

        # 의견 차이 분석
        reflection["disagreements"] = self._identify_disagreements(chatgpt_evaluation)

        # 개선안 생성
        reflection["improvement_proposal"] = self._generate_improvement_proposal(
            chatgpt_evaluation
        )

        # 논의 요청
        reflection["discussion_request"] = (
            "ChatGPT와 이 개선안에 대해 논의하고 싶습니다."
        )

        # 자기 평가
        reflection["self_assessment"] = self._self_assess_response(
            original_response, user_question
        )

        # 성찰 기록 저장
        self.reflection_history.append(reflection)

        print(f"🤔 DuRi 자기성찰 완료")
        print(f"   ✅ 수용한 비판: {len(reflection['accepted_criticisms'])}개")
        print(f"   ❓ 의견 차이: {len(reflection['disagreements'])}개")
        print(
            f"   💡 개선 제안: {len(reflection['improvement_proposal'].get('specific_improvements', []))}개"
        )

        return reflection

    def reflect_on_conversation(
        self, user_input: str, duri_response: str, chatgpt_evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """대화에 대한 자기성찰"""
        return self.reflect_on_chatgpt_feedback(
            chatgpt_evaluation, duri_response, user_input
        )

    def _analyze_accepted_points(self, evaluation: Dict[str, Any]) -> List[str]:
        """수용한 비판 분석"""
        accepted_points = []

        # 낮은 점수 영역들 수용
        scores = evaluation.get("scores", {})
        for dimension, score in scores.items():
            if score < 0.5:
                accepted_points.append(f"{dimension} 영역 개선 필요 (점수: {score})")

        # 제안사항들 수용
        suggestions = evaluation.get("suggestions", [])
        accepted_points.extend(suggestions)

        return accepted_points

    def _identify_disagreements(self, evaluation: Dict[str, Any]) -> List[str]:
        """의견 차이 식별"""
        disagreements = []

        # 예상보다 낮은 점수에 대한 의견 차이
        scores = evaluation.get("scores", {})
        if scores.get("clarity", 0) > 0.8:  # 명확성은 높게 평가받았는데
            if scores.get("depth", 0) < 0.3:  # 깊이가 낮게 평가받았다면
                disagreements.append("명확성과 깊이 평가 간의 불일치가 있습니다")

        # 실용성 평가에 대한 의견 차이
        if scores.get("actionability", 0) < 0.3:
            disagreements.append("실용성 평가에 대해 더 구체적인 기준이 필요합니다")

        # 전반적인 평가에 대한 의견 차이
        total_score = evaluation.get("total_score", 0)
        if total_score < 0.4:
            disagreements.append("ChatGPT가 평가한 점수가 예상보다 낮습니다")

        return disagreements

    def _generate_improvement_proposal(
        self, evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """개선안 생성"""
        proposal = {
            "reasoning": "",
            "specific_improvements": [],
            "code_examples": [],
            "structure_changes": [],
            "priority": "medium",
        }

        # 개선 이유 분석
        proposal["reasoning"] = self._analyze_improvement_reasoning(evaluation)

        # 구체적 개선사항
        proposal["specific_improvements"] = self._generate_specific_improvements(
            evaluation
        )

        # 코드 예제 제안
        proposal["code_examples"] = self._suggest_code_examples(evaluation)

        # 구조 변경 제안
        proposal["structure_changes"] = self._suggest_structure_changes(evaluation)

        # 우선순위 결정
        proposal["priority"] = self._determine_priority(evaluation)

        return proposal

    def _analyze_improvement_reasoning(self, evaluation: Dict[str, Any]) -> str:
        """개선 이유 분석"""
        scores = evaluation.get("scores", {})
        critical_issues = evaluation.get("critical_issues", [])

        if scores.get("actionability", 0) < 0.3:
            return "실용적인 예제와 코드가 부족하여 개선이 필요합니다"
        elif scores.get("depth", 0) < 0.3:
            return "상세한 설명과 분석이 부족하여 개선이 필요합니다"
        elif scores.get("structure", 0) < 0.3:
            return "논리적 구조와 흐름이 부족하여 개선이 필요합니다"
        else:
            return "전반적인 품질 향상을 위해 개선이 필요합니다"

    def _generate_specific_improvements(self, evaluation: Dict[str, Any]) -> List[str]:
        """구체적 개선사항 생성"""
        improvements = []
        scores = evaluation.get("scores", {})

        if scores.get("actionability", 0) < 0.5:
            improvements.append("실제 코드 예제 추가")
            improvements.append("단계별 구현 가이드 제공")

        if scores.get("depth", 0) < 0.5:
            improvements.append("이유와 근거를 더 명확히 설명")
            improvements.append("비교 분석 추가")

        if scores.get("structure", 0) < 0.5:
            improvements.append("논리적 구조 개선")
            improvements.append("단계별 설명 추가")

        return improvements

    def _suggest_code_examples(self, evaluation: Dict[str, Any]) -> List[str]:
        """코드 예제 제안"""
        examples = []
        scores = evaluation.get("scores", {})

        if scores.get("actionability", 0) < 0.5:
            examples.append("기본 사용법 예제")
            examples.append("실제 프로젝트 적용 예제")
            examples.append("에러 처리 예제")

        return examples

    def _suggest_structure_changes(self, evaluation: Dict[str, Any]) -> List[str]:
        """구조 변경 제안"""
        changes = []
        scores = evaluation.get("scores", {})

        if scores.get("structure", 0) < 0.5:
            changes.append("개요-설명-예제-결론 구조로 변경")
            changes.append("단계별 번호 매기기")
            changes.append("중요 포인트 강조")

        return changes

    def _determine_priority(self, evaluation: Dict[str, Any]) -> str:
        """우선순위 결정"""
        scores = evaluation.get("scores", {})
        critical_issues = evaluation.get("critical_issues", [])

        if critical_issues or any(score < 0.3 for score in scores.values()):
            return "high"
        elif any(score < 0.5 for score in scores.values()):
            return "medium"
        else:
            return "low"

    def _self_assess_response(self, response: str, question: str) -> Dict[str, Any]:
        """자기 응답 평가"""
        assessment = {
            "response_length": len(response.split()),
            "technical_depth": 0,
            "has_examples": "코드" in response or "예제" in response,
            "has_structure": any(
                indicator in response for indicator in ["1.", "2.", "단계"]
            ),
            "self_score": 0.0,
        }

        # 기술적 깊이 평가
        tech_keywords = ["API", "HTTP", "JSON", "async", "await", "FastAPI", "Flask"]
        tech_count = sum(
            1 for keyword in tech_keywords if keyword.lower() in response.lower()
        )
        assessment["technical_depth"] = tech_count

        # 자기 점수 계산
        score = 0.0
        if assessment["response_length"] > 20:
            score += 0.2
        if assessment["has_examples"]:
            score += 0.3
        if assessment["has_structure"]:
            score += 0.2
        if assessment["technical_depth"] > 2:
            score += 0.3

        assessment["self_score"] = min(score, 1.0)

        return assessment


# 모듈 인스턴스 생성
duri_self_reflector = DuRiSelfReflector()
