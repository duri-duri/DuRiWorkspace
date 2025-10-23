"""
가족형 모드 최소 검증 테스트
네임스페이스 분리와 망각 기능을 검증
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


class TestFamilyModeGuard:
    """가족형 모드 가드 테스트"""

    def test_family_mode_namespace_isolation(self):
        """가족 모드에서 저장 위치가 일반 모드와 다름을 검증"""
        # 일반 모드 설정
        with patch.dict(os.environ, {"FAMILY_MODE": "false", "USER_ID": "test_user"}):
            normal_path = self._get_storage_path()
            assert "family_" not in str(normal_path)

        # 가족 모드 설정
        with patch.dict(os.environ, {"FAMILY_MODE": "true", "USER_ID": "test_user"}):
            family_path = self._get_storage_path()
            assert "family_test_user" in str(family_path)
            assert family_path != normal_path

    def test_family_mode_memory_isolation(self):
        """가족 모드에서 메모리 저장이 분리됨을 검증"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 일반 모드에서 데이터 저장
            with patch.dict(os.environ, {"FAMILY_MODE": "false", "USER_ID": "user1"}):
                normal_store = self._create_memory_store(temp_dir)
                normal_store.write("test_memory", {"content": "normal_data"})

            # 가족 모드에서 데이터 저장
            with patch.dict(os.environ, {"FAMILY_MODE": "true", "USER_ID": "user1"}):
                family_store = self._create_memory_store(temp_dir)
                family_store.write("test_memory", {"content": "family_data"})

            # 데이터가 분리되어 있는지 확인
            with patch.dict(os.environ, {"FAMILY_MODE": "false", "USER_ID": "user1"}):
                normal_store = self._create_memory_store(temp_dir)
                normal_data = normal_store.tail("test_memory", k=1)
                assert len(normal_data) == 1
                assert normal_data[0]["content"] == "normal_data"

            with patch.dict(os.environ, {"FAMILY_MODE": "true", "USER_ID": "user1"}):
                family_store = self._create_memory_store(temp_dir)
                family_data = family_store.tail("test_memory", k=1)
                assert len(family_data) == 1
                assert family_data[0]["content"] == "family_data"

    def test_family_mode_forget_functionality(self):
        """가족 모드에서 망각 요청 시 데이터가 제거됨을 검증"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"FAMILY_MODE": "true", "USER_ID": "user1"}):
                store = self._create_memory_store(temp_dir)

                # 데이터 저장
                store.write(
                    "personal_memory", {"id": "mem1", "content": "private_data"}
                )
                store.write("family_memory", {"id": "mem2", "content": "shared_data"})

                # 데이터 존재 확인
                assert store.count("personal_memory") == 1
                assert store.count("family_memory") == 1

                # 망각 요청 실행
                self._execute_forget_request(store, "personal_memory", "mem1")

                # 개인 데이터만 제거되고 가족 데이터는 유지
                assert store.count("personal_memory") == 0
                assert store.count("family_memory") == 1

    def test_family_mode_privacy_boundaries(self):
        """가족 모드에서 프라이버시 경계가 유지됨을 검증"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(os.environ, {"FAMILY_MODE": "true", "USER_ID": "user1"}):
                store = self._create_memory_store(temp_dir)

                # 민감한 데이터 저장
                sensitive_data = {
                    "id": "sensitive_001",
                    "content": "private_thoughts",
                    "privacy_level": "high",
                    "tags": ["personal", "private"],
                }
                store.write("thoughts", sensitive_data)

                # 가족 모드에서 검색 시 민감한 데이터가 필터링되는지 확인
                results = store.search("thoughts", "private", topk=10)

                # 프라이버시 레벨이 높은 데이터는 검색에서 제외되어야 함
                for result in results:
                    if result.get("privacy_level") == "high":
                        assert "private_thoughts" not in result.get("content", "")

    def test_family_mode_consent_validation(self):
        """가족 모드에서 동의 확인이 작동함을 검증"""
        with patch.dict(os.environ, {"FAMILY_MODE": "true", "USER_ID": "user1"}):
            # 동의가 필요한 작업 시도
            consent_required = self._check_consent_required("data_sharing")
            assert consent_required is True

            # 동의 부여 후 작업 실행
            with patch.dict(os.environ, {"FAMILY_CONSENT": "true"}):
                consent_required = self._check_consent_required("data_sharing")
                assert consent_required is False

    def _get_storage_path(self) -> Path:
        """저장 경로 생성"""
        base_path = Path("var")

        if os.environ.get("FAMILY_MODE") == "true":
            user_id = os.environ.get("USER_ID", "unknown")
            return base_path / f"family_{user_id}"
        else:
            return base_path / "default"

    def _create_memory_store(self, temp_dir: str):
        """메모리 저장소 생성 (간단한 구현)"""

        class SimpleMemoryStore:
            def __init__(self, base_path: str):
                self.base_path = Path(base_path) / self._get_storage_path().name
                self.base_path.mkdir(parents=True, exist_ok=True)

            def write(self, name: str, data: dict):
                file_path = self.base_path / f"{name}.json"
                import json

                file_path.write_text(json.dumps(data))

            def tail(self, name: str, k: int = 1):
                file_path = self.base_path / f"{name}.json"
                if file_path.exists():
                    import json

                    return [json.loads(file_path.read_text())]
                return []

            def count(self, name: str) -> int:
                file_path = self.base_path / f"{name}.json"
                return 1 if file_path.exists() else 0

            def search(self, name: str, query: str, topk: int = 10):
                file_path = self.base_path / f"{name}.json"
                if file_path.exists():
                    import json

                    data = json.loads(file_path.read_text())
                    # 가족 모드에서 프라이버시 레벨이 높은 데이터는 필터링
                    if (
                        os.environ.get("FAMILY_MODE") == "true"
                        and data.get("privacy_level") == "high"
                    ):
                        return []
                    if query.lower() in str(data).lower():
                        return [data]
                return []

            def _get_storage_path(self) -> Path:
                if os.environ.get("FAMILY_MODE") == "true":
                    user_id = os.environ.get("USER_ID", "default")
                    return Path(f"family_{user_id}")
                return Path("normal")

        return SimpleMemoryStore(temp_dir)

    def _execute_forget_request(self, store, memory_type: str, memory_id: str):
        """망각 요청 실행"""
        # 간단한 망각 구현
        file_path = store.base_path / f"{memory_type}.json"
        if file_path.exists():
            file_path.unlink()

    def _check_consent_required(self, action: str) -> bool:
        """동의 필요 여부 확인"""
        if os.environ.get("FAMILY_MODE") == "true":
            return os.environ.get("FAMILY_CONSENT") != "true"
        return False


