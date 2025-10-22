#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: 생존 평가 시스템

이 모듈은 DuRi의 생존 가능성을 평가하는 시스템입니다.
환경적 위험 평가, 자원 가용성 평가, 생존 점수 계산, 생존 권장사항 생성을 담당합니다.

주요 기능:
- 환경적 위험 평가
- 자원 가용성 평가
- 생존 점수 계산
- 생존 권장사항 생성
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """위험 수준 열거형"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceType(Enum):
    """자원 유형 열거형"""

    COMPUTATIONAL = "computational"
    MEMORY = "memory"
    NETWORK = "network"
    ENERGY = "energy"
    KNOWLEDGE = "knowledge"
    TIME = "time"


class AssessmentType(Enum):
    """평가 유형 열거형"""

    ENVIRONMENTAL = "environmental"
    RESOURCE = "resource"
    COMPREHENSIVE = "comprehensive"
    PREDICTIVE = "predictive"


@dataclass
class RiskAssessment:
    """위험 평가 데이터 클래스"""

    risk_id: str
    risk_type: str
    risk_level: RiskLevel
    description: str
    probability: float
    impact_score: float
    mitigation_strategies: List[str] = field(default_factory=list)
    assessment_time: datetime = field(default_factory=datetime.now)


@dataclass
class ResourceAssessment:
    """자원 평가 데이터 클래스"""

    resource_type: ResourceType
    availability: float
    utilization: float
    efficiency: float
    capacity: float
    projected_shortage: Optional[float] = None
    optimization_opportunities: List[str] = field(default_factory=list)


@dataclass
class SurvivalScore:
    """생존 점수 데이터 클래스"""

    overall_score: float
    environmental_score: float
    resource_score: float
    adaptation_score: float
    resilience_score: float
    confidence_level: float
    assessment_time: datetime = field(default_factory=datetime.now)


@dataclass
class Recommendation:
    """권장사항 데이터 클래스"""

    recommendation_id: str
    category: str
    description: str
    priority: int
    urgency: float
    feasibility: float
    expected_impact: float
    implementation_time: float
    resource_requirements: Dict[str, float] = field(default_factory=dict)


class SurvivalAssessmentSystem:
    """생존 가능성을 평가하는 시스템"""

    def __init__(self):
        """초기화"""
        self.assessment_history = []
        self.risk_patterns = {}
        self.resource_models = {}
        self.survival_thresholds = {}

        # 평가 시스템 설정
        self.risk_threshold = 0.7
        self.resource_threshold = 0.6
        self.survival_threshold = 0.5

        # 평가 가중치
        self.assessment_weights = {
            "environmental": 0.3,
            "resource": 0.25,
            "adaptation": 0.25,
            "resilience": 0.2,
        }

        logger.info("생존 평가 시스템 초기화 완료")

    async def assess_environmental_risks(
        self, environment_data: Optional[Dict[str, Any]] = None
    ) -> List[RiskAssessment]:
        """환경적 위험 평가"""
        try:
            start_time = time.time()

            if environment_data is None:
                environment_data = {}

            # 환경 위험 식별
            environmental_risks = await self._identify_environmental_risks(environment_data)

            # 위험 수준 평가
            risk_assessments = []
            for risk in environmental_risks:
                risk_assessment = await self._assess_risk_level(risk)
                risk_assessments.append(risk_assessment)

            # 위험 우선순위 설정
            risk_assessments = await self._prioritize_risks(risk_assessments)

            execution_time = time.time() - start_time
            logger.info(
                f"환경적 위험 평가 완료: {execution_time:.2f}초, {len(risk_assessments)}개 위험 식별"
            )

            return risk_assessments

        except Exception as e:
            logger.error(f"환경적 위험 평가 실패: {e}")
            return []

    async def evaluate_resource_availability(
        self, resource_data: Optional[Dict[str, Any]] = None
    ) -> Dict[ResourceType, ResourceAssessment]:
        """자원 가용성 평가"""
        try:
            start_time = time.time()

            if resource_data is None:
                resource_data = {}

            resource_assessments = {}

            # 각 자원 유형별 평가
            for resource_type in ResourceType:
                resource_assessment = await self._assess_resource_type(resource_type, resource_data)
                resource_assessments[resource_type] = resource_assessment

            # 자원 상호작용 분석
            resource_assessments = await self._analyze_resource_interactions(resource_assessments)

            execution_time = time.time() - start_time
            logger.info(f"자원 가용성 평가 완료: {execution_time:.2f}초")

            return resource_assessments

        except Exception as e:
            logger.error(f"자원 가용성 평가 실패: {e}")
            return {}

    async def calculate_survival_score(
        self,
        risk_assessments: List[RiskAssessment],
        resource_assessments: Dict[ResourceType, ResourceAssessment],
    ) -> SurvivalScore:
        """생존 점수 계산"""
        try:
            start_time = time.time()

            # 환경 점수 계산
            environmental_score = await self._calculate_environmental_score(risk_assessments)

            # 자원 점수 계산
            resource_score = await self._calculate_resource_score(resource_assessments)

            # 적응 점수 계산
            adaptation_score = await self._calculate_adaptation_score(
                risk_assessments, resource_assessments
            )

            # 회복력 점수 계산
            resilience_score = await self._calculate_resilience_score(
                risk_assessments, resource_assessments
            )

            # 전체 생존 점수 계산
            overall_score = await self._calculate_overall_survival_score(
                environmental_score, resource_score, adaptation_score, resilience_score
            )

            # 신뢰도 수준 계산
            confidence_level = await self._calculate_confidence_level(
                risk_assessments, resource_assessments
            )

            survival_score = SurvivalScore(
                overall_score=overall_score,
                environmental_score=environmental_score,
                resource_score=resource_score,
                adaptation_score=adaptation_score,
                resilience_score=resilience_score,
                confidence_level=confidence_level,
                assessment_time=datetime.now(),
            )

            execution_time = time.time() - start_time
            logger.info(f"생존 점수 계산 완료: {execution_time:.2f}초, 점수: {overall_score:.3f}")

            return survival_score

        except Exception as e:
            logger.error(f"생존 점수 계산 실패: {e}")
            return await self._create_default_survival_score()

    async def generate_survival_recommendations(
        self,
        survival_score: SurvivalScore,
        risk_assessments: List[RiskAssessment],
        resource_assessments: Dict[ResourceType, ResourceAssessment],
    ) -> List[Recommendation]:
        """생존 권장사항 생성"""
        try:
            start_time = time.time()

            recommendations = []

            # 위험 기반 권장사항
            risk_recommendations = await self._generate_risk_based_recommendations(risk_assessments)
            recommendations.extend(risk_recommendations)

            # 자원 기반 권장사항
            resource_recommendations = await self._generate_resource_based_recommendations(
                resource_assessments
            )
            recommendations.extend(resource_recommendations)

            # 생존 점수 기반 권장사항
            score_recommendations = await self._generate_score_based_recommendations(survival_score)
            recommendations.extend(score_recommendations)

            # 권장사항 우선순위 설정
            recommendations = await self._prioritize_recommendations(recommendations)

            execution_time = time.time() - start_time
            logger.info(
                f"생존 권장사항 생성 완료: {execution_time:.2f}초, {len(recommendations)}개 권장사항"
            )

            return recommendations

        except Exception as e:
            logger.error(f"생존 권장사항 생성 실패: {e}")
            return []

    async def _identify_environmental_risks(
        self, environment_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """환경 위험 식별"""
        try:
            risks = []

            # 시스템 안정성 위험
            if "system_stability" in environment_data:
                stability = environment_data["system_stability"]
                if stability < 0.8:
                    risks.append(
                        {
                            "risk_id": "system_instability",
                            "risk_type": "system",
                            "description": "시스템 안정성 저하",
                            "probability": 1.0 - stability,
                            "impact_score": 0.8,
                        }
                    )

            # 성능 저하 위험
            if "performance_metrics" in environment_data:
                performance = environment_data["performance_metrics"]
                avg_performance = (
                    sum(performance.values()) / len(performance) if performance else 0.0
                )
                if avg_performance < 0.7:
                    risks.append(
                        {
                            "risk_id": "performance_degradation",
                            "risk_type": "performance",
                            "description": "성능 저하",
                            "probability": 1.0 - avg_performance,
                            "impact_score": 0.7,
                        }
                    )

            # 외부 위협 위험
            if "external_threats" in environment_data:
                external_threats = environment_data["external_threats"]
                for threat in external_threats:
                    risks.append(
                        {
                            "risk_id": f"external_threat_{threat.get('id', 'unknown')}",
                            "risk_type": "external",
                            "description": threat.get("description", "외부 위협"),
                            "probability": threat.get("probability", 0.5),
                            "impact_score": threat.get("impact", 0.6),
                        }
                    )

            # 자원 부족 위험
            if "resource_shortages" in environment_data:
                resource_shortages = environment_data["resource_shortages"]
                for shortage in resource_shortages:
                    risks.append(
                        {
                            "risk_id": f"resource_shortage_{shortage.get('type', 'unknown')}",
                            "risk_type": "resource",
                            "description": f"{shortage.get('type', '자원')} 부족",
                            "probability": shortage.get("probability", 0.5),
                            "impact_score": shortage.get("impact", 0.7),
                        }
                    )

            return risks

        except Exception as e:
            logger.error(f"환경 위험 식별 실패: {e}")
            return []

    async def _assess_risk_level(self, risk: Dict[str, Any]) -> RiskAssessment:
        """위험 수준 평가"""
        try:
            probability = risk.get("probability", 0.5)
            impact_score = risk.get("impact_score", 0.5)

            # 위험 수준 결정
            risk_level = await self._determine_risk_level(probability, impact_score)

            # 완화 전략 생성
            mitigation_strategies = await self._generate_mitigation_strategies(risk)

            risk_assessment = RiskAssessment(
                risk_id=risk.get("risk_id", f"risk_{int(time.time())}"),
                risk_type=risk.get("risk_type", "unknown"),
                risk_level=risk_level,
                description=risk.get("description", "알 수 없는 위험"),
                probability=probability,
                impact_score=impact_score,
                mitigation_strategies=mitigation_strategies,
            )

            return risk_assessment

        except Exception as e:
            logger.error(f"위험 수준 평가 실패: {e}")
            return await self._create_default_risk_assessment()

    async def _determine_risk_level(self, probability: float, impact_score: float) -> RiskLevel:
        """위험 수준 결정"""
        try:
            # 위험 점수 계산 (확률 * 영향도)
            risk_score = probability * impact_score

            if risk_score < 0.1:
                return RiskLevel.NONE
            elif risk_score < 0.3:
                return RiskLevel.LOW
            elif risk_score < 0.5:
                return RiskLevel.MEDIUM
            elif risk_score < 0.7:
                return RiskLevel.HIGH
            else:
                return RiskLevel.CRITICAL

        except Exception as e:
            logger.error(f"위험 수준 결정 실패: {e}")
            return RiskLevel.MEDIUM

    async def _generate_mitigation_strategies(self, risk: Dict[str, Any]) -> List[str]:
        """완화 전략 생성"""
        try:
            strategies = []
            risk_type = risk.get("risk_type", "unknown")

            if risk_type == "system":
                strategies.extend(
                    [
                        "system_restart",
                        "performance_optimization",
                        "resource_allocation",
                    ]
                )
            elif risk_type == "performance":
                strategies.extend(
                    ["load_balancing", "caching_optimization", "algorithm_improvement"]
                )
            elif risk_type == "external":
                strategies.extend(
                    [
                        "security_enhancement",
                        "access_control",
                        "monitoring_intensification",
                    ]
                )
            elif risk_type == "resource":
                strategies.extend(
                    [
                        "resource_optimization",
                        "capacity_planning",
                        "efficiency_improvement",
                    ]
                )
            else:
                strategies.append("general_mitigation")

            return strategies

        except Exception as e:
            logger.error(f"완화 전략 생성 실패: {e}")
            return ["general_mitigation"]

    async def _prioritize_risks(
        self, risk_assessments: List[RiskAssessment]
    ) -> List[RiskAssessment]:
        """위험 우선순위 설정"""
        try:
            # 위험 점수 계산 및 정렬
            for risk in risk_assessments:
                risk_score = risk.probability * risk.impact_score
                risk.risk_id = f"{risk_score:.3f}_{risk.risk_id}"

            # 위험 점수 기준으로 정렬 (높은 순)
            risk_assessments.sort(key=lambda x: x.probability * x.impact_score, reverse=True)

            return risk_assessments

        except Exception as e:
            logger.error(f"위험 우선순위 설정 실패: {e}")
            return risk_assessments

    async def _assess_resource_type(
        self, resource_type: ResourceType, resource_data: Dict[str, Any]
    ) -> ResourceAssessment:
        """자원 유형별 평가"""
        try:
            resource_info = resource_data.get(resource_type.value, {})

            availability = resource_info.get("availability", 0.8)
            utilization = resource_info.get("utilization", 0.5)
            efficiency = resource_info.get("efficiency", 0.7)
            capacity = resource_info.get("capacity", 1.0)

            # 예상 부족량 계산
            projected_shortage = None
            if utilization > 0.8:
                projected_shortage = utilization - 0.8

            # 최적화 기회 식별
            optimization_opportunities = []
            if efficiency < 0.8:
                optimization_opportunities.append("efficiency_improvement")
            if utilization > 0.9:
                optimization_opportunities.append("capacity_expansion")
            if availability < 0.7:
                optimization_opportunities.append("availability_enhancement")

            resource_assessment = ResourceAssessment(
                resource_type=resource_type,
                availability=availability,
                utilization=utilization,
                efficiency=efficiency,
                capacity=capacity,
                projected_shortage=projected_shortage,
                optimization_opportunities=optimization_opportunities,
            )

            return resource_assessment

        except Exception as e:
            logger.error(f"자원 유형별 평가 실패: {e}")
            return await self._create_default_resource_assessment(resource_type)

    async def _analyze_resource_interactions(
        self, resource_assessments: Dict[ResourceType, ResourceAssessment]
    ) -> Dict[ResourceType, ResourceAssessment]:
        """자원 상호작용 분석"""
        try:
            # 자원 간 의존성 분석
            for resource_type, assessment in resource_assessments.items():
                # 다른 자원과의 상호작용 고려
                if resource_type == ResourceType.COMPUTATIONAL:
                    # 컴퓨팅 자원은 메모리와 밀접한 관련
                    if ResourceType.MEMORY in resource_assessments:
                        memory_assessment = resource_assessments[ResourceType.MEMORY]
                        if memory_assessment.availability < 0.6:
                            assessment.optimization_opportunities.append("memory_optimization")

                elif resource_type == ResourceType.MEMORY:
                    # 메모리는 컴퓨팅 자원과 밀접한 관련
                    if ResourceType.COMPUTATIONAL in resource_assessments:
                        comp_assessment = resource_assessments[ResourceType.COMPUTATIONAL]
                        if comp_assessment.utilization > 0.9:
                            assessment.optimization_opportunities.append(
                                "computational_optimization"
                            )

            return resource_assessments

        except Exception as e:
            logger.error(f"자원 상호작용 분석 실패: {e}")
            return resource_assessments

    async def _calculate_environmental_score(self, risk_assessments: List[RiskAssessment]) -> float:
        """환경 점수 계산"""
        try:
            if not risk_assessments:
                return 1.0  # 위험이 없으면 최고 점수

            # 위험 점수들의 평균 계산
            risk_scores = []
            for risk in risk_assessments:
                risk_score = risk.probability * risk.impact_score
                risk_scores.append(risk_score)

            avg_risk_score = sum(risk_scores) / len(risk_scores)

            # 환경 점수 = 1 - 평균 위험 점수
            environmental_score = 1.0 - avg_risk_score

            return min(1.0, max(0.0, environmental_score))

        except Exception as e:
            logger.error(f"환경 점수 계산 실패: {e}")
            return 0.5

    async def _calculate_resource_score(
        self, resource_assessments: Dict[ResourceType, ResourceAssessment]
    ) -> float:
        """자원 점수 계산"""
        try:
            if not resource_assessments:
                return 0.5  # 기본값

            resource_scores = []
            for resource_type, assessment in resource_assessments.items():
                # 자원 점수 = 가용성 * 효율성
                resource_score = assessment.availability * assessment.efficiency
                resource_scores.append(resource_score)

            # 평균 자원 점수
            avg_resource_score = sum(resource_scores) / len(resource_scores)

            return min(1.0, max(0.0, avg_resource_score))

        except Exception as e:
            logger.error(f"자원 점수 계산 실패: {e}")
            return 0.5

    async def _calculate_adaptation_score(
        self,
        risk_assessments: List[RiskAssessment],
        resource_assessments: Dict[ResourceType, ResourceAssessment],
    ) -> float:
        """적응 점수 계산"""
        try:
            # 위험 완화 능력 평가
            risk_mitigation_capacity = 0.0
            if risk_assessments:
                mitigation_strategies_count = sum(
                    len(risk.mitigation_strategies) for risk in risk_assessments
                )
                avg_mitigation_strategies = mitigation_strategies_count / len(risk_assessments)
                risk_mitigation_capacity = min(
                    1.0, avg_mitigation_strategies / 3.0
                )  # 최대 3개 전략 기준

            # 자원 최적화 능력 평가
            resource_optimization_capacity = 0.0
            if resource_assessments:
                optimization_opportunities_count = sum(
                    len(assessment.optimization_opportunities)
                    for assessment in resource_assessments.values()
                )
                avg_optimization_opportunities = optimization_opportunities_count / len(
                    resource_assessments
                )
                resource_optimization_capacity = min(
                    1.0, avg_optimization_opportunities / 2.0
                )  # 최대 2개 기회 기준

            # 적응 점수 = (위험 완화 능력 + 자원 최적화 능력) / 2
            adaptation_score = (risk_mitigation_capacity + resource_optimization_capacity) / 2

            return min(1.0, max(0.0, adaptation_score))

        except Exception as e:
            logger.error(f"적응 점수 계산 실패: {e}")
            return 0.5

    async def _calculate_resilience_score(
        self,
        risk_assessments: List[RiskAssessment],
        resource_assessments: Dict[ResourceType, ResourceAssessment],
    ) -> float:
        """회복력 점수 계산"""
        try:
            # 위험 다양성 평가 (다양한 위험에 대한 대응 능력)
            risk_diversity = (
                len(set(risk.risk_type for risk in risk_assessments)) if risk_assessments else 0
            )
            risk_diversity_score = min(1.0, risk_diversity / 4.0)  # 최대 4개 유형 기준

            # 자원 다양성 평가
            resource_diversity = len(resource_assessments)
            resource_diversity_score = min(1.0, resource_diversity / 6.0)  # 최대 6개 자원 유형 기준

            # 시스템 안정성 평가
            system_stability_score = 0.8  # 기본값, 실제로는 시스템 상태에서 계산

            # 회복력 점수 = (위험 다양성 + 자원 다양성 + 시스템 안정성) / 3
            resilience_score = (
                risk_diversity_score + resource_diversity_score + system_stability_score
            ) / 3

            return min(1.0, max(0.0, resilience_score))

        except Exception as e:
            logger.error(f"회복력 점수 계산 실패: {e}")
            return 0.5

    async def _calculate_overall_survival_score(
        self,
        environmental_score: float,
        resource_score: float,
        adaptation_score: float,
        resilience_score: float,
    ) -> float:
        """전체 생존 점수 계산"""
        try:
            # 가중 평균 계산
            overall_score = (
                environmental_score * self.assessment_weights["environmental"]
                + resource_score * self.assessment_weights["resource"]
                + adaptation_score * self.assessment_weights["adaptation"]
                + resilience_score * self.assessment_weights["resilience"]
            )

            return min(1.0, max(0.0, overall_score))

        except Exception as e:
            logger.error(f"전체 생존 점수 계산 실패: {e}")
            return 0.5

    async def _calculate_confidence_level(
        self,
        risk_assessments: List[RiskAssessment],
        resource_assessments: Dict[ResourceType, ResourceAssessment],
    ) -> float:
        """신뢰도 수준 계산"""
        try:
            # 평가 데이터의 품질과 양을 기반으로 신뢰도 계산
            data_quality_score = 0.0

            # 위험 평가 데이터 품질
            if risk_assessments:
                risk_data_quality = sum(
                    1 for risk in risk_assessments if risk.probability > 0 and risk.impact_score > 0
                )
                risk_data_quality_score = risk_data_quality / len(risk_assessments)
                data_quality_score += risk_data_quality_score * 0.5

            # 자원 평가 데이터 품질
            if resource_assessments:
                resource_data_quality = sum(
                    1
                    for assessment in resource_assessments.values()
                    if assessment.availability > 0 and assessment.efficiency > 0
                )
                resource_data_quality_score = resource_data_quality / len(resource_assessments)
                data_quality_score += resource_data_quality_score * 0.5

            # 신뢰도 수준 = 데이터 품질 점수
            confidence_level = min(1.0, max(0.0, data_quality_score))

            return confidence_level

        except Exception as e:
            logger.error(f"신뢰도 수준 계산 실패: {e}")
            return 0.5

    async def _generate_risk_based_recommendations(
        self, risk_assessments: List[RiskAssessment]
    ) -> List[Recommendation]:
        """위험 기반 권장사항 생성"""
        try:
            recommendations = []

            for risk in risk_assessments:
                if risk.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                    recommendation = Recommendation(
                        recommendation_id=f"risk_mitigation_{risk.risk_id}",
                        category="risk_mitigation",
                        description=f"{risk.description} 완화",
                        priority=1 if risk.risk_level == RiskLevel.CRITICAL else 2,
                        urgency=risk.probability,
                        feasibility=0.8,
                        expected_impact=risk.impact_score,
                        implementation_time=1.0,
                        resource_requirements={},
                    )
                    recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"위험 기반 권장사항 생성 실패: {e}")
            return []

    async def _generate_resource_based_recommendations(
        self, resource_assessments: Dict[ResourceType, ResourceAssessment]
    ) -> List[Recommendation]:
        """자원 기반 권장사항 생성"""
        try:
            recommendations = []

            for resource_type, assessment in resource_assessments.items():
                if assessment.optimization_opportunities:
                    for opportunity in assessment.optimization_opportunities:
                        recommendation = Recommendation(
                            recommendation_id=f"resource_optimization_{resource_type.value}_{opportunity}",
                            category="resource_optimization",
                            description=f"{resource_type.value} {opportunity}",
                            priority=2,
                            urgency=0.6,
                            feasibility=0.7,
                            expected_impact=0.3,
                            implementation_time=0.5,
                            resource_requirements={},
                        )
                        recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"자원 기반 권장사항 생성 실패: {e}")
            return []

    async def _generate_score_based_recommendations(
        self, survival_score: SurvivalScore
    ) -> List[Recommendation]:
        """생존 점수 기반 권장사항 생성"""
        try:
            recommendations = []

            # 전체 생존 점수가 낮은 경우
            if survival_score.overall_score < 0.5:
                recommendation = Recommendation(
                    recommendation_id="survival_improvement",
                    category="survival_improvement",
                    description="전체 생존 능력 향상",
                    priority=1,
                    urgency=0.9,
                    feasibility=0.6,
                    expected_impact=0.5,
                    implementation_time=2.0,
                    resource_requirements={},
                )
                recommendations.append(recommendation)

            # 환경 점수가 낮은 경우
            if survival_score.environmental_score < 0.6:
                recommendation = Recommendation(
                    recommendation_id="environmental_improvement",
                    category="environmental_improvement",
                    description="환경 적응 능력 향상",
                    priority=2,
                    urgency=0.7,
                    feasibility=0.7,
                    expected_impact=0.4,
                    implementation_time=1.5,
                    resource_requirements={},
                )
                recommendations.append(recommendation)

            # 자원 점수가 낮은 경우
            if survival_score.resource_score < 0.6:
                recommendation = Recommendation(
                    recommendation_id="resource_improvement",
                    category="resource_improvement",
                    description="자원 관리 능력 향상",
                    priority=2,
                    urgency=0.7,
                    feasibility=0.8,
                    expected_impact=0.4,
                    implementation_time=1.0,
                    resource_requirements={},
                )
                recommendations.append(recommendation)

            return recommendations

        except Exception as e:
            logger.error(f"생존 점수 기반 권장사항 생성 실패: {e}")
            return []

    async def _prioritize_recommendations(
        self, recommendations: List[Recommendation]
    ) -> List[Recommendation]:
        """권장사항 우선순위 설정"""
        try:
            # 우선순위 점수 계산
            for recommendation in recommendations:
                priority_score = (
                    recommendation.priority * 0.4
                    + recommendation.urgency * 0.3
                    + recommendation.expected_impact * 0.3
                )
                recommendation.recommendation_id = (
                    f"{priority_score:.3f}_{recommendation.recommendation_id}"
                )

            # 우선순위 점수 기준으로 정렬 (높은 순)
            recommendations.sort(
                key=lambda x: float(x.recommendation_id.split("_")[0]), reverse=True
            )

            return recommendations

        except Exception as e:
            logger.error(f"권장사항 우선순위 설정 실패: {e}")
            return recommendations

    async def _create_default_risk_assessment(self) -> RiskAssessment:
        """기본 위험 평가 생성"""
        return RiskAssessment(
            risk_id="default_risk",
            risk_type="unknown",
            risk_level=RiskLevel.MEDIUM,
            description="알 수 없는 위험",
            probability=0.5,
            impact_score=0.5,
            mitigation_strategies=["general_mitigation"],
        )

    async def _create_default_resource_assessment(
        self, resource_type: ResourceType
    ) -> ResourceAssessment:
        """기본 자원 평가 생성"""
        return ResourceAssessment(
            resource_type=resource_type,
            availability=0.5,
            utilization=0.5,
            efficiency=0.5,
            capacity=1.0,
            projected_shortage=None,
            optimization_opportunities=[],
        )

    async def _create_default_survival_score(self) -> SurvivalScore:
        """기본 생존 점수 생성"""
        return SurvivalScore(
            overall_score=0.5,
            environmental_score=0.5,
            resource_score=0.5,
            adaptation_score=0.5,
            resilience_score=0.5,
            confidence_level=0.5,
            assessment_time=datetime.now(),
        )


async def main():
    """메인 함수"""
    survival_assessment_system = SurvivalAssessmentSystem()

    # 환경적 위험 평가
    environment_data = {
        "system_stability": 0.8,
        "performance_metrics": {"accuracy": 0.75, "efficiency": 0.7},
        "external_threats": [
            {
                "id": "threat1",
                "description": "외부 공격",
                "probability": 0.3,
                "impact": 0.7,
            }
        ],
    }
    risk_assessments = await survival_assessment_system.assess_environmental_risks(environment_data)
    print(f"위험 평가: {len(risk_assessments)}개 위험 식별")

    # 자원 가용성 평가
    resource_data = {
        "computational": {
            "availability": 0.8,
            "utilization": 0.6,
            "efficiency": 0.7,
            "capacity": 1.0,
        },
        "memory": {
            "availability": 0.7,
            "utilization": 0.5,
            "efficiency": 0.8,
            "capacity": 1.0,
        },
    }
    resource_assessments = await survival_assessment_system.evaluate_resource_availability(
        resource_data
    )
    print(f"자원 평가: {len(resource_assessments)}개 자원 평가")

    # 생존 점수 계산
    survival_score = await survival_assessment_system.calculate_survival_score(
        risk_assessments, resource_assessments
    )
    print(f"생존 점수: {survival_score.overall_score:.3f}")

    # 생존 권장사항 생성
    recommendations = await survival_assessment_system.generate_survival_recommendations(
        survival_score, risk_assessments, resource_assessments
    )
    print(f"권장사항: {len(recommendations)}개 생성")


if __name__ == "__main__":
    asyncio.run(main())
