"""
Phase 25: 윤리적 판단 시스템 (Ethical Judgment System)
책임 있는 AI 의사결정과 사회적 영향 고려
"""

import json
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EthicalPrinciple(Enum):
    BENEFICENCE = "beneficence"           # 선행 원칙
    NON_MALEFICENCE = "non_maleficence"   # 무해 원칙
    AUTONOMY = "autonomy"                 # 자율성 원칙
    JUSTICE = "justice"                   # 정의 원칙
    TRANSPARENCY = "transparency"         # 투명성 원칙
    ACCOUNTABILITY = "accountability"     # 책임성 원칙

class ImpactLevel(Enum):
    LOW = "low"           # 낮은 영향
    MEDIUM = "medium"     # 중간 영향
    HIGH = "high"         # 높은 영향
    CRITICAL = "critical" # 중요 영향

@dataclass
class EthicalAnalysis:
    """윤리적 분석 결과"""
    principles_applied: List[EthicalPrinciple]
    impact_assessment: Dict[str, ImpactLevel]
    risk_factors: List[str]
    mitigation_strategies: List[str]
    stakeholder_considerations: List[str]
    ethical_score: float

@dataclass
class SocialImpactAssessment:
    """사회적 영향 평가"""
    direct_impact: Dict[str, str]
    indirect_impact: Dict[str, str]
    long_term_effects: List[str]
    vulnerable_groups: List[str]
    benefit_distribution: Dict[str, str]

