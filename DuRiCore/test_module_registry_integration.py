#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 모듈 레지스트리 통합 테스트

이 모듈은 새로운 모듈 레지스트리 시스템과 DuRi Orchestrator의 통합을 테스트합니다.
"""

import asyncio
import logging
import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
sys.path.append(str(Path(__file__).parent))

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_module_registry():
    """모듈 레지스트리 테스트"""
    logger.info("🧪 모듈 레지스트리 테스트 시작")
    
    try:
        from module_registry import ModuleRegistry, BaseModule, ModulePriority
        
        # 레지스트리 인스턴스 가져오기
        registry = ModuleRegistry.get_instance()
        
        # 테스트용 모듈 클래스
        class TestModule(BaseModule):
            module_name = "test_module"
            dependencies = []
            priority = ModulePriority.NORMAL
            description = "테스트 모듈"
            
            async def initialize(self):
                self._initialized = True
                logger.info("테스트 모듈 초기화 완료")
            
            async def execute(self, context):
                return {"status": "success", "message": "테스트 모듈 실행"}
        
        # 수동으로 모듈 등록
        test_module_class = TestModule
        success = registry.register_module(
            name="test_module",
            module_class=test_module_class,
            dependencies=[],
            priority=ModulePriority.NORMAL,
            version="1.0.0",
            description="테스트 모듈",
            author="DuRi"
        )
        
        if not success:
            logger.error("❌ 테스트 모듈 등록 실패")
            return False
        
        # 레지스트리에서 모듈 확인
        module_info = registry.get_module("test_module")
        if module_info:
            logger.info(f"✅ 테스트 모듈 등록 확인: {module_info.name}")
        else:
            logger.error("❌ 테스트 모듈 등록 실패")
            return False
        
        # 모듈 로드 테스트
        success = await registry.load_module("test_module")
        if success:
            logger.info("✅ 테스트 모듈 로드 성공")
        else:
            logger.error("❌ 테스트 모듈 로드 실패")
            return False
        
        # 모듈 초기화 테스트
        success = await registry.initialize_module("test_module")
        if success:
            logger.info("✅ 테스트 모듈 초기화 성공")
        else:
            logger.error("❌ 테스트 모듈 초기화 실패")
            return False
        
        logger.info("🧪 모듈 레지스트리 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 모듈 레지스트리 테스트 실패: {e}")
        return False


async def test_system_adapters():
    """시스템 어댑터 테스트"""
    logger.info("🧪 시스템 어댑터 테스트 시작")
    
    try:
        from system_adapters import SystemAdapterFactory, wrap_existing_systems
        
        # 테스트용 시스템 클래스
        class TestJudgmentSystem:
            def judge(self, context):
                return {"status": "success", "judgment": "테스트 판단"}
        
        class TestActionSystem:
            def act(self, context):
                return {"status": "success", "action": "테스트 행동"}
        
        # 어댑터 생성 테스트
        test_judgment = TestJudgmentSystem()
        judgment_adapter = SystemAdapterFactory.create_adapter("judgment_system", test_judgment)
        
        if judgment_adapter:
            # 초기화 테스트
            await judgment_adapter.initialize()
            
            # 실행 테스트
            result = await judgment_adapter.execute({"test": "data"})
            logger.info(f"✅ 판단 시스템 어댑터 테스트 결과: {result}")
        else:
            logger.error("❌ 판단 시스템 어댑터 생성 실패")
            return False
        
        logger.info("🧪 시스템 어댑터 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ 시스템 어댑터 테스트 실패: {e}")
        return False


async def test_duri_orchestrator():
    """DuRi Orchestrator 테스트"""
    logger.info("🧪 DuRi Orchestrator 테스트 시작")
    
    try:
        from duri_orchestrator import DuRiOrchestrator
        
        # 오케스트레이터 인스턴스 생성
        orchestrator = DuRiOrchestrator()
        
        # 시스템 상태 확인
        system_status = orchestrator.get_system_status()
        logger.info(f"✅ 시스템 상태 확인: {len(system_status)}개 시스템")
        
        # 성능 메트릭 확인
        performance_metrics = orchestrator.get_performance_metrics()
        logger.info(f"✅ 성능 메트릭 확인: {len(performance_metrics)}개 메트릭")
        
        # 에러 로그 확인
        error_log = orchestrator.get_error_log()
        if error_log:
            logger.warning(f"⚠️  에러 로그 발견: {len(error_log)}개 에러")
        else:
            logger.info("✅ 에러 로그 없음")
        
        logger.info("🧪 DuRi Orchestrator 테스트 완료")
        return True
        
    except Exception as e:
        logger.error(f"❌ DuRi Orchestrator 테스트 실패: {e}")
        return False


async def test_integration():
    """통합 테스트"""
    logger.info("🧪 통합 테스트 시작")
    
    try:
        # 1. 모듈 레지스트리 테스트
        registry_success = await test_module_registry()
        if not registry_success:
            logger.error("❌ 모듈 레지스트리 테스트 실패")
            return False
        
        # 2. 시스템 어댑터 테스트
        adapter_success = await test_system_adapters()
        if not adapter_success:
            logger.error("❌ 시스템 어댑터 테스트 실패")
            return False
        
        # 3. DuRi Orchestrator 테스트
        orchestrator_success = await test_duri_orchestrator()
        if not orchestrator_success:
            logger.error("❌ DuRi Orchestrator 테스트 실패")
            return False
        
        logger.info("🎉 모든 통합 테스트 성공!")
        return True
        
    except Exception as e:
        logger.error(f"❌ 통합 테스트 실패: {e}")
        return False


async def main():
    """메인 테스트 함수"""
    logger.info("🚀 DuRi 모듈 레지스트리 통합 테스트 시작")
    
    try:
        # 통합 테스트 실행
        success = await test_integration()
        
        if success:
            logger.info("🎉 모든 테스트가 성공적으로 완료되었습니다!")
            return 0
        else:
            logger.error("❌ 일부 테스트가 실패했습니다.")
            return 1
            
    except Exception as e:
        logger.error(f"❌ 테스트 실행 중 오류 발생: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
