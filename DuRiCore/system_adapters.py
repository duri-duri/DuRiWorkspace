#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 시스템 어댑터

이 모듈은 기존 시스템들을 새로운 모듈 레지스트리 시스템과 호환되도록 하는 어댑터들을 제공합니다.
기존 시스템들을 BaseModule을 상속받는 형태로 래핑하여 모듈 레지스트리에 등록할 수 있게 합니다.

주요 기능:
- 기존 시스템 어댑터
- 호환성 래퍼
- 자동 등록 지원
"""

import asyncio
import logging
from typing import Any, Dict, Optional

# 모듈 레지스트리 시스템 import
try:
    from module_registry import BaseModule, ModuleMeta, ModulePriority  # noqa: F401

    MODULE_REGISTRY_AVAILABLE = True
except ImportError:
    MODULE_REGISTRY_AVAILABLE = False

    # ModulePriority가 없을 때 안전한 폴백 제공
    class ModulePriority:
        LOW = 10
        NORMAL = 50
        HIGH = 80
        CRITICAL = 100


logger = logging.getLogger(__name__)


class SystemAdapter(BaseModule):
    """시스템 어댑터 기본 클래스"""

    def __init__(self, original_system: Any):
        super().__init__()
        self.original_system = original_system
        self._wrapped_methods = {}

    async def initialize(self) -> None:
        """어댑터 초기화"""
        if hasattr(self.original_system, "initialize"):
            if asyncio.iscoroutinefunction(self.original_system.initialize):
                await self.original_system.initialize()
            else:
                self.original_system.initialize()
        self._initialized = True

    async def execute(self, context: Dict[str, Any]) -> Any:
        """어댑터 실행"""
        if hasattr(self.original_system, "execute"):
            if asyncio.iscoroutinefunction(self.original_system.execute):
                return await self.original_system.execute(context)
            else:
                return self.original_system.execute(context)
        return None

    def __getattr__(self, name: str) -> Any:
        """원본 시스템의 속성에 접근"""
        if hasattr(self.original_system, name):
            return getattr(self.original_system, name)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class JudgmentSystemAdapter(SystemAdapter):
    """판단 시스템 어댑터"""

    module_name = "judgment_system"
    dependencies = []
    priority = ModulePriority.CRITICAL
    description = "판단 시스템 어댑터"
    version = "1.0.0"
    author = "DuRi"

    async def execute(self, context: Dict[str, Any]) -> Any:
        """판단 시스템 실행"""
        if hasattr(self.original_system, "judge"):
            if asyncio.iscoroutinefunction(self.original_system.judge):
                return await self.original_system.judge(context)
            else:
                return self.original_system.judge(context)
        return {
            "status": "no_judgment_method",
            "message": "판단 시스템에 judge 메서드가 없습니다",
        }


class ActionSystemAdapter(SystemAdapter):
    """행동 시스템 어댑터"""

    module_name = "action_system"
    dependencies = ["judgment_system"]
    priority = ModulePriority.CRITICAL
    description = "행동 시스템 어댑터"
    version = "1.0.0"
    author = "DuRi"

    async def execute(self, context: Dict[str, Any]) -> Any:
        """행동 시스템 실행"""
        if hasattr(self.original_system, "act"):
            if asyncio.iscoroutinefunction(self.original_system.act):
                return await self.original_system.act(context)
            else:
                return self.original_system.act(context)
        return {
            "status": "no_action_method",
            "message": "행동 시스템에 act 메서드가 없습니다",
        }


class FeedbackSystemAdapter(SystemAdapter):
    """피드백 시스템 어댑터"""

    module_name = "feedback_system"
    dependencies = ["action_system"]
    priority = ModulePriority.HIGH
    description = "피드백 시스템 어댑터"
    version = "1.0.0"
    author = "DuRi"

    async def execute(self, context: Dict[str, Any]) -> Any:
        """피드백 시스템 실행"""
        if hasattr(self.original_system, "feedback"):
            if asyncio.iscoroutinefunction(self.original_system.feedback):
                return await self.original_system.feedback(context)
            else:
                return self.original_system.feedback(context)
        return {
            "status": "no_feedback_method",
            "message": "피드백 시스템에 feedback 메서드가 없습니다",
        }


class MemorySystemAdapter(SystemAdapter):
    """메모리 시스템 어댑터"""

    module_name = "memory_system"
    dependencies = []
    priority = ModulePriority.HIGH
    description = "메모리 시스템 어댑터"
    version = "1.0.0"
    author = "DuRi"

    async def execute(self, context: Dict[str, Any]) -> Any:
        """메모리 시스템 실행"""
        if hasattr(self.original_system, "store"):
            if asyncio.iscoroutinefunction(self.original_system.store):
                return await self.original_system.store(context)
            else:
                return self.original_system.store(context)
        return {
            "status": "no_memory_method",
            "message": "메모리 시스템에 store 메서드가 없습니다",
        }


class SocialIntelligenceSystemAdapter(SystemAdapter):
    """사회적 지능 시스템 어댑터"""

    module_name = "social_intelligence_system"
    dependencies = ["judgment_system", "memory_system"]
    priority = ModulePriority.NORMAL
    description = "사회적 지능 시스템 어댑터"
    version = "1.0.0"
    author = "DuRi"

    async def execute(self, context: Dict[str, Any]) -> Any:
        """사회적 지능 시스템 실행"""
        if hasattr(self.original_system, "process_social_interaction"):
            if asyncio.iscoroutinefunction(self.original_system.process_social_interaction):
                return await self.original_system.process_social_interaction(context)
            else:
                return self.original_system.process_social_interaction(context)
        return {
            "status": "no_social_method",
            "message": "사회적 지능 시스템에 process_social_interaction 메서드가 없습니다",
        }


class SystemAdapterFactory:
    """시스템 어댑터 팩토리"""

    _adapters = {
        "judgment_system": JudgmentSystemAdapter,
        "action_system": ActionSystemAdapter,
        "feedback_system": FeedbackSystemAdapter,
        "memory_system": MemorySystemAdapter,
        "social_intelligence_system": SocialIntelligenceSystemAdapter,
    }

    @classmethod
    def create_adapter(cls, system_name: str, original_system: Any) -> Optional[SystemAdapter]:
        """어댑터 생성"""
        adapter_class = cls._adapters.get(system_name)
        if adapter_class:
            return adapter_class(original_system)
        return None

    @classmethod
    def register_system(cls, system_name: str, original_system: Any) -> bool:
        """시스템을 어댑터로 래핑하여 등록"""
        try:
            adapter = cls.create_adapter(system_name, original_system)
            if adapter:
                logger.info(f"✅ 시스템 어댑터 등록 완료: {system_name}")
                return True
            else:
                logger.warning(f"⚠️  지원되지 않는 시스템: {system_name}")
                return False
        except Exception as e:
            logger.error(f"❌ 시스템 어댑터 등록 실패: {system_name} - {e}")
            return False

    @classmethod
    def get_supported_systems(cls) -> list:
        """지원되는 시스템 목록 반환"""
        return list(cls._adapters.keys())


# 기존 시스템들을 자동으로 어댑터로 래핑하는 함수
async def wrap_existing_systems(systems: Dict[str, Any]) -> Dict[str, SystemAdapter]:
    """기존 시스템들을 어댑터로 래핑"""
    wrapped_systems = {}

    for system_name, system in systems.items():
        try:
            adapter = SystemAdapterFactory.create_adapter(system_name, system)
            if adapter:
                wrapped_systems[system_name] = adapter
                logger.info(f"✅ 시스템 래핑 완료: {system_name}")
            else:
                logger.warning(f"⚠️  지원되지 않는 시스템: {system_name}")
        except Exception as e:
            logger.error(f"❌ 시스템 래핑 실패: {system_name} - {e}")

    return wrapped_systems


# 테스트 함수
async def test_system_adapters():
    """시스템 어댑터 테스트"""
    logger.info("🧪 시스템 어댑터 테스트 시작")

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

    logger.info("🧪 시스템 어댑터 테스트 완료")


if __name__ == "__main__":
    asyncio.run(test_system_adapters())
