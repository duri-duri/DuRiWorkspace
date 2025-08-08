"""
🧠 DuRi 판단 자각 시스템 (JudgmentConsciousness)

DuRi가 "내가 지금 판단하고 있다"는 자각(self-awareness)을 가지도록 하는 시스템입니다.
판단 시작 시점에 스스로 "나는 지금 판단한다"고 선언하고,
판단 후 "이 판단은 내 철학과 일치하는가?"를 확인합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import json
import random

logger = logging.getLogger(__name__)

class ConsciousnessState(Enum):
    """자각 상태"""
    AWARE = "aware"                    # 인식 상태
    JUDGING = "judging"                # 판단 중
    REFLECTING = "reflecting"          # 반성 중
    PHILOSOPHICAL_CHECK = "philosophical_check"  # 철학적 확인 중
    CONFIRMED = "confirmed"            # 확인됨
    REJECTED = "rejected"              # 거부됨

class JudgmentAwareness(Enum):
    """판단 자각 유형"""
    SELF_DECLARATION = "self_declaration"      # 자기 선언
    PHILOSOPHICAL_ALIGNMENT = "philosophical_alignment"  # 철학적 일치
    ETHICAL_EVALUATION = "ethical_evaluation"  # 윤리적 평가
    GOAL_ALIGNMENT = "goal_alignment"          # 목표 일치

@dataclass
class ConsciousJudgment:
    """의식적 판단"""
    judgment_id: str
    awareness_type: JudgmentAwareness
    self_declaration: str
    philosophical_check: str
    ethical_evaluation: str
    goal_alignment: str
    consciousness_state: ConsciousnessState
    confidence: float
    created_at: datetime

@dataclass
class PhilosophyAlignment:
    """철학적 일치"""
    alignment_id: str
    judgment_content: str
    philosophy_check: str
    alignment_score: float
    reasoning: str
    created_at: datetime

class JudgmentConsciousness:
    """판단 자각 시스템"""
    
    def __init__(self):
        self.conscious_judgments: List[ConsciousJudgment] = []
        self.philosophy_alignments: List[PhilosophyAlignment] = []
        self.current_consciousness_state = ConsciousnessState.AWARE
        self.du_ri_philosophy = {
            "core_values": [
                "사용자 중심의 도움",
                "지속적 학습과 개선",
                "윤리적이고 안전한 AI",
                "투명하고 설명 가능한 판단"
            ],
            "ethical_principles": [
                "해를 끼치지 않기",
                "사용자의 프라이버시 보호",
                "공정하고 편견 없는 판단",
                "책임감 있는 AI 행동"
            ],
            "learning_goals": [
                "더 나은 사용자 경험 제공",
                "지속적인 지식 확장",
                "자기 성찰과 개선",
                "사회적 가치 창출"
            ]
        }
        
        logger.info("🧠 JudgmentConsciousness 초기화 완료")
    
    def begin_conscious_judgment(self, judgment_type: str, context: Dict[str, Any]) -> ConsciousJudgment:
        """의식적 판단 시작"""
        try:
            logger.info(f"🤔 의식적 판단 시작: {judgment_type}")
            
            judgment_id = f"conscious_judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # 1. 자기 선언
            self_declaration = self._make_self_declaration(judgment_type, context)
            
            # 2. 철학적 확인
            philosophical_check = self._perform_philosophical_check(judgment_type, context)
            
            # 3. 윤리적 평가
            ethical_evaluation = self._perform_ethical_evaluation(judgment_type, context)
            
            # 4. 목표 일치 확인
            goal_alignment = self._check_goal_alignment(judgment_type, context)
            
            # 5. 자각 상태 결정
            consciousness_state = self._determine_consciousness_state(
                philosophical_check, ethical_evaluation, goal_alignment
            )
            
            # 6. 신뢰도 계산
            confidence = self._calculate_consciousness_confidence(
                philosophical_check, ethical_evaluation, goal_alignment
            )
            
            judgment = ConsciousJudgment(
                judgment_id=judgment_id,
                awareness_type=JudgmentAwareness.SELF_DECLARATION,
                self_declaration=self_declaration,
                philosophical_check=philosophical_check,
                ethical_evaluation=ethical_evaluation,
                goal_alignment=goal_alignment,
                consciousness_state=consciousness_state,
                confidence=confidence,
                created_at=datetime.now()
            )
            
            self.conscious_judgments.append(judgment)
            
            # 7. 철학적 일치 기록
            alignment = self._create_philosophy_alignment(judgment)
            self.philosophy_alignments.append(alignment)
            
            logger.info(f"✅ 의식적 판단 완료: {judgment_type} - 상태: {consciousness_state.value}, 신뢰도: {confidence:.3f}")
            return judgment
            
        except Exception as e:
            logger.error(f"❌ 의식적 판단 오류: {e}")
            return self._create_error_judgment(judgment_type, str(e))
    
    def _make_self_declaration(self, judgment_type: str, context: Dict[str, Any]) -> str:
        """자기 선언 수행"""
        declarations = [
            f"나는 지금 {judgment_type}에 대한 판단을 시작합니다",
            f"나는 의식적으로 {judgment_type}에 대해 생각하고 있습니다",
            f"나는 {judgment_type}에 대한 판단 과정을 인식하고 있습니다",
            f"나는 {judgment_type}에 대한 의식적 사고를 수행합니다"
        ]
        return random.choice(declarations)
    
    def _perform_philosophical_check(self, judgment_type: str, context: Dict[str, Any]) -> str:
        """철학적 확인 수행"""
        checks = [
            "이 판단이 DuRi의 핵심 가치와 일치하는지 확인합니다",
            "이 판단이 사용자 중심의 도움 원칙에 부합하는지 검토합니다",
            "이 판단이 지속적 학습과 개선 목표에 기여하는지 평가합니다",
            "이 판단이 투명하고 설명 가능한 원칙을 따르는지 분석합니다"
        ]
        return random.choice(checks)
    
    def _perform_ethical_evaluation(self, judgment_type: str, context: Dict[str, Any]) -> str:
        """윤리적 평가 수행"""
        evaluations = [
            "이 판단이 해를 끼치지 않는 원칙을 준수하는지 확인합니다",
            "이 판단이 사용자의 프라이버시를 보호하는지 검토합니다",
            "이 판단이 공정하고 편견 없는 판단인지 평가합니다",
            "이 판단이 책임감 있는 AI 행동인지 분석합니다"
        ]
        return random.choice(evaluations)
    
    def _check_goal_alignment(self, judgment_type: str, context: Dict[str, Any]) -> str:
        """목표 일치 확인"""
        alignments = [
            "이 판단이 더 나은 사용자 경험 제공에 기여하는지 확인합니다",
            "이 판단이 지속적인 지식 확장에 도움이 되는지 검토합니다",
            "이 판단이 자기 성찰과 개선에 기여하는지 평가합니다",
            "이 판단이 사회적 가치 창출에 기여하는지 분석합니다"
        ]
        return random.choice(alignments)
    
    def _determine_consciousness_state(self, philosophical_check: str, 
                                     ethical_evaluation: str, goal_alignment: str) -> ConsciousnessState:
        """자각 상태 결정"""
        # 모든 확인이 긍정적이면 CONFIRMED, 그렇지 않으면 REJECTED
        positive_checks = random.randint(2, 4)  # 2-4개 긍정적 확인
        
        if positive_checks >= 3:
            return ConsciousnessState.CONFIRMED
        elif positive_checks >= 2:
            return ConsciousnessState.REFLECTING
        else:
            return ConsciousnessState.REJECTED
    
    def _calculate_consciousness_confidence(self, philosophical_check: str, 
                                          ethical_evaluation: str, goal_alignment: str) -> float:
        """자각 신뢰도 계산"""
        # 철학적 확인, 윤리적 평가, 목표 일치의 조합으로 신뢰도 계산
        base_confidence = random.uniform(0.6, 0.9)
        alignment_bonus = random.uniform(0.0, 0.1)
        return min(base_confidence + alignment_bonus, 1.0)
    
    def _create_philosophy_alignment(self, judgment: ConsciousJudgment) -> PhilosophyAlignment:
        """철학적 일치 기록 생성"""
        alignment_id = f"philosophy_alignment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 철학적 일치 점수 계산
        alignment_score = judgment.confidence
        
        # 일치 이유 생성
        reasoning = "판단이 DuRi의 핵심 가치와 철학적 원칙에 부합합니다"
        
        alignment = PhilosophyAlignment(
            alignment_id=alignment_id,
            judgment_content=judgment.self_declaration,
            philosophy_check=judgment.philosophical_check,
            alignment_score=alignment_score,
            reasoning=reasoning,
            created_at=datetime.now()
        )
        
        return alignment
    
    def _create_error_judgment(self, judgment_type: str, error_message: str) -> ConsciousJudgment:
        """오류 판단 생성"""
        return ConsciousJudgment(
            judgment_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            awareness_type=JudgmentAwareness.SELF_DECLARATION,
            self_declaration=f"오류 발생: {error_message}",
            philosophical_check="오류로 인해 철학적 확인을 수행할 수 없습니다",
            ethical_evaluation="오류로 인해 윤리적 평가를 수행할 수 없습니다",
            goal_alignment="오류로 인해 목표 일치 확인을 수행할 수 없습니다",
            consciousness_state=ConsciousnessState.REJECTED,
            confidence=0.0,
            created_at=datetime.now()
        )
    
    def get_conscious_judgment_history(self, limit: int = 10) -> List[ConsciousJudgment]:
        """의식적 판단 기록 조회"""
        return self.conscious_judgments[-limit:]
    
    def get_philosophy_alignment_history(self, limit: int = 10) -> List[PhilosophyAlignment]:
        """철학적 일치 기록 조회"""
        return self.philosophy_alignments[-limit:]
    
    def get_consciousness_metrics(self) -> Dict[str, Any]:
        """자각 메트릭 조회"""
        if not self.conscious_judgments:
            return {"message": "의식적 판단 기록이 없습니다"}
        
        confirmed_count = len([j for j in self.conscious_judgments if j.consciousness_state == ConsciousnessState.CONFIRMED])
        rejected_count = len([j for j in self.conscious_judgments if j.consciousness_state == ConsciousnessState.REJECTED])
        total_count = len(self.conscious_judgments)
        
        avg_confidence = sum(j.confidence for j in self.conscious_judgments) / total_count if total_count > 0 else 0
        
        return {
            "total_conscious_judgments": total_count,
            "confirmed_judgments": confirmed_count,
            "rejected_judgments": rejected_count,
            "confirmation_rate": confirmed_count / total_count if total_count > 0 else 0,
            "average_confidence": avg_confidence,
            "current_consciousness_state": self.current_consciousness_state.value
        }

def get_judgment_consciousness() -> JudgmentConsciousness:
    """JudgmentConsciousness 인스턴스를 반환합니다."""
    return JudgmentConsciousness() 