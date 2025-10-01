#!/usr/bin/env python3
"""
AdvancedSocialitySimulationSystem - Phase 15.0
고급 사회성 시뮬레이션 시스템

목적:
- 사회적 상호작용 시뮬레이션을 통한 사회성 개발
- 협력, 신뢰 형성, 역할 분담 등의 사회적 능력 향상
- 시뮬레이션 로그 기반 학습 및 진화 트리거 생성
"""

import json
import logging
import random
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SocialInteractionType(Enum):
    """사회적 상호작용 유형"""

    COOPERATION = "cooperation"
    TRUST_BUILDING = "trust_building"
    ROLE_DISTRIBUTION = "role_distribution"
    CONFLICT_RESOLUTION = "conflict_resolution"
    COMMUNICATION = "communication"


class TrustLevel(Enum):
    """신뢰 수준"""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    VERY_HIGH = "very_high"


class CooperationLevel(Enum):
    """협력 수준"""

    RESISTANT = "resistant"
    PASSIVE = "passive"
    ACTIVE = "active"
    ENTHUSIASTIC = "enthusiastic"


class RoleType(Enum):
    """역할 유형"""

    LEADER = "leader"
    SUPPORTER = "supporter"
    MEDIATOR = "mediator"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"


@dataclass
class SocialEntity:
    """사회적 개체"""

    id: str
    name: str
    personality_traits: List[str]
    current_trust_level: TrustLevel
    cooperation_tendency: CooperationLevel
    preferred_role: RoleType
    communication_style: str
    emotional_state: str


@dataclass
class SocialInteraction:
    """사회적 상호작용"""

    id: str
    interaction_type: SocialInteractionType
    participants: List[str]
    context: str
    duration_minutes: int
    outcome: str
    trust_impact: float
    cooperation_impact: float
    role_evolution: Dict[str, RoleType]
    timestamp: datetime


@dataclass
class SimulationScenario:
    """시뮬레이션 시나리오"""

    id: str
    scenario_type: str
    initial_conditions: Dict[str, Any]
    participants: List[SocialEntity]
    objectives: List[str]
    success_criteria: List[str]
    duration_hours: int
    complexity_level: str


@dataclass
class SimulationLog:
    """시뮬레이션 로그"""

    id: str
    scenario_id: str
    interaction_id: str
    log_type: str
    content: str
    internal_judgment: str
    external_feedback: str
    evolution_trigger: bool
    timestamp: datetime


@dataclass
class TrustRelationship:
    """신뢰 관계"""

    id: str
    entity_a: str
    entity_b: str
    trust_level: TrustLevel
    trust_factors: List[str]
    relationship_duration: timedelta
    last_interaction: datetime


@dataclass
class RoleDistribution:
    """역할 분담"""

    id: str
    scenario_id: str
    entity_id: str
    assigned_role: RoleType
    role_effectiveness: float
    adaptation_ability: float
    collaboration_score: float
    timestamp: datetime


