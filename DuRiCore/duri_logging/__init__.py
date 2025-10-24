#!/usr/bin/env python3
"""
DuRi 로깅 자동 주입 시스템

전역 안전 로깅과 컨텍스트 전파를 제공합니다.
"""

from .adapter import ContextAdapter, get_logger
from .autodetect import infer_component
from .context import get_context, set_learning_session_id, set_phase, set_request_id, set_session_id
from .decorators import log_calls, log_exceptions, timed
from .setup import DefaultFieldsFilter, SafeLogger, setup_logging

__all__ = [
    # Setup
    "setup_logging",
    "SafeLogger",
    "DefaultFieldsFilter",
    # Context
    "set_request_id",
    "set_session_id",
    "set_learning_session_id",
    "set_phase",
    "get_context",
    # Adapter
    "get_logger",
    "ContextAdapter",
    # Decorators
    "log_calls",
    "log_exceptions",
    "timed",
    # Auto-detect
    "infer_component",
]
