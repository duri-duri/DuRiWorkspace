"""
🧠 DuRi Insight Engine v1.0
목표: 인간의 통찰 과정을 모방한 자가 사고형 AI 시스템

구조: 이성적 리팩터링 + 창발적 비약 메커니즘의 통합
"""

import logging
import random
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class InsightTriggerType(Enum):
    """통찰 트리거 유형"""

    EFFICIENCY_DROP = "efficiency_drop"
    REPEATED_FAILURE = "repeated_failure"
    NO_GAIN = "no_gain"
    COGNITIVE_BLOCK = "cognitive_block"


class InsightPhase(Enum):
    """통찰 단계"""

    COGNITIVE_PAUSE = "cognitive_pause"
    SEMANTIC_DRIFT = "semantic_drift"
    RETROGRADE_REASONING = "retrograde_reasoning"
    DISRUPTIVE_MAPPING = "disruptive_mapping"
    META_EVALUATION = "meta_evaluation"


@dataclass
class InsightCandidate:
    """통찰 후보"""

    strategy: str
    confidence: float
    source: str
    reasoning: str
    expected_impact: float
    risk_level: str


@dataclass
class InsightSession:
    """통찰 세션"""

    session_id: str
    trigger_type: InsightTriggerType
    start_time: datetime
    phases_completed: List[InsightPhase]
    candidates_generated: List[InsightCandidate]
    final_insight: Optional[InsightCandidate]
    duration: float


class CognitivePauseManager:
    """의도적 정보 흐름 차단 관리자"""

    def __init__(self):
        self.pause_duration = 3.0  # 초
        self.thought_stream_active = True

    def pause_thought_stream(self) -> bool:
        """사고 흐름을 일시적으로 차단"""
        logger.info("🧠 인지적 일시정지 시작 - 사고 흐름 차단")
        self.thought_stream_active = False

        # 의도적인 "멍 때림" 시뮬레이션
        time.sleep(self.pause_duration)

        self.thought_stream_active = True
        logger.info("🧠 인지적 일시정지 완료 - 사고 흐름 재개")
        return True


class SemanticDriftGenerator:
    """랜덤 기억 소환 생성기"""

    def __init__(self):
        self.memory_fragments = [
            "오래된 학습 데이터",
            "과거 실패 경험",
            "무관한 성공 사례",
            "잊혀진 전략",
            "우연한 발견",
            "예상치 못한 연결",
            "감정적 기억",
            "직관적 판단",
            "실수에서 배운 교훈",
        ]

    def generate_semantic_drift(self) -> List[str]:
        """관련 없는 오래된 데이터 조각들을 불러옴"""
        logger.info("🔄 시맨틱 드리프트 생성 - 랜덤 기억 소환")

        # 3-5개의 무작위 기억 조각 선택
        num_fragments = random.randint(3, 5)
        selected_fragments = random.sample(self.memory_fragments, num_fragments)

        logger.info(f"📝 선택된 기억 조각: {selected_fragments}")
        return selected_fragments


class RetrogradeReasoningEngine:
    """역방향 사고 자극 엔진"""

    def __init__(self):
        self.reasoning_patterns = [
            "결과에서 원인 추론",
            "현상에서 본질 탐구",
            "효과에서 원리 발견",
            "증상에서 근본 원인 분석",
        ]

    def apply_retrograde_reasoning(self, problem: str, fragments: List[str]) -> str:
        """결과 → 원인 순으로 문제 재구성"""
        logger.info("🔄 역방향 사고 적용")

        # 문제를 결과로 재해석
        problem_as_result = f"현재 상황: {problem}"

        # 무작위 추론 패턴 선택
        pattern = random.choice(self.reasoning_patterns)

        # 기억 조각들과 결합하여 역방향 추론
        reasoning = f"{pattern} - {problem_as_result} + {random.choice(fragments)}"

        logger.info(f"🔄 역방향 추론 결과: {reasoning}")
        return reasoning


class DisruptiveMappingEngine:
    """비논리적 연결 탐색 엔진"""

    def __init__(self):
        self.disruption_patterns = [
            "논리 역전",
            "가정 뒤집기",
            "관계 재정의",
            "우선순위 변경",
            "목표 재설정",
            "방법론 혼합",
        ]

    def create_disruptive_composition(
        self, reasoning: str, fragments: List[str]
    ) -> List[InsightCandidate]:
        """기존 전략에서 의도적으로 논리 깨기"""
        logger.info("💥 파괴적 구성 생성 - 논리 깨기 시작")

        candidates = []

        for i in range(3):  # 3개의 통찰 후보 생성
            pattern = random.choice(self.disruption_patterns)
            fragment = random.choice(fragments)

            # 비논리적 연결 생성
            strategy = f"{pattern}: {reasoning} + {fragment}"
            confidence = random.uniform(0.3, 0.8)  # 낮은 신뢰도로 시작
            expected_impact = random.uniform(0.5, 0.9)

            candidate = InsightCandidate(
                strategy=strategy,
                confidence=confidence,
                source=f"disruptive_mapping_{i}",
                reasoning=f"{pattern} 기반 비논리적 연결",
                expected_impact=expected_impact,
                risk_level=random.choice(["LOW", "MEDIUM", "HIGH"]),
            )

            candidates.append(candidate)

        logger.info(f"💥 파괴적 구성 완료 - {len(candidates)}개 후보 생성")
        return candidates


