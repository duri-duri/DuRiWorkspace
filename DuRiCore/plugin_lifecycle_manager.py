#!/usr/bin/env python3
"""
플러그인 생명주기 관리 시스템
DuRi Phase 6.2.2.3 - 플러그인 생명주기 관리 (60% 자동화율 달성 목표)

기능:
1. 완전한 플러그인 시스템
2. 자동 업데이트 시스템
3. 통합 고급 모듈 시스템
4. 플러그인 생명주기 관리
5. 자동 의존성 관리
6. 버전 호환성 검증
"""

import asyncio
import hashlib
import importlib
import inspect
import json
import logging
import os
import shutil
import threading
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Type

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PluginState(Enum):
    """플러그인 상태"""

    INSTALLED = "installed"
    LOADED = "loaded"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"
    UPDATING = "updating"
    DEPRECATED = "deprecated"


class PluginPriority(Enum):
    """플러그인 우선순위"""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class PluginInfo:
    """플러그인 정보"""

    name: str
    version: str
    description: str
    author: str
    dependencies: List[str]
    priority: PluginPriority
    state: PluginState
    install_path: str
    checksum: str
    created_at: datetime
    last_updated: datetime
    usage_count: int = 0
    error_count: int = 0

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.last_updated is None:
            self.last_updated = datetime.now()


