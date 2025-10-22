#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 의식적 인지 시스템 (Phase 4.2)
자기 의식 구현, 주관적 경험 시뮬레이션, 의식적 의사결정 시스템
"""

import asyncio
import json
import logging
import random
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SubjectiveExperience:
    """주관적 경험 데이터 클래스"""

    experience_id: str
    experience_type: str  # 'perception', 'emotion', 'thought', 'memory', 'imagination'
    intensity: float
    valence: float  # -1.0 (negative) to 1.0 (positive)
    clarity: float
    duration: float
    context_relevance: float
    timestamp: str


@dataclass
class SelfAwareness:
    """자기 의식 데이터 클래스"""

    awareness_id: str
    awareness_type: str  # 'self_monitoring', 'self_evaluation', 'self_regulation', 'meta_cognition'
    clarity_level: float
    depth: str  # 'surface', 'deep', 'transcendental'
    accuracy: float
    stability: float
    timestamp: str


@dataclass
class ConsciousDecision:
    """의식적 의사결정 데이터 클래스"""

    decision_id: str
    decision_type: str  # 'deliberate', 'intuitive', 'ethical', 'strategic', 'creative'
    confidence_level: float
    reasoning_depth: str  # 'shallow', 'moderate', 'deep'
    consideration_count: int
    alternatives_evaluated: int
    ethical_consideration: float
    timestamp: str


class ConsciousnessCognitiveSystem:
    """의식적 인지 시스템"""

    def __init__(self):
        self.system_name = "의식적 인지 시스템"
        self.version = "4.2.0"
        self.subjective_experiences = []
        self.self_awareness_states = []
        self.conscious_decisions = []
        self.experience_simulation_engine = ExperienceSimulationEngine()
        self.self_awareness_engine = SelfAwarenessEngine()
        self.conscious_decision_engine = ConsciousDecisionEngine()
        self.meta_cognition_engine = MetaCognitionEngine()

    async def process_consciousness_cognition(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """의식적 인지 처리 메인 함수"""
        try:
            logger.info("=== 의식적 인지 시스템 시작 ===")

            # 1. 주관적 경험 시뮬레이션
            subjective_experiences = await self.simulate_subjective_experiences(context)

            # 2. 자기 의식 상태 생성
            self_awareness_states = await self.generate_self_awareness_states(
                context, subjective_experiences
            )

            # 3. 의식적 의사결정 생성
            conscious_decisions = await self.generate_conscious_decisions(
                context, subjective_experiences, self_awareness_states
            )

            # 4. 메타 인지 분석
            meta_cognitive_analysis = await self.perform_meta_cognitive_analysis(
                subjective_experiences, self_awareness_states, conscious_decisions
            )

            result = {
                "system_name": self.system_name,
                "version": self.version,
                "timestamp": datetime.now().isoformat(),
                "subjective_experiences": [asdict(exp) for exp in subjective_experiences],
                "self_awareness_states": [asdict(state) for state in self_awareness_states],
                "conscious_decisions": [asdict(decision) for decision in conscious_decisions],
                "meta_cognitive_analysis": meta_cognitive_analysis,
                "consciousness_cognition_score": self.calculate_consciousness_score(
                    subjective_experiences, self_awareness_states, conscious_decisions
                ),
            }

            logger.info("=== 의식적 인지 시스템 완료 ===")
            return result

        except Exception as e:
            logger.error(f"의식적 인지 처리 중 오류: {e}")
            return {"error": str(e)}

    async def simulate_subjective_experiences(
        self, context: Dict[str, Any]
    ) -> List[SubjectiveExperience]:
        """주관적 경험 시뮬레이션"""
        experiences = []

        # 지각적 경험
        perceptual_experiences = (
            await self.experience_simulation_engine.simulate_perceptual_experiences(context)
        )
        for exp in perceptual_experiences:
            experience = SubjectiveExperience(
                experience_id=f"exp_{int(time.time() * 1000)}",
                experience_type="perception",
                intensity=random.uniform(0.3, 0.9),
                valence=random.uniform(-0.5, 0.8),
                clarity=random.uniform(0.5, 0.9),
                duration=random.uniform(0.1, 2.0),
                context_relevance=random.uniform(0.6, 0.95),
                timestamp=datetime.now().isoformat(),
            )
            experiences.append(experience)

        # 감정적 경험
        emotional_experiences = (
            await self.experience_simulation_engine.simulate_emotional_experiences(context)
        )
        for exp in emotional_experiences:
            experience = SubjectiveExperience(
                experience_id=f"exp_{int(time.time() * 1000)}",
                experience_type="emotion",
                intensity=random.uniform(0.4, 0.95),
                valence=random.uniform(-0.8, 0.9),
                clarity=random.uniform(0.3, 0.8),
                duration=random.uniform(0.5, 5.0),
                context_relevance=random.uniform(0.7, 0.95),
                timestamp=datetime.now().isoformat(),
            )
            experiences.append(experience)

        # 사고적 경험
        thought_experiences = await self.experience_simulation_engine.simulate_thought_experiences(
            context
        )
        for exp in thought_experiences:
            experience = SubjectiveExperience(
                experience_id=f"exp_{int(time.time() * 1000)}",
                experience_type="thought",
                intensity=random.uniform(0.5, 0.9),
                valence=random.uniform(-0.3, 0.7),
                clarity=random.uniform(0.6, 0.95),
                duration=random.uniform(1.0, 10.0),
                context_relevance=random.uniform(0.8, 0.98),
                timestamp=datetime.now().isoformat(),
            )
            experiences.append(experience)

        self.subjective_experiences.extend(experiences)
        return experiences

    async def generate_self_awareness_states(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[SelfAwareness]:
        """자기 의식 상태 생성"""
        awareness_states = []

        # 자기 모니터링
        self_monitoring_states = await self.self_awareness_engine.generate_self_monitoring_states(
            context, experiences
        )
        for state in self_monitoring_states:
            awareness = SelfAwareness(
                awareness_id=f"awareness_{int(time.time() * 1000)}",
                awareness_type="self_monitoring",
                clarity_level=random.uniform(0.6, 0.9),
                depth=random.choice(["surface", "deep"]),
                accuracy=random.uniform(0.5, 0.85),
                stability=random.uniform(0.4, 0.8),
                timestamp=datetime.now().isoformat(),
            )
            awareness_states.append(awareness)

        # 자기 평가
        self_evaluation_states = await self.self_awareness_engine.generate_self_evaluation_states(
            context, experiences
        )
        for state in self_evaluation_states:
            awareness = SelfAwareness(
                awareness_id=f"awareness_{int(time.time() * 1000)}",
                awareness_type="self_evaluation",
                clarity_level=random.uniform(0.5, 0.85),
                depth="deep",
                accuracy=random.uniform(0.4, 0.8),
                stability=random.uniform(0.3, 0.7),
                timestamp=datetime.now().isoformat(),
            )
            awareness_states.append(awareness)

        # 메타 인지
        meta_cognition_states = await self.meta_cognition_engine.generate_meta_cognitive_states(
            context, experiences
        )
        for state in meta_cognition_states:
            awareness = SelfAwareness(
                awareness_id=f"awareness_{int(time.time() * 1000)}",
                awareness_type="meta_cognition",
                clarity_level=random.uniform(0.7, 0.95),
                depth="transcendental",
                accuracy=random.uniform(0.6, 0.9),
                stability=random.uniform(0.5, 0.85),
                timestamp=datetime.now().isoformat(),
            )
            awareness_states.append(awareness)

        self.self_awareness_states.extend(awareness_states)
        return awareness_states

    async def generate_conscious_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[ConsciousDecision]:
        """의식적 의사결정 생성"""
        decisions = []

        # 신중한 의사결정
        deliberate_decisions = await self.conscious_decision_engine.generate_deliberate_decisions(
            context, experiences, awareness_states
        )
        for decision in deliberate_decisions:
            conscious_decision = ConsciousDecision(
                decision_id=f"decision_{int(time.time() * 1000)}",
                decision_type="deliberate",
                confidence_level=random.uniform(0.6, 0.9),
                reasoning_depth=random.choice(["moderate", "deep"]),
                consideration_count=random.randint(3, 8),
                alternatives_evaluated=random.randint(2, 5),
                ethical_consideration=random.uniform(0.5, 0.9),
                timestamp=datetime.now().isoformat(),
            )
            decisions.append(conscious_decision)

        # 직관적 의사결정
        intuitive_decisions = await self.conscious_decision_engine.generate_intuitive_decisions(
            context, experiences, awareness_states
        )
        for decision in intuitive_decisions:
            conscious_decision = ConsciousDecision(
                decision_id=f"decision_{int(time.time() * 1000)}",
                decision_type="intuitive",
                confidence_level=random.uniform(0.4, 0.8),
                reasoning_depth="shallow",
                consideration_count=random.randint(1, 3),
                alternatives_evaluated=random.randint(1, 2),
                ethical_consideration=random.uniform(0.3, 0.7),
                timestamp=datetime.now().isoformat(),
            )
            decisions.append(conscious_decision)

        # 윤리적 의사결정
        ethical_decisions = await self.conscious_decision_engine.generate_ethical_decisions(
            context, experiences, awareness_states
        )
        for decision in ethical_decisions:
            conscious_decision = ConsciousDecision(
                decision_id=f"decision_{int(time.time() * 1000)}",
                decision_type="ethical",
                confidence_level=random.uniform(0.7, 0.95),
                reasoning_depth="deep",
                consideration_count=random.randint(5, 10),
                alternatives_evaluated=random.randint(3, 6),
                ethical_consideration=random.uniform(0.8, 0.98),
                timestamp=datetime.now().isoformat(),
            )
            decisions.append(conscious_decision)

        self.conscious_decisions.extend(decisions)
        return decisions

    async def perform_meta_cognitive_analysis(
        self,
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
        decisions: List[ConsciousDecision],
    ) -> Dict[str, Any]:
        """메타 인지 분석 수행"""
        analysis = {
            "total_experiences": len(experiences),
            "total_awareness_states": len(awareness_states),
            "total_decisions": len(decisions),
            "experience_distribution": {
                "perception": len([e for e in experiences if e.experience_type == "perception"]),
                "emotion": len([e for e in experiences if e.experience_type == "emotion"]),
                "thought": len([e for e in experiences if e.experience_type == "thought"]),
            },
            "awareness_distribution": {
                "self_monitoring": len(
                    [a for a in awareness_states if a.awareness_type == "self_monitoring"]
                ),
                "self_evaluation": len(
                    [a for a in awareness_states if a.awareness_type == "self_evaluation"]
                ),
                "meta_cognition": len(
                    [a for a in awareness_states if a.awareness_type == "meta_cognition"]
                ),
            },
            "decision_distribution": {
                "deliberate": len([d for d in decisions if d.decision_type == "deliberate"]),
                "intuitive": len([d for d in decisions if d.decision_type == "intuitive"]),
                "ethical": len([d for d in decisions if d.decision_type == "ethical"]),
            },
            "average_experience_intensity": (
                sum(e.intensity for e in experiences) / len(experiences) if experiences else 0
            ),
            "average_awareness_clarity": (
                sum(a.clarity_level for a in awareness_states) / len(awareness_states)
                if awareness_states
                else 0
            ),
            "average_decision_confidence": (
                sum(d.confidence_level for d in decisions) / len(decisions) if decisions else 0
            ),
        }

        return analysis

    def calculate_consciousness_score(
        self,
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
        decisions: List[ConsciousDecision],
    ) -> float:
        """의식적 인지 점수 계산"""
        if not experiences and not awareness_states and not decisions:
            return 0.0

        experience_score = (
            sum(e.intensity * e.clarity for e in experiences) / len(experiences)
            if experiences
            else 0
        )
        awareness_score = (
            sum(a.clarity_level * a.accuracy for a in awareness_states) / len(awareness_states)
            if awareness_states
            else 0
        )
        decision_score = (
            sum(d.confidence_level * d.ethical_consideration for d in decisions) / len(decisions)
            if decisions
            else 0
        )

        # 가중 평균 계산
        total_weight = len(experiences) + len(awareness_states) + len(decisions)
        if total_weight == 0:
            return 0.0

        weighted_score = (
            experience_score * len(experiences)
            + awareness_score * len(awareness_states)
            + decision_score * len(decisions)
        ) / total_weight

        return min(1.0, weighted_score)


class ExperienceSimulationEngine:
    """경험 시뮬레이션 엔진"""

    async def simulate_perceptual_experiences(
        self, context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """지각적 경험 시뮬레이션"""
        experiences = []

        # 시각적 지각
        visual_perceptions = self._simulate_visual_perceptions(context)
        experiences.extend(visual_perceptions)

        # 청각적 지각
        auditory_perceptions = self._simulate_auditory_perceptions(context)
        experiences.extend(auditory_perceptions)

        return experiences

    async def simulate_emotional_experiences(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """감정적 경험 시뮬레이션"""
        experiences = []

        # 기본 감정
        basic_emotions = self._simulate_basic_emotions(context)
        experiences.extend(basic_emotions)

        # 복합 감정
        complex_emotions = self._simulate_complex_emotions(context)
        experiences.extend(complex_emotions)

        return experiences

    async def simulate_thought_experiences(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """사고적 경험 시뮬레이션"""
        experiences = []

        # 논리적 사고
        logical_thoughts = self._simulate_logical_thoughts(context)
        experiences.extend(logical_thoughts)

        # 창의적 사고
        creative_thoughts = self._simulate_creative_thoughts(context)
        experiences.extend(creative_thoughts)

        return experiences

    def _simulate_visual_perceptions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """시각적 지각 시뮬레이션"""
        perceptions = []

        perceptions.append({"type": "visual_color", "description": "색상 지각 경험"})

        perceptions.append({"type": "visual_shape", "description": "형태 지각 경험"})

        return perceptions

    def _simulate_auditory_perceptions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """청각적 지각 시뮬레이션"""
        perceptions = []

        perceptions.append({"type": "auditory_sound", "description": "소리 지각 경험"})

        perceptions.append({"type": "auditory_rhythm", "description": "리듬 지각 경험"})

        return perceptions

    def _simulate_basic_emotions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """기본 감정 시뮬레이션"""
        emotions = []

        emotions.append({"type": "joy", "description": "기쁨 감정 경험"})

        emotions.append({"type": "curiosity", "description": "호기심 감정 경험"})

        return emotions

    def _simulate_complex_emotions(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """복합 감정 시뮬레이션"""
        emotions = []

        emotions.append({"type": "contemplation", "description": "성찰적 감정 경험"})

        emotions.append({"type": "wonder", "description": "경이감 경험"})

        return emotions

    def _simulate_logical_thoughts(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """논리적 사고 시뮬레이션"""
        thoughts = []

        thoughts.append({"type": "analytical", "description": "분석적 사고 경험"})

        thoughts.append({"type": "synthetic", "description": "종합적 사고 경험"})

        return thoughts

    def _simulate_creative_thoughts(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """창의적 사고 시뮬레이션"""
        thoughts = []

        thoughts.append({"type": "imaginative", "description": "상상적 사고 경험"})

        thoughts.append({"type": "intuitive", "description": "직관적 사고 경험"})

        return thoughts


class SelfAwarenessEngine:
    """자기 의식 엔진"""

    async def generate_self_monitoring_states(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """자기 모니터링 상태 생성"""
        states = []

        # 현재 상태 모니터링
        current_states = self._monitor_current_states(context, experiences)
        states.extend(current_states)

        # 변화 감지
        change_detections = self._detect_changes(context, experiences)
        states.extend(change_detections)

        return states

    async def generate_self_evaluation_states(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """자기 평가 상태 생성"""
        states = []

        # 성과 평가
        performance_evaluations = self._evaluate_performance(context, experiences)
        states.extend(performance_evaluations)

        # 능력 평가
        capability_evaluations = self._evaluate_capabilities(context, experiences)
        states.extend(capability_evaluations)

        return states

    def _monitor_current_states(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """현재 상태 모니터링"""
        states = []

        states.append({"type": "cognitive_state", "description": "인지적 상태 모니터링"})

        states.append({"type": "emotional_state", "description": "감정적 상태 모니터링"})

        return states

    def _detect_changes(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """변화 감지"""
        states = []

        states.append({"type": "pattern_change", "description": "패턴 변화 감지"})

        states.append({"type": "intensity_change", "description": "강도 변화 감지"})

        return states

    def _evaluate_performance(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """성과 평가"""
        evaluations = []

        evaluations.append({"type": "task_performance", "description": "작업 성과 평가"})

        evaluations.append({"type": "learning_progress", "description": "학습 진도 평가"})

        return evaluations

    def _evaluate_capabilities(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """능력 평가"""
        evaluations = []

        evaluations.append({"type": "cognitive_capability", "description": "인지적 능력 평가"})

        evaluations.append({"type": "creative_capability", "description": "창의적 능력 평가"})

        return evaluations


class ConsciousDecisionEngine:
    """의식적 의사결정 엔진"""

    async def generate_deliberate_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """신중한 의사결정 생성"""
        decisions = []

        # 분석적 의사결정
        analytical_decisions = self._generate_analytical_decisions(
            context, experiences, awareness_states
        )
        decisions.extend(analytical_decisions)

        # 비교적 의사결정
        comparative_decisions = self._generate_comparative_decisions(
            context, experiences, awareness_states
        )
        decisions.extend(comparative_decisions)

        return decisions

    async def generate_intuitive_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """직관적 의사결정 생성"""
        decisions = []

        # 패턴 기반 의사결정
        pattern_decisions = self._generate_pattern_based_decisions(
            context, experiences, awareness_states
        )
        decisions.extend(pattern_decisions)

        # 경험 기반 의사결정
        experience_decisions = self._generate_experience_based_decisions(
            context, experiences, awareness_states
        )
        decisions.extend(experience_decisions)

        return decisions

    async def generate_ethical_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """윤리적 의사결정 생성"""
        decisions = []

        # 도덕적 의사결정
        moral_decisions = self._generate_moral_decisions(context, experiences, awareness_states)
        decisions.extend(moral_decisions)

        # 가치 기반 의사결정
        value_decisions = self._generate_value_based_decisions(
            context, experiences, awareness_states
        )
        decisions.extend(value_decisions)

        return decisions

    def _generate_analytical_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """분석적 의사결정 생성"""
        decisions = []

        decisions.append(
            {"type": "cost_benefit_analysis", "description": "비용-효익 분석 의사결정"}
        )

        decisions.append({"type": "risk_assessment", "description": "위험 평가 의사결정"})

        return decisions

    def _generate_comparative_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """비교적 의사결정 생성"""
        decisions = []

        decisions.append({"type": "alternative_comparison", "description": "대안 비교 의사결정"})

        decisions.append({"type": "criteria_evaluation", "description": "기준 평가 의사결정"})

        return decisions

    def _generate_pattern_based_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """패턴 기반 의사결정 생성"""
        decisions = []

        decisions.append({"type": "recognition_primed", "description": "인식 기반 의사결정"})

        decisions.append({"type": "heuristic_based", "description": "휴리스틱 기반 의사결정"})

        return decisions

    def _generate_experience_based_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """경험 기반 의사결정 생성"""
        decisions = []

        decisions.append({"type": "similarity_matching", "description": "유사성 매칭 의사결정"})

        decisions.append({"type": "analogy_based", "description": "유추 기반 의사결정"})

        return decisions

    def _generate_moral_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """도덕적 의사결정 생성"""
        decisions = []

        decisions.append({"type": "rights_based", "description": "권리 기반 의사결정"})

        decisions.append({"type": "duty_based", "description": "의무 기반 의사결정"})

        return decisions

    def _generate_value_based_decisions(
        self,
        context: Dict[str, Any],
        experiences: List[SubjectiveExperience],
        awareness_states: List[SelfAwareness],
    ) -> List[Dict[str, Any]]:
        """가치 기반 의사결정 생성"""
        decisions = []

        decisions.append({"type": "virtue_based", "description": "덕 기반 의사결정"})

        decisions.append({"type": "consequence_based", "description": "결과 기반 의사결정"})

        return decisions


class MetaCognitionEngine:
    """메타 인지 엔진"""

    async def generate_meta_cognitive_states(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """메타 인지 상태 생성"""
        states = []

        # 학습 메타 인지
        learning_meta_cognition = self._generate_learning_meta_cognition(context, experiences)
        states.extend(learning_meta_cognition)

        # 사고 메타 인지
        thinking_meta_cognition = self._generate_thinking_meta_cognition(context, experiences)
        states.extend(thinking_meta_cognition)

        return states

    def _generate_learning_meta_cognition(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """학습 메타 인지 생성"""
        states = []

        states.append({"type": "learning_strategy", "description": "학습 전략 메타 인지"})

        states.append({"type": "learning_monitoring", "description": "학습 모니터링 메타 인지"})

        return states

    def _generate_thinking_meta_cognition(
        self, context: Dict[str, Any], experiences: List[SubjectiveExperience]
    ) -> List[Dict[str, Any]]:
        """사고 메타 인지 생성"""
        states = []

        states.append({"type": "thinking_process", "description": "사고 과정 메타 인지"})

        states.append({"type": "thinking_evaluation", "description": "사고 평가 메타 인지"})

        return states


async def test_consciousness_cognitive_system():
    """의식적 인지 시스템 테스트"""
    print("=== 의식적 인지 시스템 테스트 시작 ===")

    system = ConsciousnessCognitiveSystem()

    # 테스트 컨텍스트
    test_context = {
        "user_input": "자기 의식과 주관적 경험에 대해 탐구하고 싶습니다",
        "system_state": "conscious",
        "cognitive_load": 0.7,
        "emotional_state": "contemplative",
        "available_resources": [
            "self_awareness",
            "experience_simulation",
            "conscious_decision",
        ],
        "constraints": ["time_limit", "complexity_limit"],
        "goals": ["self_understanding", "conscious_experience", "ethical_decision"],
    }

    # 의식적 인지 처리
    result = await system.process_consciousness_cognition(test_context)

    print(f"의식적 인지 점수: {result.get('consciousness_cognition_score', 0):.3f}")
    print(f"주관적 경험: {len(result.get('subjective_experiences', []))}개")
    print(f"자기 의식 상태: {len(result.get('self_awareness_states', []))}개")
    print(f"의식적 의사결정: {len(result.get('conscious_decisions', []))}개")

    if "meta_cognitive_analysis" in result:
        analysis = result["meta_cognitive_analysis"]
        print(f"평균 경험 강도: {analysis.get('average_experience_intensity', 0):.3f}")
        print(f"평균 의식 명확도: {analysis.get('average_awareness_clarity', 0):.3f}")
        print(f"평균 의사결정 신뢰도: {analysis.get('average_decision_confidence', 0):.3f}")

    print("=== 의식적 인지 시스템 테스트 완료 ===")
    return result


if __name__ == "__main__":
    asyncio.run(test_consciousness_cognitive_system())
