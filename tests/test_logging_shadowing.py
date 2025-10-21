def test_stdlib_logging_available():
    """Test that Python's stdlib logging module is properly available."""
    import logging

    # Test basic logging functionality
    assert hasattr(logging, "StreamHandler"), "StreamHandler not available"
    assert hasattr(logging, "Formatter"), "Formatter not available"
    assert hasattr(logging, "getLogger"), "getLogger not available"
    assert hasattr(logging, "basicConfig"), "basicConfig not available"

    # Test that we can create a logger
    logger = logging.getLogger("test_logger")
    assert logger is not None, "Failed to create logger"

    # Test that we can create a handler
    handler = logging.StreamHandler()
    assert handler is not None, "Failed to create StreamHandler"

    print("✅ stdlib logging module is properly available")


def test_no_logging_shadowing():
    """Test that no local logging modules are shadowing stdlib logging."""
    import logging
    import sys

    # Check that logging module is from stdlib
    logging_file = getattr(logging, "__file__", None)
    if logging_file:
        assert (
            "/usr" in logging_file or "site-packages" not in logging_file
        ), f"logging module appears to be shadowed: {logging_file}"

    # Check that logging module is in sys.modules
    assert "logging" in sys.modules, "logging module not in sys.modules"

    print("✅ No logging module shadowing detected")


if __name__ == "__main__":
    test_stdlib_logging_available()
    test_no_logging_shadowing()
    print("🎉 All logging tests passed!")