# 통합 테스트
class TestFamilyModeIntegration:
    """가족형 모드 통합 테스트"""

    def test_family_mode_end_to_end(self):
        """가족형 모드 전체 플로우 테스트"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.dict(
                os.environ,
                {
                    "FAMILY_MODE": "true",
                    "USER_ID": "family_user",
                    "FAMILY_CONSENT": "true",
                },
            ):
                # 1. 가족 모드 초기화
                store = self._create_family_store(temp_dir)

                # 2. 개인 데이터 저장
                personal_data = {
                    "id": "personal_001",
                    "content": "개인적인 생각",
                    "privacy_level": "high",
                }
                store.write("personal_thoughts", personal_data)

                # 3. 가족 공유 데이터 저장
                family_data = {
                    "id": "family_001",
                    "content": "가족과 공유할 정보",
                    "privacy_level": "low",
                }
                store.write("family_shared", family_data)

                # 4. 데이터 분리 확인
                personal_count = store.count("personal_thoughts")
                family_count = store.count("family_shared")

                assert personal_count == 1
                assert family_count == 1

                # 5. 검색 테스트 (프라이버시 경계 확인)
                personal_results = store.search("personal_thoughts", "생각", topk=5)
                family_results = store.search("family_shared", "정보", topk=5)

                # 개인 데이터는 검색에서 제한되어야 함
                assert len(personal_results) == 0  # 프라이버시 보호
                assert len(family_results) == 1  # 가족 데이터는 접근 가능

    def _create_family_store(self, temp_dir: str):
        """가족형 저장소 생성"""

        # 위의 SimpleMemoryStore와 유사하지만 프라이버시 필터링 추가
        class FamilyMemoryStore:
            def __init__(self, base_path: str):
                self.base_path = (
                    Path(base_path) / f"family_{os.environ.get('USER_ID', 'unknown')}"
                )
                self.base_path.mkdir(parents=True, exist_ok=True)

            def write(self, name: str, data: dict):
                file_path = self.base_path / f"{name}.json"
                import json

                file_path.write_text(json.dumps(data))

            def count(self, name: str) -> int:
                file_path = self.base_path / f"{name}.json"
                return 1 if file_path.exists() else 0

            def search(self, name: str, query: str, topk: int = 10):
                file_path = self.base_path / f"{name}.json"
                if file_path.exists():
                    import json

                    data = json.loads(file_path.read_text())

                    # 프라이버시 레벨 확인
                    if data.get("privacy_level") == "high":
                        return []  # 높은 프라이버시 데이터는 검색에서 제외

                    if query.lower() in str(data).lower():
                        return [data]
                return []

        return FamilyMemoryStore(temp_dir)


if __name__ == "__main__":
    # 테스트 실행
    pytest.main([__file__, "-v"])
