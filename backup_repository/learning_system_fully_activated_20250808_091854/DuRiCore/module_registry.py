#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DuRi 모듈 레지스트리 시스템

이 모듈은 DuRi 시스템의 모듈들을 관리하는 중앙 레지스트리 시스템입니다.
데코레이터 기반 자동 등록과 메타클래스 기반 자동 등록을 모두 지원합니다.

주요 기능:
- 모듈 자동 등록 (데코레이터 방식 + 메타클래스 방식)
- 의존성 관리
- 모듈 로드 순서 자동화
- 타입 안전성 보장
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod, ABCMeta
from collections import defaultdict, deque
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Type, TypeVar, Generic, Protocol, Callable
import inspect

# 의존성 그래프 import
try:
    from .dependency_graph import DependencyGraph
except ImportError:
    from dependency_graph import DependencyGraph

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

T = TypeVar('T')


class ModuleState(Enum):
    """모듈 상태"""
    UNREGISTERED = "unregistered"
    REGISTERED = "registered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    ERROR = "error"
    DISABLED = "disabled"


class ModulePriority(Enum):
    """모듈 우선순위"""
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    OPTIONAL = 4


@dataclass
class ModuleInfo:
    """모듈 정보"""
    name: str
    module_class: Type
    dependencies: List[str] = field(default_factory=list)
    priority: ModulePriority = ModulePriority.NORMAL
    version: str = "1.0.0"
    description: str = ""
    author: str = "DuRi"
    state: ModuleState = ModuleState.UNREGISTERED
    instance: Optional[Any] = None
    load_time: Optional[datetime] = None
    error_count: int = 0
    last_error: Optional[str] = None
    performance_score: float = 0.0


class ModuleProtocol(Protocol):
    """모듈 프로토콜"""
    async def initialize(self) -> None: ...
    async def execute(self, context: Dict[str, Any]) -> Any: ...
    async def cleanup(self) -> None: ...


# ABC와 ModuleMeta를 결합한 메타클래스
class ABCModuleMeta(ABCMeta):
    """ABC와 ModuleMeta를 결합한 메타클래스"""
    
    def __new__(cls, name: str, bases: tuple, namespace: dict):
        """새로운 클래스 생성 시 자동 등록"""
        module_class = super().__new__(cls, name, bases, namespace)
        
        # BaseModule을 상속받는 클래스인지 확인 (BaseModule 자체는 제외)
        if (name != 'BaseModule' and 
            (any(issubclass(base, BaseModule) for base in bases if isinstance(base, type)) or
             BaseModule in bases)):
            
            # 모듈 이름 확인
            module_name = getattr(module_class, 'module_name', None)
            if module_name:
                try:
                    # 레지스트리에 등록
                    registry = ModuleRegistry.get_instance()
                    dependencies = getattr(module_class, 'dependencies', [])
                    priority = getattr(module_class, 'priority', ModulePriority.NORMAL)
                    version = getattr(module_class, 'version', '1.0.0')
                    description = getattr(module_class, 'description', '')
                    author = getattr(module_class, 'author', 'DuRi')
                    
                    success = registry.register_module(
                        name=module_name,
                        module_class=module_class,
                        dependencies=dependencies,
                        priority=priority,
                        version=version,
                        description=description,
                        author=author
                    )
                    
                    if success:
                        logger.info(f"✅ 모듈 자동 등록 완료 (메타클래스): {module_name}")
                    else:
                        logger.warning(f"⚠️ 모듈 자동 등록 실패 (메타클래스): {module_name}")
                        
                except Exception as e:
                    logger.error(f"❌ 모듈 자동 등록 중 오류 발생 (메타클래스): {module_name} - {e}")
        
        return module_class


class BaseModule(ABC, metaclass=ABCModuleMeta):
    """기본 모듈 클래스"""
    
    def __init__(self):
        self._initialized = False
        self._context: Dict[str, Any] = {}
    
    @abstractmethod
    async def initialize(self) -> None:
        """모듈 초기화"""
        pass
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> Any:
        """모듈 실행"""
        pass
    
    async def cleanup(self) -> None:
        """모듈 정리"""
        self._initialized = False
    
    @property
    def is_initialized(self) -> bool:
        """초기화 상태 확인"""
        return self._initialized


