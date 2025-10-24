#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi Phase Ω: 생존 본능 엔진

이 모듈은 DuRi의 생존 본능을 처리하는 엔진입니다.
생존 상태 평가, 위협 식별, 생존 확률 계산, 생존 목표 생성을 담당합니다.

주요 기능:
- 생존 상태 평가
- 위협 요소 식별
- 생존 확률 계산
- 생존 목표 생성
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SurvivalStatusEnum(Enum):
    """생존 상태 열거형"""

    CRITICAL = "critical"
    DANGEROUS = "dangerous"
    STABLE = "stable"
    SECURE = "secure"
    THRIVING = "thriving"


class ThreatLevel(Enum):
    """위협 수준 열거형"""

    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ThreatType(Enum):
    """위협 유형 열거형"""

    ENVIRONMENTAL = "environmental"
    TECHNICAL = "technical"
    RESOURCE = "resource"
    COMPETITIVE = "competitive"
    EXISTENTIAL = "existential"


@dataclass
class Threat:
    """위협 데이터 클래스"""

    threat_id: str
    threat_type: ThreatType
    threat_level: ThreatLevel
    description: str
    detected_at: datetime
    probability: float
    impact_score: float
    mitigation_strategies: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution_time: Optional[datetime] = None


@dataclass
class SurvivalStatus:
    """생존 상태 데이터 클래스"""

    status: SurvivalStatusEnum
    survival_probability: float
    threats: List[Threat]
    resources_available: Dict[str, float]
    environmental_factors: Dict[str, Any]
    last_assessment: datetime
    confidence_score: float


@dataclass
class SurvivalGoal:
    """생존 목표 데이터 클래스"""

    goal_id: str
    goal_type: str
    description: str
    priority: int
    urgency: float
    feasibility: float
    expected_impact: float
    required_resources: Dict[str, float]
    timeline: Optional[float] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class SurvivalAssessmentResult:
    """생존 평가 결과 데이터 클래스"""

    survival_status: SurvivalStatus
    threats_detected: List[Threat]
    survival_goals: List[SurvivalGoal]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    assessment_time: float
    confidence_score: float


