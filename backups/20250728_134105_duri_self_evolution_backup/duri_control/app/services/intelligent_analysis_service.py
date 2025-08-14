"""
DuRi Memory System - Intelligent Analysis Service
지능형 메모리 분석 시스템
"""

import logging
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from dataclasses import dataclass
from enum import Enum

from ..database.database import get_db_session
from ..decorators.memory_logger import log_important_event, log_system_event

logger = logging.getLogger(__name__)


class AnalysisType(Enum):
    """분석 타입"""
    PATTERN = "pattern"
    CORRELATION = "correlation"
    PREDICTION = "prediction"
    RECOMMENDATION = "recommendation"
    TREND = "trend"


@dataclass
class MemoryPattern:
    """메모리 패턴"""
    pattern_type: str
    frequency: int
    confidence: float
    examples: List[str]
    context: str
    importance_score: float


@dataclass
class MemoryCorrelation:
    """메모리 상관관계"""
    source_type: str
    target_type: str
    correlation_strength: float
    time_lag: Optional[int] = None
    context: str = ""


class IntelligentAnalysisService:
    """지능형 메모리 분석 서비스"""
    
    def __init__(self):
        self.pattern_cache = {}
        self.correlation_cache = {}
        self.analysis_history = []
    
    def analyze_memory_patterns(self, memory_type: str = None, 
                              time_window: int = 24, 
                              min_frequency: int = 3) -> Dict[str, Any]:
        """메모리 패턴 분석"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            # 시간 범위 설정
            start_time = datetime.now() - timedelta(hours=time_window)
            
            # 메모리 조회
            memories = memory_service.query_memories(
                memory_type=memory_type,
                limit=1000
            )
            
            # 시간 필터링
            recent_memories = [
                m for m in memories 
                if m.created_at.replace(tzinfo=None) >= start_time
            ]
            
            # 패턴 분석
            patterns = self._extract_patterns(recent_memories, min_frequency)
            
            # 패턴 중요도 계산
            for pattern in patterns:
                pattern.importance_score = self._calculate_pattern_importance(pattern)
            
            # 결과 정리
            result = {
                "analysis_type": "pattern",
                "time_window_hours": time_window,
                "total_memories_analyzed": len(recent_memories),
                "patterns_found": len(patterns),
                "patterns": [
                    {
                        "type": p.pattern_type,
                        "frequency": p.frequency,
                        "confidence": p.confidence,
                        "importance_score": p.importance_score,
                        "context": p.context,
                        "examples": p.examples[:5]  # 최대 5개 예시
                    }
                    for p in patterns
                ]
            }
            
            # 분석 결과 로깅
            log_system_event(
                context="지능형 분석: 패턴 분석",
                content=f"{len(patterns)}개 패턴 발견, {len(recent_memories)}개 메모리 분석",
                importance_score=60
            )
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"패턴 분석 실패: {e}")
            return {"error": str(e)}
    
    def _extract_patterns(self, memories: List, min_frequency: int) -> List[MemoryPattern]:
        """패턴 추출"""
        patterns = []
        
        # 1. 시간 패턴 분석
        time_patterns = self._analyze_time_patterns(memories)
        patterns.extend(time_patterns)
        
        # 2. 내용 패턴 분석
        content_patterns = self._analyze_content_patterns(memories)
        patterns.extend(content_patterns)
        
        # 3. 중요도 패턴 분석
        importance_patterns = self._analyze_importance_patterns(memories)
        patterns.extend(importance_patterns)
        
        # 4. 소스 패턴 분석
        source_patterns = self._analyze_source_patterns(memories)
        patterns.extend(source_patterns)
        
        # 최소 빈도 필터링
        patterns = [p for p in patterns if p.frequency >= min_frequency]
        
        return patterns
    
    def _analyze_time_patterns(self, memories: List) -> List[MemoryPattern]:
        """시간 패턴 분석"""
        patterns = []
        
        # 시간대별 분포
        hour_distribution = defaultdict(int)
        for memory in memories:
            hour = memory.created_at.hour
            hour_distribution[hour] += 1
        
        # 주요 시간대 패턴
        for hour, count in hour_distribution.items():
            if count >= 3:
                patterns.append(MemoryPattern(
                    pattern_type="time_distribution",
                    frequency=count,
                    confidence=min(count / len(memories), 1.0),
                    examples=[f"{hour}시대 활발한 활동"],
                    context=f"시간대별 패턴: {hour}시대",
                    importance_score=0.0
                ))
        
        return patterns
    
    def _analyze_content_patterns(self, memories: List) -> List[MemoryPattern]:
        """내용 패턴 분석"""
        patterns = []
        
        # 키워드 분석
        keyword_counter = Counter()
        for memory in memories:
            # 간단한 키워드 추출 (실제로는 더 정교한 NLP 사용)
            words = re.findall(r'\b\w+\b', memory.content.lower())
            for word in words:
                if len(word) > 3:  # 3글자 이상만
                    keyword_counter[word] += 1
        
        # 주요 키워드 패턴
        for keyword, count in keyword_counter.most_common(10):
            if count >= 3:
                patterns.append(MemoryPattern(
                    pattern_type="keyword",
                    frequency=count,
                    confidence=min(count / len(memories), 1.0),
                    examples=[f"키워드 '{keyword}' {count}회 사용"],
                    context=f"키워드 패턴: {keyword}",
                    importance_score=0.0
                ))
        
        return patterns
    
    def _analyze_importance_patterns(self, memories: List) -> List[MemoryPattern]:
        """중요도 패턴 분석"""
        patterns = []
        
        # 중요도 분포
        importance_ranges = {
            "high": (80, 100),
            "medium": (50, 79),
            "low": (0, 49)
        }
        
        for range_name, (min_val, max_val) in importance_ranges.items():
            count = sum(1 for m in memories if min_val <= m.importance_score <= max_val)
            if count >= 3:
                patterns.append(MemoryPattern(
                    pattern_type="importance_distribution",
                    frequency=count,
                    confidence=count / len(memories),
                    examples=[f"{range_name} 중요도 메모리 {count}개"],
                    context=f"중요도 패턴: {range_name}",
                    importance_score=0.0
                ))
        
        return patterns
    
    def _analyze_source_patterns(self, memories: List) -> List[MemoryPattern]:
        """소스 패턴 분석"""
        patterns = []
        
        # 소스별 분포
        source_counter = Counter()
        for memory in memories:
            source_counter[memory.source] += 1
        
        # 주요 소스 패턴
        for source, count in source_counter.most_common(5):
            if count >= 3:
                patterns.append(MemoryPattern(
                    pattern_type="source_distribution",
                    frequency=count,
                    confidence=count / len(memories),
                    examples=[f"소스 '{source}'에서 {count}개 메모리"],
                    context=f"소스 패턴: {source}",
                    importance_score=0.0
                ))
        
        return patterns
    
    def _calculate_pattern_importance(self, pattern: MemoryPattern) -> float:
        """패턴 중요도 계산"""
        # 빈도, 신뢰도, 패턴 타입을 고려한 중요도 계산
        base_score = pattern.frequency * pattern.confidence
        
        # 패턴 타입별 가중치
        type_weights = {
            "keyword": 1.2,
            "time_distribution": 1.0,
            "importance_distribution": 1.1,
            "source_distribution": 0.9
        }
        
        weight = type_weights.get(pattern.pattern_type, 1.0)
        return min(base_score * weight, 100.0)
    
    def analyze_memory_correlations(self, memory_type: str = None,
                                  time_window: int = 24) -> Dict[str, Any]:
        """메모리 상관관계 분석"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            # 메모리 조회
            memories = memory_service.query_memories(
                memory_type=memory_type,
                limit=1000
            )
            
            # 상관관계 분석
            correlations = self._find_correlations(memories)
            
            result = {
                "analysis_type": "correlation",
                "time_window_hours": time_window,
                "total_memories_analyzed": len(memories),
                "correlations_found": len(correlations),
                "correlations": [
                    {
                        "source_type": c.source_type,
                        "target_type": c.target_type,
                        "correlation_strength": c.correlation_strength,
                        "time_lag": c.time_lag,
                        "context": c.context
                    }
                    for c in correlations
                ]
            }
            
            # 분석 결과 로깅
            log_system_event(
                context="지능형 분석: 상관관계 분석",
                content=f"{len(correlations)}개 상관관계 발견",
                importance_score=65
            )
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"상관관계 분석 실패: {e}")
            return {"error": str(e)}
    
    def _find_correlations(self, memories: List) -> List[MemoryCorrelation]:
        """상관관계 찾기"""
        correlations = []
        
        # 타입별 그룹화
        type_groups = defaultdict(list)
        for memory in memories:
            type_groups[memory.type].append(memory)
        
        # 타입 간 상관관계 분석
        types = list(type_groups.keys())
        for i, source_type in enumerate(types):
            for j, target_type in enumerate(types):
                if i != j:
                    correlation = self._calculate_correlation(
                        type_groups[source_type],
                        type_groups[target_type]
                    )
                    if correlation.correlation_strength > 0.3:  # 임계값
                        correlations.append(correlation)
        
        return correlations
    
    def _calculate_correlation(self, source_memories: List, 
                             target_memories: List) -> MemoryCorrelation:
        """상관관계 계산"""
        # 간단한 시간 기반 상관관계 계산
        source_times = [m.created_at for m in source_memories]
        target_times = [m.created_at for m in target_memories]
        
        # 시간 간격 분석
        time_lags = []
        for source_time in source_times:
            for target_time in target_times:
                lag = abs((source_time - target_time).total_seconds() / 3600)  # 시간 단위
                if lag < 24:  # 24시간 이내
                    time_lags.append(lag)
        
        # 상관관계 강도 계산
        if time_lags:
            avg_lag = sum(time_lags) / len(time_lags)
            correlation_strength = 1.0 / (1.0 + avg_lag)  # 간격이 작을수록 강한 상관관계
        else:
            correlation_strength = 0.0
            avg_lag = None
        
        return MemoryCorrelation(
            source_type=source_memories[0].type if source_memories else "unknown",
            target_type=target_memories[0].type if target_memories else "unknown",
            correlation_strength=correlation_strength,
            time_lag=avg_lag,
            context=f"시간 기반 상관관계"
        )
    
    def generate_intelligent_recommendations(self, 
                                          user_context: str = "",
                                          limit: int = 5) -> Dict[str, Any]:
        """지능형 추천 생성"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            # 최근 메모리 분석
            recent_memories = memory_service.query_memories(limit=100)
            
            # 추천 생성
            recommendations = self._generate_recommendations(
                recent_memories, user_context, limit
            )
            
            result = {
                "analysis_type": "recommendation",
                "user_context": user_context,
                "recommendations_count": len(recommendations),
                "recommendations": recommendations
            }
            
            # 추천 결과 로깅
            log_important_event(
                context="지능형 분석: 추천 생성",
                content=f"{len(recommendations)}개 추천 생성",
                importance_score=70
            )
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"추천 생성 실패: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(self, memories: List, 
                                user_context: str, limit: int) -> List[Dict]:
        """추천 생성"""
        recommendations = []
        
        # 1. 중요도 기반 추천
        high_importance = [m for m in memories if m.importance_score >= 80]
        if high_importance:
            recommendations.append({
                "type": "high_importance_alert",
                "title": "높은 중요도 메모리",
                "description": f"{len(high_importance)}개의 높은 중요도 메모리가 있습니다",
                "priority": "high",
                "action": "review_high_importance"
            })
        
        # 2. 패턴 기반 추천
        if len(memories) >= 10:
            patterns = self._extract_patterns(memories, min_frequency=2)
            if patterns:
                recommendations.append({
                    "type": "pattern_discovery",
                    "title": "새로운 패턴 발견",
                    "description": f"{len(patterns)}개의 새로운 패턴이 발견되었습니다",
                    "priority": "medium",
                    "action": "analyze_patterns"
                })
        
        # 3. 정리 추천
        old_memories = [m for m in memories 
                       if (datetime.now() - m.created_at.replace(tzinfo=None)).days > 30]
        if old_memories:
            recommendations.append({
                "type": "cleanup_suggestion",
                "title": "오래된 메모리 정리",
                "description": f"{len(old_memories)}개의 오래된 메모리를 정리할 수 있습니다",
                "priority": "low",
                "action": "cleanup_old_memories"
            })
        
        # 4. 사용자 컨텍스트 기반 추천
        if user_context:
            context_memories = [m for m in memories 
                              if user_context.lower() in m.content.lower()]
            if context_memories:
                recommendations.append({
                    "type": "context_relevant",
                    "title": "컨텍스트 관련 메모리",
                    "description": f"'{user_context}'와 관련된 {len(context_memories)}개 메모리",
                    "priority": "medium",
                    "action": "search_context"
                })
        
        return recommendations[:limit]
    
    def predict_memory_trends(self, days_ahead: int = 7) -> Dict[str, Any]:
        """메모리 트렌드 예측"""
        try:
            db = next(get_db_session())
            from .memory_service import MemoryService
            memory_service = MemoryService(db)
            
            # 과거 데이터 수집
            past_memories = memory_service.query_memories(limit=1000)
            
            # 트렌드 예측
            predictions = self._predict_trends(past_memories, days_ahead)
            
            result = {
                "analysis_type": "prediction",
                "prediction_days": days_ahead,
                "predictions": predictions
            }
            
            # 예측 결과 로깅
            log_important_event(
                context="지능형 분석: 트렌드 예측",
                content=f"{days_ahead}일 후 트렌드 예측 완료",
                importance_score=75
            )
            
            db.close()
            return result
            
        except Exception as e:
            logger.error(f"트렌드 예측 실패: {e}")
            return {"error": str(e)}
    
    def _predict_trends(self, memories: List, days_ahead: int) -> List[Dict]:
        """트렌드 예측"""
        predictions = []
        
        # 간단한 선형 예측 (실제로는 더 정교한 ML 모델 사용)
        if len(memories) >= 10:
            # 일별 메모리 생성 수 계산
            daily_counts = defaultdict(int)
            for memory in memories:
                date = memory.created_at.date()
                daily_counts[date] += 1
            
            # 평균 일일 생성 수
            avg_daily = sum(daily_counts.values()) / len(daily_counts) if daily_counts else 0
            
            # 예측
            predicted_count = int(avg_daily * days_ahead)
            
            predictions.append({
                "metric": "daily_memory_creation",
                "current_avg": avg_daily,
                "predicted_total": predicted_count,
                "confidence": 0.7,
                "trend": "stable" if 0.8 <= avg_daily <= 1.2 else "increasing" if avg_daily > 1.2 else "decreasing"
            })
        
        return predictions


# 전역 인스턴스
intelligent_analysis_service = IntelligentAnalysisService() 