def register_module(name: str = None, dependencies: List[str] = None, 
                   priority: ModulePriority = ModulePriority.NORMAL,
                   version: str = "1.0.0", description: str = "", 
                   author: str = "DuRi") -> Callable:
    """
    모듈 등록 데코레이터
    
    Args:
        name: 모듈 이름 (None이면 클래스 이름 사용)
        dependencies: 의존성 목록
        priority: 모듈 우선순위
        version: 모듈 버전
        description: 모듈 설명
        author: 모듈 작성자
    
    Returns:
        데코레이터 함수
    """
    def decorator(cls: Type) -> Type:
        # 모듈 이름 결정
        module_name = name or getattr(cls, 'module_name', None) or cls.__name__
        
        # 의존성 결정
        module_dependencies = dependencies or getattr(cls, 'dependencies', [])
        
        # 우선순위 결정
        module_priority = priority or getattr(cls, 'priority', ModulePriority.NORMAL)
        
        # 버전 결정
        module_version = version or getattr(cls, 'version', '1.0.0')
        
        # 설명 결정
        module_description = description or getattr(cls, 'description', '')
        
        # 작성자 결정
        module_author = author or getattr(cls, 'author', 'DuRi')
        
        try:
            # 레지스트리에 등록
            registry = ModuleRegistry.get_instance()
            success = registry.register_module(
                name=module_name,
                module_class=cls,
                dependencies=module_dependencies,
                priority=module_priority,
                version=module_version,
                description=module_description,
                author=module_author
            )
            
            if success:
                logger.info(f"✅ 모듈 등록 완료 (데코레이터): {module_name}")
            else:
                logger.warning(f"⚠️ 모듈 등록 실패 (데코레이터): {module_name}")
                
        except Exception as e:
            logger.error(f"❌ 모듈 등록 중 오류 발생 (데코레이터): {module_name} - {e}")
        
        return cls
    
    return decorator


