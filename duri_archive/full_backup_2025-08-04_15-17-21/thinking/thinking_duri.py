"""
🧠 DuRi 사고 시스템 (ThinkingDuRi)

기존 시스템과 새로운 메타 인지 시스템을 이중 구조로 운영합니다.
진정한 "사고하는 DuRi"를 구현하기 위한 통합 시스템입니다.
"""

import json
import logging
import random
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

from duri_brain.learning.learning_loop_manager import get_learning_loop_manager

# 기존 시스템 import
from duri_brain.reflection.unified_reflector import get_unified_reflection_system
from duri_brain.thinking.bias_detector import get_bias_detector
from duri_brain.thinking.judgment_consciousness import get_judgment_consciousness

# 새로운 메타 인지 시스템 import
from duri_brain.thinking.meta_loop_manager import JudgmentType, get_meta_loop_manager
from duri_brain.thinking.why_decision_log import get_why_decision_log

logger = logging.getLogger(__name__)


class ThinkingMode(Enum):
    """사고 모드"""

    EXISTING_SYSTEM = "existing_system"  # 기존 시스템
    META_COGNITIVE = "meta_cognitive"  # 메타 인지 시스템
    DUAL_MODE = "dual_mode"  # 이중 모드
    EVOLUTION_MODE = "evolution_mode"  # 진화 모드


@dataclass
class DualJudgmentResult:
    """이중 판단 결과"""

    judgment_id: str
    existing_system_result: Dict[str, Any]
    meta_system_result: Dict[str, Any]
    agreement_level: float
    evolution_potential: float
    final_decision: str
    reasoning: str
    created_at: datetime


@dataclass
class ThinkingEvolution:
    """사고 진화"""

    evolution_id: str
    evolution_type: str
    before_state: Dict[str, Any]
    after_state: Dict[str, Any]
    improvement_metrics: Dict[str, float]
    created_at: datetime