class AdvancedSocialitySimulationSystem:
    """고급 사회성 시뮬레이션 시스템"""

    def __init__(self):
        self.social_entities: List[SocialEntity] = []
        self.social_interactions: List[SocialInteraction] = []
        self.simulation_scenarios: List[SimulationScenario] = []
        self.simulation_logs: List[SimulationLog] = []
        self.trust_relationships: List[TrustRelationship] = []
        self.role_distributions: List[RoleDistribution] = []
        self.current_scenario: Optional[SimulationScenario] = None
        self.simulation_active = False

        logger.info("AdvancedSocialitySimulationSystem 초기화 완료")

    def create_social_entity(
        self,
        name: str,
        personality_traits: List[str],
        initial_trust: TrustLevel = TrustLevel.MODERATE,
        cooperation_tendency: CooperationLevel = CooperationLevel.ACTIVE,
        preferred_role: RoleType = RoleType.SUPPORTER,
    ) -> SocialEntity:
        """사회적 개체 생성"""
        entity_id = f"entity_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        entity = SocialEntity(
            id=entity_id,
            name=name,
            personality_traits=personality_traits,
            current_trust_level=initial_trust,
            cooperation_tendency=cooperation_tendency,
            preferred_role=preferred_role,
            communication_style=self._generate_communication_style(personality_traits),
            emotional_state="neutral",
        )

        self.social_entities.append(entity)
        logger.info(f"사회적 개체 생성: {name}")
        return entity

    def _generate_communication_style(self, personality_traits: List[str]) -> str:
        """의사소통 스타일 생성"""
        if "외향적" in personality_traits:
            return "직접적이고 적극적"
        elif "내향적" in personality_traits:
            return "신중하고 사려깊음"
        elif "분석적" in personality_traits:
            return "논리적이고 체계적"
        else:
            return "균형잡힌 소통"

    def create_simulation_scenario(
        self,
        scenario_type: str,
        objectives: List[str],
        participants: List[SocialEntity],
        duration_hours: int = 2,
    ) -> SimulationScenario:
        """시뮬레이션 시나리오 생성"""
        scenario_id = f"scenario_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 초기 조건 설정
        initial_conditions = {
            "trust_level": "moderate",
            "cooperation_willingness": "active",
            "communication_openness": "high",
            "conflict_resolution_approach": "collaborative",
        }

        # 성공 기준 설정
        success_criteria = [
            "상호 신뢰 수준 80% 이상 달성",
            "역할 분담 만족도 85% 이상",
            "협력 효율성 90% 이상",
            "갈등 해결 성공률 95% 이상",
        ]

        scenario = SimulationScenario(
            id=scenario_id,
            scenario_type=scenario_type,
            initial_conditions=initial_conditions,
            participants=participants,
            objectives=objectives,
            success_criteria=success_criteria,
            duration_hours=duration_hours,
            complexity_level="moderate",
        )

        self.simulation_scenarios.append(scenario)
        logger.info(f"시뮬레이션 시나리오 생성: {scenario_type}")
        return scenario

    def start_social_simulation(self, scenario: SimulationScenario) -> bool:
        """사회성 시뮬레이션 시작"""
        if self.simulation_active:
            logger.warning("이미 활성화된 시뮬레이션이 있습니다.")
            return False

        self.current_scenario = scenario
        self.simulation_active = True

        # 초기 신뢰 관계 설정
        self._initialize_trust_relationships(scenario.participants)

        # 초기 역할 분담 설정
        self._initialize_role_distributions(scenario)

        logger.info(f"사회성 시뮬레이션 시작: {scenario.scenario_type}")
        return True

    def _initialize_trust_relationships(self, participants: List[SocialEntity]):
        """신뢰 관계 초기화"""
        for i, entity_a in enumerate(participants):
            for j, entity_b in enumerate(participants):
                if i != j:
                    trust_id = f"trust_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    trust_relationship = TrustRelationship(
                        id=trust_id,
                        entity_a=entity_a.id,
                        entity_b=entity_b.id,
                        trust_level=TrustLevel.MODERATE,
                        trust_factors=["초기 상호작용", "공통 목표"],
                        relationship_duration=timedelta(0),
                        last_interaction=datetime.now(),
                    )

                    self.trust_relationships.append(trust_relationship)

    def _initialize_role_distributions(self, scenario: SimulationScenario):
        """역할 분담 초기화"""
        roles = [
            RoleType.LEADER,
            RoleType.SUPPORTER,
            RoleType.MEDIATOR,
            RoleType.SPECIALIST,
        ]

        for i, entity in enumerate(scenario.participants):
            role_id = f"role_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 개체의 선호 역할을 우선 고려
            assigned_role = (
                entity.preferred_role
                if entity.preferred_role in roles
                else roles[i % len(roles)]
            )

            role_distribution = RoleDistribution(
                id=role_id,
                scenario_id=scenario.id,
                entity_id=entity.id,
                assigned_role=assigned_role,
                role_effectiveness=0.7,  # 초기 효과성
                adaptation_ability=0.8,  # 초기 적응 능력
                collaboration_score=0.75,  # 초기 협력 점수
                timestamp=datetime.now(),
            )

            self.role_distributions.append(role_distribution)

    def conduct_social_interaction(
        self,
        interaction_type: SocialInteractionType,
        participants: List[str],
        context: str,
        duration_minutes: int = 30,
    ) -> SocialInteraction:
        """사회적 상호작용 수행"""
        if not self.simulation_active:
            logger.warning("활성화된 시뮬레이션이 없습니다.")
            return None

        interaction_id = f"interaction_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 상호작용 결과 시뮬레이션
        outcome = self._simulate_interaction_outcome(interaction_type, participants)
        trust_impact = self._calculate_trust_impact(interaction_type, outcome)
        cooperation_impact = self._calculate_cooperation_impact(
            interaction_type, outcome
        )
        role_evolution = self._simulate_role_evolution(participants, interaction_type)

        interaction = SocialInteraction(
            id=interaction_id,
            interaction_type=interaction_type,
            participants=participants,
            context=context,
            duration_minutes=duration_minutes,
            outcome=outcome,
            trust_impact=trust_impact,
            cooperation_impact=cooperation_impact,
            role_evolution=role_evolution,
            timestamp=datetime.now(),
        )

        self.social_interactions.append(interaction)

        # 시뮬레이션 로그 생성
        self._create_simulation_log(interaction)

        logger.info(f"사회적 상호작용 수행: {interaction_type.value}")
        return interaction

    def _simulate_interaction_outcome(
        self, interaction_type: SocialInteractionType, participants: List[str]
    ) -> str:
        """상호작용 결과 시뮬레이션"""
        if interaction_type == SocialInteractionType.COOPERATION:
            return "성공적인 협력으로 목표 달성"
        elif interaction_type == SocialInteractionType.TRUST_BUILDING:
            return "상호 신뢰 관계 강화"
        elif interaction_type == SocialInteractionType.ROLE_DISTRIBUTION:
            return "효과적인 역할 분담 및 조정"
        elif interaction_type == SocialInteractionType.CONFLICT_RESOLUTION:
            return "갈등 해결 및 상호 이해 증진"
        else:  # COMMUNICATION
            return "원활한 의사소통 및 정보 공유"

    def _calculate_trust_impact(
        self, interaction_type: SocialInteractionType, outcome: str
    ) -> float:
        """신뢰 영향 계산"""
        base_impact = {
            SocialInteractionType.COOPERATION: 0.3,
            SocialInteractionType.TRUST_BUILDING: 0.5,
            SocialInteractionType.ROLE_DISTRIBUTION: 0.2,
            SocialInteractionType.CONFLICT_RESOLUTION: 0.4,
            SocialInteractionType.COMMUNICATION: 0.25,
        }

        return base_impact.get(interaction_type, 0.2)

    def _calculate_cooperation_impact(
        self, interaction_type: SocialInteractionType, outcome: str
    ) -> float:
        """협력 영향 계산"""
        base_impact = {
            SocialInteractionType.COOPERATION: 0.4,
            SocialInteractionType.TRUST_BUILDING: 0.3,
            SocialInteractionType.ROLE_DISTRIBUTION: 0.35,
            SocialInteractionType.CONFLICT_RESOLUTION: 0.25,
            SocialInteractionType.COMMUNICATION: 0.2,
        }

        return base_impact.get(interaction_type, 0.25)

    def _simulate_role_evolution(
        self, participants: List[str], interaction_type: SocialInteractionType
    ) -> Dict[str, RoleType]:
        """역할 진화 시뮬레이션"""
        role_evolution = {}

        for participant in participants:
            # 현재 역할에서 약간의 진화
            current_roles = [
                rd.assigned_role
                for rd in self.role_distributions
                if rd.entity_id == participant
            ]

            if current_roles:
                current_role = current_roles[0]
                # 역할 적응성 향상
                role_evolution[participant] = current_role

        return role_evolution

    def _create_simulation_log(self, interaction: SocialInteraction):
        """시뮬레이션 로그 생성"""
        log_id = f"log_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 내부 판단 결과
        internal_judgment = self._generate_internal_judgment(interaction)

        # 외부 피드백 시뮬레이션
        external_feedback = self._simulate_external_feedback(interaction)

        # 진화 트리거 판단
        evolution_trigger = self._assess_evolution_trigger(
            interaction, internal_judgment, external_feedback
        )

        log = SimulationLog(
            id=log_id,
            scenario_id=self.current_scenario.id if self.current_scenario else "",
            interaction_id=interaction.id,
            log_type="interaction_log",
            content=f"상호작용: {interaction.interaction_type.value} - {interaction.outcome}",
            internal_judgment=internal_judgment,
            external_feedback=external_feedback,
            evolution_trigger=evolution_trigger,
            timestamp=datetime.now(),
        )

        self.simulation_logs.append(log)
        logger.info(
            f"시뮬레이션 로그 생성: 진화 트리거 {'활성화' if evolution_trigger else '비활성화'}"
        )

    def _generate_internal_judgment(self, interaction: SocialInteraction) -> str:
        """내부 판단 결과 생성"""
        if interaction.trust_impact > 0.4:
            return "신뢰 관계가 크게 향상되었습니다. 협력 기반이 강화되었습니다."
        elif interaction.cooperation_impact > 0.35:
            return "협력 수준이 향상되었습니다. 역할 분담이 효과적입니다."
        else:
            return "상호작용이 양호하지만 추가 개선이 필요합니다."

    def _simulate_external_feedback(self, interaction: SocialInteraction) -> str:
        """외부 피드백 시뮬레이션"""
        if interaction.trust_impact > 0.4 and interaction.cooperation_impact > 0.35:
            return "외부 관찰자: 매우 효과적인 사회적 상호작용입니다."
        elif interaction.trust_impact > 0.3:
            return "외부 관찰자: 신뢰 구축이 잘 이루어지고 있습니다."
        else:
            return "외부 관찰자: 기본적인 상호작용은 양호하지만 개선 여지가 있습니다."

    def _assess_evolution_trigger(
        self,
        interaction: SocialInteraction,
        internal_judgment: str,
        external_feedback: str,
    ) -> bool:
        """진화 트리거 평가"""
        # 신뢰와 협력 영향이 모두 높을 때 진화 트리거 활성화
        if interaction.trust_impact > 0.4 and interaction.cooperation_impact > 0.35:
            return True
        # 내부 판단과 외부 피드백이 모두 긍정적일 때
        elif "크게 향상" in internal_judgment and "효과적" in external_feedback:
            return True
        else:
            return False

    def update_trust_relationships(self, interaction: SocialInteraction):
        """신뢰 관계 업데이트"""
        for i, participant_a in enumerate(interaction.participants):
            for j, participant_b in enumerate(interaction.participants):
                if i != j:
                    # 해당 신뢰 관계 찾기
                    for trust_rel in self.trust_relationships:
                        if (
                            trust_rel.entity_a == participant_a
                            and trust_rel.entity_b == participant_b
                        ):
                            # 신뢰 수준 업데이트
                            current_level = trust_rel.trust_level
                            if interaction.trust_impact > 0.3:
                                if current_level == TrustLevel.LOW:
                                    trust_rel.trust_level = TrustLevel.MODERATE
                                elif current_level == TrustLevel.MODERATE:
                                    trust_rel.trust_level = TrustLevel.HIGH
                                elif current_level == TrustLevel.HIGH:
                                    trust_rel.trust_level = TrustLevel.VERY_HIGH

                            trust_rel.last_interaction = datetime.now()
                            break

    def evaluate_simulation_success(self) -> Dict[str, Any]:
        """시뮬레이션 성공도 평가"""
        if not self.current_scenario:
            return {"error": "활성화된 시나리오가 없습니다."}

        # 신뢰 관계 평가
        trust_scores = []
        for rel in self.trust_relationships:
            if rel.entity_a in [p.id for p in self.current_scenario.participants]:
                trust_value = (
                    0.25
                    if rel.trust_level == TrustLevel.LOW
                    else (
                        0.5
                        if rel.trust_level == TrustLevel.MODERATE
                        else 0.75 if rel.trust_level == TrustLevel.HIGH else 1.0
                    )
                )
                trust_scores.append(trust_value)
        avg_trust_score = sum(trust_scores) / len(trust_scores) if trust_scores else 0

        # 역할 분담 평가
        role_scores = [
            rd.role_effectiveness
            for rd in self.role_distributions
            if rd.scenario_id == self.current_scenario.id
        ]
        avg_role_score = sum(role_scores) / len(role_scores) if role_scores else 0

        # 협력 점수 평가
        cooperation_scores = [
            rd.collaboration_score
            for rd in self.role_distributions
            if rd.scenario_id == self.current_scenario.id
        ]
        avg_cooperation_score = (
            sum(cooperation_scores) / len(cooperation_scores)
            if cooperation_scores
            else 0
        )

        # 진화 트리거 수
        evolution_triggers = sum(
            1
            for log in self.simulation_logs
            if log.evolution_trigger and log.scenario_id == self.current_scenario.id
        )

        success_evaluation = {
            "scenario_type": self.current_scenario.scenario_type,
            "average_trust_score": avg_trust_score,
            "average_role_effectiveness": avg_role_score,
            "average_cooperation_score": avg_cooperation_score,
            "total_interactions": len(
                [
                    i
                    for i in self.social_interactions
                    if i.id
                    in [
                        log.interaction_id
                        for log in self.simulation_logs
                        if log.scenario_id == self.current_scenario.id
                    ]
                ]
            ),
            "evolution_triggers": evolution_triggers,
            "success_rate": (avg_trust_score + avg_role_score + avg_cooperation_score)
            / 3,
            "evaluation_timestamp": datetime.now().isoformat(),
        }

        logger.info(
            f"시뮬레이션 성공도 평가 완료: 성공률 {success_evaluation['success_rate']:.2f}"
        )
        return success_evaluation

    def end_simulation(self) -> Dict[str, Any]:
        """시뮬레이션 종료"""
        if not self.simulation_active:
            return {"error": "활성화된 시뮬레이션이 없습니다."}

        # 최종 평가
        final_evaluation = self.evaluate_simulation_success()

        # 시뮬레이션 상태 초기화
        self.simulation_active = False
        self.current_scenario = None

        logger.info("사회성 시뮬레이션 종료")
        return final_evaluation

    def get_sociality_simulation_statistics(self) -> Dict[str, Any]:
        """사회성 시뮬레이션 통계"""
        total_entities = len(self.social_entities)
        total_interactions = len(self.social_interactions)
        total_scenarios = len(self.simulation_scenarios)
        total_logs = len(self.simulation_logs)
        total_trust_relationships = len(self.trust_relationships)
        total_role_distributions = len(self.role_distributions)

        # 상호작용 유형별 통계
        interaction_type_stats = {}
        for interaction_type in SocialInteractionType:
            type_count = sum(
                1
                for i in self.social_interactions
                if i.interaction_type == interaction_type
            )
            interaction_type_stats[interaction_type.value] = type_count

        # 진화 트리거 통계
        evolution_triggers = sum(
            1 for log in self.simulation_logs if log.evolution_trigger
        )

        statistics = {
            "total_entities": total_entities,
            "total_interactions": total_interactions,
            "total_scenarios": total_scenarios,
            "total_logs": total_logs,
            "total_trust_relationships": total_trust_relationships,
            "total_role_distributions": total_role_distributions,
            "interaction_type_statistics": interaction_type_stats,
            "evolution_triggers": evolution_triggers,
            "simulation_active": self.simulation_active,
            "current_scenario": (
                self.current_scenario.scenario_type if self.current_scenario else None
            ),
            "last_updated": datetime.now().isoformat(),
        }

        logger.info("사회성 시뮬레이션 통계 생성 완료")
        return statistics

    def export_sociality_simulation_data(self) -> Dict[str, Any]:
        """사회성 시뮬레이션 데이터 내보내기"""
        return {
            "social_entities": [asdict(e) for e in self.social_entities],
            "social_interactions": [asdict(i) for i in self.social_interactions],
            "simulation_scenarios": [asdict(s) for s in self.simulation_scenarios],
            "simulation_logs": [asdict(l) for l in self.simulation_logs],
            "trust_relationships": [asdict(t) for t in self.trust_relationships],
            "role_distributions": [asdict(r) for r in self.role_distributions],
            "export_date": datetime.now().isoformat(),
        }


