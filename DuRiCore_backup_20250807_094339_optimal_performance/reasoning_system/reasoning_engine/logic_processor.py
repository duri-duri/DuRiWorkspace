#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 추론 시스템 - 논리 처리 모듈

논리 처리 및 분석을 담당하는 모듈입니다.
- 논리적 규칙 처리
- 논리적 일관성 검증
- 논리적 추론 체인 분석
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

logger = logging.getLogger(__name__)


class LogicType(Enum):
    """논리 유형"""

    PROPOSITIONAL = "propositional"  # 명제 논리
    PREDICATE = "predicate"  # 술어 논리
    MODAL = "modal"  # 양상 논리
    TEMPORAL = "temporal"  # 시간 논리
    FUZZY = "fuzzy"  # 퍼지 논리
    INTUITIONISTIC = "intuitionistic"  # 직관주의 논리


@dataclass
class LogicalRule:
    """논리적 규칙"""

    rule_id: str
    rule_type: LogicType
    premises: List[str]
    conclusion: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogicalChain:
    """논리적 체인"""

    chain_id: str
    steps: List[LogicalRule]
    conclusion: str
    confidence: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LogicAnalysis:
    """논리 분석 결과"""

    consistency_score: float
    completeness_score: float
    validity_score: float
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LogicProcessor:
    """논리 처리 클래스"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logical_rules = {}
        self.processing_history = []
        self.performance_metrics = {
            "total_processings": 0,
            "successful_processings": 0,
            "average_consistency": 0.0,
            "average_completeness": 0.0,
        }
        self.logger.info("논리 처리기 초기화 완료")

    async def process_logic(
        self,
        input_data: Dict[str, Any],
        logic_type: LogicType = LogicType.PROPOSITIONAL,
    ) -> LogicAnalysis:
        """논리 처리 수행"""
        try:
            start_time = datetime.now()
            self.logger.info(f"논리 처리 시작: {logic_type.value}")

            # 논리적 규칙 추출
            rules = self._extract_logical_rules(input_data, logic_type)

            # 논리적 체인 구축
            chains = self._build_logical_chains(rules)

            # 논리적 분석 수행
            analysis = self._analyze_logic(chains, logic_type)

            # 성능 메트릭 업데이트
            processing_time = (datetime.now() - start_time).total_seconds()
            self._update_performance_metrics(analysis, processing_time)

            # 처리 히스토리에 추가
            self.processing_history.append(
                {
                    "input_data": input_data,
                    "logic_type": logic_type,
                    "analysis": analysis,
                    "processing_time": processing_time,
                    "timestamp": datetime.now(),
                }
            )

            self.logger.info(
                f"논리 처리 완료: {logic_type.value}, 일관성: {analysis.consistency_score:.2f}"
            )
            return analysis

        except Exception as e:
            self.logger.error(f"논리 처리 중 오류 발생: {e}")
            return LogicAnalysis(
                consistency_score=0.0,
                completeness_score=0.0,
                validity_score=0.0,
                issues=[f"오류 발생: {str(e)}"],
            )

    def _extract_logical_rules(
        self, input_data: Dict[str, Any], logic_type: LogicType
    ) -> List[LogicalRule]:
        """논리적 규칙 추출"""
        rules = []

        try:
            for key, value in input_data.items():
                if (
                    isinstance(value, dict)
                    and "premises" in value
                    and "conclusion" in value
                ):
                    rule = LogicalRule(
                        rule_id=f"rule_{len(rules)}",
                        rule_type=logic_type,
                        premises=value.get("premises", []),
                        conclusion=value.get("conclusion", ""),
                        confidence=value.get("confidence", 0.5),
                    )
                    rules.append(rule)
                elif isinstance(value, str):
                    # 간단한 문자열을 규칙으로 변환
                    rule = LogicalRule(
                        rule_id=f"rule_{len(rules)}",
                        rule_type=logic_type,
                        premises=[f"입력: {key}"],
                        conclusion=value,
                        confidence=0.5,
                    )
                    rules.append(rule)

            self.logger.info(f"{len(rules)}개의 논리적 규칙 추출됨")
            return rules

        except Exception as e:
            self.logger.error(f"논리적 규칙 추출 중 오류: {e}")
            return []

    def _build_logical_chains(self, rules: List[LogicalRule]) -> List[LogicalChain]:
        """논리적 체인 구축"""
        chains = []

        try:
            # 단일 규칙 체인
            for rule in rules:
                chain = LogicalChain(
                    chain_id=f"chain_{len(chains)}",
                    steps=[rule],
                    conclusion=rule.conclusion,
                    confidence=rule.confidence,
                )
                chains.append(chain)

            # 복합 체인 구축 (규칙 간 연결)
            composite_chains = self._build_composite_chains(rules)
            chains.extend(composite_chains)

            self.logger.info(f"{len(chains)}개의 논리적 체인 구축됨")
            return chains

        except Exception as e:
            self.logger.error(f"논리적 체인 구축 중 오류: {e}")
            return []

    def _build_composite_chains(self, rules: List[LogicalRule]) -> List[LogicalChain]:
        """복합 체인 구축"""
        composite_chains = []

        try:
            # 규칙 간 연결 가능성 분석
            for i, rule1 in enumerate(rules):
                for j, rule2 in enumerate(rules[i + 1 :], i + 1):
                    if self._can_connect_rules(rule1, rule2):
                        chain = LogicalChain(
                            chain_id=f"composite_chain_{len(composite_chains)}",
                            steps=[rule1, rule2],
                            conclusion=rule2.conclusion,
                            confidence=min(rule1.confidence, rule2.confidence),
                        )
                        composite_chains.append(chain)

            return composite_chains

        except Exception as e:
            self.logger.error(f"복합 체인 구축 중 오류: {e}")
            return []

    def _can_connect_rules(self, rule1: LogicalRule, rule2: LogicalRule) -> bool:
        """규칙 간 연결 가능성 확인"""
        try:
            # 간단한 연결 조건: rule1의 결론이 rule2의 전제와 관련이 있는지
            rule1_conclusion = rule1.conclusion.lower()
            for premise in rule2.premises:
                if any(word in rule1_conclusion for word in premise.lower().split()):
                    return True
            return False
        except Exception as e:
            self.logger.error(f"규칙 연결 확인 중 오류: {e}")
            return False

    def _analyze_logic(
        self, chains: List[LogicalChain], logic_type: LogicType
    ) -> LogicAnalysis:
        """논리 분석 수행"""
        try:
            # 일관성 분석
            consistency_score = self._analyze_consistency(chains)

            # 완전성 분석
            completeness_score = self._analyze_completeness(chains)

            # 유효성 분석
            validity_score = self._analyze_validity(chains)

            # 문제점 식별
            issues = self._identify_issues(chains)

            # 개선 제안
            suggestions = self._generate_suggestions(chains, logic_type)

            return LogicAnalysis(
                consistency_score=consistency_score,
                completeness_score=completeness_score,
                validity_score=validity_score,
                issues=issues,
                suggestions=suggestions,
            )

        except Exception as e:
            self.logger.error(f"논리 분석 중 오류: {e}")
            return LogicAnalysis(
                consistency_score=0.0,
                completeness_score=0.0,
                validity_score=0.0,
                issues=[f"분석 오류: {str(e)}"],
            )

    def _analyze_consistency(self, chains: List[LogicalChain]) -> float:
        """일관성 분석"""
        try:
            if not chains:
                return 0.0

            consistency_scores = []
            conclusions = []

            for chain in chains:
                # 체인 내부 일관성
                chain_consistency = self._check_chain_consistency(chain)
                consistency_scores.append(chain_consistency)

                # 결론 수집
                conclusions.append(chain.conclusion)

            # 결론 간 일관성
            conclusion_consistency = self._check_conclusion_consistency(conclusions)

            # 전체 일관성 점수
            overall_consistency = (
                sum(consistency_scores) / len(consistency_scores)
                + conclusion_consistency
            ) / 2
            return min(1.0, overall_consistency)

        except Exception as e:
            self.logger.error(f"일관성 분석 중 오류: {e}")
            return 0.0

    def _check_chain_consistency(self, chain: LogicalChain) -> float:
        """체인 내부 일관성 확인"""
        try:
            if len(chain.steps) <= 1:
                return 1.0

            consistency_score = 1.0
            for i in range(len(chain.steps) - 1):
                step1 = chain.steps[i]
                step2 = chain.steps[i + 1]

                # 연속된 단계 간 일관성 확인
                if not self._are_steps_consistent(step1, step2):
                    consistency_score *= 0.8

            return consistency_score

        except Exception as e:
            self.logger.error(f"체인 일관성 확인 중 오류: {e}")
            return 0.5

    def _are_steps_consistent(self, step1: LogicalRule, step2: LogicalRule) -> bool:
        """단계 간 일관성 확인"""
        try:
            # 간단한 일관성 검사: 결론과 전제 간의 논리적 연결
            step1_conclusion = step1.conclusion.lower()
            step2_premises = [p.lower() for p in step2.premises]

            # 결론이 전제와 관련이 있는지 확인
            for premise in step2_premises:
                if any(word in step1_conclusion for word in premise.split()):
                    return True

            return False

        except Exception as e:
            self.logger.error(f"단계 일관성 확인 중 오류: {e}")
            return False

    def _check_conclusion_consistency(self, conclusions: List[str]) -> float:
        """결론 간 일관성 확인"""
        try:
            if len(conclusions) <= 1:
                return 1.0

            consistency_count = 0
            total_comparisons = 0

            for i in range(len(conclusions)):
                for j in range(i + 1, len(conclusions)):
                    total_comparisons += 1
                    if self._are_conclusions_consistent(conclusions[i], conclusions[j]):
                        consistency_count += 1

            return (
                consistency_count / total_comparisons if total_comparisons > 0 else 1.0
            )

        except Exception as e:
            self.logger.error(f"결론 일관성 확인 중 오류: {e}")
            return 0.5

    def _are_conclusions_consistent(self, conclusion1: str, conclusion2: str) -> bool:
        """결론 간 일관성 확인"""
        try:
            # 간단한 일관성 검사: 반대되는 내용이 없는지 확인
            c1_lower = conclusion1.lower()
            c2_lower = conclusion2.lower()

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
                if (pair[0] in c1_lower and pair[1] in c2_lower) or (
                    pair[1] in c1_lower and pair[0] in c2_lower
                ):
                    return False

            return True

        except Exception as e:
            self.logger.error(f"결론 일관성 확인 중 오류: {e}")
            return True

    def _analyze_completeness(self, chains: List[LogicalChain]) -> float:
        """완전성 분석"""
        try:
            if not chains:
                return 0.0

            # 체인 수와 규칙 수를 기반으로 한 완전성 평가
            total_rules = sum(len(chain.steps) for chain in chains)
            total_chains = len(chains)

            # 완전성 점수 계산 (더 많은 체인과 규칙일수록 높은 점수)
            completeness_score = min(1.0, (total_rules + total_chains) / 10.0)

            return completeness_score

        except Exception as e:
            self.logger.error(f"완전성 분석 중 오류: {e}")
            return 0.0

    def _analyze_validity(self, chains: List[LogicalChain]) -> float:
        """유효성 분석"""
        try:
            if not chains:
                return 0.0

            validity_scores = []

            for chain in chains:
                # 체인 유효성 확인
                chain_validity = self._check_chain_validity(chain)
                validity_scores.append(chain_validity)

            # 평균 유효성 점수
            average_validity = sum(validity_scores) / len(validity_scores)
            return min(1.0, average_validity)

        except Exception as e:
            self.logger.error(f"유효성 분석 중 오류: {e}")
            return 0.0

    def _check_chain_validity(self, chain: LogicalChain) -> float:
        """체인 유효성 확인"""
        try:
            if not chain.steps:
                return 0.0

            # 각 단계의 신뢰도를 기반으로 한 유효성 평가
            step_confidences = [step.confidence for step in chain.steps]
            average_confidence = sum(step_confidences) / len(step_confidences)

            # 체인 길이를 고려한 유효성 조정
            length_factor = min(1.0, len(chain.steps) / 5.0)

            return average_confidence * length_factor

        except Exception as e:
            self.logger.error(f"체인 유효성 확인 중 오류: {e}")
            return 0.5

    def _identify_issues(self, chains: List[LogicalChain]) -> List[str]:
        """문제점 식별"""
        issues = []

        try:
            # 체인 수가 적은 경우
            if len(chains) < 2:
                issues.append("논리적 체인이 부족합니다.")

            # 신뢰도가 낮은 체인들
            low_confidence_chains = [
                chain for chain in chains if chain.confidence < 0.5
            ]
            if low_confidence_chains:
                issues.append(
                    f"신뢰도가 낮은 체인이 {len(low_confidence_chains)}개 있습니다."
                )

            # 짧은 체인들
            short_chains = [chain for chain in chains if len(chain.steps) < 2]
            if short_chains:
                issues.append(f"단일 규칙 체인이 {len(short_chains)}개 있습니다.")

            return issues

        except Exception as e:
            self.logger.error(f"문제점 식별 중 오류: {e}")
            return [f"문제점 식별 오류: {str(e)}"]

    def _generate_suggestions(
        self, chains: List[LogicalChain], logic_type: LogicType
    ) -> List[str]:
        """개선 제안 생성"""
        suggestions = []

        try:
            # 체인 수가 적은 경우
            if len(chains) < 3:
                suggestions.append("더 많은 논리적 규칙을 추가하여 체인을 확장하세요.")

            # 신뢰도가 낮은 체인들
            low_confidence_chains = [
                chain for chain in chains if chain.confidence < 0.5
            ]
            if low_confidence_chains:
                suggestions.append("신뢰도가 낮은 규칙들을 개선하거나 대체하세요.")

            # 짧은 체인들
            short_chains = [chain for chain in chains if len(chain.steps) < 2]
            if short_chains:
                suggestions.append(
                    "단일 규칙 체인들을 연결하여 복합 체인을 구축하세요."
                )

            # 논리 유형별 제안
            if logic_type == LogicType.PROPOSITIONAL:
                suggestions.append(
                    "명제 논리를 위해 더 명확한 전제-결론 구조를 사용하세요."
                )
            elif logic_type == LogicType.PREDICATE:
                suggestions.append("술어 논리를 위해 변수와 양화사를 활용하세요.")
            elif logic_type == LogicType.MODAL:
                suggestions.append("양상 논리를 위해 가능성과 필요성을 명시하세요.")

            return suggestions

        except Exception as e:
            self.logger.error(f"개선 제안 생성 중 오류: {e}")
            return [f"제안 생성 오류: {str(e)}"]

    def _update_performance_metrics(
        self, analysis: LogicAnalysis, processing_time: float
    ):
        """성능 메트릭 업데이트"""
        self.performance_metrics["total_processings"] += 1
        if analysis.consistency_score > 0.5 and analysis.validity_score > 0.5:
            self.performance_metrics["successful_processings"] += 1

        # 평균 일관성 업데이트
        total_consistency = self.performance_metrics["average_consistency"] * (
            self.performance_metrics["total_processings"] - 1
        )
        self.performance_metrics["average_consistency"] = (
            total_consistency + analysis.consistency_score
        ) / self.performance_metrics["total_processings"]

        # 평균 완전성 업데이트
        total_completeness = self.performance_metrics["average_completeness"] * (
            self.performance_metrics["total_processings"] - 1
        )
        self.performance_metrics["average_completeness"] = (
            total_completeness + analysis.completeness_score
        ) / self.performance_metrics["total_processings"]

    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭 조회"""
        return self.performance_metrics.copy()

    def get_processing_history(self) -> List[Dict[str, Any]]:
        """처리 히스토리 조회"""
        return self.processing_history.copy()
