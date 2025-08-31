"""
DuRi Memory System - Memory Service
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc, func, text
from collections import Counter

from ..models.memory import MemoryEntry
from ..utils.db_retry import retry_on_db_error
from .pattern_detection_service import PatternDetectionService
from .learning_analysis_service import LearningAnalysisService
from .truth_judgment_service import TruthJudgmentService
from .event_trigger_service import event_trigger_service

logger = logging.getLogger(__name__)

class MemoryService:
    """DuRi Memory System의 핵심 서비스 클래스"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.pattern_detector = PatternDetectionService(db_session)
        self.learning_analyzer = LearningAnalysisService(db_session)
        self.truth_judgment = TruthJudgmentService(db_session)
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def save_memory(self, memory_data: Dict[str, Any]) -> MemoryEntry:
        """기억 저장 (기본적으로 단기 기억으로 저장)"""
        try:
            # 기본값 설정 - 모든 기억은 단기 기억으로 시작
            memory_data.setdefault('memory_level', 'short')
            memory_data.setdefault('importance_score', 50)
            memory_data.setdefault('promotion_count', 0)
            
            # 단기 기억인 경우 만료 시간 설정 (24시간)
            if memory_data.get('memory_level') == 'short':
                memory_data['expires_at'] = datetime.utcnow() + timedelta(hours=24)
            
            memory_entry = MemoryEntry.from_dict(memory_data)
            self.db.add(memory_entry)
            self.db.commit()
            self.db.refresh(memory_entry)
            
            # 이벤트 트리거 확인
            event_trigger_service.check_triggers(
                memory_type=memory_entry.type,
                memory_id=memory_entry.id,
                importance_score=memory_entry.importance_score
            )
            
            logger.info(f"Memory saved: ID={memory_entry.id}, Level={memory_entry.memory_level}, Expires={memory_entry.expires_at}")
            
            # 실시간 동기화 알림 (비동기)
            try:
                import asyncio
                from .realtime_sync_service import realtime_sync_service
                
                # 메모리 데이터 준비
                sync_data = {
                    "id": memory_entry.id,
                    "type": memory_entry.type,
                    "content": memory_entry.content,
                    "importance_score": memory_entry.importance_score,
                    "memory_level": memory_entry.memory_level,
                    "created_at": memory_entry.created_at.isoformat()
                }
                
                # 비동기로 알림 전송
                asyncio.create_task(realtime_sync_service.notify_memory_created(sync_data))
                
            except Exception as sync_error:
                logger.warning(f"실시간 동기화 알림 실패: {sync_error}")
            
            return memory_entry
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to save memory: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def query_memories(self, 
                      memory_type: Optional[str] = None,
                      source: Optional[str] = None,
                      context: Optional[str] = None,
                      tags: Optional[List[str]] = None,
                      min_importance: Optional[int] = None,
                      memory_level: Optional[str] = None,
                      limit: int = 100,
                      offset: int = 0) -> List[MemoryEntry]:
        """기억을 조회"""
        try:
            query = self.db.query(MemoryEntry)
            
            # 필터 조건 적용
            if memory_type:
                query = query.filter(MemoryEntry.type == memory_type)
            
            if source:
                query = query.filter(MemoryEntry.source == source)
            
            if context:
                query = query.filter(MemoryEntry.context.contains(context))
            
            if tags:
                # 태그 중 하나라도 포함된 경우
                tag_conditions = [MemoryEntry.tags.contains([tag]) for tag in tags]
                query = query.filter(or_(*tag_conditions))
            
            if min_importance is not None:
                query = query.filter(MemoryEntry.importance_score >= min_importance)
            
            if memory_level:
                query = query.filter(MemoryEntry.memory_level == memory_level)
            
            # 만료되지 않은 기억만 조회 (단기 기억의 경우)
            query = query.filter(
                or_(
                    MemoryEntry.memory_level != 'short',
                    and_(
                        MemoryEntry.memory_level == 'short',
                        or_(
                            MemoryEntry.expires_at.is_(None),
                            MemoryEntry.expires_at > datetime.utcnow()
                        )
                    )
                )
            )
            
            # 최신순으로 정렬하고 제한
            query = query.order_by(desc(MemoryEntry.created_at))
            query = query.offset(offset).limit(limit)
            
            print("[SQL][query_memories]", query.statement)
            memories = query.all()
            logger.info(f"Retrieved {len(memories)} memories")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to query memories: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_memory_by_id(self, memory_id: int) -> Optional[MemoryEntry]:
        """ID로 특정 기억 조회"""
        try:
            memory = self.db.query(MemoryEntry).filter(MemoryEntry.id == memory_id).first()
            return memory
        except Exception as e:
            logger.error(f"Failed to get memory by ID {memory_id}: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def update_memory(self, memory_id: int, update_data: Dict[str, Any]) -> Optional[MemoryEntry]:
        """기억 업데이트"""
        try:
            memory = self.get_memory_by_id(memory_id)
            if not memory:
                return None
            
            # 업데이트할 필드들
            for key, value in update_data.items():
                if hasattr(memory, key):
                    setattr(memory, key, value)
            
            memory.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(memory)
            
            logger.info(f"Memory updated: ID {memory_id}")
            return memory
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update memory {memory_id}: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def delete_memory(self, memory_id: int) -> bool:
        """기억 삭제"""
        try:
            memory = self.get_memory_by_id(memory_id)
            if not memory:
                return False
            
            self.db.delete(memory)
            self.db.commit()
            
            logger.info(f"Memory deleted: ID {memory_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete memory {memory_id}: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_memory_stats(self) -> Dict[str, Any]:
        """Memory 시스템 통계 조회"""
        try:
            total_count = self.db.query(func.count(MemoryEntry.id)).scalar()
            
            # 타입별 통계
            type_stats = self.db.query(
                MemoryEntry.type,
                func.count(MemoryEntry.id).label('count')
            ).group_by(MemoryEntry.type).all()
            
            # 소스별 통계
            source_stats = self.db.query(
                MemoryEntry.source,
                func.count(MemoryEntry.id).label('count')
            ).group_by(MemoryEntry.source).all()
            
            # 최근 24시간 통계
            yesterday = datetime.utcnow() - timedelta(days=1)
            recent_count = self.db.query(func.count(MemoryEntry.id)).filter(
                MemoryEntry.created_at >= yesterday
            ).scalar()
            
            return {
                'total_memories': total_count,
                'recent_24h': recent_count,
                'by_type': {stat.type: stat.count for stat in type_stats},
                'by_source': {stat.source: stat.count for stat in source_stats}
            }
            
        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def search_memories(self, search_term: str, limit: int = 50) -> List[MemoryEntry]:
        """텍스트 검색"""
        try:
            query = self.db.query(MemoryEntry).filter(
                or_(
                    MemoryEntry.content.contains(search_term),
                    MemoryEntry.context.contains(search_term)
                )
            ).order_by(desc(MemoryEntry.importance_score), desc(MemoryEntry.created_at))
            
            memories = query.limit(limit).all()
            logger.info(f"Search '{search_term}' returned {len(memories)} results")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to search memories: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def cleanup_expired_memories(self) -> int:
        """만료된 단기 기억 정리"""
        try:
            deleted_count = self.db.query(MemoryEntry).filter(
                and_(
                    MemoryEntry.memory_level == 'short',
                    MemoryEntry.expires_at.isnot(None),
                    MemoryEntry.expires_at < datetime.utcnow()
                )
            ).delete()
            
            self.db.commit()
            logger.info(f"Cleaned up {deleted_count} expired short-term memories")
            return deleted_count
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to cleanup expired memories: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_memories_by_level(self, memory_level: str, limit: int = 100) -> List[MemoryEntry]:
        """특정 레벨의 기억 조회"""
        try:
            query = self.db.query(MemoryEntry).filter(
                MemoryEntry.memory_level == memory_level
            ).order_by(desc(MemoryEntry.importance_score), desc(MemoryEntry.created_at))
            
            memories = query.limit(limit).all()
            logger.info(f"Retrieved {len(memories)} {memory_level}-level memories")
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get memories by level {memory_level}: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def promote_memory_to_medium(self, memory_id: int) -> Dict[str, Any]:
        """단기 기억을 중기 기억으로 승격"""
        try:
            memory = self.get_memory_by_id(memory_id)
            if not memory:
                return {"success": False, "reason": "Memory not found"}
            
            if memory.memory_level != 'short':
                return {"success": False, "reason": f"Memory is already {memory.memory_level} level"}
            
            # 패턴 감지를 통한 승격 평가
            promotion_evaluation = self.pattern_detector.should_promote_to_medium(memory_id)
            
            if promotion_evaluation["should_promote"]:
                # 승격 실행
                memory.memory_level = 'medium'
                memory.promotion_count += 1
                memory.expires_at = None  # 중기 기억은 만료되지 않음
                memory.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(memory)
                
                logger.info(f"Memory {memory_id} promoted to medium level. Score: {promotion_evaluation['promotion_score']}")
                
                return {
                    "success": True,
                    "memory": memory.to_dict(),
                    "promotion_score": promotion_evaluation["promotion_score"],
                    "promotion_reasons": promotion_evaluation["promotion_reasons"]
                }
            else:
                return {
                    "success": False,
                    "reason": "Promotion criteria not met",
                    "promotion_score": promotion_evaluation["promotion_score"],
                    "promotion_reasons": promotion_evaluation["promotion_reasons"]
                }
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to promote memory to medium: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def promote_memory_to_truth(self, memory_id: int) -> Dict[str, Any]:
        """중기 기억을 장기 기억(Truth)으로 승격"""
        try:
            memory = self.get_memory_by_id(memory_id)
            if not memory:
                return {"success": False, "reason": "Memory not found"}
            
            if memory.memory_level != 'medium':
                return {"success": False, "reason": f"Memory is {memory.memory_level} level, must be medium to promote to truth"}
            
            # Truth 승격 평가
            promotion_evaluation = self.pattern_detector.should_promote_to_truth(memory_id)
            
            if promotion_evaluation["should_promote"]:
                # 승격 실행
                memory.memory_level = 'truth'
                memory.promotion_count += 1
                memory.updated_at = datetime.utcnow()
                
                self.db.commit()
                self.db.refresh(memory)
                
                logger.info(f"Memory {memory_id} promoted to truth level. Score: {promotion_evaluation['promotion_score']}")
                
                return {
                    "success": True,
                    "memory": memory.to_dict(),
                    "promotion_score": promotion_evaluation["promotion_score"],
                    "promotion_reasons": promotion_evaluation["promotion_reasons"]
                }
            else:
                return {
                    "success": False,
                    "reason": "Truth promotion criteria not met",
                    "promotion_score": promotion_evaluation["promotion_score"],
                    "promotion_reasons": promotion_evaluation["promotion_reasons"]
                }
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to promote memory to truth: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def auto_promote_candidates(self) -> Dict[str, Any]:
        """자동 승격 후보 기억들 처리"""
        try:
            # 단기 기억 중 승격 후보 조회
            short_memories = self.get_memories_by_level('short', limit=100)
            
            promotion_results = {
                "short_to_medium": [],
                "medium_to_truth": [],
                "total_processed": 0
            }
            
            # 단기 → 중기 승격 시도
            for memory in short_memories:
                promotion_result = self.promote_memory_to_medium(memory.id)
                if promotion_result["success"]:
                    promotion_results["short_to_medium"].append({
                        "memory_id": memory.id,
                        "promotion_score": promotion_result["promotion_score"],
                        "reasons": promotion_result["promotion_reasons"]
                    })
                promotion_results["total_processed"] += 1
            
            # 중기 → Truth 승격 시도
            medium_memories = self.get_memories_by_level('medium', limit=50)
            for memory in medium_memories:
                promotion_result = self.promote_memory_to_truth(memory.id)
                if promotion_result["success"]:
                    promotion_results["medium_to_truth"].append({
                        "memory_id": memory.id,
                        "promotion_score": promotion_result["promotion_score"],
                        "reasons": promotion_result["promotion_reasons"]
                    })
                promotion_results["total_processed"] += 1
            
            logger.info(f"Auto promotion completed: {len(promotion_results['short_to_medium'])} to medium, {len(promotion_results['medium_to_truth'])} to truth")
            
            return promotion_results
            
        except Exception as e:
            logger.error(f"Failed to auto promote candidates: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def analyze_memory_patterns(self, memory_id: int) -> Dict[str, Any]:
        """기억의 패턴 분석"""
        try:
            memory = self.get_memory_by_id(memory_id)
            if not memory:
                return {"error": "Memory not found"}
            
            analysis = {
                "memory_id": memory_id,
                "current_level": memory.memory_level,
                "repetition_patterns": self.pattern_detector.detect_repetition_patterns(memory_id),
                "emotional_intensity": self.pattern_detector.analyze_emotional_intensity(memory_id),
                "user_feedback": self.pattern_detector.detect_user_feedback_patterns(memory_id)
            }
            
            # 중기 기억인 경우 일관성 분석 추가
            if memory.memory_level == 'medium':
                analysis["consistency"] = self.pattern_detector.analyze_medium_memory_consistency(memory_id)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze memory patterns: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def analyze_learning_patterns(self, memory_id: int) -> Dict[str, Any]:
        """중기 기억의 학습 패턴 분석"""
        try:
            return self.learning_analyzer.analyze_learning_patterns(memory_id)
        except Exception as e:
            logger.error(f"Failed to analyze learning patterns: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def compare_memories(self, memory_id_1: int, memory_id_2: int) -> Dict[str, Any]:
        """두 기억 비교 분석"""
        try:
            return self.learning_analyzer.compare_memories(memory_id_1, memory_id_2)
        except Exception as e:
            logger.error(f"Failed to compare memories: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def generate_learning_report(self, memory_id: int) -> Dict[str, Any]:
        """학습 리포트 생성"""
        try:
            return self.learning_analyzer.generate_learning_report(memory_id)
        except Exception as e:
            logger.error(f"Failed to generate learning report: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_learning_insights(self, memory_level: str = 'medium', limit: int = 10) -> Dict[str, Any]:
        """학습 인사이트 조회"""
        try:
            # 특정 레벨의 기억들 조회
            memories = self.get_memories_by_level(memory_level, limit)
            
            insights = {
                "memory_level": memory_level,
                "total_memories": len(memories),
                "success_count": 0,
                "failure_count": 0,
                "learning_patterns": [],
                "recommendations": []
            }
            
            # 성공/실패 패턴 분석
            for memory in memories:
                if self.learning_analyzer._is_success_memory(memory):
                    insights["success_count"] += 1
                elif self.learning_analyzer._is_failure_memory(memory):
                    insights["failure_count"] += 1
            
            # 학습 패턴 생성
            if insights["success_count"] > insights["failure_count"]:
                insights["learning_patterns"].append("성공 패턴이 우세합니다")
            elif insights["failure_count"] > insights["success_count"]:
                insights["learning_patterns"].append("실패 패턴이 우세합니다")
            else:
                insights["learning_patterns"].append("성공과 실패 패턴이 균형을 이룹니다")
            
            # 권장사항 생성
            if insights["success_count"] > 0:
                insights["recommendations"].append("성공 패턴을 Truth Memory로 승격을 고려하세요")
            if insights["failure_count"] > 0:
                insights["recommendations"].append("실패 패턴을 분석하여 개선점을 찾아보세요")
            
            return insights
            
        except Exception as e:
            logger.error(f"Failed to get learning insights: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_truth_memories(self, context: Optional[str] = None, 
                          memory_type: Optional[str] = None,
                          limit: int = 50) -> List[MemoryEntry]:
        """Truth Memory 조회"""
        try:
            return self.truth_judgment.get_truth_memories(context, memory_type, limit)
        except Exception as e:
            logger.error(f"Failed to get truth memories: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def make_truth_judgment(self, situation: Dict[str, Any]) -> Dict[str, Any]:
        """Truth Memory 기반 판단 수행"""
        try:
            # 판단 수행
            judgment_result = self.truth_judgment.make_judgment(situation)
            
            # 판단 결과 기록
            if judgment_result["confidence"] > 0:
                self.truth_judgment.record_judgment(situation, judgment_result)
            
            return judgment_result
            
        except Exception as e:
            logger.error(f"Failed to make truth judgment: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_judgment_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """판단 이력 조회"""
        try:
            return self.truth_judgment.get_judgment_history(limit)
        except Exception as e:
            logger.error(f"Failed to get judgment history: {e}")
            raise
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_truth_statistics(self) -> Dict[str, Any]:
        """Truth Memory 통계"""
        try:
            return self.truth_judgment.get_truth_statistics()
        except Exception as e:
            logger.error(f"Failed to get truth statistics: {e}")
            raise 

    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def auto_cleanup_truth_memories(self, max_age_days: int = 30, min_success_ratio: float = 0.5) -> Dict[str, Any]:
        """오래되었거나 신뢰도가 낮은 Truth Memory 자동 정화"""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        cutoff = now - timedelta(days=max_age_days)
        # 1. 오래된 Truth Memory 삭제
        old_truths = self.db.query(MemoryEntry).filter(
            MemoryEntry.memory_level == 'truth',
            MemoryEntry.created_at < cutoff
        ).all()
        deleted_ids = [m.id for m in old_truths]
        for m in old_truths:
            self.db.delete(m)
        # 2. 신뢰도(성공/실패 패턴) 낮은 Truth Memory 삭제
        # (실패 패턴이 min_success_ratio 미만인 경우)
        # TODO: 성공/실패 패턴 판별 함수 활용
        self.db.commit()
        return {
            "deleted_old_truths": deleted_ids,
            "count": len(deleted_ids)
        }

    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def auto_evolve_truth_memories(self) -> Dict[str, Any]:
        """새로운 성공/실패 패턴에 따라 Truth Memory 자동 진화"""
        try:
            from .evolution_service import EvolutionService
            evolution_service = EvolutionService(self.db)
            return evolution_service.auto_evolve_truth_memories()
        except Exception as e:
            logger.error(f"Truth Memory 진화 실패: {e}")
            return {"evolved": False, "error": str(e)} 

    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def meta_report(self) -> Dict[str, Any]:
        """DuRi Memory System 메타 리포트"""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)
        # 레벨별 분포
        level_counts = dict(self.db.query(MemoryEntry.memory_level, func.count(MemoryEntry.id)).group_by(MemoryEntry.memory_level).all())
        # 타입별 분포
        type_counts = dict(self.db.query(MemoryEntry.type, func.count(MemoryEntry.id)).group_by(MemoryEntry.type).all())
        # 중요도 분포
        high = self.db.query(MemoryEntry).filter(MemoryEntry.importance_score >= 80).count()
        medium = self.db.query(MemoryEntry).filter(MemoryEntry.importance_score >= 50, MemoryEntry.importance_score < 80).count()
        low = self.db.query(MemoryEntry).filter(MemoryEntry.importance_score < 50).count()
        # 최근 1주일간 진실/정화/진화 통계
        new_truths = self.db.query(MemoryEntry).filter(MemoryEntry.memory_level == 'truth', MemoryEntry.created_at >= one_week_ago).count()
        cleaned = self.db.query(MemoryEntry).filter(MemoryEntry.memory_level == 'truth', MemoryEntry.updated_at >= one_week_ago, MemoryEntry.created_at < one_week_ago).count()
        # 전체 진실/기억 수
        total_memories = self.db.query(MemoryEntry).count()
        total_truths = self.db.query(MemoryEntry).filter(MemoryEntry.memory_level == 'truth').count()
        return {
            "level_counts": level_counts,
            "type_counts": type_counts,
            "importance_distribution": {"high": high, "medium": medium, "low": low},
            "recent_new_truths": new_truths,
            "recent_cleaned_truths": cleaned,
            "total_memories": total_memories,
            "total_truths": total_truths,
            "generated_at": now.isoformat()
        }

    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_memory_count_by_type(self, memory_type: str, hours: int = 1, seconds: int = None) -> int:
        """특정 타입의 메모리 개수를 시간 범위로 조회"""
        try:
            query = self.db.query(MemoryEntry).filter(MemoryEntry.type == memory_type)
            
            if seconds:
                # N초 내
                time_threshold = datetime.utcnow() - timedelta(seconds=seconds)
            else:
                # N시간 내
                time_threshold = datetime.utcnow() - timedelta(hours=hours)
            
            query = query.filter(MemoryEntry.created_at >= time_threshold)
            return query.count()
            
        except Exception as e:
            logger.error(f"Failed to get memory count by type: {e}")
            return 0
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def get_trigger_stats(self) -> Dict[str, Any]:
        """트리거 통계 조회"""
        return event_trigger_service.get_trigger_stats()
    
    @retry_on_db_error(max_retries=3, retry_delay=1.0)
    def meta_insights(self, limit: int = 5) -> Dict[str, Any]:
        """DuRi Memory System 메타 인사이트 (최근 진화/정화/패턴 변화 등)"""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        one_week_ago = now - timedelta(days=7)
        # 최근 1주일간 진실 변화(신규/정화/진화)
        recent_truths = self.db.query(MemoryEntry).filter(MemoryEntry.memory_level == 'truth', MemoryEntry.created_at >= one_week_ago).order_by(desc(MemoryEntry.created_at)).limit(limit).all()
        recent_cleaned = self.db.query(MemoryEntry).filter(MemoryEntry.memory_level == 'truth', MemoryEntry.updated_at >= one_week_ago, MemoryEntry.created_at < one_week_ago).order_by(desc(MemoryEntry.updated_at)).limit(limit).all()
        # 최근 가장 많이 등장한 태그/패턴
        tag_counter = Counter()
        for m in self.db.query(MemoryEntry).filter(MemoryEntry.created_at >= one_week_ago).all():
            if m.tags:
                tag_counter.update(m.tags)
        top_tags = tag_counter.most_common(limit)
        return {
            "recent_new_truths": [m.to_dict() for m in recent_truths],
            "recent_cleaned_truths": [m.to_dict() for m in recent_cleaned],
            "top_tags": top_tags,
            "generated_at": now.isoformat()
        } 