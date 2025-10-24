#!/usr/bin/env python3
"""
Emotion Alias Pipeline Tests for DuRi Core

These tests verify that emotion aliases work correctly in the API pipeline.
"""

import os
import sys

import pytest

# Add the app directory to Python path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "duri_core"))


def test_emotion_alias_pipeline():
    """Test that emotion aliases work correctly in the API pipeline"""
    try:
        from duri_common.config.emotion_labels import is_valid_emotion, normalize_emotion

        # Test data
        test_data = {  # noqa: F841
            "emotion": "joy",
            "timestamp": "2025-10-22T00:00:00",
            "data": {"text": "test", "source": "test"},
            "intensity": 0.5,
        }

        # Test normalization
        normalized = normalize_emotion("joy")
        assert normalized == "happy"

        # Test validation
        assert is_valid_emotion(normalized) == True  # noqa: E712

        print("✅ Emotion alias pipeline works correctly")
    except Exception as e:
        pytest.fail(f"Emotion alias pipeline failed: {e}")


def test_emotion_alias_mapping():
    """Test comprehensive emotion alias mapping"""
    try:
        from duri_common.config.emotion_labels import EMOTION_ALIASES, normalize_emotion

        # Test all defined aliases
        for alias, expected in EMOTION_ALIASES.items():
            result = normalize_emotion(alias)
            assert result == expected, f"Alias '{alias}' should map to '{expected}', got '{result}'"

        print("✅ All emotion aliases map correctly")
    except Exception as e:
        pytest.fail(f"Emotion alias mapping failed: {e}")


def test_invalid_emotion_handling():
    """Test that invalid emotions are handled correctly"""
    try:
        from duri_common.config.emotion_labels import is_valid_emotion, normalize_emotion

        # Test invalid emotions
        invalid_emotions = ["ecstasy", "bliss", "euphoria", "invalid_emotion"]

        for emotion in invalid_emotions:
            normalized = normalize_emotion(emotion)
            is_valid = is_valid_emotion(normalized)
            assert is_valid == False, f"Invalid emotion '{emotion}' should not be valid"  # noqa: E712

        print("✅ Invalid emotions handled correctly")
    except Exception as e:
        pytest.fail(f"Invalid emotion handling failed: {e}")


def test_case_insensitive_emotions():
    """Test that emotion handling is case insensitive"""
    try:
        from duri_common.config.emotion_labels import normalize_emotion

        # Test case variations
        test_cases = [
            ("JOY", "happy"),
            ("Joy", "happy"),
            ("joy", "happy"),
            ("HAPPY", "happy"),
            ("Happy", "happy"),
            ("happy", "happy"),
        ]

        for input_emotion, expected in test_cases:
            result = normalize_emotion(input_emotion)
            assert result == expected, f"Case insensitive '{input_emotion}' should map to '{expected}', got '{result}'"

        print("✅ Case insensitive emotion handling works")
    except Exception as e:
        pytest.fail(f"Case insensitive emotion handling failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
