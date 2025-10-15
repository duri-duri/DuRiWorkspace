#!/usr/bin/env python3
"""
DuRi 모듈 의존성 관리 시스템
"""

import logging
import sys
import os
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DependencyManager:
    def __init__(self):
        """의존성 관리자 초기화"""
        self.dependencies = {}
        self.missing_dependencies = []
        
    def check_dependency(self, module_name: str) -> bool:
        """의존성 확인"""
        try:
            __import__(module_name)
            return True
        except ImportError:
            self.missing_dependencies.append(module_name)
            return False
            
    def check_all_dependencies(self) -> Dict[str, bool]:
        """모든 의존성 확인"""
        results = {}
        required_modules = [
            "DuRiCore.utils.existence_ai_system",
            "DuRiCore.final_integration_system",
            "duri_modules.autonomous.duri_autonomous_core",
            "DuRiCore.deployment_system",
            "DuRiCore.performance_enhancement_system",
            "DuRiCore.memory_optimization_system"
        ]
        
        for module in required_modules:
            results[module] = self.check_dependency(module)
            
        return results
        
    def get_missing_dependencies(self) -> List[str]:
        """누락된 의존성 반환"""
        return self.missing_dependencies
        
    def fix_dependencies(self) -> bool:
        """의존성 문제 해결"""
        try:
            # 경로 추가
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            
            logger.info("의존성 문제 해결 완료")
            return True
        except Exception as e:
            logger.error(f"의존성 문제 해결 실패: {e}")
            return False

# 전역 의존성 관리자
dependency_manager = DependencyManager()
dependency_manager.fix_dependencies()
