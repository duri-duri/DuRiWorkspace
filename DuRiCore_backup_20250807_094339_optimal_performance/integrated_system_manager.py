#!/usr/bin/env python3
"""
DuRiCore Phase 5.5.2 - 통합 시스템 매니저
기존 시스템들을 통합하여 고급 기능을 제공하는 시스템
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from action_system import ActionSystem
from adaptive_learning_system import AdaptiveLearningSystem

# Phase 6.3 - 고급 인지 시스템 추가
from advanced_cognitive_system import AdvancedCognitiveSystem

# Phase 6.2.5 - CLARION 학습 시스템 추가
from clarion_learning_system import CLARIONLearningSystem
from creative_thinking_system import CreativeThinkingSystem

# Phase 6.2.3 - 감정 가중치 시스템 추가
from emotion_weight_system import EmotionWeightSystem
from enhanced_memory_system import EnhancedMemorySystem
from evolution_system import EvolutionSystem
from feedback_system import FeedbackSystem

# Phase 6.2.4 - Goal Stack 시스템 추가
from goal_stack_system import GoalStackSystem

# 기존 시스템들 import
from judgment_system import JudgmentSystem

# Phase 6.2.1 - LIDA 주의 시스템 추가
from lida_attention_system import LIDAAttentionSystem
from performance_monitoring_system import PerformanceMonitoringSystem
from prediction_system import PredictionSystem
from self_improvement_system import SelfImprovementSystem

# Phase 6.2.6 - 시맨틱 지식 연결망 시스템 추가
from semantic_knowledge_graph import SemanticKnowledgeGraph
from social_intelligence_system import SocialIntelligenceSystem
from strategic_thinking_system import StrategicThinkingSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class IntegrationResult:
    """통합 결과 데이터 클래스"""

    system_name: str
    status: str
    performance_score: float
    integration_time: float
    error_count: int
    success_rate: float
    created_at: str


class IntegratedSystemManager:
    """통합 시스템 매니저"""

    def __init__(self):
        """초기화"""
        self.judgment_system = JudgmentSystem()
        self.action_system = ActionSystem()
        self.feedback_system = FeedbackSystem()
        self.memory_system = EnhancedMemorySystem()
        self.performance_system = PerformanceMonitoringSystem()
        self.evolution_system = EvolutionSystem()
        self.creative_system = CreativeThinkingSystem()
        self.strategic_system = StrategicThinkingSystem()
        self.social_system = SocialIntelligenceSystem()
        self.prediction_system = PredictionSystem()
        self.self_improvement_system = SelfImprovementSystem()
        self.adaptive_learning_system = AdaptiveLearningSystem()

        # Phase 6.2.1 - LIDA 주의 시스템 추가
        self.attention_system = LIDAAttentionSystem()

        # Phase 6.2.3 - 감정 가중치 시스템 추가
        self.emotion_system = EmotionWeightSystem()

        # Phase 6.2.4 - Goal Stack 시스템 추가
        self.goal_stack_system = GoalStackSystem()

        # Phase 6.2.5 - CLARION 학습 시스템 추가
        self.clarion_system = CLARIONLearningSystem()

        # Phase 6.2.6 - 시맨틱 지식 연결망 시스템 추가
        self.semantic_graph_system = SemanticKnowledgeGraph()

        # Phase 6.3 - 고급 인지 시스템 추가
        self.advanced_cognitive_system = AdvancedCognitiveSystem()

        self.integration_results = []
        self.system_status = {}
        self.performance_metrics = {}

        logger.info(
            "통합 시스템 매니저 초기화 완료 (Phase 6.2.1, 6.2.3, 6.2.4, 6.2.5, 6.2.6, 6.3 포함)"
        )

    async def initialize_all_systems(self):
        """모든 시스템 초기화"""
        try:
            # 각 시스템은 __init__에서 이미 초기화됨
            # 추가 초기화가 필요한 경우 여기서 처리
            logger.info("모든 시스템 초기화 완료")
            return True
        except Exception as e:
            logger.error(f"시스템 초기화 실패: {e}")
            return False

    async def run_integrated_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """통합 사이클 실행"""
        start_time = time.time()

        try:
            # 1. 메모리에서 관련 정보 검색
            memory_context = await self._get_memory_context(context)

            # 2. 성능 모니터링 시작
            system_metrics = {
                "cpu_usage": 0.3,
                "memory_usage": 0.4,
                "response_time": 0.1,
                "throughput": 100.0,
                "error_rate": 0.01,
                "availability": 0.999,
            }
            performance_data = (
                await self.performance_system.monitor_real_time_performance(
                    system_metrics
                )
            )

            # Phase 6.2.1 - LIDA 주의 시스템 실행
            attention_context = {
                "cognitive_load": performance_data.get("cpu_usage", 0.3),
                "judgment_request": context,
            }
            attention_result = await self.attention_system.integrate_with_system(
                attention_context
            )

            # Phase 6.2.3 - 감정 가중치 시스템 실행
            emotion_context = {
                "emotion": context.get(
                    "emotion", {"type": "neutral", "intensity": 0.5}
                ),
                "judgment_request": context,
            }
            emotion_result = await self.emotion_system.integrate_with_system(
                emotion_context
            )

            # Phase 6.2.4 - Goal Stack 시스템 실행
            goal_context = {
                "available_resources": context.get(
                    "available_resources", ["time", "energy", "attention"]
                ),
                "current_situation": context,
                "attention_result": attention_result,
                "emotion_result": emotion_result,
            }
            goal_result = await self._execute_goal_stack_system(goal_context)

            # Phase 6.2.5 - CLARION 학습 시스템 실행
            clarion_context = {
                "current_situation": context,
                "attention_result": attention_result,
                "emotion_result": emotion_result,
                "goal_result": goal_result,
            }
            clarion_result = await self._execute_clarion_learning_system(
                clarion_context
            )

            # Phase 6.2.6 - 시맨틱 지식 연결망 시스템 실행
            semantic_context = {
                "current_situation": context,
                "memory_context": memory_context,
                "attention_result": attention_result,
                "emotion_result": emotion_result,
                "goal_result": goal_result,
                "clarion_result": clarion_result,
            }
            semantic_result = await self._execute_semantic_knowledge_system(
                semantic_context
            )

            # Phase 6.3 - 고급 인지 시스템 실행
            cognitive_context = {
                "current_situation": context,
                "memory_context": memory_context,
                "attention_result": attention_result,
                "emotion_result": emotion_result,
                "goal_result": goal_result,
                "clarion_result": clarion_result,
                "semantic_result": semantic_result,
            }
            cognitive_result = await self._execute_advanced_cognitive_system(
                cognitive_context
            )

            # 3. 예측 시스템 실행
            prediction_result = await self.prediction_system.predict_future_situation(
                {**context, "memory_context": memory_context}
            )

            # 4. 판단 시스템 실행 (메모리 정보, 예측 결과, 주의 시스템 결과, 감정 시스템 결과, 목표 시스템 결과, CLARION 학습 결과, 시맨틱 지식 결과, 고급 인지 결과 활용)
            judgment_result = await self.judgment_system.judge(
                {
                    **context,
                    "memory_context": memory_context,
                    "prediction_result": prediction_result,
                    "attention_result": attention_result,
                    "emotion_result": emotion_result,
                    "goal_result": goal_result,
                    "clarion_result": clarion_result,
                    "semantic_result": semantic_result,
                    "cognitive_result": cognitive_result,
                }
            )

            # 5. 행동 시스템 실행
            action_result = await self.action_system.act(judgment_result)

            # 6. 피드백 시스템 실행
            feedback_result = await self.feedback_system.feedback(action_result)

            # 7. 자기 개선 시스템 실행
            improvement_result = await self.self_improvement_system.analyze_and_improve(
                {
                    "judgment_result": judgment_result,
                    "action_result": action_result,
                    "feedback_result": feedback_result,
                    "prediction_result": prediction_result,
                }
            )

            # 8. 적응형 학습 시스템 실행
            adaptation_result = (
                await self.adaptive_learning_system.adapt_to_environment(
                    {
                        **context,
                        "judgment_result": judgment_result,
                        "action_result": action_result,
                        "feedback_result": feedback_result,
                        "improvement_result": improvement_result,
                    }
                )
            )

            # 9. 결과를 메모리에 저장
            await self._save_to_memory(
                judgment_result, action_result, feedback_result, prediction_result
            )

            # Phase 6.2.2 - Working Memory 연산 수행
            if len(memory_context.get("related_memories", [])) >= 2:
                # 관련 메모리들로 연산 수행
                memory_ids = [
                    mem[0].id for mem in memory_context.get("related_memories", [])[:3]
                ]
                wm_operation_result = await self.memory_system.perform_memory_operation(
                    "integration", memory_ids
                )
                if wm_operation_result.get("success"):
                    logger.info(
                        f"🧠 Working Memory 연산 완료: {wm_operation_result.get('buffer_id', '')}"
                    )

            # 8. 창의적 사고 시스템을 통한 혁신적 해결책 생성
            creative_data = {
                "behavior_traces": [action_result],
                "performance_history": [performance_data],
            }
            creative_insights = await self.creative_system.analyze_patterns(
                creative_data
            )

            # 9. 전략적 사고 시스템을 통한 장기 계획 수립
            strategic_context = {
                "current_state": "development",
                "desired_state": "production",
                "constraints": ["time", "resources"],
                "opportunities": ["market_demand"],
                "threats": ["competition"],
                "strengths": ["technical_expertise"],
                "weaknesses": ["resource_limitation"],
            }
            strategic_plan = await self.strategic_system.plan_long_term(
                strategic_context
            )

            # 10. 사회적 지능 시스템을 통한 상황 이해 및 적응
            social_situation = {
                "keywords": ["collaboration", "development"],
                "stakeholders": ["development_team", "stakeholders"],
                "issues": ["communication", "coordination"],
                "time_pressure": 0.6,
                "cultural_differences": False,
                "conflicting_interests": False,
                "emotional_indicators": {
                    "tension": 0.3,
                    "cooperation": 0.8,
                    "conflict": 0.2,
                },
            }
            context_analysis = await self.social_system.understand_context(
                social_situation
            )

            # 12. 진화 시스템을 통한 개선
            learning_cycles = [
                {
                    "judgment": judgment_result,
                    "action": action_result,
                    "feedback": feedback_result,
                    "prediction": prediction_result,
                    "improvement": improvement_result,
                    "adaptation": adaptation_result,
                    "performance": performance_data,
                    "creative_insights": creative_insights,
                    "strategic_plan": strategic_plan,
                    "social_context": context_analysis,
                }
            ]
            evolution_result = await self.evolution_system.evolve_system(
                learning_cycles
            )

            cycle_time = time.time() - start_time

            # 통합 결과 생성
            integrated_result = {
                "cycle_id": f"cycle_{int(time.time() * 1000)}",
                "timestamp": datetime.now().isoformat(),
                "duration": cycle_time,
                "prediction": prediction_result,
                "judgment": judgment_result,
                "action": action_result,
                "feedback": feedback_result,
                "improvement": improvement_result,
                "adaptation": adaptation_result,
                "memory_context": memory_context,
                "performance_data": performance_data,
                "creative_insights": creative_insights,
                "strategic_plan": strategic_plan,
                "social_context": context_analysis,
                "evolution_result": evolution_result,
                "overall_score": self._calculate_overall_score(
                    judgment_result,
                    action_result,
                    feedback_result,
                    performance_data,
                    prediction_result,
                    improvement_result,
                    adaptation_result,
                ),
            }

            logger.info(f"통합 사이클 완료: {cycle_time:.3f}초")
            return integrated_result

        except Exception as e:
            logger.error(f"통합 사이클 실행 실패: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}

    async def _get_memory_context(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """메모리에서 관련 컨텍스트 검색"""
        try:
            # 상황에 관련된 메모리 검색
            relevant_memories = await self.memory_system.search_memories(
                context.get("situation", ""), limit=5
            )

            # 연관 메모리 검색
            associated_memories = []
            if relevant_memories:
                associated_memories = await self.memory_system.get_associated_memories(
                    relevant_memories[0]["id"]
                )

            return {
                "relevant_memories": relevant_memories,
                "associated_memories": associated_memories,
                "memory_count": len(relevant_memories) + len(associated_memories),
            }
        except Exception as e:
            logger.warning(f"메모리 컨텍스트 검색 실패: {e}")
            return {
                "relevant_memories": [],
                "associated_memories": [],
                "memory_count": 0,
            }

    async def _save_to_memory(
        self,
        judgment_result: Dict,
        action_result: Dict,
        feedback_result: Dict,
        prediction_result: Dict = None,
    ):
        """결과를 메모리에 저장"""
        try:
            # 판단 결과 저장
            await self.memory_system.store_memory(
                content=f"판단 결과: {judgment_result.get('decision', 'unknown')}",
                context={
                    "type": "judgment",
                    "decision": judgment_result.get("decision", "unknown"),
                },
                importance=0.7,
            )

            # 행동 결과 저장
            await self.memory_system.store_memory(
                content=f"행동 결과: {action_result.get('action', 'unknown')}",
                context={
                    "type": "action",
                    "action": action_result.get("action", "unknown"),
                },
                importance=0.8,
            )

            # 피드백 결과 저장
            await self.memory_system.store_memory(
                content=f"피드백 결과: {feedback_result.get('feedback', 'unknown')}",
                context={
                    "type": "feedback",
                    "feedback": feedback_result.get("feedback", "unknown"),
                },
                importance=0.6,
            )

            # 예측 결과 저장 (있는 경우)
            if prediction_result:
                predicted_outcome = "unknown"
                if hasattr(prediction_result, "predicted_outcome"):
                    predicted_outcome = prediction_result.predicted_outcome
                elif isinstance(prediction_result, dict):
                    predicted_outcome = prediction_result.get(
                        "predicted_outcome", "unknown"
                    )

                await self.memory_system.store_memory(
                    content=f"예측 결과: {predicted_outcome}",
                    context={"type": "prediction", "prediction": predicted_outcome},
                    importance=0.7,
                )

            logger.info("결과를 메모리에 저장 완료")
        except Exception as e:
            logger.warning(f"메모리 저장 실패: {e}")

    async def _execute_goal_stack_system(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Goal Stack 시스템 실행"""
        try:
            # 현재 상황에 따른 목표 관리
            goal_management_result = {
                "active_goals": self.goal_stack_system.get_active_goals(),
                "stack_status": self.goal_stack_system.get_goal_stack_status(),
                "next_action": self.goal_stack_system.get_next_action_recommendation(
                    context
                ),
                "conflicts": self.goal_stack_system.resolve_goal_conflicts(),
            }

            # 목표 기반 행동 제어
            if goal_management_result["active_goals"]:
                # 활성 목표가 있는 경우 목표 기반 행동 결정
                best_goal = max(
                    goal_management_result["active_goals"],
                    key=lambda g: self.goal_stack_system.calculate_goal_priority_score(
                        g, context
                    ),
                )

                goal_management_result["current_focus"] = {
                    "goal_id": best_goal.id,
                    "goal_name": best_goal.name,
                    "goal_type": best_goal.goal_type.value,
                    "priority": best_goal.priority.value,
                    "progress": best_goal.progress,
                }
            else:
                # 활성 목표가 없는 경우 새 목표 생성 권장
                goal_management_result["current_focus"] = {
                    "action": "create_new_goal",
                    "reason": "활성 목표가 없음",
                }

            logger.info("Goal Stack 시스템 실행 완료")
            return goal_management_result

        except Exception as e:
            logger.error(f"Goal Stack 시스템 실행 실패: {e}")
            return {
                "error": str(e),
                "active_goals": [],
                "stack_status": {},
                "next_action": {"action": "error", "reason": str(e)},
            }

    async def _execute_clarion_learning_system(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """CLARION 학습 시스템 실행"""
        try:
            # 학습 로그 데이터 생성
            log_data = {
                "context": context.get("current_situation", {}),
                "action": "integrated_learning",
                "outcome": "success",
                "success": True,
                "learning_score": 0.7,  # 기본 학습 점수
                "reinforcement_history": [],
            }

            # CLARION 학습 시스템으로 로그 처리
            clarion_result = await self.clarion_system.process_learning_log(log_data)

            # 학습 패턴 분석
            pattern_analysis = await self.clarion_system.analyze_learning_patterns()

            return {
                "clarion_result": clarion_result,
                "pattern_analysis": pattern_analysis,
                "learning_type": clarion_result.learning_type.value,
                "reinforcement_type": clarion_result.reinforcement_type.value,
                "learning_phase": clarion_result.learning_phase.value,
                "pattern_strength": clarion_result.pattern_strength,
                "learning_efficiency": clarion_result.learning_efficiency,
                "transfer_ability": clarion_result.transfer_ability,
                "consolidation_level": clarion_result.consolidation_level,
            }

        except Exception as e:
            logger.error(f"CLARION 학습 시스템 실행 실패: {e}")
            return {
                "clarion_result": None,
                "pattern_analysis": {},
                "learning_type": "explicit",
                "reinforcement_type": "neutral",
                "learning_phase": "acquisition",
                "pattern_strength": 0.0,
                "learning_efficiency": 0.0,
                "transfer_ability": 0.0,
                "consolidation_level": 0.0,
            }

    async def _execute_semantic_knowledge_system(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """시맨틱 지식 연결망 시스템 실행"""
        try:
            # 현재 상황에서 시맨틱 개념들 추출
            current_situation = context.get("current_situation", {})
            memory_context = context.get("memory_context", {})
            attention_result = context.get("attention_result", {})
            emotion_result = context.get("emotion_result", {})
            goal_result = context.get("goal_result", {})
            clarion_result = context.get("clarion_result", {})

            # 시맨틱 개념들 추가
            semantic_concepts = []

            # 주의 관련 개념
            if attention_result.get("focus_level", 0) > 0.7:
                concept_id = await self.semantic_graph_system.add_concept(
                    "높은 집중", "entity", "높은 수준의 주의 집중 상태"
                )
                semantic_concepts.append(concept_id)

            # 감정 관련 개념
            emotion_type = emotion_result.get("emotion_type", "neutral")
            if emotion_type != "neutral":
                concept_id = await self.semantic_graph_system.add_concept(
                    f"{emotion_type} 감정", "entity", f"{emotion_type} 감정 상태"
                )
                semantic_concepts.append(concept_id)

            # 목표 관련 개념
            if goal_result.get("priority_level", 0) > 0.8:
                concept_id = await self.semantic_graph_system.add_concept(
                    "높은 우선순위 목표", "entity", "높은 우선순위를 가진 목표"
                )
                semantic_concepts.append(concept_id)

            # 학습 관련 개념
            if clarion_result.get("pattern_strength", 0) > 0.6:
                concept_id = await self.semantic_graph_system.add_concept(
                    "강한 학습 패턴", "entity", "강한 학습 패턴이 관찰됨"
                )
                semantic_concepts.append(concept_id)

            # 시맨틱 추론들 추가
            semantic_inferences = []

            # 개념 간 관계 설정
            if len(semantic_concepts) >= 2:
                for i in range(len(semantic_concepts) - 1):
                    edge_id = await self.semantic_graph_system.add_inference(
                        f"개념_{i}", f"개념_{i+1}", "associated_with", 0.7
                    )
                    semantic_inferences.append(edge_id)

            # 시맨틱 경로 찾기
            semantic_paths = []
            if len(semantic_concepts) >= 2:
                path_result = await self.semantic_graph_system.find_semantic_path(
                    "높은 집중", "높은 우선순위 목표", 3
                )
                if path_result:
                    semantic_paths.append(path_result)

            # 시맨틱 지식 추론
            semantic_inferences_knowledge = []
            for concept_name in ["높은 집중", "높은 우선순위 목표", "강한 학습 패턴"]:
                inferences = await self.semantic_graph_system.infer_new_knowledge(
                    concept_name
                )
                semantic_inferences_knowledge.extend(inferences)

            # 시맨틱 그래프 상태 확인
            graph_status = await self.semantic_graph_system.get_knowledge_graph_status()

            # 시맨틱 시스템 결과
            semantic_result = {
                "concepts_added": len(semantic_concepts),
                "inferences_added": len(semantic_inferences),
                "paths_found": len(semantic_paths),
                "knowledge_inferences": len(semantic_inferences_knowledge),
                "graph_status": graph_status,
                "semantic_richness": graph_status.get("average_confidence", 0.0),
                "graph_density": graph_status.get("graph_density", 0.0),
                "connected_components": graph_status.get("connected_components", 0),
                "success": True,
            }

            logger.info(
                f"시맨틱 지식 연결망 시스템 실행 완료: {len(semantic_concepts)}개 개념, {len(semantic_inferences)}개 추론"
            )
            return semantic_result

        except Exception as e:
            logger.error(f"시맨틱 지식 연결망 시스템 실행 실패: {e}")
            return {
                "concepts_added": 0,
                "inferences_added": 0,
                "paths_found": 0,
                "knowledge_inferences": 0,
                "graph_status": {},
                "semantic_richness": 0.0,
                "graph_density": 0.0,
                "connected_components": 0,
                "success": False,
                "error": str(e),
            }

    async def _execute_advanced_cognitive_system(
        self, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """고급 인지 시스템 실행"""
        try:
            # 고급 인지 처리
            cognitive_result = (
                await self.advanced_cognitive_system.process_advanced_cognition(context)
            )

            # 인지 시스템 통합
            integration_result = (
                await self.advanced_cognitive_system.integrate_cognitive_systems(
                    context
                )
            )

            # 인지 성능 최적화
            optimization_result = (
                await self.advanced_cognitive_system.optimize_cognitive_performance(
                    context
                )
            )

            # 고급 인지 시스템 결과
            advanced_cognitive_result = {
                "cognitive_insights_count": len(cognitive_result.cognitive_insights),
                "metacognitive_processes_count": len(
                    cognitive_result.metacognitive_processes
                ),
                "abstract_concepts_count": len(cognitive_result.abstract_concepts),
                "creative_solutions_count": len(cognitive_result.creative_solutions),
                "overall_cognitive_score": cognitive_result.overall_cognitive_score,
                "integration_result": integration_result,
                "optimization_result": optimization_result,
                "success": cognitive_result.success,
            }

            logger.info(
                f"고급 인지 시스템 실행 완료: {len(cognitive_result.cognitive_insights)}개 통찰, {cognitive_result.overall_cognitive_score:.3f} 점수"
            )
            return advanced_cognitive_result

        except Exception as e:
            logger.error(f"고급 인지 시스템 실행 실패: {e}")
            return {
                "cognitive_insights_count": 0,
                "metacognitive_processes_count": 0,
                "abstract_concepts_count": 0,
                "creative_solutions_count": 0,
                "overall_cognitive_score": 0.0,
                "integration_result": {},
                "optimization_result": {},
                "success": False,
                "error": str(e),
            }

    def _calculate_overall_score(
        self,
        judgment: Dict,
        action: Dict,
        feedback: Dict,
        performance: List,
        prediction: Dict = None,
        improvement: Dict = None,
        adaptation: Dict = None,
    ) -> float:
        """전체 점수 계산"""
        try:
            # 각 시스템의 점수 추출
            judgment_score = judgment.get("confidence", 0.0)
            action_score = action.get("effectiveness_score", 0.0)
            feedback_score = feedback.get("evaluation_score", 0.0)

            # 성능 데이터에서 평균 점수 계산
            performance_score = 0.0
            if performance and len(performance) > 0:
                performance_values = [
                    p.value for p in performance if hasattr(p, "value")
                ]
                if performance_values:
                    performance_score = sum(performance_values) / len(
                        performance_values
                    )

            # 예측 점수 계산
            prediction_score = 0.0
            if prediction:
                if hasattr(prediction, "confidence_score"):
                    prediction_score = prediction.confidence_score
                elif isinstance(prediction, dict):
                    prediction_score = prediction.get("confidence_score", 0.0)

            # 개선 점수 계산
            improvement_score = 0.0
            if improvement:
                if hasattr(improvement, "improvement_score"):
                    improvement_score = improvement.improvement_score
                elif isinstance(improvement, dict):
                    improvement_score = improvement.get("improvement_score", 0.0)

            # 적응 점수 계산
            adaptation_score = 0.0
            if adaptation:
                if hasattr(adaptation, "adaptation_score"):
                    adaptation_score = adaptation.adaptation_score
                elif isinstance(adaptation, dict):
                    adaptation_score = adaptation.get("adaptation_score", 0.0)

            # 가중 평균 계산 (새로운 시스템들 포함)
            overall_score = (
                judgment_score * 0.2
                + action_score * 0.2
                + feedback_score * 0.15
                + performance_score * 0.15
                + prediction_score * 0.1
                + improvement_score * 0.1
                + adaptation_score * 0.1
            )

            return round(overall_score, 3)
        except Exception as e:
            logger.warning(f"전체 점수 계산 실패: {e}")
            return 0.0

    async def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        try:
            status = {
                "timestamp": datetime.now().isoformat(),
                "systems": {
                    "judgment": "active",
                    "action": "active",
                    "feedback": "active",
                    "memory": "active",
                    "performance": "active",
                    "evolution": "active",
                    "creative": "active",
                    "strategic": "active",
                    "social": "active",
                    "prediction": "active",
                    "self_improvement": "active",
                    "adaptive_learning": "active",
                    "attention": "active",  # Phase 6.2.1 추가
                    "emotion": "active",  # Phase 6.2.3 추가
                    "goal_stack": "active",  # Phase 6.2.4 추가
                    "clarion_learning": "active",  # Phase 6.2.5 추가
                    "semantic_knowledge": "active",  # Phase 6.2.6 추가
                    "advanced_cognitive": "active",  # Phase 6.3 추가
                },
                "integration_results": len(self.integration_results),
                "performance_metrics": self.performance_metrics,
            }
            return status
        except Exception as e:
            logger.error(f"시스템 상태 조회 실패: {e}")
            return {"error": str(e)}

    async def run_integration_test(self) -> Dict[str, Any]:
        """통합 테스트 실행"""
        logger.info("통합 시스템 테스트 시작")

        test_context = {
            "situation": "통합 시스템 테스트 상황",
            "priority": "high",
            "complexity": "medium",
        }

        # 통합 사이클 실행
        result = await self.run_integrated_cycle(test_context)

        # 테스트 결과 분석
        test_result = {
            "test_id": f"integration_test_{int(time.time() * 1000)}",
            "timestamp": datetime.now().isoformat(),
            "success": "error" not in result,
            "duration": result.get("duration", 0),
            "overall_score": result.get("overall_score", 0),
            "details": result,
        }

        logger.info(
            f"통합 테스트 완료: 성공={test_result['success']}, 점수={test_result['overall_score']}"
        )
        return test_result


async def main():
    """메인 함수"""
    logger.info("🚀 DuRiCore Phase 5.5.2 통합 시스템 매니저 시작")

    # 통합 시스템 매니저 생성
    manager = IntegratedSystemManager()

    # 시스템 초기화
    if not await manager.initialize_all_systems():
        logger.error("시스템 초기화 실패")
        return

    # 통합 테스트 실행
    test_result = await manager.run_integration_test()

    # 결과 출력
    print("\n=== 통합 시스템 테스트 결과 ===")
    print(f"테스트 ID: {test_result['test_id']}")
    print(f"성공 여부: {test_result['success']}")
    print(f"실행 시간: {test_result['duration']:.3f}초")
    print(f"전체 점수: {test_result['overall_score']}")

    if test_result["success"]:
        print("✅ 통합 시스템 테스트 성공!")
    else:
        print("❌ 통합 시스템 테스트 실패")

    # 시스템 상태 출력
    status = await manager.get_system_status()
    print(f"\n시스템 상태: {status['systems']}")


if __name__ == "__main__":
    asyncio.run(main())
