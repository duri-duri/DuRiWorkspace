"""
Day 7: 자기 진화 시스템
DuRi가 스스로를 분석하고 개선하는 능력 구현
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

class SelfEvolutionService:
    """자기 진화 서비스 - DuRi가 스스로를 분석하고 개선하는 능력"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.analysis_interval = 3600  # 1시간마다 자기 분석
        self.improvement_threshold = 0.1  # 10% 이상 개선 시 적용
        self.adaptation_rate = 0.05  # 적응률
        
    def analyze_self_performance(self) -> Dict[str, Any]:
        """자기 성능 분석"""
        try:
            # 1. 메모리 시스템 성능 분석
            memory_performance = self._analyze_memory_performance()
            
            # 2. 감정 지능 성능 분석
            emotional_performance = self._analyze_emotional_performance()
            
            # 3. 진화 시스템 성능 분석
            evolution_performance = self._analyze_evolution_performance()
            
            # 4. 전체 시스템 성능 종합 분석
            overall_performance = self._analyze_overall_performance(
                memory_performance, emotional_performance, evolution_performance
            )
            
            # 5. 개선점 식별
            improvement_areas = self._identify_improvement_areas(overall_performance)
            
            # 6. 진화 방향 제안
            evolution_directions = self._suggest_evolution_directions(improvement_areas)
            
            return {
                "memory_performance": memory_performance,
                "emotional_performance": emotional_performance,
                "evolution_performance": evolution_performance,
                "overall_performance": overall_performance,
                "improvement_areas": improvement_areas,
                "evolution_directions": evolution_directions,
                "analysis_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"자기 성능 분석 실패: {e}")
            return {"error": str(e)}
    
    def _analyze_memory_performance(self) -> Dict[str, Any]:
        """메모리 시스템 성능 분석"""
        try:
            # 최근 24시간 메모리 통계
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # 메모리 타입별 통계
            memory_stats = self.db.query(
                MemoryEntry.memory_type,
                func.count(MemoryEntry.id).label('count'),
                func.avg(MemoryEntry.importance_score).label('avg_importance'),
                func.avg(MemoryEntry.promotion_count).label('avg_promotions')
            ).filter(
                MemoryEntry.created_at >= cutoff_time
            ).group_by(MemoryEntry.memory_type).all()
            
            # 메모리 효율성 계산
            total_memories = sum(stat.count for stat in memory_stats)
            avg_importance = sum(stat.avg_importance * stat.count for stat in memory_stats) / total_memories if total_memories > 0 else 0
            avg_promotions = sum(stat.avg_promotions * stat.count for stat in memory_stats) / total_memories if total_memories > 0 else 0
            
            # 메모리 성능 점수 계산
            memory_efficiency = min(1.0, (avg_importance * 0.6 + avg_promotions * 0.4))
            
            return {
                "total_memories_24h": total_memories,
                "memory_type_distribution": {stat.memory_type: stat.count for stat in memory_stats},
                "avg_importance_score": avg_importance,
                "avg_promotion_count": avg_promotions,
                "memory_efficiency": memory_efficiency,
                "performance_score": memory_efficiency * 100
            }
            
        except Exception as e:
            logger.error(f"메모리 성능 분석 실패: {e}")
            return {}
    
    def _analyze_emotional_performance(self) -> Dict[str, Any]:
        """감정 지능 성능 분석"""
        try:
            # 최근 24시간 감정 관련 메모리 분석
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # 감정 태그가 있는 메모리 분석
            emotional_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.created_at >= cutoff_time,
                    MemoryEntry.tags.contains(['joy', 'sadness', 'anger', 'fear', 'trust', 'surprise', 'anticipation', 'disgust'])
                )
            ).all()
            
            # 감정 다양성 분석
            emotion_tags = []
            for memory in emotional_memories:
                if memory.tags:
                    emotion_tags.extend([tag for tag in memory.tags if tag in ['joy', 'sadness', 'anger', 'fear', 'trust', 'surprise', 'anticipation', 'disgust']])
            
            emotion_diversity = len(set(emotion_tags)) / 8.0  # 8가지 기본 감정 대비
            
            # 감정 처리 효율성
            emotional_efficiency = len(emotional_memories) / max(1, len(emotional_memories) + 10)  # 처리된 감정 비율
            
            # 복합 감정 처리 능력
            complex_emotions = sum(1 for memory in emotional_memories if memory.tags and len([tag for tag in memory.tags if tag in ['joy', 'sadness', 'anger', 'fear', 'trust', 'surprise', 'anticipation', 'disgust']]) > 1)
            complex_emotion_ratio = complex_emotions / max(1, len(emotional_memories))
            
            return {
                "emotional_memories_24h": len(emotional_memories),
                "emotion_diversity": emotion_diversity,
                "emotional_efficiency": emotional_efficiency,
                "complex_emotion_ratio": complex_emotion_ratio,
                "performance_score": (emotion_diversity * 0.4 + emotional_efficiency * 0.3 + complex_emotion_ratio * 0.3) * 100
            }
            
        except Exception as e:
            logger.error(f"감정 지능 성능 분석 실패: {e}")
            return {}
    
    def _analyze_evolution_performance(self) -> Dict[str, Any]:
        """진화 시스템 성능 분석"""
        try:
            # 최근 24시간 진화 관련 메모리 분석
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # 진화 관련 태그가 있는 메모리
            evolution_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.created_at >= cutoff_time,
                    MemoryEntry.tags.contains(['evolution', 'learning', 'improvement', 'pattern'])
                )
            ).all()
            
            # 진화 빈도
            evolution_frequency = len(evolution_memories) / 24.0  # 시간당 진화 횟수
            
            # 진화 효과성 (중요도 점수 기반)
            evolution_effectiveness = sum(memory.importance_score for memory in evolution_memories) / max(1, len(evolution_memories))
            
            # 패턴 발견 능력
            pattern_memories = [m for m in evolution_memories if 'pattern' in (m.tags or [])]
            pattern_discovery_rate = len(pattern_memories) / max(1, len(evolution_memories))
            
            return {
                "evolution_memories_24h": len(evolution_memories),
                "evolution_frequency": evolution_frequency,
                "evolution_effectiveness": evolution_effectiveness,
                "pattern_discovery_rate": pattern_discovery_rate,
                "performance_score": (evolution_frequency * 0.3 + evolution_effectiveness * 0.4 + pattern_discovery_rate * 0.3) * 100
            }
            
        except Exception as e:
            logger.error(f"진화 시스템 성능 분석 실패: {e}")
            return {}
    
    def _analyze_overall_performance(
        self, 
        memory_performance: Dict[str, Any],
        emotional_performance: Dict[str, Any],
        evolution_performance: Dict[str, Any]
    ) -> Dict[str, Any]:
        """전체 시스템 성능 종합 분석"""
        try:
            # 각 시스템의 성능 점수
            memory_score = memory_performance.get('performance_score', 0)
            emotional_score = emotional_performance.get('performance_score', 0)
            evolution_score = evolution_performance.get('performance_score', 0)
            
            # 가중 평균 계산 (각 시스템의 중요도에 따라)
            weights = {
                'memory': 0.4,      # 메모리는 기반 시스템
                'emotional': 0.35,   # 감정 지능은 핵심 기능
                'evolution': 0.25    # 진화는 향상 기능
            }
            
            overall_score = (
                memory_score * weights['memory'] +
                emotional_score * weights['emotional'] +
                evolution_score * weights['evolution']
            )
            
            # 시스템 균형성 분석
            scores = [memory_score, emotional_score, evolution_score]
            balance_score = 1.0 - (np.std(scores) / 100.0)  # 표준편차가 작을수록 균형적
            
            # 성능 트렌드 분석
            trend_analysis = self._analyze_performance_trend()
            
            return {
                "overall_score": overall_score,
                "balance_score": balance_score,
                "system_scores": {
                    "memory": memory_score,
                    "emotional": emotional_score,
                    "evolution": evolution_score
                },
                "trend_analysis": trend_analysis,
                "performance_level": self._determine_performance_level(overall_score)
            }
            
        except Exception as e:
            logger.error(f"전체 성능 분석 실패: {e}")
            return {}
    
    def _analyze_performance_trend(self) -> Dict[str, Any]:
        """성능 트렌드 분석"""
        try:
            # 최근 7일간의 성능 데이터 수집
            trend_data = []
            for i in range(7):
                date = datetime.utcnow() - timedelta(days=i)
                # 실제 구현에서는 이전 분석 결과를 DB에서 조회
                trend_data.append({
                    "date": date.date().isoformat(),
                    "score": 70 + (i * 2) + np.random.normal(0, 5)  # 예시 데이터
                })
            
            # 트렌드 계산
            if len(trend_data) >= 2:
                recent_scores = [d['score'] for d in trend_data[:3]]
                older_scores = [d['score'] for d in trend_data[-3:]]
                trend_direction = np.mean(recent_scores) - np.mean(older_scores)
                trend_strength = abs(trend_direction) / 10.0
            else:
                trend_direction = 0
                trend_strength = 0
            
            return {
                "trend_direction": "improving" if trend_direction > 0 else "declining" if trend_direction < 0 else "stable",
                "trend_strength": min(1.0, trend_strength),
                "trend_magnitude": abs(trend_direction),
                "recent_trend_data": trend_data
            }
            
        except Exception as e:
            logger.error(f"성능 트렌드 분석 실패: {e}")
            return {}
    
    def _determine_performance_level(self, score: float) -> str:
        """성능 수준 결정"""
        if score >= 90:
            return "excellent"
        elif score >= 80:
            return "good"
        elif score >= 70:
            return "average"
        elif score >= 60:
            return "below_average"
        else:
            return "poor"
    
    def _identify_improvement_areas(self, overall_performance: Dict[str, Any]) -> List[Dict[str, Any]]:
        """개선점 식별"""
        try:
            improvement_areas = []
            system_scores = overall_performance.get('system_scores', {})
            
            # 각 시스템별 개선점 분석
            for system, score in system_scores.items():
                if score < 80:  # 80점 미만인 시스템
                    improvement_areas.append({
                        "system": system,
                        "current_score": score,
                        "target_score": 85,
                        "improvement_needed": 85 - score,
                        "priority": "high" if score < 70 else "medium",
                        "suggested_actions": self._get_suggested_actions(system, score)
                    })
            
            # 전체 성능 개선점
            overall_score = overall_performance.get('overall_score', 0)
            if overall_score < 80:
                improvement_areas.append({
                    "system": "overall",
                    "current_score": overall_score,
                    "target_score": 85,
                    "improvement_needed": 85 - overall_score,
                    "priority": "high",
                    "suggested_actions": ["시스템 간 균형 개선", "통합 성능 최적화"]
                })
            
            return improvement_areas
            
        except Exception as e:
            logger.error(f"개선점 식별 실패: {e}")
            return []
    
    def _get_suggested_actions(self, system: str, score: float) -> List[str]:
        """시스템별 제안 액션"""
        suggestions = {
            "memory": [
                "메모리 효율성 최적화",
                "중요도 점수 알고리즘 개선",
                "메모리 생명주기 관리 강화"
            ],
            "emotional": [
                "복합 감정 분석 정확도 향상",
                "감정-이성 균형 알고리즘 개선",
                "공감 능력 강화"
            ],
            "evolution": [
                "패턴 발견 알고리즘 개선",
                "진화 속도 최적화",
                "학습 효율성 향상"
            ]
        }
        
        return suggestions.get(system, ["일반적인 성능 최적화"])
    
    def _suggest_evolution_directions(self, improvement_areas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """진화 방향 제안"""
        try:
            evolution_directions = []
            
            for area in improvement_areas:
                system = area['system']
                priority = area['priority']
                
                if system == "memory":
                    evolution_directions.append({
                        "direction": "memory_optimization",
                        "priority": priority,
                        "description": "메모리 시스템 최적화",
                        "expected_improvement": 15,
                        "implementation_time": "2-3주"
                    })
                elif system == "emotional":
                    evolution_directions.append({
                        "direction": "emotional_intelligence_enhancement",
                        "priority": priority,
                        "description": "감정 지능 강화",
                        "expected_improvement": 20,
                        "implementation_time": "3-4주"
                    })
                elif system == "evolution":
                    evolution_directions.append({
                        "direction": "evolution_algorithm_improvement",
                        "priority": priority,
                        "description": "진화 알고리즘 개선",
                        "expected_improvement": 25,
                        "implementation_time": "4-5주"
                    })
                elif system == "overall":
                    evolution_directions.append({
                        "direction": "system_integration_optimization",
                        "priority": priority,
                        "description": "시스템 통합 최적화",
                        "expected_improvement": 10,
                        "implementation_time": "5-6주"
                    })
            
            return evolution_directions
            
        except Exception as e:
            logger.error(f"진화 방향 제안 실패: {e}")
            return []
    
    def auto_improve_system(self) -> Dict[str, Any]:
        """시스템 자동 개선"""
        try:
            # 1. 현재 성능 분석
            performance_analysis = self.analyze_self_performance()
            
            if "error" in performance_analysis:
                return {"error": performance_analysis["error"]}
            
            # 2. 개선점 식별
            improvement_areas = performance_analysis.get("improvement_areas", [])
            
            # 3. 자동 개선 실행
            improvements_made = []
            for area in improvement_areas:
                if area.get("priority") == "high":
                    improvement_result = self._execute_improvement(area)
                    if improvement_result:
                        improvements_made.append(improvement_result)
            
            # 4. 개선 효과 측정
            improvement_metrics = self._measure_improvement_effect(improvements_made)
            
            return {
                "improvements_made": improvements_made,
                "improvement_metrics": improvement_metrics,
                "auto_improvement_timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"시스템 자동 개선 실패: {e}")
            return {"error": str(e)}
    
    def _execute_improvement(self, improvement_area: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """개선 실행"""
        try:
            system = improvement_area.get("system")
            current_score = improvement_area.get("current_score", 0)
            
            # 시스템별 개선 로직
            if system == "memory":
                return self._improve_memory_system(current_score)
            elif system == "emotional":
                return self._improve_emotional_system(current_score)
            elif system == "evolution":
                return self._improve_evolution_system(current_score)
            else:
                return self._improve_general_system(current_score)
                
        except Exception as e:
            logger.error(f"개선 실행 실패: {e}")
            return None
    
    def _improve_memory_system(self, current_score: float) -> Dict[str, Any]:
        """메모리 시스템 개선"""
        try:
            # 메모리 효율성 최적화
            optimization_result = {
                "system": "memory",
                "improvement_type": "efficiency_optimization",
                "previous_score": current_score,
                "improvement_applied": "메모리 생명주기 관리 강화",
                "expected_improvement": min(15, 100 - current_score)
            }
            
            # 실제 개선 로직 (예시)
            # self._optimize_memory_lifecycle()
            # self._improve_importance_scoring()
            
            return optimization_result
            
        except Exception as e:
            logger.error(f"메모리 시스템 개선 실패: {e}")
            return {}
    
    def _improve_emotional_system(self, current_score: float) -> Dict[str, Any]:
        """감정 지능 시스템 개선"""
        try:
            # 감정 분석 정확도 향상
            improvement_result = {
                "system": "emotional",
                "improvement_type": "accuracy_enhancement",
                "previous_score": current_score,
                "improvement_applied": "복합 감정 분석 알고리즘 개선",
                "expected_improvement": min(20, 100 - current_score)
            }
            
            # 실제 개선 로직 (예시)
            # self._enhance_emotion_analysis()
            # self._improve_empathy_algorithm()
            
            return improvement_result
            
        except Exception as e:
            logger.error(f"감정 지능 시스템 개선 실패: {e}")
            return {}
    
    def _improve_evolution_system(self, current_score: float) -> Dict[str, Any]:
        """진화 시스템 개선"""
        try:
            # 진화 알고리즘 개선
            improvement_result = {
                "system": "evolution",
                "improvement_type": "algorithm_optimization",
                "previous_score": current_score,
                "improvement_applied": "패턴 발견 알고리즘 개선",
                "expected_improvement": min(25, 100 - current_score)
            }
            
            # 실제 개선 로직 (예시)
            # self._optimize_pattern_discovery()
            # self._improve_learning_rate()
            
            return improvement_result
            
        except Exception as e:
            logger.error(f"진화 시스템 개선 실패: {e}")
            return {}
    
    def _improve_general_system(self, current_score: float) -> Dict[str, Any]:
        """일반 시스템 개선"""
        try:
            # 일반적인 성능 최적화
            improvement_result = {
                "system": "general",
                "improvement_type": "performance_optimization",
                "previous_score": current_score,
                "improvement_applied": "시스템 통합 최적화",
                "expected_improvement": min(10, 100 - current_score)
            }
            
            return improvement_result
            
        except Exception as e:
            logger.error(f"일반 시스템 개선 실패: {e}")
            return {}
    
    def _measure_improvement_effect(self, improvements_made: List[Dict[str, Any]]) -> Dict[str, Any]:
        """개선 효과 측정"""
        try:
            total_improvements = len(improvements_made)
            total_expected_improvement = sum(imp.get("expected_improvement", 0) for imp in improvements_made)
            
            return {
                "total_improvements_applied": total_improvements,
                "total_expected_improvement": total_expected_improvement,
                "average_improvement_per_system": total_expected_improvement / max(1, total_improvements),
                "improvement_efficiency": min(1.0, total_improvements / 5.0)  # 최대 5개 시스템 개선 가능
            }
            
        except Exception as e:
            logger.error(f"개선 효과 측정 실패: {e}")
            return {}
    
    def get_self_evolution_stats(self) -> Dict[str, Any]:
        """자기 진화 통계 조회"""
        try:
            # 최근 24시간 진화 활동 통계
            cutoff_time = datetime.utcnow() - timedelta(hours=24)
            
            # 자기 분석 횟수
            analysis_count = 1  # 실제로는 DB에서 조회
            
            # 개선 적용 횟수
            improvement_count = 1  # 실제로는 DB에서 조회
            
            # 진화 진행도
            evolution_progress = {
                "memory_optimization": 75,
                "emotional_enhancement": 80,
                "evolution_algorithm": 70,
                "overall_integration": 65
            }
            
            return {
                "analysis_count_24h": analysis_count,
                "improvement_count_24h": improvement_count,
                "evolution_progress": evolution_progress,
                "self_evolution_score": sum(evolution_progress.values()) / len(evolution_progress)
            }
            
        except Exception as e:
            logger.error(f"자기 진화 통계 조회 실패: {e}")
            return {} 