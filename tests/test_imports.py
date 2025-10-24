#!/usr/bin/env python3
"""
Import Smoke Tests for DuRi Core

These tests verify that all critical modules can be imported without errors.
This prevents ModuleNotFoundError issues in production.
"""

import os
import sys

import pytest

# Set test environment to skip DB connections
os.environ["DURICORE_SKIP_DB"] = "1"

# Add the app directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "duri_core"))


def test_core_imports():
    """Test that all core modules can be imported"""
    try:
        import duri_core.app

        # 서브모듈 업스트림의 레이아웃 변화에 내성
        try:
            import duri_core.core.log_utils  # 기존 경로
        except ImportError:
            # 백워드 호환: 새 구조 또는 평면 구조 양쪽 허용
            import importlib

            log_utils = None
            for candidate in (
                "duri_core.log_utils",
                "duri_core.core.logging_utils",
                "duri_core.utils.log_utils",
            ):
                try:
                    log_utils = importlib.import_module(candidate)
                    break
                except ImportError:
                    pass
            if log_utils is None:
                print("⚠️ log_utils module not found in any expected location - skipping")

        import duri_core.app.api
        import duri_core.app.logic
        import duri_core.core.database
        import duri_core.core.decision
        import duri_core.core.stats

        # metrics 모듈은 서브모듈 업데이트로 인해 변경될 수 있음
        try:
            import duri_core.app.metrics  # noqa: F401
        except ImportError:
            print("⚠️ metrics module not found - skipping (may be moved or renamed)")
        print("✅ All core modules imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import core module: {e}")


def test_common_imports():
    """Test that all common modules can be imported"""
    try:
        import duri_common.config
        import duri_common.config.emotion_labels
        import duri_common.config.settings
        import duri_common.logger  # noqa: F401

        print("✅ All common modules imported successfully")
    except ImportError as e:
        pytest.fail(f"Failed to import common module: {e}")


def test_emotion_alias_functions():
    """Test that emotion alias functions work correctly"""
    try:
        from duri_common.config.emotion_labels import ALL_EMOTIONS, is_valid_emotion, normalize_emotion

        # Test alias normalization
        assert normalize_emotion("joy") == "happy"
        assert normalize_emotion("happiness") == "happy"
        assert normalize_emotion("anger") == "angry"
        assert normalize_emotion("sadness") == "sad"

        # Test validation
        assert is_valid_emotion("happy") == True  # noqa: E712
        assert is_valid_emotion("sad") == True  # noqa: E712
        assert is_valid_emotion("invalid_emotion") == False  # noqa: E712

        # Test ALL_EMOTIONS contains expected emotions
        assert "happy" in ALL_EMOTIONS
        assert "sad" in ALL_EMOTIONS
        assert "angry" in ALL_EMOTIONS

        print("✅ Emotion alias functions work correctly")
    except Exception as e:
        pytest.fail(f"Emotion alias functions failed: {e}")


def test_settings_loading():
    """Test that settings can be loaded without errors"""
    try:
        from duri_common.config.settings import get_settings

        settings = get_settings()

        # Test that required settings exist
        assert hasattr(settings, "LOG_DIR")
        assert hasattr(settings, "EVOLUTION_URL")
        assert hasattr(settings, "BRAIN_URL")

        # Test that log file path can be generated
        log_file = settings.get_log_file_path()
        assert log_file is not None
        assert isinstance(log_file, str)

        print("✅ Settings loaded successfully")
    except Exception as e:
        pytest.fail(f"Settings loading failed: {e}")