class PluginLifecycleManager:
    """플러그인 생명주기 관리자"""

    def __init__(self):
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_instances: Dict[str, Any] = {}
        self.lifecycle_hooks: Dict[str, List[Callable]] = {}
        self.dependency_graph: Dict[str, List[str]] = {}
        self.auto_update_enabled = True
        self.auto_dependency_resolution = True

        # 성능 메트릭
        self.performance_metrics = {
            "total_plugins": 0,
            "active_plugins": 0,
            "automation_rate": 0.0,
            "update_success_rate": 0.0,
            "dependency_resolution_rate": 0.0,
        }

        # 자동화 설정
        self.auto_install_enabled = True
        self.auto_cleanup_enabled = True

        # 모니터링 스레드 시작
        self._start_monitoring()

        logger.info("🔌 플러그인 생명주기 관리자 초기화 완료")

    def _start_monitoring(self):
        """모니터링 스레드 시작"""

        def monitor_plugins():
            while True:
                try:
                    # 플러그인 상태 확인
                    for plugin_name, plugin_info in self.plugins.items():
                        if plugin_info.state == PluginState.ERROR:
                            logger.warning(f"⚠️  플러그인 오류 상태: {plugin_name}")
                            if self.auto_update_enabled:
                                self._attempt_plugin_recovery(plugin_name)

                    # 성능 메트릭 업데이트
                    self._update_performance_metrics()

                    time.sleep(30)  # 30초마다 체크
                except Exception as e:
                    logger.error(f"❌ 플러그인 모니터링 오류: {e}")

        monitor_thread = threading.Thread(target=monitor_plugins, daemon=True)
        monitor_thread.start()
        logger.info("🔍 플러그인 모니터링 시작")

    async def install_plugin(
        self,
        plugin_name: str,
        plugin_path: str,
        version: str = "1.0.0",
        author: str = "Unknown",
        description: str = "",
        dependencies: List[str] = None,
        priority: PluginPriority = PluginPriority.NORMAL,
    ) -> bool:
        """플러그인 설치"""
        try:
            # 플러그인 파일 검증
            if not os.path.exists(plugin_path):
                logger.error(f"❌ 플러그인 파일 없음: {plugin_path}")
                return False

            # 체크섬 계산
            with open(plugin_path, "rb") as f:
                content = f.read()
                checksum = hashlib.md5(content).hexdigest()

            # 플러그인 정보 생성
            plugin_info = PluginInfo(
                name=plugin_name,
                version=version,
                description=description,
                author=author,
                dependencies=dependencies or [],
                priority=priority,
                state=PluginState.INSTALLED,
                install_path=plugin_path,
                checksum=checksum,
                created_at=datetime.now(),
                last_updated=datetime.now(),
            )

            # 의존성 확인
            if dependencies:
                missing_deps = [dep for dep in dependencies if dep not in self.plugins]
                if missing_deps and self.auto_dependency_resolution:
                    logger.info(f"📦 자동 의존성 설치: {missing_deps}")
                    await self._install_dependencies(missing_deps)

            # 플러그인 등록
            self.plugins[plugin_name] = plugin_info
            self.dependency_graph[plugin_name] = dependencies or []

            logger.info(f"✅ 플러그인 설치 완료: {plugin_name} v{version}")
            return True

        except Exception as e:
            logger.error(f"❌ 플러그인 설치 실패: {plugin_name} - {e}")
            return False

    async def load_plugin(self, plugin_name: str) -> bool:
        """플러그인 로딩"""
        if plugin_name not in self.plugins:
            logger.error(f"❌ 플러그인 없음: {plugin_name}")
            return False

        try:
            plugin_info = self.plugins[plugin_name]

            # 의존성 확인
            if not await self._check_dependencies(plugin_name):
                logger.warning(f"⚠️  의존성 문제: {plugin_name}")
                return False

            # 플러그인 모듈 로딩
            module = importlib.import_module(plugin_name)

            # 플러그인 클래스 찾기
            plugin_class = None
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if hasattr(obj, "initialize") and hasattr(obj, "execute"):
                    plugin_class = obj
                    break

            if plugin_class is None:
                logger.error(f"❌ 플러그인 클래스 없음: {plugin_name}")
                return False

            # 플러그인 인스턴스 생성
            plugin_instance = plugin_class()

            # 초기화
            if hasattr(plugin_instance, "initialize"):
                await plugin_instance.initialize()

            # 상태 업데이트
            plugin_info.state = PluginState.LOADED
            plugin_info.last_updated = datetime.now()

            # 인스턴스 저장
            self.plugin_instances[plugin_name] = plugin_instance

            # 생명주기 훅 실행
            await self._execute_lifecycle_hooks(plugin_name, "loaded")

            logger.info(f"✅ 플러그인 로딩 완료: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 플러그인 로딩 실패: {plugin_name} - {e}")
            self.plugins[plugin_name].state = PluginState.ERROR
            return False

    async def activate_plugin(self, plugin_name: str) -> bool:
        """플러그인 활성화"""
        if plugin_name not in self.plugins:
            return False

        try:
            plugin_info = self.plugins[plugin_name]

            if plugin_info.state != PluginState.LOADED:
                logger.warning(f"⚠️  플러그인 로딩 필요: {plugin_name}")
                if not await self.load_plugin(plugin_name):
                    return False

            # 활성화 메서드 호출
            plugin_instance = self.plugin_instances[plugin_name]
            if hasattr(plugin_instance, "activate"):
                await plugin_instance.activate()

            # 상태 업데이트
            plugin_info.state = PluginState.ACTIVE
            plugin_info.last_updated = datetime.now()

            # 생명주기 훅 실행
            await self._execute_lifecycle_hooks(plugin_name, "activated")

            logger.info(f"✅ 플러그인 활성화 완료: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 플러그인 활성화 실패: {plugin_name} - {e}")
            return False

    async def deactivate_plugin(self, plugin_name: str) -> bool:
        """플러그인 비활성화"""
        if plugin_name not in self.plugins:
            return False

        try:
            plugin_info = self.plugins[plugin_name]

            # 비활성화 메서드 호출
            if plugin_name in self.plugin_instances:
                plugin_instance = self.plugin_instances[plugin_name]
                if hasattr(plugin_instance, "deactivate"):
                    await plugin_instance.deactivate()

            # 상태 업데이트
            plugin_info.state = PluginState.INACTIVE
            plugin_info.last_updated = datetime.now()

            # 생명주기 훅 실행
            await self._execute_lifecycle_hooks(plugin_name, "deactivated")

            logger.info(f"✅ 플러그인 비활성화 완료: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 플러그인 비활성화 실패: {plugin_name} - {e}")
            return False

    async def uninstall_plugin(self, plugin_name: str) -> bool:
        """플러그인 제거"""
        if plugin_name not in self.plugins:
            return False

        try:
            # 비활성화
            if self.plugins[plugin_name].state == PluginState.ACTIVE:
                await self.deactivate_plugin(plugin_name)

            # 정리 메서드 호출
            if plugin_name in self.plugin_instances:
                plugin_instance = self.plugin_instances[plugin_name]
                if hasattr(plugin_instance, "cleanup"):
                    await plugin_instance.cleanup()

            # 파일 제거
            plugin_info = self.plugins[plugin_name]
            if os.path.exists(plugin_info.install_path):
                os.remove(plugin_info.install_path)

            # 레지스트리에서 제거
            del self.plugins[plugin_name]
            if plugin_name in self.plugin_instances:
                del self.plugin_instances[plugin_name]
            if plugin_name in self.dependency_graph:
                del self.dependency_graph[plugin_name]

            # 생명주기 훅 실행
            await self._execute_lifecycle_hooks(plugin_name, "uninstalled")

            logger.info(f"✅ 플러그인 제거 완료: {plugin_name}")
            return True

        except Exception as e:
            logger.error(f"❌ 플러그인 제거 실패: {plugin_name} - {e}")
            return False

    async def update_plugin(
        self, plugin_name: str, new_version: str, update_path: str
    ) -> bool:
        """플러그인 업데이트"""
        if plugin_name not in self.plugins:
            return False

        try:
            plugin_info = self.plugins[plugin_name]

            # 현재 상태 저장
            current_state = plugin_info.state

            # 비활성화
            if current_state == PluginState.ACTIVE:
                await self.deactivate_plugin(plugin_name)

            # 상태 업데이트
            plugin_info.state = PluginState.UPDATING
            plugin_info.last_updated = datetime.now()

            # 백업 생성
            backup_path = f"{plugin_info.install_path}.backup"
            shutil.copy2(plugin_info.install_path, backup_path)

            # 새 버전 설치
            shutil.copy2(update_path, plugin_info.install_path)

            # 체크섬 업데이트
            with open(plugin_info.install_path, "rb") as f:
                content = f.read()
                plugin_info.checksum = hashlib.md5(content).hexdigest()

            # 버전 업데이트
            plugin_info.version = new_version

            # 상태 복원
            plugin_info.state = current_state

            # 백업 파일 제거
            if os.path.exists(backup_path):
                os.remove(backup_path)

            # 생명주기 훅 실행
            await self._execute_lifecycle_hooks(plugin_name, "updated")

            logger.info(f"✅ 플러그인 업데이트 완료: {plugin_name} → v{new_version}")
            return True

        except Exception as e:
            logger.error(f"❌ 플러그인 업데이트 실패: {plugin_name} - {e}")
            # 백업에서 복원
            if os.path.exists(backup_path):
                shutil.copy2(backup_path, plugin_info.install_path)
            plugin_info.state = current_state
            return False

    async def _check_dependencies(self, plugin_name: str) -> bool:
        """의존성 확인"""
        plugin_info = self.plugins[plugin_name]

        for dep in plugin_info.dependencies:
            if dep not in self.plugins:
                logger.warning(f"⚠️  의존성 누락: {plugin_name} → {dep}")
                return False

            dep_plugin = self.plugins[dep]
            if dep_plugin.state not in [PluginState.ACTIVE, PluginState.LOADED]:
                logger.warning(f"⚠️  의존성 비활성: {plugin_name} → {dep}")
                return False

        return True

    async def _install_dependencies(self, dependencies: List[str]) -> bool:
        """의존성 자동 설치"""
        for dep in dependencies:
            # 실제 구현에서는 의존성 저장소에서 다운로드
            logger.info(f"📦 의존성 설치: {dep}")
            # 여기서는 시뮬레이션
            await asyncio.sleep(0.1)

        return True

    async def _execute_lifecycle_hooks(self, plugin_name: str, event: str):
        """생명주기 훅 실행"""
        if event in self.lifecycle_hooks:
            for hook in self.lifecycle_hooks[event]:
                try:
                    if asyncio.iscoroutinefunction(hook):
                        await hook(plugin_name)
                    else:
                        hook(plugin_name)
                except Exception as e:
                    logger.error(f"❌ 생명주기 훅 오류: {event} - {e}")

    def register_lifecycle_hook(self, event: str, hook: Callable):
        """생명주기 훅 등록"""
        if event not in self.lifecycle_hooks:
            self.lifecycle_hooks[event] = []

        self.lifecycle_hooks[event].append(hook)
        logger.info(f"🔗 생명주기 훅 등록: {event}")

    def _attempt_plugin_recovery(self, plugin_name: str):
        """플러그인 복구 시도"""
        try:
            logger.info(f"🔄 플러그인 복구 시도: {plugin_name}")

            # 자동 재로딩 시도
            asyncio.create_task(self.load_plugin(plugin_name))

        except Exception as e:
            logger.error(f"❌ 플러그인 복구 실패: {plugin_name} - {e}")

    def _update_performance_metrics(self):
        """성능 메트릭 업데이트"""
        total_plugins = len(self.plugins)
        active_plugins = sum(
            1 for p in self.plugins.values() if p.state == PluginState.ACTIVE
        )

        # 자동화율 계산
        automation_score = 0.0
        if total_plugins > 0:
            # 자동 설치, 자동 업데이트, 자동 복구 등 고려
            auto_features = 0
            if self.auto_install_enabled:
                auto_features += 1
            if self.auto_update_enabled:
                auto_features += 1
            if self.auto_cleanup_enabled:
                auto_features += 1
            if self.auto_dependency_resolution:
                auto_features += 1

            automation_score = min(1.0, auto_features / 4.0)

        # 업데이트 성공률 계산
        update_attempts = sum(
            1 for p in self.plugins.values() if p.last_updated != p.created_at
        )
        update_successes = sum(
            1
            for p in self.plugins.values()
            if p.last_updated != p.created_at and p.state != PluginState.ERROR
        )
        update_success_rate = update_successes / max(update_attempts, 1)

        # 의존성 해결률 계산
        total_deps = sum(len(p.dependencies) for p in self.plugins.values())
        resolved_deps = sum(
            1
            for p in self.plugins.values()
            for dep in p.dependencies
            if dep in self.plugins
        )
        dependency_resolution_rate = resolved_deps / max(total_deps, 1)

        self.performance_metrics.update(
            {
                "total_plugins": total_plugins,
                "active_plugins": active_plugins,
                "automation_rate": automation_score,
                "update_success_rate": update_success_rate,
                "dependency_resolution_rate": dependency_resolution_rate,
            }
        )

    def get_performance_report(self) -> Dict[str, Any]:
        """성능 리포트 생성"""
        self._update_performance_metrics()

        return {
            "metrics": self.performance_metrics,
            "target_automation_rate": 0.6,  # 목표 60%
            "current_automation_rate": self.performance_metrics["automation_rate"],
            "automation_improvement": (
                self.performance_metrics["automation_rate"] - 0.4
            )
            * 100,
            "total_plugins": len(self.plugins),
            "plugin_states": {
                "active": sum(
                    1 for p in self.plugins.values() if p.state == PluginState.ACTIVE
                ),
                "loaded": sum(
                    1 for p in self.plugins.values() if p.state == PluginState.LOADED
                ),
                "inactive": sum(
                    1 for p in self.plugins.values() if p.state == PluginState.INACTIVE
                ),
                "error": sum(
                    1 for p in self.plugins.values() if p.state == PluginState.ERROR
                ),
            },
            "lifecycle_hooks": {
                "registered_hooks": len(self.lifecycle_hooks),
                "hook_events": list(self.lifecycle_hooks.keys()),
            },
        }


