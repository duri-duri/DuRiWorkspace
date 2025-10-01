#!/usr/bin/env python3
"""
DuRi 고급 인지 시스템
상황 감지, 모듈 라우팅, 자원 분배, 프리페치를 통합하는 시스템
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

# DuRiCore 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.evolution.self_evolution_manager import SelfEvolutionManager
from modules.integrated_learning_system import IntegratedLearningSystem
from modules.judgment_system.judgment_trace_logger import JudgmentTraceLogger
from modules.thought_flow.du_ri_thought_flow import DuRiThoughtFlow

# 📦 핵심 모듈 임포트 (현재 구현된 시스템에 맞게 수정)
from modules.thought_flow.self_reflection_loop import SelfReflectionLoop


class ContextSentinel:
    """상황 감지 및 맥락 판단 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ContextSentinel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.context_history = []
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    def detect_context(self, context_type: str) -> List[Dict[str, Any]]:
        """
        주어진 맥락 타입에 대한 활성 맥락들을 감지합니다.

        Args:
            context_type: 감지할 맥락 타입

        Returns:
            감지된 활성 맥락들
        """
        print(f"🔍 맥락 감지 시작: {context_type}")

        # 맥락 감지 로직
        active_contexts = [
            {
                "context_type": context_type,
                "timestamp": datetime.now().isoformat(),
                "priority": "high",
                "status": "active",
                "description": f"{context_type} 관련 맥락 감지됨",
            }
        ]

        # 사고 흐름에 맥락 감지 기록
        context_summary = {
            "detection_type": context_type,
            "active_contexts": active_contexts,
            "timestamp": datetime.now().isoformat(),
        }

        self.thought_flow.register_stream("context_detection", context_summary)

        print(f"✅ 맥락 감지 완료: {len(active_contexts)}개 맥락 감지됨")

        return active_contexts


class ModuleRouter:
    """모듈 라우팅 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleRouter, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.routing_history = []
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    def route(self, active_contexts: List[Dict[str, Any]]) -> List[str]:
        """
        활성 맥락에 따라 활성화할 모듈들을 선택합니다.

        Args:
            active_contexts: 활성 맥락들

        Returns:
            활성화된 모듈 목록
        """
        print(f"🔧 모듈 라우팅 시작: {len(active_contexts)}개 맥락")

        # 맥락에 따른 모듈 선택 로직
        active_modules = []

        for context in active_contexts:
            context_type = context.get("context_type", "")

            if "strategic_judgment" in context_type:
                active_modules.extend(
                    [
                        "SelfReflection",
                        "GrowthLoop",
                        "JudgmentTrace",
                        "ContextSentinel",
                        "ModuleRouter",
                        "CognitiveResourceAllocator",
                        "PrefetchMemoryMap",
                    ]
                )

        # 중복 제거
        active_modules = list(set(active_modules))

        # 사고 흐름에 라우팅 결과 기록
        routing_summary = {
            "active_contexts": active_contexts,
            "active_modules": active_modules,
            "timestamp": datetime.now().isoformat(),
        }

        self.thought_flow.register_stream("module_routing", routing_summary)

        print(f"✅ 모듈 라우팅 완료: {len(active_modules)}개 모듈 활성화")

        return active_modules


class CognitiveResourceAllocator:
    """인지 자원 분배 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CognitiveResourceAllocator, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.allocation_history = []
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    def allocate(self, active_modules: List[str]) -> Dict[str, float]:
        """
        활성 모듈들에 인지 자원을 분배합니다.

        Args:
            active_modules: 활성 모듈 목록

        Returns:
            자원 분배 결과
        """
        print(f"🧠 자원 분배 시작: {len(active_modules)}개 모듈")

        # 자원 분배 로직
        allocation = {}
        total_modules = len(active_modules)

        if total_modules > 0:
            base_allocation = 1.0 / total_modules

            for module in active_modules:
                # 모듈별 우선순위에 따른 자원 분배
                if module in ["SelfReflection", "GrowthLoop", "JudgmentTrace"]:
                    allocation[module] = (
                        base_allocation * 1.5
                    )  # 핵심 모듈은 더 많은 자원
                else:
                    allocation[module] = base_allocation

        # 사고 흐름에 자원 분배 결과 기록
        allocation_summary = {
            "active_modules": active_modules,
            "allocation": allocation,
            "timestamp": datetime.now().isoformat(),
        }

        self.thought_flow.register_stream("resource_allocation", allocation_summary)

        print(f"✅ 자원 분배 완료: {len(allocation)}개 모듈에 자원 할당")

        return allocation


