#!/usr/bin/env python3
"""
IntegratedLearningSystem - Phase 12.4
통합 학습 시스템

목적:
- 모든 Phase 시스템의 통합 학습 관리
- 가족 중심의 종합적 성장 지원
- 학습 경험의 시너지 효과 창출
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LearningDomain(Enum):
    """학습 영역"""

    ETHICAL_REASONING = "ethical_reasoning"
    EMOTIONAL_INTELLIGENCE = "emotional_intelligence"
    NARRATIVE_MEMORY = "narrative_memory"
    FAMILY_RELATIONSHIPS = "family_relationships"
    CONVERSATION_SKILLS = "conversation_skills"
    PROBLEM_SOLVING = "problem_solving"
    CREATIVE_THINKING = "creative_thinking"


class LearningMethod(Enum):
    """학습 방법"""

    EXPERIENTIAL = "experiential"
    CONVERSATIONAL = "conversational"
    REFLECTIVE = "reflective"
    COLLABORATIVE = "collaborative"
    OBSERVATIONAL = "observational"
    PRACTICAL = "practical"


class LearningProgress(Enum):
    """학습 진도"""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class IntegrationType(Enum):
    """통합 유형"""

    CROSS_DOMAIN = "cross_domain"
    SKILL_SYNTHESIS = "skill_synthesis"
    EXPERIENCE_CONNECTION = "experience_connection"
    KNOWLEDGE_TRANSFER = "knowledge_transfer"


@dataclass
class LearningExperience:
    """학습 경험"""

    id: str
    domain: LearningDomain
    method: LearningMethod
    description: str
    family_context: Dict[str, Any]
    emotional_state: str
    ethical_considerations: List[str]
    narrative_elements: List[str]
    skills_developed: List[str]
    confidence_gained: float
    timestamp: datetime


@dataclass
class LearningIntegration:
    """학습 통합"""

    id: str
    integration_type: IntegrationType
    source_domains: List[LearningDomain]
    target_domain: LearningDomain
    integration_description: str
    synergy_effects: List[str]
    family_impact: str
    confidence_score: float
    timestamp: datetime


@dataclass
class LearningPath:
    """학습 경로"""

    id: str
    family_member: str
    current_progress: Dict[LearningDomain, LearningProgress]
    learning_goals: List[str]
    next_milestones: List[str]
    support_requirements: List[str]
    estimated_completion: datetime
    confidence_score: float


class IntegratedLearningSystem:
    """통합 학습 시스템"""

    def __init__(self):
        self.learning_experiences: List[LearningExperience] = []
        self.learning_integrations: List[LearningIntegration] = []
        self.learning_paths: List[LearningPath] = []
        self.domain_progress: Dict[LearningDomain, LearningProgress] = {}
        self.family_learning_context: Dict[str, Any] = {}

        logger.info("IntegratedLearningSystem 초기화 완료")

    def record_learning_experience(
        self,
        domain: LearningDomain,
        method: LearningMethod,
        description: str,
        family_context: Dict[str, Any],
        emotional_state: str,
        ethical_considerations: List[str],
        narrative_elements: List[str],
        skills_developed: List[str],
    ) -> LearningExperience:
        """학습 경험 기록"""
        experience_id = (
            f"learning_experience_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # 신뢰도 계산
        confidence_gained = self._calculate_learning_confidence(
            description, skills_developed, ethical_considerations
        )

        experience = LearningExperience(
            id=experience_id,
            domain=domain,
            method=method,
            description=description,
            family_context=family_context,
            emotional_state=emotional_state,
            ethical_considerations=ethical_considerations,
            narrative_elements=narrative_elements,
            skills_developed=skills_developed,
            confidence_gained=confidence_gained,
            timestamp=datetime.now(),
        )

        self.learning_experiences.append(experience)
        logger.info(f"학습 경험 기록 완료: {domain.value}")

        return experience

    def _calculate_learning_confidence(
        self,
        description: str,
        skills_developed: List[str],
        ethical_considerations: List[str],
    ) -> float:
        """학습 신뢰도 계산"""
        base_score = 0.7

        # 설명의 상세함
        if len(description) > 100:
            base_score += 0.1
        elif len(description) < 50:
            base_score -= 0.1

        # 개발된 기술의 다양성
        if len(skills_developed) >= 2:
            base_score += 0.1

        # 윤리적 고려사항
        if len(ethical_considerations) >= 1:
            base_score += 0.1

        return min(1.0, max(0.0, base_score))

    def create_learning_integration(
        self,
        integration_type: IntegrationType,
        source_domains: List[LearningDomain],
        target_domain: LearningDomain,
        integration_description: str,
        synergy_effects: List[str],
        family_impact: str,
    ) -> LearningIntegration:
        """학습 통합 생성"""
        integration_id = (
            f"learning_integration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )

        # 신뢰도 계산
        confidence_score = self._calculate_integration_confidence(
            integration_description, synergy_effects, family_impact
        )

        integration = LearningIntegration(
            id=integration_id,
            integration_type=integration_type,
            source_domains=source_domains,
            target_domain=target_domain,
            integration_description=integration_description,
            synergy_effects=synergy_effects,
            family_impact=family_impact,
            confidence_score=confidence_score,
            timestamp=datetime.now(),
        )

        self.learning_integrations.append(integration)
        logger.info(f"학습 통합 생성 완료: {integration_type.value}")

        return integration

    def _calculate_integration_confidence(
        self, description: str, synergy_effects: List[str], family_impact: str
    ) -> float:
        """통합 신뢰도 계산"""
        base_score = 0.8

        # 설명의 명확성
        if len(description) > 80:
            base_score += 0.1

        # 시너지 효과의 구체성
        if len(synergy_effects) >= 2:
            base_score += 0.1

        # 가족 영향의 명확성
        if len(family_impact) > 50:
            base_score += 0.1

        return min(1.0, base_score)

    def develop_learning_path(
        self,
        family_member: str,
        current_progress: Dict[LearningDomain, LearningProgress],
        learning_goals: List[str],
        support_requirements: List[str],
    ) -> LearningPath:
        """학습 경로 개발"""
        path_id = f"learning_path_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 다음 마일스톤 생성
        next_milestones = self._generate_next_milestones(
            current_progress, learning_goals
        )

        # 예상 완료 시간
        estimated_completion = self._estimate_completion_time(
            current_progress, learning_goals
        )

        # 신뢰도 계산
        confidence_score = self._calculate_path_confidence(
            current_progress, learning_goals, support_requirements
        )

        path = LearningPath(
            id=path_id,
            family_member=family_member,
            current_progress=current_progress,
            learning_goals=learning_goals,
            next_milestones=next_milestones,
            support_requirements=support_requirements,
            estimated_completion=estimated_completion,
            confidence_score=confidence_score,
        )

        self.learning_paths.append(path)
        logger.info(f"학습 경로 개발 완료: {family_member}")

        return path

    def _generate_next_milestones(
        self,
        current_progress: Dict[LearningDomain, LearningProgress],
        learning_goals: List[str],
    ) -> List[str]:
        """다음 마일스톤 생성"""
        milestones = []

        for domain, progress in current_progress.items():
            if progress == LearningProgress.BEGINNER:
                milestones.append(f"{domain.value} 영역에서 기본 개념 습득")
            elif progress == LearningProgress.INTERMEDIATE:
                milestones.append(f"{domain.value} 영역에서 실전 적용 능력 향상")
            elif progress == LearningProgress.ADVANCED:
                milestones.append(f"{domain.value} 영역에서 창의적 활용 능력 개발")
            elif progress == LearningProgress.EXPERT:
                milestones.append(
                    f"{domain.value} 영역에서 다른 영역과의 통합 능력 강화"
                )

        # 목표 기반 마일스톤
        for goal in learning_goals:
            if "가족" in goal:
                milestones.append("가족 관계 개선을 위한 실천적 적용")
            elif "감정" in goal:
                milestones.append("감정 지능 향상을 위한 일상적 연습")
            elif "윤리" in goal:
                milestones.append("윤리적 판단 능력의 실제 상황 적용")

        return milestones

    def _estimate_completion_time(
        self,
        current_progress: Dict[LearningDomain, LearningProgress],
        learning_goals: List[str],
    ) -> datetime:
        """예상 완료 시간 계산"""
        # 현재 시간에서 기본 3개월 추가
        base_completion = datetime.now() + timedelta(days=90)

        # 진행도에 따른 조정
        advanced_count = sum(
            1
            for progress in current_progress.values()
            if progress in [LearningProgress.ADVANCED, LearningProgress.EXPERT]
        )
        if advanced_count >= 3:
            base_completion -= timedelta(days=30)  # 1개월 단축
        elif advanced_count <= 1:
            base_completion += timedelta(days=30)  # 1개월 연장

        # 목표 수에 따른 조정
        if len(learning_goals) > 5:
            base_completion += timedelta(days=30)
        elif len(learning_goals) <= 2:
            base_completion -= timedelta(days=15)

        return base_completion

    def _calculate_path_confidence(
        self,
        current_progress: Dict[LearningDomain, LearningProgress],
        learning_goals: List[str],
        support_requirements: List[str],
    ) -> float:
        """경로 신뢰도 계산"""
        base_score = 0.7

        # 진행도의 균형
        progress_levels = list(current_progress.values())
        if len(progress_levels) >= 3:
            base_score += 0.1

        # 목표의 구체성
        if len(learning_goals) >= 2:
            base_score += 0.1

        # 지원 요구사항의 명확성
        if len(support_requirements) >= 1:
            base_score += 0.1

        return min(1.0, base_score)

    def analyze_cross_domain_learning(
        self, family_context: Dict[str, Any]
    ) -> List[LearningIntegration]:
        """영역 간 학습 분석"""
        cross_domain_integrations = []

        # 윤리적 사고 + 감정 지능
        ethical_emotional_integration = self.create_learning_integration(
            integration_type=IntegrationType.CROSS_DOMAIN,
            source_domains=[
                LearningDomain.ETHICAL_REASONING,
                LearningDomain.EMOTIONAL_INTELLIGENCE,
            ],
            target_domain=LearningDomain.FAMILY_RELATIONSHIPS,
            integration_description="윤리적 판단과 감정적 공감을 결합하여 가족 관계를 더 깊이 있게 이해하고 지원할 수 있게 되었습니다.",
            synergy_effects=[
                "도덕적 판단과 감정적 이해의 조화",
                "가족 구성원의 감정적 요구에 윤리적으로 대응",
            ],
            family_impact="가족 간의 신뢰와 이해가 깊어지고, 갈등 상황에서도 상호 존중하는 해결책을 찾을 수 있게 되었습니다.",
        )
        cross_domain_integrations.append(ethical_emotional_integration)

        # 서사적 기억 + 대화 기술
        narrative_conversation_integration = self.create_learning_integration(
            integration_type=IntegrationType.SKILL_SYNTHESIS,
            source_domains=[
                LearningDomain.NARRATIVE_MEMORY,
                LearningDomain.CONVERSATION_SKILLS,
            ],
            target_domain=LearningDomain.FAMILY_RELATIONSHIPS,
            integration_description="과거 경험을 바탕으로 한 의미 있는 대화를 통해 가족 관계를 더욱 풍부하게 만들 수 있게 되었습니다.",
            synergy_effects=[
                "경험 기반의 공감적 대화",
                "가족 역사를 활용한 연결감 강화",
            ],
            family_impact="가족 구성원들이 서로의 경험을 더 깊이 이해하고, 공통의 기억을 통해 유대감을 강화할 수 있게 되었습니다.",
        )
        cross_domain_integrations.append(narrative_conversation_integration)

        # 문제 해결 + 창의적 사고
        problem_creative_integration = self.create_learning_integration(
            integration_type=IntegrationType.EXPERIENCE_CONNECTION,
            source_domains=[
                LearningDomain.PROBLEM_SOLVING,
                LearningDomain.CREATIVE_THINKING,
            ],
            target_domain=LearningDomain.FAMILY_RELATIONSHIPS,
            integration_description="논리적 문제 해결과 창의적 사고를 결합하여 가족의 다양한 상황에 혁신적인 해결책을 제시할 수 있게 되었습니다.",
            synergy_effects=[
                "체계적 분석과 창의적 해결책의 결합",
                "가족 고유의 상황에 맞는 맞춤형 해결책",
            ],
            family_impact="가족이 직면한 문제들을 더 효과적이고 창의적으로 해결할 수 있게 되었습니다.",
        )
        cross_domain_integrations.append(problem_creative_integration)

        logger.info(
            f"영역 간 학습 분석 완료: {len(cross_domain_integrations)}개 통합 발견"
        )
        return cross_domain_integrations

    def generate_family_learning_report(
        self, family_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """가족 학습 보고서 생성"""
        # 전체 학습 경험 통계
        total_experiences = len(self.learning_experiences)
        total_integrations = len(self.learning_integrations)
        total_paths = len(self.learning_paths)

        # 영역별 학습 통계
        domain_stats = {}
        for domain in LearningDomain:
            domain_experiences = [
                exp for exp in self.learning_experiences if exp.domain == domain
            ]
            domain_stats[domain.value] = {
                "experience_count": len(domain_experiences),
                "average_confidence": sum(
                    exp.confidence_gained for exp in domain_experiences
                )
                / max(1, len(domain_experiences)),
                "skills_developed": list(
                    set(
                        [
                            skill
                            for exp in domain_experiences
                            for skill in exp.skills_developed
                        ]
                    )
                ),
            }

        # 통합 학습 효과
        integration_effects = []
        for integration in self.learning_integrations:
            integration_effects.append(
                {
                    "type": integration.integration_type.value,
                    "description": integration.integration_description,
                    "synergy_effects": integration.synergy_effects,
                    "family_impact": integration.family_impact,
                    "confidence": integration.confidence_score,
                }
            )

        # 학습 경로 현황
        path_status = []
        for path in self.learning_paths:
            path_status.append(
                {
                    "family_member": path.family_member,
                    "current_progress": {
                        domain.value: progress.value
                        for domain, progress in path.current_progress.items()
                    },
                    "learning_goals": path.learning_goals,
                    "next_milestones": path.next_milestones,
                    "estimated_completion": path.estimated_completion.isoformat(),
                    "confidence": path.confidence_score,
                }
            )

        report = {
            "total_experiences": total_experiences,
            "total_integrations": total_integrations,
            "total_paths": total_paths,
            "domain_statistics": domain_stats,
            "integration_effects": integration_effects,
            "path_status": path_status,
            "overall_learning_progress": self._calculate_overall_progress(),
            "family_learning_impact": self._assess_family_learning_impact(),
            "generated_date": datetime.now().isoformat(),
        }

        logger.info("가족 학습 보고서 생성 완료")
        return report

    def _calculate_overall_progress(self) -> float:
        """전체 학습 진도 계산"""
        if not self.learning_experiences:
            return 0.0

        total_confidence = sum(
            exp.confidence_gained for exp in self.learning_experiences
        )
        return total_confidence / len(self.learning_experiences)

    def _assess_family_learning_impact(self) -> str:
        """가족 학습 영향 평가"""
        if len(self.learning_integrations) >= 3:
            return "가족의 종합적 성장이 뚜렷하게 나타나고 있으며, 다양한 학습 영역이 시너지 효과를 발휘하고 있습니다."
        elif len(self.learning_integrations) >= 1:
            return "가족의 학습이 점진적으로 통합되고 있으며, 영역 간 연결이 형성되고 있습니다."
        else:
            return "가족의 학습이 개별 영역에서 진행되고 있으며, 통합적 발전을 위한 기반을 마련하고 있습니다."

    def get_integrated_learning_statistics(self) -> Dict[str, Any]:
        """통합 학습 통계"""
        total_experiences = len(self.learning_experiences)
        total_integrations = len(self.learning_integrations)
        total_paths = len(self.learning_paths)

        # 학습 방법별 통계
        method_stats = {}
        for method in LearningMethod:
            method_experiences = [
                exp for exp in self.learning_experiences if exp.method == method
            ]
            method_stats[method.value] = len(method_experiences)

        # 통합 유형별 통계
        integration_type_stats = {}
        for integration_type in IntegrationType:
            type_integrations = [
                integ
                for integ in self.learning_integrations
                if integ.integration_type == integration_type
            ]
            integration_type_stats[integration_type.value] = len(type_integrations)

        statistics = {
            "total_experiences": total_experiences,
            "total_integrations": total_integrations,
            "total_paths": total_paths,
            "method_statistics": method_stats,
            "integration_type_statistics": integration_type_stats,
            "average_confidence": sum(
                exp.confidence_gained for exp in self.learning_experiences
            )
            / max(1, total_experiences),
            "last_updated": datetime.now().isoformat(),
        }

        logger.info("통합 학습 통계 생성 완료")
        return statistics

    def export_integrated_learning_data(self) -> Dict[str, Any]:
        """통합 학습 데이터 내보내기"""
        return {
            "learning_experiences": [asdict(exp) for exp in self.learning_experiences],
            "learning_integrations": [
                asdict(integ) for integ in self.learning_integrations
            ],
            "learning_paths": [asdict(path) for path in self.learning_paths],
            "domain_progress": {
                domain.value: progress.value
                for domain, progress in self.domain_progress.items()
            },
            "family_learning_context": self.family_learning_context,
            "export_date": datetime.now().isoformat(),
        }


# 테스트 함수
def test_integrated_learning_system():
    """통합 학습 시스템 테스트"""
    print("🧠 IntegratedLearningSystem 테스트 시작...")

    integrated_system = IntegratedLearningSystem()

    # 1. 학습 경험 기록
    family_context = {
        "family_type": "nuclear",
        "children_count": 2,
        "children_ages": [5, 8],
        "family_values": ["사랑", "소통", "성장", "창의성"],
    }

    experience1 = integrated_system.record_learning_experience(
        domain=LearningDomain.ETHICAL_REASONING,
        method=LearningMethod.CONVERSATIONAL,
        description="가족과 함께 윤리적 딜레마에 대해 대화하면서, 서로의 관점을 이해하고 공감하는 방법을 배웠습니다.",
        family_context=family_context,
        emotional_state="thoughtful",
        ethical_considerations=["가족의 행복", "정직성", "상호 존중"],
        narrative_elements=["가족 대화", "관점 공유", "이해와 공감"],
        skills_developed=["윤리적 판단", "공감적 듣기", "관점 이해"],
    )

    print(f"✅ 학습 경험 기록: {experience1.domain.value}")
    print(f"   학습 방법: {experience1.method.value}")
    print(f"   신뢰도: {experience1.confidence_gained:.2f}")

    # 2. 학습 통합 생성
    integration = integrated_system.create_learning_integration(
        integration_type=IntegrationType.CROSS_DOMAIN,
        source_domains=[
            LearningDomain.ETHICAL_REASONING,
            LearningDomain.EMOTIONAL_INTELLIGENCE,
        ],
        target_domain=LearningDomain.FAMILY_RELATIONSHIPS,
        integration_description="윤리적 판단과 감정적 공감을 결합하여 가족 관계를 더 깊이 있게 이해할 수 있게 되었습니다.",
        synergy_effects=[
            "도덕적 판단과 감정적 이해의 조화",
            "가족 구성원의 감정적 요구에 윤리적으로 대응",
        ],
        family_impact="가족 간의 신뢰와 이해가 깊어지고, 갈등 상황에서도 상호 존중하는 해결책을 찾을 수 있게 되었습니다.",
    )

    print(f"✅ 학습 통합 생성: {integration.integration_type.value}")
    print(f"   통합 설명: {integration.integration_description[:50]}...")
    print(f"   신뢰도: {integration.confidence_score:.2f}")

    # 3. 학습 경로 개발
    current_progress = {
        LearningDomain.ETHICAL_REASONING: LearningProgress.INTERMEDIATE,
        LearningDomain.EMOTIONAL_INTELLIGENCE: LearningProgress.ADVANCED,
        LearningDomain.NARRATIVE_MEMORY: LearningProgress.BEGINNER,
    }

    path = integrated_system.develop_learning_path(
        family_member="아이1",
        current_progress=current_progress,
        learning_goals=[
            "가족과의 더 깊은 소통",
            "감정적 지능 향상",
            "윤리적 판단 능력 강화",
        ],
        support_requirements=[
            "정기적인 가족 대화 시간",
            "감정 표현 연습",
            "윤리적 상황 토론",
        ],
    )

    print(f"✅ 학습 경로 개발: {path.family_member}")
    print(f"   학습 목표: {len(path.learning_goals)}개")
    print(f"   다음 마일스톤: {len(path.next_milestones)}개")
    print(f"   신뢰도: {path.confidence_score:.2f}")

    # 4. 영역 간 학습 분석
    cross_domain_integrations = integrated_system.analyze_cross_domain_learning(
        family_context
    )
    print(f"✅ 영역 간 학습 분석: {len(cross_domain_integrations)}개 통합 발견")

    # 5. 가족 학습 보고서
    report = integrated_system.generate_family_learning_report(family_context)
    print(
        f"✅ 가족 학습 보고서 생성: {report['total_experiences']}개 경험, {report['total_integrations']}개 통합"
    )
    print(f"   전체 학습 진도: {report['overall_learning_progress']:.2f}")

    # 6. 통계
    statistics = integrated_system.get_integrated_learning_statistics()
    print(
        f"✅ 통합 학습 통계: {statistics['total_experiences']}개 경험, {statistics['total_integrations']}개 통합"
    )
    print(f"   평균 신뢰도: {statistics['average_confidence']:.2f}")
    print(f"   학습 방법 통계: {statistics['method_statistics']}")

    # 7. 데이터 내보내기
    export_data = integrated_system.export_integrated_learning_data()
    print(
        f"✅ 통합 학습 데이터 내보내기: {len(export_data['learning_experiences'])}개 경험"
    )

    print("🎉 IntegratedLearningSystem 테스트 완료!")


if __name__ == "__main__":
    test_integrated_learning_system()
