"""
DuRi의 Hybrid Strategy 시스템

현실 전략과 Dream 전략을 병행 실행하고 비교하는 시스템입니다.
점수 기반 자동 승격 로직을 포함하여 더 나은 전략을 자동으로 채택합니다.
"""

import logging
import threading
import time
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

from duri_brain.dream.dream_engine import get_dream_engine
from duri_brain.eval.core_eval import get_core_eval

logger = logging.getLogger(__name__)

class StrategyType(Enum):
    """전략 유형"""
    REALITY = "reality"      # 현실 전략
    DREAM = "dream"          # Dream 전략
    HYBRID = "hybrid"        # 하이브리드 전략

class ExecutionStatus(Enum):
    """실행 상태"""
    RUNNING = "running"      # 실행 중
    COMPLETED = "completed"  # 완료
    FAILED = "failed"        # 실패
    PROMOTED = "promoted"    # 승격됨

@dataclass
class StrategyExecution:
    """전략 실행"""
    strategy_id: str
    strategy_type: StrategyType
    strategy_data: Dict[str, Any]
    start_time: datetime
    end_time: Optional[datetime]
    performance_score: float
    execution_status: ExecutionStatus
    error_message: Optional[str]

@dataclass
class ComparisonResult:
    """비교 결과"""
    reality_strategy_id: str
    dream_strategy_id: str
    reality_score: float
    dream_score: float
    winner: StrategyType
    score_difference: float
    promotion_reason: str
    comparison_time: datetime

