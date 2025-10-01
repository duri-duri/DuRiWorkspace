#!/usr/bin/env python3
"""
DuRiCore Interface Module
FastAPI 기반 인터페이스 - 새로운 엔진들과의 연동
"""

from .api import router as api_router
from .services import *

__all__ = [
    "api_router",
]
