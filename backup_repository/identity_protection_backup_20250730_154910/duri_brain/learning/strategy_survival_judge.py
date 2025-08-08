"""
DuRi의 전략 생존 판단 시스템

전략 생존 판단을 위한 핵심 로직을 구현합니다.
성과와 감정을 종합하여 전략의 지속/수정/폐기를 판단합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from duri_core.philosophy.survival_criteria import (
    get_survival_criteria_manager, 
    JudgmentAction, 
    JudgmentResult
)

logger = logging.getLogger(__name__)

class StrategyStatus(Enum):
    """전략 상태"""
    ACTIVE = "active"          # 활성
    MODIFIED = "modified"      # 수정됨
    DISCARDED = "discarded"    # 폐기됨
    PENDING = "pending"        # 판단 대기

@dataclass
class StrategyRecord:
    """전략 기록"""
    strategy_id: str
    start_date: datetime
    last_modified: datetime
    performance_history: List[float]
    emotion_history: List[str]
    modification_count: int
    status: StrategyStatus
    current_performance: float
    current_emotion: str

@dataclass
class SurvivalDecision:
    """생존 결정"""
    strategy_id: str
    action: JudgmentAction
    confidence: float
    reasoning: List[str]
    performance_score: float
    emotion_score: float
    combined_score: float
    next_evaluation_date: datetime
    recommended_action: str

class StrategySurvivalJudge:
    """
    DuRi의 전략 생존 판단 시스템
    
    전략 생존 판단을 위한 핵심 로직을 구현합니다.
    """
    
    def __init__(self):
        """StrategySurvivalJudge 초기화"""
        self.strategy_records: Dict[str, StrategyRecord] = {}
        self.survival_criteria_manager = get_survival_criteria_manager()
        self.decision_history: List[SurvivalDecision] = []
        
        logger.info("StrategySurvivalJudge 초기화 완료")
    
    def register_strategy(self, strategy_id: str, initial_performance: float = 0.0, 
                         initial_emotion: str = "neutral") -> bool:
        """
        새로운 전략을 등록합니다.
        
        Args:
            strategy_id: 전략 ID
            initial_performance: 초기 성과
            initial_emotion: 초기 감정
            
        Returns:
            bool: 등록 성공 여부
        """
        try:
            if strategy_id in self.strategy_records:
                logger.warning(f"전략 {strategy_id}가 이미 등록되어 있습니다.")
                return False
            
            strategy_record = StrategyRecord(
                strategy_id=strategy_id,
                start_date=datetime.now(),
                last_modified=datetime.now(),
                performance_history=[initial_performance],
                emotion_history=[initial_emotion],
                modification_count=0,
                status=StrategyStatus.ACTIVE,
                current_performance=initial_performance,
                current_emotion=initial_emotion
            )
            
            self.strategy_records[strategy_id] = strategy_record
            logger.info(f"전략 {strategy_id} 등록 완료")
            return True
            
        except Exception as e:
            logger.error(f"전략 등록 실패: {e}")
            return False
    
    def update_strategy_performance(self, strategy_id: str, performance: float, 
                                  emotion: str = None) -> bool:
        """
        전략 성과를 업데이트합니다.
        
        Args:
            strategy_id: 전략 ID
            performance: 새로운 성과
            emotion: 새로운 감정 (선택사항)
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            if strategy_id not in self.strategy_records:
                logger.error(f"전략 {strategy_id}가 등록되지 않았습니다.")
                return False
            
            record = self.strategy_records[strategy_id]
            record.performance_history.append(performance)
            record.current_performance = performance
            record.last_modified = datetime.now()
            
            if emotion:
                record.emotion_history.append(emotion)
                record.current_emotion = emotion
            
            logger.info(f"전략 {strategy_id} 성과 업데이트: {performance:.2f}")
            return True
            
        except Exception as e:
            logger.error(f"전략 성과 업데이트 실패: {e}")
            return False
    
    def evaluate_strategy_survival(self, strategy_id: str) -> Optional[SurvivalDecision]:
        """
        전략 생존을 판단합니다.
        
        Args:
            strategy_id: 전략 ID
            
        Returns:
            SurvivalDecision: 생존 결정
        """
        try:
            if strategy_id not in self.strategy_records:
                logger.error(f"전략 {strategy_id}가 등록되지 않았습니다.")
                return None
            
            record = self.strategy_records[strategy_id]
            
            # 전략 사용 일수 계산
            strategy_age_days = (datetime.now() - record.start_date).days
            
            # 생존 판단 실행
            judgment_result = self.survival_criteria_manager.evaluate_strategy_survival(
                performance_history=record.performance_history,
                emotion_history=record.emotion_history,
                current_performance=record.current_performance,
                current_emotion=record.current_emotion,
                strategy_age_days=strategy_age_days
            )
            
            # 권장 행동 결정
            recommended_action = self._determine_recommended_action(judgment_result, record)
            
            # 생존 결정 생성
            decision = SurvivalDecision(
                strategy_id=strategy_id,
                action=judgment_result.action,
                confidence=judgment_result.confidence,
                reasoning=judgment_result.reasoning,
                performance_score=judgment_result.performance_score,
                emotion_score=judgment_result.emotion_score,
                combined_score=judgment_result.combined_score,
                next_evaluation_date=judgment_result.next_evaluation_date,
                recommended_action=recommended_action
            )
            
            self.decision_history.append(decision)
            
            # 전략 상태 업데이트
            self._update_strategy_status(strategy_id, judgment_result.action)
            
            logger.info(f"전략 {strategy_id} 생존 판단 완료: {judgment_result.action.value}")
            return decision
            
        except Exception as e:
            logger.error(f"전략 생존 판단 실패: {e}")
            return None
    
    def _determine_recommended_action(self, judgment_result: JudgmentResult, 
                                    record: StrategyRecord) -> str:
        """권장 행동을 결정합니다."""
        if judgment_result.action == JudgmentAction.CONTINUE:
            return "전략을 현재 상태로 지속"
        elif judgment_result.action == JudgmentAction.MODIFY:
            return f"전략 수정 필요 (수정 횟수: {record.modification_count})"
        elif judgment_result.action == JudgmentAction.DISCARD:
            return "전략 폐기 및 새 전략 탐색 필요"
        else:
            return "판단 불가"
    
    def _update_strategy_status(self, strategy_id: str, action: JudgmentAction):
        """전략 상태를 업데이트합니다."""
        record = self.strategy_records[strategy_id]
        
        if action == JudgmentAction.MODIFY:
            record.status = StrategyStatus.MODIFIED
            record.modification_count += 1
            record.last_modified = datetime.now()
        elif action == JudgmentAction.DISCARD:
            record.status = StrategyStatus.DISCARDED
        elif action == JudgmentAction.CONTINUE:
            record.status = StrategyStatus.ACTIVE
    
    def get_strategy_info(self, strategy_id: str) -> Optional[Dict[str, Any]]:
        """전략 정보를 반환합니다."""
        if strategy_id not in self.strategy_records:
            return None
        
        record = self.strategy_records[strategy_id]
        strategy_age_days = (datetime.now() - record.start_date).days
        
        return {
            "strategy_id": strategy_id,
            "status": record.status.value,
            "start_date": record.start_date.isoformat(),
            "last_modified": record.last_modified.isoformat(),
            "age_days": strategy_age_days,
            "modification_count": record.modification_count,
            "current_performance": record.current_performance,
            "current_emotion": record.current_emotion,
            "performance_history_length": len(record.performance_history),
            "emotion_history_length": len(record.emotion_history),
            "average_performance": sum(record.performance_history) / len(record.performance_history) if record.performance_history else 0
        }
    
    def get_all_strategies_info(self) -> Dict[str, Any]:
        """모든 전략 정보를 반환합니다."""
        strategies_info = {}
        
        for strategy_id, record in self.strategy_records.items():
            strategies_info[strategy_id] = self.get_strategy_info(strategy_id)
        
        return strategies_info
    
    def get_survival_statistics(self) -> Dict[str, Any]:
        """생존 판단 통계를 반환합니다."""
        total_strategies = len(self.strategy_records)
        active_strategies = len([r for r in self.strategy_records.values() if r.status == StrategyStatus.ACTIVE])
        modified_strategies = len([r for r in self.strategy_records.values() if r.status == StrategyStatus.MODIFIED])
        discarded_strategies = len([r for r in self.strategy_records.values() if r.status == StrategyStatus.DISCARDED])
        
        total_decisions = len(self.decision_history)
        continue_decisions = len([d for d in self.decision_history if d.action == JudgmentAction.CONTINUE])
        modify_decisions = len([d for d in self.decision_history if d.action == JudgmentAction.MODIFY])
        discard_decisions = len([d for d in self.decision_history if d.action == JudgmentAction.DISCARD])
        
        avg_confidence = sum(d.confidence for d in self.decision_history) / total_decisions if total_decisions > 0 else 0
        avg_performance_score = sum(d.performance_score for d in self.decision_history) / total_decisions if total_decisions > 0 else 0
        avg_emotion_score = sum(d.emotion_score for d in self.decision_history) / total_decisions if total_decisions > 0 else 0
        
        return {
            "total_strategies": total_strategies,
            "active_strategies": active_strategies,
            "modified_strategies": modified_strategies,
            "discarded_strategies": discarded_strategies,
            "total_decisions": total_decisions,
            "decision_distribution": {
                "continue": continue_decisions,
                "modify": modify_decisions,
                "discard": discard_decisions
            },
            "average_confidence": avg_confidence,
            "average_performance_score": avg_performance_score,
            "average_emotion_score": avg_emotion_score
        }
    
    def should_evaluate_strategy(self, strategy_id: str) -> bool:
        """전략을 평가해야 하는지 판단합니다."""
        if strategy_id not in self.strategy_records:
            return False
        
        record = self.strategy_records[strategy_id]
        strategy_age_days = (datetime.now() - record.start_date).days
        
        # 3일마다 평가
        return strategy_age_days % 3 == 0
    
    def get_strategies_needing_evaluation(self) -> List[str]:
        """평가가 필요한 전략들을 반환합니다."""
        strategies_to_evaluate = []
        
        for strategy_id in self.strategy_records:
            if self.should_evaluate_strategy(strategy_id):
                strategies_to_evaluate.append(strategy_id)
        
        return strategies_to_evaluate

# 싱글톤 인스턴스
_strategy_survival_judge = None

def get_strategy_survival_judge() -> StrategySurvivalJudge:
    """StrategySurvivalJudge 싱글톤 인스턴스 반환"""
    global _strategy_survival_judge
    if _strategy_survival_judge is None:
        _strategy_survival_judge = StrategySurvivalJudge()
    return _strategy_survival_judge 