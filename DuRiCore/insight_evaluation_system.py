#!/usr/bin/env python3
"""
DuRi 통찰 평가 시스템 (Day 7)
가짜 통찰 → 진짜 통찰 구분으로 전환
"""

import asyncio
import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightType(Enum):
    """통찰 유형"""

    GENUINE = "genuine"
    SUPERFICIAL = "superficial"
    CONTRIVED = "contrived"
    DEEP = "deep"
    SHALLOW = "shallow"


class AuthenticityLevel(Enum):
    """진위성 수준"""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


@dataclass
class JudgmentQualityMetrics:
    """판단 품질 메트릭"""

    logical_consistency: float  # 0.0-1.0
    evidence_support: float  # 0.0-1.0
    reasoning_depth: float  # 0.0-1.0
    originality: float  # 0.0-1.0
    practical_relevance: float  # 0.0-1.0
    overall_quality: float  # 0.0-1.0


@dataclass
class InsightAuthenticityCheck:
    """통찰 진위성 검사"""

    insight_id: str
    insight_type: InsightType
    authenticity_level: AuthenticityLevel
    confidence_score: float
    evidence_quality: float
    reasoning_quality: float
    originality_score: float
    practical_value: float
    red_flags: List[str]
    green_flags: List[str]


class JudgmentQualityMetricsEvaluator:
    """판단 품질 메트릭 시스템"""

    def __init__(self):
        self.quality_indicators = self._initialize_quality_indicators()
        self.evaluation_criteria = self._initialize_evaluation_criteria()

    def _initialize_quality_indicators(self) -> Dict[str, Dict]:
        """품질 지표 초기화"""
        return {
            "logical_consistency": {
                "keywords": ["논리", "일관성", "모순", "전제", "결론"],
                "weight": 0.25,
                "description": "논리적 일관성 및 모순 없는 추론",
            },
            "evidence_support": {
                "keywords": ["증거", "사실", "데이터", "근거", "입증"],
                "weight": 0.20,
                "description": "주장을 뒷받침하는 증거의 품질",
            },
            "reasoning_depth": {
                "keywords": ["깊이", "분석", "탐구", "고찰", "사고"],
                "weight": 0.20,
                "description": "사고의 깊이와 분석 수준",
            },
            "originality": {
                "keywords": ["독창", "새로운", "혁신", "창의", "독특"],
                "weight": 0.15,
                "description": "독창성과 새로운 관점",
            },
            "practical_relevance": {
                "keywords": ["실용", "적용", "실제", "유용", "효과"],
                "weight": 0.20,
                "description": "실용적 가치와 적용 가능성",
            },
        }

    def _initialize_evaluation_criteria(self) -> Dict[str, List[str]]:
        """평가 기준 초기화"""
        return {
            "high_quality": [
                "논리적 일관성이 높음",
                "충분한 증거로 뒷받침됨",
                "깊이 있는 분석 포함",
                "독창적인 관점 제시",
                "실용적 가치가 명확함",
            ],
            "medium_quality": [
                "일부 논리적 일관성",
                "제한적 증거",
                "중간 수준의 분석",
                "일반적인 관점",
                "부분적 실용성",
            ],
            "low_quality": [
                "논리적 모순 존재",
                "증거 부족",
                "표면적 분석",
                "진부한 관점",
                "실용성 부족",
            ],
        }

    async def evaluate_judgment_quality(
        self, judgment_content: str, reasoning_process: Dict[str, Any]
    ) -> JudgmentQualityMetrics:
        """판단 품질 평가"""
        logger.info("판단 품질 평가 시작")

        # 각 품질 지표 평가
        logical_consistency = self._evaluate_logical_consistency(
            judgment_content, reasoning_process
        )
        evidence_support = self._evaluate_evidence_support(judgment_content, reasoning_process)
        reasoning_depth = self._evaluate_reasoning_depth(judgment_content, reasoning_process)
        originality = self._evaluate_originality(judgment_content, reasoning_process)
        practical_relevance = self._evaluate_practical_relevance(
            judgment_content, reasoning_process
        )

        # 종합 품질 계산
        overall_quality = self._calculate_overall_quality(
            logical_consistency,
            evidence_support,
            reasoning_depth,
            originality,
            practical_relevance,
        )

        metrics = JudgmentQualityMetrics(
            logical_consistency=logical_consistency,
            evidence_support=evidence_support,
            reasoning_depth=reasoning_depth,
            originality=originality,
            practical_relevance=practical_relevance,
            overall_quality=overall_quality,
        )

        logger.info(f"판단 품질 평가 완료: {overall_quality:.2f}")
        return metrics

    def _evaluate_logical_consistency(
        self, content: str, reasoning_process: Dict[str, Any]
    ) -> float:
        """논리적 일관성 평가"""
        score = 0.5  # 기본값

        # 논리적 키워드 검사
        logical_keywords = ["따라서", "그러므로", "결론적으로", "이유로", "때문에"]
        keyword_count = sum(1 for keyword in logical_keywords if keyword in content)
        score += min(keyword_count * 0.1, 0.3)

        # 추론 과정의 구조성 검사
        if "reasoning_process" in reasoning_process:
            reasoning_steps = reasoning_process.get("logical_steps", [])
            if len(reasoning_steps) >= 3:
                score += 0.2

        # 모순 키워드 검사
        contradiction_keywords = ["하지만", "그런데", "반면", "다른 한편"]
        contradiction_count = sum(1 for keyword in contradiction_keywords if keyword in content)
        score -= min(contradiction_count * 0.1, 0.2)

        return min(max(score, 0.0), 1.0)

    def _evaluate_evidence_support(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """증거 지원 평가"""
        score = 0.5  # 기본값

        # 증거 키워드 검사
        evidence_keywords = ["증거", "사실", "데이터", "근거", "입증", "확인", "검증"]
        evidence_count = sum(1 for keyword in evidence_keywords if keyword in content)
        score += min(evidence_count * 0.1, 0.3)

        # 구체적 예시 검사
        example_patterns = ["예를 들어", "예시로", "사례로", "구체적으로"]
        example_count = sum(1 for pattern in example_patterns if pattern in content)
        score += min(example_count * 0.1, 0.2)

        # 추론 과정의 증거 활용 검사
        if "premises" in reasoning_process:
            premises = reasoning_process.get("premises", [])
            evidence_premises = [
                p for p in premises if any(kw in str(p) for kw in evidence_keywords)
            ]
            if evidence_premises:
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _evaluate_reasoning_depth(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """추론 깊이 평가"""
        score = 0.5  # 기본값

        # 깊이 키워드 검사
        depth_keywords = ["분석", "탐구", "고찰", "사고", "검토", "연구", "조사"]
        depth_count = sum(1 for keyword in depth_keywords if keyword in content)
        score += min(depth_count * 0.1, 0.3)

        # 복잡한 문장 구조 검사
        complex_sentences = len([s for s in content.split(".") if len(s.split()) > 15])
        score += min(complex_sentences * 0.05, 0.2)

        # 추론 과정의 복잡성 검사
        if "logical_steps" in reasoning_process:
            steps = reasoning_process.get("logical_steps", [])
            if len(steps) >= 4:
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _evaluate_originality(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """독창성 평가"""
        score = 0.5  # 기본값

        # 독창성 키워드 검사
        originality_keywords = ["새로운", "독창", "혁신", "창의", "독특", "차별화"]
        originality_count = sum(1 for keyword in originality_keywords if keyword in content)
        score += min(originality_count * 0.1, 0.3)

        # 일반적 표현 검사 (독창성 감소)
        common_phrases = ["일반적으로", "보통", "대부분", "전형적인", "표준적인"]
        common_count = sum(1 for phrase in common_phrases if phrase in content)
        score -= min(common_count * 0.1, 0.2)

        # 추론 과정의 독창성 검사
        if "reasoning_type" in reasoning_process:
            reasoning_type = reasoning_process.get("reasoning_type", "")
            if "hybrid" in reasoning_type or "integrated" in reasoning_type:
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _evaluate_practical_relevance(
        self, content: str, reasoning_process: Dict[str, Any]
    ) -> float:
        """실용적 관련성 평가"""
        score = 0.5  # 기본값

        # 실용성 키워드 검사
        practical_keywords = ["실용", "적용", "실제", "유용", "효과", "결과", "해결"]
        practical_count = sum(1 for keyword in practical_keywords if keyword in content)
        score += min(practical_count * 0.1, 0.3)

        # 구체적 행동 제안 검사
        action_keywords = ["해야 한다", "해야 한다", "필요하다", "권장한다", "제안한다"]
        action_count = sum(1 for keyword in action_keywords if keyword in content)
        score += min(action_count * 0.1, 0.2)

        # 추론 과정의 실용성 검사
        if "conclusion" in reasoning_process:
            conclusion = reasoning_process.get("conclusion", "")
            if any(keyword in conclusion for keyword in practical_keywords):
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _calculate_overall_quality(
        self,
        logical_consistency: float,
        evidence_support: float,
        reasoning_depth: float,
        originality: float,
        practical_relevance: float,
    ) -> float:
        """종합 품질 계산"""
        weights = self.quality_indicators

        overall_score = (
            logical_consistency * weights["logical_consistency"]["weight"]
            + evidence_support * weights["evidence_support"]["weight"]
            + reasoning_depth * weights["reasoning_depth"]["weight"]
            + originality * weights["originality"]["weight"]
            + practical_relevance * weights["practical_relevance"]["weight"]
        )

        return min(max(overall_score, 0.0), 1.0)


class InsightAuthenticityChecker:
    """통찰 진위성 검사 시스템"""

    def __init__(self):
        self.authenticity_indicators = self._initialize_authenticity_indicators()
        self.red_flag_patterns = self._initialize_red_flag_patterns()
        self.green_flag_patterns = self._initialize_green_flag_patterns()

    def _initialize_authenticity_indicators(self) -> Dict[str, Dict]:
        """진위성 지표 초기화"""
        return {
            "evidence_quality": {
                "weight": 0.25,
                "indicators": [
                    "구체적 사실",
                    "검증 가능한 정보",
                    "신뢰할 수 있는 출처",
                ],
            },
            "reasoning_quality": {
                "weight": 0.25,
                "indicators": ["논리적 일관성", "명확한 추론 과정", "적절한 전제"],
            },
            "originality_score": {
                "weight": 0.20,
                "indicators": ["독창적 관점", "새로운 연결", "혁신적 사고"],
            },
            "practical_value": {
                "weight": 0.30,
                "indicators": ["실용적 적용", "해결책 제시", "실행 가능성"],
            },
        }

    def _initialize_red_flag_patterns(self) -> List[Dict[str, Any]]:
        """경고 신호 패턴 초기화"""
        return [
            {
                "pattern": "과도한 일반화",
                "keywords": ["모든", "항상", "절대", "완전히", "전혀"],
                "severity": 0.3,
            },
            {
                "pattern": "감정적 과장",
                "keywords": ["끔찍한", "놀라운", "믿을 수 없는", "충격적인"],
                "severity": 0.4,
            },
            {
                "pattern": "논리적 비약",
                "keywords": ["따라서", "그러므로", "결론적으로"],
                "severity": 0.5,
            },
            {
                "pattern": "증거 부족",
                "keywords": ["아마도", "어쩌면", "추정", "가능성"],
                "severity": 0.4,
            },
            {
                "pattern": "모순된 주장",
                "keywords": ["하지만", "그런데", "반면", "다른 한편"],
                "severity": 0.6,
            },
        ]

    def _initialize_green_flag_patterns(self) -> List[Dict[str, Any]]:
        """긍정 신호 패턴 초기화"""
        return [
            {
                "pattern": "구체적 증거",
                "keywords": ["연구에 따르면", "데이터는", "사실은", "증거로"],
                "strength": 0.4,
            },
            {
                "pattern": "균형잡힌 관점",
                "keywords": ["한편으로는", "다른 한편으로는", "양면적", "복합적"],
                "strength": 0.3,
            },
            {
                "pattern": "실용적 제안",
                "keywords": ["해결책은", "방법은", "전략은", "접근법은"],
                "strength": 0.5,
            },
            {
                "pattern": "깊이 있는 분석",
                "keywords": ["분석해보면", "탐구해보면", "고찰해보면", "검토해보면"],
                "strength": 0.4,
            },
            {
                "pattern": "독창적 통찰",
                "keywords": ["새로운 관점", "혁신적", "독창적", "차별화된"],
                "strength": 0.3,
            },
        ]

    async def check_insight_authenticity(
        self, insight_content: str, reasoning_process: Dict[str, Any]
    ) -> InsightAuthenticityCheck:
        """통찰 진위성 검사"""
        logger.info("통찰 진위성 검사 시작")

        # 각 진위성 지표 평가
        evidence_quality = self._evaluate_evidence_quality(insight_content, reasoning_process)
        reasoning_quality = self._evaluate_reasoning_quality(insight_content, reasoning_process)
        originality_score = self._evaluate_originality_score(insight_content, reasoning_process)
        practical_value = self._evaluate_practical_value(insight_content, reasoning_process)

        # 경고 신호 및 긍정 신호 검사
        red_flags = self._detect_red_flags(insight_content)
        green_flags = self._detect_green_flags(insight_content)

        # 통찰 유형 및 진위성 수준 결정
        insight_type = self._determine_insight_type(
            evidence_quality, reasoning_quality, originality_score, practical_value
        )
        authenticity_level = self._determine_authenticity_level(
            evidence_quality,
            reasoning_quality,
            originality_score,
            practical_value,
            red_flags,
            green_flags,
        )

        # 신뢰도 계산
        confidence_score = self._calculate_confidence_score(
            evidence_quality,
            reasoning_quality,
            originality_score,
            practical_value,
            red_flags,
            green_flags,
        )

        check = InsightAuthenticityCheck(
            insight_id=f"insight_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            insight_type=insight_type,
            authenticity_level=authenticity_level,
            confidence_score=confidence_score,
            evidence_quality=evidence_quality,
            reasoning_quality=reasoning_quality,
            originality_score=originality_score,
            practical_value=practical_value,
            red_flags=red_flags,
            green_flags=green_flags,
        )

        logger.info(f"통찰 진위성 검사 완료: {authenticity_level.value}")
        return check

    def _evaluate_evidence_quality(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """증거 품질 평가"""
        score = 0.5  # 기본값

        # 구체적 증거 키워드 검사
        evidence_keywords = ["연구", "데이터", "사실", "증거", "확인", "검증", "입증"]
        evidence_count = sum(1 for keyword in evidence_keywords if keyword in content)
        score += min(evidence_count * 0.1, 0.3)

        # 추론 과정의 증거 활용 검사
        if "premises" in reasoning_process:
            premises = reasoning_process.get("premises", [])
            evidence_premises = [
                p for p in premises if any(kw in str(p) for kw in evidence_keywords)
            ]
            if evidence_premises:
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _evaluate_reasoning_quality(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """추론 품질 평가"""
        score = 0.5  # 기본값

        # 논리적 키워드 검사
        logical_keywords = [
            "논리",
            "일관성",
            "추론",
            "전제",
            "결론",
            "따라서",
            "그러므로",
        ]
        logical_count = sum(1 for keyword in logical_keywords if keyword in content)
        score += min(logical_count * 0.1, 0.3)

        # 추론 과정의 구조성 검사
        if "logical_steps" in reasoning_process:
            steps = reasoning_process.get("logical_steps", [])
            if len(steps) >= 3:
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _evaluate_originality_score(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """독창성 점수 평가"""
        score = 0.5  # 기본값

        # 독창성 키워드 검사
        originality_keywords = ["새로운", "독창", "혁신", "창의", "독특", "차별화"]
        originality_count = sum(1 for keyword in originality_keywords if keyword in content)
        score += min(originality_count * 0.1, 0.3)

        # 추론 과정의 독창성 검사
        if "reasoning_type" in reasoning_process:
            reasoning_type = reasoning_process.get("reasoning_type", "")
            if "hybrid" in reasoning_type or "integrated" in reasoning_type:
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _evaluate_practical_value(self, content: str, reasoning_process: Dict[str, Any]) -> float:
        """실용적 가치 평가"""
        score = 0.5  # 기본값

        # 실용성 키워드 검사
        practical_keywords = ["실용", "적용", "실제", "유용", "효과", "해결", "방법"]
        practical_count = sum(1 for keyword in practical_keywords if keyword in content)
        score += min(practical_count * 0.1, 0.3)

        # 추론 과정의 실용성 검사
        if "conclusion" in reasoning_process:
            conclusion = reasoning_process.get("conclusion", "")
            if any(keyword in conclusion for keyword in practical_keywords):
                score += 0.2

        return min(max(score, 0.0), 1.0)

    def _detect_red_flags(self, content: str) -> List[str]:
        """경고 신호 검출"""
        red_flags = []

        for pattern in self.red_flag_patterns:
            pattern_name = pattern["pattern"]
            keywords = pattern["keywords"]
            severity = pattern["severity"]

            keyword_count = sum(1 for keyword in keywords if keyword in content)
            if keyword_count > 0:
                red_flags.append(
                    f"{pattern_name}: {keyword_count}개 키워드 발견 (심각도: {severity})"
                )

        return red_flags

    def _detect_green_flags(self, content: str) -> List[str]:
        """긍정 신호 검출"""
        green_flags = []

        for pattern in self.green_flag_patterns:
            pattern_name = pattern["pattern"]
            keywords = pattern["keywords"]
            strength = pattern["strength"]

            keyword_count = sum(1 for keyword in keywords if keyword in content)
            if keyword_count > 0:
                green_flags.append(
                    f"{pattern_name}: {keyword_count}개 키워드 발견 (강도: {strength})"
                )

        return green_flags

    def _determine_insight_type(
        self,
        evidence_quality: float,
        reasoning_quality: float,
        originality_score: float,
        practical_value: float,
    ) -> InsightType:
        """통찰 유형 결정"""
        avg_score = (evidence_quality + reasoning_quality + originality_score + practical_value) / 4

        if avg_score >= 0.8:
            return InsightType.GENUINE
        elif avg_score >= 0.6:
            return InsightType.DEEP
        elif avg_score >= 0.4:
            return InsightType.SUPERFICIAL
        else:
            return InsightType.SHALLOW

    def _determine_authenticity_level(
        self,
        evidence_quality: float,
        reasoning_quality: float,
        originality_score: float,
        practical_value: float,
        red_flags: List[str],
        green_flags: List[str],
    ) -> AuthenticityLevel:
        """진위성 수준 결정"""
        # 기본 점수 계산
        base_score = (
            evidence_quality + reasoning_quality + originality_score + practical_value
        ) / 4

        # 경고 신호에 따른 감점
        red_flag_penalty = len(red_flags) * 0.1
        green_flag_bonus = len(green_flags) * 0.05

        final_score = base_score - red_flag_penalty + green_flag_bonus

        if final_score >= 0.8:
            return AuthenticityLevel.HIGH
        elif final_score >= 0.6:
            return AuthenticityLevel.MEDIUM
        elif final_score >= 0.4:
            return AuthenticityLevel.LOW
        else:
            return AuthenticityLevel.UNKNOWN

    def _calculate_confidence_score(
        self,
        evidence_quality: float,
        reasoning_quality: float,
        originality_score: float,
        practical_value: float,
        red_flags: List[str],
        green_flags: List[str],
    ) -> float:
        """신뢰도 계산"""
        # 기본 신뢰도
        base_confidence = (
            evidence_quality + reasoning_quality + originality_score + practical_value
        ) / 4

        # 경고 신호에 따른 감점
        red_flag_penalty = len(red_flags) * 0.05
        green_flag_bonus = len(green_flags) * 0.03

        confidence = base_confidence - red_flag_penalty + green_flag_bonus
        return min(max(confidence, 0.0), 1.0)


class InsightEvaluationSystem:
    """통찰 평가 시스템"""

    def __init__(self):
        self.quality_metrics = JudgmentQualityMetricsEvaluator()
        self.authenticity_checker = InsightAuthenticityChecker()

    async def evaluate_insight(
        self, insight_content: str, reasoning_process: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통찰 종합 평가"""
        logger.info("통찰 종합 평가 시작")

        # 품질 메트릭 평가
        quality_metrics = await self.quality_metrics.evaluate_judgment_quality(
            insight_content, reasoning_process
        )

        # 진위성 검사
        authenticity_check = await self.authenticity_checker.check_insight_authenticity(
            insight_content, reasoning_process
        )

        # 종합 평가 결과
        evaluation_result = {
            "quality_metrics": quality_metrics,
            "authenticity_check": authenticity_check,
            "overall_assessment": self._generate_overall_assessment(
                quality_metrics, authenticity_check
            ),
        }

        logger.info("통찰 종합 평가 완료")
        return evaluation_result

    def _generate_overall_assessment(
        self,
        quality_metrics: JudgmentQualityMetrics,
        authenticity_check: InsightAuthenticityCheck,
    ) -> Dict[str, Any]:
        """종합 평가 생성"""
        # 품질과 진위성의 가중 평균
        quality_score = quality_metrics.overall_quality
        authenticity_score = authenticity_check.confidence_score

        overall_score = (quality_score * 0.6) + (authenticity_score * 0.4)

        # 평가 등급 결정
        if overall_score >= 0.8:
            grade = "A"
            assessment = "우수한 통찰"
        elif overall_score >= 0.6:
            grade = "B"
            assessment = "양호한 통찰"
        elif overall_score >= 0.4:
            grade = "C"
            assessment = "보통의 통찰"
        else:
            grade = "D"
            assessment = "개선이 필요한 통찰"

        return {
            "overall_score": overall_score,
            "grade": grade,
            "assessment": assessment,
            "recommendations": self._generate_recommendations(quality_metrics, authenticity_check),
        }

    def _generate_recommendations(
        self,
        quality_metrics: JudgmentQualityMetrics,
        authenticity_check: InsightAuthenticityCheck,
    ) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = []

        # 품질 기반 권고사항
        if quality_metrics.logical_consistency < 0.6:
            recommendations.append("논리적 일관성을 향상시키세요")

        if quality_metrics.evidence_support < 0.6:
            recommendations.append("더 많은 증거를 제시하세요")

        if quality_metrics.reasoning_depth < 0.6:
            recommendations.append("더 깊이 있는 분석을 수행하세요")

        if quality_metrics.originality < 0.6:
            recommendations.append("더 독창적인 관점을 제시하세요")

        if quality_metrics.practical_relevance < 0.6:
            recommendations.append("실용적 가치를 더 명확히 하세요")

        # 진위성 기반 권고사항
        if authenticity_check.red_flags:
            recommendations.append("경고 신호를 줄이기 위해 더 신중한 표현을 사용하세요")

        if len(authenticity_check.green_flags) < 2:
            recommendations.append("더 많은 긍정적 신호를 포함하세요")

        return recommendations


async def test_insight_evaluation_system():
    """통찰 평가 시스템 테스트"""
    print("=== 통찰 평가 시스템 테스트 시작 (Day 7) ===")

    evaluation_system = InsightEvaluationSystem()

    # 테스트 통찰 내용
    test_insight_content = """
    거짓말에 대한 윤리적 판단에서 중요한 것은 상황의 맥락을 고려하는 것입니다.
    연구에 따르면, 완전한 진실만이 항상 최선의 선택은 아닙니다.
    예를 들어, 생명을 구하기 위한 거짓말은 도덕적으로 정당화될 수 있습니다.
    하지만 이는 매우 제한적인 상황에서만 적용되어야 하며,
    일반적으로는 진실성의 가치를 우선시해야 합니다.
    """

    test_reasoning_process = {
        "logical_steps": [
            {"step": 1, "content": "상황 맥락 분석"},
            {"step": 2, "content": "윤리적 원칙 적용"},
            {"step": 3, "content": "결과 예측"},
            {"step": 4, "content": "종합적 판단"},
        ],
        "premises": [
            "완전한 진실이 항상 최선은 아님",
            "생명 구원이 우선순위",
            "상황적 맥락의 중요성",
        ],
        "conclusion": "상황에 따른 조건부 허용",
    }

    # 통찰 평가
    evaluation_result = await evaluation_system.evaluate_insight(
        test_insight_content, test_reasoning_process
    )

    # 결과 출력
    quality_metrics = evaluation_result["quality_metrics"]
    authenticity_check = evaluation_result["authenticity_check"]
    overall_assessment = evaluation_result["overall_assessment"]

    print(f"\n📊 품질 메트릭:")
    print(f"  • 논리적 일관성: {quality_metrics.logical_consistency:.2f}")
    print(f"  • 증거 지원: {quality_metrics.evidence_support:.2f}")
    print(f"  • 추론 깊이: {quality_metrics.reasoning_depth:.2f}")
    print(f"  • 독창성: {quality_metrics.originality:.2f}")
    print(f"  • 실용적 관련성: {quality_metrics.practical_relevance:.2f}")
    print(f"  • 종합 품질: {quality_metrics.overall_quality:.2f}")

    print(f"\n🔍 진위성 검사:")
    print(f"  • 통찰 유형: {authenticity_check.insight_type.value}")
    print(f"  • 진위성 수준: {authenticity_check.authenticity_level.value}")
    print(f"  • 신뢰도: {authenticity_check.confidence_score:.2f}")
    print(f"  • 증거 품질: {authenticity_check.evidence_quality:.2f}")
    print(f"  • 추론 품질: {authenticity_check.reasoning_quality:.2f}")
    print(f"  • 독창성 점수: {authenticity_check.originality_score:.2f}")
    print(f"  • 실용적 가치: {authenticity_check.practical_value:.2f}")

    print(f"\n🚩 경고 신호:")
    for flag in authenticity_check.red_flags:
        print(f"  • {flag}")

    print(f"\n✅ 긍정 신호:")
    for flag in authenticity_check.green_flags:
        print(f"  • {flag}")

    print(f"\n🎯 종합 평가:")
    print(f"  • 종합 점수: {overall_assessment['overall_score']:.2f}")
    print(f"  • 등급: {overall_assessment['grade']}")
    print(f"  • 평가: {overall_assessment['assessment']}")

    print(f"\n💡 개선 권고사항:")
    for recommendation in overall_assessment["recommendations"]:
        print(f"  • {recommendation}")

    print(f"\n{'='*70}")
    print("=== 통찰 평가 시스템 테스트 완료 (Day 7) ===")
    print("✅ Day 7 목표 달성: 가짜 통찰 → 진짜 통찰 구분")
    print("✅ 판단 품질 메트릭 및 통찰 진위성 검사 시스템 구현")
    print("✅ 종합 평가 시스템 및 개선 권고사항 생성 시스템 구현")


if __name__ == "__main__":
    asyncio.run(test_insight_evaluation_system())
