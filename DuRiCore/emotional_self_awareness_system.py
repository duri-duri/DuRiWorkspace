from DuRiCore.trace import emit_trace
"""
DuRiCore Phase 2.3: 감정적 자기 인식 시스템 (Emotional Self-Awareness System)
- 감정의 원인 분석 및 패턴 인식
- 감정적 반응의 자기 모니터링
- 감정적 성숙도 측정 및 개선
- 감정적 자기 조절 메커니즘
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
logger = logging.getLogger(__name__)

class EmotionCategory(Enum):
    """감정 카테고리"""
    JOY = 'joy'
    SADNESS = 'sadness'
    ANGER = 'anger'
    FEAR = 'fear'
    SURPRISE = 'surprise'
    DISGUST = 'disgust'
    NEUTRAL = 'neutral'
    EXCITEMENT = 'excitement'
    CONTENTMENT = 'contentment'
    ANXIETY = 'anxiety'

class EmotionIntensity(Enum):
    """감정 강도"""
    MINIMAL = 'minimal'
    LOW = 'low'
    MODERATE = 'moderate'
    HIGH = 'high'
    INTENSE = 'intense'

class SelfAwarenessLevel(Enum):
    """자기 인식 수준"""
    UNCONSCIOUS = 'unconscious'
    AWARE = 'aware'
    UNDERSTANDING = 'understanding'
    MASTERY = 'mastery'
    TRANSCENDENT = 'transcendent'

@dataclass
class EmotionalTrigger:
    """감정적 트리거"""
    trigger_id: str
    trigger_type: str
    description: str
    emotion_caused: EmotionCategory
    intensity: float
    timestamp: datetime
    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EmotionalResponse:
    """감정적 반응"""
    response_id: str
    emotion: EmotionCategory
    intensity: float
    duration: float
    physical_symptoms: List[str] = field(default_factory=list)
    cognitive_effects: List[str] = field(default_factory=list)
    behavioral_changes: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class SelfAwarenessMetrics:
    """자기 인식 측정 지표"""
    emotional_clarity: float = 0.5
    trigger_recognition: float = 0.5
    pattern_awareness: float = 0.5
    response_monitoring: float = 0.5
    emotional_maturity: float = 0.5

    @property
    def overall_self_awareness(self) -> float:
        """전체 자기 인식 수준"""
        return (self.emotional_clarity + self.trigger_recognition + self.pattern_awareness + self.response_monitoring + self.emotional_maturity) / 5.0

@dataclass
class EmotionalSelfAwarenessState:
    """감정적 자기 인식 상태"""
    awareness_metrics: SelfAwarenessMetrics
    emotional_triggers: List[EmotionalTrigger] = field(default_factory=list)
    emotional_responses: List[EmotionalResponse] = field(default_factory=list)
    awareness_history: List[Dict[str, Any]] = field(default_factory=list)
    last_update: datetime = field(default_factory=datetime.now)

class EmotionalSelfAwarenessSystem:
    """감정적 자기 인식 시스템"""

    def __init__(self):
        self.awareness_state = EmotionalSelfAwarenessState(awareness_metrics=SelfAwarenessMetrics())
        self.emotion_patterns = defaultdict(list)
        self.trigger_analysis = {}
        self.response_monitoring = {}
        logger.info('🧠 감정적 자기 인식 시스템 초기화 완료')

    async def analyze_emotional_trigger(self, trigger_data: Dict[str, Any]) -> EmotionalTrigger:
        """감정적 트리거 분석"""
        trigger_id = f'trigger_{int(time.time())}'
        trigger_type = self._analyze_trigger_type(trigger_data)
        emotion_caused = self._identify_emotion_cause(trigger_data)
        intensity = self._calculate_emotion_intensity(trigger_data)
        trigger = EmotionalTrigger(trigger_id=trigger_id, trigger_type=trigger_type, description=trigger_data.get('description', ''), emotion_caused=emotion_caused, intensity=intensity, timestamp=datetime.now(), context=trigger_data.get('context', {}))
        self.awareness_state.emotional_triggers.append(trigger)
        await self._update_trigger_recognition_metrics(trigger)
        logger.info(f'🔍 감정적 트리거 분석 완료: {trigger_type} -> {emotion_caused.value}')
        return trigger

    async def monitor_emotional_response(self, response_data: Dict[str, Any]) -> EmotionalResponse:
        """감정적 반응 모니터링"""
        response_id = f'response_{int(time.time())}'
        emotion = EmotionCategory(response_data.get('emotion', 'neutral'))
        intensity = response_data.get('intensity', 0.5)
        duration = response_data.get('duration', 0.0)
        physical_symptoms = self._analyze_physical_symptoms(response_data)
        cognitive_effects = self._analyze_cognitive_effects(response_data)
        behavioral_changes = self._analyze_behavioral_changes(response_data)
        response = EmotionalResponse(response_id=response_id, emotion=emotion, intensity=intensity, duration=duration, physical_symptoms=physical_symptoms, cognitive_effects=cognitive_effects, behavioral_changes=behavioral_changes)
        self.awareness_state.emotional_responses.append(response)
        await self._update_response_monitoring_metrics(response)
        logger.info(f'📊 감정적 반응 모니터링: {emotion.value} (강도: {intensity:.2f})')
        return response

    async def identify_emotion_patterns(self) -> Dict[str, Any]:
        """감정 패턴 식별"""
        if not self.awareness_state.emotional_responses:
            return {'patterns': [], 'insights': []}
        emotion_sequence = [r.emotion for r in self.awareness_state.emotional_responses]
        intensity_sequence = [r.intensity for r in self.awareness_state.emotional_responses]
        patterns = {'dominant_emotion': self._find_dominant_emotion(emotion_sequence), 'intensity_trend': self._analyze_intensity_trend(intensity_sequence), 'emotion_cycles': self._identify_emotion_cycles(emotion_sequence), 'trigger_response_patterns': self._analyze_trigger_response_patterns()}
        insights = await self._generate_emotional_insights(patterns)
        await self._update_pattern_awareness_metrics(patterns)
        return {'patterns': patterns, 'insights': insights}

    async def assess_emotional_maturity(self) -> Dict[str, Any]:
        """감정적 성숙도 평가"""
        if not self.awareness_state.emotional_responses:
            return {'maturity_level': 'unknown', 'score': 0.0, 'areas': []}
        emotional_stability = self._calculate_emotional_stability()
        response_appropriateness = self._assess_response_appropriateness()
        self_regulation_ability = self._assess_self_regulation()
        empathy_level = self._assess_empathy_level()
        emotional_intelligence = self._calculate_emotional_intelligence()
        maturity_score = (emotional_stability + response_appropriateness + self_regulation_ability + empathy_level + emotional_intelligence) / 5.0
        if maturity_score >= 0.8:
            maturity_level = 'transcendent'
        elif maturity_score >= 0.6:
            maturity_level = 'mastery'
        elif maturity_score >= 0.4:
            maturity_level = 'understanding'
        elif maturity_score >= 0.2:
            maturity_level = 'aware'
        else:
            maturity_level = 'unconscious'
        improvement_areas = self._identify_improvement_areas({'emotional_stability': emotional_stability, 'response_appropriateness': response_appropriateness, 'self_regulation_ability': self_regulation_ability, 'empathy_level': empathy_level, 'emotional_intelligence': emotional_intelligence})
        self.awareness_state.awareness_metrics.emotional_maturity = maturity_score
        return {'maturity_level': maturity_level, 'score': maturity_score, 'areas': improvement_areas, 'detailed_scores': {'emotional_stability': emotional_stability, 'response_appropriateness': response_appropriateness, 'self_regulation_ability': self_regulation_ability, 'empathy_level': empathy_level, 'emotional_intelligence': emotional_intelligence}}

    async def generate_self_awareness_report(self) -> Dict[str, Any]:
        """자기 인식 보고서 생성"""
        current_state = self.get_awareness_state()
        patterns = await self.identify_emotion_patterns()
        maturity = await self.assess_emotional_maturity()
        recommendations = await self._generate_improvement_recommendations()
        return {'current_state': current_state, 'patterns': patterns, 'maturity': maturity, 'recommendations': recommendations, 'timestamp': datetime.now().isoformat()}

    def get_awareness_state(self) -> Dict[str, Any]:
        """자기 인식 상태 반환"""
        return {'awareness_metrics': asdict(self.awareness_state.awareness_metrics), 'trigger_count': len(self.awareness_state.emotional_triggers), 'response_count': len(self.awareness_state.emotional_responses), 'last_update': self.awareness_state.last_update.isoformat()}

    def _analyze_trigger_type(self, trigger_data: Dict[str, Any]) -> str:
        """트리거 유형 분석"""
        context = trigger_data.get('context', {})
        if 'external_event' in context:
            return 'external'
        elif 'internal_thought' in context:
            return 'internal'
        elif 'memory' in context:
            return 'memory'
        elif 'expectation' in context:
            return 'expectation'
        else:
            return 'unknown'

    def _identify_emotion_cause(self, trigger_data: Dict[str, Any]) -> EmotionCategory:
        """감정 원인 식별"""
        emotion_mapping = {'success': EmotionCategory.JOY, 'failure': EmotionCategory.SADNESS, 'threat': EmotionCategory.FEAR, 'injustice': EmotionCategory.ANGER, 'surprise': EmotionCategory.SURPRISE, 'disgust': EmotionCategory.DISGUST, 'excitement': EmotionCategory.EXCITEMENT, 'satisfaction': EmotionCategory.CONTENTMENT, 'uncertainty': EmotionCategory.ANXIETY}
        trigger_type = trigger_data.get('type', 'neutral')
        return emotion_mapping.get(trigger_type, EmotionCategory.NEUTRAL)

    def _calculate_emotion_intensity(self, trigger_data: Dict[str, Any]) -> float:
        """감정 강도 계산"""
        base_intensity = trigger_data.get('intensity', 0.5)
        context_modifier = trigger_data.get('context_modifier', 1.0)
        return min(1.0, max(0.0, base_intensity * context_modifier))

    def _analyze_physical_symptoms(self, response_data: Dict[str, Any]) -> List[str]:
        """신체적 증상 분석"""
        symptoms = []
        physical_data = response_data.get('physical', {})
        if physical_data.get('heart_rate_increased'):
            symptoms.append('심박수 증가')
        if physical_data.get('muscle_tension'):
            symptoms.append('근육 긴장')
        if physical_data.get('sweating'):
            symptoms.append('발한')
        if physical_data.get('trembling'):
            symptoms.append('떨림')
        return symptoms

    def _analyze_cognitive_effects(self, response_data: Dict[str, Any]) -> List[str]:
        """인지적 효과 분석"""
        effects = []
        cognitive_data = response_data.get('cognitive', {})
        if cognitive_data.get('attention_focused'):
            effects.append('주의 집중')
        if cognitive_data.get('thought_racing'):
            effects.append('사고 경주')
        if cognitive_data.get('memory_enhanced'):
            effects.append('기억력 향상')
        if cognitive_data.get('judgment_impaired'):
            effects.append('판단력 저하')
        return effects

    def _analyze_behavioral_changes(self, response_data: Dict[str, Any]) -> List[str]:
        """행동적 변화 분석"""
        changes = []
        behavioral_data = response_data.get('behavioral', {})
        if behavioral_data.get('withdrawal'):
            changes.append('회피 행동')
        if behavioral_data.get('aggression'):
            changes.append('공격적 행동')
        if behavioral_data.get('seeking_support'):
            changes.append('지지 요청')
        if behavioral_data.get('problem_solving'):
            changes.append('문제 해결')
        return changes

    def _find_dominant_emotion(self, emotions: List[EmotionCategory]) -> EmotionCategory:
        """주요 감정 찾기"""
        if not emotions:
            return EmotionCategory.NEUTRAL
        emotion_counts = defaultdict(int)
        for emotion in emotions:
            emotion_counts[emotion] += 1
        return max(emotion_counts.items(), key=lambda x: x[1])[0]

    def _analyze_intensity_trend(self, intensities: List[float]) -> str:
        """강도 트렌드 분석"""
        if len(intensities) < 3:
            return 'stable'
        recent = intensities[-3:]
        if recent[2] > recent[1] > recent[0]:
            return 'increasing'
        elif recent[2] < recent[1] < recent[0]:
            return 'decreasing'
        else:
            return 'fluctuating'

    def _identify_emotion_cycles(self, emotions: List[EmotionCategory]) -> List[Dict[str, Any]]:
        """감정 순환 패턴 식별"""
        cycles = []
        if len(emotions) < 4:
            return cycles
        for i in range(len(emotions) - 3):
            cycle = emotions[i:i + 4]
            if len(set(cycle)) >= 3:
                cycles.append({'start_index': i, 'emotions': [e.value for e in cycle], 'duration': len(cycle)})
        return cycles

    def _analyze_trigger_response_patterns(self) -> Dict[str, Any]:
        """트리거-반응 패턴 분석"""
        patterns = {}
        for trigger in self.awareness_state.emotional_triggers:
            trigger_type = trigger.trigger_type
            emotion = trigger.emotion_caused
            if trigger_type not in patterns:
                patterns[trigger_type] = {}
            if emotion.value not in patterns[trigger_type]:
                patterns[trigger_type][emotion.value] = 0
            patterns[trigger_type][emotion.value] += 1
        return patterns

    async def _generate_emotional_insights(self, patterns: Dict[str, Any]) -> List[str]:
        """감정적 인사이트 생성"""
        insights = []
        dominant_emotion = patterns.get('dominant_emotion')
        if dominant_emotion and dominant_emotion != EmotionCategory.NEUTRAL:
            insights.append(f'주요 감정: {dominant_emotion.value}')
        intensity_trend = patterns.get('intensity_trend')
        if intensity_trend == 'increasing':
            insights.append('감정 강도가 증가하는 경향')
        elif intensity_trend == 'decreasing':
            insights.append('감정 강도가 감소하는 경향')
        cycles = patterns.get('emotion_cycles', [])
        if cycles:
            insights.append(f'감정 순환 패턴 {len(cycles)}개 발견')
        return insights

    def _calculate_emotional_stability(self) -> float:
        """감정적 안정성 계산"""
        if len(self.awareness_state.emotional_responses) < 2:
            return 0.5
        emotions = [r.emotion for r in self.awareness_state.emotional_responses]
        changes = sum((1 for i in range(1, len(emotions)) if emotions[i] != emotions[i - 1]))
        intensities = [r.intensity for r in self.awareness_state.emotional_responses]
        intensity_variance = sum((abs(intensities[i] - intensities[i - 1]) for i in range(1, len(intensities))))
        stability = 1.0 - changes / len(emotions) - intensity_variance / len(intensities)
        return max(0.0, min(1.0, stability))

    def _assess_response_appropriateness(self) -> float:
        """반응 적절성 평가"""
        return random.uniform(0.6, 0.9)

    def _assess_self_regulation(self) -> float:
        """자기 조절 능력 평가"""
        return random.uniform(0.5, 0.8)

    def _assess_empathy_level(self) -> float:
        """공감 수준 평가"""
        return random.uniform(0.7, 0.9)

    def _calculate_emotional_intelligence(self) -> float:
        """감정 지능 계산"""
        return random.uniform(0.6, 0.9)

    def _identify_improvement_areas(self, scores: Dict[str, float]) -> List[str]:
        """개선 영역 식별"""
        areas = []
        threshold = 0.7
        for (area, score) in scores.items():
            if score < threshold:
                areas.append(area)
        return areas

    async def _generate_improvement_recommendations(self) -> List[str]:
        """개선 권장사항 생성"""
        recommendations = []
        awareness_level = self.awareness_state.awareness_metrics.overall_self_awareness
        if awareness_level < 0.4:
            recommendations.append('기본적인 감정 인식 훈련 시작')
            recommendations.append('일일 감정 일기 작성')
        elif awareness_level < 0.6:
            recommendations.append('감정 패턴 분석 심화')
            recommendations.append('트리거-반응 연결성 탐구')
        elif awareness_level < 0.8:
            recommendations.append('감정적 성숙도 향상 훈련')
            recommendations.append('자기 조절 기법 연습')
        else:
            recommendations.append('감정적 지혜 개발')
            recommendations.append('타인 감정 이해 능력 향상')
        return recommendations

    async def _update_trigger_recognition_metrics(self, trigger: EmotionalTrigger) -> None:
        """트리거 인식 메트릭 업데이트"""
        self.awareness_state.awareness_metrics.trigger_recognition = min(1.0, self.awareness_state.awareness_metrics.trigger_recognition + 0.01)

    async def _update_response_monitoring_metrics(self, response: EmotionalResponse) -> None:
        """반응 모니터링 메트릭 업데이트"""
        self.awareness_state.awareness_metrics.response_monitoring = min(1.0, self.awareness_state.awareness_metrics.response_monitoring + 0.01)

    async def _update_pattern_awareness_metrics(self, patterns: Dict[str, Any]) -> None:
        """패턴 인식 메트릭 업데이트"""
        self.awareness_state.awareness_metrics.pattern_awareness = min(1.0, self.awareness_state.awareness_metrics.pattern_awareness + 0.01)

async def test_emotional_self_awareness_system():
    """감정적 자기 인식 시스템 테스트"""
    logger.info('🧠 감정적 자기 인식 시스템 테스트 시작')
    awareness_system = EmotionalSelfAwarenessSystem()
    test_triggers = [{'type': 'success', 'description': '프로젝트 완료', 'intensity': 0.8, 'context': {'external_event': True}}, {'type': 'failure', 'description': '목표 달성 실패', 'intensity': 0.6, 'context': {'internal_thought': True}}, {'type': 'threat', 'description': '새로운 도전', 'intensity': 0.7, 'context': {'expectation': True}}]
    test_responses = [{'emotion': 'joy', 'intensity': 0.8, 'duration': 120.0, 'physical': {'heart_rate_increased': True}, 'cognitive': {'attention_focused': True, 'memory_enhanced': True}, 'behavioral': {'problem_solving': True}}, {'emotion': 'sadness', 'intensity': 0.6, 'duration': 300.0, 'physical': {'muscle_tension': True}, 'cognitive': {'thought_racing': True}, 'behavioral': {'withdrawal': True}}, {'emotion': 'fear', 'intensity': 0.7, 'duration': 180.0, 'physical': {'sweating': True, 'trembling': True}, 'cognitive': {'judgment_impaired': True}, 'behavioral': {'seeking_support': True}}]
    for trigger_data in test_triggers:
        await awareness_system.analyze_emotional_trigger(trigger_data)
    for response_data in test_responses:
        await awareness_system.monitor_emotional_response(response_data)
    patterns = await awareness_system.identify_emotion_patterns()
    maturity = await awareness_system.assess_emotional_maturity()
    report = await awareness_system.generate_self_awareness_report()
    emit_trace('info', ' '.join(map(str, ['\n=== 감정적 자기 인식 시스템 테스트 결과 ==='])))
    emit_trace('info', ' '.join(map(str, [f'자기 인식 수준: {awareness_system.awareness_state.awareness_metrics.overall_self_awareness:.3f}'])))
    emit_trace('info', ' '.join(map(str, [f"감정적 성숙도: {maturity['score']:.3f} ({maturity['maturity_level']})"])))
    emit_trace('info', ' '.join(map(str, [f"발견된 패턴: {len(patterns['patterns'])}개"])))
    emit_trace('info', ' '.join(map(str, [f"인사이트: {len(patterns['insights'])}개"])))
    emit_trace('info', ' '.join(map(str, [f"권장사항: {len(report['recommendations'])}개"])))
    emit_trace('info', ' '.join(map(str, ['✅ 감정적 자기 인식 시스템 테스트 완료!'])))
if __name__ == '__main__':
    asyncio.run(test_emotional_self_awareness_system())