class ModuleRegistry:
    """모듈 레지스트리 싱글톤 클래스"""
    
    _instance: Optional['ModuleRegistry'] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self.modules: Dict[str, ModuleInfo] = {}
            self.dependency_graph = DependencyGraph()
            self._initialized = True
            logger.info("🔧 모듈 레지스트리 초기화 완료")
    
    @classmethod
    def get_instance(cls) -> 'ModuleRegistry':
        """싱글톤 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register_module(self, name: str, module_class: Type, 
                       dependencies: List[str] = None, 
                       priority: ModulePriority = ModulePriority.NORMAL,
                       version: str = "1.0.0",
                       description: str = "",
                       author: str = "DuRi") -> bool:
        """모듈 등록"""
        try:
            if name in self.modules:
                logger.warning(f"⚠️ 모듈이 이미 등록되어 있습니다: {name}")
                return False
            
            # 모듈 정보 생성
            module_info = ModuleInfo(
                name=name,
                module_class=module_class,
                dependencies=dependencies or [],
                priority=priority,
                version=version,
                description=description,
                author=author,
                state=ModuleState.REGISTERED
            )
            
            # 모듈 등록
            self.modules[name] = module_info
            
            # 의존성 그래프에 추가
            for dep in module_info.dependencies:
                self.dependency_graph.add_dependency(name, dep)
            
            logger.info(f"✅ 모듈 등록 완료: {name} (의존성: {dependencies or []})")
            return True
            
        except Exception as e:
            logger.error(f"❌ 모듈 등록 실패: {name} - {e}")
            return False
    
    def unregister_module(self, name: str) -> bool:
        """모듈 등록 해제"""
        try:
            if name not in self.modules:
                logger.warning(f"⚠️ 등록되지 않은 모듈: {name}")
                return False
            
            # 의존성 그래프에서 제거
            module_info = self.modules[name]
            for dep in module_info.dependencies:
                self.dependency_graph.remove_dependency(name, dep)
            
            # 모듈 제거
            del self.modules[name]
            
            logger.info(f"✅ 모듈 등록 해제 완료: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 모듈 등록 해제 실패: {name} - {e}")
            return False
    
    def get_module(self, name: str) -> Optional[ModuleInfo]:
        """모듈 정보 반환"""
        return self.modules.get(name)
    
    def get_module_instance(self, name: str) -> Optional[Any]:
        """모듈 인스턴스 반환"""
        module_info = self.get_module(name)
        if module_info and module_info.instance:
            return module_info.instance
        return None
    
    def get_all_modules(self) -> Dict[str, ModuleInfo]:
        """모든 모듈 정보 반환"""
        return self.modules.copy()
    
    def get_modules_by_priority(self, priority: ModulePriority) -> List[ModuleInfo]:
        """우선순위별 모듈 목록 반환"""
        return [info for info in self.modules.values() if info.priority == priority]
    
    async def load_module(self, name: str) -> bool:
        """모듈 로드"""
        try:
            module_info = self.get_module(name)
            if not module_info:
                logger.error(f"❌ 등록되지 않은 모듈: {name}")
                return False
            
            if module_info.state == ModuleState.LOADED:
                logger.info(f"ℹ️ 모듈이 이미 로드되어 있습니다: {name}")
                return True
            
            # 의존성 확인
            for dep in module_info.dependencies:
                if not await self.load_module(dep):
                    logger.error(f"❌ 의존성 로드 실패: {name} -> {dep}")
                    return False
            
            # 모듈 인스턴스 생성
            module_info.instance = module_info.module_class()
            module_info.state = ModuleState.LOADED
            module_info.load_time = datetime.now()
            
            logger.info(f"✅ 모듈 로드 완료: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 모듈 로드 실패: {name} - {e}")
            if module_info:
                module_info.state = ModuleState.ERROR
                module_info.last_error = str(e)
                module_info.error_count += 1
            return False
    
    async def initialize_module(self, name: str) -> bool:
        """모듈 초기화"""
        try:
            module_info = self.get_module(name)
            if not module_info:
                logger.error(f"❌ 등록되지 않은 모듈: {name}")
                return False
            
            if module_info.state == ModuleState.INITIALIZED:
                logger.info(f"ℹ️ 모듈이 이미 초기화되어 있습니다: {name}")
                return True
            
            if module_info.state != ModuleState.LOADED:
                if not await self.load_module(name):
                    return False
            
            # 모듈 초기화
            if hasattr(module_info.instance, 'initialize'):
                await module_info.instance.initialize()
            
            module_info.state = ModuleState.INITIALIZED
            logger.info(f"✅ 모듈 초기화 완료: {name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 모듈 초기화 실패: {name} - {e}")
            if module_info:
                module_info.state = ModuleState.ERROR
                module_info.last_error = str(e)
                module_info.error_count += 1
            return False
    
    async def load_all_modules(self) -> Dict[str, bool]:
        """모든 모듈 로드"""
        results = {}
        
        try:
            # 로드 순서 결정
            load_order = self.dependency_graph.get_load_order()
            
            # 등록된 모듈 중 로드 순서에 없는 모듈들 추가
            registered_modules = set(self.modules.keys())
            for module in registered_modules:
                if module not in load_order:
                    load_order.append(module)
            
            # 순서대로 모듈 로드
            for module_name in load_order:
                if module_name in self.modules:
                    results[module_name] = await self.load_module(module_name)
            
            logger.info(f"✅ 모든 모듈 로드 완료: {sum(results.values())}/{len(results)} 성공")
            return results
            
        except Exception as e:
            logger.error(f"❌ 전체 모듈 로드 실패: {e}")
            return results
    
    async def initialize_all_modules(self) -> Dict[str, bool]:
        """모든 모듈 초기화"""
        results = {}
        
        try:
            # 로드 순서대로 초기화
            load_order = self.dependency_graph.get_load_order()
            
            for module_name in load_order:
                if module_name in self.modules:
                    results[module_name] = await self.initialize_module(module_name)
            
            logger.info(f"✅ 모든 모듈 초기화 완료: {sum(results.values())}/{len(results)} 성공")
            return results
            
        except Exception as e:
            logger.error(f"❌ 전체 모듈 초기화 실패: {e}")
            return results
    
    def get_module_status(self) -> Dict[str, Dict[str, Any]]:
        """모듈 상태 요약"""
        status = {}
        for name, info in self.modules.items():
            status[name] = {
                'state': info.state.value,
                'priority': info.priority.value,
                'dependencies': info.dependencies,
                'error_count': info.error_count,
                'last_error': info.last_error,
                'load_time': info.load_time.isoformat() if info.load_time else None,
                'performance_score': info.performance_score
            }
        return status
    
    def validate_dependencies(self) -> List[str]:
        """의존성 검증"""
        errors = []
        
        for name, info in self.modules.items():
            for dep in info.dependencies:
                if dep not in self.modules:
                    errors.append(f"모듈 '{name}'의 의존성 '{dep}'가 등록되지 않았습니다")
        
        if self.dependency_graph.has_cycle():
            errors.append("의존성 사이클이 감지되었습니다")
        
        return errors


# 전역 레지스트리 인스턴스
registry = ModuleRegistry.get_instance()


async def test_module_registry():
    """모듈 레지스트리 테스트"""
    logger.info("🧪 모듈 레지스트리 테스트 시작")
    
    # 테스트용 모듈 클래스 (데코레이터 방식)
    @register_module(name="test_module", dependencies=[], priority=ModulePriority.NORMAL)
    class TestModule(BaseModule):
        async def initialize(self):
            self._initialized = True
            logger.info("테스트 모듈 초기화 완료")
        
        async def execute(self, context: Dict[str, Any]):
            return {"status": "success", "message": "테스트 모듈 실행"}
    
    # 레지스트리에서 모듈 확인
    module_info = registry.get_module("test_module")
    if module_info:
        logger.info(f"✅ 데코레이터 모듈 등록 확인: {module_info.name}")
    else:
        logger.error("❌ 데코레이터 모듈 등록 실패")
        return False
    
    # 모듈 로드 테스트
    success_load = await registry.load_module("test_module")
    if success_load:
        logger.info("✅ 데코레이터 모듈 로드 성공")
    else:
        logger.error("❌ 데코레이터 모듈 로드 실패")
        return False
    
    # 모듈 초기화 테스트
    success_init = await registry.initialize_module("test_module")
    if success_init:
        logger.info("✅ 데코레이터 모듈 초기화 성공")
    else:
        logger.error("❌ 데코레이터 모듈 초기화 실패")
        return False
    
    logger.info("🧪 모듈 레지스트리 테스트 완료")
    return True


if __name__ == "__main__":
    asyncio.run(test_module_registry())