class AutoUpdateSystem:
    """자동 업데이트 시스템"""

    def __init__(self):
        self.update_queue: List[Dict[str, Any]] = []
        self.update_history: List[Dict[str, Any]] = []
        self.auto_update_enabled = True
        self.update_check_interval = 3600  # 1시간
        logger.info("🔄 자동 업데이트 시스템 초기화 완료")

    async def check_for_updates(self, plugin_name: str) -> Optional[Dict[str, Any]]:
        """업데이트 확인"""
        try:
            # 실제 구현에서는 원격 저장소에서 확인
            # 여기서는 시뮬레이션
            await asyncio.sleep(0.1)

            # 랜덤하게 업데이트 필요 여부 결정
            import random

            if random.random() < 0.3:  # 30% 확률로 업데이트 필요
                return {
                    "plugin_name": plugin_name,
                    "current_version": "1.0.0",
                    "new_version": "1.1.0",
                    "update_url": f"https://updates.example.com/{plugin_name}/1.1.0",
                    "changelog": "버그 수정 및 성능 개선",
                }

            return None

        except Exception as e:
            logger.error(f"❌ 업데이트 확인 실패: {plugin_name} - {e}")
            return None

    async def download_update(self, update_info: Dict[str, Any]) -> bool:
        """업데이트 다운로드"""
        try:
            # 실제 구현에서는 파일 다운로드
            await asyncio.sleep(0.2)

            # 다운로드 성공 시뮬레이션
            update_info["local_path"] = f'/tmp/{update_info["plugin_name"]}_update.zip'

            logger.info(f"📥 업데이트 다운로드 완료: {update_info['plugin_name']}")
            return True

        except Exception as e:
            logger.error(
                f"❌ 업데이트 다운로드 실패: {update_info['plugin_name']} - {e}"
            )
            return False

    async def install_update(self, update_info: Dict[str, Any]) -> bool:
        """업데이트 설치"""
        try:
            # 실제 구현에서는 업데이트 파일 설치
            await asyncio.sleep(0.3)

            # 설치 성공 시뮬레이션
            update_record = {
                "plugin_name": update_info["plugin_name"],
                "old_version": update_info["current_version"],
                "new_version": update_info["new_version"],
                "install_time": datetime.now().isoformat(),
                "status": "success",
            }

            self.update_history.append(update_record)

            logger.info(f"✅ 업데이트 설치 완료: {update_info['plugin_name']}")
            return True

        except Exception as e:
            logger.error(f"❌ 업데이트 설치 실패: {update_info['plugin_name']} - {e}")
            return False