# 테스트 함수
def test_advanced_sociality_simulation_system():
    """고급 사회성 시뮬레이션 시스템 테스트"""
    print("🌐 AdvancedSocialitySimulationSystem 테스트 시작...")

    simulation_system = AdvancedSocialitySimulationSystem()

    # 1. 사회적 개체 생성
    entity1 = simulation_system.create_social_entity(
        name="김협력",
        personality_traits=["외향적", "협력적", "리더십"],
        initial_trust=TrustLevel.HIGH,
        cooperation_tendency=CooperationLevel.ENTHUSIASTIC,
        preferred_role=RoleType.LEADER,
    )

    entity2 = simulation_system.create_social_entity(
        name="이신뢰",
        personality_traits=["내향적", "신중함", "분석적"],
        initial_trust=TrustLevel.MODERATE,
        cooperation_tendency=CooperationLevel.ACTIVE,
        preferred_role=RoleType.SPECIALIST,
    )

    entity3 = simulation_system.create_social_entity(
        name="박조정",
        personality_traits=["균형잡힌", "사교적", "조정능력"],
        initial_trust=TrustLevel.MODERATE,
        cooperation_tendency=CooperationLevel.ACTIVE,
        preferred_role=RoleType.MEDIATOR,
    )

    print(f"✅ 사회적 개체 생성: {len(simulation_system.social_entities)}개")

    # 2. 시뮬레이션 시나리오 생성
    scenario = simulation_system.create_simulation_scenario(
        scenario_type="협력 가능한 관계 구축",
        objectives=["상호 신뢰 형성", "역할 분담 최적화", "협력 효율성 향상"],
        participants=[entity1, entity2, entity3],
        duration_hours=2,
    )

    print(f"✅ 시뮬레이션 시나리오 생성: {scenario.scenario_type}")

    # 3. 시뮬레이션 시작
    success = simulation_system.start_social_simulation(scenario)
    print(f"✅ 시뮬레이션 시작: {'성공' if success else '실패'}")

    # 4. 사회적 상호작용 수행
    interaction1 = simulation_system.conduct_social_interaction(
        interaction_type=SocialInteractionType.TRUST_BUILDING,
        participants=[entity1.id, entity2.id],
        context="상호 신뢰 형성을 위한 대화",
        duration_minutes=30,
    )

    interaction2 = simulation_system.conduct_social_interaction(
        interaction_type=SocialInteractionType.ROLE_DISTRIBUTION,
        participants=[entity1.id, entity2.id, entity3.id],
        context="프로젝트 역할 분담 회의",
        duration_minutes=45,
    )

    interaction3 = simulation_system.conduct_social_interaction(
        interaction_type=SocialInteractionType.COOPERATION,
        participants=[entity1.id, entity2.id, entity3.id],
        context="공동 목표 달성을 위한 협력 작업",
        duration_minutes=60,
    )

    print(f"✅ 사회적 상호작용 수행: {len(simulation_system.social_interactions)}회")

    # 5. 신뢰 관계 업데이트
    for interaction in [interaction1, interaction2, interaction3]:
        if interaction:
            simulation_system.update_trust_relationships(interaction)

    print(f"✅ 신뢰 관계 업데이트: {len(simulation_system.trust_relationships)}개 관계")

    # 6. 시뮬레이션 성공도 평가
    evaluation = simulation_system.evaluate_simulation_success()
    print(f"✅ 시뮬레이션 성공도 평가: 성공률 {evaluation['success_rate']:.2f}")
    print(f"   평균 신뢰 점수: {evaluation['average_trust_score']:.2f}")
    print(f"   평균 역할 효과성: {evaluation['average_role_effectiveness']:.2f}")
    print(f"   평균 협력 점수: {evaluation['average_cooperation_score']:.2f}")
    print(f"   진화 트리거: {evaluation['evolution_triggers']}개")

    # 7. 시뮬레이션 종료
    final_result = simulation_system.end_simulation()
    print(f"✅ 시뮬레이션 종료: 최종 성공률 {final_result['success_rate']:.2f}")

    # 8. 통계
    statistics = simulation_system.get_sociality_simulation_statistics()
    print(f"✅ 사회성 시뮬레이션 통계: {statistics['total_interactions']}회 상호작용")
    print(f"   상호작용 유형별 통계: {statistics['interaction_type_statistics']}")
    print(f"   총 진화 트리거: {statistics['evolution_triggers']}개")

    # 9. 데이터 내보내기
    export_data = simulation_system.export_sociality_simulation_data()
    print(
        f"✅ 사회성 시뮬레이션 데이터 내보내기: {len(export_data['social_interactions'])}개 상호작용"
    )

    print("🎉 AdvancedSocialitySimulationSystem 테스트 완료!")


if __name__ == "__main__":
    test_advanced_sociality_simulation_system()
