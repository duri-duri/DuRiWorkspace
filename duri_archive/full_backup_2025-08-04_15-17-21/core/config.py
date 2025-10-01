#!/usr/bin/env python3
"""
DuRi 설정 파일
"""

import logging
from typing import Any, Dict

# 로깅 설정
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Config:
    """DuRi 설정 클래스"""

    # 시스템 설정
    SYSTEM_NAME = "DuRi"
    VERSION = "1.0.0"

    # 모듈 설정
    EMOTION_MODULE_ENABLED = True
    GROWTH_MODULE_ENABLED = True
    JUDGMENT_MODULE_ENABLED = True

    # 성장 설정
    MAX_GROWTH_LEVEL = 8
    GROWTH_THRESHOLD = 0.7

    # 편향 설정
    BIAS_THRESHOLD = 0.5
    RELIABILITY_THRESHOLD = 0.6

    # 퀘스트 설정
    QUEST_TIMEOUT = 3600  # 1시간
    MAX_QUEST_ATTEMPTS = 3

    # 대역폭 설정
    DEFAULT_BANDWIDTH_LEVEL = 1
    OVERLOAD_RECOVERY_TIME = 30  # 30초

    @classmethod
    def get_emotion_config(cls) -> Dict[str, Any]:
        """감정 모듈 설정"""
        return {
            "enabled": cls.EMOTION_MODULE_ENABLED,
            "bias_detection_enabled": True,
            "meta_cognition_enabled": True,
            "regulation_enabled": True,
        }

    @classmethod
    def get_growth_config(cls) -> Dict[str, Any]:
        """성장 모듈 설정"""
        return {
            "enabled": cls.GROWTH_MODULE_ENABLED,
            "max_level": cls.MAX_GROWTH_LEVEL,
            "growth_threshold": cls.GROWTH_THRESHOLD,
            "quest_timeout": cls.QUEST_TIMEOUT,
            "max_quest_attempts": cls.MAX_QUEST_ATTEMPTS,
        }

    @classmethod
    def get_judgment_config(cls) -> Dict[str, Any]:
        """판단 모듈 설정"""
        return {
            "enabled": cls.JUDGMENT_MODULE_ENABLED,
            "bias_threshold": cls.BIAS_THRESHOLD,
            "reliability_threshold": cls.RELIABILITY_THRESHOLD,
        }

    @classmethod
    def get_bandwidth_config(cls) -> Dict[str, Any]:
        """대역폭 설정"""
        return {
            "default_level": cls.DEFAULT_BANDWIDTH_LEVEL,
            "overload_recovery_time": cls.OVERLOAD_RECOVERY_TIME,
        }

    @classmethod
    def get_system_config(cls) -> Dict[str, Any]:
        """시스템 전체 설정"""
        return {
            "name": cls.SYSTEM_NAME,
            "version": cls.VERSION,
            "emotion": cls.get_emotion_config(),
            "growth": cls.get_growth_config(),
            "judgment": cls.get_judgment_config(),
            "bandwidth": cls.get_bandwidth_config(),
        }
