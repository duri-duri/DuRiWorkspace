"""
DuRi 판단 흐름 추적 로깅 계층 (JudgmentTraceSystem)

DuRi의 모든 판단 과정을 상세히 추적하고 로깅하는 시스템입니다.
"""

import logging
import uuid
import time
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict
import traceback

logger = logging.getLogger(__name__)

class TraceLevel(Enum):
    """추적 수준"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class JudgmentType(Enum):
    """판단 유형"""
    EMOTIONAL = "emotional"
    ETHICAL = "ethical"
    LOGICAL = "logical"
    CREATIVE = "creative"
    STRATEGIC = "strategic"
    AUTONOMOUS = "autonomous"

class TraceStatus(Enum):
    """추적 상태"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class JudgmentContext:
    """판단 맥락"""
    context_id: str
    timestamp: datetime
    judgment_type: JudgmentType
    input_data: Dict[str, Any]
    external_factors: Dict[str, Any] = field(default_factory=dict)
    user_context: Optional[str] = None
    system_state: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JudgmentStep:
    """판단 단계"""
    step_id: str
    step_name: str
    timestamp: datetime
    duration: timedelta
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    reasoning: str
    confidence_score: float  # 0.0 ~ 1.0
    trace_level: TraceLevel
    status: TraceStatus
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class JudgmentTrace:
    """판단 추적"""
    trace_id: str
    judgment_id: str
    start_time: datetime
    judgment_type: JudgmentType
    context: JudgmentContext
    end_time: Optional[datetime] = None
    steps: List[JudgmentStep] = field(default_factory=list)
    final_decision: Optional[str] = None
    final_confidence: float = 0.0
    total_duration: timedelta = field(default_factory=lambda: timedelta(0))
    status: TraceStatus = TraceStatus.STARTED
    error_summary: Optional[str] = None
    performance_metrics: Dict[str, Any] = field(default_factory=dict)

@dataclass
class TraceStatistics:
    """추적 통계"""
    total_traces: int
    successful_traces: int
    failed_traces: int
    average_duration: timedelta
    judgment_type_distribution: Dict[str, int]
    error_distribution: Dict[str, int]
    performance_trends: Dict[str, List[float]]

