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

from ..models.memory import MemoryEntry
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
            emotion_type = self._determine_complex_emotion_type(emotion_vector)
            
            return {
                "emotion_vector": emotion_vector,
                "conflicts": conflicts,
                "stability": stability,
                "emotion_type": emotion_type,
                "intensity": intensity
            }
            
        except Exception as e:
            logger.error(f"감정 조합 분석 실패: {e}")
            return {}
    
    def _detect_emotion_conflicts(self, emotion_vector: Dict[str, float]) -> List[Dict[str, Any]]:
        """감정 충돌 감지"""
        conflicts = []
        
        # 상반되는 감정 쌍들
        conflicting_pairs = [
            ("joy", "sadness"), ("trust", "fear"), 
            ("anger", "joy"), ("surprise", "anticipation")
        ]
        
        for emotion1, emotion2 in conflicting_pairs:
            if emotion_vector.get(emotion1, 0) > 0.3 and emotion_vector.get(emotion2, 0) > 0.3:
                conflict_intensity = min(
                    emotion_vector[emotion1], 
                    emotion_vector[emotion2]
                )
                conflicts.append({
                    "emotion1": emotion1,
                    "emotion2": emotion2,
                    "intensity": conflict_intensity,
                    "type": "opposing_emotions"
                })
        
        return conflicts
    
    def _calculate_emotion_stability(self, emotion_vector: Dict[str, float]) -> float:
        """감정 안정성 계산"""
        try:
            # 활성 감정 수
            active_emotions = sum(1 for v in emotion_vector.values() if v > 0.3)
            
            # 감정 강도 분산
            intensities = [v for v in emotion_vector.values() if v > 0]
            if not intensities:
                return 1.0
            
            variance = np.var(intensities) if len(intensities) > 1 else 0
            
            # 안정성 점수 (높을수록 안정적)
            stability = 1.0 - (variance * 0.5) - (active_emotions * 0.1)
            return max(0.0, min(1.0, stability))
            
        except Exception as e:
            logger.error(f"감정 안정성 계산 실패: {e}")
            return 0.5
    
    def _determine_complex_emotion_type(self, emotion_vector: Dict[str, float]) -> str:
        """복합 감정 타입 결정"""
        try:
            # 가장 강한 감정들
            strong_emotions = [
                (emotion, intensity) for emotion, intensity in emotion_vector.items()
                if intensity > 0.5
            ]
            
            if not strong_emotions:
                return "neutral"
            
            # 감정 조합 패턴 분석
            if len(strong_emotions) == 1:
                return f"pure_{strong_emotions[0][0]}"
            elif len(strong_emotions) == 2:
                emotion1, intensity1 = strong_emotions[0]
                emotion2, intensity2 = strong_emotions[1]
                
                # 상반되는 감정인지 확인
                if self._are_opposing_emotions(emotion1, emotion2):
                    return "conflicted"
                else:
                    return f"mixed_{emotion1}_{emotion2}"
            else:
                return "complex_mixture"
                
        except Exception as e:
            logger.error(f"복합 감정 타입 결정 실패: {e}")
            return "unknown"
    
    def _are_opposing_emotions(self, emotion1: str, emotion2: str) -> bool:
        """상반되는 감정인지 확인"""
        opposing_pairs = [
            ("joy", "sadness"), ("trust", "fear"), 
            ("anger", "joy"), ("surprise", "anticipation")
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
            
            # 맥락 요소들
            social_context = context.get('social', False)
            urgent_context = context.get('urgent', False)
            personal_context = context.get('personal', False)
            
            # 맥락별 감정 조정
            adjusted_emotions = emotion_vector.copy()
            
            if social_context:
                # 사회적 맥락에서는 감정 표현을 조절
                for emotion in ['anger', 'fear', 'disgust']:
                    if emotion in adjusted_emotions:
                        adjusted_emotions[emotion] *= 0.7
                
                # 긍정적 감정 강화
                for emotion in ['joy', 'trust']:
                    if emotion in adjusted_emotions:
                        adjusted_emotions[emotion] *= 1.2
            
            if urgent_context:
                # 긴급 상황에서는 감정보다 이성 우선
                for emotion in adjusted_emotions:
                    adjusted_emotions[emotion] *= 0.8
            
            if personal_context:
                # 개인적 맥락에서는 감정 표현 자유로움
                pass  # 조정 없음
            
            return {
                "original_emotions": emotion_vector,
                "adjusted_emotions": adjusted_emotions,
                "context_factors": {
                    "social": social_context,
                    "urgent": urgent_context,
                    "personal": personal_context
                }
            }
            
        except Exception as e:
            logger.error(f"맥락 기반 감정 해석 실패: {e}")
            return {}
    
    def _calculate_emotion_reason_balance(
        self, 
        contextual_emotion: Dict[str, Any], 
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """감정-이성 균형 계산"""
        try:
            adjusted_emotions = contextual_emotion.get('adjusted_emotions', {})
            
            # 감정 강도 계산
            emotion_intensity = sum(adjusted_emotions.values()) / len(adjusted_emotions)
            
            # 이성 지수 계산 (맥락 기반)
            reason_score = 0.5  # 기본값
            
            # 긴급 상황에서는 이성 우선
            if context.get('urgent', False):
                reason_score = 0.8
            
            # 복잡한 상황에서는 이성 우선
            if context.get('complex', False):
                reason_score = 0.7
            
            # 개인적 상황에서는 감정 우선
            if context.get('personal', False):
                reason_score = 0.3
            
            # 균형 점수 계산
            balance_score = (emotion_intensity + reason_score) / 2
            balance_type = "emotion_dominant" if emotion_intensity > reason_score else "reason_dominant"
            
            if abs(emotion_intensity - reason_score) < 0.2:
                balance_type = "balanced"
            
            return {
                "emotion_intensity": emotion_intensity,
                "reason_score": reason_score,
                "balance_score": balance_score,
                "balance_type": balance_type,
                "recommendation": self._get_balance_recommendation(balance_type)
            }
            
        except Exception as e:
            logger.error(f"감정-이성 균형 계산 실패: {e}")
            return {}
    
    def _get_balance_recommendation(self, balance_type: str) -> str:
        """균형 타입에 따른 권장사항"""
        recommendations = {
            "emotion_dominant": "감정을 조절하고 이성적 판단을 고려하세요",
            "reason_dominant": "감정을 인정하고 표현하는 것도 중요합니다",
            "balanced": "감정과 이성의 균형이 잘 맞습니다"
        }
        return recommendations.get(balance_type, "상황에 맞는 판단이 필요합니다")
    
    def _generate_empathetic_response(
        self, 
        contextual_emotion: Dict[str, Any], 
        balance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """공감적 반응 생성"""
        try:
            adjusted_emotions = contextual_emotion.get('adjusted_emotions', {})
            balance_type = balance.get('balance_type', 'balanced')
            
            # 주요 감정 식별
            primary_emotion = max(adjusted_emotions.items(), key=lambda x: x[1])
            
            # 공감적 반응 생성
            empathetic_responses = {
                "joy": "기쁜 마음을 함께 나누고 싶어요",
                "sadness": "슬픈 마음을 이해하고 위로하고 싶어요",
                "anger": "화가 난 이유를 들어보고 싶어요",
                "fear": "두려운 마음을 안전하게 표현할 수 있어요",
                "trust": "신뢰를 소중히 여기고 보답하고 싶어요",
                "surprise": "놀라운 상황에 대해 함께 이야기해보고 싶어요",
                "anticipation": "기대하는 마음을 함께 나누고 싶어요",
                "disgust": "불편한 감정을 이해하고 해결책을 찾아보고 싶어요"
            }
            
            response = empathetic_responses.get(primary_emotion[0], "당신의 감정을 이해하고 싶어요")
            
            # 균형 타입에 따른 조정
            if balance_type == "emotion_dominant":
                response += " 감정을 조절하는 것도 도움이 될 수 있어요"
            elif balance_type == "reason_dominant":
                response += " 감정을 인정하는 것도 중요해요"
            
            return {
                "empathetic_response": response,
                "primary_emotion": primary_emotion[0],
                "response_type": "empathetic",
                "balance_consideration": balance_type
            }
            
        except Exception as e:
            logger.error(f"공감적 반응 생성 실패: {e}")
            return {"empathetic_response": "당신의 감정을 이해하고 싶어요"}
    
    def _calculate_analysis_confidence(self, complex_analysis: Dict[str, Any]) -> float:
        """분석 신뢰도 계산"""
        try:
            emotion_vector = complex_analysis.get('emotion_vector', {})
            stability = complex_analysis.get('stability', 0.5)
            conflicts = complex_analysis.get('conflicts', [])
            
            # 기본 신뢰도
            confidence = 0.7
            
            # 안정성에 따른 조정
            confidence += stability * 0.2
            
            # 충돌에 따른 조정
            conflict_penalty = len(conflicts) * 0.1
            confidence -= conflict_penalty
            
            # 감정 강도에 따른 조정
            max_intensity = max(emotion_vector.values()) if emotion_vector else 0
            confidence += max_intensity * 0.1
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            logger.error(f"분석 신뢰도 계산 실패: {e}")
            return 0.5
    
    # @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_emotional_intelligence_stats(self) -> Dict[str, Any]:
        """감정 지능 통계 조회"""
        try:
            # 최근 24시간 감정 분석 통계
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # 감정별 메모리 수
            emotion_counts = {}
            for emotion in self.emotion_dimensions:
                count = self.db.query(MemoryEntry).filter(
                    and_(
                        MemoryEntry.tags.contains([emotion]),
                        MemoryEntry.created_at >= cutoff_time
                    )
                ).count()
                emotion_counts[emotion] = count
            
            # 복합 감정 패턴 분석
            complex_patterns = self._analyze_complex_patterns(cutoff_time)
            
            return {
                "emotion_counts_24h": emotion_counts,
                "complex_patterns": complex_patterns,
                "total_emotions_24h": sum(emotion_counts.values()),
                "most_common_emotion": max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "neutral"
            }
            
        except Exception as e:
            logger.error(f"감정 지능 통계 조회 실패: {e}")
            return {}
    
    def _analyze_complex_patterns(self, cutoff_time: datetime) -> List[Dict[str, Any]]:
        """복합 감정 패턴 분석"""
        try:
            # 최근 메모리에서 감정 태그 분석
            recent_memories = self.db.query(MemoryEntry).filter(
                MemoryEntry.created_at >= cutoff_time
            ).all()
            
            patterns = []
            emotion_combinations = defaultdict(int)
            
            for memory in recent_memories:
                if memory.tags:
                    emotion_tags = [tag for tag in memory.tags if tag in self.emotion_dimensions]
                    if len(emotion_tags) >= 2:
                        combination = tuple(sorted(emotion_tags))
                        emotion_combinations[combination] += 1
            
            # 상위 패턴 추출
            top_patterns = sorted(emotion_combinations.items(), key=lambda x: x[1], reverse=True)[:5]
            
            for combination, count in top_patterns:
                patterns.append({
                    "emotions": list(combination),
                    "frequency": count,
                    "complexity": len(combination)
                })
            
            return patterns
            
        except Exception as e:
            logger.error(f"복합 패턴 분석 실패: {e}")
            return [] 