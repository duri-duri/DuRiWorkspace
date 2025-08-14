#!/usr/bin/env python3
"""
DuRi Orchestrator
DuRi의 중앙 제어 시스템 - DuRi의 심장

기능:
1. judgment → action → feedback 실행 루프 관리
2. 시스템 간 통합 및 조율
3. 상태 관리 및 모니터링
4. 의사결정 엔진
"""

import asyncio
import json
import time
import logging
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import importlib
import sys

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class SystemStatus:
    """시스템 상태 정보"""
    name: str
    status: str  # 'active', 'inactive', 'error'
    last_activity: datetime
    error_count: int = 0
    performance_score: float = 0.0

@dataclass
class ExecutionContext:
    """실행 컨텍스트"""
    input_data: Any
    current_phase: str  # 'judgment', 'action', 'feedback'
    system_states: Dict[str, SystemStatus]
    execution_history: List[Dict]
    metadata: Dict[str, Any]

class DuRiOrchestrator:
    """DuRi 중앙 제어 시스템"""
    
    def __init__(self):
        self.systems: Dict[str, Any] = {}
        self.system_status: Dict[str, SystemStatus] = {}
        self.execution_loop_active = False
        self.performance_metrics = {}
        self.error_log = []
        
        # 실행 루프 구성 요소
        self.judgment_system = None
        self.action_system = None
        self.feedback_system = None
        
        # 시스템 초기화
        self._initialize_systems()
    
    def _initialize_systems(self):
        """시스템 초기화"""
        logger.info("🔧 DuRi 시스템 초기화 시작...")
        
        try:
            # 기존 시스템들 로드 시도
            self._load_existing_systems()
            
            # 핵심 시스템 상태 확인
            self._check_core_systems()
            
            # 시스템 상태 초기화
            self._initialize_system_status()
            
            logger.info("✅ 시스템 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ 시스템 초기화 실패: {e}")
            self.error_log.append(f"초기화 실패: {e}")
    
    def _load_existing_systems(self):
        """기존 시스템들 로드"""
        logger.info("📦 기존 시스템 로드 중...")
        
        # 현재 디렉토리를 sys.path에 추가
        current_dir = Path(__file__).parent
        sys.path.insert(0, str(current_dir))
        
        # 로드할 시스템 목록
        systems_to_load = [
            'judgment_system',
            'action_system', 
            'feedback_system',
            'memory_association',
            'memory_classification',
            'enhanced_memory_system'
        ]
        
        for system_name in systems_to_load:
            try:
                # 모듈 import 시도
                module = importlib.import_module(system_name)
                self.systems[system_name] = module
                logger.info(f"✅ {system_name} 로드 성공")
                
            except ImportError as e:
                logger.warning(f"⚠️  {system_name} 로드 실패: {e}")
                self.error_log.append(f"{system_name} 로드 실패: {e}")
    
    def _check_core_systems(self):
        """핵심 시스템 상태 확인"""
        logger.info("🔍 핵심 시스템 상태 확인...")
        
        core_systems = ['judgment_system', 'action_system', 'feedback_system']
        
        for system_name in core_systems:
            if system_name in self.systems:
                logger.info(f"✅ {system_name} 존재")
            else:
                logger.warning(f"⚠️  {system_name} 없음 - 대체 구현 필요")
    
    def _initialize_system_status(self):
        """시스템 상태 초기화"""
        for system_name in self.systems.keys():
            self.system_status[system_name] = SystemStatus(
                name=system_name,
                status='inactive',
                last_activity=datetime.now(),
                error_count=0,
                performance_score=0.0
            )
    
    async def start_execution_loop(self):
        """실행 루프 시작"""
        logger.info("🚀 DuRi 실행 루프 시작")
        
        if self.execution_loop_active:
            logger.warning("⚠️  실행 루프가 이미 활성화되어 있습니다")
            return
        
        self.execution_loop_active = True
        
        try:
            while self.execution_loop_active:
                # 1. Judgment Phase
                await self._execute_judgment_phase()
                
                # 2. Action Phase
                await self._execute_action_phase()
                
                # 3. Feedback Phase
                await self._execute_feedback_phase()
                
                # 4. 시스템 상태 업데이트
                await self._update_system_status()
                
                # 5. 성능 모니터링
                await self._monitor_performance()
                
                # 6. 잠시 대기
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"❌ 실행 루프 오류: {e}")
            self.error_log.append(f"실행 루프 오류: {e}")
            self.execution_loop_active = False
    
    async def _execute_judgment_phase(self):
        """판단 단계 실행"""
        logger.info("🧠 Judgment Phase 실행")
        
        try:
            # 판단 시스템 호출
            if 'judgment_system' in self.systems:
                judgment_result = await self._call_judgment_system()
                logger.info(f"✅ 판단 결과: {judgment_result}")
            else:
                # 기본 판단 로직
                judgment_result = await self._default_judgment()
                logger.info(f"✅ 기본 판단 결과: {judgment_result}")
            
            # 판단 결과 저장
            self._store_judgment_result(judgment_result)
            
        except Exception as e:
            logger.error(f"❌ Judgment Phase 오류: {e}")
            self.error_log.append(f"Judgment Phase 오류: {e}")
    
    async def _execute_action_phase(self):
        """행동 단계 실행"""
        logger.info("⚡ Action Phase 실행")
        
        try:
            # 행동 시스템 호출
            if 'action_system' in self.systems:
                action_result = await self._call_action_system()
                logger.info(f"✅ 행동 결과: {action_result}")
            else:
                # 기본 행동 로직
                action_result = await self._default_action()
                logger.info(f"✅ 기본 행동 결과: {action_result}")
            
            # 행동 결과 저장
            self._store_action_result(action_result)
            
        except Exception as e:
            logger.error(f"❌ Action Phase 오류: {e}")
            self.error_log.append(f"Action Phase 오류: {e}")
    
    async def _execute_feedback_phase(self):
        """피드백 단계 실행"""
        logger.info("🔄 Feedback Phase 실행")
        
        try:
            # 피드백 시스템 호출
            if 'feedback_system' in self.systems:
                feedback_result = await self._call_feedback_system()
                logger.info(f"✅ 피드백 결과: {feedback_result}")
            else:
                # 기본 피드백 로직
                feedback_result = await self._default_feedback()
                logger.info(f"✅ 기본 피드백 결과: {feedback_result}")
            
            # 피드백 결과 저장
            self._store_feedback_result(feedback_result)
            
        except Exception as e:
            logger.error(f"❌ Feedback Phase 오류: {e}")
            self.error_log.append(f"Feedback Phase 오류: {e}")
    
    async def _call_judgment_system(self):
        """판단 시스템 호출"""
        try:
            judgment_module = self.systems['judgment_system']
            
            # 판단 시스템의 메인 함수 호출
            if hasattr(judgment_module, 'main'):
                result = await judgment_module.main()
                return result
            elif hasattr(judgment_module, 'judge'):
                result = await judgment_module.judge()
                return result
            else:
                return {"status": "no_judgment_function", "message": "판단 함수를 찾을 수 없음"}
                
        except Exception as e:
            logger.error(f"❌ 판단 시스템 호출 실패: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _call_action_system(self):
        """행동 시스템 호출"""
        try:
            action_module = self.systems['action_system']
            
            # 행동 시스템의 메인 함수 호출
            if hasattr(action_module, 'main'):
                result = await action_module.main()
                return result
            elif hasattr(action_module, 'act'):
                result = await action_module.act()
                return result
            else:
                return {"status": "no_action_function", "message": "행동 함수를 찾을 수 없음"}
                
        except Exception as e:
            logger.error(f"❌ 행동 시스템 호출 실패: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _call_feedback_system(self):
        """피드백 시스템 호출"""
        try:
            feedback_module = self.systems['feedback_system']
            
            # 피드백 시스템의 메인 함수 호출
            if hasattr(feedback_module, 'main'):
                result = await feedback_module.main()
                return result
            elif hasattr(feedback_module, 'feedback'):
                result = await feedback_module.feedback()
                return result
            else:
                return {"status": "no_feedback_function", "message": "피드백 함수를 찾을 수 없음"}
                
        except Exception as e:
            logger.error(f"❌ 피드백 시스템 호출 실패: {e}")
            return {"status": "error", "message": str(e)}
    
    async def _default_judgment(self):
        """기본 판단 로직"""
        return {
            "phase": "judgment",
            "status": "success",
            "decision": "continue_execution",
            "confidence": 0.8,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _default_action(self):
        """기본 행동 로직"""
        return {
            "phase": "action",
            "status": "success",
            "action": "system_monitoring",
            "result": "systems_healthy",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _default_feedback(self):
        """기본 피드백 로직"""
        return {
            "phase": "feedback",
            "status": "success",
            "feedback": "execution_loop_healthy",
            "learning": "maintain_current_state",
            "timestamp": datetime.now().isoformat()
        }
    
    def _store_judgment_result(self, result):
        """판단 결과 저장"""
        # 결과를 메모리나 로그에 저장
        logger.info(f"💾 판단 결과 저장: {result}")
    
    def _store_action_result(self, result):
        """행동 결과 저장"""
        # 결과를 메모리나 로그에 저장
        logger.info(f"💾 행동 결과 저장: {result}")
    
    def _store_feedback_result(self, result):
        """피드백 결과 저장"""
        # 결과를 메모리나 로그에 저장
        logger.info(f"💾 피드백 결과 저장: {result}")
    
    async def _update_system_status(self):
        """시스템 상태 업데이트"""
        for system_name, status in self.system_status.items():
            if system_name in self.systems:
                status.status = 'active'
                status.last_activity = datetime.now()
                status.performance_score = min(1.0, status.performance_score + 0.1)
            else:
                status.status = 'inactive'
                status.performance_score = max(0.0, status.performance_score - 0.1)
    
    async def _monitor_performance(self):
        """성능 모니터링"""
        active_systems = sum(1 for status in self.system_status.values() if status.status == 'active')
        total_systems = len(self.system_status)
        
        performance_ratio = active_systems / total_systems if total_systems > 0 else 0
        
        self.performance_metrics = {
            "active_systems": active_systems,
            "total_systems": total_systems,
            "performance_ratio": performance_ratio,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"📊 성능 지표: {active_systems}/{total_systems} 시스템 활성 ({performance_ratio:.1%})")
    
    def stop_execution_loop(self):
        """실행 루프 중지"""
        logger.info("🛑 DuRi 실행 루프 중지")
        self.execution_loop_active = False
    
    def get_system_status(self) -> Dict[str, SystemStatus]:
        """시스템 상태 반환"""
        return self.system_status
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """성능 지표 반환"""
        return self.performance_metrics
    
    def get_error_log(self) -> List[str]:
        """오류 로그 반환"""
        return self.error_log
    
    def generate_status_report(self) -> Dict[str, Any]:
        """상태 리포트 생성"""
        return {
            "orchestrator_status": "active" if self.execution_loop_active else "inactive",
            "system_count": len(self.systems),
            "active_systems": sum(1 for status in self.system_status.values() if status.status == 'active'),
            "performance_metrics": self.performance_metrics,
            "error_count": len(self.error_log),
            "timestamp": datetime.now().isoformat()
        }

async def main():
    """메인 실행 함수"""
    print("🚀 DuRi Orchestrator 시작")
    print("="*50)
    
    # 오케스트레이터 생성
    orchestrator = DuRiOrchestrator()
    
    # 초기 상태 리포트
    initial_report = orchestrator.generate_status_report()
    print(f"📊 초기 상태: {json.dumps(initial_report, indent=2, ensure_ascii=False)}")
    
    try:
        # 실행 루프 시작
        await orchestrator.start_execution_loop()
        
    except KeyboardInterrupt:
        print("\n🛑 사용자에 의해 중단됨")
        orchestrator.stop_execution_loop()
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        orchestrator.stop_execution_loop()
    
    finally:
        # 최종 상태 리포트
        final_report = orchestrator.generate_status_report()
        print(f"📊 최종 상태: {json.dumps(final_report, indent=2, ensure_ascii=False)}")
        
        print("\n✅ DuRi Orchestrator 종료")

if __name__ == "__main__":
    asyncio.run(main()) 