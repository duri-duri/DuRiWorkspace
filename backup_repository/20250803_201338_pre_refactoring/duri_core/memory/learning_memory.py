"""
DuRi의 학습 기억 시스템

이 모듈은 DuRi의 학습 과정에서 발생하는 기억을 관리합니다.
5단계 학습 루프의 각 단계별 기억을 저장하고 조회합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from .memory_sync import MemorySync, MemoryType, ExperienceSource, get_memory_sync
from enum import Enum

logger = logging.getLogger(__name__)


class LearningStage(Enum):
    """학습 단계"""
    IMITATION = "imitation"  # 모방
    PRACTICE = "practice"  # 반복
    FEEDBACK = "feedback"  # 피드백
    CHALLENGE = "challenge"  # 도전
    IMPROVEMENT = "improvement"  # 개선


class LearningMemory:
    """
    DuRi의 학습 기억 시스템
    
    5단계 학습 루프의 각 단계별 기억을 관리합니다.
    """
    
    def __init__(self):
        """LearningMemory 초기화"""
        self.memory_sync = get_memory_sync()
        logger.info("LearningMemory 초기화 완료")
    
    def store_imitation_memory(self, strategy_id: str, reference_strategy_id: str,
                              imitation_success: bool, similarity_score: float,
                              imitation_details: Dict[str, Any]) -> str:
        """
        모방 기억 저장
        
        Args:
            strategy_id: 전략 ID
            reference_strategy_id: 참조 전략 ID
            imitation_success: 모방 성공 여부
            similarity_score: 유사도 점수
            imitation_details: 모방 상세 정보
            
        Returns:
            str: 저장된 기억의 ID
        """
        try:
            content = {
                "strategy_id": strategy_id,
                "reference_strategy_id": reference_strategy_id,
                "imitation_success": imitation_success,
                "similarity_score": similarity_score,
                "imitation_details": imitation_details,
                "stage": LearningStage.IMITATION.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if imitation_success:
                confidence = min(0.5 + (similarity_score * 0.5), 1.0)
            else:
                confidence = max(0.5 - (similarity_score * 0.3), 0.1)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=["learning", "imitation", "strategy"],
                metadata={"stage": LearningStage.IMITATION.value, "strategy_id": strategy_id}
            )
            
            logger.info(f"모방 기억 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"모방 기억 저장 실패: {e}")
            raise
    
    def store_practice_memory(self, strategy_id: str, practice_count: int,
                            practice_success: bool, performance_improvement: float,
                            practice_details: Dict[str, Any]) -> str:
        """
        반복 기억 저장
        
        Args:
            strategy_id: 전략 ID
            practice_count: 반복 횟수
            practice_success: 반복 성공 여부
            performance_improvement: 성능 개선도
            practice_details: 반복 상세 정보
            
        Returns:
            str: 저장된 기억의 ID
        """
        try:
            content = {
                "strategy_id": strategy_id,
                "practice_count": practice_count,
                "practice_success": practice_success,
                "performance_improvement": performance_improvement,
                "practice_details": practice_details,
                "stage": LearningStage.PRACTICE.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if practice_success:
                confidence = min(0.5 + (performance_improvement * 0.5), 1.0)
            else:
                confidence = max(0.5 - (performance_improvement * 0.3), 0.1)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=["learning", "practice", "strategy"],
                metadata={"stage": LearningStage.PRACTICE.value, "strategy_id": strategy_id}
            )
            
            logger.info(f"반복 기억 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"반복 기억 저장 실패: {e}")
            raise
    
    def store_feedback_memory(self, strategy_id: str, feedback_data: Dict[str, Any],
                            feedback_quality: float, feedback_source: str,
                            feedback_analysis: Dict[str, Any]) -> str:
        """
        피드백 기억 저장
        
        Args:
            strategy_id: 전략 ID
            feedback_data: 피드백 데이터
            feedback_quality: 피드백 품질
            feedback_source: 피드백 출처
            feedback_analysis: 피드백 분석 결과
            
        Returns:
            str: 저장된 기억의 ID
        """
        try:
            content = {
                "strategy_id": strategy_id,
                "feedback_data": feedback_data,
                "feedback_quality": feedback_quality,
                "feedback_source": feedback_source,
                "feedback_analysis": feedback_analysis,
                "stage": LearningStage.FEEDBACK.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = min(0.5 + (feedback_quality * 0.5), 1.0)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=["learning", "feedback", "strategy"],
                metadata={"stage": LearningStage.FEEDBACK.value, "strategy_id": strategy_id}
            )
            
            logger.info(f"피드백 기억 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"피드백 기억 저장 실패: {e}")
            raise
    
    def store_challenge_memory(self, strategy_id: str, challenge_type: str,
                             challenge_success: bool, difficulty_level: float,
                             challenge_outcome: Dict[str, Any]) -> str:
        """
        도전 기억 저장
        
        Args:
            strategy_id: 전략 ID
            challenge_type: 도전 유형
            challenge_success: 도전 성공 여부
            difficulty_level: 난이도
            challenge_outcome: 도전 결과
            
        Returns:
            str: 저장된 기억의 ID
        """
        try:
            content = {
                "strategy_id": strategy_id,
                "challenge_type": challenge_type,
                "challenge_success": challenge_success,
                "difficulty_level": difficulty_level,
                "challenge_outcome": challenge_outcome,
                "stage": LearningStage.CHALLENGE.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = 0.5
            if challenge_success:
                confidence = min(0.5 + (difficulty_level * 0.5), 1.0)
            else:
                confidence = max(0.5 - (difficulty_level * 0.3), 0.1)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=["learning", "challenge", "strategy"],
                metadata={"stage": LearningStage.CHALLENGE.value, "strategy_id": strategy_id}
            )
            
            logger.info(f"도전 기억 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"도전 기억 저장 실패: {e}")
            raise
    
    def store_improvement_memory(self, old_strategy_id: str, new_strategy_id: str,
                               improvement_score: float, improvement_type: str,
                               improvement_details: Dict[str, Any]) -> str:
        """
        개선 기억 저장
        
        Args:
            old_strategy_id: 기존 전략 ID
            new_strategy_id: 새로운 전략 ID
            improvement_score: 개선 점수
            improvement_type: 개선 유형
            improvement_details: 개선 상세 정보
            
        Returns:
            str: 저장된 기억의 ID
        """
        try:
            content = {
                "old_strategy_id": old_strategy_id,
                "new_strategy_id": new_strategy_id,
                "improvement_score": improvement_score,
                "improvement_type": improvement_type,
                "improvement_details": improvement_details,
                "stage": LearningStage.IMPROVEMENT.value,
                "timestamp": datetime.now().isoformat()
            }
            
            # 신뢰도 계산
            confidence = min(0.5 + (improvement_score * 0.5), 1.0)
            
            memory_id = self.memory_sync.store_experience(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                source=ExperienceSource.REALITY,
                content=content,
                confidence=confidence,
                tags=["learning", "improvement", "strategy"],
                metadata={"stage": LearningStage.IMPROVEMENT.value, "strategy_id": new_strategy_id}
            )
            
            logger.info(f"개선 기억 저장 완료: {memory_id}")
            return memory_id
            
        except Exception as e:
            logger.error(f"개선 기억 저장 실패: {e}")
            raise
    
    def get_learning_progress(self, strategy_id: str) -> Dict[str, Any]:
        """
        학습 진행 상황 조회
        
        Args:
            strategy_id: 전략 ID
            
        Returns:
            Dict[str, Any]: 학습 진행 상황
        """
        try:
            experiences = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                limit=1000
            )
            
            # 전략별 필터링
            strategy_experiences = []
            for exp in experiences:
                content = exp.content
                if content.get("strategy_id") == strategy_id:
                    strategy_experiences.append(exp)
            
            # 단계별 진행 상황 분석
            progress = {
                "strategy_id": strategy_id,
                "stages": {},
                "overall_progress": 0.0,
                "total_experiences": len(strategy_experiences)
            }
            
            for stage in LearningStage:
                stage_experiences = [exp for exp in strategy_experiences 
                                   if exp.content.get("stage") == stage.value]
                
                if stage_experiences:
                    avg_confidence = sum(exp.confidence for exp in stage_experiences) / len(stage_experiences)
                    success_rate = len([exp for exp in stage_experiences 
                                      if exp.content.get("success", False)]) / len(stage_experiences)
                    
                    progress["stages"][stage.value] = {
                        "count": len(stage_experiences),
                        "avg_confidence": avg_confidence,
                        "success_rate": success_rate,
                        "last_experience": max(exp.timestamp for exp in stage_experiences).isoformat()
                    }
                else:
                    progress["stages"][stage.value] = {
                        "count": 0,
                        "avg_confidence": 0.0,
                        "success_rate": 0.0,
                        "last_experience": None
                    }
            
            # 전체 진행도 계산
            completed_stages = len([stage for stage in progress["stages"].values() 
                                  if stage["count"] > 0])
            progress["overall_progress"] = (completed_stages / len(LearningStage)) * 100
            
            return progress
            
        except Exception as e:
            logger.error(f"학습 진행 상황 조회 실패: {e}")
            return {"error": str(e)}
    
    def get_learning_patterns(self, days: int = 30) -> Dict[str, Any]:
        """
        학습 패턴 분석
        
        Args:
            days: 분석할 기간 (일)
            
        Returns:
            Dict[str, Any]: 학습 패턴 분석 결과
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            
            experiences = self.memory_sync.retrieve_experiences(
                memory_type=MemoryType.LEARNING_EXPERIENCE,
                limit=10000
            )
            
            # 기간 필터링
            recent_experiences = [exp for exp in experiences 
                                if exp.timestamp >= cutoff_date]
            
            patterns = {
                "total_experiences": len(recent_experiences),
                "stage_distribution": {},
                "success_patterns": {},
                "confidence_trends": {},
                "strategy_popularity": {}
            }
            
            # 단계별 분포
            for stage in LearningStage:
                stage_experiences = [exp for exp in recent_experiences 
                                   if exp.content.get("stage") == stage.value]
                patterns["stage_distribution"][stage.value] = len(stage_experiences)
            
            # 성공 패턴
            for stage in LearningStage:
                stage_experiences = [exp for exp in recent_experiences 
                                   if exp.content.get("stage") == stage.value]
                if stage_experiences:
                    success_count = len([exp for exp in stage_experiences 
                                       if exp.content.get("success", False)])
                    patterns["success_patterns"][stage.value] = {
                        "total": len(stage_experiences),
                        "success": success_count,
                        "success_rate": success_count / len(stage_experiences)
                    }
            
            # 신뢰도 트렌드
            for stage in LearningStage:
                stage_experiences = [exp for exp in recent_experiences 
                                   if exp.content.get("stage") == stage.value]
                if stage_experiences:
                    avg_confidence = sum(exp.confidence for exp in stage_experiences) / len(stage_experiences)
                    patterns["confidence_trends"][stage.value] = avg_confidence
            
            # 전략 인기도
            strategy_counts = {}
            for exp in recent_experiences:
                strategy_id = exp.content.get("strategy_id")
                if strategy_id:
                    strategy_counts[strategy_id] = strategy_counts.get(strategy_id, 0) + 1
            
            patterns["strategy_popularity"] = dict(sorted(strategy_counts.items(), 
                                                        key=lambda x: x[1], reverse=True)[:10])
            
            return patterns
            
        except Exception as e:
            logger.error(f"학습 패턴 분석 실패: {e}")
            return {"error": str(e)}
    
    def get_learning_recommendations(self, strategy_id: str = None) -> List[Dict[str, Any]]:
        """
        학습 추천사항 생성
        
        Args:
            strategy_id: 특정 전략 ID (선택사항)
            
        Returns:
            List[Dict[str, Any]]: 추천사항 목록
        """
        try:
            recommendations = []
            
            # 학습 진행 상황 분석
            if strategy_id:
                progress = self.get_learning_progress(strategy_id)
                
                for stage_name, stage_data in progress.get("stages", {}).items():
                    if stage_data["count"] == 0:
                        recommendations.append({
                            "type": "missing_stage",
                            "stage": stage_name,
                            "message": f"{stage_name} 단계 학습이 필요합니다.",
                            "priority": "high"
                        })
                    elif stage_data["success_rate"] < 0.5:
                        recommendations.append({
                            "type": "low_success_rate",
                            "stage": stage_name,
                            "message": f"{stage_name} 단계의 성공률이 낮습니다. 추가 연습이 필요합니다.",
                            "priority": "medium"
                        })
            
            # 패턴 기반 추천
            patterns = self.get_learning_patterns(days=7)
            
            if patterns.get("stage_distribution"):
                most_active_stage = max(patterns["stage_distribution"].items(), 
                                      key=lambda x: x[1])[0]
                least_active_stage = min(patterns["stage_distribution"].items(), 
                                       key=lambda x: x[1])[0]
                
                if patterns["stage_distribution"][least_active_stage] == 0:
                    recommendations.append({
                        "type": "inactive_stage",
                        "stage": least_active_stage,
                        "message": f"{least_active_stage} 단계가 비활성화되어 있습니다.",
                        "priority": "medium"
                    })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"학습 추천사항 생성 실패: {e}")
            return []


# 싱글톤 인스턴스
_learning_memory_instance = None

def get_learning_memory() -> LearningMemory:
    """LearningMemory 싱글톤 인스턴스 반환"""
    global _learning_memory_instance
    if _learning_memory_instance is None:
        _learning_memory_instance = LearningMemory()
    return _learning_memory_instance 