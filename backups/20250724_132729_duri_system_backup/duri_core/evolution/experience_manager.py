#!/usr/bin/env python3
"""
Experience Manager - 경험 관리 시스템

행동 실행 결과를 바탕으로 경험을 학습하고, 미래 의사결정에 활용할 지식을 관리합니다.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from duri_common.logger import get_logger
from .action_executor import ExecutionResult, ExecutionContext
from .result_recorder import RecordedResult

logger = get_logger("duri_evolution.experience_manager")


class ExperienceType(Enum):
    """경험 타입"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    LEARNING = "learning"


@dataclass
class ExperiencePattern:
    """경험 패턴"""
    pattern_id: str
    emotion: str
    action: str
    context_pattern: Dict[str, Any]
    success_rate: float
    avg_score: float
    confidence_level: float
    usage_count: int
    last_used: str
    created_at: str
    metadata: Dict[str, Any]


@dataclass
class LearningInsight:
    """학습 인사이트"""
    insight_id: str
    emotion: str
    action: str
    insight_type: str
    description: str
    confidence: float
    evidence_count: int
    created_at: str
    last_updated: str
    metadata: Dict[str, Any]


class ExperienceManager:
    """경험 관리자"""
    
    def __init__(self, data_dir: str = "evolution_data", stats_file: str = "experience_stats.json"):
        """
        ExperienceManager 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
            stats_file (str): 경험 통계 파일
        """
        self.data_dir = data_dir
        self.patterns_dir = os.path.join(data_dir, "patterns")
        self.insights_dir = os.path.join(data_dir, "insights")
        self.knowledge_dir = os.path.join(data_dir, "knowledge")
        
        # 디렉토리 생성
        os.makedirs(self.patterns_dir, exist_ok=True)
        os.makedirs(self.insights_dir, exist_ok=True)
        os.makedirs(self.knowledge_dir, exist_ok=True)
        
        logger.info(f"ExperienceManager 초기화 완료: {data_dir}")
        
        self.stats_file = stats_file
        self.stats = self._load_stats()
    
    def process_experience(self, recorded_result: RecordedResult) -> List[LearningInsight]:
        """
        경험 처리 및 학습
        
        Args:
            recorded_result (RecordedResult): 기록된 결과
        
        Returns:
            List[LearningInsight]: 생성된 학습 인사이트 목록
        """
        insights = []
        
        try:
            # 패턴 분석
            pattern = self._analyze_pattern(recorded_result)
            if pattern:
                self._save_pattern(pattern)
            
            # 인사이트 생성
            new_insights = self._generate_insights(recorded_result, pattern)
            insights.extend(new_insights)
            
            # 지식 베이스 업데이트
            self._update_knowledge_base(recorded_result, new_insights)
            
            logger.info(f"경험 처리 완료: {len(insights)}개 인사이트 생성")
            
        except Exception as e:
            logger.error(f"경험 처리 실패: {e}")
        
        return insights
    
    def get_recommended_action(
        self,
        emotion: str,
        context: Dict[str, Any],
        confidence_threshold: float = 0.7
    ) -> Optional[Tuple[str, float]]:
        """
        추천 액션 조회
        
        Args:
            emotion (str): 현재 감정
            context (Dict[str, Any]): 현재 컨텍스트
            confidence_threshold (float): 신뢰도 임계값
        
        Returns:
            Optional[Tuple[str, float]]: (추천 액션, 신뢰도)
        """
        try:
            # 패턴 기반 추천
            pattern_recommendation = self._get_pattern_recommendation(emotion, context)
            
            # 인사이트 기반 추천
            insight_recommendation = self._get_insight_recommendation(emotion, context)
            
            # 추천 통합
            final_recommendation = self._combine_recommendations(
                pattern_recommendation, 
                insight_recommendation
            )
            
            if final_recommendation and final_recommendation[1] >= confidence_threshold:
                return final_recommendation
            
        except Exception as e:
            logger.error(f"추천 액션 조회 실패: {e}")
        
        return None
    
    def get_experience_patterns(
        self,
        emotion: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: int = 50
    ) -> List[ExperiencePattern]:
        """
        경험 패턴 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            min_confidence (float): 최소 신뢰도
            limit (int): 조회할 최대 개수
        
        Returns:
            List[ExperiencePattern]: 경험 패턴 목록
        """
        patterns = []
        
        try:
            # 패턴 파일들 읽기
            for filename in os.listdir(self.patterns_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.patterns_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pattern = ExperiencePattern(**data)
                    
                    # 필터링
                    if emotion and pattern.emotion != emotion:
                        continue
                    if pattern.confidence_level < min_confidence:
                        continue
                    
                    patterns.append(pattern)
            
            # 신뢰도순 정렬
            patterns.sort(key=lambda x: x.confidence_level, reverse=True)
            return patterns[:limit]
            
        except Exception as e:
            logger.error(f"경험 패턴 조회 실패: {e}")
            return []
    
    def get_learning_insights(
        self,
        emotion: Optional[str] = None,
        insight_type: Optional[str] = None,
        limit: int = 50
    ) -> List[LearningInsight]:
        """
        학습 인사이트 조회
        
        Args:
            emotion (str, optional): 특정 감정 필터링
            insight_type (str, optional): 특정 인사이트 타입 필터링
            limit (int): 조회할 최대 개수
        
        Returns:
            List[LearningInsight]: 학습 인사이트 목록
        """
        insights = []
        
        try:
            # 인사이트 파일들 읽기
            for filename in os.listdir(self.insights_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.insights_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    insight = LearningInsight(**data)
                    
                    # 필터링
                    if emotion and insight.emotion != emotion:
                        continue
                    if insight_type and insight.insight_type != insight_type:
                        continue
                    
                    insights.append(insight)
            
            # 생성일순 정렬 (최신순)
            insights.sort(key=lambda x: x.created_at, reverse=True)
            return insights[:limit]
            
        except Exception as e:
            logger.error(f"학습 인사이트 조회 실패: {e}")
            return []
    
    def _analyze_pattern(self, recorded_result: RecordedResult) -> Optional[ExperiencePattern]:
        """패턴 분석"""
        try:
            # 감정-액션 조합 키 생성
            emotion_action_key = f"{recorded_result.emotion}_{recorded_result.action}"
            
            # 기존 패턴 파일 확인
            pattern_file = os.path.join(self.patterns_dir, f"pattern_{emotion_action_key}.json")
            
            if os.path.exists(pattern_file):
                # 기존 패턴 업데이트
                with open(pattern_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    pattern = ExperiencePattern(**data)
                
                # 패턴 통계 업데이트
                pattern.usage_count += 1
                pattern.last_used = datetime.now().isoformat()
                
                # 성공률 업데이트
                total_attempts = pattern.usage_count
                if recorded_result.success:
                    pattern.successful_attempts = pattern.successful_attempts + 1
                
                pattern.success_rate = pattern.successful_attempts / total_attempts
                
                # 평균 점수 업데이트
                pattern.avg_score = (
                    (pattern.avg_score * (total_attempts - 1) + recorded_result.result_score) 
                    / total_attempts
                )
                
                # 신뢰도 계산 (더 많은 데이터일수록 높은 신뢰도)
                pattern.confidence_level = min(1.0, total_attempts / 10.0)
                
            else:
                # 새로운 패턴 생성
                pattern_id = f"{emotion_action_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                pattern = ExperiencePattern(
                    pattern_id=pattern_id,
                    emotion=recorded_result.emotion,
                    action=recorded_result.action,
                    context_pattern={
                        'intensity_range': [recorded_result.context.get('intensity', 0.5)],
                        'confidence_range': [recorded_result.context.get('confidence', 0.5)],
                        'environment': recorded_result.context.get('environment'),
                        'session_count': 1
                    },
                    success_rate=1.0 if recorded_result.success else 0.0,
                    avg_score=recorded_result.result_score,
                    confidence_level=0.1,  # 초기 신뢰도
                    usage_count=1,
                    last_used=datetime.now().isoformat(),
                    created_at=datetime.now().isoformat(),
                    metadata={
                        'first_result': {
                            'success': recorded_result.success,
                            'score': recorded_result.result_score,
                            'timestamp': recorded_result.timestamp
                        }
                    }
                )
            
            return pattern
            
        except Exception as e:
            logger.error(f"패턴 분석 실패: {e}")
            return None
    
    def _generate_insights(
        self, 
        recorded_result: RecordedResult, 
        pattern: Optional[ExperiencePattern]
    ) -> List[LearningInsight]:
        """인사이트 생성"""
        insights = []
        
        try:
            # 1. 성공/실패 패턴 인사이트
            success_insight = self._generate_success_insight(recorded_result, pattern)
            if success_insight:
                insights.append(success_insight)
            
            # 2. 감정-액션 조합 인사이트
            combination_insight = self._generate_combination_insight(recorded_result, pattern)
            if combination_insight:
                insights.append(combination_insight)
            
            # 3. 성능 개선 인사이트
            performance_insight = self._generate_performance_insight(recorded_result, pattern)
            if performance_insight:
                insights.append(performance_insight)
            
            # 4. 컨텍스트 기반 인사이트
            context_insight = self._generate_context_insight(recorded_result, pattern)
            if context_insight:
                insights.append(context_insight)
            
            # 인사이트 저장
            for insight in insights:
                self._save_insight(insight)
            
        except Exception as e:
            logger.error(f"인사이트 생성 실패: {e}")
        
        return insights
    
    def _generate_success_insight(
        self, 
        recorded_result: RecordedResult, 
        pattern: Optional[ExperiencePattern]
    ) -> Optional[LearningInsight]:
        """성공/실패 패턴 인사이트 생성"""
        if not pattern or pattern.usage_count < 3:
            return None
        
        insight_id = f"success_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if pattern.success_rate > 0.8:
            description = f"{recorded_result.emotion} 감정에서 {recorded_result.action} 액션이 매우 효과적입니다. (성공률: {pattern.success_rate:.1%})"
            insight_type = "high_success_pattern"
        elif pattern.success_rate < 0.3:
            description = f"{recorded_result.emotion} 감정에서 {recorded_result.action} 액션이 효과적이지 않습니다. (성공률: {pattern.success_rate:.1%})"
            insight_type = "low_success_pattern"
        else:
            return None
        
        return LearningInsight(
            insight_id=insight_id,
            emotion=recorded_result.emotion,
            action=recorded_result.action,
            insight_type=insight_type,
            description=description,
            confidence=pattern.confidence_level,
            evidence_count=pattern.usage_count,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            metadata={
                'success_rate': pattern.success_rate,
                'usage_count': pattern.usage_count,
                'pattern_id': pattern.pattern_id
            }
        )
    
    def _generate_combination_insight(
        self, 
        recorded_result: RecordedResult, 
        pattern: Optional[ExperiencePattern]
    ) -> Optional[LearningInsight]:
        """감정-액션 조합 인사이트 생성"""
        if not pattern or pattern.usage_count < 2:
            return None
        
        insight_id = f"combination_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 감정별 효과적인 액션 패턴 분석
        emotion_action_effectiveness = {
            'happy': ['console', 'act'],
            'sad': ['console', 'reflect'],
            'angry': ['wait', 'reflect'],
            'frustration': ['wait', 'observe'],
            'grateful': ['act', 'console'],
            'inspired': ['act', 'observe']
        }
        
        effective_actions = emotion_action_effectiveness.get(recorded_result.emotion.lower(), [])
        
        if recorded_result.action in effective_actions:
            description = f"{recorded_result.emotion} 감정에 {recorded_result.action} 액션이 적합합니다."
            insight_type = "effective_combination"
        else:
            description = f"{recorded_result.emotion} 감정에 {recorded_result.action} 액션을 시도해보았습니다."
            insight_type = "exploration_combination"
        
        return LearningInsight(
            insight_id=insight_id,
            emotion=recorded_result.emotion,
            action=recorded_result.action,
            insight_type=insight_type,
            description=description,
            confidence=pattern.confidence_level * 0.8,
            evidence_count=pattern.usage_count,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            metadata={
                'effective_actions': effective_actions,
                'pattern_id': pattern.pattern_id
            }
        )
    
    def _generate_performance_insight(
        self, 
        recorded_result: RecordedResult, 
        pattern: Optional[ExperiencePattern]
    ) -> Optional[LearningInsight]:
        """성능 개선 인사이트 생성"""
        if not pattern or pattern.usage_count < 5:
            return None
        
        insight_id = f"performance_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 성능 트렌드 분석
        recent_results = pattern.metadata.get('recent_results', [])
        if len(recent_results) >= 3:
            recent_scores = [r['score'] for r in recent_results[-3:]]
            avg_recent_score = sum(recent_scores) / len(recent_scores)
            
            if avg_recent_score > pattern.avg_score * 1.2:
                description = f"{recorded_result.emotion} 감정에서 {recorded_result.action} 액션의 성능이 개선되고 있습니다."
                insight_type = "performance_improvement"
            elif avg_recent_score < pattern.avg_score * 0.8:
                description = f"{recorded_result.emotion} 감정에서 {recorded_result.action} 액션의 성능이 저하되고 있습니다."
                insight_type = "performance_degradation"
            else:
                return None
            
            return LearningInsight(
                insight_id=insight_id,
                emotion=recorded_result.emotion,
                action=recorded_result.action,
                insight_type=insight_type,
                description=description,
                confidence=pattern.confidence_level * 0.7,
                evidence_count=pattern.usage_count,
                created_at=datetime.now().isoformat(),
                last_updated=datetime.now().isoformat(),
                metadata={
                    'recent_avg_score': avg_recent_score,
                    'overall_avg_score': pattern.avg_score,
                    'trend': 'improving' if insight_type == 'performance_improvement' else 'degrading'
                }
            )
        
        return None
    
    def _generate_context_insight(
        self, 
        recorded_result: RecordedResult, 
        pattern: Optional[ExperiencePattern]
    ) -> Optional[LearningInsight]:
        """컨텍스트 기반 인사이트 생성"""
        if not pattern:
            return None
        
        insight_id = f"context_{pattern.pattern_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 컨텍스트 분석
        intensity = recorded_result.context.get('intensity', 0.5)
        confidence = recorded_result.context.get('confidence', 0.5)
        environment = recorded_result.context.get('environment')
        
        # 강도별 효과 분석
        if intensity > 0.8:
            description = f"강한 {recorded_result.emotion} 감정에서 {recorded_result.action} 액션의 효과를 관찰했습니다."
            insight_type = "high_intensity_context"
        elif intensity < 0.3:
            description = f"약한 {recorded_result.emotion} 감정에서 {recorded_result.action} 액션의 효과를 관찰했습니다."
            insight_type = "low_intensity_context"
        else:
            description = f"보통 강도의 {recorded_result.emotion} 감정에서 {recorded_result.action} 액션의 효과를 관찰했습니다."
            insight_type = "medium_intensity_context"
        
        return LearningInsight(
            insight_id=insight_id,
            emotion=recorded_result.emotion,
            action=recorded_result.action,
            insight_type=insight_type,
            description=description,
            confidence=pattern.confidence_level * 0.6,
            evidence_count=pattern.usage_count,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat(),
            metadata={
                'intensity': intensity,
                'confidence': confidence,
                'environment': environment,
                'success': recorded_result.success
            }
        )
    
    def _save_insight(self, insight: LearningInsight):
        """인사이트 저장"""
        try:
            filename = f"insight_{insight.insight_id}.json"
            filepath = os.path.join(self.insights_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(insight), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"인사이트 저장 실패: {e}")
    
    def _update_knowledge_base(
        self, 
        recorded_result: RecordedResult, 
        insights: List[LearningInsight]
    ):
        """지식 베이스 업데이트"""
        try:
            knowledge_file = os.path.join(self.knowledge_dir, "knowledge_base.json")
            
            # 기존 지식 베이스 읽기
            if os.path.exists(knowledge_file):
                with open(knowledge_file, 'r', encoding='utf-8') as f:
                    knowledge_base = json.load(f)
            else:
                knowledge_base = {
                    'emotion_action_mappings': {},
                    'success_patterns': {},
                    'performance_trends': {},
                    'context_insights': {},
                    'last_updated': datetime.now().isoformat()
                }
            
            # 감정-액션 매핑 업데이트
            emotion = recorded_result.emotion
            action = recorded_result.action
            
            if emotion not in knowledge_base['emotion_action_mappings']:
                knowledge_base['emotion_action_mappings'][emotion] = {}
            
            if action not in knowledge_base['emotion_action_mappings'][emotion]:
                knowledge_base['emotion_action_mappings'][emotion][action] = {
                    'success_count': 0,
                    'total_count': 0,
                    'avg_score': 0.0,
                    'last_used': None
                }
            
            mapping = knowledge_base['emotion_action_mappings'][emotion][action]
            mapping['total_count'] += 1
            if recorded_result.success:
                mapping['success_count'] += 1
            
            # 평균 점수 업데이트
            mapping['avg_score'] = (
                (mapping['avg_score'] * (mapping['total_count'] - 1) + recorded_result.result_score)
                / mapping['total_count']
            )
            mapping['last_used'] = recorded_result.timestamp
            
            # 인사이트 기반 지식 업데이트
            for insight in insights:
                if insight.insight_type == 'high_success_pattern':
                    knowledge_base['success_patterns'][f"{emotion}_{action}"] = {
                        'success_rate': insight.metadata.get('success_rate', 0.0),
                        'confidence': insight.confidence,
                        'evidence_count': insight.evidence_count
                    }
            
            knowledge_base['last_updated'] = datetime.now().isoformat()
            
            # 지식 베이스 저장
            with open(knowledge_file, 'w', encoding='utf-8') as f:
                json.dump(knowledge_base, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"지식 베이스 업데이트 실패: {e}")
    
    def _get_pattern_recommendation(
        self, 
        emotion: str, 
        context: Dict[str, Any]
    ) -> Optional[Tuple[str, float]]:
        """패턴 기반 추천"""
        try:
            # 해당 감정의 모든 패턴 조회
            patterns = self.get_experience_patterns(emotion=emotion, min_confidence=0.3)
            
            if not patterns:
                return None
            
            # 컨텍스트 유사도 기반 추천
            best_pattern = None
            best_score = 0.0
            
            for pattern in patterns:
                # 성공률과 신뢰도 기반 점수
                base_score = pattern.success_rate * pattern.confidence_level
                
                # 컨텍스트 유사도 보너스
                context_similarity = self._calculate_context_similarity(context, pattern.context_pattern)
                context_bonus = context_similarity * 0.3
                
                total_score = base_score + context_bonus
                
                if total_score > best_score:
                    best_score = total_score
                    best_pattern = pattern
            
            if best_pattern and best_score > 0.5:
                return best_pattern.action, best_score
            
        except Exception as e:
            logger.error(f"패턴 기반 추천 실패: {e}")
        
        return None
    
    def _get_insight_recommendation(
        self, 
        emotion: str, 
        context: Dict[str, Any]
    ) -> Optional[Tuple[str, float]]:
        """인사이트 기반 추천"""
        try:
            # 해당 감정의 인사이트 조회
            insights = self.get_learning_insights(emotion=emotion, insight_type='high_success_pattern')
            
            if not insights:
                return None
            
            # 가장 신뢰도 높은 인사이트 기반 추천
            best_insight = max(insights, key=lambda x: x.confidence)
            
            if best_insight.confidence > 0.6:
                return best_insight.action, best_insight.confidence
            
        except Exception as e:
            logger.error(f"인사이트 기반 추천 실패: {e}")
        
        return None
    
    def _combine_recommendations(
        self,
        pattern_rec: Optional[Tuple[str, float]],
        insight_rec: Optional[Tuple[str, float]]
    ) -> Optional[Tuple[str, float]]:
        """추천 통합"""
        if not pattern_rec and not insight_rec:
            return None
        
        if not pattern_rec:
            return insight_rec
        
        if not insight_rec:
            return pattern_rec
        
        # 두 추천이 같은 액션인 경우
        if pattern_rec[0] == insight_rec[0]:
            # 신뢰도 평균
            combined_confidence = (pattern_rec[1] + insight_rec[1]) / 2
            return pattern_rec[0], combined_confidence
        
        # 다른 액션인 경우 더 높은 신뢰도 선택
        if pattern_rec[1] > insight_rec[1]:
            return pattern_rec
        else:
            return insight_rec
    
    def _calculate_context_similarity(
        self, 
        current_context: Dict[str, Any], 
        pattern_context: Dict[str, Any]
    ) -> float:
        """컨텍스트 유사도 계산"""
        try:
            similarity_score = 0.0
            total_factors = 0
            
            # 강도 유사도
            if 'intensity_range' in pattern_context and 'intensity' in current_context:
                current_intensity = current_context['intensity']
                pattern_intensities = pattern_context['intensity_range']
                
                # 가장 가까운 강도 찾기
                min_diff = min(abs(current_intensity - pi) for pi in pattern_intensities)
                intensity_similarity = max(0, 1 - min_diff)
                similarity_score += intensity_similarity
                total_factors += 1
            
            # 신뢰도 유사도
            if 'confidence_range' in pattern_context and 'confidence' in current_context:
                current_confidence = current_context['confidence']
                pattern_confidences = pattern_context['confidence_range']
                
                min_diff = min(abs(current_confidence - pc) for pc in pattern_confidences)
                confidence_similarity = max(0, 1 - min_diff)
                similarity_score += confidence_similarity
                total_factors += 1
            
            # 환경 유사도
            if 'environment' in pattern_context and 'environment' in current_context:
                if pattern_context['environment'] == current_context['environment']:
                    similarity_score += 1.0
                total_factors += 1
            
            return similarity_score / total_factors if total_factors > 0 else 0.0
            
        except Exception as e:
            logger.error(f"컨텍스트 유사도 계산 실패: {e}")
            return 0.0
    
    def _save_pattern(self, pattern: ExperiencePattern):
        """패턴 저장"""
        try:
            filename = f"pattern_{pattern.pattern_id}.json"
            filepath = os.path.join(self.patterns_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(pattern), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"패턴 저장 실패: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """경험 관리 통계 조회"""
        try:
            pattern_count = len([f for f in os.listdir(self.patterns_dir) if f.endswith('.json')])
            insight_count = len([f for f in os.listdir(self.insights_dir) if f.endswith('.json')])
            
            return {
                'total_patterns': pattern_count,
                'total_insights': insight_count
            }
            
        except Exception as e:
            logger.error(f"통계 조회 실패: {e}")
            return {}

    def _load_stats(self):
        """통계 파일 로드"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_stats(self):
        """통계 파일 저장"""
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)

    def update_stats(self, emotion: str, action: str, success: bool):
        """
        감정과 행동, 성공 여부를 받아서 각 감정-행동 조합의 success/fail 횟수를 누적 저장
        Args:
            emotion (str): 감정
            action (str): 행동
            success (bool): 성공 여부
        """
        # 감정-행동 조합 키 생성
        key = f"{emotion}_{action}"
        
        # 기존 통계가 없으면 초기화
        if key not in self.stats:
            self.stats[key] = {
                'emotion': emotion,
                'action': action,
                'success_count': 0,
                'fail_count': 0,
                'total_count': 0,
                'success_rate': 0.0,
                'last_updated': datetime.now().isoformat()
            }
        
        # 통계 업데이트
        if success:
            self.stats[key]['success_count'] += 1
        else:
            self.stats[key]['fail_count'] += 1
        
        self.stats[key]['total_count'] += 1
        self.stats[key]['success_rate'] = self.stats[key]['success_count'] / self.stats[key]['total_count']
        self.stats[key]['last_updated'] = datetime.now().isoformat()
        
        # 파일에 저장
        self._save_stats()

    def get_stats(self, emotion: str = None, action: str = None):
        """
        통계 조회
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 행동 필터링
        Returns:
            dict: 필터링된 통계
        """
        if emotion and action:
            key = f"{emotion}_{action}"
            return self.stats.get(key, {})
        elif emotion:
            return {k: v for k, v in self.stats.items() if v['emotion'] == emotion}
        elif action:
            return {k: v for k, v in self.stats.items() if v['action'] == action}
        else:
            return self.stats 