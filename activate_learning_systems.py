#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 학습 시스템 활성화 스크립트
모든 학습 시스템을 시작하고 모니터링합니다.
"""

import asyncio
import logging
import sys
import os
import time
from datetime import datetime
from typing import Dict, Any, List

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('duri_learning_activation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LearningSystemActivator:
    """학습 시스템 활성화 관리자"""
    
    def __init__(self):
        self.activated_systems = []
        self.monitoring_active = False
        self.monitoring_interval = 60  # 1분마다 모니터링
        
    async def activate_unified_learning_system(self) -> Dict[str, Any]:
        """통합 학습 시스템 활성화"""
        try:
            from DuRiCore.unified_learning_system import UnifiedLearningSystem
            
            learning_system = UnifiedLearningSystem()
            
            # 학습 세션 시작
            from DuRiCore.unified_learning_system import LearningType
            session = await learning_system.start_learning_session(
                learning_type=LearningType.CONTINUOUS,
                context={"activation_time": datetime.now().isoformat()}
            )
            
            self.activated_systems.append({
                "name": "통합 학습 시스템",
                "session_id": session.id,
                "status": "활성화됨",
                "start_time": datetime.now()
            })
            
            logger.info(f"✅ 통합 학습 시스템 활성화 완료: {session.id}")
            return {"success": True, "session_id": session.id}
            
        except Exception as e:
            logger.error(f"❌ 통합 학습 시스템 활성화 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def activate_autonomous_learning_system(self) -> Dict[str, Any]:
        """자율 학습 시스템 활성화"""
        try:
            from duri_modules.autonomous.continuous_learner import AutonomousLearner
            from duri_modules.autonomous.duri_autonomous_core import DuRiAutonomousCore
            
            # 자율 학습 시작
            autonomous_learner = AutonomousLearner()
            autonomous_core = DuRiAutonomousCore()
            
            # 자율 학습 시작
            learner_started = autonomous_learner.start_autonomous_learning()
            core_started = await autonomous_core.start_autonomous_learning()
            
            if learner_started and core_started:
                self.activated_systems.append({
                    "name": "자율 학습 시스템",
                    "session_id": autonomous_learner.current_session.session_id if autonomous_learner.current_session else "N/A",
                    "status": "활성화됨",
                    "start_time": datetime.now()
                })
                
                logger.info("✅ 자율 학습 시스템 활성화 완료")
                return {"success": True, "learner_active": learner_started, "core_active": core_started}
            else:
                logger.error("❌ 자율 학습 시스템 활성화 실패")
                return {"success": False, "learner_active": learner_started, "core_active": core_started}
                
        except Exception as e:
            logger.error(f"❌ 자율 학습 시스템 활성화 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def activate_learning_loop_manager(self) -> Dict[str, Any]:
        """학습 루프 매니저 활성화"""
        try:
            from duri_brain.learning.learning_loop_manager import get_learning_loop_manager
            
            learning_loop_manager = get_learning_loop_manager()
            
            # 초기 전략 설정
            initial_strategy = {
                "learning_type": "continuous",
                "intensity": "moderate",
                "focus_areas": ["general", "problem_solving", "creativity"],
                "meta_learning_enabled": True,
                "self_assessment_enabled": True
            }
            
            # 학습 루프 시작
            cycle_id = learning_loop_manager.start_learning_loop(initial_strategy)
            
            self.activated_systems.append({
                "name": "학습 루프 매니저",
                "session_id": cycle_id,
                "status": "활성화됨",
                "start_time": datetime.now()
            })
            
            logger.info(f"✅ 학습 루프 매니저 활성화 완료: {cycle_id}")
            return {"success": True, "cycle_id": cycle_id}
            
        except Exception as e:
            logger.error(f"❌ 학습 루프 매니저 활성화 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def activate_realtime_learner(self) -> Dict[str, Any]:
        """실시간 학습 시스템 활성화"""
        try:
            from duri_modules.autonomous.realtime_learner import RealtimeLearner
            from duri_modules.autonomous.continuous_learner import AutonomousLearner
            
            autonomous_learner = AutonomousLearner()
            realtime_learner = RealtimeLearner(autonomous_learner)
            
            # 실시간 학습 시작
            realtime_learner.start_realtime_learning()
            
            self.activated_systems.append({
                "name": "실시간 학습 시스템",
                "session_id": realtime_learner.current_session.session_id if realtime_learner.current_session else "N/A",
                "status": "활성화됨",
                "start_time": datetime.now()
            })
            
            logger.info("✅ 실시간 학습 시스템 활성화 완료")
            return {"success": True}
            
        except Exception as e:
            logger.error(f"❌ 실시간 학습 시스템 활성화 실패: {e}")
            return {"success": False, "error": str(e)}
    
    async def activate_all_learning_systems(self) -> Dict[str, Any]:
        """모든 학습 시스템 활성화"""
        print("🚀 DuRi 학습 시스템 활성화 시작")
        print("=" * 50)
        
        activation_results = {}
        
        # 1. 통합 학습 시스템 활성화
        print("\n1️⃣ 통합 학습 시스템 활성화 중...")
        result = await self.activate_unified_learning_system()
        activation_results["unified_learning"] = result
        if result["success"]:
            print("   ✅ 통합 학습 시스템 활성화 완료")
        else:
            print(f"   ❌ 통합 학습 시스템 활성화 실패: {result.get('error', '알 수 없는 오류')}")
        
        # 2. 자율 학습 시스템 활성화
        print("\n2️⃣ 자율 학습 시스템 활성화 중...")
        result = await self.activate_autonomous_learning_system()
        activation_results["autonomous_learning"] = result
        if result["success"]:
            print("   ✅ 자율 학습 시스템 활성화 완료")
        else:
            print(f"   ❌ 자율 학습 시스템 활성화 실패: {result.get('error', '알 수 없는 오류')}")
        
        # 3. 학습 루프 매니저 활성화
        print("\n3️⃣ 학습 루프 매니저 활성화 중...")
        result = await self.activate_learning_loop_manager()
        activation_results["learning_loop_manager"] = result
        if result["success"]:
            print("   ✅ 학습 루프 매니저 활성화 완료")
        else:
            print(f"   ❌ 학습 루프 매니저 활성화 실패: {result.get('error', '알 수 없는 오류')}")
        
        # 4. 실시간 학습 시스템 활성화
        print("\n4️⃣ 실시간 학습 시스템 활성화 중...")
        result = await self.activate_realtime_learner()
        activation_results["realtime_learner"] = result
        if result["success"]:
            print("   ✅ 실시간 학습 시스템 활성화 완료")
        else:
            print(f"   ❌ 실시간 학습 시스템 활성화 실패: {result.get('error', '알 수 없는 오류')}")
        
        # 결과 요약
        print("\n📊 활성화 결과 요약")
        print("-" * 30)
        
        successful_activations = sum(1 for result in activation_results.values() if result["success"])
        total_systems = len(activation_results)
        
        for system_name, result in activation_results.items():
            status = "✅ 성공" if result["success"] else "❌ 실패"
            print(f"   {system_name}: {status}")
        
        print(f"\n🎯 전체 성공률: {successful_activations}/{total_systems}")
        
        if successful_activations == total_systems:
            print("\n🎉 모든 학습 시스템이 성공적으로 활성화되었습니다!")
            print("이제 DuRi가 자가학습을 시작합니다.")
        elif successful_activations > 0:
            print(f"\n⚠️ 일부 학습 시스템만 활성화되었습니다. ({successful_activations}/{total_systems})")
        else:
            print("\n🚨 모든 학습 시스템 활성화에 실패했습니다.")
        
        return {
            "total_systems": total_systems,
            "successful_activations": successful_activations,
            "activation_results": activation_results,
            "activated_systems": self.activated_systems
        }
    
    async def start_monitoring(self):
        """학습 시스템 모니터링 시작"""
        print("\n🔍 학습 시스템 모니터링 시작...")
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                await self._monitor_systems()
                await asyncio.sleep(self.monitoring_interval)
            except KeyboardInterrupt:
                print("\n🛑 모니터링 중단 요청됨")
                break
            except Exception as e:
                logger.error(f"모니터링 중 오류: {e}")
                await asyncio.sleep(10)  # 오류 시 10초 대기
    
    async def _monitor_systems(self):
        """시스템 모니터링"""
        print(f"\n📊 학습 시스템 상태 모니터링 - {datetime.now().strftime('%H:%M:%S')}")
        print("-" * 50)
        
        for system in self.activated_systems:
            runtime = datetime.now() - system["start_time"]
            runtime_str = str(runtime).split('.')[0]  # 마이크로초 제거
            
            print(f"  {system['name']}: {system['status']} (실행 시간: {runtime_str})")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        self.monitoring_active = False
        print("\n🛑 모니터링 중지됨")

async def main():
    """메인 함수"""
    activator = LearningSystemActivator()
    
    # 모든 학습 시스템 활성화
    result = await activator.activate_all_learning_systems()
    
    if result["successful_activations"] > 0:
        print("\n🔍 모니터링을 시작하시겠습니까? (y/n): ", end="")
        try:
            response = input().lower().strip()
            if response in ['y', 'yes', '네']:
                await activator.start_monitoring()
            else:
                print("모니터링을 시작하지 않습니다.")
        except KeyboardInterrupt:
            print("\n프로그램을 종료합니다.")
    else:
        print("\n❌ 활성화된 시스템이 없어 모니터링을 시작할 수 없습니다.")

if __name__ == "__main__":
    asyncio.run(main())