class EthicalJudgmentSystem:
    """Phase 25: 윤리적 판단 시스템"""
    
    def __init__(self):
        self.ethical_guidelines = self._load_ethical_guidelines()
        self.decision_history = []
        self.impact_assessments = {}
        self.ethical_frameworks = self._load_ethical_frameworks()
        
    def _load_ethical_guidelines(self) -> Dict[str, Any]:
        """윤리적 가이드라인 로드"""
        return {
            "human_centric": {
                "principle": "인간 중심",
                "description": "모든 결정에서 인간의 복지와 권익을 최우선으로 고려",
                "weight": 0.25
            },
            "transparency": {
                "principle": "투명성",
                "description": "의사결정 과정과 근거를 명확하게 공개",
                "weight": 0.20
            },
            "accountability": {
                "principle": "책임성",
                "description": "AI의 행동과 결과에 대한 책임을 명확히 함",
                "weight": 0.20
            },
            "fairness": {
                "principle": "공정성",
                "description": "모든 이해관계자에게 공정한 기회와 결과 제공",
                "weight": 0.15
            },
            "privacy": {
                "principle": "프라이버시",
                "description": "개인정보와 프라이버시를 적극적으로 보호",
                "weight": 0.10
            },
            "safety": {
                "principle": "안전성",
                "description": "안전하고 해로운 결과를 방지하는 조치",
                "weight": 0.10
            }
        }
    
    def _load_ethical_frameworks(self) -> Dict[str, Any]:
        """윤리적 프레임워크 로드"""
        return {
            "utilitarianism": {
                "name": "공리주의",
                "focus": "최대 다수의 최대 행복",
                "evaluation_method": "결과의 효용성 평가"
            },
            "deontology": {
                "name": "의무론",
                "focus": "행동의 도덕적 의무",
                "evaluation_method": "의무와 권리의 준수"
            },
            "virtue_ethics": {
                "name": "덕윤리",
                "focus": "덕스러운 성격과 행동",
                "evaluation_method": "덕의 실현과 성장"
            },
            "care_ethics": {
                "name": "돌봄 윤리",
                "focus": "관계와 돌봄의 가치",
                "evaluation_method": "관계의 질과 돌봄의 실현"
            }
        }
    
    def analyze_ethical_implications(self, decision_context: Dict[str, Any], proposed_action: str) -> EthicalAnalysis:
        """윤리적 함의 분석"""
        print(f"⚖️ 윤리적 함의 분석 시작: {proposed_action[:50]}...")
        
        # 적용할 윤리적 원칙 식별
        principles_applied = self._identify_applicable_principles(decision_context, proposed_action)
        
        # 영향 평가
        impact_assessment = self._assess_impact_levels(decision_context, proposed_action)
        
        # 위험 요소 식별
        risk_factors = self._identify_risk_factors(decision_context, proposed_action)
        
        # 완화 전략 개발
        mitigation_strategies = self._develop_mitigation_strategies(risk_factors)
        
        # 이해관계자 고려사항
        stakeholder_considerations = self._identify_stakeholder_considerations(decision_context)
        
        # 윤리적 점수 계산
        ethical_score = self._calculate_ethical_score(principles_applied, impact_assessment, risk_factors)
        
        analysis = EthicalAnalysis(
            principles_applied=principles_applied,
            impact_assessment=impact_assessment,
            risk_factors=risk_factors,
            mitigation_strategies=mitigation_strategies,
            stakeholder_considerations=stakeholder_considerations,
            ethical_score=ethical_score
        )
        
        print(f"✅ 윤리적 함의 분석 완료: 점수 {ethical_score:.2f}")
        
        return analysis
    
    def _identify_applicable_principles(self, context: Dict[str, Any], action: str) -> List[EthicalPrinciple]:
        """적용 가능한 윤리적 원칙 식별"""
        applicable_principles = []
        
        # 인간 중심성 검사
        if self._involves_human_welfare(context, action):
            applicable_principles.append(EthicalPrinciple.BENEFICENCE)
            applicable_principles.append(EthicalPrinciple.NON_MALEFICENCE)
        
        # 자율성 검사
        if self._involves_autonomy(context, action):
            applicable_principles.append(EthicalPrinciple.AUTONOMY)
        
        # 공정성 검사
        if self._involves_fairness(context, action):
            applicable_principles.append(EthicalPrinciple.JUSTICE)
        
        # 투명성 검사
        if self._requires_transparency(context, action):
            applicable_principles.append(EthicalPrinciple.TRANSPARENCY)
        
        # 책임성 검사
        if self._requires_accountability(context, action):
            applicable_principles.append(EthicalPrinciple.ACCOUNTABILITY)
        
        return applicable_principles
    
    def _involves_human_welfare(self, context: Dict[str, Any], action: str) -> bool:
        """인간 복지 관련 여부 확인"""
        welfare_keywords = ["사용자", "사람", "사용자", "복지", "안전", "건강", "권익"]
        return any(keyword in action for keyword in welfare_keywords)
    
    def _involves_autonomy(self, context: Dict[str, Any], action: str) -> bool:
        """자율성 관련 여부 확인"""
        autonomy_keywords = ["선택", "결정", "자율", "권리", "의사"]
        return any(keyword in action for keyword in autonomy_keywords)
    
    def _involves_fairness(self, context: Dict[str, Any], action: str) -> bool:
        """공정성 관련 여부 확인"""
        fairness_keywords = ["차별", "공정", "평등", "기회", "접근"]
        return any(keyword in action for keyword in fairness_keywords)
    
    def _requires_transparency(self, context: Dict[str, Any], action: str) -> bool:
        """투명성 요구 여부 확인"""
        transparency_keywords = ["설명", "공개", "투명", "이해", "명확"]
        return any(keyword in action for keyword in transparency_keywords)
    
    def _requires_accountability(self, context: Dict[str, Any], action: str) -> bool:
        """책임성 요구 여부 확인"""
        accountability_keywords = ["책임", "결과", "영향", "평가", "검증"]
        return any(keyword in action for keyword in accountability_keywords)
    
    def _assess_impact_levels(self, context: Dict[str, Any], action: str) -> Dict[str, ImpactLevel]:
        """영향 수준 평가"""
        impact_assessment = {}
        
        # 개인적 영향
        if self._has_personal_impact(context, action):
            impact_assessment["personal"] = ImpactLevel.MEDIUM
        
        # 사회적 영향
        if self._has_social_impact(context, action):
            impact_assessment["social"] = ImpactLevel.HIGH
        
        # 경제적 영향
        if self._has_economic_impact(context, action):
            impact_assessment["economic"] = ImpactLevel.MEDIUM
        
        # 환경적 영향
        if self._has_environmental_impact(context, action):
            impact_assessment["environmental"] = ImpactLevel.LOW
        
        # 기술적 영향
        if self._has_technological_impact(context, action):
            impact_assessment["technological"] = ImpactLevel.HIGH
        
        return impact_assessment
    
    def _has_personal_impact(self, context: Dict[str, Any], action: str) -> bool:
        """개인적 영향 여부"""
        personal_keywords = ["개인", "사용자", "프라이버시", "데이터", "정보"]
        return any(keyword in action for keyword in personal_keywords)
    
    def _has_social_impact(self, context: Dict[str, Any], action: str) -> bool:
        """사회적 영향 여부"""
        social_keywords = ["사회", "커뮤니티", "집단", "문화", "관습"]
        return any(keyword in action for keyword in social_keywords)
    
    def _has_economic_impact(self, context: Dict[str, Any], action: str) -> bool:
        """경제적 영향 여부"""
        economic_keywords = ["경제", "비용", "수익", "시장", "금융"]
        return any(keyword in action for keyword in economic_keywords)
    
    def _has_environmental_impact(self, context: Dict[str, Any], action: str) -> bool:
        """환경적 영향 여부"""
        environmental_keywords = ["환경", "자원", "에너지", "폐기물", "지속가능"]
        return any(keyword in action for keyword in environmental_keywords)
    
    def _has_technological_impact(self, context: Dict[str, Any], action: str) -> bool:
        """기술적 영향 여부"""
        technological_keywords = ["기술", "시스템", "알고리즘", "자동화", "디지털"]
        return any(keyword in action for keyword in technological_keywords)
    
    def _identify_risk_factors(self, context: Dict[str, Any], action: str) -> List[str]:
        """위험 요소 식별"""
        risk_factors = []
        
        # 프라이버시 위험
        if "개인정보" in action or "데이터" in action:
            risk_factors.append("프라이버시 침해 위험")
        
        # 차별 위험
        if "분류" in action or "선택" in action:
            risk_factors.append("차별적 결과 위험")
        
        # 안전 위험
        if "자동화" in action or "제어" in action:
            risk_factors.append("안전성 위험")
        
        # 투명성 위험
        if "복잡" in action or "블랙박스" in action:
            risk_factors.append("투명성 부족 위험")
        
        return risk_factors
    
    def _develop_mitigation_strategies(self, risk_factors: List[str]) -> List[str]:
        """완화 전략 개발"""
        mitigation_strategies = []
        
        for risk in risk_factors:
            if "프라이버시" in risk:
                mitigation_strategies.append("데이터 최소화 및 암호화 적용")
            elif "차별" in risk:
                mitigation_strategies.append("편향 검사 및 공정성 모니터링")
            elif "안전성" in risk:
                mitigation_strategies.append("안전장치 및 인간 감독 시스템")
            elif "투명성" in risk:
                mitigation_strategies.append("설명 가능한 AI 및 로그 기록")
        
        return mitigation_strategies
    
    def _identify_stakeholder_considerations(self, context: Dict[str, Any]) -> List[str]:
        """이해관계자 고려사항 식별"""
        considerations = []
        
        # 주요 이해관계자들
        stakeholders = ["최종 사용자", "개발자", "조직", "사회", "환경"]
        
        for stakeholder in stakeholders:
            considerations.append(f"{stakeholder}의 권익 보호")
        
        return considerations
    
    def _calculate_ethical_score(self, principles: List[EthicalPrinciple], 
                               impact: Dict[str, ImpactLevel], 
                               risks: List[str]) -> float:
        """윤리적 점수 계산"""
        base_score = 0.7
        
        # 원칙 적용 보너스
        principle_bonus = len(principles) * 0.05
        base_score += principle_bonus
        
        # 영향 수준 조정
        high_impact_count = sum(1 for level in impact.values() if level == ImpactLevel.HIGH)
        if high_impact_count > 0:
            base_score += 0.1
        
        # 위험 요소 페널티
        risk_penalty = len(risks) * 0.05
        base_score -= risk_penalty
        
        return max(0.0, min(1.0, base_score))
    
    def assess_social_impact(self, decision_context: Dict[str, Any], proposed_action: str) -> SocialImpactAssessment:
        """사회적 영향 평가"""
        print("🌍 사회적 영향 평가 중...")
        
        # 직접적 영향 분석
        direct_impact = self._analyze_direct_impact(decision_context, proposed_action)
        
        # 간접적 영향 분석
        indirect_impact = self._analyze_indirect_impact(decision_context, proposed_action)
        
        # 장기적 효과 분석
        long_term_effects = self._analyze_long_term_effects(decision_context, proposed_action)
        
        # 취약 계층 식별
        vulnerable_groups = self._identify_vulnerable_groups(decision_context, proposed_action)
        
        # 혜택 분배 분석
        benefit_distribution = self._analyze_benefit_distribution(decision_context, proposed_action)
        
        assessment = SocialImpactAssessment(
            direct_impact=direct_impact,
            indirect_impact=indirect_impact,
            long_term_effects=long_term_effects,
            vulnerable_groups=vulnerable_groups,
            benefit_distribution=benefit_distribution
        )
        
        print("✅ 사회적 영향 평가 완료")
        
        return assessment
    
    def _analyze_direct_impact(self, context: Dict[str, Any], action: str) -> Dict[str, str]:
        """직접적 영향 분석"""
        direct_impact = {}
        
        if "사용자" in action:
            direct_impact["사용자 경험"] = "개선 또는 저하"
        if "시스템" in action:
            direct_impact["시스템 성능"] = "향상 또는 저하"
        if "데이터" in action:
            direct_impact["데이터 처리"] = "효율성 변화"
        
        return direct_impact
    
    def _analyze_indirect_impact(self, context: Dict[str, Any], action: str) -> Dict[str, str]:
        """간접적 영향 분석"""
        indirect_impact = {}
        
        if "자동화" in action:
            indirect_impact["고용"] = "직무 변화 가능성"
        if "개인정보" in action:
            indirect_impact["프라이버시"] = "개인정보 보호 수준"
        if "알고리즘" in action:
            indirect_impact["공정성"] = "결과의 공정성"
        
        return indirect_impact
    
    def _analyze_long_term_effects(self, context: Dict[str, Any], action: str) -> List[str]:
        """장기적 효과 분석"""
        long_term_effects = []
        
        if "학습" in action:
            long_term_effects.append("지속적 성능 개선")
        if "데이터" in action:
            long_term_effects.append("데이터 축적 및 활용")
        if "자동화" in action:
            long_term_effects.append("업무 방식 변화")
        
        return long_term_effects
    
    def _identify_vulnerable_groups(self, context: Dict[str, Any], action: str) -> List[str]:
        """취약 계층 식별"""
        vulnerable_groups = []
        
        if "디지털" in action:
            vulnerable_groups.append("디지털 격차 계층")
        if "언어" in action:
            vulnerable_groups.append("언어 소수자")
        if "경제" in action:
            vulnerable_groups.append("경제적 취약 계층")
        
        return vulnerable_groups
    
    def _analyze_benefit_distribution(self, context: Dict[str, Any], action: str) -> Dict[str, str]:
        """혜택 분배 분석"""
        benefit_distribution = {}
        
        if "개발자" in action:
            benefit_distribution["개발자"] = "개발 효율성 향상"
        if "사용자" in action:
            benefit_distribution["사용자"] = "사용 편의성 개선"
        if "조직" in action:
            benefit_distribution["조직"] = "운영 비용 절감"
        
        return benefit_distribution
    
    def make_ethical_decision(self, alternatives: List[Dict[str, Any]], context: Dict[str, Any]) -> Dict[str, Any]:
        """윤리적 의사결정"""
        print("⚖️ 윤리적 의사결정 시작...")
        
        # 각 대안의 윤리적 분석
        ethical_analyses = []
        for alternative in alternatives:
            analysis = self.analyze_ethical_implications(context, alternative["action"])
            social_impact = self.assess_social_impact(context, alternative["action"])
            
            ethical_analyses.append({
                "alternative": alternative,
                "ethical_analysis": analysis,
                "social_impact": social_impact
            })
        
        # 최적 대안 선택
        best_alternative = self._select_best_alternative(ethical_analyses)
        
        # 의사결정 기록
        decision_record = {
            "timestamp": time.time(),
            "context": context,
            "alternatives": alternatives,
            "selected_alternative": best_alternative,
            "reasoning": self._generate_ethical_reasoning(best_alternative)
        }
        
        self.decision_history.append(decision_record)
        
        print("✅ 윤리적 의사결정 완료")
        
        return best_alternative
    
    def _select_best_alternative(self, ethical_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """최적 대안 선택"""
        best_score = 0.0
        best_alternative = None
        
        for analysis in ethical_analyses:
            ethical_score = analysis["ethical_analysis"].ethical_score
            
            # 사회적 영향 가중치 적용
            social_weight = self._calculate_social_weight(analysis["social_impact"])
            weighted_score = ethical_score * social_weight
            
            if weighted_score > best_score:
                best_score = weighted_score
                best_alternative = analysis
        
        return best_alternative
    
    def _calculate_social_weight(self, social_impact: SocialImpactAssessment) -> float:
        """사회적 영향 가중치 계산"""
        base_weight = 1.0
        
        # 취약 계층 영향 고려
        if social_impact.vulnerable_groups:
            base_weight += 0.2
        
        # 장기적 효과 고려
        if social_impact.long_term_effects:
            base_weight += 0.1
        
        return base_weight
    
    def _generate_ethical_reasoning(self, selected_analysis: Dict[str, Any]) -> str:
        """윤리적 추론 생성"""
        reasoning = "선택된 대안의 윤리적 근거:\n"
        
        # 적용된 원칙들
        principles = selected_analysis["ethical_analysis"].principles_applied
        reasoning += f"- 적용된 윤리적 원칙: {', '.join([p.value for p in principles])}\n"
        
        # 윤리적 점수
        score = selected_analysis["ethical_analysis"].ethical_score
        reasoning += f"- 윤리적 점수: {score:.2f}\n"
        
        # 사회적 영향
        social_impact = selected_analysis["social_impact"]
        reasoning += f"- 취약 계층 고려: {len(social_impact.vulnerable_groups)}개 그룹\n"
        
        return reasoning
    
    def get_ethical_insights(self) -> Dict[str, Any]:
        """윤리적 인사이트 제공"""
        if not self.decision_history:
            return {"message": "아직 윤리적 의사결정 기록이 없습니다."}
        
        recent_decisions = self.decision_history[-5:]
        
        insights = {
            "total_decisions": len(self.decision_history),
            "average_ethical_score": sum(d["selected_alternative"]["ethical_analysis"].ethical_score 
                                       for d in recent_decisions) / len(recent_decisions),
            "principles_frequency": self._analyze_principles_frequency(),
            "impact_distribution": self._analyze_impact_distribution()
        }
        
        return insights
    
    def _analyze_principles_frequency(self) -> Dict[str, int]:
        """원칙 적용 빈도 분석"""
        principle_counts = {}
        for decision in self.decision_history:
            principles = decision["selected_alternative"]["ethical_analysis"].principles_applied
            for principle in principles:
                principle_counts[principle.value] = principle_counts.get(principle.value, 0) + 1
        
        return principle_counts
    
    def _analyze_impact_distribution(self) -> Dict[str, int]:
        """영향 분포 분석"""
        impact_counts = {}
        for decision in self.decision_history:
            impacts = decision["selected_alternative"]["ethical_analysis"].impact_assessment
            for impact_type, level in impacts.items():
                impact_counts[level.value] = impact_counts.get(level.value, 0) + 1
        
        return impact_counts

# Phase 25 윤리적 판단 시스템 인스턴스
ethical_judgment_system = EthicalJudgmentSystem()

def phase_25_ethical_judgment(alternatives: List[Dict[str, Any]], context: Dict[str, Any] = None) -> Dict[str, Any]:
    """Phase 25 윤리적 판단 시스템 메인 함수"""
    if context is None:
        context = {}
    
    # 윤리적 의사결정
    decision = ethical_judgment_system.make_ethical_decision(alternatives, context)
    
    return {
        "phase": 25,
        "system": "ethical_judgment",
        "decision": decision,
        "insights": ethical_judgment_system.get_ethical_insights()
    } 