#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 가설적 추론 모듈

가설적 추론을 담당하는 모듈입니다.
- 관찰된 현상 분석
- 가능한 가설 생성
- 최적 가설 선택
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class AbductiveType(Enum):
    """가설적 추론 유형"""

    SIMPLE = "simple"  # 단순 가설
    COMPLEX = "complex"  # 복합 가설
    COMPETITIVE = "competitive"  # 경쟁 가설
    HIERARCHICAL = "hierarchical"  # 계층적 가설
    PROBABILISTIC = "probabilistic"  # 확률적 가설


@dataclass
class AbductiveObservation:
    """가설적 관찰"""

    observation_id: str
    content: str
    context: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbductiveHypothesis:
    """가설적 가설"""

    hypothesis_id: str
    content: str
    explanation_power: float = 1.0
    simplicity: float = 1.0
    testability: float = 1.0
    supporting_evidence: List[str] = field(default_factory=list)
    conflicting_evidence: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbductiveExplanation:
    """가설적 설명"""

    explanation_id: str
    hypothesis: AbductiveHypothesis
    observations: List[AbductiveObservation]
    explanatory_power: float = 1.0
    coherence: float = 1.0
    completeness: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AbductiveAnalysis:
    """가설적 분석 결과"""

    best_hypothesis: AbductiveHypothesis
    alternative_hypotheses: List[AbductiveHypothesis]
    explanatory_power: float
    coherence_score: float
    completeness_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AbductiveReasoning:
    """가설적 추론 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_history = []
        self.performance_metrics = {
            "total_reasonings": 0,
            "successful_reasonings": 0,
            "average_explanatory_power": 0.0,
            "average_coherence": 0.0,
        }
        self.logger.info("가설적 추론기 초기화 완료")

    async def perform_abductive_reasoning(
        self,
        observations: List[AbductiveObservation],
        abductive_type: AbductiveType = AbductiveType.SIMPLE,
    ) -> AbductiveAnalysis:
        """가설적 추론 수행"""
        try:
            start_time = datetime.now()
            self.logger.info(f"가설적 추론 시작: {abductive_type.value}")

            # 가설 생성
            hypotheses = self._generate_hypotheses(observations, abductive_type)

            # 가설 평가
            evaluated_hypotheses = self._evaluate_hypotheses(hypotheses, observations)

            # 최적 가설 선택
            best_hypothesis = self._select_best_hypothesis(evaluated_hypotheses)

            # 분석 수행
            analysis = self._analyze_abductive_reasoning(
                best_hypothesis, evaluated_hypotheses, observations
            )

            # 성능 메트릭 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(analysis, processing_time)

            # 추론 히스토리에 추가
            self.reasoning_history.append(
                {
                    "observations": observations,
                    "abductive_type": abductive_type,
                    "analysis": analysis,
                    "processing_time": processing_time,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(
                f"가설적 추론 완료: {abductive_type.value}, 설명력: {analysis.explanatory_power:.2f}"
            )
            return analysis

        except Exception as e:
            self.logger.error(f"가설적 추론 중 오류 발생: {e}")
            return AbductiveAnalysis(
                best_hypothesis=AbductiveHypothesis(hypothesis_id="error", content="오류 발생"),
                alternative_hypotheses=[],
                explanatory_power=0.0,
                coherence_score=0.0,
                completeness_score=0.0,
                issues=[f"오류 발생: {str(e)}"],
            )

    def _generate_hypotheses(
        self, observations: List[AbductiveObservation], abductive_type: AbductiveType
    ) -> List[AbductiveHypothesis]:
        """가설 생성"""
        hypotheses = []

        try:
            if abductive_type == AbductiveType.SIMPLE:
                hypotheses = self._generate_simple_hypotheses(observations)
            elif abductive_type == AbductiveType.COMPLEX:
                hypotheses = self._generate_complex_hypotheses(observations)
            elif abductive_type == AbductiveType.COMPETITIVE:
                hypotheses = self._generate_competitive_hypotheses(observations)
            elif abductive_type == AbductiveType.HIERARCHICAL:
                hypotheses = self._generate_hierarchical_hypotheses(observations)
            elif abductive_type == AbductiveType.PROBABILISTIC:
                hypotheses = self._generate_probabilistic_hypotheses(observations)
            else:
                hypotheses = self._generate_general_hypotheses(observations)

            return hypotheses

        except Exception as e:
            self.logger.error(f"가설 생성 중 오류: {e}")
            return []

    def _generate_simple_hypotheses(
        self, observations: List[AbductiveObservation]
    ) -> List[AbductiveHypothesis]:
        """단순 가설 생성"""
        hypotheses = []

        try:
            for i, observation in enumerate(observations):
                # 각 관찰에 대한 단순한 가설 생성
                hypothesis_content = f"가설 {i+1}: {observation.content}의 원인은 {self._generate_cause(observation.content)}이다."

                hypothesis = AbductiveHypothesis(
                    hypothesis_id=f"simple_hypothesis_{i}",
                    content=hypothesis_content,
                    explanation_power=0.7,
                    simplicity=0.9,
                    testability=0.8,
                    supporting_evidence=[observation.content],
                )
                hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            self.logger.error(f"단순 가설 생성 중 오류: {e}")
            return []

    def _generate_complex_hypotheses(
        self, observations: List[AbductiveObservation]
    ) -> List[AbductiveHypothesis]:
        """복합 가설 생성"""
        hypotheses = []

        try:
            if len(observations) >= 2:
                # 여러 관찰을 종합한 복합 가설 생성
                combined_content = " 및 ".join([obs.content for obs in observations[:3]])
                hypothesis_content = f"복합 가설: {combined_content}의 상호작용으로 인한 현상이다."

                hypothesis = AbductiveHypothesis(
                    hypothesis_id="complex_hypothesis_0",
                    content=hypothesis_content,
                    explanation_power=0.8,
                    simplicity=0.6,
                    testability=0.7,
                    supporting_evidence=[obs.content for obs in observations[:3]],
                )
                hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            self.logger.error(f"복합 가설 생성 중 오류: {e}")
            return []

    def _generate_competitive_hypotheses(
        self, observations: List[AbductiveObservation]
    ) -> List[AbductiveHypothesis]:
        """경쟁 가설 생성"""
        hypotheses = []

        try:
            # 서로 다른 관점의 경쟁 가설 생성
            for i, observation in enumerate(observations[:3]):  # 최대 3개 가설
                perspective = ["내부적", "외부적", "시스템적"][i % 3]
                hypothesis_content = f"경쟁 가설 {i+1} ({perspective} 관점): {observation.content}는 {perspective} 요인에 의해 발생한다."

                hypothesis = AbductiveHypothesis(
                    hypothesis_id=f"competitive_hypothesis_{i}",
                    content=hypothesis_content,
                    explanation_power=0.6,
                    simplicity=0.7,
                    testability=0.6,
                    supporting_evidence=[observation.content],
                )
                hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            self.logger.error(f"경쟁 가설 생성 중 오류: {e}")
            return []

    def _generate_hierarchical_hypotheses(
        self, observations: List[AbductiveObservation]
    ) -> List[AbductiveHypothesis]:
        """계층적 가설 생성"""
        hypotheses = []

        try:
            # 계층적 구조의 가설 생성
            levels = ["미시적", "중간적", "거시적"]

            for i, level in enumerate(levels):
                if i < len(observations):
                    hypothesis_content = f"계층적 가설 {i+1} ({level} 수준): {observations[i].content}는 {level} 수준의 요인에 의해 설명된다."

                    hypothesis = AbductiveHypothesis(
                        hypothesis_id=f"hierarchical_hypothesis_{i}",
                        content=hypothesis_content,
                        explanation_power=0.7,
                        simplicity=0.8,
                        testability=0.7,
                        supporting_evidence=[observations[i].content],
                    )
                    hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            self.logger.error(f"계층적 가설 생성 중 오류: {e}")
            return []

    def _generate_probabilistic_hypotheses(
        self, observations: List[AbductiveObservation]
    ) -> List[AbductiveHypothesis]:
        """확률적 가설 생성"""
        hypotheses = []

        try:
            # 확률적 특성을 고려한 가설 생성
            for i, observation in enumerate(observations[:3]):
                probability = 0.6 + (i * 0.1)  # 0.6, 0.7, 0.8
                hypothesis_content = f"확률적 가설 {i+1} (확률: {probability:.1%}): {observation.content}는 {probability:.1%}의 확률로 발생할 수 있다."

                hypothesis = AbductiveHypothesis(
                    hypothesis_id=f"probabilistic_hypothesis_{i}",
                    content=hypothesis_content,
                    explanation_power=probability,
                    simplicity=0.8,
                    testability=0.7,
                    supporting_evidence=[observation.content],
                )
                hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            self.logger.error(f"확률적 가설 생성 중 오류: {e}")
            return []

    def _generate_general_hypotheses(
        self, observations: List[AbductiveObservation]
    ) -> List[AbductiveHypothesis]:
        """일반 가설 생성"""
        hypotheses = []

        try:
            if observations:
                hypothesis_content = f"일반 가설: {observations[0].content}에 대한 일반적인 설명"

                hypothesis = AbductiveHypothesis(
                    hypothesis_id="general_hypothesis_0",
                    content=hypothesis_content,
                    explanation_power=0.5,
                    simplicity=0.7,
                    testability=0.6,
                    supporting_evidence=[obs.content for obs in observations[:2]],
                )
                hypotheses.append(hypothesis)

            return hypotheses

        except Exception as e:
            self.logger.error(f"일반 가설 생성 중 오류: {e}")
            return []

    def _generate_cause(self, observation_content: str) -> str:
        """원인 생성"""
        try:
            # 간단한 원인 생성 로직
            causes = [
                "내부적 요인",
                "외부적 요인",
                "시스템적 요인",
                "환경적 요인",
                "인간적 요인",
            ]

            # 관찰 내용에 따른 원인 선택
            content_lower = observation_content.lower()
            if any(word in content_lower for word in ["system", "machine", "computer"]):
                return "시스템적 요인"
            elif any(word in content_lower for word in ["human", "person", "user"]):
                return "인간적 요인"
            elif any(word in content_lower for word in ["environment", "weather", "climate"]):
                return "환경적 요인"
            else:
                return causes[hash(observation_content) % len(causes)]

        except Exception as e:
            self.logger.error(f"원인 생성 중 오류: {e}")
            return "알 수 없는 요인"

    def _evaluate_hypotheses(
        self,
        hypotheses: List[AbductiveHypothesis],
        observations: List[AbductiveObservation],
    ) -> List[AbductiveHypothesis]:
        """가설 평가"""
        evaluated_hypotheses = []

        try:
            for hypothesis in hypotheses:
                # 설명력 평가
                explanation_power = self._evaluate_explanation_power(hypothesis, observations)

                # 간단성 평가
                simplicity = self._evaluate_simplicity(hypothesis)

                # 검증 가능성 평가
                testability = self._evaluate_testability(hypothesis)

                # 종합 점수 계산
                overall_score = (explanation_power + simplicity + testability) / 3

                # 가설 업데이트
                hypothesis.explanation_power = explanation_power
                hypothesis.simplicity = simplicity
                hypothesis.testability = testability

                evaluated_hypotheses.append(hypothesis)

            return evaluated_hypotheses

        except Exception as e:
            self.logger.error(f"가설 평가 중 오류: {e}")
            return hypotheses

    def _evaluate_explanation_power(
        self, hypothesis: AbductiveHypothesis, observations: List[AbductiveObservation]
    ) -> float:
        """설명력 평가"""
        try:
            # 가설이 관찰들을 얼마나 잘 설명하는지 평가
            explained_observations = 0
            total_observations = len(observations)

            if total_observations == 0:
                return 0.0

            for observation in observations:
                if self._can_explain(hypothesis, observation):
                    explained_observations += 1

            explanation_power = explained_observations / total_observations
            return min(1.0, explanation_power)

        except Exception as e:
            self.logger.error(f"설명력 평가 중 오류: {e}")
            return 0.5

    def _evaluate_simplicity(self, hypothesis: AbductiveHypothesis) -> float:
        """간단성 평가"""
        try:
            # 가설의 복잡성을 평가 (간단할수록 높은 점수)
            content_length = len(hypothesis.content)
            word_count = len(hypothesis.content.split())

            # 길이와 단어 수를 기반으로 간단성 계산
            length_simplicity = max(0.0, 1.0 - (content_length / 200.0))
            word_simplicity = max(0.0, 1.0 - (word_count / 50.0))

            simplicity = (length_simplicity + word_simplicity) / 2
            return min(1.0, simplicity)

        except Exception as e:
            self.logger.error(f"간단성 평가 중 오류: {e}")
            return 0.5

    def _evaluate_testability(self, hypothesis: AbductiveHypothesis) -> float:
        """검증 가능성 평가"""
        try:
            # 가설이 얼마나 검증 가능한지 평가
            content_lower = hypothesis.content.lower()

            # 검증 가능한 키워드 확인
            testable_keywords = [
                "test",
                "measure",
                "observe",
                "experiment",
                "verify",
                "confirm",
            ]
            testable_count = sum(1 for keyword in testable_keywords if keyword in content_lower)

            # 검증 가능성 점수 계산
            testability = min(1.0, testable_count / len(testable_keywords) + 0.3)
            return testability

        except Exception as e:
            self.logger.error(f"검증 가능성 평가 중 오류: {e}")
            return 0.5

    def _can_explain(
        self, hypothesis: AbductiveHypothesis, observation: AbductiveObservation
    ) -> bool:
        """가설이 관찰을 설명할 수 있는지 확인"""
        try:
            # 간단한 설명 가능성 확인
            hypothesis_content = hypothesis.content.lower()
            observation_content = observation.content.lower()

            # 공통 단어 확인
            hypothesis_words = set(hypothesis_content.split())
            observation_words = set(observation_content.split())

            common_words = hypothesis_words.intersection(observation_words)
            return len(common_words) > 0

        except Exception as e:
            self.logger.error(f"설명 가능성 확인 중 오류: {e}")
            return False

    def _select_best_hypothesis(self, hypotheses: List[AbductiveHypothesis]) -> AbductiveHypothesis:
        """최적 가설 선택"""
        try:
            if not hypotheses:
                return AbductiveHypothesis(hypothesis_id="none", content="가설 없음")

            # 종합 점수 계산
            best_hypothesis = None
            best_score = 0.0

            for hypothesis in hypotheses:
                # 가중 평균 점수 계산
                score = (
                    hypothesis.explanation_power * 0.5
                    + hypothesis.simplicity * 0.3
                    + hypothesis.testability * 0.2
                )

                if score > best_score:
                    best_score = score
                    best_hypothesis = hypothesis

            return best_hypothesis if best_hypothesis else hypotheses[0]

        except Exception as e:
            self.logger.error(f"최적 가설 선택 중 오류: {e}")
            return AbductiveHypothesis(hypothesis_id="error", content="선택 오류")

    def _analyze_abductive_reasoning(
        self,
        best_hypothesis: AbductiveHypothesis,
        all_hypotheses: List[AbductiveHypothesis],
        observations: List[AbductiveObservation],
    ) -> AbductiveAnalysis:
        """가설적 추론 분석"""
        try:
            # 설명력 분석
            explanatory_power = best_hypothesis.explanation_power

            # 일관성 분석
            coherence_score = self._analyze_coherence(best_hypothesis, observations)

            # 완전성 분석
            completeness_score = self._analyze_completeness(best_hypothesis, observations)

            # 대안 가설들
            alternative_hypotheses = [
                h for h in all_hypotheses if h.hypothesis_id != best_hypothesis.hypothesis_id
            ]

            # 문제점 식별
            issues = self._identify_issues(best_hypothesis, alternative_hypotheses)

            # 개선 제안
            suggestions = self._generate_suggestions(best_hypothesis, alternative_hypotheses)

            return AbductiveAnalysis(
                best_hypothesis=best_hypothesis,
                alternative_hypotheses=alternative_hypotheses,
                explanatory_power=explanatory_power,
                coherence_score=coherence_score,
                completeness_score=completeness_score,
                issues=issues,
                suggestions=suggestions,
            )

        except Exception as e:
            self.logger.error(f"가설적 추론 분석 중 오류: {e}")
            return AbductiveAnalysis(
                best_hypothesis=best_hypothesis,
                alternative_hypotheses=[],
                explanatory_power=0.0,
                coherence_score=0.0,
                completeness_score=0.0,
                issues=[f"분석 오류: {str(e)}"],
            )

    def _analyze_coherence(
        self, hypothesis: AbductiveHypothesis, observations: List[AbductiveObservation]
    ) -> float:
        """일관성 분석"""
        try:
            # 가설과 관찰들 간의 일관성 분석
            coherent_observations = 0
            total_observations = len(observations)

            if total_observations == 0:
                return 0.0

            for observation in observations:
                if self._is_coherent(hypothesis, observation):
                    coherent_observations += 1

            coherence_score = coherent_observations / total_observations
            return min(1.0, coherence_score)

        except Exception as e:
            self.logger.error(f"일관성 분석 중 오류: {e}")
            return 0.5

    def _analyze_completeness(
        self, hypothesis: AbductiveHypothesis, observations: List[AbductiveObservation]
    ) -> float:
        """완전성 분석"""
        try:
            # 가설이 관찰들을 얼마나 완전히 설명하는지 분석
            explained_observations = 0
            total_observations = len(observations)

            if total_observations == 0:
                return 0.0

            for observation in observations:
                if self._is_completely_explained(hypothesis, observation):
                    explained_observations += 1

            completeness_score = explained_observations / total_observations
            return min(1.0, completeness_score)

        except Exception as e:
            self.logger.error(f"완전성 분석 중 오류: {e}")
            return 0.5

    def _is_coherent(
        self, hypothesis: AbductiveHypothesis, observation: AbductiveObservation
    ) -> bool:
        """일관성 확인"""
        try:
            # 가설과 관찰이 일관되는지 확인
            hypothesis_content = hypothesis.content.lower()
            observation_content = observation.content.lower()

            # 반대되는 키워드 확인
            opposite_pairs = [
                ("true", "false"),
                ("yes", "no"),
                ("positive", "negative"),
                ("good", "bad"),
                ("correct", "incorrect"),
                ("valid", "invalid"),
            ]

            for pair in opposite_pairs:
                if (pair[0] in hypothesis_content and pair[1] in observation_content) or (
                    pair[1] in hypothesis_content and pair[0] in observation_content
                ):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"일관성 확인 중 오류: {e}")
            return True

    def _is_completely_explained(
        self, hypothesis: AbductiveHypothesis, observation: AbductiveObservation
    ) -> bool:
        """완전한 설명 확인"""
        try:
            # 가설이 관찰을 완전히 설명하는지 확인
            hypothesis_content = hypothesis.content.lower()
            observation_content = observation.content.lower()

            # 관찰의 주요 요소들이 가설에 포함되어 있는지 확인
            observation_words = set(observation_content.split())
            hypothesis_words = set(hypothesis_content.split())

            # 50% 이상의 단어가 포함되어 있으면 완전한 설명으로 간주
            common_words = observation_words.intersection(hypothesis_words)
            coverage = len(common_words) / len(observation_words) if observation_words else 0

            return coverage > 0.5

        except Exception as e:
            self.logger.error(f"완전한 설명 확인 중 오류: {e}")
            return False

    def _identify_issues(
        self,
        best_hypothesis: AbductiveHypothesis,
        alternative_hypotheses: List[AbductiveHypothesis],
    ) -> List[str]:
        """문제점 식별"""
        issues = []

        try:
            # 설명력이 낮은 경우
            if best_hypothesis.explanation_power < 0.5:
                issues.append("가설의 설명력이 낮습니다.")

            # 간단성이 낮은 경우
            if best_hypothesis.simplicity < 0.5:
                issues.append("가설이 너무 복잡합니다.")

            # 검증 가능성이 낮은 경우
            if best_hypothesis.testability < 0.5:
                issues.append("가설의 검증 가능성이 낮습니다.")

            # 대안 가설이 많은 경우
            if len(alternative_hypotheses) > 3:
                issues.append("너무 많은 대안 가설이 존재합니다.")

            return issues

        except Exception as e:
            self.logger.error(f"문제점 식별 중 오류: {e}")
            return [f"문제점 식별 오류: {str(e)}"]

    def _generate_suggestions(
        self,
        best_hypothesis: AbductiveHypothesis,
        alternative_hypotheses: List[AbductiveHypothesis],
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        try:
            # 설명력이 낮은 경우
            if best_hypothesis.explanation_power < 0.5:
                suggestions.append("가설의 설명력을 높이기 위해 더 많은 관찰을 고려하세요.")

            # 간단성이 낮은 경우
            if best_hypothesis.simplicity < 0.5:
                suggestions.append("가설을 더 간단하게 표현하세요.")

            # 검증 가능성이 낮은 경우
            if best_hypothesis.testability < 0.5:
                suggestions.append("가설을 검증 가능한 형태로 재구성하세요.")

            # 대안 가설이 많은 경우
            if len(alternative_hypotheses) > 3:
                suggestions.append("대안 가설들을 통합하거나 우선순위를 설정하세요.")

            return suggestions

        except Exception as e:
            self.logger.error(f"개선 제안 생성 중 오류: {e}")
            return [f"제안 생성 오류: {str(e)}"]

    def _update_performance_metrics(self, analysis: AbductiveAnalysis, processing_time: float):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_reasonings"] += 1
        if analysis.explanatory_power > 0.5 and analysis.coherence_score > 0.5:
            self.performance_metrics["successful_reasonings"] += 1

        # 평균 설명력 업데이트
        total_explanatory_power = self.performance_metrics["average_explanatory_power"] * (
            self.performance_metrics["total_reasonings"] - 1
        )
        self.performance_metrics["average_explanatory_power"] = (
            total_explanatory_power + analysis.explanatory_power
        ) / self.performance_metrics["total_reasonings"]

        # 평균 일관성 업데이트
        total_coherence = self.performance_metrics["average_coherence"] * (
            self.performance_metrics["total_reasonings"] - 1
        )
        self.performance_metrics["average_coherence"] = (
            total_coherence + analysis.coherence_score
        ) / self.performance_metrics["total_reasonings"]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics.copy()

    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """추론 히스토리 조회"""
        return self.reasoning_history.copy()