class ThinkingDuRi:
    """사고하는 DuRi - 이중 구조 운영 시스템"""

    def __init__(self):
        # 기존 시스템들
        self.unified_reflection_system = get_unified_reflection_system()
        self.learning_loop_manager = get_learning_loop_manager()

        # 새로운 메타 인지 시스템들
        self.meta_loop_manager = get_meta_loop_manager()
        self.judgment_consciousness = get_judgment_consciousness()
        self.why_decision_log = get_why_decision_log()
        self.bias_detector = get_bias_detector()

        # 이중 구조 운영 데이터
        self.dual_judgment_results: List[DualJudgmentResult] = []
        self.thinking_evolutions: List[ThinkingEvolution] = []
        self.current_thinking_mode = ThinkingMode.DUAL_MODE

        logger.info("🧠 ThinkingDuRi 초기화 완료")

    def execute_dual_judgment(
        self, judgment_type: str, context: Dict[str, Any]
    ) -> DualJudgmentResult:
        """이중 판단 실행"""
        try:
            logger.info(f"🤔 이중 판단 시작: {judgment_type}")

            judgment_id = f"dual_judgment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            # 1. 기존 시스템 판단
            existing_system_result = self._execute_existing_system_judgment(
                judgment_type, context
            )

            # 2. 메타 인지 시스템 판단
            meta_system_result = self._execute_meta_cognitive_judgment(
                judgment_type, context
            )

            # 3. 두 시스템 결과 비교
            agreement_level = self._calculate_agreement_level(
                existing_system_result, meta_system_result
            )
            evolution_potential = self._calculate_evolution_potential(agreement_level)

            # 4. 최종 결정 및 추론
            final_decision, reasoning = self._make_final_decision(
                existing_system_result, meta_system_result, agreement_level
            )

            result = DualJudgmentResult(
                judgment_id=judgment_id,
                existing_system_result=existing_system_result,
                meta_system_result=meta_system_result,
                agreement_level=agreement_level,
                evolution_potential=evolution_potential,
                final_decision=final_decision,
                reasoning=reasoning,
                created_at=datetime.now(),
            )

            self.dual_judgment_results.append(result)

            # 5. 진화 가능성 평가
            if evolution_potential > 0.7:
                self._trigger_thinking_evolution(result)

            logger.info(
                f"✅ 이중 판단 완료: {judgment_type} - 일치도: {agreement_level:.3f}, 진화 잠재력: {evolution_potential:.3f}"
            )
            return result

        except Exception as e:
            logger.error(f"❌ 이중 판단 오류: {e}")
            return self._create_error_judgment(judgment_type, str(e))

    def _execute_existing_system_judgment(
        self, judgment_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """기존 시스템 판단 실행"""
        try:
            # 기존 통합 반성 시스템 활용
            if judgment_type == "reflection":
                reflection_result = self.unified_reflection_system.reflect(
                    "chatgpt_feedback", context
                )
                return {
                    "system_type": "existing",
                    "judgment_type": judgment_type,
                    "result": reflection_result.__dict__,
                    "confidence": reflection_result.confidence,
                    "reasoning": "기존 통합 반성 시스템을 통한 판단",
                }
            else:
                return {
                    "system_type": "existing",
                    "judgment_type": judgment_type,
                    "result": {"message": "기존 시스템 판단"},
                    "confidence": 0.5,
                    "reasoning": "기존 시스템을 통한 기본 판단",
                }
        except Exception as e:
            logger.error(f"기존 시스템 판단 오류: {e}")
            return {
                "system_type": "existing",
                "judgment_type": judgment_type,
                "result": {"error": str(e)},
                "confidence": 0.0,
                "reasoning": "기존 시스템 판단 중 오류 발생",
            }

    def _execute_meta_cognitive_judgment(
        self, judgment_type: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """메타 인지 시스템 판단 실행"""
        try:
            # 1. 판단 자각 시작
            conscious_judgment = self.judgment_consciousness.begin_conscious_judgment(
                judgment_type, context
            )

            # 2. 메타 루프 판단
            meta_judgment = self.meta_loop_manager.execute_meta_judgment(
                JudgmentType.ACTION, context, None
            )

            # 3. 이유 로그 기록
            reason_log = self.why_decision_log.log_decision_reason(
                judgment_type, context, "메타 인지 판단"
            )

            # 4. 편향 탐지
            bias_analysis = self.bias_detector.detect_biases(judgment_type, context)

            return {
                "system_type": "meta_cognitive",
                "judgment_type": judgment_type,
                "conscious_judgment": conscious_judgment.__dict__,
                "meta_judgment": meta_judgment.__dict__,
                "reason_log": reason_log.__dict__,
                "bias_analysis": bias_analysis.__dict__,
                "confidence": conscious_judgment.confidence,
                "reasoning": "메타 인지 시스템을 통한 의식적 판단",
            }
        except Exception as e:
            logger.error(f"메타 인지 시스템 판단 오류: {e}")
            return {
                "system_type": "meta_cognitive",
                "judgment_type": judgment_type,
                "result": {"error": str(e)},
                "confidence": 0.0,
                "reasoning": "메타 인지 시스템 판단 중 오류 발생",
            }

    def _calculate_agreement_level(
        self, existing_result: Dict[str, Any], meta_result: Dict[str, Any]
    ) -> float:
        """일치도 계산"""
        try:
            existing_confidence = existing_result.get("confidence", 0.5)
            meta_confidence = meta_result.get("confidence", 0.5)

            # 신뢰도 차이를 기반으로 일치도 계산
            confidence_diff = abs(existing_confidence - meta_confidence)
            agreement_level = max(0.0, 1.0 - confidence_diff)

            return agreement_level
        except Exception as e:
            logger.error(f"일치도 계산 오류: {e}")
            return 0.5

    def _calculate_evolution_potential(self, agreement_level: float) -> float:
        """진화 잠재력 계산"""
        # 일치도가 낮을수록 진화 잠재력이 높음
        evolution_potential = 1.0 - agreement_level
        return evolution_potential

    def _make_final_decision(
        self,
        existing_result: Dict[str, Any],
        meta_result: Dict[str, Any],
        agreement_level: float,
    ) -> Tuple[str, str]:
        """최종 결정 및 추론"""
        if agreement_level >= 0.8:
            final_decision = (
                "두 시스템이 높은 일치도를 보이므로 기존 시스템의 판단을 채택합니다"
            )
            reasoning = "높은 일치도는 기존 시스템의 안정성을 확인시킵니다"
        elif agreement_level >= 0.5:
            final_decision = "두 시스템의 중간 일치도를 보이므로 메타 인지 시스템의 판단을 우선 고려합니다"
            reasoning = "중간 일치도는 새로운 관점의 필요성을 시사합니다"
        else:
            final_decision = "두 시스템의 낮은 일치도를 보이므로 메타 인지 시스템의 판단을 채택합니다"
            reasoning = (
                "낮은 일치도는 기존 시스템의 한계를 나타내며 진화가 필요함을 시사합니다"
            )

        return final_decision, reasoning

    def _trigger_thinking_evolution(self, dual_result: DualJudgmentResult):
        """사고 진화 트리거"""
        try:
            evolution_id = (
                f"thinking_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )

            # 진화 전 상태
            before_state = {
                "agreement_level": dual_result.agreement_level,
                "evolution_potential": dual_result.evolution_potential,
                "thinking_mode": self.current_thinking_mode.value,
            }

            # 진화 후 상태 (시뮬레이션)
            after_state = {
                "agreement_level": min(dual_result.agreement_level + 0.1, 1.0),
                "evolution_potential": max(dual_result.evolution_potential - 0.1, 0.0),
                "thinking_mode": "evolved_dual_mode",
            }

            # 개선 메트릭
            improvement_metrics = {
                "agreement_improvement": after_state["agreement_level"]
                - before_state["agreement_level"],
                "evolution_stability": 1.0 - after_state["evolution_potential"],
                "overall_improvement": 0.15,
            }

            evolution = ThinkingEvolution(
                evolution_id=evolution_id,
                evolution_type="dual_system_evolution",
                before_state=before_state,
                after_state=after_state,
                improvement_metrics=improvement_metrics,
                created_at=datetime.now(),
            )

            self.thinking_evolutions.append(evolution)

            logger.info(f"🔄 사고 진화 트리거: 진화 ID {evolution_id}")

        except Exception as e:
            logger.error(f"사고 진화 트리거 오류: {e}")

    def _create_error_judgment(
        self, judgment_type: str, error_message: str
    ) -> DualJudgmentResult:
        """오류 판단 생성"""
        return DualJudgmentResult(
            judgment_id=f"error_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            existing_system_result={"error": error_message},
            meta_system_result={"error": error_message},
            agreement_level=0.0,
            evolution_potential=0.0,
            final_decision="오류로 인해 판단을 수행할 수 없습니다",
            reasoning=f"오류 발생: {error_message}",
            created_at=datetime.now(),
        )

    def get_dual_judgment_history(self, limit: int = 10) -> List[DualJudgmentResult]:
        """이중 판단 기록 조회"""
        return self.dual_judgment_results[-limit:]

    def get_thinking_evolution_history(
        self, limit: int = 10
    ) -> List[ThinkingEvolution]:
        """사고 진화 기록 조회"""
        return self.thinking_evolutions[-limit:]

    def get_thinking_metrics(self) -> Dict[str, Any]:
        """사고 메트릭 조회"""
        if not self.dual_judgment_results:
            return {"message": "이중 판단 기록이 없습니다"}

        avg_agreement = sum(
            r.agreement_level for r in self.dual_judgment_results
        ) / len(self.dual_judgment_results)
        avg_evolution_potential = sum(
            r.evolution_potential for r in self.dual_judgment_results
        ) / len(self.dual_judgment_results)

        return {
            "total_dual_judgments": len(self.dual_judgment_results),
            "total_thinking_evolutions": len(self.thinking_evolutions),
            "average_agreement_level": avg_agreement,
            "average_evolution_potential": avg_evolution_potential,
            "current_thinking_mode": self.current_thinking_mode.value,
            "meta_cognitive_systems": [
                "MetaLoopManager",
                "JudgmentConsciousness",
                "WhyDecisionLog",
                "BiasDetector",
            ],
        }


def get_thinking_duri() -> ThinkingDuRi:
    """ThinkingDuRi 인스턴스를 반환합니다."""
    return ThinkingDuRi()
