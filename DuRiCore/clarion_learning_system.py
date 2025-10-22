#!/usr/bin/env python3
"""
DuRiCore Phase 6.2.5 - CLARION 이중 학습 시스템
반복-강화 기반 log 학습 루프를 통한 암묵학습 시스템
"""

import asyncio
import json
import logging
import math
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class LearningType(Enum):
    """학습 유형"""

    EXPLICIT = "explicit"  # 명시적 학습
    IMPLICIT = "implicit"  # 암묵적 학습
    HYBRID = "hybrid"  # 혼합 학습


class ReinforcementType(Enum):
    """강화 유형"""

    POSITIVE = "positive"  # 긍정적 강화
    NEGATIVE = "negative"  # 부정적 강화
    NEUTRAL = "neutral"  # 중립적 강화


class LearningPhase(Enum):
    """학습 단계"""

    ACQUISITION = "acquisition"  # 습득 단계
    CONSOLIDATION = "consolidation"  # 통합 단계
    RETRIEVAL = "retrieval"  # 인출 단계
    TRANSFER = "transfer"  # 전이 단계


@dataclass
class LearningPattern:
    """학습 패턴"""

    id: str
    pattern_type: str
    frequency: int
    success_rate: float
    reinforcement_history: List[ReinforcementType]
    learning_phase: LearningPhase
    created_at: str
    last_used: str
    strength: float = 1.0
    decay_rate: float = 0.1


@dataclass
class LearningLog:
    """학습 로그"""

    id: str
    timestamp: str
    learning_type: LearningType
    reinforcement_type: ReinforcementType
    context: Dict[str, Any]
    action: str
    outcome: str
    success: bool
    learning_score: float
    pattern_id: Optional[str] = None


@dataclass
class CLARIONLearningResult:
    """CLARION 학습 결과"""

    learning_type: LearningType
    reinforcement_type: ReinforcementType
    learning_phase: LearningPhase
    pattern_strength: float
    learning_efficiency: float
    transfer_ability: float
    consolidation_level: float
    created_at: str
    success: bool = True


