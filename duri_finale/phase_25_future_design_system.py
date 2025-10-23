"""
Phase 25: 미래 예측 및 설계 시스템 (Future Design System)
트렌드 분석, 장기적 시나리오 구축, 혁신적 아이디어 생성
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class TrendCategory(Enum):
    TECHNOLOGICAL = "technological"  # 기술적 트렌드
    SOCIAL = "social"  # 사회적 트렌드
    ECONOMIC = "economic"  # 경제적 트렌드
    ENVIRONMENTAL = "environmental"  # 환경적 트렌드
    POLITICAL = "political"  # 정치적 트렌드


class ScenarioType(Enum):
    OPTIMISTIC = "optimistic"  # 낙관적 시나리오
    PESSIMISTIC = "pessimistic"  # 비관적 시나리오
    REALISTIC = "realistic"  # 현실적 시나리오
    DISRUPTIVE = "disruptive"  # 파괴적 시나리오


@dataclass
class TrendAnalysis:
    """트렌드 분석 결과"""

    category: TrendCategory
    trend_name: str
    description: str
    impact_level: float
    confidence: float
    time_horizon: str
    key_factors: List[str]
    implications: List[str]


@dataclass
class FutureScenario:
    """미래 시나리오"""

    scenario_type: ScenarioType
    title: str
    description: str
    time_frame: str
    key_events: List[str]
    probability: float
    impact_assessment: Dict[str, str]
    adaptation_strategies: List[str]


@dataclass
class InnovationIdea:
    """혁신 아이디어"""

    title: str
    description: str
    category: str
    novelty_score: float
    feasibility_score: float
    impact_potential: float
    implementation_steps: List[str]
    risk_factors: List[str]


class FutureDesignSystem:
    """Phase 25: 미래 예측 및 설계 시스템"""

    def __init__(self):
        self.trend_database = self._load_trend_database()
        self.scenario_templates = self._load_scenario_templates()
        self.innovation_patterns = self._load_innovation_patterns()
        self.analysis_history = []

    def _load_trend_database(self) -> Dict[str, Any]:
        """트렌드 데이터베이스 로드"""
        return {
            "technological": {
                "ai_advancement": {
                    "name": "AI 기술 고도화",
                    "description": "머신러닝, 딥러닝 기술의 지속적 발전",
                    "impact": 0.9,
                    "confidence": 0.85,
                    "time_horizon": "5-10년",
                    "key_factors": ["컴퓨팅 파워", "데이터 품질", "알고리즘 개선"],
                    "implications": ["자동화 확대", "새로운 직무 창출", "생산성 향상"],
                },
                "quantum_computing": {
                    "name": "양자 컴퓨팅 상용화",
                    "description": "양자 컴퓨팅의 실용적 응용 확대",
                    "impact": 0.8,
                    "confidence": 0.7,
                    "time_horizon": "10-15년",
                    "key_factors": [
                        "양자 우위 달성",
                        "알고리즘 개발",
                        "하드웨어 안정성",
                    ],
                    "implications": [
                        "암호화 변화",
                        "복잡한 시뮬레이션",
                        "최적화 문제 해결",
                    ],
                },
            },
            "social": {
                "remote_work": {
                    "name": "원격 근무 정착",
                    "description": "원격 근무가 새로운 표준으로 자리잡음",
                    "impact": 0.8,
                    "confidence": 0.9,
                    "time_horizon": "3-5년",
                    "key_factors": ["기술 인프라", "문화 변화", "정책 지원"],
                    "implications": [
                        "오피스 공간 변화",
                        "워라밸 향상",
                        "글로벌 인재 채용",
                    ],
                },
                "aging_population": {
                    "name": "고령화 사회 심화",
                    "description": "인구 고령화로 인한 사회 구조 변화",
                    "impact": 0.9,
                    "confidence": 0.95,
                    "time_horizon": "10-20년",
                    "key_factors": ["출산율 감소", "의료 기술 발전", "정책 대응"],
                    "implications": [
                        "노동력 부족",
                        "의료 서비스 확대",
                        "실버 산업 성장",
                    ],
                },
            },
            "economic": {
                "digital_currency": {
                    "name": "디지털 화폐 확산",
                    "description": "중앙은행 디지털 화폐(CBDC) 및 암호화폐 확산",
                    "impact": 0.7,
                    "confidence": 0.8,
                    "time_horizon": "5-10년",
                    "key_factors": ["정부 정책", "기술 발전", "사용자 수용도"],
                    "implications": [
                        "금융 시스템 변화",
                        "결제 방식 혁신",
                        "금융 포용성 향상",
                    ],
                }
            },
            "environmental": {
                "climate_action": {
                    "name": "기후 변화 대응 강화",
                    "description": "탄소 중립 및 지속가능 발전 정책 확대",
                    "impact": 0.9,
                    "confidence": 0.9,
                    "time_horizon": "10-20년",
                    "key_factors": ["국제 협약", "기술 발전", "정치적 의지"],
                    "implications": ["에너지 전환", "그린 기술 투자", "기업 ESG 경영"],
                }
            },
        }

    def _load_scenario_templates(self) -> Dict[str, Any]:
        """시나리오 템플릿 로드"""
        return {
            "optimistic": {
                "name": "낙관적 시나리오",
                "characteristics": ["기술 혁신", "사회적 협력", "지속가능한 성장"],
                "probability": 0.3,
                "key_factors": ["긍정적 정책", "기술적 돌파구", "사회적 합의"],
            },
            "pessimistic": {
                "name": "비관적 시나리오",
                "characteristics": ["기술적 위험", "사회적 갈등", "환경적 위기"],
                "probability": 0.2,
                "key_factors": ["정책 실패", "기술적 사고", "자원 고갈"],
            },
            "realistic": {
                "name": "현실적 시나리오",
                "characteristics": ["점진적 개선", "부분적 혁신", "균형적 발전"],
                "probability": 0.4,
                "key_factors": ["정책적 조정", "기술적 진화", "사회적 적응"],
            },
            "disruptive": {
                "name": "파괴적 시나리오",
                "characteristics": ["급격한 변화", "기존 질서 붕괴", "새로운 패러다임"],
                "probability": 0.1,
                "key_factors": ["기술적 돌파구", "사회적 혼란", "정치적 변화"],
            },
        }

    def _load_innovation_patterns(self) -> Dict[str, Any]:
        """혁신 패턴 로드"""
        return {
            "convergence": {
                "name": "융합 혁신",
                "description": "서로 다른 기술이나 분야의 결합",
                "examples": ["바이오-IT 융합", "AI-로봇 융합", "디지털-물리적 융합"],
            },
            "disruption": {
                "name": "파괴적 혁신",
                "description": "기존 시장을 완전히 바꾸는 새로운 접근법",
                "examples": ["스마트폰", "스트리밍 서비스", "전기차"],
            },
            "incremental": {
                "name": "점진적 혁신",
                "description": "기존 제품이나 서비스의 지속적 개선",
                "examples": ["성능 향상", "사용자 경험 개선", "비용 절감"],
            },
            "radical": {
                "name": "근본적 혁신",
                "description": "완전히 새로운 개념이나 기술",
                "examples": ["양자 컴퓨팅", "뇌-컴퓨터 인터페이스", "합성 생물학"],
            },
        }

    def analyze_trends(self, domain: str = None, time_horizon: str = "5-10년") -> List[TrendAnalysis]:
        """트렌드 분석"""
        print(f"📈 트렌드 분석 시작: {domain or '전체 도메인'}")

        trends = []

        if domain:
            # 특정 도메인 트렌드 분석
            if domain in self.trend_database:
                for trend_id, trend_data in self.trend_database[domain].items():
                    if trend_data["time_horizon"] == time_horizon:
                        trend = TrendAnalysis(
                            category=TrendCategory(domain),
                            trend_name=trend_data["name"],
                            description=trend_data["description"],
                            impact_level=trend_data["impact"],
                            confidence=trend_data["confidence"],
                            time_horizon=trend_data["time_horizon"],
                            key_factors=trend_data["key_factors"],
                            implications=trend_data["implications"],
                        )
                        trends.append(trend)
        else:
            # 전체 도메인 트렌드 분석
            for domain_name, domain_trends in self.trend_database.items():
                for trend_id, trend_data in domain_trends.items():
                    if trend_data["time_horizon"] == time_horizon:
                        trend = TrendAnalysis(
                            category=TrendCategory(domain_name),
                            trend_name=trend_data["name"],
                            description=trend_data["description"],
                            impact_level=trend_data["impact"],
                            confidence=trend_data["confidence"],
                            time_horizon=trend_data["time_horizon"],
                            key_factors=trend_data["key_factors"],
                            implications=trend_data["implications"],
                        )
                        trends.append(trend)

        # 영향도 순으로 정렬
        trends.sort(key=lambda x: x.impact_level, reverse=True)

        print(f"✅ 트렌드 분석 완료: {len(trends)}개 트렌드 발견")

        return trends

    def generate_future_scenarios(
        self, trends: List[TrendAnalysis], scenario_type: ScenarioType = None
    ) -> List[FutureScenario]:
        """미래 시나리오 생성"""
        print("🔮 미래 시나리오 생성 중...")

        scenarios = []

        if scenario_type:
            # 특정 시나리오 타입 생성
            scenarios.append(self._create_scenario(trends, scenario_type))
        else:
            # 모든 시나리오 타입 생성
            for scenario_type_enum in ScenarioType:
                scenario = self._create_scenario(trends, scenario_type_enum)
                scenarios.append(scenario)

        print(f"✅ 미래 시나리오 생성 완료: {len(scenarios)}개 시나리오")

        return scenarios

    def _create_scenario(self, trends: List[TrendAnalysis], scenario_type: ScenarioType) -> FutureScenario:
        """시나리오 생성"""
        template = self.scenario_templates[scenario_type.value]

        # 시나리오 제목 생성
        title = f"{template['name']}: {self._generate_scenario_title(trends, scenario_type)}"

        # 시나리오 설명 생성
        description = self._generate_scenario_description(trends, scenario_type)

        # 주요 이벤트 생성
        key_events = self._generate_key_events(trends, scenario_type)

        # 영향 평가
        impact_assessment = self._assess_scenario_impact(trends, scenario_type)

        # 적응 전략 생성
        adaptation_strategies = self._generate_adaptation_strategies(trends, scenario_type)

        scenario = FutureScenario(
            scenario_type=scenario_type,
            title=title,
            description=description,
            time_frame="10-20년",
            key_events=key_events,
            probability=template["probability"],
            impact_assessment=impact_assessment,
            adaptation_strategies=adaptation_strategies,
        )

        return scenario

    def _generate_scenario_title(self, trends: List[TrendAnalysis], scenario_type: ScenarioType) -> str:
        """시나리오 제목 생성"""
        if scenario_type == ScenarioType.OPTIMISTIC:
            return "기술 혁신과 사회적 협력의 황금기"
        elif scenario_type == ScenarioType.PESSIMISTIC:
            return "기술적 위험과 사회적 갈등의 시대"
        elif scenario_type == ScenarioType.REALISTIC:
            return "점진적 개선과 균형적 발전의 시대"
        else:  # DISRUPTIVE
            return "급격한 변화와 새로운 패러다임의 시대"

    def _generate_scenario_description(self, trends: List[TrendAnalysis], scenario_type: ScenarioType) -> str:
        """시나리오 설명 생성"""
        if scenario_type == ScenarioType.OPTIMISTIC:
            return "기술 혁신이 사회적 문제를 해결하고, 인간과 AI의 협력이 새로운 가치를 창조하는 낙관적인 미래"
        elif scenario_type == ScenarioType.PESSIMISTIC:
            return "기술적 위험과 사회적 갈등이 심화되어 불안정한 미래가 실현되는 비관적인 시나리오"
        elif scenario_type == ScenarioType.REALISTIC:
            return "기술과 사회가 점진적으로 발전하면서 균형을 찾아가는 현실적인 미래"
        else:  # DISRUPTIVE
            return "기존 질서가 완전히 바뀌고 새로운 패러다임이 등장하는 파괴적 변화의 시대"

    def _generate_key_events(self, trends: List[TrendAnalysis], scenario_type: ScenarioType) -> List[str]:
        """주요 이벤트 생성"""
        events = []

        for trend in trends[:3]:  # 상위 3개 트렌드만 사용
            if scenario_type == ScenarioType.OPTIMISTIC:
                events.append(f"{trend.trend_name}의 긍정적 발전과 사회적 혜택 확산")
            elif scenario_type == ScenarioType.PESSIMISTIC:
                events.append(f"{trend.trend_name}의 부정적 영향과 사회적 갈등 발생")
            elif scenario_type == ScenarioType.REALISTIC:
                events.append(f"{trend.trend_name}의 점진적 발전과 사회적 적응")
            else:  # DISRUPTIVE
                events.append(f"{trend.trend_name}의 급격한 변화와 기존 질서 붕괴")

        return events

    def _assess_scenario_impact(self, trends: List[TrendAnalysis], scenario_type: ScenarioType) -> Dict[str, str]:
        """시나리오 영향 평가"""
        impact = {}

        if scenario_type == ScenarioType.OPTIMISTIC:
            impact["경제"] = "지속적 성장과 새로운 산업 창출"
            impact["사회"] = "사회적 협력과 삶의 질 향상"
            impact["기술"] = "혁신적 기술 발전과 인간-AI 협력"
        elif scenario_type == ScenarioType.PESSIMISTIC:
            impact["경제"] = "경제적 불안정과 실업 증가"
            impact["사회"] = "사회적 갈등과 불평등 심화"
            impact["기술"] = "기술적 위험과 프라이버시 침해"
        elif scenario_type == ScenarioType.REALISTIC:
            impact["경제"] = "안정적 성장과 점진적 개선"
            impact["사회"] = "사회적 적응과 부분적 개선"
            impact["기술"] = "기술적 진화와 사회적 수용"
        else:  # DISRUPTIVE
            impact["경제"] = "급격한 변화와 새로운 경제 구조"
            impact["사회"] = "사회적 혼란과 새로운 가치관"
            impact["기술"] = "파괴적 혁신과 새로운 패러다임"

        return impact

    def _generate_adaptation_strategies(self, trends: List[TrendAnalysis], scenario_type: ScenarioType) -> List[str]:
        """적응 전략 생성"""
        strategies = []

        if scenario_type == ScenarioType.OPTIMISTIC:
            strategies.extend(
                [
                    "기술 혁신 투자 확대",
                    "인간-AI 협력 모델 개발",
                    "사회적 혜택 극대화 정책",
                ]
            )
        elif scenario_type == ScenarioType.PESSIMISTIC:
            strategies.extend(
                [
                    "위험 관리 및 안전장치 강화",
                    "사회적 안전망 구축",
                    "윤리적 가이드라인 엄격 적용",
                ]
            )
        elif scenario_type == ScenarioType.REALISTIC:
            strategies.extend(["점진적 기술 도입", "사회적 합의 도출", "균형적 발전 정책"])
        else:  # DISRUPTIVE
            strategies.extend(
                [
                    "유연한 조직 구조 구축",
                    "빠른 적응 능력 개발",
                    "새로운 기회 포착 전략",
                ]
            )

        return strategies

    def generate_innovation_ideas(self, trends: List[TrendAnalysis], domain: str = None) -> List[InnovationIdea]:
        """혁신 아이디어 생성"""
        print("💡 혁신 아이디어 생성 중...")

        ideas = []

        # 트렌드 기반 아이디어 생성
        for trend in trends[:5]:  # 상위 5개 트렌드 사용
            idea = self._create_innovation_idea(trend, domain)
            ideas.append(idea)

        # 패턴 기반 아이디어 생성
        for pattern_name, pattern_data in self.innovation_patterns.items():
            idea = self._create_pattern_based_idea(pattern_data, trends)
            ideas.append(idea)

        # 점수 순으로 정렬
        ideas.sort(
            key=lambda x: x.novelty_score + x.feasibility_score + x.impact_potential,
            reverse=True,
        )

        print(f"✅ 혁신 아이디어 생성 완료: {len(ideas)}개 아이디어")

        return ideas

    def _create_innovation_idea(self, trend: TrendAnalysis, domain: str = None) -> InnovationIdea:
        """트렌드 기반 혁신 아이디어 생성"""
        # 아이디어 제목 생성
        title = f"{trend.trend_name} 기반 혁신 솔루션"

        # 아이디어 설명 생성
        description = f"{trend.description}을 활용하여 새로운 가치를 창조하는 혁신적 접근법"

        # 카테고리 결정
        category = domain if domain else trend.category.value

        # 점수 계산
        novelty_score = min(1.0, trend.impact_level + 0.2)
        feasibility_score = min(1.0, trend.confidence + 0.1)
        impact_potential = trend.impact_level

        # 구현 단계 생성
        implementation_steps = [
            "시장 조사 및 사용자 니즈 분석",
            "프로토타입 개발 및 테스트",
            "피드백 수집 및 개선",
            "상용화 및 확산",
        ]

        # 위험 요소 식별
        risk_factors = ["기술적 복잡성", "시장 수용도 불확실성", "경쟁 환경 변화"]

        idea = InnovationIdea(
            title=title,
            description=description,
            category=category,
            novelty_score=novelty_score,
            feasibility_score=feasibility_score,
            impact_potential=impact_potential,
            implementation_steps=implementation_steps,
            risk_factors=risk_factors,
        )

        return idea

    def _create_pattern_based_idea(self, pattern_data: Dict[str, Any], trends: List[TrendAnalysis]) -> InnovationIdea:
        """패턴 기반 혁신 아이디어 생성"""
        # 패턴 기반 제목 생성
        title = f"{pattern_data['name']} 기반 혁신 플랫폼"

        # 패턴 기반 설명 생성
        description = f"{pattern_data['description']}을 통해 새로운 가치를 창조하는 플랫폼"

        # 점수 계산
        novelty_score = 0.8
        feasibility_score = 0.7
        impact_potential = 0.9

        # 구현 단계 생성
        implementation_steps = [
            "패턴 분석 및 적용 영역 식별",
            "융합 기술 개발",
            "파일럿 프로젝트 실행",
            "확산 및 상용화",
        ]

        # 위험 요소 식별
        risk_factors = [
            "기술적 융합의 복잡성",
            "시장 수용도 불확실성",
            "규제 환경 변화",
        ]

        idea = InnovationIdea(
            title=title,
            description=description,
            category="cross_domain",
            novelty_score=novelty_score,
            feasibility_score=feasibility_score,
            impact_potential=impact_potential,
            implementation_steps=implementation_steps,
            risk_factors=risk_factors,
        )

        return idea

    def create_strategic_roadmap(
        self,
        trends: List[TrendAnalysis],
        scenarios: List[FutureScenario],
        ideas: List[InnovationIdea],
    ) -> Dict[str, Any]:
        """전략적 로드맵 생성"""
        print("🗺️ 전략적 로드맵 생성 중...")

        roadmap = {
            "short_term": {
                "time_frame": "1-3년",
                "focus_areas": self._identify_short_term_focus(trends),
                "key_initiatives": self._generate_short_term_initiatives(ideas),
                "success_metrics": ["시장 진입", "기술 검증", "사용자 피드백"],
            },
            "medium_term": {
                "time_frame": "3-7년",
                "focus_areas": self._identify_medium_term_focus(trends, scenarios),
                "key_initiatives": self._generate_medium_term_initiatives(scenarios),
                "success_metrics": ["시장 확장", "수익성 달성", "경쟁 우위 확보"],
            },
            "long_term": {
                "time_frame": "7-15년",
                "focus_areas": self._identify_long_term_focus(scenarios),
                "key_initiatives": self._generate_long_term_initiatives(scenarios),
                "success_metrics": ["시장 리더십", "지속가능한 성장", "사회적 영향"],
            },
        }

        print("✅ 전략적 로드맵 생성 완료")

        return roadmap

    def _identify_short_term_focus(self, trends: List[TrendAnalysis]) -> List[str]:
        """단기 집중 영역 식별"""
        focus_areas = []

        for trend in trends[:3]:
            if trend.time_horizon == "1-3년" or trend.time_horizon == "3-5년":
                focus_areas.append(f"{trend.trend_name} 대응")

        return focus_areas

    def _identify_medium_term_focus(self, trends: List[TrendAnalysis], scenarios: List[FutureScenario]) -> List[str]:
        """중기 집중 영역 식별"""
        focus_areas = []

        # 트렌드 기반
        for trend in trends:
            if trend.time_horizon == "5-10년":
                focus_areas.append(f"{trend.trend_name} 준비")

        # 시나리오 기반
        realistic_scenario = next((s for s in scenarios if s.scenario_type == ScenarioType.REALISTIC), None)
        if realistic_scenario:
            focus_areas.extend(realistic_scenario.adaptation_strategies[:2])

        return focus_areas

    def _identify_long_term_focus(self, scenarios: List[FutureScenario]) -> List[str]:
        """장기 집중 영역 식별"""
        focus_areas = []

        # 모든 시나리오 고려
        for scenario in scenarios:
            if scenario.scenario_type in [
                ScenarioType.OPTIMISTIC,
                ScenarioType.DISRUPTIVE,
            ]:
                focus_areas.extend(scenario.adaptation_strategies[:2])

        return list(set(focus_areas))  # 중복 제거

    def _generate_short_term_initiatives(self, ideas: List[InnovationIdea]) -> List[str]:
        """단기 이니셔티브 생성"""
        initiatives = []

        for idea in ideas[:3]:  # 상위 3개 아이디어
            initiatives.append(f"{idea.title} 프로토타입 개발")

        return initiatives

    def _generate_medium_term_initiatives(self, scenarios: List[FutureScenario]) -> List[str]:
        """중기 이니셔티브 생성"""
        initiatives = []

        for scenario in scenarios:
            if scenario.scenario_type == ScenarioType.REALISTIC:
                initiatives.extend(scenario.adaptation_strategies[1:3])
                break

        return initiatives

    def _generate_long_term_initiatives(self, scenarios: List[FutureScenario]) -> List[str]:
        """장기 이니셔티브 생성"""
        initiatives = []

        for scenario in scenarios:
            if scenario.scenario_type == ScenarioType.OPTIMISTIC:
                initiatives.extend(scenario.adaptation_strategies)
                break

        return initiatives

    def get_future_insights(self) -> Dict[str, Any]:
        """미래 인사이트 제공"""
        if not self.analysis_history:
            return {"message": "아직 미래 분석 기록이 없습니다."}

        recent_analyses = self.analysis_history[-5:]  # noqa: F841

        insights = {
            "total_analyses": len(self.analysis_history),
            "trend_categories": self._analyze_trend_categories(),
            "scenario_preferences": self._analyze_scenario_preferences(),
            "innovation_patterns": self._analyze_innovation_patterns(),
        }

        return insights

    def _analyze_trend_categories(self) -> Dict[str, int]:
        """트렌드 카테고리 분석"""
        category_counts = {}
        for analysis in self.analysis_history:
            if "trends" in analysis:
                for trend in analysis["trends"]:
                    category = trend.category.value
                    category_counts[category] = category_counts.get(category, 0) + 1

        return category_counts

    def _analyze_scenario_preferences(self) -> Dict[str, int]:
        """시나리오 선호도 분석"""
        scenario_counts = {}
        for analysis in self.analysis_history:
            if "scenarios" in analysis:
                for scenario in analysis["scenarios"]:
                    scenario_type = scenario.scenario_type.value
                    scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1

        return scenario_counts

    def _analyze_innovation_patterns(self) -> Dict[str, int]:
        """혁신 패턴 분석"""
        pattern_counts = {}
        for analysis in self.analysis_history:
            if "ideas" in analysis:
                for idea in analysis["ideas"]:
                    category = idea.category
                    pattern_counts[category] = pattern_counts.get(category, 0) + 1

        return pattern_counts


# Phase 25 미래 예측 및 설계 시스템 인스턴스
future_design_system = FutureDesignSystem()


def phase_25_future_design(domain: str = None, time_horizon: str = "5-10년") -> Dict[str, Any]:
    """Phase 25 미래 예측 및 설계 시스템 메인 함수"""
    # 1. 트렌드 분석
    trends = future_design_system.analyze_trends(domain, time_horizon)

    # 2. 미래 시나리오 생성
    scenarios = future_design_system.generate_future_scenarios(trends)

    # 3. 혁신 아이디어 생성
    ideas = future_design_system.generate_innovation_ideas(trends, domain)

    # 4. 전략적 로드맵 생성
    roadmap = future_design_system.create_strategic_roadmap(trends, scenarios, ideas)

    # 분석 기록 저장
    analysis_record = {
        "timestamp": time.time(),
        "domain": domain,
        "time_horizon": time_horizon,
        "trends": trends,
        "scenarios": scenarios,
        "ideas": ideas,
        "roadmap": roadmap,
    }

    future_design_system.analysis_history.append(analysis_record)

    return {
        "phase": 25,
        "system": "future_design",
        "trends": trends,
        "scenarios": scenarios,
        "ideas": ideas,
        "roadmap": roadmap,
        "insights": future_design_system.get_future_insights(),
    }
