"""
Day 8: 감정 지능 시스템
복합 감정 분석, 감정-이성 균형, 공감 능력 구현
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc
from collections import Counter, defaultdict
import numpy as np

# from ..models.memory import MemoryEntry
# from ..utils.retry_decorator import retry_on_db_error

logger = logging.getLogger(__name__)

class EmotionalIntelligenceService:
    """감정 지능 서비스 - 고급 감정 처리 및 공감 능력"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.emotion_dimensions = [
            "joy", "anger", "fear", "trust", "surprise", 
            "sadness", "anticipation", "disgust"
        ]
        self.emotion_weights = {
            "joy": 0.8, "anger": -0.6, "fear": -0.7, "trust": 0.9,
            "surprise": 0.3, "sadness": -0.8, "anticipation": 0.6, "disgust": -0.5
        }
        
    def analyze_complex_emotion(self, emotion_data: Dict[str, Any]) -> Dict[str, Any]:
        """복합 감정 분석"""
        try:
            # 1. 기본 감정 추출
            primary_emotion = emotion_data.get('primary_emotion', 'neutral')
            secondary_emotions = emotion_data.get('secondary_emotions', [])
            intensity = emotion_data.get('intensity', 0.5)
            context = emotion_data.get('context', {})
            
            # 2. 복합 감정 분석
            complex_analysis = self._analyze_emotion_combination(
                primary_emotion, secondary_emotions, intensity
            )
            
            # 3. 맥락 기반 감정 해석
            contextual_emotion = self._analyze_contextual_emotion(
                complex_analysis, context
            )
            
            # 4. 감정-이성 균형 계산
            emotion_reason_balance = self._calculate_emotion_reason_balance(
                contextual_emotion, context
            )
            
            # 5. 공감적 반응 생성
            empathetic_response = self._generate_empathetic_response(
                contextual_emotion, emotion_reason_balance
            )
            
            return {
                "complex_emotion": complex_analysis,
                "contextual_emotion": contextual_emotion,
                "emotion_reason_balance": emotion_reason_balance,
                "empathetic_response": empathetic_response,
                "confidence": self._calculate_analysis_confidence(complex_analysis)
            }
            
        except Exception as e:
            logger.error(f"복합 감정 분석 실패: {e}")
            return {"error": str(e)}
    
    def _analyze_emotion_combination(
        self, 
        primary: str, 
        secondary: List[str], 
        intensity: float
    ) -> Dict[str, Any]:
        """감정 조합 분석"""
        try:
            # 감정 벡터 생성
            emotion_vector = {dim: 0.0 for dim in self.emotion_dimensions}
            
            # 주요 감정 설정
            if primary in self.emotion_dimensions:
                emotion_vector[primary] = intensity
            
            # 보조 감정들 추가
            for sec_emotion in secondary:
                if sec_emotion in self.emotion_dimensions:
                    emotion_vector[sec_emotion] = min(intensity * 0.7, 1.0)
            
            # 감정 충돌 분석
            conflicts = self._detect_emotion_conflicts(emotion_vector)
            
            # 감정 안정성 계산
            stability = self._calculate_emotion_stability(emotion_vector)
            
            # 복합 감정 타입 결정
            complex_type = self._determine_complex_emotion_type(emotion_vector)
            
            return {
                "emotion_vector": emotion_vector,
                "conflicts": conflicts,
                "stability": stability,
                "complex_type": complex_type,
                "intensity": intensity
            }
            
        except Exception as e:
            logger.error(f"감정 조합 분석 실패: {e}")
            return {}
    
    def _detect_emotion_conflicts(self, emotion_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """감정 충돌 탐지"""
        conflicts = []
        
        # 대립되는 감정들 확인
        opposing_pairs = [
            ("joy", "sadness"), ("trust", "fear"), 
            ("anticipation", "surprise"), ("anger", "trust")
        ]
        
        for emotion1, emotion2 in opposing_pairs:
            if (emotion_vector.get(emotion1, 0) > 0.3 and 
                emotion_vector.get(emotion2, 0) > 0.3):
                conflicts.append({
                    "type": "opposing_emotions",
                    "emotions": [emotion1, emotion2],
                    "intensity": min(emotion_vector[emotion1], emotion_vector[emotion2]),
                    "severity": "moderate" if min(emotion_vector[emotion1], emotion_vector[emotion2]) < 0.6 else "high"
                })
        
        return conflicts
    
    def _calculate_emotion_stability(self, emotion_vector: Dict[str, float]) -> float:
        """감정 안정성 계산"""
        try:
            # 감정 강도들의 표준편차 계산
            intensities = [v for v in emotion_vector.values() if v > 0]
            
            if not intensities:
                return 1.0  # 감정이 없으면 안정적
            
            mean_intensity = np.mean(intensities)
            std_intensity = np.std(intensities)
            
            # 안정성 점수 계산 (0-1, 높을수록 안정적)
            stability = max(0, 1 - (std_intensity / mean_intensity if mean_intensity > 0 else 0))
            
            return min(1.0, stability)
            
        except Exception as e:
            logger.error(f"감정 안정성 계산 실패: {e}")
            return 0.5
    
    def _determine_complex_emotion_type(self, emotion_vector: Dict[str, float]) -> str:
        """복합 감정 타입 결정"""
        try:
            # 가장 강한 감정들 찾기
            sorted_emotions = sorted(
                emotion_vector.items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            top_emotions = [emotion for emotion, intensity in sorted_emotions if intensity > 0.3]
            
            if len(top_emotions) == 0:
                return "neutral"
            elif len(top_emotions) == 1:
                return f"primary_{top_emotions[0]}"
            elif len(top_emotions) == 2:
                return f"dual_{top_emotions[0]}_{top_emotions[1]}"
            else:
                return f"complex_{top_emotions[0]}_dominant"
                
        except Exception as e:
            logger.error(f"복합 감정 타입 결정 실패: {e}")
            return "unknown"
    
    def _are_opposing_emotions(self, emotion1: str, emotion2: str) -> bool:
        """대립되는 감정인지 확인"""
        opposing_pairs = [
            ("joy", "sadness"), ("trust", "fear"), 
            ("anticipation", "surprise"), ("anger", "trust")
        ]
        
        return (emotion1, emotion2) in opposing_pairs or (emotion2, emotion1) in opposing_pairs
    
    def _analyze_contextual_emotion(
        self, 
        complex_analysis: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """맥락 기반 감정 해석"""
        try:
            emotion_vector = complex_analysis.get('emotion_vector', {})
            context_type = context.get('type', 'general')
            social_context = context.get('social', {})
            environmental_context = context.get('environmental', {})
            
            # 맥락별 감정 해석
            contextual_interpretation = {
                "work_context": self._interpret_work_emotion(emotion_vector, context),
                "social_context": self._interpret_social_emotion(emotion_vector, social_context),
                "personal_context": self._interpret_personal_emotion(emotion_vector, context)
            }
            
            # 맥락 적합성 평가
            context_fit = self._evaluate_context_fit(emotion_vector, context)
            
            # 맥락별 권장사항
            recommendations = self._generate_context_recommendations(
                contextual_interpretation, context_fit
            )
            
            return {
                "interpretation": contextual_interpretation,
                "context_fit": context_fit,
                "recommendations": recommendations,
                "context_type": context_type
            }
            
        except Exception as e:
            logger.error(f"맥락 기반 감정 해석 실패: {e}")
            return {}
    
    def _interpret_work_emotion(self, emotion_vector: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """업무 맥락 감정 해석"""
        work_stress = emotion_vector.get('fear', 0) + emotion_vector.get('anger', 0)
        work_satisfaction = emotion_vector.get('joy', 0) + emotion_vector.get('trust', 0)
        
        return {
            "stress_level": work_stress,
            "satisfaction_level": work_satisfaction,
            "productivity_impact": "positive" if work_satisfaction > work_stress else "negative",
            "recommendation": "break_needed" if work_stress > 0.6 else "continue"
        }
    
    def _interpret_social_emotion(self, emotion_vector: Dict[str, float], social_context: Dict[str, Any]) -> Dict[str, Any]:
        """사회적 맥락 감정 해석"""
        social_comfort = emotion_vector.get('trust', 0) + emotion_vector.get('joy', 0)
        social_anxiety = emotion_vector.get('fear', 0) + emotion_vector.get('sadness', 0)
        
        return {
            "comfort_level": social_comfort,
            "anxiety_level": social_anxiety,
            "social_readiness": "ready" if social_comfort > social_anxiety else "cautious",
            "recommendation": "engage" if social_comfort > 0.5 else "withdraw"
        }
    
    def _interpret_personal_emotion(self, emotion_vector: Dict[str, float], context: Dict[str, Any]) -> Dict[str, Any]:
        """개인적 맥락 감정 해석"""
        personal_wellbeing = emotion_vector.get('joy', 0) + emotion_vector.get('trust', 0)
        personal_distress = emotion_vector.get('sadness', 0) + emotion_vector.get('fear', 0)
        
        return {
            "wellbeing_level": personal_wellbeing,
            "distress_level": personal_distress,
            "self_care_needed": personal_distress > 0.5,
            "recommendation": "self_care" if personal_distress > 0.5 else "maintain"
        }
    
    def _evaluate_context_fit(self, emotion_vector: Dict[str, float], context: Dict[str, Any]) -> float:
        """맥락 적합성 평가"""
        try:
            context_type = context.get('type', 'general')
            
            if context_type == 'work':
                # 업무 맥락에서는 스트레스가 낮고 만족도가 높을 때 적합
                stress = emotion_vector.get('fear', 0) + emotion_vector.get('anger', 0)
                satisfaction = emotion_vector.get('joy', 0) + emotion_vector.get('trust', 0)
                return max(0, satisfaction - stress)
            
            elif context_type == 'social':
                # 사회적 맥락에서는 편안함이 높을 때 적합
                comfort = emotion_vector.get('trust', 0) + emotion_vector.get('joy', 0)
                anxiety = emotion_vector.get('fear', 0) + emotion_vector.get('sadness', 0)
                return max(0, comfort - anxiety)
            
            else:
                # 일반적인 맥락에서는 긍정적 감정이 높을 때 적합
                positive = emotion_vector.get('joy', 0) + emotion_vector.get('trust', 0)
                negative = emotion_vector.get('sadness', 0) + emotion_vector.get('fear', 0)
                return max(0, positive - negative)
                
        except Exception as e:
            logger.error(f"맥락 적합성 평가 실패: {e}")
            return 0.5
    
    def _generate_context_recommendations(
        self, 
        interpretation: Dict[str, Any], 
        context_fit: float
    ) -> List[str]:
        """맥락별 권장사항 생성"""
        recommendations = []
        
        if context_fit < 0.3:
            recommendations.append("감정 조절이 필요합니다")
            recommendations.append("맥락에 맞지 않는 감정 상태입니다")
        
        if interpretation.get('work_context', {}).get('stress_level', 0) > 0.6:
            recommendations.append("업무 스트레스가 높습니다. 휴식이 필요합니다")
        
        if interpretation.get('social_context', {}).get('anxiety_level', 0) > 0.5:
            recommendations.append("사회적 불안이 있습니다. 천천히 접근하세요")
        
        return recommendations
    
    def _calculate_emotion_reason_balance(
        self, 
        contextual_emotion: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정-이성 균형 계산"""
        try:
            interpretation = contextual_emotion.get('interpretation', {})
            context_fit = contextual_emotion.get('context_fit', 0.5)
            
            # 감정 지배도 계산
            emotion_dominance = 1 - context_fit
            
            # 이성 지배도 계산
            reason_dominance = context_fit
            
            # 균형 타입 결정
            balance_type = self._determine_balance_type(emotion_dominance, reason_dominance)
            
            # 균형 권장사항
            recommendation = self._get_balance_recommendation(balance_type)
            
            return {
                "emotion_dominance": emotion_dominance,
                "reason_dominance": reason_dominance,
                "balance_type": balance_type,
                "recommendation": recommendation,
                "is_balanced": abs(emotion_dominance - reason_dominance) < 0.2
            }
            
        except Exception as e:
            logger.error(f"감정-이성 균형 계산 실패: {e}")
            return {}
    
    def _determine_balance_type(self, emotion_dominance: float, reason_dominance: float) -> str:
        """균형 타입 결정"""
        if abs(emotion_dominance - reason_dominance) < 0.1:
            return "balanced"
        elif emotion_dominance > reason_dominance + 0.2:
            return "emotion_dominant"
        elif reason_dominance > emotion_dominance + 0.2:
            return "reason_dominant"
        else:
            return "slightly_imbalanced"
    
    def _get_balance_recommendation(self, balance_type: str) -> str:
        """균형 권장사항"""
        recommendations = {
            "balanced": "현재 균형이 잘 맞춰져 있습니다",
            "emotion_dominant": "이성적 판단을 더 고려해보세요",
            "reason_dominant": "감정적 측면도 고려해보세요",
            "slightly_imbalanced": "약간의 조정이 필요합니다"
        }
        return recommendations.get(balance_type, "상황에 맞게 조정하세요")
    
    def _generate_empathetic_response(
        self, 
        contextual_emotion: Dict[str, Any], 
        balance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """공감적 반응 생성"""
        try:
            interpretation = contextual_emotion.get('interpretation', {})
            balance_type = balance.get('balance_type', 'balanced')
            
            # 공감 수준 결정
            empathy_level = self._calculate_empathy_level(interpretation, balance_type)
            
            # 공감적 반응 생성
            empathetic_response = self._create_empathetic_response(
                interpretation, empathy_level, balance_type
            )
            
            # 공감 효과 예측
            predicted_effect = self._predict_empathy_effect(empathetic_response, interpretation)
            
            return {
                "empathy_level": empathy_level,
                "response": empathetic_response,
                "predicted_effect": predicted_effect,
                "response_type": "supportive" if empathy_level > 0.6 else "neutral"
            }
            
        except Exception as e:
            logger.error(f"공감적 반응 생성 실패: {e}")
            return {}
    
    def _calculate_empathy_level(self, interpretation: Dict[str, Any], balance_type: str) -> float:
        """공감 수준 계산"""
        try:
            # 개인적 웰빙과 스트레스 수준 고려
            personal = interpretation.get('personal_context', {})
            wellbeing = personal.get('wellbeing_level', 0)
            distress = personal.get('distress_level', 0)
            
            # 기본 공감 수준
            base_empathy = max(0.3, min(0.9, (wellbeing - distress + 1) / 2))
            
            # 균형 타입에 따른 조정
            if balance_type == 'emotion_dominant':
                base_empathy *= 1.2  # 감정적일 때 공감 수준 증가
            elif balance_type == 'reason_dominant':
                base_empathy *= 0.9  # 이성적일 때 공감 수준 감소
            
            return min(1.0, base_empathy)
            
        except Exception as e:
            logger.error(f"공감 수준 계산 실패: {e}")
            return 0.5
    
    def _create_empathetic_response(
        self, 
        interpretation: Dict[str, Any], 
        empathy_level: float, 
        balance_type: str
    ) -> str:
        """공감적 반응 생성"""
        try:
            personal = interpretation.get('personal_context', {})
            social = interpretation.get('social_context', {})
            work = interpretation.get('work_context', {})
            
            responses = []
            
            # 개인적 웰빙에 대한 공감
            if personal.get('distress_level', 0) > 0.5:
                responses.append("지금 힘든 상황이신 것 같습니다. 충분히 이해합니다")
            
            # 사회적 불안에 대한 공감
            if social.get('anxiety_level', 0) > 0.5:
                responses.append("사회적 상황에서 불안하신 것 같습니다. 천천히 진행하세요")
            
            # 업무 스트레스에 대한 공감
            if work.get('stress_level', 0) > 0.6:
                responses.append("업무 스트레스가 많으신 것 같습니다. 휴식이 필요합니다")
            
            # 긍정적 상황에 대한 공감
            if personal.get('wellbeing_level', 0) > 0.7:
                responses.append("좋은 상태를 유지하고 계시네요. 계속 이어가세요")
            
            if not responses:
                responses.append("현재 상황을 잘 파악하고 있습니다")
            
            return " ".join(responses)
            
        except Exception as e:
            logger.error(f"공감적 반응 생성 실패: {e}")
            return "현재 상황을 이해하고 있습니다"
    
    def _predict_empathy_effect(self, response: str, interpretation: Dict[str, Any]) -> Dict[str, Any]:
        """공감 효과 예측"""
        try:
            personal = interpretation.get('personal_context', {})
            current_wellbeing = personal.get('wellbeing_level', 0.5)
            current_distress = personal.get('distress_level', 0.5)
            
            # 공감 효과 예측 (간단한 시뮬레이션)
            predicted_wellbeing = min(1.0, current_wellbeing + 0.1)
            predicted_distress = max(0.0, current_distress - 0.1)
            
            return {
                "predicted_wellbeing_improvement": predicted_wellbeing - current_wellbeing,
                "predicted_distress_reduction": current_distress - predicted_distress,
                "overall_positive_effect": predicted_wellbeing > current_wellbeing
            }
            
        except Exception as e:
            logger.error(f"공감 효과 예측 실패: {e}")
            return {}
    
    def _calculate_analysis_confidence(self, complex_analysis: Dict[str, Any]) -> float:
        """분석 신뢰도 계산"""
        try:
            emotion_vector = complex_analysis.get('emotion_vector', {})
            conflicts = complex_analysis.get('conflicts', [])
            stability = complex_analysis.get('stability', 0.5)
            
            # 기본 신뢰도
            base_confidence = 0.7
            
            # 감정 강도에 따른 조정
            max_intensity = max(emotion_vector.values()) if emotion_vector else 0
            if max_intensity > 0.8:
                base_confidence += 0.1
            elif max_intensity < 0.3:
                base_confidence -= 0.1
            
            # 충돌에 따른 조정
            if conflicts:
                base_confidence -= len(conflicts) * 0.05
            
            # 안정성에 따른 조정
            base_confidence += (stability - 0.5) * 0.2
            
            return max(0.3, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"분석 신뢰도 계산 실패: {e}")
            return 0.5
    
    def get_emotional_intelligence_stats(self) -> Dict[str, Any]:
        """감정 지능 통계 조회"""
        try:
            # 최근 24시간 데이터 분석
            cutoff_time = datetime.now() - timedelta(hours=24)
            
            # 복합 패턴 분석
            complex_patterns = self._analyze_complex_patterns(cutoff_time)
            
            # 감정 지능 점수 계산
            ei_score = self._calculate_emotional_intelligence_score(complex_patterns)
            
            return {
                "emotional_intelligence_score": ei_score,
                "complex_patterns": complex_patterns,
                "analysis_period": "24_hours",
                "confidence_level": 0.85
            }
            
        except Exception as e:
            logger.error(f"감정 지능 통계 조회 실패: {e}")
            return {"error": str(e)}
    
    def _analyze_complex_patterns(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """복합 패턴 분석"""
        try:
            # 최근 메모리 엔트리 조회 (임시로 빈 리스트 반환)
            recent_memories = []
            
            patterns = []
            
            for memory in recent_memories:
                if memory.emotion_data:
                    # 감정 패턴 분석
                    emotion_pattern = {
                        "timestamp": memory.timestamp.isoformat(),
                        "primary_emotion": memory.emotion_data.get('primary_emotion'),
                        "intensity": memory.emotion_data.get('intensity', 0),
                        "complexity": len(memory.emotion_data.get('secondary_emotions', [])),
                        "context": memory.context
                    }
                    patterns.append(emotion_pattern)
            
            return patterns
            
        except Exception as e:
            logger.error(f"복합 패턴 분석 실패: {e}")
            return []
    
    def _calculate_emotional_intelligence_score(self, patterns: List[Dict[str, Any]]) -> float:
        """감정 지능 점수 계산"""
        try:
            if not patterns:
                return 0.5
            
            # 다양한 감정 처리 능력
            emotion_diversity = len(set(p.get('primary_emotion') for p in patterns))
            diversity_score = min(1.0, emotion_diversity / 8)  # 8개 기본 감정
            
            # 감정 강도 조절 능력
            intensities = [p.get('intensity', 0) for p in patterns]
            avg_intensity = sum(intensities) / len(intensities) if intensities else 0.5
            intensity_score = 1.0 - abs(avg_intensity - 0.5)  # 중간 강도가 이상적
            
            # 복합 감정 처리 능력
            complexities = [p.get('complexity', 0) for p in patterns]
            avg_complexity = sum(complexities) / len(complexities) if complexities else 0
            complexity_score = min(1.0, avg_complexity / 3)  # 복합성이 높을수록 좋음
            
            # 종합 점수 계산
            total_score = (diversity_score * 0.4 + 
                          intensity_score * 0.3 + 
                          complexity_score * 0.3)
            
            return min(1.0, total_score)
            
        except Exception as e:
            logger.error(f"감정 지능 점수 계산 실패: {e}")
            return 0.5 