class CLARIONLearningSystem:
    """CLARION 이중 학습 시스템"""

    def __init__(self):
        """초기화"""
        self.learning_patterns = {}
        self.learning_logs = []
        self.reinforcement_history = []
        self.pattern_analyzer = PatternAnalyzer()
        self.reinforcement_engine = ReinforcementEngine()
        self.consolidation_manager = ConsolidationManager()
        self.transfer_analyzer = TransferAnalyzer()

        # CLARION 기반 학습 매개변수
        self.learning_parameters = {
            "explicit_weight": 0.4,
            "implicit_weight": 0.6,
            "reinforcement_decay": 0.95,
            "pattern_threshold": 0.3,
            "consolidation_threshold": 0.7,
            "transfer_threshold": 0.5,
        }

        logger.info("CLARION 이중 학습 시스템 초기화 완료")

    async def process_learning_log(self, log_data: Dict[str, Any]) -> CLARIONLearningResult:
        """학습 로그 처리 및 패턴 분석"""
        try:
            # 1. 로그 데이터 정규화
            normalized_log = self._normalize_log_data(log_data)

            # 2. 학습 유형 결정
            learning_type = await self._determine_learning_type(normalized_log)

            # 3. 강화 유형 결정
            reinforcement_type = await self._determine_reinforcement_type(normalized_log)

            # 4. 패턴 분석 및 생성
            pattern_result = await self.pattern_analyzer.analyze_pattern(
                normalized_log, learning_type
            )

            # 5. 강화 학습 실행
            reinforcement_result = await self.reinforcement_engine.apply_reinforcement(
                pattern_result, reinforcement_type
            )

            # 6. 통합 관리
            consolidation_result = await self.consolidation_manager.manage_consolidation(
                pattern_result, reinforcement_result
            )

            # 7. 전이 분석
            transfer_result = await self.transfer_analyzer.analyze_transfer(
                pattern_result, consolidation_result
            )

            # 8. 학습 결과 생성
            learning_result = self._create_learning_result(
                learning_type,
                reinforcement_type,
                pattern_result,
                reinforcement_result,
                consolidation_result,
                transfer_result,
            )

            # 9. 로그 저장
            await self._save_learning_log(normalized_log, learning_result)

            logger.info(f"학습 로그 처리 완료: {learning_type.value} - {reinforcement_type.value}")
            return learning_result

        except Exception as e:
            logger.error(f"학습 로그 처리 실패: {e}")
            return CLARIONLearningResult(
                learning_type=LearningType.EXPLICIT,
                reinforcement_type=ReinforcementType.NEUTRAL,
                learning_phase=LearningPhase.ACQUISITION,
                pattern_strength=0.0,
                learning_efficiency=0.0,
                transfer_ability=0.0,
                consolidation_level=0.0,
                created_at=datetime.now().isoformat(),
                success=False,
            )

    def _normalize_log_data(self, log_data: Dict[str, Any]) -> Dict[str, Any]:
        """로그 데이터 정규화"""
        normalized = {
            "timestamp": log_data.get("timestamp", datetime.now().isoformat()),
            "context": log_data.get("context", {}),
            "action": log_data.get("action", "unknown"),
            "outcome": log_data.get("outcome", "unknown"),
            "success": log_data.get("success", False),
            "learning_score": log_data.get("learning_score", 0.0),
            "pattern_id": log_data.get("pattern_id"),
            "reinforcement_history": log_data.get("reinforcement_history", []),
        }
        return normalized

    async def _determine_learning_type(self, log_data: Dict[str, Any]) -> LearningType:
        """학습 유형 결정"""
        # 명시적 학습 vs 암묵적 학습 판단
        context_complexity = self._calculate_context_complexity(log_data["context"])
        action_consciousness = self._calculate_action_consciousness(log_data["action"])
        outcome_predictability = self._calculate_outcome_predictability(log_data["outcome"])

        # 명시적 학습 지표
        explicit_indicators = [
            context_complexity > 0.7,
            action_consciousness > 0.6,
            outcome_predictability > 0.5,
        ]

        explicit_score = sum(explicit_indicators) / len(explicit_indicators)

        if explicit_score > self.learning_parameters["explicit_weight"]:
            return LearningType.EXPLICIT
        elif explicit_score < (1 - self.learning_parameters["implicit_weight"]):
            return LearningType.IMPLICIT
        else:
            return LearningType.HYBRID

    async def _determine_reinforcement_type(self, log_data: Dict[str, Any]) -> ReinforcementType:
        """강화 유형 결정"""
        success = log_data["success"]
        learning_score = log_data["learning_score"]

        if success and learning_score > 0.7:
            return ReinforcementType.POSITIVE
        elif not success and learning_score < 0.3:
            return ReinforcementType.NEGATIVE
        else:
            return ReinforcementType.NEUTRAL

    def _calculate_context_complexity(self, context: Dict[str, Any]) -> float:
        """컨텍스트 복잡도 계산"""
        if not context:
            return 0.0

        # 컨텍스트 요소 수와 다양성 기반 복잡도 계산
        element_count = len(context)
        value_diversity = len(set(str(v) for v in context.values()))

        complexity = (element_count * 0.3 + value_diversity * 0.7) / 10.0
        return min(1.0, max(0.0, complexity))

    def _calculate_action_consciousness(self, action: str) -> float:
        """행동 의식성 계산"""
        # 의식적 행동 키워드 기반 판단
        conscious_keywords = [
            "think",
            "plan",
            "analyze",
            "decide",
            "consider",
            "evaluate",
        ]
        unconscious_keywords = ["react", "automatic", "habit", "instinct", "reflex"]

        action_lower = action.lower()

        conscious_count = sum(1 for keyword in conscious_keywords if keyword in action_lower)
        unconscious_count = sum(1 for keyword in unconscious_keywords if keyword in action_lower)

        if conscious_count > unconscious_count:
            return 0.8
        elif unconscious_count > conscious_count:
            return 0.2
        else:
            return 0.5

    def _calculate_outcome_predictability(self, outcome: str) -> float:
        """결과 예측 가능성 계산"""
        # 결과의 명확성과 일관성 기반 판단
        predictable_keywords = ["success", "complete", "achieve", "satisfy", "meet"]
        unpredictable_keywords = ["unexpected", "surprise", "fail", "error", "unknown"]

        outcome_lower = outcome.lower()

        predictable_count = sum(1 for keyword in predictable_keywords if keyword in outcome_lower)
        unpredictable_count = sum(
            1 for keyword in unpredictable_keywords if keyword in outcome_lower
        )

        if predictable_count > unpredictable_count:
            return 0.8
        elif unpredictable_count > predictable_count:
            return 0.2
        else:
            return 0.5

    def _create_learning_result(
        self,
        learning_type: LearningType,
        reinforcement_type: ReinforcementType,
        pattern_result: Dict[str, Any],
        reinforcement_result: Dict[str, Any],
        consolidation_result: Dict[str, Any],
        transfer_result: Dict[str, Any],
    ) -> CLARIONLearningResult:
        """학습 결과 생성"""
        return CLARIONLearningResult(
            learning_type=learning_type,
            reinforcement_type=reinforcement_type,
            learning_phase=consolidation_result.get("learning_phase", LearningPhase.ACQUISITION),
            pattern_strength=pattern_result.get("strength", 0.0),
            learning_efficiency=reinforcement_result.get("efficiency", 0.0),
            transfer_ability=transfer_result.get("ability", 0.0),
            consolidation_level=consolidation_result.get("level", 0.0),
            created_at=datetime.now().isoformat(),
        )

    async def _save_learning_log(
        self, log_data: Dict[str, Any], learning_result: CLARIONLearningResult
    ):
        """학습 로그 저장"""
        learning_log = LearningLog(
            id=str(len(self.learning_logs) + 1),
            timestamp=log_data["timestamp"],
            learning_type=learning_result.learning_type,
            reinforcement_type=learning_result.reinforcement_type,
            context=log_data["context"],
            action=log_data["action"],
            outcome=log_data["outcome"],
            success=log_data["success"],
            learning_score=log_data["learning_score"],
            pattern_id=log_data.get("pattern_id"),
        )

        self.learning_logs.append(learning_log)

    async def analyze_learning_patterns(self) -> Dict[str, Any]:
        """학습 패턴 분석"""
        try:
            # 패턴 빈도 분석
            pattern_frequency = self._analyze_pattern_frequency()

            # 강화 효과 분석
            reinforcement_effectiveness = self._analyze_reinforcement_effectiveness()

            # 학습 단계별 분석
            phase_analysis = self._analyze_learning_phases()

            # 전이 능력 분석
            transfer_analysis = self._analyze_transfer_ability()

            return {
                "pattern_frequency": pattern_frequency,
                "reinforcement_effectiveness": reinforcement_effectiveness,
                "phase_analysis": phase_analysis,
                "transfer_analysis": transfer_analysis,
                "total_patterns": len(self.learning_patterns),
                "total_logs": len(self.learning_logs),
                "analysis_timestamp": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"학습 패턴 분석 실패: {e}")
            return {"error": str(e)}

    def _analyze_pattern_frequency(self) -> Dict[str, Any]:
        """패턴 빈도 분석"""
        if not self.learning_patterns:
            return {"patterns": [], "total_frequency": 0}

        patterns = []
        total_frequency = 0

        for pattern_id, pattern in self.learning_patterns.items():
            patterns.append(
                {
                    "pattern_id": pattern_id,
                    "type": pattern.pattern_type,
                    "frequency": pattern.frequency,
                    "strength": pattern.strength,
                    "success_rate": pattern.success_rate,
                }
            )
            total_frequency += pattern.frequency

        # 빈도순 정렬
        patterns.sort(key=lambda x: x["frequency"], reverse=True)

        return {
            "patterns": patterns,
            "total_frequency": total_frequency,
            "average_frequency": total_frequency / len(patterns) if patterns else 0,
        }

    def _analyze_reinforcement_effectiveness(self) -> Dict[str, Any]:
        """강화 효과 분석"""
        if not self.learning_logs:
            return {"effectiveness": {}, "total_reinforcements": 0}

        reinforcement_counts = {
            ReinforcementType.POSITIVE: 0,
            ReinforcementType.NEGATIVE: 0,
            ReinforcementType.NEUTRAL: 0,
        }

        success_counts = {
            ReinforcementType.POSITIVE: 0,
            ReinforcementType.NEGATIVE: 0,
            ReinforcementType.NEUTRAL: 0,
        }

        for log in self.learning_logs:
            reinforcement_counts[log.reinforcement_type] += 1
            if log.success:
                success_counts[log.reinforcement_type] += 1

        effectiveness = {}
        for reinforcement_type in ReinforcementType:
            total = reinforcement_counts[reinforcement_type]
            success = success_counts[reinforcement_type]
            effectiveness[reinforcement_type.value] = {
                "total": total,
                "success": success,
                "success_rate": success / total if total > 0 else 0,
            }

        return {
            "effectiveness": effectiveness,
            "total_reinforcements": sum(reinforcement_counts.values()),
        }

    def _analyze_learning_phases(self) -> Dict[str, Any]:
        """학습 단계별 분석"""
        phase_counts = {
            LearningPhase.ACQUISITION: 0,
            LearningPhase.CONSOLIDATION: 0,
            LearningPhase.RETRIEVAL: 0,
            LearningPhase.TRANSFER: 0,
        }

        for log in self.learning_logs:
            # 간단한 단계 판단 (실제로는 더 복잡한 로직 필요)
            if log.learning_score < 0.3:
                phase_counts[LearningPhase.ACQUISITION] += 1
            elif log.learning_score < 0.7:
                phase_counts[LearningPhase.CONSOLIDATION] += 1
            elif log.learning_score < 0.9:
                phase_counts[LearningPhase.RETRIEVAL] += 1
            else:
                phase_counts[LearningPhase.TRANSFER] += 1

        return {
            "phase_counts": {phase.value: count for phase, count in phase_counts.items()},
            "total_phases": sum(phase_counts.values()),
        }

    def _analyze_transfer_ability(self) -> Dict[str, Any]:
        """전이 능력 분석"""
        if not self.learning_logs:
            return {"transfer_ability": 0.0, "transfer_patterns": []}

        # 전이 가능성이 높은 패턴들 식별
        transfer_patterns = []
        total_transfer_score = 0.0

        for pattern_id, pattern in self.learning_patterns.items():
            if pattern.strength > self.learning_parameters["transfer_threshold"]:
                transfer_score = pattern.strength * pattern.success_rate
                transfer_patterns.append(
                    {
                        "pattern_id": pattern_id,
                        "type": pattern.pattern_type,
                        "transfer_score": transfer_score,
                        "strength": pattern.strength,
                        "success_rate": pattern.success_rate,
                    }
                )
                total_transfer_score += transfer_score

        return {
            "transfer_ability": (
                total_transfer_score / len(self.learning_patterns)
                if self.learning_patterns
                else 0.0
            ),
            "transfer_patterns": sorted(
                transfer_patterns, key=lambda x: x["transfer_score"], reverse=True
            ),
        }

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "total_patterns": len(self.learning_patterns),
            "total_logs": len(self.learning_logs),
            "learning_parameters": self.learning_parameters,
            "pattern_types": list(
                set(pattern.pattern_type for pattern in self.learning_patterns.values())
            ),
            "reinforcement_types": [rt.value for rt in ReinforcementType],
            "learning_types": [lt.value for lt in LearningType],
            "timestamp": datetime.now().isoformat(),
        }


