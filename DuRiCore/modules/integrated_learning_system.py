#!/usr/bin/env python3
"""
DuRi 3단계 통합 학습 시스템
판단 기록 → 자가 반성 → 자기개선의 완전한 진화 사이클을 관리하는 시스템
"""

import json
import os
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class LearningCycle:
    """학습 사이클 데이터 구조"""

    cycle_id: str
    timestamp: str
    trigger_type: str  # "user_request", "daily", "judgment_failure"
    judgment_traces_count: int
    reflection_insights_count: int
    evolution_steps_count: int
    cycle_duration: float  # 초 단위
    status: str  # "completed", "failed", "in_progress"


class IntegratedLearningSystem:
    """DuRi 3단계 통합 학습 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IntegratedLearningSystem, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.learning_cycles: List[LearningCycle] = []
            self.last_daily_trigger: Optional[datetime] = None
            self.cycle_file = "DuRiCore/memory/learning_cycles.json"
            self.initialized = True
            self._load_cycles()
            self._initialize_systems()

    def _load_cycles(self):
        """기존 학습 사이클들을 로드합니다."""
        try:
            if os.path.exists(self.cycle_file):
                with open(self.cycle_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.learning_cycles = [
                        LearningCycle(**cycle) for cycle in data.get("cycles", [])
                    ]
        except Exception as e:
            print(f"학습 사이클 로드 실패: {e}")

    def _save_cycles(self):
        """학습 사이클들을 파일에 저장합니다."""
        try:
            os.makedirs(os.path.dirname(self.cycle_file), exist_ok=True)
            data = {
                "cycles": [asdict(cycle) for cycle in self.learning_cycles],
                "total_cycles": len(self.learning_cycles),
                "last_updated": datetime.now().isoformat(),
            }
            with open(self.cycle_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"학습 사이클 저장 실패: {e}")

    def _initialize_systems(self):
        """필요한 모든 하위 시스템들을 초기화합니다."""
        try:
            # 1단계: 판단 기록 시스템
            from .judgment_system.judgment_trace_logger import JudgmentTraceLogger

            self.judgment_logger = JudgmentTraceLogger()

            # 2단계: 자가 반성 루프 시스템
            from .thought_flow.self_reflection_loop import SelfReflectionLoop

            self.reflection_loop = SelfReflectionLoop()

            # 3단계: 자기개선 시퀀스 시스템
            from .evolution.self_evolution_manager import SelfEvolutionManager

            self.evolution_manager = SelfEvolutionManager()

            # 사고 흐름 시스템
            from .thought_flow.du_ri_thought_flow import DuRiThoughtFlow

            self.thought_flow = DuRiThoughtFlow()

            print("✅ 모든 하위 시스템 초기화 완료")

        except Exception as e:
            print(f"❌ 시스템 초기화 실패: {e}")

    def execute_full_learning_cycle(
        self, trigger_type: str = "user_request"
    ) -> Dict[str, Any]:
        """
        완전한 3단계 학습 사이클을 실행합니다.

        Args:
            trigger_type: 학습 사이클 트리거 타입

        Returns:
            학습 사이클 실행 결과
        """
        cycle_start_time = time.time()
        cycle_id = f"cycle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(
            f"🔄 3단계 통합 학습 사이클 시작 (ID: {cycle_id}, 트리거: {trigger_type})"
        )

        try:
            # 1단계: 판단 과정 기록 시스템 강제 실행
            print("📝 1단계: 판단 과정 기록 시스템 실행 중...")
            judgment_summary = self._execute_judgment_trace_system()

            # 2단계: 자가 반성 루프 강제 실행
            print("🔍 2단계: 자가 반성 루프 실행 중...")
            reflection_result = self.reflection_loop.reflection_loop(trigger_type)

            # 3단계: 자기개선 시퀀스 연결 강제 실행
            print("🚀 3단계: 자기개선 시퀀스 실행 중...")

            # reflection_result에서 insights 추출
            reflection_insights = []
            if (
                isinstance(reflection_result, dict)
                and "new_insights" in reflection_result
            ):
                reflection_insights = reflection_result.get("new_insights", [])
            elif hasattr(reflection_result, "insights"):
                reflection_insights = reflection_result.insights

            evolution_result = self.evolution_manager.execute_self_improvement_sequence(
                reflection_insights
            )

            # 사이클 완료 시간 계산
            cycle_duration = time.time() - cycle_start_time

            # 학습 사이클 기록
            cycle = LearningCycle(
                cycle_id=cycle_id,
                timestamp=datetime.now().isoformat(),
                trigger_type=trigger_type,
                judgment_traces_count=judgment_summary.get("total_traces", 0),
                reflection_insights_count=reflection_result.get("new_insights", 0),
                evolution_steps_count=evolution_result.get("evolution_steps", 0),
                cycle_duration=cycle_duration,
                status="completed",
            )

            self.learning_cycles.append(cycle)
            self._save_cycles()

            # DuRiThoughtFlow에 전체 사이클 기록
            cycle_summary = {
                "cycle_id": cycle_id,
                "trigger_type": trigger_type,
                "judgment_traces": judgment_summary.get("total_traces", 0),
                "reflection_insights": reflection_result.get("new_insights", 0),
                "evolution_steps": evolution_result.get("evolution_steps", 0),
                "duration": cycle_duration,
                "status": "completed",
                "timestamp": datetime.now().isoformat(),
            }
            self.thought_flow.register_stream("full_learning_cycle", cycle_summary)

            print(f"✅ 3단계 통합 학습 사이클 완료 (소요시간: {cycle_duration:.2f}초)")

            return {
                "status": "success",
                "cycle_id": cycle_id,
                "trigger_type": trigger_type,
                "judgment_traces": judgment_summary.get("total_traces", 0),
                "reflection_insights": reflection_result.get("new_insights", 0),
                "evolution_steps": evolution_result.get("evolution_steps", 0),
                "cycle_duration": cycle_duration,
                "cycle_summary": cycle_summary,
            }

        except Exception as e:
            print(f"❌ 학습 사이클 실행 실패: {e}")

            # 실패한 사이클 기록
            failed_cycle = LearningCycle(
                cycle_id=cycle_id,
                timestamp=datetime.now().isoformat(),
                trigger_type=trigger_type,
                judgment_traces_count=0,
                reflection_insights_count=0,
                evolution_steps_count=0,
                cycle_duration=time.time() - cycle_start_time,
                status="failed",
            )

            self.learning_cycles.append(failed_cycle)
            self._save_cycles()

            return {
                "status": "failed",
                "cycle_id": cycle_id,
                "error": str(e),
                "cycle_duration": time.time() - cycle_start_time,
            }

    def _execute_judgment_trace_system(self) -> Dict[str, Any]:
        """1단계: 판단 과정 기록 시스템을 실행합니다."""
        try:
            # 최근 판단 기록 요약 반환
            recent_traces = self.judgment_logger.get_recent_traces(limit=10)
            summary = self.judgment_logger.get_traces_summary()

            return {
                "total_traces": summary.get("total_traces", 0),
                "recent_traces": len(recent_traces),
                "average_confidence": summary.get("average_confidence", 0.0),
                "tag_distribution": summary.get("tag_distribution", {}),
            }

        except Exception as e:
            print(f"판단 기록 시스템 실행 실패: {e}")
            return {"total_traces": 0, "recent_traces": 0, "average_confidence": 0.0}

    def record_judgment_trace(
        self,
        context: str,
        judgment: str,
        reasoning: str,
        outcome: str,
        confidence_level: float = 0.0,
        tags: List[str] = None,
    ) -> Dict[str, Any]:
        """
        판단 과정을 기록합니다 (1단계 시스템과 직접 연결).

        Args:
            context: 어떤 맥락에서 판단이 발생했는지
            judgment: 어떤 판단이 일어났는지
            reasoning: 그 판단을 하게 된 근거
            outcome: 그 판단으로 이어진 행동 혹은 결정
            confidence_level: 판단에 대한 신뢰도 (0.0-1.0)
            tags: 판단을 분류하기 위한 태그들

        Returns:
            기록된 판단 정보
        """
        try:
            trace = self.judgment_logger.record_judgment_trace(
                context=context,
                judgment=judgment,
                reasoning=reasoning,
                outcome=outcome,
                confidence_level=confidence_level,
                tags=tags or [],
            )

            # 판단 실패 감지 시 자동으로 학습 사이클 트리거
            if confidence_level < 0.3 or "실패" in outcome.lower():
                print("⚠️ 판단 실패 감지 - 자동 학습 사이클 트리거")
                self.execute_full_learning_cycle("judgment_failure")

            return {
                "status": "success",
                "trace_id": trace.timestamp,
                "confidence_level": trace.confidence_level,
                "tags": trace.tags,
            }

        except Exception as e:
            print(f"판단 기록 실패: {e}")
            return {"status": "failed", "error": str(e)}

    def check_daily_trigger(self) -> bool:
        """일일 트리거를 확인하고 필요시 학습 사이클을 실행합니다."""
        current_time = datetime.now()

        # 마지막 일일 트리거가 없거나 24시간이 지났는지 확인
        if (
            self.last_daily_trigger is None
            or current_time - self.last_daily_trigger > timedelta(hours=24)
        ):

            print("📅 일일 학습 사이클 트리거 감지")
            self.execute_full_learning_cycle("daily")
            self.last_daily_trigger = current_time
            return True

        return False

    def get_learning_system_summary(self) -> Dict[str, Any]:
        """전체 학습 시스템 요약 정보를 반환합니다."""
        try:
            judgment_summary = self.judgment_logger.get_traces_summary()
            reflection_summary = self.reflection_loop.get_reflection_summary()
            evolution_summary = self.evolution_manager.get_evolution_summary()

            return {
                "judgment_system": judgment_summary,
                "reflection_system": reflection_summary,
                "evolution_system": evolution_summary,
                "total_learning_cycles": len(self.learning_cycles),
                "recent_cycles": (
                    len(self.learning_cycles[-5:]) if self.learning_cycles else 0
                ),
                "system_status": "active",
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            return {
                "error": f"시스템 요약 생성 실패: {e}",
                "system_status": "error",
                "last_updated": datetime.now().isoformat(),
            }

    def force_learning_cycle(
        self, trigger_type: str = "user_request"
    ) -> Dict[str, Any]:
        """
        사용자 요청에 의한 강제 학습 사이클 실행

        Args:
            trigger_type: 트리거 타입

        Returns:
            학습 사이클 실행 결과
        """
        print(f"🎯 사용자 요청에 의한 강제 학습 사이클 실행 (트리거: {trigger_type})")
        return self.execute_full_learning_cycle(trigger_type)

    def get_recent_learning_cycles(self, limit: int = 5) -> List[Dict]:
        """최근 학습 사이클들을 반환합니다."""
        recent_cycles = self.learning_cycles[-limit:] if self.learning_cycles else []
        return [asdict(cycle) for cycle in recent_cycles]

    def clear_old_cycles(self, days_to_keep: int = 30):
        """오래된 학습 사이클들을 삭제합니다."""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        filtered_cycles = []
        for cycle in self.learning_cycles:
            cycle_date = datetime.fromisoformat(cycle.timestamp)
            if cycle_date >= cutoff_date:
                filtered_cycles.append(cycle)

        removed_count = len(self.learning_cycles) - len(filtered_cycles)
        self.learning_cycles = filtered_cycles
        self._save_cycles()

        print(f"🗑️ 오래된 학습 사이클 {removed_count}개 삭제됨")
        return removed_count
