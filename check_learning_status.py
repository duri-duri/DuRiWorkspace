#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 학습 시스템 상태 확인 스크립트
현재 학습 시스템의 활성화 상태와 세션 정보를 확인합니다.
"""

import asyncio
import logging
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def check_unified_learning_system():
    """통합 학습 시스템 상태 확인"""
    try:
        from DuRiCore.unified_learning_system import UnifiedLearningSystem
        
        # 통합 학습 시스템 인스턴스 생성
        learning_system = UnifiedLearningSystem()
        
        # 현재 활성 세션 수 확인
        active_sessions = [s for s in learning_system.learning_sessions if s.status.value == "in_progress"]
        evolution_sessions = [s for s in learning_system.evolution_sessions if s.status.value == "in_progress"]
        
        return {
            "system": "통합 학습 시스템",
            "status": "초기화됨",
            "active_learning_sessions": len(active_sessions),
            "active_evolution_sessions": len(evolution_sessions),
            "total_learning_sessions": len(learning_system.learning_sessions),
            "total_evolution_sessions": len(learning_system.evolution_sessions),
            "learning_history": len(learning_system.learning_history),
            "evolution_history": len(learning_system.evolution_history)
        }
    except Exception as e:
        logger.error(f"통합 학습 시스템 확인 실패: {e}")
        return {
            "system": "통합 학습 시스템",
            "status": "오류",
            "error": str(e)
        }

async def check_autonomous_learning_system():
    """자율 학습 시스템 상태 확인"""
    try:
        from duri_modules.autonomous.continuous_learner import AutonomousLearner
        from duri_modules.autonomous.duri_autonomous_core import DuRiAutonomousCore
        
        # 자율 학습 시스템들 확인
        autonomous_learner = AutonomousLearner()
        autonomous_core = DuRiAutonomousCore()
        
        return {
            "system": "자율 학습 시스템",
            "autonomous_learner_status": "실행 중" if autonomous_learner.is_running else "대기",
            "autonomous_core_status": "활성" if autonomous_core.is_active else "비활성",
            "current_session": autonomous_learner.current_session.session_id if autonomous_learner.current_session else None,
            "total_learning_cycles": autonomous_learner.total_learning_cycles,
            "total_problems_detected": autonomous_learner.total_problems_detected,
            "total_decisions_made": autonomous_learner.total_decisions_made,
            "learning_history_count": len(autonomous_learner.learning_history)
        }
    except Exception as e:
        logger.error(f"자율 학습 시스템 확인 실패: {e}")
        return {
            "system": "자율 학습 시스템",
            "status": "오류",
            "error": str(e)
        }

async def check_learning_loop_manager():
    """학습 루프 매니저 상태 확인"""
    try:
        from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
        
        # 학습 루프 매니저 가져오기
        learning_loop_manager = get_learning_loop_manager()
        
        # 현재 상태 확인
        current_status = learning_loop_manager.get_current_status()
        
        return {
            "system": "학습 루프 매니저",
            "is_running": learning_loop_manager.is_running,
            "current_cycle": learning_loop_manager.current_cycle.cycle_id if learning_loop_manager.current_cycle else None,
            "learning_cycle_count": learning_loop_manager.learning_cycle_count,
            "total_cycles": len(learning_loop_manager.learning_cycles),
            "current_stage": current_status.get("current_stage"),
            "performance_metrics": current_status.get("performance_metrics", {})
        }
    except Exception as e:
        logger.error(f"학습 루프 매니저 확인 실패: {e}")
        return {
            "system": "학습 루프 매니저",
            "status": "오류",
            "error": str(e)
        }

async def check_realtime_learner():
    """실시간 학습 시스템 상태 확인"""
    try:
        from duri_modules.autonomous.realtime_learner import RealtimeLearner
        from duri_modules.autonomous.continuous_learner import AutonomousLearner
        
        # 실시간 학습 시스템 확인
        autonomous_learner = AutonomousLearner()
        realtime_learner = RealtimeLearner(autonomous_learner)
        
        return {
            "system": "실시간 학습 시스템",
            "is_active": realtime_learner.is_active,
            "learning_interval": realtime_learner.learning_interval,
            "last_learning_time": realtime_learner.last_learning_time.isoformat() if realtime_learner.last_learning_time else None,
            "total_learning_sessions": len(realtime_learner.learning_history),
            "current_session": realtime_learner.current_session.session_id if realtime_learner.current_session else None
        }
    except Exception as e:
        logger.error(f"실시간 학습 시스템 확인 실패: {e}")
        return {
            "system": "실시간 학습 시스템",
            "status": "오류",
            "error": str(e)
        }

async def generate_learning_summary():
    """학습 시스템 전체 요약 생성"""
    print("🤖 DuRi 학습 시스템 현황 서머리")
    print("=" * 50)
    
    # 각 시스템 상태 확인
    systems = [
        await check_unified_learning_system(),
        await check_autonomous_learning_system(),
        await check_learning_loop_manager(),
        await check_realtime_learner()
    ]
    
    # 결과 출력
    for system in systems:
        print(f"\n📋 {system['system']}")
        print("-" * 30)
        
        for key, value in system.items():
            if key != "system":
                if isinstance(value, dict):
                    print(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"    {sub_key}: {sub_value}")
                else:
                    print(f"  {key}: {value}")
    
    # 전체 상태 요약
    print("\n🎯 전체 학습 시스템 상태")
    print("-" * 30)
    
    active_systems = 0
    total_systems = len(systems)
    
    for system in systems:
        if "status" in system:
            if system["status"] == "오류":
                print(f"  ❌ {system['system']}: 오류 발생")
            else:
                print(f"  ✅ {system['system']}: 정상")
                active_systems += 1
        else:
            # 자율 학습 시스템의 경우 별도 확인
            if "autonomous_learner_status" in system:
                if system["autonomous_learner_status"] == "실행 중":
                    active_systems += 1
                    print(f"  ✅ {system['system']}: 활성")
                else:
                    print(f"  ⏸️ {system['system']}: 대기")
            else:
                print(f"  ✅ {system['system']}: 정상")
                active_systems += 1
    
    print(f"\n📊 활성 시스템: {active_systems}/{total_systems}")
    
    if active_systems == 0:
        print("\n🚨 모든 학습 시스템이 비활성 상태입니다!")
        print("내일 학습 시스템을 활성화해야 합니다.")
    elif active_systems < total_systems:
        print(f"\n⚠️ 일부 학습 시스템이 비활성 상태입니다. ({total_systems - active_systems}개)")
    else:
        print("\n🎉 모든 학습 시스템이 활성 상태입니다!")

if __name__ == "__main__":
    asyncio.run(generate_learning_summary())