class HybridStrategyExecutor:
    """
    DuRi의 Hybrid Strategy 실행기
    
    현실 전략과 Dream 전략을 병행 실행하고 비교하는 시스템입니다.
    """
    
    def __init__(self):
        """HybridStrategyExecutor 초기화"""
        self.dream_engine = get_dream_engine()
        self.core_eval = get_core_eval()
        
        self.reality_strategies: Dict[str, StrategyExecution] = {}
        self.dream_strategies: Dict[str, StrategyExecution] = {}
        self.comparison_history: List[ComparisonResult] = []
        
        self.is_running = False
        self.execution_thread: Optional[threading.Thread] = None
        
        # 실행 설정
        self.execution_config = {
            'comparison_interval': 10,  # 10초마다 비교
            'min_score_difference': 0.1,  # 최소 점수 차이
            'max_execution_time': 300,  # 최대 실행 시간 (5분)
            'auto_promotion': True,  # 자동 승격 활성화
            'parallel_execution': True  # 병렬 실행 활성화
        }
        
        logger.info("HybridStrategyExecutor 초기화 완료")
    
    def start_hybrid_execution(self, reality_strategy: Dict[str, Any]) -> str:
        """
        하이브리드 실행을 시작합니다.
        
        Args:
            reality_strategy: 현실 전략 데이터
            
        Returns:
            str: 실행 ID
        """
        if self.is_running:
            logger.warning("하이브리드 실행이 이미 진행 중입니다.")
            return "already_running"
        
        try:
            # 실행 ID 생성
            execution_id = f"hybrid_exec_{int(time.time() * 1000)}"
            
            # 현실 전략 등록
            reality_execution = StrategyExecution(
                strategy_id=f"{execution_id}_reality",
                strategy_type=StrategyType.REALITY,
                strategy_data=reality_strategy,
                start_time=datetime.now(),
                end_time=None,
                performance_score=0.0,
                execution_status=ExecutionStatus.RUNNING,
                error_message=None
            )
            
            self.reality_strategies[reality_execution.strategy_id] = reality_execution
            
            # Dream Engine 시작
            self.dream_engine.start_dream_engine(evaluation_callback=self._dream_evaluation_callback)
            
            # 하이브리드 실행 시작
            self.is_running = True
            self.execution_thread = threading.Thread(target=self._run_hybrid_execution, args=(execution_id,))
            self.execution_thread.daemon = True
            self.execution_thread.start()
            
            logger.info(f"하이브리드 실행 시작: {execution_id}")
            return execution_id
            
        except Exception as e:
            logger.error(f"하이브리드 실행 시작 실패: {e}")
            return "failed"
    
    def stop_hybrid_execution(self):
        """하이브리드 실행을 중지합니다."""
        if not self.is_running:
            logger.warning("하이브리드 실행이 진행되지 않았습니다.")
            return False
        
        self.is_running = False
        self.dream_engine.stop_dream_engine()
        
        if self.execution_thread:
            self.execution_thread.join(timeout=5)
        
        logger.info("하이브리드 실행 중지됨")
        return True
    
    def _run_hybrid_execution(self, execution_id: str):
        """하이브리드 실행 루프를 실행합니다."""
        logger.info(f"하이브리드 실행 루프 시작: {execution_id}")
        
        while self.is_running:
            try:
                # 1. 현실 전략 실행
                self._execute_reality_strategies()
                
                # 2. Dream 전략 평가 및 실행
                self._evaluate_and_execute_dream_strategies()
                
                # 3. 전략 비교
                self._compare_strategies()
                
                # 4. 승격 결정
                self._make_promotion_decisions()
                
                # 5. 대기
                time.sleep(self.execution_config['comparison_interval'])
                
            except Exception as e:
                logger.error(f"하이브리드 실행 루프 오류: {e}")
                time.sleep(5)
        
        logger.info(f"하이브리드 실행 루프 종료: {execution_id}")
    
    def _execute_reality_strategies(self):
        """현실 전략들을 실행합니다."""
        for strategy_id, execution in self.reality_strategies.items():
            if execution.execution_status == ExecutionStatus.RUNNING:
                try:
                    # 현실 전략 실행 (시뮬레이션)
                    performance_score = self._simulate_strategy_execution(execution.strategy_data)
                    
                    execution.performance_score = performance_score
                    execution.end_time = datetime.now()
                    execution.execution_status = ExecutionStatus.COMPLETED
                    
                    logger.debug(f"현실 전략 {strategy_id} 실행 완료: {performance_score:.2f}")
                    
                except Exception as e:
                    execution.execution_status = ExecutionStatus.FAILED
                    execution.error_message = str(e)
                    logger.error(f"현실 전략 {strategy_id} 실행 실패: {e}")
    
    def _evaluate_and_execute_dream_strategies(self):
        """Dream 전략들을 평가하고 실행합니다."""
        # 승격된 Dream 전략들 가져오기
        promoted_dreams = self.dream_engine.get_promoted_dreams()
        
        for dream_result in promoted_dreams:
            dream_id = dream_result.dream_id
            
            # 이미 실행 중인지 확인
            if dream_id in self.dream_strategies:
                continue
            
            try:
                # Dream 전략 평가
                evaluation_decision = self.core_eval.evaluate_dream_strategy(
                    dream_data={
                        'dream_id': dream_id,
                        'type': dream_result.strategy.get('type', 'unknown'),
                        'confidence_score': dream_result.confidence,
                        'novelty_score': dream_result.novelty,
                        'complexity_score': dream_result.complexity,
                        'priority': dream_result.strategy.get('priority', 0.5)
                    }
                )
                
                # 채택된 경우 실행
                if evaluation_decision.result.value in ['adopt', 'eureka_promote']:
                    dream_execution = StrategyExecution(
                        strategy_id=dream_id,
                        strategy_type=StrategyType.DREAM,
                        strategy_data=dream_result.strategy,
                        start_time=datetime.now(),
                        end_time=None,
                        performance_score=0.0,
                        execution_status=ExecutionStatus.RUNNING,
                        error_message=None
                    )
                    
                    self.dream_strategies[dream_id] = dream_execution
                    logger.info(f"Dream 전략 {dream_id} 실행 시작")
                
            except Exception as e:
                logger.error(f"Dream 전략 {dream_id} 평가 실패: {e}")
        
        # 실행 중인 Dream 전략들 실행
        for strategy_id, execution in self.dream_strategies.items():
            if execution.execution_status == ExecutionStatus.RUNNING:
                try:
                    # Dream 전략 실행 (시뮬레이션)
                    performance_score = self._simulate_strategy_execution(execution.strategy_data)
                    
                    execution.performance_score = performance_score
                    execution.end_time = datetime.now()
                    execution.execution_status = ExecutionStatus.COMPLETED
                    
                    logger.debug(f"Dream 전략 {strategy_id} 실행 완료: {performance_score:.2f}")
                    
                except Exception as e:
                    execution.execution_status = ExecutionStatus.FAILED
                    execution.error_message = str(e)
                    logger.error(f"Dream 전략 {strategy_id} 실행 실패: {e}")
    
    def _simulate_strategy_execution(self, strategy_data: Dict[str, Any]) -> float:
        """전략 실행을 시뮬레이션합니다."""
        # 기본 성과 점수
        base_score = strategy_data.get('priority', 0.5)
        
        # 전략 유형별 가중치
        strategy_type = strategy_data.get('type', 'unknown')
        type_weights = {
            'random_combination': 0.7,
            'pattern_mutation': 0.8,
            'concept_fusion': 0.85,
            'intuition_exploration': 0.6
        }
        
        weight = type_weights.get(strategy_type, 0.7)
        
        # 랜덤 변동 추가
        random_factor = 0.1
        performance_score = base_score * weight + random.uniform(-random_factor, random_factor)
        
        return max(min(performance_score, 1.0), 0.0)
    
    def _compare_strategies(self):
        """전략들을 비교합니다."""
        # 완료된 현실 전략들
        completed_reality = [execution for execution in self.reality_strategies.values() 
                           if execution.execution_status == ExecutionStatus.COMPLETED]
        
        # 완료된 Dream 전략들
        completed_dreams = [execution for execution in self.dream_strategies.values() 
                          if execution.execution_status == ExecutionStatus.COMPLETED]
        
        for reality_execution in completed_reality:
            for dream_execution in completed_dreams:
                # 이미 비교된 조합인지 확인
                comparison_key = f"{reality_execution.strategy_id}_{dream_execution.strategy_id}"
                if any(c.reality_strategy_id == reality_execution.strategy_id and 
                      c.dream_strategy_id == dream_execution.strategy_id 
                      for c in self.comparison_history):
                    continue
                
                # 비교 실행
                comparison_result = self._execute_comparison(reality_execution, dream_execution)
                if comparison_result:
                    self.comparison_history.append(comparison_result)
    
    def _execute_comparison(self, reality_execution: StrategyExecution, 
                          dream_execution: StrategyExecution) -> Optional[ComparisonResult]:
        """두 전략을 비교합니다."""
        try:
            reality_score = reality_execution.performance_score
            dream_score = dream_execution.performance_score
            score_difference = abs(reality_score - dream_score)
            
            # 승자 결정
            if dream_score > reality_score:
                winner = StrategyType.DREAM
                promotion_reason = f"Dream 전략이 현실 전략보다 {score_difference:.2f}점 높음"
            elif reality_score > dream_score:
                winner = StrategyType.REALITY
                promotion_reason = f"현실 전략이 Dream 전략보다 {score_difference:.2f}점 높음"
            else:
                winner = StrategyType.REALITY  # 동점 시 현실 전략 유지
                promotion_reason = "동점으로 현실 전략 유지"
            
            comparison_result = ComparisonResult(
                reality_strategy_id=reality_execution.strategy_id,
                dream_strategy_id=dream_execution.strategy_id,
                reality_score=reality_score,
                dream_score=dream_score,
                winner=winner,
                score_difference=score_difference,
                promotion_reason=promotion_reason,
                comparison_time=datetime.now()
            )
            
            logger.info(f"전략 비교 완료: {winner.value} 승리 (차이: {score_difference:.2f})")
            return comparison_result
            
        except Exception as e:
            logger.error(f"전략 비교 실패: {e}")
            return None
    
    def _make_promotion_decisions(self):
        """승격 결정을 내립니다."""
        if not self.execution_config['auto_promotion']:
            return
        
        for comparison in self.comparison_history:
            # 최소 점수 차이 확인
            if comparison.score_difference < self.execution_config['min_score_difference']:
                continue
            
            # Dream 전략이 승리한 경우
            if comparison.winner == StrategyType.DREAM:
                # 현실 전략을 Dream 전략으로 교체
                reality_strategy_id = comparison.reality_strategy_id
                dream_strategy_id = comparison.dream_strategy_id
                
                if reality_strategy_id in self.reality_strategies:
                    # 현실 전략을 Dream 전략으로 승격
                    reality_execution = self.reality_strategies[reality_strategy_id]
                    dream_execution = self.dream_strategies.get(dream_strategy_id)
                    
                    if dream_execution:
                        # 전략 데이터 교체
                        reality_execution.strategy_data = dream_execution.strategy_data.copy()
                        reality_execution.strategy_type = StrategyType.HYBRID
                        reality_execution.execution_status = ExecutionStatus.PROMOTED
                        
                        logger.info(f"Dream 전략 {dream_strategy_id}가 현실 전략으로 승격됨")
    
    def _dream_evaluation_callback(self, dream_candidate) -> Optional[Dict[str, Any]]:
        """Dream 평가 콜백 함수"""
        try:
            # Dream 전략 평가
            evaluation_decision = self.core_eval.evaluate_dream_strategy(
                dream_data={
                    'dream_id': dream_candidate.dream_id,
                    'type': dream_candidate.strategy_data.get('type', 'unknown'),
                    'confidence_score': dream_candidate.confidence_score,
                    'novelty_score': dream_candidate.novelty_score,
                    'complexity_score': dream_candidate.complexity_score,
                    'priority': dream_candidate.strategy_data.get('priority', 0.5)
                }
            )
            
            return {
                'recommendation': evaluation_decision.result.value,
                'confidence': evaluation_decision.confidence,
                'combined_score': evaluation_decision.combined_score
            }
            
        except Exception as e:
            logger.error(f"Dream 평가 콜백 실패: {e}")
            return None
    
    def get_hybrid_statistics(self) -> Dict[str, Any]:
        """하이브리드 실행 통계를 반환합니다."""
        total_reality = len(self.reality_strategies)
        total_dreams = len(self.dream_strategies)
        total_comparisons = len(self.comparison_history)
        
        # 실행 상태별 통계
        reality_status = {}
        dream_status = {}
        
        for status in ExecutionStatus:
            reality_status[status.value] = len([s for s in self.reality_strategies.values() 
                                             if s.execution_status == status])
            dream_status[status.value] = len([s for s in self.dream_strategies.values() 
                                           if s.execution_status == status])
        
        # 승격 통계
        promotions = len([c for c in self.comparison_history if c.winner == StrategyType.DREAM])
        promotion_rate = promotions / total_comparisons if total_comparisons > 0 else 0
        
        return {
            "is_running": self.is_running,
            "total_reality_strategies": total_reality,
            "total_dream_strategies": total_dreams,
            "total_comparisons": total_comparisons,
            "reality_status_distribution": reality_status,
            "dream_status_distribution": dream_status,
            "promotions": promotions,
            "promotion_rate": promotion_rate,
            "average_score_difference": sum(c.score_difference for c in self.comparison_history) / total_comparisons if total_comparisons > 0 else 0
        }
    
    def get_recent_comparisons(self, limit: int = 10) -> List[ComparisonResult]:
        """최근 비교 결과들을 반환합니다."""
        return self.comparison_history[-limit:] if self.comparison_history else []

# 싱글톤 인스턴스
_hybrid_strategy_executor = None

def get_hybrid_strategy_executor() -> HybridStrategyExecutor:
    """HybridStrategyExecutor 싱글톤 인스턴스 반환"""
    global _hybrid_strategy_executor
    if _hybrid_strategy_executor is None:
        _hybrid_strategy_executor = HybridStrategyExecutor()
    return _hybrid_strategy_executor 