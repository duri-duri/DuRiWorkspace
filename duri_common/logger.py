#!/usr/bin/env python3
"""
DuRi Common Logger Module

공통으로 사용되는 로깅 기능을 제공합니다.
"""

from datetime import datetime
import logging
import os
import sys
from typing import Optional

from duri_common.config.config import Config

logger_config = Config()


def setup_logger(
    name: str = "duri_core",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: str = "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
) -> logging.Logger:
    """
    로거 설정 및 반환

    Args:
        name (str): 로거 이름
        level (str): 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file (str, optional): 로그 파일 경로
        log_format (str): 로그 포맷

    Returns:
        logging.Logger: 설정된 로거
    """
    # 로거 생성
    logger = logging.getLogger(name)

    # 이미 핸들러가 설정되어 있다면 중복 설정 방지
    if logger.handlers:
        return logger

    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 포맷터 생성
    formatter = logging.Formatter(log_format)

    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 설정 (선택적)
    if log_file:
        try:
            # 로그 디렉토리 생성
            log_dir = os.path.dirname(log_file)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file, encoding="utf-8")
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception as e:
            logger.warning(f"로그 파일 핸들러 설정 실패: {e}")

    return logger


def get_logger(name: str = "duri_core") -> logging.Logger:
    """
    기본 로거 반환

    Args:
        name (str): 로거 이름

    Returns:
        logging.Logger: 로거 인스턴스
    """
    return logging.getLogger(name)


# 기본 로거 설정
def configure_default_logger(log_file: Optional[str] = None) -> logging.Logger:
    """
    기본 로거 설정

    Args:
        log_file (str, optional): 로그 파일 경로

    Returns:
        logging.Logger: 설정된 로거
    """
    # 설정에서 로그 레벨 가져오기
    log_level = logger_config.get_log_level()

    # 로그 파일 경로 설정
    if not log_file:
        log_dir = logger_config.get_log_dir()
        log_file = os.path.join(log_dir, "duri_core.log")

    return setup_logger(name="duri_core", level=log_level, log_file=log_file)


# 로거 데코레이터
def log_function_call(logger: Optional[logging.Logger] = None):
    """
    함수 호출을 로깅하는 데코레이터

    Args:
        logger (logging.Logger, optional): 로거 인스턴스
    """

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


# 컨텍스트 매니저
class LogContext:
    """
    로그 컨텍스트 매니저
    """

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
            self.logger.error(
                f"실패: {self.message} (소요시간: {duration.total_seconds():.3f}s)"
            )
        else:
            self.logger.info(
                f"완료: {self.message} (소요시간: {duration.total_seconds():.3f}s)"
            )


# 기본 로거 인스턴스
default_logger = configure_default_logger()
