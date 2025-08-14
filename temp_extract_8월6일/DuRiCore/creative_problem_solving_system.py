"""
DuRiCore Phase 2.4: 창의적 문제 해결 시스템 (Creative Problem Solving System)
- 복잡한 문제의 창의적 분석
- 혁신적 해결책 생성 및 평가
- 문제 해결 과정의 자기 모니터링
- 창의적 사고 패턴 개발
"""

import asyncio
import logging
import random
import time
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict

# 로깅 설정
logger = logging.getLogger(__name__)

class ProblemComplexity(Enum):
    """문제 복잡성 수준"""
    SIMPLE = "simple"           # 단순 (1-2개 요소)
    MODERATE = "moderate"       # 보통 (3-5개 요소)
    COMPLEX = "complex"         # 복잡 (6-10개 요소)
    VERY_COMPLEX = "very_complex" # 매우 복잡 (10개 이상 요소)

class SolutionInnovation(Enum):
    """해결책 혁신 수준"""
    INCREMENTAL = "incremental"      # 점진적 개선
    MODULAR = "modular"              # 모듈적 혁신
    RADICAL = "radical"              # 급진적 혁신
    DISRUPTIVE = "disruptive"        # 파괴적 혁신
    TRANSFORMATIVE = "transformative" # 변혁적 혁신

class CreativeThinkingMode(Enum):
    """창의적 사고 모드"""
    DIVERGENT = "divergent"      # 발산적 사고
    CONVERGENT = "convergent"    # 수렴적 사고
    LATERAL = "lateral"          # 측면적 사고
    ANALYTICAL = "analytical"    # 분석적 사고
    INTUITIVE = "intuitive"      # 직관적 사고

@dataclass
class ProblemDefinition:
    """문제 정의"""
    problem_id: str
    title: str
    description: str
    complexity: ProblemComplexity
    constraints: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    stakeholders: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CreativeSolution:
    """창의적 해결책"""
    solution_id: str
    problem_id: str
    title: str
    description: str
    approach: str
    innovation_level: SolutionInnovation
    novelty_score: float  # 0.0-1.0
    feasibility_score: float  # 0.0-1.0
    effectiveness_score: float  # 0.0-1.0
    efficiency_score: float  # 0.0-1.0
    implementation_steps: List[str] = field(default_factory=list)
    risk_assessment: Dict[str, float] = field(default_factory=dict)
    resource_requirements: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def overall_score(self) -> float:
        """전체 점수"""
        return (self.novelty_score + self.feasibility_score + 
                self.effectiveness_score + self.efficiency_score) / 4.0

@dataclass
class ProblemSolvingProcess:
    """문제 해결 과정"""
    process_id: str
    problem_id: str
    thinking_mode: CreativeThinkingMode
    steps_taken: List[Dict[str, Any]] = field(default_factory=list)
    insights_generated: List[str] = field(default_factory=list)
    solutions_considered: List[str] = field(default_factory=list)
    final_solution: Optional[str] = None
    process_duration: float = 0.0  # 초 단위
    success_metrics: Dict[str, float] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class CreativeProblemSolvingMetrics:
    """창의적 문제 해결 측정 지표"""
    problem_analysis_skill: float = 0.5      # 문제 분석 능력 (0.0-1.0)
    solution_generation_skill: float = 0.5   # 해결책 생성 능력 (0.0-1.0)
    innovation_capability: float = 0.5       # 혁신 능력 (0.0-1.0)
    implementation_skill: float = 0.5        # 구현 능력 (0.0-1.0)
    process_efficiency: float = 0.5          # 과정 효율성 (0.0-1.0)
    
    @property
    def overall_problem_solving_skill(self) -> float:
        """전체 문제 해결 능력"""
        return (self.problem_analysis_skill + self.solution_generation_skill + 
                self.innovation_capability + self.implementation_skill + 
                self.process_efficiency) / 5.0

@dataclass
class CreativeProblemSolvingState:
    """창의적 문제 해결 상태"""
    solving_metrics: CreativeProblemSolvingMetrics
    problems_solved: List[ProblemDefinition] = field(default_factory=list)
    solutions_generated: List[CreativeSolution] = field(default_factory=list)
    solving_processes: List[ProblemSolvingProcess] = field(default_factory=list)
    solving_history: List[Dict[str, Any]] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)

