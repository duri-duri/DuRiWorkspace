#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 연역적 추론 모듈

연역적 추론을 담당하는 모듈입니다.
- 논리적 규칙 적용
- 전제-결론 구조 분석
- 연역적 추론 체인 구축
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class DeductiveRuleType(Enum):
    """연역적 규칙 유형"""

    MODUS_PONENS = "modus_ponens"  # 긍정 논법
    MODUS_TOLLENS = "modus_tollens"  # 부정 논법
    HYPOTHETICAL_SYLLOGISM = "hypothetical_syllogism"  # 가설적 삼단논법
    DISJUNCTIVE_SYLLOGISM = "disjunctive_syllogism"  # 선언적 삼단논법
    CONSTRUCTIVE_DILEMMA = "constructive_dilemma"  # 구성적 딜레마
    DESTRUCTIVE_DILEMMA = "destructive_dilemma"  # 파괴적 딜레마


@dataclass
class DeductivePremise:
    """연역적 전제"""

    premise_id: str
    content: str
    truth_value: bool = True
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeductiveConclusion:
    """연역적 결론"""

    conclusion_id: str
    content: str
    truth_value: bool = True
    confidence: float = 1.0
    reasoning_chain: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeductiveRule:
    """연역적 규칙"""

    rule_id: str
    rule_type: DeductiveRuleType
    premises: List[DeductivePremise]
    conclusion: DeductiveConclusion
    validity: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DeductiveAnalysis:
    """연역적 분석 결과"""

    validity_score: float
    soundness_score: float
    completeness_score: float
    reasoning_chains: List[List[str]] = field(default_factory=list)
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DeductiveReasoning:
    """연역적 추론 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.reasoning_history = []
        self.performance_metrics = {
            "total_reasonings": 0,
            "successful_reasonings": 0,
            "average_validity": 0.0,
            "average_soundness": 0.0,
        }
        self.logger.info("연역적 추론기 초기화 완료")

    async def perform_deductive_reasoning(
        self,
        premises: List[DeductivePremise],
        rule_type: DeductiveRuleType = DeductiveRuleType.MODUS_PONENS,
    ) -> DeductiveAnalysis:
        """연역적 추론 수행"""
        try:
            start_time = datetime.now()
            self.logger.info(f"연역적 추론 시작: {rule_type.value}")

            # 연역적 규칙 적용
            rule = self._create_deductive_rule(premises, rule_type)

            # 추론 체인 구축
            reasoning_chains = self._build_reasoning_chains(rule)

            # 분석 수행
            analysis = self._analyze_deductive_reasoning(rule, reasoning_chains)

            # 성능 메트릭 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(analysis, processing_time)

            # 추론 히스토리에 추가
            self.reasoning_history.append(
                {
                    "premises": premises,
                    "rule_type": rule_type,
                    "analysis": analysis,
                    "processing_time": processing_time,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(
                f"연역적 추론 완료: {rule_type.value}, 유효성: {analysis.validity_score:.2f}"
            )
            return analysis

        except Exception as e:
            self.logger.error(f"연역적 추론 중 오류 발생: {e}")
            return DeductiveAnalysis(
                validity_score=0.0,
                soundness_score=0.0,
                completeness_score=0.0,
                issues=[f"오류 발생: {str(e)}"],
            )

    def _create_deductive_rule(
        self, premises: List[DeductivePremise], rule_type: DeductiveRuleType
    ) -> DeductiveRule:
        """연역적 규칙 생성"""
        try:
            # 규칙 유형에 따른 결론 생성
            conclusion = self._generate_conclusion(premises, rule_type)

            rule = DeductiveRule(
                rule_id=f"rule_{len(self.reasoning_history)}",
                rule_type=rule_type,
                premises=premises,
                conclusion=conclusion,
            )

            return rule

        except Exception as e:
            self.logger.error(f"연역적 규칙 생성 중 오류: {e}")
            return DeductiveRule(
                rule_id="error",
                rule_type=rule_type,
                premises=premises,
                conclusion=DeductiveConclusion(
                    conclusion_id="error", content="오류 발생"
                ),
            )

    def _generate_conclusion(
        self, premises: List[DeductivePremise], rule_type: DeductiveRuleType
    ) -> DeductiveConclusion:
        """결론 생성"""
        try:
            if rule_type == DeductiveRuleType.MODUS_PONENS:
                return self._modus_ponens_conclusion(premises)
            elif rule_type == DeductiveRuleType.MODUS_TOLLENS:
                return self._modus_tollens_conclusion(premises)
            elif rule_type == DeductiveRuleType.HYPOTHETICAL_SYLLOGISM:
                return self._hypothetical_syllogism_conclusion(premises)
            elif rule_type == DeductiveRuleType.DISJUNCTIVE_SYLLOGISM:
                return self._disjunctive_syllogism_conclusion(premises)
            elif rule_type == DeductiveRuleType.CONSTRUCTIVE_DILEMMA:
                return self._constructive_dilemma_conclusion(premises)
            elif rule_type == DeductiveRuleType.DESTRUCTIVE_DILEMMA:
                return self._destructive_dilemma_conclusion(premises)
            else:
                return self._default_conclusion(premises)

        except Exception as e:
            self.logger.error(f"결론 생성 중 오류: {e}")
            return DeductiveConclusion(conclusion_id="error", content="결론 생성 오류")

    def _modus_ponens_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """긍정 논법 결론"""
        try:
            if len(premises) >= 2:
                # P → Q, P ⊢ Q
                antecedent = premises[0].content
                consequent = premises[1].content if len(premises) > 1 else "결론"

                conclusion_content = f"만약 {antecedent}라면 {consequent}이다."
                confidence = min(
                    premises[0].confidence,
                    premises[1].confidence if len(premises) > 1 else 1.0,
                )

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["긍정 논법 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 부족하여 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 부족"],
                )

        except Exception as e:
            self.logger.error(f"긍정 논법 결론 생성 중 오류: {e}")
            return DeductiveConclusion(conclusion_id="error", content="긍정 논법 오류")

    def _modus_tollens_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """부정 논법 결론"""
        try:
            if len(premises) >= 2:
                # P → Q, ¬Q ⊢ ¬P
                antecedent = premises[0].content
                negated_consequent = (
                    premises[1].content if len(premises) > 1 else "부정된 결론"
                )

                conclusion_content = f"만약 {antecedent}라면 {negated_consequent}이므로, {antecedent}는 거짓이다."
                confidence = min(
                    premises[0].confidence,
                    premises[1].confidence if len(premises) > 1 else 1.0,
                )

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["부정 논법 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 부족하여 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 부족"],
                )

        except Exception as e:
            self.logger.error(f"부정 논법 결론 생성 중 오류: {e}")
            return DeductiveConclusion(conclusion_id="error", content="부정 논법 오류")

    def _hypothetical_syllogism_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """가설적 삼단논법 결론"""
        try:
            if len(premises) >= 3:
                # P → Q, Q → R ⊢ P → R
                first_antecedent = premises[0].content
                second_antecedent = premises[1].content
                third_antecedent = premises[2].content

                conclusion_content = f"만약 {first_antecedent}라면 {second_antecedent}이고, {second_antecedent}라면 {third_antecedent}이므로, {first_antecedent}라면 {third_antecedent}이다."
                confidence = min(premise.confidence for premise in premises[:3])

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["가설적 삼단논법 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 부족하여 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 부족"],
                )

        except Exception as e:
            self.logger.error(f"가설적 삼단논법 결론 생성 중 오류: {e}")
            return DeductiveConclusion(
                conclusion_id="error", content="가설적 삼단논법 오류"
            )

    def _disjunctive_syllogism_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """선언적 삼단논법 결론"""
        try:
            if len(premises) >= 2:
                # P ∨ Q, ¬P ⊢ Q
                first_disjunct = premises[0].content
                negated_disjunct = (
                    premises[1].content if len(premises) > 1 else "부정된 선언"
                )

                conclusion_content = f"{first_disjunct} 또는 {negated_disjunct}이고, {negated_disjunct}가 거짓이므로 {first_disjunct}이다."
                confidence = min(
                    premises[0].confidence,
                    premises[1].confidence if len(premises) > 1 else 1.0,
                )

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["선언적 삼단논법 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 부족하여 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 부족"],
                )

        except Exception as e:
            self.logger.error(f"선언적 삼단논법 결론 생성 중 오류: {e}")
            return DeductiveConclusion(
                conclusion_id="error", content="선언적 삼단논법 오류"
            )

    def _constructive_dilemma_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """구성적 딜레마 결론"""
        try:
            if len(premises) >= 3:
                # (P → Q) ∧ (R → S), P ∨ R ⊢ Q ∨ S
                first_implication = premises[0].content
                second_implication = premises[1].content
                disjunction = premises[2].content

                conclusion_content = f"만약 {first_implication}이고 {second_implication}이며, {disjunction}이므로, 첫 번째 또는 두 번째 결과가 성립한다."
                confidence = min(premise.confidence for premise in premises[:3])

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["구성적 딜레마 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 부족하여 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 부족"],
                )

        except Exception as e:
            self.logger.error(f"구성적 딜레마 결론 생성 중 오류: {e}")
            return DeductiveConclusion(
                conclusion_id="error", content="구성적 딜레마 오류"
            )

    def _destructive_dilemma_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """파괴적 딜레마 결론"""
        try:
            if len(premises) >= 3:
                # (P → Q) ∧ (R → S), ¬Q ∨ ¬S ⊢ ¬P ∨ ¬R
                first_implication = premises[0].content
                second_implication = premises[1].content
                negated_disjunction = premises[2].content

                conclusion_content = f"만약 {first_implication}이고 {second_implication}이며, {negated_disjunction}이므로, 첫 번째 또는 두 번째 전제가 거짓이다."
                confidence = min(premise.confidence for premise in premises[:3])

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["파괴적 딜레마 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 부족하여 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 부족"],
                )

        except Exception as e:
            self.logger.error(f"파괴적 딜레마 결론 생성 중 오류: {e}")
            return DeductiveConclusion(
                conclusion_id="error", content="파괴적 딜레마 오류"
            )

    def _default_conclusion(
        self, premises: List[DeductivePremise]
    ) -> DeductiveConclusion:
        """기본 결론"""
        try:
            if premises:
                conclusion_content = (
                    f"주어진 전제들로부터 결론을 도출합니다: {premises[0].content}"
                )
                confidence = min(premise.confidence for premise in premises)

                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content=conclusion_content,
                    confidence=confidence,
                    reasoning_chain=["기본 추론 적용"],
                )
            else:
                return DeductiveConclusion(
                    conclusion_id=f"conclusion_{len(self.reasoning_history)}",
                    content="전제가 없어 결론을 도출할 수 없습니다.",
                    confidence=0.0,
                    reasoning_chain=["전제 없음"],
                )

        except Exception as e:
            self.logger.error(f"기본 결론 생성 중 오류: {e}")
            return DeductiveConclusion(conclusion_id="error", content="기본 결론 오류")

    def _build_reasoning_chains(self, rule: DeductiveRule) -> List[List[str]]:
        """추론 체인 구축"""
        try:
            chains = []

            # 기본 추론 체인
            basic_chain = [f"전제: {premise.content}" for premise in rule.premises]
            basic_chain.append(f"규칙: {rule.rule_type.value}")
            basic_chain.append(f"결론: {rule.conclusion.content}")
            chains.append(basic_chain)

            # 상세 추론 체인
            detailed_chain = []
            for i, premise in enumerate(rule.premises):
                detailed_chain.append(
                    f"전제 {i+1}: {premise.content} (신뢰도: {premise.confidence:.2f})"
                )
            detailed_chain.append(f"적용된 규칙: {rule.rule_type.value}")
            detailed_chain.append(
                f"도출된 결론: {rule.conclusion.content} (신뢰도: {rule.conclusion.confidence:.2f})"
            )
            chains.append(detailed_chain)

            return chains

        except Exception as e:
            self.logger.error(f"추론 체인 구축 중 오류: {e}")
            return [["추론 체인 구축 오류"]]

    def _analyze_deductive_reasoning(
        self, rule: DeductiveRule, reasoning_chains: List[List[str]]
    ) -> DeductiveAnalysis:
        """연역적 추론 분석"""
        try:
            # 유효성 분석
            validity_score = self._analyze_validity(rule)

            # 건전성 분석
            soundness_score = self._analyze_soundness(rule)

            # 완전성 분석
            completeness_score = self._analyze_completeness(rule)

            # 문제점 식별
            issues = self._identify_issues(rule)

            # 개선 제안
            suggestions = self._generate_suggestions(rule)

            return DeductiveAnalysis(
                validity_score=validity_score,
                soundness_score=soundness_score,
                completeness_score=completeness_score,
                reasoning_chains=reasoning_chains,
                issues=issues,
                suggestions=suggestions,
            )

        except Exception as e:
            self.logger.error(f"연역적 추론 분석 중 오류: {e}")
            return DeductiveAnalysis(
                validity_score=0.0,
                soundness_score=0.0,
                completeness_score=0.0,
                issues=[f"분석 오류: {str(e)}"],
            )

    def _analyze_validity(self, rule: DeductiveRule) -> float:
        """유효성 분석"""
        try:
            if not rule.premises:
                return 0.0

            # 전제와 결론의 논리적 연결성 확인
            validity_score = 1.0

            # 전제의 일관성 확인
            premise_contents = [premise.content.lower() for premise in rule.premises]
            for i, content1 in enumerate(premise_contents):
                for j, content2 in enumerate(premise_contents[i + 1 :], i + 1):
                    if self._are_premises_contradictory(content1, content2):
                        validity_score *= 0.5

            # 결론이 전제로부터 논리적으로 도출되는지 확인
            if not self._is_conclusion_logically_derived(rule):
                validity_score *= 0.7

            return validity_score

        except Exception as e:
            self.logger.error(f"유효성 분석 중 오류: {e}")
            return 0.0

    def _analyze_soundness(self, rule: DeductiveRule) -> float:
        """건전성 분석"""
        try:
            if not rule.premises:
                return 0.0

            # 전제의 진리성 확인
            premise_truth_scores = [premise.confidence for premise in rule.premises]
            average_truth_score = sum(premise_truth_scores) / len(premise_truth_scores)

            # 결론의 신뢰도
            conclusion_confidence = rule.conclusion.confidence

            # 건전성 점수 (전제의 진리성과 결론의 신뢰도의 조합)
            soundness_score = (average_truth_score + conclusion_confidence) / 2

            return soundness_score

        except Exception as e:
            self.logger.error(f"건전성 분석 중 오류: {e}")
            return 0.0

    def _analyze_completeness(self, rule: DeductiveRule) -> float:
        """완전성 분석"""
        try:
            # 전제의 수와 복잡성을 기반으로 한 완전성 평가
            premise_count = len(rule.premises)
            conclusion_complexity = len(rule.conclusion.content)

            # 완전성 점수 계산
            completeness_score = min(
                1.0, (premise_count + conclusion_complexity / 50) / 5.0
            )

            return completeness_score

        except Exception as e:
            self.logger.error(f"완전성 분석 중 오류: {e}")
            return 0.0

    def _are_premises_contradictory(self, content1: str, content2: str) -> bool:
        """전제 간 모순 확인"""
        try:
            # 간단한 모순 검사
            opposite_pairs = [
                ("true", "false"),
                ("yes", "no"),
                ("positive", "negative"),
                ("good", "bad"),
                ("correct", "incorrect"),
                ("valid", "invalid"),
            ]

            for pair in opposite_pairs:
                if (pair[0] in content1 and pair[1] in content2) or (
                    pair[1] in content1 and pair[0] in content2
                ):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"전제 모순 확인 중 오류: {e}")
            return False

    def _is_conclusion_logically_derived(self, rule: DeductiveRule) -> bool:
        """결론이 논리적으로 도출되는지 확인"""
        try:
            # 간단한 논리적 도출 확인
            premise_contents = [premise.content.lower() for premise in rule.premises]
            conclusion_content = rule.conclusion.content.lower()

            # 결론이 전제와 관련이 있는지 확인
            for premise_content in premise_contents:
                if any(word in conclusion_content for word in premise_content.split()):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"논리적 도출 확인 중 오류: {e}")
            return False

    def _identify_issues(self, rule: DeductiveRule) -> List[str]:
        """문제점 식별"""
        issues = []

        try:
            # 전제가 부족한 경우
            if len(rule.premises) < 2:
                issues.append("전제가 부족합니다.")

            # 신뢰도가 낮은 전제들
            low_confidence_premises = [
                premise for premise in rule.premises if premise.confidence < 0.5
            ]
            if low_confidence_premises:
                issues.append(
                    f"신뢰도가 낮은 전제가 {len(low_confidence_premises)}개 있습니다."
                )

            # 결론의 신뢰도가 낮은 경우
            if rule.conclusion.confidence < 0.5:
                issues.append("결론의 신뢰도가 낮습니다.")

            return issues

        except Exception as e:
            self.logger.error(f"문제점 식별 중 오류: {e}")
            return [f"문제점 식별 오류: {str(e)}"]

    def _generate_suggestions(self, rule: DeductiveRule) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        try:
            # 전제가 부족한 경우
            if len(rule.premises) < 2:
                suggestions.append("더 많은 전제를 추가하여 추론을 강화하세요.")

            # 신뢰도가 낮은 전제들
            low_confidence_premises = [
                premise for premise in rule.premises if premise.confidence < 0.5
            ]
            if low_confidence_premises:
                suggestions.append("신뢰도가 낮은 전제들을 개선하거나 대체하세요.")

            # 결론의 신뢰도가 낮은 경우
            if rule.conclusion.confidence < 0.5:
                suggestions.append("결론의 신뢰도를 높이기 위해 전제를 강화하세요.")

            # 규칙 유형별 제안
            if rule.rule_type == DeductiveRuleType.MODUS_PONENS:
                suggestions.append("긍정 논법을 위해 명확한 조건문 구조를 사용하세요.")
            elif rule.rule_type == DeductiveRuleType.MODUS_TOLLENS:
                suggestions.append("부정 논법을 위해 부정된 결론을 명시하세요.")
            elif rule.rule_type == DeductiveRuleType.HYPOTHETICAL_SYLLOGISM:
                suggestions.append("가설적 삼단논법을 위해 연쇄적 조건문을 구성하세요.")

            return suggestions

        except Exception as e:
            self.logger.error(f"개선 제안 생성 중 오류: {e}")
            return [f"제안 생성 오류: {str(e)}"]

    def _update_performance_metrics(
        self, analysis: DeductiveAnalysis, processing_time: float
    ):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_reasonings"] += 1
        if analysis.validity_score > 0.5 and analysis.soundness_score > 0.5:
            self.performance_metrics["successful_reasonings"] += 1

        # 평균 유효성 업데이트
        total_validity = self.performance_metrics["average_validity"] * (
            self.performance_metrics["total_reasonings"] - 1
        )
        self.performance_metrics["average_validity"] = (
            total_validity + analysis.validity_score
        ) / self.performance_metrics["total_reasonings"]

        # 평균 건전성 업데이트
        total_soundness = self.performance_metrics["average_soundness"] * (
            self.performance_metrics["total_reasonings"] - 1
        )
        self.performance_metrics["average_soundness"] = (
            total_soundness + analysis.soundness_score
        ) / self.performance_metrics["total_reasonings"]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics.copy()

    def get_reasoning_history(self) -> List[Dict[str, Any]]:
        """추론 히스토리 조회"""
        return self.reasoning_history.copy()
