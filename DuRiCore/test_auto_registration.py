#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
자동 등록 실패 재현 및 테스트

이 모듈은 ChatGPT가 지적한 자동 등록 실패 문제를 재현하고 테스트합니다.
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


async def test_auto_registration():
    """자동 등록 테스트"""
    logger.info("🧪 자동 등록 테스트 시작")
    
    try:
        from module_registry import ModuleRegistry, BaseModule, ModulePriority, register_module
        
        # 레지스트리 인스턴스 가져오기
        registry = ModuleRegistry.get_instance()
        
        # 테스트 1: 데코레이터 방식 자동 등록
        logger.info("📝 테스트 1: 데코레이터 방식 자동 등록")
        
        @register_module(name="auto_test_module", dependencies=[], priority=ModulePriority.NORMAL)
        class AutoTestModule(BaseModule):
            async def initialize(self):
                self._initialized = True
                logger.info("AutoTestModule 초기화 완료")
            
            async def execute(self, context):
                return {"status": "success", "message": "AutoTestModule 실행"}
        
        # 자동 등록 확인
        module_info = registry.get_module("auto_test_module")
        if module_info:
            logger.info("✅ 데코레이터 방식 자동 등록 성공")
        else:
            logger.error("❌ 데코레이터 방식 자동 등록 실패")
            return False
        
        # 테스트 2: 메타클래스 방식 자동 등록 (기존 방식)
        logger.info("📝 테스트 2: 메타클래스 방식 자동 등록")
        
        class MetaTestModule(BaseModule):
            module_name = "meta_test_module"
            dependencies = []
            priority = ModulePriority.NORMAL
            
            async def initialize(self):
                self._initialized = True
                logger.info("MetaTestModule 초기화 완료")
            
            async def execute(self, context):
                return {"status": "success", "message": "MetaTestModule 실행"}
        
        # 메타클래스 방식 등록 확인
        module_info = registry.get_module("meta_test_module")
        if module_info:
            logger.info("✅ 메타클래스 방식 자동 등록 성공")
        else:
            logger.warning("⚠️ 메타클래스 방식 자동 등록 실패 (예상됨)")
        
        # 테스트 3: 수동 등록
        logger.info("📝 테스트 3: 수동 등록")
        
        class ManualTestModule(BaseModule):
            async def initialize(self):
                self._initialized = True
                logger.info("ManualTestModule 초기화 완료")
            
            async def execute(self, context):
                return {"status": "success", "message": "ManualTestModule 실행"}
        
        # 수동 등록
        success = registry.register_module(
            name="manual_test_module",
            module_class=ManualTestModule,
            dependencies=[],
            priority=ModulePriority.NORMAL
        )
        
        if success:
            logger.info("✅ 수동 등록 성공")
        else:
            logger.error("❌ 수동 등록 실패")
            return False
        
        # 모든 등록된 모듈 확인
        all_modules = registry.get_all_modules()
        logger.info(f"📊 등록된 모듈 수: {len(all_modules)}")
        for name, info in all_modules.items():
            logger.info(f"   - {name}: {info.state.value}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ 자동 등록 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_import_order_issue():
    """Import 순서 문제 테스트"""
    logger.info("🧪 Import 순서 문제 테스트 시작")
    
    try:
        # 모듈을 새로 import하여 순서 문제 재현
        import importlib
        import module_registry
        
        # 모듈을 다시 로드
        importlib.reload(module_registry)
        
        from module_registry import ModuleRegistry, BaseModule, ModulePriority, register_module
        
        # 레지스트리 인스턴스 가져오기
        registry = ModuleRegistry.get_instance()
        
        # 데코레이터 방식 테스트
        @register_module(name="import_order_test", dependencies=[])
        class ImportOrderTestModule(BaseModule):
            async def initialize(self):
                self._initialized = True
            
            async def execute(self, context):
                return {"status": "success"}
        
        # 등록 확인
        module_info = registry.get_module("import_order_test")
        if module_info:
            logger.info("✅ Import 순서 문제 없음")
            return True
        else:
            logger.error("❌ Import 순서 문제 발생")
            return False
        
    except Exception as e:
        logger.error(f"❌ Import 순서 문제 테스트 실패: {e}")
        return False


async def test_metaclass_conflict():
    """메타클래스 충돌 테스트"""
    logger.info("🧪 메타클래스 충돌 테스트 시작")
    
    try:
        from module_registry import ModuleRegistry, BaseModule, ModulePriority, register_module
        
        # ABC 상속 확인
        if hasattr(BaseModule, '__abstractmethods__'):
            logger.info("✅ BaseModule이 ABC를 상속받고 있음")
        else:
            logger.warning("⚠️ BaseModule이 ABC를 상속받지 않음")
        
        # 메타클래스 확인
        module_metaclass = type(BaseModule)
        logger.info(f"📝 BaseModule 메타클래스: {module_metaclass}")
        
        # 데코레이터 방식으로 테스트
        @register_module(name="metaclass_test", dependencies=[])
        class MetaclassTestModule(BaseModule):
            async def initialize(self):
                self._initialized = True
            
            async def execute(self, context):
                return {"status": "success"}
        
        # 등록 확인
        registry = ModuleRegistry.get_instance()
        module_info = registry.get_module("metaclass_test")
        if module_info:
            logger.info("✅ 메타클래스 충돌 없음")
            return True
        else:
            logger.error("❌ 메타클래스 충돌 발생")
            return False
        
    except Exception as e:
        logger.error(f"❌ 메타클래스 충돌 테스트 실패: {e}")
        return False


async def main():
    """메인 함수"""
    logger.info("🚀 자동 등록 실패 재현 테스트 시작")
    print("=" * 60)
    
    # 테스트 실행
    tests = [
        ("자동 등록 테스트", test_auto_registration),
        ("Import 순서 문제 테스트", test_import_order_issue),
        ("메타클래스 충돌 테스트", test_metaclass_conflict)
    ]
    
    results = {}
    for test_name, test_func in tests:
        print(f"\n🧪 {test_name} 실행 중...")
        try:
            result = await test_func()
            results[test_name] = result
            status = "✅ 성공" if result else "❌ 실패"
            print(f"   {status}")
        except Exception as e:
            results[test_name] = False
            print(f"   ❌ 예외 발생: {e}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📊 테스트 결과 요약:")
    for test_name, result in results.items():
        status = "✅ 성공" if result else "❌ 실패"
        print(f"   {test_name}: {status}")
    
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    print(f"\n🎯 전체 결과: {success_count}/{total_count} 성공")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공했습니다!")
    else:
        print("⚠️ 일부 테스트가 실패했습니다.")
    
    return success_count == total_count


if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
