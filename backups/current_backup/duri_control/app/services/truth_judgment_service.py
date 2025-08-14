"""
DuRi Memory System - Truth Memory 기반 판단 서비스
DuRi의 신념(Truth Memory)을 바탕으로 정확한 판단 수행
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

class TruthJudgmentService:
    """Truth Memory 기반 판단 서비스"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_truth_memories(self, context: Optional[str] = None, 
                          memory_type: Optional[str] = None,
                          limit: int = 50) -> List[MemoryEntry]:
        """Truth Memory 조회"""
        try:
            query = self.db.query(MemoryEntry).filter(
                MemoryEntry.memory_level == 'truth'
            ).order_by(desc(MemoryEntry.importance_score), desc(MemoryEntry.created_at))
            
            if context:
                query = query.filter(MemoryEntry.context.contains(context))
            
            if memory_type:
                query = query.filter(MemoryEntry.type == memory_type)
            
            memories = query.limit(limit).all()
            logger.info(f"Retrieved {len(memories)} truth memories")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get truth memories: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def make_judgment(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """상황에 대한 Truth Memory 기반 판단"""
        try:
            # 상황 분석
            situation_type = situation.get('type', 'general')
            situation_context = situation.get('context', '')
            situation_content = situation.get('content', '')
            situation_tags = situation.get('tags', [])
            
            # 관련 Truth Memory 조회
            relevant_truths = self._find_relevant_truth_memories(
                situation_type, situation_context, situation_content, situation_tags
            )
            
            if not relevant_truths:
                return {
                    "judgment": "uncertain",
                    "confidence": 0,
                    "reason": "No relevant truth memories found",
                    "relevant_truths": [],
                    "recommendations": ["더 많은 Truth Memory를 수집하세요"]
                }
            
            # 판단 수행
            judgment_result = self._perform_judgment(situation, relevant_truths)
            
            return judgment_result
            
        except Exception as e:
            logger.error(f"Failed to make judgment: {e}")
            raise
    
    def _find_relevant_truth_memories(self, situation_type: str, situation_context: str,
                                    situation_content: str, situation_tags: List[str]) -> List[MemoryEntry]:
        """상황과 관련된 Truth Memory 찾기"""
        relevant_memories = []
        
        # 1. 타입 기반 매칭
        type_query = self.db.query(MemoryEntry).filter(
            and_(
                MemoryEntry.memory_level == 'truth',
                MemoryEntry.type == situation_type
            )
        )
        print("[SQL][type_query]", type_query.statement)
        type_matches = type_query.all()
        relevant_memories.extend(type_matches)
        
        # 2. 컨텍스트 기반 매칭
        if situation_context:
            try:
                context_query = self.db.query(MemoryEntry).filter(
                    and_(
                        MemoryEntry.memory_level == 'truth',
                        MemoryEntry.context.contains(situation_context[:30])
                    )
                )
                print("[SQL][context_query]", context_query.statement)
                context_matches = context_query.all()
                relevant_memories.extend(context_matches)
            except Exception as e:
                logger.warning(f"Context matching failed: {e}")
        
        # 3. 태그 기반 매칭 (임시로 비활성화)
        # JSONB LIKE 연산자 문제로 인해 임시로 비활성화
        # TODO: PostgreSQL JSONB 연산자로 수정 필요
        pass
        
        # 4. 내용 기반 유사도 매칭
        content_matches = self._find_content_similar_truths(situation_content)
        relevant_memories.extend(content_matches)
        
        # 중복 제거 및 정렬
        unique_memories = list({memory.id: memory for memory in relevant_memories}.values())
        unique_memories.sort(key=lambda x: x.importance_score, reverse=True)
        
        return unique_memories[:20]  # 최대 20개
    
    def _find_content_similar_truths(self, situation_content: str) -> List[MemoryEntry]:
        """내용 유사도 기반 Truth Memory 찾기"""
        if not situation_content:
            return []
        
        # 모든 Truth Memory 조회
        all_truths = self.db.query(MemoryEntry).filter(
            MemoryEntry.memory_level == 'truth'
        ).all()
        
        similar_memories = []
        content_words = set(situation_content.lower().split())
        
        for memory in all_truths:
            memory_words = set(memory.content.lower().split())
            
            # 단어 겹침 계산
            if memory_words:
                overlap = len(content_words & memory_words) / len(content_words | memory_words)
                if overlap > 0.3:  # 30% 이상 겹치면 관련성 있다고 판단
                    similar_memories.append(memory)
        
        return similar_memories
    
    def _perform_judgment(self, situation: Dict[str, Any], 
                         relevant_truths: List[MemoryEntry]) -> Dict[str, Any]:
        """Truth Memory 기반 판단 수행"""
        if not relevant_truths:
            return {
                "judgment": "uncertain",
                "confidence": 0,
                "reason": "No relevant truth memories",
                "relevant_truths": [],
                "recommendations": []
            }
        
        # 성공/실패 패턴 분석
        success_truths = []
        failure_truths = []
        
        for truth in relevant_truths:
            if self._is_success_truth(truth):
                success_truths.append(truth)
            elif self._is_failure_truth(truth):
                failure_truths.append(truth)
        
        # 판단 로직
        total_relevant = len(relevant_truths)
        success_ratio = len(success_truths) / total_relevant if total_relevant > 0 else 0
        failure_ratio = len(failure_truths) / total_relevant if total_relevant > 0 else 0
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(relevant_truths, success_ratio, failure_ratio)
        
        # 판단 결정
        if success_ratio > 0.7:
            judgment = "success_likely"
            reason = f"성공 패턴이 우세합니다 ({success_ratio:.1%})"
        elif failure_ratio > 0.7:
            judgment = "failure_likely"
            reason = f"실패 패턴이 우세합니다 ({failure_ratio:.1%})"
        elif success_ratio > failure_ratio:
            judgment = "success_possible"
            reason = f"성공 가능성이 있습니다 ({success_ratio:.1%} vs {failure_ratio:.1%})"
        elif failure_ratio > success_ratio:
            judgment = "failure_possible"
            reason = f"실패 가능성이 있습니다 ({failure_ratio:.1%} vs {success_ratio:.1%})"
        else:
            judgment = "uncertain"
            reason = "성공과 실패 패턴이 균형을 이룹니다"
        
        # 권장사항 생성
        recommendations = self._generate_judgment_recommendations(
            judgment, success_truths, failure_truths, situation
        )
        
        return {
            "judgment": judgment,
            "confidence": confidence,
            "reason": reason,
            "relevant_truths": [truth.to_dict() for truth in relevant_truths[:5]],  # 상위 5개만
            "success_ratio": success_ratio,
            "failure_ratio": failure_ratio,
            "recommendations": recommendations
        }
    
    def _is_success_truth(self, truth: MemoryEntry) -> bool:
        """성공 Truth Memory 판별"""
        success_indicators = ['success', 'good', 'correct', 'helpful', 'solved', 'fixed', 'effective']
        
        # 태그 기반 판별
        if truth.tags:
            for tag in truth.tags:
                if tag in success_indicators:
                    return True
        
        # 내용 기반 판별
        content_lower = truth.content.lower()
        for indicator in success_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _is_failure_truth(self, truth: MemoryEntry) -> bool:
        """실패 Truth Memory 판별"""
        failure_indicators = ['error', 'fail', 'wrong', 'bad', 'useless', 'broken', 'ineffective']
        
        # 태그 기반 판별
        if truth.tags:
            for tag in truth.tags:
                if tag in failure_indicators:
                    return True
        
        # 내용 기반 판별
        content_lower = truth.content.lower()
        for indicator in failure_indicators:
            if indicator in content_lower:
                return True
        
        return False
    
    def _calculate_confidence(self, relevant_truths: List[MemoryEntry], 
                            success_ratio: float, failure_ratio: float) -> float:
        """판단 신뢰도 계산"""
        if not relevant_truths:
            return 0.0
        
        # 기본 신뢰도: 관련 Truth Memory 수 기반
        base_confidence = min(len(relevant_truths) / 10.0, 1.0) * 50  # 최대 50점
        
        # 중요도 기반 신뢰도
        avg_importance = sum(truth.importance_score for truth in relevant_truths) / len(relevant_truths)
        importance_confidence = (avg_importance / 100.0) * 30  # 최대 30점
        
        # 패턴 명확도 기반 신뢰도
        pattern_clarity = max(success_ratio, failure_ratio) * 20  # 최대 20점
        
        total_confidence = base_confidence + importance_confidence + pattern_clarity
        return min(total_confidence, 100.0)
    
    def _generate_judgment_recommendations(self, judgment: str, 
                                         success_truths: List[MemoryEntry],
                                         failure_truths: List[MemoryEntry],
                                         situation: Dict[str, Any]) -> List[str]:
        """판단 기반 권장사항 생성"""
        recommendations = []
        
        if judgment == "success_likely":
            recommendations.append("성공 가능성이 높으므로 적극적으로 진행하세요")
            if success_truths:
                top_success = success_truths[0]
                recommendations.append(f"'{top_success.content[:50]}...' 패턴을 참고하세요")
        
        elif judgment == "failure_likely":
            recommendations.append("실패 가능성이 높으므로 주의가 필요합니다")
            if failure_truths:
                top_failure = failure_truths[0]
                recommendations.append(f"'{top_failure.content[:50]}...' 패턴을 피하세요")
        
        elif judgment == "success_possible":
            recommendations.append("성공 가능성이 있으므로 신중하게 진행하세요")
            recommendations.append("더 많은 Truth Memory를 수집하여 판단을 정교화하세요")
        
        elif judgment == "failure_possible":
            recommendations.append("실패 가능성이 있으므로 대안을 고려하세요")
            recommendations.append("더 많은 Truth Memory를 수집하여 판단을 정교화하세요")
        
        else:  # uncertain
            recommendations.append("판단이 불확실하므로 더 많은 정보를 수집하세요")
            recommendations.append("관련 Truth Memory를 더 많이 생성하세요")
        
        return recommendations
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_judgment_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """판단 이력 조회"""
        try:
            # 최근 판단 관련 기억들 조회
            judgment_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.type == 'judgment',
                    MemoryEntry.memory_level.in_(['medium', 'truth'])
                )
            ).order_by(desc(MemoryEntry.created_at)).limit(limit).all()
            
            history = []
            for memory in judgment_memories:
                history.append({
                    "id": memory.id,
                    "content": memory.content,
                    "context": memory.context,
                    "level": memory.memory_level,
                    "importance": memory.importance_score,
                    "created_at": memory.created_at.isoformat(),
                    "tags": memory.tags
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Failed to get judgment history: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def record_judgment(self, situation: Dict[str, Any], 
                       judgment_result: Dict[str, Any]) -> MemoryEntry:
        """판단 결과 기록"""
        try:
            judgment_data = {
                "type": "judgment",
                "context": situation.get('context', 'Truth Memory 기반 판단'),
                "content": f"판단: {judgment_result['judgment']}, 신뢰도: {judgment_result['confidence']:.1f}%, 이유: {judgment_result['reason']}",
                "source": "truth_judgment_service",
                "tags": ["judgment", "truth_based", judgment_result['judgment']],
                "importance_score": int(judgment_result['confidence']),
                "memory_level": "medium",  # 판단은 중기 기억으로 시작
                "raw_data": {
                    "situation": situation,
                    "judgment_result": judgment_result,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
            
            # 판단 기억 저장
            from ..services.memory_service import MemoryService
            memory_service = MemoryService(self.db)
            memory_entry = memory_service.save_memory(judgment_data)
            
            logger.info(f"Judgment recorded: {judgment_result['judgment']} (confidence: {judgment_result['confidence']:.1f}%)")
            
            return memory_entry
            
        except Exception as e:
            logger.error(f"Failed to record judgment: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_truth_statistics(self) -> Dict[str, Any]:
        """Truth Memory 통계"""
        try:
            # 전체 Truth Memory 수
            total_truths = self.db.query(MemoryEntry).filter(
                MemoryEntry.memory_level == 'truth'
            ).count()
            
            # 타입별 분포
            type_distribution = self.db.query(
                MemoryEntry.type,
                func.count(MemoryEntry.id).label('count')
            ).filter(
                MemoryEntry.memory_level == 'truth'
            ).group_by(MemoryEntry.type).all()
            
            # 중요도 분포
            high_importance = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.importance_score >= 80
                )
            ).count()
            
            medium_importance = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.importance_score >= 50,
                    MemoryEntry.importance_score < 80
                )
            ).count()
            
            low_importance = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'truth',
                    MemoryEntry.importance_score < 50
                )
            ).count()
            
            return {
                "total_truth_memories": total_truths,
                "type_distribution": {t.type: t.count for t in type_distribution},
                "importance_distribution": {
                    "high": high_importance,
                    "medium": medium_importance,
                    "low": low_importance
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get truth statistics: {e}")
            raise 