class PatternAnalyzer:
    """패턴 분석기"""

    async def analyze_pattern(
        self, log_data: Dict[str, Any], learning_type: LearningType
    ) -> Dict[str, Any]:
        """패턴 분석 및 생성"""
        try:
            # 패턴 식별
            pattern_key = self._generate_pattern_key(log_data)

            # 기존 패턴 확인
            if pattern_key in self.parent.learning_patterns:
                pattern = self.parent.learning_patterns[pattern_key]
                # 패턴 강화
                pattern.frequency += 1
                pattern.last_used = datetime.now().isoformat()
                pattern.strength = min(1.0, pattern.strength + 0.1)
            else:
                # 새 패턴 생성
                pattern = LearningPattern(
                    id=pattern_key,
                    pattern_type=learning_type.value,
                    frequency=1,
                    success_rate=1.0 if log_data["success"] else 0.0,
                    reinforcement_history=[
                        log_data.get("reinforcement_type", ReinforcementType.NEUTRAL)
                    ],
                    learning_phase=LearningPhase.ACQUISITION,
                    created_at=datetime.now().isoformat(),
                    last_used=datetime.now().isoformat(),
                    strength=0.5,
                )
                self.parent.learning_patterns[pattern_key] = pattern

            return {
                "pattern_id": pattern_key,
                "strength": pattern.strength,
                "frequency": pattern.frequency,
                "success_rate": pattern.success_rate,
                "learning_phase": pattern.learning_phase,
            }

        except Exception as e:
            logger.error(f"패턴 분석 실패: {e}")
            return {
                "pattern_id": "unknown",
                "strength": 0.0,
                "frequency": 0,
                "success_rate": 0.0,
            }

    def _generate_pattern_key(self, log_data: Dict[str, Any]) -> str:
        """패턴 키 생성"""
        # 컨텍스트, 행동, 결과를 조합하여 패턴 키 생성
        context_str = str(sorted(log_data["context"].items()))
        action_str = log_data["action"]
        outcome_str = log_data["outcome"]

        pattern_str = f"{context_str}|{action_str}|{outcome_str}"
        return str(hash(pattern_str))