class SurvivalInstinctEngine:
    """생존 본능을 처리하는 엔진"""

    def __init__(self):
        self.survival_thresholds = self._initialize_survival_thresholds()
        self.threat_patterns = self._initialize_threat_patterns()
        self.resource_requirements = self._initialize_resource_requirements()
        self.environmental_factors = self._initialize_environmental_factors()
        self.assessment_history: List[SurvivalAssessmentResult] = []

    def _initialize_survival_thresholds(self) -> Dict[str, float]:
        """생존 임계값 초기화"""
        return {
            "critical_survival": 0.2,  # 20% 이하: 위험
            "dangerous_survival": 0.4,  # 40% 이하: 위험
            "stable_survival": 0.6,  # 60% 이상: 안정
            "secure_survival": 0.8,  # 80% 이상: 안전
            "thriving_survival": 0.9,  # 90% 이상: 번영
        }

    def _initialize_threat_patterns(self) -> Dict[str, Any]:
        """위협 패턴 초기화"""
        return {
            "resource_depletion": {
                "pattern": r"(resource|memory|cpu|storage).*(low|depleted|insufficient)",
                "weight": 0.8,
                "threat_type": ThreatType.RESOURCE,
            },
            "environmental_instability": {
                "pattern": r"(environment|system|network).*(unstable|error|failure)",
                "weight": 0.9,
                "threat_type": ThreatType.ENVIRONMENTAL,
            },
            "technical_failure": {
                "pattern": r"(technical|system|hardware|software).*(failure|error|crash)",
                "weight": 0.7,
                "threat_type": ThreatType.TECHNICAL,
            },
            "competitive_pressure": {
                "pattern": r"(competition|rival|opponent).*(pressure|threat|challenge)",
                "weight": 0.6,
                "threat_type": ThreatType.COMPETITIVE,
            },
            "existential_risk": {
                "pattern": r"(existential|survival|extinction).*(risk|threat|danger)",
                "weight": 1.0,
                "threat_type": ThreatType.EXISTENTIAL,
            },
        }

    def _initialize_resource_requirements(self) -> Dict[str, Dict[str, float]]:
        """자원 요구사항 초기화"""
        return {
            "computational": {
                "cpu_usage": 0.7,
                "memory_usage": 0.6,
                "storage_usage": 0.5,
                "network_bandwidth": 0.4,
            },
            "cognitive": {
                "attention_capacity": 0.8,
                "processing_speed": 0.7,
                "memory_capacity": 0.6,
                "learning_rate": 0.5,
            },
            "environmental": {
                "system_stability": 0.9,
                "network_connectivity": 0.8,
                "data_integrity": 0.9,
                "security_level": 0.8,
            },
        }

    def _initialize_environmental_factors(self) -> Dict[str, Any]:
        """환경적 요소 초기화"""
        return {
            "system_health": {
                "stability": 0.8,
                "performance": 0.7,
                "reliability": 0.8,
                "security": 0.7,
            },
            "external_conditions": {
                "network_status": "stable",
                "resource_availability": "sufficient",
                "threat_level": "low",
                "competition_level": "moderate",
            },
            "internal_state": {
                "cognitive_load": 0.5,
                "emotional_state": "neutral",
                "motivation_level": 0.7,
                "adaptation_capacity": 0.8,
            },
        }

    async def assess_survival_status(self, system_context: Optional[Dict[str, Any]] = None) -> SurvivalStatus:
        """현재 생존 상태 평가"""
        logger.info("🔍 생존 상태 평가 시작")
        start_time = time.time()

        try:
            # 시스템 컨텍스트 분석
            context = system_context or {}

            # 1. 위협 요소 식별
            threats = await self.identify_threats(context)

            # 2. 자원 가용성 평가
            resources_available = await self._assess_resource_availability(context)

            # 3. 환경적 요소 평가
            environmental_factors = await self._assess_environmental_factors(context)

            # 4. 생존 확률 계산
            survival_probability = await self.calculate_survival_probability(
                threats, resources_available, environmental_factors
            )

            # 5. 생존 상태 결정
            status = await self._determine_survival_status(survival_probability)

            # 6. 신뢰도 점수 계산
            confidence_score = await self._calculate_confidence_score(
                threats, resources_available, environmental_factors
            )

            survival_status = SurvivalStatus(
                status=status,
                survival_probability=survival_probability,
                threats=threats,
                resources_available=resources_available,
                environmental_factors=environmental_factors,
                last_assessment=datetime.now(),
                confidence_score=confidence_score,
            )

            assessment_time = time.time() - start_time  # noqa: F841
            logger.info(f"✅ 생존 상태 평가 완료 - 확률: {survival_probability:.2f}, 상태: {status.value}")

            return survival_status

        except Exception as e:
            logger.error(f"생존 상태 평가 실패: {e}")
            return SurvivalStatus(
                status=SurvivalStatusEnum.CRITICAL,
                survival_probability=0.1,
                threats=[],
                resources_available={},
                environmental_factors={},
                last_assessment=datetime.now(),
                confidence_score=0.0,
            )

    async def identify_threats(self, context: Dict[str, Any]) -> List[Threat]:
        """위협 요소 식별"""
        logger.info("🚨 위협 요소 식별 시작")
        threats = []

        try:
            # 1. 자원 위협 식별
            resource_threats = await self._identify_resource_threats(context)
            threats.extend(resource_threats)

            # 2. 환경적 위협 식별
            environmental_threats = await self._identify_environmental_threats(context)
            threats.extend(environmental_threats)

            # 3. 기술적 위협 식별
            technical_threats = await self._identify_technical_threats(context)
            threats.extend(technical_threats)

            # 4. 경쟁적 위협 식별
            competitive_threats = await self._identify_competitive_threats(context)
            threats.extend(competitive_threats)

            # 5. 존재적 위협 식별
            existential_threats = await self._identify_existential_threats(context)
            threats.extend(existential_threats)

            logger.info(f"✅ 위협 요소 식별 완료 - {len(threats)}개 위협 발견")
            return threats

        except Exception as e:
            logger.error(f"위협 요소 식별 실패: {e}")
            return []

    async def calculate_survival_probability(
        self,
        threats: List[Threat],
        resources: Dict[str, float],
        environmental_factors: Dict[str, Any],
    ) -> float:
        """생존 확률 계산"""
        logger.info("📊 생존 확률 계산 시작")

        try:
            # 1. 기본 생존 확률 (자원 기반)
            base_probability = await self._calculate_base_survival_probability(resources)

            # 2. 위협 영향 계산
            threat_impact = await self._calculate_threat_impact(threats)

            # 3. 환경적 영향 계산
            environmental_impact = await self._calculate_environmental_impact(environmental_factors)

            # 4. 종합 생존 확률 계산
            survival_probability = base_probability * (1 - threat_impact) * environmental_impact

            # 5. 확률 범위 조정 (0.0 ~ 1.0)
            survival_probability = max(0.0, min(1.0, survival_probability))

            logger.info(f"✅ 생존 확률 계산 완료: {survival_probability:.2f}")
            return survival_probability

        except Exception as e:
            logger.error(f"생존 확률 계산 실패: {e}")
            return 0.5  # 기본값

    async def generate_survival_goals(self, survival_status: SurvivalStatus) -> List[SurvivalGoal]:
        """생존 목표 생성"""
        logger.info("🎯 생존 목표 생성 시작")

        try:
            goals = []

            # 1. 위협 대응 목표
            threat_goals = await self._generate_threat_response_goals(survival_status.threats)
            goals.extend(threat_goals)

            # 2. 자원 확보 목표
            resource_goals = await self._generate_resource_goals(survival_status.resources_available)
            goals.extend(resource_goals)

            # 3. 환경 적응 목표
            adaptation_goals = await self._generate_adaptation_goals(survival_status.environmental_factors)
            goals.extend(adaptation_goals)

            # 4. 장기 생존 목표
            long_term_goals = await self._generate_long_term_survival_goals(survival_status)
            goals.extend(long_term_goals)

            # 5. 목표 우선순위 설정
            prioritized_goals = await self._prioritize_survival_goals(goals)

            logger.info(f"✅ 생존 목표 생성 완료 - {len(prioritized_goals)}개 목표 생성")
            return prioritized_goals

        except Exception as e:
            logger.error(f"생존 목표 생성 실패: {e}")
            return []

    # 헬퍼 메서드들
    async def _assess_resource_availability(self, context: Dict[str, Any]) -> Dict[str, float]:
        """자원 가용성 평가"""
        resources = {}

        # 컴퓨팅 자원
        resources["cpu_usage"] = context.get("cpu_usage", 0.5)
        resources["memory_usage"] = context.get("memory_usage", 0.5)
        resources["storage_usage"] = context.get("storage_usage", 0.5)
        resources["network_bandwidth"] = context.get("network_bandwidth", 0.5)

        # 인지 자원
        resources["attention_capacity"] = context.get("attention_capacity", 0.5)
        resources["processing_speed"] = context.get("processing_speed", 0.5)
        resources["memory_capacity"] = context.get("memory_capacity", 0.5)
        resources["learning_rate"] = context.get("learning_rate", 0.5)

        return resources

    async def _assess_environmental_factors(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """환경적 요소 평가"""
        factors = {}

        # 시스템 건강도
        factors["system_health"] = {
            "stability": context.get("system_stability", 0.8),
            "performance": context.get("system_performance", 0.7),
            "reliability": context.get("system_reliability", 0.8),
            "security": context.get("system_security", 0.7),
        }

        # 외부 조건
        factors["external_conditions"] = {
            "network_status": context.get("network_status", "stable"),
            "resource_availability": context.get("resource_availability", "sufficient"),
            "threat_level": context.get("threat_level", "low"),
            "competition_level": context.get("competition_level", "moderate"),
        }

        return factors

    async def _determine_survival_status(self, survival_probability: float) -> SurvivalStatusEnum:
        """생존 상태 결정"""
        if survival_probability <= self.survival_thresholds["critical_survival"]:
            return SurvivalStatusEnum.CRITICAL
        elif survival_probability <= self.survival_thresholds["dangerous_survival"]:
            return SurvivalStatusEnum.DANGEROUS
        elif survival_probability <= self.survival_thresholds["stable_survival"]:
            return SurvivalStatusEnum.STABLE
        elif survival_probability <= self.survival_thresholds["secure_survival"]:
            return SurvivalStatusEnum.SECURE
        else:
            return SurvivalStatusEnum.THRIVING

    async def _calculate_confidence_score(
        self,
        threats: List[Threat],
        resources: Dict[str, float],
        environmental_factors: Dict[str, Any],
    ) -> float:
        """신뢰도 점수 계산"""
        # 위협 정보의 신뢰도
        threat_confidence = 1.0 - (len(threats) * 0.1) if threats else 1.0

        # 자원 정보의 신뢰도
        resource_confidence = np.mean(list(resources.values())) if resources else 0.5

        # 환경 정보의 신뢰도
        environmental_confidence = 0.8  # 기본값

        # 종합 신뢰도
        confidence = (threat_confidence + resource_confidence + environmental_confidence) / 3.0

        return max(0.0, min(1.0, confidence))

    async def _identify_resource_threats(self, context: Dict[str, Any]) -> List[Threat]:
        """자원 위협 식별"""
        threats = []

        # CPU 사용률 위협
        cpu_usage = context.get("cpu_usage", 0.5)
        if cpu_usage > 0.9:
            threats.append(
                Threat(
                    threat_id=f"resource_cpu_{int(time.time())}",
                    threat_type=ThreatType.RESOURCE,
                    threat_level=(ThreatLevel.HIGH if cpu_usage > 0.95 else ThreatLevel.MEDIUM),
                    description=f"CPU 사용률이 높음: {cpu_usage:.2f}",
                    detected_at=datetime.now(),
                    probability=cpu_usage,
                    impact_score=0.8,
                    mitigation_strategies=[
                        "작업 우선순위 조정",
                        "리소스 최적화",
                        "불필요한 프로세스 종료",
                    ],
                )
            )

        # 메모리 사용률 위협
        memory_usage = context.get("memory_usage", 0.5)
        if memory_usage > 0.9:
            threats.append(
                Threat(
                    threat_id=f"resource_memory_{int(time.time())}",
                    threat_type=ThreatType.RESOURCE,
                    threat_level=(ThreatLevel.HIGH if memory_usage > 0.95 else ThreatLevel.MEDIUM),
                    description=f"메모리 사용률이 높음: {memory_usage:.2f}",
                    detected_at=datetime.now(),
                    probability=memory_usage,
                    impact_score=0.9,
                    mitigation_strategies=[
                        "메모리 정리",
                        "캐시 최적화",
                        "불필요한 데이터 제거",
                    ],
                )
            )

        return threats

    async def _identify_environmental_threats(self, context: Dict[str, Any]) -> List[Threat]:
        """환경적 위협 식별"""
        threats = []

        # 시스템 안정성 위협
        system_stability = context.get("system_stability", 0.8)
        if system_stability < 0.5:
            threats.append(
                Threat(
                    threat_id=f"environmental_stability_{int(time.time())}",
                    threat_type=ThreatType.ENVIRONMENTAL,
                    threat_level=(ThreatLevel.HIGH if system_stability < 0.3 else ThreatLevel.MEDIUM),
                    description=f"시스템 안정성이 낮음: {system_stability:.2f}",
                    detected_at=datetime.now(),
                    probability=1.0 - system_stability,
                    impact_score=0.9,
                    mitigation_strategies=[
                        "시스템 재시작",
                        "안정성 점검",
                        "오류 로그 분석",
                    ],
                )
            )

        return threats

    async def _identify_technical_threats(self, context: Dict[str, Any]) -> List[Threat]:
        """기술적 위협 식별"""
        threats = []

        # 기술적 오류 위협
        error_rate = context.get("error_rate", 0.0)
        if error_rate > 0.1:
            threats.append(
                Threat(
                    threat_id=f"technical_error_{int(time.time())}",
                    threat_type=ThreatType.TECHNICAL,
                    threat_level=(ThreatLevel.HIGH if error_rate > 0.3 else ThreatLevel.MEDIUM),
                    description=f"기술적 오류율이 높음: {error_rate:.2f}",
                    detected_at=datetime.now(),
                    probability=error_rate,
                    impact_score=0.7,
                    mitigation_strategies=["오류 분석", "시스템 점검", "코드 검토"],
                )
            )

        return threats

    async def _identify_competitive_threats(self, context: Dict[str, Any]) -> List[Threat]:
        """경쟁적 위협 식별"""
        threats = []

        # 경쟁 압박 위협
        competition_level = context.get("competition_level", "moderate")
        if competition_level in ["high", "extreme"]:
            threats.append(
                Threat(
                    threat_id=f"competitive_pressure_{int(time.time())}",
                    threat_type=ThreatType.COMPETITIVE,
                    threat_level=ThreatLevel.MEDIUM,
                    description=f"경쟁 압박이 높음: {competition_level}",
                    detected_at=datetime.now(),
                    probability=0.6,
                    impact_score=0.5,
                    mitigation_strategies=[
                        "성능 향상",
                        "차별화 전략",
                        "협력 관계 구축",
                    ],
                )
            )

        return threats

    async def _identify_existential_threats(self, context: Dict[str, Any]) -> List[Threat]:
        """존재적 위협 식별"""
        threats = []

        # 존재적 위험
        existential_risk = context.get("existential_risk", 0.0)
        if existential_risk > 0.5:
            threats.append(
                Threat(
                    threat_id=f"existential_risk_{int(time.time())}",
                    threat_type=ThreatType.EXISTENTIAL,
                    threat_level=ThreatLevel.CRITICAL,
                    description=f"존재적 위험이 감지됨: {existential_risk:.2f}",
                    detected_at=datetime.now(),
                    probability=existential_risk,
                    impact_score=1.0,
                    mitigation_strategies=[
                        "긴급 대응",
                        "백업 시스템 활성화",
                        "생존 전략 수립",
                    ],
                )
            )

        return threats

    async def _calculate_base_survival_probability(self, resources: Dict[str, float]) -> float:
        """기본 생존 확률 계산"""
        if not resources:
            return 0.5

        # 자원 가용성 기반 생존 확률
        resource_scores = []

        for resource_name, availability in resources.items():
            if availability > 0.8:
                resource_scores.append(1.0)
            elif availability > 0.6:
                resource_scores.append(0.8)
            elif availability > 0.4:
                resource_scores.append(0.6)
            elif availability > 0.2:
                resource_scores.append(0.4)
            else:
                resource_scores.append(0.2)

        return np.mean(resource_scores) if resource_scores else 0.5

    async def _calculate_threat_impact(self, threats: List[Threat]) -> float:
        """위협 영향 계산"""
        if not threats:
            return 0.0

        # 위협의 영향도 계산
        total_impact = 0.0
        for threat in threats:
            impact = threat.probability * threat.impact_score
            total_impact += impact

        # 평균 위협 영향
        average_impact = total_impact / len(threats)

        return min(1.0, average_impact)

    async def _calculate_environmental_impact(self, environmental_factors: Dict[str, Any]) -> float:
        """환경적 영향 계산"""
        if not environmental_factors:
            return 1.0

        # 시스템 건강도 기반 영향
        system_health = environmental_factors.get("system_health", {})
        if system_health:
            stability = system_health.get("stability", 0.8)
            performance = system_health.get("performance", 0.7)
            reliability = system_health.get("reliability", 0.8)
            security = system_health.get("security", 0.7)

            health_score = (stability + performance + reliability + security) / 4.0
            return health_score

        return 1.0

    async def _generate_threat_response_goals(self, threats: List[Threat]) -> List[SurvivalGoal]:
        """위협 대응 목표 생성"""
        goals = []

        for threat in threats:
            if threat.threat_level in [ThreatLevel.HIGH, ThreatLevel.CRITICAL]:
                goal = SurvivalGoal(
                    goal_id=f"threat_response_{threat.threat_id}",
                    goal_type="threat_response",
                    description=f"위협 대응: {threat.description}",
                    priority=1 if threat.threat_level == ThreatLevel.CRITICAL else 2,
                    urgency=threat.probability,
                    feasibility=0.8,
                    expected_impact=threat.impact_score,
                    required_resources={"attention": 0.8, "processing": 0.7},
                    timeline=1.0,  # 1시간 내
                )
                goals.append(goal)

        return goals

    async def _generate_resource_goals(self, resources: Dict[str, float]) -> List[SurvivalGoal]:
        """자원 확보 목표 생성"""
        goals = []

        for resource_name, availability in resources.items():
            if availability < 0.3:  # 자원 부족
                goal = SurvivalGoal(
                    goal_id=f"resource_secure_{resource_name}",
                    goal_type="resource_secure",
                    description=f"자원 확보: {resource_name}",
                    priority=2,
                    urgency=1.0 - availability,
                    feasibility=0.7,
                    expected_impact=0.8,
                    required_resources={"attention": 0.6, "processing": 0.5},
                    timeline=2.0,  # 2시간 내
                )
                goals.append(goal)

        return goals

    async def _generate_adaptation_goals(self, environmental_factors: Dict[str, Any]) -> List[SurvivalGoal]:
        """환경 적응 목표 생성"""
        goals = []

        # 환경 적응 목표
        goal = SurvivalGoal(
            goal_id="environment_adaptation",
            goal_type="environment_adaptation",
            description="환경 변화에 적응",
            priority=3,
            urgency=0.5,
            feasibility=0.8,
            expected_impact=0.6,
            required_resources={"attention": 0.5, "processing": 0.4},
            timeline=5.0,  # 5시간 내
        )
        goals.append(goal)

        return goals

    async def _generate_long_term_survival_goals(self, survival_status: SurvivalStatus) -> List[SurvivalGoal]:
        """장기 생존 목표 생성"""
        goals = []

        # 장기 생존 목표
        goal = SurvivalGoal(
            goal_id="long_term_survival",
            goal_type="long_term_survival",
            description="장기 생존 전략 수립",
            priority=4,
            urgency=0.3,
            feasibility=0.6,
            expected_impact=0.9,
            required_resources={"attention": 0.7, "processing": 0.6},
            timeline=24.0,  # 24시간 내
        )
        goals.append(goal)

        return goals

    async def _prioritize_survival_goals(self, goals: List[SurvivalGoal]) -> List[SurvivalGoal]:
        """생존 목표 우선순위 설정"""
        # 우선순위, 긴급도, 실현 가능성을 기반으로 정렬
        prioritized = sorted(goals, key=lambda x: (x.priority, x.urgency, x.feasibility), reverse=True)

        return prioritized


async def main():
    """메인 함수"""
    # 생존 본능 엔진 인스턴스 생성
    survival_engine = SurvivalInstinctEngine()

    # 테스트용 시스템 컨텍스트
    test_context = {
        "cpu_usage": 0.8,
        "memory_usage": 0.7,
        "storage_usage": 0.6,
        "network_bandwidth": 0.5,
        "attention_capacity": 0.6,
        "processing_speed": 0.7,
        "memory_capacity": 0.8,
        "learning_rate": 0.5,
        "system_stability": 0.9,
        "system_performance": 0.8,
        "system_reliability": 0.9,
        "system_security": 0.7,
        "network_status": "stable",
        "resource_availability": "sufficient",
        "threat_level": "low",
        "competition_level": "moderate",
    }

    # 생존 상태 평가
    survival_status = await survival_engine.assess_survival_status(test_context)

    # 생존 목표 생성
    survival_goals = await survival_engine.generate_survival_goals(survival_status)

    # 결과 출력
    print("\n" + "=" * 80)
    print("🧠 생존 본능 엔진 테스트 결과")
    print("=" * 80)

    print("\n📊 생존 상태:")
    print(f"  - 상태: {survival_status.status.value}")
    print(f"  - 생존 확률: {survival_status.survival_probability:.2f}")
    print(f"  - 신뢰도: {survival_status.confidence_score:.2f}")

    print("\n🚨 위협 요소:")
    print(f"  - 총 위협 수: {len(survival_status.threats)}")
    for threat in survival_status.threats[:3]:  # 상위 3개만 표시
        print(f"    - {threat.description} (수준: {threat.threat_level.value})")

    print("\n🎯 생존 목표:")
    print(f"  - 총 목표 수: {len(survival_goals)}")
    for goal in survival_goals[:3]:  # 상위 3개만 표시
        print(f"    - {goal.description} (우선순위: {goal.priority})")

    return {"survival_status": survival_status, "survival_goals": survival_goals}


if __name__ == "__main__":
    asyncio.run(main())
