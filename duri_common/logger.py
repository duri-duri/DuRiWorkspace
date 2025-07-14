#!/usr/bin/env python3
"""
DuRi Common Logger Module

공통으로 사용되는 로깅 기능을 제공합니다.
"""

import logging
import os
import sys
from datetime import datetime
from typing import Optional

try:
    from duri_common.config.config import Config
    logger_config = Config()
except ImportError:
    # fallback 설정
    class FallbackConfig:
        def get_log_level(self): return "INFO"
        def get_log_dir(self): return "./logs"
    logger_config = FallbackConfig()


def setup_logger(
    name: str = "duri_core",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    formatter = logging.Formatter(log_format)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        try:
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"로그 파일 핸들러 설정 실패: {e}")

    return logger


def get_logger(name: str = "duri_core") -> logging.Logger:
    return logging.getLogger(name)


def configure_default_logger(log_file: Optional[str] = None) -> logging.Logger:
    log_level = logger_config.get_log_level()
    if not log_file:
        log_dir = logger_config.get_log_dir()
        log_file = os.path.join(log_dir, "duri_core.log")
    return setup_logger(name="duri_core", level=log_level, log_file=log_file)


def log_function_call(logger: Optional[logging.Logger] = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            log = logger or get_logger()
            log.debug(f"함수 호출: {func.__name__} (args: {args}, kwargs: {kwargs})")
            try:
                result = func(*args, **kwargs)
                log.debug(f"함수 완료: {func.__name__} -> {result}")
                return result
            except Exception as e:
                log.error(f"함수 오류: {func.__name__} -> {e}")
                raise
        return wrapper
    return decorator


class LogContext:
    def __init__(self, logger: logging.Logger, message: str, level: str = "info"):
        self.logger = logger
        self.message = message
        self.level = level
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        log_func = getattr(self.logger, self.level, self.logger.info)
        log_func(f"시작: {self.message}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = datetime.now() - self.start_time
        if exc_type:
            self.logger.error(f"실패: {self.message} (소요시간: {duration.total_seconds():.3f}s)")
        else:
            self.logger.info(f"완료: {self.message} (소요시간: {duration.total_seconds():.3f}s)")


# ✅ 진입점에서 사용되는 기본 로거
default_logger = configure_default_logger()
