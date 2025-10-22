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

logger_config = None


def setup_logger(
    name: str = "duri_core",
    level: str = "INFO",
    log_file: Optional[str] = None,
    log_format: Optional[str] = None,
) -> logging.Logger:
    """
    로거를 설정하고 반환합니다.

    Args:
        name: 로거 이름
        level: 로그 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 로그 파일 경로 (선택사항)
        log_format: 로그 포맷 (선택사항)

    Returns:
        설정된 로거
    """
    logger = logging.getLogger(name)

    # 이미 핸들러가 있으면 제거
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # 로그 레벨 설정
    log_level = getattr(logging, level.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 기본 포맷 설정
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    formatter = logging.Formatter(log_format)

    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 파일 핸들러 추가 (선택사항)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "duri_core") -> logging.Logger:
    """
    로거를 가져옵니다. 없으면 새로 생성합니다.

    Args:
        name: 로거 이름

    Returns:
        로거
    """
    logger = logging.getLogger(name)

    # 핸들러가 없으면 기본 설정
    if not logger.handlers:
        return setup_logger(name)

    return logger


def log_performance(func):
    """
    함수 실행 시간을 로깅하는 데코레이터
    """

    def wrapper(*args, **kwargs):
        logger = get_logger("performance")
        start_time = datetime.now()

        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.info(f"{func.__name__} 실행 완료: {duration:.3f}초")
            return result

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            logger.error(f"{func.__name__} 실행 실패: {duration:.3f}초 - {str(e)}")
            raise

    return wrapper


def log_error(func):
    """
    에러를 로깅하는 데코레이터
    """

    def wrapper(*args, **kwargs):
        logger = get_logger("error")

        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{func.__name__} 에러: {str(e)}", exc_info=True)
            raise

    return wrapper