class ReinforcementEngine:
    """강화 엔진"""

    async def apply_reinforcement(
        self, pattern_result: Dict[str, Any], reinforcement_type: ReinforcementType
    ) -> Dict[str, Any]:
        """강화 적용"""
        try:
            pattern_id = pattern_result["pattern_id"]
            current_strength = pattern_result["strength"]

            # 강화 유형에 따른 강도 조정
            if reinforcement_type == ReinforcementType.POSITIVE:
                strength_change = 0.1
            elif reinforcement_type == ReinforcementType.NEGATIVE:
                strength_change = -0.05
            else:
                strength_change = 0.0

            # 새로운 강도 계산
            new_strength = max(0.0, min(1.0, current_strength + strength_change))

            # 강화 효과 계산
            efficiency = abs(strength_change) / 0.1  # 최대 강화 효과 대비

            return {
                "pattern_id": pattern_id,
                "old_strength": current_strength,
                "new_strength": new_strength,
                "strength_change": strength_change,
                "efficiency": efficiency,
                "reinforcement_type": reinforcement_type.value,
            }

        except Exception as e:
            logger.error(f"강화 적용 실패: {e}")
            return {"efficiency": 0.0, "reinforcement_type": reinforcement_type.value}


class ConsolidationManager:
    """통합 관리자"""

    async def manage_consolidation(
        self, pattern_result: Dict[str, Any], reinforcement_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """통합 관리"""
        try:
            pattern_strength = pattern_result["strength"]
            frequency = pattern_result["frequency"]

            # 통합 레벨 계산
            consolidation_level = min(1.0, (pattern_strength + frequency * 0.1) / 2.0)

            # 학습 단계 결정
            if consolidation_level < 0.3:
                learning_phase = LearningPhase.ACQUISITION
            elif consolidation_level < 0.7:
                learning_phase = LearningPhase.CONSOLIDATION
            elif consolidation_level < 0.9:
                learning_phase = LearningPhase.RETRIEVAL
            else:
                learning_phase = LearningPhase.TRANSFER

            return {
                "level": consolidation_level,
                "learning_phase": learning_phase,
                "threshold_met": consolidation_level
                > self.parent.learning_parameters["consolidation_threshold"],
            }

        except Exception as e:
            logger.error(f"통합 관리 실패: {e}")
            return {"level": 0.0, "learning_phase": LearningPhase.ACQUISITION}


class TransferAnalyzer:
    """전이 분석기"""

    async def analyze_transfer(
        self, pattern_result: Dict[str, Any], consolidation_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """전이 분석"""
        try:
            pattern_strength = pattern_result["strength"]
            consolidation_level = consolidation_result["level"]

            # 전이 능력 계산
            transfer_ability = (pattern_strength + consolidation_level) / 2.0

            # 전이 가능성 판단
            transfer_possible = (
                transfer_ability > self.parent.learning_parameters["transfer_threshold"]
            )

            return {
                "ability": transfer_ability,
                "possible": transfer_possible,
                "threshold_met": transfer_possible,
            }

        except Exception as e:
            logger.error(f"전이 분석 실패: {e}")
            return {"ability": 0.0, "possible": False}


# 테스트 함수
async def test_clarion_learning_system():
    """CLARION 학습 시스템 테스트"""
    system = CLARIONLearningSystem()

    # 테스트 로그 데이터
    test_logs = [
        {
            "context": {"situation": "problem_solving", "complexity": "high"},
            "action": "analyze_and_plan",
            "outcome": "success",
            "success": True,
            "learning_score": 0.8,
        },
        {
            "context": {"situation": "routine_task", "complexity": "low"},
            "action": "automatic_response",
            "outcome": "success",
            "success": True,
            "learning_score": 0.6,
        },
        {
            "context": {"situation": "new_challenge", "complexity": "medium"},
            "action": "explore_and_learn",
            "outcome": "partial_success",
            "success": False,
            "learning_score": 0.4,
        },
    ]

    # 로그 처리
    results = []
    for log_data in test_logs:
        result = await system.process_learning_log(log_data)
        results.append(result)

    # 패턴 분석
    pattern_analysis = await system.analyze_learning_patterns()

    # 결과 출력
    print("=== CLARION 학습 시스템 테스트 결과 ===")
    print(f"처리된 로그 수: {len(results)}")
    print(f"생성된 패턴 수: {len(system.learning_patterns)}")
    print(f"학습 유형 분포: {pattern_analysis.get('phase_analysis', {}).get('phase_counts', {})}")
    print(
        f"전이 능력: {pattern_analysis.get('transfer_analysis', {}).get('transfer_ability', 0.0):.3f}"
    )


if __name__ == "__main__":
    asyncio.run(test_clarion_learning_system())