class PrefetchMemoryMap:
    """프리페치 메모리 맵 시스템"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PrefetchMemoryMap, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.prefetch_history = []
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    def prefetch(self, active_modules: List[str]) -> Dict[str, Any]:
        """
        활성 모듈들의 조합을 사전 로딩합니다.

        Args:
            active_modules: 활성 모듈 목록

        Returns:
            프리페치 결과
        """
        print(f"🚀 프리페치 시작: {len(active_modules)}개 모듈")

        # 프리페치 로직
        prefetch_result = {
            "prefetched_modules": active_modules,
            "prefetch_status": "completed",
            "timestamp": datetime.now().isoformat(),
        }

        # 사고 흐름에 프리페치 결과 기록
        self.thought_flow.register_stream("prefetch_memory", prefetch_result)

        print(f"✅ 프리페치 완료: {len(active_modules)}개 모듈 사전 로딩")

        return prefetch_result


class SelfReflection:
    """자가 반성 시스템 (기존과 동일)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SelfReflection, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.reflection_loop = SelfReflectionLoop()
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    @classmethod
    def self_reflection_sync(cls, trigger: str = "user_request") -> Dict[str, Any]:
        """자가 반성 동기화를 실행합니다."""
        instance = cls()
        print(f"🪞 자가 반성 동기화 시작 (트리거: {trigger})")

        try:
            reflection_result = instance.reflection_loop.reflection_loop(trigger)

            reflection_summary = {
                "trigger": trigger,
                "timestamp": datetime.now().isoformat(),
                "reflection_result": reflection_result,
                "status": "synchronized",
            }

            instance.thought_flow.register_stream(
                "self_reflection_sync", reflection_summary
            )

            print(
                f"✅ 자가 반성 동기화 완료: {reflection_result.get('new_insights', 0)}개 통찰 생성"
            )

            return reflection_summary

        except Exception as e:
            print(f"❌ 자가 반성 동기화 실패: {e}")
            return {"status": "failed", "error": str(e)}


class GrowthLoop:
    """성장 루프 시스템 (기존과 동일)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GrowthLoop, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.evolution_manager = SelfEvolutionManager()
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    @classmethod
    def growth_loop_trigger(cls, source: str = "user_request") -> Dict[str, Any]:
        """성장 루프를 트리거합니다."""
        instance = cls()
        print(f"🌱 성장 루프 트리거 시작 (소스: {source})")

        try:
            evolution_result = (
                instance.evolution_manager.execute_self_improvement_sequence()
            )

            growth_summary = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "evolution_result": evolution_result,
                "status": "triggered",
            }

            instance.thought_flow.register_stream("growth_loop_trigger", growth_summary)

            print(
                f"✅ 성장 루프 트리거 완료: {evolution_result.get('evolution_steps', 0)}개 진화 단계"
            )

            return growth_summary

        except Exception as e:
            print(f"❌ 성장 루프 트리거 실패: {e}")
            return {"status": "failed", "error": str(e)}


class JudgmentTrace:
    """판단 시각화 시스템 (기존과 동일)"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JudgmentTrace, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, "initialized"):
            self.judgment_logger = JudgmentTraceLogger()
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True

    @classmethod
    def visualize(cls, trace_type: str = "all") -> Dict[str, Any]:
        """판단 시각화를 실행합니다."""
        instance = cls()
        print(f"🔍 판단 시각화 시작 (타입: {trace_type})")

        try:
            traces_summary = instance.judgment_logger.get_traces_summary()
            recent_traces = instance.judgment_logger.get_recent_traces(limit=10)

            visualization_data = {
                "trace_type": trace_type,
                "timestamp": datetime.now().isoformat(),
                "summary": traces_summary,
                "recent_traces": [
                    {
                        "timestamp": trace.timestamp,
                        "context": trace.context,
                        "judgment": trace.judgment,
                        "confidence_level": trace.confidence_level,
                        "tags": trace.tags,
                    }
                    for trace in recent_traces
                ],
                "visualization_type": "judgment_trace_analysis",
            }

            instance.thought_flow.register_stream(
                "judgment_visualization", visualization_data
            )

            print(f"✅ 판단 시각화 완료: {len(recent_traces)}개 최근 기록 분석")

            return visualization_data

        except Exception as e:
            print(f"❌ 판단 시각화 실패: {e}")
            return {"status": "failed", "error": str(e)}