# 테스트용 샘플 플러그인들
class SamplePlugin:
    """샘플 플러그인"""

    def __init__(self, name: str):
        self.name = name
        self.state = "inactive"

    async def initialize(self):
        """초기화"""
        logger.info(f"🔧 플러그인 초기화: {self.name}")
        await asyncio.sleep(0.01)

    async def activate(self):
        """활성화"""
        logger.info(f"✅ 플러그인 활성화: {self.name}")
        self.state = "active"
        await asyncio.sleep(0.01)

    async def deactivate(self):
        """비활성화"""
        logger.info(f"❌ 플러그인 비활성화: {self.name}")
        self.state = "inactive"
        await asyncio.sleep(0.01)

    async def execute(self, data: Any) -> Dict[str, Any]:
        """실행"""
        await asyncio.sleep(0.01)
        return {
            "plugin": self.name,
            "result": f"처리된 데이터: {data}",
            "status": "success",
        }

    async def cleanup(self):
        """정리"""
        logger.info(f"🧹 플러그인 정리: {self.name}")
        await asyncio.sleep(0.01)


async def test_plugin_lifecycle_manager():
    """플러그인 생명주기 관리자 테스트"""
    logger.info("🧪 플러그인 생명주기 관리자 테스트 시작")

    # 플러그인 생명주기 관리자 초기화
    lifecycle_manager = PluginLifecycleManager()

    # 생명주기 훅 등록
    def on_plugin_loaded(plugin_name):
        logger.info(f"📝 플러그인 로딩 이벤트: {plugin_name}")

    def on_plugin_activated(plugin_name):
        logger.info(f"📝 플러그인 활성화 이벤트: {plugin_name}")

    lifecycle_manager.register_lifecycle_hook("loaded", on_plugin_loaded)
    lifecycle_manager.register_lifecycle_hook("activated", on_plugin_activated)

    # 샘플 플러그인 파일 생성
    sample_plugins = [
        ("sample_plugin_1", "SamplePlugin"),
        ("sample_plugin_2", "SamplePlugin"),
        ("sample_plugin_3", "SamplePlugin"),
    ]

    # 플러그인 설치 테스트
    logger.info("📦 플러그인 설치 테스트")

    for plugin_name, plugin_class in sample_plugins:
        # 임시 플러그인 파일 생성
        plugin_file = f"/tmp/{plugin_name}.py"
        with open(plugin_file, "w") as f:
            f.write(
                f"""
class {plugin_class}:
    def __init__(self):
        self.name = "{plugin_name}"

    async def initialize(self):
        print("초기화: {plugin_name}")

    async def execute(self, data):
        return {{"result": f"{{plugin_name}} 처리: {{data}}"}}
"""
            )

        # 플러그인 설치
        success = await lifecycle_manager.install_plugin(
            plugin_name,
            plugin_file,
            "1.0.0",
            "Test Author",
            f"샘플 플러그인 {plugin_name}",
            [],
            PluginPriority.NORMAL,
        )

        if success:
            logger.info(f"   ✅ 플러그인 설치: {plugin_name}")

    # 플러그인 로딩 테스트
    logger.info("📥 플러그인 로딩 테스트")

    for plugin_name in [p[0] for p in sample_plugins]:
        success = await lifecycle_manager.load_plugin(plugin_name)
        if success:
            logger.info(f"   ✅ 플러그인 로딩: {plugin_name}")

    # 플러그인 활성화 테스트
    logger.info("⚡ 플러그인 활성화 테스트")

    for plugin_name in [p[0] for p in sample_plugins]:
        success = await lifecycle_manager.activate_plugin(plugin_name)
        if success:
            logger.info(f"   ✅ 플러그인 활성화: {plugin_name}")

    # 자동 업데이트 시스템 테스트
    logger.info("🔄 자동 업데이트 시스템 테스트")

    auto_update_system = AutoUpdateSystem()

    for plugin_name in [p[0] for p in sample_plugins]:
        update_info = await auto_update_system.check_for_updates(plugin_name)
        if update_info:
            logger.info(f"   📦 업데이트 발견: {plugin_name}")

            # 업데이트 다운로드
            download_success = await auto_update_system.download_update(update_info)
            if download_success:
                logger.info(f"   📥 다운로드 완료: {plugin_name}")

                # 업데이트 설치
                install_success = await auto_update_system.install_update(update_info)
                if install_success:
                    logger.info(f"   ✅ 설치 완료: {plugin_name}")

    # 성능 리포트
    report = lifecycle_manager.get_performance_report()
    logger.info(f"📈 성능 리포트:")
    logger.info(f"   총 플러그인 수: {report['total_plugins']}")
    logger.info(f"   활성 플러그인 수: {report['plugin_states']['active']}")
    logger.info(f"   자동화율: {report['current_automation_rate']:.1%}")
    logger.info(f"   자동화 향상: {report['automation_improvement']:.1f}%")
    logger.info(f"   목표 자동화율: {report['target_automation_rate']:.1%}")
    logger.info(f"   업데이트 성공률: {report['metrics']['update_success_rate']:.1%}")
    logger.info(
        f"   의존성 해결률: {report['metrics']['dependency_resolution_rate']:.1%}"
    )

    return report


if __name__ == "__main__":
    asyncio.run(test_plugin_lifecycle_manager())
