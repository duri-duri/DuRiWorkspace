#!/usr/bin/env python3
"""
DuRiCore - 메인 루프
실제 AI의 핵심 루프: Input → 감정 → 판단 → 실행 → 성찰 → 저장
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

# 모듈 임포트
from ..modules.emotion_engine import EmotionalAnalysis, EmotionEngine
from ..modules.self_evolution import EvolutionResult, SelfEvolutionEngine

logger = logging.getLogger(__name__)


@dataclass
class InputData:
    """입력 데이터"""

    text: str
    context: Dict[str, Any]
    user_id: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class JudgmentResult:
    """판단 결과"""

    decision: str
    reasoning: str
    confidence: float
    alternatives: List[str]
    timestamp: datetime


@dataclass
class ExecutionResult:
    """실행 결과"""

    action: str
    success: bool
    feedback: str
    performance_metrics: Dict[str, Any]
    timestamp: datetime


@dataclass
class ReflectionResult:
    """성찰 결과"""

    insights: List[str]
    lessons_learned: List[str]
    improvement_suggestions: List[str]
    emotional_state: EmotionalAnalysis
    timestamp: datetime


@dataclass
class MemoryEntry:
    """메모리 엔트리"""

    input_data: InputData
    judgment: JudgmentResult
    execution: ExecutionResult
    reflection: ReflectionResult
    importance_score: float
    created_at: datetime


class MainLoop:
    """DuRiCore 메인 루프 - 실제 AI의 핵심 처리 과정"""

    def __init__(self):
        # 핵심 모듈 초기화
        self.emotion_engine = EmotionEngine()
        self.self_evolution_engine = SelfEvolutionEngine()

        # 상태 관리
        self.current_state = {
            "emotional_state": "neutral",
            "learning_level": 1,
            "confidence": 0.5,
            "last_evolution": None,
        }

        # 메모리 저장소 (임시)
        self.memory_store: List[MemoryEntry] = []

        # 성능 통계
        self.performance_stats = {
            "total_cycles": 0,
            "successful_cycles": 0,
            "average_confidence": 0.0,
            "last_cycle_time": 0.0,
        }

    async def process_input(self, input_data: InputData) -> Dict[str, Any]:
        """완전한 AI 루프 처리: Input → 감정 → 판단 → 실행 → 성찰 → 저장"""
        cycle_start_time = datetime.now()

        try:
            logger.info(f"새로운 입력 처리 시작: {input_data.text[:50]}...")

            # 1단계: 감정 분석
            emotional_analysis = await self._analyze_emotion(input_data)
            logger.info(f"감정 분석 완료: {emotional_analysis.primary_emotion}")

            # 2단계: 판단 생성
            judgment = await self._create_judgment(input_data, emotional_analysis)
            logger.info(f"판단 생성 완료: {judgment.decision[:50]}...")

            # 3단계: 실행
            execution = await self._execute_action(judgment, emotional_analysis)
            logger.info(f"실행 완료: {execution.success}")

            # 4단계: 성찰
            reflection = await self._reflect_on_cycle(input_data, emotional_analysis, judgment, execution)
            logger.info(f"성찰 완료: {len(reflection.insights)}개 인사이트")

            # 5단계: 메모리 저장
            memory_entry = await self._store_memory(input_data, judgment, execution, reflection)
            logger.info("메모리 저장 완료")

            # 6단계: 자기 진화 (주기적)
            evolution_result = await self._check_and_evolve()

            # 7단계: 성능 통계 업데이트
            await self._update_performance_stats(cycle_start_time)

            # 결과 반환
            return {
                "emotional_analysis": emotional_analysis,
                "judgment": judgment,
                "execution": execution,
                "reflection": reflection,
                "memory_entry": memory_entry,
                "evolution_result": evolution_result,
                "cycle_time": (datetime.now() - cycle_start_time).total_seconds(),
                "performance_stats": self.performance_stats,
            }

        except Exception as e:
            logger.error(f"메인 루프 처리 실패: {e}")
            return {
                "error": str(e),
                "cycle_time": (datetime.now() - cycle_start_time).total_seconds(),
            }

    async def _analyze_emotion(self, input_data: InputData) -> EmotionalAnalysis:
        """감정 분석 단계"""
        try:
            # 감정 엔진을 통한 분석
            analysis_input = {"text": input_data.text, "context": input_data.context}

            emotional_analysis = self.emotion_engine.analyze_complex_emotion(analysis_input)

            # 현재 상태 업데이트
            self.current_state["emotional_state"] = emotional_analysis.primary_emotion

            return emotional_analysis

        except Exception as e:
            logger.error(f"감정 분석 실패: {e}")
            # 기본 감정 분석 반환
            return EmotionalAnalysis(
                primary_emotion="neutral",
                secondary_emotions=[],
                intensity=0.0,
                confidence=0.0,
                context_fit=0.0,
                emotion_reason_balance={
                    "balance_type": "neutral",
                    "recommendation": "관찰 필요",
                },
                empathetic_response="감정을 더 자세히 이해하고 싶어요.",
                analysis_timestamp=datetime.now(),
            )

    async def _create_judgment(self, input_data: InputData, emotional_analysis: EmotionalAnalysis) -> JudgmentResult:
        """판단 생성 단계"""
        try:
            # 감정 상태를 고려한 판단 생성
            emotional_context = {
                "primary_emotion": emotional_analysis.primary_emotion,
                "intensity": emotional_analysis.intensity,
                "balance_type": emotional_analysis.emotion_reason_balance.get("balance_type", "balanced"),
            }

            # 간단한 판단 로직 (실제로는 더 복잡한 LLM 기반 판단)
            if emotional_context["intensity"] > 0.7:
                if emotional_context["primary_emotion"] in ["joy", "trust"]:
                    decision = "긍정적으로 반응하고 적극적으로 참여하겠습니다."
                    confidence = 0.8
                elif emotional_context["primary_emotion"] in ["anger", "fear"]:
                    decision = "신중하게 접근하고 안전을 우선시하겠습니다."
                    confidence = 0.7
                else:
                    decision = "관찰하고 적절한 시점에 반응하겠습니다."
                    confidence = 0.6
            else:
                decision = "평온하게 상황을 파악하고 적절히 대응하겠습니다."
                confidence = 0.5

            # 판단 근거 생성
            reasoning = f"감정 상태({emotional_context['primary_emotion']}, 강도: {emotional_context['intensity']:.2f})를 고려하여 {decision}"  # noqa: E501

            # 대안 생성
            alternatives = [
                "더 적극적으로 참여하기",
                "더 신중하게 접근하기",
                "관찰만 하기",
            ]

            return JudgmentResult(
                decision=decision,
                reasoning=reasoning,
                confidence=confidence,
                alternatives=alternatives,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"판단 생성 실패: {e}")
            return JudgmentResult(
                decision="안전하게 관찰하겠습니다.",
                reasoning="판단 과정에서 오류가 발생했습니다.",
                confidence=0.3,
                alternatives=["관찰만 하기"],
                timestamp=datetime.now(),
            )

    async def _execute_action(self, judgment: JudgmentResult, emotional_analysis: EmotionalAnalysis) -> ExecutionResult:
        """실행 단계"""
        try:
            # 판단에 따른 실행
            action = judgment.decision

            # 실행 성공률 계산 (감정 상태와 판단 신뢰도 기반)
            success_probability = judgment.confidence * (1 - emotional_analysis.intensity * 0.3)
            success = success_probability > 0.5

            # 피드백 생성
            if success:
                feedback = f"성공적으로 {action}을 실행했습니다."
            else:
                feedback = f"{action}을 시도했지만 예상과 다르게 진행되었습니다."

            # 성능 메트릭
            performance_metrics = {
                "execution_speed": 1.0,  # 초
                "accuracy": judgment.confidence,
                "emotional_impact": emotional_analysis.intensity,
                "user_satisfaction": success_probability,
            }

            return ExecutionResult(
                action=action,
                success=success,
                feedback=feedback,
                performance_metrics=performance_metrics,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"실행 실패: {e}")
            return ExecutionResult(
                action="오류 발생으로 인한 안전 모드",
                success=False,
                feedback="실행 중 오류가 발생했습니다.",
                performance_metrics={"error": str(e)},
                timestamp=datetime.now(),
            )

    async def _reflect_on_cycle(
        self,
        input_data: InputData,
        emotional_analysis: EmotionalAnalysis,
        judgment: JudgmentResult,
        execution: ExecutionResult,
    ) -> ReflectionResult:
        """성찰 단계"""
        try:
            insights = []
            lessons_learned = []
            improvement_suggestions = []

            # 1. 감정적 인사이트
            if emotional_analysis.intensity > 0.7:
                insights.append(f"강한 감정({emotional_analysis.primary_emotion})이 판단에 영향을 주었습니다.")

            # 2. 판단 품질 분석
            if judgment.confidence < 0.6:
                insights.append("판단에 대한 확신이 낮았습니다.")
                improvement_suggestions.append("더 많은 정보를 수집하여 판단의 정확도를 높이세요.")

            # 3. 실행 결과 분석
            if execution.success:
                lessons_learned.append("성공적인 실행 패턴을 학습했습니다.")
            else:
                lessons_learned.append("실패한 실행에서 교훈을 얻었습니다.")
                improvement_suggestions.append("다음에는 다른 접근 방식을 시도해보세요.")

            # 4. 감정-이성 균형 분석
            balance_type = emotional_analysis.emotion_reason_balance.get("balance_type", "balanced")
            if balance_type == "emotion_dominant":
                insights.append("감정이 이성보다 우세했습니다.")
                improvement_suggestions.append("더 객관적인 판단을 위해 이성적 분석을 강화하세요.")
            elif balance_type == "reason_dominant":
                insights.append("이성이 감정보다 우세했습니다.")
                improvement_suggestions.append("감정적 공감 능력을 향상시키세요.")

            # 5. 전반적인 학습
            insights.append(f"이번 경험을 통해 {emotional_analysis.primary_emotion} 상황에 대한 이해가 깊어졌습니다.")

            return ReflectionResult(
                insights=insights,
                lessons_learned=lessons_learned,
                improvement_suggestions=improvement_suggestions,
                emotional_state=emotional_analysis,
                timestamp=datetime.now(),
            )

        except Exception as e:
            logger.error(f"성찰 실패: {e}")
            return ReflectionResult(
                insights=["성찰 과정에서 오류가 발생했습니다."],
                lessons_learned=[],
                improvement_suggestions=["시스템 안정성을 개선하세요."],
                emotional_state=emotional_analysis,
                timestamp=datetime.now(),
            )

    async def _store_memory(
        self,
        input_data: InputData,
        judgment: JudgmentResult,
        execution: ExecutionResult,
        reflection: ReflectionResult,
    ) -> MemoryEntry:
        """메모리 저장 단계"""
        try:
            # 중요도 점수 계산
            importance_score = self._calculate_importance_score(input_data, judgment, execution, reflection)

            # 메모리 엔트리 생성
            memory_entry = MemoryEntry(
                input_data=input_data,
                judgment=judgment,
                execution=execution,
                reflection=reflection,
                importance_score=importance_score,
                created_at=datetime.now(),
            )

            # 메모리 저장
            self.memory_store.append(memory_entry)

            # 메모리 크기 제한 (최근 1000개만 유지)
            if len(self.memory_store) > 1000:
                self.memory_store = self.memory_store[-1000:]

            return memory_entry

        except Exception as e:
            logger.error(f"메모리 저장 실패: {e}")
            return MemoryEntry(
                input_data=input_data,
                judgment=judgment,
                execution=execution,
                reflection=reflection,
                importance_score=0.5,
                created_at=datetime.now(),
            )

    def _calculate_importance_score(
        self,
        input_data: InputData,
        judgment: JudgmentResult,
        execution: ExecutionResult,
        reflection: ReflectionResult,
    ) -> float:
        """중요도 점수 계산"""
        try:
            score = 0.5  # 기본 점수

            # 감정 강도에 따른 가중치
            emotional_intensity = reflection.emotional_state.intensity
            score += emotional_intensity * 0.2

            # 판단 신뢰도에 따른 가중치
            score += judgment.confidence * 0.2

            # 실행 성공 여부에 따른 가중치
            if execution.success:
                score += 0.1

            # 인사이트 수에 따른 가중치
            insights_count = len(reflection.insights)
            score += min(insights_count * 0.05, 0.2)

            return min(1.0, max(0.0, score))

        except Exception as e:
            logger.error(f"중요도 점수 계산 실패: {e}")
            return 0.5

    async def _check_and_evolve(self) -> Optional[EvolutionResult]:
        """자기 진화 확인 및 실행"""
        try:
            # 진화 주기 확인 (1시간마다)
            last_evolution = self.current_state.get("last_evolution")
            current_time = datetime.now()

            if last_evolution is None or (current_time - last_evolution).total_seconds() > 3600:
                logger.info("자기 진화 분석 시작")
                evolution_result = self.self_evolution_engine.analyze_and_evolve()

                # 진화 결과 적용
                self.current_state["last_evolution"] = current_time

                logger.info(f"자기 진화 완료: 점수 {evolution_result.evolution_score:.2f}")
                return evolution_result

            return None

        except Exception as e:
            logger.error(f"자기 진화 실패: {e}")
            return None

    async def _update_performance_stats(self, cycle_start_time: datetime):
        """성능 통계 업데이트"""
        try:
            cycle_time = (datetime.now() - cycle_start_time).total_seconds()

            self.performance_stats["total_cycles"] += 1
            self.performance_stats["last_cycle_time"] = cycle_time

            # 평균 사이클 시간 업데이트
            total_cycles = self.performance_stats["total_cycles"]
            current_avg = self.performance_stats.get("average_cycle_time", 0)
            new_avg = (current_avg * (total_cycles - 1) + cycle_time) / total_cycles
            self.performance_stats["average_cycle_time"] = new_avg

        except Exception as e:
            logger.error(f"성능 통계 업데이트 실패: {e}")

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 반환"""
        return {
            "current_state": self.current_state,
            "performance_stats": self.performance_stats,
            "memory_count": len(self.memory_store),
            "last_activity": datetime.now().isoformat(),
        }

    def get_memory_summary(self, limit: int = 10) -> List[Dict[str, Any]]:
        """메모리 요약 반환"""
        recent_memories = sorted(self.memory_store, key=lambda x: x.created_at, reverse=True)[:limit]

        return [
            {
                "input": memory.input_data.text[:100] + "...",
                "emotion": memory.reflection.emotional_state.primary_emotion,
                "decision": memory.judgment.decision[:100] + "...",
                "success": memory.execution.success,
                "importance": memory.importance_score,
                "created_at": memory.created_at.isoformat(),
            }
            for memory in recent_memories
        ]
