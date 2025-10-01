#!/usr/bin/env python3
"""
DuRi 결과 평가 시스템 (Result Evaluator)
대화와 행동의 결과를 정밀하게 평가
"""
from datetime import datetime
import json
import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ResultEvaluator:
    def __init__(self):
        self.evaluation_criteria = {
            "의도_달성": {
                "weight": 0.3,
                "indicators": ["정확한 답변", "구체적 설명", "실행 가능한 제안"],
            },
            "통찰_포함": {
                "weight": 0.25,
                "indicators": ["새로운 개념", "개선점 인지", "학습 내용"],
            },
            "개선_유도": {
                "weight": 0.2,
                "indicators": ["행동 변화", "전략 수정", "접근법 개선"],
            },
            "교훈_명시": {
                "weight": 0.15,
                "indicators": ["배운 내용", "교훈", "경험 정리"],
            },
            "사용자_만족": {
                "weight": 0.1,
                "indicators": ["긍정적 반응", "추가 질문", "감사 표현"],
            },
        }

        self.success_patterns = {
            "정확한 답변": [r"정확", r"맞습니다", r"올바른", r"적절한"],
            "구체적 설명": [r"다음과 같이", r"구체적으로", r"예를 들어", r"단계별로"],
            "실행 가능한 제안": [r"실행", r"구현", r"생성", r"설치", r"설정"],
            "새로운 개념": [r"개념", r"이론", r"방법론", r"접근법"],
            "개선점 인지": [r"개선", r"향상", r"발전", r"진화"],
            "학습 내용": [r"배웠", r"학습", r"이해", r"알게 되"],
            "행동 변화": [r"다음에는", r"이후에는", r"개선하여", r"변경하여"],
            "전략 수정": [r"전략", r"방법", r"접근", r"해결책"],
            "접근법 개선": [r"접근법", r"방식", r"방법론", r"프로세스"],
            "배운 내용": [r"교훈", r"배운 것", r"경험", r"학습한 것"],
            "교훈": [r"교훈", r"배운 것", r"경험", r"학습한 것"],
            "경험 정리": [r"경험", r"실험", r"시도", r"테스트"],
            "긍정적 반응": [r"좋습니다", r"감사", r"훌륭", r"완벽"],
            "추가 질문": [r"추가로", r"더", r"또한", r"그리고"],
            "감사 표현": [r"감사", r"고맙", r"도움", r"유용"],
        }

        self.failure_patterns = {
            "부정확한 답변": [r"모르겠", r"확실하지 않", r"잘 모르", r"불확실"],
            "모호한 설명": [r"아마도", r"어쩌면", r"대략", r"추정"],
            "실행 불가능": [r"불가능", r"어려움", r"문제", r"오류"],
            "부족한 정보": [r"부족", r"미흡", r"부족한", r"적은"],
            "오류 발생": [r"오류", r"에러", r"실패", r"문제"],
            "부정적 반응": [r"나쁘", r"안 좋", r"실망", r"불만"],
        }

    def evaluate_conversation(
        self, user_input: str, duri_response: str, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """대화 결과 평가"""
        try:
            evaluation = {
                "timestamp": datetime.now().isoformat(),
                "user_input": user_input,
                "duri_response": duri_response,
                "overall_score": 0.0,
                "detailed_scores": {},
                "success_indicators": [],
                "failure_indicators": [],
                "improvement_suggestions": [],
                "learning_insights": [],
            }

            # 각 기준별 평가
            for criterion, config in self.evaluation_criteria.items():
                score, indicators = self._evaluate_criterion(
                    duri_response, user_input, criterion, config
                )
                evaluation["detailed_scores"][criterion] = score

                if score > 0.5:
                    evaluation["success_indicators"].extend(indicators)
                else:
                    evaluation["failure_indicators"].extend(indicators)

            # 전체 점수 계산
            total_score = 0.0
            for criterion, config in self.evaluation_criteria.items():
                total_score += (
                    evaluation["detailed_scores"][criterion] * config["weight"]
                )

            evaluation["overall_score"] = total_score

            # 개선 제안 생성
            evaluation["improvement_suggestions"] = (
                self._generate_improvement_suggestions(evaluation)
            )

            # 학습 인사이트 추출
            evaluation["learning_insights"] = self._extract_learning_insights(
                evaluation
            )

            # 성공/실패 판정
            evaluation["is_success"] = total_score > 0.6
            evaluation["success_level"] = self._determine_success_level(total_score)

            logger.info(
                f"결과 평가 완료: 점수 {total_score:.2f} ({evaluation['success_level']})"
            )

            return evaluation

        except Exception as e:
            logger.error(f"결과 평가 오류: {e}")
            return self._create_fallback_evaluation(user_input, duri_response)

    def _evaluate_criterion(
        self, response: str, user_input: str, criterion: str, config: Dict
    ) -> tuple:
        """개별 기준 평가"""
        score = 0.0
        indicators = []

        response_lower = response.lower()

        # 성공 패턴 확인
        for indicator in config["indicators"]:
            if indicator in self.success_patterns:
                patterns = self.success_patterns[indicator]
                for pattern in patterns:
                    if re.search(pattern, response_lower):
                        score += 0.2
                        indicators.append(indicator)
                        break

        # 실패 패턴 확인
        for failure_type, patterns in self.failure_patterns.items():
            for pattern in patterns:
                if re.search(pattern, response_lower):
                    score -= 0.1
                    indicators.append(failure_type)

        # 응답 길이와 품질 기반 추가 점수
        if len(response) > 50:
            score += 0.1
        if len(response) > 100:
            score += 0.1

        # 사용자 의도와의 일치도
        if self._check_intent_alignment(user_input, response):
            score += 0.2

        return min(max(score, 0.0), 1.0), indicators

    def _check_intent_alignment(self, user_input: str, response: str) -> bool:
        """사용자 의도와 응답의 일치도 확인"""
        user_lower = user_input.lower()
        response_lower = response.lower()

        # 질문에 대한 답변
        if "?" in user_input or any(
            word in user_lower for word in ["어떻게", "무엇", "왜"]
        ):
            return len(response) > 30 and "?" not in response

        # 요청에 대한 실행 가능한 답변
        if any(word in user_lower for word in ["해줘", "만들어", "구현해"]):
            return any(
                word in response_lower
                for word in ["다음과 같이", "실행", "구현", "생성"]
            )

        # 평가에 대한 명확한 판단
        if any(word in user_lower for word in ["어떠니", "좋니", "성공했니"]):
            return any(
                word in response_lower
                for word in ["좋습니다", "나쁩니다", "성공", "실패"]
            )

        return True

    def _generate_improvement_suggestions(
        self, evaluation: Dict[str, Any]
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        if evaluation["overall_score"] < 0.6:
            suggestions.append("전반적인 응답 품질 향상 필요")

        # 세부 기준별 개선 제안
        detailed_scores = evaluation["detailed_scores"]

        if detailed_scores.get("의도_달성", 0) < 0.5:
            suggestions.append("사용자 의도에 더 정확히 맞는 답변 제공")

        if detailed_scores.get("통찰_포함", 0) < 0.5:
            suggestions.append("더 깊이 있는 분석과 통찰 포함")

        if detailed_scores.get("개선_유도", 0) < 0.5:
            suggestions.append("구체적인 개선 방안과 다음 단계 제시")

        if detailed_scores.get("교훈_명시", 0) < 0.5:
            suggestions.append("학습한 내용을 명확히 정리하여 교훈으로 제시")

        if detailed_scores.get("사용자_만족", 0) < 0.5:
            suggestions.append("사용자 관점에서 더 유용하고 만족스러운 답변 제공")

        return suggestions

    def _extract_learning_insights(self, evaluation: Dict[str, Any]) -> List[str]:
        """학습 인사이트 추출"""
        insights = []

        # 성공 요인 분석
        if evaluation["success_indicators"]:
            insights.append(
                f"성공 요인: {', '.join(evaluation['success_indicators'][:3])}"
            )

        # 실패 요인 분석
        if evaluation["failure_indicators"]:
            insights.append(
                f"개선 필요: {', '.join(evaluation['failure_indicators'][:3])}"
            )

        # 점수별 인사이트
        overall_score = evaluation["overall_score"]
        if overall_score > 0.8:
            insights.append("매우 우수한 응답 - 이 패턴을 유지하고 확장")
        elif overall_score > 0.6:
            insights.append("양호한 응답 - 일부 개선점 보완 필요")
        elif overall_score > 0.4:
            insights.append("보통 수준 - 전반적인 개선 필요")
        else:
            insights.append("개선 필요 - 근본적인 접근법 재검토 필요")

        return insights

    def _determine_success_level(self, score: float) -> str:
        """성공 수준 판정"""
        if score >= 0.8:
            return "매우 우수"
        elif score >= 0.6:
            return "양호"
        elif score >= 0.4:
            return "보통"
        elif score >= 0.2:
            return "미흡"
        else:
            return "부족"

    def _create_fallback_evaluation(
        self, user_input: str, duri_response: str
    ) -> Dict[str, Any]:
        """오류 시 기본 평가 생성"""
        return {
            "timestamp": datetime.now().isoformat(),
            "user_input": user_input,
            "duri_response": duri_response,
            "overall_score": 0.5,
            "detailed_scores": {
                "의도_달성": 0.5,
                "통찰_포함": 0.5,
                "개선_유도": 0.5,
                "교훈_명시": 0.5,
                "사용자_만족": 0.5,
            },
            "success_indicators": [],
            "failure_indicators": ["평가 시스템 오류"],
            "improvement_suggestions": ["평가 시스템 점검 필요"],
            "learning_insights": ["평가 중 오류 발생"],
            "is_success": True,
            "success_level": "보통",
        }

    def batch_evaluate(
        self, conversations: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """여러 대화의 결과를 일괄 평가"""
        evaluations = []

        for conversation in conversations:
            evaluation = self.evaluate_conversation(
                conversation.get("user_input", ""),
                conversation.get("duri_response", ""),
            )
            evaluations.append(evaluation)

        return evaluations

    def get_evaluation_summary(
        self, evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """평가 요약 생성"""
        if not evaluations:
            return {"error": "평가할 대화가 없습니다"}

        total_evaluations = len(evaluations)
        successful_evaluations = sum(
            1 for e in evaluations if e.get("is_success", False)
        )
        success_rate = (
            successful_evaluations / total_evaluations if total_evaluations > 0 else 0
        )

        # 평균 점수 계산
        total_score = sum(e.get("overall_score", 0) for e in evaluations)
        average_score = total_score / total_evaluations if total_evaluations > 0 else 0

        # 성공 수준별 분포
        success_levels = {}
        for evaluation in evaluations:
            level = evaluation.get("success_level", "보통")
            success_levels[level] = success_levels.get(level, 0) + 1

        # 주요 개선 제안 수집
        all_suggestions = []
        for evaluation in evaluations:
            all_suggestions.extend(evaluation.get("improvement_suggestions", []))

        # 주요 학습 인사이트 수집
        all_insights = []
        for evaluation in evaluations:
            all_insights.extend(evaluation.get("learning_insights", []))

        return {
            "total_evaluations": total_evaluations,
            "success_rate": success_rate,
            "average_score": average_score,
            "success_levels_distribution": success_levels,
            "key_improvements": list(set(all_suggestions))[:5],  # 중복 제거 후 상위 5개
            "key_insights": list(set(all_insights))[:5],  # 중복 제거 후 상위 5개
            "analysis_timestamp": datetime.now().isoformat(),
        }


# 전역 인스턴스
result_evaluator = ResultEvaluator()
