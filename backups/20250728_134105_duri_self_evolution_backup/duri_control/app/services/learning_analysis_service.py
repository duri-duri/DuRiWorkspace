"""
DuRi Memory System - Learning Analysis Service
중기 기억에서의 학습 및 교정 분석
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from collections import defaultdict, Counter
import difflib
import re

from ..models.memory import MemoryEntry
from ..utils.db_retry import retry_on_db_error

logger = logging.getLogger(__name__)

class LearningAnalysisService:
    """학습 분석 및 교정 서비스"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def analyze_learning_patterns(self, memory_id: int) -> Dict[str, Any]:
        """중기 기억의 학습 패턴 분석"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory or memory.memory_level != 'medium':
                return {"error": "Not a medium-level memory"}
            
            # 유사한 중기 기억들 조회
            similar_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.id != memory_id,
                    MemoryEntry.memory_level == 'medium',
                    or_(
                        MemoryEntry.context == memory.context,
                        MemoryEntry.type == memory.type,
                        MemoryEntry.content.contains(memory.content[:30])
                    )
                )
            ).order_by(desc(MemoryEntry.created_at)).all()
            
            if not similar_memories:
                return {
                    "learning_patterns": False,
                    "reason": "No similar medium memories found",
                    "similar_count": 0
                }
            
            # 학습 패턴 분석
            learning_analysis = {
                "learning_patterns": True,
                "similar_count": len(similar_memories),
                "success_patterns": [],
                "failure_patterns": [],
                "improvement_suggestions": [],
                "consistency_score": 0
            }
            
            # 성공/실패 패턴 분석
            success_memories = []
            failure_memories = []
            
            for similar_memory in similar_memories:
                if self._is_success_memory(similar_memory):
                    success_memories.append(similar_memory)
                elif self._is_failure_memory(similar_memory):
                    failure_memories.append(similar_memory)
            
            # 성공 패턴 분석
            if success_memories:
                success_patterns = self._extract_success_patterns(success_memories)
                learning_analysis["success_patterns"] = success_patterns
            
            # 실패 패턴 분석
            if failure_memories:
                failure_patterns = self._extract_failure_patterns(failure_memories)
                learning_analysis["failure_patterns"] = failure_patterns
            
            # 개선 제안 생성
            improvement_suggestions = self._generate_improvement_suggestions(
                success_memories, failure_memories, memory
            )
            learning_analysis["improvement_suggestions"] = improvement_suggestions
            
            # 일관성 점수 계산
            total_memories = len(similar_memories)
            if total_memories > 0:
                success_rate = len(success_memories) / total_memories
                learning_analysis["consistency_score"] = int(success_rate * 100)
            
            logger.info(f"Learning patterns analyzed for memory {memory_id}: {len(similar_memories)} similar memories")
            
            return learning_analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze learning patterns: {e}")
            raise
    
    def _is_success_memory(self, memory: MemoryEntry) -> bool:
        """성공 기억 판별"""
        success_indicators = ['success', 'good', 'correct', 'helpful', 'solved', 'fixed']
        
        # 태그 기반 판별
        if memory.tags:
            for tag in memory.tags:
                if tag in success_indicators:
                    return True
        
        # 내용 기반 판별
        content_lower = memory.content.lower()
        for indicator in success_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _is_failure_memory(self, memory: MemoryEntry) -> bool:
        """실패 기억 판별"""
        failure_indicators = ['error', 'fail', 'wrong', 'bad', 'useless', 'broken', 'confusion']
        
        # 태그 기반 판별
        if memory.tags:
            for tag in memory.tags:
                if tag in failure_indicators:
                    return True
        
        # 내용 기반 판별
        content_lower = memory.content.lower()
        for indicator in failure_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _extract_success_patterns(self, success_memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
        """성공 패턴 추출"""
        patterns = []
        
        for memory in success_memories:
            pattern = {
                "memory_id": memory.id,
                "content": memory.content,
                "tags": memory.tags,
                "importance_score": memory.importance_score,
                "created_at": memory.created_at.isoformat(),
                "success_factors": self._extract_success_factors(memory)
            }
            patterns.append(pattern)
        
        return patterns
    
    def _extract_failure_patterns(self, failure_memories: List[MemoryEntry]) -> List[Dict[str, Any]]:
        """실패 패턴 추출"""
        patterns = []
        
        for memory in failure_memories:
            pattern = {
                "memory_id": memory.id,
                "content": memory.content,
                "tags": memory.tags,
                "importance_score": memory.importance_score,
                "created_at": memory.created_at.isoformat(),
                "failure_factors": self._extract_failure_factors(memory)
            }
            patterns.append(pattern)
        
        return patterns
    
    def _extract_success_factors(self, memory: MemoryEntry) -> List[str]:
        """성공 요인 추출"""
        factors = []
        
        # 높은 중요도 점수
        if memory.importance_score >= 70:
            factors.append("high_importance")
        
        # 사용자 소스
        if memory.source == 'user':
            factors.append("user_feedback")
        
        # 긍정적 태그
        if memory.tags:
            positive_tags = ['success', 'good', 'correct', 'helpful']
            for tag in memory.tags:
                if tag in positive_tags:
                    factors.append(f"positive_tag_{tag}")
        
        return factors
    
    def _extract_failure_factors(self, memory: MemoryEntry) -> List[str]:
        """실패 요인 추출"""
        factors = []
        
        # 부정적 태그
        if memory.tags:
            negative_tags = ['error', 'fail', 'wrong', 'bad', 'useless']
            for tag in memory.tags:
                if tag in negative_tags:
                    factors.append(f"negative_tag_{tag}")
        
        # 낮은 중요도 점수
        if memory.importance_score <= 30:
            factors.append("low_importance")
        
        return factors
    
    def _generate_improvement_suggestions(self, success_memories: List[MemoryEntry], 
                                        failure_memories: List[MemoryEntry], 
                                        target_memory: MemoryEntry) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 성공 패턴에서 학습할 점
        if success_memories:
            success_factors = []
            for memory in success_memories:
                factors = self._extract_success_factors(memory)
                success_factors.extend(factors)
            
            # 가장 빈번한 성공 요인
            factor_counter = Counter(success_factors)
            common_success_factors = factor_counter.most_common(3)
            
            for factor, count in common_success_factors:
                if factor == "high_importance":
                    suggestions.append("중요도 점수를 높여보세요 (70점 이상)")
                elif factor == "user_feedback":
                    suggestions.append("사용자 피드백을 더 적극적으로 수집하세요")
                elif factor.startswith("positive_tag_"):
                    tag = factor.replace("positive_tag_", "")
                    suggestions.append(f"'{tag}' 태그를 활용하세요")
        
        # 실패 패턴에서 피할 점
        if failure_memories:
            failure_factors = []
            for memory in failure_memories:
                factors = self._extract_failure_factors(memory)
                failure_factors.extend(factors)
            
            factor_counter = Counter(failure_factors)
            common_failure_factors = factor_counter.most_common(3)
            
            for factor, count in common_failure_factors:
                if factor == "low_importance":
                    suggestions.append("중요도 점수를 높여 실패 가능성을 줄이세요")
                elif factor.startswith("negative_tag_"):
                    tag = factor.replace("negative_tag_", "")
                    suggestions.append(f"'{tag}' 상황을 피하거나 개선하세요")
        
        # 일반적인 개선 제안
        if not suggestions:
            suggestions.append("더 많은 데이터를 수집하여 패턴을 분석하세요")
            suggestions.append("사용자 피드백을 정기적으로 수집하세요")
        
        return suggestions[:5]  # 최대 5개 제안
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def compare_memories(self, memory_id_1: int, memory_id_2: int) -> Dict[str, Any]:
        """두 기억 비교 분석"""
        try:
            memory_1 = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id_1).first()
            memory_2 = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id_2).first()
            
            if not memory_1 or not memory_2:
                return {"error": "One or both memories not found"}
            
            comparison = {
                "memory_1": {
                    "id": memory_1.id,
                    "content": memory_1.content,
                    "level": memory_1.memory_level,
                    "importance": memory_1.importance_score,
                    "tags": memory_1.tags,
                    "created_at": memory_1.created_at.isoformat()
                },
                "memory_2": {
                    "id": memory_2.id,
                    "content": memory_2.content,
                    "level": memory_2.memory_level,
                    "importance": memory_2.importance_score,
                    "tags": memory_2.tags,
                    "created_at": memory_2.created_at.isoformat()
                },
                "similarities": [],
                "differences": [],
                "learning_insights": []
            }
            
            # 유사점 분석
            similarities = self._find_similarities(memory_1, memory_2)
            comparison["similarities"] = similarities
            
            # 차이점 분석
            differences = self._find_differences(memory_1, memory_2)
            comparison["differences"] = differences
            
            # 학습 인사이트 생성
            insights = self._generate_comparison_insights(memory_1, memory_2, similarities, differences)
            comparison["learning_insights"] = insights
            
            return comparison
            
        except Exception as e:
            logger.error(f"Failed to compare memories: {e}")
            raise
    
    def _find_similarities(self, memory_1: MemoryEntry, memory_2: MemoryEntry) -> List[str]:
        """유사점 찾기"""
        similarities = []
        
        # 같은 타입
        if memory_1.type == memory_2.type:
            similarities.append(f"Same type: {memory_1.type}")
        
        # 같은 소스
        if memory_1.source == memory_2.source:
            similarities.append(f"Same source: {memory_1.source}")
        
        # 유사한 중요도 점수
        if abs(memory_1.importance_score - memory_2.importance_score) <= 10:
            similarities.append("Similar importance scores")
        
        # 공통 태그
        if memory_1.tags and memory_2.tags:
            common_tags = set(memory_1.tags) & set(memory_2.tags)
            if common_tags:
                similarities.append(f"Common tags: {list(common_tags)}")
        
        # 유사한 컨텍스트
        if memory_1.context == memory_2.context:
            similarities.append("Same context")
        
        return similarities
    
    def _find_differences(self, memory_1: MemoryEntry, memory_2: MemoryEntry) -> List[str]:
        """차이점 찾기"""
        differences = []
        
        # 다른 레벨
        if memory_1.memory_level != memory_2.memory_level:
            differences.append(f"Different levels: {memory_1.memory_level} vs {memory_2.memory_level}")
        
        # 다른 중요도 점수
        if abs(memory_1.importance_score - memory_2.importance_score) > 10:
            differences.append(f"Different importance: {memory_1.importance_score} vs {memory_2.importance_score}")
        
        # 다른 태그
        if memory_1.tags and memory_2.tags:
            unique_tags_1 = set(memory_1.tags) - set(memory_2.tags)
            unique_tags_2 = set(memory_2.tags) - set(memory_1.tags)
            if unique_tags_1:
                differences.append(f"Unique tags in memory 1: {list(unique_tags_1)}")
            if unique_tags_2:
                differences.append(f"Unique tags in memory 2: {list(unique_tags_2)}")
        
        # 다른 컨텍스트
        if memory_1.context != memory_2.context:
            differences.append("Different contexts")
        
        return differences
    
    def _generate_comparison_insights(self, memory_1: MemoryEntry, memory_2: MemoryEntry, 
                                    similarities: List[str], differences: List[str]) -> List[str]:
        """비교 인사이트 생성"""
        insights = []
        
        # 성공/실패 패턴 분석
        is_success_1 = self._is_success_memory(memory_1)
        is_success_2 = self._is_success_memory(memory_2)
        
        if is_success_1 and not is_success_2:
            insights.append("Memory 1이 성공 패턴을 보이므로 Memory 2의 개선점을 찾아보세요")
        elif not is_success_1 and is_success_2:
            insights.append("Memory 2가 성공 패턴을 보이므로 Memory 1의 문제점을 분석해보세요")
        elif is_success_1 and is_success_2:
            insights.append("두 기억 모두 성공 패턴을 보이므로 공통 성공 요인을 활용하세요")
        else:
            insights.append("두 기억 모두 개선이 필요합니다. 실패 요인을 분석해보세요")
        
        # 중요도 점수 인사이트
        if memory_1.importance_score > memory_2.importance_score + 20:
            insights.append("Memory 1의 높은 중요도가 성공에 기여했을 수 있습니다")
        elif memory_2.importance_score > memory_1.importance_score + 20:
            insights.append("Memory 2의 높은 중요도가 성공에 기여했을 수 있습니다")
        
        # 태그 기반 인사이트
        if memory_1.tags and memory_2.tags:
            success_tags = ['success', 'good', 'correct', 'helpful']
            failure_tags = ['error', 'fail', 'wrong', 'bad']
            
            success_tags_1 = [tag for tag in memory_1.tags if tag in success_tags]
            success_tags_2 = [tag for tag in memory_2.tags if tag in success_tags]
            
            if success_tags_1 and not success_tags_2:
                insights.append(f"Memory 1의 성공 태그({success_tags_1})가 성공에 기여했습니다")
            elif success_tags_2 and not success_tags_1:
                insights.append(f"Memory 2의 성공 태그({success_tags_2})가 성공에 기여했습니다")
        
        return insights
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def generate_learning_report(self, memory_id: int) -> Dict[str, Any]:
        """학습 리포트 생성"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory:
                return {"error": "Memory not found"}
            
            # 학습 패턴 분석
            learning_patterns = self.analyze_learning_patterns(memory_id)
            
            # 유사한 기억들 조회
            similar_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.id != memory_id,
                    MemoryEntry.memory_level == 'medium',
                    or_(
                        MemoryEntry.context == memory.context,
                        MemoryEntry.type == memory.type
                    )
                )
            ).order_by(desc(MemoryEntry.created_at)).limit(5).all()
            
            # 비교 분석
            comparisons = []
            if len(similar_memories) >= 2:
                for i in range(min(3, len(similar_memories))):
                    comparison = self.compare_memories(memory_id, similar_memories[i].id)
                    if "error" not in comparison:
                        comparisons.append(comparison)
            
            # 리포트 생성
            report = {
                "memory_id": memory_id,
                "memory_info": {
                    "content": memory.content,
                    "level": memory.memory_level,
                    "importance": memory.importance_score,
                    "tags": memory.tags,
                    "created_at": memory.created_at.isoformat()
                },
                "learning_patterns": learning_patterns,
                "similar_memories_count": len(similar_memories),
                "comparisons": comparisons,
                "summary": self._generate_learning_summary(memory, learning_patterns, comparisons),
                "recommendations": self._generate_learning_recommendations(memory, learning_patterns)
            }
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate learning report: {e}")
            raise
    
    def _generate_learning_summary(self, memory: MemoryEntry, learning_patterns: Dict[str, Any], 
                                 comparisons: List[Dict[str, Any]]) -> str:
        """학습 요약 생성"""
        summary_parts = []
        
        if learning_patterns.get("learning_patterns"):
            similar_count = learning_patterns.get("similar_count", 0)
            consistency_score = learning_patterns.get("consistency_score", 0)
            
            summary_parts.append(f"이 기억은 {similar_count}개의 유사한 중기 기억과 연관되어 있습니다.")
            summary_parts.append(f"일관성 점수는 {consistency_score}점입니다.")
            
            if consistency_score >= 70:
                summary_parts.append("높은 일관성을 보이므로 Truth Memory로 승격을 고려해보세요.")
            elif consistency_score >= 50:
                summary_parts.append("보통의 일관성을 보이므로 더 많은 데이터를 수집해보세요.")
            else:
                summary_parts.append("낮은 일관성을 보이므로 개선이 필요합니다.")
        else:
            summary_parts.append("아직 유사한 중기 기억이 충분하지 않습니다.")
            summary_parts.append("더 많은 경험을 쌓아 패턴을 분석해보세요.")
        
        if comparisons:
            summary_parts.append(f"{len(comparisons)}개의 비교 분석이 수행되었습니다.")
        
        return " ".join(summary_parts)
    
    def _generate_learning_recommendations(self, memory: MemoryEntry, 
                                         learning_patterns: Dict[str, Any]) -> List[str]:
        """학습 권장사항 생성"""
        recommendations = []
        
        if learning_patterns.get("learning_patterns"):
            # 개선 제안 추가
            improvement_suggestions = learning_patterns.get("improvement_suggestions", [])
            recommendations.extend(improvement_suggestions)
            
            # 일관성 기반 권장사항
            consistency_score = learning_patterns.get("consistency_score", 0)
            if consistency_score >= 80:
                recommendations.append("Truth Memory 승격을 시도해보세요")
            elif consistency_score <= 30:
                recommendations.append("더 많은 성공 사례를 수집해보세요")
            
            # 성공/실패 패턴 기반 권장사항
            success_patterns = learning_patterns.get("success_patterns", [])
            failure_patterns = learning_patterns.get("failure_patterns", [])
            
            if len(success_patterns) > len(failure_patterns):
                recommendations.append("성공 패턴을 더 적극적으로 활용하세요")
            elif len(failure_patterns) > len(success_patterns):
                recommendations.append("실패 패턴을 분석하여 개선점을 찾아보세요")
        else:
            recommendations.append("더 많은 중기 기억을 생성하여 학습 패턴을 분석하세요")
            recommendations.append("다양한 상황에서의 경험을 기록하세요")
        
        return recommendations[:5]  # 최대 5개 권장사항 