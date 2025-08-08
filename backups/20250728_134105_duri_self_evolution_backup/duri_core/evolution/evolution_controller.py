#!/usr/bin/env python3
"""
Evolution Controller - 진화 제어 시스템

행동 실행, 결과 기록, 경험 학습을 통합 관리하여 시스템의 진화를 제어합니다.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from duri_common.logger import get_logger
from .action_executor import ActionExecutor, ExecutionContext, ExecutionResult
from .result_recorder import ResultRecorder, RecordedResult
from .experience_manager import ExperienceManager, LearningInsight

logger = get_logger("duri_evolution.evolution_controller")


class EvolutionState(Enum):
    """진화 상태"""
    IDLE = "idle"
    LEARNING = "learning"
    ADAPTING = "adapting"
    OPTIMIZING = "optimizing"


@dataclass
class EvolutionSession:
    """진화 세션"""
    session_id: str
    start_time: str
    end_time: Optional[str] = None
    total_actions: int = 0
    successful_actions: int = 0
    learning_insights: int = 0
    state: str = "idle"
    metadata: Dict[str, Any] = None


@dataclass
class EvolutionMetrics:
    """진화 메트릭"""
    total_sessions: int
    total_actions: int
    success_rate: float
    learning_rate: float
    adaptation_score: float
    last_updated: str
    metadata: Dict[str, Any]


class EvolutionController:
    """진화 제어기"""
    
    def __init__(self, data_dir: str = "evolution_data"):
        """
        EvolutionController 초기화
        
        Args:
            data_dir (str): 데이터 저장 디렉토리
        """
        self.data_dir = data_dir
        self.sessions_dir = os.path.join(data_dir, "sessions")
        self.metrics_dir = os.path.join(data_dir, "metrics")
        
        # 컴포넌트 초기화
        self.action_executor = ActionExecutor()
        self.result_recorder = ResultRecorder(data_dir)
        self.experience_manager = ExperienceManager(data_dir)
        
        # 상태 관리
        self.current_session: Optional[EvolutionSession] = None
        self.evolution_state = EvolutionState.IDLE
        
        # 디렉토리 생성
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.metrics_dir, exist_ok=True)
        
        logger.info(f"EvolutionController 초기화 완료: {data_dir}")
    
    def start_evolution_session(self, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        진화 세션 시작
        
        Args:
            metadata (Dict[str, Any], optional): 세션 메타데이터
        
        Returns:
            str: 세션 ID
        """
        session_id = str(uuid.uuid4())
        
        self.current_session = EvolutionSession(
            session_id=session_id,
            start_time=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        self.evolution_state = EvolutionState.LEARNING
        
        logger.info(f"진화 세션 시작: {session_id}")
        return session_id
    
    def end_evolution_session(self) -> Optional[EvolutionSession]:
        """
        진화 세션 종료
        
        Returns:
            Optional[EvolutionSession]: 종료된 세션 정보
        """
        if not self.current_session:
            logger.warning("활성 세션이 없습니다.")
            return None
        
        self.current_session.end_time = datetime.now().isoformat()
        self.current_session.state = "completed"
        
        # 세션 저장
        self._save_session(self.current_session)
        
        # 메트릭 업데이트
        self._update_evolution_metrics(self.current_session)
        
        session = self.current_session
        self.current_session = None
        self.evolution_state = EvolutionState.IDLE
        
        logger.info(f"진화 세션 종료: {session.session_id}")
        return session
    
    def execute_evolution_cycle(
        self,
        emotion: str,
        context: Dict[str, Any],
        use_experience: bool = True
    ) -> Tuple[ExecutionResult, RecordedResult, List[LearningInsight]]:
        """
        진화 사이클 실행
        
        Args:
            emotion (str): 현재 감정
            context (Dict[str, Any]): 실행 컨텍스트
            use_experience (bool): 경험 활용 여부
        
        Returns:
            Tuple[ExecutionResult, RecordedResult, List[LearningInsight]]: 실행 결과, 기록 결과, 학습 인사이트
        """
        if not self.current_session:
            logger.warning("진화 세션이 시작되지 않았습니다.")
            return None, None, []
        
        try:
            # 1. 경험 기반 액션 추천
            recommended_action = None
            if use_experience:
                recommendation = self.experience_manager.get_recommended_action(
                    emotion, context
                )
                if recommendation:
                    recommended_action, confidence = recommendation
                    logger.info(f"경험 기반 추천 액션: {recommended_action} (신뢰도: {confidence:.2f})")
            
            # 2. 실행 컨텍스트 생성
            execution_context = ExecutionContext(
                emotion=emotion,
                intensity=context.get('intensity', 0.5),
                confidence=context.get('confidence', 0.5),
                environment=context.get('environment'),
                user_context=context.get('user_context'),
                session_id=self.current_session.session_id
            )
            
            # 3. 액션 실행
            action_to_execute = recommended_action or context.get('action', 'reflect')
            execution_result = self.action_executor.execute_action(
                action_to_execute, 
                execution_context
            )
            
            # 4. 결과 기록
            recorded_result = self.result_recorder.record_execution_result(
                execution_result, 
                execution_context
            )
            
            # 5. 경험 학습
            learning_insights = self.experience_manager.process_experience(recorded_result)
            
            # 6. 세션 업데이트
            self.current_session.total_actions += 1
            if execution_result.success:
                self.current_session.successful_actions += 1
            self.current_session.learning_insights += len(learning_insights)
            
            logger.info(f"진화 사이클 완료: 액션={action_to_execute}, 성공={execution_result.success}, 인사이트={len(learning_insights)}개")
            
            return execution_result, recorded_result, learning_insights
            
        except Exception as e:
            logger.error(f"진화 사이클 실행 실패: {e}")
            return None, None, []
    
    def execute_adaptive_evolution_cycle(
        self,
        emotion: str,
        context: Dict[str, Any],
        learning_rate: float = 0.1
    ) -> Tuple[ExecutionResult, RecordedResult, List[LearningInsight], Dict[str, Any]]:
        """
        적응형 진화 사이클 실행
        
        Args:
            emotion (str): 현재 감정
            context (Dict[str, Any]): 실행 컨텍스트
            learning_rate (float): 학습률
        
        Returns:
            Tuple[ExecutionResult, RecordedResult, List[LearningInsight], Dict[str, Any]]: 
            실행 결과, 기록 결과, 학습 인사이트, 진화 메타데이터
        """
        if not self.current_session:
            logger.warning("진화 세션이 시작되지 않았습니다.")
            return None, None, [], {}
        
        try:
            # 1. 현재 상태 분석
            current_metrics = self.get_evolution_metrics()
            session_progress = self.current_session.total_actions / max(1, current_metrics.total_actions)
            
            # 2. 적응형 파라미터 조정
            adaptive_params = self._calculate_adaptive_parameters(
                emotion, context, current_metrics, session_progress
            )
            
            # 3. 경험 활용도 동적 조정
            experience_utilization = self._calculate_experience_utilization(
                current_metrics, session_progress, learning_rate
            )
            
            # 4. 진화 사이클 실행
            execution_result, recorded_result, learning_insights = self.execute_evolution_cycle(
                emotion, context, use_experience=experience_utilization > 0.3
            )
            
            # 5. 진화 상태 업데이트
            evolution_metadata = self._update_evolution_state(
                execution_result, recorded_result, learning_insights, adaptive_params
            )
            
            # 6. 학습률 조정
            self._adjust_learning_rate(execution_result, learning_insights, learning_rate)
            
            logger.info(f"적응형 진화 사이클 완료: 경험활용도={experience_utilization:.2f}, 학습률={learning_rate:.2f}")
            
            return execution_result, recorded_result, learning_insights, evolution_metadata
            
        except Exception as e:
            logger.error(f"적응형 진화 사이클 실행 실패: {e}")
            return None, None, [], {}
    
    def _calculate_adaptive_parameters(
        self,
        emotion: str,
        context: Dict[str, Any],
        current_metrics: EvolutionMetrics,
        session_progress: float
    ) -> Dict[str, Any]:
        """적응형 파라미터 계산"""
        try:
            # 성공률 기반 파라미터 조정
            success_rate = current_metrics.success_rate
            adaptation_score = current_metrics.adaptation_score
            
            # 신뢰도 임계값 동적 조정
            if success_rate > 0.8:
                confidence_threshold = 0.6  # 높은 성공률에서는 더 낮은 임계값
            elif success_rate < 0.4:
                confidence_threshold = 0.8  # 낮은 성공률에서는 더 높은 임계값
            else:
                confidence_threshold = 0.7
            
            # 탐험률 계산 (성공률이 낮을수록 더 많이 탐험)
            exploration_rate = max(0.1, 1.0 - success_rate)
            
            # 세션 진행도에 따른 파라미터 조정
            if session_progress > 0.8:
                # 세션 후반부: 더 보수적
                confidence_threshold *= 1.1
                exploration_rate *= 0.8
            elif session_progress < 0.2:
                # 세션 초반부: 더 적극적
                confidence_threshold *= 0.9
                exploration_rate *= 1.2
            
            return {
                'confidence_threshold': min(0.95, confidence_threshold),
                'exploration_rate': min(0.5, exploration_rate),
                'adaptation_score': adaptation_score,
                'session_progress': session_progress
            }
            
        except Exception as e:
            logger.error(f"적응형 파라미터 계산 실패: {e}")
            return {
                'confidence_threshold': 0.7,
                'exploration_rate': 0.3,
                'adaptation_score': 0.5,
                'session_progress': session_progress
            }
    
    def _calculate_experience_utilization(
        self,
        current_metrics: EvolutionMetrics,
        session_progress: float,
        learning_rate: float
    ) -> float:
        """경험 활용도 계산"""
        try:
            # 기본 활용도 (학습률 기반)
            base_utilization = learning_rate
            
            # 데이터 양에 따른 조정
            if current_metrics.total_actions < 10:
                # 데이터가 적으면 경험 활용도 낮춤
                data_factor = 0.3
            elif current_metrics.total_actions > 100:
                # 데이터가 많으면 경험 활용도 높임
                data_factor = 1.2
            else:
                data_factor = 0.8
            
            # 성공률에 따른 조정
            success_factor = current_metrics.success_rate
            
            # 세션 진행도에 따른 조정
            if session_progress < 0.3:
                # 초반에는 경험 활용도 낮춤
                session_factor = 0.6
            elif session_progress > 0.7:
                # 후반에는 경험 활용도 높임
                session_factor = 1.1
            else:
                session_factor = 0.9
            
            utilization = base_utilization * data_factor * success_factor * session_factor
            return min(1.0, max(0.0, utilization))
            
        except Exception as e:
            logger.error(f"경험 활용도 계산 실패: {e}")
            return 0.5
    
    def _update_evolution_state(
        self,
        execution_result: ExecutionResult,
        recorded_result: RecordedResult,
        learning_insights: List[LearningInsight],
        adaptive_params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """진화 상태 업데이트"""
        try:
            # 진화 상태 결정
            if len(learning_insights) > 2:
                self.evolution_state = EvolutionState.LEARNING
            elif execution_result and execution_result.success:
                if adaptive_params['adaptation_score'] > 0.7:
                    self.evolution_state = EvolutionState.OPTIMIZING
                else:
                    self.evolution_state = EvolutionState.ADAPTING
            else:
                self.evolution_state = EvolutionState.LEARNING
            
            # 진화 메타데이터 생성
            evolution_metadata = {
                'evolution_state': self.evolution_state.value,
                'adaptive_params': adaptive_params,
                'learning_insights_count': len(learning_insights),
                'execution_success': execution_result.success if execution_result else False,
                'timestamp': datetime.now().isoformat()
            }
            
            return evolution_metadata
            
        except Exception as e:
            logger.error(f"진화 상태 업데이트 실패: {e}")
            return {}
    
    def _adjust_learning_rate(
        self,
        execution_result: ExecutionResult,
        learning_insights: List[LearningInsight],
        current_learning_rate: float
    ):
        """학습률 조정"""
        try:
            # 성공/실패에 따른 학습률 조정
            if execution_result and execution_result.success:
                # 성공 시 학습률 감소 (더 안정적)
                adjustment = -0.02
            else:
                # 실패 시 학습률 증가 (더 적극적)
                adjustment = 0.05
            
            # 인사이트 수에 따른 조정
            insight_adjustment = len(learning_insights) * 0.01
            
            # 새로운 학습률 계산
            new_learning_rate = current_learning_rate + adjustment + insight_adjustment
            new_learning_rate = max(0.05, min(0.3, new_learning_rate))  # 0.05 ~ 0.3 범위
            
            # 메트릭 업데이트
            self._update_learning_rate_metric(new_learning_rate)
            
        except Exception as e:
            logger.error(f"학습률 조정 실패: {e}")
    
    def _update_learning_rate_metric(self, learning_rate: float):
        """학습률 메트릭 업데이트"""
        try:
            metrics_file = os.path.join(self.metrics_dir, "evolution_metrics.json")
            
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metrics = EvolutionMetrics(**data)
            else:
                metrics = EvolutionMetrics(
                    total_sessions=0,
                    total_actions=0,
                    success_rate=0.0,
                    learning_rate=learning_rate,
                    adaptation_score=0.0,
                    last_updated=datetime.now().isoformat(),
                    metadata={}
                )
            
            metrics.learning_rate = learning_rate
            metrics.last_updated = datetime.now().isoformat()
            
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"학습률 메트릭 업데이트 실패: {e}")
    
    def get_evolution_metrics(self) -> EvolutionMetrics:
        """
        진화 메트릭 조회
        
        Returns:
            EvolutionMetrics: 진화 메트릭
        """
        try:
            metrics_file = os.path.join(self.metrics_dir, "evolution_metrics.json")
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return EvolutionMetrics(**data)
        except Exception as e:
            logger.error(f"진화 메트릭 조회 실패: {e}")
        
        # 기본 메트릭 반환
        return EvolutionMetrics(
            total_sessions=0,
            total_actions=0,
            success_rate=0.0,
            learning_rate=0.0,
            adaptation_score=0.0,
            last_updated=datetime.now().isoformat(),
            metadata={}
        )
    
    def get_session_history(
        self,
        limit: int = 20
    ) -> List[EvolutionSession]:
        """
        세션 히스토리 조회
        
        Args:
            limit (int): 조회할 최대 개수
        
        Returns:
            List[EvolutionSession]: 세션 히스토리
        """
        sessions = []
        
        try:
            for filename in os.listdir(self.sessions_dir):
                if not filename.endswith('.json'):
                    continue
                
                filepath = os.path.join(self.sessions_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    session = EvolutionSession(**data)
                    sessions.append(session)
            
            # 시작 시간순 정렬 (최신순)
            sessions.sort(key=lambda x: x.start_time, reverse=True)
            return sessions[:limit]
            
        except Exception as e:
            logger.error(f"세션 히스토리 조회 실패: {e}")
            return []
    
    def get_current_session(self) -> Optional[EvolutionSession]:
        """
        현재 세션 조회
        
        Returns:
            Optional[EvolutionSession]: 현재 세션 정보
        """
        return self.current_session
    
    def get_evolution_state(self) -> EvolutionState:
        """
        진화 상태 조회
        
        Returns:
            EvolutionState: 현재 진화 상태
        """
        return self.evolution_state
    
    def _save_session(self, session: EvolutionSession):
        """세션 저장"""
        try:
            filename = f"session_{session.session_id}.json"
            filepath = os.path.join(self.sessions_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(session), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"세션 저장 실패: {e}")
    
    def _update_evolution_metrics(self, session: EvolutionSession):
        """진화 메트릭 업데이트"""
        try:
            metrics_file = os.path.join(self.metrics_dir, "evolution_metrics.json")
            
            # 기존 메트릭 읽기
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    metrics = EvolutionMetrics(**data)
            else:
                metrics = EvolutionMetrics(
                    total_sessions=0,
                    total_actions=0,
                    success_rate=0.0,
                    learning_rate=0.0,
                    adaptation_score=0.0,
                    last_updated=datetime.now().isoformat(),
                    metadata={}
                )
            
            # 메트릭 업데이트
            metrics.total_sessions += 1
            metrics.total_actions += session.total_actions
            
            # 성공률 계산
            if metrics.total_actions > 0:
                metrics.success_rate = (
                    (metrics.success_rate * (metrics.total_actions - session.total_actions) + session.successful_actions)
                    / metrics.total_actions
                )
            
            # 학습률 계산
            if session.total_actions > 0:
                session_learning_rate = session.learning_insights / session.total_actions
                metrics.learning_rate = (
                    (metrics.learning_rate * (metrics.total_sessions - 1) + session_learning_rate)
                    / metrics.total_sessions
                )
            
            # 적응 점수 계산 (간단한 구현)
            if session.total_actions > 0:
                session_adaptation_score = session.successful_actions / session.total_actions
                metrics.adaptation_score = (
                    (metrics.adaptation_score * (metrics.total_sessions - 1) + session_adaptation_score)
                    / metrics.total_sessions
                )
            
            metrics.last_updated = datetime.now().isoformat()
            
            # 메트릭 저장
            with open(metrics_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(metrics), f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"진화 메트릭 업데이트 실패: {e}")
    
    def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """
        종합 통계 조회
        
        Returns:
            Dict[str, Any]: 종합 통계
        """
        try:
            # 각 컴포넌트의 통계 수집
            action_stats = self.action_executor.get_execution_statistics()
            recorder_stats = self.result_recorder.get_statistics()
            experience_stats = self.experience_manager.get_statistics()
            evolution_metrics = self.get_evolution_metrics()
            
            return {
                'action_executor': action_stats,
                'result_recorder': recorder_stats,
                'experience_manager': experience_stats,
                'evolution_metrics': asdict(evolution_metrics),
                'current_session': asdict(self.current_session) if self.current_session else None,
                'evolution_state': self.evolution_state.value
            }
            
        except Exception as e:
            logger.error(f"종합 통계 조회 실패: {e}")
            return {}
    
    def get_evolution_insights(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        진화 인사이트 조회
        
        Args:
            limit (int): 조회할 최대 개수
        
        Returns:
            List[Dict[str, Any]]: 진화 인사이트 목록
        """
        insights = []
        
        try:
            # 1. 경험 패턴 분석
            patterns = self.experience_manager.get_experience_patterns(limit=limit)
            for pattern in patterns:
                if pattern.confidence_level > 0.7:
                    insights.append({
                        'type': 'pattern_insight',
                        'title': f"{pattern.emotion} 감정의 {pattern.action} 액션 패턴",
                        'description': f"성공률 {pattern.success_rate:.1%}, 신뢰도 {pattern.confidence_level:.1%}",
                        'confidence': pattern.confidence_level,
                        'data': asdict(pattern)
                    })
            
            # 2. 학습 인사이트 분석
            learning_insights = self.experience_manager.get_learning_insights(limit=limit)
            for insight in learning_insights:
                if insight.confidence > 0.6:
                    insights.append({
                        'type': 'learning_insight',
                        'title': f"{insight.insight_type} 인사이트",
                        'description': insight.description,
                        'confidence': insight.confidence,
                        'data': asdict(insight)
                    })
            
            # 3. 진화 메트릭 분석
            metrics = self.get_evolution_metrics()
            if metrics.total_actions > 0:
                insights.append({
                    'type': 'evolution_metric',
                    'title': "진화 진행 상황",
                    'description': f"총 {metrics.total_actions}개 액션, 성공률 {metrics.success_rate:.1%}, 학습률 {metrics.learning_rate:.1%}",
                    'confidence': 1.0,
                    'data': asdict(metrics)
                })
            
            # 신뢰도순 정렬
            insights.sort(key=lambda x: x['confidence'], reverse=True)
            return insights[:limit]
            
        except Exception as e:
            logger.error(f"진화 인사이트 조회 실패: {e}")
            return []
    
    def reset_evolution_data(self, confirm: bool = False) -> bool:
        """
        진화 데이터 초기화
        
        Args:
            confirm (bool): 초기화 확인
        
        Returns:
            bool: 초기화 성공 여부
        """
        if not confirm:
            logger.warning("진화 데이터 초기화를 위해서는 confirm=True를 설정해야 합니다.")
            return False
        
        try:
            # 현재 세션 종료
            if self.current_session:
                self.end_evolution_session()
            
            # 데이터 디렉토리 초기화
            import shutil
            if os.path.exists(self.data_dir):
                shutil.rmtree(self.data_dir)
                os.makedirs(self.data_dir, exist_ok=True)
            
            # 하위 디렉토리 재생성
            os.makedirs(self.sessions_dir, exist_ok=True)
            os.makedirs(self.metrics_dir, exist_ok=True)
            
            # 컴포넌트 재초기화
            self.result_recorder = ResultRecorder(self.data_dir)
            self.experience_manager = ExperienceManager(self.data_dir)
            
            logger.info("진화 데이터 초기화 완료")
            return True
            
        except Exception as e:
            logger.error(f"진화 데이터 초기화 실패: {e}")
            return False
    
    def export_evolution_data(self, export_path: str) -> bool:
        """
        진화 데이터 내보내기
        
        Args:
            export_path (str): 내보낼 경로
        
        Returns:
            bool: 내보내기 성공 여부
        """
        try:
            import shutil
            import zipfile
            
            # 임시 디렉토리 생성
            temp_dir = os.path.join(export_path, "duri_evolution_export")
            os.makedirs(temp_dir, exist_ok=True)
            
            # 데이터 복사
            if os.path.exists(self.data_dir):
                shutil.copytree(self.data_dir, os.path.join(temp_dir, "data"))
            
            # 메타데이터 생성
            metadata = {
                'export_timestamp': datetime.now().isoformat(),
                'evolution_metrics': asdict(self.get_evolution_metrics()),
                'current_session': asdict(self.current_session) if self.current_session else None,
                'evolution_state': self.evolution_state.value
            }
            
            with open(os.path.join(temp_dir, "metadata.json"), 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            # ZIP 파일 생성
            zip_path = f"{export_path}/duri_evolution_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, temp_dir)
                        zipf.write(file_path, arcname)
            
            # 임시 디렉토리 삭제
            shutil.rmtree(temp_dir)
            
            logger.info(f"진화 데이터 내보내기 완료: {zip_path}")
            return True
            
        except Exception as e:
            logger.error(f"진화 데이터 내보내기 실패: {e}")
            return False

    def run_loop(self, emotion: str, action: str):
        """
        감정과 행동을 받아서 실행하고 결과를 저장하고 학습
        Args:
            emotion (str): 감정
            action (str): 행동
        Returns:
            dict: 실행 결과
        """
        try:
            # 1. ActionExecutor로 행동 실행
            result = self.action_executor.execute(emotion, action)
            
            # 2. ResultRecorder에 결과 저장
            self.result_recorder.write_result(emotion, action, result)
            
            # 3. ExperienceManager에 통계 업데이트 (success/fail 결과 전달)
            success = result.get('success', False)
            self.experience_manager.update_stats(emotion, action, success)
            
            logger.info(f"진화 루프 완료: {emotion} -> {action} -> {'성공' if success else '실패'}")
            return result
            
        except Exception as e:
            logger.error(f"진화 루프 실행 실패: {e}")
            # 실패 시에도 기본 결과 반환
            return {
                'success': False,
                'details': f"실행 실패: {str(e)}",
                'error': True
            }

    def get_experience_stats(self, emotion: str = None, action: str = None):
        """
        경험 통계 조회
        Args:
            emotion (str, optional): 특정 감정 필터링
            action (str, optional): 특정 행동 필터링
        Returns:
            dict: 경험 통계
        """
        return self.experience_manager.get_stats(emotion, action) 