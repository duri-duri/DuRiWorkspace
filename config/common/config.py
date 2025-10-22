#!/usr/bin/env python3
"""
Configuration management for DuRi Emotion Processing System
"""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# 환경변수 로드
env_path = Path("/app/.env")
load_dotenv(dotenv_path=env_path)


class Config:
    """중앙화된 설정 관리 클래스"""

    # ========================================
    # 📁 디렉토리 설정
    # ========================================

    @staticmethod
    def get_log_dir() -> str:
        """로그 디렉토리 경로"""
        return os.getenv("LOG_DIR", "/tmp/logs")

    @staticmethod
    def get_emotion_data_dir() -> str:
        """감정 데이터 디렉토리 경로"""
        return os.getenv("EMOTION_DATA_DIR", "/tmp/emotion_data")

    @staticmethod
    def get_script_dir() -> str:
        """스크립트 디렉토리 경로"""
        return os.getenv("SCRIPT_DIR", "/tmp/scripts")

    @staticmethod
    def get_evolution_dir() -> str:
        """진화 데이터 디렉토리 경로"""
        return os.getenv("EVOLUTION_DIR", "/tmp/evolution_data")

    # ========================================
    # 📄 파일 경로 설정
    # ========================================

    @staticmethod
    def get_receive_json_log() -> str:
        """감정 수신 JSON 로그 파일 경로"""
        return os.getenv("RECEIVE_JSON_LOG", "/tmp/receive.json")

    @staticmethod
    def get_update_script_path() -> str:
        """업데이트 스크립트 경로"""
        return os.getenv("UPDATE_SCRIPT_PATH", "/tmp/../scripts/update_cur_from_delta.py")

    @staticmethod
    def get_evolution_log() -> str:
        """진화 로그 파일 경로"""
        return os.getenv("EVOLUTION_LOG", "/tmp/emotion_data/evolution_log.json")

    @staticmethod
    def get_action_stats_path() -> str:
        """액션 통계 파일 경로"""
        return os.getenv("ACTION_STATS_PATH", "/tmp/evolution_data/action_stats.json")

    # ========================================
    # 🌐 네트워크 설정
    # ========================================

    @staticmethod
    def get_port() -> int:
        """서버 포트"""
        return int(os.getenv("PORT", "8080"))

    @staticmethod
    def get_brain_url() -> str:
        """Brain 서비스 URL"""
        return os.getenv("BRAIN_URL", "http://localhost:8081/brain")

    @staticmethod
    def get_evolution_url() -> str:
        """Evolution 서비스 URL"""
        return os.getenv("EVOLUTION_URL", "http://localhost:8082/evolve")

    # ========================================
    # 🧠 Brain 시스템 설정
    # ========================================

    @staticmethod
    def get_state_dir() -> str:
        """Brain 상태 디렉토리"""
        return os.getenv("STATE_DIR", "/tmp/brain_state")

    @staticmethod
    def get_decision_log() -> str:
        """Brain 결정 로그"""
        return os.getenv("DECISION_LOG", "/tmp/brain_state/decision_log.json")

    @staticmethod
    def get_brain_port() -> int:
        """Brain 서버 포트"""
        return int(os.getenv("BRAIN_PORT", "8081"))

    # ========================================
    # 🔄 Evolution 시스템 설정
    # ========================================

    @staticmethod
    def get_evolution_port() -> int:
        """Evolution 서버 포트"""
        return int(os.getenv("EVOLUTION_PORT", "8082"))

    # ========================================
    # 🏠 로컬 개발 환경 설정
    # ========================================

    @staticmethod
    def get_local_brain_url() -> str:
        """로컬 Brain URL (개발용)"""
        return os.getenv("LOCAL_BRAIN_URL", "http://localhost:8081/brain")

    @staticmethod
    def get_local_evolution_url() -> str:
        """로컬 Evolution URL (개발용)"""
        return os.getenv("LOCAL_EVOLUTION_URL", "http://localhost:8082/evolve")

    @staticmethod
    def get_local_emotion_url() -> str:
        """로컬 감정 전송 URL"""
        return os.getenv("LOCAL_EMOTION_URL", "http://127.0.0.1:8080/emotion")

    # ========================================
    # 📊 정책 설정
    # ========================================

    @staticmethod
    def get_importance_threshold() -> float:
        """중요도 임계값"""
        return float(os.getenv("IMPORTANCE_THRESHOLD", "0.3"))

    # ========================================
    # 🔧 기타 설정
    # ========================================

    @staticmethod
    def get_debug() -> bool:
        """디버그 모드"""
        return os.getenv("DEBUG", "false").lower() == "true"

    @staticmethod
    def get_log_level() -> str:
        """로그 레벨"""
        return os.getenv("LOG_LEVEL", "INFO")

    @staticmethod
    def get_request_timeout() -> int:
        """요청 타임아웃 (초)"""
        return int(os.getenv("REQUEST_TIMEOUT", "3"))

    @staticmethod
    def get_max_log_size() -> int:
        """최대 로그 파일 크기 (MB)"""
        return int(os.getenv("MAX_LOG_SIZE", "100"))

    # ========================================
    # 🗄️ 데이터베이스 설정
    # ========================================

    @staticmethod
    def get_database_url() -> str:
        """데이터베이스 연결 URL"""
        return os.getenv("DATABASE_URL", "postgresql://duri:duri@localhost:5432/duri")

    @staticmethod
    def get_redis_url() -> str:
        """Redis 연결 URL"""
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")

    # ========================================
    # 🛠️ 유틸리티 메서드
    # ========================================

    @staticmethod
    def get_all_config() -> dict:
        """모든 설정을 딕셔너리로 반환"""
        return {
            "directories": {
                "log_dir": Config.get_log_dir(),
                "emotion_data_dir": Config.get_emotion_data_dir(),
                "script_dir": Config.get_script_dir(),
                "evolution_dir": Config.get_evolution_dir(),
                "state_dir": Config.get_state_dir(),
            },
            "files": {
                "receive_json_log": Config.get_receive_json_log(),
                "update_script_path": Config.get_update_script_path(),
                "evolution_log": Config.get_evolution_log(),
                "action_stats_path": Config.get_action_stats_path(),
                "decision_log": Config.get_decision_log(),
            },
            "network": {
                "port": Config.get_port(),
                "brain_url": Config.get_brain_url(),
                "evolution_url": Config.get_evolution_url(),
                "brain_port": Config.get_brain_port(),
                "evolution_port": Config.get_evolution_port(),
            },
            "local": {
                "local_brain_url": Config.get_local_brain_url(),
                "local_evolution_url": Config.get_local_evolution_url(),
                "local_emotion_url": Config.get_local_emotion_url(),
            },
            "policy": {
                "importance_threshold": Config.get_importance_threshold(),
            },
            "system": {
                "debug": Config.get_debug(),
                "log_level": Config.get_log_level(),
                "request_timeout": Config.get_request_timeout(),
                "max_log_size": Config.get_max_log_size(),
            },
            "database": {
                "database_url": Config.get_database_url(),
                "redis_url": Config.get_redis_url(),
            },
        }

    @staticmethod
    def print_config():
        """현재 설정을 출력"""
        config = Config.get_all_config()
        print("=== DuRi Configuration ===")
        for category, settings in config.items():
            print(f"\n[{category.upper()}]")
            for key, value in settings.items():
                print(f"  {key}: {value}")
        print("=" * 30)


# 전역 설정 인스턴스
config = Config()
