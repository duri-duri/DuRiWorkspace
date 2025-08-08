#!/usr/bin/env python3
"""
DuRi 로깅 자동 주입 시스템

전역 안전 로깅과 컨텍스트 전파를 제공합니다.
"""

from .setup import setup_logging, SafeLogger, DefaultFieldsFilter
from .context import set_request_id, set_session_id, set_learning_session_id, set_phase, get_context
from .adapter import get_logger, ContextAdapter
from .decorators import log_calls, log_exceptions, timed
from .autodetect import infer_component

__all__ = [
    # Setup
    'setup_logging',
    'SafeLogger', 
    'DefaultFieldsFilter',
    
    # Context
    'set_request_id',
    'set_session_id', 
    'set_learning_session_id',
    'set_phase',
    'get_context',
    
    # Adapter
    'get_logger',
    'ContextAdapter',
    
    # Decorators
    'log_calls',
    'log_exceptions', 
    'timed',
    
    # Auto-detect
    'infer_component'
]
