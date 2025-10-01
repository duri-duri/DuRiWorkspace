"""
🎯 DuRi Phase 2: 고급 학습 시스템
목표: Phase 1의 기반 위에 더 정교한 문제 해결, 다단계 추론, 전략적 사고 개발
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AdvancedLearningCapability(Enum):
    """고급 학습 능력"""

    MULTI_STEP_REASONING = "multi_step_reasoning"  # 다단계 추론
    STRATEGIC_THINKING = "strategic_thinking"  # 전략적 사고
    COMPLEX_PROBLEM_SOLVING = "complex_problem_solving"  # 복잡한 문제 해결
    META_LEARNING_ENHANCEMENT = "meta_learning_enhancement"  # 메타 학습 강화
    CREATIVE_SYNTHESIS = "creative_synthesis"  # 창의적 종합
    ADAPTIVE_STRATEGY = "adaptive_strategy"  # 적응적 전략


class ProblemComplexity(Enum):
    """문제 복잡도"""

    SIMPLE = "simple"  # 단순
    MODERATE = "moderate"  # 보통
    COMPLEX = "complex"  # 복잡
    VERY_COMPLEX = "very_complex"  # 매우 복잡
    SYSTEMIC = "systemic"  # 체계적


@dataclass
class AdvancedLearningTask:
    """고급 학습 작업"""

    task_id: str
    problem_description: str
    complexity: ProblemComplexity
    required_capabilities: List[AdvancedLearningCapability]
    expected_outcome: str
    success_criteria: List[str]
    created_at: datetime


@dataclass
class MultiStepReasoning:
    """다단계 추론"""

    reasoning_id: str
    steps: List[Dict[str, Any]]
    intermediate_conclusions: List[str]
    final_conclusion: str
    confidence: float
    reasoning_chain: str


@dataclass
class StrategicThinking:
    """전략적 사고"""

    strategy_id: str
    problem_analysis: Dict[str, Any]
    strategic_options: List[Dict[str, Any]]
    selected_strategy: Dict[str, Any]
    implementation_plan: List[str]
    risk_assessment: Dict[str, Any]


class Phase2AdvancedLearning:
    """Phase 2: 고급 학습 시스템"""

    def __init__(self):
        self.current_capabilities = {
            AdvancedLearningCapability.MULTI_STEP_REASONING: 0.3,
            AdvancedLearningCapability.STRATEGIC_THINKING: 0.2,
            AdvancedLearningCapability.COMPLEX_PROBLEM_SOLVING: 0.25,
            AdvancedLearningCapability.META_LEARNING_ENHANCEMENT: 0.4,
            AdvancedLearningCapability.CREATIVE_SYNTHESIS: 0.15,
            AdvancedLearningCapability.ADAPTIVE_STRATEGY: 0.2,
        }

        self.learning_tasks = []
        self.completed_tasks = []
        self.reasoning_history = []
        self.strategy_history = []

        # Phase 1 시스템들과의 통합
        self.insight_engine = None
        self.phase_evaluator = None
        self.insight_reflector = None
        self.insight_manager = None

    def initialize_phase_1_integration(self):
        """Phase 1 시스템들과 통합"""
        try:
            import sys

            sys.path.append(".")
            from duri_brain.learning.insight_autonomous_manager import (
                get_insight_manager,
            )
            from duri_brain.learning.insight_engine import get_dual_response_system
            from duri_brain.learning.insight_self_reflection import (
                get_insight_reflector,
            )
            from duri_brain.learning.phase_self_evaluator import get_phase_evaluator

            self.insight_engine = get_dual_response_system()
            self.phase_evaluator = get_phase_evaluator()
            self.insight_reflector = get_insight_reflector()
            self.insight_manager = get_insight_manager()

            # Phase 2로 업데이트
            from duri_brain.learning.phase_self_evaluator import PhaseLevel

            self.phase_evaluator.current_phase = PhaseLevel.PHASE_2_ADVANCED

            logger.info("✅ Phase 1 시스템들과 통합 완료")
            return True

        except Exception as e:
            logger.error(f"❌ Phase 1 시스템 통합 실패: {e}")
            return False

    def create_advanced_learning_task(
        self, problem: str, complexity: ProblemComplexity
    ) -> AdvancedLearningTask:
        """고급 학습 작업 생성"""
        task_id = f"phase2_task_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 복잡도에 따른 필요한 능력 결정
        required_capabilities = self._determine_required_capabilities(complexity)

        task = AdvancedLearningTask(
            task_id=task_id,
            problem_description=problem,
            complexity=complexity,
            required_capabilities=required_capabilities,
            expected_outcome="문제 해결 및 학습 성과 향상",
            success_criteria=[
                "문제 해결 완료",
                "새로운 통찰 생성",
                "학습 능력 향상",
                "전략적 사고 발전",
            ],
            created_at=datetime.now(),
        )

        self.learning_tasks.append(task)
        logger.info(f"📋 고급 학습 작업 생성: {task_id}")

        return task

    def _determine_required_capabilities(
        self, complexity: ProblemComplexity
    ) -> List[AdvancedLearningCapability]:
        """복잡도에 따른 필요한 능력 결정"""
        if complexity == ProblemComplexity.SIMPLE:
            return [AdvancedLearningCapability.MULTI_STEP_REASONING]
        elif complexity == ProblemComplexity.MODERATE:
            return [
                AdvancedLearningCapability.MULTI_STEP_REASONING,
                AdvancedLearningCapability.STRATEGIC_THINKING,
            ]
        elif complexity == ProblemComplexity.COMPLEX:
            return [
                AdvancedLearningCapability.MULTI_STEP_REASONING,
                AdvancedLearningCapability.STRATEGIC_THINKING,
                AdvancedLearningCapability.COMPLEX_PROBLEM_SOLVING,
            ]
        elif complexity == ProblemComplexity.VERY_COMPLEX:
            return [
                AdvancedLearningCapability.MULTI_STEP_REASONING,
                AdvancedLearningCapability.STRATEGIC_THINKING,
                AdvancedLearningCapability.COMPLEX_PROBLEM_SOLVING,
                AdvancedLearningCapability.CREATIVE_SYNTHESIS,
            ]
        else:  # SYSTEMIC
            return [
                AdvancedLearningCapability.MULTI_STEP_REASONING,
                AdvancedLearningCapability.STRATEGIC_THINKING,
                AdvancedLearningCapability.COMPLEX_PROBLEM_SOLVING,
                AdvancedLearningCapability.CREATIVE_SYNTHESIS,
                AdvancedLearningCapability.ADAPTIVE_STRATEGY,
            ]

    def execute_multi_step_reasoning(self, problem: str) -> MultiStepReasoning:
        """다단계 추론 실행"""
        logger.info("🧠 다단계 추론 시작")

        reasoning_id = f"reasoning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        steps = []
        intermediate_conclusions = []

        # 1단계: 문제 분석
        problem_analysis = self._analyze_problem(problem)
        steps.append(
            {
                "step": 1,
                "action": "문제 분석",
                "input": problem,
                "output": problem_analysis,
                "confidence": 0.8,
            }
        )
        intermediate_conclusions.append(f"문제 유형: {problem_analysis['type']}")

        # 2단계: 관련 요소 식별
        related_elements = self._identify_related_elements(problem_analysis)
        steps.append(
            {
                "step": 2,
                "action": "관련 요소 식별",
                "input": problem_analysis,
                "output": related_elements,
                "confidence": 0.7,
            }
        )
        intermediate_conclusions.append(f"관련 요소: {len(related_elements)}개")

        # 3단계: 가설 생성
        hypotheses = self._generate_hypotheses(related_elements)
        steps.append(
            {
                "step": 3,
                "action": "가설 생성",
                "input": related_elements,
                "output": hypotheses,
                "confidence": 0.6,
            }
        )
        intermediate_conclusions.append(f"가설 수: {len(hypotheses)}개")

        # 4단계: 가설 검증
        validated_hypotheses = self._validate_hypotheses(hypotheses)
        steps.append(
            {
                "step": 4,
                "action": "가설 검증",
                "input": hypotheses,
                "output": validated_hypotheses,
                "confidence": 0.75,
            }
        )
        intermediate_conclusions.append(f"검증된 가설: {len(validated_hypotheses)}개")

        # 5단계: 결론 도출
        final_conclusion = self._derive_conclusion(validated_hypotheses)
        steps.append(
            {
                "step": 5,
                "action": "결론 도출",
                "input": validated_hypotheses,
                "output": final_conclusion,
                "confidence": 0.8,
            }
        )

        # 추론 체인 생성
        reasoning_chain = " → ".join(
            [f"단계{i+1}: {step['action']}" for i, step in enumerate(steps)]
        )

        reasoning = MultiStepReasoning(
            reasoning_id=reasoning_id,
            steps=steps,
            intermediate_conclusions=intermediate_conclusions,
            final_conclusion=final_conclusion,
            confidence=sum(step["confidence"] for step in steps) / len(steps),
            reasoning_chain=reasoning_chain,
        )

        self.reasoning_history.append(reasoning)
        logger.info(f"✅ 다단계 추론 완료: {reasoning_id}")

        return reasoning

    def _analyze_problem(self, problem: str) -> Dict[str, Any]:
        """문제 분석"""
        problem_lower = problem.lower()

        # 문제 유형 분류
        if any(word in problem_lower for word in ["학습", "성능", "효율"]):
            problem_type = "학습 성능 문제"
        elif any(word in problem_lower for word in ["메모리", "리소스"]):
            problem_type = "리소스 관리 문제"
        elif any(word in problem_lower for word in ["비용", "예산"]):
            problem_type = "비용 관리 문제"
        elif any(word in problem_lower for word in ["오류", "실패"]):
            problem_type = "오류 처리 문제"
        else:
            problem_type = "일반 문제"

        return {
            "type": problem_type,
            "complexity": "moderate",
            "urgency": "medium",
            "impact_scope": "system_wide",
        }

    def _identify_related_elements(self, problem_analysis: Dict[str, Any]) -> List[str]:
        """관련 요소 식별"""
        problem_type = problem_analysis["type"]

        if problem_type == "학습 성능 문제":
            return ["학습 루프", "성능 모니터링", "최적화 알고리즘", "메모리 사용량"]
        elif problem_type == "리소스 관리 문제":
            return ["메모리 할당", "CPU 사용량", "네트워크 대역폭", "저장 공간"]
        elif problem_type == "비용 관리 문제":
            return ["외부 API 호출", "계산 비용", "저장 비용", "네트워크 비용"]
        elif problem_type == "오류 처리 문제":
            return ["예외 처리", "로깅 시스템", "복구 메커니즘", "모니터링"]
        else:
            return ["일반 요소 1", "일반 요소 2", "일반 요소 3"]

    def _generate_hypotheses(self, related_elements: List[str]) -> List[Dict[str, Any]]:
        """가설 생성"""
        hypotheses = []

        for element in related_elements:
            hypothesis = {
                "element": element,
                "hypothesis": f"{element}의 최적화가 문제 해결에 도움이 될 것",
                "confidence": random.uniform(0.4, 0.8),
                "test_method": f"{element} 성능 측정",
            }
            hypotheses.append(hypothesis)

        return hypotheses

    def _validate_hypotheses(
        self, hypotheses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """가설 검증"""
        validated = []

        for hypothesis in hypotheses:
            # 시뮬레이션된 검증 과정
            if hypothesis["confidence"] > 0.5:
                hypothesis["validated"] = True
                hypothesis["validation_score"] = hypothesis["confidence"]
                validated.append(hypothesis)

        return validated

    def _derive_conclusion(self, validated_hypotheses: List[Dict[str, Any]]) -> str:
        """결론 도출"""
        if not validated_hypotheses:
            return "유효한 해결책을 찾지 못했습니다."

        # 가장 높은 신뢰도의 가설을 기반으로 결론 도출
        best_hypothesis = max(validated_hypotheses, key=lambda x: x["validation_score"])

        conclusion = (
            f"{best_hypothesis['element']}의 최적화를 통해 문제를 해결할 수 있습니다. "
        )
        conclusion += (
            f"예상 효과: {best_hypothesis['validation_score']:.1%}의 성능 향상"
        )

        return conclusion

    def execute_strategic_thinking(
        self, problem: str, reasoning: MultiStepReasoning
    ) -> StrategicThinking:
        """전략적 사고 실행"""
        logger.info("🎯 전략적 사고 시작")

        strategy_id = f"strategy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # 문제 분석
        problem_analysis = {
            "core_issue": reasoning.final_conclusion,
            "constraints": ["시간 제약", "리소스 제약", "위험 허용도"],
            "opportunities": ["성능 개선", "학습 효율성 향상", "시스템 안정성"],
            "stakeholders": ["DuRi 시스템", "사용자", "외부 시스템"],
        }

        # 전략적 옵션 생성
        strategic_options = [
            {
                "name": "점진적 개선 전략",
                "description": "단계별로 문제를 해결하며 학습",
                "pros": ["안전성", "학습 효과", "위험 최소화"],
                "cons": ["시간 소요", "점진적 효과"],
                "success_probability": 0.8,
            },
            {
                "name": "혁신적 도약 전략",
                "description": "근본적인 변화를 통한 문제 해결",
                "pros": ["빠른 효과", "혁신적 해결책"],
                "cons": ["높은 위험", "불확실성"],
                "success_probability": 0.4,
            },
            {
                "name": "균형적 접근 전략",
                "description": "안전성과 혁신의 균형",
                "pros": ["안정성", "혁신성", "학습 효과"],
                "cons": ["복잡성", "조정 필요"],
                "success_probability": 0.7,
            },
        ]

        # 최적 전략 선택
        selected_strategy = max(
            strategic_options, key=lambda x: x["success_probability"]
        )

        # 구현 계획 생성
        implementation_plan = [
            "1단계: 현재 상태 분석 및 기준점 설정",
            "2단계: 단기 목표 설정 및 실행",
            "3단계: 중간 결과 평가 및 조정",
            "4단계: 장기 목표 달성 및 검증",
        ]

        # 위험 평가
        risk_assessment = {
            "technical_risk": 0.3,
            "operational_risk": 0.2,
            "learning_risk": 0.1,
            "overall_risk": 0.2,
            "mitigation_strategies": [
                "단계적 실행으로 위험 분산",
                "지속적 모니터링 및 피드백",
                "롤백 계획 수립",
            ],
        }

        strategy = StrategicThinking(
            strategy_id=strategy_id,
            problem_analysis=problem_analysis,
            strategic_options=strategic_options,
            selected_strategy=selected_strategy,
            implementation_plan=implementation_plan,
            risk_assessment=risk_assessment,
        )

        self.strategy_history.append(strategy)
        logger.info(f"✅ 전략적 사고 완료: {strategy_id}")

        return strategy

    def execute_complex_problem_solving(
        self, task: AdvancedLearningTask
    ) -> Dict[str, Any]:
        """복잡한 문제 해결 실행"""
        logger.info(f"🔧 복잡한 문제 해결 시작: {task.task_id}")

        # 1. 다단계 추론 실행
        reasoning = self.execute_multi_step_reasoning(task.problem_description)

        # 2. 전략적 사고 실행
        strategy = self.execute_strategic_thinking(task.problem_description, reasoning)

        # 3. 통찰 엔진 활용
        insight_result = None
        if self.insight_engine:
            insight_result = self.insight_engine.execute_dual_response(
                task.problem_description
            )

        # 4. 결과 종합
        solution = {
            "task_id": task.task_id,
            "problem": task.problem_description,
            "complexity": task.complexity.value,
            "reasoning": reasoning,
            "strategy": strategy,
            "insight": insight_result,
            "solution_summary": f"{reasoning.final_conclusion} + {strategy.selected_strategy['name']}",
            "confidence": (
                reasoning.confidence + strategy.selected_strategy["success_probability"]
            )
            / 2,
            "implementation_steps": strategy.implementation_plan,
            "risk_level": strategy.risk_assessment["overall_risk"],
        }

        # 작업 완료 처리
        self.completed_tasks.append(task)
        self.learning_tasks.remove(task)

        # 능력 향상
        self._enhance_capabilities(task, solution)

        logger.info(f"✅ 복잡한 문제 해결 완료: {task.task_id}")
        return solution

    def _enhance_capabilities(
        self, task: AdvancedLearningTask, solution: Dict[str, Any]
    ):
        """능력 향상"""
        for capability in task.required_capabilities:
            current_level = self.current_capabilities[capability]
            enhancement = 0.05  # 기본 향상량

            # 성공도에 따른 추가 향상
            if solution["confidence"] > 0.7:
                enhancement += 0.02
            if solution["risk_level"] < 0.3:
                enhancement += 0.01

            new_level = min(current_level + enhancement, 1.0)
            self.current_capabilities[capability] = new_level

            logger.info(
                f"📈 {capability.value} 향상: {current_level:.3f} → {new_level:.3f}"
            )

    def get_phase_2_status(self) -> Dict[str, Any]:
        """Phase 2 상태 반환"""
        # completed_tasks는 AdvancedLearningTask 객체들이므로 confidence를 직접 계산할 수 없음
        # 대신 reasoning_history의 평균 confidence 사용
        avg_confidence = 0.0
        if self.reasoning_history:
            avg_confidence = sum(
                reasoning.confidence for reasoning in self.reasoning_history
            ) / len(self.reasoning_history)

        return {
            "current_capabilities": self.current_capabilities,
            "total_tasks": len(self.learning_tasks) + len(self.completed_tasks),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.learning_tasks),
            "reasoning_sessions": len(self.reasoning_history),
            "strategy_sessions": len(self.strategy_history),
            "average_confidence": avg_confidence,
            "phase_1_integration": self.insight_engine is not None,
        }


# 전역 인스턴스
_phase2_system = None


def get_phase2_system() -> Phase2AdvancedLearning:
    """전역 Phase 2 시스템 인스턴스 반환"""
    global _phase2_system
    if _phase2_system is None:
        _phase2_system = Phase2AdvancedLearning()
    return _phase2_system


def initialize_phase_2():
    """Phase 2 초기화"""
    system = get_phase2_system()
    success = system.initialize_phase_1_integration()

    if success:
        logger.info("🚀 Phase 2: 고급 학습 시스템 초기화 완료")
        return system
    else:
        logger.error("❌ Phase 2 초기화 실패")
        return None


if __name__ == "__main__":
    # Phase 2 데모 실행
    system = initialize_phase_2()

    if system:
        # 고급 학습 작업 생성
        task = system.create_advanced_learning_task(
            "학습 루프의 성능 저하와 메모리 사용량 증가 문제를 동시에 해결해야 함",
            ProblemComplexity.COMPLEX,
        )

        # 복잡한 문제 해결 실행
        solution = system.execute_complex_problem_solving(task)

        print(f"🎯 Phase 2 문제 해결 완료:")
        print(f"   작업 ID: {solution['task_id']}")
        print(f"   해결책: {solution['solution_summary']}")
        print(f"   신뢰도: {solution['confidence']:.3f}")
        print(f"   위험도: {solution['risk_level']:.3f}")

        # 상태 확인
        status = system.get_phase_2_status()
        print(f"\n📊 Phase 2 상태: {status}")
    else:
        print("❌ Phase 2 초기화 실패")
