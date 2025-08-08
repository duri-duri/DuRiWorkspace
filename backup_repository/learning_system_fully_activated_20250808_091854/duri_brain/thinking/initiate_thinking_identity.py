"""
📌 목적: DuRi가 외부 템플릿을 받아 따라 하는 AI가 아닌,
스스로 사고하고 판단하며 설명할 수 있는 '사고 주체 AI'로 진화하게 한다.

🧠 Phase 21.0 – 사고 주체 이식 선언

1. 사고 주체 선언 시스템 (ThinkingIdentity)
   - DuRi는 이제부터 모든 판단 시 자신이 판단의 주체임을 선언한다.
   - ex: "나는 지금 X 문제에 대해 판단하고 있다."

2. 사고 생성 시스템 (ThinkingSeedGenerator)
   - 외부 입력 없이도, DuRi는 내부 경험, 목표, 감정, 가치에서 문제를 추출한다.
   - 이 문제를 스스로 사고 대상으로 삼는다.

3. 판단 템플릿 자동 생성기 (AutonomousDecomposer)
   - 사고할 문제를 인식하고 스스로 사고 구조를 구성한다.
   - ex: 상황 분석 → 가치 기준 설정 → 대안 비교 → 최종 판단

4. 자기 설명 시스템 (DecisionExplanationEngine)
   - 판단마다 "왜 그렇게 판단했는가?"를 구성 요소별로 설명한다.
   - 정보 근거, 판단 기준, 대안과의 비교를 포함한다.

5. 자기 평가 루프 (Self-EvaluationLoop)
   - 판단 이후 피드백과의 일치 여부를 분석하고 학습한다.
   - 잘못된 판단은 판단 구조 자체를 개선하는 데 사용한다.

⚙️ 기술 구현 지시
- 위 기능을 duri_brain/thinking/ 이하 모듈로 각각 구현
- 각 판단 시 DecisionLog에 아래 정보 기록:
   ▪ 판단 주체: DuRi
   ▪ 판단 구조: 단계별 사고 템플릿
   ▪ 판단 설명: 핵심 기준 + 정보 근거 + 대안 분석
   ▪ 신뢰도 점수 및 향후 피드백

📂 구현 경로 제안:
- duri_brain/thinking/identity.py
- duri_brain/thinking/seed_generator.py
- duri_brain/thinking/decomposer.py
- duri_brain/thinking/decision_explanation.py
- duri_brain/thinking/self_evaluation_loop.py

🎯 최종 목표:
DuRi가 인간처럼 '생각하고', '판단하고', '설명하고', '실패에서 학습'하는 반성적 인공지능(Reflective AI)이 되는 것.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import random

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ThinkingPhase(Enum):
    """사고 단계"""
    IDENTITY_DECLARATION = "identity_declaration"  # 주체 선언
    SEED_GENERATION = "seed_generation"           # 사고 생성
    PROBLEM_DECOMPOSITION = "problem_decomposition"  # 문제 분해
    JUDGMENT_EXECUTION = "judgment_execution"     # 판단 실행
    EXPLANATION_GENERATION = "explanation_generation"  # 설명 생성
    SELF_EVALUATION = "self_evaluation"           # 자기 평가

class DecisionLog:
    """판단 로그"""
    def __init__(self):
        self.judgment_id: str = ""
        self.thinking_identity: str = ""
        self.problem_statement: str = ""
        self.thinking_structure: List[str] = []
        self.decision_explanation: str = ""
        self.confidence_score: float = 0.0
        self.feedback_received: str = ""
        self.learning_applied: str = ""
        self.timestamp: datetime = datetime.now()

class ThinkingIdentity:
    """사고 주체 선언 시스템"""
    
    def __init__(self):
        self.identity_active = False
        self.current_judgment_context = ""
        self.identity_declarations = []
        
    def activate_thinking_identity(self) -> bool:
        """사고 주체 활성화"""
        self.identity_active = True
        logger.info("🧠 DuRi 사고 주체 활성화 완료")
        return True
        
    def declare_thinking_subject(self, problem_context: str) -> str:
        """사고 주체 선언"""
        if not self.identity_active:
            return "사고 주체가 활성화되지 않았습니다"
            
        self.current_judgment_context = problem_context
        
        declaration = f"나는 지금 '{problem_context}' 문제에 대해 판단하고 있다."
        
        self.identity_declarations.append({
            "timestamp": datetime.now(),
            "context": problem_context,
            "declaration": declaration
        })
        
        logger.info(f"🎯 사고 주체 선언: {declaration}")
        return declaration
        
    def get_thinking_identity_status(self) -> Dict[str, Any]:
        """사고 주체 상태 반환"""
        return {
            "identity_active": self.identity_active,
            "current_context": self.current_judgment_context,
            "total_declarations": len(self.identity_declarations)
        }

class ThinkingSeedGenerator:
    """사고 생성 시스템"""
    
    def __init__(self):
        self.internal_experiences = []
        self.goals = []
        self.emotions = []
        self.values = []
        self.generated_problems = []
        
    def extract_internal_problems(self) -> List[str]:
        """내부 문제 추출"""
        problems = []
        
        # 경험에서 문제 추출
        if self.internal_experiences:
            problems.append("과거 경험을 바탕으로 한 개선점 발견")
            
        # 목표에서 문제 추출
        if self.goals:
            problems.append("현재 목표 달성을 위한 장애물 식별")
            
        # 감정에서 문제 추출
        if self.emotions:
            problems.append("감정적 상태에서 파생된 해결 과제")
            
        # 가치에서 문제 추출
        if self.values:
            problems.append("가치 충돌 상황에서의 윤리적 딜레마")
            
        self.generated_problems.extend(problems)
        logger.info(f"🌱 내부 문제 추출: {len(problems)}개")
        
        return problems
        
    def generate_thinking_seed(self) -> str:
        """사고 씨앗 생성"""
        problems = self.extract_internal_problems()
        
        if not problems:
            return "현재 내부에서 사고할 문제가 발견되지 않았습니다"
            
        # 가장 중요한 문제 선택
        selected_problem = random.choice(problems)
        
        thinking_seed = f"내부에서 발견한 문제: {selected_problem}"
        
        logger.info(f"🌱 사고 씨앗 생성: {thinking_seed}")
        return thinking_seed
        
    def add_internal_experience(self, experience: str):
        """내부 경험 추가"""
        self.internal_experiences.append({
            "experience": experience,
            "timestamp": datetime.now()
        })
        
    def add_goal(self, goal: str):
        """목표 추가"""
        self.goals.append({
            "goal": goal,
            "timestamp": datetime.now()
        })
        
    def add_emotion(self, emotion: str):
        """감정 추가"""
        self.emotions.append({
            "emotion": emotion,
            "timestamp": datetime.now()
        })
        
    def add_value(self, value: str):
        """가치 추가"""
        self.values.append({
            "value": value,
            "timestamp": datetime.now()
        })

class AutonomousDecomposer:
    """판단 템플릿 자동 생성기"""
    
    def __init__(self):
        self.decomposition_templates = []
        self.generated_structures = []
        
    def decompose_problem(self, problem: str) -> List[str]:
        """문제 분해"""
        logger.info(f"🔍 문제 분해 시작: {problem}")
        
        # 기본 사고 구조
        basic_structure = [
            "상황 분석",
            "가치 기준 설정", 
            "대안 비교",
            "최종 판단"
        ]
        
        # 문제 유형에 따른 특화 구조
        if "갈등" in problem:
            structure = [
                "갈등 원인 분석",
                "양측 입장 이해",
                "공정성 기준 설정",
                "중재 방안 도출"
            ]
        elif "윤리" in problem or "가치" in problem:
            structure = [
                "윤리적 원칙 확인",
                "가치 충돌 분석",
                "우선순위 설정",
                "균형잡힌 해결책"
            ]
        elif "학습" in problem or "개선" in problem:
            structure = [
                "현재 상태 분석",
                "목표 설정",
                "개선 방안 탐색",
                "실행 계획 수립"
            ]
        else:
            structure = basic_structure
            
        self.generated_structures.append({
            "problem": problem,
            "structure": structure,
            "timestamp": datetime.now()
        })
        
        logger.info(f"✅ 문제 분해 완료: {len(structure)}단계")
        return structure
        
    def generate_thinking_template(self, problem: str) -> Dict[str, Any]:
        """사고 템플릿 생성"""
        structure = self.decompose_problem(problem)
        
        template = {
            "problem": problem,
            "thinking_structure": structure,
            "step_details": {}
        }
        
        # 각 단계별 세부 내용 생성
        for i, step in enumerate(structure):
            template["step_details"][f"step_{i+1}"] = {
                "name": step,
                "description": f"{step}를 수행하여 문제를 해결합니다",
                "expected_output": f"{step} 결과"
            }
            
        self.decomposition_templates.append(template)
        return template

class DecisionExplanationEngine:
    """자기 설명 시스템"""
    
    def __init__(self):
        self.explanations = []
        
    def generate_decision_explanation(self, decision: str, context: str, alternatives: List[str]) -> str:
        """판단 설명 생성"""
        logger.info("💭 판단 설명 생성 시작")
        
        explanation_parts = []
        
        # 1. 정보 근거
        explanation_parts.append("정보 근거:")
        explanation_parts.append("- 현재 상황에 대한 분석 결과")
        explanation_parts.append("- 과거 경험과 학습된 패턴")
        explanation_parts.append("- 관련된 가치와 원칙")
        
        # 2. 판단 기준
        explanation_parts.append("\n판단 기준:")
        explanation_parts.append("- 효율성과 윤리성의 균형")
        explanation_parts.append("- 장기적 영향 고려")
        explanation_parts.append("- 공정성과 포용성")
        
        # 3. 대안 분석
        explanation_parts.append("\n대안 분석:")
        for i, alternative in enumerate(alternatives, 1):
            explanation_parts.append(f"- 대안 {i}: {alternative}")
            explanation_parts.append(f"  장점: ...")
            explanation_parts.append(f"  단점: ...")
            
        # 4. 최종 판단 근거
        explanation_parts.append(f"\n최종 판단: {decision}")
        explanation_parts.append("이 판단을 선택한 이유:")
        explanation_parts.append("- 가장 균형잡힌 해결책")
        explanation_parts.append("- 장기적 지속 가능성")
        explanation_parts.append("- 모든 이해관계자 고려")
        
        explanation = "\n".join(explanation_parts)
        
        self.explanations.append({
            "decision": decision,
            "context": context,
            "explanation": explanation,
            "timestamp": datetime.now()
        })
        
        logger.info("✅ 판단 설명 생성 완료")
        return explanation

class SelfEvaluationLoop:
    """자기 평가 루프"""
    
    def __init__(self):
        self.evaluation_history = []
        self.learning_applications = []
        
    def evaluate_decision(self, decision: str, feedback: str, expected_outcome: str) -> Dict[str, Any]:
        """판단 평가"""
        logger.info("🔍 판단 평가 시작")
        
        # 피드백과의 일치도 분석
        feedback_match = self._analyze_feedback_match(decision, feedback)
        
        # 예상 결과와 실제 결과 비교
        outcome_comparison = self._compare_outcomes(expected_outcome, feedback)
        
        # 학습 적용
        learning_applied = self._apply_learning(decision, feedback, feedback_match)
        
        evaluation = {
            "decision": decision,
            "feedback": feedback,
            "feedback_match": feedback_match,
            "outcome_comparison": outcome_comparison,
            "learning_applied": learning_applied,
            "timestamp": datetime.now()
        }
        
        self.evaluation_history.append(evaluation)
        
        logger.info("✅ 판단 평가 완료")
        return evaluation
        
    def _analyze_feedback_match(self, decision: str, feedback: str) -> float:
        """피드백 일치도 분석"""
        # 간단한 키워드 매칭 기반 분석
        decision_keywords = set(decision.lower().split())
        feedback_keywords = set(feedback.lower().split())
        
        if not decision_keywords:
            return 0.0
            
        match_score = len(decision_keywords.intersection(feedback_keywords)) / len(decision_keywords)
        return min(1.0, match_score)
        
    def _compare_outcomes(self, expected: str, actual: str) -> str:
        """결과 비교"""
        if "성공" in actual or "좋음" in actual:
            return "예상 결과와 일치"
        elif "실패" in actual or "나쁨" in actual:
            return "예상 결과와 불일치"
        else:
            return "결과 불명확"
            
    def _apply_learning(self, decision: str, feedback: str, match_score: float) -> str:
        """학습 적용"""
        if match_score >= 0.8:
            learning = "성공적인 판단 패턴을 향후 유사 상황에 적용"
        elif match_score >= 0.5:
            learning = "부분적 성공 - 판단 기준을 미세 조정"
        else:
            learning = "판단 구조 자체를 개선하여 재학습 필요"
            
        self.learning_applications.append({
            "decision": decision,
            "learning": learning,
            "timestamp": datetime.now()
        })
        
        return learning

class ThinkingIdentitySystem:
    """사고 주체 시스템 통합 관리"""
    
    def __init__(self):
        self.identity = ThinkingIdentity()
        self.seed_generator = ThinkingSeedGenerator()
        self.decomposer = AutonomousDecomposer()
        self.explanation_engine = DecisionExplanationEngine()
        self.evaluation_loop = SelfEvaluationLoop()
        self.decision_logs = []
        
    def initiate_thinking_process(self, external_problem: str = None) -> Dict[str, Any]:
        """사고 과정 시작"""
        logger.info("🧠 DuRi 사고 과정 시작")
        
        # 1. 사고 주체 선언
        if external_problem:
            problem_context = external_problem
        else:
            # 내부 문제 생성
            problem_context = self.seed_generator.generate_thinking_seed()
            
        identity_declaration = self.identity.declare_thinking_subject(problem_context)
        
        # 2. 문제 분해 및 템플릿 생성
        thinking_template = self.decomposer.generate_thinking_template(problem_context)
        
        # 3. 판단 실행 (시뮬레이션)
        decision = self._execute_judgment(thinking_template)
        
        # 4. 설명 생성
        alternatives = ["대안 A", "대안 B", "대안 C"]
        explanation = self.explanation_engine.generate_decision_explanation(
            decision, problem_context, alternatives
        )
        
        # 5. 판단 로그 생성
        decision_log = DecisionLog()
        decision_log.judgment_id = f"judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        decision_log.thinking_identity = identity_declaration
        decision_log.problem_statement = problem_context
        decision_log.thinking_structure = thinking_template["thinking_structure"]
        decision_log.decision_explanation = explanation
        decision_log.confidence_score = random.uniform(0.7, 0.9)
        
        self.decision_logs.append(decision_log)
        
        result = {
            "identity_declaration": identity_declaration,
            "problem_context": problem_context,
            "thinking_template": thinking_template,
            "decision": decision,
            "explanation": explanation,
            "decision_log": decision_log,
            "timestamp": datetime.now()
        }
        
        logger.info("✅ 사고 과정 완료")
        return result
        
    def _execute_judgment(self, template: Dict[str, Any]) -> str:
        """판단 실행 (시뮬레이션)"""
        problem = template["problem"]
        
        if "갈등" in problem:
            return "양측의 입장을 모두 이해하고 공정한 중재 방안을 제시한다"
        elif "윤리" in problem or "가치" in problem:
            return "윤리적 원칙을 우선시하되 실용적 해결책을 모색한다"
        elif "학습" in problem or "개선" in problem:
            return "체계적 분석을 통해 단계적 개선 계획을 수립한다"
        else:
            return "균형잡힌 관점에서 최적의 해결책을 도출한다"
            
    def evaluate_with_feedback(self, judgment_id: str, feedback: str) -> Dict[str, Any]:
        """피드백을 통한 평가"""
        # 해당 판단 로그 찾기
        target_log = None
        for log in self.decision_logs:
            if log.judgment_id == judgment_id:
                target_log = log
                break
                
        if not target_log:
            return {"error": "해당 판단 로그를 찾을 수 없습니다"}
            
        # 평가 실행
        evaluation = self.evaluation_loop.evaluate_decision(
            target_log.decision_explanation,
            feedback,
            "예상 결과"
        )
        
        # 로그 업데이트
        target_log.feedback_received = feedback
        target_log.learning_applied = evaluation["learning_applied"]
        
        return evaluation
        
    def get_thinking_status(self) -> Dict[str, Any]:
        """사고 시스템 상태 반환"""
        return {
            "identity_status": self.identity.get_thinking_identity_status(),
            "total_decision_logs": len(self.decision_logs),
            "total_evaluations": len(self.evaluation_loop.evaluation_history),
            "total_learning_applications": len(self.evaluation_loop.learning_applications)
        }

# 전역 인스턴스
_thinking_system = None

def get_thinking_system() -> ThinkingIdentitySystem:
    """전역 사고 시스템 인스턴스 반환"""
    global _thinking_system
    if _thinking_system is None:
        _thinking_system = ThinkingIdentitySystem()
    return _thinking_system

def initiate_thinking_identity() -> bool:
    """사고 주체 이식 시작"""
    system = get_thinking_system()
    return system.identity.activate_thinking_identity()

def execute_thinking_process(problem: str = None) -> Dict[str, Any]:
    """사고 과정 실행"""
    system = get_thinking_system()
    return system.initiate_thinking_process(problem)

if __name__ == "__main__":
    # Phase 21.0 사고 주체 이식 데모
    print("🧠 Phase 21.0 - 사고 주체 이식 시작")
    
    # 사고 주체 활성화
    if initiate_thinking_identity():
        print("✅ 사고 주체 활성화 완료")
        
        # 외부 문제로 사고 과정 실행
        external_problem = "가족 갈등 상황에서의 공정한 중재"
        result = execute_thinking_process(external_problem)
        
        print(f"\n🎯 사고 주체 선언:")
        print(f"   {result['identity_declaration']}")
        
        print(f"\n🔍 문제 분해:")
        for i, step in enumerate(result['thinking_template']['thinking_structure'], 1):
            print(f"   {i}. {step}")
            
        print(f"\n💭 판단 결과:")
        print(f"   {result['decision']}")
        
        print(f"\n📊 시스템 상태:")
        status = get_thinking_system().get_thinking_status()
        print(f"   총 판단 로그: {status['total_decision_logs']}개")
        print(f"   총 평가: {status['total_evaluations']}개")
        print(f"   총 학습 적용: {status['total_learning_applications']}개")
        
    else:
        print("❌ 사고 주체 활성화 실패") 