class JudgmentTraceSystem:
    """DuRi 판단 흐름 추적 로깅 계층"""
    
    def __init__(self):
        """JudgmentTraceSystem 초기화"""
        self.active_traces: Dict[str, JudgmentTrace] = {}
        self.completed_traces: List[JudgmentTrace] = []
        self.trace_statistics: TraceStatistics = None
        
        # 추적 설정
        self.trace_config = {
            'enable_detailed_logging': True,
            'enable_performance_tracking': True,
            'enable_error_tracking': True,
            'max_trace_history': 1000,
            'trace_retention_days': 30
        }
        
        # 성능 메트릭
        self.performance_metrics = {
            'total_judgments': 0,
            'successful_judgments': 0,
            'failed_judgments': 0,
            'average_processing_time': 0.0,
            'peak_processing_time': 0.0
        }
        
        logger.info("JudgmentTraceSystem 초기화 완료")
    
    def start_judgment_trace(self, judgment_id: str, judgment_type: JudgmentType, 
                           context_data: Dict[str, Any], user_context: Optional[str] = None) -> str:
        """판단 추적을 시작합니다."""
        try:
            trace_id = f"trace_{uuid.uuid4().hex[:8]}"
            start_time = datetime.now()
            
            # 판단 맥락 생성
            context = JudgmentContext(
                context_id=f"context_{uuid.uuid4().hex[:8]}",
                timestamp=start_time,
                judgment_type=judgment_type,
                input_data=context_data,
                user_context=user_context,
                system_state=self._capture_system_state()
            )
            
            # 판단 추적 생성
            trace = JudgmentTrace(
                trace_id=trace_id,
                judgment_id=judgment_id,
                start_time=start_time,
                judgment_type=judgment_type,
                context=context,
                status=TraceStatus.STARTED
            )
            
            self.active_traces[trace_id] = trace
            
            # 상세 로깅
            if self.trace_config['enable_detailed_logging']:
                logger.info(f"판단 추적 시작: {trace_id} (유형: {judgment_type.value})")
            
            return trace_id
            
        except Exception as e:
            logger.error(f"판단 추적 시작 실패: {e}")
            return None
    
    def add_judgment_step(self, trace_id: str, step_name: str, input_data: Dict[str, Any],
                         output_data: Dict[str, Any], reasoning: str, confidence_score: float,
                         trace_level: TraceLevel = TraceLevel.INFO) -> bool:
        """판단 단계를 추가합니다."""
        try:
            if trace_id not in self.active_traces:
                logger.error(f"추적 ID를 찾을 수 없음: {trace_id}")
                return False
            
            trace = self.active_traces[trace_id]
            step_start_time = datetime.now()
            
            # 단계 생성
            step = JudgmentStep(
                step_id=f"step_{uuid.uuid4().hex[:8]}",
                step_name=step_name,
                timestamp=step_start_time,
                duration=timedelta(0),  # 나중에 계산
                input_data=input_data,
                output_data=output_data,
                reasoning=reasoning,
                confidence_score=confidence_score,
                trace_level=trace_level,
                status=TraceStatus.COMPLETED
            )
            
            # 단계 추가
            trace.steps.append(step)
            trace.status = TraceStatus.IN_PROGRESS
            
            # 상세 로깅
            if self.trace_config['enable_detailed_logging']:
                logger.info(f"판단 단계 추가: {trace_id} - {step_name} (신뢰도: {confidence_score:.2f})")
            
            return True
            
        except Exception as e:
            logger.error(f"판단 단계 추가 실패: {e}")
            return False
    
    def add_error_step(self, trace_id: str, step_name: str, error_message: str,
                      input_data: Dict[str, Any] = None) -> bool:
        """오류 단계를 추가합니다."""
        try:
            if trace_id not in self.active_traces:
                logger.error(f"추적 ID를 찾을 수 없음: {trace_id}")
                return False
            
            trace = self.active_traces[trace_id]
            step_start_time = datetime.now()
            
            # 오류 단계 생성
            step = JudgmentStep(
                step_id=f"error_step_{uuid.uuid4().hex[:8]}",
                step_name=step_name,
                timestamp=step_start_time,
                duration=timedelta(0),
                input_data=input_data or {},
                output_data={},
                reasoning=f"오류 발생: {error_message}",
                confidence_score=0.0,
                trace_level=TraceLevel.ERROR,
                status=TraceStatus.FAILED,
                error_message=error_message
            )
            
            # 단계 추가
            trace.steps.append(step)
            trace.status = TraceStatus.FAILED
            trace.error_summary = error_message
            
            # 오류 로깅
            if self.trace_config['enable_error_tracking']:
                logger.error(f"판단 오류: {trace_id} - {step_name}: {error_message}")
            
            return True
            
        except Exception as e:
            logger.error(f"오류 단계 추가 실패: {e}")
            return False
    
    def complete_judgment_trace(self, trace_id: str, final_decision: str, 
                              final_confidence: float) -> bool:
        """판단 추적을 완료합니다."""
        try:
            if trace_id not in self.active_traces:
                logger.error(f"추적 ID를 찾을 수 없음: {trace_id}")
                return False
            
            trace = self.active_traces[trace_id]
            end_time = datetime.now()
            
            # 단계별 지속 시간 계산
            for i, step in enumerate(trace.steps):
                if i == 0:
                    step.duration = step.timestamp - trace.start_time
                else:
                    step.duration = step.timestamp - trace.steps[i-1].timestamp
            
            # 최종 결과 설정
            trace.end_time = end_time
            trace.final_decision = final_decision
            trace.final_confidence = final_confidence
            trace.total_duration = end_time - trace.start_time
            trace.status = TraceStatus.COMPLETED
            
            # 성능 메트릭 업데이트
            self._update_performance_metrics(trace)
            
            # 완료된 추적을 저장
            self.completed_traces.append(trace)
            del self.active_traces[trace_id]
            
            # 히스토리 관리
            self._manage_trace_history()
            
            # 상세 로깅
            if self.trace_config['enable_detailed_logging']:
                logger.info(f"판단 추적 완료: {trace_id} (결정: {final_decision}, 신뢰도: {final_confidence:.2f}, 소요시간: {trace.total_duration})")
            
            return True
            
        except Exception as e:
            logger.error(f"판단 추적 완료 실패: {e}")
            return False
    
    def get_trace_details(self, trace_id: str) -> Optional[JudgmentTrace]:
        """추적 상세 정보를 반환합니다."""
        try:
            # 활성 추적에서 검색
            if trace_id in self.active_traces:
                return self.active_traces[trace_id]
            
            # 완료된 추적에서 검색
            for trace in self.completed_traces:
                if trace.trace_id == trace_id:
                    return trace
            
            return None
            
        except Exception as e:
            logger.error(f"추적 상세 정보 조회 실패: {e}")
            return None
    
    def get_trace_statistics(self) -> TraceStatistics:
        """추적 통계를 반환합니다."""
        try:
            total_traces = len(self.completed_traces)
            successful_traces = sum(1 for trace in self.completed_traces if trace.status == TraceStatus.COMPLETED)
            failed_traces = sum(1 for trace in self.completed_traces if trace.status == TraceStatus.FAILED)
            
            # 평균 지속 시간 계산
            if total_traces > 0:
                total_duration_seconds = sum(trace.total_duration.total_seconds() for trace in self.completed_traces)
                average_duration_seconds = total_duration_seconds / total_traces
                average_duration = timedelta(seconds=average_duration_seconds)
            else:
                average_duration = timedelta(0)
            
            # 판단 유형 분포
            judgment_type_distribution = defaultdict(int)
            for trace in self.completed_traces:
                judgment_type_distribution[trace.judgment_type.value] += 1
            
            # 오류 분포
            error_distribution = defaultdict(int)
            for trace in self.completed_traces:
                if trace.error_summary:
                    error_distribution[trace.error_summary] += 1
            
            # 성능 트렌드 (최근 10개)
            recent_traces = self.completed_traces[-10:] if len(self.completed_traces) >= 10 else self.completed_traces
            performance_trends = {
                'duration': [trace.total_duration.total_seconds() for trace in recent_traces],
                'confidence': [trace.final_confidence for trace in recent_traces]
            }
            
            self.trace_statistics = TraceStatistics(
                total_traces=total_traces,
                successful_traces=successful_traces,
                failed_traces=failed_traces,
                average_duration=average_duration,
                judgment_type_distribution=dict(judgment_type_distribution),
                error_distribution=dict(error_distribution),
                performance_trends=performance_trends
            )
            
            return self.trace_statistics
            
        except Exception as e:
            logger.error(f"추적 통계 계산 실패: {e}")
            return None
    
    def export_trace_data(self, trace_id: str, format_type: str = "json") -> Optional[str]:
        """추적 데이터를 내보냅니다."""
        try:
            trace = self.get_trace_details(trace_id)
            if not trace:
                return None
            
            if format_type == "json":
                # dataclass를 dict로 변환
                trace_dict = asdict(trace)
                
                # datetime 객체를 문자열로 변환
                def convert_datetime(obj):
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    elif isinstance(obj, timedelta):
                        return str(obj)
                    return obj
                
                # 재귀적으로 datetime 변환
                def convert_recursive(data):
                    if isinstance(data, dict):
                        return {k: convert_recursive(v) for k, v in data.items()}
                    elif isinstance(data, list):
                        return [convert_recursive(item) for item in data]
                    else:
                        return convert_datetime(data)
                
                trace_dict = convert_recursive(trace_dict)
                return json.dumps(trace_dict, indent=2, ensure_ascii=False)
            
            return None
            
        except Exception as e:
            logger.error(f"추적 데이터 내보내기 실패: {e}")
            return None
    
    def _capture_system_state(self) -> Dict[str, Any]:
        """시스템 상태를 캡처합니다."""
        try:
            import psutil
            
            return {
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent,
                'timestamp': datetime.now().isoformat(),
                'active_traces_count': len(self.active_traces),
                'completed_traces_count': len(self.completed_traces)
            }
        except Exception as e:
            logger.error(f"시스템 상태 캡처 실패: {e}")
            return {}
    
    def _update_performance_metrics(self, trace: JudgmentTrace):
        """성능 메트릭을 업데이트합니다."""
        try:
            self.performance_metrics['total_judgments'] += 1
            
            if trace.status == TraceStatus.COMPLETED:
                self.performance_metrics['successful_judgments'] += 1
            else:
                self.performance_metrics['failed_judgments'] += 1
            
            # 처리 시간 업데이트
            processing_time = trace.total_duration.total_seconds()
            self.performance_metrics['average_processing_time'] = (
                (self.performance_metrics['average_processing_time'] * (self.performance_metrics['total_judgments'] - 1) + processing_time) /
                self.performance_metrics['total_judgments']
            )
            
            if processing_time > self.performance_metrics['peak_processing_time']:
                self.performance_metrics['peak_processing_time'] = processing_time
                
        except Exception as e:
            logger.error(f"성능 메트릭 업데이트 실패: {e}")
    
    def _manage_trace_history(self):
        """추적 히스토리를 관리합니다."""
        try:
            # 최대 히스토리 수 제한
            if len(self.completed_traces) > self.trace_config['max_trace_history']:
                # 오래된 추적 제거
                self.completed_traces = self.completed_traces[-self.trace_config['max_trace_history']:]
                
        except Exception as e:
            logger.error(f"추적 히스토리 관리 실패: {e}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 메트릭을 반환합니다."""
        return self.performance_metrics.copy()

# 싱글톤 인스턴스
_judgment_trace_system = None

def get_judgment_trace_system() -> JudgmentTraceSystem:
    """JudgmentTraceSystem 싱글톤 인스턴스 반환"""
    global _judgment_trace_system
    if _judgment_trace_system is None:
        _judgment_trace_system = JudgmentTraceSystem()
    return _judgment_trace_system 