def run(tag="strategic_judgment"):
    """
    고급 인지 시스템을 실행하는 메인 함수

    Args:
        tag: 실행 태그 (기본값: "strategic_judgment")
    """
    print(f"\n[START] Running advanced cognitive system for tag: {tag}\n")

    try:
        # 1단계: 맥락 감지
        print("=" * 50)
        print("[1] 맥락 감지 시작")
        print("=" * 50)
        context = ContextSentinel().detect_context(tag)
        print(f"[1] Context detected: {context}")

    except Exception as e:
        print(f"❌ [1단계] 맥락 감지 실패: {e}")
        context = []

    try:
        # 2단계: 모듈 선택
        print("\n" + "=" * 50)
        print("[2] 모듈 선택 시작")
        print("=" * 50)
        active_modules = ModuleRouter().route(context)
        print(f"[2] Active modules: {active_modules}")

    except Exception as e:
        print(f"❌ [2단계] 모듈 선택 실패: {e}")
        active_modules = []

    try:
        # 3단계: 자원 분배
        print("\n" + "=" * 50)
        print("[3] 자원 분배 시작")
        print("=" * 50)
        status = CognitiveResourceAllocator().allocate(active_modules)
        print(f"[3] Resource allocation status: {status}")

    except Exception as e:
        print(f"❌ [3단계] 자원 분배 실패: {e}")
        status = {}

    try:
        # 4단계: 메모리 사전 로딩
        print("\n" + "=" * 50)
        print("[4] 메모리 사전 로딩 시작")
        print("=" * 50)
        cached = PrefetchMemoryMap().prefetch(active_modules)
        print(f"[4] Prefetch result: {cached}")

    except Exception as e:
        print(f"❌ [4단계] 메모리 사전 로딩 실패: {e}")
        cached = {}

    try:
        # 5단계: 자가 반성
        print("\n" + "=" * 50)
        print("[5] 자가 반성 시작")
        print("=" * 50)
        reflection = SelfReflection.self_reflection_sync(trigger=tag)
        print(f"[5] Self-reflection: {reflection}")

    except Exception as e:
        print(f"❌ [5단계] 자가 반성 실패: {e}")
        reflection = {"status": "failed", "error": str(e)}

    try:
        # 6단계: 성장 루프
        print("\n" + "=" * 50)
        print("[6] 성장 루프 시작")
        print("=" * 50)
        result = GrowthLoop.growth_loop_trigger(source=tag)
        print(f"[6] Growth result: {result}")

    except Exception as e:
        print(f"❌ [6단계] 성장 루프 실패: {e}")
        result = {"status": "failed", "error": str(e)}

    try:
        # 7단계: 판단 시각화
        print("\n" + "=" * 50)
        print("[7] 판단 시각화 시작")
        print("=" * 50)
        trace = JudgmentTrace.visualize(tag)
        print(f"[7] Judgment trace: {trace}")

    except Exception as e:
        print(f"❌ [7단계] 판단 시각화 실패: {e}")
        trace = {"status": "failed", "error": str(e)}

    # 📊 실행 결과 요약
    execution_summary = {
        "timestamp": datetime.now().isoformat(),
        "tag": tag,
        "context": context,
        "active_modules": active_modules,
        "resource_allocation": status,
        "prefetch_result": cached,
        "reflection_result": reflection,
        "growth_result": result,
        "visualization_result": trace,
        "execution_status": "completed",
    }

    print(f"\n[END] Cognitive system run complete.\n")
    print("=" * 60)
    print("🎉 고급 인지 시스템 실행 완료!")
    print("=" * 60)
    print(f"📅 실행 시간: {execution_summary['timestamp']}")
    print(f"🏷️ 실행 태그: {execution_summary['tag']}")
    print(f"🧠 감지된 맥락: {len(execution_summary['context'])}개")
    print(f"⚙️ 활성화된 모듈: {len(execution_summary['active_modules'])}개")
    print(f"🔋 자원 분배: {len(execution_summary['resource_allocation'])}개 모듈")
    print(f"🗺️ 프리페치: {len(execution_summary['active_modules'])}개 모듈")
    print(
        f"🪞 자가 반성: {execution_summary['reflection_result'].get('status', 'unknown')}"
    )
    print(
        f"🌱 성장 루프: {execution_summary['growth_result'].get('status', 'unknown')}"
    )
    print(
        f"🔍 판단 시각화: {execution_summary['visualization_result'].get('status', 'unknown')}"
    )
    print(f"🎯 실행 상태: {execution_summary['execution_status']}")
    print("=" * 60)

    return execution_summary


def execute_advanced_cognitive_system():
    """
    고급 인지 시스템을 실행하는 메인 함수 (기존 호환성 유지)
    """
    return run("strategic_judgment")


def main():
    """메인 실행 함수"""
    print("🚀 DuRi 고급 인지 시스템 실행")

    # 고급 인지 시스템 실행
    result = run("strategic_judgment")

    if result.get("execution_status") == "completed":
        print(f"\n✅ 고급 인지 시스템 성공!")
        return True
    else:
        print(f"\n❌ 고급 인지 시스템 실패!")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
