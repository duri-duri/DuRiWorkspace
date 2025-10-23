#!/usr/bin/env python3
"""
SSOT (Single Source of Truth) Configuration for DuRi System

This module provides a centralized configuration management using Pydantic Settings.
All configuration values are defined here with proper defaults and validation.
"""

import os
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class DuRiSettings(BaseSettings):
    """
    DuRi System Configuration Settings

    This class defines all configuration parameters for the DuRi system.
    It serves as the single source of truth for all configuration values.
    """

    # === Core Application Settings ===
    SECRET_KEY: str = Field(default="dev-secret-key", description="Flask secret key")
    DEBUG: bool = Field(default=False, description="Debug mode")

    # === Database Settings ===
    DATABASE_URL: str = Field(default="sqlite:///duri_core.db", description="Database connection URL")

    # === Redis Settings ===
    REDIS_URL: str = Field(default="redis://localhost:6379", description="Redis connection URL")

    # === Logging Settings ===
    LOG_DIR: str = Field(default="/tmp/logs", description="Log directory path")
    LOG_FILE: Optional[str] = Field(default=None, description="Main log file path (auto-generated if None)")
    RECEIVE_JSON_LOG: str = Field(default="/tmp/receive.json", description="Receive log file path")

    # === Evolution Settings ===
    EVOLUTION_LOG_PATH: str = Field(
        default="/tmp/emotion_data/evolution_log.json",
        description="Evolution log file path",
    )
    ACTION_STATS_PATH: str = Field(
        default="/tmp/evolution_data/action_stats.json",
        description="Action stats file path",
    )

    # === Service URLs ===
    BRAIN_URL: str = Field(default="http://duri-brain:8081/brain", description="Brain service URL")
    EVOLUTION_URL: str = Field(default="http://duri-evolution:8082/evolve", description="Evolution service URL")

    # === Request Settings ===
    REQUEST_TIMEOUT: int = Field(default=5, description="Default request timeout in seconds")

    # === Monitoring Settings ===
    METRICS_ENABLED: bool = Field(default=True, description="Enable metrics collection")
    HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Health check interval in seconds")

    class Config:
        env_file = "/app/.env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_log_file_path(self) -> str:
        """
        Get the log file path, creating it if it doesn't exist.

        Returns:
            str: Full path to the log file
        """
        if self.LOG_FILE:
            return self.LOG_FILE

        # Auto-generate log file path
        os.makedirs(self.LOG_DIR, exist_ok=True)
        return os.path.join(self.LOG_DIR, "duri_core.log")

    def ensure_directories(self) -> None:
        """
        Ensure all required directories exist.
        """
        directories = [
            self.LOG_DIR,
            os.path.dirname(self.RECEIVE_JSON_LOG),
            os.path.dirname(self.EVOLUTION_LOG_PATH),
            os.path.dirname(self.ACTION_STATS_PATH),
        ]

        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)

    def validate_required_paths(self) -> None:
        """
        Validate that all required paths are accessible.
        Raises SystemExit if any required path is invalid.
        """
        required_paths = [
            self.RECEIVE_JSON_LOG,
            self.EVOLUTION_LOG_PATH,
            self.ACTION_STATS_PATH,
        ]

        missing_paths = []
        for path in required_paths:
            if not path:
                missing_paths.append(path)

        if missing_paths:
            raise SystemExit(f"Missing required configuration paths: {missing_paths}")


# Global settings instance
settings = DuRiSettings()


def get_settings() -> DuRiSettings:
    """
    Get the global settings instance.

    Returns:
        DuRiSettings: The global settings instance
    """
    return settings


def reload_settings() -> DuRiSettings:
    """
    Reload settings from environment variables.

    Returns:
        DuRiSettings: New settings instance
    """
    global settings
    settings = DuRiSettings()
    return settings
