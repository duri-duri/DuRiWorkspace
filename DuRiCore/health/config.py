#!/usr/bin/env python3
"""
DuRi Health Config - SLO 임계치 런타임 구성화
"""

import os
import time
from typing import Dict, Any, Optional
from DuRiCore.global_logging_manager import get_duri_logger

logger = get_duri_logger("health_config")

class HealthConfig:
    """SLO 임계치 및 헬스체크 설정 관리"""
    
    def __init__(self):
        self._cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 60  # 60초 캐시
        self._lock = False
        
        # 기본값 정의
        self._defaults = {
            "latency_p95_ms_threshold": 500,
            "error_rate_threshold": 0.05,
            "readiness_fail_threshold": 0.05,
            "canary_token": "duri-canary-readonly-token",
            "cache_ttl": 60,
            "readiness_window_sec": 900,
            "rate_limit_rps": 1,
            "rate_limit_burst": 3
        }
        
        logger.info("HealthConfig 초기화 완료")
    
    def _is_cache_valid(self) -> bool:
        """캐시 유효성 확인"""
        return time.time() - self._cache_timestamp < self._cache_ttl
    
    def _load_from_env(self) -> Dict[str, Any]:
        """환경변수에서 설정 로드"""
        config = {}
        
        # SLO 임계치
        config["latency_p95_ms_threshold"] = int(
            os.getenv("DURI_LATENCY_P95_MS_THRESHOLD", 
                     str(self._defaults["latency_p95_ms_threshold"]))
        )
        
        config["error_rate_threshold"] = float(
            os.getenv("DURI_ERROR_RATE_THRESHOLD", 
                     str(self._defaults["error_rate_threshold"]))
        )
        
        config["readiness_fail_threshold"] = float(
            os.getenv("DURI_READINESS_FAIL_THRESHOLD", 
                     str(self._defaults["readiness_fail_threshold"]))
        )
        
        # 토큰 설정
        config["canary_token"] = os.getenv(
            "CANARY_TOKEN", 
            self._defaults["canary_token"]
        )
        
        # 캐시 설정
        config["cache_ttl"] = int(
            os.getenv("DURI_CONFIG_CACHE_TTL", 
                     str(self._defaults["cache_ttl"]))
        )
        
        # Readiness 설정
        config["readiness_window_sec"] = int(
            os.getenv("DURI_READINESS_WINDOW_SEC", 
                     str(self._defaults["readiness_window_sec"]))
        )
        
        # Rate limit 설정
        config["rate_limit_rps"] = int(
            os.getenv("DURI_RATE_LIMIT_RPS", 
                     str(self._defaults["rate_limit_rps"]))
        )
        
        config["rate_limit_burst"] = int(
            os.getenv("DURI_RATE_LIMIT_BURST", 
                     str(self._defaults["rate_limit_burst"]))
        )
        
        return config
    
    def get_config(self, force_reload: bool = False) -> Dict[str, Any]:
        """
        설정 가져오기 (캐시 사용)
        
        Args:
            force_reload: 강제 리로드 여부
            
        Returns:
            설정 딕셔너리
        """
        if force_reload or not self._is_cache_valid():
            self._cache = self._load_from_env()
            self._cache_timestamp = time.time()
            self._cache_ttl = self._cache.get("cache_ttl", 60)
            
            logger.info(f"HealthConfig 리로드: {self._cache}")
        
        return self._cache.copy()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        특정 설정값 가져오기
        
        Args:
            key: 설정 키
            default: 기본값
            
        Returns:
            설정값
        """
        config = self.get_config()
        return config.get(key, default or self._defaults.get(key))
    
    def get_slo_thresholds(self) -> Dict[str, Any]:
        """SLO 임계치만 가져오기"""
        config = self.get_config()
        return {
            "latency_p95_ms_threshold": config["latency_p95_ms_threshold"],
            "error_rate_threshold": config["error_rate_threshold"],
            "readiness_fail_threshold": config["readiness_fail_threshold"]
        }
    
    def get_rate_limit_config(self) -> Dict[str, Any]:
        """Rate limit 설정만 가져오기"""
        config = self.get_config()
        return {
            "rps": config["rate_limit_rps"],
            "burst": config["rate_limit_burst"]
        }
    
    def reload(self) -> Dict[str, Any]:
        """설정 강제 리로드"""
        logger.info("HealthConfig 강제 리로드 요청")
        return self.get_config(force_reload=True)
    
    def validate_config(self) -> Dict[str, Any]:
        """설정 유효성 검증"""
        config = self.get_config()
        issues = []
        
        # 임계치 유효성 검증
        if config["latency_p95_ms_threshold"] <= 0:
            issues.append("latency_p95_ms_threshold must be positive")
        
        if not 0 <= config["error_rate_threshold"] <= 1:
            issues.append("error_rate_threshold must be between 0 and 1")
        
        if not 0 <= config["readiness_fail_threshold"] <= 1:
            issues.append("readiness_fail_threshold must be between 0 and 1")
        
        if config["readiness_window_sec"] <= 0:
            issues.append("readiness_window_sec must be positive")
        
        if config["rate_limit_rps"] <= 0:
            issues.append("rate_limit_rps must be positive")
        
        if config["rate_limit_burst"] <= 0:
            issues.append("rate_limit_burst must be positive")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": config
        }

# 전역 인스턴스
health_config = HealthConfig()

def get_health_config() -> HealthConfig:
    """전역 HealthConfig 인스턴스 반환"""
    return health_config

def get_slo_thresholds() -> Dict[str, Any]:
    """SLO 임계치 가져오기"""
    return health_config.get_slo_thresholds()

def get_rate_limit_config() -> Dict[str, Any]:
    """Rate limit 설정 가져오기"""
    return health_config.get_rate_limit_config()