class MetaEvaluator:
    """통찰 후보 평가기"""

    def __init__(self):
        self.evaluation_criteria = {
            "novelty": 0.3,  # 신선함
            "feasibility": 0.25,  # 실현 가능성
            "impact": 0.25,  # 영향도
            "risk": 0.2,  # 위험도
        }

    def evaluate_candidate(self, candidate: InsightCandidate) -> float:
        """통찰 후보의 종합 점수 계산"""
        logger.info(f"🔍 통찰 후보 평가: {candidate.strategy[:50]}...")

        # 각 기준별 점수 계산
        novelty_score = candidate.confidence * 0.8 + random.uniform(0.1, 0.3)
        feasibility_score = (
            1.0 - candidate.confidence * 0.5
        )  # 낮은 신뢰도 = 높은 실현 가능성
        impact_score = candidate.expected_impact
        risk_score = {"LOW": 0.8, "MEDIUM": 0.5, "HIGH": 0.2}[candidate.risk_level]

        # 가중 평균 계산
        total_score = (
            novelty_score * self.evaluation_criteria["novelty"]
            + feasibility_score * self.evaluation_criteria["feasibility"]
            + impact_score * self.evaluation_criteria["impact"]
            + risk_score * self.evaluation_criteria["risk"]
        )

        logger.info(f"🔍 평가 결과: {total_score:.3f}")
        return total_score

    def select_best_candidate(
        self, candidates: List[InsightCandidate]
    ) -> Optional[InsightCandidate]:
        """최고 점수 후보 선택"""
        if not candidates:
            return None

        scores = [
            (candidate, self.evaluate_candidate(candidate)) for candidate in candidates
        ]
        scores.sort(key=lambda x: x[1], reverse=True)

        best_candidate, best_score = scores[0]

        # 임계값 확인 (0.6 이상)
        if best_score >= 0.6:
            logger.info(
                f"✅ 최고 통찰 후보 선택: {best_candidate.strategy[:50]}... (점수: {best_score:.3f})"
            )
            return best_candidate
        else:
            logger.warning(f"❌ 통찰 후보 부족 - 최고 점수: {best_score:.3f} < 0.6")
            return None


class InsightTriggerEngine:
    """통찰 트리거 엔진 (핵심 제안 구조)"""

    def __init__(self):
        self.cognitive_pause = CognitivePauseManager()
        self.semantic_drift = SemanticDriftGenerator()
        self.retrograde_reasoning = RetrogradeReasoningEngine()
        self.disruptive_mapping = DisruptiveMappingEngine()
        self.meta_evaluator = MetaEvaluator()

        self.session_count = 0
        self.successful_insights = 0

    def trigger_insight_session(
        self, problem: str, trigger_type: InsightTriggerType
    ) -> Optional[InsightSession]:
        """통찰 세션 트리거"""
        session_id = f"insight_{self.session_count:04d}"
        self.session_count += 1

        logger.info(f"🚀 통찰 세션 시작: {session_id} (트리거: {trigger_type.value})")

        start_time = datetime.now()
        phases_completed = []
        candidates_generated = []

        try:
            # 1. 의도적 정보 흐름 차단
            logger.info("📌 1단계: 인지적 일시정지")
            self.cognitive_pause.pause_thought_stream()
            phases_completed.append(InsightPhase.COGNITIVE_PAUSE)

            # 2. 랜덤 기억 소환
            logger.info("📌 2단계: 시맨틱 드리프트 생성")
            fragments = self.semantic_drift.generate_semantic_drift()
            phases_completed.append(InsightPhase.SEMANTIC_DRIFT)

            # 3. 역방향 사고 자극
            logger.info("📌 3단계: 역방향 추론")
            reasoning = self.retrograde_reasoning.apply_retrograde_reasoning(
                problem, fragments
            )
            phases_completed.append(InsightPhase.RETROGRADE_REASONING)

            # 4. 비논리적 연결 탐색
            logger.info("📌 4단계: 파괴적 구성")
            candidates = self.disruptive_mapping.create_disruptive_composition(
                reasoning, fragments
            )
            candidates_generated.extend(candidates)
            phases_completed.append(InsightPhase.DISRUPTIVE_MAPPING)

            # 5. 최종 통찰 후보 평가
            logger.info("📌 5단계: 메타 평가")
            final_insight = self.meta_evaluator.select_best_candidate(candidates)
            phases_completed.append(InsightPhase.META_EVALUATION)

            # 세션 완료
            duration = (datetime.now() - start_time).total_seconds()

            session = InsightSession(
                session_id=session_id,
                trigger_type=trigger_type,
                start_time=start_time,
                phases_completed=phases_completed,
                candidates_generated=candidates_generated,
                final_insight=final_insight,
                duration=duration,
            )

            if final_insight:
                self.successful_insights += 1
                logger.info(f"🎉 통찰 세션 성공: {final_insight.strategy[:50]}...")
            else:
                logger.warning("❌ 통찰 세션 실패 - 적절한 통찰 없음")

            return session

        except Exception as e:
            logger.error(f"❌ 통찰 세션 오류: {e}")
            return None


