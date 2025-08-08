"""
DuRi의 경험 저장소

이 모듈은 DuRi의 다양한 경험을 체계적으로 저장하고 관리하는 시스템을 제공합니다.
학습, 창의성, 진화 경험을 분류하여 저장합니다.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from .memory_sync import MemorySync, MemoryType, ExperienceSource, get_memory_sync

logger = logging.getLogger(__name__)


class ExperienceStore:
    """
    DuRi의 경험 저장소
    
    다양한 유형의 경험을 체계적으로 저장하고 관리합니다.
    """
    
    def __init__(self):
        """ExperienceStore 초기화"""
        self.memory_sync = get_memory_sync()
        logger.info("ExperienceStore 초기화 완료")
    
    def store_learning_experience(self, strategy_id: str, stage: str, 
                                success: bool, performance: float,
                                feedback: Dict[str, Any], tags: List[str] = None) -> str:
        """
        학습 경험 저장
        
        Args:
            strategy_id: 전략 ID
            stage: 학습 단계 (imitation, practice, feedback, challenge, improvement)
            success: 성공 여부
            performance: 성능 점수
            feedback: 피드백 데이터
            tags: 태그들
            
        Returns:
            str: 저장된 경험의 ID
        """
        try:
            content = {
                "strategy_id": strategy_id,
                "stage": stage,
                "success": success,
                "performance": performance,
                "feedback": feedback,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if success:
                confidence = min(0.5 + (performance * 0.5), 1.0)
            else:
                confidence = max(0.5 - (performance * 0.3), 0.1)
            
            # 태그 설정
            default_tags = ["learning", stage, "strategy"]
            if tags:
                default_tags.extend(tags)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=default_tags,
                metadata={"experience_type": "learning", "strategy_id": strategy_id}
            )
            
            logger.info(f"학습 경험 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"학습 경험 저장 실패: {e}")
            raise
    
    def store_creativity_experience(self, dream_strategy_id: str, reality_strategy_id: str,
                                  dream_score: float, reality_score: float,
                                  promotion_decision: bool, tags: List[str] = None) -> str:
        """
        창의성 경험 저장
        
        Args:
            dream_strategy_id: Dream 전략 ID
            reality_strategy_id: Reality 전략 ID
            dream_score: Dream 전략 점수
            reality_score: Reality 전략 점수
            promotion_decision: 승격 결정 여부
            tags: 태그들
            
        Returns:
            str: 저장된 경험의 ID
        """
        try:
            content = {
                "dream_strategy_id": dream_strategy_id,
                "reality_strategy_id": reality_strategy_id,
                "dream_score": dream_score,
                "reality_score": reality_score,
                "promotion_decision": promotion_decision,
                "score_difference": dream_score - reality_score,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if promotion_decision:
                confidence = min(0.5 + (dream_score * 0.5), 1.0)
            else:
                confidence = max(0.5 - (reality_score * 0.3), 0.1)
            
            # 태그 설정
            default_tags = ["creativity", "dream_vs_reality", "promotion"]
            if tags:
                default_tags.extend(tags)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.CREATIVITY_EXPERIENCE,
                source=ExperienceSource.HYBRID,
                content=content,
                confidence=confidence,
                tags=default_tags,
                metadata={"experience_type": "creativity", "promotion": promotion_decision}
            )
            
            logger.info(f"창의성 경험 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"창의성 경험 저장 실패: {e}")
            raise
    
    def store_evolution_experience(self, old_strategy_id: str, new_strategy_id: str,
                                 improvement_score: float, evolution_type: str,
                                 mutation_details: Dict[str, Any], tags: List[str] = None) -> str:
        """
        진화 경험 저장
        
        Args:
            old_strategy_id: 기존 전략 ID
            new_strategy_id: 새로운 전략 ID
            improvement_score: 개선 점수
            evolution_type: 진화 유형
            mutation_details: 변이 상세 정보
            tags: 태그들
            
        Returns:
            str: 저장된 경험의 ID
        """
        try:
            content = {
                "old_strategy_id": old_strategy_id,
                "new_strategy_id": new_strategy_id,
                "improvement_score": improvement_score,
                "evolution_type": evolution_type,
                "mutation_details": mutation_details,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = min(0.5 + (improvement_score * 0.5), 1.0)
            
            # 태그 설정
            default_tags = ["evolution", evolution_type, "mutation"]
            if tags:
                default_tags.extend(tags)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.EVOLUTION_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=default_tags,
                metadata={"experience_type": "evolution", "evolution_type": evolution_type}
            )
            
            logger.info(f"진화 경험 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"진화 경험 저장 실패: {e}")
            raise
    
    def store_dream_experience(self, dream_strategy_id: str, creativity_score: float,
                             unexpected_success: bool, exploration_type: str,
                             dream_content: Dict[str, Any], tags: List[str] = None) -> str:
        """
        Dream 경험 저장
        
        Args:
            dream_strategy_id: Dream 전략 ID
            creativity_score: 창의성 점수
            unexpected_success: 예상치 못한 성공 여부
            exploration_type: 탐색 유형
            dream_content: Dream 내용
            tags: 태그들
            
        Returns:
            str: 저장된 경험의 ID
        """
        try:
            content = {
                "dream_strategy_id": dream_strategy_id,
                "creativity_score": creativity_score,
                "unexpected_success": unexpected_success,
                "exploration_type": exploration_type,
                "dream_content": dream_content,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if unexpected_success:
                confidence = min(0.5 + (creativity_score * 0.5), 1.0)
            else:
                confidence = max(0.5 - (creativity_score * 0.3), 0.1)
            
            # 태그 설정
            default_tags = ["dream", exploration_type, "creativity"]
            if unexpected_success:
                default_tags.append("eureka")
            if tags:
                default_tags.extend(tags)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.DREAM_EXPERIENCE,
                source=ExperienceSource.DREAM,
                content=content,
                confidence=confidence,
                tags=default_tags,
                metadata={"experience_type": "dream", "unexpected_success": unexpected_success}
            )
            
            logger.info(f"Dream 경험 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Dream 경험 저장 실패: {e}")
            raise
    
    def store_reality_experience(self, reality_strategy_id: str, stability_score: float,
                               execution_success: bool, performance_metrics: Dict[str, Any],
                               reality_content: Dict[str, Any], tags: List[str] = None) -> str:
        """
        Reality 경험 저장
        
        Args:
            reality_strategy_id: Reality 전략 ID
            stability_score: 안정성 점수
            execution_success: 실행 성공 여부
            performance_metrics: 성능 지표
            reality_content: Reality 내용
            tags: 태그들
            
        Returns:
            str: 저장된 경험의 ID
        """
        try:
            content = {
                "reality_strategy_id": reality_strategy_id,
                "stability_score": stability_score,
                "execution_success": execution_success,
                "performance_metrics": performance_metrics,
                "reality_content": reality_content,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if execution_success:
                confidence = min(0.5 + (stability_score * 0.5), 1.0)
            else:
                confidence = max(0.5 - (stability_score * 0.3), 0.1)
            
            # 태그 설정
            default_tags = ["reality", "stability", "execution"]
            if tags:
                default_tags.extend(tags)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.REALITY_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=default_tags,
                metadata={"experience_type": "reality", "execution_success": execution_success}
            )
            
            logger.info(f"Reality 경험 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"Reality 경험 저장 실패: {e}")
            raise
    
    def get_learning_experiences(self, strategy_id: str = None, stage: str = None,
                               limit: int = 50) -> List[Dict[str, Any]]:
        """학습 경험 조회"""
        try:
            experiences = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                limit=limit
            )
            
            # 필터링
            filtered_experiences = []
            for exp in experiences:
                content = exp.content
                
                if strategy_id and content.get("strategy_id") != strategy_id:
                    continue
                
                if stage and content.get("stage") != stage:
                    continue
                
                filtered_experiences.append({
                    "id": exp.id,
                    "content": content,
                    "confidence": exp.confidence,
                    "timestamp": exp.timestamp
                })
            
            return filtered_experiences
            
        except Exception as e:
            logger.error(f"학습 경험 조회 실패: {e}")
            return []
    
    def get_creativity_experiences(self, limit: int = 50) -> List[Dict[str, Any]]:
        """창의성 경험 조회"""
        try:
            experiences = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.CREATIVITY_EXPERIENCE,
                limit=limit
            )
            
            return [{
                "id": exp.id,
                "content": exp.content,
                "confidence": exp.confidence,
                "timestamp": exp.timestamp
            } for exp in experiences]
            
        except Exception as e:
            logger.error(f"창의성 경험 조회 실패: {e}")
            return []
    
    def get_evolution_experiences(self, evolution_type: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """진화 경험 조회"""
        try:
            experiences = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.EVOLUTION_EXPERIENCE,
                limit=limit
            )
            
            # 필터링
            filtered_experiences = []
            for exp in experiences:
                content = exp.content
                
                if evolution_type and content.get("evolution_type") != evolution_type:
                    continue
                
                filtered_experiences.append({
                    "id": exp.id,
                    "content": content,
                    "confidence": exp.confidence,
                    "timestamp": exp.timestamp
                })
            
            return filtered_experiences
            
        except Exception as e:
            logger.error(f"진화 경험 조회 실패: {e}")
            return []
    
    def get_experience_statistics(self) -> Dict[str, Any]:
        """경험 통계 정보"""
        try:
            summary = self.memory_sync.get_memory_summary()
            
            # 유형별 통계
            type_stats = {}
            for memory_type in MemoryType:
                experiences = self.memory_sync.retrieve_experiences(
                    memory_type=memory_type,
                    limit=1000
                )
                
                if experiences:
                    avg_confidence = sum(exp.confidence for exp in experiences) / len(experiences)
                    type_stats[memory_type.value] = {
                        "count": len(experiences),
                        "avg_confidence": avg_confidence,
                        "recent_count": len([exp for exp in experiences 
                                           if (datetime.now() - exp.timestamp).days < 7])
                    }
            
            return {
                "total_experiences": summary.get("total_memories", 0),
                "type_statistics": type_stats,
                "source_statistics": summary.get("memories_by_source", {}),
                "average_confidence": summary.get("average_confidence", 0.0)
            }
            
        except Exception as e:
            logger.error(f"경험 통계 조회 실패: {e}")
            return {"error": str(e)}


# 싱글톤 인스턴스
_experience_store_instance = None

def get_experience_store() -> ExperienceStore:
    """ExperienceStore 싱글톤 인스턴스 반환"""
    global _experience_store_instance
    if _experience_store_instance is None:
        _experience_store_instance = ExperienceStore()
    return _experience_store_instance 