class CreativeProblemSolvingSystem:
    """창의적 문제 해결 시스템"""
    
    def __init__(self):
        self.solving_state = CreativeProblemSolvingState(
            solving_metrics=CreativeProblemSolvingMetrics()
        )
        self.problem_templates = {}
        self.solution_patterns = defaultdict(list)
        self.innovation_techniques = []
        logger.info("🧠 창의적 문제 해결 시스템 초기화 완료")
    
    async def analyze_problem(self, problem_data: Dict[str, Any]) -> ProblemDefinition:
        """문제 분석"""
        problem_id = f"problem_{int(time.time())}"
        
        # 문제 복잡성 분석
        complexity = self._assess_problem_complexity(problem_data)
        
        # 제약 조건 식별
        constraints = self._identify_constraints(problem_data)
        
        # 목표 식별
        objectives = self._identify_objectives(problem_data)
        
        # 이해관계자 식별
        stakeholders = self._identify_stakeholders(problem_data)
        
        problem = ProblemDefinition(
            problem_id=problem_id,
            title=problem_data.get('title', ''),
            description=problem_data.get('description', ''),
            complexity=complexity,
            constraints=constraints,
            objectives=objectives,
            stakeholders=stakeholders,
            context=problem_data.get('context', {})
        )
        
        self.solving_state.problems_solved.append(problem)
        await self._update_problem_analysis_metrics(problem)
        
        logger.info(f"🔍 문제 분석 완료: {complexity.value} 복잡성")
        return problem
    
    async def generate_creative_solutions(self, problem: ProblemDefinition) -> List[CreativeSolution]:
        """창의적 해결책 생성"""
        solutions = []
        
        # 다양한 사고 모드로 해결책 생성
        thinking_modes = [
            CreativeThinkingMode.DIVERGENT,
            CreativeThinkingMode.LATERAL,
            CreativeThinkingMode.ANALYTICAL,
            CreativeThinkingMode.INTUITIVE
        ]
        
        for mode in thinking_modes:
            solution = await self._generate_solution_with_mode(problem, mode)
            if solution:
                solutions.append(solution)
        
        # 해결책 평가 및 순위 결정
        evaluated_solutions = await self._evaluate_solutions(solutions)
        
        # 상위 해결책 선택
        top_solutions = evaluated_solutions[:3]  # 상위 3개
        
        for solution in top_solutions:
            self.solving_state.solutions_generated.append(solution)
        
        await self._update_solution_generation_metrics(top_solutions)
        
        logger.info(f"💡 창의적 해결책 생성 완료: {len(top_solutions)}개")
        return top_solutions
    
    async def execute_problem_solving_process(self, problem: ProblemDefinition, 
                                           target_solution: CreativeSolution) -> ProblemSolvingProcess:
        """문제 해결 과정 실행"""
        process_id = f"process_{int(time.time())}"
        start_time = time.time()
        
        # 문제 해결 과정 정의
        process = ProblemSolvingProcess(
            process_id=process_id,
            problem_id=problem.problem_id,
            thinking_mode=CreativeThinkingMode.CONVERGENT
        )
        
        # 단계별 실행
        steps = [
            {"step": "문제 재정의", "action": "문제의 핵심 요소 재분석"},
            {"step": "해결책 세분화", "action": "구현 가능한 단위로 분해"},
            {"step": "자원 분석", "action": "필요한 자원과 제약 조건 파악"},
            {"step": "위험 평가", "action": "구현 과정의 위험 요소 식별"},
            {"step": "실행 계획", "action": "단계별 실행 계획 수립"}
        ]
        
        insights = []
        for i, step in enumerate(steps):
            # 각 단계 실행
            step_result = await self._execute_solving_step(step, problem, target_solution)
            process.steps_taken.append(step_result)
            
            # 인사이트 생성
            insight = await self._generate_step_insight(step, step_result)
            if insight:
                insights.append(insight)
        
        process.insights_generated = insights
        process.final_solution = target_solution.solution_id
        process.process_duration = time.time() - start_time
        
        # 성공 지표 계산
        success_metrics = await self._calculate_success_metrics(process, target_solution)
        process.success_metrics = success_metrics
        
        self.solving_state.solving_processes.append(process)
        await self._update_process_efficiency_metrics(process)
        
        logger.info(f"⚡ 문제 해결 과정 완료: {process.process_duration:.1f}초")
        return process
    
    async def assess_innovation_capability(self) -> Dict[str, Any]:
        """혁신 능력 평가"""
        if not self.solving_state.solutions_generated:
            return {"capability_level": "unknown", "score": 0.0, "areas": []}
        
        # 혁신 능력 지표 계산
        novelty_average = sum(s.novelty_score for s in self.solving_state.solutions_generated) / len(self.solving_state.solutions_generated)
        feasibility_average = sum(s.feasibility_score for s in self.solving_state.solutions_generated) / len(self.solving_state.solutions_generated)
        effectiveness_average = sum(s.effectiveness_score for s in self.solving_state.solutions_generated) / len(self.solving_state.solutions_generated)
        efficiency_average = sum(s.efficiency_score for s in self.solving_state.solutions_generated) / len(self.solving_state.solutions_generated)
        
        # 전체 혁신 능력 점수
        innovation_score = (novelty_average + feasibility_average + 
                           effectiveness_average + efficiency_average) / 4.0
        
        # 혁신 수준 결정
        if innovation_score >= 0.8:
            capability_level = "transformative"
        elif innovation_score >= 0.6:
            capability_level = "disruptive"
        elif innovation_score >= 0.4:
            capability_level = "radical"
        elif innovation_score >= 0.2:
            capability_level = "modular"
        else:
            capability_level = "incremental"
        
        # 개선 영역 식별
        improvement_areas = self._identify_innovation_improvement_areas({
            "novelty": novelty_average,
            "feasibility": feasibility_average,
            "effectiveness": effectiveness_average,
            "efficiency": efficiency_average
        })
        
        self.solving_state.solving_metrics.innovation_capability = innovation_score
        
        return {
            "capability_level": capability_level,
            "score": innovation_score,
            "areas": improvement_areas,
            "detailed_scores": {
                "novelty": novelty_average,
                "feasibility": feasibility_average,
                "effectiveness": effectiveness_average,
                "efficiency": efficiency_average
            }
        }
    
    async def generate_problem_solving_report(self) -> Dict[str, Any]:
        """문제 해결 보고서 생성"""
        # 현재 상태 분석
        current_state = self.get_solving_state()
        
        # 혁신 능력 평가
        innovation = await self.assess_innovation_capability()
        
        # 해결된 문제 통계
        problem_stats = self._calculate_problem_statistics()
        
        # 개선 권장사항
        recommendations = await self._generate_solving_recommendations()
        
        return {
            "current_state": current_state,
            "innovation": innovation,
            "problem_statistics": problem_stats,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_solving_state(self) -> Dict[str, Any]:
        """문제 해결 상태 반환"""
        return {
            "solving_metrics": asdict(self.solving_state.solving_metrics),
            "problems_solved": len(self.solving_state.problems_solved),
            "solutions_generated": len(self.solving_state.solutions_generated),
            "processes_executed": len(self.solving_state.solving_processes),
            "last_update": self.solving_state.last_update.isoformat()
        }
    
    # 내부 분석 메서드들
    def _assess_problem_complexity(self, problem_data: Dict[str, Any]) -> ProblemComplexity:
        """문제 복잡성 평가"""
        # 실제 구현에서는 더 정교한 분석 로직 사용
        factors = problem_data.get('complexity_factors', [])
        
        if len(factors) <= 2:
            return ProblemComplexity.SIMPLE
        elif len(factors) <= 5:
            return ProblemComplexity.MODERATE
        elif len(factors) <= 10:
            return ProblemComplexity.COMPLEX
        else:
            return ProblemComplexity.VERY_COMPLEX
    
    def _identify_constraints(self, problem_data: Dict[str, Any]) -> List[str]:
        """제약 조건 식별"""
        constraints = problem_data.get('constraints', [])
        
        # 기본 제약 조건 추가
        if 'time_limit' in problem_data:
            constraints.append("시간 제약")
        if 'resource_limit' in problem_data:
            constraints.append("자원 제약")
        if 'budget_limit' in problem_data:
            constraints.append("예산 제약")
        
        return constraints
    
    def _identify_objectives(self, problem_data: Dict[str, Any]) -> List[str]:
        """목표 식별"""
        objectives = problem_data.get('objectives', [])
        
        # 기본 목표 추가
        if 'efficiency' in problem_data:
            objectives.append("효율성 향상")
        if 'quality' in problem_data:
            objectives.append("품질 개선")
        if 'innovation' in problem_data:
            objectives.append("혁신 도입")
        
        return objectives
    
    def _identify_stakeholders(self, problem_data: Dict[str, Any]) -> List[str]:
        """이해관계자 식별"""
        stakeholders = problem_data.get('stakeholders', [])
        
        # 기본 이해관계자 추가
        if 'users' in problem_data:
            stakeholders.append("사용자")
        if 'management' in problem_data:
            stakeholders.append("경영진")
        if 'developers' in problem_data:
            stakeholders.append("개발자")
        
        return stakeholders
    
    async def _generate_solution_with_mode(self, problem: ProblemDefinition, 
                                         mode: CreativeThinkingMode) -> Optional[CreativeSolution]:
        """특정 사고 모드로 해결책 생성"""
        solution_id = f"solution_{int(time.time())}"
        
        # 사고 모드별 해결책 생성
        if mode == CreativeThinkingMode.DIVERGENT:
            approach = "다양한 관점에서 문제를 바라보고 여러 대안을 생성"
        elif mode == CreativeThinkingMode.LATERAL:
            approach = "기존 패턴을 깨고 새로운 관점에서 접근"
        elif mode == CreativeThinkingMode.ANALYTICAL:
            approach = "체계적 분석을 통해 논리적 해결책 도출"
        elif mode == CreativeThinkingMode.INTUITIVE:
            approach = "직관과 경험을 바탕으로 한 창의적 접근"
        else:
            approach = "통합적 접근 방법"
        
        # 해결책 점수 계산
        novelty_score = random.uniform(0.4, 0.9)
        feasibility_score = random.uniform(0.5, 0.8)
        effectiveness_score = random.uniform(0.6, 0.9)
        efficiency_score = random.uniform(0.5, 0.8)
        
        # 혁신 수준 결정
        overall_score = (novelty_score + feasibility_score + effectiveness_score + efficiency_score) / 4.0
        
        if overall_score >= 0.8:
            innovation_level = SolutionInnovation.TRANSFORMATIVE
        elif overall_score >= 0.7:
            innovation_level = SolutionInnovation.DISRUPTIVE
        elif overall_score >= 0.6:
            innovation_level = SolutionInnovation.RADICAL
        elif overall_score >= 0.5:
            innovation_level = SolutionInnovation.MODULAR
        else:
            innovation_level = SolutionInnovation.INCREMENTAL
        
        solution = CreativeSolution(
            solution_id=solution_id,
            problem_id=problem.problem_id,
            title=f"{mode.value} 접근 해결책",
            description=f"{approach}를 통한 {problem.title} 해결 방안",
            approach=approach,
            innovation_level=innovation_level,
            novelty_score=novelty_score,
            feasibility_score=feasibility_score,
            effectiveness_score=effectiveness_score,
            efficiency_score=efficiency_score,
            implementation_steps=[
                "문제 상황 분석",
                "해결 방안 설계",
                "프로토타입 개발",
                "테스트 및 검증",
                "최종 구현"
            ],
            risk_assessment={
                "기술적 위험": random.uniform(0.2, 0.6),
                "조직적 위험": random.uniform(0.3, 0.7),
                "시장적 위험": random.uniform(0.2, 0.5)
            }
        )
        
        return solution
    
    async def _evaluate_solutions(self, solutions: List[CreativeSolution]) -> List[CreativeSolution]:
        """해결책 평가 및 순위 결정"""
        # 전체 점수로 정렬
        return sorted(solutions, key=lambda s: s.overall_score, reverse=True)
    
    async def _execute_solving_step(self, step: Dict[str, str], problem: ProblemDefinition, 
                                  solution: CreativeSolution) -> Dict[str, Any]:
        """문제 해결 단계 실행"""
        step_result = {
            "step_name": step["step"],
            "action": step["action"],
            "status": "completed",
            "duration": random.uniform(10, 60),  # 초 단위
            "insights": [],
            "challenges": [],
            "next_steps": []
        }
        
        # 단계별 특화 로직
        if step["step"] == "문제 재정의":
            step_result["insights"].append("문제의 핵심 요소를 명확히 파악")
        elif step["step"] == "해결책 세분화":
            step_result["insights"].append("구현 가능한 단위로 분해 완료")
        elif step["step"] == "자원 분석":
            step_result["insights"].append("필요한 자원과 제약 조건 파악")
        elif step["step"] == "위험 평가":
            step_result["insights"].append("주요 위험 요소 식별")
        elif step["step"] == "실행 계획":
            step_result["insights"].append("단계별 실행 계획 수립")
        
        return step_result
    
    async def _generate_step_insight(self, step: Dict[str, str], step_result: Dict[str, Any]) -> Optional[str]:
        """단계별 인사이트 생성"""
        insights = {
            "문제 재정의": "문제의 본질을 정확히 파악하는 것이 해결의 절반",
            "해결책 세분화": "복잡한 문제는 작은 단위로 나누어 접근",
            "자원 분석": "가용 자원을 최대한 활용하는 전략적 사고",
            "위험 평가": "예상되는 위험을 미리 파악하여 대비",
            "실행 계획": "체계적인 계획이 성공의 열쇠"
        }
        
        return insights.get(step["step"])
    
    async def _calculate_success_metrics(self, process: ProblemSolvingProcess, 
                                       solution: CreativeSolution) -> Dict[str, float]:
        """성공 지표 계산"""
        return {
            "process_efficiency": min(1.0, 1000 / process.process_duration),  # 시간 효율성
            "solution_quality": solution.overall_score,
            "innovation_level": solution.novelty_score,
            "implementation_readiness": solution.feasibility_score,
            "overall_success": (solution.overall_score + min(1.0, 1000 / process.process_duration)) / 2
        }
    
    def _identify_innovation_improvement_areas(self, scores: Dict[str, float]) -> List[str]:
        """혁신 개선 영역 식별"""
        areas = []
        threshold = 0.7
        
        for area, score in scores.items():
            if score < threshold:
                areas.append(area)
        
        return areas
    
    def _calculate_problem_statistics(self) -> Dict[str, Any]:
        """해결된 문제 통계"""
        if not self.solving_state.problems_solved:
            return {"total_problems": 0, "complexity_distribution": {}, "success_rate": 0.0}
        
        complexity_counts = defaultdict(int)
        for problem in self.solving_state.problems_solved:
            complexity_counts[problem.complexity.value] += 1
        
        total_problems = len(self.solving_state.problems_solved)
        success_rate = len(self.solving_state.solving_processes) / total_problems if total_problems > 0 else 0.0
        
        return {
            "total_problems": total_problems,
            "complexity_distribution": dict(complexity_counts),
            "success_rate": success_rate,
            "average_solution_quality": sum(s.overall_score for s in self.solving_state.solutions_generated) / len(self.solving_state.solutions_generated) if self.solving_state.solutions_generated else 0.0
        }
    
    async def _generate_solving_recommendations(self) -> List[str]:
        """문제 해결 권장사항 생성"""
        recommendations = []
        
        # 문제 해결 능력 수준에 따른 권장사항
        solving_level = self.solving_state.solving_metrics.overall_problem_solving_skill
        
        if solving_level < 0.4:
            recommendations.append("기본적인 문제 분석 기법 학습")
            recommendations.append("체계적 사고 방법론 도입")
        elif solving_level < 0.6:
            recommendations.append("창의적 사고 기법 심화 학습")
            recommendations.append("다양한 문제 해결 프레임워크 활용")
        elif solving_level < 0.8:
            recommendations.append("혁신적 문제 해결 방법론 적용")
            recommendations.append("팀 기반 창의적 문제 해결 훈련")
        else:
            recommendations.append("문제 해결 전문가 수준 유지")
            recommendations.append("다른 사람들의 문제 해결 능력 향상 지원")
        
        return recommendations
    
    async def _update_problem_analysis_metrics(self, problem: ProblemDefinition) -> None:
        """문제 분석 메트릭 업데이트"""
        # 실제 구현에서는 더 정교한 업데이트 로직 사용
        self.solving_state.solving_metrics.problem_analysis_skill = min(1.0, 
            self.solving_state.solving_metrics.problem_analysis_skill + 0.01)
    
    async def _update_solution_generation_metrics(self, solutions: List[CreativeSolution]) -> None:
        """해결책 생성 메트릭 업데이트"""
        # 실제 구현에서는 더 정교한 업데이트 로직 사용
        self.solving_state.solving_metrics.solution_generation_skill = min(1.0, 
            self.solving_state.solving_metrics.solution_generation_skill + 0.01)
    
    async def _update_process_efficiency_metrics(self, process: ProblemSolvingProcess) -> None:
        """과정 효율성 메트릭 업데이트"""
        # 실제 구현에서는 더 정교한 업데이트 로직 사용
        self.solving_state.solving_metrics.process_efficiency = min(1.0, 
            self.solving_state.solving_metrics.process_efficiency + 0.01)

async def test_creative_problem_solving_system():
    """창의적 문제 해결 시스템 테스트"""
    logger.info("🧠 창의적 문제 해결 시스템 테스트 시작")
    
    # 시스템 생성
    solving_system = CreativeProblemSolvingSystem()
    
    # 테스트 문제 데이터
    test_problems = [
        {
            "title": "사용자 경험 개선",
            "description": "웹사이트의 사용자 경험을 크게 개선하여 사용자 만족도를 높이는 방안",
            "complexity_factors": ["사용자 행동 분석", "UI/UX 설계", "기술적 구현", "성능 최적화", "접근성 개선"],
            "constraints": ["기존 시스템 호환성", "개발 기간 제한"],
            "objectives": ["사용자 만족도 향상", "사용률 증가", "이탈률 감소"],
            "stakeholders": ["사용자", "개발팀", "경영진"],
            "context": {"platform": "web", "user_count": 10000}
        },
        {
            "title": "데이터 보안 강화",
            "description": "기업의 민감한 데이터를 보호하면서도 사용성은 유지하는 보안 시스템 구축",
            "complexity_factors": ["암호화 기술", "접근 제어", "감사 로그", "백업 시스템", "복구 절차", "규정 준수"],
            "constraints": ["예산 제약", "성능 영향 최소화"],
            "objectives": ["데이터 보안 강화", "규정 준수", "사용성 유지"],
            "stakeholders": ["IT팀", "보안팀", "사용자", "규제 기관"],
            "context": {"data_type": "personal", "compliance": "GDPR"}
        }
    ]
    
    # 문제 분석 및 해결책 생성
    for problem_data in test_problems:
        # 문제 분석
        problem = await solving_system.analyze_problem(problem_data)
        
        # 창의적 해결책 생성
        solutions = await solving_system.generate_creative_solutions(problem)
        
        # 최적 해결책 선택 및 실행
        if solutions:
            best_solution = solutions[0]
            process = await solving_system.execute_problem_solving_process(problem, best_solution)
    
    # 혁신 능력 평가
    innovation = await solving_system.assess_innovation_capability()
    
    # 보고서 생성
    report = await solving_system.generate_problem_solving_report()
    
    # 결과 출력
    print("\n=== 창의적 문제 해결 시스템 테스트 결과 ===")
    print(f"문제 해결 능력: {solving_system.solving_state.solving_metrics.overall_problem_solving_skill:.3f}")
    print(f"혁신 능력: {innovation['score']:.3f} ({innovation['capability_level']})")
    print(f"해결된 문제: {len(solving_system.solving_state.problems_solved)}개")
    print(f"생성된 해결책: {len(solving_system.solving_state.solutions_generated)}개")
    print(f"실행된 과정: {len(solving_system.solving_state.solving_processes)}개")
    
    print("✅ 창의적 문제 해결 시스템 테스트 완료!")

if __name__ == "__main__":
    asyncio.run(test_creative_problem_solving_system()) 