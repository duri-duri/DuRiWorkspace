"""
DuRi Memory System - Pattern Detection Service
패턴 감지 및 분석을 통한 기억 승격 결정
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from collections import defaultdict, Counter

from ..models.memory import MemoryEntry
from ..utils.db_retry import retry_on_db_error

logger = logging.getLogger(__name__)

class PatternDetectionService:
    """패턴 감지 및 분석 서비스"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def detect_repetition_patterns(self, memory_id: int, time_window_hours: int = 24) -> Dict[str, Any]:
        """반복 패턴 감지"""
        try:
            # 대상 기억 조회
            target_memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not target_memory:
                return {"pattern_found": False, "reason": "Memory not found"}
            
            # 시간 윈도우 내 유사한 기억들 조회
            time_threshold = datetime.utcnow() - timedelta(hours=time_window_hours)
            
            similar_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.id != memory_id,
                    MemoryEntry.created_at >= time_threshold,
                    MemoryEntry.memory_level == 'short',
                    or_(
                        MemoryEntry.context == target_memory.context,
                        MemoryEntry.content.contains(target_memory.content[:50]),
                        MemoryEntry.type == target_memory.type
                    )
                )
            ).all()
            
            pattern_info = {
                "pattern_found": len(similar_memories) >= 2,  # 3회 이상 반복 시 패턴으로 인식
                "similar_count": len(similar_memories),
                "similar_memories": [m.id for m in similar_memories],
                "time_window_hours": time_window_hours,
                "pattern_type": "repetition"
            }
            
            if pattern_info["pattern_found"]:
                logger.info(f"Repetition pattern detected for memory {memory_id}: {len(similar_memories)} similar memories")
            
            return pattern_info
            
        except Exception as e:
            logger.error(f"Failed to detect repetition patterns: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def analyze_emotional_intensity(self, memory_id: int) -> Dict[str, Any]:
        """감정 강도 분석"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory:
                return {"intensity": 0, "reason": "Memory not found"}
            
            # 감정 강도 점수 계산
            intensity_score = 0
            
            # 1. 중요도 점수 기반 (0-100)
            intensity_score += memory.importance_score * 0.3
            
            # 2. 태그 기반 감정 분석
            if memory.tags:
                emotional_tags = ['error', 'success', 'confusion', 'frustration', 'joy', 'surprise', 'anger']
                emotional_count = sum(1 for tag in memory.tags if tag in emotional_tags)
                intensity_score += emotional_count * 20
            
            # 3. 컨텍스트 기반 감정 분석
            emotional_keywords = {
                'error': 30, 'fail': 25, 'success': 20, 'confusion': 25,
                'frustration': 30, 'joy': 15, 'surprise': 20, 'anger': 35
            }
            
            for keyword, score in emotional_keywords.items():
                if keyword in memory.context.lower() or keyword in memory.content.lower():
                    intensity_score += score
            
            # 4. 소스 기반 가중치
            if memory.source == 'user':
                intensity_score *= 1.5  # 사용자 피드백은 더 중요
            
            # 최대 100점으로 정규화
            intensity_score = min(intensity_score, 100)
            
            intensity_level = "low"
            if intensity_score >= 70:
                intensity_level = "high"
            elif intensity_score >= 40:
                intensity_level = "medium"
            
            return {
                "intensity": intensity_score,
                "intensity_level": intensity_level,
                "analysis_factors": {
                    "importance_score": memory.importance_score,
                    "emotional_tags": len([tag for tag in (memory.tags or []) if tag in ['error', 'success', 'confusion', 'frustration', 'joy', 'surprise', 'anger']]),
                    "source_weight": 1.5 if memory.source == 'user' else 1.0
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze emotional intensity: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def detect_user_feedback_patterns(self, memory_id: int) -> Dict[str, Any]:
        """사용자 피드백 패턴 감지"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory:
                return {"feedback_pattern": False, "reason": "Memory not found"}
            
            # 최근 24시간 내 사용자 소스 기억들 조회
            time_threshold = datetime.utcnow() - timedelta(hours=24)
            
            user_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.source == 'user',
                    MemoryEntry.created_at >= time_threshold,
                    MemoryEntry.memory_level == 'short'
                )
            ).all()
            
            # 피드백 패턴 분석
            feedback_keywords = ['good', 'bad', 'wrong', 'correct', 'helpful', 'useless', 'thanks', 'thank you']
            feedback_count = 0
            
            for user_memory in user_memories:
                for keyword in feedback_keywords:
                    if keyword in user_memory.content.lower():
                        feedback_count += 1
                        break
            
            has_feedback_pattern = feedback_count >= 2  # 2회 이상 피드백 시 패턴으로 인식
            
            return {
                "feedback_pattern": has_feedback_pattern,
                "feedback_count": feedback_count,
                "user_memories_count": len(user_memories),
                "time_window_hours": 24
            }
            
        except Exception as e:
            logger.error(f"Failed to detect user feedback patterns: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def should_promote_to_medium(self, memory_id: int) -> Dict[str, Any]:
        """중기 기억으로 승격 여부 결정"""
        try:
            # 1. 반복 패턴 감지
            repetition_result = self.detect_repetition_patterns(memory_id)
            
            # 2. 감정 강도 분석
            intensity_result = self.analyze_emotional_intensity(memory_id)
            
            # 3. 사용자 피드백 패턴 감지
            feedback_result = self.detect_user_feedback_patterns(memory_id)
            
            # 승격 조건 평가
            promotion_score = 0
            promotion_reasons = []
            
            # 반복 패턴 (40점)
            if repetition_result["pattern_found"]:
                promotion_score += 40
                promotion_reasons.append(f"Repetition pattern: {repetition_result['similar_count']} similar memories")
            
            # 높은 감정 강도 (30점)
            if intensity_result["intensity_level"] in ["medium", "high"]:
                promotion_score += 30
                promotion_reasons.append(f"High emotional intensity: {intensity_result['intensity']}")
            
            # 사용자 피드백 패턴 (30점)
            if feedback_result["feedback_pattern"]:
                promotion_score += 30
                promotion_reasons.append(f"User feedback pattern: {feedback_result['feedback_count']} feedbacks")
            
            # 승격 기준: 50점 이상
            should_promote = promotion_score >= 50
            
            return {
                "should_promote": should_promote,
                "promotion_score": promotion_score,
                "promotion_reasons": promotion_reasons,
                "analysis": {
                    "repetition": repetition_result,
                    "intensity": intensity_result,
                    "feedback": feedback_result
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate promotion to medium: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def analyze_medium_memory_consistency(self, memory_id: int) -> Dict[str, Any]:
        """중기 기억의 일관성 분석"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory or memory.memory_level != 'medium':
                return {"consistency": 0, "reason": "Not a medium-level memory"}
            
            # 유사한 중기 기억들 조회
            similar_medium_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.id != memory_id,
                    MemoryEntry.memory_level == 'medium',
                    or_(
                        MemoryEntry.context == memory.context,
                        MemoryEntry.type == memory.type,
                        MemoryEntry.content.contains(memory.content[:30])
                    )
                )
            ).all()
            
            # 일관성 점수 계산
            consistency_score = 0
            
            if similar_medium_memories:
                # 성공/실패 패턴 분석
                success_count = 0
                failure_count = 0
                
                for similar_memory in similar_medium_memories:
                    if 'success' in (similar_memory.tags or []) or 'success' in similar_memory.content.lower():
                        success_count += 1
                    elif 'error' in (similar_memory.tags or []) or 'fail' in similar_memory.content.lower():
                        failure_count += 1
                
                # 일관된 성공 또는 실패 패턴이 있으면 높은 점수
                if success_count >= 3 and failure_count <= 1:
                    consistency_score = 80  # 일관된 성공
                elif failure_count >= 3 and success_count <= 1:
                    consistency_score = 70  # 일관된 실패 (학습 가치)
                elif success_count + failure_count >= 5:
                    consistency_score = 60  # 충분한 데이터
                else:
                    consistency_score = 30  # 불충분한 데이터
            
            return {
                "consistency": consistency_score,
                "similar_medium_memories": len(similar_medium_memories),
                "success_count": success_count if 'success_count' in locals() else 0,
                "failure_count": failure_count if 'failure_count' in locals() else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to analyze medium memory consistency: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def should_promote_to_truth(self, memory_id: int) -> Dict[str, Any]:
        """장기 기억(Truth)으로 승격 여부 결정"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            if not memory or memory.memory_level != 'medium':
                return {"should_promote": False, "reason": "Not a medium-level memory"}
            
            # 1. 일관성 분석
            consistency_result = self.analyze_medium_memory_consistency(memory_id)
            
            # 2. 사용자 명시적 승인 확인
            user_approval = self.check_user_explicit_approval(memory_id)
            
            # 승격 조건 평가
            promotion_score = 0
            promotion_reasons = []
            
            # 높은 일관성 (60점)
            if consistency_result["consistency"] >= 70:
                promotion_score += 60
                promotion_reasons.append(f"High consistency: {consistency_result['consistency']}")
            elif consistency_result["consistency"] >= 50:
                promotion_score += 40
                promotion_reasons.append(f"Moderate consistency: {consistency_result['consistency']}")
            
            # 사용자 명시적 승인 (40점)
            if user_approval["has_approval"]:
                promotion_score += 40
                promotion_reasons.append("User explicit approval")
            
            # 승격 기준: 80점 이상
            should_promote = promotion_score >= 80
            
            return {
                "should_promote": should_promote,
                "promotion_score": promotion_score,
                "promotion_reasons": promotion_reasons,
                "analysis": {
                    "consistency": consistency_result,
                    "user_approval": user_approval
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to evaluate promotion to truth: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def check_user_explicit_approval(self, memory_id: int) -> Dict[str, Any]:
        """사용자 명시적 승인 확인"""
        try:
            # 최근 7일 내 사용자 승인 관련 기억 조회
            time_threshold = datetime.utcnow() - timedelta(days=7)
            
            approval_memories = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.source == 'user',
                    MemoryEntry.created_at >= time_threshold,
                    or_(
                        MemoryEntry.content.contains('correct'),
                        MemoryEntry.content.contains('right'),
                        MemoryEntry.content.contains('good'),
                        MemoryEntry.content.contains('approve'),
                        MemoryEntry.content.contains('confirm')
                    )
                )
            ).all()
            
            has_approval = len(approval_memories) > 0
            
            return {
                "has_approval": has_approval,
                "approval_count": len(approval_memories),
                "approval_memories": [m.id for m in approval_memories]
            }
            
        except Exception as e:
            logger.error(f"Failed to check user explicit approval: {e}")
            raise 