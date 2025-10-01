#!/usr/bin/env python3
"""
DuRi Core Module
통합 관리자 및 설정
"""

from .config import Config
from .unified_manager import UnifiedManager

__all__ = ["UnifiedManager", "Config"]
