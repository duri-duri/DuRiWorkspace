#!/usr/bin/env python3
"""
DuRi 고급 통합 시스템
자가 반성, 성장 루프, 판단 시각화를 통합하는 시스템
"""

import sys
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, List

# DuRiCore 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 📦 핵심 모듈 임포트 (현재 구현된 시스템에 맞게 수정)
from modules.thought_flow.self_reflection_loop import SelfReflectionLoop
from modules.evolution.self_evolution_manager import SelfEvolutionManager
from modules.judgment_system.judgment_trace_logger import JudgmentTraceLogger
from modules.thought_flow.du_ri_thought_flow import DuRiThoughtFlow
from modules.integrated_learning_system import IntegratedLearningSystem

class SelfReflection:
    """자가 반성 시스템 (현재 SelfReflectionLoop와 연동)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SelfReflection, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.reflection_loop = SelfReflectionLoop()
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True
    
    @classmethod
    def self_reflection_sync(cls, trigger: str = "user_request") -> Dict[str, Any]:
        """
        자가 반성 동기화를 실행합니다.
        
        Args:
            trigger: 반성 트리거 타입
        
        Returns:
            반성 동기화 결과
        """
        instance = cls()
        print(f"🔍 자가 반성 동기화 시작 (트리거: {trigger})")
        
        try:
            # 자가 반성 루프 실행
            reflection_result = instance.reflection_loop.reflection_loop(trigger)
            
            # 사고 흐름에 반성 결과 기록
            reflection_summary = {
                "trigger": trigger,
                "timestamp": datetime.now().isoformat(),
                "reflection_result": reflection_result,
                "status": "synchronized"
            }
            
            instance.thought_flow.register_stream("self_reflection_sync", reflection_summary)
            
            print(f"✅ 자가 반성 동기화 완료: {reflection_result.get('new_insights', 0)}개 통찰 생성")
            
            return reflection_summary
            
        except Exception as e:
            print(f"❌ 자가 반성 동기화 실패: {e}")
            return {"status": "failed", "error": str(e)}

class GrowthLoop:
    """성장 루프 시스템 (현재 SelfEvolutionManager와 연동)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GrowthLoop, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.evolution_manager = SelfEvolutionManager()
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True
    
    @classmethod
    def growth_loop_trigger(cls, source: str = "user_request") -> Dict[str, Any]:
        """
        성장 루프를 트리거합니다.
        
        Args:
            source: 성장 루프 소스
        
        Returns:
            성장 루프 실행 결과
        """
        instance = cls()
        print(f"🚀 성장 루프 트리거 시작 (소스: {source})")
        
        try:
            # 자기개선 시퀀스 실행
            evolution_result = instance.evolution_manager.execute_self_improvement_sequence()
            
            # 사고 흐름에 성장 결과 기록
            growth_summary = {
                "source": source,
                "timestamp": datetime.now().isoformat(),
                "evolution_result": evolution_result,
                "status": "triggered"
            }
            
            instance.thought_flow.register_stream("growth_loop_trigger", growth_summary)
            
            print(f"✅ 성장 루프 트리거 완료: {evolution_result.get('evolution_steps', 0)}개 진화 단계")
            
            return growth_summary
            
        except Exception as e:
            print(f"❌ 성장 루프 트리거 실패: {e}")
            return {"status": "failed", "error": str(e)}

class JudgmentTrace:
    """판단 시각화 시스템 (현재 JudgmentTraceLogger와 연동)"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JudgmentTrace, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.judgment_logger = JudgmentTraceLogger()
            self.thought_flow = DuRiThoughtFlow()
            self.initialized = True
    
    @classmethod
    def visualize(cls, trace_type: str = "all") -> Dict[str, Any]:
        """
        판단 시각화를 실행합니다.
        
        Args:
            trace_type: 시각화할 추적 타입
        
        Returns:
            시각화 결과
        """
        instance = cls()
        print(f"📊 판단 시각화 시작 (타입: {trace_type})")
        
        try:
            # 판단 기록 요약 가져오기
            traces_summary = instance.judgment_logger.get_traces_summary()
            
            # 최근 판단 기록들 가져오기
            recent_traces = instance.judgment_logger.get_recent_traces(limit=10)
            
            # 시각화 데이터 구성
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
                        "tags": trace.tags
                    }
                    for trace in recent_traces
                ],
                "visualization_type": "judgment_trace_analysis"
            }
            
            # 사고 흐름에 시각화 결과 기록
            instance.thought_flow.register_stream("judgment_visualization", visualization_data)
            
            print(f"✅ 판단 시각화 완료: {len(recent_traces)}개 최근 기록 분석")
            
            return visualization_data
            
        except Exception as e:
            print(f"❌ 판단 시각화 실패: {e}")
            return {"status": "failed", "error": str(e)}

def execute_advanced_integration():
    """
    고급 통합 시스템을 실행하는 메인 함수
    """
    print("🚀 DuRi 고급 통합 시스템 시작")
    print(f"📅 실행 시작: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # ① 자가 반성 동기화
        print("\n" + "="*50)
        print("① 자가 반성 동기화 실행")
        print("="*50)
        reflection_result = SelfReflection.self_reflection_sync(trigger="strategic_judgment")
        
        # ② 성장 루프 트리거
        print("\n" + "="*50)
        print("② 성장 루프 트리거 실행")
        print("="*50)
        growth_result = GrowthLoop.growth_loop_trigger(source="strategic_judgment")
        
        # ③ 판단 시각화 실행
        print("\n" + "="*50)
        print("③ 판단 시각화 실행")
        print("="*50)
        visualization_result = JudgmentTrace.visualize("strategic_judgment")
        
        # 📊 통합 결과 요약
        integration_summary = {
            "timestamp": datetime.now().isoformat(),
            "reflection_sync": reflection_result,
            "growth_loop": growth_result,
            "judgment_visualization": visualization_result,
            "integration_status": "completed"
        }
        
        print("\n" + "="*60)
        print("🎉 고급 통합 시스템 완료!")
        print("="*60)
        print(f"📅 실행 시간: {integration_summary['timestamp']}")
        print(f"🔍 자가 반성: {reflection_result.get('status', 'unknown')}")
        print(f"🚀 성장 루프: {growth_result.get('status', 'unknown')}")
        print(f"📊 판단 시각화: {visualization_result.get('status', 'unknown')}")
        print(f"🎯 통합 상태: {integration_summary['integration_status']}")
        print("="*60)
        
        return integration_summary
        
    except Exception as e:
        print(f"❌ 고급 통합 시스템 실행 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "failed", "error": str(e)}

def main():
    """메인 실행 함수"""
    print("🚀 DuRi 고급 통합 시스템 실행")
    
    # 고급 통합 시스템 실행
    result = execute_advanced_integration()
    
    if result.get("status") == "failed":
        print(f"\n❌ 통합 실패: {result.get('error')}")
        return False
    else:
        print(f"\n✅ 고급 통합 성공!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