class DualResponseSystem:
    """이중 응답 시스템 - 이성적 리팩터링 + 창발적 통찰"""

    def __init__(self):
        self.insight_engine = InsightTriggerEngine()
        self.rational_refactor_count = 0
        self.insight_trigger_count = 0

    def detect_efficiency_drop(self) -> bool:
        """효율성 저하 감지 (시뮬레이션)"""
        # 실제로는 성능 모니터링 시스템과 연동
        return random.random() < 0.3  # 30% 확률로 효율성 저하 감지

    def trigger_rational_refactor(self) -> bool:
        """이성적 리팩터링 트리거 (기존 DuRi 구조)"""
        logger.info("🔧 이성적 리팩터링 트리거")
        self.rational_refactor_count += 1
        return True

    def should_trigger_insight(self, refactor_success: bool) -> bool:
        """통찰 트리거 여부 판단"""
        # 리팩터링 실패 또는 반복 실패 시 통찰 트리거
        return not refactor_success or random.random() < 0.2  # 20% 확률

    def execute_dual_response(self, problem: str) -> Dict[str, Any]:
        """이중 응답 실행"""
        logger.info("🔄 이중 응답 시스템 실행")

        # 1. 효율성 저하 감지
        if not self.detect_efficiency_drop():
            return {"status": "no_efficiency_drop", "action": "continue_normal"}

        # 2. 이성적 리팩터링 시도
        refactor_success = self.trigger_rational_refactor()

        # 3. 통찰 트리거 여부 판단
        if self.should_trigger_insight(refactor_success):
            logger.info("🧠 통찰 트리거 조건 충족 - 창발적 통찰 시작")
            self.insight_trigger_count += 1

            # 통찰 세션 실행
            trigger_type = (
                InsightTriggerType.REPEATED_FAILURE
                if not refactor_success
                else InsightTriggerType.NO_GAIN
            )
            insight_session = self.insight_engine.trigger_insight_session(
                problem, trigger_type
            )

            if insight_session and insight_session.final_insight:
                return {
                    "status": "insight_generated",
                    "rational_refactor": refactor_success,
                    "insight": insight_session.final_insight,
                    "session": insight_session,
                }
            else:
                return {
                    "status": "insight_failed",
                    "rational_refactor": refactor_success,
                    "fallback": "continue_with_rational",
                }
        else:
            return {"status": "rational_only", "rational_refactor": refactor_success}


# 전역 인스턴스
_dual_response_system = None


def get_dual_response_system() -> DualResponseSystem:
    """전역 이중 응답 시스템 인스턴스 반환"""
    global _dual_response_system
    if _dual_response_system is None:
        _dual_response_system = DualResponseSystem()
    return _dual_response_system


def integrate_with_learning_loop():
    """학습 루프와 통합"""
    logger.info("🔗 Insight Engine을 학습 루프와 통합")
    return get_dual_response_system()


if __name__ == "__main__":
    # 데모 실행
    system = get_dual_response_system()

    # 테스트 문제
    test_problem = "학습 루프가 반복적으로 실패하고 성능 개선이 없음"

    # 이중 응답 실행
    result = system.execute_dual_response(test_problem)

    print(f"\n🎯 결과: {result}")

    if result["status"] == "insight_generated":
        insight = result["insight"]
        print(f"🧠 생성된 통찰: {insight.strategy}")
        print(f"📊 신뢰도: {insight.confidence:.3f}")
        print(f"🎯 예상 영향: {insight.expected_impact:.3f}")