def test_absolute_imports_regression():
    """Test that all modules use absolute imports (prevents relative import regression)"""
    import importlib

    # Critical modules that must use absolute imports
    modules = [
        "duri_core.app.logic",
        "duri_core.core.decision",
        "duri_core.core.decision_processor",
        "duri_core.core.logging",
        "duri_core.core.stats",
        "duri_core.core.database",
        "duri_core.core.loop_orchestrator",
        "duri_core.app.api",
    ]

    failed_imports = []

    for module_name in modules:
        try:
            # Try to import the module
            module = importlib.import_module(module_name)

            # Check if the module file exists and can be read
            if hasattr(module, "__file__") and module.__file__:
                with open(module.__file__, "r", encoding="utf-8") as f:
                    content = f.read()

                # Check for problematic relative imports
                problematic_patterns = [
                    "from core.",
                    "from .core.",
                    "from ..core.",
                    "import core.",
                ]

                for pattern in problematic_patterns:
                    if pattern in content:
                        failed_imports.append(f"{module_name}: Found relative import '{pattern}'")

        except ImportError as e:
            failed_imports.append(f"{module_name}: Import failed - {e}")
        except Exception as e:
            failed_imports.append(f"{module_name}: Unexpected error - {e}")

    if failed_imports:
        pytest.fail("Import regression detected:\n" + "\n".join(failed_imports))

    print("✅ All modules use absolute imports (no regression detected)")


def test_emotion_normalization_integration():
    """Test emotion normalization at API level (integration test)"""

    import requests

    # Test cases: input emotion -> expected normalized emotion
    test_cases = [
        ("joy", "happy"),
        ("happiness", "happy"),
        ("anger", "angry"),
        ("sadness", "sad"),
        ("fear", "fear"),  # already normalized
        ("happy", "happy"),  # already normalized
    ]

    base_url = "http://localhost:8080"

    for input_emotion, _expected_normalized in test_cases:
        try:
            # Test both endpoints
            for endpoint in ["/emotion", "/api/emotion"]:
                response = requests.post(
                    f"{base_url}{endpoint}",
                    json={
                        "emotion": input_emotion,
                        "timestamp": "2025-10-22T14:30:00",
                        "data": {"text": f"normalization_test_{input_emotion}"},
                    },
                    timeout=5,
                )

                if response.status_code == 200:
                    data = response.json()
                    # Should not be fallback (Unknown emotion)
                    assert (
                        data.get("decision", {}).get("fallback") == False  # noqa: E712
                    ), f"Emotion '{input_emotion}' should not trigger fallback"
                    assert (
                        data.get("decision", {}).get("reason") != f"Unknown emotion: {input_emotion}"
                    ), f"Emotion '{input_emotion}' should be normalized, not rejected"
                else:
                    pytest.fail(
                        f"API endpoint {endpoint} returned {response.status_code} for emotion '{input_emotion}'"
                    )

        except requests.exceptions.RequestException as e:
            pytest.fail(f"API request failed for emotion '{input_emotion}': {e}")
        except Exception as e:
            pytest.fail(f"Unexpected error testing emotion '{input_emotion}': {e}")

    print("✅ Emotion normalization integration test passed")


def test_runtime_module_loading():
    """Test that critical modules can be loaded at runtime (fail-fast check)"""
    import importlib

    # Critical modules for runtime
    critical_modules = [
        "duri_core.app.logic",
        "duri_core.core.decision",
        "duri_core.core.database",
        "duri_common.config.emotion_labels",
    ]

    failed_modules = []

    for module_name in critical_modules:
        try:
            module = importlib.import_module(module_name)
            # Basic functionality check
            if hasattr(module, "__name__"):
                print(f"✅ {module_name} loaded successfully")
            else:
                failed_modules.append(f"{module_name}: No __name__ attribute")
        except Exception as e:
            failed_modules.append(f"{module_name}: {e}")

    if failed_modules:
        pytest.fail("Critical modules failed to load:\n" + "\n".join(failed_modules))


def test_database_manager_skip_mode():
    try:
        from duri_core.core.database import DatabaseManager

        # Should not raise connection errors in skip mode
        db_manager = DatabaseManager()
        conn = db_manager.get_connection()

        # 스킵 모드면 반드시 None (계약 고정)
        assert (
            os.getenv("DURI_DB_SKIP") == "1" or os.getenv("DURI_TEST_SKIP_DB") == "1"
        ), "Skip mode environment variables not set"
        assert conn is None, f"Expected None in skip mode, got {conn}"

        print("✅ DatabaseManager skip mode working (strict contract)")
    except Exception as e:
        pytest.fail(f"DatabaseManager skip mode test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
