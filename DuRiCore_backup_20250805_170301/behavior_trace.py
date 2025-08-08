#!/usr/bin/env python3
"""
DuRiCore Phase 5 - 행동 추적 시스템
Memory → Judgment → Action → Evolution 전체 루프 추적 및 메타데이터 관리
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import logging
import hashlib
import time
import uuid

logger = logging.getLogger(__name__)

class TraceStatus(Enum):
    """추적 상태 열거형"""
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TraceType(Enum):
    """추적 타입 열거형"""
    MEMORY_ACCESS = "memory_access"
    JUDGMENT_PROCESS = "judgment_process"
    ACTION_EXECUTION = "action_execution"
    EVOLUTION_UPDATE = "evolution_update"
    FULL_CYCLE = "full_cycle"

@dataclass
class TraceMetadata:
    """추적 메타데이터"""
    trace_id: str
    parent_trace_id: Optional[str]
    trace_type: TraceType
    status: TraceStatus
    input_hash: str
    output_hash: str
    response_version: str
    timestamp: datetime
    duration: float
    metadata: Dict[str, Any]

@dataclass
class MemoryTrace:
    """기억 추적"""
    memory_id: str
    access_type: str  # read, write, update, delete
    memory_type: str  # experience, knowledge, pattern, emotion
    importance_score: float
    access_count: int
    last_accessed: datetime
    associations: List[str]
    trace_metadata: TraceMetadata

@dataclass
class JudgmentTrace:
    """판단 추적"""
    judgment_id: str
    situation_type: str
    decision: str
    confidence: float
    reasoning: str
    alternatives: List[str]
    risk_assessment: Dict[str, float]
    ethical_score: float
    trace_metadata: TraceMetadata

@dataclass
class ActionTrace:
    """행동 추적"""
    action_id: str
    action_type: str
    behavior_type: str
    strategy: str
    priority: float
    success: bool
    effectiveness_score: float
    efficiency_score: float
    learning_points: List[str]
    trace_metadata: TraceMetadata

@dataclass
class EvolutionTrace:
    """진화 추적"""
    evolution_id: str
    evolution_type: str  # pattern_improvement, strategy_optimization, meta_learning
    improvement_score: float
    changes_applied: List[str]
    performance_impact: Dict[str, float]
    stability_score: float
    trace_metadata: TraceMetadata

@dataclass
class FullCycleTrace:
    """전체 사이클 추적"""
    cycle_id: str
    memory_trace: MemoryTrace
    judgment_trace: JudgmentTrace
    action_trace: ActionTrace
    evolution_trace: Optional[EvolutionTrace]
    cycle_duration: float
    overall_success: bool
    performance_metrics: Dict[str, float]
    trace_metadata: TraceMetadata

class BehaviorTracer:
    """행동 추적 시스템"""
    
    def __init__(self):
        self.trace_store = {}
        self.metadata_chain = {}
        self.performance_history = []
        self.evolution_patterns = {}
        
        # 추적 설정
        self.enable_detailed_tracing = True
        self.trace_retention_days = 30
        self.max_trace_size = 10000
        
        logger.info("행동 추적 시스템 초기화 완료")
    
    async def start_trace(self, trace_type: TraceType, input_data: Dict[str, Any], 
                         parent_trace_id: Optional[str] = None) -> str:
        """추적 시작"""
        try:
            trace_id = str(uuid.uuid4())
            input_hash = self._generate_hash(input_data)
            response_version = self._generate_version()
            
            metadata = TraceMetadata(
                trace_id=trace_id,
                parent_trace_id=parent_trace_id,
                trace_type=trace_type,
                status=TraceStatus.STARTED,
                input_hash=input_hash,
                output_hash="",  # 나중에 설정
                response_version=response_version,
                timestamp=datetime.now(),
                duration=0.0,
                metadata={"input_data": input_data}
            )
            
            self.trace_store[trace_id] = metadata
            self.metadata_chain[trace_id] = metadata
            
            logger.info(f"추적 시작: {trace_id} ({trace_type.value})")
            return trace_id
            
        except Exception as e:
            logger.error(f"추적 시작 실패: {e}")
            raise
    
    async def update_trace(self, trace_id: str, status: TraceStatus, 
                          output_data: Optional[Dict[str, Any]] = None,
                          additional_metadata: Optional[Dict[str, Any]] = None) -> None:
        """추적 업데이트"""
        try:
            if trace_id not in self.trace_store:
                raise ValueError(f"추적 ID를 찾을 수 없음: {trace_id}")
            
            trace = self.trace_store[trace_id]
            trace.status = status
            
            if output_data:
                trace.output_hash = self._generate_hash(output_data)
                trace.metadata["output_data"] = output_data
            
            if additional_metadata:
                trace.metadata.update(additional_metadata)
            
            # 지속 시간 계산
            if status in [TraceStatus.COMPLETED, TraceStatus.FAILED]:
                trace.duration = (datetime.now() - trace.timestamp).total_seconds()
            
            logger.info(f"추적 업데이트: {trace_id} -> {status.value}")
            
        except Exception as e:
            logger.error(f"추적 업데이트 실패: {e}")
            raise
    
    async def create_memory_trace(self, trace_id: str, memory_data: Dict[str, Any]) -> MemoryTrace:
        """기억 추적 생성"""
        try:
            metadata = self.trace_store[trace_id]
            
            memory_trace = MemoryTrace(
                memory_id=memory_data.get("memory_id", str(uuid.uuid4())),
                access_type=memory_data.get("access_type", "read"),
                memory_type=memory_data.get("memory_type", "experience"),
                importance_score=memory_data.get("importance_score", 0.0),
                access_count=memory_data.get("access_count", 1),
                last_accessed=datetime.now(),
                associations=memory_data.get("associations", []),
                trace_metadata=metadata
            )
            
            # 추적 저장
            self.trace_store[f"{trace_id}_memory"] = memory_trace
            
            return memory_trace
            
        except Exception as e:
            logger.error(f"기억 추적 생성 실패: {e}")
            raise
    
    async def create_judgment_trace(self, trace_id: str, judgment_data: Dict[str, Any]) -> JudgmentTrace:
        """판단 추적 생성"""
        try:
            metadata = self.trace_store[trace_id]
            
            judgment_trace = JudgmentTrace(
                judgment_id=judgment_data.get("judgment_id", str(uuid.uuid4())),
                situation_type=judgment_data.get("situation_type", "unknown"),
                decision=judgment_data.get("decision", ""),
                confidence=judgment_data.get("confidence", 0.0),
                reasoning=judgment_data.get("reasoning", ""),
                alternatives=judgment_data.get("alternatives", []),
                risk_assessment=judgment_data.get("risk_assessment", {}),
                ethical_score=judgment_data.get("ethical_score", 0.0),
                trace_metadata=metadata
            )
            
            # 추적 저장
            self.trace_store[f"{trace_id}_judgment"] = judgment_trace
            
            return judgment_trace
            
        except Exception as e:
            logger.error(f"판단 추적 생성 실패: {e}")
            raise
    
    async def create_action_trace(self, trace_id: str, action_data: Dict[str, Any]) -> ActionTrace:
        """행동 추적 생성"""
        try:
            metadata = self.trace_store[trace_id]
            
            action_trace = ActionTrace(
                action_id=action_data.get("action_id", str(uuid.uuid4())),
                action_type=action_data.get("action_type", "unknown"),
                behavior_type=action_data.get("behavior_type", "unknown"),
                strategy=action_data.get("strategy", "unknown"),
                priority=action_data.get("priority", 0.0),
                success=action_data.get("success", False),
                effectiveness_score=action_data.get("effectiveness_score", 0.0),
                efficiency_score=action_data.get("efficiency_score", 0.0),
                learning_points=action_data.get("learning_points", []),
                trace_metadata=metadata
            )
            
            # 추적 저장
            self.trace_store[f"{trace_id}_action"] = action_trace
            
            return action_trace
            
        except Exception as e:
            logger.error(f"행동 추적 생성 실패: {e}")
            raise
    
    async def create_evolution_trace(self, trace_id: str, evolution_data: Dict[str, Any]) -> EvolutionTrace:
        """진화 추적 생성"""
        try:
            metadata = self.trace_store[trace_id]
            
            evolution_trace = EvolutionTrace(
                evolution_id=evolution_data.get("evolution_id", str(uuid.uuid4())),
                evolution_type=evolution_data.get("evolution_type", "pattern_improvement"),
                improvement_score=evolution_data.get("improvement_score", 0.0),
                changes_applied=evolution_data.get("changes_applied", []),
                performance_impact=evolution_data.get("performance_impact", {}),
                stability_score=evolution_data.get("stability_score", 0.0),
                trace_metadata=metadata
            )
            
            # 추적 저장
            self.trace_store[f"{trace_id}_evolution"] = evolution_trace
            
            return evolution_trace
            
        except Exception as e:
            logger.error(f"진화 추적 생성 실패: {e}")
            raise
    
    async def create_full_cycle_trace(self, cycle_id: str, memory_trace: MemoryTrace,
                                    judgment_trace: JudgmentTrace, action_trace: ActionTrace,
                                    evolution_trace: Optional[EvolutionTrace] = None) -> FullCycleTrace:
        """전체 사이클 추적 생성"""
        try:
            # 전체 사이클 메타데이터 생성
            cycle_metadata = TraceMetadata(
                trace_id=cycle_id,
                parent_trace_id=None,
                trace_type=TraceType.FULL_CYCLE,
                status=TraceStatus.COMPLETED,
                input_hash=memory_trace.trace_metadata.input_hash,
                output_hash=action_trace.trace_metadata.output_hash,
                response_version=action_trace.trace_metadata.response_version,
                timestamp=memory_trace.trace_metadata.timestamp,
                duration=action_trace.trace_metadata.duration,
                metadata={"cycle_type": "memory_judgment_action_evolution"}
            )
            
            # 성능 메트릭 계산
            performance_metrics = {
                "memory_access_time": memory_trace.trace_metadata.duration,
                "judgment_time": judgment_trace.trace_metadata.duration,
                "action_execution_time": action_trace.trace_metadata.duration,
                "total_cycle_time": cycle_metadata.duration,
                "memory_importance": memory_trace.importance_score,
                "judgment_confidence": judgment_trace.confidence,
                "action_effectiveness": action_trace.effectiveness_score,
                "action_efficiency": action_trace.efficiency_score
            }
            
            if evolution_trace:
                performance_metrics["evolution_improvement"] = evolution_trace.improvement_score
                performance_metrics["evolution_stability"] = evolution_trace.stability_score
            
            # 전체 성공 여부 판단
            overall_success = (
                memory_trace.trace_metadata.status == TraceStatus.COMPLETED and
                judgment_trace.trace_metadata.status == TraceStatus.COMPLETED and
                action_trace.trace_metadata.status == TraceStatus.COMPLETED and
                action_trace.success
            )
            
            full_cycle_trace = FullCycleTrace(
                cycle_id=cycle_id,
                memory_trace=memory_trace,
                judgment_trace=judgment_trace,
                action_trace=action_trace,
                evolution_trace=evolution_trace,
                cycle_duration=cycle_metadata.duration,
                overall_success=overall_success,
                performance_metrics=performance_metrics,
                trace_metadata=cycle_metadata
            )
            
            # 추적 저장
            self.trace_store[cycle_id] = full_cycle_trace
            
            # 성능 히스토리에 추가
            self.performance_history.append({
                "cycle_id": cycle_id,
                "timestamp": cycle_metadata.timestamp,
                "success": overall_success,
                "metrics": performance_metrics
            })
            
            return full_cycle_trace
            
        except Exception as e:
            logger.error(f"전체 사이클 추적 생성 실패: {e}")
            raise
    
    async def analyze_performance_patterns(self) -> Dict[str, Any]:
        """성능 패턴 분석"""
        try:
            if not self.performance_history:
                return {"message": "분석할 성능 데이터가 없습니다."}
            
            # 기본 통계
            total_cycles = len(self.performance_history)
            successful_cycles = sum(1 for p in self.performance_history if p["success"])
            success_rate = successful_cycles / total_cycles if total_cycles > 0 else 0.0
            
            # 평균 성능 메트릭
            avg_metrics = {}
            if self.performance_history:
                metric_keys = self.performance_history[0]["metrics"].keys()
                for key in metric_keys:
                    values = [p["metrics"].get(key, 0.0) for p in self.performance_history]
                    avg_metrics[key] = sum(values) / len(values)
            
            # 성능 트렌드 분석
            recent_performance = self.performance_history[-10:] if len(self.performance_history) >= 10 else self.performance_history
            recent_success_rate = sum(1 for p in recent_performance if p["success"]) / len(recent_performance) if recent_performance else 0.0
            
            return {
                "total_cycles": total_cycles,
                "success_rate": success_rate,
                "recent_success_rate": recent_success_rate,
                "average_metrics": avg_metrics,
                "performance_trend": "improving" if recent_success_rate > success_rate else "stable" if recent_success_rate == success_rate else "declining"
            }
            
        except Exception as e:
            logger.error(f"성능 패턴 분석 실패: {e}")
            raise
    
    async def record_integration(self, integration_data: Dict[str, Any]) -> None:
        """통합 데이터 기록"""
        try:
            integration_id = f"integration_{int(time.time())}"
            
            # 통합 추적 데이터 생성
            integration_trace = {
                "trace_id": integration_id,
                "trace_type": "integration",
                "timestamp": datetime.now(),
                "integration_data": integration_data,
                "status": "completed"
            }
            
            self.trace_store[integration_id] = integration_trace
            logger.info(f"통합 데이터 기록 완료: {integration_id}")
            
        except Exception as e:
            logger.error(f"통합 데이터 기록 실패: {e}")

    async def get_evolution_suggestions(self) -> List[Dict[str, Any]]:
        """진화 제안 생성"""
        try:
            suggestions = []
            
            # 성능 패턴 분석
            patterns = await self.analyze_performance_patterns()
            
            # 성공률 기반 제안
            if patterns.get("success_rate", 0.0) < 0.8:
                suggestions.append({
                    "type": "success_rate_improvement",
                    "priority": "high",
                    "description": "성공률 향상을 위한 판단 시스템 개선 필요",
                    "target_metric": "success_rate",
                    "current_value": patterns.get("success_rate", 0.0),
                    "target_value": 0.8
                })
            
            # 응답 시간 기반 제안
            avg_cycle_time = patterns.get("average_metrics", {}).get("total_cycle_time", 0.0)
            if avg_cycle_time > 1.0:
                suggestions.append({
                    "type": "response_time_optimization",
                    "priority": "medium",
                    "description": "응답 시간 단축을 위한 시스템 최적화 필요",
                    "target_metric": "total_cycle_time",
                    "current_value": avg_cycle_time,
                    "target_value": 1.0
                })
            
            # 효과성 기반 제안
            avg_effectiveness = patterns.get("average_metrics", {}).get("action_effectiveness", 0.0)
            if avg_effectiveness < 0.8:
                suggestions.append({
                    "type": "effectiveness_improvement",
                    "priority": "high",
                    "description": "행동 효과성 향상을 위한 학습 패턴 개선 필요",
                    "target_metric": "action_effectiveness",
                    "current_value": avg_effectiveness,
                    "target_value": 0.8
                })
            
            return suggestions
            
        except Exception as e:
            logger.error(f"진화 제안 생성 실패: {e}")
            raise
    
    def _generate_hash(self, data: Any) -> str:
        """데이터 해시 생성"""
        data_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _generate_version(self) -> str:
        """응답 버전 생성"""
        return f"v{int(time.time())}"
    
    async def cleanup_old_traces(self) -> None:
        """오래된 추적 데이터 정리"""
        try:
            current_time = datetime.now()
            traces_to_remove = []
            
            for trace_id, trace in self.trace_store.items():
                if isinstance(trace, TraceMetadata):
                    age_days = (current_time - trace.timestamp).days
                    if age_days > self.trace_retention_days:
                        traces_to_remove.append(trace_id)
            
            for trace_id in traces_to_remove:
                del self.trace_store[trace_id]
            
            logger.info(f"오래된 추적 데이터 {len(traces_to_remove)}개 정리 완료")
            
        except Exception as e:
            logger.error(f"추적 데이터 정리 실패: {e}")
            raise

async def test_behavior_tracer():
    """행동 추적 시스템 테스트"""
    print("=== DuRiCore Phase 5 - 행동 추적 시스템 테스트 ===")
    
    # 추적 시스템 초기화
    tracer = BehaviorTracer()
    
    # 1. 메모리 추적 테스트
    print("\n1. 메모리 추적 테스트")
    memory_input = {
        "query": "긴급한 상황에서의 대응 방법",
        "context": "시스템 오류 발생"
    }
    
    memory_trace_id = await tracer.start_trace(TraceType.MEMORY_ACCESS, memory_input)
    await asyncio.sleep(0.1)  # 시뮬레이션
    
    memory_output = {
        "memory_id": "mem_001",
        "access_type": "read",
        "memory_type": "experience",
        "importance_score": 0.8,
        "access_count": 5,
        "associations": ["emergency", "response", "system_error"]
    }
    
    await tracer.update_trace(memory_trace_id, TraceStatus.COMPLETED, memory_output)
    memory_trace = await tracer.create_memory_trace(memory_trace_id, memory_output)
    
    print(f"메모리 추적 완료: {memory_trace.memory_id}")
    
    # 2. 판단 추적 테스트
    print("\n2. 판단 추적 테스트")
    judgment_input = {
        "situation": "시스템 오류 발생",
        "urgency": "high",
        "available_resources": ["cpu", "memory"]
    }
    
    judgment_trace_id = await tracer.start_trace(TraceType.JUDGMENT_PROCESS, judgment_input, memory_trace_id)
    await asyncio.sleep(0.2)  # 시뮬레이션
    
    judgment_output = {
        "judgment_id": "judg_001",
        "situation_type": "emergency",
        "decision": "immediate_response",
        "confidence": 0.85,
        "reasoning": "긴급 상황이므로 즉시 대응 필요",
        "alternatives": ["wait_and_observe", "escalate"],
        "risk_assessment": {"time_risk": 0.3, "resource_risk": 0.2},
        "ethical_score": 0.7
    }
    
    await tracer.update_trace(judgment_trace_id, TraceStatus.COMPLETED, judgment_output)
    judgment_trace = await tracer.create_judgment_trace(judgment_trace_id, judgment_output)
    
    print(f"판단 추적 완료: {judgment_trace.judgment_id}")
    
    # 3. 행동 추적 테스트
    print("\n3. 행동 추적 테스트")
    action_input = {
        "decision": "immediate_response",
        "available_resources": ["cpu", "memory"],
        "constraints": {"time_limit": 60}
    }
    
    action_trace_id = await tracer.start_trace(TraceType.ACTION_EXECUTION, action_input, judgment_trace_id)
    await asyncio.sleep(0.3)  # 시뮬레이션
    
    action_output = {
        "action_id": "act_001",
        "action_type": "immediate",
        "behavior_type": "response",
        "strategy": "urgent",
        "priority": 0.9,
        "success": True,
        "effectiveness_score": 0.85,
        "efficiency_score": 0.8,
        "learning_points": ["긴급 상황 대응 패턴 학습", "빠른 응답의 중요성 확인"]
    }
    
    await tracer.update_trace(action_trace_id, TraceStatus.COMPLETED, action_output)
    action_trace = await tracer.create_action_trace(action_trace_id, action_output)
    
    print(f"행동 추적 완료: {action_trace.action_id}")
    
    # 4. 전체 사이클 추적 테스트
    print("\n4. 전체 사이클 추적 테스트")
    cycle_id = f"cycle_{int(time.time())}"
    full_cycle_trace = await tracer.create_full_cycle_trace(
        cycle_id, memory_trace, judgment_trace, action_trace
    )
    
    print(f"전체 사이클 추적 완료: {full_cycle_trace.cycle_id}")
    print(f"- 전체 성공: {full_cycle_trace.overall_success}")
    print(f"- 사이클 시간: {full_cycle_trace.cycle_duration:.3f}초")
    print(f"- 성능 메트릭: {full_cycle_trace.performance_metrics}")
    
    # 5. 성능 패턴 분석 테스트
    print("\n5. 성능 패턴 분석 테스트")
    patterns = await tracer.analyze_performance_patterns()
    print(f"성능 패턴 분석 결과:")
    print(f"- 총 사이클: {patterns.get('total_cycles', 0)}")
    print(f"- 성공률: {patterns.get('success_rate', 0.0):.3f}")
    print(f"- 최근 성공률: {patterns.get('recent_success_rate', 0.0):.3f}")
    print(f"- 성능 트렌드: {patterns.get('performance_trend', 'unknown')}")
    
    # 6. 진화 제안 테스트
    print("\n6. 진화 제안 테스트")
    suggestions = await tracer.get_evolution_suggestions()
    print(f"진화 제안:")
    for suggestion in suggestions:
        print(f"- {suggestion['type']}: {suggestion['description']}")
        print(f"  우선순위: {suggestion['priority']}")
        print(f"  현재값: {suggestion['current_value']:.3f} -> 목표값: {suggestion['target_value']:.3f}")
    
    print("\n=== 테스트 완료 ===")

if __name__ == "__main__":
    asyncio.run(test_behavior_tracer()) 