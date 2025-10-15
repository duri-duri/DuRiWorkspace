#!/usr/bin/env python3
"""
DuRi 로그 관리 시스템
"""

import logging
import os
from typing import Dict, Any

class LoggingManager:
    def __init__(self):
        """로그 관리자 초기화"""
        self.log_levels = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL
        }
        
    def set_log_level(self, level: str = "DEBUG"):
        """로그 레벨 설정"""
        if level in self.log_levels:
            logging.basicConfig(
                level=self.log_levels[level],
                format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            print(f"✅ 로그 레벨 설정 완료: {level}")
            return True
        else:
            print(f"❌ 잘못된 로그 레벨: {level}")
            return False
            
    def get_log_level(self):
        """현재 로그 레벨 반환"""
        return logging.getLogger().level
        
    def enable_debug_mode(self):
        """디버그 모드 활성화"""
        return self.set_log_level("DEBUG")
        
    def enable_production_mode(self):
        """프로덕션 모드 활성화"""
        return self.set_log_level("INFO")

# 전역 로그 관리자
logging_manager = LoggingManager()
logging_manager.enable_debug_mode()
