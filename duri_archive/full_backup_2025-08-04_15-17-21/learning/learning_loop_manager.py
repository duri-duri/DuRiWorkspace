"""
DuRi의 학습 루프 관리자

5단계 학습 루프 통합 시스템
모방 → 반복 → 피드백 → 도전 → 개선의 순환 구조를 관리합니다.
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio
import threading
import time

from .strategy_imitator import get_strategy_imitator, ImitationType
from .practice_engine import get_practice_engine, PracticeType
from .challenge_trigger import get_challenge_trigger, ChallengeType
from .self_improvement_engine import get_self_improvement_engine, ImprovementType
from .strategy_survival_judge import get_strategy_survival_judge
from .auto_retrospector import get_auto_retrospector
from duri_core.assessment.self_assessment_manager import get_self_assessment_manager
from duri_core.memory.strategy_graveyard import get_strategy_graveyard
from duri_brain.goals.goal_oriented_thinking import get_goal_oriented_thinking
from duri_brain.ethics.emotional_ethical_judgment import get_emotional_ethical_judgment
from duri_brain.goals.autonomous_goal_setting import get_autonomous_goal_setting
from duri_brain.creativity.advanced_creativity_system import get_advanced_creativity_system
from duri_core.memory.memory_sync import MemoryType

logger = logging.getLogger(__name__)

class LearningStage(Enum):
    """학습 단계"""
    IMITATION = "imitation"  # 1단계: 모방
    PRACTICE = "practice"    # 2단계: 반복
    FEEDBACK = "feedback"    # 3단계: 피드백
    CHALLENGE = "challenge"  # 4단계: 도전
    IMPROVEMENT = "improvement"  # 5단계: 개선

@dataclass
class LearningCycle:
    """학습 사이클"""
    cycle_id: str
    start_time: datetime
    end_time: Optional[datetime]
    stages_completed: List[LearningStage]
    current_stage: Optional[LearningStage]
    strategy: Dict[str, Any]
    modified_strategy: Optional[Dict[str, Any]]
    performance_metrics: Dict[str, float]
    success: bool

@dataclass
class LearningResult:
    """학습 결과"""
    cycle: LearningCycle
    stage_results: Dict[LearningStage, Dict[str, Any]]
    overall_performance: float
    improvement_score: float
    recommendations: List[str]
    next_actions: List[str]

class LearningLoopManager:
    """
    DuRi의 학습 루프 관리자
    
    5단계 학습 루프를 통합하고 관리하는 시스템입니다.
    """
    
    def __init__(self):
        """LearningLoopManager 초기화"""
        self.learning_cycles: List[LearningCycle] = []
        self.current_cycle: Optional[LearningCycle] = None
        self.is_running = False
        self.loop_thread: Optional[threading.Thread] = None
        self.learning_cycle_count = 0  # 학습 사이클 카운터 추가
        
        # 각 단계별 모듈 초기화
        self.strategy_imitator = get_strategy_imitator()
        self.practice_engine = get_practice_engine()
        self.challenge_trigger = get_challenge_trigger()
        self.self_improvement_engine = get_self_improvement_engine()
        self.strategy_survival_judge = get_strategy_survival_judge()
        self.strategy_graveyard = get_strategy_graveyard()
        
        # Meta Learning 모듈 초기화
        self.auto_retrospector = get_auto_retrospector()
        
        # Self Assessment 모듈 초기화
        self.self_assessment_manager = get_self_assessment_manager()
        
        # Goal Oriented Thinking 모듈 초기화
        self.goal_oriented_thinking = get_goal_oriented_thinking()
        
        # Emotional Ethical Judgment 모듈 초기화
        self.emotional_ethical_judgment = get_emotional_ethical_judgment()
        
        # Autonomous Goal Setting 모듈 초기화
        self.autonomous_goal_setting = get_autonomous_goal_setting()
        
        # Advanced Creativity System 모듈 초기화
        self.advanced_creativity_system = get_advanced_creativity_system()
        
        # 학습 설정
        self.learning_config = {
            'max_cycles': 100,
            'cycle_timeout': 300,  # 5분
            'min_improvement_threshold': 0.1,
            'max_failure_streak': 5,
            'meta_learning_interval': 3600  # 1시간마다 메타 학습
        }
        
        logger.info("LearningLoopManager 초기화 완료")
    
    def start_learning_loop(self, initial_strategy: Dict[str, Any], 
                           context: Optional[Dict[str, Any]] = None) -> str:
        """
        학습 루프를 시작합니다.
        
        Args:
            initial_strategy: 초기 전략
            context: 학습 컨텍스트
            
        Returns:
            str: 학습 사이클 ID
        """
        if self.is_running:
            logger.warning("학습 루프가 이미 실행 중입니다.")
            return self.current_cycle.cycle_id if self.current_cycle else "unknown"
        
        cycle_id = f"learning_cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.current_cycle = LearningCycle(
            cycle_id=cycle_id,
            start_time=datetime.now(),
            end_time=None,
            stages_completed=[],
            current_stage=None,
            strategy=initial_strategy,
            modified_strategy=None,
            performance_metrics={},
            success=False
        )
        
        self.is_running = True
        
        # 별도 스레드에서 학습 루프 실행
        self.loop_thread = threading.Thread(
            target=self._run_learning_loop,
            args=(context,),
            daemon=True
        )
        self.loop_thread.start()
        
        logger.info(f"학습 루프 시작: {cycle_id}")
        return cycle_id
    
    def stop_learning_loop(self):
        """학습 루프를 중지합니다."""
        self.is_running = False
        if self.current_cycle:
            self.current_cycle.end_time = datetime.now()
            self.learning_cycles.append(self.current_cycle)
            self.current_cycle = None
        
        logger.info("학습 루프 중지됨")
    
    def _run_learning_loop(self, context: Optional[Dict[str, Any]]):
        """학습 루프를 실행합니다."""
        try:
            cycle_count = 0
            failure_streak = 0
            last_meta_learning_time = None
            start_time = time.time()
            
            while self.is_running and cycle_count < self.learning_config['max_cycles']:
                # 타임아웃 체크
                if (time.time() - start_time) > self.learning_config['cycle_timeout']:
                    logger.warning(f"⚠️ 학습 루프 타임아웃 ({self.learning_config['cycle_timeout']}초)")
                    break
                
                cycle_count += 1
                logger.info(f"학습 사이클 {cycle_count} 시작")
                
                # 메타 학습 실행 (주기적)
                current_time = datetime.now()
                if (last_meta_learning_time is None or 
                    (current_time - last_meta_learning_time).total_seconds() >= self.learning_config['meta_learning_interval']):
                    
                    self._run_meta_learning_cycle()
                    last_meta_learning_time = current_time
                
                # 자기 평가 실행 (주기적)
                if self.self_assessment_manager.should_run_assessment():
                    self._run_self_assessment_cycle()
                
                # 목표 지향적 사고 실행 (주기적)
                if self.goal_oriented_thinking.should_set_new_goals():
                    self._run_goal_oriented_thinking_cycle()
                
                # 감정/윤리 판단 실행 (주기적)
                if self._should_run_emotional_ethical_judgment():
                    self._run_emotional_ethical_judgment_cycle()
                
                # 자율 목표 설정 실행 (주기적)
                if self.autonomous_goal_setting.should_generate_autonomous_goals():
                    self._run_autonomous_goal_setting_cycle()
                
                # 창의성 고도화 실행 (주기적)
                if self.advanced_creativity_system.should_enhance_creativity():
                    self._run_creativity_enhancement_cycle()
                
                # 5단계 학습 루프 실행 (타임아웃 보호)
                result = self._execute_learning_cycle_with_timeout(context)
                
                if result and result.cycle.success:
                    failure_streak = 0
                    logger.info(f"사이클 {cycle_count} 성공: 개선점수 {result.improvement_score:.2f}")
                else:
                    failure_streak += 1
                    logger.warning(f"사이클 {cycle_count} 실패 (연속 실패: {failure_streak})")
                
                # 연속 실패 시 중단
                if failure_streak >= self.learning_config['max_failure_streak']:
                    logger.error(f"연속 실패로 인한 학습 루프 중단: {failure_streak}회")
                    break
                
                # 개선이 미미한 경우 중단
                if result and result.improvement_score < self.learning_config['min_improvement_threshold']:
                    logger.info(f"개선이 미미하여 학습 루프 중단: {result.improvement_score:.2f}")
                    break
                
                # 다음 사이클을 위한 전략 업데이트
                if result and result.cycle.modified_strategy:
                    self.current_cycle.strategy = result.cycle.modified_strategy
                
                time.sleep(1)  # 사이클 간 간격
            
            self.stop_learning_loop()
            
        except Exception as e:
            logger.error(f"학습 루프 실행 중 오류: {e}")
            self.stop_learning_loop()
    
    def _execute_learning_cycle_with_timeout(self, context: Optional[Dict[str, Any]]) -> Optional[LearningResult]:
        """타임아웃 보호가 포함된 학습 사이클 실행"""
        try:
            import threading
            import time
            
            # 결과를 저장할 변수
            result = {"learning_result": None, "error": None}
            
            def execute_cycle():
                try:
                    learning_result = self._execute_learning_cycle(context)
                    result["learning_result"] = learning_result
                except Exception as e:
                    result["error"] = str(e)
            
            # 별도 스레드에서 사이클 실행
            thread = threading.Thread(target=execute_cycle, daemon=True)
            thread.start()
            
            # 타임아웃 대기 (60초)
            timeout = 60
            start_time = time.time()
            
            while thread.is_alive() and (time.time() - start_time) < timeout:
                time.sleep(0.1)  # 100ms 간격으로 체크
            
            if thread.is_alive():
                logger.error(f"❌ 학습 사이클 실행 타임아웃 ({timeout}초)")
                return None
            
            if result["error"]:
                logger.error(f"❌ 학습 사이클 실행 실패: {result['error']}")
                return None
            
            return result["learning_result"]
            
        except Exception as e:
            logger.error(f"❌ 학습 사이클 실행 중 오류: {e}")
            return None
    
    def _execute_imitation_stage(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """1단계: 모방 단계를 실행합니다."""
        try:
            # 참조 전략 선택 (시뮬레이션)
            reference_strategy = {
                'id': 'reference_strategy_001',
                'type': 'successful_pattern',
                'parameters': {'speed': 0.8, 'accuracy': 0.9, 'efficiency': 0.85},
                'execution_method': 'standard'
            }
            
            # 모방 유형 결정
            imitation_type = ImitationType.ADAPTIVE_COPY
            
            # 모방 실행
            imitation_result = self.strategy_imitator.imitate(
                reference_strategy=reference_strategy,
                imitation_type=imitation_type,
                context=context
            )
            
            return {
                'success': imitation_result.success,
                'imitated_strategy': imitation_result.imitated_strategy,
                'confidence': imitation_result.confidence,
                'adaptation_notes': imitation_result.adaptation_notes
            }
            
        except Exception as e:
            logger.error(f"모방 단계 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_practice_stage(self, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """2단계: 반복 단계를 실행합니다."""
        try:
            # 모방된 전략 가져오기
            imitated_strategy = self.current_cycle.strategy
            
            # 연습 유형 결정
            practice_type = PracticeType.REPETITION
            
            # 연습 실행
            practice_result = self.practice_engine.practice_strategy(
                strategy=imitated_strategy,
                practice_type=practice_type,
                iterations=10,
                context=context
            )
            
            return {
                'success': practice_result.success_rate > 0.5,
                'success_rate': practice_result.success_rate,
                'average_performance': practice_result.average_performance,
                'improvement_score': practice_result.improvement_score,
                'recommendations': practice_result.recommendations
            }
            
        except Exception as e:
            logger.error(f"반복 단계 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_feedback_stage(self, practice_result: Dict[str, Any], 
                              context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """3단계: 피드백 단계를 실행합니다."""
        try:
            # 연습 결과를 바탕으로 피드백 생성
            feedback_data = {
                'performance_issues': [],
                'reliability_issues': [],
                'efficiency_issues': [],
                'positive_feedback': 0,
                'negative_feedback': 0,
                'issues_resolved': 0
            }
            
            # 성능 기반 피드백
            if practice_result.get('average_performance', 0) < 0.6:
                feedback_data['performance_issues'].append('낮은 평균 성능')
                feedback_data['negative_feedback'] += 1
            else:
                feedback_data['positive_feedback'] += 1
            
            # 성공률 기반 피드백
            if practice_result.get('success_rate', 0) < 0.5:
                feedback_data['reliability_issues'].append('낮은 성공률')
                feedback_data['negative_feedback'] += 1
            else:
                feedback_data['positive_feedback'] += 1
            
            # 개선 점수 기반 피드백
            if practice_result.get('improvement_score', 0) < 0.1:
                feedback_data['efficiency_issues'].append('미미한 개선')
                feedback_data['negative_feedback'] += 1
            else:
                feedback_data['positive_feedback'] += 1
                feedback_data['issues_resolved'] += 1
            
            return {
                'success': True,
                'feedback_data': feedback_data,
                'positive_feedback': feedback_data['positive_feedback'],
                'negative_feedback': feedback_data['negative_feedback'],
                'issues_resolved': feedback_data['issues_resolved']
            }
            
        except Exception as e:
            logger.error(f"피드백 단계 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_challenge_stage(self, feedback_result: Dict[str, Any], 
                               context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """4단계: 도전 단계를 실행합니다."""
        try:
            # 전략 히스토리 구성
            strategy_history = {
                'success_streak': len(self.learning_cycles) if self.learning_cycles else 0,
                'performance_stability': 0.8,  # 시뮬레이션
                'new_feedback_detected': feedback_result.get('negative_feedback', 0) > 0
            }
            
            # 도전 판단
            challenge_decision = self.challenge_trigger.should_explore(
                strategy_history=strategy_history,
                current_context=context
            )
            
            return {
                'success': True,
                'should_challenge': challenge_decision.should_challenge,
                'challenge_type': challenge_decision.challenge_type.value if challenge_decision.challenge_type else None,
                'confidence': challenge_decision.confidence,
                'reasoning': challenge_decision.reasoning,
                'recommended_strategy': challenge_decision.recommended_strategy,
                'risk_level': challenge_decision.risk_level
            }
            
        except Exception as e:
            logger.error(f"도전 단계 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_improvement_stage(self, challenge_result: Dict[str, Any], 
                                 context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """5단계: 개선 단계를 실행합니다."""
        try:
            # 피드백 데이터 구성
            feedback_data = {
                'performance_issues': [],
                'reliability_issues': [],
                'efficiency_issues': [],
                'positive_feedback': 0,
                'negative_feedback': 0,
                'issues_resolved': 0
            }
            
            # 도전 결과에 따른 피드백 조정
            if challenge_result.get('should_challenge', False):
                feedback_data['positive_feedback'] += 1
            else:
                feedback_data['negative_feedback'] += 1
            
            # 개선 실행
            improvement_result = self.self_improvement_engine.improve(
                old_strategy=self.current_cycle.strategy,
                feedback_data=feedback_data
            )
            
            return {
                'success': improvement_result.success,
                'improvement_score': improvement_result.improvement_score,
                'confidence_gain': improvement_result.confidence_gain,
                'changes_made': improvement_result.changes_made,
                'modified_strategy': improvement_result.improved_strategy
            }
            
        except Exception as e:
            logger.error(f"개선 단계 실패: {e}")
            return {'success': False, 'error': str(e)}
    
    def _calculate_overall_performance(self, stage_results: Dict[LearningStage, Dict[str, Any]]) -> float:
        """전체 성과를 계산합니다."""
        performances = []
        
        # 각 단계별 성과 수집
        for stage, result in stage_results.items():
            if result.get('success', False):
                if stage == LearningStage.IMITATION:
                    performances.append(result.get('confidence', 0.0))
                elif stage == LearningStage.PRACTICE:
                    performances.append(result.get('average_performance', 0.0))
                elif stage == LearningStage.FEEDBACK:
                    feedback_ratio = result.get('positive_feedback', 0) / max(result.get('positive_feedback', 0) + result.get('negative_feedback', 1), 1)
                    performances.append(feedback_ratio)
                elif stage == LearningStage.CHALLENGE:
                    performances.append(result.get('confidence', 0.0))
                elif stage == LearningStage.IMPROVEMENT:
                    performances.append(result.get('improvement_score', 0.0))
        
        return sum(performances) / len(performances) if performances else 0.0
    
    def _calculate_improvement_score(self, stage_results: Dict[LearningStage, Dict[str, Any]]) -> float:
        """개선 점수를 계산합니다."""
        improvement_scores = []
        
        for stage, result in stage_results.items():
            if stage == LearningStage.PRACTICE:
                improvement_scores.append(result.get('improvement_score', 0.0))
            elif stage == LearningStage.IMPROVEMENT:
                improvement_scores.append(result.get('improvement_score', 0.0))
        
        return sum(improvement_scores) / len(improvement_scores) if improvement_scores else 0.0
    
    def _generate_recommendations(self, stage_results: Dict[LearningStage, Dict[str, Any]]) -> List[str]:
        """추천사항을 생성합니다."""
        recommendations = []
        
        # 각 단계별 추천사항 수집
        for stage, result in stage_results.items():
            if stage == LearningStage.PRACTICE and result.get('recommendations'):
                recommendations.extend(result['recommendations'])
            elif stage == LearningStage.CHALLENGE and result.get('reasoning'):
                recommendations.extend(result['reasoning'])
        
        if not recommendations:
            recommendations.append("모든 단계가 정상적으로 완료되었습니다.")
        
        return recommendations
    
    def _determine_next_actions(self, stage_results: Dict[LearningStage, Dict[str, Any]]) -> List[str]:
        """다음 행동을 결정합니다."""
        next_actions = []
        
        # 개선 결과에 따른 다음 행동 결정
        improvement_result = stage_results.get(LearningStage.IMPROVEMENT, {})
        if improvement_result.get('success', False):
            next_actions.append("개선된 전략으로 다음 사이클 진행")
        else:
            next_actions.append("전략 재검토 필요")
        
        # 도전 결과에 따른 행동
        challenge_result = stage_results.get(LearningStage.CHALLENGE, {})
        if challenge_result.get('should_challenge', False):
            next_actions.append("도전적 전략 시도")
        
        return next_actions
    
    def _evaluate_strategy_survival(self, overall_performance: float, context: Optional[Dict[str, Any]]) -> Optional[Any]:
        """전략 생존을 평가합니다."""
        try:
            strategy_id = self.current_cycle.cycle_id
            
            # 전략 등록 (아직 등록되지 않은 경우)
            if not self.strategy_survival_judge.get_strategy_info(strategy_id):
                self.strategy_survival_judge.register_strategy(
                    strategy_id=strategy_id,
                    initial_performance=overall_performance,
                    initial_emotion=context.get('emotion', 'neutral') if context else 'neutral'
                )
            
            # 성과 업데이트
            self.strategy_survival_judge.update_strategy_performance(
                strategy_id=strategy_id,
                performance=overall_performance,
                emotion=context.get('emotion', 'neutral') if context else None
            )
            
            # 생존 판단
            survival_decision = self.strategy_survival_judge.evaluate_strategy_survival(strategy_id)
            
            # 폐기된 경우 묘지에 안장
            if survival_decision and survival_decision.action.value == 'discard':
                self._bury_failed_strategy(survival_decision, context)
            
            return survival_decision
            
        except Exception as e:
            logger.error(f"전략 생존 평가 실패: {e}")
            return None
    
    def _bury_failed_strategy(self, survival_decision: Any, context: Optional[Dict[str, Any]]):
        """실패한 전략을 묘지에 안장합니다."""
        try:
            strategy_id = survival_decision.strategy_id
            strategy_info = self.strategy_survival_judge.get_strategy_info(strategy_id)
            
            if strategy_info:
                self.strategy_graveyard.bury_strategy(
                    strategy_id=strategy_id,
                    failure_reason=survival_decision.recommended_action,
                    context=context or {},
                    emotion_trend=[],
                    performance_history=[strategy_info['current_performance']],
                    modification_count=strategy_info['modification_count'],
                    strategy_age_days=strategy_info['age_days']
                )
                
                logger.info(f"전략 {strategy_id} 묘지에 안장됨")
                
        except Exception as e:
            logger.error(f"전략 안장 실패: {e}")
    
    def get_learning_statistics(self) -> Dict[str, Any]:
        """학습 통계를 반환합니다."""
        total_cycles = len(self.learning_cycles)
        successful_cycles = len([c for c in self.learning_cycles if c.success])
        
        stage_completion_rates = {}
        for stage in LearningStage:
            completed_count = sum(1 for c in self.learning_cycles if stage in c.stages_completed)
            stage_completion_rates[stage.value] = completed_count / total_cycles if total_cycles > 0 else 0
        
        avg_performance = sum(c.performance_metrics.get('overall_performance', 0) for c in self.learning_cycles) / total_cycles if total_cycles > 0 else 0
        avg_improvement = sum(c.performance_metrics.get('improvement_score', 0) for c in self.learning_cycles) / total_cycles if total_cycles > 0 else 0
        
        return {
            "total_cycles": total_cycles,
            "successful_cycles": successful_cycles,
            "success_rate": successful_cycles / total_cycles if total_cycles > 0 else 0,
            "stage_completion_rates": stage_completion_rates,
            "average_performance": avg_performance,
            "average_improvement": avg_improvement,
            "is_running": self.is_running,
            "survival_statistics": self.strategy_survival_judge.get_survival_statistics(),
            "graveyard_statistics": self.strategy_graveyard.get_failure_statistics()
        }
    
    def _run_meta_learning_cycle(self):
        """메타 학습 사이클을 실행합니다."""
        try:
            logger.info("메타 학습 사이클 시작")
            
            # AutoRetrospector를 통한 종합 분석
            meta_learning_data = self.auto_retrospector.run_comprehensive_analysis()
            
            # 분석 결과를 바탕으로 학습 전략 업데이트
            self._update_learning_strategy_based_on_meta_analysis(meta_learning_data)
            
            logger.info("메타 학습 사이클 완료")
            
        except Exception as e:
            logger.error(f"메타 학습 사이클 실행 중 오류: {e}")
    
    def _update_learning_strategy_based_on_meta_analysis(self, meta_learning_data):
        """메타 학습 분석 결과를 바탕으로 학습 전략을 업데이트합니다."""
        try:
            # 개선 제안 처리
            for suggestion in meta_learning_data.improvement_suggestions:
                if suggestion.priority == "critical":
                    logger.warning(f"중요한 개선 제안: {suggestion.description}")
                    self._apply_critical_improvement(suggestion)
                elif suggestion.priority == "high":
                    logger.info(f"높은 우선순위 개선 제안: {suggestion.description}")
                    self._apply_high_priority_improvement(suggestion)
            
            # 학습 전략 업데이트
            for strategy_update in meta_learning_data.learning_strategy_updates:
                logger.info(f"학습 전략 업데이트: {strategy_update.strategy_name}")
                self._apply_learning_strategy_update(strategy_update)
            
            # 성능 패턴 분석 결과 반영
            for pattern in meta_learning_data.performance_patterns:
                if pattern.pattern_type == "high_cpu_usage":
                    logger.warning("CPU 사용률이 높아 학습 강도를 조정합니다")
                    self._adjust_learning_intensity("reduce")
                elif pattern.pattern_type == "low_cpu_usage":
                    logger.info("CPU 사용률이 낮아 학습 강도를 증가시킵니다")
                    self._adjust_learning_intensity("increase")
            
        except Exception as e:
            logger.error(f"학습 전략 업데이트 중 오류: {e}")
    
    def _apply_critical_improvement(self, suggestion):
        """중요한 개선 제안을 적용합니다."""
        try:
            # 딕셔너리와 객체 모두 지원
            category = suggestion.get("category") if isinstance(suggestion, dict) else getattr(suggestion, "category", None)
            
            if category == "error_handling":
                # 오류 처리 개선
                self.learning_config['max_failure_streak'] = max(3, self.learning_config['max_failure_streak'] - 1)
                logger.info("오류 처리 개선: 실패 허용 횟수 감소")
            
            elif category == "performance":
                # 성능 최적화
                self.learning_config['cycle_timeout'] = min(600, self.learning_config['cycle_timeout'] + 60)
                logger.info("성능 최적화: 사이클 타임아웃 증가")
            
            elif category == "learning":
                # 학습 전략 개선
                self.learning_config['min_improvement_threshold'] = max(0.05, self.learning_config['min_improvement_threshold'] - 0.01)
                logger.info("학습 전략 개선: 개선 임계값 조정")
            
        except Exception as e:
            logger.error(f"중요한 개선 제안 적용 실패: {e}")
    
    def _apply_high_priority_improvement(self, suggestion):
        """높은 우선순위 개선 제안을 적용합니다."""
        try:
            # 딕셔너리와 객체 모두 지원
            category = suggestion.get("category") if isinstance(suggestion, dict) else getattr(suggestion, "category", None)
            
            if category == "learning":
                # 학습 전략 개선
                self.learning_config['min_improvement_threshold'] = max(0.05, self.learning_config['min_improvement_threshold'] - 0.02)
                logger.info("학습 전략 개선: 개선 임계값 조정")
            
            elif category == "system_health":
                # 시스템 건강도 개선
                self.learning_config['meta_learning_interval'] = min(7200, self.learning_config['meta_learning_interval'] + 600)
                logger.info("시스템 건강도 개선: 메타 학습 간격 조정")
            
        except Exception as e:
            logger.error(f"높은 우선순위 개선 제안 적용 실패: {e}")
    
    def _apply_learning_strategy_update(self, strategy_update):
        """학습 전략 업데이트를 적용합니다."""
        try:
            if strategy_update.strategy_name == "learning_efficiency":
                # 학습 효율성 개선
                if strategy_update.current_performance < 0.5:
                    self.learning_config['min_improvement_threshold'] = max(0.05, self.learning_config['min_improvement_threshold'] - 0.01)
                    logger.info("학습 효율성 개선: 개선 임계값 낮춤")
            
            elif strategy_update.strategy_name == "learning_speed":
                # 학습 속도 개선
                if strategy_update.current_performance < 1.0:
                    self.learning_config['cycle_timeout'] = max(120, self.learning_config['cycle_timeout'] - 30)
                    logger.info("학습 속도 개선: 사이클 타임아웃 단축")
            
        except Exception as e:
            logger.error(f"학습 전략 업데이트 적용 실패: {e}")
    
    def update_learning_strategy(self, retrospection: Dict[str, Any]) -> Dict[str, Any]:
        """반성 결과를 바탕으로 학습 전략 업데이트 - 기존 메서드들과 완벽 통합"""
        try:
            logger.info("🔄 학습 전략 업데이트 시작")
            
            result = {
                "applied_improvements": [],
                "strategy_updates": [],
                "meta_reflection_log": retrospection,
                "update_timestamp": datetime.now().isoformat()
            }
            
            # 반성 결과에서 개선안 추출
            improvement_proposal = retrospection.get("improvement_proposal", {})
            specific_improvements = improvement_proposal.get("specific_improvements", [])
            
            # 우선순위별 개선안 적용
            for improvement in specific_improvements:
                if isinstance(improvement, dict):
                    priority = improvement.get("priority", "medium")
                    description = improvement.get("description", str(improvement))
                else:
                    priority = "medium"
                    description = str(improvement)
                
                if priority == "critical":
                    self._apply_critical_improvement({"category": "learning", "description": description})
                    result["applied_improvements"].append({"priority": "critical", "description": description})
                    logger.info(f"🔴 중요 개선안 적용: {description}")
                
                elif priority == "high":
                    self._apply_high_priority_improvement({"category": "learning", "description": description})
                    result["applied_improvements"].append({"priority": "high", "description": description})
                    logger.info(f"🟡 높은 우선순위 개선안 적용: {description}")
                
                else:
                    # 일반 개선안은 학습 강도 조정
                    self._adjust_learning_intensity("increase")
                    result["strategy_updates"].append({"type": "intensity_increase", "description": description})
                    logger.info(f"🟢 일반 개선안 적용: {description}")
            
            # 자체 평가 결과 반영
            self_assessment = retrospection.get("self_assessment", {})
            if self_assessment.get("overall_rating") == "needs_improvement":
                self._adjust_learning_intensity("reduce")
                result["strategy_updates"].append({"type": "intensity_reduce", "reason": "성과 개선 필요"})
                logger.info("📉 성과 개선을 위해 학습 강도 감소")
            
            # 메타 반성 로그 저장
            self._log_meta_reflection(retrospection)
            
            logger.info(f"✅ 학습 전략 업데이트 완료 - 적용된 개선안: {len(result['applied_improvements'])}개")
            return result
            
        except Exception as e:
            logger.error(f"❌ 학습 전략 업데이트 오류: {e}")
            return {
                "error": str(e),
                "applied_improvements": [],
                "strategy_updates": [],
                "meta_reflection_log": retrospection
            }

    def _log_meta_reflection(self, retrospection: Dict[str, Any]):
        """메타 반성 결과 기록"""
        try:
            # 반성 기록을 메모리에 저장
            reflection_log = {
                "timestamp": datetime.now().isoformat(),
                "accepted_criticisms": retrospection.get("accepted_criticisms", []),
                "improvement_proposals": retrospection.get("improvement_proposal", {}).get("specific_improvements", []),
                "self_assessment": retrospection.get("self_assessment", {}),
                "meta_analysis": retrospection.get("meta_analysis", {})
            }
            
            # 메모리 동기화 시스템에 저장
            if hasattr(self, 'memory_sync'):
                self.memory_sync.store_data(
                    data_type=MemoryType.LEARNING_REFLECTION,
                    data=reflection_log,
                    metadata={"source": "learning_loop_manager", "type": "meta_reflection"}
                )
            
            logger.info("📝 메타 반성 로그 저장 완료")
            
        except Exception as e:
            logger.error(f"❌ 메타 반성 로그 저장 오류: {e}")

    def _adjust_learning_intensity(self, direction: str):
        """학습 강도를 조정합니다."""
        try:
            if direction == "reduce":
                # 학습 강도 감소
                self.learning_config['cycle_timeout'] = min(600, self.learning_config['cycle_timeout'] + 60)
                self.learning_config['meta_learning_interval'] = min(7200, self.learning_config['meta_learning_interval'] + 600)
                logger.info("학습 강도 감소")
            
            elif direction == "increase":
                # 학습 강도 증가
                self.learning_config['cycle_timeout'] = min(300, self.learning_config['cycle_timeout'] - 30)
                self.learning_config['meta_learning_interval'] = max(1800, self.learning_config['meta_learning_interval'] - 300)
                logger.info("학습 강도 증가")
            
        except Exception as e:
            logger.error(f"학습 강도 조정 실패: {e}")
    
    def get_current_status(self) -> Dict[str, Any]:
        """현재 상태를 반환합니다."""
        if not self.current_cycle:
            return {"status": "idle", "message": "학습 루프가 실행되지 않음"}
        
        return {
            "status": "running" if self.is_running else "completed",
            "cycle_id": self.current_cycle.cycle_id,
            "current_stage": self.current_cycle.current_stage.value if self.current_cycle.current_stage else None,
            "stages_completed": [stage.value for stage in self.current_cycle.stages_completed],
            "start_time": self.current_cycle.start_time.isoformat(),
            "elapsed_time": (datetime.now() - self.current_cycle.start_time).total_seconds() if self.current_cycle.start_time else 0,
            "meta_learning_enabled": True,
            "last_meta_learning": self.auto_retrospector.last_analysis_time.isoformat() if self.auto_retrospector.last_analysis_time else None,
            "self_assessment_enabled": True,
            "last_self_assessment": self.self_assessment_manager.last_assessment_time.isoformat() if self.self_assessment_manager.last_assessment_time else None,
            "assessment_statistics": self.self_assessment_manager.get_assessment_statistics(),
            "goal_oriented_thinking_enabled": True,
            "goal_statistics": self.goal_oriented_thinking.get_goal_statistics(),
            "emotional_ethical_judgment_enabled": True,
            "judgment_statistics": self.emotional_ethical_judgment.get_judgment_statistics(),
            "autonomous_goal_setting_enabled": True,
            "autonomous_goal_statistics": self.autonomous_goal_setting.get_autonomous_goal_statistics(),
            "advanced_creativity_system_enabled": True,
            "creativity_statistics": self.advanced_creativity_system.get_creativity_statistics()
        }

    def _run_self_assessment_cycle(self):
        """자기 평가 사이클을 실행합니다."""
        try:
            logger.info("자기 평가 사이클 시작")
            
            # 종합 자기 평가 실행
            assessment_result = self.self_assessment_manager.run_comprehensive_assessment()
            
            # 평가 결과를 바탕으로 학습 전략 조정
            self._adjust_learning_strategy_based_on_assessment(assessment_result)
            
            logger.info(f"자기 평가 사이클 완료 - 전체 점수: {assessment_result.overall_score:.2f}")
            
        except Exception as e:
            logger.error(f"자기 평가 사이클 실행 중 오류: {e}")
    
    def _adjust_learning_strategy_based_on_assessment(self, assessment_result):
        """평가 결과를 바탕으로 학습 전략을 조정합니다."""
        try:
            overall_score = assessment_result.overall_score
            
            # 전체 점수에 따른 학습 강도 조정
            if overall_score < 0.5:
                # 점수가 낮은 경우 학습 강도 감소
                self.learning_config['cycle_timeout'] = min(600, self.learning_config['cycle_timeout'] + 60)
                self.learning_config['meta_learning_interval'] = min(7200, self.learning_config['meta_learning_interval'] + 600)
                logger.warning("전체 점수가 낮아 학습 강도를 감소시킵니다")
                
            elif overall_score > 0.8:
                # 점수가 높은 경우 학습 강도 증가
                self.learning_config['cycle_timeout'] = max(120, self.learning_config['cycle_timeout'] - 30)
                self.learning_config['meta_learning_interval'] = max(1800, self.learning_config['meta_learning_interval'] - 300)
                logger.info("전체 점수가 높아 학습 강도를 증가시킵니다")
            
            # 중요 이슈에 따른 특별 조정
            for issue in assessment_result.critical_issues:
                if "CPU 사용률" in issue:
                    self.learning_config['cycle_timeout'] = min(600, self.learning_config['cycle_timeout'] + 60)
                    logger.warning("CPU 사용률 문제로 학습 강도를 감소시킵니다")
                    
                elif "메모리 사용률" in issue:
                    self.learning_config['meta_learning_interval'] = min(7200, self.learning_config['meta_learning_interval'] + 600)
                    logger.warning("메모리 사용률 문제로 메타 학습 간격을 늘립니다")
                    
                elif "오류율" in issue:
                    self.learning_config['max_failure_streak'] = max(3, self.learning_config['max_failure_streak'] - 1)
                    logger.warning("오류율 문제로 실패 허용 횟수를 감소시킵니다")
            
            # 개선 우선순위에 따른 조정
            for priority in assessment_result.improvement_priorities:
                if "학습" in priority:
                    self.learning_config['min_improvement_threshold'] = max(0.05, self.learning_config['min_improvement_threshold'] - 0.01)
                    logger.info("학습 개선을 위해 개선 임계값을 조정합니다")
                    
        except Exception as e:
            logger.error(f"학습 전략 조정 중 오류: {e}")

    def _run_goal_oriented_thinking_cycle(self):
        """목표 지향적 사고 사이클을 실행합니다."""
        try:
            logger.info("목표 지향적 사고 사이클 시작")
            
            # 새로운 목표 생성
            new_goals = self.goal_oriented_thinking.generate_goals()
            
            if new_goals:
                logger.info(f"새로운 목표 {len(new_goals)}개 생성됨")
                for goal in new_goals:
                    logger.info(f"목표: {goal.title} ({goal.category.value})")
                    # 목표를 활성 목표 목록에 추가
                    self.goal_oriented_thinking.active_goals.append(goal)
                    
                    # 목표 실행 계획 생성
                    plan = self.goal_oriented_thinking.create_execution_plan(goal)
                    if plan:
                        logger.info(f"목표 실행 계획 생성: {plan.plan_id}")
            
            logger.info("목표 지향적 사고 사이클 완료")
            
        except Exception as e:
            logger.error(f"목표 지향적 사고 사이클 실행 중 오류: {e}")

    def _should_run_emotional_ethical_judgment(self) -> bool:
        """감정/윤리 판단 모듈이 실행되어야 하는지 결정합니다."""
        # 주기적으로 실행 (예: 10번째 사이클마다)
        return self.learning_cycle_count % 10 == 0

    def _run_emotional_ethical_judgment_cycle(self):
        """감정/윤리 판단 사이클을 실행합니다."""
        try:
            logger.info("감정/윤리 판단 사이클 시작")
            
            # 현재 학습 상황에 대한 감정/윤리 판단
            situation = "학습 루프 실행 중 - 전략 적용 및 결과 평가"
            result = self.emotional_ethical_judgment.make_judgment(
                situation=situation,
                judgment_type=self.emotional_ethical_judgment.JudgmentType.HYBRID
            )
            
            if result:
                logger.info(f"감정/윤리 판단 완료: {result.decision}")
                logger.info(f"점수 - 윤리적: {result.ethical_score:.2f}, 감정적: {result.emotional_score:.2f}, 전체: {result.overall_score:.2f}")
                
                # 판단 결과를 메모리에 저장
                self.memory_sync.store_experience(
                    experience_type=MemoryType.LEARNING_EXPERIENCE,
                    content=f"감정/윤리 판단: {result.decision} - {result.reasoning}",
                    metadata={
                        "judgment_type": result.judgment_type.value,
                        "ethical_score": result.ethical_score,
                        "emotional_score": result.emotional_score,
                        "overall_score": result.overall_score,
                        "confidence": result.confidence.value
                    }
                )
            
            logger.info("감정/윤리 판단 사이클 완료")
            
        except Exception as e:
            logger.error(f"감정/윤리 판단 사이클 실행 중 오류: {e}")

    def _run_autonomous_goal_setting_cycle(self):
        """자율 목표 설정 사이클을 실행합니다."""
        try:
            logger.info("자율 목표 설정 사이클 시작")
            
            # 자율 목표 생성
            new_autonomous_goals = self.autonomous_goal_setting.generate_autonomous_goals()
            
            if new_autonomous_goals:
                logger.info(f"새로운 자율 목표 {len(new_autonomous_goals)}개 생성됨")
                
                # 목표 우선순위 결정
                prioritization_result = self.autonomous_goal_setting.prioritize_goals(new_autonomous_goals)
                
                if prioritization_result:
                    logger.info(f"목표 우선순위 결정 완료: {prioritization_result.reasoning}")
                    
                    # 상위 목표들을 메모리에 저장
                    for goal in prioritization_result.goals[:3]:  # 상위 3개 목표
                        self.memory_sync.store_experience(
                            experience_type=MemoryType.LEARNING_EXPERIENCE,
                            content=f"자율 목표: {goal.title} - {goal.description}",
                            metadata={
                                "goal_id": goal.goal_id,
                                "source": goal.source.value,
                                "priority_score": goal.priority_score,
                                "overall_score": goal.overall_score
                            }
                        )
            
            logger.info("자율 목표 설정 사이클 완료")
            
        except Exception as e:
            logger.error(f"자율 목표 설정 사이클 실행 중 오류: {e}")

    def _run_creativity_enhancement_cycle(self):
        """창의성 고도화 사이클을 실행합니다."""
        try:
            logger.info("창의성 고도화 사이클 시작")
            
            # 창의성 세션 실행
            session = self.advanced_creativity_system.run_creativity_session(
                context="시스템 성능 및 기능 개선",
                duration_minutes=15
            )
            
            if session:
                logger.info(f"창의성 세션 완료: {len(session.ideas_generated)}개 아이디어 생성")
                logger.info(f"세션 품질: {session.session_quality:.2f}")
                
                # 창의적 아이디어들을 메모리에 저장
                for idea in session.ideas_generated[:5]:  # 상위 5개 아이디어
                    self.memory_sync.store_experience(
                        experience_type=MemoryType.LEARNING_EXPERIENCE,
                        content=f"창의적 아이디어: {idea.title} - {idea.description}",
                        metadata={
                            "idea_id": idea.idea_id,
                            "creativity_type": idea.creativity_type.value,
                            "technique_used": idea.technique_used.value,
                            "overall_score": idea.overall_score
                        }
                    )
                
                # 인사이트 발견
                if session.insights_discovered:
                    logger.info(f"발견된 인사이트: {session.insights_discovered}")
            
            logger.info("창의성 고도화 사이클 완료")
            
        except Exception as e:
            logger.error(f"창의성 고도화 사이클 실행 중 오류: {e}")

    def _execute_learning_cycle(self, context: Optional[Dict[str, Any]]) -> LearningResult:
        """단일 학습 사이클을 실행합니다."""
        stage_results = {}
        
        try:
            # 1단계: 모방
            logger.info("1단계: 모방 시작")
            self.current_cycle.current_stage = LearningStage.IMITATION
            imitation_result = self._execute_imitation_stage(context)
            stage_results[LearningStage.IMITATION] = imitation_result
            self.current_cycle.stages_completed.append(LearningStage.IMITATION)
            
            # 2단계: 반복
            logger.info("2단계: 반복 시작")
            self.current_cycle.current_stage = LearningStage.PRACTICE
            practice_result = self._execute_practice_stage(context)
            stage_results[LearningStage.PRACTICE] = practice_result
            self.current_cycle.stages_completed.append(LearningStage.PRACTICE)
            
            # 3단계: 피드백
            logger.info("3단계: 피드백 시작")
            self.current_cycle.current_stage = LearningStage.FEEDBACK
            feedback_result = self._execute_feedback_stage(practice_result, context)
            stage_results[LearningStage.FEEDBACK] = feedback_result
            self.current_cycle.stages_completed.append(LearningStage.FEEDBACK)
            
            # 4단계: 도전
            logger.info("4단계: 도전 시작")
            self.current_cycle.current_stage = LearningStage.CHALLENGE
            challenge_result = self._execute_challenge_stage(feedback_result, context)
            stage_results[LearningStage.CHALLENGE] = challenge_result
            self.current_cycle.stages_completed.append(LearningStage.CHALLENGE)
            
            # 5단계: 개선
            logger.info("5단계: 개선 시작")
            self.current_cycle.current_stage = LearningStage.IMPROVEMENT
            improvement_result = self._execute_improvement_stage(challenge_result, context)
            stage_results[LearningStage.IMPROVEMENT] = improvement_result
            self.current_cycle.stages_completed.append(LearningStage.IMPROVEMENT)
            
            # 전체 성과 계산
            overall_performance = self._calculate_overall_performance(stage_results)
            improvement_score = self._calculate_improvement_score(stage_results)
            recommendations = self._generate_recommendations(stage_results)
            next_actions = self._determine_next_actions(stage_results)
            
            # 전략 생존 판단
            survival_decision = self._evaluate_strategy_survival(overall_performance, context)
            
            # 사이클 완료
            self.current_cycle.end_time = datetime.now()
            self.current_cycle.performance_metrics = {
                'overall_performance': overall_performance,
                'improvement_score': improvement_score,
                'survival_action': survival_decision.action.value if survival_decision else 'unknown'
            }
            self.current_cycle.success = improvement_score > 0.0
            
            if improvement_result.get('modified_strategy'):
                self.current_cycle.modified_strategy = improvement_result['modified_strategy']
            
            result = LearningResult(
                cycle=self.current_cycle,
                stage_results=stage_results,
                overall_performance=overall_performance,
                improvement_score=improvement_score,
                recommendations=recommendations,
                next_actions=next_actions
            )
            
            logger.info(f"학습 사이클 완료: 성과 {overall_performance:.2f}, 개선점수 {improvement_score:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"학습 사이클 실행 실패: {e}")
            self.current_cycle.end_time = datetime.now()
            self.current_cycle.success = False
            
            return LearningResult(
                cycle=self.current_cycle,
                stage_results=stage_results,
                overall_performance=0.0,
                improvement_score=0.0,
                recommendations=["학습 사이클 실행 중 오류 발생"],
                next_actions=["오류 수정 후 재시도"]
            )

# 싱글톤 인스턴스
_learning_loop_manager = None

def get_learning_loop_manager() -> LearningLoopManager:
    """LearningLoopManager 싱글톤 인스턴스 반환"""
    global _learning_loop_manager
    if _learning_loop_manager is None:
        _learning_loop_manager = LearningLoopManager()
    return _learning_loop_manager 